"""Round 31: combat_meridian_motion.gif (with HUD) + meridian_backdrop_motion.gif (no HUD) + combat_meridian.jpg
(still, frame 6: train stopped, container coming down) + hq_meridian_close_{night,day}.jpg. 20-frame loop."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "combat_r23"))
import backdrop30 as B
from PIL import Image

OUT = os.path.dirname(HERE)
os.chdir(os.path.join(HERE, "combat_r23"))
import make_combat27 as MC

N = 20
hud, raw = [], []
for f in range(N):
    tag = "meridian_hq_f%02d" % f
    im = B.finish(tag, "night")
    raw.append(im.resize((960, 540), Image.LANCZOS))
    MC.BACK["meridian"] = tag + "_night"
    MC.compose("meridian")
    hud.append(Image.open(os.path.join(OUT, "combat_meridian.jpg")).convert("RGB").resize((960, 540), Image.LANCZOS))
for name, frames in (("combat_meridian_motion", hud), ("meridian_backdrop_motion", raw)):
    q = [fr.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for fr in frames]
    p = os.path.join(OUT, name + ".gif")
    q[0].save(p, save_all=True, append_images=q[1:], duration=150, loop=0, optimize=True)
    print(name, os.path.getsize(p) // 1024, "KB", flush=True)
strip = Image.new("RGB", (5 * 480, 2 * 270))
for i, f in enumerate((1, 5, 8, 12, 17)):
    strip.paste(raw[f].resize((480, 270), Image.LANCZOS), (i * 480, 0))
    strip.paste(hud[f].resize((480, 270), Image.LANCZOS), (i * 480, 270))
strip.save(os.path.join(OUT, "combat_meridian_motion_strip.jpg"), quality=88)
MC.BACK["meridian"] = "meridian_hq_f06_night"
MC.compose("meridian")  # the still: train stopped, the container coming down
for m in ("night", "day"):
    B.calm(B.finish("meridian_hq", m)).save(os.path.join(OUT, "hq_meridian_close_%s.jpg" % m), quality=90)
