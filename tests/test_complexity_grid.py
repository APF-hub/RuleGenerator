import unittest
from rulegen.complexity_grid import evaluate_complexity_grid


class ComplexityGridTests(unittest.TestCase):
    def test_grid_and_failure_denominators(self):
        report=evaluate_complexity_grid(seeds=(0,),arithmetic_levels=(1,2),
                                        include_pair=False,max_nodes=3,
                                        budget=100,max_generated=100)
        self.assertEqual(len(report["records"]),2)
        self.assertEqual(len(report["summary"]),2)
        self.assertEqual([s["generator_nodes"] for s in report["summary"]],[3,5])
        for row in report["summary"]:
            self.assertEqual(row["trials"],1)
            self.assertLessEqual(row["fully_heldout_correct"],row["admitted"])
            self.assertLessEqual(row["break_even_trials"],row["fully_heldout_correct"])
        self.assertFalse(report["cross_rule_transfer_tested"])

    def test_duplicate_seed_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            evaluate_complexity_grid(seeds=(1,1))
