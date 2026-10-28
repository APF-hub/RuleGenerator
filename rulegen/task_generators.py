"""Seeded, typed AST generators with structural and behavioral diagnostics.

Generator programs are composed from the public legacy combinator basis.
Distinct input values are sampled without replacement. Structural complexity
is not a guarantee of semantic complexity or synthesis difficulty.
"""
import random
from .engine import execute, hash_of, typecheck, typ


def ast_complexity(expr):
    """Count AST nodes, depth and primitive applications (operator calls)."""
    if not isinstance(expr,list) or not expr:raise ValueError("invalid AST")
    if expr[0] in ("input","const"):
        if len(expr)!=(1 if expr[0]=="input" else 2):raise ValueError("invalid leaf")
        return {"nodes":1,"depth":1,"calls":0}
    if expr[0]!="call" or len(expr)<3:raise ValueError("invalid call")
    children=[ast_complexity(child) for child in expr[2:]]
    return {"nodes":1+sum(x["nodes"] for x in children),
            "depth":1+max(x["depth"] for x in children),
            "calls":1+sum(x["calls"] for x in children)}


def generate_task(seed, *, family="arithmetic", complexity=1,
                  training_count=3, validation_count=2, test_count=3):
    """Generate a deterministic rule and disjoint examples from its execution.

    Arithmetic: repeated add of constant 1 (2 AST nodes per extra layer).
    Pair: fst/snd projections and pair recomposition, at least 4 AST nodes.
    The generator is intentionally small; complexity denotes construction
    layers, not a guaranteed minimum semantic difficulty.
    """
    if type(seed) is not int or type(complexity) is not int or complexity<1:
        raise ValueError("seed integer and positive complexity required")
    counts=(training_count,validation_count,test_count)
    if any(type(x) is not int or x<1 for x in counts):
        raise ValueError("positive split counts required")
    rng=random.Random(seed)
    if family=="arithmetic":
        program=["input"]
        for _ in range(complexity):
            program=["call","add",program,["const",1]]
        candidates=list(range(-1000,1001))
    elif family=="pair":
        if complexity!=1:raise ValueError("pair family supports one construction layer")
        program=["call","pair",["call","snd",["input"]],["call","fst",["input"]]]
        candidates=[(i,bool(i%2)) for i in range(-1000,1001)]
    else:raise ValueError("unknown generator family")
    total=sum(counts)
    if total>len(candidates):raise ValueError("sample count exceeds domain")
    inputs=rng.sample(candidates,total)
    rows=[(x,execute(program,x)) for x in inputs]
    a,b,c=counts
    complexity_metrics=ast_complexity(program)
    return {"schema_version":1,"seed":seed,"family":family,
            "construction_complexity":complexity,
            "generator_program":program,
            "generator_complexity":complexity_metrics,
            "generator_digest":hash_of(program),
            "training":rows[:a],"validation":rows[a:a+b],"test":rows[a+b:a+b+c],
            "disjoint_inputs":True}
