"""Focused checks for retimed motion and lossless-alpha sprite composition.

Run with a Pillow-enabled Python: python -m unittest discover -s dev/pets/tools -p 'test_*.py'
"""

import json
import math
import tempfile
import unittest
from decimal import Decimal, localcontext
from pathlib import Path

from PIL import Image

from build_pet import apply_opacity, build, compose_layer, digest
from motion import frame_start_times, motion_offsets, motion_state, sample_motion


class MotionTests(unittest.TestCase):
    def test_unequal_delays_sample_starts_not_frame_indices(self):
        # Final frame begins at 350 ms and holds for 400 ms. It must not be
        # sampled at 750 ms, nor at equally spaced fractions of the cycle.
        delays = [100, 250, 400]
        trajectory = {"type": "ballistic", "duration_ms": 500,
                      "displacement": [100, 0], "height_px": 50}
        self.assertEqual(frame_start_times(delays), [0, 100, 350])
        self.assertEqual(motion_offsets(trajectory, delays), [[0, 0], [20, -32], [70, -42]])

    def test_delayed_start_and_settled_position_clamp(self):
        trajectory = {"type": "ballistic", "start_ms": 100, "duration_ms": 400,
                      "displacement": [40, 20], "height_px": 30}
        self.assertEqual([sample_motion(trajectory, time) for time in (0, 100, 300, 500, 900)],
                         [[0, 0], [0, 0], [20, -20], [40, 20], [40, 20]])

    def test_knockback_decelerates_and_stops(self):
        trajectory = {"type": "decelerate", "duration_ms": 400, "displacement": [-32, 0]}
        self.assertEqual([sample_motion(trajectory, time) for time in (0, 100, 200, 300, 400, 900)],
                         [[0, 0], [-14, 0], [-24, 0], [-30, 0], [-32, 0], [-32, 0]])

    def test_default_deceleration_matches_explicit_quadratic(self):
        trajectory = {"type": "decelerate", "start_ms": 75, "duration_ms": 600,
                      "displacement": [46, -30], "pixel_step": 2}
        explicit = dict(trajectory, exponent=2)
        for time in range(-100, 1000):
            with self.subTest(time=time):
                self.assertEqual(sample_motion(trajectory, time), sample_motion(explicit, time))
        self.assertEqual([sample_motion(trajectory, time) for time in (75, 225, 375, 525, 675)],
                         [[0, 0], [20, -14], [34, -22], [44, -28], [46, -30]])

    def test_stronger_deceleration_at_runtime_frame_starts(self):
        trajectory = {"type": "decelerate", "duration_ms": 600,
                      "displacement": [46, 0], "pixel_step": 2, "exponent": 4}
        self.assertEqual(motion_offsets(trajectory, [150, 150, 150, 150, 150, 260]),
                         [[0, 0], [32, 0], [44, 0], [46, 0], [46, 0], [46, 0]])

    def test_stronger_deceleration_keeps_endpoints_and_slows_monotonically(self):
        trajectory = {"type": "decelerate", "start_ms": 100, "duration_ms": 400,
                      "displacement": [4096, -4096], "exponent": 4}
        self.assertEqual(sample_motion(trajectory, -100), [0, 0])
        self.assertEqual(sample_motion(trajectory, 100), [0, 0])
        self.assertEqual(sample_motion(trajectory, 500), [4096, -4096])
        self.assertEqual(sample_motion(trajectory, 900), [4096, -4096])
        positions = [sample_motion(trajectory, time) for time in (100, 200, 300, 400, 500)]
        steps = [after[0] - before[0] for before, after in zip(positions, positions[1:])]
        self.assertTrue(all(step > 0 for step in steps))
        self.assertTrue(all(before > after for before, after in zip(steps, steps[1:])))
        self.assertTrue(all(y == -x for x, y in positions))
        self.assertGreater(positions[1][0], sample_motion(dict(trajectory, exponent=2), 200)[0])

    def test_fractional_deceleration_exponent_is_supported(self):
        trajectory = {"type": "decelerate", "duration_ms": 100,
                      "displacement": [100, 0], "exponent": 1.5}
        self.assertEqual(sample_motion(trajectory, 50), [65, 0])

    def test_invalid_deceleration_exponents_are_rejected(self):
        trajectory = {"type": "decelerate", "duration_ms": 100, "displacement": [10, 0]}
        for exponent in (1, 0, -2, float("nan"), float("inf"), float("-inf"),
                         True, False, "4", None, [], {}):
            with self.subTest(exponent=exponent), self.assertRaisesRegex(ValueError, "exponent"):
                sample_motion(dict(trajectory, exponent=exponent), 50)

    def test_pixel_step_is_symmetric_for_both_directions(self):
        for dx in (-6, 6):
            trajectory = {"type": "decelerate", "duration_ms": 100,
                          "displacement": [dx, 0], "pixel_step": 4}
            self.assertEqual(sample_motion(trajectory, 100), [-8 if dx < 0 else 8, 0])

    def test_exponential_stop_samples_fixed_endpoints_and_signed_motion(self):
        trajectory = {"type": "exponential-stop", "duration_ms": 600,
                      "decay_rate_per_s": 5, "displacement": [42, -21]}
        self.assertEqual(motion_offsets(trajectory, [150, 150, 150, 150, 150, 260]),
                         [[0, 0], [26, -13], [37, -18], [41, -21], [42, -21], [42, -21]])
        states = [motion_state(trajectory, time) for time in (0, 100, 200, 300, 400, 500, 600)]
        self.assertTrue(all(before["offset_px"][0] < after["offset_px"][0]
                            for before, after in zip(states, states[1:])))
        self.assertTrue(all(before["velocity_px_s"][0] > after["velocity_px_s"][0]
                            for before, after in zip(states, states[1:])))
        for state in states[:-1]:
            self.assertLess(state["acceleration_px_s2"][0], 0)
            self.assertGreater(state["acceleration_px_s2"][1], 0)
            self.assertAlmostEqual(state["velocity_px_s"][1], -state["velocity_px_s"][0] / 2)

    def test_motion_state_holds_before_start_and_at_finish(self):
        base = {"start_ms": 100, "duration_ms": 400, "displacement": [40, -20]}
        models = ({"type": "ballistic", "height_px": 30},
                  {"type": "decelerate", "exponent": 1.5},
                  {"type": "exponential-stop", "decay_rate_per_s": 5})
        for model in models:
            trajectory = dict(base, **model)
            with self.subTest(model=model):
                self.assertEqual(motion_state(trajectory, 0),
                                 {"offset_px": [0.0, 0.0], "velocity_px_s": [0.0, 0.0],
                                  "acceleration_px_s2": [0.0, 0.0]})
                self.assertGreater(motion_state(trajectory, 100)["velocity_px_s"][0], 0)
                for time in (500, 900):
                    self.assertEqual(motion_state(trajectory, time),
                                     {"offset_px": [40.0, -20.0], "velocity_px_s": [0.0, 0.0],
                                      "acceleration_px_s2": [0.0, 0.0]})

    def test_analytical_derivatives_agree_with_interior_finite_differences(self):
        base = {"duration_ms": 600, "displacement": [80, -30]}
        models = ({"type": "ballistic", "height_px": 32},
                  {"type": "decelerate", "exponent": 4},
                  {"type": "exponential-stop", "decay_rate_per_s": 5},
                  {"type": "exponential-stop", "decay_rate_per_s": 0.001})
        delta_ms = 0.01
        for model in models:
            trajectory = dict(base, **model)
            for time in (10, 125, 300, 550):
                with self.subTest(model=model, time=time):
                    before = motion_state(trajectory, time - delta_ms)
                    state = motion_state(trajectory, time)
                    after = motion_state(trajectory, time + delta_ms)
                    for axis in range(2):
                        velocity = (after["offset_px"][axis] - before["offset_px"][axis]) / (2 * delta_ms / 1000)
                        acceleration = (after["velocity_px_s"][axis] - before["velocity_px_s"][axis]) / (2 * delta_ms / 1000)
                        self.assertTrue(math.isclose(state["velocity_px_s"][axis], velocity, rel_tol=1e-7, abs_tol=1e-7))
                        self.assertTrue(math.isclose(state["acceleration_px_s2"][axis], acceleration, rel_tol=1e-7, abs_tol=1e-7))

    def test_zero_and_tiny_decay_rates_match_quadratic_limit(self):
        base = {"duration_ms": 1000, "displacement": [100, -50]}
        quadratic = dict(base, type="decelerate")
        for rate in (0, 1e-300, 1e-20, 1e-12):
            trajectory = dict(base, type="exponential-stop", decay_rate_per_s=rate)
            for time in (0, 100, 500, 999, 1000):
                with self.subTest(rate=rate, time=time):
                    state = motion_state(trajectory, time)
                    expected = motion_state(quadratic, time)
                    for key in state:
                        for actual, reference in zip(state[key], expected[key]):
                            self.assertTrue(math.isclose(actual, reference, rel_tol=1e-10, abs_tol=1e-10))

    def test_small_rate_series_agrees_with_high_precision_formula(self):
        with localcontext() as context:
            context.prec = 100
            u = Decimal("0.37")
            for rate in ("1e-18", "1e-8", "0.0999", "0.1", "0.1001", "3"):
                q = Decimal(rate)
                tail, decay = (-q).exp(), (-q * u).exp()
                denominator = 1 - (1 + q) * tail
                expected = [(1 - decay - q * u * tail) / denominator,
                            q * (decay - tail) / denominator, -q * q * decay / denominator]
                trajectory = {"type": "exponential-stop", "duration_ms": 1000,
                              "displacement": [1, 0], "decay_rate_per_s": float(rate)}
                state = motion_state(trajectory, 370)
                with self.subTest(rate=rate):
                    for key, reference in zip(("offset_px", "velocity_px_s", "acceleration_px_s2"), expected):
                        self.assertTrue(math.isclose(state[key][0], float(reference), rel_tol=1e-12, abs_tol=1e-12))

    def test_strong_decay_remains_finite_and_stops(self):
        trajectory = {"type": "exponential-stop", "duration_ms": 1000,
                      "displacement": [10, -10], "decay_rate_per_s": 1000}
        start = motion_state(trajectory, 0)
        self.assertEqual(start["velocity_px_s"], [10000.0, -10000.0])
        self.assertEqual(start["acceleration_px_s2"], [-10000000.0, 10000000.0])
        self.assertEqual(sample_motion(trajectory, 1), [6, -6])
        for time in (1, 10, 500, 1000):
            state = motion_state(trajectory, time)
            self.assertTrue(all(math.isfinite(value) for vector in state.values() for value in vector))
        self.assertEqual(motion_state(trajectory, 1000)["velocity_px_s"], [0.0, 0.0])

    def test_invalid_decay_rates_and_unrepresentable_duration_product(self):
        trajectory = {"type": "exponential-stop", "duration_ms": 100, "displacement": [10, 0]}
        for rate in (-1, True, False, None, "5", float("nan"), float("inf"), 10 ** 1000):
            with self.subTest(rate=rate), self.assertRaisesRegex(ValueError, "decay_rate_per_s"):
                motion_state(dict(trajectory, decay_rate_per_s=rate), 0)
        with self.assertRaisesRegex(ValueError, "rate × duration"):
            motion_state(dict(trajectory, duration_ms=1e308, decay_rate_per_s=1e308), 0)

    def test_invalid_physics_are_rejected(self):
        trajectory = {"type": "ballistic", "duration_ms": 100,
                      "displacement": [10, 0], "height_px": 20}
        for override in ({"duration_ms": 0}, {"height_px": -1}, {"pixel_step": 0},
                         {"displacement": [float("nan"), 0]}, {"pixel_step": True}):
            with self.subTest(override=override), self.assertRaises(ValueError):
                sample_motion(dict(trajectory, **override), 50)


