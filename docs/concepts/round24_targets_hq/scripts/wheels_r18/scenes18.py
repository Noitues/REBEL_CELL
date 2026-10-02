"""Round 18 corp slice animations: round 17 set with Solace GROWTH and Meridian changes.

- Solace GROWTH: no pinch arrows; one round cell divides into two.
- Meridian DEFEND: running bond; container 1 drops BEHIND the value block, container 2 lands beside it
  in the slice CENTRE, offset half a container.
- Meridian CRIT -> AIRMAIL: an airplane crosses bottom-left to top-right leaving a contrail.
- Meridian RAM drain -> PRIORITY: uses the round 17 crit screen (a parcel gets the PRIORITY stamp).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import f_num, f_mono
import scenes as S0
import scenes17 as S17
from scenes import Sc, tri, ease, rot, rect_pts, W_, container

PAL = S17.PAL
YC = S17.YC


def sol_growth(s, t):
    u, d, P = s.u, s.d, s.P
    cx, cy = s.cx, s.Y(0.66)
    R = 50 * u
    if t < 0.25:
        sep, waist = 0.0, 1.0
    elif t < 0.55:
        q = ease((t - 0.25) / 0.30)
        sep, waist = 70 * u * q, 1.0 - q
    else:
        q = ease(min(1, (t - 0.55) / 0.30))
        sep, waist = 70 * u + 50 * u * q, 0.0
    r = R * (1 - 0.18 * min(1, sep / (70 * u)))
    H, W = s.im.size[1], s.im.size[0]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    f = np.zeros((H, W), np.float32)
    for sx in (-1, 1):
        f = np.maximum(f, 1 - np.hypot(xx - (cx + sx * sep / 2), yy - cy) / r)
    if waist > 0:
        bridge = 1 - np.maximum(np.abs(xx - cx) / (sep / 2 + 1e-3), np.abs(yy - cy) / (r * (0.25 + 0.75 * waist)))
        f = np.maximum(f, bridge * (np.abs(xx - cx) < sep / 2 + 1))
    mi = Image.fromarray(((f > 0) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2 * u)).point(lambda v: 255 if v > 128 else 0)
    edge = mi.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(7))
    s.im.paste(Image.new("RGBA", s.im.size, (110, 190, 40, 175)), (0, 0), mi)
    s.im.paste(Image.new("RGBA", s.im.size, P["a"] + (255,)), (0, 0), edge)
    s.gl.paste(Image.new("RGBA", s.im.size, P["a"] + (200,)), (0, 0), edge)
    d = ImageDraw.Draw(s.im)
    nuc = [(cx - sep / 2, cy), (cx + sep / 2, cy)] if t >= 0.18 else [(cx, cy)]
    for (x, y) in nuc:
        rn = 12 * u
        d.ellipse([x - rn, y - rn, x + rn, y + rn], fill=(40, 90, 10, 255), outline=P["a"] + (255,), width=W_(2 * u))


def mer_defend(s, t):
    """Running bond. The value block sits at screen row ~0.40. The wall's top course is laid at that row:
    container 1 drops in BEHIND the value ('12', right of centre), container 2 lands beside it at the slice
    CENTRE. Every course is offset half a container from the one below."""
    u, d, P = s.u, s.d, s.P
    cols = [(196, 92, 30), (60, 120, 170), (200, 150, 40), (150, 60, 50)]
    ch, cw = 30 * u, 72 * u
    c1x = s.cx - 6 * u                  # behind the value number
    c2x = c1x - cw                      # next to it, at the centre
    land = s.Y(0.40) - ch / 2
    y = land + ch
    r = 0
    while y < s.Y(0.80):                # existing courses below, half-offset alternately (running bond)
        off = cw / 2 if r % 2 == 0 else 0.0
        for k in range(-4, 5):
            x = c1x + k * cw + off
            container(d, x, y, cw - 2 * u, ch - 2 * u, cols[(k + r) % 4], P["ink"], u)
        y += ch
        r += 1
    jy = s.Y(0.0)
    d.rectangle([0, jy, s.W, jy + 9 * u], fill=P["crane"] + (255,), outline=P["ink"] + (255,), width=W_(2 * u))
    for k in np.arange(0, s.W, 14 * u):
        d.line([(k, jy), (k + 14 * u, jy + 9 * u)], fill=P["ink"] + (255,), width=W_(2 * u))
    newc = [(255, 176, 70), (140, 210, 255)]  # bright: they sit under the darkened read plate
    for j, x0 in enumerate((c1x, c2x)):
        q = (t - j * 0.42) / 0.42
        if 0 <= q < 1:
            k = ease(min(1, q / 0.8))
            cy = s.Y(-0.25) + (land - s.Y(-0.25)) * k
            tx = x0 + cw / 2
            d.rectangle([tx - 14 * u, jy + 9 * u, tx + 14 * u, jy + 17 * u], fill=(70, 70, 76, 255))
            d.line([(tx - 8 * u, jy + 17 * u), (tx - cw * 0.35, cy)], fill=(30, 30, 34, 255), width=W_(1.5 * u))
            d.line([(tx + 8 * u, jy + 17 * u), (tx + cw * 0.35, cy)], fill=(30, 30, 34, 255), width=W_(1.5 * u))
            container(d, x0, cy, cw - 2 * u, ch - 2 * u, newc[j], P["ink"], u, "MRDU")
        elif q >= 1:
            container(d, x0, land, cw - 2 * u, ch - 2 * u, newc[j], P["ink"], u, "MRDU")

def mer_airmail(s, t):
    """AIRMAIL: a cargo plane flies bottom-left to top-right across the slice, leaving a contrail."""
    u, d, P = s.u, s.d, s.P
    x0, y0 = s.cx - 230 * u, s.Y(0.86)
    x1, y1 = s.cx + 230 * u, s.Y(0.02)
    q = t * 1.15 - 0.075
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    px, py = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
    # contrail: two parallel streaks fading behind the plane
    for side in (-1, 1):
        n = 26
        for k in range(n):
            qa = q - k * 0.03
            if qa < -0.1:
                break
            xa, ya = x0 + (x1 - x0) * qa, y0 + (y1 - y0) * qa
            ox, oy = -math.sin(math.radians(ang)) * side * 8 * u, math.cos(math.radians(ang)) * side * 8 * u
            r = (3 + k * 0.5) * u
            a = int(200 * (1 - k / n))
            d.ellipse([xa + ox - r, ya + oy - r, xa + ox + r, ya + oy + r], fill=(240, 236, 228, a))
    # plane (top view), nose along the path
    L = 70 * u
    body = rect_pts(px - L / 2, py - 7 * u, px + L / 2, py + 7 * u)
    wing = [(px + 6 * u, py), (px - 14 * u, py - 46 * u), (px - 26 * u, py - 46 * u), (px - 14 * u, py),
            (px - 26 * u, py + 46 * u), (px - 14 * u, py + 46 * u)]
    tail = [(px - L / 2 + 6 * u, py), (px - L / 2 - 4 * u, py - 18 * u), (px - L / 2 - 12 * u, py - 18 * u), (px - L / 2 - 6 * u, py),
            (px - L / 2 - 12 * u, py + 18 * u), (px - L / 2 - 4 * u, py + 18 * u)]
    nose = [(px + L / 2, py - 7 * u), (px + L / 2 + 12 * u, py), (px + L / 2, py + 7 * u)]
    for pts, col in ((wing, (226, 228, 236)), (tail, (226, 228, 236)), (body, (246, 246, 250)), (nose, (246, 246, 250))):
        d.polygon(rot(pts, ang, px, py), fill=col + (255,), outline=P["ink"] + (255,))
    stripe = rect_pts(px - L / 2 + 8 * u, py - 2.5 * u, px + L / 2 - 4 * u, py + 2.5 * u)
    d.polygon(rot(stripe, ang, px, py), fill=P["a"] + (255,))
    s.g.polygon(rot(body, ang, px, py), fill=(255, 255, 255, 120))


SCENES = {k: dict(v) for k, v in S17.SCENES.items()}
SCENES["solace"]["HEAL"] = sol_growth
SCENES["meridian"].update({"CRITICAL": mer_airmail, "DEFEND": mer_defend, "SPECIAL": S17.mer_crit})
FALLBACK = S17.FALLBACK


def scene(ctx, corp, kind, t):
    tab = SCENES[corp]
    fn = tab.get(kind) or tab.get(FALLBACK.get(kind, "ATTACK"))
    s = Sc(ctx, corp)
    s.P = PAL[corp]
    fn(s, t % 1.0)
    return s.done()
