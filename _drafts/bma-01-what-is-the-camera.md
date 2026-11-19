---
layout: single
title: "BMA360, Part 1: A Camera That Starts by Listening"
excerpt: "The goal is to make bird calls locatable and trackable. The first surprise was that the BMA360 is not one computer, or one audio path."
tags:
  - Hardware
  - Audio
  - BMA360
---

A Bird Microphone Array is supposed to do more than tell me that a bird called. The goal is to turn sound into bearings, then combine bearings from more than one array into a track. That is an acoustic camera: no lens, just microphones, timing, geometry, and a lot of software that has to agree about where a sound came from.

The BMA360DX looked like a shortcut. It already had a large microphone array and a Dante network card. Surely the hard part was writing the tracking algorithm.

It wasn't.

The teardown turned up several machines hiding inside the one product name. The main board has a TI OMAP-L138E, an Altera Cyclone V and a SHARC+ DSP cluster. The separate Brooklyn-3 Dante card has a Xilinx Zynq-7000. The boot path, image loader, audio DSPs and network card are different pieces of the puzzle; the Zynq is not the Cyclone, and neither chip name tells us which one owns the samples we want.

That sounds like a block-diagram detail. It isn't. If a direction estimate is wrong, I need to know whether the error came from the microphones, the SHARC's channel order, the FPGA route, the Dante card, or the PC. "The BMA360 sent it" is not a useful debugging statement.

The tempting number is 121 microphones. But a microphone count is not a channel count. The signal has already passed through DSP and FPGA routing before it reaches the network. A cable carrying eight channels might contain raw microphones, fixed beams, or some processed mixture. Those are different inputs to a tracker, even if they all arrive in packets marked "audio."

So the first chapter of this project is not "here is the bird tracker." It is "what is this box actually doing with the sound?" The firmware teardown starts with read-only image pulls, checksums and a map of the separate processors. That work made the black box smaller, but it did not yet point to a bird.

The [teardown timeline](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md) is in a private repository; the link requires GitHub access. It records which findings were observed and which are inferred. That distinction becomes important in the next post, when a result that sounds like beamforming turns out to prove something narrower.
