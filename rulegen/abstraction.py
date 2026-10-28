"""Discover parameterized reusable expressions from independently solved tasks.

This module proposes typed abstractions from structurally aligned program
solutions. It does not claim to infer the true generative mechanism.
Candidates remain separate from validated/promoted operators.
"""
import copy
import json
from .functional import Core

def _canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)

def anti_unify(left,right):
    """Find shared AST structure, replacing differing subtrees with holes.

    Identical differing subtrees share one hole. Return generalized template
    and corresponding substitutions. Hole names are internal placeholders.
    """
    holes={}
    def walk(a,b):
        if _canonical(a)==_canonical(b):
            return copy.deepcopy(a)
        if isinstance(a,dict) and isinstance(b,dict) and a.get("op")==b.get("op"):
            if a.get("op")=="call" and a.get("name")==b.get("name") and len(a.get("args",[]))==len(b.get("args",[])):
                return {"op":"call","name":a["name"],"args":[walk(x,y) for x,y in zip(a["args"],b["args"])]}
        key=(_canonical(a),_canonical(b))
        if key not in holes:
            holes[key]="p"+str(len(holes))
        return {"op":"var","name":holes[key]}
    template=walk(left,right)
    substitutions={}
    def collect(a,b,t):
        if t["op"]=="var" and t["name"].startswith("p") and t["name"] in holes.values():
            substitutions[t["name"]]=(a,b)
        elif t["op"]=="call":
            for x,y,z in zip(a["args"],b["args"],t["args"]):collect(x,y,z)
    collect(left,right,template)
    return template,substitutions

def propose(name,examples,core=None):
    """Propose a typed abstraction from >=2 distinct executable ASTs.

    Examples are pairs of (program, input_environment). This stage checks
    structural recurrence and type consistency, not independent validation.
    """
    core=Core("math") if core is None else core
    if len(examples)<2:raise ValueError("need independent solutions")
    left,env1=examples[0];right,env2=examples[1]
    if _canonical(left)==_canonical(right):raise ValueError("no variable structure")
    template,substitutions=anti_unify(left,right)
    if not substitutions:raise ValueError("no shared parameterizable structure")
    params=[]
    for key,(a,b) in sorted(substitutions.items()):
        t1=core.infer(a,{k:core._runtime_type(v) for k,v in env1.items()})
        t2=core.infer(b,{k:core._runtime_type(v) for k,v in env2.items()})
        if t1!=t2:raise TypeError("incompatible parameter types")
        params.append({"name":key,"type":t1})
    expected=core.infer(left,{k:core._runtime_type(v) for k,v in env1.items()})
    if core.infer(right,{k:core._runtime_type(v) for k,v in env2.items()})!=expected:
        raise TypeError("incompatible solution types")
    definition={"params":params,"return_type":expected,"body":template}
    verifier=Core(core.tier,core.definitions)
    verifier.validate_definition(name,definition)
    return {"name":name,"definition":definition,"substitutions":substitutions,
            "status":"candidate"}

def validate(candidate,observations,core=None,tolerance=1e-9):
    """Held-out tests: (argument_values, expected_output).

    Never mutate the active library; returns evidence and a status only.
    """
    if not observations:raise ValueError("independent validation required")
    core=Core("math") if core is None else core
    candidate_core=Core(core.tier,core.definitions)
    candidate_core.validate_definition(candidate["name"],candidate["definition"])
    params=candidate["definition"]["params"]
    successes=0
    for args,expected in observations:
        if len(args)!=len(params):continue
        try:
            result=candidate_core.execute(
                {"op":"call","name":candidate["name"],
                 "args":[{"op":"literal","value":x} for x in args]})
            if type(result) is type(expected) and result==expected:
                successes+=1
            elif type(result) in (int,float) and type(expected) in (int,float):
                if abs(result-expected)<=tolerance:successes+=1
        except (TypeError,ValueError,ArithmeticError,OverflowError,RuntimeError):
            pass
    return {"status":"validated" if successes==len(observations) else "rejected",
            "passed":successes,"total":len(observations),
            "candidate":candidate["name"]}
