---
layout: single
title: "BMA360, Part 9: From Dante Packets to the Web Dashboard"
excerpt: "Two tiles feed a Windows hub over the stock Dante output. Packet decoding, gap handling, classification, bearings, the dashboard, and a decoder test you can run without the hardware."
tags:
  - Hardware
  - Audio
  - BMA360
---

On November 19 both tiles were sending eight channels at 3,000 packets per second with no gaps. One snapshot of the hub's fleet feed showed **two arrays, 42 bearing rays, and zero fused tracks**.

This runs on the Brooklyn-3 cards' stock Dante output, not the wire from Part 8.

## The pipeline

```text
Two tiles -> Dante -> Windows bridge per tile -> sample-numbered audio blocks
                                                |-> BirdNET + multichannel analysis (WSL)
                                                `-> per-array direction estimates -> fleet hub

Analysis records + fleet feed -> Python HTTP server -> web dashboard
Selected live audio          -> listening engine   -> browser
```

A media packet in the flow I captured is a 9-byte header plus 16 frames of interleaved big-endian 24-bit PCM. At 48 kHz that's `48,000 / 16 = 3,000` packets per second and `3,000 × 16 × 8 × 3 = 1,152,000` PCM bytes per second per tile.

```text
byte 0       0x02
bytes 1..4   seconds, unsigned big-endian
bytes 5..8   frame within second, unsigned big-endian (< 48000)
bytes 9..    16 frames; within each frame, channel 0 through 7
             each sample is signed 24-bit big-endian

8-channel packet length = 9 + 16 * 8 * 3 = 393 bytes
first sample index      = seconds * 48000 + frame
```

Frame `f`, channel `c` lives at byte `9 + 3 * (8*f + c)`; subtract `2**24` if bit 23 is set. Each packet's first index should be the last one plus 16. Rollover and restarts get handled separately.

The bridge repacks selected channels into 256-sample blocks (about 5.33 ms) on the card's sample clock. When a packet goes missing it flushes what it has as a short block and marks the next one `gap_before`. A supervisor runs one bridge per tile and restarts any that die, and reports packet arrival, nonzero audio, and calibrated level separately. On November 19 that read zero loss, with the input-gain check still marked **unverified**.

On the WSL side a mono branch feeds BirdNET, and an analysis branch does levels, spectra, and multichannel classification. The classifier gates on activity and logs each detection with its provenance.

Direction is a third branch. With direction estimation on and a mic map configured, each tile's worker sends angle estimates to the fleet hub, and the hub decides whether reports from different tiles fuse into a position. The estimator runs **4,800-sample windows (100 ms) every 2,400 samples (50 ms)**. A missing sample masks its window, and a sample-index jump starts a new epoch and drops local tracks. Records carry sample index, epoch, registry clock domain, and quality flags. BMAA has no PTP timestamp, so `t_ns` and `epoch_ns` are null; a host wall time rides along for class hints.

Here's why nothing fused. Fleet feed at **2026-11-20 03:20:47 UTC**, both units configured PTP-locked to the same reference:

```text
rays: 2   per-array bearing tracks: 2   fused tracks: 0
not_fused_reason=clock_local   (both units)
hub log: clock_rebooted=2
```

The hub has a restart guard that marks a unit clock-local if its post-restart sample index lands more than 60 seconds off the shared timeline. That's my first suspect.

## The dashboard

A Python web service tails the analysis logs and the fleet feed, handles rotation, and keeps hourly summaries so a restart doesn't blank the charts. Positions come only from the hub.

| View | Shows |
|---|---|
| **Live / analysis** | Spectrum, levels, detections, history |
| **Targets** | Per-array polar plots in each tile's own frame; fused tracks listed separately |
| **Fleet** | Registered tile poses, bearing rays with angular uncertainty, hub-reported positions |

Targets used to read `/api/v2/targets`; nothing produces that anymore and the view reads the fleet feed instead. It shows loading, unavailable, live, stale, and "live, no tracks" as distinct states. Spectrum goes stale after 3 seconds, the fleet feed after 5. The tile poses started as my estimates, whatever the registry's `surveyed` label says. Relative calibration shipped in the November 15 deployment but its opt-in wasn't set in that snapshot.

## Listening

The listening engine steers a host-side delay-and-sum beam at one array's bearing, or at a fused target when there is one. It builds 20 ms chunks with fractional delays and aligns arrays by cross-correlation; if that doesn't lock, it plays one array. There's also an auto-follow mode that picks its target from the hub's fused-target state.

## A decoder test you can run without a tile

Synthetic values, for catching byte-order and sign-extension mistakes:

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

Gap handling: with 240 samples buffered at index 1000 and a gap before 1256, the bridge emits a 240-sample block, then the next 16-sample block starts at 1256 with `gap_before` set.

## Back on the bench

Next session uses the Dante path as the control: a fixed source at a measured spot, logging both bridges' loss and gap counts, per-array angles and sample indices, hub clock eligibility and pose state, and any fused position. Then silence, then the source moved.

For the custom path, the first test is a real DSP payload captured at the Zynq receiver and followed through the ring into the host. Before that, the 17-cell lead-in gets checked against the receiver's 20-idle-edge rule, and the host gets a regression test that rejects delayed samples from a previous epoch.