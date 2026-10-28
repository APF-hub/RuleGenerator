import unittest
import tempfile
from pathlib import Path
import numpy as np
from rulegen.audio import render, save_wav
from rulegen.spectrogram import stft_magnitude, spectrogram_image, SpectrogramAudioAdapter, reconstruct_spectrogram_wav

class SpectrogramTests(unittest.TestCase):
    def test_spectrogram_image_shape_and_type(self):
        signal=render(((440.,.5,0.),),8000,800)
        matrix=stft_magnitude(signal,window=128,hop=32)
        image=spectrogram_image(signal,window=128,hop=32)
        self.assertEqual(image.shape, matrix.T.shape)
        self.assertEqual(image.dtype,np.uint8)
    def test_identical_signal_zero_loss(self):
        signal=render(((440.,.5,0.),),8000,800)
        adapter=SpectrogramAudioAdapter(8000)
        self.assertAlmostEqual(adapter.loss(signal,signal),0)
    def test_phase_ambiguity_spectral_vs_waveform(self):
        signal=render(((440.,.5,0.),),8000,800)
        inverted=[-x for x in signal]
        spectral=SpectrogramAudioAdapter(8000,waveform_weight=0)
        joint=SpectrogramAudioAdapter(8000,waveform_weight=.5)
        self.assertLess(spectral.loss(signal,inverted),1e-20)
        self.assertGreater(joint.loss(signal,inverted),.1)
    def test_search_and_file_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            src,dst=Path(d)/'source.wav',Path(d)/'reconstructed.wav'
            save_wav(src,8000,render(((400.,.5,0.),),8000,800))
            result=reconstruct_spectrogram_wav(src,dst,budget=40)
            self.assertTrue(dst.exists())
            self.assertLessEqual(result['evaluations'],40)
            self.assertLess(result['waveform_mse'],.2)
if __name__=='__main__':unittest.main()
