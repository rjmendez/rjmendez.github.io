---
layout: single
title: "BMA360, Part 5: Testing the Tracker on Generated Bearings"
excerpt: "The hub tracker gets debugged against bearings the harness makes up. Everything in this post is simulation."
tags:
  - Simulation
  - Tracking
  - BMA360
---

Birds are bad test fixtures. They never fly the same path twice, and when a track falls apart there is no way to replay it and see whether the cause was a missed detection, a bad clock, a wrong array pose or the association code in the hub.

So the hub tracker gets tested against made-up bearings first. The firmware tree has a harness for this in `bench-kit/bma-audiod/hub/sim/`. It generates bearing records for a set of scenarios, feeds them into the fusion tracker, scores the same reports with baselines, and writes a report with per-seed values and 95% confidence intervals. The docstring in `run_eval.py` calls it a report generator, not a test.

From `bench-kit/bma-audiod`:

```
python -I hub/sim/run_eval.py --seeds 30 --out hub/sim/reports/fleet_eval.json --jobs 1
```

With `--seeds 30` the evaluation seeds are 0..29. Adding `--tuning` uses 1000..1029 instead, so tuning doesn't happen on the same seeds that get scored. The scenario, config and seed set go into the report next to the numbers, which means a tracker change can be rerun on identical input and diffed.

Position error is reported twice. One number only counts steps where the track is within 20 m of the true target; the other drops that cutoff. Coverage goes alongside both. The cutoff version on its own looks great on a tracker that keeps the easy steps and loses the source on the hard ones, so the uncensored error and coverage are the ones to read first.

Every number that comes out of this is SIMULATED. The generator made the targets, so it knows the truth and can score against it. What it can check is how the tracker behaves under the bearings, clock offsets, noise levels and report patterns it was told to assume. It has no way of knowing whether the BMA360's eight channels are raw microphones or processed beams (Part 3), whether the mic map is right, or whether a bearing from an actual array lands anywhere near a bird. A good score here says the tracker copes with the model. The acoustic camera is untested by it.

I'm not publishing scores from it in this post. The run worth reporting is the one with measured bearings, and Part 6 covers what's still in the way of that.

Source: private [`hub/sim/run_eval.py`](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/hub/sim/run_eval.py) at `dcde9a1`.