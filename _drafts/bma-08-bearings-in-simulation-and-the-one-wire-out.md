---
layout: single
title: "BMA360, Part 8: Bearings in Simulation, and the One Wire Out"
header:
  og_image: bma/og/bma360-part-8.png
excerpt: "A DOA estimator running on generated signals, an egress daemon, and a one-wire link from the Cyclone to the Zynq that passes RTL simulation. Plus a scorecard for the whole series."
tags:
  - Hardware
  - FPGA
  - DSP
  - Reverse Engineering
  - BMA360
---

The hub already gets live audio from both tiles over Dante (Part 9). This part covers two things built next to that: a bearing estimator, and a single wire to pull audio straight off the Cyclone.

![The main board's SMSC LAN9500A Ethernet PHY beside the Power-over-Ethernet input section](/images/BMA360_LAN9500_ethernet.jpg)

Bearings
======

The bearing map is a DOA estimator fed generated signals, so I can check it against inputs where I already know the angle:

```
generated signal --> DOA estimator --> hub display --> bearings on a map
```

![Top-down sketch of three tiles, each turning a sound into one bearing; the bearings cross at the source and successive fixes form a track. Labeled simulated, generated signals.](/images/bma/bearing-crossing-light.svg){: .only-light}
![Top-down sketch of three tiles, each turning a sound into one bearing; the bearings cross at the source and successive fixes form a track. Labeled simulated, generated signals.](/images/bma/bearing-crossing-dark.svg){: .only-dark}

I also pointed a host-side "virtual edge" at the live raw-mic streams. With nothing in the room to track it produced noise-level tracks with a median length of about two seconds. The next run needs a speaker at a measured position.

bma_egressd
======

On the stock image the Zynq's PL packetizes audio somewhere the processor can't read, so I wrote my own egress daemon, `bma_egressd`, with pluggable sources:

```
bma_egressd sources:
  synthetic   -> framing/transport tests
  zynq-pl     -> PL ring reader; waiting on a PL ring writer + Cyclone wiring
  omap-emif   -> not written
```

The synthetic source has run on a card. On November 11 I started `bma_egressd` from RAM on board A's card, under the vendor kernel, broadcasting eight synthetic streams to a receiver on my PC. The receiver saw the array announce itself with eight streams and logged 0.00% loss. That covers the framing and the transport on real hardware. It says nothing about microphone audio.

It also showed where the card's CPU goes. With the vendor stack up, the CPU sits at 100%. `ipcore_manager` takes about three quarters of it, and the two UARTs each take about 12,200 interrupts a second: the vendor control link receives a constant stream of `0x00` bytes and logs each one as a lost sync, and that log had filled tmpfs at 119 MB. Under that load the daemon skipped 64,050 of 214,050 frames to stay on time. With `ipcore_manager` paused, the CPU was 69% idle and all eight streams ran with no skipped frames and no send errors. I resumed it afterwards.

![Card CPU busy and frames skipped, with ipcore_manager running and paused.](/images/bma/p08-egress-cpu-light.svg){: .only-light}
![Card CPU busy and frames skipped, with ipcore_manager running and paused.](/images/bma/p08-egress-cpu-dark.svg){: .only-dark}

The host side already has a real-audio checker and a listen mode, both tuned on vendor-path mic audio, so whatever comes out of the custom source gets judged the same way.

The one wire out
======

The only Cyclone-to-Zynq net anyone has measured is the Cyclone's R9 pin landing on the Zynq's W13, so the link is one wire. LINK1W v1 is Manchester at one cell per 24.576 MHz clock, one frame per 48 kHz tick, eight 24-bit words:

![LINK1W v1 tick drawn to scale: a 17-cell lead-in, then 512 cells per tick made of a 6-cell preamble, 16-cell header, eight 48-cell words, a 16-cell CRC-8 and 90 idle cells](/images/bma/p08-link1w-frame-light.svg){: .only-light}
![LINK1W v1 tick drawn to scale: a 17-cell lead-in, then 512 cells per tick made of a 6-cell preamble, 16-cell header, eight 48-cell words, a 16-cell CRC-8 and 90 idle cells](/images/bma/p08-link1w-frame-dark.svg){: .only-dark}

The preamble is three cells high and three low. No Manchester data can hold a level for three cells, so the receiver can't mistake data for a frame start. The header carries version 1 and the word count, and the CRC-8 (poly 0x07) covers header and words. The receiver takes its cell period from the idle run, which is why every frame needs a lead-in.

Here is the transmitter RTL in Icarus, fed the `ramp8` fixture (words 1, -1, 0x7FFFFF, -0x800000, 0x123456, 0, 2, -2):

![Simulated R9 waveform: 40 disabled cells, then the 17-cell lead-in, preamble, header 0x18 and the eight words; the zoom shows the header bits 00011000 and the first word 0x000001 as Manchester cells](/images/bma/p08-link1w-wave-light.svg){: .only-light}
![Simulated R9 waveform: 40 disabled cells, then the 17-cell lead-in, preamble, header 0x18 and the eight words; the zoom shows the header bits 00011000 and the first word 0x000001 as Manchester cells](/images/bma/p08-link1w-wave-dark.svg){: .only-dark}

All 483 cells match the reference model's checked-in vector. The Zynq receiver and image top pass RTL and open-flow checks. The Cyclone transmitter and the SHARC return block pass 12 Icarus simulations on synthetic fixtures. Neither side has been built into a board image, and no frame has crossed R9 to W13.

One mismatch is already known: at non-nominal rates the receiver's documented acquisition rule wants at least 20 idle edges, and the transmitter sends a 17-cell lead-in. The source of the 24.576 MHz clock and the physical return mapping are also open. Those are the first things to put a scope on once both images are loaded.

Scorecard
======

![Status matrix of every result in Parts 2 to 8: eight on real silicon (Parts 2 to 6), one mechanism-only beam and one failed probe in Part 6, two unresolved items in Part 7, five host or RTL test results and one simulation in Part 8](/images/bma/p08-scorecard-light.svg){: .only-light}
![Status matrix of every result in Parts 2 to 8: eight on real silicon (Parts 2 to 6), one mechanism-only beam and one failed probe in Part 6, two unresolved items in Part 7, five host or RTL test results and one simulation in Part 8](/images/bma/p08-scorecard-dark.svg){: .only-dark}

The corrected levels hook is merged and host-tested, not loaded on a board; mutating out its scale conversion fails 25 of the host tests. A static review flagged that delayed beam history might survive an epoch change in the egress path. That gets a fix or a test before the combined path goes on a board.

What's left
======

1. Load the fixed levels hook on a board, and check the multi-frame delay ring, which probe v2 didn't cover.
2. Build R9 TX against W13 RX, settle the lead-in and clock, load both images, check alignment, CRC and payload on the wire.
3. Real samples through the PL ring reader and egress path, run through the audio checker and listen mode.
4. A controlled capture to pin down the eight Dante channels (Part 7).
5. A bearing on a known source, then two arrays with measured poses and verified slot-to-mic geometry.
6. The 24 silent elements (mics 97-120). That's a fabric rewrite, and the Cyclone bitstream self-loads from its own flash with no way to round-trip it yet (Part 4).

Part 9 is the path that runs today: the hub and dashboard on the stock Dante stream.
