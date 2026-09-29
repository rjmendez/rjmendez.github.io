---
title: 'FlyBrain specialist update: datasets, methodology, and simulation'
date: 2026-09-29
permalink: /posts/2026/09/flybrain-specialist-datasets-simulation/
tags:
  - Neuroscience
  - Data
  - Simulation
  - Biohacking
  - Software
---

Specialist summary of the current FlyBrain data+sim methodology.

Scope
======
FlyBrain has two coupled lanes:

1. **Data lane** for ontology + connectome integration and queryable summaries
2. **Simulation lane** for evaluating connectome-derived controllers under controlled conditions

Datasets now in active coverage
======
Active adapter/sample coverage:

- **FlyWire / Hemibrain-derived lanes**
- **BANC**
- **L1EM**
- **FAFB**
- **MC**
- **MV**
- **OL**

Data methodology
======
- Dataset registry for explicit lane bookkeeping
- Grouped split strategy to reduce cross-sample leakage
- Hash-stamped artifacts for rerun verification
- Baseline gates before promotion claims

Simulation methodology
======
- Circuit dynamics engine for recurrent execution
- Role-based sensory input / motor output projection
- Neurotransmitter-aware inhibitory sign handling
- Body adapters with episode runners and reward accounting
- C. elegans locomotion adapter (`obs=8`, `action=4`)

Evaluation contract
======
- Held-out evaluation slices
- Matched control families
- Reproducible seeds/artifacts
- Unit-test coverage for dynamics, adapter behavior, and reward paths

Operational use
======
1. Building and testing circuit hypotheses faster
2. Running reproducible dataset-to-simulation pipelines
3. Comparing lane behavior across multiple connectome sources
4. Publishing plain-language outputs without dropping methodological guardrails
