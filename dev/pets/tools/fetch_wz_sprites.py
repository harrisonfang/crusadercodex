#!/usr/bin/env python3
"""Fetch lossless MapleStory WZ frame canvases with origins and explicit delays.

Usage: python3 dev/pets/tools/fetch_wz_sprites.py dev/pets/recipes/maplestory-slime/fetch-effects.json
Requires curl; decoding/downloads use only the Python standard library.
Existing cached HTTP responses are reused unless --refresh is passed.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from urllib.parse import quote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    out = (args.config.resolve().parent / config["output"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "raw"
    cache.mkdir(exist_ok=True)
    base = "https://maplestory.io/api/wz/" + quote(config["region"], safe="") + "/" + quote(config["version"], safe="") + "/"

    def fetch(path):
        url = base + quote(path, safe="/")
        target = cache / (hashlib.sha256(url.encode()).hexdigest() + ".json")
        if target.exists() and not args.refresh:
            return json.loads(target.read_text())
        result = subprocess.run(["curl", "-fsSL", "--retry", "3", "--max-time", "40", url], capture_output=True, check=True)
        parsed = json.loads(result.stdout)
        target.write_bytes(result.stdout)
        return parsed

    def frame(job):
        name, source, index = job
        path = source + "/" + str(index)
        node = fetch(path)
        if node["type"] != 12:
            raise ValueError(f"{path}: expected a WZ Canvas (type 12), got {node['type']}; resolve links explicitly")
        png = base64.b64decode(node["value"], validate=True)
        if png[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"{path}: invalid PNG signature")
        width, height = struct.unpack(">II", png[16:24])
        props = {key: fetch(path + "/" + key).get("value") for key in node["children"]}
        origin = props.get("origin")
        if not isinstance(origin, dict) or not {"x", "y"} <= origin.keys():
            raise ValueError(f"{path}: explicit origin required")
        target = out / "frames" / name / f"{index}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(png)
        return name, {
            "index": index, "file": str(target.relative_to(out)),
            "width": width, "height": height,
            "origin": {"x": origin["x"], "y": origin["y"]},
            "delay_ms": props.get("delay"),
            "delay_status": "explicit_wz" if "delay" in props else "absent_in_wz",
            "properties": props, "wz_path": path, "source_url": base + quote(path, safe="/"),
            "sha256": hashlib.sha256(png).hexdigest(),
        }

    animations, jobs = {}, []
    for name, path in config["animations"].items():
        ids = sorted(int(child) for child in fetch(path)["children"] if child.isdigit())
        if not ids:
            raise ValueError(f"{path}: no numbered frames")
        animations[name] = {"wz_path": path, "frames": []}
        jobs.extend((name, path, index) for index in ids)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for name, data in pool.map(frame, jobs):
            animations[name]["frames"].append(data)
    manifest = {
        "source": {"provider": "maplestory.io", "region": config["region"], "version": config["version"],
                   "retrieved_at": datetime.now(timezone.utc).isoformat(), "base_url": base,
                   "art_owner": "Nexon / Wizet", "method": "Base64 PNG canvases decoded without pixel edits; original WZ properties retained."},
        "animations": animations,
        "notes": ["A null delay_ms means the WZ frame does not specify a delay. No game-client fallback timing has been assumed."],
    }
    (out / "animations.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for name, animation in animations.items():
        frames = animation["frames"]
        print(f"{name}: {len(frames)} frames; delays {[f['delay_ms'] for f in frames]} ms")
    print(out / "animations.json")


if __name__ == "__main__":
    main()
