import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.learning_cycle import run_manifest_learning_cycle
from rulegen.provenance import Observation


def manifest():
    return [
        Observation("train-a","train",(1,True),(True,1)),
        Observation("train-b","train",(2,False),(False,2)),
        Observation("train-c","train",(3,True),(True,3)),
        Observation("valid-a","validation",([1,2],False),(False,[1,2])),
        Observation("valid-b","validation",(False,[3,4]),([3,4],False)),
        Observation("test-a","test",(4,False),(False,4)),
        Observation("test-b","test",(7,True),(True,7)),
    ]


class ManifestLearningCycleTests(unittest.TestCase):
    def test_manifest_promotion_and_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/"db.sqlite") as registry:
                result=run_manifest_learning_cycle(registry,"swap",manifest())
                self.assertTrue(result["admitted"],result)
                self.assertIn("swap",registry.active())
                self.assertEqual(result["manifest"]["split_counts"],
                                 {"train":3,"validation":2,"test":2})
                self.assertFalse(result["promotion_provenance_verified"])
                self.assertEqual(result["provenance"],"caller_declared_unverified")

    def test_reused_source_fails_before_registry_mutation(self):
        observations=manifest()
        observations[-1]=Observation("train-a","test",(7,True),(True,7))
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/"db.sqlite") as registry:
                with self.assertRaisesRegex(ValueError,"leakage"):
                    run_manifest_learning_cycle(registry,"swap",observations)
                self.assertEqual(registry.active(),{})

    def test_missing_split_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with Registry(Path(tmp)/"db.sqlite") as registry:
                with self.assertRaisesRegex(ValueError,"required"):
                    run_manifest_learning_cycle(registry,"swap",manifest()[:-2])
                self.assertEqual(registry.active(),{})
