"""Part 10 figures: mushroom-body model, iCE40 sim/HIL match, the retracted accuracy-vs-SNR
table, the Cyclone 121-mic band engine, and the reference/RTL flow.

Provenance:
- p10-accuracy-snr: _figures/data/p10-brain-eval.csv (ANT_BRAIN_SLOT.md 2026-11-13, host
  simulation on synthetic audio; reproduced by the 2026-11-15 FlyBrain honesty audit).
- p10-hil-match: doc (Part 10 draft) + audit 2026-11-15 (3386 pass, 1 timeout, 0 wrong).
- p10-mb-model: mb_core parameters and standalone synthesis as quoted in the draft/audit.
- p10-feature-engine: block diagram drawn from the draft text only (RTL sim, synthetic
  vectors; no board run). No FlyBrain source appears in any figure.
"""
from __future__ import annotations

import csv
from pathlib import Path

from bmafig import PALETTES, THEMES, out_path, save_mpl

DATA = Path(__file__).parent / "data"
FONT = "Segoe UI, DejaVu Sans, Arial, sans-serif"
MONO = "Consolas, DejaVu Sans Mono, monospace"


def _svg(w, h, body, p):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="{FONT}" font-size="13" fill="{p["fg"]}">\n'
            f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'fill="{p["muted"]}"/></marker></defs>\n{body}\n</svg>\n')


def _write(name, w, h, draw):
    paths = []
    for theme in THEMES:
        p = PALETTES[theme]
        path = out_path(name, theme)
        path.write_text(_svg(w, h, draw(p), p), encoding="utf-8")
        paths.append(path)
    return paths


def _box(x, y, w, h, fill, stroke, label, sub=None, p=None, size=13, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" '
         f'stroke="{stroke}" stroke-width="1.5"{d}/>')
    cy = y + h / 2 + (-4 if sub else 5)
    s += f'<text x="{x + w / 2}" y="{cy}" text-anchor="middle" font-size="{size}" font-weight="600">{label}</text>'
    if sub:
        s += (f'<text x="{x + w / 2}" y="{cy + 17}" text-anchor="middle" font-size="11.5" '
              f'fill="{p["muted"]}">{sub}</text>')
    return s


def _arrow(x1, y1, x2, y2, p, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{p["muted"]}" '
            f'stroke-width="1.5" marker-end="url(#ar)"{d}/>')


# ---------------------------------------------------------------- MB model

