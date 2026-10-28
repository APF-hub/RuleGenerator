"""C1: bounded legacy discover -> validate -> promote -> separate-task reuse.

This is an explicit orchestrator for the existing legacy discovery path,
not a general autonomous curriculum or verified data provenance system.
"""
from .discovery import discover
from .engine import hash_of, synthesize
from .provenance import Observation, verify_splits


def run_learning_cycle(registry, name, training, validation, reuse_rows, *,
                       max_nodes=5, acquisition_budget=10000,
                       reuse_budget=10000, max_generated=10000):
    """Return measured candidate checks and cold/warm reuse outcomes.

    Input overlap across all three splits is rejected before any mutation.
    Promotion occurs only after validation; unsuccessful acquisition never
    starts a warm run. Candidate-check counts exclude validation execution
    and other computational costs.
    """
    if not training or not validation or not reuse_rows:
        raise ValueError("training, validation and reuse observations required")
    for key,value in (("max_nodes",max_nodes),("acquisition_budget",acquisition_budget),
                      ("reuse_budget",reuse_budget),("max_generated",max_generated)):
        if type(value) is not int or value<1:
            raise ValueError(key+" must be a positive integer")
    split_inputs=[{hash_of(x) for x,_ in split}
                  for split in (training,validation,reuse_rows)]
    if any(split_inputs[a] & split_inputs[b]
           for a,b in ((0,1),(0,2),(1,2))):
        raise ValueError("input overlap across learning-cycle splits")
    # Baseline is evaluated before acquisition to avoid any promoted-operator
    # contamination, while explicitly disabling preexisting operator reuse.
    cold=synthesize(registry,reuse_rows,max_nodes=max_nodes,budget=reuse_budget,
                    reuse=False,max_generated=max_generated)
    acquisition=discover(registry,name,training,validation,
                         max_nodes=max_nodes,budget=acquisition_budget,
                         max_generated=max_generated)
    if not acquisition["admitted"]:
        return {"schema_version":1,"admitted":False,"reason":acquisition.get("reason"),
                "acquisition_checks":acquisition["checks"],"cold":cold,
                "warm":None,"warm_checks_including_acquisition":None,
                "validation_execution_count":acquisition["validation_executions"],
                "acquisition_work_units":acquisition["checks"]+acquisition["validation_executions"],
                "work_unit_definition":"candidate_checks_plus_admission_executions"}
    warm=synthesize(registry,reuse_rows,max_nodes=max_nodes,budget=reuse_budget,
                    reuse=True,max_generated=max_generated)
    return {"schema_version":1,"admitted":True,"operator":name,
            "acquisition_checks":acquisition["checks"],"cold":cold,"warm":warm,
            "warm_checks_including_acquisition":acquisition["checks"]+warm["checks"],
            "validation_execution_count":acquisition["validation_executions"],
            "acquisition_work_units":acquisition["checks"]+acquisition["validation_executions"],
            "warm_work_units_including_acquisition":acquisition["checks"]+acquisition["validation_executions"]+warm["checks"],
            "work_unit_definition":"candidate_checks_plus_admission_executions",
            "matched_evaluation_budget":True,"matched_total_budget":False}


def run_manifest_learning_cycle(registry, name, observations, *,
                                max_nodes=5, acquisition_budget=10000,
                                reuse_budget=10000, max_generated=10000):
    """Fail closed on declared provenance before calling the C1 learning cycle.

    A manifest binds every observation to a caller-declared source and split.
    It cannot establish that sources are authentic or independent in reality.
    No registry mutation occurs before the complete manifest is validated.
    """
    manifest=verify_splits(observations)
    counts=manifest["split_counts"]
    if any(counts[s]==0 for s in ("train","validation","test")):
        raise ValueError("train, validation and test splits required")
    split_rows={s:[] for s in ("train","validation","test")}
    for row in observations:
        split_rows[row.split].append((row.inputs,row.expected))
    result=run_learning_cycle(
        registry,name,split_rows["train"],split_rows["validation"],
        split_rows["test"],max_nodes=max_nodes,
        acquisition_budget=acquisition_budget,reuse_budget=reuse_budget,
        max_generated=max_generated)
    return dict(result,manifest=manifest,
                provenance="caller_declared_unverified",
                promotion_provenance_verified=False)
