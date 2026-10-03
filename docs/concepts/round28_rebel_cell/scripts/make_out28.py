"""Round 28 deliverables (after render_all28.py and map28.py):
  map_fist_paint_v2_{home,dispatch}.jpg, map_fist_holo_{home,dispatch}.jpg,
  canyon_close_night_{home,dispatch}.jpg (the darker canyon), canyon_street_night_home.jpg,
  combat_rebel_cell.png (DISPATCH boss, combat zoom), combat_street_level.png (DISPATCH boss, eye height),
  combat_rebel_cell_motion.gif (960 x 540, 12 frames: the backdrop's signs and holograms animate).
The combat UI is the round 25 composite unchanged (combat_r23/make_combat25.py)."""
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R28 = os.path.dirname(HERE)
SC = os.path.join(R28, "scratch")
F = "C:/Windows/Fonts/bahnschrift.ttf"
NFR = 12


def label(im, text):
    im = im.convert("RGB").copy()
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F, max(20, im.width // 62))
    tw = d.textlength(text, font=f)
    d.rectangle([0, 0, tw + 30, f.size + 18], fill=(10, 9, 16))
    d.rectangle([0, 0, 6, f.size + 18], fill=(212, 255, 0))
    d.text((16, 8), text, font=f, fill=(240, 236, 226))
    return im


def jpg(name, src, text):
    label(Image.open(os.path.join(SC, src)), text).save(os.path.join(R28, name), quality=90, optimize=True)
    print("wrote", name)


what = sys.argv[1:] or ["maps", "stills", "combat", "gif"]
if "maps" in what:
    jpg("map_fist_paint_v2_home.jpg", "mapcrops/map_paint_home.png", "CITY MAP - PAINT V2 (home): a few big crude roller strokes draw the fist across the roofs")
    jpg("map_fist_paint_v2_dispatch.jpg", "mapcrops/map_paint_dispatch.png", "CITY MAP - PAINT V2 (DISPATCH): the strokes re-lit red, torn and blacked out")
    jpg("map_fist_holo_home.jpg", "mapcrops/map_holo_home.png", "CITY MAP - HOLOGRAM (home): a flat fist hovering just above the rooftops")
    jpg("map_fist_holo_dispatch.jpg", "mapcrops/map_holo_dispatch.png", "CITY MAP - HOLOGRAM (DISPATCH): red, torn, dropping out")
if "stills" in what:
    jpg("canyon_close_night_home.jpg", "backdrops/rc28_canyon_night.png", "CANYON - COMBAT ZOOM, DARKER (home)")
    jpg("canyon_close_night_dispatch.jpg", "backdrops/rc28_canyon_dispatch_night.png", "CANYON - COMBAT ZOOM, DARKER (DISPATCH)")
    jpg("canyon_street_night_home.jpg", "backdrops/rc28_canyon_street_night.png", "CANYON - STREET LEVEL (home)")
    jpg("canyon_street_night_dispatch.jpg", "backdrops/rc28_canyon_dispatch_street_night.png", "CANYON - STREET LEVEL (DISPATCH)")

sys.path.insert(0, os.path.join(HERE, "combat_r23"))
import make_combat25 as M

M.SITE["rebel_cell"] = "THE CANYON (TAKEN)"
OUTC = os.path.join(R28, "combat_rebel_cell.png")
if "combat" in what:
    M.BACK["rebel_cell"] = "rc28_canyon_street_dispatch_night" if False else "rc28_canyon_dispatch_street_night"
    M.SITE["rebel_cell"] = "THE CANYON, STREET LEVEL (TAKEN)"
    M.compose("rebel_cell")
    shutil.move(OUTC, os.path.join(R28, "combat_street_level.png"))
    M.SITE["rebel_cell"] = "THE CANYON (TAKEN)"
    M.BACK["rebel_cell"] = "rc28_canyon_dispatch_night"
    M.compose("rebel_cell")
if "gif" in what:
    frames = []
    keep = os.path.exists(OUTC) and open(OUTC, "rb").read()
    for f in range(NFR):
        M.BACK["rebel_cell"] = "rc28_canyon_dispatch_f%02d_night" % f
        M.compose("rebel_cell")
        frames.append(Image.open(OUTC).convert("RGB").resize((960, 540), Image.LANCZOS))
    if keep:
        open(OUTC, "wb").write(keep)  # the still stays the still
    pal = frames[0].quantize(colors=200, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    q[0].save(os.path.join(R28, "combat_rebel_cell_motion.gif"), save_all=True, append_images=q[1:], duration=140, loop=0, optimize=True)
    print("gif", os.path.getsize(os.path.join(R28, "combat_rebel_cell_motion.gif")) // 1024, "KB")
