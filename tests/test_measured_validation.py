import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry, INT
from rulegen.discovery import discover
from rulegen.learning_cycle import run_learning_cycle

class MeasuredValidationTests(unittest.TestCase):
    def test_rejected_admission_counts_actual_executions(self):
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/'db.sqlite') as registry:
                counter={'attempted':0}
                accepted=registry.admit('identity',['arg',0],[INT],INT,
                    [([1],1)],[([2],999)],execution_counter=counter)
                self.assertFalse(accepted)
                self.assertEqual(counter['attempted'],2)
                self.assertEqual(registry.active(),{})
    def test_learning_cycle_exposes_measured_work_units(self):
        train=[((1,True),(True,1)),((2,False),(False,2)),((3,True),(True,3))]
        valid=[(([1,2],False),(False,[1,2])),((False,[3,4]),([3,4],False))]
        reuse=[((4,False),(False,4)),((7,True),(True,7))]
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/'db.sqlite') as registry:
                result=run_learning_cycle(registry,'swap',train,valid,reuse)
                self.assertTrue(result['admitted'],result)
                self.assertEqual(result['validation_execution_count'],5)
                self.assertEqual(result['acquisition_work_units'],result['acquisition_checks']+5)
                self.assertEqual(result['warm_work_units_including_acquisition'],result['acquisition_work_units']+result['warm']['checks'])
