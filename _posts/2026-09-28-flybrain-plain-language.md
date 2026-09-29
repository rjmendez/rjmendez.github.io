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

I have been building out a private FlyBrain repo and wanted a plain-English update instead of a wall of backend details.

Inspiration
======
Brains are complicated enough without making the tooling complicated too. The goal here is simple: make it easy to ask practical questions about fly brain structure and circuits, and get useful answers without needing to be a specialist in every database format.

What FlyBrain is (without the jargon)
======
Think of it as a translator and organizer between different kinds of neuroscience data. It helps answer things like:

- What type of neuron is this?
- What region is it part of?
- What does it connect to?
- What neurotransmitter is it likely using?

Instead of manually hopping between multiple tools, we can run one workflow and keep results in a consistent format.

What data we already have from it
======
At this point we already have usable data flowing for:

- **Term and ID resolution** (finding the right entity even when names/synonyms differ)
- **Hierarchy data** (parent/child relationships for neuron classes and brain regions)
- **Connectivity summaries** (who talks to who, with dataset-aware views)
- **Neurotransmitter information** (both curated known labels and prediction-based outputs)
- **Cross-dataset comparisons** (so we can spot agreement/disagreement instead of trusting one source blindly)

In other words: we are past "toy demo" stage and already using it for real lookups and cross-checks.

Applications
======
The most immediate applications are:

1. Faster hypothesis building (especially for circuit questions)
2. Cleaner experiment planning (less time lost resolving terminology)
3. Better communication (plain summaries for mixed technical/non-technical teams)
4. Reproducible data pulls (same query pattern, same output shape)

Longer term, this also gives us a solid base for automation and model-assisted analysis without turning everything into a giant one-off script.

Where this is headed next
======
The next focus is reliability and repeatability: keep the query layer stable, keep outputs easy to read, and keep the pipeline practical for day-to-day use.

Private repo for now, public-friendly explanations here.
