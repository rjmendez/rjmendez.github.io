"""Social preview cards (1200x630 PNG) for each BMA360 part: title plus the part's first figure.

python _figures/og_cards.py      # needs `pip install playwright` + `playwright install chromium`

Reads every BMA360 post in _posts/ and _drafts/ and writes images/bma/og/bma360-part-N.png.
Posts reference the card with `header: og_image: bma/og/bma360-part-N.png`.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from bmafig import PALETTES, ROOT

OUT = ROOT / "images" / "bma" / "og"
TITLE = re.compile(r'^title:\s*"BMA360, Part (\d+):\s*(.+)"\s*$', re.M)
FIG = re.compile(r"\(/images/bma/([\w.-]+-light\.(?:svg|png))\)")


def posts():
    for p in sorted((ROOT / "_posts").glob("*bma360-part-*.md")) + sorted((ROOT / "_drafts").glob("bma-*.md")):
        t = p.read_text(encoding="utf-8")
        m = TITLE.search(t)
        f = FIG.search(t)
        if m and f:
            yield int(m.group(1)), m.group(2), ROOT / "images" / "bma" / f.group(1)


def card(n: int, title: str, fig: Path) -> str:
    p = PALETTES["light"]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
body {{ margin:0; width:1200px; height:630px; background:{p['bg']}; font-family:'Segoe UI',Arial,sans-serif;
       display:flex; box-sizing:border-box; border-top:14px solid {p['blue']}; }}
.txt {{ width:470px; padding:56px 30px 48px 60px; display:flex; flex-direction:column; }}
.kick {{ color:{p['blue']}; font-weight:700; letter-spacing:.12em; font-size:24px; }}
h1 {{ color:{p['fg']}; font-size:50px; line-height:1.12; margin:22px 0 0; }}
.foot {{ margin-top:auto; color:{p['muted']}; font-size:22px; }}
.fig {{ flex:1; display:flex; align-items:center; justify-content:center; padding:36px 48px 36px 10px;
        background:{p['panel']}; }}
.fig img {{ max-width:100%; max-height:540px; object-fit:contain; }}
</style></head><body>
<div class="txt"><div class="kick">BMA360 &middot; PART {n}</div><h1>{html.escape(title)}</h1>
<div class="foot">rjmendez.github.io</div></div>
<div class="fig"><img src="{fig.as_uri()}"></div>
</body></html>"""


def main() -> None:
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "_card.html"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1200, "height": 630})
        for n, title, fig in posts():
            tmp.write_text(card(n, title, fig), encoding="utf-8")
            page.goto(tmp.as_uri())
            page.wait_for_load_state("networkidle")
            out = OUT / f"bma360-part-{n}.png"
            page.screenshot(path=str(out))
            print(out.relative_to(ROOT))
        b.close()
    tmp.unlink()


if __name__ == "__main__":
    main()
