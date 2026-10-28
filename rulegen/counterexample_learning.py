"""Bounded counterexample-guided refinement for the legacy synthesizer.

Probe labels are an explicit oracle supplied by the experiment. They become
training data when used; never count probes as independent held-out evidence.
"""
from .engine import execute, hash_of, synthesize


def refine_with_counterexamples(registry, training, probes, *,
                                max_rounds=5, max_nodes=5,
                                budget=10000, max_generated=10000):
    if not training or not probes:raise ValueError("training and probes required")
    if any(type(x) is not int or x<1
           for x in (max_rounds,max_nodes,budget,max_generated)):
        raise ValueError("positive integer limits required")
    seen={hash_of(x) for x,_ in training}
    if len(seen)!=len(training):raise ValueError("duplicate training inputs")
    for x,_ in probes:
        key=hash_of(x)
        if key in seen:raise ValueError("overlapping or duplicate probe input")
        seen.add(key)
    rows=list(training)
    history=[]
    total_checks=0
    for round_number in range(1,max_rounds+1):
        search=synthesize(registry,rows,max_nodes=max_nodes,budget=budget,
                          max_generated=max_generated,reuse=False)
        total_checks+=search["checks"]
        candidate=search["program"]
        if candidate is None:
            history.append({"round":round_number,"checks":search["checks"],
                            "status":"no_solution","exhausted":search["exhausted"]})
            break
        counterexample=None
        for x,expected in probes:
            try:
                valid=execute(candidate,x)==expected
            except (TypeError,ValueError,RecursionError,OverflowError):
                valid=False
            if not valid:
                counterexample=(x,expected)
                break
        if counterexample is None:
            history.append({"round":round_number,"checks":search["checks"],
                            "status":"probe_consistent"})
            return {"program":candidate,"probe_consistent":True,
                    "rounds":round_number,"added_counterexamples":len(rows)-len(training),
                    "total_checks":total_checks,"history":history,
                    "independent_heldout_verified":False}
        rows.append(counterexample)
        probes=[row for row in probes if hash_of(row[0])!=hash_of(counterexample[0])]
        history.append({"round":round_number,"checks":search["checks"],
                        "status":"counterexample_added"})
        if not probes:break
    return {"program":None,"probe_consistent":False,
            "rounds":len(history),"added_counterexamples":len(rows)-len(training),
            "total_checks":total_checks,"history":history,
            "independent_heldout_verified":False}
