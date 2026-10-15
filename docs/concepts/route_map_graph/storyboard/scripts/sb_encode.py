"""Storyboard: encode and sheet.

python sb_encode.py mp4     -> ../storyboard.mp4 (1280 x 720, 24 fps, H.264 through Blender's sequencer, headless)
python sb_encode.py gif     -> ../storyboard.gif (960 x 540, 12 fps: every 2nd frame, one shared palette, delta frames)
python sb_encode.py sheet   -> ../storyboard_sheet.jpg (every board, captioned with its beat and time)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
ROOT = os.path.dirname(HERE)
FR = os.path.join(ROOT, "scratch", "frames3")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

VSE = r'''
import bpy, os, sys
fr, out, n = sys.argv[sys.argv.index("--") + 1:]
n = int(n)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
sc.render.fps, sc.render.fps_base = 24, 1.0
sc.frame_start, sc.frame_end = 1, n
se = sc.sequence_editor_create()
coll = se.strips if hasattr(se, "strips") else se.sequences
files = ["f_%04d.png" % i for i in range(n)]
st = coll.new_image("sb", os.path.join(fr, files[0]), 1, 1)
for f in files[1:]:
    st.elements.append(f)
st.frame_final_duration = n
try:
    sc.view_settings.view_transform = "Standard"
except TypeError:
    pass
im = sc.render.image_settings
for k, v in (("media_type", "VIDEO"), ("file_format", "FFMPEG")):
    try:
        setattr(im, k, v)
    except (AttributeError, TypeError):
        pass
ff = sc.render.ffmpeg
ff.format = "MPEG4"
ff.codec = "H264"
ff.constant_rate_factor = "HIGH"
ff.ffmpeg_preset = "GOOD"
ff.gopsize = 12
sc.render.filepath = out
bpy.ops.render.render(animation=True)
print("ENCODED", out)
'''


def mp4():
    import sb_cams as SB
    n = SB.NF
    sp = os.path.join(ROOT, "scratch", "vse_encode.py")
    with open(sp, "w") as f:
        f.write(VSE)
    out = os.path.join(ROOT, "storyboard.mp4")
    log = os.path.join(ROOT, "scratch", "vse_encode.log")
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", sp, "--", FR, out, str(n)], stdout=f,
                           stderr=subprocess.STDOUT)
    for p in os.listdir(ROOT):
        if p.startswith("storyboard") and p.endswith(".mp4") and p != "storyboard.mp4":
            os.replace(os.path.join(ROOT, p), out)
    print("mp4 exit", r.returncode, os.path.getsize(out) if os.path.exists(out) else "missing")


def gif(step=3, thr=14.0):
    import numpy as np
    from PIL import Image
    import sb_cams as SB
    idx_f = list(range(0, SB.NF, step))
    frames = [Image.open(os.path.join(FR, "f_%04d.png" % i)).convert("RGB").resize((960, 540), Image.LANCZOS) for i in idx_f]
    picks = [frames[int(k * (len(frames) - 1) / 9)] for k in range(10)]
    mosaic = Image.new("RGB", (960 * 5, 540 * 2))
    for k, im in enumerate(picks):
        mosaic.paste(im, (960 * (k % 5), 540 * (k // 5)))
    pal_im = mosaic.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pal = np.array(pal_im.getpalette()[:255 * 3], np.float32).reshape(255, 3)
    shown = None
    out = []
    for k, f in enumerate(frames):
        idx = np.asarray(f.quantize(palette=pal_im, dither=Image.Dither.NONE), np.uint8)
        if shown is None:
            shown, enc = idx.copy(), idx
        else:
            ch = np.abs(pal[idx] - pal[shown]).max(axis=-1) > thr
            enc = np.where(ch, idx, 255).astype(np.uint8)
            shown = np.where(ch, idx, shown)
        im = Image.fromarray(enc, "P")
        im.putpalette(list(pal.astype(np.uint8).ravel()) + [0, 0, 0])
        out.append(im)
    path = os.path.join(ROOT, "storyboard.gif")
    dur = [120 if k % 2 else 130 for k in range(len(out))]     # 8 fps (step 3 of 24): 125 ms average
    out[0].save(path, save_all=True, append_images=out[1:], duration=dur, loop=0, optimize=False, disposal=1,
                transparency=255)
    print("gif %.1f MB, %d frames" % (os.path.getsize(path) / 1e6, len(out)))


def sheet():
    from PIL import Image, ImageDraw
    import ui31 as K
    import sb_frames2 as SF
    import sb_cams as SB
    import sb_ui as U
    jobs = {}
    try:
        import json
        jobs = {x["name"]: x["frame"] for x in json.load(open(os.path.join(ROOT, "scratch", "job_dive_board_m.json")))["sb"]["frames"]}
    except (OSError, KeyError):
        pass
    tw, th, cap = 640, 360, 54
    cols = 3
    rows = (len(SF.BOARD_LIST) + cols - 1) // cols
    out = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + cap + 12) + 70), (10, 9, 14))
    d = ImageDraw.Draw(out)
    d.text((16, 22), "REBEL_CELL  //  NETRUN ENTRY STORYBOARD  (%.1f s animatic, 24 fps)" % (SB.NF / SB.FPS),
           font=K.F(K.MONO, 26), fill=(212, 255, 0))
    for k, (name, f) in enumerate(SF.BOARD_LIST):
        p = os.path.join(ROOT, "boards", name + ".png")
        if not os.path.exists(p):
            continue
        ff = jobs.get(f, f) if isinstance(f, str) else f
        t = ff / SB.FPS
        im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = 16 + (k % cols) * (tw + 16)
        y = 70 + (k // cols) * (th + cap + 12)
        out.paste(im, (x, y))
        d.text((x, y + th + 8), "%s   t = %.2f s  (frame %d)" % (name.replace("_", " "), t, ff), font=K.F(K.MONO, 18),
               fill=(230, 232, 240))
        d.text((x, y + th + 32), "beat %s" % U.beat_of(t), font=K.F(K.MONO, 15), fill=(150, 200, 220))
    out.save(os.path.join(ROOT, "storyboard_sheet.jpg"), quality=90)
    print("sheet saved")


if __name__ == "__main__":
    {"mp4": mp4, "gif": gif, "sheet": sheet}[sys.argv[1]]()
