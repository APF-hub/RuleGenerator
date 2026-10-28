"""E4: seeded generator -> admission -> held-out test -> repeated reuse.

A held-out failure is reported, never silently treated as successful transfer.
This benchmark uses equal per-target budgets, NOT matched total budgets.
"""
import tempfile
from pathlib import Path
from .cumulative_experiment import run_reuse_experiment
from .engine import Registry, execute
from .task_generators import ast_complexity, generate_task


def evaluate_generated_cumulative(seed, *, family="pair", complexity=1,
                                  target_tasks=2, target_examples=2,
                                  max_nodes=5, budget=10000,
                                  max_generated=10000):
    if type(target_tasks) is not int or target_tasks<1:
        raise ValueError("positive target_tasks required")
    if type(target_examples) is not int or target_examples<1:
        raise ValueError("positive target_examples required")
    task=generate_task(seed,family=family,complexity=complexity,
                       test_count=target_tasks*target_examples)
    rows=task["test"]
    targets=[rows[i:i+target_examples] for i in range(0,len(rows),target_examples)]
    with tempfile.TemporaryDirectory() as tmp:
        with Registry(Path(tmp)/"experiment.sqlite") as registry:
            result=run_reuse_experiment(
                registry,"generated_rule",task["training"],task["validation"],targets,
                max_nodes=max_nodes,acquisition_budget=budget,
                target_budget=budget,max_generated=max_generated)
            active=registry.active().get("generated_rule")
            # The promoted body is checked against all held-out observations
            # independently of warm search success.
            heldout_correct=0
            if active is not None:
                for x,y in rows:
                    try:
                        if execute(active["body"],(x,),registry.active())==y:
                            heldout_correct+=1
                    except (TypeError,ValueError,RecursionError,OverflowError):
                        pass
    learned=active["body"] if active is not None else None
    return {"schema_version":1,"seed":seed,"family":family,
            "construction_complexity":complexity,
            "generator_complexity":task["generator_complexity"],
            "generator_digest":task["generator_digest"],
            "admitted":result["admitted"],
            "learned_body_complexity":_body_complexity(learned) if learned is not None else None,
            "heldout_correct":heldout_correct if learned is not None else None,
            "heldout_total":len(rows),
            "heldout_accuracy":heldout_correct/len(rows) if learned is not None else None,
            "acquisition_checks":result["acquisition_checks"],
            "admission_executions":result["admission_executions"],
            "acquisition_work_units":result["acquisition_work_units"],
            "history":result.get("history"),
            "break_even_target":result["break_even_target"],
            "matched_total_budget":False,
            "semantic_equivalence_proven":False}


def _body_complexity(body):
    """Normalize unary operator positional argument to input for AST metrics."""
    if body[0]=="arg":return {"nodes":1,"depth":1,"calls":0}
    if body[0]=="const":return ast_complexity(body)
    if body[0]=="call":
        children=[_body_complexity(x) for x in body[2:]]
        return {"nodes":1+sum(x["nodes"] for x in children),
                "depth":1+max(x["depth"] for x in children),
                "calls":1+sum(x["calls"] for x in children)}
    raise ValueError("unknown operator body")
