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
    s.append(f'<text x="20" y="40" font-size="12" fill="{p["muted"]}">integer logic, inference only; '
             f'a fixed number of cycles per inference</text>')
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


def build():
    out = []
    out += _write("p10-mb-model", 1020, 406, mb_model)
    out += _write("p10-hil-match", 960, 212, hil_match)
    out += save_mpl("p10-accuracy-snr", accuracy_snr, figsize=(8.6, 4.6))
    out += _write("p10-feature-engine", 1020, 212, feature_engine)
    out += _write("p10-flow", 870, 196, flow)
    return out


if __name__ == "__main__":
    for path in build():
        print(path.name)
