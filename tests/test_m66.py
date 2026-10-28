import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.session import synthesize_resumable

class SessionTests(unittest.TestCase):
    def test_resume_matches_uninterrupted(self):
        rows=[((1,True),(True,1)),((2,False),(False,2))]
        with tempfile.TemporaryDirectory() as d:
            r=Registry(Path(d)/'a.db')
            a=synthesize_resumable(r,rows,budget=1)
            self.assertFalse(a['done'])
            self.assertEqual(a['checks'],1)
            r.db.close()
            r=Registry(Path(d)/'a.db')
            b=synthesize_resumable(r,rows,budget=200)
            self.assertTrue(b['done'])
            self.assertIsNotNone(b['program'])
            r.db.close()
            other=Registry(Path(d)/'b.db')
            baseline=synthesize_resumable(other,rows,budget=200)
            self.assertEqual(b['program'],baseline['program'])
            self.assertEqual(b['total_checks'],baseline['total_checks'])
            other.db.close()
    def test_observation_scope_and_completed_cache(self):
        with tempfile.TemporaryDirectory() as d:
            r=Registry(Path(d)/'a.db')
            first=synthesize_resumable(r,[(1,1)],budget=3)
            second=synthesize_resumable(r,[(1,1)],budget=3)
            changed=synthesize_resumable(r,[(1,2)],budget=3)
            self.assertTrue(first['done'])
            self.assertEqual(second['checks'],0)
            self.assertEqual(changed['cursor'],changed['checks'])
            r.db.close()
    def test_invalid_budget(self):
        with tempfile.TemporaryDirectory() as d:
            r=Registry(Path(d)/'a.db')
            with self.assertRaises(ValueError):synthesize_resumable(r,[(1,1)],budget=-1)
            r.db.close()
if __name__=='__main__':unittest.main()
