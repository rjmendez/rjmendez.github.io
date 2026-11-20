---
layout: single
title: "BMA360, Part 9: From Dante Packets to the Web Dashboard"
excerpt: "Two tiles feed a Windows hub over the stock Dante output. How the hub decodes packets, handles gaps, classifies sound, and shows bearings, and why the fused-track list is still empty."
tags:
  - Hardware
  - Audio
  - BMA360
---

On November 19 both tiles were sending eight channels at 3,000 packets per second, with no gaps in the sampled intervals. One snapshot of the hub's fleet feed showed **two arrays, 42 bearing rays, and zero fused tracks**. The 42 rays are per-array estimates, not 42 birds, and with nothing fused the hub had no position to plot.

This is the part that runs today. It uses the Brooklyn-3 cards' existing Dante output, not the experimental wire from Part 8.

## What the hub does with a packet

```text
Two tiles -> Dante -> Windows bridge per tile -> sample-numbered audio blocks
                                                |-> BirdNET + multichannel analysis (WSL)
                                                `-> per-array direction estimates -> fleet hub

Analysis records + fleet feed -> Python HTTP server -> web dashboard
Selected live audio          -> listening engine   -> browser
```

In the flow I captured, a media packet is a 9-byte header plus 16 frames of interleaved big-endian 24-bit PCM. At 48 kHz that's `48,000 / 16 = 3,000` packets per second, or `3,000 × 16 × 8 × 3 = 1,152,000` PCM bytes per second per tile. The Windows bridge repacks selected channels into 256-sample blocks (about 5.33 ms) on the card's sample clock. When a packet goes missing, the bridge flushes whatever it has as a short block and starts the next one marked `gap_before`, so no block spans the hole.

The layout of this one 16-frame format (I haven't checked other Dante flows):

```text
byte 0       0x02
bytes 1..4   seconds, unsigned big-endian
bytes 5..8   frame within second, unsigned big-endian (< 48000)
bytes 9..    16 frames; within each frame, channel 0 through 7
             each sample is signed 24-bit big-endian

8-channel packet length = 9 + 16 * 8 * 3 = 393 bytes
first sample index      = seconds * 48000 + frame
```

Sample for frame `f`, channel `c` is the three bytes at `9 + 3 * (8*f + c)`; subtract `2**24` if bit 23 is set. Each packet's first index should be the previous one plus 16. Anything else is a discontinuity and the two blocks stay separate. Counter rollover and restarts need their own handling.

A supervisor runs one bridge per tile and restarts any that die. It tracks packet arrival, nonzero audio, and calibrated level as three separate status checks. In the November 19 capture the bridge reported zero packet loss and also marked its input-gain check **unverified**. Eight channels at the right rate also says nothing about what those channels carry in each routing mode (Part 7).

On the WSL side a mono branch feeds BirdNET, and an analysis branch takes the multichannel stream for levels, spectra, and multichannel classification. The classifier gates windows on activity and writes each detection with its provenance. The label is the model's guess at what it heard; it has no bearing attached and isn't a confirmed species record.

Direction is its own branch. With direction estimation on and a full microphone map configured, each tile's worker reports angle estimates to the fleet hub, and the hub decides whether reports from different tiles agree on a position. The worker will start with any complete map. Nobody has checked the physical channel ordering against it yet.

The estimator works on **4,800-sample windows (100 ms) every 2,400 samples (50 ms)**. A missing sample masks its whole window. A confirmed sample-index jump starts a new epoch and drops local tracks. Each detection record carries sample index, epoch, registry clock domain, and measurement/quality flags, but no absolute time: BMAA has no PTP timestamp, so `t_ns` and `epoch_ns` are null. There's a host-derived wall time for class hints, and it can't be used to line two arrays up.

That showed up in a fleet-feed snapshot at **2026-11-20 03:20:47 UTC**. Both units were configured as PTP-locked on the same reference, and both reported `not_fused_reason=clock_local`:

```text
rays: 2   per-array bearing tracks: 2   fused tracks: 0
not_fused_reason=clock_local   (both units)
hub log: clock_rebooted=2
```

I don't know yet why each unit got excluded, and this snapshot doesn't show that PTP failed. The code has a restart guard that marks a unit clock-local if its post-restart sample index lands more than 60 seconds off the shared timeline. That fits, and I haven't tested it.

## What the browser knows

The Python web service reads the analysis logs and the hub's fleet feed. It tails the logs, handles rotation, and keeps hourly summaries so a restart doesn't blank the charts. Nothing in the browser derives a position from audio. Fleet and Targets both read the same hub feed:

| View | What it shows | Caveat |
|---|---|---|
| **Live / analysis** | Spectrum, levels, detections, history | Healthy packets don't validate a direction; scores don't confirm a species |
| **Targets** | Per-array polar plots in the tile's own frame; fused tracks listed separately when there are any | A local angle needs the tile's orientation to become a compass bearing |
| **Fleet** | Registered tile poses, bearing rays with angular uncertainty, hub-reported positions | The pose labels weren't physically surveyed; the browser never intersects rays itself |

The legacy `/api/v2/targets` payload has no producer anymore and Targets doesn't read it. The view tells loading, unavailable, live, and stale apart from a live feed with no tracks, so two healthy inputs and an empty fused list is a valid display. The poses for this install started as estimates, and the registry's `surveyed` label doesn't change that. Fusion still needs compatible timing, verified poses, consistent mic geometry, and bearings that agree on one source.

Staleness: spectrum goes stale after 3 seconds and the fleet feed after 5. The timers only track updates, not content. Relative-calibration support went out in the November 15 deployment, but its opt-in wasn't set in that snapshot, so it wasn't producing fleet output.

## Listening

The listening engine can steer a host-side delay-and-sum beam at one array's bearing, or at a fused target if one exists. It builds 20 ms chunks with fractional delays and checks inter-array alignment by cross-correlation. If alignment doesn't lock it plays a single array instead of summing two misaligned streams. There's also an auto-following fused soundscape mode, which picks its output from the hub's fused-target state. It's handy for hearing what the system is following and says nothing about whether two-array localization works.

## A decoder test you can run without a tile

The fixture below is **synthetic**; I generated the values. It catches byte-order and sign-extension mistakes in the packet layout and nothing else.

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

The gap rule can be tested the same way. With 240 samples buffered at index 1000 and a gap detected before 1256, the bridge emits the 240-sample partial block, and the next 16-sample block starts at 1256 with `gap_before` set. Passing this means the host decoder and reblocker follow their format. Channel identity, the physical stream, levels, and bearings are all untested by it.

## Where to resume on the bench

The working Dante path is the control. Put a fixed source at a measured spot and record both bridges' loss and gap counts, per-array angles and sample indices, hub clock-eligibility and pose states, and any fused position. Ignore the registry's `surveyed` flag. Check each angle against the source before looking at positions, then repeat with silence and with the source moved.

The custom path starts somewhere else: capture a real DSP payload at the Zynq receiver and follow the same samples through the ring into the host. The indexed-copy probe matched the absolute read on DSP4 (`0/48` wrong, after `42/48` differed on the first try) but didn't touch the multi-frame delay ring. The levels hook is fixed and merged, with 474 host tests passing (110 skipped) and 25 failing when the fix is mutated out; it hasn't been on a board. The Cyclone transmit/return block passed 12 synthetic RTL tests, with no wire capture. Before that path gets trusted, the transmitter's 17-cell lead-in has to be checked against the receiver's 20-idle-edge acquisition requirement, and the host needs a regression test that rejects delayed samples left over from a previous epoch.