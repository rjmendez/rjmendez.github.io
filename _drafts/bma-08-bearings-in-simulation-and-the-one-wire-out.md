---
layout: single
title: "BMA360, Part 8: Bearings in Simulation, and the One Wire Out"
excerpt: "The map of bird bearings on my screen is simulated. The transport that carries one channel off the array works — in RTL simulation, never yet on the real fabric. This is the honest ledger: what runs on silicon, what runs only in a testbench, and everything still between here and an acoustic camera."
tags:
  - Hardware
  - FPGA
  - DSP
  - Reverse Engineering
  - BMA360
---

This is the last post in the series, and the one most likely to be misread. So, up front: **the acoustic camera does not work yet.** The pictures of bird bearings are simulated. What is real is a pile of mechanism results — a shell on each computer, my code on a DSP, a frame of microphone audio — and a clear-eyed list of the gap between those and a working instrument.

Where the bearings come from today
======

The direction-of-arrival and the little hub that paints bearings on a map are **simulation only**. They run on generated input, not on live array audio:

```
TODAY (what actually runs end to end):
  generated signal --> DOA estimator --> hub display --> bearings on a map
       ^ synthetic                                          ^ SIMULATED

MISSING for the real thing:
  live 8ch (identity unresolved, Part 7) --> DOA --> hub
       ^ this join does not exist yet
```

The DOA harness produces bearings, and in simulation they are correct for the synthetic sources I feed it. That is a useful component test and nothing more. The "virtual edge" tracks you might see in development logs are built from short or noise-level inputs; I do not treat them as validated detections, and neither should you. Run the bearing harness with fixed evaluation seeds and it reports simulation results — labeled as such, every time.

The egress daemon that only has a synthetic source
======

To get audio off the array I wrote an egress daemon, `bma_egressd`. It has a clean internal structure — a source, a framer, a transport — but only one of its sources actually produces data today: the **synthetic** one. The path that would pull from the Zynq's programmable logic returns "not implemented" on the stock image, because, as Part 3 established, the stock PL packetizes audio where the processor cannot reach it:

```
bma_egressd sources:
  synthetic   -> WORKS (test tone / generated frames)            [validated in sim]
  zynq-pl     -> ENOTIMPL on stock image (PL owns the samples)   [not available]
```

So `bma_egressd` is real code that runs, but the only thing it can currently carry is a signal I generated. It is plumbing waiting for a water supply.

The one wire out
======

The nearest thing to a genuine egress path is a minimal one-channel transport I designed to live in the FPGA fabric — a single serialized link that carries one audio channel off the array on one wire, framed deterministically:

```
LINK1W FRAME (one-wire transport)
  6 cells   lead framing
  400 cells audio payload
  16 cells  checksum/trailer
  90 cells  inter-frame gap
  ------------------------------------
  512 cells per frame; a 17-cell lead-in appears once per enable
```

Here is the status, stated the way it has to be: this transport **passes its RTL simulation** — the register-transfer testbench runs clean (twelve of twelve on one suite, sixty-seven of sixty-seven on another) — and it has **never run on the real FPGA.** It is not instantiated in the active design. A passing testbench means the logic is internally consistent against my model of the world; it does not mean a single bit has crossed a real pin. RTL-sim pass, hardware zero.

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
  [+] indexed-copy == absolute-copy, bit-exact on silicon        (Part 6)

MECHANISM ONLY (real data, no directional/quality claim):
  [~] in-memory bit-exact beam on one DSP4 snapshot              (Part 6)

UNRESOLVED (measured oddity, no settled cause):
  [?] eight Dante channels: gated beams vs raw mics              (Part 7)
  [?] 602-603 sample lag                                         (Part 7)

SIMULATION / TESTBENCH ONLY (never on hardware):
  [-] DOA + hub bearings (synthetic input)                       (Part 8)
  [-] bma_egressd (only synthetic source works)                 (Part 8)
  [-] LINK1W one-wire transport (RTL-sim pass, not instantiated) (Part 8)
```

The top block is real. The bottom block is not yet real. The middle is real data with a deliberately narrow claim.

What stands between here and an acoustic camera
======

The concrete remaining work, in rough order:

1. **Resolve the eight-channel identity** with a controlled packet capture (Part 7's experiment). Everything acoustic depends on this answer.
2. If the channels are not raw aperture, **get raw samples out another way** — which means my own logic in the Zynq PL, since the stock PL hides them.
3. **Instantiate a real egress transport** (LINK1W or a successor) on the actual fabric and prove one bit crosses a real pin.
4. **Recover the 24 silent elements** (mics 97–120), which needs rewriting the Cyclone bitstream — a self-loaded, opaque image (Part 4). Long pole.
5. **Join live audio to the DOA path** and only then, with a known source at a known bearing, make the first *validated* direction claim.
6. **Establish array pose, baseline, and slot-to-mic geometry** before any bearing means a physical direction.

None of that is done. What is done is the unglamorous foundation: I own every computer in the tile, I can run my own code down to a single DSP instruction, and I can read a real microphone sample. The surplus conference-phone ceiling tile is, demonstrably, a general-purpose 121-element acoustic front end that answers to my code. Turning it into a camera that watches birds is the next project, and I will write that one when the bearings on the screen come from the air instead of a random-number generator.
