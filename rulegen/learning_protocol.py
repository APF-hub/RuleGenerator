"""M78 bridge: run both maintained synthesis dialects under one evidence protocol.

Do not translate ASTs or type constructors implicitly. Each backend retains its
own interpreter and registry, while results share a versioned experiment schema.
"""
import hashlib
import json
from .engine import synthesize as legacy_synthesize
from .typedholes import synthesize_goal
from .functional_synthesis import synthesize_functional

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def evaluate_backend(backend,rows,registry,*,budget,max_nodes=5,reuse=True):
    """Return a comparable record, without claiming equivalent search spaces."""
    if backend=="legacy":
        result=legacy_synthesize(registry,rows,max_nodes=max_nodes,budget=budget,reuse=reuse)
    elif backend=="legacy-goal":
        result=synthesize_goal(registry,rows,max_nodes=max_nodes,budget=budget,reuse=reuse)
    elif backend=="functional":
        result=synthesize_functional(rows,registry,max_nodes=max_nodes,budget=budget,reuse=reuse)
    else:
        raise ValueError("unknown backend")
    return {"schema_version":1,"backend":backend,"observations_digest":fingerprint(rows),
            "budget":budget,"max_nodes":max_nodes,"reuse":reuse,
            "checks":result["checks"],"solved":result["program"] is not None,
            "program":result["program"],"exhausted":result["exhausted"],
            "type_pruned":result.get("type_pruned",result.get("stats",{}).get("type_pruned")),
            "acquisition_checks":None}

def compare_cold_warm(backend,rows,registry,*,budget,max_nodes=5,acquisition_checks=None):
    """Matched evaluation budget; acquisition accounting is explicit and optional.

    Do not interpret the total as a matched TOTAL budget unless acquisition is
    separately deducted or an equal total allowance is supplied.
    """
    cold=evaluate_backend(backend,rows,registry,budget=budget,max_nodes=max_nodes,reuse=False)
    warm=evaluate_backend(backend,rows,registry,budget=budget,max_nodes=max_nodes,reuse=True)
    if acquisition_checks is not None and acquisition_checks<0:
        raise ValueError("negative acquisition cost")
    return {"schema_version":1,"cold":cold,"warm":warm,
            "acquisition_checks":acquisition_checks,
            "warm_checks_including_acquisition":None if acquisition_checks is None else
                warm["checks"]+acquisition_checks,
            "matched_evaluation_budget":True,"matched_total_budget":False}
