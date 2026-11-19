---
layout: single
title: "BMA360 Reproduction, 2: A DSP4 Beam Is a Mechanism Result, Not a Camera"
excerpt: "How to frame the reported real-silicon DSP4 memory experiment precisely, what to compare, and which stronger conclusions it does not support."
tags:
  - Hardware
  - DSP
  - Audio
  - BMA360
---

The narrow result: the project manager reports that owner code on one BMA360 array copied a pointer-named DSP4 ring block from one TDM snapshot and formed a bit-exact beam from that same snapshot. No live audio egress was used. This is a reported real-silicon memory-read/copy/beam mechanism. It is not a beam-quality test, a directional result, DOA, or multi-array tracking.

The distinction is not rhetorical. A byte-exact reconstruction can establish that a memory location was read and a specified transform was applied. It cannot establish that the samples correspond to the intended microphones, that their phases and gains are correct, or that a source angle is recoverable.

## Reproduce the comparison, not just the headline

On the compatible board and the exact code/image pair used for the experiment:

1. Capture the DSP4 ring and the code's pointer/block metadata from one time-bounded snapshot. Preserve the raw capture, tool version, image checksums, and timestamp locally; do not publish private audio.
2. Resolve the pointer to the block actually copied. Do not infer the base from a variable name. The older `bma-audiod/STATUS.md` notes that `DM(0x256dc4)` is a descriptor pointer and identifies a different fixed receive-buffer base at `0x256dcc`; those addresses should not be casually conflated with the later DSP4 ring report.
3. Decode words using the observed frame/slot layout. The project-manager report for this DSP4 snapshot describes active microphone slots 0-3, 5, and 6; slot 4 is not a microphone, slots 7-18 are zero, and 19/20 are sync. Keep this as a snapshot-specific report, not a universal mapping for every buffer or firmware version.
4. Run the copy and beam computation over the same captured bytes. Compare output words exactly, not by visual inspection or a rounded RMS value. Keep input hash, output hash, code revision, and the comparison script together.
5. Repeat with a second capture and report whether it is an independent capture or a replay of the same snapshot.

The Loci finding associated with the result is marked `model_asserted`; its recorded window-4 level list is `0:-67, 1:-65, 2:-71, 3:-72, 5:-78, 6:-79 dBFS`. The project-manager summary also gave a broader level range, but it is not interchangeable with that per-window record. These levels are diagnostics, not evidence that a beam points at a source.

## What is missing for independent reproduction

The public source snapshot documents prior DSP and egress work, but the memory-only experiment's exact capture, command line, owner code, and expected output are not all part of this procedure. Without those artifacts, a reader can understand the reported method but cannot independently verify the headline. A publishable reproduction package should include a non-sensitive fixture or a capture-generation recipe, hashes, exact code revision, and a comparator whose expected result is known before running it.

Do not fill this gap with synthetic audio and call it a live result. Synthetic input may test a decoder or a transform, but it cannot show that the board's live ring has the assumed slot map. Likewise, a bit-exact beam is not a proof of useful acoustic performance.

## Why the labels matter

| Evidence | Supports | Does not support |
|---|---|---|
| Same-snapshot memory copy and bit-exact output, if independently reproduced | buffer access and transform mechanism | spatial response, SNR gain, or correct channel identity |
| Known-source acoustic measurement with verified channels and pose | measured bearing behavior for that setup | multi-array fusion by itself |
| Generated-bearing simulation | behavior under the stated generator/model | live microphone, DSP, or field performance |

The next step is not to draw a compass arrow from this beam. It is to resolve which physical microphones feed each channel, then survey the array and clocks before interpreting bearings.

## Sources and provenance

* [Historical live-audio status and buffer notes](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/STATUS.md)
* [DSP/FPGA teardown timeline](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md)
* Project-manager report received 2026-11-19 and Loci finding `626c8743-95fa-485e-97d7-cdb3c3d47dca`; the latter is explicitly `model_asserted`. These are provenance notes, not public raw data.
