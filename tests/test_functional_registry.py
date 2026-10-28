import math
import tempfile
import unittest
from pathlib import Path
from rulegen.abstraction import propose
from rulegen.functional_registry import FunctionalRegistry

def lit(v):return {"op":"literal","value":v}
def call(name,*args):return {"op":"call","name":name,"args":list(args)}

class FunctionalRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"operators.sqlite"
        a=call("*",lit(0.4),call("sin",call("*",lit(2.0),lit(0.5))))
        b=call("*",lit(0.7),call("sin",call("*",lit(3.0),lit(0.5))))
        self.candidate=propose("wave",[(a,{}),(b,{})])
    def tearDown(self):self.tmp.cleanup()
    def test_promote_reload_and_reuse(self):
        with FunctionalRegistry(self.path) as registry:
            evidence=registry.promote(self.candidate,
                [([0.4,2.0],0.4*math.sin(1.0))],
                [([0.8,5.0],0.8*math.sin(2.5))])
            self.assertEqual(evidence["validation_count"],1)
        with FunctionalRegistry(self.path) as registry:
            self.assertIn("wave",registry.active())
            actual=registry.core().execute(call("wave",lit(0.3),lit(6.0)))
            self.assertAlmostEqual(actual,0.3*math.sin(3.0))
            registry.retire("wave")
            self.assertNotIn("wave",registry.active())
    def test_reject_overlapping_evidence(self):
        with FunctionalRegistry(self.path) as registry:
            with self.assertRaises(ValueError):
                registry.promote(self.candidate,
                    [([0.4,2.0],0.4*math.sin(1))],
                    [([0.4,2.0],0.4*math.sin(1))])
            self.assertFalse(registry.active())
    def test_reject_wrong_validation(self):
        with FunctionalRegistry(self.path) as registry:
            with self.assertRaises(ValueError):
                registry.promote(self.candidate,
                    [([0.4,2.0],0.4*math.sin(1))],
                    [([0.8,5.0],99.0)])
            self.assertFalse(registry.active())

if __name__=="__main__":unittest.main()
