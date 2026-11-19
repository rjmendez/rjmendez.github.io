---
layout: single
title: "BMA360 Reproduction, 6: A Wire Protocol Is Not an Acoustic Camera"
excerpt: "Separate packet codecs and contracts from real sample acquisition, tracked beams, and a complete multi-array system."
tags:
  - Firmware
  - Audio
  - Tracking
  - BMA360
---

The final reproduction boundary is end-to-end: a physical source is captured, correctly identified and timed at each array, converted to detections or beams, transported, fused, and checked against independent ground truth. A codec, a protocol document, or a simulated tracker covers only part of that chain.

## Separate the layers

The egress branch defines BMA3 audio packets, BMAR source reports, and BMAN announcements. Its wire header also declares payload kinds for raw microphones, beams, and tracked targets. Those declarations are valuable: they make byte order, field sizes, sequence numbers and stream identity inspectable. But the daemon source says its synthetic source is the only implemented source in that snapshot. `zynq-pl` exits as not implemented because the stock bitstream exposes no samples to the processing system; the OMAP-EMIF source is also not implemented.

Therefore:

* successful encode/decode tests establish wire-format behavior;
* `--source synth` establishes only that synthetic data traverses the selected software path;
* neither establishes that a physical microphone stream reaches the egress daemon;
* a `TARGETS` enum or per-target report layout does not prove that the array computes live tracked beams;
* a hub contract is not evidence of an implemented receiver or successful multi-array field fusion.

The `BMA_TRACKS_V1` document is a contract. Treat it as the intended interface until the exact producer and consumer implementations, source path, and integration tests are all present in the same revision.

## Build a meaningful acceptance ladder

| Stage | Required evidence | What it still does not prove |
|---|---|---|
| Wire codec | exact vectors and parser/encoder round trips | live source acquisition |
| Synthetic egress | labeled synthetic packets and receiver output | real audio or hardware timing |
| Physical acquisition | real samples with source path, channel map, rate, gaps and checksums | correct bearing |
| Single-array DOA | known-position acoustic sources, verified mic map and pose, held-out captures | fused 3D tracks |
| Multi-array tracking | surveyed positions/orientations, measured clock offsets, known trajectories and independent ground truth | general performance outside tested conditions |
| Acoustic camera | live per-target beams tied to stable tracks, verified source identity and listening/measurement checks | any untested operating condition |

Each stage should preserve the source commit, hardware/image hashes, test data provenance, command line, output and failure reason. Keep synthetic and live results in separate report sections. If the sample source is unavailable, the correct result is "not implemented" or "not measured," not a success-shaped placeholder.

## Current status at the reviewed snapshot

The main-board teardown and egress work are separate snapshots. At `edge/egress-v1` commit `993f6d3c3bf70eba061cb16d524fb84d33f86850`, the codec and protocol definitions exist, but the egress daemon comments mark the physical Zynq PL and OMAP paths unavailable. The PC-side DOA/hub path from Parts 3-4 is a separate host implementation. Do not combine these into an end-to-end tracking claim.

This is the practical conclusion of the series: reproduce each layer with explicit inputs and outputs, and stop at the first unverified boundary. A credible partial result with a precise label is more useful than an impressive demo whose audio, geometry, or processing path cannot be traced.

## Sources

* [`BMA_STREAM_V1.md`](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/docs/BMA_STREAM_V1.md) — edge-to-hub wire-format draft.
* [`BMA_TRACKS_V1.md`](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/docs/BMA_TRACKS_V1.md) — per-track interface contract.
* [`bma_egressd.c`](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/zynq/egress/bma_egressd.c) — source availability and daemon behavior.
* [`bs_wire.h`](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/zynq/egress/bs_wire.h) — packet kinds and codec interface.
