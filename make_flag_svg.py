"""Generate clean vector replicas / variants of the 'All Creatures Welcome' flag.

Geometry was measured from the perspective-corrected photo (flag_straightened.jpg)
and idealised to a regular grid. Text is Archivo Regular, converted to outlines.

usage: python3 make_flag_svg.py <Archivo-Regular.ttf> <out_dir>
needs: fonttools, uharfbuzz
"""
import os
import re
import sys

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT, OUT_DIR = sys.argv[1], sys.argv[2]

W = 3575            # artwork width
STRIPE = 290        # stripe height = cap height
GAP = 24            # dark separator between stripes
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
PALETTES = {"": COLORS, "-pride": PRIDE_COLORS}
ROW_COLORS = ["red", "orange", "yellow", "green", "blue", "pink"]

# femboy flag, 7 stripes
FEMBOY_COLORS = {
    "dark":      COLORS["dark"],
    "violet":    "#d460a7",
    "pink":      "#e4adcd",
    "white":     "#ffffff",
    "lightblue": "#57cef8",
}
FEMBOY_ROW_COLORS = ["violet", "pink", "white", "lightblue", "white", "pink", "violet"]

# placement measured on the original flag: ink left, ink right, block start
MEASURED = {
    "ALL":       (9, 760, 790),
    "CREATURES": (2, 2571, 2588),
    "WELCOME":   (14, 2182, 2196),
}
DEFAULT_LEFT = 12
DEFAULT_TRACKING = 5.1  # font units, as fitted for CREATURES
DEFAULT_BLOCK_GAP = 17

# variant name -> text per row (rows without text are full stripes)
VARIANTS = {
    "all-creatures-welcome":   {0: "ALL", 1: "CREATURES", 2: "WELCOME"},
    "creatures":               {1: "CREATURES"},
    "creatures-3":             {1: "CREATURES :3"},
    "creatures-3-yellow":      {1: "CREATURES", 2: ":3"},
    "all-creatures-3":         {0: "ALL", 1: "CREATURES", 2: ":3"},
    "all-creatures-are-beautiful": {0: "ALL", 1: "CREATURES", 2: "ARE", 3: "BEAUTIFUL"},
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


def ink_extent(run, tracking):
    x, first_l, last_r = 0, None, None
    for name, adv in run:
        b = bounds(name)
        if b:
            first_l = x + b[0] if first_l is None else first_l
            last_r = x + b[2]
        x += adv + tracking
    return first_l, last_r


def text_row(text):
    """Return (path data, block start x) for a text row placed at baseline 0."""
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

    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    x = -first_l
    for name, adv in run:
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, left + x * scale, 0)))
        x += adv + tracking
    return pen.getCommands(), block_x


def build(rows, colors, overlay="", row_colors=ROW_COLORS):
    H = len(row_colors) * STRIPE + (len(row_colors) - 1) * GAP
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W + 2 * BORDER} {H + 2 * BORDER}" '
        f'width="{W + 2 * BORDER}" height="{H + 2 * BORDER}">',
        "  <title>All Creatures Welcome</title>",
        "  <!-- Text: Archivo Regular (SIL OFL), converted to outlines -->",
        "  <style>" + " ".join(f".{k}{{fill:{v}}}" for k, v in colors.items()) + "</style>",
        f'  <rect class="dark" width="{W + 2 * BORDER}" height="{H + 2 * BORDER}"/>',
        f'  <g transform="translate({BORDER} {BORDER})">',
    ]
    for i, color in enumerate(row_colors):
        top = i * (STRIPE + GAP)
        if i in rows:
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

out = os.path.join(OUT_DIR, "all-femboys-3.svg")
with open(out, "w") as fh:
    fh.write(build({0: "ALL", 1: "FEMBOYS", 2: ":3"}, FEMBOY_COLORS, row_colors=FEMBOY_ROW_COLORS))
print("wrote", out)
