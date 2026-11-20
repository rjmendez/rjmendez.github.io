"""Part 1 figures: annotated Brooklyn-3 photo, board/bus block diagram, front-end stage chain.

Sources: part markings read off the photos and docs/BOARD_IDENTIFICATION.md of the RE notes
(Zynq-7000 XC7Z015 U1, "BROOKLYN 3 PCB REV 2", J12 socket, "PD high voltage area" silkscreen);
bus facts (SPI 750 kHz, EMIF CS4 0x64000000) and stage list from the Part 1 draft.
The photo's serial/assembly stickers are blurred before publishing.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from bmafig import PALETTES, ROOT, THEMES, out_path, save_svg_template

PHOTO = ROOT / "images" / "BMA360_mainboard_with_Brooklyn3.jpg"
CROP = (0, 150, 2256, 2900)  # in EXIF-transposed pixels
BLUR = [(1420, 1720, 1700, 2010), (1925, 2480, 2125, 2905)]  # serial sticker, assembly label
SCALE = 0.55


def _font(size: int, bold: bool = False):
    from matplotlib import font_manager as fm

    for fam in ("Segoe UI", "DejaVu Sans"):
        try:
            path = fm.findfont(fm.FontProperties(family=fam, weight="bold" if bold else "normal"),
                               fallback_to_default=False)
            return ImageFont.truetype(path, size)
        except Exception:  # noqa: BLE001 - try the next family
            continue
    return ImageFont.load_default()


# (label, sublabel, target point in transposed px, label anchor in transposed px)
CALLOUTS = [
    ("Zynq-7000 XC7Z015 (U1)", "Brooklyn-3's processor + FPGA", (1000, 1560), (330, 2540)),
    ("Brooklyn-3 Dante card", "Audinate, \"BROOKLYN 3 PCB REV 2\"", (1560, 1080), (1000, 760)),
    ("J12 card-edge socket", "main board side", (190, 1900), (40, 820)),
    ("magnet wire on test points", "", (520, 1150), (40, 1240)),
    ("\"High voltage area\" silkscreen", "PoE input section, main board", (2070, 330), (1080, 260)),
]


def _annotated(theme: str) -> Image.Image:
    p = PALETTES[theme]
    im = ImageOps.exif_transpose(Image.open(PHOTO)).convert("RGB")
    for box in BLUR:
        region = im.crop(box).filter(ImageFilter.GaussianBlur(28))
        im.paste(region, box)
    im = im.crop(CROP)
    w, h = im.size
    im = im.resize((int(w * SCALE), int(h * SCALE)), Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA")
    f1, f2 = _font(26, bold=True), _font(20)

    def pt(xy):
        return ((xy[0] - CROP[0]) * SCALE, (xy[1] - CROP[1]) * SCALE)

    box_fill = (255, 255, 255, 235) if theme == "light" else (59, 63, 69, 235)
    line = p["gold"] if theme == "dark" else "#ffd54a"
    for title, sub, target, anchor in CALLOUTS:
        tx, ty = pt(target)
        ax, ay = pt(anchor)
        tw = max(d.textlength(title, font=f1), d.textlength(sub, font=f2) if sub else 0)
        bh = 64 if sub else 40
        bx0, by0, bx1, by1 = ax, ay, ax + tw + 24, ay + bh
        cx = min(max(tx, bx0), bx1)
        cy = by1 if ty > by1 else (by0 if ty < by0 else ty)
        d.line([(cx, cy), (tx, ty)], fill="#000000", width=7)
        d.line([(cx, cy), (tx, ty)], fill=line, width=4)
        d.ellipse([tx - 9, ty - 9, tx + 9, ty + 9], outline="#000000", width=6)
        d.ellipse([tx - 9, ty - 9, tx + 9, ty + 9], outline=line, width=3)
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=6, fill=box_fill, outline=p["edge"], width=2)
        d.text((bx0 + 12, by0 + 6), title, font=f1, fill=p["fg"])
        if sub:
            d.text((bx0 + 12, by0 + 36), sub, font=f2, fill=p["muted"])
    return im


def build_photo():
    out = []
    for theme in THEMES:
        path = out_path("p01-brooklyn3-callouts", theme, "jpg")
        _annotated(theme).save(path, quality=85, optimize=True, progressive=True)
        out.append(path)
    return out


BLOCKS = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" font-family="Segoe UI, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="ar" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="{red}"/></marker>
    <marker id="ac" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="{blue}"/></marker>
  </defs>
  <style>
    .t{{fill:{fg};font-size:14px;font-weight:600}}
    .s{{fill:{muted};font-size:12px}}
    .m{{fill:{muted};font-size:11.5px;font-family:Consolas, Menlo, monospace}}
    .board{{fill:none;stroke:{edge};stroke-width:1.4;stroke-dasharray:6 4}}
    .chip{{fill:{panel};stroke:{edge};stroke-width:1.2}}
    .audio{{stroke:{red};stroke-width:3.2;fill:none}}
    .ctl{{stroke:{blue};stroke-width:1.6;fill:none;stroke-dasharray:5 4}}
  </style>

  <rect class="board" x="20" y="20" width="860" height="330" rx="8"/>
  <text class="s" x="34" y="40">MAIN BOARD (ClearOne)</text>
  <rect class="board" x="20" y="390" width="860" height="110" rx="8"/>
  <text class="s" x="866" y="410" text-anchor="end">BROOKLYN-3 DANTE CARD (Audinate), on a card-edge socket</text>

  <!-- mics -->
  <rect class="chip" x="40" y="60" width="160" height="70" rx="5"/>
  <text class="t" x="52" y="84">121 MEMS mics</text>
  <text class="s" x="52" y="102">disc, radial 12-spoke</text>
  <text class="s" x="52" y="118">TDM, 24-bit, 48 kHz</text>

  <!-- Cyclone -->
  <rect class="chip" x="270" y="60" width="230" height="88" rx="5"/>
  <text class="t" x="282" y="84">Cyclone V FPGA</text>
  <text class="m" x="282" y="102">5CEBA9F23C8N</text>
  <text class="s" x="282" y="120">mic front end, 121&#8594;36 fold,</text>
  <text class="s" x="282" y="136">routing matrix</text>

  <!-- SHARC -->
  <rect class="chip" x="600" y="60" width="260" height="88" rx="5"/>
  <text class="t" x="612" y="84">9&#215; SHARC+ DSP</text>
  <text class="m" x="612" y="102">ADSP-2156x</text>
  <text class="s" x="612" y="120">beamforming, echo cancel</text>

  <!-- OMAP -->
  <rect class="chip" x="270" y="220" width="300" height="110" rx="5"/>
  <text class="t" x="282" y="244">OMAP-L138E module</text>
  <text class="s" x="282" y="262">ARM926 + C674x, 372 MHz, Linux 2.6.37</text>
  <text class="s" x="282" y="280">NAND 512 MB, eMMC 8 GB</text>
  <text class="s" x="282" y="298">UART J8 "Linux 115200"</text>
  <text class="s" x="282" y="316" fill="{blue}">control plane: no audio passes here</text>

  <!-- switch -->
  <rect class="chip" x="620" y="232" width="240" height="70" rx="5"/>
  <text class="t" x="632" y="256">Marvell 88E6352</text>
  <text class="s" x="632" y="274">6-port GbE switch</text>
  <text class="s" x="632" y="292">(PoE powered device input nearby)</text>

  <!-- Zynq -->
  <rect class="chip" x="270" y="425" width="300" height="62" rx="5"/>
  <text class="t" x="282" y="449">Zynq-7000 XC7Z015</text>
  <text class="s" x="282" y="467">own QSPI flash, own Linux, 8&#215; SDI TDM in</text>

  <rect class="chip" x="640" y="425" width="200" height="62" rx="5"/>
  <text class="t" x="652" y="449">Dante network</text>
  <text class="s" x="652" y="467">finished audio only</text>

  <!-- audio path -->
  <line class="audio" x1="200" y1="95" x2="266" y2="95" marker-end="url(#ar)"/>
  <line class="audio" x1="500" y1="92" x2="596" y2="92" marker-end="url(#ar)"/>
  <line class="audio" x1="600" y1="122" x2="504" y2="122" marker-end="url(#ar)"/>
  <text class="s" x="522" y="86">TDM</text>
  <path class="audio" d="M290 148 L290 190 L110 190 L110 456 L266 456" marker-end="url(#ar)"/>
  <text class="s" x="122" y="300">TDM, 8 lanes</text>
  <text class="s" x="122" y="316">over the card edge</text>
  <line class="audio" x1="570" y1="456" x2="636" y2="456" marker-end="url(#ar)"/>

  <!-- control -->
  <path class="ctl" d="M520 220 L520 170 L700 170 L700 152" marker-end="url(#ac)"/>
  <text class="m" x="530" y="188" fill="{blue}">SPI 750 kHz: load DSP code</text>
  <line class="ctl" x1="420" y1="220" x2="420" y2="152" marker-end="url(#ac)"/>
  <text class="m" x="412" y="200" text-anchor="end" fill="{blue}">EMIF CS4 0x64000000</text>
  <line class="ctl" x1="570" y1="267" x2="616" y2="267" marker-end="url(#ac)"/>

  <!-- legend -->
  <line class="audio" x1="620" y1="330" x2="660" y2="330"/><text class="s" x="668" y="334">audio</text>
  <line class="ctl" x1="730" y1="330" x2="770" y2="330"/><text class="s" x="778" y="334">control</text>
</svg>
"""


