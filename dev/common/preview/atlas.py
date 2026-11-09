"""Render the standalone HTML preview for the finished atlas."""

import html
import json
from pathlib import Path


def preview_html(pet: dict, profile: dict, report: dict) -> str:
    """Embed playback metadata in a page that loads the adjacent spritesheet."""
    data = {"pet": pet, "profile": profile, "rows": report["rows"]}
    payload = json.dumps(data, ensure_ascii=False).replace("<", r"\u003c")
    title = html.escape(pet["displayName"])
    template = Path(__file__).with_name("atlas.html").read_text(encoding="utf-8")
    before, after = template.split("__ATLAS_DATA__")
    return before.replace("__PET_TITLE__", title) + payload + after
