import json
import unittest
from rulegen.failure_diagnostics import diagnose_grid


class IncrementalCoverageTests(unittest.TestCase):
    def test_publish_comparable_diagnostics(self):
        report=diagnose_grid(seeds=(0,1,2),max_nodes=5,
                             budget=300,max_generated=300)
        self.assertEqual(sum(report["counts"].values()),12)
        print("INCREMENTAL_COVERAGE_JSON="+json.dumps(report["counts"],sort_keys=True),flush=True)
