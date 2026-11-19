---
layout: single
title: "BMA360, Part 3: What Is on the Eight Dante Channels?"
excerpt: "Two docs in the same firmware repo describe the eight-channel Dante feed differently. Until a packet capture settles it, the DOA input is unknown."
tags:
  - Audio
  - Calibration
  - BMA360
---

Getting one raw channel out on Dante Tx1 (Part 2) meant the SHARC transmit path could carry my samples. It said nothing about what the fleet code is reading today, which is an eight-channel Dante feed per array.

I went looking for the answer in the firmware repo and found two. Paraphrased:

```
bench-kit/bma-audiod/STATUS.md (dated 2026-10-27)
  capture route receives 8 processed/gated beams
  raw ungated audio is not available over Dante

bench-kit/bma-audiod/docs/fleet.md
  Dante: 8 raw mics -> pc/bma_doa.py
  arrays do not run DOA yet
```

Same repo, same snapshot, same eight channels. Both can't be right about the same stream.

The Biamp data sheet leans toward STATUS.md. On a stock BMA 360D the Dante outputs carry unprocessed beam audio, one Tx channel per beam, plus a separate mixed channel with AEC and noise cancel. That's what the box ships with, though, and these units are running modified firmware. It tells me what the channels were designed to carry. My units might be sending something else.

The Tx1 experiment doesn't break the tie either. That was one raw channel routed by my own DSP code during a specific bench session. The fleet feed is whatever the board is sending now, and the timeline doesn't say those are the same route.

This decides what kind of instrument I have. Eight raw mics on a ring can feed a small-array bearing estimate. Eight beams that the ClearOne code has already formed and gated are a different input, and `bma_doa.py` would be doing math on the wrong thing. The array has 121 mic elements, but an eight-channel network stream is still eight channels.

Mic map
======

Suppose the capture comes back raw. `pc/bma_doa.py` still won't start on a unit without a full `mic_map` in the registry:

```
python -I pc/bma_doa.py --unit <unit> --registry <root>\units.json ...
# missing or incomplete mic_map -> exit 3
```

Good. If I guess which physical `MIC<n>` sits behind each input, the bearings still come out looking tidy, they're just wrong. The ambient-event circle fits I have so far look like eight slots spaced around a ring but don't pin down which slot is which, the rotation, or whether the ring is mirrored.

Geometry and clocks
======

A local bearing from a board nobody has surveyed is not a world bearing. Each array needs a measured position, orientation and port normal before the hub can put two of them on a map.

Then time. The fleet notes list an unresolved two-array lag of roughly 602-603 samples, about 12.5 ms. One sample at 48 kHz is 20.83 µs. 12.5 ms is around four meters of sound travel, which is more than enough to make two arrays disagree about one call.

So the next job is a packet capture with a channel identity test: put a known signal on known mics and see which Dante channel it lands on. Until then I'm not plotting bearings from this feed.

The [status page](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/STATUS.md), [fleet guide](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/docs/fleet.md) and [teardown timeline](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md) are in a private repo.