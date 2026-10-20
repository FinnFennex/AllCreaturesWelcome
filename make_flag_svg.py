"""Generate clean vector replicas / variants of the 'All Creatures Welcome' flag.

Geometry was measured from the perspective-corrected photo (flag_straightened.jpg)
and idealised to a regular grid. Text is Archivo Regular, converted to outlines.

usage: python3 make_flag_svg.py <Archivo-Regular.ttf> <out_dir>
needs: fonttools, uharfbuzz
"""
import math
import os
import re
import sys

import uharfbuzz as hb
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

FONT, OUT_DIR = sys.argv[1], sys.argv[2]

W = 3575            # artwork width
STRIPE = 290        # stripe height = cap height
GAP = 24            # dark separator between stripes
H = 6 * STRIPE + 5 * GAP
BORDER = GAP       # dark frame around the stripes

COLORS = {
    "dark":   "#231a15",
    "red":    "#e2563f",
    "orange": "#f39a3d",
    "yellow": "#f5c730",
    "green":  "#1d5c52",
    "blue":   "#3d3a7a",
    "pink":   "#9e4566",
}
# six-stripe rainbow flag (Gilbert Baker, 1979), as used on Wikipedia
PRIDE_COLORS = {
    **COLORS,
    "red":    "#e40303",
    "orange": "#ff8c00",
    "yellow": "#ffed00",
    "green":  "#008026",
    "blue":   "#24408e",
    "pink":   "#732982",
}
PALETTES = {"-pride": PRIDE_COLORS}
ROW_COLORS = ["red", "orange", "yellow", "green", "blue", "pink"]

# placement measured on the original flag: ink left, ink right, block start
MEASURED = {
    "ALL":       (9, 760, 790),
    "CREATURES": (2, 2571, 2588),
    "WELCOME":   (14, 2182, 2196),
}
DEFAULT_LEFT = 12
DEFAULT_TRACKING = 5.1  # font units, as fitted for CREATURES
DEFAULT_BLOCK_GAP = 17
# text drawn in dark over a full stripe instead of before a block, with its rotation in degrees
# ("@file.svg" = hand-drawn shape traced by trace_colon3.py, thickened to the font's stem width)
TILTED = {"@colon3-fat.svg": -10}
TILT_PAD = 8            # keep the tilted text this far inside the stripe
TILT_OPACITY = 0.86     # 14% transparent
PATH_NTOS = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
MATRIX_NTOS = lambda v: f"{v:.5f}".rstrip("0").rstrip(".")

# variant name -> text per row (rows without text are full stripes)
VARIANTS = {
    "all-creatures-welcome":   {0: "ALL", 1: "CREATURES", 2: "WELCOME"},
    "creatures":               {1: "CREATURES"},
    "creatures-3":             {1: "CREATURES :3"},
    "creatures-3-yellow":      {1: "CREATURES", 2: "@colon3-fat.svg"},
    "all-creatures-3":         {0: "ALL", 1: "CREATURES", 2: "@colon3-fat.svg"},
}

tt = TTFont(FONT)
glyphs = tt.getGlyphSet()
hb_font = hb.Font(hb.Face(hb.Blob.from_file_path(FONT)))
scale = STRIPE / tt["OS/2"].sCapHeight


