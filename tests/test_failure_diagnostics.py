import json
import unittest
from rulegen.failure_diagnostics import diagnose_grid, diagnose_generated_task


class FailureDiagnosticsTests(unittest.TestCase):
    def test_structural_limit_is_explicit(self):
        result=diagnose_generated_task(0,complexity=3,max_nodes=5,
                                       budget=300,max_generated=300)
        self.assertEqual(result["failure_category"],"generator_exceeds_max_nodes")
        self.assertEqual(result["generator_nodes"],7)

    def test_publish_diagnostic_distribution(self):
        report=diagnose_grid()
        self.assertEqual(sum(report["counts"].values()),12)
        print("FAILURE_DIAGNOSTICS_JSON="+json.dumps(report,sort_keys=True),flush=True)
