import unittest
import rules


# --------------------------------------------------
# Base CBC Test Data
# --------------------------------------------------

def create_normal_facts():

    return {
        "age": 35,
        "sex": "male",

        "hb": 15,
        "pcv": 45,
        "wbc": 5,

        "neutrophils_pct": 50,
        "lymphocytes_pct": 30,
        "monocytes_pct": 5,
        "eosinophils_pct": 2,

        "neutrophils_abs": 2.5,
        "lymphocytes_abs": 1.5,
        "monocytes_abs": 0.25,
        "eosinophils_abs": 0.1,

        "platelets": 250,
        "rbc": 5,

        "mcv": 85,
        "mch": 29,
        "mchc": 33,
        "rdw": 13,

        "units_valid": True
    }


# --------------------------------------------------
# Testing All 30 Rules
# --------------------------------------------------

class TestMedExpertRules(unittest.TestCase):

    # Rule 01
    def test_rule_01(self):
        f = create_normal_facts()
        f["hb"] = 11

        self.assertEqual(rules.rule_01(f)["rule_id"], "R01")

    # Rule 02
    def test_rule_02(self):
        f = create_normal_facts()
        f.update({"hb": 11, "mcv": 70})

        self.assertEqual(rules.rule_02(f)["rule_id"], "R02")

    # Rule 03
    def test_rule_03(self):
        f = create_normal_facts()
        f.update({"hb": 11, "mcv": 85})

        self.assertEqual(rules.rule_03(f)["rule_id"], "R03")

    # Rule 04
    def test_rule_04(self):
        f = create_normal_facts()
        f.update({"hb": 11, "mcv": 105})

        self.assertEqual(rules.rule_04(f)["rule_id"], "R04")

    # Rule 05
    def test_rule_05(self):
        f = create_normal_facts()
        f["mcv"] = 70

        self.assertEqual(rules.rule_05(f)["rule_id"], "R05")

    # Rule 06
    def test_rule_06(self):
        f = create_normal_facts()
        f["mcv"] = 105

        self.assertEqual(rules.rule_06(f)["rule_id"], "R06")

    # Rule 07
    def test_rule_07(self):
        f = create_normal_facts()
        f.update({"hb": 11, "rdw": 16})

        self.assertEqual(rules.rule_07(f)["rule_id"], "R07")

    # Rule 08
    def test_rule_08(self):
        f = create_normal_facts()
        f.update({"mcv": 70, "rbc": 5})

        self.assertEqual(rules.rule_08(f)["rule_id"], "R08")

    # Rule 09
    def test_rule_09(self):
        f = create_normal_facts()
        f.update({"mcv": 70, "mch": 24})

        self.assertEqual(rules.rule_09(f)["rule_id"], "R09")

    # Rule 10
    def test_rule_10(self):
        f = create_normal_facts()
        f.update({
            "hb": 19,
            "pcv": 55,
            "rbc": 7
        })

        self.assertEqual(rules.rule_10(f)["rule_id"], "R10")

    # Rule 11
    def test_rule_11(self):
        f = create_normal_facts()
        f["wbc"] = 3

        self.assertEqual(rules.rule_11(f)["rule_id"], "R11")

    # Rule 12
    def test_rule_12(self):
        f = create_normal_facts()
        f["wbc"] = 11

        self.assertEqual(rules.rule_12(f)["rule_id"], "R12")

    # Rule 13
    def test_rule_13(self):
        f = create_normal_facts()
        f["neutrophils_abs"] = 1.5

        self.assertEqual(rules.rule_13(f)["rule_id"], "R13")

    # Rule 14
    def test_rule_14(self):
        f = create_normal_facts()
        f["neutrophils_abs"] = 0.3

        self.assertEqual(rules.rule_14(f)["rule_id"], "R14")

    # Rule 15
    def test_rule_15(self):
        f = create_normal_facts()
        f["lymphocytes_abs"] = 0.8

        self.assertEqual(rules.rule_15(f)["rule_id"], "R15")

    # Rule 16
    def test_rule_16(self):
        f = create_normal_facts()
        f["lymphocytes_abs"] = 5

        self.assertEqual(rules.rule_16(f)["rule_id"], "R16")

    # Rule 17
    def test_rule_17(self):
        f = create_normal_facts()
        f["eosinophils_abs"] = 0.7

        self.assertEqual(rules.rule_17(f)["rule_id"], "R17")

    # Rule 18
    def test_rule_18(self):
        f = create_normal_facts()
        f["monocytes_abs"] = 0.9

        self.assertEqual(rules.rule_18(f)["rule_id"], "R18")

    # Rule 19
    def test_rule_19(self):
        f = create_normal_facts()
        f["platelets"] = 100

        self.assertEqual(rules.rule_19(f)["rule_id"], "R19")

    # Rule 20
    def test_rule_20(self):
        f = create_normal_facts()
        f["platelets"] = 40

        self.assertEqual(rules.rule_20(f)["rule_id"], "R20")

    # Rule 21
    def test_rule_21(self):
        f = create_normal_facts()
        f["platelets"] = 10

        self.assertEqual(rules.rule_21(f)["rule_id"], "R21")

    # Rule 22
    def test_rule_22(self):
        f = create_normal_facts()
        f["platelets"] = 500

        self.assertEqual(rules.rule_22(f)["rule_id"], "R22")

    # Rule 23
    def test_rule_23(self):
        f = create_normal_facts()

        results = rules.rule_23(f)

        self.assertEqual(len(results), 4)

        self.assertTrue(
            all(item["rule_id"] == "R23" for item in results)
        )

        self.assertAlmostEqual(
            results[0]["details"]["calculated_value"],
            2.5
        )

    # Rule 24
    def test_rule_24(self):
        f = create_normal_facts()
        f["lymphocytes_pct"] = 50
        f["lymphocytes_abs"] = 2.5

        self.assertEqual(rules.rule_24(f)["rule_id"], "R24")

    # Rule 25
    def test_rule_25(self):
        f = create_normal_facts()
        f["neutrophils_pct"] = 75
        f["neutrophils_abs"] = 3.75

        self.assertEqual(rules.rule_25(f)["rule_id"], "R25")

    # Rule 26
    def test_rule_26(self):
        f = create_normal_facts()
        f.update({
            "hb": 11,
            "wbc": 3,
            "platelets": 100
        })

        self.assertEqual(rules.rule_26(f)["rule_id"], "R26")

    # Rule 27
    def test_rule_27(self):
        f = create_normal_facts()
        f.update({
            "hb": 11,
            "wbc": 3
        })

        self.assertEqual(rules.rule_27(f)["rule_id"], "R27")

    # Rule 28
    def test_rule_28(self):
        f = create_normal_facts()
        f["age"] = 17

        self.assertEqual(rules.rule_28(f)["rule_id"], "R28")

    # Rule 29
    def test_rule_29(self):
        f = create_normal_facts()
        f["hb"] = None

        self.assertEqual(rules.rule_29(f)["rule_id"], "R29")

    # Rule 30
    def test_rule_30(self):
        f = create_normal_facts()
        f["units_valid"] = False

        self.assertEqual(rules.rule_30(f)["rule_id"], "R30")


# --------------------------------------------------
# Negative Tests
# --------------------------------------------------

class TestRulesNotActivated(unittest.TestCase):

    def test_normal_values_do_not_activate_rules(self):

        f = create_normal_facts()

        for rule in rules.RULES:

            if rule.name == "rule_23":
                continue

            if rule.name == "rule_28":
                continue

            result = rule(f)

            self.assertIsNone(
                result,
                msg=f"{rule.name} activated unexpectedly"
            )

    def test_normal_age(self):

        f = create_normal_facts()

        self.assertIsNone(rules.rule_28(f))

    def test_complete_data(self):

        f = create_normal_facts()

        self.assertIsNone(rules.rule_29(f))

    def test_valid_units(self):

        f = create_normal_facts()

        self.assertIsNone(rules.rule_30(f))


# --------------------------------------------------
# Run All Tests
# --------------------------------------------------

if __name__ == "__main__":

    print("\nMED EXPERT - CBC RULES TESTING")
    print("=" * 45)

    unittest.main(verbosity=2)