def shape(text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf, {"kern": True})
    return [(tt.getGlyphName(i.codepoint), p.x_advance) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def bounds(name):
    bp = BoundsPen(glyphs)
    glyphs[name].draw(bp)
    return bp.bounds


STEM = (lambda b: (b[2] - b[0]) * scale)(bounds("I"))  # vertical stem width in flag units


def ink_extent(run, tracking):
    x, first_l, last_r = 0, None, None
    for name, adv in run:
        b = bounds(name)
        if b:
            first_l = x + b[0] if first_l is None else first_l
            last_r = x + b[2]
        x += adv + tracking
    return first_l, last_r


def layout(text):
    """Return ([(glyph, x)], block start x) for a text row: glyph origins in flag units, baseline 0."""
    run = shape(text)
    if text in MEASURED:
        left, right, block_x = MEASURED[text]
        first_l, last_r = ink_extent(run, 0)
        tracking = ((right - left) / scale - (last_r - first_l)) / (len(run) - 1)
    else:
        left, tracking = DEFAULT_LEFT, DEFAULT_TRACKING
        if text.startswith("CREATURES"):
            left = MEASURED["CREATURES"][0]
        first_l, last_r = ink_extent(run, tracking)
        block_x = round(left + (last_r - first_l) * scale + DEFAULT_BLOCK_GAP)

    placed, x = [], -first_l
    for name, adv in run:
        placed.append((name, left + x * scale))
        x += adv + tracking
    return placed, block_x


def draw(placed, pen, matrix=Transform()):
    for name, x in placed:
        glyphs[name].draw(TransformPen(pen, matrix.transform((scale, 0, 0, -scale, x, 0))))


def text_row(text):
    """Return (path data, block start x) for a text row placed at baseline 0."""
    placed, block_x = layout(text)
    pen = SVGPathPen(glyphs, ntos=PATH_NTOS)
    draw(placed, pen)
    return pen.getCommands(), block_x


def tilted_row(spec, angle):
    """Return (path data, matrix, stroke width) for text or a drawing ("@file.svg") over a full
    stripe, rotated by angle degrees, scaled to fit inside the stripe with TILT_PAD around it,
    left-aligned. Baseline 0. The stroke width (in path units) thickens drawn lines."""
    if spec.startswith("@"):
        src = open(os.path.join(OUT_DIR, spec[1:])).read()
        d = re.search(r' d="([^"]+)"', src).group(1)
        line = float(re.search(r'data-stroke-width="([^"]+)"', src).group(1))
        vh = float(re.search(r'viewBox="([^"]+)"', src).group(1).split()[3])
        ratio = STEM / STRIPE    # stem width relative to cap height, as in the font
        extra = (ratio * vh - line) / (1 - ratio)
        extra = extra if extra > 0.01 * vh else 0   # already fat enough (e.g. colon3-fat.svg)

        def paint(pen, m):
            parse_path(d, TransformPen(pen, m))
    else:
        placed, _ = layout(spec)
        pen = SVGPathPen(glyphs, ntos=PATH_NTOS)
        draw(placed, pen)
        d, extra = pen.getCommands(), 0

        def paint(pen, m):
            draw(placed, pen, m)

    def ink(m):
        bp = BoundsPen(glyphs)
        paint(bp, m)
        return bp.bounds

    x0, y0, x1, y1 = ink(Transform())
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rot = Transform().rotate(math.radians(angle)).translate(-cx, -cy)
    rx0, ry0, rx1, ry1 = ink(rot)
    rx0, ry0, ry1 = rx0 - extra / 2, ry0 - extra / 2, ry1 + extra / 2
    k = (STRIPE - 2 * TILT_PAD) / (ry1 - ry0)
    m = Transform().translate(TILT_PAD - k * rx0, -STRIPE / 2 - k * (ry0 + ry1) / 2).scale(k).transform(rot)
    return d, m, extra


def build(rows, colors, overlay=""):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W + 2 * BORDER} {H + 2 * BORDER}" '
        f'width="{W + 2 * BORDER}" height="{H + 2 * BORDER}">',
        "  <title>All Creatures Welcome</title>",
        "  <!-- Text: Archivo Regular (SIL OFL), converted to outlines -->",
        "  <style>" + " ".join(f".{k}{{fill:{v}}}" for k, v in colors.items()) + "</style>",
        f'  <rect class="dark" width="{W + 2 * BORDER}" height="{H + 2 * BORDER}"/>',
        f'  <g transform="translate({BORDER} {BORDER})">',
    ]
    for i, color in enumerate(ROW_COLORS):
        top = i * (STRIPE + GAP)
        if rows.get(i) in TILTED:
            d, m, extra = tilted_row(rows[i], TILTED[rows[i]])
            m = Transform().translate(0, top + STRIPE).transform(m)
            stroke = (f' fill-rule="evenodd" stroke="{colors["dark"]}" stroke-width="{extra:.2f}"'
                      ' stroke-linejoin="round"' if extra else "")
            parts.append(f'  <rect class="{color}" y="{top}" width="{W}" height="{STRIPE}"/>')
            parts.append(f'  <g opacity="{TILT_OPACITY}"><path class="dark"{stroke} '
                         f'transform="matrix({" ".join(MATRIX_NTOS(v) for v in m)})" d="{d}"/></g>')
        elif i in rows:
            d, block_x = text_row(rows[i])
            parts.append(f'  <rect class="{color}" x="{block_x}" y="{top}" width="{W - block_x}" height="{STRIPE}"/>')
            parts.append(f'  <path class="{color}" transform="translate(0 {top + STRIPE})" d="{d}"/>')
        else:
            parts.append(f'  <rect class="{color}" y="{top}" width="{W}" height="{STRIPE}"/>')
    parts.append("  </g>")
    if overlay:
        parts.append(f"  {overlay}")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


for suffix, colors in PALETTES.items():
    for name, rows in VARIANTS.items():
        out = os.path.join(OUT_DIR, name + suffix + ".svg")
        with open(out, "w") as fh:
            fh.write(build(rows, colors))
        print("wrote", out)

# pride versions with the hand-drawn pawprint (traced by trace_pawprint.py)
for paw_name, suffix in [("pawprint.svg", "-paw"), ("pawprint-solid.svg", "-paw-solid")]:
    paw_file = os.path.join(OUT_DIR, paw_name)
    if os.path.exists(paw_file):
        paw = re.search(r"<path[^>]*/>", open(paw_file).read()).group(0)
        out = os.path.join(OUT_DIR, "all-creatures-3-pride" + suffix + ".svg")
        with open(out, "w") as fh:
            fh.write(build(VARIANTS["all-creatures-3"], PRIDE_COLORS, paw))
        print("wrote", out)
