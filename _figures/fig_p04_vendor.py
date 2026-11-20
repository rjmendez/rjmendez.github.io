"""Part 4 figures: the vendor stack.

p04-ioctl-cmd   bit layout of the c1fpga ioctl numbers and what the driver does with them (c1fpga.ko disassembly)
p04-cs4-sweep   the 16,128-word read-only sweep of the CS4 window (data/p04-cs4-sweep.txt, measured 2026-10-05)
p04-meter-trace vendor level meters during a stimulus test (data/p04-meter-stim.csv, measured 2026-10-04)
p04-aperture    which of the 121 elements carry signal on the stock bitstream (echo-canceller group sweep)
"""
from __future__ import annotations

import re
from pathlib import Path

from bmafig import save_mpl, save_svg_template

DATA = Path(__file__).resolve().parent / "data"
BASE = 0x64000000


# ---------------------------------------------------------------- ioctl numbers

IOCTL_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 300" font-family="Segoe UI, Arial, sans-serif">
  <style>
    .t{{font-size:13px;fill:{fg}}} .s{{font-size:12px;fill:{muted}}} .h{{font-size:12px;font-weight:600;fill:{muted};letter-spacing:.5px}}
    .m{{font-family:Consolas,monospace;font-size:13px;fill:{fg}}} .mb{{font-family:Consolas,monospace;font-size:15px;font-weight:600;fill:{fg}}}
  </style>
  <text x="20" y="24" class="h">IOCTL NUMBER 0xC0046B01, AS _IOC() PACKS IT</text>
  <text x="20" y="54" class="s">bit 31</text><text x="840" y="54" text-anchor="end" class="s">bit 0</text>
  <rect x="20" y="62" width="100" height="44" fill="{panel}" stroke="{purple}" stroke-width="1.5"/>
  <rect x="120" y="62" width="320" height="44" fill="{panel2}" stroke="{red}" stroke-width="1.5"/>
  <rect x="440" y="62" width="200" height="44" fill="{panel}" stroke="{blue}" stroke-width="1.5"/>
  <rect x="640" y="62" width="200" height="44" fill="{panel}" stroke="{green}" stroke-width="1.5"/>
  <text x="70" y="90" text-anchor="middle" class="mb">11</text>
  <text x="280" y="90" text-anchor="middle" class="mb">00 0000 0000 0100</text>
  <text x="540" y="90" text-anchor="middle" class="mb">0110 1011</text>
  <text x="740" y="90" text-anchor="middle" class="mb">0000 0001</text>
  <text x="70" y="124" text-anchor="middle" class="t">dir = R|W</text>
  <text x="280" y="124" text-anchor="middle" class="t">size = 4</text>
  <text x="540" y="124" text-anchor="middle" class="t">type = 0x6B ('k')</text>
  <text x="740" y="124" text-anchor="middle" class="t">nr = 0x01..0x04</text>
  <text x="280" y="142" text-anchor="middle" class="s" fill="{red}">driver copies 12 bytes (100 for bulk)</text>
  <text x="740" y="142" text-anchor="middle" class="s">idx = nr - 1</text>

  <text x="20" y="182" class="h">WHAT c1fpga.ko DOES WITH IT</text>
  <text x="20" y="206" class="m">idx = cmd + 0x3FFB94FF</text>
  <text x="250" y="206" class="s">the base is stored negated, so grep for C0046B01 finds nothing</text>
  <text x="20" y="230" class="m">idx &gt; 3  -&gt;  return 0</text>
  <text x="250" y="230" class="s">unknown commands succeed silently</text>
  <text x="20" y="254" class="m">arg = &amp;ptr  -&gt;  struct</text>
  <text x="250" y="254" class="s">pointer to a pointer; passing the struct directly gives EFAULT</text>
  <text x="20" y="282" class="m">0 read  1 log dump  2 write  3 bulk write (16 regs)</text>
