"""V3 AAA: put the V3 dynamic frame UI and route overlay on a 2560 x 1440 plate.

python compose_aaa.py <plate.png> <bl_dir> <out.png> [hover]

The overlay code (compose3 / sidekit / ui31 / kit44) draws at 1920 x 1080 and is reused unchanged:
  - the world grade (room state tints, the hover power cut) is redone here at 2560 x 1440 from the same anchors;
  - every overlay op is per-pixel affine in the plate (alpha composites, glows, shadows), so the overlay is drawn twice
    on flat plates (0 and 0.5) and solved per channel: out = plate * m + b. m and b are upscaled to 2560 x 1440 and
    applied to the real plate. The UI is therefore a 1.33x upscale (noted in NOTES.md).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import compose3 as C3  # noqa: E402
import sidekit as S  # noqa: E402
import sgraph3 as G  # noqa: E402
import ui31 as K  # noqa: E402
import cam_rig as R  # noqa: E402
import wax_r2 as WX  # noqa: E402

W0, H0 = 1920, 1080
POWER_CUT_2D = 0.62      # on top of the 3D power cut (22 %), so the street lands near V3 dynamic's 32 % in total
FLAT = 0.5
ROUTE_DARKEN = 0.2
CABLE_W = {}               # r2: the route is the wax grease pencil at full weight (no 3D holo tubes)


def poly_mask(poly, size, s, grow=0, blur=0):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([(p[0] * s, p[1] * s) for p in poly], fill=255)
    if grow:
        m = m.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m, np.float32) / 255.0


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def grade(plate, A, st, cur, hover):
    """compose3.grade at full resolution (overview: no decision vignette)."""
    W, H = plate.size
    s = W / W0
    out = np.asarray(plate.convert("RGB"), np.float32) / 255.0
    br = G.branch(hover)[0] if hover else set()
    # local darken under the route (CRITIQUE §6.7): a soft 0.2 multiply, radius 24 px at 1080p, along every cable
    # and over the option rooms, so the dashed lines always have contrast
    dm = Image.new("L", (W, H), 0)
    dd = ImageDraw.Draw(dm)
    for e in A["edges"]:
        pts = [(q[0] * s, q[1] * s) for q in e["pts"] if q is not None]
        if len(pts) > 1:
            dd.line(pts, fill=255, width=int(10 * s))
    for i in G.states(G.WALK_MID)[1]:
        p = C3.room_poly(A, i)
        if p:
            dd.polygon([(q[0] * s, q[1] * s) for q in p], fill=255)
    dm = np.asarray(dm.filter(ImageFilter.GaussianBlur(24 * s)), np.float32) / 255.0
    out = out * (1 - ROUTE_DARKEN * np.clip(dm * 2.0, 0, 1))[..., None]
    if hover:
        keep = np.zeros((H, W), np.float32)
        for i in sorted(br | {cur}):
            p = C3.room_poly(A, i)
            if p:
                keep = np.maximum(keep, poly_mask(p, (W, H), s, grow=8, blur=8))
        l3 = lum(out)[..., None]
        dim = (out * 0.75 + l3 * 0.25) * POWER_CUT_2D
        out = out * keep[..., None] + dim * (1 - keep[..., None])
    for i in G.NODES:
        p = C3.room_poly(A, i)
        if not p:
            continue
        m = poly_mask(p, (W, H), s, grow=1)[..., None]
        l3 = lum(out)[..., None]
        state = st[i]
        if state == "grey":
            ghost = np.array((0.06, 0.05, 0.11), np.float32)
            v = (l3 * 0.55) * 0.5 + ghost * 0.5
        elif state == "walked":
            v = (out * 0.55 + l3 * 0.45) * 0.62
        elif hover and i in br:
            v = out * 1.3
        elif state == "option":
            v = out        # (was x1.15: the option interiors washed toward white; the 3D light carries them now)
        else:
            v = out
        out = out * (1 - m) + v * m
    img = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    if hover:
        for i in sorted(br, key=lambda n: (G.LAYER[n], G.K[n])):
            p = C3.room_poly(A, i)
            if p:
                m = Image.fromarray((poly_mask(p, (W, H), s) * 255).astype(np.uint8))
                img = K.add_glow(img, m, S.TYPE_COL[G.KIND[i]], int(30 * s), 0.5)
    return img


def overlay(plate, A, state, part="all"):
    """compose3.frame without the world grade (the UI and the route overlay only). part: all | cables | rest."""
    walked = state["walked"]
    hover = state.get("hover")
    hk = state.get("hover_k", 1.0 if hover else 0.0)
    zoom = state.get("zoom", 0.0)
    st, opts = G.states(walked)
    est = G.edge_states(walked, st)
    cur = walked[-1]
    img = plate.convert("RGBA")
    k = min(1.6, max(0.8, C3.room_scale(A, cur) * 0.62))
    if part in ("all", "cables"):
        img = WX.draw_wax(img, A, est, st, opts, cur, hover=hover, hover_k=hk, k=k)   # r2: wax grease pencil
    if part == "cables":
        return img.convert("RGB")
    img = C3.draw_nodes(img, A, st, opts, hover=hover, hover_k=hk)
    img = C3.target_mark(img, A)
    img = C3.token_at(img, A, cur, k)
    if hover and hk > 0.5:
        p = C3.room_poly(A, hover)
        ks = min(1.9, max(0.75, C3.room_scale(A, hover) * 0.8))
        img = S.tag(img, p[3][0] + 8 * ks, p[3][1] - 20 * ks, hover, "option")
    img = S.chrome_top(img, C3.DISPATCH["mid"])
    img = S.sidebar(img, len(opts), hover=hover if (hover and hk > 0.5) else None)
    img = S.legend(img, hot=False, cx=1010)
    img = C3.view_toggle(img, zoom)
    if hover and hk > 0.5:
        p = C3.room_poly(A, hover)
        img = S.cursor(img, sum(q[0] for q in p) / 4 + 6, sum(q[1] for q in p) / 4 + 2)
    return img.convert("RGB")


def compose(plate_path, bl, out_path, hover=False):
    plate = Image.open(plate_path).convert("RGB")
    W, H = plate.size
    A = json.load(open(os.path.join(bl, "anchors_O_overview.json")))
    state = dict(walked=G.WALK_MID, zoom=1.0)
    if hover:
        state.update(hover=G.HOVER_MID, hover_k=1.0)
    st, _ = G.states(G.WALK_MID)
    graded = grade(plate, A, st, G.WALK_MID[-1], G.HOVER_MID if hover else None)
    def up(a):
        return np.stack([np.asarray(Image.fromarray(a[..., c].astype(np.float32), "F").resize((W, H), Image.LANCZOS), np.float32)
                         for c in range(3)], axis=-1)

    def matte(part):
        o0 = np.asarray(overlay(Image.new("RGB", (W0, H0), (0, 0, 0)), A, state, part), np.float32) / 255.0
        o1 = np.asarray(overlay(Image.new("RGB", (W0, H0), (int(255 * FLAT),) * 3), A, state, part), np.float32) / 255.0
        return np.clip(up(np.clip((o1 - o0) / FLAT, 0, 1)), 0, 1), np.clip(up(o0), 0, 1)
    P = np.asarray(graded.convert("RGB"), np.float32) / 255.0
    w = CABLE_W.get(A.get("look", "cel"), 1.0)
    if w >= 1.0:
        M, B = matte("all")
        out = np.clip(P * M + B, 0, 1)
    else:
        # AAA-2: the route lines are 3D holo-projections; the 2D cables stay as a lighter guide layer on top
        Mc, Bc = matte("cables")
        P = P * (1 - w + w * Mc) + w * Bc
        Mr, Br = matte("rest")
        out = np.clip(P * Mr + Br, 0, 1)
    img = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
    img.save(out_path)
    print("composed", out_path, flush=True)
    return img


if __name__ == "__main__":
    compose(sys.argv[1], sys.argv[2], sys.argv[3], len(sys.argv) > 4 and sys.argv[4] == "hover")
