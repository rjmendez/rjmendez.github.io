"""Diagrams that replace prose across the series. Every fact here is already stated in the posts."""
from __future__ import annotations

from fig_p10_figures import _arrow, _box, _dbox, _lines, _write


def _title(t):
    return f'<text x="20" y="22" font-weight="600" font-size="14">{t}</text>'


def _note(p, y, lines, h=None):
    h = h or 22 + 17 * len(lines)
    return (f'<rect x="20" y="{y}" width="1050" height="{h}" rx="6" fill="{p["panel"]}" stroke="{p["faint"]}" '
            f'stroke-width="1.5"/>' + _lines(36, y + 21, lines, p, size=11.5, step=17, anchor="start", fill=p["fg"]))


# ------------------------------------------------------------ Part 1: where a wrong bearing can come from

def suspects(p):
    s = [_title("Where a wrong bearing can come from, and which part of the series looks there")]
    stages = [("Microphones", "121 elements"), ("The fold", "121 into 36"), ("SHARC channel order", "DSP rings"),
              ("FPGA route", "register window"), ("Dante mapping", "8 channels out"), ("My code on the PC", "hub and bearing")]
    looks = [("Part 4", "24 elements are silent"), ("Part 4", "inside the Cyclone, no way in"), ("Parts 5, 6", "load DSPs, read a ring"),
             ("Part 4", "sixteen register banks"), ("Part 7", "what is on the 8 channels"), ("Parts 8, 9", "bearings, hub, dashboard")]
    w, gap = 160, 18
    for i, ((t, sub), (part, what)) in enumerate(zip(stages, looks)):
        x = 20 + i * (w + gap)
        s.append(_box(x, 56, w, 62, p["panel"], p["blue"], t, sub, p, size=12.5))
        if i:
            s.append(_arrow(x - gap, 87, x, 87, p))
        s.append(f'<line x1="{x + w / 2}" y1="118" x2="{x + w / 2}" y2="160" stroke="{p["faint"]}" stroke-width="1.3" stroke-dasharray="3 4"/>')
        s.append(f'<rect x="{x}" y="160" width="{w}" height="62" rx="6" fill="{p["panel2"]}" stroke="{p["faint"]}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        s.append(f'<text x="{x + w / 2}" y="182" text-anchor="middle" font-size="12.5" font-weight="600">{part}</text>')
        s.append(_lines(x + w / 2, 200, [what], p, size=11, step=0))
    s.append(_note(p, 246, ["A wrong bearing could be any of these. The series is about getting a probe between two of them",
                            "on hardware built as a sealed appliance."]))
    return "\n".join(s)


# ------------------------------------------------------------ Part 2: three ways to boot a kernel

def boot_paths(p):
    s = [_title("Three ways to run a kernel on the tile, from least to most permanent")]
    cols = [
        ("1. NFS root from the bench", p["green"], False,
         ["interrupt U-Boot, point the kernel", "at an NFS root, boot", "", "flash is not written", "a power cycle restores stock"]),
        ("2. Primary NAND slot, 0x200000", p["blue"], False,
         ["save the stock kernel first, through", "the MTD char node so ECC applies", "erase and write the primary slot", "update imagesize if the size changed",
          "test over TFTP before writing"]),
        ("3. The safe slot, 0x4220000", p["faint"], True,
         ["never touched", "bootcmd tries normal, then safe", "", "but a kernel that hangs after", "a good bootm does not fall through"]),
    ]
    for i, (t, st, dash, lines) in enumerate(cols):
        x = 20 + i * 356
        s.append(_dbox(x, 44, 338, 160, st, t, p, dash=dash, fill=p["panel"]))
        s.append(_lines(x + 169, 84, lines, p, size=11.5, step=18))
    s.append(_note(p, 224, ["Check the minor number before you trust a dump. MTD char nodes use minor 2N for partition N.",
                            "A /dev/mtd4 made with minor 4 opens mtd2, the blank U-Boot partition, and dd copies 512 KiB of 0xFF without an error."]))
    return "\n".join(s)


# ------------------------------------------------------------ Part 4: why the bitstream route is closed

def bitstream(p):
    s = [_title("Why rewriting the Cyclone is out of scope for now")]
    lanes = [("Power on", p["blue"], ["Cyclone V reads its own SPI flash", "(Active Serial)", "Linux is not involved"]),
             ("Update", p["faint"], ["fpgaupdate writes the SPI flash", "then reads it back", "3-wire bit-bang shifter, no TMS:", "not a JTAG port"]),
             ("Verify, read-only", p["green"], ["read register 0x64000022", "shows which bitstream is running,", "not what is in flash"])]
    for i, (t, st, lines) in enumerate(lanes):
        x = 20 + i * 356
        s.append(_dbox(x, 44, 338, 130, st, t, p, dash=(st == p["faint"]), fill=p["panel"]))
        s.append(_lines(x + 169, 82, lines, p, size=11.5, step=17))
    s.append(_dbox(20, 200, 510, 130, p["red"], "Blocker 1: the update path is unsafe", p, fill=p["panel2"]))
    s.append(_lines(275, 240, ["on a long-uptime board the driver asked the kernel", "for an order-10 allocation: 4 MiB of contiguous memory", "it failed, and the process stayed in D state",
                               "until a power cycle", "reproducible"], p, size=11.5, step=17))
    s.append(_dbox(560, 200, 510, 130, p["red"], "Blocker 2: the bitstream is opaque", p, fill=p["panel2"]))
    s.append(_lines(815, 240, ["vendor ASCII container, CRC-16/ARC checks out", "payload is not a Xilinx or stock Quartus image", "no sync word",
                               "about 6.6 bits per byte, so not encrypted", "cannot round-trip the format yet"], p, size=11.5, step=17))
    s.append(_note(p, 350, ["The fabric stays as it is. My own egress has to go through the Zynq side."]))
    return "\n".join(s)


# ------------------------------------------------------------ Part 8: what is left, in order

def whats_left(p):
    s = [_title("What stands between here and a bearing from live array audio")]
    steps = [("1", "Fixed levels hook on a board", "multi-frame delay ring still to check"),
             ("2", "R9 TX against W13 RX", "settle lead-in and clock; check alignment, CRC, payload on the wire"),
             ("3", "Real samples through the PL ring reader and egress", "audio checker, then listen mode"),
             ("4", "A controlled capture of the eight Dante channels", "Part 7"),
             ("5", "A bearing on a known source", "then two arrays with measured poses and verified geometry"),
             ("6", "The 24 silent elements, mics 97 to 120", "a fabric rewrite; blocked by Part 4")]
    for i, (n, t, sub) in enumerate(steps):
        y = 44 + i * 62
        st = p["red"] if n == "6" else p["faint"]
        s.append(f'<circle cx="46" cy="{y + 26}" r="16" fill="{p["panel2"]}" stroke="{st}" stroke-width="1.5"/>'
                 f'<text x="46" y="{y + 31}" text-anchor="middle" font-size="13" font-weight="600">{n}</text>')
        s.append(_box(80, y, 700, 52, p["panel2"], st, t, sub, p, size=13, dash=True))
        if i < 5:
            s.append(f'<line x1="46" y1="{y + 42}" x2="46" y2="{y + 72}" stroke="{p["faint"]}" stroke-width="1.5" stroke-dasharray="3 4"/>')
    s.append(_dbox(810, 44, 260, 362, p["green"], "Runs today", p, dash=False, fill=p["panel"]))
    s.append(_lines(940, 84, ["stock Dante audio", "through the hub and", "web dashboard", "", "Part 9"], p, size=12, step=18))
    s.append(_note(p, 420, ["Every box on the left is undone. No bird has been tracked and no bearing has come from live array audio."]))
    return "\n".join(s)


# ------------------------------------------------------------ Part 9: how listening picks its audio

def listening(p):
    s = [_title("How the listening engine decides what to play")]
    s.append(f'<rect x="20" y="62" width="190" height="72" rx="6" fill="{p["panel"]}" stroke="{p["blue"]}" stroke-width="1.5"/>'
             f'<text x="115" y="84" text-anchor="middle" font-size="13" font-weight="600">Target</text>')
    s.append(_lines(115, 102, ["one array's bearing, or the", "fused target when there is one"], p, size=11, step=15))
    s.append(_box(20, 150, 190, 46, p["panel2"], p["faint"], "Auto-follow", None, p, size=12.5, dash=True))
    s.append(_lines(115, 214, ["picks its target from the", "hub's fused-target state"], p, size=10.5, step=12))
    s.append(_arrow(210, 98, 270, 98, p))
    s.append(_box(272, 70, 220, 56, p["panel"], p["blue"], "Delay-and-sum beam", "20 ms chunks, fractional delays", p, size=13))
    s.append(_arrow(492, 98, 552, 98, p))
    s.append(_box(554, 70, 220, 56, p["panel"], p["blue"], "Align arrays", "by cross-correlation", p, size=13))
    s.append(_arrow(774, 98, 834, 98, p))
    s.append(_box(836, 56, 234, 40, p["panel"], p["green"], "Locked: play both arrays", None, p, size=12.5))
    s.append(_box(836, 104, 234, 40, p["panel2"], p["red"], "No lock: play one array", None, p, size=12.5, dash=True))
    s.append(_note(p, 250, ["Host-side, on the PC. It steers a delay-and-sum beam on the stock Dante audio; nothing here runs on the arrays."]))
    return "\n".join(s)


# ------------------------------------------------------------ Part 10: why ants, then what comes next

def why_ants(p):
    s = [_title("Where the ants come from, and the five jobs they have on the array")]
    s.append(_dbox(20, 44, 330, 250, p["faint"], "A separate project, unreleased", p))
    s.append(_lines(185, 86, ["each ant: a small model", "watching one raw data stream", "", "shown as an ant farm", "", "no ant is clever", "the behaviour comes from many",
                              "reacting together", "", "jobs there: anomaly detection,", "fast reflex"], p, size=11.5, step=16))
    s.append(_arrow(350, 170, 410, 170, p))
    s.append(_lines(380, 140, ["borrowed", "idea"], p, size=10.5, step=12))
    s.append(_dbox(412, 44, 658, 250, p["blue"], "On the array (design; only the first small piece exists, in simulation)", p, fill=p["panel"]))
    jobs = [("Anomaly detection", "baseline per feature; alarm when a window leaves it", "gate piece in RTL, simulation"),
            ("Fast reflex", "respond to a fast impulse without waiting; target not set", "design only"),
            ("Target acquisition", "notice something new in a beam, keep the evidence", "design only"),
            ("Tracking", "follow it across beams and windows; expire it explicitly", "design only"),
            ("Data enrichment", "attach what the ants saw, so the hub gets a labelled event", "design only")]
    for i, (t, d, st) in enumerate(jobs):
        y = 76 + i * 42
        ok = i == 0
        s.append(f'<rect x="428" y="{y}" width="626" height="36" rx="5" fill="{p["panel"]}" stroke="{p["blue"] if ok else p["faint"]}" '
                 f'stroke-width="1.5"{"" if ok else " stroke-dasharray=\"5 4\""}/>')
        s.append(f'<text x="440" y="{y + 15}" font-size="12.5" font-weight="600">{t}</text>')
        s.append(f'<text x="440" y="{y + 30}" font-size="11" fill="{p["muted"]}">{d}</text>')
        s.append(f'<text x="1044" y="{y + 22}" text-anchor="end" font-size="11" fill="{p["muted"]}">{st}</text>')
    s.append(_note(p, 316, ["Why: raw audio from 121 microphones cannot all go to the hub, so each array decides locally what is worth sending, and quickly.",
                            "The big models (Perch, BirdNET) stay on the hub, where the GPU is. No ant output has come from a live array."]))
    return "\n".join(s)


def next_gates(p):
    s = [_title("The path to a FlyBrain bench load: five gates, none passed yet")]
    gates = [("1", "Freeze the contract", "Cyclone to Zynq link and exact bit mapping, reviewed against source"),
             ("2", "Replay offline", "recorded events with resets, gaps, reordering, model changes"),
             ("3", "Real recordings", "clean splits, calibrated scores, per-class numbers, linear and nearest-neighbour baselines"),
             ("4", "Synthesis and review", "timing and an independent RTL review"),
             ("5", "Bench load, one array", "its own review and sign-off")]
    for i, (n, t, d) in enumerate(gates):
        x = 20 + i * 212
        s.append(_dbox(x, 50, 198, 130, p["faint"], f"{n}. {t}", p, fill=p["panel2"]))
        words = d.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 > 26:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        s.append(_lines(x + 99, 92, lines, p, size=11.5, step=16))
        if i < 4:
            s.append(_arrow(x + 198, 135, x + 212, 135, p, dash=True))
    s.append(_note(p, 204, ["Our Cyclone images already go through that last gate. The latest, a link probe with no FlyBrain logic in it,",
                            "got a NO-GO on 2026-11-20. A later probe load on one array passed its register checks and the array went",
                            "back to stock. No FlyBrain logic has been loaded on any array."]))
    return "\n".join(s)


def build():
    out = []
    out += _write("p01-suspects", 1090, 316, suspects)
    out += _write("p02-boot-paths", 1090, 290, boot_paths)
    out += _write("p04-bitstream", 1090, 406, bitstream)
    out += _write("p08-whats-left", 1090, 470, whats_left)
    out += _write("p09-listening", 1090, 300, listening)
    out += _write("p10-why-ants", 1090, 400, why_ants)
    out += _write("p10-next-gates", 1090, 290, next_gates)
    return out


if __name__ == "__main__":
    for path in build():
        print(path.name)
