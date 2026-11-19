---
layout: single
title: "BMA360 Reproduction, 1: Map the Computers Before the Microphones"
excerpt: "A reproducible teardown starts by separating the main array processor from the Dante card, then pinning exactly which firmware snapshot and artifacts are available."
tags:
  - Hardware
  - Audio
  - Reverse Engineering
  - BMA360
---

This series is about reproducing a Bird Microphone Array (BMA) acoustic-camera and multi-array tracker from the private BMA360DX firmware repository. The links below resolve only for authorized GitHub users; this draft describes repository content, not public availability. "Reproduce" needs a boundary: the repository can reproduce code inspection and host-side experiments; some claims require a physical board, owner-held captures, calibrated array geometry, or firmware images that are not in Git. These are different deliverables.

## Start with the block diagram

The BMA360DX is not one processor with one audio path. The main board contains a TI OMAP-L138E, an Altera Cyclone V (`5CEBA9F23C8N`), and SHARC+ DSPs. The separate Brooklyn-3 Dante card contains a Xilinx Zynq-7000 (`XC7Z015`). The Zynq card is not the Cyclone array processor. Treating them as one device makes later claims about which chip captured, transformed, or transmitted samples impossible to audit.

The firmware repository's teardown timeline describes the main-board boot/load path, DSP and FPGA image extraction, and the separate Dante card. Its evidence labels matter: some entries are verified observations, while others are explicitly inferred. Read the timeline and hardware identification before following a recipe:

* [Teardown timeline at the reviewed source snapshot](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md)
* [Repository README at the same snapshot](https://github.com/rjmendez/bma360dx-firmware/tree/dcde9a116bc39a970f5909e96821b1e22ef8025d)

The first pass should be read-only. Record board identity, device tree and boot evidence, firmware version and checksums, and which artifact came from which processor. The teardown documents a non-destructive NFS-root shell recipe and read-only image pulls. It also says large firmware dumps are not checked in. Therefore a clean clone is not a complete reproduction kit: any image-level experiment needs independently obtained artifacts and matching checksums. Do not silently substitute a similarly named image.

## Pin the baseline

Before running an experiment, write down:

| Item | Record |
|---|---|
| Hardware | board revision, main-board processor, FPGA, DSPs, Dante card |
| Software | repository commit, branch, image/version identifiers |
| Artifacts | filename, byte count, checksum, acquisition method |
| Evidence class | code inspection, live observation, simulation, or inference |
| Reproduction gap | hardware, data, calibration, or missing implementation |

Use the immutable commit links in this series rather than treating a moving branch name as a result. The main-board snapshot used for the repository walkthrough is `dcde9a116bc39a970f5909e96821b1e22ef8025d`. The separate egress work discussed in Part 6 is on `edge/egress-v1` at `993f6d3c3bf70eba061cb16d524fb84d33f86850`. A result from one snapshot does not automatically describe another branch or a deployed board.

## What this establishes

This inventory makes it possible to ask the right experiment question: which processor owns the buffer, what format is in it, and which downstream link sees it? It does not establish that the 121 microphones are independently available at the Dante connector, that the array computes a direction, or that multiple arrays can track one source. Those claims need separate measurements.

The next post narrows the claim further: one DSP4 memory-read and beam mechanism was reported on real silicon, but it is not evidence of beam quality or direction finding.

## Sources and evidence notes

* [BMA360DX teardown timeline](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md) — platform identification and the repository's own verified/inferred labels.
* [BMA 360DX audio-pipeline status](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/STATUS.md) — current capture-path description and historical egress notes.

This is a reproduction guide, not a claim that every result described later can be independently reproduced from public files alone.
