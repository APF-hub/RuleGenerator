"""Publish bounded, reproducible complexity experiment measurements in CI."""
import json
import unittest
from rulegen.complexity_grid import evaluate_complexity_grid


class ComplexityResultsTests(unittest.TestCase):
    def test_publish_bounded_grid(self):
        result=evaluate_complexity_grid(
            seeds=(0,1,2),arithmetic_levels=(1,2,3),
            include_pair=True,max_nodes=5,budget=300,
            max_generated=300,target_tasks=2)
        self.assertEqual(len(result["records"]),12)
        self.assertEqual(len(result["summary"]),4)
        print("COMPLEXITY_GRID_JSON="+json.dumps({
            "configuration":{"seeds":[0,1,2],"max_nodes":5,
                             "budget":300,"max_generated":300,
                             "target_tasks":2},
            "summary":result["summary"],
            "trials":[{"family":r["family"],"level":r["construction_complexity"],
                       "seed":r["seed"],"admitted":r["admitted"],
                       "learned_nodes":(r["learned_body_complexity"] or {}).get("nodes"),
                       "heldout_accuracy":r["heldout_accuracy"],
                       "acquisition_work_units":r["acquisition_work_units"],
                       "break_even_target":r["break_even_target"]}
                      for r in result["records"]],
        },sort_keys=True),flush=True)
