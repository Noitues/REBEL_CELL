"""r3 idle loop: sum the rendered layers per frame, finish with the still's post (post_aaa.finish), lay the static UI on
top with its two living touches (DISPATCH cursor, option-sticker gloss sweep), write PNG frames.

python post_loop.py [f0 f1]          -> ../scratch/loop/frames/f_000.png ...
All timing below is in frames (24 fps, 96 frames = 4 s); every function is periodic in 96, so frame 96 = frame 0.
"""
import colorsys
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import post_aaa as PA  # noqa: E402
import compose_aaa as CA  # noqa: E402
import compose3 as C3  # noqa: E402
import sgraph3 as G  # noqa: E402
import ui31 as K  # noqa: E402

ROOT = os.path.dirname(HERE)
LD = os.path.join(ROOT, "scratch", "loop")
OUT = os.path.join(LD, "frames")
CFG = json.load(open(os.path.join(LD, "groups.json")))
NF, FPS = CFG["nf"], CFG["fps"]
GROUPS = CFG["groups"]

# ------------------------------------------------------------------ timing tables (seeded, periodic)
RNG = np.random.default_rng(9700)
BUZZ = 0.86 + 0.14 * RNG.random(NF)                   # a neon hum, frame to frame
BUZZ[[30, 31]] = (0.22, 0.55)                          # two dropouts
BUZZ[71] = 0.35
FLICK = np.ones(NF)
FLICK[52:59] = (0.2, 1.0, 0.08, 0.9, 0.3, 1.0, 0.95)    # one flicker burst
BROKEN = 0.9 + 0.1 * RNG.random(NF)                    # the broken sign: a stutter, a dead spell, a stutter
BROKEN[10:23] = (0.1, 1.0, 0.0, 0.0, 1.0, 0.15, 0.0, 0.0, 0.0, 0.0, 0.7, 0.0, 1.0)
BROKEN[64:71] = (0.0, 1.0, 0.0, 0.6, 0.0, 0.0, 1.0)
WIN = {"win_0": [(24, 70)], "win_1": [(60, 96), (0, 6)], "win_2": [(40, 52)]}   # off spans: rare switches
STROBE_PH = {"strobe_0": 0, "strobe_1": 9, "strobe_2": 17}  # 1 s period, 2-frame flash
BILL_A = set(range(0, 46))
BILL_B = set(range(48, 94))
BILL_GLITCH = {46, 47, 94, 95}
HOLO_ROLL = {"holo_solace": 1, "holo_orbital": 2, "holo_halcyon": 1}    # scan-band rolls per loop
HOLO_GLITCH = {"holo_solace": (37, 38), "holo_orbital": (77,), "holo_halcyon": (15, 16)}
CURSOR_ON = [(f % 24) < 12 for f in range(NF)]        # 1 s blink
GLOSS = {1: (12, 41), 2: (60, 89)}                     # option n: sweep frames (1.2 s), one sticker at a time
DRIFT_PX = (13.0, 0.0)                                 # fog 2D drift over the loop at 640 px: top row, below 55 %


def gain(g, f):
    if g == "sign_buzz":
        return BUZZ[f]
    if g == "sign_flicker":
        return FLICK[f]
    if g == "sign_broken":
        return BROKEN[f]
    if g in WIN:
        return 0.0 if any(a <= f < b for a, b in WIN[g]) else 1.0
    if g in STROBE_PH:
        ph = (f - STROBE_PH[g]) % 24
        return 2.2 if ph < 2 else 0.12
    if g == "bill_a":
        return 1.0 if f in BILL_A else 0.0
    if g == "bill_b":
        return 1.0 if f in BILL_B else 0.0
    return 1.0


