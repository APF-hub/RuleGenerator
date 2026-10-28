import tempfile
import unittest
from pathlib import Path
from rulegen.counterexample_learning import refine_with_counterexamples
from rulegen.engine import Registry, execute


class CounterexampleLearningTests(unittest.TestCase):
    def test_probe_consistent_simple_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/"db.sqlite") as registry:
                result=refine_with_counterexamples(
                    registry,[(1,2),(2,3)],[(3,4),(4,5)],
                    max_rounds=4,max_nodes=3,budget=100)
        self.assertTrue(result["probe_consistent"],result)
        self.assertFalse(result["independent_heldout_verified"])
        self.assertEqual(execute(result["program"],10),11)

    def test_reject_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/"db.sqlite") as registry:
                with self.assertRaisesRegex(ValueError,"overlapping"):
                    refine_with_counterexamples(registry,[(1,2)],[(1,2)])
