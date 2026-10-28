"""Measured synthesis trials for the research allocation portfolio.

Each task has disjoint training and validation observations. The policy
selects a search-depth direction and a bounded real synthesis run determines
validated success. This is a toy-workload benchmark, not generalisation proof.
"""
import random
from .engine import Registry, execute
from .portfolio import Portfolio
from .session import synthesize_resumable

def run_trials(tasks, *, policy='adaptive', directions=(1,3,5),
               evaluations_per_trial=12, seed=13, db_path=':memory:'):
    if policy not in ('adaptive','round_robin','random'):
        raise ValueError('unknown allocation policy')
    if not tasks or evaluations_per_trial<1 or not directions:
        raise ValueError('nonempty tasks, directions and positive budget required')
    rng=random.Random(seed)
    portfolio=Portfolio(db_path)
    for depth in directions:
        if depth<1:raise ValueError('invalid depth')
        portfolio.register(str(depth))
    outcomes=[]
    try:
        for i,task in enumerate(tasks):
            training,validation=task
            if not training or not validation or set(map(repr,training)) & set(map(repr,validation)):
                raise ValueError('independent nonempty train/validation required')
            if policy=='adaptive':
                depth=int(portfolio.select()['direction'])
            elif policy=='round_robin':
                depth=directions[i%len(directions)]
            else:
                depth=rng.choice(directions)
            with Registry(':memory:') as registry:
                result=synthesize_resumable(registry,training,max_nodes=depth,
                                            budget=evaluations_per_trial,reuse=False)
                expression=result['program']
                passed=False
                if expression is not None:
                    try:passed=all(execute(expression,x)==y for x,y in validation)
                    except (TypeError,ValueError,IndexError,OverflowError,RecursionError):passed=False
            cost=max(1,result['checks'])
            portfolio.record(str(depth),cost,int(passed),validated=passed,
                             metadata={'task':i,'program':expression,'checks':result['checks'],
                                       'max_nodes':depth,'validation_passed':passed})
            outcomes.append({'task':i,'direction':depth,'checks':result['checks'],
                             'cost':cost,'solved':passed,'program':expression})
        return {'policy':policy,'trials':outcomes,'total_checks':sum(x['checks'] for x in outcomes),
                'total_cost':sum(x['cost'] for x in outcomes),
                'validated_solutions':sum(x['solved'] for x in outcomes),
                'portfolio':portfolio.report()}
    finally:
        portfolio.db.close()

def compare_real(tasks, **kwargs):
    return {policy:run_trials(tasks,policy=policy,**kwargs)
            for policy in ('adaptive','round_robin','random')}
