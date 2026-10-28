"""E5: transparent complexity-scaling grid over seeded cumulative learning.

Descriptive rates are not confidence intervals or evidence of cross-rule transfer.
Failed acquisitions remain in the denominator.
"""
from .generated_cumulative import evaluate_generated_cumulative


def evaluate_complexity_grid(*, seeds=(0,1,2), arithmetic_levels=(1,2,3),
                             include_pair=True, max_nodes=5, budget=10000,
                             max_generated=10000, target_tasks=2):
    if not seeds or not arithmetic_levels:
        raise ValueError("nonempty seeds and levels required")
    if len(set(seeds))!=len(seeds):
        raise ValueError("duplicate seeds")
    specifications=[("arithmetic",level) for level in arithmetic_levels]
    if include_pair:specifications.append(("pair",1))
    records=[]
    summary=[]
    for family,level in specifications:
        batch=[]
        for seed in seeds:
            row=evaluate_generated_cumulative(
                seed,family=family,complexity=level,max_nodes=max_nodes,
                budget=budget,max_generated=max_generated,target_tasks=target_tasks)
            records.append(row)
            batch.append(row)
        admitted=[r for r in batch if r["admitted"]]
        accurate=[r for r in admitted if r["heldout_accuracy"]==1.0]
        break_even=[r for r in accurate if r["break_even_target"] is not None]
        summary.append({
            "family":family,"construction_complexity":level,
            "generator_nodes":batch[0]["generator_complexity"]["nodes"],
            "trials":len(batch),"admitted":len(admitted),
            "fully_heldout_correct":len(accurate),
            "break_even_trials":len(break_even),
            "admission_rate":len(admitted)/len(batch),
            "heldout_success_rate":len(accurate)/len(batch),
            "break_even_rate":len(break_even)/len(batch),
            "mean_acquisition_work_units":sum(r["acquisition_work_units"] for r in batch)/len(batch),
            "mean_learned_nodes":(
                sum(r["learned_body_complexity"]["nodes"] for r in admitted)/len(admitted)
                if admitted else None),
        })
    return {"schema_version":1,"records":records,"summary":summary,
            "matched_total_budget":False,
            "cross_rule_transfer_tested":False,
            "confidence_intervals_computed":False}
