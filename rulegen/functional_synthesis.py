"""Bounded typed enumeration over the functional AST and promoted library.

This is a deliberately small first-order synthesizer, not a general solution
to higher-order program induction. Candidate evaluations are counted, and
operator-acquisition cost is reported separately by callers.
"""
import itertools
import json
from .functional import Core, INT, REAL

def literal(value):
    return {"op":"literal","value":value}

def variable(name):
    return {"op":"var","name":name}

def call(name,*args):
    return {"op":"call","name":name,"args":list(args)}

def _key(node):
    return json.dumps(node,sort_keys=True,separators=(",",":"))

def synthesize_functional(rows,registry=None,*,tier="math",max_nodes=7,
                          budget=2000,constants=(0,1,2),reuse=True,max_generated=10000):
    """Rows: (environment_dict, expected_output), with consistent input types.

    Enumerates expressions by AST node count; learned operator calls cost one
    node plus argument nodes. The score is candidate evaluations, not elapsed
    time, and excludes the acquisition/validation cost of learned operators.
    """
    if not rows:raise ValueError("observations required")
    if max_nodes<1 or budget<1 or max_generated<1:raise ValueError("positive limits required")
    core=(registry.core() if registry is not None and reuse else Core(tier))
    env_type={k:core._runtime_type(v) for k,v in rows[0][0].items()}
    for env,_ in rows:
        if set(env)!=set(env_type) or any(core._runtime_type(env[k])!=t for k,t in env_type.items()):
            raise TypeError("inconsistent input environments")
    target=core._runtime_type(rows[0][1])
    for _,expected in rows[1:]:
        if core._runtime_type(expected)!=target:raise TypeError("inconsistent outputs")
    signatures={
        "+":2,"-":2,"*":2,"/":2,
        "sin":1,"cos":1,"exp":1,"sqrt":1,
    }
    names=sorted(core.definitions) if reuse else []
    for name in names:signatures[name]=len(core.definitions[name]["params"])
    signatures={name:arity for name,arity in signatures.items()
                if name in core.definitions or name in __import__("rulegen.functional",fromlist=["TIERS"]).TIERS[core.tier]}
    pool={1:[variable(k) for k in sorted(env_type)]+[literal(v) for v in constants]}
    seen=set()
    generated=len(pool[1])
    checks=0;type_pruned=0;runtime_errors=0
    for size in range(1,max_nodes+1):
        if size>1:
            pool[size]=[]
            for name,arity in signatures.items():
                if arity>size-1:continue
                for sizes in itertools.product(range(1,size),repeat=arity):
                    if sum(sizes)!=size-1:continue
                    for args in itertools.product(*(pool[s] for s in sizes)):
                        if generated>=max_generated:
                            return {"program":None,"checks":checks,"type_pruned":type_pruned,
                                    "runtime_errors":runtime_errors,"exhausted":True}
                        pool[size].append(call(name,*args))
                        generated+=1
        for expr in pool[size]:
            key=_key(expr)
            if key in seen:continue
            seen.add(key)
            try:
                inferred=core.infer(expr,env_type)
                if inferred!=target and not (inferred==INT and target==REAL):
                    type_pruned+=1;continue
            except (TypeError,KeyError,IndexError):
                type_pruned+=1;continue
            if checks>=budget:
                return {"program":None,"checks":checks,"type_pruned":type_pruned,
                        "runtime_errors":runtime_errors,"exhausted":True}
            checks+=1
            try:
                if all(_matches(core.execute(expr,env),expected) for env,expected in rows):
                    return {"program":expr,"checks":checks,"type_pruned":type_pruned,
                            "runtime_errors":runtime_errors,"exhausted":False}
            except (ValueError,TypeError,ArithmeticError,OverflowError,RuntimeError):
                runtime_errors+=1
    return {"program":None,"checks":checks,"type_pruned":type_pruned,
            "runtime_errors":runtime_errors,"exhausted":False}

def _matches(actual,expected):
    return type(actual) is type(expected) and actual==expected
