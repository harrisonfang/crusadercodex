"""Rebuild each published recipe against its install files, without the network."""

import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from build_pet import build


def pixel_digest(image):
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


class ShippedPetTest(unittest.TestCase):
    def test_recipes_match_published_pets(self):
        authoring = Path(__file__).resolve().parents[1]
        published = authoring.parent / "assets" / "pets"
        manifests = {}
        for path in sorted(published.rglob("pet.json")):
            manifest = json.loads(path.read_text())
            pet_id = manifest["id"]
            if pet_id in manifests:
                self.fail(f"Duplicate pet ID {pet_id!r} in {manifests[pet_id][0]} and {path.parent}")
            manifests[pet_id] = (path.parent, manifest)

        matched = 0
        for recipe in sorted(authoring.glob("*/recipe.json")):
            pet_id = json.loads(recipe.read_text())["pet"]["id"]
            if pet_id not in manifests:  # A draft recipe need not have install files yet.
                continue
            shipped, manifest = manifests[pet_id]
            matched += 1
            with self.subTest(pet=pet_id), tempfile.TemporaryDirectory() as directory:
                with contextlib.redirect_stdout(io.StringIO()):
                    generated = build(recipe, Path(directory))
                self.assertEqual(json.loads((generated / "pet.json").read_text()), manifest)
                filename = manifest["spritesheetPath"]
                with Image.open(generated / filename) as result, Image.open(shipped / filename) as expected:
                    self.assertEqual(result.size, expected.size)
                    # PNG compression can differ across builds. Compare every RGBA pixel.
                    self.assertEqual(pixel_digest(result), pixel_digest(expected))
        self.assertGreater(matched, 0, "No published pets matched an authoring recipe")


if __name__ == "__main__":
    unittest.main()
