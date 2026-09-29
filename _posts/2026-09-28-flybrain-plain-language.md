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

I have been building out a private FlyBrain repo and wanted a plain-English update instead of a wall of backend details. This post replaces an earlier draft that only covered the data side; it now also covers the "grow a brain" side and where that honestly stands.

Inspiration
======
Brains are complicated enough without making the tooling complicated too. The goal here is simple: make it easy to ask practical questions about fly brain structure and circuits, and get useful answers without needing to be a specialist in every database format.

What FlyBrain is (without the jargon)
======
Two things, really.

**The data side** is a translator and organizer between different kinds of neuroscience data. It helps answer things like:

- What type of neuron is this?
- What region is it part of?
- What does it connect to?
- What neurotransmitter is it likely using?

Instead of manually hopping between multiple tools, we can run one workflow and keep results in a consistent format.

**The "grow a brain" side** is more experimental: an attempt to build small neural-network controllers whose wiring is *derived from* real fly connectome data (FlyWire, the hemibrain) rather than just hand-designed, and to test whether that gives them any real advantage over an equivalent random network of the same size. That second half is where a lot of the recent work has gone, and it's also where I've been strictest about not overclaiming — more below.

What data we already have from it
======
At this point we already have usable data flowing for:

- **Term and ID resolution** (finding the right entity even when names/synonyms differ)
- **Hierarchy data** (parent/child relationships for neuron classes and brain regions)
- **Connectivity summaries** (who talks to who, with dataset-aware views), grounded in the real connectomes: FlyWire (139,255 neurons, 3.7M+ connections) and the hemibrain (21,739 neurons, 3.55M weighted edges)
- **Neurotransmitter information** (both curated known labels and prediction-based outputs)
- **Cross-dataset comparisons** (so we can spot agreement/disagreement instead of trusting one source blindly)

In other words: we are past "toy demo" stage and already using it for real lookups and cross-checks.

Where the "grow a brain" work actually stands
======
This is the part I want to be direct about. The honest, current answer is: **not yet proven.** A self-audit run against the grown and evolved controllers found that, so far, none of them beat a size- and budget-matched random network on the tests that would actually show real connectome structure mattering. That's not a failure of the idea, it's just where the evidence is today, and I'd rather say that plainly than round it up.

What's actually changed in response is methodology, not marketing:

- Every wiring claim now has to be compared against four matched controls (random sparse, degree-scrambled, dense random, a plain small network), not just "better than nothing."
- Evaluations run against a *held-out* animal and held-out statistics the model was never fit on, instead of checking the model against the same data it was built from.
- The statistical tests behind these comparisons got a real audit too: the old per-arm significance test was found to falsely reject a true null result more often than it should, and has been replaced.
- The simulated sandbox used to test candidate brains had its food/sensor inputs quietly acting like a "cheat" sense (an exact, noiseless bearing to the goal) — that's been removed so a trained controller has to actually earn its performance.

None of that is glamorous, but it's the difference between a number I can defend and a number that just looks good.

Applications
======
The most immediate applications are still on the data side:

1. Faster hypothesis building (especially for circuit questions)
2. Cleaner experiment planning (less time lost resolving terminology)
3. Better communication (plain summaries for mixed technical/non-technical teams)
4. Reproducible data pulls (same query pattern, same output shape)

Longer term, if the "grow a brain" work clears its own held-out bar, it also gives a path toward automation and model-assisted analysis that's actually grounded in real biology instead of an architecture that merely looks biological.

Where this is headed next
======
Two tracks: keep the data/query layer stable and easy to use day to day, and keep pushing the grown/evolved controllers against harder, fairer, held-out tests until (or unless) they show a real, repeatable advantage. I'd rather report a slower, honest "not yet" than a fast "yes" I can't back up.

Private repo for now, public-friendly explanations here.
