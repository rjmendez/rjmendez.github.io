"""Part 9 diagrams: pipeline, Dante packet byte map, bridge reblocking, DOA windows,
and the 2026-11-20 03:20:47 UTC fleet-feed snapshot.

Numbers come from _figures/data/p09-diagrams.json (doc: Part 9 draft; hub fleet feed
2026-11-20 03:20:47 UTC). The reblock and window figures are worked examples of the
documented rules, not captures.
"""
from __future__ import annotations

import json
from pathlib import Path

from bmafig import PALETTES, THEMES, out_path

DATA = json.loads((Path(__file__).parent / "data" / "p09-diagrams.json").read_text(encoding="utf-8"))
FONT = "Segoe UI, DejaVu Sans, Arial, sans-serif"
MONO = "Consolas, DejaVu Sans Mono, monospace"


def _svg(w, h, body, p):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="{FONT}" font-size="13" fill="{p["fg"]}">\n'
            f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'fill="{p["muted"]}"/></marker></defs>\n{body}\n</svg>\n')


def _write(name, w, h, draw):
    paths = []
    for theme in THEMES:
        p = PALETTES[theme]
        path = out_path(name, theme)
        path.write_text(_svg(w, h, draw(p), p), encoding="utf-8")
        paths.append(path)
    return paths


def _box(x, y, w, h, fill, stroke, label, sub=None, p=None, size=13, bold=True):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" '
         f'stroke="{stroke}" stroke-width="1.4"/>')
    cy = y + h / 2 + (-4 if sub else 5)
    fw = ' font-weight="600"' if bold else ""
    s += f'<text x="{x + w / 2}" y="{cy}" text-anchor="middle" font-size="{size}"{fw}>{label}</text>'
    if sub:
        s += (f'<text x="{x + w / 2}" y="{cy + 17}" text-anchor="middle" font-size="11.5" '
              f'fill="{p["muted"]}">{sub}</text>')
    return s


def _arrow(x1, y1, x2, y2, p, dash=False):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{p["muted"]}" '
            f'stroke-width="1.5" marker-end="url(#ar)"{d}/>')


# ---------------------------------------------------------------- pipeline

def pipeline(p):
    s = []
    s.append(_box(10, 70, 120, 56, p["panel"], p["edge"], "Two tiles", "Brooklyn-3 Dante", p))
    s.append(_arrow(130, 98, 163, 98, p))
    s.append(_box(165, 70, 165, 56, p["panel"], p["blue"], "Bridge per tile", "Windows, 256-sample blocks", p))
    s.append(_arrow(330, 98, 352, 98, p))
    # three branches
    s.append(_box(355, 8, 200, 50, p["panel2"], p["green"], "BirdNET (mono)", "WSL", p))
    s.append(_box(355, 73, 200, 50, p["panel2"], p["green"], "Levels, spectra, classifier", "WSL, multichannel", p))
    s.append(_box(355, 138, 200, 50, p["panel2"], p["purple"], "Direction estimator", "per array, bearings", p))
    for y in (33, 98, 163):
        s.append(f'<path d="M352,98 L352,{y} L353,{y}" fill="none" stroke="{p["muted"]}" stroke-width="1.5"/>')
    s.append(_arrow(555, 163, 588, 163, p))
    s.append(_box(590, 138, 130, 50, p["panel"], p["purple"], "Fleet hub", "fuses; fleet feed", p))
    s.append(_arrow(555, 33, 750, 33, p))
    s.append(f'<path d="M555,98 L740,98" fill="none" stroke="{p["muted"]}" stroke-width="1.5"/>')
    s.append(_arrow(720, 163, 750, 163, p))
    s.append(f'<text x="645" y="26" text-anchor="middle" font-size="11" fill="{p["muted"]}">analysis records</text>')
    s.append(_box(752, 8, 150, 180, p["panel"], p["blue"], "", None, p))
    s.append(f'<text x="827" y="80" text-anchor="middle" font-weight="600">Python web</text>')
    s.append(f'<text x="827" y="98" text-anchor="middle" font-weight="600">service</text>')
    s.append(f'<text x="827" y="122" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">tails logs, hourly</text>')
    s.append(f'<text x="827" y="137" text-anchor="middle" font-size="11.5" fill="{p["muted"]}">rollups, dashboard</text>')
    s.append(_arrow(902, 98, 935, 98, p))
    s.append(_box(937, 70, 90, 56, p["panel2"], p["edge"], "Browser", "views + audio", p))
    # listening engine
    s.append(_box(752, 205, 150, 44, p["panel"], p["teal"], "Listening engine", "delay-and-sum", p, size=12.5))
    s.append(f'<path d="M245,126 L245,227 L750,227" fill="none" stroke="{p["muted"]}" '
             f'stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ar)"/>')
    s.append(f'<text x="480" y="220" text-anchor="middle" font-size="11" fill="{p["muted"]}">selected live audio</text>')
    s.append(f'<path d="M902,227 L982,227 L982,128" fill="none" stroke="{p["muted"]}" '
             f'stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ar)"/>')
    return "\n".join(s)