</svg>
"""


def ioctl_cmd():
    cmd = 0xC0046B01
    assert (cmd >> 30, (cmd >> 16) & 0x3FFF, (cmd >> 8) & 0xFF, cmd & 0xFF) == (3, 4, 0x6B, 1)
    assert (cmd + 0x3FFB94FF) & 0xFFFFFFFF == 0
    return save_svg_template("p04-ioctl-cmd", IOCTL_SVG)


# ---------------------------------------------------------------- CS4 sweep

def read_sweep():
    mem = {}
    for ln in open(DATA / "p04-cs4-sweep.txt", encoding="ascii"):
        m = re.match(r"^0x([0-9A-Fa-f]+) - (.*)$", ln.strip())
        if m:
            a = int(m.group(1), 16)
            for i, w in enumerate(m.group(2).split()):
                mem[a + 2 * i] = int(w, 16)
    return mem


def cs4_sweep():
    import numpy as np
    from matplotlib.colors import ListedColormap

    mem = read_sweep()
    assert len(mem) == 16128
    nwords = 0x120 // 2  # register file occupies +0x000..+0x11F of every bank
    vals = np.array([[mem[BASE + b * 0x800 + 2 * w] for w in range(nwords)] for b in range(1, 16)])
    mode = [max(set(col), key=list(col).count) for col in vals.T]
    # classes: 0 same as other banks, 1 echo word, 2 +0x07E, 3 other difference
    cls = np.zeros_like(vals)
    for w in range(nwords):
        for b in range(15):
            if vals[b, w] != mode[w] or len(set(vals[:, w])) == 15:
                cls[b, w] = 1 if w == 1 else 2 if w == 0x7E // 2 else 3
    echo = [mem[BASE + b * 0x800 + 2] for b in range(1, 16)]
    assert echo == [b << 4 for b in range(1, 16)]
    assert {(b, w * 2) for b, w in zip(*np.nonzero(cls == 3))} == {(0, 0x88), (0, 0x8C), (0, 0x8E)}
    # outside the register file: everything reads the 0x0002 fill except one burst in bank 6
    odd = sorted(a for a, v in mem.items() if v != 2 and (a - BASE) % 0x800 >= 0x120)
    assert odd[0] == BASE + 6 * 0x800 + 0x26C and len(odd) == 74

    def draw(fig, p, theme):
        cmap = ListedColormap([p["grid"], p["blue"], p["gold"], p["red"]])
        ax = fig.add_axes([0.09, 0.14, 0.88, 0.56])
        ax.imshow(cls, cmap=cmap, vmin=0, vmax=3, aspect="auto", interpolation="nearest",
                  extent=(-0.5, nwords - 0.5, 15.5, 0.5))
        ax.grid(False)
        ax.set_yticks([1, 5, 10, 15])
        ax.set_ylabel("bank (base + N x 0x800)")
        ticks = list(range(0, nwords + 1, 16))
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"+0x{2 * t:03X}" for t in ticks], fontsize=9)
        ax.set_xlim(-0.5, nwords - 0.5)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title("CS4 window, banks 1-15: word-by-word difference from the other banks", pad=62)
        lab = dict(fontsize=9.5, color=p["fg"])
        ax.annotate("+0x002 = N << 4", xy=(1, 0.5), xytext=(3, -1.6),
                    annotation_clip=False, ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", color=p["muted"], lw=0.8), **lab)
        ax.annotate("+0x07E: differs in every bank (a live value)",
                    xy=(0x7E // 2, 0.5), xytext=(20, -3.4), annotation_clip=False, ha="left",
                    va="center", arrowprops=dict(arrowstyle="-", color=p["muted"], lw=0.8), **lab)
        ax.annotate("+0x088/08C/08E: 0000/0005/0000 in bank 1,\n00FF/FF05/00FF in banks 2-15",
                    xy=(0x8C // 2, 0.5), xytext=(73, -1.6), annotation_clip=False, ha="left",
                    va="center", arrowprops=dict(arrowstyle="-", color=p["muted"], lw=0.8), **lab)
        fig.text(0.09, 0.015,
                 "Grey: identical in all 15 banks. +0x120..+0x7FF of every bank reads 0x0002 "
                 "(one 74-word burst of 0x0000 in bank 6). Read-only sweep, measured.",
                 fontsize=9.5, color=p["muted"])

    return save_mpl("p04-cs4-sweep", draw, figsize=(10, 4.6))


# ---------------------------------------------------------------- meters

def read_meters():
    rows = []
    for ln in open(DATA / "p04-meter-stim.csv", encoding="ascii"):
        if ln.startswith("#") or "=" not in ln:
            continue
        parts = ln.strip().split(",")
        regs = {int(k, 16): int(v, 16) for k, v in (x.split("=") for x in parts[1:])}
        rows.append((int(parts[0]) / 1000.0, regs))
    return rows


def to_db(byte):
    return None if byte == 0 else max(-99, 20 - (byte >> 1))


def meter_trace():
    rows = read_meters()
    t = [r[0] for r in rows]
    pre = [to_db(r[1][0x76] >> 8) for r in rows]
    post = [to_db(r[1][0x76] & 0xFF) for r in rows]
    t_dsp = next(tt for tt, r in rows if r[0x96])
    t_76 = next(tt for tt, r in rows if r[0x76])

    def draw(fig, p, theme):
        ax = fig.add_subplot(111)
        ax.plot(t, [v if v is not None else float("nan") for v in pre], lw=0.9, color=p["blue"],
                label="0x76 high byte (pre-gain)")
        ax.plot(t, [v if v is not None else float("nan") for v in post], lw=0.9, color=p["red"],
                label="0x76 low byte (post-gain)")
        ax.axvspan(0, t_dsp, color=p["grid"], alpha=0.6, lw=0)
        ax.text(t_dsp / 2, 8, "all meters read 0x0000\n(DSPs not loaded)", ha="center", va="top",
                fontsize=9.5, color=p["muted"])
        ax.axvline(t_76, color=p["muted"], lw=0.8, ls="--")
        ax.text(t_76 + 0.8, 15, f"0x76 comes alive, t = {t_76:.1f} s", fontsize=9.5,
                color=p["muted"], va="top")
        ax.set_xlim(0, t[-1])
        ax.set_ylim(-52, 18)
        ax.annotate("first live read -99 dB, off scale", xy=(t_76, -52), xytext=(t_76 + 1.5, -49),
                    fontsize=9, color=p["muted"])
        ax.set_xlabel("seconds")
        ax.set_ylabel("dB = 20 - (byte >> 1)")
        ax.set_title("Vendor level meter 0x76 during a stimulus test, ~20 reads/s", pad=10)
        ax.legend(loc="lower left", fontsize=9.5)

    return save_mpl("p04-meter-trace", draw, figsize=(10, 4))


# ---------------------------------------------------------------- aperture

def aperture():
    def draw(fig, p, theme):
        from matplotlib.patches import Rectangle

        ax = fig.add_axes([0.02, 0.18, 0.96, 0.62])
        ax.set_xlim(-0.5, 16 * 9)
        ax.set_ylim(-0.4, 1.6)
        ax.axis("off")
        mic = 1
        for g in range(16):
            n = 1 if g == 15 else 8
            silent = 12 <= g <= 14
            x0 = g * 9
            for i in range(n):
                ax.add_patch(Rectangle((x0 + i, 0), 0.85, 0.85,
                                       facecolor=p["red"] if silent else p["green"], edgecolor="none"))
                mic += 1
            ax.text(x0 + n / 2 - 0.1, 1.05, str(g), ha="center", fontsize=9, color=p["muted"])
        ax.text(-0.5, 1.45, "element group", fontsize=9, color=p["muted"])
        ax.text(12 * 9 + 13, -0.3, "mics 97-120: silent", ha="center", va="top", fontsize=10,
                color=p["red"], fontweight="semibold")
        ax.text(6 * 9 - 1, -0.3, "mics 1-96: live", ha="center", va="top", fontsize=10, color=p["green"])
        ax.text(15 * 9 + 0.4, -0.3, "121", ha="center", va="top", fontsize=10, color=p["green"])
        assert mic - 1 == 121
        fig.text(0.02, 0.92, "Which elements carry signal on the stock bitstream (97 of 121)",
                 fontsize=13, fontweight="semibold", color=p["fg"])

    return save_mpl("p04-aperture", draw, figsize=(10, 1.9))


def build():
    out = []
    out += ioctl_cmd()
    out += cs4_sweep()
    out += meter_trace()
    out += aperture()
    return out
