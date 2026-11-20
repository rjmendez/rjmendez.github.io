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

For this captured 16-frame format, the bridge decodes the packet as follows; this is not a claim about every Dante flow:

```text
byte 0       0x02
bytes 1..4   seconds, unsigned big-endian
bytes 5..8   frame within second, unsigned big-endian (< 48000)
bytes 9..    16 frames; within each frame, channel 0 through 7
             each sample is signed 24-bit big-endian

8-channel packet length = 9 + 16 * 8 * 3 = 393 bytes
first sample index      = seconds * 48000 + frame
```

For sample `frame f`, `channel c`, read three bytes at `9 + 3 * (8*f + c)`. Interpret the 24-bit value as signed: subtract `2**24` if bit 23 is set. Compare the next packet's sample index with the preceding index plus 16; a jump is a discontinuity, not a reason to join the two blocks. Counter rollover and restart require their own handling.

The supervisor runs a bridge for each tile and restarts failed workers. Separate status records matter here: an arriving packet, a nonzero audio block, and a calibrated level are different checks. In that November 19 capture the bridge reported zero packet loss but marked its input-gain check **unverified**. And eight channels arriving at the right rate doesn't settle what those channels carry in every routing mode (Part 7).

On the WSL side, a mono branch feeds BirdNET; an analysis branch takes the multichannel stream for level and spectral measurements and multichannel classification. The classifier gates windows on activity and writes detections with their provenance. A label answers *what the model thinks it heard*. It doesn't supply a bearing, and it isn't a confirmed species record.

Direction runs on a separate branch. With direction estimation enabled and a complete microphone map configured, each tile's worker takes the multichannel audio and reports angle estimates to the fleet hub. The hub, not the classifier or browser, decides whether reports from different tiles support a single position. A configured microphone map is enough to start the worker; it is not evidence that the physical channel ordering has been checked.

The host direction estimator processes **4,800-sample windows (100 ms) every 2,400 samples (50 ms)**. A missing sample masks its window: the estimator does not bridge the hole with made-up continuity. A confirmed sample-index jump starts a new epoch and discards local tracks. The detection record carries the sample index, epoch, registry clock domain, measurement and quality flags. It does **not** carry an absolute timestamp: BMAA has no PTP timestamp, so `t_ns` and `epoch_ns` are null. A host-derived wall time is available for class hints, not proof of cross-array synchronization.

That distinction showed up in the live hub. In one fleet-feed snapshot at **2026-11-20 03:20:47 UTC**, the two units were configured as PTP-locked and shared the same reference, yet both reported `not_fused_reason=clock_local`. The feed had two rays, two per-array bearing tracks and zero fused tracks; the adjacent hub log reported `clock_rebooted=2`. This is a timed operational snapshot, not evidence that PTP itself failed or a diagnosis of why each unit was excluded. The code has a restart guard that can mark a unit clock-local when its sample index after restart is more than 60 seconds from the shared timeline. That is a plausible explanation to test, not a confirmed cause. A clock label in the registry and a ray on screen do not prove that the hub can compare two arrays in time.

## What the browser knows

The Python web service reads analysis logs and the hub's fleet feed. It reads the logs incrementally, handles rotation, and stores hourly summaries so a restart doesn't wipe out the charts. It does not derive positions from audio in the browser. The Fleet and Targets views use the same hub feed:

| View | What it shows | What it doesn't tell you |
|---|---|---|
| **Live / analysis** | Spectrum, levels, detections and history | Packet and signal health do not validate a direction; model scores do not confirm a species |
| **Targets** | Per-array polar plots in the tile's own frame; fused tracks listed separately when available | A local angle is not a compass bearing without the tile's orientation |
| **Fleet** | Registered tile poses, bearing rays and angular uncertainty, plus positions reported by the hub | The registry label is not proof of a physical survey. The browser does not intersect rays and turn the crossing into a fix |

Targets reads the fleet feed; the legacy `/api/v2/targets` payload has no producer and the current view no longer reads it. The view distinguishes loading, unavailable, live and stale from a live feed with no tracks. That's why a dashboard with two healthy audio inputs and an empty fused-track list can be working correctly. The poses entered for this installation began as estimates, not measured positions; the registry's `surveyed` label alone doesn't establish their accuracy. The hub still needs compatible timing and verified poses, consistent microphone geometry, and bearings that agree on the same source.

Freshness is a separate signal too. In the current interface implementation, spectrum becomes stale after 3 seconds and the fleet feed after 5. Those timers say when a file or sample stopped updating; they do not grade its contents. A fresh feed with zero fused tracks is a real state, not a browser failure and not a localization. Relative-calibration support was included in the November 15 deployment, but its opt-in was absent in that snapshot, so it was not active fleet output.

## Listening is a separate output

The listening engine can steer a host-side delay-and-sum beam at one array's bearing or at a fused target when one exists. It builds 20 ms chunks with fractional delays and checks inter-array alignment using cross-correlation. If that check doesn't lock, it plays one array rather than summing two misaligned streams. The deployed interface also has an auto-following fused soundscape mode: it chooses listening output from the hub's fused-target state, not from an independent acoustic truth source. Listening can help inspect what the system follows; it does not prove two-array localization.

## A decoder test you can run without a tile

This fixture is **synthetic**. It checks signed-24-bit decoding and packet layout only; its values were generated, not recorded from the array. It is useful for catching byte-order and sign-extension mistakes before using real captures.

```python
import struct

header = bytes.fromhex("020000007b000001c8")  # marker, second=123, frame=456
frame = bytes.fromhex(
    "800000ffffff0000000000017fffff00002affffd6000011"
)
packet = header + frame * 16
assert len(packet) == 393

def signed24(b):
    value = int.from_bytes(b, "big")
    return value - (1 << 24) if value & (1 << 23) else value

first_frame = [
    signed24(packet[9 + 3*c : 12 + 3*c])
    for c in range(8)
]
sample_index = 123 * 48000 + 456
assert sample_index == 5904456
assert first_frame == [-8388608, -1, 0, 1, 8388607, 42, -42, 17]
```

The bridge's discontinuity rule is also testable without the hardware. If 240 samples are buffered at index 1000 and a gap is detected before index 1256, the bridge emits the 240-sample partial block; the next 16-sample block begins at 1256 and carries `gap_before`. Neither block pretends to contain samples from the missing interval. Passing this fixture proves only that the host decoder and reblocker honor their format contract. It does not identify the Dante channels, test the physical stream, calibrate levels, or validate a bearing.

## Where to resume on the bench

Start with the working Dante path as the control. Play a fixed source at a physically measured location. Save both bridges' loss and gap counts, per-array angles and sample indices, hub clock-eligibility and pose states, and any fused position. Do not treat a registry `surveyed` flag as a physical measurement. Compare each angle to the source before judging a position. Repeat with silence and with the source in a second location. That separates a good-looking plot from a repeatable bearing.

The custom path has a different first test: capture a real DSP payload at the Zynq receiver, then trace those same samples through the ring and into the host. The indexed-copy probe matched the absolute read on DSP4 (`0/48` wrong after `42/48` differed on the first attempt); it didn't test the multi-frame delay ring. The dependent levels hook is corrected and merged, with 474 host tests passed (110 skipped) and a mutation check that failed 25 tests when the fix was removed, but it has not been loaded on a board. The Cyclone transmit/return block passed 12 synthetic RTL tests; that's not a wire capture. Before accepting that path, the transmitter's 17-cell lead-in and the receiver's non-nominal acquisition requirement of at least 20 idle edges need to be checked together, and the host needs a regression that rejects delayed samples left over from a previous stream epoch.
