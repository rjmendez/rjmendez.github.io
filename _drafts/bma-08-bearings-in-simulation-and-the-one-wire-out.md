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

The synthetic source has run on a card. On November 11 I started `bma_egressd` from RAM on board A's card, under the vendor kernel, broadcasting eight synthetic streams to a receiver on my PC. The receiver saw the array announce itself with eight streams and logged 0.00% loss. That covers the framing and the transport on real hardware. It says nothing about microphone audio. The egress code also has an adaptive mode, up to 64 output streams with a default of 32, that re-steers beams toward a tracker's targets between reads. It is in the source on master. I haven't tested it, and it has not run on a board with microphone audio.

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

All 483 cells match the reference model's checked-in vector. The Zynq receiver and image top pass RTL and open-flow checks. The Cyclone transmitter and the SHARC return block pass 12 Icarus simulations on synthetic fixtures. Those are the simulation results. Since then the link has run on boards, in logged runs I haven't had independently reviewed: the Zynq receiver writes records into a DDR ring, and one run on board B captured 8,509,310 records with no gaps, no duplicates and no CRC violations, at about 48.1k records per second against the card's own timer. A small program on the card sends the ring out as UDP to the host, and a longer capture of 4.4 million records arrived with no sequence gaps. Board C's Cyclone now runs my own image and its ring runs too. A host bridge feeds the ring into the hub's existing eight-slot path, and the operator saw a waveform in the dashboard.

That proves the transport. It doesn't prove the payload is microphone audio: the eight lanes correlate at 0.92 to 0.98 and are dominated by a tone near 103 Hz, so a common electrical source isn't excluded. Which microphone is which lane is assumed, not mapped. I fitted the lanes against the measured 121-microphone layout with a search over ordered eight-microphone subsets; the search is too big to enumerate, so the fit is a lower bound. The result is inconclusive and leans toward a fixed per-lane skew rather than real acoustic delay. The 48 kHz is the card's timer, not a reference clock, so the skew against a true 48 kHz is unmeasured. Each record is eight lanes, not the adaptive 32 or 64 streams, and Dante isn't in this path. The ring-enable step doesn't survive a power cycle yet. An install script that flashes the Cyclone, arms the link, starts the sender and registers a watchdog is written and tested, and its cold power-cycle run is still to do. The bearings the hub draws from this feed aren't evidence of direction: replaying one capture through the hub's estimator, 91.7% of windows failed the coherence gate and 5.6% produced a bearing.

One mismatch is already known: at non-nominal rates the receiver's documented acquisition rule wants at least 20 idle edges, and the transmitter sends a 17-cell lead-in. The source of the 24.576 MHz clock and the physical return mapping are also open. Those are the first things to put a scope on once both images are loaded.

Scorecard
======

![Status matrix of every result in Parts 2 to 8: eight on real silicon (Parts 2 to 6), one mechanism-only beam and one failed probe in Part 6, two unresolved items in Part 7, five host or RTL test results and one simulation in Part 8](/images/bma/p08-scorecard-light.svg){: .only-light}
![Status matrix of every result in Parts 2 to 8: eight on real silicon (Parts 2 to 6), one mechanism-only beam and one failed probe in Part 6, two unresolved items in Part 7, five host or RTL test results and one simulation in Part 8](/images/bma/p08-scorecard-dark.svg){: .only-dark}

The corrected levels hook is merged and host-tested, not loaded on a board; mutating out its scale conversion fails 25 of the host tests. A static review flagged that delayed beam history might survive an epoch change in the egress path. That gets a fix or a test before the combined path goes on a board.

What's left
======

![Six undone steps in order: the fixed levels hook on a board, R9 TX against W13 RX, real samples through the PL ring reader and egress, a controlled capture of the eight Dante channels, a bearing on a known source, and the 24 silent elements, which are blocked. Beside them, the stock Dante path through the hub and dashboard, which runs today.](/images/bma/p08-whats-left-light.svg){: .only-light}
![Six undone steps in order: the fixed levels hook on a board, R9 TX against W13 RX, real samples through the PL ring reader and egress, a controlled capture of the eight Dante channels, a bearing on a known source, and the 24 silent elements, which are blocked. Beside them, the stock Dante path through the hub and dashboard, which runs today.](/images/bma/p08-whats-left-dark.svg){: .only-dark}

Part 9 is the path that runs today: the hub and dashboard on the stock Dante stream.
