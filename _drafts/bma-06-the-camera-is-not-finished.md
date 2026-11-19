---
layout: single
title: "BMA360, Part 6: The Camera Is Not Finished"
excerpt: "The protocol can describe raw audio, beams and tracked targets. The current edge daemon still needs a real source, and the system still needs a bird it can locate."
tags:
  - Firmware
  - Audio
  - Tracking
  - BMA360
---

An acoustic camera is not a packet format. It is not a map with moving dots, either. It is a chain that starts with real sound and ends with a track whose source and position can be checked.

The egress work has names for the links in that chain: BMA3 audio, BMAR source reports, BMAN announcements. Its wire header distinguishes raw microphones, beams and tracked targets. That is useful groundwork. It gives the producer and hub something precise to agree on.

But the daemon's source comment is the part I keep coming back to: in the reviewed egress snapshot, the synthetic source is the one implemented. The Zynq-PL path exits as unavailable because the stock bitstream exposes no samples to the processing system; the OMAP-EMIF path is also not implemented. A protocol can be ready before a microphone stream is.

That puts the project in an uncomfortable but productive place. There is a reported DSP4 memory-to-beam mechanism. There is a PC-side DOA/hub scaffold. There is a simulation harness for generated bearings. There is a wire contract for future egress. Those pieces matter, but they are not yet one live system. There is no validated claim here that a bird has been found, assigned a direction, and tracked across arrays.

The next milestone is less glamorous than a dashboard: settle what the eight channels contain, identify their microphones, survey each array, measure the clock offsets, and get real samples through an actual egress source. Then test against known sources and independent ground truth. If any link is synthetic, model-asserted or unmeasured, label it that way.

That is the story so far: not "we built the camera," but the slow separation of what the BMA360 already does, what the new software can model, and what still has to work before the camera can point to a bird.

Sources: private [stream contract](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/docs/BMA_STREAM_V1.md), [track contract](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/docs/BMA_TRACKS_V1.md), [`bma_egressd.c`](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/zynq/egress/bma_egressd.c), and [`bs_wire.h`](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/zynq/egress/bs_wire.h).
