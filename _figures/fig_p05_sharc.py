"""Part 5 figures: loading the SHARCs and running our own instruction on one.

p05-load-soak   full 9-DSP load from empty plus the identify soak (data/p05-sharcload.json)
p05-dsp-sites   what sits in each of the ten DSP sites (same file)
p05-ready-bits  the 0x6400010E ready register, bit per DSP, as read and as the vendor loader logged it
p05-isr-patch   the one-word patch in DSP4's receive ISR, parcel by parcel
"""
from __future__ import annotations

import json
from pathlib import Path

from bmafig import save_mpl, save_svg_template

DATA = Path(__file__).resolve().parent / "data"


def _load():
    return json.loads((DATA / "p05-sharcload.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- load + soak timeline

def load_soak():
    d = _load()
    dsps = [x for x in d["dsps"] if x["words"]]
    total_w = sum(x["words"] for x in dsps)
    span = d["load_end_up"] - d["load_start_up"]
    lone = d["lone_dsp4"]
    lone_s = lone["end_s"] - lone["start_s"]
    rounds = d["soak"]["rounds"]

    def draw(fig, p, theme):
        img_col = {"sharc1g": p["purple"], "sharc3g": p["teal"], "sharc2g": p["blue"]}
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.45], wspace=0.08)
        ax = fig.add_subplot(gs[0])
        t = 0.0
        for x in dsps:
            w = span * x["words"] / total_w
            ax.barh(1, w, left=t, height=0.5, color=img_col[x["image"]], edgecolor=p["bg"], lw=1.2)
            ax.text(t + w / 2, 1, str(x["dsp"]), ha="center", va="center", fontsize=9,
                    color=p["bg"], fontweight="bold")
            t += w
        ax.barh(0, lone_s, left=0, height=0.5, color=p["blue"], edgecolor=p["bg"])
        ax.text(lone_s + 1, 0, f"DSP4 alone: {lone['words']} words in {lone_s} s",
                va="center", fontsize=9.5, color=p["fg"])
        ax.set_yticks([1, 0], ["all nine", "one DSP"])
        ax.set_ylim(-0.6, 1.9)
        ax.set_xlim(0, span * 1.04)
        ax.set_xlabel("seconds from start of load")
        ax.grid(axis="y", visible=False)
        ax.set_title(f"Load from empty: {span:.1f} s", pad=8)
        ax.text(0, 1.45, "per-DSP split estimated from word counts", fontsize=8.5, color=p["muted"])
        for i, (k, lab) in enumerate((("sharc1g", "sharc1g"), ("sharc3g", "sharc3g"), ("sharc2g", "sharc2g"))):
            ax.text(span * (0.52 + 0.17 * i), 1.62, lab, fontsize=8.5, color=img_col[k], ha="left")

        ax2 = fig.add_subplot(gs[1])
        rows = {2: 2, 5: 1, 9: 0}
        for r in rounds:
            for dsp in r["dsps"]:
                ax2.plot(r["t"], rows[dsp], marker="|", ms=13, mew=2,
                         color=p["green"] if r["ok"] else p["red"])
        for x in dsps:
            ax2.plot(0, 3.2, marker="|", ms=13, mew=2, color=p["green"])
        ax2.set_yticks([3.2, 2, 1, 0], ["at load (9)", "DSP2", "DSP5", "DSP9"])
        ax2.yaxis.tick_right()
        ax2.set_ylim(-0.7, 3.9)
        ax2.set_xlim(-12, 500)
        ax2.set_xlabel("seconds after load finished")
        ax2.grid(axis="y", visible=False)
        ax2.spines["left"].set_visible(False)
        ax2.spines["right"].set_visible(True)
        n_ok = len(dsps) + sum(r["ok"] for r in rounds)
        ax2.set_title(f"Identify: {n_ok}/{len(dsps) + len(rounds)} checks ok "
                      f"(9 at load, {len(rounds)} rounds every 15 s)", pad=8)

    return save_mpl("p05-load-soak", draw, figsize=(10.5, 3.0))


# ---------------------------------------------------------------- DSP sites

