# P5 evaluation-budget contract

The shared learning protocol now requires positive integer evaluation budgets and AST node limits and checks that backend-reported candidate checks never exceed the requested budget. The matched-total-budget comparison deducts caller-supplied acquisition checks from the warm search allowance, including the case where no warm evaluation remains.

This is an evaluation-count contract, not a wall-clock, CPU, memory or cancellation guarantee. Acquisition costs are supplied by the caller and explicitly labeled unmeasured. The current synthesizers may still allocate substantial candidate pools before evaluation; bounding enumeration memory and cooperative cancellation remain open platform gates.
