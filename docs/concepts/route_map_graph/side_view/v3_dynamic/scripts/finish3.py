"""V3 dynamic: the deliverables built from the composed frames and passes.

python finish3.py sheet     -> architecture_sheet.png (2560 x 2000: 10 connection types + 7 building types, labelled)
python finish3.py gif       -> zoom.gif (decision -> overview, ~1.5 s, 960 x 540)
python finish3.py mp4       -> cam_run.mp4 (Blender's own FFmpeg via the sequencer; 1280 x 720, 24 fps)
python finish3.py compare   -> compare_v3.jpg (old V3 mid | new D_mid / D_mid_hover / O_overview)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw  # noqa: E402

import ui31 as K  # noqa: E402
import sidekit as S  # noqa: E402
import sgraph3 as G  # noqa: E402
import cam_rig as R  # noqa: E402

ROOT = os.path.dirname(HERE)
PARENT = os.path.dirname(ROOT)
SCR = os.path.join(ROOT, "scratch")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

ORDER = ["tube", "zip", "lift", "duct", "ladder", "roofjump", "tram", "plank", "pipe", "tunnel"]


def dashed(d, pts, col, w, on=14, off=9):
    import math
    t = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-3:
            continue
        s = 0.0
        while s < L:
            c = (t + s) % (on + off)
            if c < on:
                e = min(L, s + on - c)
                d.line([(x0 + (x1 - x0) * s / L, y0 + (y1 - y0) * s / L), (x0 + (x1 - x0) * e / L, y0 + (y1 - y0) * e / L)],
                       fill=col, width=w)
                s = e
            else:
                s += on + off - c
        t += L


def sheet():
    import post3
    bl = os.path.join(SCR, "bl")
    strips = []
    for name in ("sheet_c1", "sheet_c2", "sheet_b"):
        A = json.load(open(os.path.join(bl, "anchors_%s.json" % name)))
        A["cam"]["dist"] = 400.0
        json.dump(A, open(os.path.join(bl, "anchors_%s.json" % name), "w"))
        sz = Image.open(os.path.join(bl, "%s_beauty.png" % name)).size
        plate = post3.finish(name, bl, rain_n=0, out_size=sz).convert("RGBA")
        d = ImageDraw.Draw(plate)
        for k, c in A["cells"].items():
            if "path" in c and c["path"] and all(c["path"]):
                pts = [tuple(p) for p in c["path"]]
                d.line(pts, fill=(8, 6, 14, 230), width=10, joint="curve")
                dashed(d, pts, S.ORANGE + (255,), 6)
        for k, c in A["cells"].items():
            if not c.get("label_at"):
                continue
            x, y = c["label_at"]
            if k.startswith("arch_"):
                lab, sub = c["label"].upper(), ""
            else:
                lab, sub = G.CONN_NAME[k].upper(), "hint: " + G.CONN_HINT[k]
            if not (0 < x < plate.width):
                continue
            f = K.F(K.MONO, 26)
            tw = max(f.getlength(lab), K.F(K.MONO, 19).getlength(sub)) + 28
            y = min(y, plate.height - 70)
            box = (x - tw / 2, y + 6, x + tw / 2, y + (66 if sub else 44))
            d.rectangle(box, fill=(5, 13, 28, 235), outline=(92, 225, 255, 200), width=2)
            K.text(plate, (x, y + 25), lab, f, (212, 255, 0), "mm", 0.6)
            if sub:
                K.text(plate, (x, y + 52), sub, K.F(K.MONO, 19), (200, 210, 225), "mm", 0.4)
        strips.append(plate)
    W = 2560
    head = 92
    bar = 46
    Hh = head + sum(s.height + bar for s in strips)
    out = Image.new("RGBA", (W, Hh), (8, 6, 14, 255))
    d = ImageDraw.Draw(out)
    K.text(out, (32, 46), "NETRUN STREET KIT  //  CONNECTION TYPES + BUILDING TYPES", K.F(K.ANTON, 44), (242, 246, 255), "lm", 0.6)
    K.text(out, (1700, 46), "the orange dash = the route the operative takes (overlay)", K.F(K.MONO, 22), S.ORANGE, "lm", 0.4)
    y = head
    titles = ["CONNECTIONS 1-5  (the link type hints the step; the room and sticker always give the node type)",
              "CONNECTIONS 6-10", "BUILDING SILHOUETTES  (route columns and the mid row; widths, heights and depths vary)"]
    for s, t in zip(strips, titles):
        d.rectangle([0, y, W, y + bar], fill=(5, 13, 28, 255))
        K.text(out, (24, y + bar / 2), t, K.F(K.MONO, 22), (92, 225, 255), "lm", 0.5)
        out.alpha_composite(s, (0, y + bar))
        y += bar + s.height
    out.convert("RGB").save(os.path.join(ROOT, "architecture_sheet.png"))
    print("saved architecture_sheet.png", out.size)


def gif():
    fr, (zs, ze) = R.timeline()
    frames = [Image.open(os.path.join(SCR, "fr", "f%03d.png" % k)).convert("RGB").resize((960, 540), Image.LANCZOS)
              for k in range(zs, ze)]
    durs = [int(1000 / R.FPS)] * len(frames)
    durs[-1] = 250
    S.save_gif(frames, durs, os.path.join(ROOT, "zoom.gif"))
    print("zoom.gif", len(frames), "frames", sum(durs) / 1000.0, "s")


ENC = r'''
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]
src, n, out, fps = a[0], int(a[1]), a[2], int(a[3])
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
sc.render.fps = fps
sc.frame_start, sc.frame_end = 1, n
ed = sc.sequence_editor_create()
coll = ed.strips if hasattr(ed, "strips") else ed.sequences
files = sorted(f for f in os.listdir(src) if f.endswith(".png"))
st = coll.new_image("frames", os.path.join(src, files[0]), 1, 1)
for f in files[1:]:
    st.elements.append(f)
st.frame_final_duration = n
ims = sc.render.image_settings
try:
    ims.media_type = "VIDEO"
except Exception as e:
    print("media_type", e)
ims.file_format = "FFMPEG"
ff = sc.render.ffmpeg
ff.format = "MPEG4"
ff.codec = "H264"
try:
    ff.constant_rate_factor = "HIGH"
except Exception as e:
    print("crf", e)
ff.ffmpeg_preset = "GOOD"
sc.render.filepath = out
bpy.ops.render.render(animation=True)
print("ENCODED", out)
'''


def mp4():
    fr, _ = R.timeline()
    src = os.path.join(SCR, "fr")
    n = len([f for f in os.listdir(src) if f.endswith(".png")])
    assert n == len(fr), (n, len(fr))
    sp = os.path.join(SCR, "encode_bl.py")
    with open(sp, "w") as f:
        f.write(ENC)
    out = os.path.join(ROOT, "cam_run.mp4")
    log = os.path.join(SCR, "bl_encode.log")
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", sp, "--", src, str(n), out, str(R.FPS)],
                           stdout=f, stderr=subprocess.STDOUT)
    print("exit", r.returncode, "log", log, "exists", os.path.exists(out))


def compare():
    CW, CH, BAR = 960, 540, 44
    tiles = [(os.path.join(PARENT, "V3_mid.png"), "OLD V3  (2D crop-zoom, fixed 3/4 camera)", (230, 230, 240)),
             (os.path.join(ROOT, "D_mid.png"), "NEW  DECISION VIEW  (mid-run, camera centred)", (212, 255, 0)),
             (os.path.join(ROOT, "D_mid_hover.png"), "NEW  HOVER OPTION 2  (power cut 32 %, camera eases in)", (212, 255, 0)),
             (os.path.join(ROOT, "O_overview.png"), "NEW  OVERVIEW  (Z / scroll: the whole run)", (212, 255, 0))]
    img = Image.new("RGBA", (CW * 2, (CH + BAR) * 2), (8, 6, 14, 255))
    for n, (f, lab, col) in enumerate(tiles):
        im = Image.open(f).convert("RGB").resize((CW, CH), Image.LANCZOS)
        x, y = (n % 2) * CW, (n // 2) * (CH + BAR)
        img.paste(im, (x, y + BAR))
        d = ImageDraw.Draw(img)
        d.rectangle([x, y, x + CW, y + BAR], fill=(5, 13, 28))
        K.text(img, (x + 16, y + BAR / 2), lab, K.F(K.MONO, 20), col, "lm", 0.6)
    img.convert("RGB").save(os.path.join(ROOT, "compare_v3.jpg"), quality=90)
    print("saved compare_v3.jpg")


if __name__ == "__main__":
    {"sheet": sheet, "gif": gif, "mp4": mp4, "compare": compare}[sys.argv[1]]()
