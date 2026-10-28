"""C4: deterministic repeated-target, acquisition-inclusive reuse experiment.

Counts are heterogeneous candidate checks and operator admission executions,
not elapsed time or equivalent compute. No claim of independent source attestation.
"""
from .discovery import discover
from .engine import hash_of, synthesize


def run_reuse_experiment(registry, name, training, validation, targets, *,
                         acquisition_budget=10000, target_budget=10000,
                         max_nodes=5, max_generated=10000):
    """Run cold and warm searches on distinct targets; report break-even.

    Each target is a nonempty set of observations. Targets, training and
    validation must have disjoint input fingerprints. Cold searches disable
    library reuse; warm searches include the newly promoted operator.
    """
    if not training or not validation or not targets or any(not rows for rows in targets):
        raise ValueError("nonempty acquisition splits and target tasks required")
    for value in (acquisition_budget,target_budget,max_nodes,max_generated):
        if type(value) is not int or value<1:
            raise ValueError("positive integer limits required")
    groups=[training,validation,*targets]
    seen=set()
    for group in groups:
        keys={hash_of(x) for x,_ in group}
        if seen & keys:raise ValueError("cross-task or split input overlap")
        seen.update(keys)
    # Perform all cold controls before operator promotion.
    cold=[synthesize(registry,rows,max_nodes=max_nodes,budget=target_budget,
                     max_generated=max_generated,reuse=False) for rows in targets]
    acquisition=discover(registry,name,training,validation,
                         max_nodes=max_nodes,budget=acquisition_budget,
                         max_generated=max_generated)
    admission_executions=acquisition["validation_executions"]
    acquisition_units=acquisition["checks"]+admission_executions
    if not acquisition["admitted"]:
        return {"schema_version":1,"admitted":False,
                "reason":acquisition.get("reason"),"cold":cold,"warm":None,
                "acquisition_checks":acquisition["checks"],
                "admission_executions":admission_executions,
                "acquisition_work_units":acquisition_units,
                "break_even_target":None,"matched_total_budget":False}
    warm=[synthesize(registry,rows,max_nodes=max_nodes,budget=target_budget,
                     max_generated=max_generated,reuse=True) for rows in targets]
    cumulative_cold=0
    cumulative_warm=acquisition_units
    history=[]
    break_even=None
    for index,(baseline,learned) in enumerate(zip(cold,warm),start=1):
        cumulative_cold+=baseline["checks"]
        cumulative_warm+=learned["checks"]
        comparable=all(x["program"] is not None for x in (baseline,learned))
        if comparable and cumulative_warm<=cumulative_cold and break_even is None:
            break_even=index
        history.append({"target":index,"cold_checks":baseline["checks"],
                        "warm_checks":learned["checks"],
                        "cold_solved":baseline["program"] is not None,
                        "warm_solved":learned["program"] is not None,
                        "cumulative_cold_checks":cumulative_cold,
                        "cumulative_warm_work_units":cumulative_warm,
                        "both_solved":comparable})
    return {"schema_version":1,"admitted":True,"operator":name,
            "acquisition_checks":acquisition["checks"],
            "admission_executions":admission_executions,
            "acquisition_work_units":acquisition_units,
            "cold":cold,"warm":warm,"history":history,
            "break_even_target":break_even,
            "matched_total_budget":False,
            "work_unit_definition":"candidate_checks_plus_admission_executions",
            "limitations":["not equivalent CPU costs","no independent source attestation",
                           "same target search budget, not matched total budget"]}
