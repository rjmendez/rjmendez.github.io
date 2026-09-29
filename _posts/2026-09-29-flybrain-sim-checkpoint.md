---
title: 'FlyBrain simulation: architecture and evaluation'
date: 2026-09-29
permalink: /posts/2026/09/flybrain-sim-checkpoint/
tags:
  - Simulation
  - Neuroscience
  - Data
  - Biohacking
  - Software
---

This post describes the current simulation stack in concrete terms.

Simulation architecture
======
The sim layer has three parts:

1. **Circuit dynamics**
   - recurrent rate-model execution over connectome-derived adjacency
   - normalized weights, inhibitory sign handling (`gaba`, `octopamine`)
   - bounded hidden state update (`tanh`) and clipped action output

2. **Role projections**
   - observation projected to sensory neurons
   - action readout projected from motor/descending neurons
   - deterministic fallback indexing when role labels are missing

3. **Body adapters**
   - closed-loop `reset -> step -> reward -> done` execution
   - vector-action path for episode simulation
   - task-specific observation/reward definitions

Task environments
======
- **Radio source seeking**
  - observation includes position, source bearing terms, signal, and previous movement
  - reward increases when distance-to-source decreases
  - terminal bonus on arrival

- **C. elegans locomotion**
  - compact obs/action interface (`obs=8`, `action=4`)
  - one-dimensional locomotion reward in vector-action mode
  - legacy biomechanical step path retained for discrete-action tests

Evaluation protocol
======
- episode rollouts with accumulated return
- deterministic reset path via seeds
- shape/bounds checks in unit tests
- control comparisons against matched non-connectome baselines

Data dependencies
======
Simulation currently runs against standardized dataset lanes:

- FlyWire/Hemibrain-derived flows
- BANC, L1EM, FAFB
- MC, MV, OL

These are wired through registry + grouped split + hash-stamped artifacts so runs are reproducible.

Current status
======
- The stack can execute connectome-derived controllers end-to-end in episodes.
- The instrumentation is good enough to reject weak results quickly.
- Claims remain gated by held-out controls; no free passes.
