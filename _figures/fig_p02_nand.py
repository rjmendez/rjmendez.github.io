"""Part 2 figures: measured NAND block map (board A) and the OMAP DDR layout from the U-Boot env.

Data: _figures/data/p02-nand-blocks.json, extracted from board A's golden NAND backup
(MTD char-device reads from the vendor Linux) plus the partition table printed by the stock
2.6.37 kernel. RAM layout values come from the stock U-Boot env (mem=, loadaddr) and the
UBL/U-Boot console lines (entry 0xC1080000) and kernel header (load 0xC0008000).
"""
from __future__ import annotations

import json
from pathlib import Path

from bmafig import save_mpl, save_svg_template

DATA = Path(__file__).resolve().parent / "data" / "p02-nand-blocks.json"
COLS = 64


def _draw_nand(fig, p, theme):
    from matplotlib.patches import Rectangle

    doc = json.loads(DATA.read_text(encoding="utf-8"))
    parts = doc["partitions"]
    knorm = -(-doc["kernel_normal_bytes"] // doc["erase_block"])
    ksafe = -(-doc["kernel_safe_bytes"] // doc["erase_block"])
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    colors = {".": p["grid"], "k": p["blue"], "u": p["red"], "t": p["purple"], "j": p["green"],
              "#": p["faint"]}
    row = 0
    lx = -1.2
    for part in parts:
        m = part["map"]
        size = int(part["end"], 16) - int(part["start"], 16)
        size_s = f"{size // 1024} KiB" if size < 1 << 20 else f"{size / (1 << 20):g} MiB"
        ax.text(lx, row + 0.35, f"mtd{part['mtd']}  {part['name']}", ha="right", va="center",
                fontsize=10.5, color=p["fg"], fontweight="semibold")
        ax.text(lx, row + 1.75, f"{part['start']}  {size_s}", ha="right", va="center",
                fontsize=8.5, color=p["muted"], family="monospace")
        if m is None:
            ax.text(0, row + 0.55, "not dumped (unused by boot)", va="center", fontsize=10,
                    color=p["muted"], style="italic")
            row += 2.6
            continue
        lines = max(1, -(-len(m) // COLS))
        for i, ch in enumerate(m):
            c = colors[ch]
            if ch == "#" and part["name"].startswith("kernel"):
                lim = knorm if part["name"] == "kernel-normal" else ksafe
                c = p["blue"] if i < lim else p["faint"]
            if ch == "#" and part["name"] == "u-boot env2":
                c = p["red"]
                c_alpha = 0.55
            else:
                c_alpha = 1.0
            x, y = i % COLS, row + i // COLS
            ax.add_patch(Rectangle((x + 0.08, y + 0.08), 0.84, 0.84, facecolor=c, alpha=c_alpha,
                                   edgecolor="none"))
        note = {
            "u-boot": "erased: U-Boot is not here",
            "u-boot env2": "3 copies of U-Boot at blocks 6, 9, 12 (what the UBL boots)",
            "kernel-normal": f"stock uImage = first {knorm} blocks; rest not erased",
            "kernel-safe": f"safe uImage = {ksafe} blocks",
            "Rsvd1": "erased",
            "FileSystem": "JFFS2 nodes in 100 of 256 blocks",
            "u-boot env": "environment",
            "UBL": "TI AIS image ('TIPA')",
        }.get(part["name"], "")
        nx = (len(m) if lines == 1 else COLS) + 0.8
        ax.text(nx, row + 0.55, note, va="center", fontsize=9.5, color=p["muted"])
        row += max(lines, 2) + 1.3
    # legend
    ly = row + 0.6
    items = [(p["red"], "U-Boot image"), (p["purple"], "UBL"), (p["blue"], "kernel image"),
             (p["green"], "JFFS2"), (p["faint"], "other data"), (p["grid"], "erased (0xFF)")]
    x = 0
    for c, lab in items:
        ax.add_patch(Rectangle((x, ly), 0.84, 0.84, facecolor=c, edgecolor="none"))
        ax.text(x + 1.3, ly + 0.45, lab, va="center", fontsize=9.5, color=p["fg"])
        x += 3.2 + len(lab) * 0.55
    ax.text(0, -1.0, "OMAP NAND, board A: one square per 128 KiB erase block (64 per row)",
            fontsize=12, fontweight="semibold", color=p["fg"], va="center")
    ax.set_xlim(-17, 92)
    ax.set_ylim(ly + 1.6, -2.0)
    ax.set_aspect("equal")


RAM = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 400" font-family="Segoe UI, Helvetica, Arial, sans-serif">
  <style>
    .t{{fill:{fg};font-size:13px;font-weight:600}}
    .s{{fill:{muted};font-size:12px}}
    .m{{fill:{muted};font-size:11.5px;font-family:Consolas, Menlo, monospace}}
    .lin{{fill:{panel};stroke:{blue};stroke-width:1.4}}
    .hole{{fill:{panel2};stroke:{gold};stroke-width:1.4;stroke-dasharray:5 3}}
    .tick{{stroke:{fg};stroke-width:1.4}}
  </style>
  <text class="t" x="30" y="28">OMAP DDR from 0xC0000000, as the stock bootargs split it (to scale)</text>
  <!-- bar from x=60 to x=840 => 780 px for 256 MiB, 3.047 px/MiB -->
  <rect class="lin" x="60" y="120" width="97.5" height="60"/>
  <rect class="hole" x="157.5" y="120" width="109.7" height="60"/>
  <rect class="lin" x="267.2" y="120" width="572.8" height="60"/>
  <text class="t" x="66" y="146">mem=32M</text>
  <text class="s" x="66" y="164">Linux</text>
  <text class="t" x="163" y="146">36 MiB</text>
  <text class="s" x="163" y="164">not given to Linux</text>
  <text class="t" x="275" y="146">mem=188M@0xc4400000</text>
  <text class="s" x="275" y="164">Linux</text>

  <g class="m" text-anchor="middle">
    <text x="60" y="206">0xC0000000</text>
    <text x="172" y="222">0xC2000000</text>
    <text x="267" y="206">0xC4400000</text>
    <text x="830" y="206">0xD0000000</text>
  </g>

  <!-- markers inside the first 32 MiB -->
  <path class="tick" fill="none" d="M60.6 120 L60.6 68 L140 68"/>
  <path class="tick" fill="none" d="M81.3 120 L81.3 86 L140 86"/>
  <path class="tick" fill="none" d="M110.2 120 L110.2 104 L140 104"/>
  <text class="m" x="146" y="72">kernel runs at 0xC0008000</text>
  <text class="m" x="146" y="90">uImage loadaddr 0xC0700000</text>
  <text class="m" x="146" y="108">U-Boot runs at 0xC1080000</text>

  <rect x="30" y="250" width="840" height="120" rx="5" fill="{panel}" stroke="{grid}"/>
  <text class="s" x="44" y="274">Before DDR is up, the UBL runs from on-chip shared RAM (AIS load to 0x80000000), copies U-Boot from NAND to 0xC1080000 and jumps.</text>
  <text class="s" x="44" y="296">U-Boot reads the kernel image to 0xC0700000; bootm unpacks it to 0xC0008000. The initramfs is linked into that image.</text>
  <text class="s" x="44" y="318">The kernel only sees the two mem= ranges; the 36 MiB between them is outside its view.</text>
  <text class="m" x="44" y="346">mem=32M@0xc0000000 mem=188M@0xc4400000 rdinit=/sbin/init noinitrd emmc=</text>
</svg>
"""


def build():
    out = save_mpl("p02-nand-map", _draw_nand, figsize=(13, 4.95))
    out += save_svg_template("p02-ram-map", RAM)
    return out
