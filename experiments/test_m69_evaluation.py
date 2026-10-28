"""Historical matched-budget experiment; intentionally not a CI capability contract."""
import unittest
from rulegen.evaluation import TASKS,evaluate
class M69Tests(unittest.TestCase):
 def test_splits_disjoint(self):
  for _,training,validation,_ in TASKS:
   self.assertFalse(set(map(repr,training)) & set(map(repr,validation)))
 def test_matched_budget_and_negative_controls(self):
  report=evaluate(budget=12,depth=5,seeds=(0,))
  self.assertEqual(report['summary']['cold']['tasks'],len(TASKS))
  self.assertEqual(report['summary']['warm']['tasks'],len(TASKS))
  self.assertTrue(any(not t['related'] for t in report['trials']))
  for trial in report['trials']:self.assertLessEqual(trial['checks'],12)
  self.assertEqual(report['warm_checks_including_acquisition'],
                   report['summary']['warm']['checks']+report['total_acquisition_checks'])
 def test_invalid_budget(self):
  with self.assertRaises(ValueError):evaluate(budget=0)
if __name__=='__main__':unittest.main()
