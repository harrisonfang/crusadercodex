#!/usr/bin/env python3
"""Compile original game frames into a Codex v1 pet, without repainting pixels.

Usage: python3 dev/common/build_pet.py dev/maplestory/slime/recipe.json
Dependency: Pillow. Each source manifest locates its image_root relative to its
own directory. Frame paths are relative to image_root. The runtime profile is a separate
input so updated Codex timings and future game assets do not require code edits.

Config schema_version=1: pet (Codex manifest), output, runtime_profile, sources
(alias -> animation manifest), defaults, and rows (runtime state -> layers).
Each layer selects a source, animation, integer scale, anchor [x,y], mirror, and
one frame selector per runtime column. A selector is an integer frame index,
null (hide the layer), or {animation: name, frame: index}. Optional offsets are
one [x,y] pair per column. Prefer a reusable motion curve (ballistic, decelerate,
or exponential-stop) for translation; each path is
sampled at actual runtime frame start times; its coordinates are output pixels.
Optional opacities are one number from 0 to 1 per column, applied to source alpha
only. Intentional cropping requires allow_clipping: true on the affected layer;
clipped layers include diagnostics and an uncropped composite in the build output.
Layer order is back-to-front. Origins are preserved;
the scaled WZ origin is placed on the anchor plus that column's offset.

This deliberately uses explicit frame maps: Codex cannot honor source durations.
Source timing, source hashes, and the final mapping are saved in build_report.json.
Every used layer is checked for clipped visible pixels before output is written.
Unexpected clipping is an error; explicit clipping never permits an empty cell.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

if __package__:
    from .preview.atlas import preview_html
    from .motion import finite_number, frame_start_times, motion_offsets, motion_state
else:
    from preview.atlas import preview_html
    from motion import finite_number, frame_start_times, motion_offsets, motion_state

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Pillow is required. Run this with a Python environment containing Pillow.")


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value, label: str, minimum: int | None = None) -> int:
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ValueError(f"{label} must be an integer" + (f" >= {minimum}" if minimum is not None else ""))
    return value


def pair(value, label: str) -> tuple[int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{label} must contain two integer coordinates")
    return integer(value[0], label), integer(value[1], label)


def load_profile(path: Path) -> dict:
    raw = read_json(path)
    profile = {key: raw[key] for key in ("sprite_version", "cell_width", "cell_height", "columns", "rows")}
    if profile["sprite_version"] != 1:
        raise ValueError("This compiler currently supports Codex sprite version 1; version 2 needs pointer-look poses.")
    for key in ("cell_width", "cell_height", "columns"):
        integer(profile[key], f"runtime profile {key}", 1)
    names = set()
    for row in profile["rows"]:
        if row["name"] in names:
            raise ValueError(f"Duplicate runtime row {row['name']}")
        names.add(row["name"])
        count = integer(row["frames"], f"runtime {row['name']} frame count", 1)
        if count > profile["columns"] or len(row["delays_ms"]) != count:
            raise ValueError(f"Invalid runtime frame count/delays for {row['name']}")
        for delay in row["delays_ms"]:
            integer(delay, f"runtime {row['name']} delay", 1)
    return profile


def apply_opacity(sprite: Image.Image, opacity: float) -> Image.Image:
    """Multiply existing alpha without altering RGB, including transparent RGB."""
    opacity = finite_number(opacity, "layer opacity", 0)
    if opacity > 1:
        raise ValueError("layer opacity must be <= 1")
    if opacity == 1:
        return sprite
    faded = sprite.copy()
    faded.putalpha(sprite.getchannel("A").point([math.floor(alpha * opacity + 0.5) for alpha in range(256)]))
    return faded


def clipping_info(sprite: Image.Image, position: tuple[int, int], cell_size: tuple[int, int]) -> dict | None:
    """Measure actual alpha-positive pixels lost at the cell boundary, after fading."""
    alpha = sprite.getchannel("A")
    visible = alpha.getbbox()
    if not visible:
        return None
    x, y = position
    width, height = cell_size
    bounds = [visible[0] + x, visible[1] + y, visible[2] + x, visible[3] + y]
    overflow = {"left": max(0, -bounds[0]), "top": max(0, -bounds[1]),
                "right": max(0, bounds[2] - width), "bottom": max(0, bounds[3] - height)}
    if not any(overflow.values()):
        return None
    visible_pixels = sum(alpha.histogram()[1:])
    inside = (max(0, -x), max(0, -y), min(sprite.width, width - x), min(sprite.height, height - y))
    kept_pixels = (sum(alpha.crop(inside).histogram()[1:])
                   if inside[0] < inside[2] and inside[1] < inside[3] else 0)
    return {"visible_bounds": bounds, "overflow": overflow,
            "visible_pixels": visible_pixels, "lost_pixels": visible_pixels - kept_pixels}


def uncropped_composite(composed_layers: list, cell_size: tuple[int, int]) -> tuple[Image.Image, list[int]]:
    """Render the same prepared layers on a canvas including the cell and all visible art."""
    left, top, right, bottom = 0, 0, *cell_size
    for sprite, (x, y) in composed_layers:
        visible = sprite.getchannel("A").getbbox()
        if visible:
            left, top = min(left, visible[0] + x), min(top, visible[1] + y)
            right, bottom = max(right, visible[2] + x), max(bottom, visible[3] + y)
    composite = Image.new("RGBA", (right - left, bottom - top))
    for sprite, (x, y) in composed_layers:
        composite.alpha_composite(sprite, (x - left, y - top))
    return composite, [-left, -top]


def compose_layer(layer: dict, selector, offset, sources: dict, cell_size: tuple[int, int], label: str, opacity: float = 1):
    source = sources[layer["source"]]
    if isinstance(selector, dict):
        animation = selector.get("animation", layer.get("animation"))
        index = selector["frame"]
    else:
        animation, index = layer["animation"], selector
    integer(index, f"{label} source frame", 0)
    frames = source["data"]["animations"][animation]["frames"]
    if index >= len(frames):
        raise ValueError(f"{label}: {animation} has {len(frames)} frames, requested {index}")
    frame = frames[index]
    path = (source["path"].parent / source["data"]["image_root"] / frame["file"]).resolve()
    sha256 = digest(path)
    if frame.get("sha256") and frame["sha256"] != sha256:
        raise ValueError(f"{label}: source PNG hash changed: {path}")
    with Image.open(path) as image:
        sprite = image.convert("RGBA")
    original_size = sprite.size
    origin_x, origin_y = pair([frame["origin"]["x"], frame["origin"]["y"]], f"{label} source origin")
    scale = integer(layer.get("scale", 1), f"{label} scale", 1)
    mirror = layer.get("mirror", False)
    if not isinstance(mirror, bool):
        raise ValueError(f"{label} mirror must be true or false")
    if mirror:
        sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        origin_x = sprite.width - origin_x
    if scale != 1:
        sprite = sprite.resize((sprite.width * scale, sprite.height * scale), Image.Resampling.NEAREST)
    sprite = apply_opacity(sprite, opacity)
    anchor_x, anchor_y = pair(layer["anchor"], f"{label} anchor")
    offset_x, offset_y = pair(offset, f"{label} offset")
    position = (anchor_x + offset_x - origin_x * scale, anchor_y + offset_y - origin_y * scale)
    allow_clipping = layer.get("allow_clipping", False)
    if not isinstance(allow_clipping, bool):
        raise ValueError(f"{label} allow_clipping must be true or false")
    clipping = clipping_info(sprite, position, cell_size)
    if clipping and not allow_clipping:
        raise ValueError(f"{label}: visible pixels would clip: {clipping['visible_bounds']}, cell {cell_size}; adjust scale/anchor/offset or explicitly set allow_clipping on this layer")
    provenance = {
        "source": layer["source"], "animation": animation, "frame": index,
        "file": frame["file"], "sha256": sha256, "original_size": list(original_size),
        "source_delay_ms": frame.get("delay_ms"), "source_origin": frame["origin"],
        "scale": scale, "mirror": mirror, "anchor": list(layer["anchor"]),
        "offset": list(offset), "top_left": list(position),
    }
    if "opacities" in layer or "motion" in layer:
        provenance["opacity"] = opacity
    if "motion" in layer:
        provenance["motion"] = layer["motion"]
    if clipping:
        provenance["clipping"] = clipping
    return sprite, position, provenance


def build(config_path: Path, output_override: Path | None = None) -> Path:
    config_path = config_path.resolve()
    config = read_json(config_path)
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported config schema_version; expected 1")
    base = config_path.parent
    profile_path = (base / config["runtime_profile"]).resolve()
    profile = load_profile(profile_path)
    output = output_override.resolve() if output_override else (base / config["output"]).resolve()
    pet = dict(config["pet"])
    allowed = {"id", "displayName", "description", "spriteVersionNumber", "spritesheetPath"}
    if set(pet) - allowed:
        raise ValueError(f"Unsupported Codex manifest fields: {sorted(set(pet) - allowed)}")
    if pet.get("spriteVersionNumber") != profile["sprite_version"]:
        raise ValueError("Manifest spriteVersionNumber must match runtime profile")
    if pet.get("spritesheetPath") != "spritesheet.png":
        raise ValueError("Set pet.spritesheetPath to spritesheet.png for this lossless PNG compiler")
    if not pet.get("displayName"):
        raise ValueError("pet.displayName is required")
    sources = {}
    for name, relative_path in config["sources"].items():
        path = (base / relative_path).resolve()
        sources[name] = {"path": path, "data": read_json(path)}
    width, height = profile["cell_width"], profile["cell_height"]
    expected_names = [row["name"] for row in profile["rows"]]
    if set(config["rows"]) != set(expected_names):
        raise ValueError(f"Config rows must match runtime states exactly: {expected_names}")
    atlas = Image.new("RGBA", (width * profile["columns"], height * len(profile["rows"])))
    report = {
        "config": config_path.name, "config_sha256": digest(config_path),
        "runtime_profile_sha256": digest(profile_path), "runtime": profile,
        "timing_policy": "Explicit source frame maps retimed to fixed Codex runtime durations. Source delays are preserved as provenance, never treated as target delays.",
        "image_policy": "Original RGBA sprites; integer nearest-neighbor scaling, optional exact horizontal reflection, original origins, and alpha compositing only.",
        "sources": {name: {"manifest": config["sources"][name], "manifest_sha256": digest(value["path"]), "source": value["data"]["source"]} for name, value in sources.items()},
        "rows": [],
    }
    previews = []
    uncropped_images = []
    clipped_layer_count = 0
    for row_index, runtime in enumerate(profile["rows"]):
        name, count = runtime["name"], runtime["frames"]
        recipe = config["rows"][name]
        layers = [dict(config.get("defaults", {}), **layer) for layer in recipe["layers"]]
        offsets = []
        starts = frame_start_times(runtime["delays_ms"])
        for layer_index, layer in enumerate(layers):
            label = f"{name}, layer {layer_index}"
            if len(layer["frames"]) != count:
                raise ValueError(f"{name}, layer {layer_index}: expected exactly {count} frame selectors")
            if "offsets" in layer and len(layer["offsets"]) != count:
                raise ValueError(f"{name}, layer {layer_index}: expected exactly {count} offsets")
            if "offsets" in layer and "motion" in layer:
                raise ValueError(f"{label}: offsets and motion are mutually exclusive")
            offsets.append(motion_offsets(layer["motion"], runtime["delays_ms"], label) if "motion" in layer
                           else layer.get("offsets", [[0, 0]] * count))
            if "opacities" in layer:
                if not isinstance(layer["opacities"], list) or len(layer["opacities"]) != count:
                    raise ValueError(f"{label}: expected exactly {count} opacities")
                for opacity in layer["opacities"]:
                    if finite_number(opacity, f"{label} opacity", 0) > 1:
                        raise ValueError(f"{label}: opacity must be <= 1")
        row_report = {"state": name, "row": row_index, "description": recipe.get("description", ""), "frames": []}
        if "label" in recipe:
            row_report["label"] = recipe["label"]
        row_images = []
        for column in range(count):
            cell = Image.new("RGBA", (width, height))
            cell_report = {"column": column, "duration_ms": runtime["delays_ms"][column], "layers": []}
            composed_layers = []
            for layer_index, layer in enumerate(layers):
                selector = layer["frames"][column]
                if selector is None:
                    continue
                offset = offsets[layer_index][column]
                opacity = layer.get("opacities", [1] * count)[column]
                sprite, position, provenance = compose_layer(layer, selector, offset, sources, (width, height), f"{name} column {column} layer {layer_index}", opacity)
                if "motion" in layer:
                    provenance["sample_ms"] = starts[column]
                    provenance["motion_state"] = motion_state(layer["motion"], starts[column], f"{name} layer {layer_index}")
                cell.alpha_composite(sprite, position)
                composed_layers.append((sprite, position))
                cell_report["layers"].append(provenance)
            if not cell.getchannel("A").getbbox():
                raise ValueError(f"{name} column {column}: a required pet frame is completely transparent")
            clipped_layers = sum("clipping" in layer for layer in cell_report["layers"])
            if clipped_layers:
                clipped_layer_count += clipped_layers
                full_art, cell_offset = uncropped_composite(composed_layers, (width, height))
                filename = f"clipping/{name}-{column}.png"
                cell_report["uncropped"] = {"file": filename, "size": list(full_art.size), "cell_offset": cell_offset}
                uncropped_images.append((filename, full_art))
            atlas.alpha_composite(cell, (column * width, row_index * height))
            row_images.append(cell)
            row_report["frames"].append(cell_report)
        report["rows"].append(row_report)
        previews.append((runtime, row_images))

    # All validation and composition complete before replacing generated files.
    output.mkdir(parents=True, exist_ok=True)
    preview_dir = output / "previews"
    preview_dir.mkdir(exist_ok=True)
    atlas_path = output / "spritesheet.png"
    atlas.save(atlas_path, optimize=True)
    if uncropped_images:
        (output / "clipping").mkdir(exist_ok=True)
        for filename, full_art in uncropped_images:
            full_art.save(output / filename, optimize=True)
    for runtime, frames in previews:
        row_strip = Image.new("RGBA", (width * len(frames), height))
        for column, frame in enumerate(frames):
            row_strip.alpha_composite(frame, (column * width, 0))
        row_strip.save(preview_dir / f"{runtime['name']}.png", optimize=True)
        frames[0].save(preview_dir / f"{runtime['name']}.apng", format="PNG", save_all=True,
                       append_images=frames[1:], duration=runtime["delays_ms"], loop=0,
                       disposal=0, blend=0, optimize=False)
    report["output"] = {"atlas": "spritesheet.png", "sha256": digest(atlas_path), "size": list(atlas.size), "mode": atlas.mode, "active_frames": sum(row["frames"] for row in profile["rows"])}
    for filename, data in (("pet.json", pet), ("build_report.json", report)):
        (output / filename).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "preview.html").write_text(preview_html(pet, profile, report), encoding="utf-8")
    with Image.open(atlas_path) as saved:
        if saved.mode != "RGBA" or saved.size != atlas.size or saved.tobytes() != atlas.tobytes():
            raise ValueError("Saved atlas failed lossless round-trip verification")
    clipping_summary = (f"{clipped_layer_count} intentionally clipped layer frames across {len(uncropped_images)} cells"
                        if clipped_layer_count else "no clipped layers")
    print(f"Built {pet['displayName']}: {atlas.width}×{atlas.height}, {report['output']['active_frames']} active frames, {clipping_summary}")
    print(f"Output: {output}")
    print(f"Preview: {output / 'preview.html'}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path, help="Override the config's output directory")
    args = parser.parse_args()
    try:
        build(args.config, args.output)
    except (ValueError, KeyError, IndexError, OSError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
