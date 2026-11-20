---
layout: single
title: "BMA360, Part 9: From Dante Packets to the Web Dashboard"
excerpt: "Two tiles feed a Windows hub. Here is how it handles gaps, classifies sound, and shows bearings without inventing a position."
tags:
  - Hardware
  - Audio
  - BMA360
---

On November 19, both tiles were sending eight channels at 3,000 packets per second, with no gaps reported in the sampled intervals. The hub's fleet feed showed **two arrays, 42 bearing rays, and zero fused tracks** in one snapshot. The audio was coming in. The rays were estimates from individual arrays, not 42 birds, and the hub had no position to plot.

This is the system that runs today. It uses the Brooklyn-3 cards' existing Dante output, not the experimental wire from Part 8.

## What the hub does with a packet

```text
Two tiles -> Dante -> Windows bridge per tile -> sample-numbered audio blocks
                                                |-> BirdNET + multichannel analysis (WSL)
                                                `-> per-array direction estimates -> fleet hub

Analysis records + fleet feed -> Python HTTP server -> web dashboard
Selected live audio          -> listening engine   -> browser
```

In the observed flow, one media packet has a 9-byte header and 16 frames of interleaved, big-endian, 24-bit PCM. At 48 kHz, that's `48,000 / 16 = 3,000` packets per second, or `3,000 × 16 × 8 × 3 = 1,152,000` PCM bytes per second per tile. The Windows bridge repacks selected channels into 256-sample blocks, about 5.33 ms each, using the card's sample clock. If a packet goes missing, the bridge emits any accumulated samples as a short block, then starts a new block marked `gap_before`. No block straddles the hole.

The supervisor runs a bridge for each tile and restarts failed workers. Separate status records matter here: an arriving packet, a nonzero audio block, and a calibrated level are different checks. In that November 19 capture the bridge reported zero packet loss but marked its input-gain check **unverified**. And eight channels arriving at the right rate doesn't settle what those channels carry in every routing mode (Part 7).

On the WSL side, a mono branch feeds BirdNET; an analysis branch takes the multichannel stream for level and spectral measurements and multichannel classification. The classifier gates windows on activity and writes detections with their provenance. A label answers *what the model thinks it heard*. It doesn't supply a bearing, and it isn't a confirmed species record.

Direction runs on a separate branch. With direction estimation enabled and a complete microphone map configured, each tile's worker takes the multichannel audio and reports angle estimates to the fleet hub. The hub, not the classifier or browser, decides whether reports from different tiles support a single position. A configured microphone map is enough to start the worker; it is not evidence that the physical channel ordering has been checked.

## What the browser knows

The Python web service reads analysis logs and the hub's fleet feed. It reads the logs incrementally, handles rotation, and stores hourly summaries so a restart doesn't wipe out the charts. It does not derive positions from audio in the browser. The Fleet and Targets views use the same hub feed:

| View | What it shows | What it doesn't tell you |
|---|---|---|
| **Live / analysis** | Spectrum, levels, detections and history | Packet and signal health do not validate a direction; model scores do not confirm a species |
| **Targets** | Per-array polar plots in the tile's own frame; fused tracks listed separately when available | A local angle is not a compass bearing without the tile's orientation |
| **Fleet** | Surveyed tiles, bearing rays and angular uncertainty, plus positions reported by the hub; a separate relative-calibration view | The browser does not intersect rays and turn the crossing into a fix. Relative calibration is not a geographic position |

Fleet and Targets distinguish stale or missing data from a fresh feed with no tracks. That's why a dashboard with two healthy audio inputs and an empty fused-track list can be working correctly. The hub still needs compatible timing and poses, consistent microphone geometry, and bearings that agree on the same source.

## Listening is a separate output

The listening engine can steer a host-side delay-and-sum beam at one array's bearing or at a fused target when one exists. It builds 20 ms chunks with fractional delays and checks inter-array alignment using cross-correlation. If that check doesn't lock, it plays one array rather than summing two misaligned streams. You can listen to what the system is following without mistaking audible output for proof of two-array localization.

## Where to resume on the bench

Start with the working Dante path as the control. Play a fixed source at a measured location. Save the two bridges' loss and gap counts, the per-array angles and sample times, the hub's clock and pose states, and any fused position. Compare each angle to the surveyed source before judging the position. Repeat with silence and with the source in a second location. That separates a good-looking plot from a repeatable bearing.

The custom path has a different first test: capture a real DSP payload at the Zynq receiver, then trace those same samples through the ring and into the host. The indexed-copy probe already matched the absolute read on DSP4 (`0/48` wrong after `42/48` differed on the first attempt); it didn't test the multi-frame delay ring or the separate levels hook. The Cyclone transmit/return block passed 12 synthetic RTL tests; that's not a wire capture. Before accepting that path, the transmitter's 17-cell lead-in and the receiver's non-nominal acquisition requirement of at least 20 idle edges need to be checked together, and the host needs a regression that rejects delayed samples left over from a previous stream epoch.
