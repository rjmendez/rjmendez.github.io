"""Render every images/bma/*-light/-dark pair onto its page background for eyeballing.

python _figures/preview.py  ->  writes <session or tmp>/bma_contact_sheet.png
"""
from __future__ import annotations

import sys
from pathlib import Path

from bmafig import OUT, PALETTES

dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "bma_contact_sheet.png"
names = sorted({p.name.rsplit("-", 1)[0] for p in OUT.glob("*-light.*")})
rows = []
for n in names:
    light = next(OUT.glob(f"{n}-light.*"))
    dark = next(OUT.glob(f"{n}-dark.*"))
    rows.append(
        f'<h3>{n}</h3><div class="row">'
        f'<div style="background:{PALETTES["light"]["bg"]}"><img src="{light.as_uri()}"></div>'
        f'<div style="background:{PALETTES["dark"]["bg"]}"><img src="{dark.as_uri()}"></div></div>')
html = ("<html><body style='font-family:sans-serif;margin:12px'>"
        "<style>.row{display:flex;gap:8px}.row div{flex:1;padding:8px}img{width:100%}</style>"
        + "".join(rows) + "</body></html>")
page = dest.with_suffix(".html")
page.write_text(html, encoding="utf-8")

from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1800, "height": 1000})
    pg.goto(page.as_uri())
    pg.wait_for_timeout(500)
    pg.screenshot(path=str(dest), full_page=True)
    b.close()
print(dest)
