"""Three ants, three split points, on each of the three published Part 9 clips (real audio)."""
from __future__ import annotations

import csv
from pathlib import Path

from bmafig import save_mpl
from fig_p10_figures import _arrow, _box, _lines, _write

DATA = Path(__file__).parent / "data"
CLIPS = [("carolina-wren", "Carolina Wren"), ("hairy-woodpecker", "Hairy Woodpecker"),
         ("white-throated-sparrow", "White-throated Sparrow")]
SPLITS = {2: "about 1.9 kHz", 3: "955 Hz", 4: "477 Hz"}


def _rows():
    with (DATA / "p10-ant-real.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def real_ants(fig, p, theme):
    import numpy as np
    from gen_p10_ant_real import FS, WINDOW, load

    rows = _rows()
    cols = {2: p["blue"], 3: p["green"], 4: p["purple"]}
    gs = fig.add_gridspec(3, 3, height_ratios=[1.0, 0.9, 0.9], hspace=0.14, wspace=0.12)
    cmap = "magma" if theme == "dark" else "Greys"
    for c, (slug, title) in enumerate(CLIPS):
        sig = load(slug).astype(float) / (1 << 23)
        n = len(sig) // WINDOW
        frames = sig[: n * WINDOW].reshape(n, WINDOW) * np.hanning(WINDOW)
        spec = 20 * np.log10(np.abs(np.fft.rfft(frames, axis=1)) + 1e-9).T
        kmax = int(10000 / (FS / WINDOW))
        secs = n * WINDOW / FS
        a1 = fig.add_subplot(gs[0, c])
        a2 = fig.add_subplot(gs[1, c], sharex=a1)
        a3 = fig.add_subplot(gs[2, c], sharex=a1)
        a1.imshow(spec[:kmax], origin="lower", aspect="auto", cmap=cmap, extent=(0, secs, 0, 10),
                  vmin=spec.max() - 70, vmax=spec.max())
        a1.grid(False)
        a1.set_title(title, fontsize=11)
        for k in (2, 3, 4):
            sel = [r for r in rows if r["clip"] == slug and int(r["lp_shift"]) == k]
            t = [float(r["t_end_s"]) for r in sel]
            a2.step(t, [int(r["d"]) for r in sel], where="mid", color=cols[k], lw=1.3,
                    label=f"ant split {SPLITS[k]}")
            a3.step(t, [int(r["r_high"]) for r in sel], where="mid", color=cols[k], lw=1.3)
        a1.set_xlim(0, secs)
        a3.set_xlabel("seconds")
        for a in (a1, a2):
            a.tick_params(labelbottom=False)
        if c == 0:
            a1.set_ylabel("kHz")
            a2.set_ylabel("band ratio\n(steps)")
            a3.set_ylabel("high band above\nfloor (steps)")
        else:
            for a in (a1, a2, a3):
                a.tick_params(labelleft=False)
    h, l = a2.get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=9.5, frameon=False, bbox_to_anchor=(0.5, -0.07))
    fig.text(0.01, -0.11, "Real array audio, but the published clips: one Dante channel, high-passed at 1 kHz, "
             "boosted 33 to 52 dB, lossy. Integer reference encoder on a PC; no board run.",
             color=p["muted"], fontsize=9)


def edge_classify(p):
    s = ['<text x="20" y="22" font-weight="600" font-size="14">Following at the edge: fast reflex first, the hub names it later</text>']
    steps = [("Any sound", "cars, drones, birds, voices", "the array hears it", p["edge"]),
             ("Ants", "features and flags", "simulation", p["blue"]),
             ("Follow", "bearing hint, beam steer", "design", p["faint"]),
             ("Code rides along", "versioned, experimental", "design", p["faint"]),
             ("Zynq filter", "drops stale or false", "design", p["faint"]),
             ("Hub names it", "BirdNET, Perch", "runs today", p["edge"])]
    w, gap = 155, 22
    for i, (t, sub, st, col) in enumerate(steps):
        x = 20 + i * (w + gap)
        s.append(_box(x, 44, w, 56, p["panel"], col, t, sub, p, size=12.5, dash=(col == p["faint"])))
        s.append(f'<text x="{x + w / 2}" y="118" text-anchor="middle" font-size="10.5" fill="{p["muted"]}">{st if i else "the array hears it"}</text>')
        if i:
            s.append(_arrow(x - gap, 72, x, 72, p))
    ideas = [("Measure the reflex", ["First sound to beam steer, impulse", "recall and false triggers, on real", "audio. None measured yet."]),
             ("A separate onset path", ["A 21 ms window and two flagged", "windows can miss one chirp or click.", "Add a short-window onset path."]),
             ("Direction, then steer", ["One broadside sum has no direction.", "A direction estimator and track", "manager guide steer requests."]),
             ("Prove what rides along", ["The 64-bit code is not mel and not", "proven useful to the hub. Version it,", "stamp it, test it against hub verdicts."]),
             ("False triggers are cheap", ["Wrong reflexes cost a beam move.", "The Zynq and hub filter them, so", "tune the ant for speed."]),
             ("Several sources at once", ["Different ants on different beams", "can hold different sources. The", "tracker decides who is who."])]
    bw, bh = 340, 86
    for i, (t, lines) in enumerate(ideas):
        x = 20 + (i % 3) * (bw + 15)
        y = 150 + (i // 3) * (bh + 12)
        s.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="6" fill="{p["panel"]}" stroke="{p["faint"]}" '
                 f'stroke-width="1.5" stroke-dasharray="5 4"/>')
        s.append(f'<text x="{x + 12}" y="{y + 21}" font-size="12.5" font-weight="600">{t}</text>')
        s.append(_lines(x + 12, y + 41, lines, p, size=11, step=15, anchor="start"))
    return "\n".join(s)


def build():
    out = save_mpl("p10-ant-real", real_ants, figsize=(11, 6.2))
    out += _write("p10-edge-reflex", 1090, 340, edge_classify)
    return out
