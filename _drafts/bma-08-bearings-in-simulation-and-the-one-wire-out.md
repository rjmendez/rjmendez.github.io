---
layout: single
title: "BMA360, Part 8: Bearings in Simulation, and the One Wire Out"
excerpt: "The bearing map is simulated. The one-wire link from the Cyclone to the Zynq passes RTL simulation and has never carried a frame on a real board. Where every piece of the series stands, and what is left."
tags:
  - Hardware
  - FPGA
  - DSP
  - Reverse Engineering
  - BMA360
---

The hub already gets live audio from both tiles over Dante; that is Part 9. This part covers two things built beside that path: the bearing map, and a custom one-wire link to get audio off the Cyclone without going through the Dante card. Neither works on a real array yet.

![The main board's SMSC LAN9500A Ethernet PHY beside the Power-over-Ethernet input section](/images/BMA360_LAN9500_ethernet.jpg)

Where the bearings come from
======

The bearing map in this series comes from a DOA run on generated input. It is a simulation.

A second, host-side virtual-edge path has been connected to live raw-microphone streams. Its tracks so far have a median length of about two seconds, sit at noise level, and had no stable source to follow. I don't count that as a detection.

```
SIMULATION:
  generated signal --> DOA estimator --> hub display --> bearings on a map

LIVE INPUT, NOT VALIDATED:
  raw microphone stream --> virtual edge / track pipeline --> short, noise-level tracks

MISSING:
  stable source at known bearing --> repeatable array bearing --> two-array crossing
```

The virtual-edge records carry per-track sample and timing fields. Those say when something was computed, not whether the angle was right. The generated-signal harness is still worth keeping for checking the estimator against inputs where I know the answer.

This is the geometry the finished instrument is supposed to run:

![Each tile sweeps its delay-and-sum beam to find a bearing; several tiles' bearings cross at a position, and successive fixes make a track. Labeled SIMULATED: today this runs on generated signals, not live array audio.](/images/BMA360_bearing_crossing.svg)

bma_egressd
======

To get audio off the array I wrote an egress daemon, `bma_egressd`, with pluggable sources:

```
bma_egressd sources:
  synthetic   -> framing/transport tests only
  zynq-pl     -> ring-reader code exists; needs a live PL ring
  omap-emif   -> not implemented
```

On the stock image the PL packetizes audio where the processor can't reach it, which is why the ring reader exists. It needs a PL ring writer and the Cyclone-to-Zynq wiring, and neither is on a board yet. The synthetic source only exercises framing and transport.

The host-side real-audio checker and listen mode were calibrated on vendor-path microphone audio. When the custom source finally produces something, it has to be real samples that pass that checker and sound right through listen mode.

The one wire out
======

The nearest experimental egress is a single serialized wire from the Cyclone's R9 pin to the Zynq's W13 pin. A LINK1W v1 frame carries eight 24-bit words:

```
LINK1W v1 FRAME (one-wire transport)
  6 cells   frame lead
  400 cells body (8 x 24-bit words)
  16 cells  checksum/trailer
  90 cells  inter-frame gap
  ------------------------------------
  512 cells per frame; a 17-cell idle lead-in starts transmission
```

Zynq side: the receive logic and a Zynq image top pass RTL and open-flow checks. The image has not been loaded on the card.

Cyclone side: an experimental transmitter and SHARC return block pass 12 Icarus RTL simulations against synthetic fixtures. They have not been built into a board image.

There is one mismatch I already know about. The receiver documents a non-nominal-rate acquisition requirement of at least 20 idle edges; the transmitter's lead-in is 17 cells. Whether the configured clock makes that matter, and how the receiver counts the lead-in, is the first thing to settle on hardware. Where the 24.576 MHz clock comes from, and the physical return mapping, aren't established either. No frame has crossed R9 to W13 on a running array.

Where everything stands
======

Every result in the series, sorted by how much I trust it:

```
RUNS ON REAL SILICON (measured, read-only or reversible):
  [+] serial console + our own kernel on the OMAP               (Part 2)
  [+] shell on the Brooklyn-3 Zynq over the internal link        (Part 3)
  [+] FPGA register reads via /dev/c1fpga; version 0x0117        (Part 4)
  [+] level meters move to real sound (array hears)              (Part 4)
  [+] our loader loads + identifies the DSPs (52s, 41/41)        (Part 5)
  [+] our one-word ISR hook executes, reversibly                 (Part 5)
  [+] one frame of real mic audio copied off DSP4's ring         (Part 6)
  [+] indexed-copy probe v2 matches absolute copy: 0/48 wrong    (Part 6)

MECHANISM ONLY (real data, no directional/quality claim):
  [~] in-memory bit-exact beam on one DSP4 snapshot              (Part 6)

MEASURED FAILURE:
  [!] indexed-copy probe v1: 42 of 48 words differed             (Part 6)

UNRESOLVED (measured oddity, no settled cause):
  [?] eight Dante channels: gated beams vs raw mics              (Part 7)
  [?] 602-603 sample lag                                         (Part 7)

HOST / RTL TESTS ONLY:
  [~] levels-hook indexed caller                                  (merged; host-tested, not board-loaded)
  [~] Zynq receive top + ring path                                (not loaded on the card)
  [~] Cyclone transmitter / SHARC return RTL                      (12 synthetic RTL tests; not built/loaded)
  [~] Zynq-PL egress source                                        (needs live PL ring data)
  [~] virtual-edge live-input tracks                              (short/noise-level; not validated)

SIMULATION ONLY:
  [-] displayed DOA bearings from generated sources               (Part 8)
```

The indexed-address unit passes its id-39 silicon comparison. The levels-hook caller that depends on it is fixed and merged: 474 host tests pass (110 skipped), and taking out the scale conversion fails 25 of them. It hasn't been loaded on a board. The multi-frame delay ring needs its own check, and the R9 transmitter still has to be integrated.

A static review flagged that delayed beam history might survive an epoch change in the egress path. Nobody has seen it on hardware. It still needs either a fix or a test that rules it out before the combined path gets a real-board run.

What's left
======

Roughly in order:

1. **Multi-frame delay history, and a board load of the corrected levels hook.** Probe v2 matched the absolute copy at id-39; the levels caller is host-tested only. Neither says anything about a table-driven delay ring.
2. **Build the R9 transmitter against the W13 receiver.** Sort out the lead-in and clock, load real Cyclone and Zynq images, then check frame alignment, CRC, and payload across the wire.
3. **Real samples into the PL ring reader and egress path**, run through the real-audio checker and listen mode. Generated tones don't count.
4. **Pin down the eight Dante channels** with a controlled capture (Part 7). Raw mics versus gated beams changes what any host-side estimator is looking at.
5. **A bearing on a known source**, then the same on two arrays with measured poses and verified slot-to-mic geometry.
6. **The 24 silent elements** (mics 97-120). That is a fabric rewrite, and the Cyclone bitstream self-loads from its own flash and can't be round-tripped yet (Part 4).

Part 9 covers the path that does run: what the hub and dashboard do with the stock Dante stream.