def pick_windows(emit, dec_box, W, H, n=3):
    """Seeded rule: n lit window cells (small warm emitters in the building band, off the decision set, apart), as
    pixel masks of the base emission. 1280-px coordinates; dec_box is in 1920-px."""
    L = PA.lum(emit)
    hue_warm = (emit[..., 0] > emit[..., 2] * 1.2)
    s = W / 1920.0
    db = [v * s for v in dec_box]
    cand = []
    for y in range(int(H * 0.30), int(H * 0.80), 3):
        for x in range(int(W * 0.12), int(W * 0.95), 3):
            v = L[y, x]
            if 0.12 < v < 1.2 and hue_warm[y, x] and not (db[0] - 20 < x < db[2] + 20 and db[1] - 20 < y < db[3] + 20):
                win = L[y - 4:y + 5, x - 4:x + 5]
                if v >= win.max() and (win > v * 0.3).mean() < 0.45:     # a small isolated cell, not a sign band
                    cand.append((x, y))
    rr = np.random.default_rng(9601)
    rr.shuffle(cand)
    out = {}
    for x, y in cand:
        if all(abs(x - a) + abs(y - b) > 120 for (a, b, m) in out.values()):
            m = np.zeros((H, W), np.float32)
            reg = L[y - 5:y + 6, x - 5:x + 6]
            m[y - 5:y + 6, x - 5:x + 6] = (reg > L[y, x] * 0.25).astype(np.float32)
            out["win_%d" % len(out)] = (x, y, m)
        if len(out) >= n:
            break
    print("windows (2D rule)", [(k, v[0], v[1]) for k, v in out.items()], flush=True)
    return {k: v[2] for k, v in out.items()}


def load(name):
    return np.load(os.path.join(LD, name + ".npy")).astype(np.float32)


def load_or(name, fallback):
    p = os.path.join(LD, name + ".npy")
    return load(name) if os.path.exists(p) else load(fallback)


def shift_rows(a, amt):
    """Shift each row of a (h, w[, c]) right by amt[row] px (linear interpolation, edge-clamped)."""
    h, w = a.shape[:2]
    xs = np.arange(w, dtype=np.float32)[None, :] - amt[:, None]
    x0 = np.clip(np.floor(xs).astype(np.int32), 0, w - 1)
    x1 = np.clip(x0 + 1, 0, w - 1)
    fr = (xs - np.floor(xs))
    rows = np.arange(h)[:, None]
    if a.ndim == 3:
        fr = fr[..., None]
    return a[rows, x0] * (1 - fr) + a[rows, x1] * fr


def drift(a, f):
    """The loop-safe 2D drift: (1 - p) S(s p) + p S(s (p - 1)), faster near the top (higher bands are deeper)."""
    h, w = a.shape[:2]
    p = f / NF
    k = w / 640.0
    # the fog drifts with the wind high up and not at all below ~55 % of the frame (street cones, god rays stay put)
    yy = np.arange(h) / (h - 1)
    s = (DRIFT_PX[1] + (DRIFT_PX[0] - DRIFT_PX[1]) * np.clip(1.0 - yy / 0.55, 0, 1)) * k
    return (1 - p) * shift_rows(a, s * p) + p * shift_rows(a, s * (p - 1))


def holo_mod(L, g, f, box):
    """Scan-band roll (a soft bright band rolling down the panel) and a 1-2 frame glitch (slices + RGB split)."""
    H, W = L.shape[:2]
    x0, y0, x1, y1 = [int(round(v * W / 1920.0)) for v in box]
    x0, y0 = max(0, x0 - 6), max(0, y0 - 6)
    x1, y1 = min(W, x1 + 6), min(H, y1 + 6)
    out = L.copy()
    hh = max(1, y1 - y0)
    yy = (np.arange(H, dtype=np.float32) - y0) / hh
    ph = (f / NF) * HOLO_ROLL.get(g, 1)
    d = ((yy - ph) % 1.0) - 0.5
    band = np.exp(-(d / 0.09) ** 2)
    m = 0.84 + 0.55 * band
    out = out * m[:, None, None]
    if f in HOLO_GLITCH.get(g, ()):
        r = np.random.default_rng(9800 + f + len(g))
        reg = out[y0:y1, x0:x1].copy()
        n = 5
        for s_ in range(n):
            a, b = s_ * reg.shape[0] // n, (s_ + 1) * reg.shape[0] // n
            reg[a:b] = np.roll(reg[a:b], int(r.integers(-9, 10)), axis=1)
        reg[..., 0] = np.roll(reg[..., 0], 3, axis=1)
        reg[..., 2] = np.roll(reg[..., 2], -3, axis=1)
        out[y0:y1, x0:x1] = reg * 1.25
    return out


