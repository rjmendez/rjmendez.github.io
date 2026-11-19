---
layout: single
title: "BMA360, Part 5: The Tracker in a World I Made Up"
excerpt: "Generated bearings let the hub face controlled scenarios and baselines. They are useful for debugging the tracker—and cannot tell us whether the microphones work."
tags:
  - Simulation
  - Tracking
  - BMA360
---

A tracker is hard to debug with birds. They do not fly the same path twice, and when a track breaks it is rarely obvious whether the cause was a missed detection, a bad clock, a wrong pose, or the association logic.

The project has a generated-bearing harness for that part of the problem. It builds repeatable target scenarios, feeds reports into the hub tracker, varies timing and report uncertainty, and compares results with baselines. The seeds and per-seed values make a software change testable without asking a bird to repeat a trajectory on demand.

The harness is not hand-waving. It records the scenario, config, seed set, per-seed scores and 95% confidence intervals. It distinguishes tuning seeds from evaluation seeds. It reports position error both with a 20 m matching cutoff and without that censoring, alongside coverage. These choices matter: a low error calculated only on the easy matched steps can hide the steps where the tracker lost the source.

That is exactly what a simulation is for. It is also exactly where its authority ends.

The generator already knows the target truth it created. It can tell us whether the tracker handles those assumed bearings, clocks, noise levels and report patterns. It cannot tell us whether the BMA360's eight channels are raw microphones, whether the microphone map is correct, or whether a real bearing lands on a real bird. A strong result in this harness would be evidence about the tracker under that model, not about the acoustic camera in the field.

I want this harness in the story because it is useful engineering, not because it gives the project a victory lap. It lets us find out whether the hub can handle difficult reports before we feed it real ones. When the report says "go," the next question is still: go on what data?

Source: private [`hub/sim/run_eval.py`](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/hub/sim/run_eval.py). Its own docstring calls it a report generator, not a test. No result from this simulation is presented here as a live measurement.
