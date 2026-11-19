---
layout: single
title: "BMA360, Part 9: From a DSP Snapshot to a Live Bearing"
excerpt: "A real frame and a same-snapshot beam are measured on one DSP. The indexed read failed, the one-wire path has not crossed a pin, and live host tracks are not yet bearings. These are separate experiments, not one working pipeline."
tags:
  - Hardware
  - Audio
  - FPGA
  - SHARC
  - BMA360
---

Parts 1–8 follow the route from the ceiling tile to the first samples. The next question is whether the new pieces form a live path from the DSP to a bearing on a map. They do not yet. Several pieces exist and have useful test results; those results stop at different boundaries.

![Evidence status along the experimental path from the DSP ring to a bearing: the real sample and memory-only beam are measured; indexed-copy v1 failed and v2 is unverified; the R9-to-W13 link and Zynq ring have no hardware run; the host bearing display is simulated and live tracks are not validated.](/images/BMA360_experimental_pipeline_status.svg)

The distinction matters. “The code is written,” “the host test passes,” “the logic passes RTL simulation,” and “the array produced this result” are four different claims.

The measured starting point: DSP4 memory
======

On one array, my code read a block named by DSP4's receive-ring pointer. A frame is 21 words; the ring has three buffers, each holding eight frames. Across 24 captured frames, the two sync words were present in the expected positions every time: `0xff00` and `0x123456`. Slots 0–3, 5, and 6 carried microphone samples; slot 4 was not a microphone, and slots 7–18 were zero in the stock configuration.

That is a real microphone frame, copied into host-visible memory for inspection. It is not a continuous audio stream off the device.

There is a second, narrower result. Owner code copied the pointer-named block and formed a beam from that same snapshot. The result was bit-exact against the reference arithmetic. It was an in-memory operation: no samples left the board, and it proves nothing about steering direction, beam quality, or tracking.

The indexed read that failed
======

The first indexed-copy probe compared 48 words from an index-register load with the absolute-address copy in the same pass on DSP4. **42 of 48 differed.** In frame 0, slot `s` returned the word at `4*s`; six words happened to match because both copies read zero.

That mismatch led to a correction in the host model: indexed displacement is word-scaled on this DSP, while ordinary `MODIFY` remains byte-scaled. The corrected probe has not yet been rerun on the DSP. A separate levels-hook change also remains host-tested only. So the useful result is not “indexed reads are fixed”; it is “the old probe was wrong, the failure pattern is measured, and the corrected form still needs its silicon check.”

Why care about one addressing mode? A delay line needs to walk through several frames of history. An absolute copy can prove that a frame exists; it does not by itself prove that the DSP can traverse a history ring with the intended delay. Until the indexed form passes on the chip, a delay-ring result cannot be trusted.

The proposed R9-to-W13 wire
======

The single-wire experiment connects the Cyclone's R9 output to the Brooklyn-3 Zynq's W13 input. LINK1W v1 is specified as a 512-cell frame carrying eight 24-bit words, with a 17-cell idle lead-in. The Zynq receiver and image top have RTL/open-flow results. An experimental Cyclone transmitter and SHARC return block now pass 12 Icarus RTL simulations using synthetic fixtures, but no board image has been built or loaded.

There is a specific integration detail to settle before the first hardware run: the receiver's documented non-nominal-rate acquisition requirement is at least 20 idle edges, while the transmitter's current lead-in is 17 cells. Whether that requirement applies at the configured clock, and how the lead-in is counted at the receiver, has not been demonstrated. The link nominally expects a 24.576 MHz clock, but the selected source is not established; physical return mapping is also open. No frame has been confirmed at W13 on a running array. A receiver testbench cannot establish pin mapping, clock relationship, or that a real DSP sample survives the transmitter and receiver. The next meaningful result is a decoded frame from the physical wire, with framing and CRC checked against a known real-audio input—not a test pattern.

The wider raw-mic map is another experimental change, separate from the transport. The stock DSP4 capture has six microphone slots per lane (0–3, 5, 6). A proposed 18-mic-per-lane map uses slots 0–3 and 5–18 across DSP4–9, for 108 positions. That map has not been loaded; the lane-to-DSP assignment and bus-slot-to-microphone labels remain unverified, and the DSP0 bridge image is still a prerequisite. Even a successful wider capture would establish channel transport, not beam quality or direction.

From the Zynq ring to the network
======

The egress daemon now has a Zynq-PL ring-reader path as well as a synthetic test source. The reader needs a live ring writer in the programmable logic and a working Cyclone-to-Zynq input path. On the stock card, the programmable logic owns the audio and the processor cannot read those samples. A synthetic source can exercise software framing; it cannot establish that the board is streaming audio.

There is also a state boundary to check before calling this path ready. A static review raised a concern that the delayed-beam history may retain samples from the previous epoch after a resynchronization. With a two-tap delay, that could mark old samples as belonging to the new epoch for the first two outputs. This is a code-level review finding, not a measured hardware failure; it needs a regression or a fix before the stream is accepted.

What the host sees today
======

There is real audio available on the existing vendor path: one hub input has been observed at about 3,000 packets per second, with a zero-block fraction returning to 0.0 after reboot. In one DSP-load/capture window, that fraction was 0.05–0.19. A real-audio checker and listen mode have been calibrated against the vendor source. This verifies that the host can receive live microphone data through that path, but it does not verify the experimental R9-to-W13 link or Zynq-PL egress route—and it shows why the stream must be checked during, not just after, board experiments.

The map display is a different experiment. Its bearings come from generated signals. Separately, a host-side virtual-edge path has processed live raw-microphone streams, but it is not yet a supervised hub child; the tracks observed so far are short and near the noise floor, with a median duration of about two seconds and no stable source. Per-track classification has not run live. The track timing fields are useful diagnostics, not evidence that the array has localized a bird—or any known source.

The test that would change the claim
======

| Stage | What is established | What is still needed |
|---|---|---|
| DSP receive ring | Real frames read from DSP4; sync words align in 24/24 frames | A sustained, verified stream from the experimental path |
| In-memory beam | Bit-exact arithmetic on one same-instant snapshot | A valid indexed delay history, then a known-source beam-direction test |
| Index addressing | Probe v1 failed 42/48; the host model was corrected | Probe v2 passes against the absolute copy on the DSP |
| R9-to-W13 link | Receiver checks; transmitter/return RTL passes 12 synthetic tests | Reconcile lead-in/acquisition requirements; establish clock and return mapping; build/load images; capture real frame at W13 |
| Wider raw-mic map | Proposed 18 slots per lane across DSP4–9 | Load only after DSP0 bridge image; verify lane and microphone identities on real audio |
| Zynq egress | Ring-reader and host-side acceptance components exist | Real samples through the PL ring, with frame, sequence, and audio checks |
| Bearing and track | Generated-source bearing plots; live-input tracks are exploratory | A stable known source, verified microphone map and array pose, then repeatable bearings from two arrays |

This is not all blocked only by hardware verification. The levels-hook and transmitter integration still have software work open, and the egress epoch-history concern needs resolution. Some other stages are ready for a carefully controlled board test. A hardware run is useful only when the image, input, expected values, and acceptance test are fixed first.

The result I want next is not another screenshot of a simulated bearing. It is a real sample, with a traceable frame boundary, crossing the custom link; then a stable bearing from a source whose position is known. Until then, the prototype is a set of measured mechanisms and unfinished joins—not an acoustic camera.
