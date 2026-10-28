"""Durable capability tests for portable executable program documents."""
import json
import math
import unittest
from rulegen.programs import (audio_catalog,audio_events_program,
                              audio_sines_program,call,config,number,encode,decode)

class ProgramDocumentTests(unittest.TestCase):
    def test_sine_legacy_equivalence(self):
        from rulegen.audio import render
        events=((437.5,.3,.1),(656.25,.2,-.3))
        document=audio_sines_program(events)
        reconstructed=audio_catalog().execute(decode(encode(document),audio_catalog()),
                                              {},rate=8000,length=512)
        expected=render(events,8000,512)
        self.assertLess(max(abs(x-y) for x,y in zip(reconstructed,expected)),1e-12)

    def test_event_legacy_equivalence(self):
        from rulegen.residual import ResidualAudioAdapter
        events=((437.5,.3,.1,0,256),(656.25,.2,-.3,256,512))
        document=audio_events_program(events,8000)
        generated=audio_catalog().execute(document,{},rate=8000,length=512)
        expected=ResidualAudioAdapter(8000).execute(events,[0]*512)
        self.assertLess(max(abs(x-y) for x,y in zip(generated,expected)),1e-12)

    def test_config_driven_program_generalizes(self):
        program=call("oscillator",config("frequency"),config("amplitude"),number(0))
        catalog=audio_catalog()
        a=catalog.execute(program,{"frequency":220,"amplitude":.4},rate=8000,length=128)
        b=catalog.execute(program,{"frequency":440,"amplitude":.4},rate=8000,length=128)
        self.assertNotEqual(a,b)
        self.assertEqual(decode(encode(program),catalog),program)

    def test_typecheck_rejects_invalid_ast(self):
        catalog=audio_catalog()
        with self.assertRaises(TypeError):
            catalog.infer(call("mix",number(1),call("silence")))
        with self.assertRaises(TypeError):
            catalog.infer(call("unknown"))
        with self.assertRaises(TypeError):
            catalog.infer({"op":"number","value":True})

    def test_missing_configuration_fails(self):
        with self.assertRaises(KeyError):
            audio_catalog().execute(config("frequency"),{},rate=8000,length=64)

    def test_program_has_no_embedded_observations(self):
        program=audio_events_program(((440,.3,0,0,100),),8000)
        text=encode(program)
        self.assertNotIn("samples",text)
        self.assertNotIn("waveform",text)
        self.assertEqual(audio_catalog().infer(program),"Signal")
if __name__=="__main__":unittest.main()
