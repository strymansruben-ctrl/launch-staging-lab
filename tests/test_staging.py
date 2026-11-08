import math
import unittest

from staging import G0, Stage, calculate


class StagingTests(unittest.TestCase):
    def test_single_stage_matches_hand_calculation(self):
        burn, = calculate([Stage("single", 100, 120, 300)], 20)
        self.assertEqual((burn.start_kg, burn.burnout_kg), (240, 120))
        self.assertAlmostEqual(burn.delta_v_m_s, G0 * 300 * math.log(2))

    def test_booster_carries_fueled_upper_stage_and_separates(self):
        booster, upper = calculate([Stage("b", 100, 300, 300), Stage("u", 20, 80, 320)], 10)
        self.assertEqual((booster.start_kg, booster.burnout_kg), (510, 210))
        self.assertEqual((upper.start_kg, upper.burnout_kg), (110, 30))
        self.assertAlmostEqual(booster.delta_v_m_s, G0 * 300 * math.log(510 / 210))
        self.assertAlmostEqual(upper.delta_v_m_s, G0 * 320 * math.log(110 / 30))

    def test_payload_reduces_delta_v(self):
        stages = [Stage("single", 100, 120, 300)]
        self.assertGreater(calculate(stages, 20)[0].delta_v_m_s,
                           calculate(stages, 40)[0].delta_v_m_s)

    def test_zero_propellant_gives_zero_delta_v(self):
        burn, = calculate([Stage("single", 100, 0, 300)], 0)
        self.assertEqual(burn.delta_v_m_s, 0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            Stage("single", True, 10, 300)
        with self.assertRaises(ValueError):
            calculate([Stage("single", 100, 120, 300)], float("nan"))
