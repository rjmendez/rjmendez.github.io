---
layout: single
title: "BMA360, Part 6: Where It's Stuck"
excerpt: "The wire format can describe raw mics, beams and tracked targets. The daemon that would send them only has a synthetic source, and the index-register probe I needed next failed on the hardware."
tags:
  - Firmware
  - Audio
  - Tracking
  - BMA360
---

The egress daemon speaks three packet types: BMA3 for audio, BMAR for source reports, BMAN for announcements. `bs_wire.h` gives the audio header a kind field with three values, `BS_KIND_RAW_121=0`, `BS_KIND_BEAMS=1` and `BS_KIND_TARGETS=2`. TARGETS gets a variable channel count capped by the announced stream count, plus a zero-channel heartbeat for when nothing is being tracked. The parser in `bs_wire.c` enforces those rules, so the producer and the hub have something exact to agree on.

Then there's source selection in `bma_egressd.c`. In the snapshot I reviewed, `synthetic` is the only source that works. Ask for `zynq-pl` and the daemon exits before it opens a socket, because the stock bitstream on the Brooklyn-3 card exposes no samples to the Zynq's processing system. `omap-emif` exits the same way; nobody has written it. The packet format is done and there is nothing real to put in it.

The plan, as the roadmap stood on 2026-11-18, is edge-first: Cyclone mic TDM into SHARC code I wrote, beamform and track on the array, Zynq PL ingest into a DDR ring, DOA/tracker/egress on the card, hub on the far end. The 121 raw mics never leave the array, and Dante goes away. Everything in that chain after the SHARC is still a plan.

Where it was stuck on 2026-11-19:

**Index registers.** My SHARC hooks address memory through index registers, and I don't know what unit the displacement field is in. idxprobe v1 (PR #504) was supposed to settle that. It ran on silicon and failed, with the indexed copy wrong in 42 of 48 comparisons. The best guess is that the field counts words, not bytes. Draft PR #509 adds `WORD_SCALE=4` to the emulator in `sharcasm/emu.py` (indexed LD/ST and MODIFY) and to an idxprobe v2 hook. Review of #509 found the scaling where it should be, the sharcasm suite at 454 passed, and five targeted tests going red when `WORD_SCALE` is mutated back to 1. All of that is host-side. The x4 is inferred, v2 hasn't had its own approved hardware run, and no other hook should depend on it until it does.

**Images.** The project manager reports that the Cyclone R9 transmitter only exists in simulation and isn't instantiated in the active design, the DSP0 bridge image hasn't been reviewed, and the image that puts 18 mics on each lane hasn't been loaded. I haven't checked those branches myself yet.

**Geometry.** Mic labels, rim-ring order and mirror orientation are unresolved. The baseline I gave the software for the two arrays is 1.5 m; an acoustic estimate comes out near 1.0 m. Either my number is wrong or the mic map under the estimate is. The eight-channel Dante question from part 3 is also still open.

**Bearings.** Virtual-edge DOA output on the hub is classified simulated-only. The reported track segments have a median length around 2 s with no stable source, so none of those bearings count.

**Integration.** Six PRs merged on 2026-11-19, all into integration branches, none into master. #397 (adaptive beams) is open and marked DO-NOT-MERGE after review found tracked-beam power underestimated after a re-steer. #501 merged with issue #508 still open; static review says the beam delay history in `bs_beam.c` survives an epoch reanchor. CI is stopped on the open PRs because the GitHub Actions budget ran out.

The one real-silicon result in this chain is still the DSP4 memory read from part 2: one array, one ring snapshot, a bit-exact copy and a beam formed from it. It proves the read and the arithmetic. It points at nothing.

Next on the list is an approved hardware window for idxprobe v2.

Sources: private [stream contract](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/docs/BMA_STREAM_V1.md), [track contract](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/docs/BMA_TRACKS_V1.md), [`bma_egressd.c`](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/zynq/egress/bma_egressd.c), and [`bs_wire.h`](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/zynq/egress/bs_wire.h).
