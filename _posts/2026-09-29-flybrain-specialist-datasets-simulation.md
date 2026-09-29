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

This is the deeper technical follow-up to the plain-language FlyBrain update.

The repo is still private, but the architecture and findings are useful to share publicly.

Scope
======
FlyBrain currently has two tightly-coupled lanes:

1. **Data lane** for ontology + connectome integration and queryable summaries
2. **Simulation lane** for evaluating connectome-derived controllers under controlled conditions

The key change from earlier iterations is that the two lanes now share stricter provenance and evaluation gates, so data preparation and simulation outcomes can be compared reproducibly.

Datasets now in active coverage
======
Recent code expanded adapter/sample support beyond the initial path to include:

- **FlyWire / Hemibrain-derived lanes** (existing baseline)
- **BANC**
- **L1EM**
- **FAFB**
- **MC**
- **MV**
- **OL**

The practical effect is less hand-built one-off glue and more standardized transforms into a common training/evaluation interface.

Methodology updates
======
Recent methodology hardening focused on reducing false confidence:

- Added stronger **dataset registry** handling so each lane has explicit bookkeeping
- Added **grouped split strategy** updates to reduce leakage between related examples
- Added **hash-stamped data artifacts** for repeatability checks
- Added stricter trivial-baseline gating before claiming progress

Net result: if we rerun a given experiment configuration, we can now verify we are actually testing the same underlying slices/artifacts.

Simulation updates
======
Recent simulation work added:

- A **circuit dynamics engine** for executing grown circuits over time
- A **C. elegans locomotion body adapter** (obs=8, action=4)
- **Reward functions + episode simulation** integrated into the body-adapter test path

This shifts evaluation from static snapshot checks toward temporal behavior checks (episode return, step-wise control quality, and stability over trajectories).

Current read on results
======
The conservative interpretation is still the right one:

- The data lane is already productive for structured lookups and cross-checking.
- The simulation lane is improving in rigor and instrumentation.
- Connectome-derived wiring is still held to strict matched-control comparisons before we call anything a win.

Applications right now
======
What this is good for today:

1. Building and testing circuit hypotheses faster
2. Running reproducible dataset-to-simulation pipelines
3. Comparing lane behavior across multiple connectome sources
4. Sharing results in plain language without dropping methodological guardrails

If you only care about outcomes: we now have better data coverage, tighter methodology, and more realistic simulation mechanics than we had even a short time ago.
