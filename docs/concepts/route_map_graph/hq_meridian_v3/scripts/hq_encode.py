"""HQ kit (from HQ Halcyon): encode composed frames (r3 encode_loop.py, Blender's built-in FFmpeg through the sequencer, headless).

python hq_encode.py orbit|reveal      -> ../H_orbit_run.mp4 / ../H_reveal.mp4 (1280 x 720, 24 fps) + .gif (960 x 540)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
SCR = os.path.join(ROOT, "scratch")
import hq_preset as HP  # noqa: E402
BIG = HP.PRESET["hq"]["out_big"]
os.makedirs(BIG, exist_ok=True)
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
NAMES = {"reveal": HP.PRESET["hq"].get("reveal_name", "H_reveal") + HP.PRESET["hq"].get("suffix", "")}  # HQ_REV_V2

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
files = ["f%03d.png" % i for i in range(n)]
st = coll.new_image("clip", os.path.join(fr, files[0]), 1, 1)
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


def mp4(kind):
    fr = os.path.join(BIG, "fr_" + kind)
    n = len([f for f in os.listdir(fr) if f.startswith("f") and f.endswith(".png")])
    sp = os.path.join(SCR, "vse_encode.py")
    with open(sp, "w") as f:
        f.write(VSE)
    name = NAMES[kind]
    out = os.path.join(ROOT, name + ".mp4")
    log = os.path.join(SCR, "vse_%s.log" % kind)
    with open(log, "w") as f:
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python", sp, "--", fr, out, str(n)], stdout=f,
                           stderr=subprocess.STDOUT)
    for p in os.listdir(ROOT):
        if p.startswith(name) and p.endswith(".mp4") and p != name + ".mp4":
            os.replace(os.path.join(ROOT, p), out)
    print("mp4", kind, n, "frames, exit", r.returncode, os.path.getsize(out) if os.path.exists(out) else "missing")


def gif(kind):
    from PIL import Image
    fr = os.path.join(BIG, "fr_" + kind)
    files = sorted(f for f in os.listdir(fr) if f.startswith("f") and f.endswith(".png"))[::2]   # 12 fps: size
    frames = [Image.open(os.path.join(fr, f)).convert("RGB").resize((960, 540), Image.LANCZOS) for f in files]
    n = len(frames)
    mosaic = Image.new("RGB", (960 * 4, 540))
    for k, i in enumerate((0, n // 4, n // 2, 3 * n // 4)):
        mosaic.paste(frames[i], (960 * k, 0))
    pal = mosaic.quantize(colors=160, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]           # no dither: the grain already dithers
    out = os.path.join(ROOT, NAMES[kind] + ".gif")
    dur = [83 if k % 3 else 84 for k in range(n)]                    # ~83 ms: 12 fps (every 2nd frame)
    q[0].save(out, save_all=True, append_images=q[1:], duration=dur, loop=0, optimize=False, disposal=1)
    print("gif", kind, "%.1f MB" % (os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    k = sys.argv[1]
    mp4(k)
    gif(k)
