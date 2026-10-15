"""Storyboard v3 frame assembly: the mainline HQ (beats 1-2 and the jack-in backdrop), the dive from the mainline world
into the AAA-2 world (the look_blend_by_zoom band behind a cloud veil), then sb_frames2 for the street (REVEAL, MARK),
the zoom and the choose.

python sb_frames3.py frames [f0 f1] [-j N]  -> ../scratch/frames3/f_0000.png ... (1280 x 720)
python sb_frames3.py boards                 -> ../boards/ (1920 x 1080)
python sb_frames3.py one <f>                -> ../scratch/one_<f>.png
"""
import json
import math
import os
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import sb_cams as SB  # noqa: E402
import sb_frames as SF  # noqa: E402
import sb_frames2 as F2  # noqa: E402
import sb_mhq as MH  # noqa: E402
import sb_ui as U  # noqa: E402
import post_aaa as PA  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
OUT = os.path.join(SCR, "frames3")
BOARDS = os.path.join(ROOT, "boards")
VW, VH = 1280, 720
K = U.K
KT = U.KT
_MP = {}
U.TERM_BOX = (1010, 170, 1810, 470)     # mainline layout: the terminal clear of the chosen link (the rain must read)


# ---------------------------------------------------------------- the mainline world
def m_plate(f):
    """The mainline city at frame f (HQ: the held HQ render; dive: its own perspective render), live (post40 at t)."""
    if f in _MP:
        return _MP[f]
    t = f / SB.FPS
    seg = SB.cam_at(f)[0]
    sel = t >= SB.T["click"]
    if seg == "hq":
        p, cam = MH.plate("m_hq", t, selected=sel)
    else:
        lt = t - SB.T["dive"]
        p, cam = MH.plate("m_f%04d" % f, t, selected=True, net_k=1.0 - U.ease(U.clamp(lt / 0.6)))
    if len(_MP) > 6:
        _MP.clear()
    _MP[f] = (p, cam)
    return _MP[f]


def jack_in_m(img, t, cam, k=1.0):
    """Beat 3 over the mainline page: dim, the binary rain on the chosen link (the border link to the Site), the
    terminal and its CRT collapse (straight into the dive: the wheel lens was dropped)."""
    T = SB.T
    if t < T["dive"]:
        img = K.over(img, (2, 2, 8), Image.new("L", (1920, 1080), 255), 0.25 * U.ease(U.phase(t, T["b3"], T["b3"] + 0.3)))
    lp = MH.link_poly(cam)
    if t >= T["rain"] and lp:
        img = U.link_rain(img, lp, t, T["rain"], k)
    if t < T["dive"]:
        img = U.terminal(img, t)
    return img


