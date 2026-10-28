"""Audio adapter: WAV observations and compositional sinusoidal programs.

This is a deliberately bounded starter grammar, not unrestricted music
transcription. Program representation is an executable list of oscillators.
"""
import math
import wave
import struct
from pathlib import Path

TAU = 2 * math.pi

def load_wav(path):
    with wave.open(str(path), 'rb') as w:
        if w.getcomptype() != 'NONE' or w.getsampwidth() != 2:
            raise ValueError('only uncompressed 16-bit PCM WAV supported')
        rate, channels, n = w.getframerate(), w.getnchannels(), w.getnframes()
        samples = struct.unpack('<' + 'h' * (n * channels), w.readframes(n))
    return rate, [sum(samples[i:i+channels]) / (32768 * channels) for i in range(0, len(samples), channels)]

def save_wav(path, rate, samples):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        values = [max(-32768, min(32767, round(x * 32767))) for x in samples]
        w.writeframes(struct.pack('<' + 'h' * len(values), *values))

def render(program, rate, length):
    return [sum(a * math.sin(TAU * f * i / rate + phase) for f, a, phase in program)
            for i in range(length)]

class SineAdapter:
    def __init__(self, rate, *, min_freq=50, max_freq=2000, components=3):
        self.rate = rate
        self.min_freq = min_freq
        self.max_freq = min(max_freq, rate / 2)
        self.components = components
    def key(self, program):
        return tuple(tuple(round(float(x), 7) for x in oscillator) for oscillator in program)
    def initial(self, samples):
        n = len(samples)
        if not n:
            raise ValueError('empty audio')
        # Spectral candidates from the observations, not an expected answer.
        step = max(1, n // 512)
        decimated = samples[::step]
        effective_rate = self.rate / step
        size = len(decimated)
        resolution = effective_rate / size
        candidates = []
        for bin_id in range(max(1, int(self.min_freq / resolution)),
                            min(size // 2, int(self.max_freq / resolution) + 1)):
            freq = bin_id * resolution
            real = sum(v * math.cos(TAU * bin_id * i / size) for i, v in enumerate(decimated))
            imag = -sum(v * math.sin(TAU * bin_id * i / size) for i, v in enumerate(decimated))
            magnitude = math.hypot(real, imag)
            amplitude = min(1.0, 2 * magnitude / size)
            phase = math.atan2(real, -imag)
            candidates.append((magnitude, (freq, amplitude, phase)))
        candidates.sort(reverse=True)
        self.peaks = [c for _, c in candidates[:min(10, len(candidates))]]
        return [(peak,) for peak in self.peaks[:5]] or [((440.0, 0.0, 0.0),)]
    def execute(self, program, samples):
        return render(program, self.rate, len(samples))
    def loss(self, samples, generated):
        return sum((x-y)**2 for x, y in zip(samples, generated)) / len(samples)
    def refine(self, program, samples, generated):
        for index, (freq, amp, phase) in enumerate(program):
            for delta in (-4, -1, 1, 4):
                f = freq + delta
                if self.min_freq <= f <= self.max_freq:
                    child = list(program)
                    child[index] = (f, amp, phase)
                    yield tuple(child)
            for factor in (0.75, 1.25):
                child = list(program)
                child[index] = (freq, min(1.0, amp * factor), phase)
                yield tuple(child)
            for delta in (-0.25, 0.25):
                child = list(program)
                child[index] = (freq, amp, phase + delta)
                yield tuple(child)
        if len(program) < self.components:
            for peak in self.peaks:
                if all(abs(peak[0]-p[0]) > 3 for p in program):
                    yield program + (peak,)

def reconstruct_wav(source, destination, *, budget=300, components=3):
    from .reconstruct import search
    rate, samples = load_wav(source)
    adapter = SineAdapter(rate, components=components)
    result = search(samples, adapter, budget=budget)
    save_wav(destination, rate, adapter.execute(result.program, samples))
    return {'program':result.program, 'mse':result.loss,
            'evaluations':result.evaluations, 'history':result.history,
            'rate':rate, 'samples':len(samples)}
