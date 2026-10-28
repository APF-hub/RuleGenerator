import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.functional_registry import FunctionalRegistry
from rulegen.learning_protocol import evaluate_backend

class UnifiedGenerationContractTests(unittest.TestCase):
    def test_legacy_backends(self):
        with Registry(':memory:') as lib:
            for backend in ('legacy','legacy-goal'):
                with self.subTest(backend=backend):
                    report=evaluate_backend(backend,[(1,1),(2,2)],lib,budget=20,max_nodes=1,max_generated=10)
                    self.assertTrue(report['solved'])
                    self.assertEqual(report['max_generated'],10)
    def test_functional_backend(self):
        with tempfile.TemporaryDirectory() as d:
            with FunctionalRegistry(Path(d)/'lib.db',tier='algebra') as lib:
                report=evaluate_backend('functional',[({'x':2},2)],lib,budget=20,max_nodes=1,max_generated=10)
                self.assertTrue(report['solved'])
    def test_invalid_generation_limit(self):
        with Registry(':memory:') as lib:
            with self.assertRaises(ValueError):
                evaluate_backend('legacy',[(1,1)],lib,budget=20,max_generated=0)
