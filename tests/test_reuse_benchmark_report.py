"""Print actual benchmark measurements in CI; no performance pass threshold."""
import json
import tempfile
import unittest
from pathlib import Path

from rulegen.cumulative_experiment import run_reuse_experiment
from rulegen.engine import Registry


class ReuseBenchmarkReport(unittest.TestCase):
    def test_publish_observed_checks(self):
        training=[((1,True),(True,1)),((2,False),(False,2)),((3,True),(True,3))]
        validation=[(([1,2],False),(False,[1,2])),((False,[3,4]),([3,4],False))]
        targets=[
            [((4,False),(False,4)),((7,True),(True,7))],
            [((8,True),(True,8)),((9,False),(False,9))],
        ]
        with tempfile.TemporaryDirectory() as directory:
            with Registry(Path(directory)/"benchmark.sqlite") as registry:
                report=run_reuse_experiment(registry,"swap",training,validation,targets)
        summary={
            "experiment":"pair_swap_two_targets_v1",
            "training_examples":len(training),
            "validation_examples":len(validation),
            "target_tasks":len(targets),
            "admitted":report["admitted"],
            "acquisition_checks":report["acquisition_checks"],
            "admission_executions":report["admission_executions"],
            "acquisition_work_units":report["acquisition_work_units"],
            "history":report.get("history"),
            "break_even_target":report["break_even_target"],
            "matched_total_budget":report["matched_total_budget"],
            "unit":"heterogeneous candidate checks + admission executions",
        }
        print("REUSE_BENCHMARK_JSON="+json.dumps(summary,sort_keys=True),flush=True)
        self.assertTrue(report["admitted"])
        self.assertEqual(len(report["history"]),2)
