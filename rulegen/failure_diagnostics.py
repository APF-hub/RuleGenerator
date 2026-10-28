"""E7: explain acquisition failures without conflating coverage and validation."""
from .engine import Registry, synthesize
from .task_generators import generate_task
from .discovery import discover
import tempfile
from pathlib import Path


def diagnose_generated_task(seed, *, family="arithmetic", complexity=1,
                            max_nodes=5,budget=300,max_generated=300):
    task=generate_task(seed,family=family,complexity=complexity)
    with tempfile.TemporaryDirectory() as directory:
        with Registry(Path(directory)/"diagnostic.sqlite") as registry:
            search=synthesize(registry,task["training"],max_nodes=max_nodes,
                              budget=budget,max_generated=max_generated,reuse=False)
        with Registry(Path(directory)/"admission.sqlite") as registry:
            admission=discover(registry,"diagnostic",task["training"],task["validation"],
                               max_nodes=max_nodes,budget=budget,max_generated=max_generated)
    if task["generator_complexity"]["nodes"]>max_nodes:
        reason="generator_exceeds_max_nodes"
    elif search["program"] is None and search["exhausted"]:
        reason="bounded_search_exhausted"
    elif search["program"] is None:
        reason="no_training_solution_within_enumerated_space"
    elif not admission["admitted"]:
        reason="promotion_rejected"
    else:
        reason="admitted"
    return {"seed":seed,"family":family,"complexity":complexity,
            "generator_ast":task["generator_program"],
            "generator_nodes":task["generator_complexity"]["nodes"],
            "sample_training":task["training"][:2],
            "search_checks":search["checks"],"search_exhausted":search["exhausted"],
            "type_pruned":search["type_pruned"],
            "failure_skips":search["failure_skips"],
            "search_program":search["program"],
            "admission_reason":admission.get("reason"),
            "admitted":admission["admitted"],"failure_category":reason}


def diagnose_grid(seeds=(0,1,2), *, max_nodes=5,budget=300,max_generated=300):
    results=[diagnose_generated_task(seed,family=family,complexity=level,
                                    max_nodes=max_nodes,budget=budget,
                                    max_generated=max_generated)
             for family,level in (("arithmetic",1),("arithmetic",2),
                                  ("arithmetic",3),("pair",1))
             for seed in seeds]
    counts={}
    for row in results:
        category=row["failure_category"]
        counts[category]=counts.get(category,0)+1
    return {"counts":counts,"examples":results}
