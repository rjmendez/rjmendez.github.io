"""Shared helpers for the BMA360 post figures.

Every figure ships as a light and a dark file in images/bma/:
    <name>-light.svg / <name>-dark.svg   (or .png for screenshots)
Posts embed both, tagged {: .only-light} / {: .only-dark}; _sass/layout/_figures.scss
shows the one matching html[data-theme].

Run everything with:  python _figures/build.py
"""
from __future__ import annotations

import colorsys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images" / "bma"
OUT.mkdir(parents=True, exist_ok=True)

# Site backgrounds: light theme is #fff, dark theme (_sass/theme/_default_dark.scss) is #474747.
PALETTES = {
    "light": {
        "bg": "#ffffff", "fg": "#1a1a1a", "muted": "#555555", "faint": "#999999",
        "grid": "#e3e3e3", "panel": "#f7f9fc", "panel2": "#fdf8ee", "edge": "#9a9a9a",
        "blue": "#2c6cb0", "red": "#c0392b", "green": "#2e7d32", "gold": "#b8860b",
        "purple": "#7b3fa0", "teal": "#2f7f93",
    },
    "dark": {
        "bg": "#474747", "fg": "#f2f2f2", "muted": "#c9c9c9", "faint": "#9a9a9a",
        "grid": "#5c5c5c", "panel": "#3b3f45", "panel2": "#45403a", "edge": "#8a8a8a",
        "blue": "#7cb6ff", "red": "#ff8a7a", "green": "#86d98f", "gold": "#f0c24b",
        "purple": "#c9a0ff", "teal": "#5fd0e8",
    },
}
THEMES = ("light", "dark")


def out_path(name: str, theme: str, ext: str = "svg") -> Path:
    return OUT / f"{name}-{theme}.{ext}"


# ---------------------------------------------------------------- matplotlib

def mpl_theme(theme: str):
    """rc dict for matplotlib matching the site theme."""
    from cycler import cycler

    p = PALETTES[theme]
    return {
        "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
        "savefig.transparent": True,
        "text.color": p["fg"], "axes.labelcolor": p["fg"], "axes.edgecolor": p["edge"],
        "axes.titlecolor": p["fg"],
        "xtick.color": p["muted"], "ytick.color": p["muted"],
        "axes.grid": True, "grid.color": p["grid"], "grid.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "font.family": ["Segoe UI", "DejaVu Sans", "Arial", "sans-serif"],
        "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "semibold",
        "axes.titlelocation": "left", "legend.frameon": False,
        "svg.fonttype": "none", "svg.hashsalt": "bma360",
        "axes.prop_cycle": cycler(
            color=[p["blue"], p["red"], p["green"], p["gold"], p["purple"], p["teal"]]),
    }


def save_mpl(name: str, draw, figsize=(9, 4.2)):
    """draw(fig, palette, theme) -> None. Writes both theme variants as SVG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    written = []
    for theme in THEMES:
        with plt.rc_context(mpl_theme(theme)):
            fig = plt.figure(figsize=figsize)
            draw(fig, PALETTES[theme], theme)
            path = out_path(name, theme)
            fig.savefig(path, bbox_inches="tight", metadata={"Date": None})
            plt.close(fig)
            written.append(path)
    return written


# ---------------------------------------------------------------- SVG templates

def save_svg_template(name: str, template: str):
    """template uses {fg}, {muted}, {blue}, ... tokens from PALETTES (literal braces as {{ }})."""
    written = []
    for theme in THEMES:
        path = out_path(name, theme)
        path.write_text(template.format(**PALETTES[theme]), encoding="utf-8")
        written.append(path)
    return written


# ---------------------------------------------------------------- retheme hand-drawn SVGs

_HEX = re.compile(r"(?<![&\w])#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
_NAMED = re.compile(r'(fill|stroke|stop-color)="(white|black)"')


def _dark_hex(h: str) -> str:
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    if sat < 0.15 or light > 0.85:
        # neutrals and pale fills: invert lightness around the #474747 page
        light2 = 0.96 - 0.74 * light
        sat2 = sat * 0.45
    else:
        # accents: brighten so they read on a dark page
        light2 = min(0.80, 1.0 - 0.6 * light)
        sat2 = min(1.0, sat * 1.05)
    r, g, b = colorsys.hls_to_rgb(hue, light2, sat2)
    return "#%02x%02x%02x" % tuple(round(c * 255) for c in (r, g, b))


def retheme_svg_text(svg: str) -> str:
    svg = _NAMED.sub(
        lambda m: f'{m.group(1)}="{"#ffffff" if m.group(2) == "white" else "#000000"}"', svg)
    return _HEX.sub(lambda m: _dark_hex(m.group(1)), svg)


def light_dark_from_svg(name: str, source: Path):
    """Copy a hand-drawn light SVG to <name>-light.svg and write a rethemed <name>-dark.svg."""
    text = source.read_text(encoding="utf-8")
    out_path(name, "light").write_text(text, encoding="utf-8")
    out_path(name, "dark").write_text(retheme_svg_text(text), encoding="utf-8")
    return [out_path(name, t) for t in THEMES]


def figure_md(name: str, alt: str, ext: str = "svg") -> str:
    """Markdown for a post."""
    return (f"![{alt}](/images/bma/{name}-light.{ext}){{: .only-light}}\n"
            f"![{alt}](/images/bma/{name}-dark.{ext}){{: .only-dark}}")
