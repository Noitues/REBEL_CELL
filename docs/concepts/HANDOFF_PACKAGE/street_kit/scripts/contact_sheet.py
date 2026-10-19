"""Compose kit_contact_sheet.png (1280x720) from the verify tiles. Usage: python contact_sheet.py [scratch_dir]"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, ".."))
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else "D:/rc_scratch/street_kit"
props = json.load(open(os.path.join(KIT, "roles.json")))["props"]


def sheet(W, H, cols, rows, name, fs):
    cw, ch = W // cols, H // rows
    img = Image.new("RGB", (W, H), (10, 10, 14))
    dr = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=fs)
    except TypeError:
        font = ImageFont.load_default()
    for i, p in enumerate(props):
        t = Image.open(os.path.join(SCRATCH, "tile_%s.png" % p["id"])).convert("RGB").resize((cw - 2, ch - 2), Image.LANCZOS)
        x, y = (i % cols) * cw, (i // cols) * ch
        img.paste(t, (x + 1, y + 1))
        dr.rectangle([x + 1, y + ch - fs - 5, x + cw - 2, y + ch - 2], fill=(0, 0, 0))
        dr.text((x + 3, y + ch - fs - 4), p["id"], fill=(230, 230, 230), font=font)
    img.save(os.path.join(KIT, name))


assert len(props) <= 35
sheet(1280, 720, 7, 5, "kit_contact_sheet.png", 10)
print("sheet written", len(props))
