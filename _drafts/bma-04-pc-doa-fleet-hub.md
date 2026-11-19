---
layout: single
title: "BMA360 Reproduction, 4: Run the PC DOA Stand-In and Fleet Hub"
excerpt: "Reproduce the host-side stream-to-bearing-to-fleet path while keeping the boundary clear: this is not edge DOA or field-validated tracking."
tags:
  - Python
  - Audio
  - Tracking
  - BMA360
---

The current reproducible software path places DOA on the PC. `pc/bma_doa.py` consumes one unit's BMAA stream and emits array-detection records; `pc/bma_hub.py` consumes those records, fuses them, and writes the fleet feed. The fleet document says the arrays do not yet run this DOA implementation. Reproducing the PC path is useful, but it is not a demonstration of edge processing or validated multi-array accuracy.

## Prerequisites

Use the firmware snapshot pinned in the source links below. Install the kit's declared Python dependencies, deploy the current `hub/`, `pc/` and `ui/` files to the data root, and prepare a registry containing a complete measured microphone map. Use a known BMAA input stream for a controlled run. First resolve the capture-path conflict from Part 3: the status page calls the Dante inputs processed beams, while the fleet page calls them raw microphones.

Start the hub on loopback port 48790:

```text
python -I pc/bma_hub.py --registry <root>/units.json --root <root> --listen 127.0.0.1:48790 --feed <root>/fleet.json
```

With that process listening, start the stand-in for one unit:

```text
python -I pc/bma_doa.py --unit <unit-id> --registry <root>/units.json --listen 127.0.0.1:<doa-port> --out-dir <unit-dir>/analysis --hub 127.0.0.1:48790 --stats-file <unit-dir>/doa_status.json --run-s 30
```

`--run-s 30` bounds the process for a test; omit it for a supervised run. The script writes `doa_status.json` with state, detections, rate, gaps, drops and the gate profile. Exit code 3 is an intentional refusal (for example, missing/incomplete mic map or a derived-port conflict); fix the registry rather than restarting it forever. Exit code 2 indicates bad arguments, registry, or gate profile.

For the owner's supervisor-driven path, create the `enable_doa.txt` marker in the data root and restart `run_pipeline.ps1`. The supervisor starts a DOA child only for units with a complete map and starts one hub when at least one DOA child is active. Check `logs/doa_<id>.log`, `logs/hub.log`, `doa_status.json`, and the freshness of `fleet.json`; a stale or absent feed is not a tracking result.

## Keep quality labels intact

The gate-profile guide documents a two-array proof-of-concept profile called `poc-2array-1.5m`. Its `best_available` setting publishes weak estimates with quality labels rather than hiding them. That makes debugging more informative; it does not increase evidence quality. A weak, range-unobservable track remains weak. Preserve the quality, covariance, detection rate, packet gaps and registry provenance in any screenshot or exported result.

Run the integration tests named by the fleet guide when changing this path (`hub/test_gates.py`, UI fleet tests, launcher and supervisor tests). A test that feeds fixtures through the path proves software behavior on those fixtures; it does not establish that live array channels are correctly mapped.

## What this run proves

It proves only the behavior observed in the host-side pipeline for the input stream and registry used. It does not show that the array runs DOA, that the data are raw microphone samples, that source bearings are field accurate, or that the hub can track a real source across calibrated arrays. Those require live, labeled audio and independently surveyed array geometry and timing.

## Source

* [Fleet architecture, setup markers, registry fields, gate profiles and tests](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/docs/fleet.md)
* [`pc/bma_doa.py` launcher and refusal semantics](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/pc/bma_doa.py)
* [`pc/bma_hub.py` launcher](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/pc/bma_hub.py)
