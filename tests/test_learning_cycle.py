import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.learning_cycle import run_learning_cycle

class LearningCycleTests(unittest.TestCase):
    def test_discover_and_reuse(self):
        train=[((1,True),(True,1)),((2,False),(False,2)),((3,True),(True,3))]
        valid=[(([1,2],False),(False,[1,2])),((False,[3,4]),([3,4],False))]
        reuse=[((4,False),(False,4)),((7,True),(True,7))]
        with tempfile.TemporaryDirectory() as d:
            with Registry(Path(d)/'lib.db') as r:
                result=run_learning_cycle(r,'swap',train,valid,reuse)
                self.assertTrue(result['admitted'],result)
                self.assertIn('swap',r.active())
                self.assertIsNotNone(result['warm']['program'])
                self.assertEqual(result['warm_checks_including_acquisition'],result['acquisition_checks']+result['warm']['checks'])
                self.assertFalse(result['matched_total_budget'])
    def test_split_leakage(self):
        train=[((1,True),(True,1))]
        valid=[((2,False),(False,2))]
        reuse=[((1,True),(False,999))]
        with tempfile.TemporaryDirectory() as d:
            with Registry(Path(d)/'lib.db') as r:
                with self.assertRaisesRegex(ValueError,'overlap'):
                    run_learning_cycle(r,'swap',train,valid,reuse)
                self.assertNotIn('swap',r.active())
