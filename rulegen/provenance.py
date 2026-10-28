"""M81: reproducible, source-declared splits and measured acquisition accounting.

Provenance is caller-declared and fingerprinted, not independently attested.
"""
import hashlib
import json
from dataclasses import dataclass

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

@dataclass(frozen=True)
class Observation:
    source_id:str
    split:str
    inputs:object
    expected:object

    def __post_init__(self):
        if not self.source_id:raise ValueError("source id required")
        if self.split not in ("train","validation","test"):raise ValueError("unknown split")

def verify_splits(observations):
    """Detect identical sources, arguments, and input/output pairs across splits."""
    if not observations:raise ValueError("observations required")
    by_source={}
    by_input={}
    by_pair={}
    for row in observations:
        if not isinstance(row,Observation):raise TypeError("expected Observation")
        for index,key in ((by_source,row.source_id),
                          (by_input,digest(row.inputs)),
                          (by_pair,digest([row.inputs,row.expected]))):
            if key in index and index[key]!=row.split:
                raise ValueError("cross-split leakage")
            index[key]=row.split
    return {"schema_version":1,"count":len(observations),
            "split_counts":{s:sum(o.split==s for o in observations)
                            for s in ("train","validation","test")},
            "manifest_digest":digest([{"source_id":o.source_id,"split":o.split,
                                      "inputs":o.inputs,"expected":o.expected}
                                     for o in observations]),
            "provenance":"caller_declared_unverified"}

def acquisition_report(*,proposal_checks,validation_checks,search_checks):
    """Explicit accounting; never substitute unknown costs with zero."""
    values=(proposal_checks,validation_checks,search_checks)
    if any(type(v) is not int or v<0 for v in values):
        raise ValueError("all check counts must be nonnegative integers")
    return {"proposal_checks":proposal_checks,
            "validation_checks":validation_checks,
            "search_checks":search_checks,
            "acquisition_checks":proposal_checks+validation_checks,
            "total_checks":sum(values)}
