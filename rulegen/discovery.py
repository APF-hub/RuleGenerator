"""M61: discover executable operators, infer a candidate generic signature, validate and persist.

Important: structural generality is justified by parametric typechecking of the body,
not merely by its success on finitely many observations. This is a restricted,
non-recursive combinator language; no claim of universal synthesis is made.
"""
from .engine import (Registry, PRIMS, C, V, INT, BOOL, PAIR, LIST, FN,
                 typ, unify, substitute, typecheck, check_body, synthesize, execute)


def generalize_shape(t, prefix='t'):
    """Give each observed atomic position an independent type variable.

    Retain composite type constructors as *hypotheses*; do not assume the
    implementation works for all instantiations until its body typechecks.
    """
    counter=[0]
    def visit(t):
        if t[0]=='var':return t
        if t[1] in ('Pair','List','Fn'):
            return C(t[1],*(visit(a) for a in t[2:]))
        counter[0]+=1
        return V(prefix+str(counter[0]))
    return visit(t)


def lift_body(expr):
    """Turn a unary program using input into an operator body using arg 0."""
    if expr[0]=='input':return ['arg',0]
    if expr[0]=='const':return expr
    if expr[0]=='call':return ['call',expr[1],*(lift_body(a) for a in expr[2:])]
    raise TypeError('invalid program AST')


def discover(registry, name, training, validation, max_nodes=5, budget=10000):
    """Discover from training only, validate on separate observations.

    Polymorphism is admitted only when the executable body itself typechecks
    against a structurally generalised input. No domain-specific operator is
    given to the synthesizer. The constructor structure remains an inductive bias.
    """
    if not training or not validation:raise ValueError('nonempty disjoint splits required')
    from .engine import hash_of
    if {hash_of(x) for x,_ in training} & {hash_of(x) for x,_ in validation}:
        raise ValueError("train/validation input overlap")
    result=synthesize(registry,training,max_nodes=max_nodes,budget=budget,reuse=True)
    expr=result['program']
    if expr is None:return dict(result,admitted=False,reason='no training solution')
    generalized_input=generalize_shape(typ(training[0][0]))
    try:
        generic_output=typecheck(expr,generalized_input,registry.active())
        body=lift_body(expr)
        # Typecheck the body with the same type variables to justify the relation.
        unify(check_body(body,[generalized_input],registry.active()),generic_output)
        # Independent validation may contain different types; enforce signature.
        accepted=registry.admit(name,body,[generalized_input],generic_output,
                                [([x],y) for x,y in training],
                                [([x],y) for x,y in validation])
    except (TypeError,ValueError,IndexError,KeyError) as exc:
        return dict(result,admitted=False,reason=str(exc))
    return dict(result,admitted=accepted,operator=name if accepted else None,
                signature=[generalized_input,generic_output],reason=None if accepted else 'validation mismatch')


def benchmark(db_path):
    r=Registry(db_path)
    train=[((1,True),(True,1)),((2,False),(False,2)),((3,True),(True,3))]
    validate=[(([1,2],False),(False,[1,2])),((False,[3,4]),([3,4],False))]
    learned=discover(r,'learned_swap',train,validate)
    if not learned['admitted']:return {'discovery':learned}
    targets=[((4,False),(False,4)),((7,True),(True,7))]
    # First candidate learned operator call is only one of many search candidates.
    with_library=synthesize(r,targets,max_nodes=5,budget=10000,reuse=True)
    without_library=synthesize(r,targets,max_nodes=5,budget=10000,reuse=False)
    return {'discovery':learned,'reuse':with_library,'baseline':without_library,
            'acquisition_checks':learned['checks'],
            'total_with_acquisition':learned['checks']+with_library['checks'],
            'total_baseline_target_only':without_library['checks']}

if __name__=='__main__':
    import json,sys
    print(json.dumps(benchmark(sys.argv[1] if len(sys.argv)>1 else 'm61.sqlite3'),indent=2))
