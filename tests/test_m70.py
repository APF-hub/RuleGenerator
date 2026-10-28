import math
import tempfile
import unittest
from pathlib import Path
from rulegen.reconstruct import search
from rulegen.audio import SineAdapter, render, save_wav, load_wav, reconstruct_wav

class AudioTests(unittest.TestCase):
    def test_wav_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'in.wav'
            save_wav(path, 8000, [0, .25, -.5, 1])
            rate, samples = load_wav(path)
            self.assertEqual(rate, 8000)
            self.assertLess(abs(samples[1]-.25), 0.001)
    def test_observation_to_executable_program(self):
        rate = 8000
        observed = render(((440., .5, .2),), rate, 800)
        result = search(observed, SineAdapter(rate, components=2), budget=100)
        self.assertLess(result.loss, .1)
        self.assertLessEqual(result.evaluations, 100)
        self.assertTrue(result.history)
    def test_file_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d)/'input.wav', Path(d)/'output.wav'
            save_wav(src, 8000, render(((400., .6, 0),), 8000, 800))
            result = reconstruct_wav(src, dst, budget=40)
            self.assertTrue(dst.exists())
            self.assertLess(result['mse'], .05)
    def test_budget(self):
        with self.assertRaises(ValueError):
            search([0.0], SineAdapter(8000), budget=0)
if __name__ == '__main__':unittest.main()
