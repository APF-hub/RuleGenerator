import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.functional_registry import FunctionalRegistry
from rulegen.learning_protocol import evaluate_backend,compare_matched_total_budget

class BudgetContractTests(unittest.TestCase):
    def test_reject_noninteger_limits(self):
        with Registry(":memory:") as lib:
            for budget,nodes in ((0,1),(True,1),(1.5,1),(1,0),(1,True)):
                with self.subTest(budget=budget,nodes=nodes):
                    with self.assertRaises(ValueError):
                        evaluate_backend("legacy",[(1,1)],lib,budget=budget,max_nodes=nodes)

    def test_matched_budget_deducts_acquisition(self):
        with tempfile.TemporaryDirectory() as d:
            with FunctionalRegistry(Path(d)/"lib.db",tier="algebra") as lib:
                rows=[({"x":2},2),({"x":3},3)]
                report=compare_matched_total_budget(
                    "functional",rows,lib,total_budget=12,acquisition_checks=4,max_nodes=1)
                self.assertEqual(report["cold"]["budget"],12)
                self.assertEqual(report["warm"]["budget"],8)
                self.assertLessEqual(report["warm_checks_including_acquisition"],12)
                self.assertTrue(report["matched_total_budget"])
                self.assertFalse(report["acquisition_measured"])

    def test_acquisition_consumes_all_budget(self):
        with Registry(":memory:") as lib:
            report=compare_matched_total_budget(
                "legacy",[(1,1)],lib,total_budget=3,acquisition_checks=3,max_nodes=1)
            self.assertIsNone(report["warm"])
            self.assertEqual(report["warm_search_budget"],0)
            self.assertEqual(report["warm_unavailable_reason"],"acquisition_exhausted_total_budget")

    def test_invalid_acquisition_rejected(self):
        with Registry(":memory:") as lib:
            for value in (-1,True,1.5):
                with self.assertRaises(ValueError):
                    compare_matched_total_budget("legacy",[(1,1)],lib,total_budget=3,
                                                 acquisition_checks=value,max_nodes=1)

if __name__=="__main__":unittest.main()
