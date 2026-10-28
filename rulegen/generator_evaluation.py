"""E3: compare generator AST complexity with observed synthesis outcomes.

Search finds programs consistent with training observations; held-out agreement
is empirical and does not prove equivalence. No learned operator is promoted.
"""
import tempfile
from pathlib import Path
from .engine import Registry, execute, synthesize
from .task_generators import ast_complexity, generate_task


def evaluate_generated_task(seed, *, family="arithmetic", complexity=1,
                            max_nodes=5, budget=10000, max_generated=10000):
    task=generate_task(seed,family=family,complexity=complexity)
    with tempfile.TemporaryDirectory() as tmp:
        with Registry(Path(tmp)/"search.sqlite") as registry:
            search=synthesize(registry,task["training"],max_nodes=max_nodes,
                              budget=budget,max_generated=max_generated,reuse=False)
    learned=search["program"]
    tested=len(task["validation"])+len(task["test"])
    correct=0
    if learned is not None:
        for x,y in task["validation"]+task["test"]:
            try:
                if execute(learned,x)==y:correct+=1
            except (TypeError,ValueError,RecursionError,OverflowError):
                pass
    return {"schema_version":1,"seed":seed,"family":family,
            "construction_complexity":complexity,
            "generator_complexity":task["generator_complexity"],
            "generator_digest":task["generator_digest"],
            "learned_program":learned,
            "learned_complexity":ast_complexity(learned) if learned is not None else None,
            "search_checks":search["checks"],
            "type_pruned":search["type_pruned"],
            "failure_skips":search["failure_skips"],
            "exhausted":search["exhausted"],
            "training_solved":learned is not None,
            "heldout_correct":correct if learned is not None else None,
            "heldout_total":tested,
            "heldout_accuracy":correct/tested if learned is not None else None,
            "structurally_identical":learned==task["generator_program"] if learned is not None else None,
            "semantic_equivalence_proven":False}


def evaluate_grid(seeds=(0,1,2), *, families=("arithmetic","pair"),
                  arithmetic_levels=(1,2,3), max_nodes=5,
                  budget=10000,max_generated=10000):
    """Return individual results; do not silently discard unsuccessful searches."""
    if not seeds or not families or not arithmetic_levels:
        raise ValueError("nonempty grid axes required")
    results=[]
    for family in families:
        levels=arithmetic_levels if family=="arithmetic" else (1,)
        for level in levels:
            for seed in seeds:
                results.append(evaluate_generated_task(
                    seed,family=family,complexity=level,
                    max_nodes=max_nodes,budget=budget,max_generated=max_generated))
    return results
