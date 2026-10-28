import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry, INT, BOOL, PAIR
from rulegen.typedholes import synthesize_goal

class EvidenceTests(unittest.TestCase):
    def test_verified_type_proof_survives_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'knowledge.sqlite'
            expression=['call','fst',['input']]
            with Registry(path) as r:
                self.assertFalse(r.evidence.can_prune(expression,INT,INT))
                self.assertTrue(r.evidence.prove_type_impossible(expression,INT,INT))
                self.assertTrue(r.evidence.can_prune(expression,INT,INT))
            with Registry(path) as r:
                self.assertTrue(r.evidence.can_prune(expression,INT,INT))
                self.assertFalse(r.evidence.can_prune(expression,PAIR(INT,BOOL),INT))
    def test_no_false_proof_for_valid_program(self):
        with Registry(':memory:') as r:
            expr=['input']
            self.assertFalse(r.evidence.prove_type_impossible(expr,INT,INT))
            self.assertFalse(r.evidence.can_prune(expr,INT,INT))
    def test_empirical_failure_never_proves_type_impossibility(self):
        with Registry(':memory:') as r:
            r.evidence.append('empirical_failure','observation-A',['input'],{'mismatch':True})
            self.assertFalse(r.evidence.can_prune(['input'],INT,INT))
            self.assertEqual(r.evidence.count('empirical_failure'),1)
    def test_mismatch_integrated_with_search(self):
        with Registry(':memory:') as r:
            synthesize_goal(r,[(1,2),(2,3)],max_nodes=3,budget=2)
            self.assertGreater(r.evidence.count('empirical_failure'),0)
            self.assertEqual(r.evidence.count('type_proof'),0)
    def test_reject_unknown_schema(self):
        with Registry(':memory:') as r:
            r.db.execute("UPDATE rg_metadata SET value='999' WHERE key='schema_version'")
            r.db.commit()
            from rulegen.evidence import Evidence
            with self.assertRaises(ValueError):Evidence(r.db)
if __name__=='__main__':unittest.main()
