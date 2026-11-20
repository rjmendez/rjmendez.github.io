"""Part 3 figures: the Brooklyn-3 card.

p03-card-photo   annotated photo of the card in its Mini-PCI socket (serial label blacked out)
p03-flash-map    the card's QSPI partition table drawn to scale (data/p03-card-mtd.csv, from /proc/mtd)
p03-minipci-pins power/ground map of the 124-pin Mini-PCI Type III edge (module datasheet)
"""
from __future__ import annotations

import csv
from pathlib import Path

from bmafig import PALETTES, ROOT, THEMES, out_path, save_mpl

DATA = Path(__file__).resolve().parent / "data"
MiB = 1 << 20


# ---------------------------------------------------------------- annotated photo

def _font(size, bold=False):
    from PIL import ImageFont
    for name in (("segoeuib.ttf", "DejaVuSans-Bold.ttf") if bold else ("segoeui.ttf", "DejaVuSans.ttf")):
        for d in (Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu")):
            if (d / name).exists():
                return ImageFont.truetype(str(d / name), size)
    return ImageFont.load_default(size=size)


def annotate_photo(src: Path, name: str, boxes, redact, panel_w=760, scale=0.7):
    """boxes: [(x0, y0, x1, y1, color_key, title, sub)]; redact: [(x0, y0, x1, y1)] in source pixels."""
    from PIL import Image, ImageDraw

    written = []
    for theme in THEMES:
        p = PALETTES[theme]
        img = Image.open(src).convert("RGB")
        d = ImageDraw.Draw(img)
        for r in redact:
            d.rectangle(r, fill="#111111")
            d.text(((r[0] + r[2]) / 2, (r[1] + r[3]) / 2), "redacted", fill="#bbbbbb",
                   font=_font(26), anchor="mm")
        for i, (x0, y0, x1, y1, ck, _, _) in enumerate(boxes, 1):
            col = PALETTES["dark"][ck]
            d.rectangle((x0, y0, x1, y1), outline=col, width=7)
            cx, cy = x0 + 34, y0 + 34
            d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=col)
            d.text((cx, cy), str(i), fill="#111111", font=_font(36, True), anchor="mm")
        w, h = img.size
        canvas = Image.new("RGB", (w + int(panel_w / scale), h), p["bg"])
        canvas.paste(img, (0, 0))
        d = ImageDraw.Draw(canvas)
        x, y = w + 50, 60
        for i, (_, _, _, _, ck, title, sub) in enumerate(boxes, 1):
            col = p[ck]
            d.ellipse((x, y + 4, x + 64, y + 68), fill=col)
            d.text((x + 32, y + 36), str(i), fill=p["bg"], font=_font(40, True), anchor="mm")
            d.text((x + 90, y), title, fill=p["fg"], font=_font(54, True))
            yy = y + 72
            for line in sub:
                d.text((x + 90, yy), line, fill=p["muted"], font=_font(44))
                yy += 58
            y = yy + 46
        canvas = canvas.resize((int(canvas.width * scale), int(canvas.height * scale)), Image.LANCZOS)
        path = out_path(name, theme, "jpg")
        canvas.save(path, quality=86, optimize=True)
        written.append(path)
    return written


def card_photo():
    return annotate_photo(
        ROOT / "images" / "BMA360_Dante_card.jpg", "p03-card-photo",
        boxes=[
            (838, 432, 1288, 878, "red", "U1: Zynq-7000 XC7Z015",
             ["under the thermal pad", "ARM PS runs Linux", "PL packetizes the audio"]),
            (325, 1005, 1795, 1205, "blue", "J12: Mini-PCI Type III",
             ["124 pins, on the main board", "TDM audio, RGMII, 2x RS-232,", "power and ground"]),
            (565, 158, 805, 238, "gold", "Brooklyn 3, PCB rev 2", ["Audinate module"]),
        ],
        redact=[(1140, 128, 1368, 348)],
    )


# ---------------------------------------------------------------- flash map