# ---------------------------------------------------------------- packet byte map

def packet(p):
    d = DATA["packet"]
    s = []
    x0, y0, W = 20, 46, 960
    s.append(f'<text x="{x0}" y="22" font-weight="600" font-size="14">One {d["length"]}-byte media packet, '
             f'8 channels</text>')
    s.append(f'<text x="{x0 + W}" y="22" text-anchor="end" font-size="12" fill="{p["muted"]}">'
             f'not to scale: frames 2..14 collapsed</text>')
    cells = [("0x02", "0", 46, p["red"]), ("seconds", "1..4", 112, p["gold"]),
             ("frame in second", "5..8", 132, p["gold"])]
    for i in range(2):
        a = 9 + 24 * i
        cells.append((f"frame {i}", f"{a}..{a + 23}", 118, p["blue"]))
    cells.append(("frames 2..14", "57..368", 316, p["faint"]))
    cells.append(("frame 15", "369..392", 118, p["blue"]))
    x = x0
    for label, rng, w, col in cells:
        s.append(f'<rect x="{x}" y="{y0}" width="{w}" height="44" fill="{p["panel"]}" stroke="{col}" stroke-width="1.6"/>')
        s.append(f'<text x="{x + w / 2}" y="{y0 + 20}" text-anchor="middle" font-weight="600" font-size="12.5">{label}</text>')
        s.append(f'<text x="{x + w / 2}" y="{y0 + 36}" text-anchor="middle" font-family="{MONO}" '
                 f'font-size="11" fill="{p["muted"]}">{rng}</text>')
        x += w
    s.append(f'<text x="{x0}" y="{y0 + 62}" font-size="11.5" fill="{p["muted"]}">9-byte header, big-endian; '
             f'first sample index = seconds × 48000 + frame (frame &lt; 48000)</text>')
    # zoom of frame 0
    zx, zy = x0 + 290, y0 + 70
    y1 = y0 + 108
    s.append(f'<path d="M{zx},{zy} L{x0},{y1} M{zx + 118},{zy} L{x0 + W},{y1}" stroke="{p["faint"]}" '
             f'stroke-dasharray="3 3" fill="none"/>')
    cw = W / 8
    for c in range(8):
        cx = x0 + c * cw
        b = 9 + 3 * c
        s.append(f'<rect x="{cx}" y="{y1}" width="{cw}" height="52" fill="{p["panel2"]}" '
                 f'stroke="{p["blue"]}" stroke-width="1.2"/>')
        s.append(f'<text x="{cx + cw / 2}" y="{y1 + 21}" text-anchor="middle" font-weight="600">ch {c}</text>')
        s.append(f'<text x="{cx + cw / 2}" y="{y1 + 40}" text-anchor="middle" font-family="{MONO}" '
                 f'font-size="11" fill="{p["muted"]}">bytes {b}..{b + 2}</text>')
    s.append(f'<text x="{x0}" y="{y1 + 74}" font-size="12.5">Each sample: signed 24-bit big-endian. '
             f'Frame f, channel c starts at byte <tspan font-family="{MONO}">9 + 3·(8f + c)</tspan>.</text>')
    s.append(f'<text x="{x0}" y="{y1 + 96}" font-size="12.5">{d["pps"]:,} packets/s × 16 frames = 48 kHz;  '
             f'{d["pcm_bytes_per_s"]:,} PCM bytes/s per tile;  next packet starts 16 samples later.</text>')
    return "\n".join(s)


# ---------------------------------------------------------------- reblock timeline

