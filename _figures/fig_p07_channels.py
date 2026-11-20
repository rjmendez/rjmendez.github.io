"""Part 7 figures: what the eight Dante channels look like on the wire.

p07-channel-levels       per-channel RMS for three captures + per-channel spectra (data/p07-dante-channels.json)
p07-channel-correlation  8x8 correlation matrix and cross-correlation lag vs channel 0 (same data)
p07-mirror-fit           the two mirror-image two-array layouts that fit the ambient delays equally well
                         (numbers from the Part 7 delay fit; no audio)

data/p07-dante-channels.json was derived from three Dante captures of one tile on 2026-11-03 (stock
firmware and configuration): levels, Welch spectra and correlations only. Its "provenance" field says how.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from bmafig import save_mpl

DATA = Path(__file__).resolve().parent / "data"


def _load():
    return json.loads((DATA / "p07-dante-channels.json").read_text(encoding="utf-8"))


def _caps(d):
    return {c["label"]: c for c in d["captures"]}


def levels():
    d = _load()
    caps = _caps(d)
    ch = np.arange(8)

    def draw(fig, p, theme):
        ax1, ax2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.45], "wspace": 0.28})
        for (lab, c), col in zip(sorted(caps.items()), (p["blue"], p["red"], p["green"])):
            ax1.plot(ch, c["rms_dbfs"], "o-", color=col, lw=1.8,
                     label=f"capture {lab} ({c['seconds']:.2f} s)")
        ax1.set_xticks(ch)
        ax1.set_xlabel("Dante channel")
        ax1.set_ylabel("RMS (dBFS)")
        ax1.set_title("Level per channel")
        ax1.set_ylim(-50, -33)
        ax1.legend(loc="center", bbox_to_anchor=(0.55, 0.52), fontsize=9)

        c = caps["B"]
        f = np.array(c["psd_freq_hz"])
        P = np.array(c["psd_db_per_hz"])
        m = f >= 20
        cmap = [p["blue"], p["teal"], p["green"], p["gold"], p["red"], p["purple"], p["muted"], p["fg"]]
        for i in range(8):
            ax2.semilogx(f[m], P[i][m], color=cmap[i], lw=1.1, label=f"ch {i}")
        ax2.set_xlim(20, 24000)
        ax2.set_xlabel("Frequency (Hz)")
        ax2.set_ylabel("PSD (dB/Hz re full scale)")
        ax2.set_title("Spectrum per channel, capture B")
        ax2.legend(ncol=4, fontsize=8.5, loc="upper right", handlelength=1.2, columnspacing=0.8)
        fig.text(0.01, -0.04, "Measured: Dante packets from one tile, stock firmware, 48 kHz, 24-bit. "
                 "Ambient room sound, no controlled source.", color=p["muted"], fontsize=9)

    return save_mpl("p07-channel-levels", draw, figsize=(11, 4.2))


def correlation():
    d = _load()
    caps = _caps(d)
    ch = np.arange(8)

    def draw(fig, p, theme):
        from matplotlib.colors import LinearSegmentedColormap

        ax1, ax2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.2], "wspace": 0.35})
        C = np.array(caps["B"]["corr"])
        cm = LinearSegmentedColormap.from_list("t", [p["panel"], p["blue"]])
        im = ax1.imshow(C, vmin=0.5, vmax=1.0, cmap=cm)
        ax1.grid(False)
        for i in range(8):
            for j in range(8):
                v = C[i, j]
                ax1.text(j, i, f"{v:.2f}"[1:] if v < 1 else "1", ha="center", va="center", fontsize=7.5,
                         color=p["bg"] if v > 0.8 else p["fg"])
        ax1.set_xticks(ch)
        ax1.set_yticks(ch)
        ax1.set_xlabel("channel")
        ax1.set_ylabel("channel")
        ax1.set_title("Correlation, capture B")
        cb = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.03)
        cb.outline.set_edgecolor(p["edge"])
        cb.ax.tick_params(colors=p["muted"])

        for (lab, c), col in zip(sorted(caps.items()), (p["blue"], p["red"], p["green"])):
            ax2.plot(ch, c["lag_vs_ch0_samples"], "o-", color=col, lw=1.8, label=f"capture {lab}")
        ax2.axhline(0, color=p["edge"], lw=0.8)
        ax2.set_xticks(ch)
        ax2.set_xlabel("channel")
        ax2.set_ylabel("lag of peak vs channel 0 (samples @ 48 kHz)")
        ax2.set_title("Cross-correlation peak vs channel 0")
        ax2.legend(fontsize=9, loc="upper left")

    return save_mpl("p07-channel-correlation", draw, figsize=(11, 4.4))


def mirror_fit():
    a = (0.135, -0.180, 0.942)
    b = (0.942, -0.180, 0.135)

    def draw(fig, p, theme):
        ax = fig.subplots()
        ax.plot([-0.2, 0.8], [-0.2, 0.8], ls="--", color=p["faint"], lw=1)
        ax.text(0.62, 0.55, "mirror line x = z", color=p["faint"], fontsize=9, rotation=45,
                ha="center", va="center")
        ax.scatter([0], [0], s=160, marker="s", color=p["fg"], zorder=3)
        ax.annotate("array 1", (0, 0), xytext=(10, -14), textcoords="offset points", fontsize=10)
        for (x, _, z), lab, col in ((a, "ordinary", p["blue"]), (b, "mirrored", p["red"])):
            ax.scatter([x], [z], s=160, marker="s", color=col, zorder=3)
            ax.plot([0, x], [0, z], color=col, lw=1.2, alpha=0.7)
            ax.annotate(f"array 2, {lab}\n({x:.3f}, {z:.3f}) m", (x, z), xytext=(10, 6),
                        textcoords="offset points", fontsize=9.5, color=col)
        ax.set_xlim(-0.2, 1.6)
        ax.set_ylim(-0.2, 1.2)
        ax.set_aspect("equal")
        ax.set_xlabel("model x (m)")
        ax.set_ylabel("model z (m)")
        ax.set_title("Two layouts, one fit")
        rows = ["cost 55.81 / 55.81", "offset -10 / -10 samples", "residuals <= 2 samples 0.98 / 0.98",
                "range 0.969 / 0.969 m", "y = -0.180 m in both"]
        ax.text(0.98, 0.97, "\n".join(rows), transform=ax.transAxes, ha="right", va="top", fontsize=9,
                color=p["muted"], family="monospace")

    return save_mpl("p07-mirror-fit", draw, figsize=(7.6, 5.4))


def build():
    return levels() + correlation() + mirror_fit()
