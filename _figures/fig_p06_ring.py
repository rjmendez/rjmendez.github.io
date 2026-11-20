"""Part 6 figures: what sits in DSP4's SPORT0 ring, and the index-register unit bug.

p06-frame-levels  per-slot level of one full-stack frame (data/p06-ring-levels.json, window 4)
p06-lone-dsp4     128 raw frames with only DSP4 loaded (data/p06-lone-dsp4-ring.txt)
p06-idxprobe      index-register copy vs absolute copy, probe v1 and v2 (data/p06-ring-levels.json)
p06-sport0-regs   SPORT0 and DMA registers as copied out by the MMR hook (same file)
"""
from __future__ import annotations

import json
from pathlib import Path

from bmafig import save_mpl, save_svg_template

DATA = Path(__file__).resolve().parent / "data"
FLOOR = -100


def _levels():
    return json.loads((DATA / "p06-ring-levels.json").read_text(encoding="utf-8"))


def _ring():
    rows = []
    for ln in (DATA / "p06-lone-dsp4-ring.txt").read_text(encoding="ascii").splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        w = [int(x, 16) for x in ln.split()]
        rows += [w[f * 21:(f + 1) * 21] for f in range(8)]
    return rows


# ---------------------------------------------------------------- full-stack frame levels

def frame_levels():
    d = _levels()["full_stack_window4"]
    db = {int(k): v for k, v in d["dbfs"].items()}

    def draw(fig, p, theme):
        ax = fig.add_axes([0.07, 0.2, 0.9, 0.66])
        for s in range(21):
            if s in db:
                c = p["blue"] if s <= 6 and s != 4 else (p["gold"] if s == 4 else p["green"])
                ax.bar(s, db[s] - FLOOR, bottom=FLOOR, width=0.72, color=c)
                ax.text(s, db[s] + 1.5, f"{db[s]}", ha="center", va="bottom", fontsize=8.5, color=p["fg"])
            else:
                ax.text(s, FLOOR + 1.5, "0", ha="center", va="bottom", fontsize=9, color=p["faint"])
        ax.set_xlim(-0.7, 20.7)
        ax.set_ylim(FLOOR, 0)
        ax.set_xticks(range(21))
        ax.set_xlabel("slot (word in the 21-word frame)")
        ax.set_ylabel("peak level, dBFS")
        ax.grid(axis="x", visible=False)
        ax.set_title("One frame off DSP4, with other DSPs loaded too", pad=22)
        ax.text(0, 1.03, "slots 0-3, 5, 6: microphone noise floor  |  slot 4: not a mic  |  "
                "7-18: exact zero  |  19, 20: sync constants 0x0000ff00, 0x00123456",
                transform=ax.transAxes, fontsize=9, color=p["muted"])
        ax.annotate("sparse spikes, not audio", (4, -10), (7.5, -14), fontsize=9, color=p["gold"],
                    va="center", arrowprops=dict(arrowstyle="-", color=p["gold"], lw=1))

    return save_mpl("p06-frame-levels", draw, figsize=(10, 3.4))


# ---------------------------------------------------------------- lone DSP4 raw frames

