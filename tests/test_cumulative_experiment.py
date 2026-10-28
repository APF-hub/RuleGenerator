import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.cumulative_experiment import run_reuse_experiment


class CumulativeExperimentTests(unittest.TestCase):
    def data(self):
        training=[((1,True),(True,1)),((2,False),(False,2)),((3,True),(True,3))]
        validation=[(([1,2],False),(False,[1,2])),((False,[3,4]),([3,4],False))]
        targets=[
            [((4,False),(False,4)),((7,True),(True,7))],
            [((8,True),(True,8)),((9,False),(False,9))],
        ]
        return training,validation,targets

    def test_repeated_reuse_and_accounting(self):
        train,valid,targets=self.data()
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/"db.sqlite") as registry:
                report=run_reuse_experiment(registry,"swap",train,valid,targets)
                self.assertTrue(report["admitted"],report)
                self.assertEqual(len(report["history"]),2)
                self.assertEqual(report["admission_executions"],5)
                self.assertEqual(report["acquisition_work_units"],
                                 report["acquisition_checks"]+5)
                self.assertEqual(report["history"][0]["cumulative_warm_work_units"],
                                 report["acquisition_work_units"]+report["warm"][0]["checks"])
                self.assertFalse(report["matched_total_budget"])

    def test_cross_task_leakage_rejected_before_promotion(self):
        train,valid,targets=self.data()
        targets[1][0]=targets[0][0]
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/"db.sqlite") as registry:
                with self.assertRaisesRegex(ValueError,"overlap"):
                    run_reuse_experiment(registry,"swap",train,valid,targets)
                self.assertEqual(registry.active(),{})
