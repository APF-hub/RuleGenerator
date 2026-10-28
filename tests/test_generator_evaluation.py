import unittest
from rulegen.generator_evaluation import evaluate_generated_task, evaluate_grid


class GeneratorEvaluationTests(unittest.TestCase):
    def test_simple_arithmetic(self):
        report=evaluate_generated_task(42,family="arithmetic",complexity=1)
        self.assertEqual(report["generator_complexity"]["nodes"],3)
        self.assertTrue(report["training_solved"],report)
        self.assertEqual(report["heldout_accuracy"],1.0)
        self.assertFalse(report["semantic_equivalence_proven"])

    def test_pair(self):
        report=evaluate_generated_task(42,family="pair")
        self.assertEqual(report["generator_complexity"]["nodes"],5)
        self.assertTrue(report["training_solved"],report)
        self.assertEqual(report["heldout_accuracy"],1.0)

    def test_grid_preserves_failures(self):
        results=evaluate_grid(seeds=(0,),families=("arithmetic",),
                              arithmetic_levels=(1,2),max_nodes=3,
                              budget=100,max_generated=100)
        self.assertEqual(len(results),2)
        self.assertTrue(all("exhausted" in row for row in results))