def lone_dsp4():
    frames = _ring()
    assert len(frames) == 128
    n_sync = sum(f[19] == 0xff00 and f[20] == 0x123456 for f in frames)
    nz = {s for f in frames for s in range(19) if f[s]}
    slot4 = sorted({f[4] for f in frames})

    def draw(fig, p, theme):
        import numpy as np
        from matplotlib.colors import ListedColormap

        cat = np.zeros((21, len(frames)))
        for i, f in enumerate(frames):
            for s in range(21):
                cat[s, i] = 2 if s >= 19 else (1 if f[s] else 0)
        ax = fig.add_axes([0.07, 0.18, 0.66, 0.68])
        ax.imshow(cat, aspect="auto", interpolation="nearest", origin="upper",
                  cmap=ListedColormap([p["grid"], p["gold"], p["green"]]), vmin=0, vmax=2)
        ax.set_yticks([0, 4, 6, 10, 18, 19, 20])
        ax.set_ylabel("slot")
        ax.set_xlabel("frame (16 snapshots x 8 frames)")
        ax.set_xticks([0, 32, 64, 96, 127])
        ax.grid(False)
        for s in range(1, 21):
            ax.axhline(s - 0.5, color=p["bg"], lw=0.5)
        ax.set_title(f"Only DSP4 loaded: {len(frames)} raw frames from 0x256dc8", pad=22)
        ax.text(0, 1.03, f"sync at words 19/20 in {n_sync}/{len(frames)} frames; the only non-zero slot "
                f"below 19 is slot {', '.join(map(str, sorted(nz)))}", transform=ax.transAxes, fontsize=9, color=p["muted"])

        ax2 = fig.add_axes([0.77, 0.18, 0.22, 0.68])
        ax2.axis("off")
        ax2.text(0, 1.03, f"slot 4: {len(slot4)} distinct words", transform=ax2.transAxes,
                 fontsize=10, color=p["fg"], fontweight="bold")
        from collections import Counter
        cnt = Counter(f[4] for f in frames).most_common(9)
        for i, (v, n) in enumerate(cnt):
            ax2.text(0, 0.92 - i * 0.1, f"0x{v:08x}", transform=ax2.transAxes, fontsize=9.5,
                     family="monospace", color=p["gold"] if v else p["faint"])
            ax2.text(0.72, 0.92 - i * 0.1, f"x{n}", transform=ax2.transAxes, fontsize=9.5, color=p["muted"])
        ax2.text(0, -0.1, "slots 0-3, 5, 6 are exactly 0", transform=ax2.transAxes,
                 fontsize=9, color=p["muted"])

    return save_mpl("p06-lone-dsp4", draw, figsize=(10, 3.6))


# ---------------------------------------------------------------- idxprobe v1 vs v2

def idxprobe():
    d = _levels()
    slots = [0, 1, 2, 3, 5, 6]

    def draw(fig, p, theme):
        for k, (key, title) in enumerate((("idxprobe_v1", "probe v1"), ("idxprobe_v2", "probe v2"))):
            r = d[key]
            ax = fig.add_axes([0.07 + k * 0.48, 0.2, 0.42, 0.6])
            for j, s in enumerate(slots):
                for m, (form, col, lab) in enumerate((("absolute_B", p["blue"], "absolute loads"),
                                                      ("index_A", p["red"], "DM(disp, I4)"))):
                    v = r[form][str(s)]
                    x = j + (m - 0.5) * 0.36
                    if v is None:
                        ax.text(x, FLOOR + 1.5, "0", ha="center", va="bottom", fontsize=9, color=col)
                    else:
                        ax.bar(x, v - FLOOR, bottom=FLOOR, width=0.34, color=col,
                               label=lab if j == 0 else None)
            ax.set_xticks(range(len(slots)), [str(s) for s in slots])
            ax.set_ylim(FLOOR, 0)
            ax.set_xlabel("slot")
            ax.grid(axis="x", visible=False)
            if k == 0:
                ax.set_ylabel("level, dBFS")
                ax.annotate("read word 4 (slot-4 stream)", (1.3, -10), (1.55, -6), fontsize=8.5,
                            color=p["red"], va="center",
                            arrowprops=dict(arrowstyle="-", color=p["red"], lw=1))
                ax.annotate("read word 20 (sync 0x123456)", (4.0, -24), (1.55, -30), fontsize=8.5,
                            color=p["red"], va="center",
                            arrowprops=dict(arrowstyle="-", color=p["red"], lw=1))
                ax.text(1.55, -54, "read words 8, 12: zero", fontsize=8.5, color=p["red"])
                ax.legend(loc="upper right", bbox_to_anchor=(1.0, 1.32), ncol=2, fontsize=9)
            else:
                ax.set_yticklabels([])
            ax.set_title(f"{title}: {r['wrong_words']}/{r['of']} words differ", pad=8,
                         color=p["red"] if r["wrong_words"] else p["green"])

    return save_mpl("p06-idxprobe", draw, figsize=(10, 3.4))