def mb_model(p):
    import random
    rng = random.Random(7)
    s = []
    s.append('<text x="20" y="22" font-weight="600" font-size="14">Mushroom-body core, the tested shape</text>')
    s.append(f'<text x="20" y="40" font-size="12" fill="{p["muted"]}">integer logic, weights trained on the host '
             f'and loaded; a fixed number of cycles per inference</text>')
    # input bits column
    ix, iy0 = 70, 62
    bits = [iy0 + i * 4.2 for i in range(64)]
    for i, y in enumerate(bits):
        on = rng.random() < 0.4
        s.append(f'<rect x="{ix}" y="{y}" width="14" height="3.4" fill="{p["blue"] if on else p["grid"]}"/>')
    s.append(f'<text x="{ix + 7}" y="{iy0 + 286}" text-anchor="middle" font-weight="600">64</text>')
    s.append(f'<text x="{ix + 7}" y="{iy0 + 302}" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">input bits</text>')
    # KC grid 16x16
    kx, ky, cs = 300, 70, 15.5
    winners = set(rng.sample(range(256), 16))
    shown = sorted(winners)[:3] + [5, 77]
    for k in range(256):
        r, c = divmod(k, 16)
        x, y = kx + c * cs, ky + r * cs
        win = k in winners
        s.append(f'<rect x="{x}" y="{y}" width="{cs - 3}" height="{cs - 3}" rx="2" '
                 f'fill="{p["gold"] if win else p["panel"]}" stroke="{p["gold"] if win else p["edge"]}" '
                 f'stroke-width="0.8"/>')
    # fan-in lines for a few KCs
    for k in shown:
        r, c = divmod(k, 16)
        tx, ty = kx + c * cs + 6, ky + r * cs + 6
        for src in rng.sample(range(64), 6):
            s.append(f'<line x1="{ix + 14}" y1="{bits[src] + 1.7}" x2="{tx}" y2="{ty}" '
                     f'stroke="{p["purple"]}" stroke-width="0.7" opacity="0.55"/>')
    s.append(f'<text x="{kx + 124}" y="{ky + 268}" text-anchor="middle" font-weight="600">256 Kenyon cells</text>')
    s.append(f'<text x="{kx + 124}" y="{ky + 284}" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">'
             f'each reads 6 input bits (fan-in 6)</text>')
    s.append(f'<text x="{(ix + kx) / 2 + 10}" y="{ky + 6}" text-anchor="middle" font-size="11.5" '
             f'fill="{p["purple"]}">fan-in 6</text>')
    # k-WTA
    wx = 590
    s.append(_arrow(kx + 250, 194, wx - 4, 194, p))
    s.append(_box(wx, 154, 130, 80, p["panel2"], p["gold"], "k-WTA", "keep top K = 16", p))
    s.append(f'<text x="{wx + 65}" y="252" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">16 of 256 active</text>')
    s.append(_arrow(wx + 130, 194, wx + 164, 194, p))
    rx = wx + 166
    s.append(_box(rx, 154, 130, 80, p["panel"], p["green"], "int8 readout", "3 class scores", p))
    s.append(_arrow(rx + 130, 194, rx + 164, 194, p))
    ax = rx + 166
    s.append(_box(ax, 164, 92, 60, p["panel"], p["blue"], "argmax", "ties: lowest", p))
    # footer
    s.append(f'<line x1="20" y1="372" x2="1000" y2="372" stroke="{p["grid"]}"/>')
    s.append(f'<text x="20" y="394" font-size="12.5">Standalone synthesis (Cyclone V, core only): '
             f'<tspan font-weight="600">405 ALUTs · 361 registers · 4 M10K</tspan>.  '
             f'Not in any BMA bitstream yet.</text>')
    return "\n".join(s)


# ---------------------------------------------------------------- HIL match

def hil_match(p):
    s = []
    s.append('<text x="20" y="22" font-weight="600" font-size="14">iCE40 HX1K, 256 KCs: does the FPGA match '
             'the reference?</text>')
    s.append(f'<text x="20" y="40" font-size="12" fill="{p["muted"]}">golden vectors from the host reference; '
             f'every output compared</text>')
    x0, W = 190, 620
    rows = [("RTL simulation", 2762, 2762, 0, 0), ("hardware in the loop", 3387, 3386, 1, 0)]
    for i, (lab, n, ok, to, wrong) in enumerate(rows):
        y = 62 + i * 62
        s.append(f'<text x="{x0 - 12}" y="{y + 22}" text-anchor="end" font-weight="600">{lab}</text>')
        wok = W * ok / n
        s.append(f'<rect x="{x0}" y="{y}" width="{wok}" height="32" fill="{p["green"]}" opacity="0.85"/>')
        if to:
            tw = 6
            s.append(f'<rect x="{x0 + W - tw}" y="{y}" width="{tw}" height="32" fill="{p["gold"]}"/>')
        s.append(f'<rect x="{x0}" y="{y}" width="{W}" height="32" fill="none" stroke="{p["edge"]}"/>')
        txt = f"{ok:,} / {n:,} match" + (f" · {to} timeout · {wrong} wrong answers" if to else "")
        s.append(f'<text x="{x0 + W + 12}" y="{y + 15}" font-size="12.5">{ok:,} / {n:,}</text>')
        s.append(f'<text x="{x0 + W + 12}" y="{y + 31}" font-size="11.5" fill="{p["muted"]}">'
                 f'{"all match" if not to else f"{to} timeout, {wrong} wrong"}</text>')
    s.append(f'<text x="{x0}" y="200" font-size="12">Task accuracy on that set: '
             f'<tspan font-weight="600">0.892</tspan> on hardware and on the reference '
             f'(the miss was a timeout, not a different answer).</text>')
    return "\n".join(s)


