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

FlyBrain is a private repo with two parts: a data layer, and an experimental brain-growing layer.

What FlyBrain is
======
**Data layer.** Integrates neuroscience datasets so a question like "what is this neuron, what does it connect to, what neurotransmitter does it use" doesn't require hopping between tools by hand.

**Brain-growing layer.** Builds small neural-network controllers whose wiring is derived from real fly connectome data (FlyWire, the hemibrain), and tests whether that wiring gives them any advantage over an equivalent random network of the same size.

What the data layer already does
======
- Term and ID resolution across datasets (same entity, different names)
- Hierarchy data (neuron class / brain region parent-child relationships)
- Connectivity summaries, grounded in FlyWire (139,255 neurons, 3.7M+ connections) and the hemibrain (21,739 neurons, 3.55M weighted edges)
- Neurotransmitter data (curated labels and prediction-based outputs)
- Cross-dataset comparison

In production use for lookups and cross-checks, not a demo.

What the brain-growing layer has shown so far
======
Result: none of the grown or evolved controllers built so far beat a size- and budget-matched random network on held-out tests. Zero of 20 in the latest realism check.

What changed as a result:

- Every wiring claim now requires four matched controls (random sparse, degree-scrambled, dense random, small MLP), not a bare "better than nothing" comparison.
- Evaluation runs against a held-out animal and held-out statistics, not the data the model was fit on.
- The significance test behind these comparisons had a real bug: it falsely rejected a true null result more often than its stated rate. Replaced.
- The simulated test environment had a sensor giving an exact, noiseless bearing to the goal — effectively a cheat. Removed.

Applications
======
Current, on the data layer:

1. Faster hypothesis building for circuit questions
2. Less time lost resolving terminology during experiment planning
3. Plain summaries for mixed technical/non-technical teams
4. Reproducible data pulls: same query, same output shape

Contingent on the brain-growing layer clearing its own held-out bar: a path to model-assisted analysis grounded in real connectome structure, not just architecture that resembles one.

Next
======
Data layer: keep the query layer stable, keep output easy to read. Brain-growing layer: keep running it against held-out tests until it shows a real, repeatable advantage, or doesn't.

Private repo for now, public-friendly explanations here.