KIND = {
    "skd": "boot", "fsbl": "boot",
    "safefpga": "safe", "safeboot": "safe", "safebootenv": "safe",
    "fpga": "live", "boot": "live", "bootenv": "live", "kernel": "live", "rootfs": "live",
    "userarea": "data", "brdinfo": "data", "license": "data", "safelicense": "data",
    "capability": "data", "config": "data",
}
OVERLAYS = ("flashall", "image", "safeall")


def read_mtd():
    rows = [r for r in csv.DictReader(
        (ln for ln in open(DATA / "p03-card-mtd.csv", encoding="ascii") if not ln.startswith("#")))]
    parts, off = [], 0
    sizes = {r["name"]: int(r["size_hex"], 16) for r in rows}
    for r in rows:
        if r["name"] in OVERLAYS:
            continue
        s = int(r["size_hex"], 16)
        parts.append((r["name"], off, s))
        off += s
    return parts, sizes


def flash_map():
    parts, sizes = read_mtd()
    total = sizes["flashall"]
    used = parts[-1][1] + parts[-1][2]
    start = {n: o for n, o, _ in parts}
    assert sizes["image"] == sizes["kernel"] + sizes["rootfs"]
    assert sizes["safeall"] == start["safebootenv"]

    def draw(fig, p, theme):
        colors = {"boot": p["purple"], "safe": p["gold"], "live": p["green"], "data": p["teal"]}
        ax = fig.add_axes([0.02, 0.42, 0.96, 0.28])
        ax.set_xlim(0, total / MiB)
        ax.set_ylim(0, 1)
        ax.axis("off")
        for n, o, s in parts:
            ax.add_patch(_rect(o / MiB, 0, s / MiB, 1, colors[KIND[n]], p["bg"]))
        ax.add_patch(_rect(used / MiB, 0, (total - used) / MiB, 1, p["grid"], p["bg"], hatch="//"))
        inside = {"safefpga": "safefpga", "fpga": "fpga", "kernel": "kernel", "rootfs": "rootfs",
                  "userarea": "userarea", "safeboot": "safe\nboot", "boot": "boot"}
        for n, o, s in parts:
            if n in inside:
                ax.text((o + s / 2) / MiB, 0.5, inside[n] + f"\n{s / MiB:.3g} MiB" if s >= 4 * MiB else inside[n],
                        ha="center", va="center", fontsize=9.5 if s >= 4 * MiB else 8,
                        color="#111111" if theme == "dark" else "#ffffff", fontweight="semibold")
        ax.text((used + (total - used) / 2) / MiB, 0.5, f"unpartitioned\n{(total - used) / MiB:.1f} MiB",
                ha="center", va="center", fontsize=9.5, color=p["muted"])
        # small partitions: leader lines below the bar
        small = [("skd", "skd 256K"), ("fsbl", "fsbl 256K"), ("safebootenv", "safebootenv 64K"),
                 ("bootenv", "bootenv 64K")]
        tail = ["brdinfo", "license", "safelicense", "capability", "config"]
        for i, (n, label) in enumerate(small):
            o, s = start[n], sizes[n]
            x = (o + s / 2) / MiB
            tx, ty = [(2.5, -0.5), (2.5, -0.9), (9.0, -0.5), (13.5, -0.9)][i]
            ax.annotate(label, xy=(x, 0), xytext=(tx, ty), ha="left", va="center", fontsize=8.5,
                        color=p["fg"], arrowprops=dict(arrowstyle="-", color=p["muted"], lw=0.8))
        t0 = start[tail[0]]
        t1 = start[tail[-1]] + sizes[tail[-1]]
        ax.annotate("brdinfo, license, safelicense,\ncapability (64K each), config 128K",
                    xy=((t0 + t1) / 2 / MiB, 0), xytext=(54.0, -0.8), ha="center", fontsize=8.5,
                    color=p["fg"], arrowprops=dict(arrowstyle="-", color=p["muted"], lw=0.8))
        # overlays as brackets above
        def bracket(a, b, y, label, col):
            ax.plot([a / MiB, a / MiB, b / MiB, b / MiB], [y - 0.08, y, y, y - 0.08],
                    color=col, lw=1.4, clip_on=False)
            ax.text((a + b) / 2 / MiB, y + 0.06, label, ha="center", va="bottom", fontsize=9,
                    color=col, clip_on=False)
        bracket(0, sizes["safeall"], 1.18, "safeall 5.5 MiB", p["gold"])
        bracket(start["kernel"], start["kernel"] + sizes["image"], 1.18, "image = kernel + rootfs (38.1 MiB)",
                p["green"])
        bracket(0, total, 1.62, "flashall: 64 MiB QSPI", p["muted"])
        for mb in range(0, 65, 8):
            ax.text(mb, -0.12, f"{mb}", ha="center", va="top", fontsize=8, color=p["faint"])
        ax.text(total / MiB, -0.3, "MiB", ha="right", va="top", fontsize=8, color=p["faint"])
        # legend
        lx = 0.02
        for k, lab in (("boot", "first-stage boot"), ("safe", "safe (fallback) set"),
                       ("live", "live set"), ("data", "board data")):
            fig.patches.append(_rect(lx, 0.02, 0.018, 0.05, colors[k], p["bg"], transform=fig.transFigure))
            fig.text(lx + 0.024, 0.045, lab, fontsize=9.5, va="center", color=p["fg"])
            lx += 0.2

    return save_mpl("p03-flash-map", draw, figsize=(10, 4.2))


