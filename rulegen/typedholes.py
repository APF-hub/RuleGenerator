"""Goal-directed typed-hole enumeration with constraint propagation.

Every partial expression carries a required output type. Unification prunes
impossible operator signatures before constructing children. The primitive
basis remains an explicit inductive bias, not a learned operator grammar.
"""
from itertools import count
from .engine import PRIMS, V, typ, fresh, unify, substitute, typecheck, encode


def enumerate_goal(goal, input_type, operators=None, max_nodes=5):
    operators = operators or {}
    serial=count()
    stats={'type_pruned':0,'expanded_holes':0,'generated':0}
    def build(required, size, subst):
        stats['expanded_holes']+=1
        required=substitute(required,subst)
        if size==1:
            leaves=[(['input'],input_type),(['const',0],typ(0)),(['const',1],typ(1)),
                    (['const',True],typ(True)),(['const',False],typ(False))]
            for e,t in leaves:
                try:
                    s=unify(required,t,subst)
                    stats['generated']+=1
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
                        stats['generated']+=1
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


def synthesize_goal(registry,rows,max_nodes=5,budget=10000,reuse=True):
    """Find first matching program, retaining sound observation-scoped failures."""
    from .engine import execute,hash_of
    if not rows:raise ValueError('no observations')
    ti,to=typ(rows[0][0]),typ(rows[0][1]);scope=hash_of(['typedholes-v1',rows])
    ops=registry.active() if reuse else {}
    candidates,stats=enumerate_goal(to,ti,ops,max_nodes)
    checks=skips=0
    for e in candidates:
        if registry.failed(scope,e):skips+=1;continue
        if checks>=budget:return {'program':None,'checks':checks,'failure_skips':skips,'exhausted':True,'stats':stats}
        checks+=1
        try:good=all(execute(e,x,ops)==y for x,y in rows)
        except (ValueError,TypeError,IndexError,RecursionError,OverflowError):good=False
        if good:return {'program':e,'checks':checks,'failure_skips':skips,'exhausted':False,'stats':stats}
        registry.record_failure(scope,e,'empirical mismatch: scope only')
        registry.evidence.append('empirical_failure',scope,e,{'reason':'observation mismatch','schema':1})
    return {'program':None,'checks':checks,'failure_skips':skips,'exhausted':False,'stats':stats}
