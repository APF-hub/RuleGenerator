# Roadmap: platform-first stabilization

Status labels: DONE = merged capability; PARTIAL = interface exists but
missing production guarantees; PLANNED = not implemented.

| Track | Workstream | State | Next acceptance gate |
| --- | --- | --- | --- |
| P | Python 3.12 CI and PR-first workflow | DONE (policy; branch protection unverified) | Enforce required checks in repository ruleset |
| P | Common experiment result protocol | PARTIAL (M78) | Versioned schema and compatibility tests |
| P | Shared evidence storage | PARTIAL (M79) | Atomic transaction and migration tests |
| P | Common operator lifecycle facade | PARTIAL (M80) | Backend-independent contract tests |
| P | Provenance manifests and accounting | PARTIAL (M81) | Integrate with admission; instrument costs |
| P | Resource bounds and error handling | PLANNED | No unbounded generation; deterministic failures |
| P | Schema migrations, backup and recovery | PLANNED | Upgrade/downgrade policy, crash recovery tests |
| C | Legacy typed synthesis and learned operator reuse | DONE (existing) | Preserve behavior while integrating |
| C | Functional AST and anti-unification | DONE (M74-M75) | Adversarial validation and type coverage |
| C | Functional promotion and reuse | DONE (M76-M77) | Shared lifecycle, independent evidence |
| C | End-to-end autonomous learning pipeline | PLANNED | No manual operator insertion; held-out gate |
| E | Historical M68/M69 cumulative transfer | PRESERVED | Reproduce with pinned revision and seeds |
| E | Acquisition-inclusive multi-family transfer | PLANNED | Negative controls and matched total budgets |

## Release sequencing

1. **P1 platform integrity:** atomic promotion/evidence, schema/version tests,
   recovery, PR checks. Do not begin a new synthesis engine.
2. **P2 execution integrity:** bounded enumeration, explicit compute accounting,
   typed backend contract tests.
3. **C1 learning orchestration:** discovery -> validation -> admission -> reuse
   with provenance enforcement.
4. **E1 research:** run acquisition-inclusive matched-total-budget experiments;
   publish outcomes and limitations separately.
5. **Decision:** only promote generalizable findings into supported capabilities
   through reviewed C/P PRs.

Every roadmap update must state whether an item is an engineering deliverable,
a capability contract, or a research hypothesis.
