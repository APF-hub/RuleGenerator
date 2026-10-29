"""Minimal domain-neutral observation contracts and synthetic experiment splits."""
from dataclasses import dataclass
from hashlib import sha256
import json
import random


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


@dataclass(frozen=True)
class Observation:
    value: object
    kind: str
    units: str = "dimensionless"
    source: str = "external"
    parent_digest: str = ""
    method_digest: str = ""

    @property
    def identifier(self):
        return digest({"value":self.value,"kind":self.kind,"units":self.units,
                       "source":self.source,"parent":self.parent_digest,
                       "method":self.method_digest})


@dataclass(frozen=True)
class ObservationMethod:
    name: str
    input_kind: str
    output_kind: str
    transform: object
    version: int = 1

    @property
    def identifier(self):
        return digest({"name":self.name,"version":self.version,
                       "input_kind":self.input_kind,"output_kind":self.output_kind})

    def apply(self,observation):
        if observation.kind!=self.input_kind:
            raise TypeError("observation kind mismatch")
        return Observation(self.transform(observation.value),self.output_kind,
                           observation.units,"derived",observation.identifier,
                           self.identifier)


@dataclass(frozen=True)
class ExperimentSpec:
    name: str
    seed: int
    sample_count: int
    generator_id: str
    generator_version: int = 1

    def __post_init__(self):
        if type(self.seed) is not int or type(self.sample_count) is not int or self.sample_count<3:
            raise ValueError("seed must be integer and sample_count at least three")
        if not self.name or not self.generator_id or self.generator_version<1:
            raise ValueError("experiment requires versioned generator identity")

    @property
    def identifier(self):
        return digest(self.__dict__)


def generate_experiment(spec,mechanism,inputs,*,training_fraction=0.6,validation_fraction=0.2):
    """Return learner observations separately from synthetic evaluator provenance."""
    if not 0<training_fraction<1 or not 0<validation_fraction<1 or training_fraction+validation_fraction>=1:
        raise ValueError("invalid split fractions")
    values=list(inputs)
    if len({digest(x) for x in values})!=len(values) or len(values)<spec.sample_count:
        raise ValueError("unique input domain must cover sample count")
    chosen=random.Random(spec.seed).sample(values,spec.sample_count)
    rows=[(x,mechanism(x)) for x in chosen]
    a=int(spec.sample_count*training_fraction)
    b=int(spec.sample_count*validation_fraction)
    if min(a,b,spec.sample_count-a-b)<1:raise ValueError("each split must be nonempty")
    public={"schema_version":1,"observations":{
        "training":rows[:a],"validation":rows[a:a+b],"test":rows[a+b:]},
        "input_kind":"generic","output_kind":"generic"}
    evaluator={"experiment_id":spec.identifier,"generator_id":spec.generator_id,
               "generator_version":spec.generator_version,"seed":spec.seed,
               "sample_count":spec.sample_count,"dataset_digest":digest(public),
               "splits":{"training":a,"validation":b,"test":spec.sample_count-a-b},
               "synthetic":True,"external_validation":False}
    return {"learner":public,"evaluator":evaluator}
