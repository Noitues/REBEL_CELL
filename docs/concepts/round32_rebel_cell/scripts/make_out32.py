"""Round 32 deliverables (after map_all31.py, render_all31.py stills gif homegif and the wheels):
  map_A_{home,dispatch}.jpg, map_A_{home,dispatch}_crop.jpg, map_ring_{home,dispatch}.jpg (+ _crop),
  map_ring_blackout.gif (the ring lights flickering off, home then DISPATCH, <= 3 MB),
  canyon_home.jpg, canyon_dispatch.jpg, canyon_home_motion.gif (the microchips turn),
  combat_rebel_cell.png (DISPATCH boss), combat_rebel_cell_motion.gif (DISPATCH)."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)
SC = os.path.join(R, "scratch")
F = "C:/Windows/Fonts/bahnschrift.ttf"
NFR = 12


def label(im, text):
    im = im.convert("RGB").copy()
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F, max(16, im.width // 62))
    d.rectangle([0, 0, d.textlength(text, font=f) + 30, f.size + 18], fill=(10, 9, 16))
    d.rectangle([0, 0, 6, f.size + 18], fill=(255, 40, 50))
    d.text((16, 8), text, font=f, fill=(240, 236, 226))
    return im


def jpg(name, im, text):
    label(im, text).save(os.path.join(R, name), quality=88, optimize=True)
    print("wrote", name)


def gif(name, frames, ms, colors=160):
    pal = frames[len(frames) // 2].quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(os.path.join(R, name), save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True)
    print("gif", name, os.path.getsize(os.path.join(R, name)) // 1024, "KB")


what = sys.argv[1:] or ["maps", "mapgif", "stills", "combat", "gif"]
if "maps" in what:
    for st in ("home", "dispatch"):
        jpg("map_A_%s.jpg" % st, Image.open(os.path.join(SC, "map32_A_%s.png" % st)).resize((2560, 1440), Image.LANCZOS),
            "CITY MAP - red-window fist with blacked-out detail lines (%s)" % st.upper())
        jpg("map_A_%s_crop.jpg" % st, Image.open(os.path.join(SC, "map32_A_%s_crop.png" % st)), "CROP A (%s)" % st.upper())
        jpg("map_ring_%s.jpg" % st, Image.open(os.path.join(SC, "map32_A_%s_ring.png" % st)).resize((2560, 1440), Image.LANCZOS),
            "CITY MAP A + BLACKOUT RING - the city's lights round the fist are off (%s)" % st.upper())
        jpg("map_ring_%s_crop.jpg" % st, Image.open(os.path.join(SC, "map32_A_%s_ring_crop.png" % st)), "CROP A + BLACKOUT RING (%s)" % st.upper())
if "mapgif" in what:
    frames = []
    for st in ("home", "dispatch"):
        for f in range(NFR):
            im = Image.open(os.path.join(SC, "map32_A_%s_ring_%02d_crop.png" % (st, f))).convert("RGB").resize((640, 460), Image.LANCZOS)
            frames.append(label(im, "BLACKOUT RING - %s" % st.upper()))
    gif("map_ring_blackout.gif", frames, 220, colors=96)
if "stills" in what:
    jpg("canyon_home.jpg", Image.open(os.path.join(SC, "backdrops", "rc32_canyon_night.png")),
        "CANYON (home): brighter, every sign panel filled")
    jpg("canyon_dispatch.jpg", Image.open(os.path.join(SC, "backdrops", "rc32_canyon_dispatch_night.png")),
        "CANYON (DISPATCH): anti-human takeover")
if "homegif" in what:
    gif("canyon_home_motion.gif", [Image.open(os.path.join(SC, "backdrops", "rc32_canyon_f%02d_night.png" % f)).convert("RGB").resize((800, 450), Image.LANCZOS)
                                  for f in range(NFR)], 140, colors=128)

sys.path.insert(0, os.path.join(HERE, "combat_r23"))
import make_combat25 as M

M.SITE["rebel_cell"] = "THE CANYON (TAKEN)"
OUTC = os.path.join(R, "combat_rebel_cell.png")
if "combat" in what:
    M.BACK["rebel_cell"] = "rc32_canyon_dispatch_night"
    M.compose("rebel_cell")
if "gif" in what:
    frames = []
    keep = os.path.exists(OUTC) and open(OUTC, "rb").read()
    for f in range(NFR):
        M.BACK["rebel_cell"] = "rc32_canyon_dispatch_f%02d_night" % f
        M.compose("rebel_cell")
        frames.append(Image.open(OUTC).convert("RGB").resize((960, 540), Image.LANCZOS))
    if keep:
        open(OUTC, "wb").write(keep)
    gif("combat_rebel_cell_motion.gif", frames, 140, colors=200)
