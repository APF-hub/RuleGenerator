"""Residual-guided structural discovery of audio events.

Proposals are inferred from unexplained waveform energy; the generic search
controller evaluates and selects executable hypotheses.
"""
import numpy as np
from .spectrogram import SpectrogramAudioAdapter

class ResidualAudioAdapter(SpectrogramAudioAdapter):
    """Events: (frequency, amplitude, phase, start_sample, end_sample)."""
    def __init__(self, rate, *, max_events=5, **kwargs):
        super().__init__(rate, **kwargs)
        self.max_events=max_events

    def initial(self, samples):
        return [tuple()]

    def execute(self, program, samples):
        n=len(samples)
        times=np.arange(n)/self.rate
        output=np.zeros(n)
        for f,a,p,start,end in program:
            if not (0<=start<end<=n):
                raise ValueError('invalid event interval')
            output[start:end]+=a*np.sin(2*np.pi*f*times[start:end]+p)
        return output.tolist()

    def _proposals(self, residual):
        n=len(residual)
        if n<32:return
        widths=sorted(set([n,max(64,n//2),max(64,n//4)]))
        ranked=[]
        for width in widths:
            if width>n:continue
            starts=sorted(set(range(0,n-width+1,max(1,width//2)))|{n-width})
            for start in starts:
                chunk=np.asarray(residual[start:start+width],dtype=float)
                spectrum=np.fft.rfft(chunk*np.hanning(width))
                freqs=np.fft.rfftfreq(width,1/self.rate)
                eligible=np.flatnonzero((freqs>=self.min_freq)&(freqs<=self.max_freq))
                if not len(eligible):continue
                peaks=eligible[np.argsort(np.abs(spectrum[eligible]))[-3:]]
                for bin_id in peaks:
                    f=float(freqs[bin_id])
                    t=np.arange(start,start+width)/self.rate
                    basis=np.column_stack((np.sin(2*np.pi*f*t),np.cos(2*np.pi*f*t)))
                    coefs=np.linalg.lstsq(basis,chunk,rcond=None)[0]
                    amplitude=float(np.hypot(*coefs))
                    if amplitude<1e-4:continue
                    phase=float(np.arctan2(coefs[1],coefs[0]))
                    gain=float(np.dot(basis@coefs,basis@coefs))
                    ranked.append((gain,(f,amplitude,phase,start,start+width)))
        ranked.sort(key=lambda item:item[0],reverse=True)
        seen=set()
        for _,event in ranked:
            key=(round(event[0]),event[3],event[4])
            if key not in seen:
                seen.add(key)
                yield event
                if len(seen)>=12:return

    def refine(self, program, samples, generated):
        residual=np.asarray(samples)-np.asarray(generated)
        if len(program)<self.max_events:
            for event in self._proposals(residual):
                yield program+(event,)
        for i,(f,a,p,start,end) in enumerate(program):
            for df in (-2.,-0.5,0.5,2.):
                if self.min_freq<=f+df<=self.max_freq:
                    child=list(program)
                    child[i]=(f+df,a,p,start,end)
                    yield tuple(child)
            for factor in (0.8,1.2):
                child=list(program)
                child[i]=(f,a*factor,p,start,end)
                yield tuple(child)

def reconstruct_residual_wav(source,destination,*,budget=150,max_events=5,database=None):
    from .audio import load_wav,save_wav
    from .reconstruct import search
    rate,observed=load_wav(source)
    adapter=ResidualAudioAdapter(rate,max_events=max_events,waveform_weight=1)
    result=search(observed,adapter,budget=budget)
    save_wav(destination,rate,adapter.execute(result.program,observed))
    experiment_id=None
    if database is not None:
        from .experiments import ExperimentStore
        with ExperimentStore(database) as store:
            experiment_id=store.record('audio.residual_events.v1',[rate,observed],result,budget)
    return dict(program=result.program,mse=result.loss,evaluations=result.evaluations,
                history=result.history,experiment_id=experiment_id)
