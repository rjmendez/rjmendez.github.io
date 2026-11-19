---
layout: single
title: "BMA360, Part 4: For Now, the PC Is the Array"
excerpt: "The current DOA-to-fleet path runs on a PC. It lets the tracking software take shape while making clear how much still isn't running on the hardware."
tags:
  - Python
  - Audio
  - Tracking
  - BMA360
---

With the audio path and geometry still unsettled, waiting for the embedded tracker would stall everything else. The firmware tree takes a useful middle step: run the per-array DOA on a PC, then send its detections to a separate hub.

The path is easy to draw:

```text
BMAA stream -> PC DOA stand-in -> array-detection records -> fleet hub -> fleet.json -> UI
```

`pc/bma_doa.py` processes one unit's stream and emits the same sort of array-detection record planned for edge DOA. `pc/bma_hub.py` consumes those records, fuses them and writes the fleet feed. The fleet guide says plainly that the arrays do not yet run this DOA implementation.

That separation is a good engineering move. It means the receiver, record format and fusion logic can be worked on without rewriting the hub when the DOA process eventually moves onto the array. It also gives us a place to inspect failures: a unit with a missing mic map is refused instead of being assigned a made-up identity; a local-only clock stays local rather than being silently fused.

But the PC step can make a diagram look more finished than the machine is. A nice fleet map is downstream of every uncertainty in the input. If the PC receives preformed beams when it expects microphones, the DOA mathematics is solving the wrong problem. If the pose or clock is guessed, the hub can publish a track with a precise-looking location and no physical basis.

The same is true of the gate profiles. The two-array `poc-2array-1.5m` profile was designed to publish "best available" estimates with quality labels. That is useful when the defaults hide everything, but exposing a weak estimate does not improve it. In the guide's simulation, the default gates publish no tracks at a low detection rate; the relaxed profile publishes weak ones. This is a visibility change, not a real-world accuracy result.

The host pipeline is a scaffold, not a fake result. It lets the project make progress on the pieces that do not require new board firmware. The next step is not to admire the map; it is to feed this scaffold measured, correctly labeled audio and see which assumptions survive.

Sources: private [`bma_doa.py`](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/pc/bma_doa.py), [`bma_hub.py`](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/pc/bma_hub.py), and [fleet guide](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/docs/fleet.md).