STAGES = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 245" font-family="Segoe UI, Helvetica, Arial, sans-serif">
  <defs>
    <marker id="a" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="{fg}"/></marker>
  </defs>
  <style>
    .k{{fill:{muted};font-size:12px;font-weight:600}}
    .n{{fill:{fg};font-size:24px;font-weight:600}}
    .u{{fill:{muted};font-size:11.5px}}
    .d{{fill:{fg};font-size:12.5px}}
    .box{{fill:{panel};stroke:{edge};stroke-width:1.2}}
    .bf{{fill:{panel2};stroke:{gold};stroke-width:1.6}}
    .f{{stroke:{fg};stroke-width:1.4}}
  </style>
  <g>
    <rect class="box" x="10" y="40" width="112" height="120" rx="5"/>
    <text class="k" x="22" y="60">A</text><text class="n" x="22" y="94">121</text>
    <text class="u" x="22" y="114">MEMS mics</text><text class="u" x="22" y="130">24-bit, 48 kHz</text>

    <rect class="box" x="138" y="40" width="112" height="120" rx="5"/>
    <text class="k" x="150" y="60">B</text><text class="n" x="150" y="94">36</text>
    <text class="u" x="150" y="114">time-multiplexed</text><text class="u" x="150" y="130">pre-combine</text>

    <rect class="bf" x="266" y="40" width="112" height="120" rx="5"/>
    <text class="k" x="278" y="60">C</text><text class="n" x="278" y="94">13</text>
    <text class="u" x="278" y="114">FIR bands,</text><text class="u" x="278" y="130">1024 taps each</text>

    <rect class="bf" x="394" y="40" width="112" height="120" rx="5"/>
    <text class="k" x="406" y="60">D</text><text class="n" x="406" y="94">12</text>
    <text class="u" x="406" y="114">beams: weights +</text><text class="u" x="406" y="130">8-tap frac. delay</text>

    <rect class="box" x="522" y="40" width="112" height="120" rx="5"/>
    <text class="k" x="534" y="60">E</text><text class="n" x="534" y="94">matrix</text>
    <text class="u" x="534" y="114">routing / gain</text><text class="u" x="534" y="130">crosspoints</text>

    <rect class="box" x="650" y="40" width="112" height="120" rx="5"/>
    <text class="k" x="662" y="60">F</text><text class="n" x="662" y="94">24&#8594;16</text>
    <text class="u" x="662" y="114">bit reduction</text>

    <rect class="box" x="778" y="40" width="112" height="120" rx="5"/>
    <text class="k" x="790" y="60">G</text><text class="n" x="790" y="94">36&#8594;8</text>
    <text class="u" x="790" y="114">TDM slots to lanes</text><text class="u" x="790" y="130">&#8594; Brooklyn-3</text>
  </g>
  <g>
    <line class="f" x1="122" y1="100" x2="136" y2="100" marker-end="url(#a)"/>
    <line class="f" x1="250" y1="100" x2="264" y2="100" marker-end="url(#a)"/>
    <line class="f" x1="378" y1="100" x2="392" y2="100" marker-end="url(#a)"/>
    <line class="f" x1="506" y1="100" x2="520" y2="100" marker-end="url(#a)"/>
    <line class="f" x1="634" y1="100" x2="648" y2="100" marker-end="url(#a)"/>
    <line class="f" x1="762" y1="100" x2="776" y2="100" marker-end="url(#a)"/>
  </g>
  <line x1="130" y1="32" x2="130" y2="196" stroke="{red}" stroke-width="2.4" stroke-dasharray="6 4"/>
  <text class="d" x="10" y="214" fill="{red}">per-mic audio ends here,</text>
  <text class="d" x="10" y="232" fill="{red}">inside the Cyclone</text>
  <path d="M266 176 L266 186 L506 186 L506 176" fill="none" stroke="{gold}" stroke-width="1.6"/>
  <text class="d" x="300" y="206">the beamformer</text>
  <text class="u" x="140" y="22">front end, recovered from the Cyclone image and the kernel driver</text>
</svg>
"""


def build():
    out = build_photo()
    out += save_svg_template("p01-board-blocks", BLOCKS)
    out += save_svg_template("p01-frontend-stages", STAGES)
    return out
