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

def evaluate_backend(backend,rows,registry,*,budget,max_nodes=5,reuse=True,max_generated=10000,cancel=None):
    """Return a comparable record, without claiming equivalent search spaces."""
    if type(budget) is not int or budget<1:
        raise ValueError("budget must be a positive integer")
    if type(max_nodes) is not int or max_nodes<1:
        raise ValueError("max_nodes must be a positive integer")
    if type(max_generated) is not int or max_generated<1:
        raise ValueError("max_generated must be a positive integer")
    if backend=="legacy":
        result=legacy_synthesize(registry,rows,max_nodes=max_nodes,budget=budget,reuse=reuse,max_generated=max_generated,cancel=cancel)
    elif backend=="legacy-goal":
        result=synthesize_goal(registry,rows,max_nodes=max_nodes,budget=budget,reuse=reuse)
    elif backend=="functional":
        result=synthesize_functional(rows,registry,max_nodes=max_nodes,budget=budget,reuse=reuse)
    else:
        raise ValueError("unknown backend")
    if type(result["checks"]) is not int or not 0<=result["checks"]<=budget:
        raise RuntimeError("backend violated evaluation budget")
    return {"schema_version":1,"backend":backend,"observations_digest":fingerprint(rows),
            "budget":budget,"max_nodes":max_nodes,"max_generated":max_generated,"reuse":reuse,
            "checks":result["checks"],"solved":result["program"] is not None,
            "program":result["program"],"exhausted":result["exhausted"],
            "type_pruned":result.get("type_pruned",result.get("stats",{}).get("type_pruned")),
            "acquisition_checks":None}

def compare_cold_warm(backend,rows,registry,*,budget,max_nodes=5,acquisition_checks=None):
    """Matched evaluation budget; acquisition accounting is explicit and optional.

    Do not interpret the total as a matched TOTAL budget unless acquisition is
    separately deducted or an equal total allowance is supplied.
    """
    if acquisition_checks is not None and (type(acquisition_checks) is not int or acquisition_checks<0):
        raise ValueError("acquisition cost must be a nonnegative integer")
    cold=evaluate_backend(backend,rows,registry,budget=budget,max_nodes=max_nodes,reuse=False)
    warm=evaluate_backend(backend,rows,registry,budget=budget,max_nodes=max_nodes,reuse=True)
    if acquisition_checks is not None and acquisition_checks<0:
        raise ValueError("negative acquisition cost")
    return {"schema_version":1,"cold":cold,"warm":warm,
            "acquisition_checks":acquisition_checks,
            "warm_checks_including_acquisition":None if acquisition_checks is None else
                warm["checks"]+acquisition_checks,
            "matched_evaluation_budget":True,"matched_total_budget":False}


def compare_matched_total_budget(backend,rows,registry,*,total_budget,
                                 acquisition_checks,max_nodes=5):
    """Match total candidate-check allowance, including caller-supplied acquisition.

    Acquisition counts are NOT instrumented by this protocol. Results do not
    establish equivalent CPU time, memory use or search-space difficulty.
    """
    if type(total_budget) is not int or total_budget<1:
        raise ValueError("total budget must be a positive integer")
    if type(acquisition_checks) is not int or acquisition_checks<0:
        raise ValueError("acquisition checks must be a nonnegative integer")
    cold=evaluate_backend(backend,rows,registry,budget=total_budget,
                          max_nodes=max_nodes,reuse=False)
    available=total_budget-acquisition_checks
    if available<=0:
        warm=None
        reason="acquisition_exhausted_total_budget"
    else:
        warm=evaluate_backend(backend,rows,registry,budget=available,
                              max_nodes=max_nodes,reuse=True)
        reason=None
    return {"schema_version":1,"cold":cold,"warm":warm,
            "total_budget":total_budget,"acquisition_checks":acquisition_checks,
            "warm_search_budget":max(0,available),
            "warm_checks_including_acquisition":acquisition_checks+(warm["checks"] if warm else 0),
            "matched_total_budget":True,"acquisition_measured":False,
            "warm_unavailable_reason":reason}
