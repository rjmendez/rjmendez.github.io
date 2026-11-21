"""Generate _figures/data/p10-ant-stream.csv: one ant (AntFeatureEncoder v2) run over a
synthetic test stream.

The encoder is the integer reference flybrain/ant_features_ref.py from the private firmware
tree (the RTL is bit-exact with it in simulation). Point BMA_ANT_REF at the directory that
holds the `flybrain` package (o-fpga-bitstream). Only the per-window outputs are saved here;
no FlyBrain source is copied into this repo.

The stream is synthetic, not a recording: a coloured-noise background, a 3 kHz tone at two
levels 12 dB apart, a 2-7 kHz chirp, and a drone-like stack of 150 Hz harmonics.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import numpy as np

FS = 48_000
FULL = 1 << 23
WINDOW = 1024
SEED = 20261120

# (label, seconds, kind, dBFS RMS of the source; background always on)
SEGMENTS = [
    ("background", 1.0, None, None),
    ("tone 3 kHz", 0.5, "tone", -40),
    ("background", 0.3, None, None),
    ("tone 3 kHz, +12 dB", 0.5, "tone", -28),
    ("background", 0.3, None, None),
    ("chirp 2-7 kHz", 0.5, "chirp", -34),
    ("background", 0.3, None, None),
    ("drone 150 Hz", 0.6, "drone", -34),
    ("background", 0.4, None, None),
]
BG_DBFS = -62


def _rms_to(x, dbfs):
    return x / np.sqrt(np.mean(x ** 2)) * (10 ** (dbfs / 20))


def make_stream(seed: int = SEED):
    """Return (samples as int24 numpy array, list of (label, start_sample, end_sample))."""
    rng = np.random.default_rng(seed)
    parts, spans, pos = [], [], 0
    for label, sec, kind, db in SEGMENTS:
        n = int(sec * FS)
        t = np.arange(n) / FS
        if kind == "tone":
            src = np.sin(2 * np.pi * 3000 * t)
        elif kind == "chirp":
            f = 2000 + (7000 - 2000) * t / sec
            src = np.sin(2 * np.pi * np.cumsum(f) / FS)
        elif kind == "drone":
            src = sum(np.sin(2 * np.pi * 150 * k * t + rng.uniform(0, 6.28)) / k for k in range(1, 13))
            src = src + 0.3 * rng.standard_normal(n)
        else:
            src = None
        seg = np.zeros(n) if src is None else _rms_to(src, db)
        parts.append(seg)
        spans.append((label, pos, pos + n))
        pos += n
    sig = np.concatenate(parts)
    # 1/f-ish background: white noise through a one-pole low-pass, mixed with some white
    w = rng.standard_normal(len(sig))
    pink = np.zeros_like(w)
    a = 0.97
    for i in range(1, len(w)):
        pink[i] = a * pink[i - 1] + (1 - a) * w[i]
    bg = _rms_to(pink + 0.02 * w, BG_DBFS)
    sig = sig + bg
    return np.round(sig * FULL).astype(np.int64).clip(-FULL, FULL - 1), spans


def main():
    ref = os.environ.get("BMA_ANT_REF")
    if not ref:
        sys.exit("set BMA_ANT_REF to the o-fpga-bitstream directory (holds flybrain/)")
    sys.path.insert(0, ref)
    from flybrain.ant_features_ref import encode_stream  # noqa: E402

    samples, spans = make_stream()
    wins = encode_stream([int(s) for s in samples])
    out = Path(__file__).parent / "data" / "p10-ant-stream.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        f.write("# provenance: AntFeatureEncoder v2 integer reference (flybrain/ant_features_ref.py, "
                "bit-exact with rtl/ant_feature_encoder.v in simulation) over the synthetic stream "
                f"in gen_p10_ant_data.py, seed {SEED}. Synthetic audio, not a recording; no board run.\n")
        w = csv.writer(f)
        w.writerow(["win", "t_end_s", "segment", "x_hex", "d", "r_low", "r_high", "zc", "q_low", "q_high"])
        for i, a in enumerate(wins):
            end = (i + 1) * WINDOW
            seg = next(lab for lab, s, e in spans if s < end <= e)
            w.writerow([i, f"{end / FS:.4f}", seg, f"{a.x:016x}", a.d, a.r_low, a.r_high, a.zc,
                        a.q_low, a.q_high])
    print(out, len(wins), "windows")


if __name__ == "__main__":
    main()
