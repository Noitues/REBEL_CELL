"""Storyboard v3 proof (one continuous city): assemble the dive video and its boards.

Every frame is ONE scene seen by ONE camera. The mainline look (the kit's Eevee passes + its post) and the AAA-2 look
(Cycles on the same objects + the r3 post) are two shadings of identical geometry from identical cameras; the frame is
their mix by look_blend_by_zoom (a material / lighting / fog blend, never a geometry swap; no veil).

python sb_ocframes.py frames [-j N]   -> ../scratch/oc_frames/f_0000.png
python sb_ocframes.py one <k>          -> ../scratch/oc_one_<k>.png (1920)
python sb_ocframes.py boards           -> ../boards_v3/
python sb_ocframes.py mp4              -> ../storyboard_v3_dive.mp4
"""
import os
import subprocess
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import post_aaa as PA  # noqa: E402
import sb_frames as SF  # noqa: E402
import sb_frames3 as F3  # noqa: E402
import sb_mhq as MH  # noqa: E402
import sb_ocjobs as OJ  # noqa: E402
import sb_ui as U  # noqa: E402
import sb_cams as SB  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
OUT = os.path.join(SCR, "oc_frames")
BOARDS = os.path.join(ROOT, "boards_v3")
K = U.K
D = OJ.derive()
FR = {f: (t, s, u) for f, t, s, u in OJ.frames()}


def mainline(f, t, u, size=(1920, 1080)):
    lt = t - OJ.T_DIVE
    p, cam = MH.plate("m_%04d" % f if u > 0 else "m_hq", t, selected=True, net_k=1.0 - U.ease(U.clamp(lt / 0.6)))
    img = p.convert("RGBA")
    if lt < 0.3:
        ui = MH.page(img, cam, SB.T["b3"] + 0.01)
        ui = K.over(ui, (2, 2, 8), Image.new("L", (1920, 1080), 255), 0.25)
        img = Image.blend(img, ui, 1.0 - U.ease(lt / 0.3))
        ph, camh = MH.plate("m_hq", t, selected=True)
        hq = MH.page(ph, camh, SB.T["b3"] + 0.01)
        hq = K.over(hq, (2, 2, 8), Image.new("L", (1920, 1080), 255), 0.25)
        hq = F3.jack_in_m(hq, t, camh, 1.0 - U.ease(U.clamp(lt / 0.6)))
        img = F3.jack_in_m(img, t, cam, 1.0 - U.ease(U.clamp(lt / 0.6)))
        img = Image.blend(img.convert("RGBA"), hq.convert("RGBA"), 1.0 - U.ease(lt / 0.3))
    elif lt < 0.6:
        img = F3.jack_in_m(img, t, cam, 1.0 - U.ease(U.clamp(lt / 0.6)))
    return img.convert("RGB")


def aaa(f, t, z, name=None):
    nm = name or "c_%04d" % f
    if name is None and not os.path.exists(os.path.join(OJ.OUTC, nm + "_combined.npy")):
        # the held end pose (the camera has stopped): the last render; the post's rain still falls with t
        have = sorted(int(p[2:6]) for p in os.listdir(OJ.OUTC) if p.startswith("c_") and p.endswith("_combined.npy"))
        nm = "c_%04d" % max(g for g in have if g <= f)
    over = SF.post_over("dive", z)
    return PA.finish(OJ.OUTC, "real", shot=nm, t=t, over=over).convert("RGB").resize((1920, 1080), Image.LANCZOS)


def compose(f, size_out=(1280, 720)):
    t, s, u = FR[f]
    if s == "hq":
        p, cam = MH.plate("m_hq", t, selected=t >= SB.T["click"])
        img = MH.page(p, cam, t)
        if t >= SB.T["b3"]:
            img = F3.jack_in_m(img, t, cam)
    else:
        c = OJ.pose_at(u, D)
        z = OJ.zoom_of(c, D)
        w = OJ.look_w(z)
        if w <= 0.001:
            img = mainline(f, t, u)
        elif w >= 0.999:
            img = aaa(f, t, z)
        else:
            img = Image.blend(mainline(f, t, u), aaa(f, t, z), w)
    img = U.title(img.convert("RGB"), t)
    return img if img.size == size_out else img.resize(size_out, Image.LANCZOS)


def _chunk(fs):
    for f in fs:
        compose(f).save(os.path.join(OUT, "f_%04d.png" % f))
    return fs


def frames(j):
    os.makedirs(OUT, exist_ok=True)
    todo = [f for f in sorted(FR) if not os.path.exists(os.path.join(OUT, "f_%04d.png" % f))]
    chunks = [todo[i:i + 6] for i in range(0, len(todo), 6)]
    with Pool(j) as pool:
        for c in pool.imap_unordered(_chunk, chunks):
            print("done", c[0], "-", c[-1], flush=True)


def boards():
    os.makedirs(BOARDS, exist_ok=True)
    f_hq = 0
    compose(f_hq, (1920, 1080)).save(os.path.join(BOARDS, "01_HQ_select.png"))
    # mid-dive: the frame in the middle of the look band, from the 1920 renders of both looks
    fm = max((f for f in FR if FR[f][1] == "dive" and OJ.look_w(OJ.zoom_of(OJ.pose_at(FR[f][2], D), D)) <= 0.5), default=None)
    compose(fm, (1920, 1080)).save(os.path.join(BOARDS, "02_DIVE_mid_one_city.png"))
    t = OJ.T_END - 0.1
    st = aaa(None, t, 1.0, "b_street")
    U.title(st, t).save(os.path.join(BOARDS, "03_STREET_reveal_start.png"))
    rm = aaa(None, t, 1.0, "b_rooms")
    U.title(rm, t).save(os.path.join(BOARDS, "04_STREET_rooms_derived_preview.png"))
    print("boards ok")


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
sc.view_settings.view_transform = "Standard"
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
'''


def mp4():
    sp = os.path.join(SCR, "oc_vse.py")
    open(sp, "w").write(VSE)
    out = os.path.join(ROOT, "storyboard_v3_dive.mp4")
    with open(os.path.join(SCR, "oc_vse.log"), "w") as f:
        subprocess.run([OJ.BLENDER, "-b", "--factory-startup", "--python", sp, "--", OUT, out, str(len(FR))], stdout=f,
                       stderr=subprocess.STDOUT)
    for p in os.listdir(ROOT):
        if p.startswith("storyboard_v3_dive") and p.endswith(".mp4") and p != "storyboard_v3_dive.mp4":
            os.replace(os.path.join(ROOT, p), out)
    print("mp4", os.path.getsize(out) if os.path.exists(out) else "missing")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "frames":
        frames(int(a[a.index("-j") + 1]) if "-j" in a else 4)
    elif a[0] == "one":
        compose(int(a[1]), (1920, 1080)).save(os.path.join(SCR, "oc_one_%s.png" % a[1]))
    elif a[0] == "boards":
        boards()
    elif a[0] == "mp4":
        mp4()
