# All Creatures Welcome – flag vectors

Clean vector replicas and variants of the *All Creatures Welcome* flag (as seen at 37C3),
in the six-stripe pride colours. All text is converted to outlines, so the SVGs do not
need any font installed to display correctly.

## Requirements

- Python 3.10+
- Python packages:

  | Package     | Needed for                                         |
  |-------------|----------------------------------------------------|
  | `fonttools` | `make_flag_svg.py` – reads the font, glyph outlines |
  | `uharfbuzz` | `make_flag_svg.py` – text shaping / kerning         |
  | `numpy`     | `trace_*.py`                                        |
  | `scipy`     | `trace_*.py`                                        |
  | `potracer`  | `trace_*.py` – bitmap → Bézier tracing (imported as `potrace`) |
  | `pillow`    | `trace_*.py`                                        |
  | `cairosvg`  | optional – rendering PNG previews                   |

  ```bash
  pip install fonttools uharfbuzz numpy scipy potracer pillow cairosvg
  ```

  `cairosvg` also needs the system Cairo library (`sudo apt install libcairo2` on Debian/Ubuntu).
  ImageMagick (`montage`) is only used for the overview image and is optional.

- Font: **Archivo Regular** (SIL Open Font License), not included in this repo.
  Download the static TTF:

  ```bash
  mkdir -p fonts
  curl -L -o fonts/Archivo-Regular.ttf \
    https://github.com/Omnibus-Type/Archivo/raw/master/fonts/ttf/Archivo-Regular.ttf
  ```

## Generate the flags

```bash
python3 make_flag_svg.py fonts/Archivo-Regular.ttf .
```

Arguments: the font file and the output directory. The output directory must also contain
the traced drawings used by the variants (`colon3-fat.svg`, `pawprint.svg`, `pawprint-solid.svg`).

Written files:

| File                                  | Content                                              |
|---------------------------------------|------------------------------------------------------|
| `all-creatures-welcome-pride.svg`     | ALL / CREATURES / WELCOME                            |
| `creatures-pride.svg`                 | CREATURES only                                       |
| `creatures-3-pride.svg`               | CREATURES :3 on the orange row                       |
| `creatures-3-yellow-pride.svg`        | CREATURES, hand-drawn :3 over the yellow stripe      |
| `all-creatures-3-pride.svg`           | ALL / CREATURES, hand-drawn :3 over the yellow stripe |
| `all-creatures-3-pride-paw.svg`       | as above, plus the outlined pawprint                 |
| `all-creatures-3-pride-paw-solid.svg` | as above, plus the solid pawprint                    |

### PNG previews

```bash
python3 -c "
import glob, cairosvg
for f in glob.glob('*-pride*.svg'):
    cairosvg.svg2png(url=f, write_to=f[:-4] + '.png')
"
montage $(ls *-pride*.png | grep -v '^montage') -tile 2x -geometry 900x474+12+12 -background white montage-pride.png
```

Use cairosvg rather than ImageMagick's built-in SVG renderer, which ignores `opacity`
(the tilted :3 is 14 % transparent).

### Settings in `make_flag_svg.py`

| Setting                     | Meaning                                                    |
|-----------------------------|------------------------------------------------------------|
| `W`, `STRIPE`, `GAP`, `BORDER` | artwork width, stripe height (= cap height), separator, frame |
| `COLORS`, `PRIDE_COLORS`, `PALETTES` | colours; `PALETTES` decides which colour sets are written |
| `VARIANTS`                  | which text goes on which row (0 = red … 5 = violet); `"@file.svg"` places a traced drawing |
| `TILTED`                    | rows drawn in dark over a full stripe, with their rotation in degrees |
| `TILT_PAD`, `TILT_OPACITY`  | inset and opacity of the tilted drawing                    |