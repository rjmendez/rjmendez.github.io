---
layout: single
title: "BMA360, Part 3: Eight Channels, Two Stories"
excerpt: "The firmware notes disagree about what the eight-channel Dante stream contains. Until the packets settle it, the DOA input is an open question."
tags:
  - Audio
  - Calibration
  - BMA360
---

One channel had made it to Dante. That did not answer the question I needed answered next: what are the eight channels on the actual fleet input?

One BMA360 status page says the Dante bridge receives eight processed, gated beams. The fleet guide describes eight raw microphone channels feeding a PC DOA process. Both descriptions are in the same firmware repository. They cannot both describe the same stream in the same sense.

The teardown timeline records an earlier, specific success: a raw channel was forwarded to Dante Tx1 after fixing the SHARC transmit path. That proves a route worked in that experiment. It does not identify the contents of today's eight-channel fleet stream. The snapshots describe different points in the system, so combining them into one confident claim would be fiction.

This is not a documentation nit. A DOA algorithm needs to know what each input channel means. Eight raw microphones could support a small-array bearing estimate. Eight already-formed beams would be a different instrument. The array may have 121 microphone elements, but that number does not turn an eight-channel network stream into 121 raw channels.

Even a confirmed raw stream is not enough. The fleet code refuses to process a unit without a complete microphone map. That is the right failure. Guessing which physical `MIC<n>` sits behind each input can still produce neat-looking bearings; it just makes them wrong with confidence.

Then there is the geometry. A map needs each array's surveyed position, orientation and port normal. The time bases need a measured offset. A local bearing from an unsurveyed board is not yet a world bearing, and two arrays with clocks that cannot be compared cannot reliably agree that they heard the same call. The fleet notes describe an unresolved two-array lag of roughly 602-603 samples, about 12.5 ms. At 48 kHz, one sample is only 20.83 microseconds; the error accumulates into distance and phase.

This is where the project changed character for me. I had been thinking about tracking as an algorithm problem. The limiting factor was upstream: which microphones, in which order, at what time, pointed where? Until a packet capture settles the channel question, a bearing plot is only a plot.

The [status page](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/STATUS.md), [fleet guide](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/docs/fleet.md), and [teardown timeline](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md) are private. The conflict is unresolved in the reviewed snapshot; the capture, not another paragraph of documentation, has to settle it.
