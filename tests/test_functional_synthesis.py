import tempfile
import unittest
from pathlib import Path
from rulegen.abstraction import propose
from rulegen.functional_registry import FunctionalRegistry
from rulegen.functional_synthesis import synthesize_functional,call,literal

class FunctionalSynthesisTests(unittest.TestCase):
    def test_learned_operator_unlocks_bounded_search(self):
        a=call("+",literal(3),literal(1))
        b=call("+",literal(5),literal(1))
        candidate=propose("increment",[(a,{}),(b,{})])
        with tempfile.TemporaryDirectory() as d:
            with FunctionalRegistry(Path(d)/"lib.db",tier="algebra") as registry:
                registry.promote(candidate,[([3],4)],[([5],6)])
                rows=[({"x":7},8),({"x":9},10)]
                cold=synthesize_functional(rows,registry,tier="algebra",
                                            max_nodes=2,budget=100,reuse=False)
                warm=synthesize_functional(rows,registry,tier="algebra",
                                            max_nodes=2,budget=100,reuse=True)
                self.assertIsNone(cold["program"])
                self.assertEqual(warm["program"]["name"],"increment")
                self.assertEqual(warm["program"]["args"],[{"op":"var","name":"x"}])
    def test_budget_and_types(self):
        rows=[({"x":3},5),({"x":4},6)]
        result=synthesize_functional(rows,tier="algebra",max_nodes=3,budget=1)
        self.assertTrue(result["exhausted"])
        self.assertEqual(result["checks"],1)
        with self.assertRaises(TypeError):
            synthesize_functional([({"x":1},2),({"x":True},3)])

if __name__=="__main__":unittest.main()
