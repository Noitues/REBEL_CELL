"""Storyboard v3: the FULL animatic on the one-city street (replaces v2). One scene, one city, one camera path:
HQ (mainline look) -> select -> jack in -> the dive (mainline -> AAA-2 by look_blend_by_zoom, the section lowering) ->
REVEAL (walls into bits left to right, links write on) -> MARK -> ZOOM -> CHOOSE, all on the derived street.

python sb_ocfull.py frames [-j N] | one <f> | boards | mp4 | gif | sheet
"""
import json
import math
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
import sb_cams as SB  # noqa: E402
import sb_frames as SF  # noqa: E402
import sb_frames2 as F2  # noqa: E402
import sb_frames3 as F3  # noqa: E402
import sb_mhq as MH  # noqa: E402
import sb_ocjobs as OJ  # noqa: E402
import sb_reveal as RV  # noqa: E402
import sb_ui as U  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
OUT = "D:/rc_scratch/storyboard/full_frames"     # heavy scratch on D: (coordinator rule)
BOARDS = os.path.join(ROOT, "boards")
K = U.K
D = OJ.derive()
C = OJ.OUTC
STREET_POST = dict(exposure=float(os.environ.get("OC_EXPOSURE", "0.84")))     # v3-r3: 1.1 -> 0.84 for the denser, lit fog (the near shots)
# v3-r3: the street grade by zoom. The OVERVIEW (and the dive that lands on it) sees the most fog and the lit ground bank,
# so it is graded down to EXP_OV; the near shots (decision, hovers) keep STREET_POST; the zoom move eases between them.
# Value-checked on the held shots (median 0.12-0.13, 35-39 % under 0.10)
EXP_OV = float(os.environ.get("OC_EXP_OV", "0.77"))


def exp_for(f):
    s_, c_, ex_ = seg(f)
    if s_ in ("ov", "dive"):
        return EXP_OV
    if s_ == "zoom":
        return EXP_OV + (STREET_POST["exposure"] - EXP_OV) * ex_.get("u", 0.0)
    return STREET_POST["exposure"]
SEG = {}


def seg(f):
    if f not in SEG:
        SEG[f] = OJ.full_at(f, D)
    return SEG[f]


def load(name):
    return np.load(os.path.join(C, name + ".npy")).astype(np.float32)


def anchors(name):
    return json.load(open(os.path.join(C, "anchors_%s.json" % name)))


def finish_name(name, t, over=None):
    o = dict(STREET_POST)
    o.update(over or {})
    return PA.finish(C, "real", shot=name, t=t, over=o)


# ---------------------------------------------------------------- held shots: a base render + the moving lanes (8 fps)
_HB = {}


def hold_plate(base, f, t, size=(1280, 720)):
    if base not in _HB:
        comb, emit = load(base + "_combined"), load(base + "_emit")
        alb, z = load(base + "_albedo"), load(base + "_z")[..., 0]
        _HB[base] = dict(comb=comb, emit=emit, alb=alb, z=z, cache={})
    d = _HB[base]
    s = seg(f)[0]
    fs = sorted(int(p[2:6]) for p in os.listdir(C) if p.startswith("Y_") and p.endswith("_combined.npy")
                and seg(int(p[2:6]))[0] == s)
    if fs:
        lo = max([g for g in fs if g <= f] or [fs[0]])
        hi = min([g for g in fs if g >= f] or [fs[-1]])
        dy = load("Y_%04d_combined" % lo)
        if hi != lo:
            w = (f - lo) / float(hi - lo)
            dy = dy * (1 - w) + load("Y_%04d_combined" % hi) * w
    else:
        dy = 0.0
    inp = dict(comb=np.maximum(d["comb"] + dy, 0), emit=np.maximum(d["emit"] + dy, 0), alb=d["alb"], z=d["z"],
               vol=np.zeros((90, 160, 3), np.float32), T_het=None, cache=d["cache"])
    o = dict(STREET_POST, exposure=exp_for(f))
    return PA.finish(C, "real", shot=base, t=t, inp=inp, over=o)


# ---------------------------------------------------------------- compose
def compose(f, size_out=(1280, 720)):
    t = f / SB.FPS
    s, c, ex = seg(f)
    T = SB.T
    if s == "hq":
        p, cam = MH.plate("m_hq", t, selected=t >= T["click"])
        img = MH.page(p, cam, t)
        if t >= T["b3"]:
            img = F3.jack_in_m(img, t, cam)
    elif s == "dive":
        img = dive(f, t, c)
    elif s == "ov":
        A = anchors("S_ov_open")
        tr = t - T["b4"]
        op = hold_plate("S_ov_open", f, t)
        if tr < RV.reveal_len():
            cl = hold_plate("S_ov_closed", f, t)
            pl = RV.reveal_plate(cl, op, A, tr)
        else:
            pl = op
        img = F2.street_overlay(pl.resize((1920, 1080), Image.LANCZOS).convert("RGBA"), A, f)
    elif s in ("dec", "h1", "h2"):
        nm = "S_" + s
        A = anchors(nm)
        pl = hold_plate(nm, f, t).resize((1920, 1080), Image.LANCZOS)
        img = SF.route_ui_cached(pl.convert("RGBA"), A, SF.route_state(f, A), nm)
    else:                                        # zoom, hin, hmove: every frame rendered
        nm = "g_%04d" % f
        A = anchors(nm)
        pl = finish_name(nm, t, dict(exposure=exp_for(f))).resize((1920, 1080), Image.LANCZOS)
        img = SF.route_ui_cached(pl.convert("RGBA"), A, SF.route_state(f, A), None)
    img = U.title(img.convert("RGB"), t)
    return img if img.size == size_out else img.resize(size_out, Image.LANCZOS)


