"""Contact sheet of the five RISO PUNK ZINE stills, labelled, on riso paper.

python contact_sheet.py
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from riso_print import INK, font, paper

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STILLS = os.path.join(ROOT, "stills")
ITEMS = [("01_combat.png", "01 COMBAT: stacked discs, 0/1 shards, sticker hand, SEND IT over EXECUTE"),
         ("02_city_night.png", "02 CITY NIGHT: pop-up diorama, 3 road levels, holo acetates, grid on one plane"),
         ("03_heat.png", "03 HEAT HUNTED: helis + searchlights, drones, red overprint, heat glitch"),
         ("04_hq_modem.png", "04 MODEM: bent-tube MODEM / CYBER SHOP sign, stickered glass, GRAB IT / BAIL"),
         ("05_marker_strip.png", "05 MARKER LIFE: write-on / drips wait / page leaves, ink runs")]

TW, TH = 900, 506
PAD, LAB = 40, 54
W = PAD * 3 + TW * 2
H = PAD + 150 + (TH + LAB + PAD) * 3
sheet = paper((W, H), INK["paper"], 900, amount=16)
d = ImageDraw.Draw(sheet)
d.text((PAD, 30), "RISO PUNK ZINE", font=font("anton", 84), fill=INK["black"])
d.text((PAD + 520, 64), "concept C . c_riso_zine . the world as printed matter", font=font("mono", 28), fill=INK["black"])
for i, (fn, label) in enumerate(ITEMS):
    im = Image.open(os.path.join(STILLS, fn)).convert("RGB").resize((TW, TH), Image.LANCZOS)
    col, row = i % 2, i // 2
    x = PAD + col * (TW + PAD)
    y = PAD + 150 + row * (TH + LAB + PAD)
    if i == 4:
        x = (W - TW) // 2
    d.rectangle((x + 8, y + 8, x + TW + 8, y + TH + 8), fill=(40, 36, 40))
    sheet.paste(im, (x, y))
    d.text((x, y + TH + 12), label, font=font("mono", 18), fill=INK["black"])
out = os.path.join(ROOT, "contact_sheet.jpg")
sheet.save(out, quality=88)
print("sheet ->", out)