def reblock(p):
    d = DATA["reblock"]
    lo, hi = 728, 1544
    x0, W = 40, 900

    def X(i):
        return x0 + (i - lo) * W / (hi - lo)

    s = []
    s.append(f'<text x="20" y="22" font-weight="600" font-size="14">Bridge reblocking across a lost packet</text>')
    s.append(f'<text x="20" y="40" font-size="12" fill="{p["muted"]}">    worked example of the documented rule, '
                 f'sample indices on the card clock</text>')
    # packets row
    y = 66
    s.append(f'<text x="20" y="{y - 6}" font-size="12" fill="{p["muted"]}">packets in (16 samples each)</text>')
    for i in range(744, 1528, 16):
        lost = d["gap_start"] <= i < d["gap_before"]
        col = p["red"] if lost else p["edge"]
        fill = "none" if lost else p["panel"]
        dash = ' stroke-dasharray="2 2"' if lost else ""
        s.append(f'<rect x="{X(i) + 0.5}" y="{y}" width="{X(i + 16) - X(i) - 1}" height="16" fill="{fill}" '
                 f'stroke="{col}" stroke-width="1"{dash}/>')
    s.append(f'<text x="{(X(d["gap_start"]) + X(d["gap_before"])) / 2}" y="{y + 34}" text-anchor="middle" '
             f'font-size="12" fill="{p["red"]}">lost packet</text>')
    # blocks row
    y = 120
    s.append(f'<text x="20" y="{y - 6}" font-size="12" fill="{p["muted"]}">blocks out</text>')
    blocks = [(744, 1000, "256 samples", p["blue"], p["panel"]),
              (d["buffered_start"], d["gap_start"], f'{d["short_block"]} samples, flushed short', p["gold"], p["panel2"]),
              (d["gap_before"], d["gap_before"] + 256, "next block, gap_before = 1", p["green"], p["panel"])]
    for a, b, label, col, fill in blocks:
        s.append(f'<rect x="{X(a)}" y="{y}" width="{X(b) - X(a)}" height="38" rx="4" fill="{fill}" '
                 f'stroke="{col}" stroke-width="1.8"/>')
        s.append(f'<text x="{(X(a) + X(b)) / 2}" y="{y + 24}" text-anchor="middle" font-size="12.5" '
                 f'font-weight="600">{label}</text>')
    s.append(f'<rect x="{X(d["gap_start"])}" y="{y}" width="{X(d["gap_before"]) - X(d["gap_start"])}" height="38" '
             f'fill="none" stroke="{p["red"]}" stroke-dasharray="3 3"/>')
    # axis
    ya = 182
    s.append(f'<line x1="{X(lo)}" y1="{ya}" x2="{X(hi)}" y2="{ya}" stroke="{p["edge"]}"/>')
    for t, anc in ((744, "middle"), (d["buffered_start"], "middle"), (d["gap_start"], "end"),
                   (d["gap_before"], "start"), (d["gap_before"] + 256, "middle")):
        s.append(f'<line x1="{X(t)}" y1="{ya - 4}" x2="{X(t)}" y2="{ya + 4}" stroke="{p["edge"]}"/>')
        s.append(f'<text x="{X(t)}" y="{ya + 19}" text-anchor="{anc}" font-family="{MONO}" font-size="11.5" '
                 f'fill="{p["muted"]}">{t}</text>')
    return "\n".join(s)


# ---------------------------------------------------------------- DOA windows