def dive(f, t, c):
    T = SB.T
    z = OJ.zoom_of(c, D)
    w = OJ.look_w(z)
    lt = t - T["dive"]

    def mainline():
        p, cam = MH.plate("m_g_%04d" % f, t, selected=True, net_k=1.0 - U.ease(U.clamp(lt / 0.6)))
        img = p.convert("RGBA")
        if lt < 0.3:
            ph, camh = MH.plate("m_hq", t, selected=True)
            hq = MH.page(ph, camh, T["b3"] + 0.01)
            hq = K.over(hq, (2, 2, 8), Image.new("L", (1920, 1080), 255), 0.25)
            hq = F3.jack_in_m(hq, t, camh, 1.0 - U.ease(U.clamp(lt / 0.6)))
            img = F3.jack_in_m(img, t, cam, 1.0 - U.ease(U.clamp(lt / 0.6)))
            img = Image.blend(img.convert("RGBA"), hq.convert("RGBA"), 1.0 - U.ease(lt / 0.3))
        elif lt < 0.6:
            img = F3.jack_in_m(img, t, cam, 1.0 - U.ease(U.clamp(lt / 0.6)))
        return img.convert("RGB")

    def aaa():
        nm = "g_%04d" % f
        if not os.path.exists(os.path.join(C, nm + "_combined.npy")):
            have = sorted(int(p[2:6]) for p in os.listdir(C) if p.startswith("g_") and p.endswith("_combined.npy") and seg(int(p[2:6]))[0] == "dive")
            nm = "g_%04d" % max(g for g in have if g <= f)
        o = SF.post_over("dive", z)
        o["exposure"] = o.get("exposure", 2.0) + (EXP_OV - 2.4) * OJ.look_w(z)
        return PA.finish(C, "real", shot=nm, t=t, over=o).convert("RGB").resize((1920, 1080), Image.LANCZOS)
    if w <= 0.001:
        return mainline()
    if w >= 0.999:
        return aaa()
    return Image.blend(mainline(), aaa(), w)


def _chunk(fs):
    for f in fs:
        compose(f).save(os.path.join(OUT, "f_%04d.png" % f))
    return fs


def frames(f0, f1, j):
    os.makedirs(OUT, exist_ok=True)
    todo = [f for f in range(f0, f1) if not os.path.exists(os.path.join(OUT, "f_%04d.png" % f))]
    chunks = [todo[i:i + 6] for i in range(0, len(todo), 6)]
    with Pool(j) as pool:
        for c in pool.imap_unordered(_chunk, chunks):
            print("done", c[0], "-", c[-1], flush=True)


BOARD_LIST = [
    ("01_HQ_idle", SB.fr(1.0)), ("02_SELECT_hover_site_file", SB.fr(4.4)), ("03_SELECT_plan_and_jack_in", SB.fr(6.3)),
    ("04_JACKIN_terminal", SB.fr(8.45)), ("05_JACKIN_binary_rain", SB.fr(9.5)), ("06_JACKIN_crt_collapse", SB.fr(10.2)),
    ("07_DIVE_mid_one_city", SB.fr(SB.T["dive"] + 1.4)), ("08_DIVE_section_lowering", SB.fr(SB.T["dive"] + 2.2)),
    ("09_REVEAL_first_walls", SB.fr(SB.T["b4"] + 0.22)), ("10_REVEAL_trace", SB.fr(SB.T["b4"] + RV.link_start(4) + 0.13)),
    ("11_MARK_markers_target", SB.fr(SB.T["mark"] + RV.marks_len() + 0.3)), ("12_ZOOM_decision", SB.fr(SB.T["b6"] - 0.1)),
    ("13_CHOOSE_hover_option_1", SB.fr(SB.T["hover2"] - 0.3)), ("14_CHOOSE_hover_option_2", SB.fr(SB.T["end"] - 0.5)),
]


def boards():
    os.makedirs(BOARDS, exist_ok=True)
    for name, f in BOARD_LIST:
        compose(f, (1920, 1080)).save(os.path.join(BOARDS, name + ".png"))
        print("board", name, flush=True)


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
    sp = os.path.join(SCR, "full_vse.py")
    open(sp, "w").write(VSE)
    out = os.path.join(ROOT, "storyboard.mp4")
    with open(os.path.join(SCR, "full_vse.log"), "w") as fo:
        subprocess.run([OJ.BLENDER, "-b", "--factory-startup", "--python", sp, "--", OUT, out, str(SB.NF)], stdout=fo,
                       stderr=subprocess.STDOUT)
    for p in os.listdir(ROOT):
        if p.startswith("storyboard") and p.endswith(".mp4") and p not in ("storyboard.mp4", "storyboard_v3_dive.mp4") and not p.startswith("storyboard_v3"):
            os.replace(os.path.join(ROOT, p), out)
    print("mp4", os.path.getsize(out))


if __name__ == "__main__":
    a = sys.argv[1:]
    j = int(a[a.index("-j") + 1]) if "-j" in a else 4
    if a[0] == "frames":
        frames(int(a[1]) if len(a) > 1 and a[1] != "-j" else 0, int(a[2]) if len(a) > 2 and a[2] != "-j" else SB.NF, j)
    elif a[0] == "one":
        compose(int(a[1]), (1920, 1080)).save(os.path.join(SCR, "full_one_%s.png" % a[1]))
    elif a[0] == "boards":
        boards()
    elif a[0] == "mp4":
        mp4()
    elif a[0] in ("gif", "sheet"):
        import sb_encode as E
        E.FR = OUT                      # the full v3 frames
        import sb_frames2 as SF2
        SF2.BOARD_LIST = BOARD_LIST     # the v3 boards
        getattr(E, a[0])()
