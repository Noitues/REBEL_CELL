"""Round 17 corp slice animations: round 16 set (scenes16) with the round 16 review fixes.

Changed: Solace GROWTH (true mitosis), Meridian CRIT (a box gets the stamp), DEFEND (running bond),
JUDGEMENT (a real courtroom gavel on a round sound block), MISS (the box shreds away), Halcyon SHIELD
(reverted to round 15: a rock bounces off a riot shield). Everything else is scenes16 unchanged.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import f_num, f_mono
import scenes as S0
import scenes16 as S16
from scenes import Sc, tri, ease, rot, rect_pts, W_, container

PAL = S16.PAL
PAL["solace"] = dict(S0.PAL["solace"])
YC = S16.YC


# ================================================================== SOLACE: GROWTH = mitosis
def sol_growth(s, t):
    u, d, P = s.u, s.d, s.P
    cx, cy = s.cx, s.Y(0.66)
    R = 50 * u
    # 0-.25 one round cell; .25-.55 it elongates and pinches; .55-.85 two round cells drift apart; .85-1 hold
    if t < 0.25:
        sep, waist = 0.0, 1.0
    elif t < 0.55:
        q = ease((t - 0.25) / 0.30)
        sep, waist = 70 * u * q, 1.0 - q
    else:
        q = ease(min(1, (t - 0.55) / 0.30))
        sep, waist = 70 * u + 80 * u * q, 0.0
    r = R * (1 - 0.18 * min(1, sep / (70 * u)))
    H, W = s.im.size[1], s.im.size[0]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = np.zeros((H, W), np.float32)
    for sx in (-1, 1):  # metaball field of two circles; the waist term holds them together while pinching
        dx = xx - (cx + sx * sep / 2)
        f = np.maximum(f, 1 - np.hypot(dx, yy - cy) / r)
    if waist > 0:
        bridge = 1 - np.maximum(np.abs(xx - cx) / (sep / 2 + 1e-3), np.abs(yy - cy) / (r * (0.25 + 0.75 * waist)))
        f = np.maximum(f, bridge * (np.abs(xx - cx) < sep / 2 + 1))
    m = (f > 0).astype(np.float32)
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2 * u)).point(lambda v: 255 if v > 128 else 0)
    edge = mi.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(7))
    s.im.paste(Image.new("RGBA", s.im.size, (110, 190, 40, 175)), (0, 0), mi)
    s.im.paste(Image.new("RGBA", s.im.size, P["a"] + (255,)), (0, 0), edge)
    s.gl.paste(Image.new("RGBA", s.im.size, P["a"] + (200,)), (0, 0), edge)
    d = ImageDraw.Draw(s.im)
    nuc = [(cx - sep / 2, cy), (cx + sep / 2, cy)] if t >= 0.18 else [(cx, cy)]
    for (x, y) in nuc:  # the nucleus divides first
        rn = 12 * u
        d.ellipse([x - rn, y - rn, x + rn, y + rn], fill=(40, 90, 10, 255), outline=P["a"] + (255,), width=W_(2 * u))
    if 0.25 <= t < 0.55:  # pinch arrows
        for sy in (-1, 1):
            y = cy + sy * (r + 14 * u)
            d.polygon([(cx, cy + sy * (r * (0.3 + 0.7 * waist) + 2 * u)), (cx - 6 * u, y), (cx + 6 * u, y)], fill=(240, 255, 210, 220))


# ================================================================== MERIDIAN
def parcel(d, P, u, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=P["card"] + (255,), outline=P["ink"] + (255,), width=W_(3 * u))
    d.rectangle([x0 + (x1 - x0) * 0.44, y0, x0 + (x1 - x0) * 0.56, y1], fill=(206, 160, 100, 255))
    d.line([(x0, y0 + 10 * u), (x1, y0 + 10 * u)], fill=(150, 104, 58, 255), width=W_(2 * u))
    d.text((x0 + 6 * u, y1 - 14 * u), "MRD  PKG 4471", font=f_mono(int(8 * u)), fill=P["ink"] + (255,))


def mer_crit(s, t):  # a parcel slides in, the PRIORITY stamp slams onto it, it ships out
    u, d, P = s.u, s.d, s.P
    w, h = 130 * u, 74 * u
    cy = s.Y(0.56)
    if t < 0.2:
        x = s.cx - w / 2 - (1 - ease(t / 0.2)) * 260 * u
    elif t < 0.8:
        x = s.cx - w / 2
    else:
        x = s.cx - w / 2 + ease((t - 0.8) / 0.2) * 260 * u
    parcel(d, P, u, x, cy - h / 2, x + w, cy + h / 2)
    if t >= 0.36:
        st = S16.stamp_img("PRIORITY", u, P["hot"], 26)
        if t < 0.42:
            k = (t - 0.36) / 0.06
            sc = 1.8 - 0.8 * k
            st = st.resize((int(st.width * sc), int(st.height * sc)))
        s.im.alpha_composite(st, (int(x + w / 2 - st.width / 2), int(cy - st.height / 2)))
    if 0.2 <= t < 0.36:  # the stamp comes down from the top
        k = ease((t - 0.2) / 0.16)
        sy = s.Y(-0.1) + (cy - 50 * u - s.Y(-0.1)) * k
        d.rectangle([s.cx - 30 * u, sy + 26 * u, s.cx + 30 * u, sy + 40 * u], fill=(150, 40, 36, 255), outline=P["ink"] + (255,))
        d.rectangle([s.cx - 7 * u, sy - 6 * u, s.cx + 7 * u, sy + 26 * u], fill=(90, 64, 40, 255))
        d.ellipse([s.cx - 16 * u, sy - 24 * u, s.cx + 16 * u, sy], fill=(110, 80, 50, 255), outline=P["ink"] + (255,))
    if 0.36 <= t < 0.5:
        k = (t - 0.36) / 0.14
        r = (40 + 50 * k) * u
        s.g.ellipse([s.cx - r, cy - r * 0.4, s.cx + r, cy + r * 0.4], outline=P["hot"] + (int(220 * (1 - k)),), width=W_(6 * u))


def mer_defend(s, t):  # the crane lays two containers on top of the wall in a running (offset brick) bond
    u, d, P = s.u, s.d, s.P
    cols = [(196, 92, 30), (60, 120, 170), (200, 150, 40), (150, 60, 50)]
    ch, cw = 26 * u, 64 * u
    wy = s.Y(0.72) - ch
    for r in range(2):  # existing wall: two courses, each offset half a container from the one below
        y = wy + r * ch
        off = ((r + 1) % 2) * cw / 2
        for k in range(-3, 4):
            x = s.cx - cw / 2 + k * cw - off
            container(d, x, y, cw - 2 * u, ch - 2 * u, cols[(k + r) % 4], P["ink"], u)
    jy = s.Y(0.02)
    d.rectangle([0, jy, s.W, jy + 10 * u], fill=P["crane"] + (255,), outline=P["ink"] + (255,), width=W_(2 * u))
    for k in np.arange(0, s.W, 14 * u):
        d.line([(k, jy), (k + 14 * u, jy + 10 * u)], fill=P["ink"] + (255,), width=W_(2 * u))
    land = wy - ch
    slots = [s.cx - cw, s.cx]  # new course: joints over the middle of the containers below (running bond)
    newc = [(230, 120, 30), (70, 150, 200)]
    for j, sx in enumerate(slots):
        q = (t - j * 0.45) / 0.45
        if 0 <= q < 1:
            k = ease(min(1, q / 0.8))
            cy = s.Y(0.10) + (land - s.Y(0.10)) * k
            tx = sx + cw / 2
            d.rectangle([tx - 14 * u, jy + 10 * u, tx + 14 * u, jy + 18 * u], fill=(70, 70, 76, 255))
            d.line([(tx - 8 * u, jy + 18 * u), (tx - cw * 0.35, cy)], fill=(30, 30, 34, 255), width=W_(1.5 * u))
            d.line([(tx + 8 * u, jy + 18 * u), (tx + cw * 0.35, cy)], fill=(30, 30, 34, 255), width=W_(1.5 * u))
            container(d, sx, cy, cw - 2 * u, ch - 2 * u, newc[j], P["ink"], u, "MRDU")
        elif q >= 1:
            container(d, sx, land, cw - 2 * u, ch - 2 * u, newc[j], P["ink"], u, "MRDU")


def mer_judgement(s, t):  # a courtroom gavel: cylindrical head, handle into its middle, a FACE strikes the round block
    u, d, P = s.u, s.d, s.P
    bx, by = s.cx + 60 * u, s.Y(0.68)          # top surface centre of the sound block (right of the read block)
    # sound block: a short round cylinder seen slightly from above
    rbx, rby, bh = 46 * u, 12 * u, 14 * u
    d.rectangle([bx - rbx, by, bx + rbx, by + bh], fill=(150, 90, 44, 255))
    d.ellipse([bx - rbx, by + bh - rby, bx + rbx, by + bh + rby], fill=(150, 90, 44, 255), outline=P["ink"] + (255,), width=W_(2 * u))
    d.rectangle([bx - rbx, by, bx + rbx, by + bh], fill=(150, 90, 44, 255))
    d.line([(bx - rbx, by), (bx - rbx, by + bh)], fill=P["ink"] + (255,), width=W_(2 * u))
    d.line([(bx + rbx, by), (bx + rbx, by + bh)], fill=P["ink"] + (255,), width=W_(2 * u))
    d.ellipse([bx - rbx, by - rby, bx + rbx, by + rby], fill=(214, 150, 84, 255), outline=P["ink"] + (255,), width=W_(2 * u))
    d.ellipse([bx - rbx * 0.6, by - rby * 0.6, bx + rbx * 0.6, by + rby * 0.6], outline=(120, 70, 32, 255), width=W_(1.5 * u))
    # gavel at rest (impact): head axis vertical above the block, handle horizontal to the right, pivot at its end
    hl, hr = 58 * u, 17 * u                     # head length (axis), head radius
    head_cx, head_bot = bx, by - 2 * u
    piv = (bx - 150 * u, head_bot - hl / 2)
    if t < 0.40:
        ang = -55 * (1 - ease(t / 0.40) ** 2)    # swings down from above
    elif t < 0.60:
        ang = 0.0
    else:
        ang = -55 * ease((t - 0.60) / 0.40)
    yc = head_bot - hl / 2
    handle = rect_pts(piv[0], yc - 6 * u, head_cx - hr + 2 * u, yc + 6 * u)
    d.polygon(rot(handle, ang, *piv), fill=(214, 150, 80, 255), outline=P["ink"] + (255,))
    d.polygon(rot(rect_pts(piv[0], yc - 8 * u, piv[0] + 34 * u, yc + 8 * u), ang, *piv), fill=(170, 110, 56, 255), outline=P["ink"] + (255,))
    body = rect_pts(head_cx - hr, head_bot - hl, head_cx + hr, head_bot)
    d.polygon(rot(body, ang, *piv), fill=(226, 160, 90, 255), outline=P["ink"] + (255,), width=W_(2 * u))
    for yb in (head_bot - hl + 10 * u, head_bot - 10 * u):  # the two brass bands near the faces
        d.polygon(rot(rect_pts(head_cx - hr, yb - 3 * u, head_cx + hr, yb + 3 * u), ang, *piv), fill=(220, 180, 90, 255))
    d.polygon(rot(rect_pts(head_cx - hr * 0.35, head_bot - hl, head_cx - hr * 0.1, head_bot), ang, *piv), fill=(250, 200, 140, 255))
    for yf in (head_bot - hl, head_bot):  # the two flat faces, shown as thin ellipses (cylinder ends)
        face = [(head_cx + hr * math.cos(math.radians(a)), yf + 4 * u * math.sin(math.radians(a))) for a in range(0, 360, 20)]
        d.polygon(rot(face, ang, *piv), fill=(240, 190, 120, 255), outline=P["ink"] + (255,))
    if 0.40 <= t < 0.78:  # impact: flash + shockwave on the block top
        k = (t - 0.40) / 0.38
        a = int(255 * (1 - k))
        for sc in (1.0, 0.6):
            rx, ry = (40 + 140 * k * sc) * u, (10 + 30 * k * sc) * u
            s.g.ellipse([bx - rx, by - ry, bx + rx, by + ry], outline=P["a"] + (a,), width=W_(10 * u))
            d.ellipse([bx - rx, by - ry, bx + rx, by + ry], outline=(255, 230, 190, a), width=W_(3 * u))
        if k < 0.3:
            s.g.ellipse([bx - 50 * u, by - 26 * u, bx + 50 * u, by + 16 * u], fill=(255, 240, 200, 255))


def mer_miss(s, t):  # the tape peels off, the box opens, then it shreds into strips and particles: nothing left
    u, d, P = s.u, s.d, s.P
    half = 64 * u
    x0, x1 = s.cx - half, s.cx + half
    y0, y1 = s.Y(0.30), s.Y(0.72)
    if t < 0.45:
        S16.box(d, P, u, x0, y0, x1, y1)
        S16.flaps(d, P, u, s.cx, y0, half, 1 - ease(max(0, (t - 0.25) / 0.2)))
        if t < 0.25:
            k = ease(t / 0.25)
            xe = x1 - 4 * u - (x1 - x0 - 8 * u) * k
            d.rectangle([x0 + 4 * u, y0 - 6 * u, xe, y0], fill=(236, 210, 150, 240))
            d.line([(xe, y0 - 3 * u), (xe + 18 * u, y0 - 26 * u * (0.4 + k))], fill=(236, 210, 150, 240), width=W_(6 * u))
        return
    q = (t - 0.45) / 0.55  # shred: vertical strips peel apart, fall, spin and break into flecks
    n = 9
    sw = (x1 - x0) / n
    rng = np.random.default_rng(7)
    for i in range(n):
        delay = rng.random() * 0.25
        k = max(0.0, min(1.0, (q - delay) / 0.75))
        dx = (i - (n - 1) / 2) * 10 * u * k + (rng.random() - 0.5) * 30 * u * k
        dy = 140 * u * k * k
        a = (rng.random() - 0.5) * 70 * k
        h = (y1 - y0) * (1 - 0.7 * k)
        cx = x0 + (i + 0.5) * sw + dx
        cy = (y0 + y1) / 2 + dy
        alpha = int(255 * (1 - k) ** 1.2)
        if alpha > 8:
            pts = rot(rect_pts(cx - sw / 2 + 1 * u, cy - h / 2, cx + sw / 2 - 1 * u, cy + h / 2), a, cx, cy)
            d.polygon(pts, fill=(P["card"] if i % 3 else (206, 160, 100)) + (alpha,), outline=P["ink"] + (alpha,))
        for j in range(4):  # flecks
            fk = min(1.0, k * 1.3)
            fx = cx + (rng.random() - 0.5) * 60 * u * fk
            fy = cy - h / 2 + rng.random() * h + 60 * u * fk * fk
            fa = int(220 * (1 - fk))
            if fa > 8 and k > 0.15:
                r = (1.5 + rng.random() * 2) * u
                d.rectangle([fx - r, fy - r, fx + r, fy + r], fill=P["card"] + (fa,))


SCENES = {k: dict(v) for k, v in S16.SCENES.items()}
SCENES["solace"]["HEAL"] = sol_growth
SCENES["meridian"].update({"CRITICAL": mer_crit, "DEFEND": mer_defend, "SPECIAL": mer_judgement, "MISS": mer_miss})
SCENES["halcyon"]["SHIELD"] = S0.hal_shield      # reverted to round 15
SCENES["halcyon"]["ATTACK"] = S16.hal_attack_b    # option B chosen
FALLBACK = S16.FALLBACK


def scene(ctx, corp, kind, t):
    tab = SCENES[corp]
    fn = tab.get(kind) or tab.get(FALLBACK.get(kind, "ATTACK"))
    s = Sc(ctx, corp)
    s.P = PAL[corp]
    fn(s, t % 1.0)
    return s.done()