# ---------------------------------------------------------------- accuracy vs SNR

def _rows():
    with open(DATA / "p10-brain-eval.csv", encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    return list(csv.DictReader(lines))


def accuracy_snr(fig, p, theme):
    rows = _rows()
    snr = [float(r["snr_db"]) for r in rows]
    ax = fig.add_subplot(111)
    series = [
        ("b_v2_mb", "b_std", "MB head, v2 features", p["gold"], "o", "-"),
        ("c_linear", "c_std", "linear head, same features", p["blue"], "s", "-"),
        ("e2_knn_d_zc", "e2_std", "5-NN on two raw integers", p["green"], "^", "-"),
        ("a_v1_mb", None, "MB head, v1 features", p["faint"], "o", "--"),
    ]
    for key, sk, lab, col, mk, ls in series:
        y = [float(r[key]) for r in rows]
        err = [float(r[sk]) for r in rows] if sk else None
        ax.errorbar(snr, y, yerr=err, label=lab, color=col, marker=mk, ls=ls, lw=2,
                    ms=6, capsize=3, elinewidth=1)
    ax.axhline(1 / 3, color=p["muted"], lw=1, ls=":")
    ax.text(-7.3, 1 / 3 + 0.012, "chance (3 classes)", color=p["muted"], ha="right", fontsize=10)
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("accuracy")
    ax.set_xticks(snr)
    ax.set_xlim(-7.5, 13)
    ax.set_ylim(0.3, 0.95)
    ax.invert_xaxis()
    ax.set_title("The retracted headline: MB never beat a linear readout")
    ax.legend(loc="upper right", fontsize=10)
    fig.text(0.01, -0.04, "Host simulation on synthetic audio (ANT_BRAIN_SLOT.md, 2026-11-13); means ± std, "
             "n=100 (MB) / 10 (others). kNN margins at +12/+6/0 dB are within seed noise.",
             color=p["muted"], fontsize=9)


# ---------------------------------------------------------------- feature engine

def feature_engine(p):
    s = []
    s.append('<text x="20" y="22" font-weight="600" font-size="14">Cyclone V shared feature engine</text>')
    s.append(f'<text x="20" y="40" font-size="12" fill="{p["muted"]}">status: RTL simulation on synthetic '
             f'vectors, 5 tests pass; not routed, no board run</text>')
    y = 70
    s.append(_box(20, y, 130, 70, p["panel"], p["edge"], "121 mic channels", "on the mainboard", p))
    s.append(_arrow(150, y + 35, 186, y + 35, p))
    s.append(_box(188, y, 150, 70, p["panel"], p["blue"], "Windowing", "tagged windows", p))
    s.append(_arrow(338, y + 35, 374, y + 35, p))
    s.append(_box(376, y, 160, 70, p["panel"], p["blue"], "8 magnitude bands", "per channel", p))
    s.append(_arrow(536, y + 35, 572, y + 35, p))
    s.append(_box(574, y, 150, 70, p["panel"], p["blue"], "Output register", "holds under backpressure", p))
    s.append(_arrow(724, y + 35, 760, y + 35, p, dash=True))
    s.append(_box(762, y, 140, 70, p["panel2"], p["faint"], "FlyBrain adapter", "not built", p, dash=True))
    s.append(_arrow(902, y + 35, 932, y + 35, p, dash=True))
    s.append(_box(934, y, 76, 70, p["panel2"], p["faint"], "MB core", "brain_slot", p, size=12, dash=True))
    # gap handling under windowing
    s.append(f'<path d="M263,{y + 70} L263,{y + 100}" stroke="{p["red"]}" stroke-width="1.5" fill="none"/>')
    s.append(f'<text x="263" y="{y + 116}" text-anchor="middle" font-size="12" fill="{p["red"]}">'
             f'gap handling</text>')
    s.append(f'<text x="263" y="{y + 132}" text-anchor="middle" font-size="11" fill="{p["muted"]}">'
             f'mutating it breaks the test</text>')
    s.append(f'<text x="836" y="{y + 100}" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">'
             f'next: route, board load,</text>')
    s.append(f'<text x="836" y="{y + 116}" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">'
             f'diff vs host on real mic data</text>')
    return "\n".join(s)


# ---------------------------------------------------------------- reference / RTL flow

def flow(p):
    s = []
    s.append(_box(20, 20, 140, 56, p["panel"], p["edge"], "Training data", "ant-data Parquet", p))
    s.append(_arrow(160, 48, 196, 48, p))
    s.append(_box(198, 20, 220, 56, p["panel"], p["blue"], "Host trainer + reference", "Python, SageMaker", p))
    s.append(_arrow(418, 48, 454, 48, p))
    s.append(_box(456, 20, 200, 56, p["panel"], p["blue"], "Exported weights", "+ SHA-256 sidecar", p))
    s.append(_arrow(308, 76, 308, 112, p))
    s.append(f'<text x="316" y="98" font-size="11.5" fill="{p["muted"]}">golden vectors</text>')
    s.append(_box(198, 114, 220, 50, p["panel2"], p["green"], "Python tests", None, p))
    s.append(_arrow(556, 76, 556, 112, p))
    s.append(f'<text x="564" y="98" font-size="11.5" fill="{p["muted"]}">load / test</text>')
    s.append(_box(456, 114, 200, 50, p["panel2"], p["green"], "FPGA RTL + testbench", None, p))
    s.append(f'<path d="M418,139 L454,139" stroke="{p["muted"]}" stroke-width="1.5" stroke-dasharray="3 3"/>')
    s.append(f'<text x="436" y="186" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">'
             f'same inputs and weights, same outputs, fixed cycle count</text>')
    s.append(_arrow(656, 139, 692, 139, p, dash=True))
    s.append(_box(694, 114, 160, 50, p["panel2"], p["faint"], "BMA audio path", "next", p, dash=True))
    return "\n".join(s)


# ---------------------------------------------------------------- ant: one stream through the encoder

FIELDS = [  # (name, lsb, width, palette key)
    ("band ratio", 0, 24, "blue"),
    ("low band above floor", 24, 12, "green"),
    ("high band above floor", 36, 12, "teal"),
    ("zero-crossing rate", 48, 16, "purple"),
]


def _ant_rows():
    with open(DATA / "p10-ant-stream.csv", encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def _segments(rows):
    segs, start = [], 0
    for i in range(1, len(rows) + 1):
        if i == len(rows) or rows[i]["segment"] != rows[start]["segment"]:
            segs.append((rows[start]["segment"], start, i))
            start = i
    return segs


def ant_stream(fig, p, theme):
    import numpy as np
    from matplotlib.colors import ListedColormap
    from gen_p10_ant_data import FS, WINDOW, make_stream

    rows = _ant_rows()
    n = len(rows)
    samples, _ = make_stream()
    sig = samples[: n * WINDOW].astype(float) / (1 << 23)
    gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.25, 0.9], hspace=0.12)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax3 = fig.add_subplot(gs[2], sharex=ax1)

    # spectrogram, one column per encoder window
    frames = sig.reshape(n, WINDOW) * np.hanning(WINDOW)
    spec = 20 * np.log10(np.abs(np.fft.rfft(frames, axis=1)) + 1e-9).T
    fmax = 12000
    kmax = int(fmax / (FS / WINDOW))
    cmap = "magma" if theme == "dark" else "Greys"
    ax1.imshow(spec[:kmax], origin="lower", aspect="auto", cmap=cmap,
               extent=(0, n, 0, fmax / 1000), vmin=spec.max() - 70, vmax=spec.max())
    ax1.set_ylabel("kHz")
    ax1.grid(False)
    for lab, a, b in _segments(rows):
        if lab != "background":
            ax1.axvspan(a, b, color=p["gold"], alpha=0.08, lw=0)
            ax1.text((a + b) / 2, fmax / 1000 * 1.04, lab, ha="center", va="bottom", fontsize=9.5,
                     color=p["fg"])
    ax1.set_title("One ant over a synthetic test stream", pad=22)

    # the 64-bit codes
    img = np.zeros((64, n))
    for j, r in enumerate(rows):
        x = int(r["x_hex"], 16)
        for fi, (_, lsb, w, _) in enumerate(FIELDS):
            for b in range(lsb, lsb + w):
                if (x >> b) & 1:
                    img[b, j] = fi + 1
    colors = ["none"] + [p[k] for *_, k in FIELDS]
    ax2.imshow(img, origin="lower", aspect="auto", interpolation="nearest",
               cmap=ListedColormap(colors), vmin=0, vmax=4, extent=(0, n, 0, 64))
    ax2.grid(False)
    for name, lsb, w, k in FIELDS:
        ax2.axhline(lsb, color=p["grid"], lw=0.8)
        ax2.text(-2, lsb + w / 2, name, ha="right", va="center", fontsize=9, color=p[k])
    ax2.set_yticks([0, 24, 36, 48, 64])

    # decoded fields
    t = np.arange(n) + 0.5
    ax3.step(t, [int(r["d"]) for r in rows], where="mid", color=p["blue"], lw=1.6, label="band ratio (steps)")
    ax3.step(t, [int(r["r_low"]) for r in rows], where="mid", color=p["green"], lw=1.6,
             label="low band above floor")
    ax3.step(t, [int(r["r_high"]) for r in rows], where="mid", color=p["teal"], lw=1.6,
             label="high band above floor")
    ax3.set_ylabel("q steps\n(~1.5 dB)")
    ax3b = ax3.twinx()
    ax3b.step(t, [int(r["zc"]) for r in rows], where="mid", color=p["purple"], lw=1.2, ls="--",
              label="zero crossings / window")
    ax3b.set_ylabel("crossings", color=p["purple"])
    ax3b.grid(False)
    ax3b.spines["right"].set_visible(True)
    h1, l1 = ax3.get_legend_handles_labels()
    h2, l2 = ax3b.get_legend_handles_labels()
    ax3.legend(h1 + h2, l1 + l2, loc="upper center", fontsize=8.5, ncol=4, bbox_to_anchor=(0.5, -0.32))
    ax3.set_xlabel(f"window ({WINDOW} samples = 21.3 ms each)", labelpad=2)
    ax3.set_xlim(0, n)
    for ax in (ax1, ax2):
        ax.tick_params(labelbottom=False)
    fig.text(0.01, -0.04, "Output of the integer reference encoder, which the RTL matches bit for bit in "
             "simulation. Synthetic audio, not a recording.", color=p["muted"], fontsize=9)