def bill_glitch(La, Lb, f, box):
    H, W = La.shape[:2]
    x0, y0, x1, y1 = [int(round(v * W / 1920.0)) for v in box]
    x0, y0, x1, y1 = max(0, x0 - 4), max(0, y0 - 4), min(W, x1 + 4), min(H, y1 + 4)
    r = np.random.default_rng(9900 + f)
    mix = 0.35 if f in (46, 94) else 0.7
    reg = La[y0:y1, x0:x1] * (1 - mix) + Lb[y0:y1, x0:x1] * mix
    n = 7
    for s_ in range(n):
        a, b = s_ * reg.shape[0] // n, (s_ + 1) * reg.shape[0] // n
        reg[a:b] = np.roll(reg[a:b], int(r.integers(-12, 13)), axis=1)
    reg[..., 0] = np.roll(reg[..., 0], 4, axis=1)
    reg[..., 2] = np.roll(reg[..., 2], -4, axis=1)
    out = np.zeros_like(La)
    out[y0:y1, x0:x1] = reg * 1.15
    return out


# ------------------------------------------------------------------ UI: mattes once, live touches per frame
def ui_setup(W, H):
    A = json.load(open(os.path.join(LD, "anchors_O_overview.json")))
    state = dict(walked=G.WALK_MID, zoom=1.0)

    def down(a):
        return np.stack([np.asarray(Image.fromarray(a[..., c].astype(np.float32), "F").resize((W, H), Image.LANCZOS),
                                    np.float32) for c in range(3)], axis=-1)
    o0 = np.asarray(CA.overlay(Image.new("RGB", (1920, 1080), (0, 0, 0)), A, state, "all"), np.float32) / 255.0
    o1 = np.asarray(CA.overlay(Image.new("RGB", (1920, 1080), (int(255 * CA.FLAT),) * 3), A, state, "all"),
                    np.float32) / 255.0
    M = np.clip(down(np.clip((o1 - o0) / CA.FLAT, 0, 1)), 0, 1)
    B = np.clip(down(o0), 0, 1)
    st, opts = G.states(G.WALK_MID)
    stickers = []
    for n, i in enumerate(opts, 1):
        ks = min(1.9, max(0.75, C3.room_scale(A, i) * 0.8))
        x, y = C3.sticker_xy(A, i, ks)
        px = C3.STK_PX["option"] * ks
        stickers.append((n, x, y - 0.0, px / 2.0))
    f15 = K.F(K.MONO, 15)
    disp = C3.DISPATCH["mid"]
    tw = ImageDraw.Draw(Image.new("L", (8, 8))).textlength(disp, font=f15)
    cur_xy = (250 + 120 + tw + 0.4 * len(disp) + 4, (92 + 122) / 2)
    return dict(A=A, M=M, B=B, stickers=stickers, cursor=cur_xy)


def ui_frame(plate, U, f):
    W, H = plate.size
    s = W / 1920.0
    st, _ = G.states(G.WALK_MID)
    graded = CA.grade(plate, U["A"], st, G.WALK_MID[-1], None)
    P = np.asarray(graded.convert("RGB"), np.float32) / 255.0
    out = np.clip(P * U["M"] + U["B"], 0, 1)
    img = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    if CURSOR_ON[f]:
        cx, cy = U["cursor"]
        d.rectangle([cx * s, (cy - 7) * s, (cx + 8) * s, (cy + 7) * s], fill=(226, 230, 240, 235))
    for n, (a, b) in GLOSS.items():
        if not a <= f <= b:
            continue
        _n, x, y, r = next(t for t in U["stickers"] if t[0] == n)
        u = (f - a) / float(b - a)
        # a diagonal rainbow band (28 deg) crossing the die-cut disc once
        R = int(r * s * 2.2) + 4
        lay = np.zeros((2 * R, 2 * R, 4), np.float32)
        yy, xx = np.mgrid[-R:R, -R:R].astype(np.float32)
        ang = math.radians(28)
        dpos = (xx * math.cos(ang) + yy * math.sin(ang)) / (r * s)
        c = -1.6 + 3.2 * u
        band = np.exp(-((dpos - c) / 0.22) ** 2)
        disc = np.clip((r * s + 1.0 - np.sqrt(xx ** 2 + yy ** 2)), 0, 1)
        hue = (dpos - c) * 0.9 + 0.5
        rgb = np.stack([np.array(colorsys.hsv_to_rgb(h % 1.0, 0.35, 1.0)) for h in np.linspace(0, 1, 64)])
        hi = np.clip((hue * 63).astype(np.int32), 0, 63)
        lay[..., :3] = rgb[hi]
        lay[..., 3] = band * disc * 0.6
        layer = Image.fromarray((lay * 255).astype(np.uint8), "RGBA")
        img.paste(layer, (int(x * s) - R, int(y * s) - R), layer)
    return img


