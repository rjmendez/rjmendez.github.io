"""Part 9: screenshots of the live hub dashboard, light and dark.

build() only returns the PNGs already in images/bma/ (the normal site build never needs the hub).
Capturing needs the running dashboard on this host and is opt-in:

    set BMA_SCREENSHOT=1
    set BMA_DASHBOARD_TOKEN_FILE=<the dashboard's --auth-token-file>
    python _figures/fig_p09_screens.py

The dashboard login token is read from that file at run time, sent only to the loopback
dashboard as a Basic credential header, and never printed or written anywhere. Before each
screenshot the page text is scrubbed (MACs, IPs, host names, device ids) and checked again; the
Map panel, Survey setup, Hub identity and the account panel are never captured.
"""
from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bmafig import THEMES, out_path  # noqa: E402

URL = "https://127.0.0.1:48500/"
SHOTS = ("p09-live", "p09-det", "p09-targets", "p09-fleet", "p09-sys")

SCRUB_JS = r"""() => {
  const pats = [
    [/\b[0-9a-f]{2}(:[0-9a-f]{2}){5}\b/gi, 'xx:xx:xx:xx:xx:xx'],
    [/\b\d{1,3}(\.\d{1,3}){3}(:\d+)?\b/g, 'x.x.x.x'],
    [/\b[a-z][a-z0-9]*-[0-9a-f]{8}\b/gi, 'device-xxxx'],
    [/\b[\w-]+(\.[\w-]+)*\.(net|com|org|ts\.net|local|lan)\b/gi, 'host.masked'],
    [/[A-Za-z]:\\[^\s]*/g, '<path>'],
    [/-?\d{1,3}\.\d{4,}/g, 'x.xxxx'],
  ];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n; while ((n = w.nextNode())) {
    let t = n.nodeValue, o = t;
    for (const [re, r] of pats) t = t.replace(re, r);
    if (t !== o) n.nodeValue = t;
  }
  for (const id of ['account-btn']) { const e = document.getElementById(id); if (e) e.style.visibility = 'hidden'; }
}"""

LEAK_JS = r"""() => {
  const t = document.body.innerText;
  const res = [/\b[0-9a-f]{2}(:[0-9a-f]{2}){5}\b/i, /\b\d{1,3}(\.\d{1,3}){3}\b/, /\b[a-z][a-z0-9]*-[0-9a-f]{8}\b/i,
               /\.(net|com|org)\b/i, /[A-Za-z]:\\/];
  return res.filter(r => r.test(t)).map(r => String(r));
}"""


def build():
    out = []
    for name in SHOTS:
        for theme in THEMES:
            p = out_path(name, theme, "png")
            if p.exists():
                out.append(p)
    return out


def _auth_header() -> str:
    tok = Path(os.environ["BMA_DASHBOARD_TOKEN_FILE"]).read_text(encoding="utf-8").strip()
    try:
        return "Basic " + base64.b64encode(("viewer:" + tok).encode()).decode()
    finally:
        del tok


def _scrub(pg):
    pg.evaluate(SCRUB_JS)
    leaks = pg.evaluate(LEAK_JS)
    if leaks:
        raise RuntimeError("unmasked text matched %s; not saving" % leaks)


def _open_panel(pg, pid):
    pg.click('button[data-view="live"]')
    pg.wait_for_timeout(800)
    for d in ("lp-map", "lp-3d", "lp-targets", "lp-fleet"):
        pg.evaluate("id => { document.getElementById(id).open = false }", d)
    pg.evaluate("id => { document.getElementById(id).open = true }", pid)
    pg.wait_for_timeout(5000)
    el = pg.locator("#" + pid)
    el.scroll_into_view_if_needed()
    pg.wait_for_timeout(500)
    return el


def _shot(pg, path, box, bottom=None, pad=14):
    pg.evaluate("() => { document.getElementById('top').style.visibility = 'hidden' }")
    sy = pg.evaluate("window.scrollY")
    box = dict(box, y=box["y"] + sy)
    bottom = None if bottom is None else bottom + sy
    vw = pg.viewport_size["width"]
    x0 = max(0, box["x"] - pad)
    y0 = max(0, box["y"] - pad)
    y1 = (bottom if bottom is not None else box["y"] + box["height"]) + pad
    x1 = min(vw, box["x"] + box["width"] + pad)
    pg.screenshot(path=str(path), full_page=True, clip={"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0})


def capture():
    from playwright.sync_api import sync_playwright

    hdr = _auth_header()
    written = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for theme in THEMES:
            ctx = b.new_context(ignore_https_errors=True, color_scheme=theme,
                                viewport={"width": 1440, "height": 1060},
                                extra_http_headers={"Authorization": hdr})
            pg = ctx.new_page()
            pg.goto(URL + "#live", wait_until="networkidle", timeout=30000)
            pg.wait_for_timeout(14000)
            if pg.evaluate("document.documentElement.dataset.theme || ''") not in ("", theme):
                pg.click("#theme")
                pg.wait_for_timeout(800)

            _scrub(pg)
            pg.screenshot(path=str(out_path("p09-live", theme, "png")))

            pg.click('button[data-view="det"]')
            pg.wait_for_timeout(5000)
            _scrub(pg)
            pg.screenshot(path=str(out_path("p09-det", theme, "png")))

            for name, pid in (("p09-targets", "lp-targets"), ("p09-fleet", "lp-fleet")):
                el = _open_panel(pg, pid)
                _scrub(pg)
                box = el.bounding_box()
                bottom = None
                if pid == "lp-fleet":
                    rel = el.get_by_text("Relative frame", exact=True)
                    if rel.count():
                        bottom = rel.first.bounding_box()["y"] - 10
                _shot(pg, out_path(name, theme, "png"), box, bottom)

            pg.click('button[data-view="sys"]')
            pg.wait_for_timeout(5000)
            _scrub(pg)
            top = pg.locator("#v-sys").bounding_box()
            setup = pg.locator("section.sys-setup").bounding_box()
            _shot(pg, out_path("p09-sys", theme, "png"), top, setup["y"] - 20)
            ctx.close()
        b.close()
    for name in SHOTS:
        for theme in THEMES:
            written.append(out_path(name, theme, "png"))
    return written


if __name__ == "__main__":
    if os.environ.get("BMA_SCREENSHOT") != "1":
        sys.exit("set BMA_SCREENSHOT=1 to capture from the live dashboard")
    for p in capture():
        print(p.name)
