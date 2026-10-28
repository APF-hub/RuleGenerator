"""Spectrogram observation view and multi-representation audio objective."""
import numpy as np
from .audio import SineAdapter

def stft_magnitude(samples, *, window=256, hop=64):
    """Hann-windowed, nonnegative STFT magnitude, frames x frequency bins."""
    if window < 8 or hop < 1:
        raise ValueError('invalid STFT geometry')
    x = np.asarray(samples, dtype=float)
    if x.ndim != 1 or not len(x) or not np.all(np.isfinite(x)):
        raise ValueError('audio must be a finite nonempty mono signal')
    if len(x) < window:
        x = np.pad(x, (0, window-len(x)))
    frames = np.lib.stride_tricks.sliding_window_view(x, window)[::hop]
    return np.abs(np.fft.rfft(frames * np.hanning(window), axis=-1)) / (window / 2)

def spectrogram_image(samples, *, window=256, hop=64, floor_db=-80):
    """Display-only 8-bit grayscale image. Do not use this quantization for loss."""
    mag = stft_magnitude(samples, window=window, hop=hop)
    db = 20 * np.log10(np.maximum(mag, 1e-10))
    return np.uint8(np.rint(np.clip((db-floor_db) * 255 / (-floor_db), 0, 255)).T[::-1])

class SpectrogramAudioAdapter(SineAdapter):
    """Same executable program search, weighted waveform and spectral evidence."""
    def __init__(self, rate, *, waveform_weight=0.5, window=256, hop=64, **kwargs):
        super().__init__(rate, **kwargs)
        if not 0 <= waveform_weight <= 1:
            raise ValueError('waveform_weight must be in [0,1]')
        self.waveform_weight = waveform_weight
        self.window, self.hop = window, hop
        self._reference = None
        self._reference_id = None

    def loss(self, samples, generated):
        a, b = np.asarray(samples), np.asarray(generated)
        waveform = float(np.mean((a-b)**2))
        if self.waveform_weight == 1:
            return waveform
        if self._reference_id != id(samples):
            self._reference = stft_magnitude(a, window=self.window, hop=self.hop)
            self._reference_id = id(samples)
        predicted = stft_magnitude(b, window=self.window, hop=self.hop)
        spectral = float(np.mean((self._reference-predicted)**2))
        return self.waveform_weight * waveform + (1-self.waveform_weight) * spectral

def reconstruct_spectrogram_wav(source, destination, *, budget=300, components=3,
                                 waveform_weight=0.5, database=None):
    from .audio import load_wav, save_wav
    from .reconstruct import search
    rate, samples = load_wav(source)
    adapter = SpectrogramAudioAdapter(rate, components=components,
                                      waveform_weight=waveform_weight)
    result = search(samples, adapter, budget=budget)
    output = adapter.execute(result.program, samples)
    save_wav(destination, rate, output)
    waveform_mse = float(np.mean((np.asarray(samples)-np.asarray(output))**2))
    experiment_id = None
    if database is not None:
        from .experiments import ExperimentStore
        with ExperimentStore(database) as store:
            experiment_id = store.record('audio.waveform_spectrogram.v1',
                                         [rate, samples, waveform_weight], result, budget)
    return dict(program=result.program, objective=result.loss,
                waveform_mse=waveform_mse, evaluations=result.evaluations,
                experiment_id=experiment_id)
