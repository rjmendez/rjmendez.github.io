---
layout: single
title: "BMA360, Part 2: Getting Samples Off DSP4"
excerpt: "Own SHARC code on DSP4, a repointed TX descriptor, one raw channel on Dante Tx1, and a memory-only beam that says nothing about direction yet."
tags:
  - DSP
  - Audio
  - Reverse Engineering
  - BMA360
---

The ceiling tile has 121 mic elements, but the SHARCs never see 121 microphones. By the time audio reaches DSP4 the FPGA has already folded it down to seven pre-combined channels, 24-bit at 48 kHz. That was the first thing I got to watch with my own code running live on DSP4: a hook that captured 273 contiguous blocks of those seven channels.

Next job was getting them out of the box.

My first try was writing the transmit data in place from the ISR. Nothing useful came out, because the DMA had already latched the buffer before the ISR exited. So I left the data alone and repointed the static TX descriptor at my own buffer instead. That worked, and the first raw channel showed up on Dante Tx1:

```
Dante Tx1: 543 distinct values, -16.4 dBFS
```

The path from 24 bits down to 16 is lossy, so the samples got pre-compensated before going out. The recorded check on that was 208/208 exact.

Good transport result. It still only moves seven pre-combined channels, and one of them at a time, so there is no direction in it.

Later there was a second, smaller result on array B that gets confused with this one. Per the project manager's report, owner code on real silicon copied a pointer-named block out of one DSP4 TDM-ring snapshot and formed a beam from that same snapshot, bit-exact. Nothing left the board; this was memory only. The reported slot layout for that snapshot:

```
slots 0-3, 5, 6   mic data
slot  4           not a mic
slots 7-18        zero
slots 19, 20      sync
```

Levels for window 4 of that run, as stored in Loci:

```
0:-67  1:-65  2:-71  3:-72  5:-78  6:-79   (dBFS)
```

Those are diagnostics. Nobody listened to anything and nothing was measured for bearing.

What this shows is that I can read the ring and redo the beam math over the same bytes. It doesn't show the beam points at anything, that it beats a single mic on SNR, or that these slot numbers line up with the physical mic labels I need for DOA. The mic map hasn't been checked independently. Loci has the finding as `model_asserted`, and the capture, code revision and comparison files aren't packaged anywhere you could rerun them.

The [DSP/FPGA teardown timeline](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/docs/HOW_WE_GOT_HERE.md) and [audio-pipeline status](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/STATUS.md) live in a private repo. The memory-only beam is Loci finding `626c8743-95fa-485e-97d7-cdb3c3d47dca`.
