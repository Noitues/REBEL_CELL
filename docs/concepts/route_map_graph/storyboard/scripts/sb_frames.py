"""Storyboard: assemble every animatic frame (plates from the Blender passes, finished with the r3 post, plus the 2D
layers of sb_ui.py) and the 1920 x 1080 boards.

python sb_frames.py frames [f0 f1] [-j N]  -> ../scratch/frames/f_0000.png ... (1280 x 720)
python sb_frames.py boards                 -> ../boards/NN_<beat>.png (1920 x 1080)
python sb_frames.py one <f>                -> ../scratch/one_<f>.png (1920 x 1080 check)
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
from PIL import Image  # noqa: E402

import post_aaa as PA  # noqa: E402
import look_preset as LP  # noqa: E402
import sb_cams as SB  # noqa: E402
import sb_ui as U  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
OUT = os.path.join(SCR, "frames")
BOARDS = os.path.join(ROOT, "boards")
VW, VH = 1280, 720
LODB = LP.PRESET["lod_bands"]
STD = {k: PA.LOOKS["real"][k] for k in ("bg_dim", "bg_desat", "exposure", "vol_k")}
STD["bg_emit_cut"] = 0.65
AERIAL_POST = dict(bg_emit_cut=0.0, bg_dim=1.0, bg_desat=0.15, exposure=2.0, vol_k=0.9)   # v2 review: a dark night city (median ~0.13, 32 % < 0.10)
BL = {"dive": "bl_dive2", "zoom": "bl_zoom", "hin": "bl_hin", "hmove": "bl_hmove", "ov": "bl_ov", "dec": "bl_dec",
      "h1": "bl_h1", "h2": "bl_h2"}
STATIC = ("ov", "dec", "h1", "h2")
XF = 5            # plate cross-fade frames at a segment change (moving <-> static), so no pop between render types


def band(z, key):
    a, b = LODB[key]
    return U.ease(U.clamp((z - a) / (b - a)))


def post_over(seg, zoom):
    """The grade lerps from the aerial city grade to the r3 street grade over the dive; the LOD bands drive the rain
    (small lights) and the puddle sharpness."""
    if seg not in ("hq", "dive"):
        return {}
    w = U.ease(U.clamp((zoom - 0.4) / 0.6))
    o = {k: AERIAL_POST[k] + (STD[k] - AERIAL_POST[k]) * w for k in AERIAL_POST}
    o["rain_k"] = band(zoom, "small_lights_on_at")
    o["puddle_blur"] = 3.0 * (1.0 - band(zoom, "puddles_sharp_at"))
    return o


def load(bl, name):
    return np.load(os.path.join(SCR, bl, name + ".npy")).astype(np.float32)


def rs(a, size, nearest=False):
    return PA.resize_f(a, size, Image.NEAREST if nearest else Image.BICUBIC)


# ---------------------------------------------------------------- the static holds: layers summed per frame
_ST = {}


def static_setup(seg, size):
    key = (seg, size)
    if key in _ST:
        return _ST[key]
    bl = BL[seg]
    nm = "S_" + seg
    base = load(bl, nm + "_combined")
    emit = load(bl, nm + "_emit")
    alb = load(bl, nm + "_albedo")
    z = load(bl, nm + "_z")[..., 0]
    if base.shape[1] != size[0]:
        base, emit, alb = rs(base, size), rs(emit, size), rs(alb, size)
        z = rs(z, size, True)
    vs = load(bl, nm + "_volstatic_combined")
    T_het = np.clip(load(bl, nm + "_trans_combined"), 1e-4, 1)
    bf = load(bl, nm + "_beamsfull_combined")
    vol = vs + rs(bf, (vs.shape[1], vs.shape[0]))          # the beams through every medium, held
    dyn_fr = sorted(int(p[1:5]) for p in os.listdir(os.path.join(SCR, bl)) if p.startswith("f") and p.endswith("_dyn_combined.npy"))
    d = dict(bl=bl, nm=nm, base=base, emit=emit, alb=alb, z=z, vol=vol, T_het=T_het, dyn_fr=dyn_fr, cache={})
    _ST[key] = d
    return d


def dyn_at(d, f, size):
    """The moving-emitter layer at frame f: rendered at 8 fps, linearly blended between the two nearest renders."""
    fr = d["dyn_fr"]
    lo = max([g for g in fr if g <= f] or [fr[0]])
    hi = min([g for g in fr if g >= f] or [fr[-1]])
    a = load(d["bl"], "f%04d_dyn_combined" % lo)
    if hi != lo:
        w = (f - lo) / float(hi - lo)
        a = a * (1 - w) + load(d["bl"], "f%04d_dyn_combined" % hi) * w
    return a if a.shape[1] == size[0] else rs(a, size)


def static_plate(seg, f, size=(VW, VH)):
    d = static_setup(seg, size)
    dyn = dyn_at(d, f, size)
    inp = dict(comb=np.maximum(d["base"] + dyn, 0), emit=np.maximum(d["emit"] + dyn, 0), alb=d["alb"], z=d["z"],
               vol=d["vol"], T_het=d["T_het"], cache=d["cache"])
    return PA.finish(os.path.join(SCR, d["bl"]), "real", shot=d["nm"], t=f / SB.FPS, inp=inp), d["nm"]


_KAPPA = {}


def kappa():
    """T_het ~ exp(-kappa * lum(in-scatter)): fitted once on the HQ frame (which has both passes); used where a moving
    frame has no transmittance pass (budget cut)."""
    if "k" not in _KAPPA:
        v = load("bl_hq2", "hq_vol_combined")
        t = np.clip(load("bl_hq2", "hq_trans_combined"), 1e-3, 1)
        t = rs(t, (v.shape[1], v.shape[0]))
        lv = PA.lum(v)
        m = lv > 0.004
        _KAPPA["k"] = float(np.median(-np.log(PA.lum(t)[m]) / lv[m])) if m.sum() > 100 else 8.0
    return _KAPPA["k"]


def warp_arr(arr, A_src, z, pose, size):
    """warp() for a float array (any channels) at `size` (w, h), z resized to it."""
    w_, h_ = size
    if arr.shape[1] != w_:
        arr = rs(arr, size)
    zz = z if z.shape[1] == w_ else rs(z, size, True)
    im = arr
    out, val = warp_f(im, A_src, zz, pose)
    return out, val


def vol_reproject(bl, f, pose, size):
    """The in-scatter of frame f from the two nearest frames that have a volume render, reprojected by their depth."""
    a, b = seg_bounds()["dive"]
    have = [g for g in range(a, b + 1) if os.path.exists(os.path.join(SCR, bl, "f%04d_vol_combined.npy" % g))]
    g0 = max([g for g in have if g <= f] or [have[0]])
    g1 = min([g for g in have if g >= f] or [have[-1]])
    outs = []
    for g in sorted(set((g0, g1))):
        A = json.load(open(os.path.join(SCR, bl, "anchors_f%04d.json" % g)))
        v = load(bl, "f%04d_vol_combined" % g)
        z = load(bl, "f%04d_z" % g)[..., 0]
        outs.append((g, warp_arr(v, A, z, pose, size)))
    if len(outs) == 1:
        o, val = outs[0][1]
        o, val = fill_holes(o, val, 6)
        return o
    w = (f - g0) / float(g1 - g0)
    (c0, v0), (c1, v1) = outs[0][1], outs[1][1]
    out = np.where((v0 & v1)[..., None], c0 * (1 - w) + c1 * w, np.where(v0[..., None], c0, c1))
    out, val = fill_holes(out, v0 | v1, 6)
    return out


def moving_plate(seg, f, zoom):
    bl = BL[seg]
    nm = "f%04d" % f
    has_vol = os.path.exists(os.path.join(SCR, bl, nm + "_vol_combined.npy"))
    has_tr = os.path.exists(os.path.join(SCR, bl, nm + "_trans_combined.npy"))
    if has_vol and has_tr:
        return PA.finish(os.path.join(SCR, bl), "real", shot=nm, t=f / SB.FPS, over=post_over(seg, zoom)), nm
    comb, emit, alb = load(bl, nm + "_combined"), load(bl, nm + "_emit"), load(bl, nm + "_albedo")
    z = load(bl, nm + "_z")[..., 0]
    pose = SB.cam_at(f)[1]
    vsz = (400, 225)
    vol = load(bl, nm + "_vol_combined") if has_vol else vol_reproject(bl, f, pose, vsz)
    T_het = np.exp(-kappa() * PA.gblur(PA.lum(np.maximum(vol, 0)), 1.5))[..., None].repeat(3, -1)
    T_het = np.clip(T_het, 0.25, 1.0)
    inp = dict(comb=comb, emit=emit, alb=alb, z=z, vol=vol, T_het=T_het, cache={})
    return PA.finish(os.path.join(SCR, bl), "real", shot=nm, t=f / SB.FPS, over=post_over(seg, zoom), inp=inp), nm


_HQ = {}


def hq_plate():
    if "p" not in _HQ:
        p = os.path.join(SCR, "hq_plate.png")
        if not os.path.exists(p):
            PA.finish(os.path.join(SCR, "bl_hq2"), "real", shot="hq", over=post_over("hq", 0.0)).save(p)
        _HQ["p"] = Image.open(p).convert("RGB")
    return _HQ["p"]


_PL = {}
_LY = None


def layout():
    global _LY
    if _LY is None:
        _LY = json.load(open(os.path.join(SCR, "layout.json")))
    return _LY


def anchors_from_pose(pose, bl):
    """The overlay anchors (rooms, edges, column tops at 1920) projected from the rig pose in python (the same camera
    model as Blender: track -Z / up Y, horizontal sensor fit, lens shift), for the frames between renders."""
    LY = layout()
    C = LY["const"]
    A = dict(rooms={}, edges=[], cols={})
    for i, n in LY["nodes"].items():
        x0, z0, x1, z1 = n["room"]
        y0 = n["dy"]
        y1 = y0 + C["DEPTH"] - 0.6
        A["rooms"][i] = dict(front=[pose.proj(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1))],
                             back=[pose.proj(p) for p in ((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1))])
    for e in LY["edges"]:
        A["edges"].append(dict(a=e["a"], b=e["b"], type=e["type"], pts=[pose.proj(q) for q in e["path"]], world=e["path"]))
    for l in range(8):
        x0, x1 = LY["cols"][str(l)]
        top = LY["storeys"][str(l)] * C["FLOOR_H"]
        A["cols"][str(l)] = [pose.proj((x0, LY["dy"][l], top)), pose.proj((x1, LY["dy"][l], top))]
    return A


def rendered(bl, f):
    return os.path.exists(os.path.join(SCR, bl, "f%04d_combined.npy" % f))


def warp(src_img, A_src, z, pose):
    """Forward-warp a finished plate to the camera `pose` by its depth (z-buffered splat). Returns (rgb, valid)."""
    a = np.asarray(src_img.convert("RGB"), np.float32)
    zz = z if z.shape == a.shape[:2] else rs(z, (a.shape[1], a.shape[0]), True)
    return warp_f(a, A_src, zz, pose)


def warp_f(a, A_src, z, pose):
    H_, W_ = z.shape
    o, dw = PA.cam_rays(A_src, W_, H_)
    zz = np.where(z > 5000, 2.0e4, z)
    P = o[None, None, :] + dw * zz[..., None]
    loc = np.array(pose.loc())
    fwd = np.array(pose.F) - loc
    fwd /= np.linalg.norm(fwd)
    r = np.cross(fwd, (0.0, 0.0, 1.0))
    r /= np.linalg.norm(r)
    u = np.cross(r, fwd)
    d = P - loc
    cx, cy, cz = d @ r, d @ u, d @ fwd
    k = 36.0 / pose.lens
    ok = cz > 0.5
    xs, ys = cx / np.maximum(cz, 1e-3), cy / np.maximum(cz, 1e-3)
    ii = np.round((xs / k - pose.sx + 0.5) * W_ - 0.5).astype(np.int64)
    jj = np.round((0.5 - (ys / k - pose.sy) * (W_ / H_)) * H_ - 0.5).astype(np.int64)
    ok &= (ii >= 0) & (ii < W_) & (jj >= 0) & (jj < H_)
    order = np.argsort(-cz[ok], kind="stable")          # far first, near last: the nearest wins
    src = a[ok][order]
    ti, tj = ii[ok][order], jj[ok][order]
    out = np.zeros_like(a)
    val = np.zeros(z.shape, bool)
    out[tj, ti] = src
    val[tj, ti] = True
    return out, val


def fill_holes(img, val, it=4):
    out, v = img.copy(), val.astype(np.float32)
    for _ in range(it):
        if v.min() > 0:
            break
        acc = np.zeros_like(out)
        cnt = np.zeros(v.shape, np.float32)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                acc += np.roll(np.roll(out * v[..., None], dy, 0), dx, 1)
                cnt += np.roll(np.roll(v, dy, 0), dx, 1)
        new = cnt > 0
        hole = (v == 0) & new
        out[hole] = acc[hole] / cnt[hole][:, None]
        v = np.maximum(v, hole.astype(np.float32))
    return out, v > 0


def move_param(f):
    seg, pose, ex = SB.cam_at(f)
    if seg in ("zoom", "dive"):
        return ex["u"]
    if seg in ("hin", "hmove"):
        return ex["k"]
    return None


def source(seg, g):
    """(plate, anchors, z) of a reprojection source frame g (a moving render or a held shot)."""
    sg = SB.cam_at(g)[0]
    p, A = plate_of(g)
    if sg in STATIC:
        z = static_setup(sg, (VW, VH))["z"]
    else:
        z = load(BL[sg], "f%04d_z" % g)[..., 0]
    return p, A, z


def warped_plate(seg, f):
    """A frame between renders: the two neighbouring sources (renders in this move, or the held shot at either end)
    forward-warped by depth to this frame's camera, blended by the move's own ease, holes from the other source, the
    last cracks filled from their neighbours. Light is linear, so the blend also carries the hover power cut."""
    bl = BL[seg]
    a, b = seg_bounds()[seg]
    cands = [(g, move_param(g)) for g in range(a, b + 1) if rendered(bl, g)]
    if a > 0 and SB.cam_at(a - 1)[0] in STATIC and SB.cam_at(a - 1)[0] != "hq":
        cands.append((a - 1, 0.0))
    if b + 1 < SB.NF and SB.cam_at(b + 1)[0] in STATIC:
        cands.append((b + 1, 1.0))
    cands.sort(key=lambda c: c[0])
    f0 = max(c for c in cands if c[0] < f)
    f1 = min(c for c in cands if c[0] > f)
    pose = SB.cam_at(f)[1]
    pf = move_param(f)
    w = (pf - f0[1]) / max(1e-6, (f1[1] - f0[1]))
    outs = []
    for g in (f0[0], f1[0]):
        p, A, z = source(seg, g)
        if p.size != (VW, VH):
            p = p.resize((VW, VH), Image.LANCZOS)
        outs.append(warp(p, A, z, pose))
    (c0, v0), (c1, v1) = outs
    both = v0 & v1
    out = np.where(both[..., None], c0 * (1 - w) + c1 * w, np.where(v0[..., None], c0, c1))
    out, val = fill_holes(out, v0 | v1)
    if not val.all():
        q = plate_of(f0[0] if w < 0.5 else f1[0])[0]
        q = np.asarray(q.convert("RGB").resize((VW, VH), Image.LANCZOS), np.float32)
        out = np.where(val[..., None], out, q)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def plate_of(f):
    """(1280 plate, overlay anchors) of frame f by its own segment (cached per process)."""
    if f in _PL:
        return _PL[f]
    seg, pose, ex = SB.cam_at(f)
    if seg in STATIC:
        p, nm = static_plate(seg, f)
        A = json.load(open(os.path.join(SCR, BL[seg], "anchors_%s.json" % nm)))
    elif rendered(BL[seg], f):
        p, nm = moving_plate(seg, f, SB.zoom_at(seg, pose))
        A = json.load(open(os.path.join(SCR, BL[seg], "anchors_%s.json" % nm)))
    else:
        p = warped_plate(seg, f)
        A = anchors_from_pose(pose, BL[seg])
    if len(_PL) > 12:
        _PL.clear()
    _PL[f] = (p, A)
    return _PL[f]


def seg_bounds():
    return {s: (a, b) for s, a, b in SB.segments()}


def blended_plate(f):
    """The plate with the cross-fade at a change between a moving and a static segment."""
    p, A = plate_of(f)
    seg = SB.cam_at(f)[0]
    sb = seg_bounds()
    a, _ = sb[seg]
    j = f - a
    if 0 <= j < XF and a > 0:
        prev = SB.cam_at(a - 1)[0]
        if prev != "hq" and (prev in STATIC) != (seg in STATIC):
            q, _ = plate_of(a - 1)
            w = 1.0 - (j + 1) / (XF + 1.0)
            p = Image.blend(p, q.resize(p.size, Image.LANCZOS) if q.size != p.size else q, w)
    return p, A


def up(img, size=(1920, 1080)):
    return img if img.size == size else img.resize(size, Image.LANCZOS)


# ---------------------------------------------------------------- the route UI state per frame
def route_state(f, A):
    t = f / SB.FPS
    seg, pose, ex = SB.cam_at(f)
    st = dict(zoom=1.0)
    T = SB.T

    def ctr(i):
        p = A["rooms"][i]["front"]
        return (sum(q[0] for q in p) / 4 + 6, sum(q[1] for q in p) / 4 + 2)
    if seg in ("ov", "dive"):
        st["zoom"] = 1.0
    elif seg == "zoom":
        st["zoom"] = 1.0 - ex["u"]
    else:
        st["zoom"] = 0.0
    if seg == "dec" and t >= T["b6"]:
        u = U.ease(U.phase(t, T["b6"], T["hover1"]))
        c = ctr(SB.OPT1)
        st["cursor"] = (1500 + (c[0] - 1500) * u, 860 + (c[1] - 860) * u)
    elif seg == "hin":
        st.update(hover=SB.OPT1, hover_k=ex["k"], cursor=ctr(SB.OPT1))
    elif seg == "h1":
        st.update(hover=SB.OPT1, hover_k=1.0, cursor=ctr(SB.OPT1))
    elif seg == "hmove":
        c1, c2 = ctr(SB.OPT1), ctr(SB.OPT2)
        k = ex["k"]
        st.update(hover=SB.OPT1 if k < 0.5 else SB.OPT2, hover_k=1.0,
                  cursor=(c1[0] + (c2[0] - c1[0]) * k, c1[1] + (c2[1] - c1[1]) * k))
    elif seg == "h2":
        st.update(hover=SB.OPT2, hover_k=1.0, cursor=ctr(SB.OPT2))
    return st


_RU = {}


def route_ui_cached(pl, A, st, key_nm):
    """The route UI is affine in the plate for a fixed state (grade, power cut, wax, stickers, panels), so for a static
    hold it is solved once on two flat plates and applied per frame as plate * m + b. The cursor is drawn after."""
    cur = st.pop("cursor", None)
    if key_nm is None:
        img = U.route_ui(pl, A, st)
    else:
        key = (key_nm, st.get("hover"), round(st.get("hover_k", 0.0), 3), round(st.get("zoom", 0.0), 3))
        stt, opts = U.G.states(U.SB.WALK)
        hv = st.get("hover")
        hk = st.get("hover_k", 0.0)
        pl = U.route_grade(pl, A, stt, U.SB.WALK[-1], hv if hk > 0 else None, hk, 1.0 - st.get("zoom", 0.0))
        if key not in _RU:
            o0 = np.asarray(U.route_overlay(Image.new("RGBA", (1920, 1080), (0, 0, 0, 255)), A, dict(st)).convert("RGB"),
                            np.float32) / 255
            o1 = np.asarray(U.route_overlay(Image.new("RGBA", (1920, 1080), (128, 128, 128, 255)), A, dict(st)).convert("RGB"),
                            np.float32) / 255
            if len(_RU) > 3:
                _RU.clear()
            _RU[key] = (np.clip((o1 - o0) / (128 / 255.0), 0, 2.5), o0)
        m, b = _RU[key]
        a = np.asarray(pl.convert("RGB"), np.float32) / 255
        img = Image.fromarray((np.clip(a * m + b, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    if cur:
        img = U.KT.cursor(img, *cur)
    return img


def compose(f, plate=None, A=None, size_out=(VW, VH)):
    """The full 1920 composite of frame f (then scaled to size_out)."""
    t = f / SB.FPS
    seg, pose, ex = SB.cam_at(f)
    T = SB.T
    if seg == "hq":
        img = U.hq_page(hq_plate(), t)
        if t >= T["b3"]:
            img = U.jack_in(img, t)
    else:
        if plate is None:
            plate, A = blended_plate(f)
        pl = up(plate).convert("RGBA")
        if seg == "dive":
            lt = t - T["dive"]
            if lt < 0.25:       # hand-over from the 1920 HQ render to the dive renders (the camera barely moves yet)
                pl = Image.blend(pl, hq_plate().resize(pl.size, Image.LANCZOS).convert("RGBA"), 1.0 - lt / 0.25)
            img = pl
            if lt < 0.3:
                ui = U.hq_page(up(plate), T["b3"] + 0.01, pose=pose)
                img = Image.blend(img, ui, 1.0 - U.ease(lt / 0.3))
            img = U.dive_over(img, t, pose)
            img = U.wall_bits(img, A, t)
        else:
            img = route_ui_cached(pl, A, route_state(f, A), ("S_" + seg) if seg in STATIC else None)
            if seg == "ov":
                a = U.ease(U.phase(t, T["b4"], T["b4"] + 0.35))
                if a < 1:
                    img = Image.blend(U.wall_bits(pl, A, t), img, a)
            img = U.wall_bits(img, A, t)
    img = U.title(img.convert("RGB"), t)
    return img if size_out == img.size else img.resize(size_out, Image.LANCZOS)


def _job(f):
    p = os.path.join(OUT, "f_%04d.png" % f)
    compose(f).save(p)
    return f


def frames(f0, f1, j):
    os.makedirs(OUT, exist_ok=True)
    todo = [f for f in range(f0, f1) if not os.path.exists(os.path.join(OUT, "f_%04d.png" % f))]
    # chunks of consecutive frames per worker, so the per-process caches (statics, neighbour plates) are reused
    chunks = [todo[i:i + 8] for i in range(0, len(todo), 8)]
    with Pool(j) as pool:
        for c in pool.imap_unordered(_chunk, chunks):
            print("done", c[0], "-", c[-1], flush=True)


def _chunk(fs):
    for f in fs:
        _job(f)
    return fs


# ---------------------------------------------------------------- boards (1920 x 1080)
def board_static(seg, f):
    p, nm = static_plate(seg, f, (1920, 1080))
    A = json.load(open(os.path.join(SCR, BL[seg], "anchors_%s.json" % nm)))
    return p, A


BOARD_LIST = [
    ("01_HQ_idle", SB.fr(1.0)),
    ("02_SELECT_hover_site_file", SB.fr(4.4)),
    ("03_SELECT_plan_and_jack_in", SB.fr(6.3)),
    ("04_JACKIN_terminal", SB.fr(8.45)),
    ("05_JACKIN_binary_rain_crt", SB.fr(9.72)),
    ("06_JACKIN_wheel_slap", SB.fr(10.3)),
    ("07_DIVE_mid", "dboard_a"),
    ("08_DIVE_walls_dissolve", "dboard_b"),
    ("09_OVERVIEW", SB.fr(14.2)),
    ("10_ZOOM_decision", SB.fr(16.3)),
    ("11_CHOOSE_hover_option_1", SB.fr(18.4)),
    ("12_CHOOSE_hover_option_2", SB.fr(21.0)),
]


def boards():
    os.makedirs(BOARDS, exist_ok=True)
    jobs = json.load(open(os.path.join(SCR, "job_dive_board_m.json")))["sb"]["frames"]
    for name, f in BOARD_LIST:
        if isinstance(f, str):
            fr = next(x for x in jobs if x["name"] == f)
            ff = fr["frame"]
            seg, pose, ex = SB.cam_at(ff)
            plate = PA.finish(os.path.join(SCR, "bl_diveboard2"), "real", shot=f, t=ff / SB.FPS,
                              over=post_over("dive", SB.zoom_at(seg, pose)))
            A = json.load(open(os.path.join(SCR, "bl_diveboard2", "anchors_%s.json" % f)))
            img = compose(ff, plate, A, (1920, 1080))
        else:
            seg = SB.cam_at(f)[0]
            if seg in STATIC:
                plate, A = board_static(seg, f)
                img = compose(f, plate, A, (1920, 1080))
            else:
                img = compose(f, size_out=(1920, 1080))
        img.save(os.path.join(BOARDS, name + ".png"))
        print("board", name, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    j = 5
    if "-j" in a:
        j = int(a[a.index("-j") + 1])
        a = a[:a.index("-j")] + a[a.index("-j") + 2:]
    if a[0] == "frames":
        f0 = int(a[1]) if len(a) > 1 else 0
        f1 = int(a[2]) if len(a) > 2 else SB.NF
        frames(f0, f1, j)
    elif a[0] == "boards":
        boards()
    elif a[0] == "one":
        compose(int(a[1]), size_out=(1920, 1080)).save(os.path.join(SCR, "one_%s.png" % a[1]))
