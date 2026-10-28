import tempfile
import unittest
from pathlib import Path
from rulegen.audio import render,save_wav,reconstruct_wav,load_wav
from rulegen.experiments import ExperimentStore

class PersistentAudioTests(unittest.TestCase):
    def test_persist_and_reload(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/'in.wav'
            output=root/'out.wav'
            db=root/'research.sqlite'
            save_wav(source,8000,render(((400.,.4,0),),8000,400))
            result=reconstruct_wav(source,output,budget=15,database=db)
            self.assertGreater(result['experiment_id'],0)
            rate,observed=load_wav(source)
            with ExperimentStore(db) as store:
                saved=store.best('audio.sine.v1',[rate,observed])
                self.assertIsNotNone(saved)
                self.assertEqual(saved['id'],result['experiment_id'])
                self.assertAlmostEqual(saved['loss'],result['mse'])
                self.assertIsNone(store.best('image.rgba.v1',[rate,observed]))
    def test_no_database_is_opt_in(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/'in.wav'
            save_wav(source,8000,render(((400.,.4,0),),8000,400))
            result=reconstruct_wav(source,root/'out.wav',budget=15)
            self.assertIsNone(result['experiment_id'])
if __name__=='__main__':unittest.main()
