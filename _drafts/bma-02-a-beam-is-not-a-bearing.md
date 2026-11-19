---
layout: single
title: "BMA360, Part 2: I Found a Beam. It Still Couldn't Point to a Bird."
excerpt: "Live SHARC code and a raw channel reached Dante, but that transport milestone was not DOA. A separate memory-only beam result proves even less."
tags:
  - DSP
  - Audio
  - Reverse Engineering
  - BMA360
---

The first useful signal was not 121 separate microphone channels. The teardown timeline records my own SHARC code running live on DSP4 and a hook capturing 273 contiguous blocks of seven pre-combined 24-bit channels at 48 kHz. That gave me something real to follow through the machine.

Getting those samples out took a few wrong turns. Writing transmit data in place was a dead end: the DMA had already latched it before the ISR exited. Repointing the static TX descriptor worked. The first raw channel reached Dante Tx1, with 543 distinct values at -16.4 dBFS. The 24-to-16-bit conversion was lossy, so I pre-compensated the samples; the recorded check was 208/208 exact.

That was a real transport milestone. It was not a directional result, and seven pre-combined channels are not 121 independent microphones.

There is a second, narrower result that is easy to mix up with the transport experiment. The project manager reports that owner code on a real array copied a pointer-named block from one DSP4 TDM-ring snapshot and formed a beam from that same snapshot. The output was bit-exact. No live egress was used in that memory-only test.

The reported slot interpretation is specific to that snapshot: microphone data in slots 0-3, 5 and 6; slot 4 is not a microphone; slots 7-18 are zero; 19 and 20 carry sync. The result says the DSP memory could be read and the beam computation could be reproduced over those bytes. It does not say the beam points at a source, improves signal-to-noise ratio, or even that the slot labels correspond to the physical microphone labels we need for DOA.

That is the uncomfortable shape of progress here: one experiment got a raw channel out; another reproduced a beam from memory. Neither tells us the direction of a bird.

Loci stores the memory-only window as `model_asserted`, not as an independently validated measurement. Its recorded levels are diagnostics, not a listening test or a bearing measurement. The capture, exact code revision, and comparison artifacts are not packaged here for independent reproduction.

The [DSP/FPGA teardown timeline](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md) and [audio-pipeline status](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/STATUS.md) are private and access-controlled. The separate memory-only result is in the project-manager report and Loci finding `626c8743-95fa-485e-97d7-cdb3c3d47dca` (`model_asserted`).
