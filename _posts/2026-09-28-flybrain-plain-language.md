---
title: 'FlyBrain in plain language: what it does and what we already have'
date: 2026-09-28
permalink: /posts/2026/09/flybrain-plain-language/
tags:
  - Neuroscience
  - Data
  - Biohacking
  - Software
---

FlyBrain is a private repo with two parts: data and simulation.

What FlyBrain is
======
**Data.** Answers core biology questions without manual tool-jumping:

- What is this cell type?
- Where is it in the anatomy hierarchy?
- What does it connect to?
- What transmitter family is it associated with?

**Simulation.** Builds controllers from connectome structure, runs them in task environments, and compares behavior against matched controls.

What we already have in data
======
Current data capabilities:

- term/ID resolution across naming variants
- hierarchy lookups for regions and cell classes
- connectivity summaries
- curated + predicted neurotransmitter signals
- dataset-aware comparison views

Current lanes: FlyWire/Hemibrain-derived flows plus BANC, L1EM, FAFB, MC, MV, and OL.

How the sim actually runs
======
Execution path:

1. Build or sample a circuit graph from a genome/connectome representation
2. Convert it to a bounded recurrent dynamics model
3. Project observations into sensory nodes and read actions from motor/descending nodes
4. Run episodes in body adapters with explicit reward/termination logic
5. Compare outcomes against strict controls and held-out evaluation slices

Mechanics: normalized adjacency, transmitter-aware inhibitory sign handling, `tanh` state updates, clipped action outputs, step-wise closed-loop episodes.

What this means
======
This is a usable pipeline, not a demo:

- answer structural/circuit questions from integrated data
- run controllers in simulation repeatedly
- reject weak wiring ideas under controlled evaluation

Applications
======
1. Faster hypothesis generation for circuit questions
2. Cleaner experiment planning with less naming friction
3. Reproducible dataset-to-sim runs
4. Better communication of technical results to mixed audiences

Private repo for now, public-friendly explanations here.
