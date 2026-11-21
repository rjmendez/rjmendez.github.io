"""Generate _figures/data/p10-ant-real.csv: one ant (AntFeatureEncoder v2) run over the three
published Part 9 detection clips (real array audio, one Dante channel each).

The clips as published are high-passed at 1 kHz and boosted 33 to 52 dB, then encoded lossy, so
the encoder sees processed audio: the low band (below ~477 Hz) is nearly empty and levels are
not calibrated. Only per-window outputs are saved. Point BMA_ANT_REF at the directory that holds
the `flybrain` package (o-fpga-bitstream).
"""
from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ["carolina-wren", "hairy-woodpecker", "white-throated-sparrow"]
WINDOW = 1024
SHIFTS = [2, 3, 4]  # one-pole split at about 1.9 kHz, 955 Hz and 477 Hz
FS = 48_000


def load(name: str) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(ROOT / "files" / "bma" / f"p09-clip-{name}.opus"),
         "-f", "s16le", "-ac", "1", "-ar", str(FS), "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.int64) << 8  # 16-bit to 24-bit


def main():
    ref = os.environ.get("BMA_ANT_REF")
    if not ref:
        sys.exit("set BMA_ANT_REF to the o-fpga-bitstream directory (holds flybrain/)")
    sys.path.insert(0, ref)
    from flybrain.ant_features_ref import AntParams, encode_stream  # noqa: E402

    out = Path(__file__).parent / "data" / "p10-ant-real.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        f.write("# provenance: AntFeatureEncoder v2 integer reference (flybrain/ant_features_ref.py) "
                "with three split points (lp_shift 2, 3, 4) over the three published Part 9 clips (real array audio, processed: 1 kHz high-pass, "
                "33-52 dB gain, lossy). Reference run on a PC; no board run.\n")
        w = csv.writer(f)
        w.writerow(["clip", "lp_shift", "win", "t_end_s", "x_hex", "d", "r_low", "r_high", "zc", "q_low", "q_high"])
        for name in CLIPS:
            s = load(name)
            s = s[: len(s) // WINDOW * WINDOW]
            for k in SHIFTS:
                for i, a in enumerate(encode_stream([int(v) for v in s], AntParams(lp_shift=k))):
                    w.writerow([name, k, i, f"{(i + 1) * WINDOW / FS:.4f}", f"{a.x:016x}", a.d,
                                a.r_low, a.r_high, a.zc, a.q_low, a.q_high])
            print(name, len(s) // WINDOW, "windows")


if __name__ == "__main__":
    main()
