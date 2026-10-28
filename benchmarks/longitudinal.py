"""M68 longitudinal transfer evaluation: cold vs learned-operator library.

Acquisition is reported separately from marginal reuse cost. The comparison
uses identical task observations and search budgets, not estimated future value.
"""
import json
from rulegen.engine import Registry, synthesize, execute
from rulegen.discovery import discover

TRAIN=[((1,True),(True,1)),((2,False),(False,2))]
VALIDATE=[(([1,2],False),(False,[1,2]))]
TASKS=[
    ([( (3,True),(True,3) ),( (4,False),(False,4) )],
     [((5,True),(True,5))]),
    ([( (False,[3,4]),([3,4],False) )],
     [((True,[5,6]),([5,6],True))]),
    ([( (7,False),(False,7) )],
     [((8,True),(True,8))]),
]

def evaluate(max_nodes=5,budget=10000):
    with Registry(':memory:') as warm, Registry(':memory:') as cold:
        acquisition=discover(warm,'swap',TRAIN,VALIDATE,max_nodes=max_nodes,budget=budget)
        results=[]
        for training,held_out in TASKS:
            baseline=synthesize(cold,training,max_nodes=max_nodes,budget=budget,reuse=False)
            reused=synthesize(warm,training,max_nodes=max_nodes,budget=budget,reuse=True)
            def held_out_passes(out,operators):
                if out['program'] is None:return False
                try:return all(execute(out['program'],x,operators)==y for x,y in held_out)
                except (ValueError,TypeError,IndexError,OverflowError,RecursionError):return False
            results.append({
                'baseline_checks':baseline['checks'],
                'reuse_checks':reused['checks'],
                'baseline_valid':held_out_passes(baseline,{}),
                'reuse_valid':held_out_passes(reused,warm.active()),
                'baseline_program':baseline['program'],
                'reuse_program':reused['program'],
            })
        return {
            'operator_admitted':acquisition['admitted'],
            'acquisition_checks':acquisition['checks'],
            'tasks':results,
            'cold_checks':sum(r['baseline_checks'] for r in results),
            'warm_marginal_checks':sum(r['reuse_checks'] for r in results),
            'warm_plus_acquisition_checks':acquisition['checks']+sum(r['reuse_checks'] for r in results),
            'note':'Candidate checks only; wall time, memory and storage excluded.'
        }

if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
