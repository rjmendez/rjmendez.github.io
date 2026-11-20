---
layout: single
title: "BMA360, Part 8: Bearings in Simulation, and the One Wire Out"
excerpt: "The map of bird bearings on my screen is simulated. The one-wire transmitter and receiver have separate RTL results, but no frame has crossed the real board. This is the honest ledger: what runs on silicon, what runs only in a testbench, and everything still between here and an acoustic camera."
tags:
  - Hardware
  - FPGA
  - DSP
  - Reverse Engineering
  - BMA360
---

The custom audio link and the bearing map are two separate experiments. The hub already receives live audio over Dante; neither experiment shows that the custom link can deliver that audio, or that two arrays can locate a real source.

![The main board's SMSC LAN9500A Ethernet PHY beside the Power-over-Ethernet input section](/images/BMA360_LAN9500_ethernet.jpg) The pictures of bird bearings are simulated. What is real is a pile of mechanism results — a shell on each computer, my code on a DSP, a frame of microphone audio — and a clear-eyed list of the gap between those and a working instrument.

Where the bearings come from today
======

The bearing map shown here is **simulation only**: that DOA run uses generated input. There is also a separate host-side virtual-edge path that has been connected to live raw-microphone streams. Its tracks so far are short and at noise level; that is not a validated detection or bearing:

```
SIMULATION:
  generated signal --> DOA estimator --> hub display --> bearings on a map
       ^ synthetic                                          ^ SIMULATED

LIVE INPUT, NOT YET VALIDATED:
  raw microphone stream --> virtual edge / track pipeline --> short, noise-level tracks

STILL MISSING:
  stable source at known bearing --> repeatable array bearing --> two-array crossing
```

The virtual-edge path reports per-track sample and timing information, but timing fields are not accuracy evidence. The live tracks observed so far have a median duration of about two seconds, with no stable source. The generated-signal DOA harness remains useful for checking the estimator against known synthetic input; it cannot validate an acoustic direction.

The geometry the finished instrument is meant to run is simple enough to draw; what is missing is a stable, known bearing from a real array:

![Each tile sweeps its delay-and-sum beam to find a bearing; several tiles' bearings cross at a position, and successive fixes make a track. Labeled SIMULATED: today this runs on generated signals, not live array audio.](/images/BMA360_bearing_crossing.svg)

The egress daemon: source code is not a live stream
======

To get audio off the array I wrote an egress daemon, `bma_egressd`. The source interface now has both a synthetic source and a Zynq-PL ring reader. Those are different maturity levels: the synthetic source can exercise framing and transport in tests, while the Zynq source needs a PL ring writer and the Cyclone-to-Zynq wiring. Neither is an end-to-end result from the custom link on a real array. On the stock image, the PL packetizes audio where the processor cannot reach it:

```
bma_egressd sources:
  synthetic   -> test source; never acceptance evidence
  zynq-pl     -> ring-reader code exists; needs a live PL ring
  omap-emif   -> not implemented
```

The host-side real-audio checker and listen mode have been calibrated on vendor-path microphone audio. A synthetic egress pass is not acceptance: the custom source must carry real samples, with the received data checked and listened to.

The one wire out
======

The nearest experimental egress path is a single serialized wire from the Cyclone's R9 pin to the Zynq's W13 pin. The LINK1W v1 frame design carries eight 24-bit words:

```
LINK1W v1 FRAME (one-wire transport)
  6 cells   frame lead
  400 cells body (8 x 24-bit words)
  16 cells  checksum/trailer
  90 cells  inter-frame gap
  ------------------------------------
  512 cells per frame; a 17-cell idle lead-in starts transmission
```

The receive logic and a Zynq image top have passed RTL/open-flow checks, but the image has not been loaded onto the card. An experimental Cyclone transmitter and SHARC return block now pass 12 Icarus RTL simulations using synthetic fixtures; they have not been built into a board image. The receiver's documented non-nominal-rate acquisition requirement is at least 20 idle edges, while the transmitter's current lead-in is 17 cells. Whether the configured clock makes that requirement relevant, and how the lead-in is counted at the receiver, still need to be resolved in the first physical test. The 24.576 MHz source and physical return mapping are not established. No frame has been verified crossing R9-to-W13 on a running array. A passing testbench means the logic is internally consistent against its model; it does not mean a single bit has crossed a real pin.

The honest ledger
======

Everything this series covered, sorted by how much I actually trust it:

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

MEASURED FAILURE / NOT A PASS:
  [!] indexed-copy probe v1: 42 of 48 words differed             (Part 6)

UNRESOLVED (measured oddity, no settled cause):
  [?] eight Dante channels: gated beams vs raw mics              (Part 7)
  [?] 602-603 sample lag                                         (Part 7)

HOST / RTL TESTS, NOT AN END-TO-END HARDWARE RESULT:
  [~] levels-hook indexed caller                                  (merged; host-tested, not board-loaded)
  [~] Zynq receive top + ring path                                (not loaded on the card)
  [~] Cyclone transmitter / SHARC return RTL                      (12 synthetic RTL tests; not built/loaded)
  [~] Zynq-PL egress source                                        (needs live PL ring data)
  [~] virtual-edge live-input tracks                              (short/noise-level; not validated)

SIMULATION ONLY:
  [-] displayed DOA bearings from generated sources               (Part 8)
```

These are not all hardware-verification-only tasks. The indexed-address unit passes its id-39 silicon comparison. The dependent levels-hook caller is now corrected and merged; its full host suite passed 474 tests (110 skipped), and a mutation that removed the scale conversion failed 25 tests. The hook has still not been loaded on a board. The multi-frame delay ring still needs its own check. R9 transmitter integration also remains open. A static review has raised a concern that delayed beam history may survive an epoch change in the egress path; that needs a code fix or a disproving test before hardware acceptance. It has not been confirmed on hardware. Only after these gates clear does a real-board run answer whether the combined path works.

What stands between here and an acoustic camera
======

The concrete remaining work, in rough order:

1. **Exercise multi-frame delay history and load-test the corrected levels hook.** Probe v2 matched the absolute copy 0/48 wrong at id-39; the levels caller has been corrected and host-tested, but not exercised on silicon, and neither result validates a table-driven delay ring.
2. **Integrate and build the R9 transmitter with the W13 receiver.** Resolve the lead-in/acquisition and clock requirements, load the actual Cyclone and Zynq images, then prove frame alignment, CRC, and real payload across the wire.
3. **Feed the PL ring reader and egress path real samples.** Run the real-audio checker and listen mode on captured output; generated tones do not count as acceptance.
4. **Resolve the eight-channel identity** with a controlled capture (Part 7). The raw-mics-versus-gated-beams discrepancy still changes what a host-side estimator receives.
5. **Prove a bearing with a known source**, then repeat on two arrays with measured poses and verified slot-to-mic geometry.
6. **Recover the 24 silent elements** (mics 97–120) as a separate fabric-rewrite problem. The Cyclone bitstream self-loads from its own flash and is not yet round-trippable (Part 4).

The custom path still needs a continuous stream of real samples and a known-source bearing test. Part 9 starts at the other end: what the existing Dante stream lets the hub and dashboard do before the custom link is ready.
