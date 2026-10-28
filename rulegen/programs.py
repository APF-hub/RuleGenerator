"""Portable, typed, declarative program representation for observation models.

Program documents contain only JSON values, operator names and explicit
configuration. Runtime implementations live in a separate operator catalog.
No observed samples are embedded in the executable program.
"""
import json
import math
from dataclasses import dataclass

NUMBER = "Number"
SIGNAL = "Signal"
CONFIG = "Config"

@dataclass(frozen=True)
class Operator:
    name: str
    inputs: tuple
    output: str
    implementation: object

class Catalog:
    def __init__(self):
        self.operators = {}
    def register(self, name, inputs, output, implementation):
        if name in self.operators:
            raise ValueError("duplicate operator: " + name)
        self.operators[name] = Operator(name, tuple(inputs), output, implementation)
    def infer(self, node):
        if not isinstance(node, dict):
            raise TypeError("program nodes must be objects")
        tag = node.get("op")
        if tag == "number":
            value = node.get("value")
            if type(value) not in (int, float) or not math.isfinite(value):
                raise TypeError("invalid numeric literal")
            return NUMBER
        if tag == "config":
            if not isinstance(node.get("key"), str):
                raise TypeError("configuration key must be a string")
            return NUMBER
        if tag not in self.operators:
            raise TypeError("unknown operator: " + str(tag))
        entry = self.operators[tag]
        args = node.get("args")
        if not isinstance(args, list) or len(args) != len(entry.inputs):
            raise TypeError("operator arity mismatch")
        for arg, expected in zip(args, entry.inputs):
            if self.infer(arg) != expected:
                raise TypeError("operator input type mismatch")
        return entry.output
    def execute(self, node, config, *, rate, length):
        self.infer(node)
        if not isinstance(config, dict) or rate <= 0 or length < 0:
            raise ValueError("invalid execution configuration")
        def run(n):
            tag = n["op"]
            if tag == "number":
                return float(n["value"])
            if tag == "config":
                key = n["key"]
                if key not in config:
                    raise KeyError("missing configuration: " + key)
                val = config[key]
                if type(val) not in (int, float) or not math.isfinite(val):
                    raise TypeError("configuration value must be finite numeric")
                return float(val)
            return self.operators[tag].implementation(
                *(run(a) for a in n["args"]), rate=rate, length=length)
        return run(node)

def number(value):
    return {"op":"number","value":float(value)}

def config(name):
    return {"op":"config","key":name}

def call(name, *args):
    return {"op":name,"args":list(args)}

def encode(program):
    return json.dumps(program,sort_keys=True,separators=(",",":"),allow_nan=False)

def decode(serialized, catalog):
    program = json.loads(serialized)
    catalog.infer(program)
    return program

def audio_catalog():
    import numpy as np
    catalog = Catalog()
    def oscillator(frequency, amplitude, phase, *, rate, length):
        t = np.arange(length, dtype=float)/rate
        return (amplitude*np.sin(2*np.pi*frequency*t+phase)).tolist()
    def mix(a,b,*,rate,length):
        return [x+y for x,y in zip(a,b)]
    def gate(signal,start,end,*,rate,length):
        begin=max(0,min(length,int(round(start*rate))))
        finish=max(begin,min(length,int(round(end*rate))))
        return [v if begin<=i<finish else 0.0 for i,v in enumerate(signal)]
    def silence(*,rate,length):
        return [0.0]*length
    catalog.register("oscillator",(NUMBER,NUMBER,NUMBER),SIGNAL,oscillator)
    catalog.register("mix",(SIGNAL,SIGNAL),SIGNAL,mix)
    catalog.register("gate",(SIGNAL,NUMBER,NUMBER),SIGNAL,gate)
    catalog.register("silence",(),SIGNAL,silence)
    return catalog

def audio_events_program(events, rate):
    """Compile M73 event tuples into a portable typed expression."""
    expression=call("silence")
    for frequency, amplitude, phase, start, end in events:
        if not 0 <= start < end:
            raise ValueError("invalid event interval")
        event=call("gate",call("oscillator",number(frequency),
                              number(amplitude),number(phase)),
                   number(start/rate),number(end/rate))
        expression=call("mix",expression,event)
    audio_catalog().infer(expression)
    return expression

def audio_sines_program(oscillators):
    expression=call("silence")
    for frequency, amplitude, phase in oscillators:
        expression=call("mix",expression,
                        call("oscillator",number(frequency),
                             number(amplitude),number(phase)))
    audio_catalog().infer(expression)
    return expression
