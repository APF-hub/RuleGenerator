from .cancellation import check_cancel, make_deadline
"""Goal-directed typed-hole enumeration with constraint propagation.

Every partial expression carries a required output type. Unification prunes
impossible operator signatures before constructing children. The primitive
basis remains an explicit inductive bias, not a learned operator grammar.
"""
from itertools import count

class GenerationLimitReached(Exception):
    """Candidate construction reached the configured cap."""

from .engine import PRIMS, V, typ, fresh, unify, substitute, typecheck, encode


def enumerate_goal(goal, input_type, operators=None, max_nodes=5, max_generated=10000, cancel=None, deadline=None):
    if type(max_nodes) is not int or max_nodes<1 or type(max_generated) is not int or max_generated<1:
        raise ValueError('positive integer limits required')
    operators = operators or {}
    serial=count()
    stats={'type_pruned':0,'expanded_holes':0,'generated':0}
    def consume():
        check_cancel(cancel,deadline)
        if stats['generated']>=max_generated:
            raise GenerationLimitReached()
        stats['generated']+=1
    def build(required, size, subst):
        check_cancel(cancel,deadline)
        stats['expanded_holes']+=1
        required=substitute(required,subst)
        if size==1:
            leaves=[(['input'],input_type),(['const',0],typ(0)),(['const',1],typ(1)),
                    (['const',True],typ(True)),(['const',False],typ(False))]
            for e,t in leaves:
                try:
                    s=unify(required,t,subst)
                    consume()
                    yield e,s
                except TypeError:stats['type_pruned']+=1
            return
        signatures={n:(v[0],v[1]) for n,v in PRIMS.items()}
        signatures.update({n:(v['args'],v['out']) for n,v in operators.items()})
        for name,(arguments,output) in signatures.items():
            arity=len(arguments)
            if arity>size-1:continue
            args,out=fresh((arguments,output),'h'+str(next(serial)))
            try:s=unify(required,out,subst)
            except TypeError:
                stats['type_pruned']+=1
                continue
            def partitions(total,k):
                if k==0:
                    if total==0:yield ()
                else:
                    for n in range(1,total-k+2):
                        for tail in partitions(total-n,k-1):yield (n,)+tail
            for sizes in partitions(size-1,arity):
                def children(i,chosen,state):
                    if i==arity:
                        consume()
                        yield ['call',name,*chosen],state
                        return
                    for e,s2 in build(substitute(args[i],state),sizes[i],state):
                        yield from children(i+1,chosen+[e],s2)
                yield from children(0,[],s)
    def iterator():
        seen=set()
        for size in range(1,max_nodes+1):
            for e,_ in build(goal,size,{}):
                k=encode(e)
                if k in seen:continue
                seen.add(k)
                # Independent full-expression check guards partial inference.
                try:unify(typecheck(e,input_type,operators),goal)
                except TypeError:
                    stats['type_pruned']+=1
                    continue
                yield e
    return iterator(),stats


def synthesize_goal(registry,rows,max_nodes=5,budget=10000,reuse=True,max_generated=10000,cancel=None,timeout_seconds=None):
    """Find first matching program, retaining sound observation-scoped failures."""
    from .engine import execute,hash_of
    if not rows:raise ValueError('no observations')
    if type(budget) is not int or budget<1:
        raise ValueError('positive integer budget required')
    deadline=make_deadline(timeout_seconds)
    check_cancel(cancel,deadline)
    ti,to=typ(rows[0][0]),typ(rows[0][1]);scope=hash_of(['typedholes-v1',rows])
    ops=registry.active() if reuse else {}
    candidates,stats=enumerate_goal(to,ti,ops,max_nodes,max_generated,cancel,deadline)
    try:
        return _evaluate_candidates(candidates,stats,registry,scope,rows,ops,budget,cancel,deadline)
    except GenerationLimitReached:
        return {'program':None,'checks':stats.get('checks',0),'failure_skips':stats.get('skips',0),'exhausted':True,'stats':stats}

def _evaluate_candidates(candidates,stats,registry,scope,rows,ops,budget,cancel,deadline):
    from .engine import execute
    checks=skips=0
    for e in candidates:
        check_cancel(cancel,deadline)
        stats['checks']=checks
        stats['skips']=skips
        if registry.failed(scope,e):
            skips+=1
            stats['skips']=skips
            continue
        if checks>=budget:return {'program':None,'checks':checks,'failure_skips':skips,'exhausted':True,'stats':stats}
        checks+=1
        stats['checks']=checks
        try:good=all(execute(e,x,ops)==y for x,y in rows)
        except (ValueError,TypeError,IndexError,RecursionError,OverflowError):good=False
        if good:return {'program':e,'checks':checks,'failure_skips':skips,'exhausted':False,'stats':stats}
        registry.record_failure(scope,e,'empirical mismatch: scope only')
        registry.evidence.append('empirical_failure',scope,e,{'reason':'observation mismatch','schema':1})
    return {'program':None,'checks':checks,'failure_skips':skips,'exhausted':False,'stats':stats}
