"""Round 26: solace_helix_lights.gif (LED chaser climbing the helix) and halcyon_eye_scan.gif (the eye turns and
scans the city with its searchlight). Frames come from hq_scene.py "anim" (beauty + glow per frame, passes once),
finished with the same style pass as the stills (backdrop26.finish)."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backdrop26 as B
from PIL import Image

OUT = os.path.dirname(HERE)
JOBS = [("solace_hq", "solace_helix_lights", (540, 600), 90), ("halcyon_hq", "halcyon_eye_scan", (720, 405), 110)]
CROP = {"solace_hq": (420, 0, 1392, 1080)}  # frame the helix so the climbing lights read
for tag, name, size, dur in JOBS:
    frames = []
    for f in range(12):
        v = "%s_f%02d" % (tag, f)
        for k in ("normal", "id", "depth"):
            shutil.copyfile(os.path.join(B.SRC, "%s_anim_%s.png" % (tag, k)), os.path.join(B.SRC, "%s_%s.png" % (v, k)))
        im = B.finish(v, "night")
        frames.append(im)
    if tag == "halcyon_hq":  # a still strip of four scan positions
        strip = Image.new("RGB", (4 * 640, 360))
        for i, f in enumerate((0, 3, 6, 9)):
            strip.paste(frames[f].resize((640, 360), Image.LANCZOS), (i * 640, 0))
        strip.save(os.path.join(OUT, "halcyon_eye_scan_strip.jpg"), quality=88)
    if tag in CROP:
        frames = [fr.crop(CROP[tag]) for fr in frames]
    q = [fr.resize(size, Image.LANCZOS).quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for fr in frames]
    p = os.path.join(OUT, name + ".gif")
    q[0].save(p, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=True)
    print(name, os.path.getsize(p) // 1024, "KB", flush=True)
