import unittest

from inference_engine.engine import run_inference


class TestWBCNormalization(unittest.TestCase):
    def test_parser_label_t_wbc_is_normalized_and_evaluated(self):
        result = run_inference({"T.WBC": 4.32})

        self.assertEqual(result["facts"]["wbc"], 4.32)
        self.assertEqual(result["statuses"]["wbc"]["value"], 4.32)
        self.assertEqual(result["statuses"]["wbc"]["status"], "طبيعي")
        self.assertNotIn(
            "wbc",
            next(
                rule["explanation"]
                for rule in result["fired_rules"]
                if rule["rule_id"] == "R29"
            ),
        )

    def test_t_wbc_variant_is_normalized(self):
        result = run_inference({"T_WBC": 12.0})

        self.assertEqual(result["facts"]["wbc"], 12.0)
        self.assertEqual(result["statuses"]["wbc"]["status"], "مرتفع")


if __name__ == "__main__":
    unittest.main()
