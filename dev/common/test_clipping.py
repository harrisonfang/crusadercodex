"""Verify explicit clipping preserves the real cell and exposes honest full-art diagnostics."""

import contextlib
import base64
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from build_pet import build, clipping_info, compose_layer
from dev.common.preview.source import compiled_animations


class ClippingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        images = {"base": Image.new("RGBA", (4, 4), (220, 40, 20, 255)),
                  "effect": Image.new("RGBA", (3, 3), (20, 40, 220, 128)),
                  "front": Image.new("RGBA", (1, 1), (10, 240, 30, 255))}
        animations = {}
        for name, image in images.items():
            image.save(self.path / f"{name}.png")
            animations[name] = {"frames": [{"file": f"{name}.png", "origin": {"x": 0, "y": 0}}]}
        self.source = {"image_root": ".", "source": {"description": "fixture"}, "animations": animations}
        (self.path / "source.json").write_text(json.dumps(self.source))
        self.sources = {"fixture": {"path": self.path / "source.json", "data": self.source}}
        self.profile = {"sprite_version": 1, "cell_width": 4, "cell_height": 4, "columns": 1,
                        "rows": [{"name": "review", "frames": 1, "delays_ms": [280]}]}
        (self.path / "profile.json").write_text(json.dumps(self.profile))
        self.config = {"schema_version": 1, "output": "built", "runtime_profile": "profile.json",
                       "pet": {"displayName": "Fixture", "spriteVersionNumber": 1, "spritesheetPath": "spritesheet.png"},
                       "sources": {"fixture": "source.json"}, "rows": {"review": {"layers": []}}}
        self.effect = {"source": "fixture", "animation": "effect", "anchor": [-1, -1], "frames": [0]}

    def run_build(self, layers):
        self.config["rows"]["review"]["layers"] = layers
        config_path = self.path / "config.json"
        config_path.write_text(json.dumps(self.config))
        with contextlib.redirect_stdout(io.StringIO()):
            return build(config_path)

    def test_clipping_is_rejected_by_default_and_requires_boolean(self):
        with self.assertRaisesRegex(ValueError, "would clip"):
            self.run_build([self.effect])
        self.assertFalse((self.path / "built").exists())
        with self.assertRaisesRegex(ValueError, "must be true or false"):
            self.run_build([dict(self.effect, allow_clipping="true")])

    def test_counts_visible_pixels_not_bounding_box_area_or_alpha_sum(self):
        sprite = Image.new("RGBA", (3, 3))
        for xy, alpha in (((0, 0), 1), ((2, 0), 128), ((1, 1), 255), ((2, 2), 1)):
            sprite.putpixel(xy, (30, 40, 50, alpha))
        info = clipping_info(sprite, (-1, -1), (2, 2))
        self.assertEqual(info, {"visible_bounds": [-1, -1, 2, 2],
                                "overflow": {"left": 1, "top": 1, "right": 0, "bottom": 0},
                                "visible_pixels": 4, "lost_pixels": 2})
        fully_outside = clipping_info(sprite, (5, 5), (2, 2))
        self.assertEqual(fully_outside["lost_pixels"], 4)

    def test_transparent_margins_are_not_clipping(self):
        sprite = Image.new("RGBA", (5, 5))
        sprite.putpixel((2, 2), (50, 60, 70, 255))
        self.assertIsNone(clipping_info(sprite, (-2, -2), (1, 1)))
        faded, _, info = compose_layer(dict(self.effect, opacities=[0]), 0, [0, 0],
                                      self.sources, (4, 4), "fixture", 0)
        self.assertIsNone(faded.getchannel("A").getbbox())
        self.assertNotIn("clipping", info)

    def test_full_art_matches_cell_and_preserves_layer_order_and_opacity(self):
        layers = [{"source": "fixture", "animation": "base", "anchor": [0, 0], "frames": [0]},
                  dict(self.effect, allow_clipping=True, opacities=[0.5]),
                  {"source": "fixture", "animation": "front", "anchor": [0, 0], "frames": [0]}]
        output = self.run_build(layers)
        report = json.loads((output / "build_report.json").read_text())
        frame = report["rows"][0]["frames"][0]
        self.assertEqual(frame["uncropped"], {"file": "clipping/review-0.png", "size": [5, 5], "cell_offset": [1, 1]})
        self.assertEqual(frame["layers"][1]["clipping"]["lost_pixels"], 5)
        with Image.open(output / frame["uncropped"]["file"]) as full_art, Image.open(output / "spritesheet.png") as atlas:
            self.assertEqual(full_art.crop((1, 1, 5, 5)).tobytes(), atlas.tobytes())
            self.assertEqual(full_art.getpixel((0, 0)), (20, 40, 220, 64))
            self.assertEqual(atlas.getpixel((0, 0)), (10, 240, 30, 255))
            self.assertEqual(atlas.getpixel((1, 1)), (170, 40, 70, 255))

    def test_explicit_clipping_never_allows_a_completely_empty_cell(self):
        with self.assertRaisesRegex(ValueError, "completely transparent"):
            self.run_build([dict(self.effect, anchor=[-10, -10], allow_clipping=True)])
        self.assertFalse((self.path / "built").exists())

    def test_unrelated_state_and_multiple_layers_survive_preview_embedding_on_all_edges(self):
        # This is deliberately neither a Slime animation nor a built-in row name.
        # Metadata must be driven entirely by the chosen runtime, source and geometry.
        state = "future-pet-effect"
        self.profile["rows"][0]["name"] = state
        (self.path / "profile.json").write_text(json.dumps(self.profile))
        self.config["rows"] = {state: {"layers": [
            dict(self.effect, allow_clipping=True),
            dict(self.effect, anchor=[3, 3], allow_clipping=True),
        ]}}
        config_path = self.path / "config.json"
        config_path.write_text(json.dumps(self.config))
        with contextlib.redirect_stdout(io.StringIO()):
            output = build(config_path)
        animations, defaults = compiled_animations(output, None, self.profile, 1, [0, 0])
        self.assertEqual(defaults, {state: "compiled:" + state})
        self.assertEqual(animations[0]["state"], state)
        frame = animations[0]["frames"][0]
        self.assertEqual(frame["layers"][0]["clipping"]["overflow"],
                         {"left": 1, "top": 1, "right": 0, "bottom": 0})
        self.assertEqual(frame["layers"][1]["clipping"],
                         {"visible_bounds": [3, 3, 6, 6],
                          "overflow": {"left": 0, "top": 0, "right": 2, "bottom": 2},
                          "visible_pixels": 9, "lost_pixels": 8})
        self.assertEqual(frame["uncropped"]["size"], [7, 7])
        self.assertEqual(frame["uncropped"]["cell_offset"], [1, 1])
        full_bytes = base64.b64decode(frame["uncropped"]["image"].split(",", 1)[1])
        cell_bytes = base64.b64decode(frame["image"].split(",", 1)[1])
        with Image.open(io.BytesIO(full_bytes)) as full_art, Image.open(io.BytesIO(cell_bytes)) as cell:
            self.assertEqual(full_art.crop((1, 1, 5, 5)).tobytes(), cell.tobytes())
            self.assertGreater(full_art.getpixel((0, 0))[3], 0)
            self.assertGreater(full_art.getpixel((6, 6))[3], 0)

    def test_no_clipping_keeps_report_shape_and_artifact_set(self):
        output = self.run_build([dict(self.effect, anchor=[0, 0])])
        report = json.loads((output / "build_report.json").read_text())
        frame = report["rows"][0]["frames"][0]
        self.assertNotIn("uncropped", frame)
        self.assertNotIn("clipping", frame["layers"][0])
        self.assertFalse((output / "clipping").exists())


if __name__ == "__main__":
    unittest.main()
