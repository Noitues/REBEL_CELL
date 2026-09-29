"""W3 before/after sheets: the W10 baseline next to a W3 capture, one JPG per screen and combo.

    python docs/art_review/W3/before_after.py <baseline full dir> <out dir> <after dir> [<after dir> ...]

Each after dir is a capture_pack output (<combo>/<screen>.png). Every picture found in an
after dir and in the baseline (same relative path) becomes <out>/<combo>/<screen>.jpg: the
before and the after side by side at half size, labelled, JPG q85. Written as a file on
purpose (never run Python from stdin on this machine).
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw

base = Path(sys.argv[1])
out = Path(sys.argv[2])
made = 0
for after in [Path(a) for a in sys.argv[3:]]:
    for png in sorted(after.glob("*/*.png")):
        rel = png.relative_to(after)
        b = base / rel
        if not b.exists():
            continue
        half = (640, 360)
        pb = Image.open(b).convert("RGB").resize(half)
        pa = Image.open(png).convert("RGB").resize(half)
        sheet = Image.new("RGB", (1284, 384), (6, 8, 22))
        sheet.paste(pb, (0, 24))
        sheet.paste(pa, (644, 24))
        d = ImageDraw.Draw(sheet)
        d.text((6, 6), "BEFORE (W10 baseline)  %s" % rel.as_posix(), fill=(175, 192, 214))
        d.text((650, 6), "AFTER (W3)", fill=(242, 238, 228))
        dest = out / rel.parent.name / (png.stem + ".jpg")
        dest.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(dest, "JPEG", quality=85)
        made += 1
print("before/after sheets:", made)
