import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.functional_registry import FunctionalRegistry
from rulegen.learning_protocol import evaluate_backend,compare_cold_warm

class LearningProtocolTests(unittest.TestCase):
    def test_legacy_preserved(self):
        with Registry(":memory:") as registry:
            result=evaluate_backend("legacy",[(1,1),(2,2)],registry,budget=20,max_nodes=1)
            self.assertTrue(result["solved"])
            self.assertEqual(result["backend"],"legacy")
            self.assertEqual(result["checks"],1)
    def test_legacy_goal_preserved(self):
        with Registry(":memory:") as registry:
            result=evaluate_backend("legacy-goal",[(1,1),(2,2)],registry,budget=20,max_nodes=1)
            self.assertTrue(result["solved"])
    def test_functional_protocol_and_accounting(self):
        with tempfile.TemporaryDirectory() as d:
            with FunctionalRegistry(Path(d)/"operators.db",tier="algebra") as registry:
                rows=[({"x":2},2),({"x":3},3)]
                report=compare_cold_warm("functional",rows,registry,budget=20,max_nodes=1,
                                         acquisition_checks=7)
                self.assertTrue(report["cold"]["solved"])
                self.assertTrue(report["warm"]["solved"])
                self.assertEqual(report["warm_checks_including_acquisition"],
                                 report["warm"]["checks"]+7)
                self.assertFalse(report["matched_total_budget"])
    def test_no_invented_acquisition_cost(self):
        with Registry(":memory:") as registry:
            report=compare_cold_warm("legacy",[(1,1)],registry,budget=10,max_nodes=1)
            self.assertIsNone(report["acquisition_checks"])
            self.assertIsNone(report["warm_checks_including_acquisition"])
    def test_reject_unknown_backend(self):
        with self.assertRaises(ValueError):
            evaluate_backend("other",[],None,budget=10)
if __name__=="__main__":unittest.main()
