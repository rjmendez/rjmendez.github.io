"""Build every BMA360 post figure (light + dark) into images/bma/.

python _figures/build.py            # all
python _figures/build.py fig_p06    # only modules whose name starts with this
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from bmafig import ROOT, light_dark_from_svg  # noqa: E402

# Hand-drawn diagrams kept as the light source of truth; dark is generated.
HAND_DRAWN = {
    "delay-and-sum": "BMA360_delay_and_sum.svg",
    "boot-chain": "BMA360_boot_chain.svg",
    "two-computers": "BMA360_two_computers.svg",
    "tdm-vs-registers": "BMA360_tdm_vs_registers.svg",
    "sharc-load-handshake": "BMA360_sharc_load_handshake.svg",
    "dsp4-receive-ring": "BMA360_dsp4_receive_ring.svg",
    "eight-channel-question": "BMA360_eight_channel_question.svg",
    "bearing-crossing": "BMA360_bearing_crossing.svg",
}


def main(prefix: str = "") -> None:
    if not prefix or prefix == "hand":
        for name, src in HAND_DRAWN.items():
            p = ROOT / "_figures" / "src" / src
            if not p.exists():
                p = ROOT / "images" / src
            for out in light_dark_from_svg(name, p):
                print(out.relative_to(ROOT))
    for mod in sorted(HERE.glob("fig_*.py")):
        if prefix and prefix != "hand" and not mod.stem.startswith(prefix):
            continue
        m = importlib.import_module(mod.stem)
        for out in m.build():
            print(Path(out).relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
