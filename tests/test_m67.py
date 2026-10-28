import unittest
from rulegen.engine import Registry,V
from rulegen.trials import run_trials,compare_real
from rulegen.session import synthesize_resumable

TASKS=[
 ([(1,1),(2,2)],[(3,3),(4,4)]),
 ([(1,2),(2,3)],[(3,4),(4,5)]),
 ([((1,True),(True,1)),((2,False),(False,2))],
  [((3,True),(True,3)),((4,False),(False,4))]),
 ([((True,False),(False,True))],[((False,True),(True,False))]),
]
class M67Tests(unittest.TestCase):
 def test_real_trials_deterministic(self):
  a=compare_real(TASKS,directions=(1,3,5),evaluations_per_trial=12,seed=11)
  b=compare_real(TASKS,directions=(1,3,5),evaluations_per_trial=12,seed=11)
  self.assertEqual(a,b)
  for p in a.values():
   self.assertEqual(len(p['trials']),len(TASKS))
   self.assertEqual(p['total_checks'],sum(t['checks'] for t in p['trials']))
   self.assertEqual(p['validated_solutions'],sum(t['solved'] for t in p['trials']))
 def test_no_validation_leak(self):
  r=run_trials([([(1,1),(2,2)],[(3,4)])],directions=(1,),evaluations_per_trial=10)
  self.assertEqual(r['validated_solutions'],0)
 def test_reject_overgeneral_operator(self):
  with Registry(':memory:') as r:
   with self.assertRaises(TypeError):
    r.admit('unsound',['arg',0],[V('a')],V('b'),
            [([1],1)],[([True],True)])
 def test_valid_identity_operator(self):
  with Registry(':memory:') as r:
   self.assertTrue(r.admit('id',['arg',0],[V('a')],V('a'),
                            [([1],1)],[([True],True)]))
 def test_checkpoint_zero_budget(self):
  with Registry(':memory:') as r:
   out=synthesize_resumable(r,[(1,2)],budget=0)
   self.assertEqual(out['checks'],0)
   self.assertEqual(out['cursor'],0)
 def test_disjoint_validation(self):
  with self.assertRaises(ValueError):
   run_trials([([(1,1)],[(1,1)])])
if __name__=='__main__':unittest.main()
