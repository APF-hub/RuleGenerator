"""M69: matched-budget synthesis transfer evaluation, with unrelated controls."""
import random
import time
import tracemalloc
from .engine import Registry, execute
from .discovery import discover
from .session import synthesize_resumable

ACQUISITION_TRAIN=[((1,True),(True,1)),((2,False),(False,2))]
ACQUISITION_VALIDATION=[(([1,2],False),(False,[1,2]))]
TASKS=[
 ('swap_int_bool',[((3,True),(True,3)),((4,False),(False,4))],[((5,True),(True,5))],True),
 ('swap_list_bool',[((False,[3,4]),([3,4],False))],[((True,[5,6]),([5,6],True))],True),
 ('swap_bool_int',[((True,7),(7,True)),((False,8),(8,False))],[((True,9),(9,True))],True),
 ('identity_int',[(11,11),(12,12)],[(13,13)],False),
 ('identity_bool',[(True,True)],[(False,False)],False),
 ('increment_int',[(10,11),(20,21)],[(30,31)],False),
 ('fst_pair',[((10,True),10),((20,False),20)],[((30,True),30)],False),
 ('snd_pair',[((10,True),True),((20,False),False)],[((30,True),True)],False),
 ('eq_pair',[((10,10),True),((10,11),False)],[((12,12),True),((12,13),False)],False),
]
def _valid(expr,observations,operators):
    if expr is None:return False
    try:return all(execute(expr,x,operators)==y for x,y in observations)
    except (TypeError,ValueError,IndexError,RecursionError,OverflowError):return False

def evaluate(*,budget=100,depth=5,seeds=(0,1,2),tasks=TASKS):
    if budget<1 or depth<1 or not seeds:raise ValueError('positive budget/depth and nonempty seeds required')
    results=[]
    tracemalloc.start()
    try:
        for seed in seeds:
            ordered=list(tasks)
            random.Random(seed).shuffle(ordered)
            with Registry(':memory:') as warm:
                acquisition=discover(warm,'swap',ACQUISITION_TRAIN,ACQUISITION_VALIDATION,
                                     max_nodes=depth,budget=10000)
                if not acquisition['admitted']:raise RuntimeError('operator acquisition failed')
                for name,train,validation,related in ordered:
                    if not train or not validation or set(map(repr,train)) & set(map(repr,validation)):
                        raise ValueError('train/validation overlap')
                    for mode in ('cold','warm'):
                        with Registry(':memory:') as registry:
                            if mode=='warm':
                                record=warm.db.execute('SELECT * FROM operators WHERE name=?',('swap',)).fetchone()
                                registry.db.execute('INSERT INTO operators VALUES(?,?,?,?,?,?)',record)
                                registry.db.commit()
                            start=time.perf_counter()
                            outcome=synthesize_resumable(registry,train,max_nodes=depth,
                                                         budget=budget,reuse=(mode=='warm'))
                            elapsed=time.perf_counter()-start
                            passed=_valid(outcome['program'],validation,
                                          registry.active() if mode=='warm' else {})
                            results.append(dict(seed=seed,task=name,related=related,mode=mode,
                                                checks=outcome['checks'],passed=passed,
                                                found=outcome['program'] is not None,
                                                elapsed_seconds=elapsed,program=outcome['program']))
        _,peak=tracemalloc.get_traced_memory()
    finally:tracemalloc.stop()
    summary={}
    for mode in ('cold','warm'):
        subset=[r for r in results if r['mode']==mode]
        summary[mode]=dict(tasks=len(subset),validated=sum(r['passed'] for r in subset),
                           checks=sum(r['checks'] for r in subset),
                           wall_seconds=sum(r['elapsed_seconds'] for r in subset),
                           related_validated=sum(r['passed'] for r in subset if r['related']),
                           unrelated_validated=sum(r['passed'] for r in subset if not r['related']))
    return dict(config=dict(budget_per_task=budget,depth=depth,seeds=list(seeds),
                            tasks_per_seed=len(tasks),matched_per_task_budget=True),
                acquisition_checks_per_seed=acquisition['checks'],
                total_acquisition_checks=acquisition['checks']*len(seeds),
                summary=summary,
                warm_checks_including_acquisition=summary['warm']['checks']+acquisition['checks']*len(seeds),
                peak_python_traced_bytes=peak,trials=results,
                caveats=['Tracemalloc tracks Python allocations, not process RSS.',
                         'Candidate checks exclude enumeration/typechecking cost.',
                         'Seeds reorder the same tasks, not independent task draws.'])
