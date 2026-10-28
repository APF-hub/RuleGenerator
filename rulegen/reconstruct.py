"""Generic budgeted executable-hypothesis search with a domain adapter.

The controller knows only candidates, execution, loss, refinements and budget.
Audio-specific models are defined in audio.py.
"""
from dataclasses import dataclass
import heapq
import itertools

@dataclass
class Result:
    program: object
    loss: float
    evaluations: int
    history: list

def search(observation, adapter, budget=1000, beam=12):
    if budget < 1 or beam < 1:
        raise ValueError('budget and beam must be positive')
    serial = itertools.count()
    pending = []
    visited = set()
    history = []
    best = None
    evaluations = 0
    def enqueue(candidate, priority):
        key = adapter.key(candidate)
        if key not in visited:
            visited.add(key)
            heapq.heappush(pending, (priority, next(serial), candidate))
    for candidate in adapter.initial(observation):
        enqueue(candidate, 0.0)
    while pending and evaluations < budget:
        _, _, candidate = heapq.heappop(pending)
        try:
            generated = adapter.execute(candidate, observation)
            loss = float(adapter.loss(observation, generated))
        except (ArithmeticError, ValueError, TypeError):
            continue
        evaluations += 1
        if not (loss >= 0 and loss < float('inf')):
            continue
        if best is None or loss < best.loss:
            best = Result(candidate, loss, evaluations, history)
            history.append({'evaluation':evaluations, 'loss':loss, 'program':candidate})
        for child in adapter.refine(candidate, observation, generated):
            enqueue(child, loss)
        if len(pending) > beam * 30:
            pending = heapq.nsmallest(beam * 15, pending)
            heapq.heapify(pending)
    if best is None:
        raise ValueError('no valid hypothesis')
    best.evaluations = evaluations
    return best
