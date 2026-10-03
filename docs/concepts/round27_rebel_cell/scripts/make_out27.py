"""Round 27 deliverables: map_painted_roofs_{home,dispatch}.jpg, canyon_close_night_{home,dispatch}.jpg, combat_rebel_cell.png.
Run after map27.py and post26.py; the combat uses the round 25 composite (combat_r23/make_combat25.py) with the round 27
DISPATCH canyon as the backdrop (wheels: wheels_r18/render_bosses24.py rebel_cell, dump_boss_slots24.py, combat_r23/render_player24.py)."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R27 = os.path.dirname(HERE)
SC = os.path.join(R27, "scratch")
F = "C:/Windows/Fonts/bahnschrift.ttf"


def label(im, text):
    im = im.convert("RGB").copy()
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F, max(20, im.width // 62))
    tw = d.textlength(text, font=f)
    d.rectangle([0, 0, tw + 30, f.size + 18], fill=(10, 9, 16))
    d.rectangle([0, 0, 6, f.size + 18], fill=(212, 255, 0))
    d.text((16, 8), text, font=f, fill=(240, 236, 226))
    return im


for name, src, text in (
        ("map_painted_roofs_home.jpg", "mapcrops/rc27_canyon.png", "CITY MAP - THE CELL'S DISTRICT (home): painted roofs, normal street grid"),
        ("map_painted_roofs_dispatch.jpg", "mapcrops/rc27_canyon_dispatch.png", "CITY MAP - AFTER THE BETRAYAL (DISPATCH): the paint corrupted"),
        ("canyon_close_night_home.jpg", "backdrops/rc27_canyon_night.png", "COMBAT BACKDROP - THE CANYON (home)"),
        ("canyon_close_night_dispatch.jpg", "backdrops/rc27_canyon_dispatch_night.png", "COMBAT BACKDROP - THE CANYON (DISPATCH)")):
    label(Image.open(os.path.join(SC, src)), text).save(os.path.join(R27, name), quality=90, optimize=True)
    print("wrote", name)

sys.path.insert(0, os.path.join(HERE, "combat_r23"))
import make_combat25 as M

M.BACK["rebel_cell"] = "rc27_canyon_dispatch_night"
M.SITE["rebel_cell"] = "THE CANYON (TAKEN)"
M.compose("rebel_cell")