def dsp_sites():
    d = _load()
    W, H = 900, 250
    bw, gap, x0 = 82, 6, 20
    col = {"sharc1g": "{purple}", "sharc3g": "{teal}", "sharc2g": "{blue}", None: "{faint}"}
    cells = []
    for i, x in enumerate(d["dsps"]):
        bx = x0 + i * (bw + gap)
        c = col[x["image"]]
        if x["image"]:
            cells.append(
                f'<rect x="{bx}" y="56" width="{bw}" height="92" rx="5" fill="{{panel}}" stroke="{c}" stroke-width="2"/>'
                f'<text x="{bx + bw / 2}" y="80" class="b" text-anchor="middle">DSP{x["dsp"]}</text>'
                f'<text x="{bx + bw / 2}" y="100" class="m" text-anchor="middle" fill="{c}">{x["image"]}</text>'
                f'<text x="{bx + bw / 2}" y="118" class="s" text-anchor="middle">v{x["version"]}</text>'
                f'<text x="{bx + bw / 2}" y="136" class="s" text-anchor="middle">{x["words"]} w</text>')
        else:
            cells.append(
                f'<rect x="{bx}" y="56" width="{bw}" height="92" rx="5" fill="none" stroke="{{faint}}" '
                f'stroke-width="1.4" stroke-dasharray="4,3"/>'
                f'<text x="{bx + bw / 2}" y="80" class="b" text-anchor="middle" fill="{{faint}}">DSP1</text>'
                f'<text x="{bx + bw / 2}" y="104" class="s" text-anchor="middle">site</text>'
                f'<text x="{bx + bw / 2}" y="120" class="s" text-anchor="middle">empty</text>')
    xs = lambda i: x0 + i * (bw + gap)
    braces = (
        f'<path d="M{xs(0)} 158 v8 h{bw} v-8" fill="none" stroke="{{purple}}" stroke-width="1.3"/>'
        f'<text x="{xs(0)}" y="184" class="s">control plane,</text>'
        f'<text x="{xs(0)}" y="200" class="s">SPI master to the FPGA</text>'
        f'<path d="M{xs(4)} 158 v8 h{xs(9) + bw - xs(4)} v-8" fill="none" stroke="{{blue}}" stroke-width="1.3"/>'
        f'<text x="{(xs(4) + xs(9) + bw) / 2}" y="184" class="s" text-anchor="middle">'
        f'DSP4 to DSP9 carry the 36 data channels</text>'
        f'<text x="{(xs(4) + xs(9) + bw) / 2}" y="200" class="s" text-anchor="middle">'
        f'DSP4 is the one I hook in Parts 5 and 6</text>')
    tpl = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">
<style>.t{{{{font-size:17px;font-weight:600;fill:{{fg}}}}}} .b{{{{font-size:14px;font-weight:600;fill:{{fg}}}}}}
.m{{{{font-family:Consolas,monospace;font-size:12.5px}}}} .s{{{{font-size:11.5px;fill:{{muted}}}}}}</style>
<text x="20" y="30" class="t">Ten DSP sites, nine SHARCs, three images</text>
<text x="20" y="48" class="s">word counts are what sharcload clocks into each DSP</text>
{"".join(cells)}
{braces}
<text x="20" y="236" class="s">versions read back over SPI after load. DSP0's identify reply is all zeros, so its version read is the liveness check.</text>
</svg>'''
    return save_svg_template("p05-dsp-sites", tpl)


# ---------------------------------------------------------------- ready bits

def ready_bits():
    d = _load()["ready_10e"]
    rows = [("idle, DSP1 site empty", d["idle"], "measured"),
            ("vendor loader gave up on DSP6", d["vendor_timeout_log"]["DSP6"], "vendor log"),
            ("vendor loader gave up on DSP7", d["vendor_timeout_log"]["DSP7"], "vendor log"),
            ("vendor loader gave up on DSP8", d["vendor_timeout_log"]["DSP8"], "vendor log"),
            ("vendor loader gave up on DSP9", d["vendor_timeout_log"]["DSP9"], "vendor log"),
            ("after vendor ResetDspSpiInterface", d["after_vendor_reset"]["10E"][1], "measured")]
    W, cw, ch, gx, gy = 900, 40, 26, 330, 70
    parts = []
    for b in range(10):
        x = gx + (9 - b) * cw
        parts.append(f'<text x="{x + cw / 2}" y="{gy - 8}" class="s" text-anchor="middle">DSP{b}</text>')
    for r, (lab, hexv, src) in enumerate(rows):
        y = gy + r * (ch + 6)
        v = int(hexv, 16)
        parts.append(f'<text x="20" y="{y + 18}" class="l">{lab}</text>')
        parts.append(f'<text x="{gx - 14}" y="{y + 18}" class="m" text-anchor="end">0x{v:04X}</text>')
        for b in range(10):
            x = gx + (9 - b) * cw
            on = (v >> b) & 1
            parts.append(f'<rect x="{x + 2}" y="{y}" width="{cw - 4}" height="{ch}" rx="3" '
                         f'fill="{"{red}" if on else "{panel}"}" stroke="{"{red}" if on else "{edge}"}" '
                         f'stroke-width="1" fill-opacity="{0.85 if on else 1}"/>')
            parts.append(f'<text x="{x + cw / 2}" y="{y + 18}" class="m" text-anchor="middle" '
                         f'fill="{"{bg}" if on else "{faint}"}">{on}</text>')
        parts.append(f'<text x="{gx + 10 * cw + 14}" y="{y + 18}" class="s">{src}</text>')
    H = gy + len(rows) * (ch + 6) + 50
    tpl = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">
<style>.t{{{{font-size:17px;font-weight:600;fill:{{fg}}}}}} .l{{{{font-size:13px;fill:{{fg}}}}}}
.m{{{{font-family:Consolas,monospace;font-size:13px;fill:{{fg}}}}}} .s{{{{font-size:11.5px;fill:{{muted}}}}}}</style>
<text x="20" y="30" class="t">0x6400010E: one bit per DSP, 1 = not ready</text>
{"".join(parts)}
<text x="20" y="{H - 22}" class="s">Bits are live pad levels, active-low. sharcload polls the target DSP's bit before every 4-byte word and sends when it reads 0.</text>
</svg>'''
    return save_svg_template("p05-ready-bits", tpl)