def _code_cells(s, p, x0, y0, code, cell=14):
    for b in range(64):
        fi = next(i for i, (_, lsb, w, _) in enumerate(FIELDS) if lsb <= b < lsb + w)
        col = p[FIELDS[fi][3]]
        hot = (code >> b) & 1
        x = x0 + (63 - b) * cell
        s.append(f'<rect x="{x}" y="{y0}" width="{cell - 2}" height="{cell + 6}" rx="2" '
                 f'fill="{col if hot else p["panel"]}" stroke="{col}" stroke-width="0.8" '
                 f'opacity="{1 if hot else 0.55}"/>')


def ant_pipeline(p):
    rows = _ant_rows()
    r = rows[58]  # middle of the first tone
    s = []
    s.append('<text x="20" y="22" font-weight="600" font-size="14">One ant: a beam in, a 64-bit code and a '
             'class out</text>')
    s.append(f'<text x="20" y="40" font-size="12" fill="{p["muted"]}">integer only, no multiplier or divider '
             f'in the encoder; RTL bit-exact with the reference in simulation, not on a board</text>')
    y = 58
    boxes = [
        ("one beam", "24-bit PCM, 48 kHz", p["edge"]),
        ("one-pole split", "low (&lt; ~477 Hz) + rest", p["blue"]),
        ("1024-sample window", "Σ|low|, Σ|rest|, crossings", p["blue"]),
        ("log2, ~1.5 dB steps", "shift + 2 mantissa bits", p["blue"]),
        ("noise floors", "drop at once, rise slowly", p["blue"]),
    ]
    x, w, gap = 20, 178, 22
    for i, (a, b, c) in enumerate(boxes):
        s.append(_box(x, y, w, 60, p["panel"], c, a, b, p))
        if i < len(boxes) - 1:
            s.append(_arrow(x + w, y + 30, x + w + gap - 2, y + 30, p))
        x += w + gap
    # second row: code -> head -> result
    y2 = 150
    s.append(f'<path d="M{x - gap - w / 2},{y + 60} L{x - gap - w / 2},{y + 76} L120,{y + 76} L120,{y2 - 4}" '
             f'fill="none" stroke="{p["muted"]}" stroke-width="1.5" marker-end="url(#ar)"/>')
    s.append(_box(20, y2, 200, 60, p["panel"], p["gold"], "64-bit code", "4 fields, 8-12 hot bits", p))
    s.append(_arrow(220, y2 + 30, 256, y2 + 30, p))
    s.append(_box(258, y2, 210, 60, p["panel"], p["green"], "head: MB or linear", "int8 weights from the host", p))
    s.append(_arrow(468, y2 + 30, 504, y2 + 30, p))
    s.append(_box(506, y2, 200, 60, p["panel"], p["green"], "result register", "class, 3 scores, sequence", p))
    s.append(f'<text x="730" y="{y2 + 18}" font-size="11.5" fill="{p["muted"]}">code ready 104 clocks after the '
             f'window ends</text>')
    s.append(f'<text x="730" y="{y2 + 35}" font-size="11.5" fill="{p["muted"]}">MB inference: 1,803 clocks '
             f'(256 cells)</text>')
    s.append(f'<text x="730" y="{y2 + 52}" font-size="11.5" fill="{p["muted"]}">a window at the real sample '
             f'rate: 524,288 clocks</text>')
    # zoom on one code
    y3 = 252
    s.append(f'<text x="20" y="{y3}" font-weight="600">One code, from the 3 kHz tone '
             f'(window {r["win"]} of the stream below)</text>')
    x0, yc, cell = 40, y3 + 30, 14
    code = int(r["x_hex"], 16)
    _code_cells(s, p, x0, yc, code, cell)
    zc = int(r["zc"])
    vals = {
        "band ratio": f'high − low = {r["d"]} steps',
        "low band above floor": f'{r["r_low"]} steps',
        "high band above floor": f'{min(int(r["r_high"]), 20)} steps (cap 20)',
        "zero-crossing rate": f'{zc} per window',
    }
    for name, lsb, w, k in FIELDS:
        xa = x0 + (63 - (lsb + w - 1)) * cell
        xb = x0 + (63 - lsb) * cell + cell - 2
        yb = yc + cell + 12
        s.append(f'<path d="M{xa},{yb} L{xa},{yb + 6} L{xb},{yb + 6} L{xb},{yb}" fill="none" '
                 f'stroke="{p[k]}" stroke-width="1.5"/>')
        s.append(f'<text x="{(xa + xb) / 2}" y="{yb + 22}" text-anchor="middle" font-size="12" '
                 f'font-weight="600" fill="{p[k]}">{name}</text>')
        s.append(f'<text x="{(xa + xb) / 2}" y="{yb + 38}" text-anchor="middle" font-size="11.5" '
                 f'fill="{p["muted"]}">{vals[name]}</text>')
    s.append(f'<text x="{x0 + 64 * cell + 14}" y="{yc + 9}" font-size="11.5" fill="{p["muted"]}">bit 0</text>')
    s.append(f'<text x="{x0 - 8}" y="{yc + 14}" text-anchor="end" font-size="11.5" fill="{p["muted"]}">63</text>')
    s.append(f'<text x="20" y="{yc + 92}" font-size="12">Each field is a "bump" of 2-3 adjacent hot bits, so '
             f'nearby values share bits and none of the 64 is stuck on or off. The ratio and crossing fields</text>')
    s.append(f'<text x="20" y="{yc + 109}" font-size="12">ignore overall loudness (the same tone 12 dB up: same '
             f'crossings, ratio one step off); the two above-floor fields carry the level.</text>')
    return "\n".join(s)


