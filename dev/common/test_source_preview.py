"""Check when the editable source preview can represent the built row exactly."""
import unittest

from build_source_preview import editable_mapping


class PreviewMappingTests(unittest.TestCase):
    def setUp(self):
        self.layer = {
            "source": "monster", "animation": "stand", "frame": 2, "mirror": True,
            "anchor": [12, 30], "scale": 2, "offset": [0, 0],
        }

    def mapping(self, second_frame):
        row = {"frames": [{"layers": [self.layer]}, {"layers": second_frame}]}
        return editable_mapping(row, 2, [12, 30])

    def test_simple_row_keeps_recipe_order_and_mirroring(self):
        self.assertEqual(self.mapping([dict(self.layer, frame=0)]),
                         {"source": "raw:monster/stand", "mirror": True, "frames": [2, 0]})

    def test_composition_and_transform_changes_use_built_pixels(self):
        for second in ([], [self.layer, self.layer], [dict(self.layer, source="effect")],
                       [dict(self.layer, offset=[1, 0])], [dict(self.layer, opacity=0.5)],
                       [dict(self.layer, clipping={"lost_pixels": 1})]):
            with self.subTest(second=second):
                self.assertIsNone(self.mapping(second))