def main(f0=0, f1=NF):
    os.makedirs(OUT, exist_ok=True)
    base = load("base_combined")
    H, W = base.shape[:2]
    emit0 = load("base_emit")
    alb, z = load("base_albedo"), load("base_z")[..., 0]
    layers = {g: load("layer_%s_combined" % g) for g in GROUPS}
    vol_static, beams_full = load("vol_static_combined"), load("beams_full_combined")
    vol_strata = vol_static
    T_het = np.clip(load("static_trans_combined"), 1e-4, 1)
    tau = -np.log(T_het)
    tau_l = tau.mean(-1)
    VH, VW = vol_strata.shape[:2]

    def up(a):
        return a if a.shape[:2] == (VH, VW) else PA.resize_f(a, (VW, VH))
    b0 = up(load("beams_000_combined"))
    # fit beams_full ~ s b0 + k b0 tau (the strata brighten the shafts where they cross)
    m = PA.lum(b0) > 0.004
    X = np.stack([PA.lum(b0)[m], (PA.lum(b0) * tau_l)[m]], -1)
    y = PA.lum(beams_full)[m]
    sk = np.linalg.lstsq(X, y, rcond=None)[0] if m.sum() > 50 else np.array([1.0, 0.0])
    sk = np.clip(sk, [0.3, 0.0], [3.0, 40.0])
    print("beam fit s %.3f k %.3f (pixels %d)" % (sk[0], sk[1], int(m.sum())), flush=True)
    U = ui_setup(W, H)
    WINS = pick_windows(emit0, CFG["dec_box"], W, H) if not any(g.startswith("win_") for g in GROUPS) else {}
    cache = {}
    bx = {g: GROUPS[g].get("px") for g in GROUPS}
    for f in range(f0, f1):
        comb = base.copy()
        emit = emit0.copy()
        for g, L in layers.items():
            if g.startswith("holo_"):
                Lm = holo_mod(L, g, f, bx[g])
                comb += Lm - L
                emit += Lm - L
                continue
            k = gain(g, f) - (0.0 if g == "bill_b" else 1.0)
            if k != 0.0:
                comb += k * L
                emit += k * L
        for g, m in WINS.items():       # 2D window switch: the window's own emission leaves (its spill is negligible)
            k = gain(g, f) - 1.0
            if k != 0.0:
                comb += k * emit0 * m[..., None]
                emit += k * emit0 * m[..., None]
        if f in BILL_GLITCH:
            gl = bill_glitch(layers["bill_a"], layers["bill_b"], f, bx["bill_a"])
            comb += gl
            emit += gl
        dyn = load("dyn_%03d_combined" % f)
        comb += dyn
        emit += dyn
        # beams: [1 2 1] / 4 over neighbouring frames (cyclic) against the last denoiser shimmer
        bm = sum(w * up(load_or("beams_%03d_combined" % ((f + o) % NF), "beams_%03d_combined" % f))
                 for o, w in ((-1, 0.25), (0, 0.5), (1, 0.25)))
        tau_d = drift(tau, f)
        vol = drift(vol_static, f) + bm * (sk[0] + sk[1] * tau_d.mean(-1))[..., None]
        inp = dict(comb=np.maximum(comb, 0), emit=np.maximum(emit, 0), alb=alb, z=z, vol=vol, T_het=np.exp(-tau_d),
                   loop_p=f / NF, loop_T=NF / FPS, cache=cache)
        plate = PA.finish(LD, "real", inp=inp)
        img = ui_frame(plate, U, f)
        img.save(os.path.join(OUT, "f_%03d.png" % f))
        plate.save(os.path.join(OUT, "p_%03d.png" % f))
        print("frame", f, flush=True)


if __name__ == "__main__":
    a = [int(v) for v in sys.argv[1:3]]
    main(*a) if a else main()