# ---------------------------------------------------------------- SPORT0 registers

def sport0_regs():
    r = _levels()["sport0_mmr"]["regs"]
    rows = [
        ("SPORT0_CTL_A", r["SPORT0_CTL_A"], "SPTRAN set: half A transmits. SLEN 23: 24-bit words"),
        ("SPORT0_CTL_B", r["SPORT0_CTL_B"], "half B receives, same word length"),
        ("SPORT0_MCTL_A/B", r["SPORT0_MCTL_A"], "multichannel on, WSIZE 20: a 21-slot window"),
        ("SPORT0_CS0_A/B", r["SPORT0_CS0_A"], "only slot 0 of the window is enabled"),
        ("SPORT0_CS1..3", r["SPORT0_CS1..3"], "nothing above slot 31"),
        ("SPORT0_DIV_A/B", r["SPORT0_DIV_A"], "clock and frame sync come from outside"),
        ("DMA0 ADDRSTART", r["DMA0_ADDRSTART"], "0x256dc8, one of the three ring buffers"),
        ("DMA1 ADDRSTART", r["DMA1_ADDRSTART"], "0x257308, another one"),
        ("DMA0/1 XCNT, XMOD", f'{r["DMA0_XCNT"]}, {int(r["DMA0_XMOD"], 16)}', "168 words of 4 bytes = 8 frames x 21"),
        ("DMA0 / DMA1 CFG", f'{r["DMA0_CFG"]} / {r["DMA1_CFG"][-2:]}', "DMA1 writes memory, DMA0 reads it"),
    ]
    rh, y0 = 27, 62
    body = []
    for i, (n, v, note) in enumerate(rows):
        y = y0 + i * rh
        hl = n.startswith("SPORT0_CS0")
        fill = "{panel2}" if hl else ("{panel}" if i % 2 == 0 else "none")
        body.append(f'<rect x="20" y="{y}" width="860" height="{rh}" fill="{fill}"'
                    + (' stroke="{red}" stroke-width="1.4"' if hl else '') + '/>')
        body.append(f'<text x="32" y="{y + 18}" class="m">{n}</text>')
        body.append(f'<text x="230" y="{y + 18}" class="mv"' + (' fill="{red}"' if hl else '') + f'>{v}</text>')
        body.append(f'<text x="400" y="{y + 18}" class="l">{note}</text>')
    H = y0 + len(rows) * rh + 44
    tpl = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {H}" font-family="Segoe UI, Arial, sans-serif">
<style>.t{{{{font-size:17px;font-weight:600;fill:{{fg}}}}}} .l{{{{font-size:13px;fill:{{fg}}}}}}
.m{{{{font-family:Consolas,monospace;font-size:13px;fill:{{muted}}}}}} .mv{{{{font-family:Consolas,monospace;font-size:13px;font-weight:700;fill:{{fg}}}}}}
.s{{{{font-size:11.5px;fill:{{muted}}}}}}</style>
<text x="20" y="30" class="t">DSP4's SPORT0, read from the inside</text>
<text x="20" y="50" class="s">copied into data memory by a one-shot hook in the ISR, then read over SPI. Only DSP4 loaded, 2026-11-16.</text>
{"".join(body)}
<text x="20" y="{H - 16}" class="s">Decode from the ADSP-2156x hardware reference. A nine-DSP reload sets CS0 back to 0x00000001.</text>
</svg>'''
    return save_svg_template("p06-sport0-regs", tpl)


def build():
    out = []
    out += frame_levels()
    out += lone_dsp4()
    out += idxprobe()
    out += sport0_regs()
    return out
