---
layout: single
title: "BMA360, Part 4: Running DOA on a PC"
excerpt: "The arrays don't compute bearings yet, so pc/bma_doa.py does it on the host and pc/bma_hub.py fuses the results. Notes on what that path will and won't do."
tags:
  - Python
  - Audio
  - Tracking
  - BMA360
---

The fleet guide in the firmware repo says it in one line: "The arrays do not run DOA yet." So for now the direction-of-arrival math lives on a PC.

The stock ceiling tile does have something like this already: its TCP control protocol reports beam activity so a meeting-room PTZ camera can swing toward whoever is talking. That tells you which of its beams is busy. It doesn't give a bearing you can fuse with a second array 1.5 m away.

```text
BMAA stream -> pc/bma_doa.py (one per unit) -> array-detection 1.0.0 records -> pc/bma_hub.py -> fleet.json -> UI
```

`bma_doa.py` takes one unit's stream and emits the same array-detection record that edge DOA is supposed to emit someday. `bma_hub.py` collects records from every unit, fuses them and writes `fleet.json` on a timer. When DOA eventually moves onto the array, the hub shouldn't need to change.

Starting it by hand looks like this (ports and paths are placeholders):

```text
python -I pc/bma_doa.py --unit <unit> --registry <root>\units.json --listen <host:port> \
    --out-dir <unit-dir>\analysis --hub <host:hub-port> --stats-file <unit-dir>\doa_status.json

python -I pc/bma_hub.py --registry <root>\units.json --root <root> --listen <host:hub-port> \
    --feed <root>\fleet.json --write-s 0.5
```

Under the supervisor you drop an `enable_doa.txt` marker and it launches one `bma_doa.py` per unit, but only for units that have a complete `mic_map` in `units.json`. Everything else gets one log line:

```text
doa: <id> skipped: mic_map missing/incomplete
```

Run it by hand without a map and `bma_doa.py` exits with code 3. The supervisor treats exit 3 as "refused" and doesn't restart it. I like this. The map is 8 `MIC<n>` labels, slot i being FPGA matrix input 14+i, and the guide says nobody gets to guess them; they have to be measured with a tap or a localized source. The guide calls those 8 slots raw mics. `STATUS.md` says the Dante feed is 8 processed, gated beams. Part 3 covers that fight. If it's beams, the DOA code is solving the wrong problem no matter how good the map is.

The registry has a few more fields, and each one has a specific failure when it's missing:

| Missing | Result |
|---|---|
| `mic_map.slots` | unit refused, `no_mic_map` |
| `pose.position` | no map marker, no rays, bearings only on the unit's own card |
| `pose.orientation` | `bearing_deg_world` is null |
| `clock` (or domain `LOCAL`) | `clock_local`, never associated with other arrays |

The clock one is the important one for two arrays. Until someone measures `offset_samples` between units, the domain stays `LOCAL` and cross-array fusion is off. All the example values in `contracts/fixtures/units.json` are fictitious, so copying the fixture gets you a pretty map of nothing.

Gate profiles
======

The default gates were tuned for clean, well-separated arrays: band coherence >= 0.7, no track birth closer than 10 m, two supporting units with three hits each. On the two-array, 1.5 m baseline setup they publish almost nothing. `contracts\profiles\hub_gates_poc.json` (`poc-2array-1.5m`) loosens them, dropping `doa.coh_gate` to 0.4, `hub.publish_min_units` to 1 and `hub.publish_max_range_m` to 100, and sets `hub.best_available` so the hub publishes everything with a `quality` label of good, fair or weak. Copy it to `<root>\hub_gates.json` and restart; delete it and `fleet.json` goes back to byte-for-byte what it was before profiles existed. A typo in the file stops both processes with exit code 2 instead of silently running defaults.

The numbers in the guide for this are from simulation (`hub/test_gates.py`, 1.5 m baseline, source 8.6 m away). At 0.3 detections/s per array the defaults publish 0 tracks and the POC profile publishes all of them, every one labelled weak because range is unobservable. At 3 detections/s the POC profile also produces `good` fixes. Those are generated bearings, so all this shows is what the hub lets through.

On the live side, the project manager's 2026-11-19 report puts the virtual-edge bearings in the simulated-only bucket: short, noise-level track segments, median about 2 s, no stable source. The pose is still open too. The owner baseline is 1.5 m, an acoustic estimate says roughly 1.0 m, and the mic label and ring/mirror order are still open.

Sources: private [`bma_doa.py`](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/pc/bma_doa.py), [`bma_hub.py`](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/pc/bma_hub.py), and [fleet guide](https://github.com/rjmendez/bma360dx-firmware/blob/dcde9a116bc39a970f5909e96821b1e22ef8025d/bench-kit/bma-audiod/docs/fleet.md).