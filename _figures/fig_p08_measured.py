"""Part 8: the two measured results that read better as pictures than as sentences.

Both figures are drawn only from numbers stated in the post text:
  p08-link-rate    frame-counter rates of boards B and C against the host clock
  p08-lane-delays  how few of the 28 lane pairs keep a steady delay
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bmafig import save_mpl  # noqa: E402

RATE_B = 48010.71   # records per second against the host PC clock, 150 s, one run
RATE_C = 48010.39
NOMINAL = 48000.0
HOST_UNCERTAINTY_HZ = 10.0

PAIRS = 28
STEADY_LIVE = 2          # saved live capture, 1,500 windows
STEADY_MAX_CAPTURES = 4  # best of six captures (upper bound)
LAG_LO, LAG_HI = -7.6, 3.3  # lane 0 to 1 lag range across six captures, samples


def link_rate():
    def draw(fig, p, theme):
        ax = fig.add_subplot(111)
        ax.axvspan(NOMINAL - HOST_UNCERTAINTY_HZ, NOMINAL + HOST_UNCERTAINTY_HZ,
                   color=p["gold"], alpha=0.0)
        rows = [("board C", RATE_C, p["teal"]), ("board B", RATE_B, p["blue"])]
        for y, (label, rate, colour) in enumerate(rows):
            ax.errorbar(rate, y, xerr=HOST_UNCERTAINTY_HZ, fmt="o", color=colour,
                        ecolor=colour, elinewidth=2.2, capsize=5, markersize=8)
            ax.text(rate, y + 0.22, f"{rate:,.2f}", ha="center", va="bottom",
                    color=p["fg"], fontsize=10)
        ax.axvline(NOMINAL, color=p["red"], lw=1.6, ls="--")
        ax.text(NOMINAL + 0.4, 1.62, "48,000 (nominal)", color=p["red"], fontsize=10,
                va="center")
        ax.set_yticks([0, 1])
        ax.set_yticklabels([r[0] for r in rows])
        ax.set_ylim(-0.7, 1.9)
        ax.set_xlim(47996, 48026)
        ax.set_xlabel("frame-counter records per second, against the host PC's clock")
        ax.set_title("The two boards cannot be told apart, and neither can the PC's clock")
        ax.grid(axis="y", visible=False)
        ax.text(0.99, 0.04, "bars: about ±10 Hz, the host clock's absolute uncertainty\n"
                "difference between boards: 0.32 Hz (one run)",
                transform=ax.transAxes, ha="right", va="bottom", color=p["muted"], fontsize=9)

    return save_mpl("p08-link-rate", draw, figsize=(9, 3.3))


def lane_delays():
    def draw(fig, p, theme):
        gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.25], wspace=0.62)

        ax = fig.add_subplot(gs[0])
        ax.barh([0], [LAG_HI - LAG_LO], left=[LAG_LO], height=0.34, color=p["red"], alpha=0.85)
        ax.axvline(0, color=p["edge"], lw=1)
        ax.text(LAG_LO, 0.28, f"{LAG_LO:+.1f}", ha="center", color=p["fg"], fontsize=10)
        ax.text(LAG_HI, 0.28, f"{LAG_HI:+.1f}", ha="center", color=p["fg"], fontsize=10)
        ax.set_ylim(-0.6, 0.7)
        ax.set_xlim(-10, 6)
        ax.set_yticks([])
        ax.set_xlabel("samples")
        ax.set_title("Lane 0 to 1 lag, range across six captures")
        ax.grid(axis="y", visible=False)

        bx = fig.add_subplot(gs[1])
        rows = [("saved live capture\n(1,500 windows)", STEADY_LIVE, p["green"]),
                ("best of six captures\n(at most)", STEADY_MAX_CAPTURES, p["blue"])]
        for y, (label, n, colour) in enumerate(rows):
            for i in range(PAIRS):
                bx.add_patch(__import__("matplotlib").patches.Rectangle(
                    (i, y - 0.32), 0.82, 0.64,
                    facecolor=colour if i < n else "none",
                    edgecolor=colour if i < n else p["edge"], lw=1.0))
            bx.text(PAIRS + 0.6, y, f"{n} of {PAIRS}", va="center", color=p["fg"], fontsize=11)
        bx.set_xlim(-0.3, PAIRS + 5)
        bx.set_ylim(-0.8, 1.8)
        bx.set_yticks([0, 1])
        bx.set_yticklabels([r[0] for r in rows], fontsize=9)
        bx.set_xticks([])
        bx.set_title("Lane pairs holding within one sample")
        bx.grid(visible=False)
        for s in ("left", "bottom"):
            bx.spines[s].set_visible(False)
        bx.tick_params(axis="y", length=0)
        bx.text(0, -0.72, "each square is one of the 28 pairs; filled squares are counts, "
                "not particular pairs", color=p["muted"], fontsize=8.5, va="top")

    return save_mpl("p08-lane-delays", draw, figsize=(11.5, 3.0))


def build():
    return link_rate() + lane_delays()


if __name__ == "__main__":
    for path in build():
        print(path)
