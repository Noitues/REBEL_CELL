"""options_sheet.png: the three CAM options (source crop thumbnail + feed at 1:1) and the old slab."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
from PIL import Image, ImageDraw, ImageFont

import cam
import r31lib as L

PICK = sys.argv[1] if len(sys.argv) > 1 else "B"
sheet = Image.new("RGB", (1920, 1080), (10, 9, 16))
d = ImageDraw.Draw(sheet)
d.text((24, 16), "TERMINAL EVENT CARD: CAM FEED OPTIONS (O-9)", font=L.font(L.ANTON, 40), fill=(244, 244, 248))
d.text((26, 62), "street-cam treatment: 280x190 low-res cel, barrel fisheye, Solace duotone, scanlines, grain, REC + timestamp.  Feed at 1:1 (560x380).",
       font=L.f_mono(15), fill=(160, 168, 186))
cols = [("OLD", None)] + [(k, k) for k in "ABC"]
xs = [20, 500, 1000, 1500]
# 2 x 2 grid: old, A, B, C
cell = [(20, 100), (980, 100), (20, 590), (980, 590)]
oldp = os.path.join(os.path.dirname(os.path.dirname(OUT)), "cohesion", "supporting_r42", "01_terminal_event.png")
old = Image.open(oldp).convert("RGB").crop((120, 184, 680, 564))
items = [("OLD  the pale slab (r42)", old, None)]
for k in "ABC":
    o = cam.OPTIONS[k]
    src = Image.open(o["src"]).convert("RGB")
    thumb = src.copy(); td = ImageDraw.Draw(thumb); td.rectangle(o["crop"], outline=(255, 214, 64), width=8)
    thumb = thumb.resize((340, 191), Image.LANCZOS)
    items.append(("%s  %s%s" % (k, o["name"], "   <- PICK" if k == PICK else ""), cam.feed_panel_for(k, L.f_mono(16)).convert("RGB"), thumb))
for (x, y), (title, feed, thumb) in zip(cell, items):
    d.text((x, y), title, font=L.font(L.ANTON, 30), fill=(255, 214, 64) if "PICK" in title else (230, 236, 240))
    sheet.paste(feed, (x, y + 44))
    if thumb:
        sheet.paste(thumb, (x + 580, y + 44))
        d.text((x + 580, y + 44 + 197), "source crop (yellow)", font=L.f_mono(14), fill=(150, 160, 175))
sheet.save(os.path.join(OUT, "01_cam_options_sheet.png"))
print("ok")
