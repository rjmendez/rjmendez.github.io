---
layout: single
title: "BMA360 Reproduction, 3: Calibrate Channels, Pose, and Clock Before Bearings"
excerpt: "A DOA pipeline cannot repair an unknown microphone map, mirrored array frame, unsurveyed pose, or unaligned clocks."
tags:
  - Audio
  - Calibration
  - Tracking
  - BMA360
---

Before comparing bearings, establish what each input channel means. The fleet implementation makes this dependency explicit: a complete `mic_map` is required before its PC DOA stand-in will process a unit. Position without orientation is not a world bearing; a local clock is not cross-array time; a protocol field is not a measurement.

## Resolve the stream first

There is a documentation conflict in the reviewed firmware snapshot. `bench-kit/bma-audiod/STATUS.md` describes the Dante bridge as receiving eight processed, gated beams. `bench-kit/bma-audiod/docs/fleet.md` describes the fleet path as eight raw microphones. Neither statement should be silently selected as ground truth.

On the actual capture path, record a short packet capture and establish:

* BMAA header channel count, sample rate, packet sequence and sample count;
* payload format and whether channels are raw microphones, fixed beams, or another processed stream;
* packet loss, gaps, and channel amplitude on a known input;
* bridge command line and exact software revision.

Do not describe the input as "121-channel raw audio" based on a system's microphone count. The current documented Dante path is eight channels, while the status document says raw ungated audio is unavailable over Dante. A packet/channel audit is a prerequisite, not a detail to infer from the device name.

## Build the per-array registry from measurements

The fleet guide lists these registry dependencies:

| Registry item | Measurement required | Failure if absent or wrong |
|---|---|---|
| `mic_map.slots` | identify which physical `MIC<n>` reaches each of the eight stream channels | DOA refuses an incomplete map; a wrong complete map can produce plausible but wrong bearings |
| `pose.position` | surveyed east/north/up position, uncertainty, origin ID | no map marker or 3D contribution |
| `pose.orientation` | heading, pitch, roll, port normal, uncertainties | world bearing remains null or is rotated incorrectly |
| `clock` | clock domain, reference unit, offset samples and offset source | `LOCAL` clocks cannot be associated across arrays |

Never copy the example `units.json` values as if they were measured; the fleet guide marks them fictitious. For each array, keep a provenance field or accompanying notebook entry that says how the mapping and pose were obtained, when, and with what uncertainty.

A practical calibration run uses a localized source at a surveyed position, records the raw channel packets and a reference timestamp, and tests candidate channel permutations and mirror/ring orders against the known source. Keep left/right ambiguity as ambiguity: a collinear subset can yield a cone rather than a unique azimuth. Confirm the selected mapping with a second source position that is not symmetric around the array. A one-position fit can hide a mirrored map.

For two arrays, measure the inter-array sample offset with a known-position impulse before enabling cross-array fusion. The fleet notes report an unresolved lag in the two-array setup and state that clocks in `LOCAL` mode remain unassociated. Do not "fix" that by changing a registry number until the acoustic path and card/bridge delay have been separated.

## Acceptance conditions

Do not move to a bearing plot until all four conditions are met:

1. The capture confirms the channel count and stream kind.
2. Every channel has a physically verified mic label, not a guessed index.
3. The array position, orientation and port normal are surveyed with stated uncertainty.
4. Cross-array time offset is measured and the registry clock domain reflects the measurement.

If a prerequisite is missing, the correct output is a refusal or a labeled local-only result. A relaxed gate profile may expose weak estimates; it does not calibrate the array or make the estimates accurate.

## Sources

* [Live-audio status](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/STATUS.md) and [fleet path, registry, and calibration requirements](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/docs/fleet.md)
* [BMA stream protocol draft](https://github.com/rjmendez/bma360dx-firmware/blob/993f6d3c3bf70eba061cb16d524fb84d33f86850/docs/BMA_STREAM_V1.md)
