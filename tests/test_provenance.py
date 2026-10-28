import unittest
from rulegen.provenance import Observation,verify_splits,acquisition_report

class ProvenanceTests(unittest.TestCase):
    def test_disjoint_manifest(self):
        result=verify_splits([
            Observation("source-a","train",[1],2),
            Observation("source-b","validation",[2],3),
            Observation("source-c","test",[3],4)])
        self.assertEqual(result["split_counts"],{"train":1,"validation":1,"test":1})
        self.assertEqual(result["provenance"],"caller_declared_unverified")
        self.assertEqual(len(result["manifest_digest"]),64)
    def test_reject_same_source_across_splits(self):
        with self.assertRaises(ValueError):
            verify_splits([Observation("source-a","train",[1],2),
                           Observation("source-a","validation",[2],3)])
    def test_reject_same_inputs_across_splits(self):
        with self.assertRaises(ValueError):
            verify_splits([Observation("a","train",[1],2),
                           Observation("b","validation",[1],2)])
    def test_acquisition_counts(self):
        report=acquisition_report(proposal_checks=4,validation_checks=3,search_checks=8)
        self.assertEqual(report["acquisition_checks"],7)
        self.assertEqual(report["total_checks"],15)
        with self.assertRaises(ValueError):
            acquisition_report(proposal_checks=-1,validation_checks=0,search_checks=1)

if __name__=="__main__":unittest.main()
