---
layout: single
title: "BMA360 Reproduction, 5: Evaluate the Tracker Without Calling It a Field Test"
excerpt: "The generated-bearing harness is useful for repeatable algorithm comparisons; its outputs are simulation results, not microphone or array validation."
tags:
  - Simulation
  - Tracking
  - Evaluation
  - BMA360
---

The tracker repository includes a generated-bearing evaluation harness. It is a report generator, not a test of the physical Bird Microphone Array. The distinction should appear in the report title, plots, and any summary that leaves the development machine.

## Run a fixed evaluation seed set

From the `bench-kit/bma-audiod` kit root, the documented full invocation is:

```text
python -I hub/sim/run_eval.py --seeds 30 --jobs 1 --out hub/sim/reports/fleet_eval.json
```

The default evaluation seeds are 0 through 29. Use `--jobs 1` for the easiest-to-audit serial run; set `--jobs N` only when parallel execution is desired and record the value. The script writes the report, prints its path and a short SHA-256 prefix, and prints its computed `go` flags.

For tuning, use a separate output file:

```text
python -I hub/sim/run_eval.py --seeds 30 --jobs 1 --tuning --out hub/sim/reports/fleet_tuning.json
```

Tuning uses seeds 1000 through 1029. Do not tune on the evaluation seed set and then present that same set as held-out evaluation. `--quick` is a smoke run with a reduced grid and one scenario; it is not a substitute for the full evaluation.

## Read the report, not just the go flags

The harness records the seed list, config, per-seed values, means and 95% confidence intervals. It includes a two-array range/noise/clock-offset grid, generated scenarios, baseline comparisons, and realism variants such as report-sigma scaling, local-ID churn, staggered reports and unknown classes. Read each cell's configuration and `variant`; do not collapse different generated conditions into one headline.

Pay particular attention to two positional metrics:

* `pos_rmse_h_m` is censored at the 20 m GOSPA assignment cutoff.
* `pos_rmse_h_uncensored_m` is calculated over all late steps with confirmed estimates, and is paired with `uncensored_coverage`.

The uncensored number is not meaningful without its coverage and scenario. Neither metric is a measurement of live array accuracy. The report's `go` booleans are computed from paired simulation rows and statistical comparisons; the script docstring explicitly says they are data, not assertions.

## Reproducibility checklist

Keep the exact commit, command, Python and NumPy versions, seed set, output JSON, and output hash. When comparing a code change, use the same evaluation seeds and config; reserve the 1000-series for tuning. Include confidence intervals and per-seed values, not only a mean. If the run is partial, label it quick/smoke or incomplete.

Finally, keep a strict boundary between this harness and physical acceptance. Synthetic data is appropriate for algorithm behavior under explicit model assumptions and for hardware points where real samples cannot exist, but a synthetic-source pass is not live egress or end-to-end acceptance. Moving from simulation to physical acceptance requires real samples with a measured source path and calibrated geometry.

## Source

* [`hub/sim/run_eval.py`](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/hub/sim/run_eval.py) — seed semantics, scenario grid, metrics and report fields.
* [Fleet guide](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/docs/fleet.md) — live registry and calibration prerequisites.
