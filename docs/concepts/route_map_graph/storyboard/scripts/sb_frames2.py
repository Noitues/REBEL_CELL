"""Storyboard v2 frame assembly (the designer's re-plan). Reuses sb_frames.py (post, depth reprojection, route UI) and
adds the live held shots, the street-level reveal on the r3 idle loop, and the v2 boards.

City-alive rule: every held shot is a base render plus, per frame, the moving-emitter layer (streak lanes, globe), the
beams through the haze (fitted to the beams through every medium), the flicker layers (signs, strobes, windows,
billboard swap, holo scan roll and glitches) with the r3 loop's seeded tables (sb_live.py), the 2D fog drift and the
falling rain. Everything is indexed by the video frame (f % 96), so every shot is in phase.

python sb_frames2.py frames [f0 f1] [-j N]  -> ../scratch/frames/f_0000.png ... (1280 x 720)
python sb_frames2.py boards                 -> ../boards/ (1920 x 1080)
python sb_frames2.py one <f>                -> ../scratch/one_<f>.png (1920 x 1080)
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
import sb_cams as SB  # noqa: E402
import sb_frames as SF  # noqa: E402
import sb_live as LV  # noqa: E402
import sb_reveal as RV  # noqa: E402
import sb_ui as U  # noqa: E402

ROOT = os.path.dirname(HERE)
SCR = os.path.join(ROOT, "scratch")
OUT = os.path.join(SCR, "frames2")
BOARDS = os.path.join(ROOT, "boards")
VW, VH = 1280, 720
BL = {"hq": "bl_hq3", "dive": "bl_dive2", "ov": "loop", "zoom": "D:/rc_scratch/storyboard/bl_zoom", "hin": "bl_hin", "hmove": "bl_hmove",
      "dec": "bl_dec", "h1": "bl_h1", "h2": "D:/rc_scratch/storyboard/bl_h2"}
SF.BL.update(BL)
HOLDS = ("hq", "dec", "h1", "h2")
STATIC = ("hq", "ov", "dec", "h1", "h2")
SF.STATIC = STATIC
DRIFT_PX = (13.0, 3.0)        # the r3 loop's fog drift (px at 640 over 96 frames: the top rows, fading below 55 %)


def load(bl, name):
    return np.load(os.path.join(SCR, bl, name + ".npy")).astype(np.float32)


def exists(bl, name):
    return os.path.exists(os.path.join(SCR, bl, name + ".npy"))


def rs(a, size, nearest=False):
    if a.shape[1] == size[0]:
        return a
    return PA.resize_f(a, size, Image.NEAREST if nearest else Image.BICUBIC)


def shift_rows(a, amt):
    h, w = a.shape[:2]
    xs = np.arange(w, dtype=np.float32)[None, :] - amt[:, None]
    x0 = np.clip(np.floor(xs).astype(np.int32), 0, w - 1)
    x1 = np.clip(x0 + 1, 0, w - 1)
    fr = (xs - np.floor(xs))
    rows = np.arange(h)[:, None]
    if a.ndim == 3:
        fr = fr[..., None]
    return a[rows, x0] * (1 - fr) + a[rows, x1] * fr


def drift(a, f, uniform=False):
    """The r3 loop-safe fog drift, (1 - p) S(s p) + p S(s (p - 1)), p = (f % 96) / 96. Street: the top rows drift,
    nothing below 55 % (the street cones and god rays stay put); aerial (uniform): the whole bank field drifts."""
    h, w = a.shape[:2]
    p = (f % LV.NF) / float(LV.NF)
    k = w / 640.0
    yy = np.arange(h) / max(1, h - 1)
    if uniform:
        s = np.full(h, DRIFT_PX[0] * 0.8 * k)
    else:
        s = (DRIFT_PX[1] + (DRIFT_PX[0] - DRIFT_PX[1]) * np.clip(1.0 - yy / 0.55, 0, 1)) * k
    return (1 - p) * shift_rows(a, s * p) + p * shift_rows(a, s * (p - 1))


def layer_box(L):
    m = PA.lum(L) > 0.01
    if not m.any():
        return None
    ys, xs = np.where(m)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def holo_mod(L, g, f):
    """Scan-band roll and the 1-2 frame glitch of a holo ad (r3 post_loop), boxed by the layer itself."""
    b = layer_box(L)
    if b is None:
        return L
    x0, y0, x1, y1 = b
    H_, W_ = L.shape[:2]
    out = L.copy()
    yy = (np.arange(H_, dtype=np.float32) - y0) / max(1, y1 - y0)
    ph = ((f % LV.NF) / LV.NF) * LV.HOLO_ROLL.get(g, 1)
    d = ((yy - ph) % 1.0) - 0.5
    out = out * (0.84 + 0.55 * np.exp(-(d / 0.09) ** 2))[:, None, None]
    if (f % LV.NF) in LV.HOLO_GLITCH.get(g, ()):
        r = np.random.default_rng(9800 + (f % LV.NF) + len(g))
        reg = out[y0:y1, x0:x1].copy()
        for s_ in range(5):
            a, b2 = s_ * reg.shape[0] // 5, (s_ + 1) * reg.shape[0] // 5
            reg[a:b2] = np.roll(reg[a:b2], int(r.integers(-9, 10)), axis=1)
        reg[..., 0] = np.roll(reg[..., 0], 3, axis=1)
        reg[..., 2] = np.roll(reg[..., 2], -3, axis=1)
        out[y0:y1, x0:x1] = reg * 1.25
    return out


def bill_glitch(La, Lb, f):
    b = layer_box(La + Lb)
    out = np.zeros_like(La)
    if b is None:
        return out
    x0, y0, x1, y1 = b
    r = np.random.default_rng(9900 + (f % LV.NF))
    mix = 0.35 if (f % LV.NF) in (46, 94) else 0.7
    reg = La[y0:y1, x0:x1] * (1 - mix) + Lb[y0:y1, x0:x1] * mix
    for s_ in range(7):
        a, b2 = s_ * reg.shape[0] // 7, (s_ + 1) * reg.shape[0] // 7
        reg[a:b2] = np.roll(reg[a:b2], int(r.integers(-12, 13)), axis=1)
    reg[..., 0] = np.roll(reg[..., 0], 4, axis=1)
    reg[..., 2] = np.roll(reg[..., 2], -4, axis=1)
    out[y0:y1, x0:x1] = reg * 1.15
    return out


def flicker(comb, emit, layers, f):
    """Add every flicker layer at its gain for frame f (the base holds each at rest = gain 1; bill_b is off at rest)."""
    for g, L in layers.items():
        if g.startswith("holo_"):
            Lm = holo_mod(L, g, f)
            comb = comb + Lm - L
            emit = emit + Lm - L
            continue
        k = LV.gain(g, f) - (0.0 if g == "bill_b" else 1.0)
        if k != 0.0:
            comb = comb + k * L
            emit = emit + k * L
    if (f % LV.NF) in LV.BILL_GLITCH and "bill_a" in layers and "bill_b" in layers:
        gl = bill_glitch(layers["bill_a"], layers["bill_b"], f)
        comb, emit = comb + gl, emit + gl
    return comb, emit


# ---------------------------------------------------------------- held shots
_HS = {}


def hold_setup(seg, size):
    key = (seg, size)
    if key in _HS:
        return _HS[key]
    bl = BL[seg]
    if seg == "ov":
        nm, shot = "base", "O_overview"
        base, emit = load(bl, "base_combined"), load(bl, "base_emit")
        alb, z = load(bl, "base_albedo"), load(bl, "base_z")[..., 0]
        cb, ce = load(bl, "S_ovc_combined"), load(bl, "S_ovc_emit")
        vs = load(bl, "S_street_volstatic_combined")
        bf = load(bl, "S_street_beamsfull_combined")
        T_het = np.clip(load(bl, "static_trans_combined"), 1e-4, 1)
        lay = {p[6:-13]: load(bl, p[:-4]) for p in os.listdir(os.path.join(SCR, bl))
               if p.startswith("layer_") and p.endswith("_combined.npy")}
        beams = lambda f: "beams_%03d_combined" % (f % LV.NF)      # noqa: E731
        dyn = lambda f: "dyn_%03d_combined" % (f % LV.NF)          # noqa: E731
        dyn_fr = None
    else:
        nm = shot = "S_" + seg
        base, emit = load(bl, nm + "_combined"), load(bl, nm + "_emit")
        alb, z = load(bl, nm + "_albedo"), load(bl, nm + "_z")[..., 0]
        cb = ce = None
        vs = load(bl, nm + "_volstatic_combined")
        bf = load(bl, nm + "_beamsfull_combined")
        T_het = np.clip(load(bl, nm + "_trans_combined"), 1e-4, 1)
        pre = nm + "_layer_"
        lay = {p[len(pre):-13]: load(bl, p[:-4]) for p in os.listdir(os.path.join(SCR, bl))
               if p.startswith(pre) and p.endswith("_combined.npy")}
        beams = lambda f: "f%04d_beams_combined" % f              # noqa: E731
        dyn = lambda f: "f%04d_dyn_combined" % f                  # noqa: E731
        dyn_fr = sorted(int(p[1:5]) for p in os.listdir(os.path.join(SCR, bl)) if p.startswith("f") and p.endswith("_dyn_combined.npy"))
    if base.shape[1] != size[0]:
        base, emit, alb = rs(base, size), rs(emit, size), rs(alb, size)
        z = rs(z, size, True)
        if cb is not None:
            cb, ce = rs(cb, size), rs(ce, size)
    lay = {g: rs(L, size) for g, L in lay.items()}
    tau = -np.log(T_het)
    # the beam fit: beams_full ~ s b + k b tau (r3), on the first per-frame beams render
    bfr = sorted(int(p[1:5]) for p in os.listdir(os.path.join(SCR, bl)) if p.startswith("f") and p.endswith("_beams_combined.npy")) \
        if seg != "ov" else list(range(LV.NF))
    b0 = load(bl, beams(bfr[0])) if bfr else None
    sk = np.array([1.0, 0.0])
    if b0 is not None:
        b0r = rs(b0, (bf.shape[1], bf.shape[0]))
        tl = rs(tau, (bf.shape[1], bf.shape[0])).mean(-1)
        m = PA.lum(b0r) > 0.004
        if m.sum() > 50:
            X = np.stack([PA.lum(b0r)[m], (PA.lum(b0r) * tl)[m]], -1)
            sk = np.clip(np.linalg.lstsq(X, PA.lum(bf)[m], rcond=None)[0], [0.3, 0.0], [3.0, 40.0])
    d = dict(bl=bl, nm=nm, shot=shot, base=base, emit=emit, alb=alb, z=z, cb=cb, ce=ce, vs=vs, bf=bf, tau=tau,
             lay=lay, beams=beams, dyn=dyn, dyn_fr=dyn_fr, bfr=bfr, sk=sk, cache={}, cache_c={})
    _HS[key] = d
    return d


def _interp(d, namef, frames, f, size):
    """A per-frame layer rendered at a reduced rate, blended between the two nearest renders."""
    if frames is None:
        return rs(load(d["bl"], namef(f)), size)
    lo = max([g for g in frames if g <= f] or [frames[0]])
    hi = min([g for g in frames if g >= f] or [frames[-1]])
    a = load(d["bl"], namef(lo))
    if hi != lo:
        w = (f - lo) / float(hi - lo)
        a = a * (1 - w) + load(d["bl"], namef(hi)) * w
    return rs(a, size)


def hold_inputs(seg, f, size, closed=False):
    d = hold_setup(seg, size)
    dyn = _interp(d, d["dyn"], d["dyn_fr"], f, size)
    base, emit = (d["cb"], d["ce"]) if closed else (d["base"], d["emit"])
    comb, em = flicker(base + dyn, emit + dyn, d["lay"], f)
    if d["bfr"]:
        bm = _interp(d, d["beams"], d["bfr"] if seg != "ov" else None, f, (d["vs"].shape[1], d["vs"].shape[0]))
        tau_d = drift(d["tau"], f, uniform=(seg == "hq"))
        tl = rs(tau_d, (bm.shape[1], bm.shape[0])).mean(-1)
        vol = drift(d["vs"], f, uniform=(seg == "hq")) + bm * (d["sk"][0] + d["sk"][1] * tl)[..., None]
    else:
        tau_d = d["tau"]
        vol = d["vs"] + rs(d["bf"], (d["vs"].shape[1], d["vs"].shape[0]))
    return dict(comb=np.maximum(comb, 0), emit=np.maximum(em, 0), alb=d["alb"], z=d["z"], vol=vol,
                T_het=np.exp(-tau_d), cache=d["cache_c"] if closed else d["cache"])


def hold_plate(seg, f, size=(VW, VH), closed=False):
    d = hold_setup(seg, size)
    inp = hold_inputs(seg, f, size, closed)
    over = SF.post_over("hq", 0.0) if seg == "hq" else {}
    return PA.finish(os.path.join(SCR, d["bl"]), "real", shot=d["shot"], t=f / SB.FPS, inp=inp, over=over)


def hold_anchors(seg):
    if seg == "ov":
        return json.load(open(os.path.join(SCR, "loop", "anchors_O_overview.json")))
    if seg == "hq":
        return None
    return json.load(open(os.path.join(SCR, BL[seg], "anchors_S_%s.json" % seg)))


def street_plate(f, size=(VW, VH)):
    """The street at frame f: the live loop composite with walls closed and open, revealed per room."""
    tr = f / SB.FPS - SB.T["b4"]
    A = hold_anchors("ov")
    op = hold_plate("ov", f, size)
    if tr >= RV.reveal_len():
        return op, A
    cl = hold_plate("ov", f, size, closed=True)
    return RV.reveal_plate(cl, op, A, tr), A


# ---------------------------------------------------------------- the plate of any frame (monkeypatched into sb_frames)
_PL = {}


def plate_of(f):
    if f in _PL:
        return _PL[f]
    seg, pose, ex = SB.cam_at(f)
    if seg == "ov":
        p, A = street_plate(f)
    elif seg in HOLDS:
        p, A = hold_plate(seg, f, (1920, 1080) if seg == "hq" else (VW, VH)), hold_anchors(seg)
    elif SF.rendered(BL[seg], f):
        p, nm = SF.moving_plate(seg, f, SB.zoom_at(seg, pose))
        A = json.load(open(os.path.join(SCR, BL[seg], "anchors_%s.json" % nm)))
    else:
        p = SF.warped_plate(seg, f)
        A = SF.anchors_from_pose(pose, BL[seg])
    if len(_PL) > 12:
        _PL.clear()
    _PL[f] = (p, A)
    return _PL[f]


def source(seg, g):
    sg = SB.cam_at(g)[0]
    p, A = plate_of(g)
    if sg in STATIC:
        z = hold_setup(sg, (VW, VH))["z"]
    else:
        z = load(BL[sg], "f%04d_z" % g)[..., 0]
    return p, A, z


SF.plate_of = plate_of
SF.source = source


def up(img, size=(1920, 1080)):
    return img if img.size == size else img.resize(size, Image.LANCZOS)


def street_overlay(img, A, f):
    """REVEAL bits + the links writing on; MARK: the markers, the route grade and the route UI arriving."""
    t = f / SB.FPS
    tr = t - SB.T["b4"]
    tm = t - SB.T["mark"]
    img = RV.reveal_bits(img, A, tr)
    if tm > 0:
        a = U.ease(U.clamp(tm / 0.35))
        st, opts = U.G.states(SB.WALK)
        graded = U.route_grade(img, A, st, SB.WALK[-1], None, 0.0, 0.0)
        img = Image.blend(img.convert("RGBA"), graded.convert("RGBA"), a)
    img = RV.draw_links(img, A, tr, zones=tm > 0)
    if tm > 0:
        img = RV.draw_marks(img, A, tm)
        img = RV.route_chrome(img, A, 1.0, U.ease(U.clamp(tm / 0.35)))
    return img


def compose(f, plate=None, A=None, size_out=(VW, VH)):
    t = f / SB.FPS
    seg, pose, ex = SB.cam_at(f)
    T = SB.T
    if plate is None:
        plate, A = SF.blended_plate(f)
    if seg == "hq":
        img = U.hq_page(up(plate), t)
        if t >= T["b3"]:
            img = U.jack_in(img, t)
    elif seg == "dive":
        pl = up(plate).convert("RGBA")
        lt = t - T["dive"]
        if lt < 0.25:       # hand-over from the 1920 live HQ render to the dive renders (the camera barely moves yet)
            pl = Image.blend(pl, up(plate_of(SB.fr(T["dive"]) - 1)[0]).convert("RGBA"), 1.0 - lt / 0.25)
        img = pl
        if lt < 0.3:
            ui = U.hq_page(up(plate), T["b3"] + 0.01, pose=pose)
            img = Image.blend(img, ui, 1.0 - U.ease(lt / 0.3))
        img = U.dive_over(img, t, pose)
    elif seg == "ov":
        img = street_overlay(up(plate).convert("RGBA"), A, f)
    else:
        img = SF.route_ui_cached(up(plate).convert("RGBA"), A, SF.route_state(f, A), ("S_" + seg) if seg in STATIC else None)
    img = U.title(img.convert("RGB"), t)
    return img if size_out == img.size else img.resize(size_out, Image.LANCZOS)


def _chunk(fs):
    for f in fs:
        compose(f).save(os.path.join(OUT, "f_%04d.png" % f))
    return fs


def frames(f0, f1, j):
    os.makedirs(OUT, exist_ok=True)
    todo = [f for f in range(f0, f1) if not os.path.exists(os.path.join(OUT, "f_%04d.png" % f))]
    chunks = [todo[i:i + 8] for i in range(0, len(todo), 8)]
    with Pool(j) as pool:
        for c in pool.imap_unordered(_chunk, chunks):
            print("done", c[0], "-", c[-1], flush=True)


# ---------------------------------------------------------------- boards (1920 x 1080)
BOARD_LIST = [
    ("01_HQ_idle", SB.fr(1.0)),
    ("02_SELECT_hover_site_file", SB.fr(4.4)),
    ("03_SELECT_plan_and_jack_in", SB.fr(6.3)),
    ("04_JACKIN_terminal", SB.fr(8.45)),
    ("05_JACKIN_binary_rain", SB.fr(9.5)),
    ("06_JACKIN_crt_collapse", SB.fr(10.2)),
    ("07_DIVE_mid_no_route", "dboard_a"),
    ("08_DIVE_low_no_route", "dboard_b"),
    ("09_REVEAL_first_walls", SB.fr(SB.T["b4"] + 0.22)),
    ("10_REVEAL_trace", SB.fr(SB.T["b4"] + RV.link_start(4) + 0.13)),
    ("11_MARK_markers_target", SB.fr(SB.T["mark"] + RV.marks_len() + 0.3)),
    ("12_ZOOM_decision", SB.fr(SB.T["b6"] - 0.1)),
    ("13_CHOOSE_hover_option_1", SB.fr(SB.T["hover2"] - 0.3)),
    ("14_CHOOSE_hover_option_2", SB.fr(SB.T["end"] - 0.5)),
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
                              over=SF.post_over("dive", SB.zoom_at(seg, pose)))
            A = json.load(open(os.path.join(SCR, "bl_diveboard2", "anchors_%s.json" % f)))
            img = compose(ff, plate, A, (1920, 1080))
        else:
            seg = SB.cam_at(f)[0]
            if seg == "ov":
                # the live street (the r3 loop layers at the run start, 1280 passes finished at 1920), revealed
                A = hold_anchors("ov")
                tr = f / SB.FPS - SB.T["b4"]
                op = hold_plate("ov", f, (1920, 1080))
                plate = RV.reveal_plate(hold_plate("ov", f, (1920, 1080), closed=True), op, A, tr) \
                    if tr < RV.reveal_len() else op
                img = compose(f, plate, A, (1920, 1080))
            elif seg in HOLDS:
                plate = hold_plate(seg, f, (1920, 1080))
                img = compose(f, plate, hold_anchors(seg), (1920, 1080))
            else:
                img = compose(f, size_out=(1920, 1080))
        img.save(os.path.join(BOARDS, name + ".png"))
        print("board", name, flush=True)


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
