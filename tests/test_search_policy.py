import json
import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.search_policy import ExperiencePolicy, guided_synthesize
from rulegen.task_features import extract_features
from rulegen.task_generators import generate_task


class SearchPolicyTests(unittest.TestCase):
    def test_features_do_not_require_generator_ast(self):
        f=extract_features([((1,True),(True,1)),((2,False),(False,2))])
        self.assertTrue(f["pair_swap_consistent"])
        self.assertNotIn("generator_program",f)

    def test_compare_three_strategies(self):
        results=[]
        policy=ExperiencePolicy()
        for family,level in (("arithmetic",1),("arithmetic",2),("pair",1)):
            for seed in (0,1,2):
                task=generate_task(seed,family=family,complexity=level)
                for mode in ("baseline","feature","learned"):
                    with tempfile.TemporaryDirectory() as tmp:
                        with Registry(Path(tmp)/"search.sqlite") as registry:
                            result=guided_synthesize(
                                registry,task["training"],mode=mode,policy=policy,
                                max_nodes=5,budget=300,max_generated=300,reuse=False)
                    results.append({"family":family,"level":level,"seed":seed,
                                    "mode":mode,"solved":result["program"] is not None,
                                    "checks":result["checks"],
                                    "exhausted":result["exhausted"]})
        self.assertEqual(len(results),27)
        print("FEATURE_SEARCH_COMPARISON_JSON="+json.dumps(results,sort_keys=True),flush=True)
