# All Creatures Welcome – flag vectors

Clean vector replicas and variants of the *All Creatures Welcome* flag (as seen at 37C3),
in the six-stripe pride colours. All text is converted to outlines, so the SVGs do not
need any font installed to display correctly.

## Requirements

- Python 3.10+
- Python packages:

  | Package     | Needed for                                          |
  |-------------|-----------------------------------------------------|
  | `fonttools` | `make_flag_svg.py` – reads the font, glyph outlines |
  | `uharfbuzz` | `make_flag_svg.py` – text shaping / kerning         |
  | `cairosvg`  | optional – rendering PNG previews                   |

  ```bash
  pip install fonttools uharfbuzz cairosvg
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

Arguments: the font file and the output directory. The paw variants are only written if the
output directory contains the traced pawprints (`pawprint.svg`, `pawprint-solid.svg`, both
included in this repo).

Every variant is written twice: with the `-pride` suffix in the pride colours, and without
a suffix in the colours of the original flag. Only the pride versions below are part of
this repo; the others are listed in `.gitignore`.

| File                                    | Content                                    |
|-----------------------------------------|--------------------------------------------|
| `all-creatures-welcome-pride.svg`       | ALL / CREATURES / WELCOME                  |
| `all-creatures-3-pride.svg`             | ALL / CREATURES / :3                       |
| `all-creatures-3-pride-paw.svg`         | as above, plus the outlined pawprint       |
| `all-creatures-3-pride-paw-solid.svg`   | as above, plus the solid pawprint          |
| `all-creatures-are-beautiful-pride.svg` | ALL / CREATURES / ARE / BEAUTIFUL          |
| `creatures-pride.svg`                   | CREATURES only (not committed)             |
| `creatures-3-pride.svg`                 | CREATURES :3 on the orange row (not committed) |
| `creatures-3-yellow-pride.svg`          | CREATURES, :3 on the yellow row (not committed) |

### PNG previews

```bash
python3 -c "
import glob, cairosvg
for f in glob.glob('*-pride*.svg'):
    cairosvg.svg2png(url=f, write_to=f[:-4] + '.png')
"
montage $(ls *-pride*.png | grep -v '^montage') -tile 2x -geometry 900x474+12+12 -background white montage-pride.png
```

### Settings in `make_flag_svg.py`

| Setting                        | Meaning                                                       |
|--------------------------------|---------------------------------------------------------------|
| `W`, `STRIPE`, `GAP`, `BORDER` | artwork width, stripe height (= cap height), separator, frame |
| `COLORS`, `PRIDE_COLORS`       | original and pride colours                                    |
| `PALETTES`                     | which colour sets are written, mapped to their file suffix    |
| `MEASURED`                     | placement of ALL / CREATURES / WELCOME as measured on the original flag |
| `DEFAULT_LEFT`, `DEFAULT_TRACKING`, `DEFAULT_BLOCK_GAP` | placement of any other text |
| `VARIANTS`                     | file name → text per row (0 = red … 5 = violet); rows without text are full stripes |

To make a new variant, add a line to `VARIANTS`, e.g.
`"all-creatures-are-cute": {0: "ALL", 1: "CREATURES", 2: "ARE", 3: "CUTE"}`.