def cloud_veil(img, w, f):
    """The swap between the two worlds hides behind a cloud bank the camera drops through: soft drifting noise, densest
    mid-band, lit violet from below (the city glow), never fully opaque."""
    a = math.sin(math.pi * w) ** 1.3 * 0.62
    if a <= 0.01:
        return img
    H_, W_ = img.size[1], img.size[0]
    rng = np.random.default_rng(1700)
    k = 1.0 + 2.0 * w
    n = np.zeros((H_, W_), np.float32)
    for cell, amp in ((int(260 / k) + 40, 0.6), (int(110 / k) + 20, 0.3), (int(46 / k) + 10, 0.1)):
        g = rng.random((H_ // cell + 3, W_ // cell + 3)).astype(np.float32)
        im = Image.fromarray(g, "F").resize(((W_ // cell + 3) * cell, (H_ // cell + 3) * cell), Image.BICUBIC)
        arr = np.asarray(im, np.float32)
        oy = int((f * 9) % cell)
        n += amp * arr[oy:oy + H_, :W_]
    m = np.clip((n - 0.32) * 2.2, 0, 1) * a
    yy = np.linspace(0, 1, H_)[:, None]
    col = np.array([0.38, 0.33, 0.52], np.float32)[None, None, :] * (0.8 + 0.4 * yy[..., None])
    base = np.asarray(img.convert("RGB"), np.float32) / 255
    out = base * (1 - m[..., None]) + col * m[..., None]
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8))


def dive_plate(f):
    """The dive: the mainline render and / or the AAA-2 render (or its depth reprojection), crossed by the look blend."""
    s, pose, ex = SB.cam_at(f)
    z = SB.zoom_at(s, pose)
    w = SB.look_blend(z)
    pm = pa = None
    if SB.mainline_dive(f) and w < 0.999:
        pm = m_plate(f)[0].convert("RGB").resize((VW, VH), Image.LANCZOS)
    if SB.aaa_dive(f) and w > 0.001:
        p, A = F2.plate_of(f)
        pa = p.convert("RGB").resize((VW, VH), Image.LANCZOS)
    if pm is None:
        out = pa
    elif pa is None:
        out = pm
    else:
        out = Image.blend(pm, pa, w)
    return cloud_veil(out, w, f), w


# ---------------------------------------------------------------- compose
def compose(f, size_out=(VW, VH)):
    t = f / SB.FPS
    seg, pose, ex = SB.cam_at(f)
    T = SB.T
    if seg == "hq":
        p, cam = m_plate(f)
        img = MH.page(p, cam, t)
        if t >= T["b3"]:
            img = jack_in_m(img, t, cam)
    elif seg == "dive":
        pl, w = dive_plate(f)
        img = pl.resize((1920, 1080), Image.LANCZOS).convert("RGBA")
        lt = t - T["dive"]
        if lt < 0.6 and SB.mainline_dive(f):
            cam = m_plate(f)[1]
            if lt < 0.3:        # the HQ page furniture and the jack-in dim fade out as the camera starts to move
                ui = MH.page(img, cam, T["b3"] + 0.01)
                ui = K.over(ui, (2, 2, 8), Image.new("L", (1920, 1080), 255), 0.25)
                img = Image.blend(img, ui, 1.0 - U.ease(lt / 0.3))
            img = jack_in_m(img, t, cam, 1.0 - U.ease(U.clamp(lt / 0.6)))
            if lt < 0.3:        # hand-over from the orthographic HQ render (no jump while the long lens settles)
                ph, camh = MH.plate("m_hq", t, selected=True)
                hq = MH.page(ph, camh, T["b3"] + 0.01)
                hq = K.over(hq, (2, 2, 8), Image.new("L", (1920, 1080), 255), 0.25)
                hq = jack_in_m(hq, t, camh, 1.0 - U.ease(U.clamp(lt / 0.6)))
                img = Image.blend(img.convert("RGBA"), hq.convert("RGBA"), 1.0 - U.ease(lt / 0.3))
    else:
        return F2.compose(f, size_out=size_out)
    img = U.title(img.convert("RGB"), t)
    return img if size_out == img.size else img.resize(size_out, Image.LANCZOS)


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


# ---------------------------------------------------------------- boards
def boards():
    os.makedirs(BOARDS, exist_ok=True)
    for name, f in F2.BOARD_LIST:
        seg = SB.cam_at(f if not isinstance(f, str) else 0)[0]
        if isinstance(f, str):
            jobs = json.load(open(os.path.join(SCR, "job_dive_board_m.json")))["sb"]["frames"]
            fr = next(x for x in jobs if x["name"] == f)
            ff = fr["frame"]
            s, pose, ex = SB.cam_at(ff)
            z = SB.zoom_at(s, pose)
            w = SB.look_blend(z)
            pa = PA.finish(os.path.join(SCR, "bl_diveboard2"), "real", shot=f, t=ff / SB.FPS,
                           over=SF.post_over("dive", z)).convert("RGB").resize((1920, 1080), Image.LANCZOS)
            if f == "dboard_a" and w < 0.999:
                pm, _ = MH.plate("m_dboard_a", ff / SB.FPS, selected=True, net_k=0.0)
                pl = Image.blend(pm.convert("RGB").resize((1920, 1080), Image.LANCZOS), pa, w)
            else:
                pl = pa
            img = U.title(cloud_veil(pl, w, ff), ff / SB.FPS)
        elif seg == "hq":
            img = compose(f, size_out=(1920, 1080))
        else:
            img = None
            F2.boards_one = True
        if img is not None:
            img.save(os.path.join(BOARDS, name + ".png"))
            print("board", name, flush=True)
    # the street, zoom and choose boards (sb_frames2, AAA-2)
    keep = F2.BOARD_LIST
    F2.BOARD_LIST = [b for b in keep if not isinstance(b[1], str) and SB.cam_at(b[1])[0] not in ("hq", "dive")]
    F2.boards()
    F2.BOARD_LIST = keep


if __name__ == "__main__":
    a = sys.argv[1:]
    j = 4
    if "-j" in a:
        j = int(a[a.index("-j") + 1])
        a = a[:a.index("-j")] + a[a.index("-j") + 2:]
    if a[0] == "frames":
        frames(int(a[1]) if len(a) > 1 else 0, int(a[2]) if len(a) > 2 else SB.NF, j)
    elif a[0] == "boards":
        boards()
    elif a[0] == "one":
        compose(int(a[1]), size_out=(1920, 1080)).save(os.path.join(SCR, "one_%s.png" % a[1]))
