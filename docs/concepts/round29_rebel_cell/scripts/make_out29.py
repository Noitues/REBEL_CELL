"""Round 29 deliverables (after map29.py and render_all29.py stills gif + the wheels):
  map_redlights_city_{home,dispatch}.jpg (whole map, 2560 x 1440), map_redlights_crop_{home,dispatch}.jpg,
  canyon_home.jpg, canyon_dispatch.jpg, combat_rebel_cell.png (DISPATCH boss), combat_rebel_cell_motion_v2.gif.
The combat UI is the round 25 composite unchanged (combat_r23/make_combat25.py)."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R29 = os.path.dirname(HERE)
SC = os.path.join(R29, "scratch")
F = "C:/Windows/Fonts/bahnschrift.ttf"
NFR = 12


def label(im, text):
    im = im.convert("RGB").copy()
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F, max(20, im.width // 62))
    tw = d.textlength(text, font=f)
    d.rectangle([0, 0, tw + 30, f.size + 18], fill=(10, 9, 16))
    d.rectangle([0, 0, 6, f.size + 18], fill=(255, 40, 50))
    d.text((16, 8), text, font=f, fill=(240, 236, 226))
    return im


def jpg(name, im, text):
    label(im, text).save(os.path.join(R29, name), quality=90, optimize=True)
    print("wrote", name)


what = sys.argv[1:] or ["maps", "stills", "combat", "gif"]
if "maps" in what:
    for st, t in (("home", "home: red window lights"), ("dispatch", "DISPATCH: harsher red, glitched")):
        jpg("map_redlights_city_%s.jpg" % st, Image.open(os.path.join(SC, "map29_%s.png" % st)).resize((2560, 1440), Image.LANCZOS),
            "CITY MAP - THE CELL'S FIST IN RED WINDOW LIGHT (%s)" % t)
        jpg("map_redlights_crop_%s.jpg" % st, Image.open(os.path.join(SC, "map29_%s_crop.png" % st)), "CITY MAP CROP (%s)" % t)
if "stills" in what:
    jpg("canyon_home.jpg", Image.open(os.path.join(SC, "backdrops", "rc29_canyon_night.png")), "CANYON (home): lay low - ordinary shop signs")
    jpg("canyon_dispatch.jpg", Image.open(os.path.join(SC, "backdrops", "rc29_canyon_dispatch_night.png")),
        "CANYON (DISPATCH): every sign shows the fist / REBEL_CELL")

sys.path.insert(0, os.path.join(HERE, "combat_r23"))
import make_combat25 as M

M.SITE["rebel_cell"] = "THE CANYON (TAKEN)"
OUTC = os.path.join(R29, "combat_rebel_cell.png")
if "combat" in what:
    M.BACK["rebel_cell"] = "rc29_canyon_dispatch_night"
    M.compose("rebel_cell")
if "gif" in what:
    frames = []
    keep = os.path.exists(OUTC) and open(OUTC, "rb").read()
    for f in range(NFR):
        M.BACK["rebel_cell"] = "rc29_canyon_dispatch_f%02d_night" % f
        M.compose("rebel_cell")
        frames.append(Image.open(OUTC).convert("RGB").resize((960, 540), Image.LANCZOS))
    if keep:
        open(OUTC, "wb").write(keep)
    pal = frames[0].quantize(colors=200, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    q[0].save(os.path.join(R29, "combat_rebel_cell_motion_v2.gif"), save_all=True, append_images=q[1:], duration=140, loop=0, optimize=True)
    print("gif", os.path.getsize(os.path.join(R29, "combat_rebel_cell_motion_v2.gif")) // 1024, "KB")
