import unittest
import numpy as np
from rulegen.reconstruct import search
from rulegen.residual import ResidualAudioAdapter

class ResidualTests(unittest.TestCase):
 def test_silence(self):
  observed=[0.]*512
  result=search(observed,ResidualAudioAdapter(8000),budget=10)
  self.assertEqual(result.loss,0)
  self.assertEqual(result.program,())
 def test_two_simultaneous_tones(self):
  rate=8000;n=1024;t=np.arange(n)/rate
  observed=(.4*np.sin(2*np.pi*437.5*t)+.3*np.sin(2*np.pi*656.25*t)).tolist()
  result=search(observed,ResidualAudioAdapter(rate,max_events=3),budget=120)
  self.assertLess(result.loss,.035)
  self.assertGreaterEqual(len(result.program),2)
 def test_sequential_notes(self):
  rate=8000;n=1024;t=np.arange(n)/rate
  observed=np.zeros(n)
  observed[:512]=.45*np.sin(2*np.pi*437.5*t[:512])
  observed[512:]=.45*np.sin(2*np.pi*656.25*t[512:])
  result=search(observed.tolist(),ResidualAudioAdapter(rate,max_events=4),budget=150)
  self.assertLess(result.loss,.055)
  self.assertGreaterEqual(len(result.program),2)
if __name__=='__main__':unittest.main()