def _rect(x, y, w, h, fc, ec, **kw):
    from matplotlib.patches import Rectangle
    return Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=0.8, **kw)


# ---------------------------------------------------------------- Mini-PCI pins

PWR = {
    "3.3V": [19, 24, 28, 63, 70, 88, 89],
    "5V (VCC5VA)": [123],
    "3.3VAUX": [124],
    "GND": [23, 27, 55, 62, 69, 74, 77, 82, 83, 85, 119, 120],
}


def minipci_pins():
    def draw(fig, p, theme):
        col = {"3.3V": p["red"], "5V (VCC5VA)": p["gold"], "3.3VAUX": p["purple"], "GND": p["fg"]}
        role = {pin: k for k, pins in PWR.items() for pin in pins}
        ax = fig.add_axes([0.02, 0.22, 0.96, 0.66])
        ax.set_xlim(-1.5, 63.5)
        ax.set_ylim(-1.2, 2.2)
        ax.axis("off")
        for c in range(62):
            for row, pin in ((1, 2 * c + 1), (0, 2 * c + 2)):
                r = role.get(pin)
                fc = col[r] if r else p["grid"]
                ax.add_patch(_rect(c + 0.12, row + 0.1, 0.76, 0.8, fc, p["bg"]))
                if r:
                    ax.text(c + 0.5, row + 1.05 if row else -0.08, str(pin), ha="center",
                            va="bottom" if row else "top", fontsize=7.5, color=col[r], rotation=90)
        ax.plot([1, 1], [-0.1, 2.1], color=p["muted"], lw=1.6, ls=(0, (2, 2)))
        ax.text(1, 2.12, "key", ha="center", va="bottom", fontsize=8.5, color=p["muted"])
        ax.text(-0.4, 1.5, "odd", ha="right", va="center", fontsize=9, color=p["muted"])
        ax.text(-0.4, 0.5, "even", ha="right", va="center", fontsize=9, color=p["muted"])
        ax.text(0.5, -0.9, "pins 1, 2", ha="left", va="center", fontsize=8.5, color=p["faint"])
        ax.text(62, -0.9, "pins 123, 124", ha="right", va="center", fontsize=8.5, color=p["faint"])
        lx = 0.06
        for k in PWR:
            fig.patches.append(_rect(lx, 0.04, 0.016, 0.07, col[k], p["bg"], transform=fig.transFigure))
            fig.text(lx + 0.022, 0.075, f"{k}  ({len(PWR[k])})", fontsize=9.5, va="center", color=p["fg"])
            lx += 0.19
        fig.patches.append(_rect(lx, 0.04, 0.016, 0.07, p["grid"], p["bg"], transform=fig.transFigure))
        fig.text(lx + 0.022, 0.075, "signal / NDA", fontsize=9.5, va="center", color=p["fg"])

    return save_mpl("p03-minipci-pins", draw, figsize=(10, 2.6))


def build():
    out = []
    out += card_photo()
    out += flash_map()
    out += minipci_pins()
    return out
