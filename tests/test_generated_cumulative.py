import unittest
from rulegen.generated_cumulative import evaluate_generated_cumulative


class GeneratedCumulativeTests(unittest.TestCase):
    def test_pair_reuse_and_heldout(self):
        result=evaluate_generated_cumulative(42,family="pair")
        self.assertTrue(result["admitted"],result)
        self.assertEqual(result["generator_complexity"]["nodes"],5)
        self.assertEqual(result["heldout_accuracy"],1.0)
        self.assertEqual(len(result["history"]),2)
        self.assertEqual(result["admission_executions"],5)
        self.assertFalse(result["matched_total_budget"])
        self.assertFalse(result["semantic_equivalence_proven"])

    def test_arithmetic_reports_failure_or_success(self):
        result=evaluate_generated_cumulative(7,family="arithmetic",complexity=2,
                                              max_nodes=3,budget=100,max_generated=100)
        self.assertEqual(result["generator_complexity"]["nodes"],5)
        self.assertIn("admitted",result)
        self.assertEqual(result["heldout_total"],4)
        if not result["admitted"]:
            self.assertIsNone(result["history"])
            self.assertIsNone(result["heldout_accuracy"])

    def test_invalid_target_count(self):
        with self.assertRaises(ValueError):
            evaluate_generated_cumulative(1,target_tasks=0)
