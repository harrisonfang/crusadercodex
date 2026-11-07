#!/usr/bin/env python3
"""Rebuild a pet recipe and write a self-contained, editable animation preview."""

import argparse
import base64
import hashlib
import html
import io
import json
import math
from pathlib import Path
from urllib.parse import quote

from PIL import Image

if __package__:
    from .build_pet import build, read_json
else:
    from build_pet import build, read_json


def compiled_animations(directory, states, runtime, scale, anchor, prefix='compiled'):
    """Embed exact built cells without allowing their timed layer samples to be remapped."""
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError('Compiled scale must be positive and finite')
    report = read_json(directory / 'build-report.json')
    for key in ('sprite_version', 'cell_width', 'cell_height', 'columns', 'rows'):
        if report['runtime'][key] != runtime[key]:
            raise ValueError(f'Compiled pet and preview runtime disagree on {key}')
    rows = {row['state']: row for row in report['rows']}
    selected = states if states is not None else [row['name'] for row in runtime['rows']]
    if len(set(selected)) != len(selected) or any(state not in rows for state in selected):
        raise ValueError('Compiled states must be unique names present in the build report')
    cell_width, cell_height = runtime['cell_width'], runtime['cell_height']
    with Image.open(directory / 'spritesheet.png') as image:
        atlas = image.convert('RGBA')
    expected_size = (cell_width * runtime['columns'], cell_height * len(runtime['rows']))
    if atlas.size != expected_size:
        raise ValueError(f'Compiled atlas must measure {expected_size}, got {atlas.size}')
    animations = []
    defaults = {}
    for state in selected:
        row = rows[state]
        row_index = next(i for i, item in enumerate(runtime['rows']) if item['name'] == state)
        timing = runtime['rows'][row_index]
        if row['row'] != row_index or len(row['frames']) != timing['frames']:
            raise ValueError(f'{state}: compiled row index or frame count is incorrect')
        frames = []
        for column, frame in enumerate(row['frames']):
            if frame['column'] != column or frame['duration_ms'] != timing['delays_ms'][column]:
                raise ValueError(f'{state}: compiled frame order or timing is incorrect')
            left, top = column * cell_width, row_index * cell_height
            cell = atlas.crop((left, top, left + cell_width, top + cell_height))
            buffer = io.BytesIO()
            cell.save(buffer, format='PNG')
            # Geometry uses original-source units, while the PNG retains every atlas pixel.
            embedded = {'origin': {'x': anchor[0] / scale, 'y': anchor[1] / scale},
                        'width': cell_width / scale, 'height': cell_height / scale,
                        'layers': frame['layers'],
                        'image': 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')}
            if 'uncropped' in frame:
                uncropped = frame['uncropped']
                raw = (directory / uncropped['file']).read_bytes()
                with Image.open(io.BytesIO(raw)) as image:
                    if image.format != 'PNG' or list(image.size) != uncropped['size']:
                        raise ValueError(f'{state} frame {column}: invalid uncropped PNG dimensions')
                offset = uncropped['cell_offset']
                if (len(offset) != 2 or any(type(n) is not int or n < 0 for n in offset)
                        or offset[0] + cell_width > uncropped['size'][0]
                        or offset[1] + cell_height > uncropped['size'][1]):
                    raise ValueError(f'{state} frame {column}: cell lies outside uncropped PNG')
                embedded['uncropped'] = {**uncropped,
                    'image': 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')}
            frames.append(embedded)
        name = prefix + ':' + state
        defaults[state] = name
        animations.append({'name': name, 'label': row.get('label', state + ' composition'),
                           'note': row.get('description', 'Exact composed atlas cells.'),
                           'state': state, 'composed': True, 'pixel_scale': scale,
                           'cell_size': [cell_width, cell_height], 'frames': frames})
    return animations, defaults


def source_key(alias, animation):
    return f"raw:{quote(alias, safe='')}/{quote(animation, safe='')}"


def raw_animations(recipe_path, recipe):
    animations = []
    for alias, relative in recipe["sources"].items():
        manifest_path = recipe_path.parent / relative
        source = read_json(manifest_path)
        for name, animation in source["animations"].items():
            frames = []
            for item in animation["frames"]:
                path = manifest_path.parent / item["file"]
                raw = path.read_bytes()
                if item.get("sha256") and hashlib.sha256(raw).hexdigest() != item["sha256"]:
                    raise ValueError(f"Source PNG checksum does not match: {path}")
                with Image.open(io.BytesIO(raw)) as image:
                    if image.format != "PNG":
                        raise ValueError(f"Expected a PNG source: {path}")
                    width, height = image.size
                frames.append({
                    "origin": item["origin"], "width": width, "height": height,
                    "source_delay_ms": item.get("delay_ms"),
                    "image": "data:image/png;base64," + base64.b64encode(raw).decode("ascii"),
                })
            if not frames:
                raise ValueError(f"No frames in {alias}/{name}")
            animations.append({
                "name": source_key(alias, name), "label": f"{alias} / {name}",
                "note": "One static source pose." if len(frames) == 1 else "",
                "frames": frames,
            })
    return animations


def editable_mapping(row, scale, anchor):
    """Use raw frames only when they reproduce every compiled pose and transform."""
    selectors = []
    mapping = None
    for frame in row["frames"]:
        if len(frame["layers"]) != 1:
            return None
        layer = frame["layers"][0]
        if (layer["scale"] != scale or layer["anchor"] != anchor or layer["offset"] != [0, 0]
                or layer.get("opacity", 1) != 1 or "clipping" in layer):
            return None
        choice = (source_key(layer["source"], layer["animation"]), layer["mirror"])
        if mapping is not None and choice != mapping:
            return None
        mapping = choice
        selectors.append(layer["frame"])
    return {"source": mapping[0], "mirror": mapping[1], "frames": selectors}


def write_preview(recipe_path, build_directory=None, comparisons=()):
    recipe = read_json(recipe_path)
    directory = build(recipe_path, build_directory)
    report = read_json(directory / "build-report.json")
    runtime = report["runtime"]
    profile = read_json(recipe_path.parent / recipe["runtime_profile"])
    scale = recipe.get("defaults", {}).get("scale", 1)
    anchor = recipe.get("defaults", {}).get("anchor", [runtime["cell_width"] // 2, runtime["cell_height"] // 2])
    originals = raw_animations(recipe_path, recipe)
    cells, compiled_defaults = compiled_animations(directory, None, runtime, scale, anchor)
    defaults = {}
    for row in report["rows"]:
        mapping = editable_mapping(row, scale, anchor)
        if mapping:
            state = row["state"]
            defaults[state] = mapping
            del compiled_defaults[state]
    animations = originals + cells
    for index, comparison in enumerate(comparisons):
        candidates, _ = compiled_animations(comparison, None, runtime, scale, anchor, f"comparison:{index}")
        for candidate in candidates:
            candidate["label"] = f"{comparison.name} / {candidate['label']}"
        animations.extend(candidates)
    data = {
        "profile": {
            "rows": runtime["rows"], "sprite_version": runtime["sprite_version"],
            "non_idle_repeat_count": profile.get("playback", {}).get("nonIdleRepeatCount", 3),
        },
        "animations": animations, "defaults": defaults, "compiled_defaults": compiled_defaults,
    }
    template = (Path(__file__).parent / "templates" / "source-preview.html").read_text(encoding="utf-8")
    # A literal '<' in JSON could close the script tag even in a non-executable data block.
    payload = json.dumps(data, separators=(",", ":")).replace("<", r"\u003c")
    title = html.escape(recipe["pet"]["displayName"])
    before, after = template.split("__SOURCE_PREVIEW_DATA__")
    output = directory / "source-preview.html"
    output.write_text(before.replace("__PET_TITLE__", title) + payload + after, encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--build-dir", type=Path, help="Override the recipe's build directory")
    parser.add_argument("--compare-build", type=Path, action="append", default=[],
                        help="Include exact cells from a previously built pet (repeatable)")
    args = parser.parse_args()
    try:
        output = write_preview(args.recipe, args.build_dir, args.compare_build)
    except (ValueError, KeyError, IndexError, OSError) as error:
        parser.exit(1, f"Preview failed: {error}\n")
    print(f"Source preview: {output}")


if __name__ == "__main__":
    main()