# ---------------------------------------------------------------- ISR patch

def isr_patch():
    tpl = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" font-family="Segoe UI, Arial, sans-serif">
<defs><marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{muted}"/></marker>
<marker id="g" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{green}"/></marker></defs>
<style>.t{{font-size:17px;font-weight:600;fill:{fg}}} .h{{font-size:12px;font-weight:600;fill:{muted};letter-spacing:.5px}}
.m{{font-family:Consolas,monospace;font-size:14px;fill:{fg}}} .mb{{font-family:Consolas,monospace;font-size:14px;font-weight:700}}
.s{{font-size:11.5px;fill:{muted}}} .l{{font-size:13px;fill:{fg}}}</style>
<text x="20" y="30" class="t">One 32-bit write turns a load into a jump</text>
<text x="20" y="50" class="s">DSP4 receive ISR, sw 0x1c5544. The instruction is three 16-bit parcels; the patch rewrites the first two.</text>

<text x="20" y="84" class="h">STOCK</text>
<rect x="110" y="66" width="90" height="28" rx="3" fill="{panel}" stroke="{edge}"/><text x="155" y="85" class="m" text-anchor="middle">1002</text>
<rect x="204" y="66" width="90" height="28" rx="3" fill="{panel}" stroke="{edge}"/><text x="249" y="85" class="m" text-anchor="middle">0025</text>
<rect x="298" y="66" width="90" height="28" rx="3" fill="{panel}" stroke="{edge}"/><text x="343" y="85" class="m" text-anchor="middle">6db8</text>
<text x="410" y="85" class="m">R2 = DM(0x256db8)</text>

<text x="20" y="130" class="h">PATCHED</text>
<rect x="110" y="112" width="90" height="28" rx="3" fill="{panel2}" stroke="{red}" stroke-width="1.6"/><text x="155" y="131" class="mb" text-anchor="middle" fill="{red}">063e</text>
<rect x="204" y="112" width="90" height="28" rx="3" fill="{panel2}" stroke="{red}" stroke-width="1.6"/><text x="249" y="131" class="mb" text-anchor="middle" fill="{red}">0018</text>
<rect x="298" y="112" width="90" height="28" rx="3" fill="{panel}" stroke="{edge}"/><text x="343" y="131" class="m" text-anchor="middle">6db8</text>
<text x="410" y="131" class="m">JUMP sw 0x186db8</text>
<path d="M110 146 v6 h184 v-6" fill="none" stroke="{red}" stroke-width="1.2"/>
<text x="110" y="170" class="s">one 32-bit word at 0x2838aa88: 00251002 becomes 0018063e</text>
<path d="M298 146 v6 h90 v-6" fill="none" stroke="{muted}" stroke-width="1.2"/><line x1="343" y1="152" x2="343" y2="176" stroke="{muted}" stroke-width="1"/>
<text x="298" y="188" class="s">third parcel kept: the target's low 16 bits</text>

<rect x="582" y="64" width="300" height="168" rx="6" fill="{panel}" stroke="{green}" stroke-width="1.4"/>
<text x="596" y="86" class="h">MY ROUTINE, sw 0x186db8 (free RAM)</text>
<text x="596" y="112" class="m">R2 = DM(0x256db8)</text><text x="770" y="112" class="s">displaced load</text>
<text x="596" y="138" class="m">... counter / copy ...</text>
<text x="596" y="158" class="s">uses only R0, R2, I4</text>
<text x="596" y="184" class="m">JUMP sw 0x1c5547</text><text x="770" y="184" class="s">next stock instr</text>
<text x="596" y="216" class="s">the ISR carries on as if nothing happened</text>
<path d="M552 126 C566 126 566 108 580 108" fill="none" stroke="{green}" stroke-width="2" marker-end="url(#g)"/>

<text x="20" y="222" class="h">ISR RATE ON DSP4, MEASURED</text>
<text x="20" y="246" class="l">stock ISR rate: 5999.6 /s</text>
<text x="20" y="268" class="l">first counter hook, 2026-11-01: ~6000 /s over a 75 s soak</text>
<text x="20" y="290" class="l">lone DSP4, 2026-11-16, patched and unpatched: 6145 to 6231 per ~1 s read</text>
<text x="20" y="314" class="s">Unpatch writes 00251002 back; the readback matched every time. The rate staying put is how I know the routine returns.</text>
</svg>'''
    return save_svg_template("p05-isr-patch", tpl)


def build():
    out = []
    out += load_soak()
    out += dsp_sites()
    out += ready_bits()
    out += isr_patch()
    return out
