"""Convert sticker SVGs to CMYK print PDFs with trim and bleed box.

usage: python3 make_print_pdf.py <cmyk.icc> <bleed mm> <file.svg>...
needs: cairosvg, pypdf, ghostscript
"""
import os
import subprocess
import sys
import tempfile

import cairosvg
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

MM = 72 / 25.4

icc, bleed = sys.argv[1], float(sys.argv[2]) * MM
for svg in sys.argv[3:]:
    out = svg[:-4] + ".pdf"
    with tempfile.TemporaryDirectory() as tmp:
        rgb, cmyk = os.path.join(tmp, "rgb.pdf"), os.path.join(tmp, "cmyk.pdf")
        cairosvg.svg2pdf(url=svg, write_to=rgb)
        subprocess.run(["gs", "-q", "-dBATCH", "-dNOPAUSE", "-dSAFER", "-sDEVICE=pdfwrite",
                        "-dCompatibilityLevel=1.6", "-sColorConversionStrategy=CMYK",
                        f"-sOutputICCProfile={icc}", "-dRenderIntent=1", "-o", cmyk, rgb], check=True)
        writer = PdfWriter(clone_from=cmyk)
    for page in writer.pages:
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        page.bleedbox = RectangleObject([0, 0, w, h])
        page.trimbox = RectangleObject([bleed, bleed, w - bleed, h - bleed])
    writer.add_metadata({"/Title": os.path.basename(out)})
    writer.write(out)
    print("wrote", out)
