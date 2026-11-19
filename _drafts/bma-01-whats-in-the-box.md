---
layout: single
title: "BMA360, Part 1: What's in the Box"
excerpt: "Opening up a conference room ceiling mic to see if several of them can be a multi-array acoustic camera. First finding: it's at least two computers."
tags:
  - Hardware
  - Audio
  - BMA360
---

This is the first part of a series on turning conference room ceiling mics into a multi-array acoustic camera: several tiles spread out, their beams fused into bearings and positions of whatever is making sound. Birds are the target.

The BMA 360D is a ceiling microphone for meeting rooms. It's a 24 inch square tile, about 5 kg, that drops into a drop-ceiling grid in place of a regular tile. ClearOne designed it; Biamp announced in October 2025 that it was buying ClearOne's IP, brands and product designs, and sells it now as the Biamp BMA 360D. Our units and the firmware repo call it the BMA360DX, so that's the name I'll use. Around here BMA stands for Bird Microphone Array.

Inside the tile are 121 microphone elements. Stock, it forms up to 12 beams at once, puts each beam on its own Dante channel alongside a separate echo-cancelled mix, and runs off one PoE cable. It also reports beam activity over a text TCP control port so a PTZ camera can turn toward whoever is talking.

That last feature is what makes it interesting outdoors. A box that already points a camera at a talker is part of the way to pointing at a bird. No lens on this camera: each array turns a call into a bearing, bearings from several arrays get combined into a position, and positions over time become a track. I figured the hard part would be the tracking code.

Hardware
======

The firmware teardown found two separate boards doing two separate jobs.

```
Main board (ClearOne)
  TI OMAP-L138E          Linux 2.6.37, runs the vendor app heb_app.bin
  Cyclone V 5CEBA9F23C8N mic front end and routing
  ADSP-2156x SHARC+      beamforming / AEC

Brooklyn-3 Dante card (Audinate)
  Xilinx Zynq-7000       Dante network interface
```

All the ClearOne audio processing lives on the main board. The Zynq on the Dante card moves audio onto the network and that's it. There are two FPGAs in the parts list and only the Cyclone is in the audio path. `heb_app.bin` shipped unstripped with full DWARF, which was nice of them.

Signal path
======

Pieced together from the Cyclone image and the kernel driver, front to back:

```
[A] CIC, PDM -> PCM at 48 kHz
[B] 121 -> 36 time-mux pre-combine
[C] 13 x 1024-tap band FIR bank
[D] per beam/band/mic weights + 8-tap sinc fractional delay
[E] matrix / gain crosspoint
[F] 24 -> 16 bit reduction (not located yet)
[G] 36-slot TDM -> 8 SDIN lanes -> Brooklyn-3
```

Stage B is where the easy plan fell apart. The 121 microphones get folded down to 36 before anything downstream sees them, so raw per-mic data only exists on the main board, up in the FPGA and SHARC side. The OMAP gets 16 processed channels through `/dev/c1fpga` (char device major 200, ioctl magic `'k'`, registers mapped at CS4 `0x64000000`) and DSP/BIOS Link. There is no ALSA or McASP path to tap.

The Dante card never sees 121 channels. What the eight channels on our Dante feed actually are is unsettled; two documents in the firmware repo disagree, and Part 3 is about that.

For debugging, when a bearing comes out wrong I need to know whether it was the mics, the SHARC channel order, the FPGA route, the Dante card or my code on the PC. "The BMA360 sent it" doesn't narrow anything down.

Firmware
======

Everything started with read-only image pulls, checksummed, and a map of which processor owns what. The [teardown timeline](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md) marks which findings were observed and which were inferred. The repo has the reverse-engineering scripts and a working NFS-root shell recipe; the multi-GB dump images are not in it, so you would need your own dumps and to check them against the hashes. It's a private repo for now.

None of this points at a bird yet. Next up is DSP4, where my code copied a block out of SHARC memory and formed a beam from it, and what that does and doesn't prove.