def doa_windows(p):
    d = DATA["doa"]
    win, hop = d["window"], d["hop"]
    x0, W = 40, 880
    lo, hi = 0, 26400

    def X(i):
        return x0 + (i - lo) * W / (hi - lo)

    s = []
    s.append(f'<text x="20" y="22" font-weight="600" font-size="14">Direction estimator windows: '
             f'{win:,} samples ({win // 48} ms), hop {hop:,} ({hop // 48} ms)</text>')
    s.append(f'<text x="20" y="40" font-size="12" fill="{p["muted"]}">illustration of the rule, '
             f'not a capture; positions are arbitrary</text>')
    miss = 8700
    jump = 14400
    y = 58
    starts = list(range(0, jump - win + 1, hop))
    rows = []
    for k, a in enumerate(starts):
        masked = a <= miss < a + win
        rows.append((a, masked, 0, k))
    for k, a in enumerate(range(jump, hi - win + 1, hop)):
        rows.append((a, False, 1, k))
    for idx, (a, masked, epoch, k) in enumerate(rows):
        yy = y + (k % 2) * 24
        col = p["red"] if masked else (p["blue"] if epoch == 0 else p["green"])
        fill = "none" if masked else p["panel"]
        dash = ' stroke-dasharray="4 3"' if masked else ""
        s.append(f'<rect x="{X(a)}" y="{yy}" width="{X(a + win) - X(a)}" height="18" rx="3" fill="{fill}" '
                 f'stroke="{col}" stroke-width="1.6"{dash}/>')
        lbl = "masked" if masked else "estimate"
        s.append(f'<text x="{(X(a) + X(a + win)) / 2}" y="{yy + 13}" text-anchor="middle" font-size="11" '
                 f'fill="{col if masked else p["muted"]}">{lbl}</text>')
    ya = 124
    s.append(f'<line x1="{X(lo)}" y1="{ya}" x2="{X(jump)}" y2="{ya}" stroke="{p["edge"]}" stroke-width="2"/>')
    s.append(f'<line x1="{X(jump)}" y1="{ya}" x2="{X(hi)}" y2="{ya}" stroke="{p["edge"]}" stroke-width="2"/>')
    s.append(f'<line x1="{X(miss)}" y1="{y - 4}" x2="{X(miss)}" y2="{ya + 6}" stroke="{p["red"]}" stroke-width="2"/>')
    s.append(f'<text x="{X(miss)}" y="{ya + 22}" text-anchor="middle" font-size="12" fill="{p["red"]}">'
             f'one missing sample</text>')
    s.append(f'<line x1="{X(jump)}" y1="{y - 4}" x2="{X(jump)}" y2="{ya + 6}" stroke="{p["gold"]}" '
             f'stroke-width="2" stroke-dasharray="6 3"/>')
    s.append(f'<text x="{X(jump) + 6}" y="{ya + 22}" font-size="12" fill="{p["gold"]}">'
             f'index jump: new epoch, local tracks dropped</text>')
    s.append(f'<text x="{X(lo)}" y="{ya + 22}" font-size="12" fill="{p["blue"]}">epoch n</text>')
    s.append(f'<text x="{X(hi)}" y="{ya + 22}" text-anchor="end" font-size="12" fill="{p["green"]}">epoch n+1</text>')
    return "\n".join(s)


# ---------------------------------------------------------------- fleet snapshot card

def fleet_snapshot(p):
    d = DATA["fleet_snapshot"]
    s = []
    s.append(f'<rect x="1" y="1" width="598" height="196" rx="8" fill="{p["panel"]}" stroke="{p["edge"]}"/>')
    s.append(f'<text x="20" y="30" font-weight="600" font-size="14">Fleet feed, {d["utc"]} UTC</text>')
    s.append(f'<text x="20" y="49" font-size="12" fill="{p["muted"]}">both units configured PTP-locked '
             f'to the same reference</text>')
    stats = [("rays", d["rays"], p["blue"]), ("per-array bearing tracks", d["bearing_tracks"], p["blue"]),
             ("fused tracks", d["fused"], p["red"])]
    for i, (lab, val, col) in enumerate(stats):
        cx = 20 + i * 190
        s.append(f'<text x="{cx}" y="98" font-size="34" font-weight="700" fill="{col}">{val}</text>')
        s.append(f'<text x="{cx}" y="118" font-size="12" fill="{p["muted"]}">{lab}</text>')
    s.append(f'<line x1="20" y1="136" x2="580" y2="136" stroke="{p["grid"]}"/>')
    s.append(f'<text x="20" y="160" font-family="{MONO}" font-size="13">not_fused_reason='
             f'<tspan fill="{p["red"]}">{d["reason"]}</tspan>  (both units)</text>')
    s.append(f'<text x="20" y="182" font-family="{MONO}" font-size="13">hub log: clock_rebooted='
             f'{d["clock_rebooted"]}   guard: &gt;{d["guard_s"]} s off timeline</text>')
    return "\n".join(s)


def build():
    out = []
    out += _write("p09-pipeline", 1030, 256, pipeline)
    out += _write("p09-packet", 1000, 270, packet)
    out += _write("p09-reblock", 960, 210, reblock)
    out += _write("p09-doa-windows", 960, 156, doa_windows)
    out += _write("p09-fleet-snapshot", 600, 198, fleet_snapshot)
    return out


if __name__ == "__main__":
    for path in build():
        print(path.name)
