"""r3 idle loop: encode the PNG frames.

python encode_loop.py mp4   -> ../idle_loop.mp4   (Blender's built-in FFmpeg through the sequencer, headless)
python encode_loop.py gif   -> ../idle_loop.gif   (960 x 540, one shared palette, so no palette flicker)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FR = os.path.join(ROOT, "scratch", "loop", "frames")
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
files = ["f_%03d.png" % i for i in range(n)]
st = coll.new_image("loop", os.path.join(fr, files[0]), 1, 1)
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


def mp4(n=96):
    sp = os.path.join(ROOT, "scratch", "vse_encode.py")
    with open(sp, "w") as f:
        f.write(VSE)
    out = os.path.join(ROOT, "idle_loop.mp4")
    log = os.path.join(ROOT, "scratch", "vse_encode.log")
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", sp, "--", FR, out, str(n)], stdout=f,
                           stderr=subprocess.STDOUT)
    # Blender appends the frame range to the name when the path has no extension handling; normalise
    cands = [p for p in os.listdir(ROOT) if p.startswith("idle_loop") and p.endswith(".mp4")]
    for p in cands:
        if p != "idle_loop.mp4":
            os.replace(os.path.join(ROOT, p), out)
    print("mp4 exit", r.returncode, os.path.getsize(out) if os.path.exists(out) else "missing")


def gif(n=96, dither=True):
    from PIL import Image
    frames = [Image.open(os.path.join(FR, "f_%03d.png" % i)).convert("RGB").resize((960, 540), Image.LANCZOS)
              for i in range(n)]
    mosaic = Image.new("RGB", (960 * 4, 540))
    for k, i in enumerate((0, n // 4, n // 2, 3 * n // 4)):
        mosaic.paste(frames[i], (960 * k, 0))
    pal = mosaic.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    dm = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    q = [f.quantize(palette=pal, dither=dm) for f in frames]
    out = os.path.join(ROOT, "idle_loop.gif")
    q[0].save(out, save_all=True, append_images=q[1:], duration=42, loop=0, optimize=False, disposal=1)
    print("gif", os.path.getsize(out) / 1e6, "MB")


def gif_delta(n=96, thr=10.0, dither=False):
    """A GIF with inter-frame transparency: 255 shared colours + 1 transparent index; each frame stores only the pixels
    whose colour moved more than thr (0-255 RGB distance) from what is on screen, so the static city costs nothing.
    Frame 0 is stored whole, so the loop restarts clean."""
    import numpy as np
    from PIL import Image
    frames = [Image.open(os.path.join(FR, "f_%03d.png" % i)).convert("RGB").resize((960, 540), Image.LANCZOS)
              for i in range(n)]
    mosaic = Image.new("RGB", (960 * 4, 540))
    for k, i in enumerate((0, n // 4, n // 2, 3 * n // 4)):
        mosaic.paste(frames[i], (960 * k, 0))
    pal_im = mosaic.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pal = np.array(pal_im.getpalette()[:255 * 3], np.float32).reshape(255, 3)
    dm = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    shown = None
    out = []
    for k, f in enumerate(frames):
        idx = np.asarray(f.quantize(palette=pal_im, dither=dm), np.uint8)
        if shown is None:
            shown = idx.copy()
            enc = idx
        else:
            d = np.abs(pal[idx] - pal[shown]).max(axis=-1)
            ch = d > thr
            enc = np.where(ch, idx, 255).astype(np.uint8)
            shown = np.where(ch, idx, shown)
        im = Image.fromarray(enc, "P")
        im.putpalette(list(pal.astype(np.uint8).ravel()) + [0, 0, 0])
        out.append(im)
    path = os.path.join(ROOT, "idle_loop.gif")
    # GIF delays are in 1/100 s: 80 frames of 40 ms + 16 of 50 ms = exactly 4.00 s (24 fps on average)
    dur = [50 if (k % 6) == 5 else 40 for k in range(n)]
    out[0].save(path, save_all=True, append_images=out[1:], duration=dur, loop=0, optimize=False, disposal=1,
                transparency=255)
    print("gif (delta, thr %g) %.1f MB" % (thr, os.path.getsize(path) / 1e6))


if __name__ == "__main__":
    if sys.argv[1] == "gifd":
        gif_delta(thr=float(sys.argv[2]) if len(sys.argv) > 2 else 10.0)
        sys.exit(0)
    if sys.argv[1] == "mp4":
        mp4()
    else:
        gif(dither=(len(sys.argv) < 3 or sys.argv[2] != "nodither"))