class AlphaTests(unittest.TestCase):
    def test_fade_preserves_rgb_and_multiplies_source_alpha(self):
        source = Image.new("RGBA", (3, 1))
        source.putdata([(10, 20, 30, 255), (40, 50, 60, 128), (70, 80, 90, 0)])
        faded = apply_opacity(source, 0.5)
        self.assertEqual([faded.getpixel((x, 0)) for x in range(3)],
                         [(10, 20, 30, 128), (40, 50, 60, 64), (70, 80, 90, 0)])
        self.assertEqual(source.getpixel((0, 0)), (10, 20, 30, 255))

    def test_full_opacity_is_a_byte_identical_no_op(self):
        source = Image.new("RGBA", (1, 1), (17, 23, 91, 128))
        self.assertIs(apply_opacity(source, 1), source)

    def test_invalid_opacity_is_rejected(self):
        source = Image.new("RGBA", (1, 1))
        for opacity in (-0.1, 1.1, float("nan"), True):
            with self.subTest(opacity=opacity), self.assertRaises(ValueError):
                apply_opacity(source, opacity)


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        Image.new("RGBA", (2, 2), (21, 42, 63, 255)).save(self.path / "sprite.png")
        frame = {"file": "sprite.png", "origin": {"x": 1, "y": 2},
                 "sha256": digest(self.path / "sprite.png")}
        self.source_data = {"source": {"description": "test fixture"},
                            "animations": {"stand": {"frames": [frame]}}}
        self.manifest = self.path / "source.json"
        self.manifest.write_text(json.dumps(self.source_data))
        self.sources = {"test": {"path": self.manifest, "data": self.source_data}}
        self.layer = {"source": "test", "animation": "stand", "scale": 2,
                      "anchor": [4, 8], "frames": [0]}

    def test_offsets_keep_scaled_source_origin(self):
        sprite, position, info = compose_layer(self.layer, 0, [1, -2], self.sources, (10, 10), "fixture")
        self.assertEqual(position, (3, 2))
        self.assertEqual(sprite.size, (4, 4))
        self.assertEqual(info["source_origin"], {"x": 1, "y": 2})
        self.assertNotIn("opacity", info)

    def test_invisible_layer_allowed_but_visible_clipping_still_rejected(self):
        invisible = dict(self.layer, opacities=[0])
        sprite, _, info = compose_layer(invisible, 0, [0, -20], self.sources, (10, 10), "fixture", 0)
        self.assertIsNone(sprite.getchannel("A").getbbox())
        self.assertEqual(info["opacity"], 0)
        with self.assertRaisesRegex(ValueError, "would clip"):
            compose_layer(self.layer, 0, [0, -20], self.sources, (10, 10), "fixture")

    def test_build_rejects_empty_composite_and_conflicting_motion(self):
        profile = {"sprite_version": 1, "cell_width": 10, "cell_height": 10, "columns": 1,
                   "rows": [{"name": "idle", "frames": 1, "delays_ms": [100]}]}
        (self.path / "profile.json").write_text(json.dumps(profile))
        config = {"schema_version": 1, "output": "built", "runtime_profile": "profile.json",
                  "pet": {"displayName": "Fixture", "spriteVersionNumber": 1, "spritesheetPath": "spritesheet.png"},
                  "sources": {"test": "source.json"}, "rows": {"idle": {"layers": []}}}
        config_path = self.path / "config.json"
        cases = [(dict(self.layer, opacities=[0]), "completely transparent"),
                 (dict(self.layer, offsets=[[0, 0]], motion={}), "mutually exclusive"),
                 (dict(self.layer, opacities=[1, 1]), "exactly 1 opacities")]
        for layer, expected in cases:
            with self.subTest(expected=expected):
                config["rows"]["idle"]["layers"] = [layer]
                config_path.write_text(json.dumps(config))
                with self.assertRaisesRegex(ValueError, expected):
                    build(config_path)
                self.assertFalse((self.path / "built").exists())

    def test_build_reports_analytical_state_at_unequal_frame_starts(self):
        profile = {"sprite_version": 1, "cell_width": 10, "cell_height": 10, "columns": 4,
                   "rows": [{"name": "idle", "frames": 4, "delays_ms": [50, 100, 100, 70]}]}
        (self.path / "profile.json").write_text(json.dumps(profile))
        trajectory = {"type": "exponential-stop", "duration_ms": 250,
                      "displacement": [2, 0], "decay_rate_per_s": 5}
        layer = dict(self.layer, frames=[0, 0, 0, 0], motion=trajectory)
        config = {"schema_version": 1, "output": "built", "runtime_profile": "profile.json",
                  "pet": {"displayName": "Fixture", "spriteVersionNumber": 1, "spritesheetPath": "spritesheet.png"},
                  "sources": {"test": "source.json"}, "rows": {"idle": {"layers": [layer]}}}
        config_path = self.path / "config.json"
        config_path.write_text(json.dumps(config))
        output = build(config_path)
        report = json.loads((output / "build-report.json").read_text())
        layers = [frame["layers"][0] for frame in report["rows"][0]["frames"]]
        self.assertEqual([layer["sample_ms"] for layer in layers], [0, 50, 150, 250])
        for layer, time in zip(layers, (0, 50, 150, 250)):
            self.assertEqual(layer["motion_state"], motion_state(trajectory, time))
            self.assertEqual(layer["offset"], sample_motion(trajectory, time))
            self.assertTrue(all(type(value) is float for vector in layer["motion_state"].values() for value in vector))
        self.assertNotEqual(layers[1]["motion_state"]["offset_px"], layers[1]["offset"])
        self.assertEqual(layers[-1]["motion_state"]["velocity_px_s"], [0.0, 0.0])
        self.assertEqual(layers[-1]["motion_state"]["acceleration_px_s2"], [0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
