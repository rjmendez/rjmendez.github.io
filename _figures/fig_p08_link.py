"""Part 8 figures: the one wire out, and the scorecard.

p08-link1w-frame   LINK1W v1 tick drawn to scale: 17-cell lead-in, then 512 cells per 48 kHz tick
                   (layout from docs/LINK1W.md in the firmware repo)
p08-link1w-wave    R9 as driven by rtl/link1w_tx.v in Icarus, synthetic 'ramp8' fixture
                   (data/p08-link1w-rtl-ramp8.csv, sampled from the VCD)
p08-scorecard      every result in the series by part and status
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from bmafig import save_mpl

DATA = Path(__file__).resolve().parent / "data"

LEAD = 17
# (name, cells, colour key)
TICK = [("preamble", 6, "red"), ("header", 16, "gold")] + \
       [(f"w{i}", 48, "blue" if i % 2 == 0 else "teal") for i in range(8)] + \
       [("CRC-8", 16, "purple"), ("idle", 90, "faint")]


def _segments(start):
    """[(name, x0, width, colour)] for a lead-in at `start` followed by one tick."""
    segs = [("lead-in", start, LEAD, "green")]
    x = start + LEAD
    for name, n, ck in TICK:
        segs.append((name, x, n, ck))
        x += n
    return segs


def frame():
    def draw(fig, p, theme):
        from matplotlib.patches import Rectangle

        ax = fig.subplots()
        ax.grid(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_visible(False)
        ax.set_yticks([])
        y, h = 0.0, 1.0
        for name, x0, w, ck in _segments(-LEAD):
            ax.add_patch(Rectangle((x0, y), w, h, facecolor=p[ck], edgecolor=p["bg"], lw=1.2,
                                   alpha=0.35 if ck == "faint" else 0.9))
            if name.startswith("w"):
                ax.text(x0 + w / 2, y + h / 2, name, ha="center", va="center", fontsize=9, color=p["bg"])
        # labels above / below
        for txt, xt, yt, xa, ya, ha in (("lead-in 17", -20, -0.4, None, None, "left"),
                                        ("preamble 6", 34, -0.4, 3, 0.0, "left"),
                                        ("header 16", 14, 1.25, None, None, "left"),
                                        ("CRC-8 16", 414, -0.4, None, None, "center"),
                                        ("idle 90 (bit 1 repeated)", 467, 1.25, None, None, "center")):
            if xa is None:
                ax.text(xt, yt, txt, ha=ha, va="center", fontsize=9.5, color=p["fg"])
            else:
                ax.annotate(txt, xy=(xa, ya), xytext=(xt, yt), ha=ha, va="center", fontsize=9.5,
                            color=p["fg"], arrowprops=dict(arrowstyle="-", color=p["muted"], lw=0.8))
        ax.annotate("", xy=(22, 1.55), xytext=(406, 1.55),
                    arrowprops=dict(arrowstyle="<->", color=p["muted"], lw=1))
        ax.text(214, 1.72, "8 words x 24 bit = 384 cells (Manchester, 2 cells per bit)", ha="center",
                fontsize=9.5, color=p["muted"])
        ax.annotate("", xy=(0, -0.75), xytext=(512, -0.75),
                    arrowprops=dict(arrowstyle="<->", color=p["fg"], lw=1.2))
        ax.text(256, -0.95, "one 48 kHz tick = 512 cells at 24.576 MBd", ha="center", va="top",
                fontsize=10, color=p["fg"])
        ax.set_xlim(-LEAD - 4, 516)
        ax.set_ylim(-1.4, 2.0)
        ax.set_xticks([-17, 0, 22, 406, 422, 512])
        ax.tick_params(axis="x", labelsize=8.5)
        ax.set_xlabel("cell")
        ax.set_title("LINK1W v1 on R9 \u2192 W13")
        ax.text(0.0, -0.36, "Receiver acquisition at non-nominal rates wants >= 20 idle edges; "
                "the transmitter sends a 17-cell lead-in.", transform=ax.transAxes, fontsize=9.5,
                color=p["red"])

    return save_mpl("p08-link1w-frame", draw, figsize=(11, 3.4))


def _cells():
    rows = [ln.split(",") for ln in (DATA / "p08-link1w-rtl-ramp8.csv").read_text().splitlines()
            if ln and not ln.startswith("#") and not ln.startswith("cell")]
    en = np.array([int(r[1]) for r in rows])
    r9 = np.array([int(r[2]) for r in rows])
    return en, r9


def wave():
    en, r9 = _cells()
    start = int(np.argmax(en))  # first enabled cell = first lead-in cell

    def draw(fig, p, theme):
        ax1, ax2 = fig.subplots(2, 1, gridspec_kw={"height_ratios": [1, 1.25], "hspace": 0.75})
        x = np.arange(len(r9) + 1)
        segs = _segments(start)
        for ax, lo, hi in ((ax1, 0, len(r9)), (ax2, start - 4, start + 17 + 6 + 16 + 48 + 2)):
            for name, x0, w, ck in segs:
                if x0 + w < lo or x0 > hi:
                    continue
                ax.axvspan(max(x0, lo), min(x0 + w, hi), color=p[ck], alpha=0.18 if ck != "faint" else 0.1,
                           lw=0)
            ax.step(x[lo:hi + 1], np.r_[r9, r9[-1]][lo:hi + 1], where="post", color=p["fg"], lw=1.1)
            ax.set_xlim(lo, hi)
            ax.set_ylim(-0.25, 1.45)
            ax.set_yticks([0, 1])
            ax.set_yticklabels(["low", "high"])
            ax.grid(False)
        ax1.axvspan(0, start, color=p["faint"], alpha=0.12, lw=0)
        ax1.text(start / 2, 1.22, "disabled", ha="center", fontsize=8.5, color=p["muted"])
        for name, x0, w, ck in segs:
            if name in ("lead-in", "w0", "w3", "w7", "CRC-8"):
                ax1.text(x0 + w / 2, 1.22, name, ha="center", fontsize=8.5, color=p[ck] if ck != "faint"
                         else p["muted"])
        ax1.set_title("R9 from rtl/link1w_tx.v, whole run (483 cells)")
        ax1.set_xlabel("cell (24.576 MHz clock)")

        # zoom: label each decoded bit
        names = {"lead-in": "lead-in: (low, high) x 8 + low", "preamble": "preamble",
                 "header": "header 0x18 (ver 1, n 8)", "w0": "w0 = 0x000001"}
        for name, x0, w, ck in segs:
            if name in names:
                ax2.text(x0 + w / 2, 1.24, names[name], ha="center", fontsize=8.5, color=p["fg"])
        hdr0 = start + LEAD + 6
        bits = "00011000" + "000000000000000000000001"
        for i, b in enumerate(bits[:8 + 24]):
            cx = hdr0 + 2 * i + 1
            if cx < start + 17 + 6 + 16 + 48 + 2:
                ax2.text(cx, -0.12, b, ha="center", va="top", fontsize=8.5, color=p["muted"],
                         family="monospace")
        ax2.set_ylim(-0.6, 1.45)
        ax2.set_title("Zoom: lead-in, preamble, header, first word (bit values below)")
        ax2.set_xlabel("cell")
        fig.text(0.01, -0.03, "RTL simulation, synthetic fixture 'ramp8' (Icarus Verilog). "
                 "Matches the checked-in reference vector cell for cell. Not hardware.",
                 color=p["red"], fontsize=9.5)

    return save_mpl("p08-link1w-wave", draw, figsize=(11, 5.0))


# status key -> (label, colour key)
STATUS = {
    "si": ("real silicon", "green"),
    "mech": ("mechanism only", "gold"),
    "fail": ("failed", "red"),
    "open": ("unresolved", "purple"),
    "host": ("host / RTL tests, not on a board", "blue"),
    "sim": ("simulation", "faint"),
}

RESULTS = [
    ("si", 2, "serial console + own kernel on the OMAP"),
    ("si", 3, "shell on the Brooklyn-3 Zynq"),
    ("si", 4, "FPGA register reads, version 0x0117"),
    ("si", 4, "level meters move to real sound"),
    ("si", 5, "own loader loads + identifies the DSPs (52 s, 41/41)"),
    ("si", 5, "one-word ISR hook executes, reversibly"),
    ("si", 6, "one frame of real mic audio off DSP4's ring"),
    ("si", 6, "indexed-copy probe v2: 0/48 wrong"),
    ("mech", 6, "in-memory bit-exact beam, one DSP4 snapshot"),
    ("fail", 6, "indexed-copy probe v1: 42/48 wrong"),
    ("open", 7, "eight Dante channels: gated beams or raw mics"),
    ("open", 7, "602-603 sample lag"),
    ("host", 8, "levels-hook indexed caller: 474 pass, 110 skip"),
    ("host", 8, "Zynq receive top + ring path"),
    ("host", 8, "Cyclone TX / SHARC return: 12 synthetic RTL tests"),
    ("host", 8, "Zynq-PL egress source: needs a live PL ring"),
    ("host", 8, "virtual-edge tracks on live input: noise level"),
    ("sim", 8, "DOA bearings from generated sources"),
]


def scorecard():
    def draw(fig, p, theme):
        ax = fig.subplots()
        ax.grid(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_visible(False)
        n = len(RESULTS)
        parts = list(range(2, 9))
        x0 = 0.0
        for j, part in enumerate(parts):
            ax.text(x0 + j, n + 0.2, f"P{part}", ha="center", va="bottom", fontsize=10,
                    color=p["fg"], weight="bold")
            ax.plot([x0 + j, x0 + j], [-0.6, n - 0.4], color=p["grid"], lw=0.8, zorder=0)
        prev = None
        for i, (st, part, text) in enumerate(RESULTS):
            y = n - 1 - i
            if prev is not None and st != prev:
                ax.plot([-0.5, 14.5], [y + 0.5, y + 0.5], color=p["edge"], lw=0.6)
            prev = st
            ck = STATUS[st][1]
            col = p[ck] if ck != "faint" else p["muted"]
            ax.scatter([x0 + parts.index(part)], [y], s=150, color=col, zorder=3,
                       marker="o" if st != "fail" else "X")
            ax.text(7.0, y, text, va="center", fontsize=9.5, color=p["fg"])
        # legend
        lx = 7.0
        for k, (st, (label, ck)) in enumerate(STATUS.items()):
            col = p[ck] if ck != "faint" else p["muted"]
            yy = -1.6 - (k // 3) * 0.8
            xx = -0.3 + (k % 3) * 4.9
            ax.scatter([xx], [yy], s=90, color=col, marker="o" if st != "fail" else "X")
            ax.text(xx + 0.3, yy, label, va="center", fontsize=9, color=p["muted"])
        ax.set_xlim(-0.6, 15.2)
        ax.set_ylim(-3.2, n + 0.9)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Scorecard, Parts 2-8")

    return save_mpl("p08-scorecard", draw, figsize=(10, 7.2))


def build():
    return frame() + wave() + scorecard()
