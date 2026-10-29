import unittest
from rulegen.observation_contracts import (
    Observation,ObservationMethod,ExperimentSpec,generate_experiment,digest
)


class ObservationContractsTests(unittest.TestCase):
    def test_transform_lineage_and_type(self):
        raw=Observation([1,2,3],"series","samples")
        method=ObservationMethod("differences","series","series",
                                 lambda xs:[b-a for a,b in zip(xs,xs[1:])])
        derived=method.apply(raw)
        self.assertEqual(derived.value,[1,1])
        self.assertEqual(derived.parent_digest,raw.identifier)
        self.assertEqual(derived.method_digest,method.identifier)
        with self.assertRaises(TypeError):
            method.apply(Observation(3,"scalar"))

    def test_deterministic_splits_and_hidden_generator(self):
        spec=ExperimentSpec("trial",7,15,"mechanism-v1")
        a=generate_experiment(spec,lambda x:x*x,range(100))
        b=generate_experiment(spec,lambda x:x*x,range(100))
        self.assertEqual(a,b)
        self.assertEqual(a["evaluator"]["dataset_digest"],digest(a["learner"]))
        self.assertNotIn("generator_id",str(a["learner"]))
        self.assertEqual(sum(map(len,a["learner"]["observations"].values())),15)
        xs=[x for rows in a["learner"]["observations"].values() for x,_ in rows]
        self.assertEqual(len(xs),len(set(xs)))
        self.assertFalse(a["evaluator"]["external_validation"])

    def test_invalid_domains_and_splits(self):
        spec=ExperimentSpec("trial",0,6,"mechanism")
        with self.assertRaises(ValueError):
            generate_experiment(spec,lambda x:x,[1,1,2,3,4,5])
        with self.assertRaises(ValueError):
            generate_experiment(spec,lambda x:x,range(10),training_fraction=0.95)