# ---------------------------------------------------------------- where the brains sit

def _tbox(x, y, w, h, stroke, title, p):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{p["panel"]}" stroke="{stroke}" '
            f'stroke-width="1.5"/><text x="{x + w / 2}" y="{y + 28}" text-anchor="middle" font-size="13" '
            f'font-weight="600">{title}</text>')


def system_split(p):
    s = []
    s.append('<text x="20" y="22" font-weight="600" font-size="14">Where the FlyBrain parts sit on one array, '
             'and what exists today</text>')
    # legend
    lx = 20
    for lab, fill, stroke, dash in [("running today", p["panel"], p["green"], False),
                                     ("RTL or code, tested in simulation", p["panel"], p["blue"], False),
                                     ("design or draft only", p["panel2"], p["faint"], True)]:
        d = ' stroke-dasharray="5 4"' if dash else ""
        s.append(f'<rect x="{lx}" y="36" width="22" height="14" rx="3" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="1.5"{d}/>')
        s.append(f'<text x="{lx + 30}" y="48" font-size="12">{lab}</text>')
        lx += 46 + len(lab) * 6.6
    y = 120
    h = 118
    # SHARC
    s.append(_tbox(20, y, 170, h, p["green"], "SHARC DSPs", p))
    s.append(f'<text x="105" y="{y + 62}" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">beamforming</text>')
    s.append(f'<text x="105" y="{y + 78}" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">(ClearOne firmware)</text>')
    s.append(_arrow(190, y + 40, 246, y + 40, p, dash=True))
    s.append(f'<text x="218" y="{y + 30}" text-anchor="middle" font-size="10.5" fill="{p["red"]}">no rx RTL</text>')
    # Cyclone
    s.append(_tbox(248, y, 220, h, p["blue"], "Cyclone V: the ants", p))
    s.append(f'<text x="358" y="{y + 62}" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">one small classifier per</text>')
    s.append(f'<text x="358" y="{y + 78}" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">beam or channel, at the mics</text>')
    # OMAP above Cyclone
    s.append(_box(248, 66, 220, 40, p["panel"], p["green"], "OMAP", None, p, size=12))
    s.append(f'<text x="480" y="84" font-size="11" fill="{p["muted"]}">loads images, sets registers,</text>')
    s.append(f'<text x="480" y="98" font-size="11" fill="{p["muted"]}">metadata; not an audio path</text>')
    s.append(_arrow(526, y + 40, 584, y + 40, p, dash=True))
    s.append(f'<line x1="468" y1="{y + 40}" x2="528" y2="{y + 40}" stroke="{p["muted"]}" stroke-width="1.5" '
             f'stroke-dasharray="5 4"/>')
    s.append(f'<text x="526" y="{y + 30}" text-anchor="middle" font-size="10.5" fill="{p["muted"]}">results sideband</text>')
    s.append(f'<text x="526" y="{y + 60}" text-anchor="middle" font-size="10.5" fill="{p["muted"]}">draft, zero on wire</text>')
    # Zynq
    s.append(_tbox(586, y, 230, h, p["blue"], "Zynq: the coordinator", p))
    for i, line in enumerate(["joins ant results and beams", "over short windows, picks", "beams, drops stale or gappy",
                              "data; never reruns the ants"]):
        s.append(f'<text x="701" y="{y + 58 + i * 16}" text-anchor="middle" font-size="11.5" '
                 f'fill="{p["muted"]}">{line}</text>')
    s.append(f'<text x="701" y="{y + h + 16}" text-anchor="middle" font-size="10.5" fill="{p["muted"]}">'
             f'bk3_brain: simulation only, being reworked</text>')
    s.append(_arrow(816, y + 40, 872, y + 40, p, dash=True))
    s.append(f'<text x="844" y="{y + 30}" text-anchor="middle" font-size="10.5" fill="{p["muted"]}">events</text>')
    # Hub
    s.append(_tbox(874, y, 196, h, p["green"], "Hub: fleet brain", p))
    for i, line in enumerate(["Perch, BirdNET,", "cross-array matching,", "review"]):
        s.append(f'<text x="972" y="{y + 62 + i * 16}" text-anchor="middle" font-size="11.5" '
                 f'fill="{p["muted"]}">{line}</text>')
    # today's path
    yt = y + h + 44
    s.append(f'<path d="M105,{y + h} L105,{yt} L972,{yt} L972,{y + h + 4}" fill="none" stroke="{p["green"]}" '
             f'stroke-width="2" marker-end="url(#ar)"/>')
    s.append(f'<text x="540" y="{yt - 7}" text-anchor="middle" font-size="11.5" fill="{p["green"]}">today: stock '
             f'audio over Dante through the Zynq card (Part 9)</text>')
    # event record
    ye = yt + 26
    s.append(f'<rect x="586" y="{ye}" width="484" height="128" rx="6" fill="{p["panel2"]}" stroke="{p["faint"]}" '
             f'stroke-width="1.5" stroke-dasharray="5 4"/>')
    s.append(f'<text x="600" y="{ye + 20}" font-weight="600" font-size="12.5">What every event must carry (design)</text>')
    items = ["array, boot epoch", "exact sample range [start, end)", "beam or channel id",
             "gaps, padding, validity", "model + preprocessing digest", "what the score means",
             "clock, frame and pose source", "a link back to the raw audio"]
    for i, it in enumerate(items):
        cx = 600 + (i % 2) * 236
        cy = ye + 44 + (i // 2) * 19
        s.append(f'<text x="{cx}" y="{cy}" font-size="11.5">· {it}</text>')
    s.append(f'<text x="20" y="{ye + 40}" font-size="12">Events with unknown alignment stay unjoined.</text>')
    s.append(f'<text x="20" y="{ye + 58}" font-size="12">A rounded wall-clock time is not a join key.</text>')
    s.append(f'<text x="20" y="{ye + 76}" font-size="12">Raw audio and derived scores stay separate.</text>')
    return "\n".join(s)


def build():
    out = []
    out += save_mpl("p10-ant-stream", ant_stream, figsize=(10, 7.4))
    out += _write("p10-ant-pipeline", 1060, 420, ant_pipeline)
    out += _write("p10-system-split", 1090, 470, system_split)
    out += _write("p10-mb-model", 1020, 406, mb_model)
    out += _write("p10-hil-match", 960, 212, hil_match)
    out += save_mpl("p10-accuracy-snr", accuracy_snr, figsize=(8.6, 4.6))
    out += _write("p10-feature-engine", 1020, 212, feature_engine)
    out += _write("p10-flow", 870, 196, flow)
    return out


if __name__ == "__main__":
    for path in build():
        print(path.name)
