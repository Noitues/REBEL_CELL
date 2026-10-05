"""Round 30 v2 (HQ_PAN=32: the castle and yard pan left so the crane, trolley and train sit in the gap between the wheels): combat_meridian_motion.gif - the 16 animation frames (crane loop + passing train) finished with the style
pass, composited under the locked combat HUD (make_combat27.compose), 960 x 540."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "combat_r23"))
import backdrop30 as B
from PIL import Image

OUT = os.path.dirname(HERE)
os.chdir(os.path.join(HERE, "combat_r23"))
import make_combat27 as MC

frames = []
for f in range(16):
    tag = "meridian_hq_f%02d" % f
    B.finish(tag, "night")
    MC.BACK["meridian"] = tag + "_night"
    MC.compose("meridian")
    frames.append(Image.open(os.path.join(OUT, "combat_meridian.jpg")).convert("RGB").resize((960, 540), Image.LANCZOS))
strip = Image.new("RGB", (4 * 480, 270))
for i, f in enumerate((0, 5, 9, 13)):
    strip.paste(frames[f].resize((480, 270), Image.LANCZOS), (i * 480, 0))
strip.save(os.path.join(OUT, "combat_meridian_motion_strip_v2.jpg"), quality=88)
q = [fr.quantize(colors=160, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for fr in frames]
p = os.path.join(OUT, "combat_meridian_motion_v2.gif")
q[0].save(p, save_all=True, append_images=q[1:], duration=160, loop=0, optimize=True)
print("gif", os.path.getsize(p) // 1024, "KB")
import shutil
MC.BACK["meridian"] = "meridian_hq_f00_night"
MC.compose("meridian")
shutil.move(os.path.join(OUT, "combat_meridian.jpg"), os.path.join(OUT, "combat_meridian_v2.jpg"))  # the still (frame 0)
