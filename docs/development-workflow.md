# Contribution and CI workflow

All future RuleGenerator development should use short-lived branches and pull
requests. Do not commit directly to `main`.

1. Create a branch from `main` for each bounded change.
2. Commit implementation and capability regression tests together.
3. Open a pull request targeting `main`.
4. Wait for the Python 3.11 and 3.12 capability jobs to finish.
5. On failure, retrieve the failed workflow job logs, reproduce where possible,
   repair on the same branch, and repeat until checks pass.
6. Merge only after required checks pass. Report the exact CI run and commit.
7. Keep experimental benchmarks outside the mandatory capability test suite;
   do not delete regression tests merely to make CI pass.

Repository administrator: enable branch protection or a ruleset for `main`,
require a pull request, and select the exact required check names shown by the
Actions matrix. GitHub permissions and repository rules may require manual
administrator setup.

## Existing baseline

The first functional-core and abstraction commits were pushed directly to
`main` before this policy was adopted. The initial PR using this policy
cannot retroactively verify those commits as an isolated change. Repair
baseline failures separately and track them as evidence.

## Validation integrity

A discovered operator must remain a candidate until independent validation
and evidence-based promotion. Manually registered operator definitions and
reference audio primitives must not be counted as discoveries.
