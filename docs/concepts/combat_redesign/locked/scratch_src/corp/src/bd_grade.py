"""bd_grade: the room post grade for the locked combat board (roadmap step 6).

grade(bare, P) -> graded backdrop (float RGB 0-255) BEFORE the board scrim.  bare = room_<n>_bare.png (v3.1 post).
Every step is a per-pixel or separable operation that a Godot post shader can do (screen UV, one mask texture or
an analytic ellipse, a gaussian pass):
  1. focus hull m: analytic ellipse round the cutaway (centre cx,cy; radii rx,ry; smoothstep feather f0..f1)
  2. haze/blur: hull blurred by hull_blur px, city by city_blur px (two gaussian passes, mixed by m)
  3. chroma: lerp toward Rec709 luma by chroma (all pixels), further by neon_chroma on neon pixels (S>0.35, V>0.35)
     and by pink_chroma on player-pink hues (295-350 deg), so pink stays the player's
  4. contrast around pivot (in 0-1 value): v' = pivot + (v - pivot) * contrast
  5. value: hull_value inside, city_value outside (mixed by m)
  6. highlight shoulder on luma: above knee, luma -> knee + (ceil-knee)*(1-exp(-(l-knee)/(ceil-knee)))  (hue kept)
  7. haze: mix toward haze_rgb by haze (lifts the blacks a little so the room stays atmospheric, not dead)
  8. vignette: x (1 - vignette * smoothstep(v0, v1, d_focus))  and a left falloff toward the board:
     x (1 - board_falloff * (1 - smoothstep(bx0, bx1, x)))
The board scrim (r2_ground.scrim 'P': 55 % SCRIM #02030A + 6 px blur, r 330-560) is board ground and is kept as is.

2026-11-03 stage 2 (AD review 2.8, grade version rb2-1).  The step-6 grade switched the room off (room mean L* 21 in the reviewer's box).
Added steps, each off unless its key is present, so step6-1 still reproduces exactly:
  1'. hull_poly: the focus hull follows the cutaway box (iso hexagon of the walls and floor slab; m = 1 - smoothstep(-pf0, pf1, sdf))
  2'. mid_blur: one blur ramp (hull_blur -> mid_blur -> city_blur across the hull edge + blur_reach) instead of a cross-fade (no double image)
  2''. corp light (hue_lo..hue_hi pulled toward hue_to by hue_amt): Meridian's shop light turned from the shop's lime to the corp's amber
  3'. city_chroma: the city outside the hull keeps that share of its chroma
  5'. local tone: gain from the local mean luma (tone_blur px): target = tone_lo + (tone_hi - tone_lo)(1 - exp(-x / tone_s)), capped at
      tone_gmax; full in the hull, tone_out of it in the city out to hull distance tone_d0..tone_d1.  Dark areas come up by multiplication,
      so ink lines and relative detail survive (a flat lift would fog the room)
  7'. haze_out + spill_rgb: the haze ramps from haze (room) to haze_out (city) and its colour is the room's own key light at the hull,
      the night haze_rgb from d = sp0 to sp1: the seam where the city meets the room is one atmosphere lit by the room
Per room: the shoulder ceiling ceil is solved (backdrop/src/bd2_solve.py) so the rb_checks room region reads p95 L* 38 on p1; the room
mean follows (checked at L* 28.6-33.4 on the room regions of all five beats; tone_lo steps up from 0.17 if a beat reads low).
grade_pre / grade_post split the work at the tone step so a solver can cache the expensive half.
"""
import numpy as np
from PIL import Image, ImageFilter

W, H = 1920, 1080
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)

BASE = dict(cx=1500.0, cy=600.0, rx=330.0, ry=270.0, f0=0.85, f1=1.55,
            hull_blur=0.0, city_blur=2.0,
            chroma=1.0, neon_chroma=1.0, pink_chroma=1.0,
            contrast=1.0, pivot=0.18,
            hull_value=1.0, city_value=0.85,
            knee=1.0, ceil=1.0,
            haze=0.0, haze_rgb=[22, 18, 40],
            vignette=0.0, v0=0.9, v1=2.6,
            board_falloff=0.0, bx0=700.0, bx1=1250.0)


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def blur(a, px):
    if px <= 0:
        return a
    return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(px)), np.float32)


_SDF = {}


def poly_sdf(pts):
    """signed distance (px) to a polygon, positive outside; cached per polygon"""
    key = tuple(tuple(p) for p in pts)
    if key not in _SDF:
        from PIL import ImageDraw
        from scipy.ndimage import distance_transform_edt
        im = Image.new('L', (W, H), 0)
        ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
        inside = np.asarray(im) > 127
        _SDF[key] = (distance_transform_edt(~inside) - distance_transform_edt(inside)).astype(np.float32)
    return _SDF[key]


def hull(P):
    d = np.hypot((XX - P['cx']) / P['rx'], (YY - P['cy']) / P['ry'])
    if P.get('hull_poly'):
        # 2026-11-03 (rb2) seam: the focus hull follows the cutaway box (iso hexagon of the room's walls and floor slab) instead of an ellipse,
        # so the hull edge is the room's own wall line and the neighbouring facades are wholly city.  m = 1 - smoothstep(-pf0, pf1, sdf).
        # d (the ellipse distance) still drives the vignette, the spill colour and the tone reach.
        sd = poly_sdf(P['hull_poly'])
        return 1 - smooth(-P['pf0'], P['pf1'], sd), d
    return 1 - smooth(P['f0'], P['f1'], d), d


def luma(a):
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def hue(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60.0
    return h


def pinkw(a):
    """weight of player-pink hues (magenta to rose, about 302-350 deg) with some chroma; pink belongs to the player.
    The violet night city (hue below about 296) is left alone."""
    h = hue(a)
    mx, mn = a.max(-1), a.min(-1)
    S = (mx - mn) / np.maximum(mx, 1e-4)
    hw = smooth(296, 308, h) * (1 - smooth(345, 358, h))
    return hw * smooth(0.18, 0.35, S)


def hue_rotate(a, deg):
    """rotate RGB (0-1, [...,3]) about the grey axis by deg (per pixel array or scalar), Rec709 luma kept"""
    t = np.radians(deg)[..., None] if np.ndim(deg) else np.radians(deg)
    c, s = np.cos(t), np.sin(t)
    k = 1.0 / 3.0
    sq = np.sqrt(k)
    r, g, b = a[..., 0:1], a[..., 1:2], a[..., 2:3]
    # Rodrigues rotation about (1,1,1)/sqrt(3)
    m0 = c + (1 - c) * k
    m1 = k * (1 - c) - sq * s
    m2 = k * (1 - c) + sq * s
    out = np.concatenate([r * m0 + g * m1 + b * m2, r * m2 + g * m0 + b * m1, r * m1 + g * m2 + b * m0], -1)
    l0, l1 = luma(a), luma(np.clip(out, 0, None))
    return np.clip(out, 0, None) * (l0 / np.maximum(l1, 1e-5))[..., None]


def corp_light(a, P):
    """2026-11-03 (rb2): the corp light.  Pixels whose hue sits in the room's key-light window (hue_lo..hue_hi, feathered by hue_f) with
    some chroma are rotated toward hue_to by hue_amt.  Off (hue_amt 0) for every room except a corp variant (Meridian on the shop)."""
    if not P.get('hue_amt'):
        return a
    h = hue(a)
    mx, mn = a.max(-1), a.min(-1)
    S = (mx - mn) / np.maximum(mx, 1e-4)
    w = smooth(P['hue_lo'] - P['hue_f'], P['hue_lo'], h) * (1 - smooth(P['hue_hi'], P['hue_hi'] + P['hue_f'], h)) * smooth(0.10, 0.30, S)
    # each pixel's hue is pulled toward hue_to by hue_amt (the window's spread of greens becomes one narrow band of the corp light)
    return hue_rotate(a, (P['hue_to'] - h) * P['hue_amt'] * w)


def grade_pre(bare, P):
    """steps 1-5 of the grade (hull, blur ramp, corp light, chroma, contrast, value) plus the local-mean luma the tone step needs.
    Independent of tone_lo / tone_hi / knee / ceil / haze, so a solver can cache it.  Returns (a 0-1, m, d, lb or None)."""
    P = dict(BASE, **P)
    m, d = hull(P)
    m3 = m[..., None]
    if P.get('mid_blur') is not None:
        # 2026-11-03 (rb2) seam: one blur ramp instead of a sharp / blurred cross-fade (no double-image band where the city meets the room):
        # hull_blur inside, mid_blur at the middle of the edge band, city_blur beyond it; smoothsteps on the hull sdf (or the ellipse d)
        if P.get('hull_poly'):
            q, e0, e1 = poly_sdf(P['hull_poly']), -P['pf0'], P['pf1'] + P.get('blur_reach', 0.0)
        else:
            q, e0, e1 = d, P['f0'], P['f1']
        fm = 0.5 * (e0 + e1)
        s1 = smooth(e0, fm, q)[..., None]
        s2 = smooth(fm, e1, q)[..., None]
        a = (blur(bare, P['hull_blur']) * (1 - s1) + blur(bare, P['mid_blur']) * s1) * (1 - s2) + blur(bare, P['city_blur']) * s2
    else:
        a = blur(bare, P['hull_blur']) * m3 + blur(bare, P['city_blur']) * (1 - m3)
    a = a / 255.0
    a = corp_light(a, P)
    # chroma
    mx, mn = a.max(-1), a.min(-1)
    S = (mx - mn) / np.maximum(mx, 1e-4)
    neon = (smooth(0.35, 0.60, S) * smooth(0.35, 0.65, mx))[..., None]
    k = P['chroma'] * (1 - (1 - P['neon_chroma']) * neon) * (1 - (1 - P['pink_chroma']) * pinkw(a)[..., None])
    if P.get('city_chroma') is not None:
        # 2026-11-03 (rb2) seam: the city outside the hull keeps city_chroma of its chroma, so the violet / mauve facades next to the room do not
        # read as a second picture; the room's light (spill haze, step 7) then tints that calmer street
        k = k * (m3 + P['city_chroma'] * (1 - m3))
    l = luma(a)[..., None]
    a = l + (a - l) * k
    # contrast
    a = P['pivot'] + (a - P['pivot']) * P['contrast']
    a = np.clip(a, 0, None)
    # value
    a = a * (P['hull_value'] * m3 + P['city_value'] * (1 - m3))
    lb = None
    if P.get('tone_hi'):
        from scipy.ndimage import gaussian_filter
        lb = gaussian_filter(luma(a).astype(np.float32), P['tone_blur'])
    return a, m, d, lb


def grade_post(pre, P):
    """steps 5b-8 of the grade on grade_pre's output"""
    P = dict(BASE, **P)
    a, m, d, lb = pre
    # 2026-11-03 (rb2): local tone (a dodge).  The gain comes from the LOCAL mean luma (gaussian tone_blur px), not the pixel's own luma, so
    # dark areas of the room come up by multiplication and keep their ink lines and their relative detail; bright areas come down the same
    # way.  target(x) = tone_lo + (tone_hi - tone_lo) * (1 - exp(-x / tone_s)); gain = target / x, capped at tone_gmax; full in the hull,
    # tone_out of it in the city out to hull distance tone_d0..tone_d1.  One extra blurred-luma pass in a shader.
    if lb is not None:
        tgt = P['tone_lo'] + (P['tone_hi'] - P['tone_lo']) * (1 - np.exp(-lb / P['tone_s']))
        g = np.clip(tgt / np.maximum(lb, 1e-4), 0.0, P['tone_gmax'])
        reach = 1 - smooth(P.get('tone_d0', 9.0), P.get('tone_d1', 10.0), d)
        g = 1 + (g - 1) * (m + P.get('tone_out', 0.0) * (1 - m) * reach)
        a = a * g[..., None]
    # highlight shoulder on luma
    kn, ce = P['knee'], P['ceil']
    if kn < ce:
        l = luma(a)
        span = ce - kn
        l2 = np.where(l > kn, kn + span * (1 - np.exp(-(l - kn) / span)), l)
        a = a * (l2 / np.maximum(l, 1e-4))[..., None]
    # haze
    hz = np.array(P['haze_rgb'], np.float32) / 255.0
    if P.get('haze_out') is not None:
        # 2026-11-03 (rb2) seam: the haze amount ramps from haze (room) to haze_out (city) with the hull weight, and its colour is the room's
        # own light (spill_rgb) at the hull and the night haze (haze_rgb) from d = sp0 to sp1, so the room's light carries into the street
        # round it and the city meets the room through one atmosphere
        hk = (P['haze'] * m + P['haze_out'] * (1 - m))[..., None]
        sp = np.array(P['spill_rgb'], np.float32) / 255.0
        ws = smooth(P['sp0'], P['sp1'], d)[..., None]
        hz = sp * (1 - ws) + hz * ws
        a = a * (1 - hk) + hz * hk
    else:
        a = a * (1 - P['haze']) + hz * P['haze']
    # vignette + board falloff
    v = (1 - P['vignette'] * smooth(P['v0'], P['v1'], d)) * (1 - P['board_falloff'] * (1 - smooth(P['bx0'], P['bx1'], XX)))
    a = a * v[..., None]
    return np.clip(a * 255.0, 0, 255)


def grade(bare, P):
    return grade_post(grade_pre(bare, P), P)


# ------------------------------------------------------------------------------------------------ O-30 fix 2: the default room grade of corp/src
# step6-1 per-room parameters (O-30, backdrop/src/bd_solve.py), kept for before / after (env BD_GRADE=step6 renders with them).
ROOMS_STEP61 = {
 "bio": {
  "board_falloff": 0.3,
  "bx0": 700.0,
  "bx1": 1250.0,
  "ceil": 0.3,
  "chroma": 0.876,
  "city_blur": 4.0,
  "city_value": 0.55,
  "contrast": 1.12,
  "cx": 1500.0,
  "cy": 600.0,
  "f0": 0.85,
  "f1": 1.55,
  "haze": 0.0,
  "haze_rgb": [
   22,
   18,
   40
  ],
  "hull_blur": 0.4,
  "hull_value": 0.466,
  "knee": 0.18,
  "neon_chroma": 0.8,
  "pink_chroma": 0.55,
  "pivot": 0.16,
  "rx": 330.0,
  "ry": 270.0,
  "v0": 0.9,
  "v1": 2.6,
  "vignette": 0.3
 },
 "event": {
  "board_falloff": 0.3,
  "bx0": 700.0,
  "bx1": 1250.0,
  "ceil": 0.32,
  "chroma": 0.836,
  "city_blur": 4.0,
  "city_value": 0.55,
  "contrast": 1.24,
  "cx": 1500.0,
  "cy": 600.0,
  "f0": 0.85,
  "f1": 1.55,
  "haze": 0.0,
  "haze_rgb": [
   22,
   18,
   40
  ],
  "hull_blur": 0.4,
  "hull_value": 0.478,
  "knee": 0.18,
  "neon_chroma": 0.8,
  "pink_chroma": 0.42,
  "pivot": 0.16,
  "rx": 330.0,
  "ry": 270.0,
  "v0": 0.9,
  "v1": 2.6,
  "vignette": 0.3
 },
 "gh": {
  "board_falloff": 0.3,
  "bx0": 700.0,
  "bx1": 1250.0,
  "ceil": 0.3,
  "chroma": 0.891,
  "city_blur": 4.0,
  "city_value": 0.55,
  "contrast": 1.12,
  "cx": 1500.0,
  "cy": 600.0,
  "f0": 0.85,
  "f1": 1.55,
  "haze": 0.0,
  "haze_rgb": [
   22,
   18,
   40
  ],
  "hull_blur": 0.4,
  "hull_value": 0.47,
  "knee": 0.18,
  "neon_chroma": 0.8,
  "pink_chroma": 0.55,
  "pivot": 0.16,
  "rx": 330.0,
  "ry": 270.0,
  "v0": 0.9,
  "v1": 2.6,
  "vignette": 0.3
 },
 "lobby": {
  "board_falloff": 0.3,
  "bx0": 700.0,
  "bx1": 1250.0,
  "ceil": 0.3,
  "chroma": 0.849,
  "city_blur": 4.0,
  "city_value": 0.55,
  "contrast": 1.12,
  "cx": 1500.0,
  "cy": 600.0,
  "f0": 0.85,
  "f1": 1.55,
  "haze": 0.0,
  "haze_rgb": [
   22,
   18,
   40
  ],
  "hull_blur": 0.4,
  "hull_value": 0.45,
  "knee": 0.18,
  "neon_chroma": 0.8,
  "pink_chroma": 0.55,
  "pivot": 0.16,
  "rx": 330.0,
  "ry": 270.0,
  "v0": 0.9,
  "v1": 2.6,
  "vignette": 0.3
 },
 "rec": {
  "board_falloff": 0.3,
  "bx0": 700.0,
  "bx1": 1250.0,
  "ceil": 0.3,
  "chroma": 0.941,
  "city_blur": 4.0,
  "city_value": 0.55,
  "contrast": 1.12,
  "cx": 1500.0,
  "cy": 600.0,
  "f0": 0.85,
  "f1": 1.55,
  "haze": 0.0,
  "haze_rgb": [
   22,
   18,
   40
  ],
  "hull_blur": 0.4,
  "hull_value": 0.458,
  "knee": 0.18,
  "neon_chroma": 0.8,
  "pink_chroma": 0.55,
  "pivot": 0.16,
  "rx": 330.0,
  "ry": 270.0,
  "v0": 0.9,
  "v1": 2.6,
  "vignette": 0.3
 },
 "shop": {
  "board_falloff": 0.3,
  "bx0": 700.0,
  "bx1": 1250.0,
  "ceil": 0.3,
  "chroma": 0.826,
  "city_blur": 4.0,
  "city_value": 0.55,
  "contrast": 1.12,
  "cx": 1500.0,
  "cy": 600.0,
  "f0": 0.85,
  "f1": 1.55,
  "haze": 0.0,
  "haze_rgb": [
   22,
   18,
   40
  ],
  "hull_blur": 0.4,
  "hull_value": 0.415,
  "knee": 0.18,
  "neon_chroma": 0.8,
  "pink_chroma": 0.55,
  "pivot": 0.16,
  "rx": 330.0,
  "ry": 270.0,
  "v0": 0.9,
  "v1": 2.6,
  "vignette": 0.3
 },
 "srv": {
  "board_falloff": 0.3,
  "bx0": 700.0,
  "bx1": 1250.0,
  "ceil": 0.3,
  "chroma": 0.814,
  "city_blur": 4.0,
  "city_value": 0.55,
  "contrast": 1.12,
  "cx": 1500.0,
  "cy": 600.0,
  "f0": 0.85,
  "f1": 1.55,
  "haze": 0.0,
  "haze_rgb": [
   22,
   18,
   40
  ],
  "hull_blur": 0.4,
  "hull_value": 0.439,
  "knee": 0.18,
  "neon_chroma": 0.8,
  "pink_chroma": 0.55,
  "pivot": 0.16,
  "rx": 330.0,
  "ry": 270.0,
  "v0": 0.9,
  "v1": 2.6,
  "vignette": 0.3
 }
}


# ------------------------------------------------------------------------------------------------ 2026-11-03 stage 2: the default room grade (rb2-1)
# Per-room parameters as published in locked/backdrop/grade.json (version rb2-1), solved by backdrop/src/bd2_solve.py.
# Keys: <room> = the room's grade; <room>_<corp> = a corp variant of that room (shop_meridian: the Meridian corp light).
GRADE_VERSION = 'rb2-1'
KIT_ROOMS = ('bio', 'srv', 'gh', 'rec', 'lobby', 'event', 'shop')
# the room each skin fights in.  Review 2.8: Meridian plates were still in the Solace lab; the shop is the only kit room with no Solace sign.
CORP_ROOM = {'neutral': 'bio', 'solace': 'bio', 'meridian': 'shop'}
# >>> ROOMS_RB2 (written by backdrop/src/bd2_embed.py from backdrop/work/bd2_params.json)
ROOMS = {
 "bio": {
  "cx": 1500.0,
  "cy": 600.0,
  "rx": 330.0,
  "ry": 270.0,
  "f0": 0.85,
  "f1": 1.55,
  "hull_poly": [
   [
    1195,
    488
   ],
   [
    1465,
    338
   ],
   [
    1792,
    523
   ],
   [
    1792,
    672
   ],
   [
    1512,
    808
   ],
   [
    1195,
    632
   ]
  ],
  "pf0": 10.0,
  "pf1": 3.0,
  "hull_blur": 0.4,
  "mid_blur": 1.6,
  "city_blur": 4.0,
  "blur_reach": 40.0,
  "neon_chroma": 0.8,
  "city_chroma": 0.3,
  "pivot": 0.16,
  "hull_value": 0.8,
  "city_value": 0.6,
  "tone_lo": 0.17,
  "tone_hi": 0.38,
  "tone_s": 0.09,
  "tone_blur": 14.0,
  "tone_gmax": 3.5,
  "tone_out": 0.45,
  "tone_d0": 1.5,
  "tone_d1": 2.6,
  "knee": 0.24,
  "ceil": 0.3502,
  "haze": 0.05,
  "haze_out": 0.5,
  "haze_rgb": [
   20,
   18,
   34
  ],
  "sp0": 1.0,
  "sp1": 2.6,
  "vignette": 0.1,
  "v0": 0.9,
  "v1": 2.6,
  "board_falloff": 0.08,
  "bx0": 700.0,
  "bx1": 1250.0,
  "chroma": 0.876,
  "contrast": 1.12,
  "pink_chroma": 0.55,
  "spill_rgb": [
   77,
   106,
   68
  ]
 },
 "srv": {
  "cx": 1500.0,
  "cy": 600.0,
  "rx": 330.0,
  "ry": 270.0,
  "f0": 0.85,
  "f1": 1.55,
  "hull_poly": [
   [
    1195,
    488
   ],
   [
    1465,
    338
   ],
   [
    1792,
    523
   ],
   [
    1792,
    672
   ],
   [
    1512,
    808
   ],
   [
    1195,
    632
   ]
  ],
  "pf0": 10.0,
  "pf1": 3.0,
  "hull_blur": 0.4,
  "mid_blur": 1.6,
  "city_blur": 4.0,
  "blur_reach": 40.0,
  "neon_chroma": 0.8,
  "city_chroma": 0.3,
  "pivot": 0.16,
  "hull_value": 0.8,
  "city_value": 0.6,
  "tone_lo": 0.17,
  "tone_hi": 0.38,
  "tone_s": 0.09,
  "tone_blur": 14.0,
  "tone_gmax": 3.5,
  "tone_out": 0.45,
  "tone_d0": 1.5,
  "tone_d1": 2.6,
  "knee": 0.24,
  "ceil": 0.35,
  "haze": 0.05,
  "haze_out": 0.5,
  "haze_rgb": [
   20,
   18,
   34
  ],
  "sp0": 1.0,
  "sp1": 2.6,
  "vignette": 0.1,
  "v0": 0.9,
  "v1": 2.6,
  "board_falloff": 0.08,
  "bx0": 700.0,
  "bx1": 1250.0,
  "chroma": 0.814,
  "contrast": 1.12,
  "pink_chroma": 0.55,
  "spill_rgb": [
   65,
   107,
   85
  ]
 },
 "gh": {
  "cx": 1500.0,
  "cy": 600.0,
  "rx": 330.0,
  "ry": 270.0,
  "f0": 0.85,
  "f1": 1.55,
  "hull_poly": [
   [
    1195,
    488
   ],
   [
    1465,
    338
   ],
   [
    1792,
    523
   ],
   [
    1792,
    672
   ],
   [
    1512,
    808
   ],
   [
    1195,
    632
   ]
  ],
  "pf0": 10.0,
  "pf1": 3.0,
  "hull_blur": 0.4,
  "mid_blur": 1.6,
  "city_blur": 4.0,
  "blur_reach": 40.0,
  "neon_chroma": 0.8,
  "city_chroma": 0.3,
  "pivot": 0.16,
  "hull_value": 0.8,
  "city_value": 0.6,
  "tone_lo": 0.17,
  "tone_hi": 0.38,
  "tone_s": 0.09,
  "tone_blur": 14.0,
  "tone_gmax": 3.5,
  "tone_out": 0.45,
  "tone_d0": 1.5,
  "tone_d1": 2.6,
  "knee": 0.24,
  "ceil": 0.3519,
  "haze": 0.05,
  "haze_out": 0.5,
  "haze_rgb": [
   20,
   18,
   34
  ],
  "sp0": 1.0,
  "sp1": 2.6,
  "vignette": 0.1,
  "v0": 0.9,
  "v1": 2.6,
  "board_falloff": 0.08,
  "bx0": 700.0,
  "bx1": 1250.0,
  "chroma": 0.891,
  "contrast": 1.12,
  "pink_chroma": 0.55,
  "spill_rgb": [
   88,
   103,
   61
  ]
 },
 "rec": {
  "cx": 1500.0,
  "cy": 600.0,
  "rx": 330.0,
  "ry": 270.0,
  "f0": 0.85,
  "f1": 1.55,
  "hull_poly": [
   [
    1195,
    488
   ],
   [
    1465,
    338
   ],
   [
    1792,
    523
   ],
   [
    1792,
    672
   ],
   [
    1512,
    808
   ],
   [
    1195,
    632
   ]
  ],
  "pf0": 10.0,
  "pf1": 3.0,
  "hull_blur": 0.4,
  "mid_blur": 1.6,
  "city_blur": 4.0,
  "blur_reach": 40.0,
  "neon_chroma": 0.8,
  "city_chroma": 0.3,
  "pivot": 0.16,
  "hull_value": 0.8,
  "city_value": 0.6,
  "tone_lo": 0.17,
  "tone_hi": 0.38,
  "tone_s": 0.09,
  "tone_blur": 14.0,
  "tone_gmax": 3.5,
  "tone_out": 0.45,
  "tone_d0": 1.5,
  "tone_d1": 2.6,
  "knee": 0.24,
  "ceil": 0.3547,
  "haze": 0.05,
  "haze_out": 0.5,
  "haze_rgb": [
   20,
   18,
   34
  ],
  "sp0": 1.0,
  "sp1": 2.6,
  "vignette": 0.1,
  "v0": 0.9,
  "v1": 2.6,
  "board_falloff": 0.08,
  "bx0": 700.0,
  "bx1": 1250.0,
  "chroma": 0.941,
  "contrast": 1.12,
  "pink_chroma": 0.55,
  "spill_rgb": [
   94,
   101,
   69
  ]
 },
 "lobby": {
  "cx": 1500.0,
  "cy": 600.0,
  "rx": 330.0,
  "ry": 270.0,
  "f0": 0.85,
  "f1": 1.55,
  "hull_poly": [
   [
    1195,
    488
   ],
   [
    1465,
    338
   ],
   [
    1792,
    523
   ],
   [
    1792,
    672
   ],
   [
    1512,
    808
   ],
   [
    1195,
    632
   ]
  ],
  "pf0": 10.0,
  "pf1": 3.0,
  "hull_blur": 0.4,
  "mid_blur": 1.6,
  "city_blur": 4.0,
  "blur_reach": 40.0,
  "neon_chroma": 0.8,
  "city_chroma": 0.3,
  "pivot": 0.16,
  "hull_value": 0.8,
  "city_value": 0.6,
  "tone_lo": 0.17,
  "tone_hi": 0.38,
  "tone_s": 0.09,
  "tone_blur": 14.0,
  "tone_gmax": 3.5,
  "tone_out": 0.45,
  "tone_d0": 1.5,
  "tone_d1": 2.6,
  "knee": 0.24,
  "ceil": 0.3493,
  "haze": 0.05,
  "haze_out": 0.5,
  "haze_rgb": [
   20,
   18,
   34
  ],
  "sp0": 1.0,
  "sp1": 2.6,
  "vignette": 0.1,
  "v0": 0.9,
  "v1": 2.6,
  "board_falloff": 0.08,
  "bx0": 700.0,
  "bx1": 1250.0,
  "chroma": 0.849,
  "contrast": 1.12,
  "pink_chroma": 0.55,
  "spill_rgb": [
   69,
   109,
   59
  ]
 },
 "event": {
  "cx": 1500.0,
  "cy": 600.0,
  "rx": 330.0,
  "ry": 270.0,
  "f0": 0.85,
  "f1": 1.55,
  "hull_poly": [
   [
    1195,
    488
   ],
   [
    1465,
    338
   ],
   [
    1792,
    523
   ],
   [
    1792,
    672
   ],
   [
    1512,
    808
   ],
   [
    1195,
    632
   ]
  ],
  "pf0": 10.0,
  "pf1": 3.0,
  "hull_blur": 0.4,
  "mid_blur": 1.6,
  "city_blur": 4.0,
  "blur_reach": 40.0,
  "neon_chroma": 0.8,
  "city_chroma": 0.3,
  "pivot": 0.16,
  "hull_value": 0.8,
  "city_value": 0.6,
  "tone_lo": 0.17,
  "tone_hi": 0.38,
  "tone_s": 0.09,
  "tone_blur": 14.0,
  "tone_gmax": 3.5,
  "tone_out": 0.45,
  "tone_d0": 1.5,
  "tone_d1": 2.6,
  "knee": 0.24,
  "ceil": 0.3496,
  "haze": 0.05,
  "haze_out": 0.5,
  "haze_rgb": [
   20,
   18,
   34
  ],
  "sp0": 1.0,
  "sp1": 2.6,
  "vignette": 0.1,
  "v0": 0.9,
  "v1": 2.6,
  "board_falloff": 0.08,
  "bx0": 700.0,
  "bx1": 1250.0,
  "chroma": 0.836,
  "contrast": 1.24,
  "pink_chroma": 0.42,
  "spill_rgb": [
   88,
   101,
   81
  ]
 },
 "shop": {
  "cx": 1500.0,
  "cy": 600.0,
  "rx": 330.0,
  "ry": 270.0,
  "f0": 0.85,
  "f1": 1.55,
  "hull_poly": [
   [
    1195,
    488
   ],
   [
    1465,
    338
   ],
   [
    1792,
    523
   ],
   [
    1792,
    672
   ],
   [
    1512,
    808
   ],
   [
    1195,
    632
   ]
  ],
  "pf0": 10.0,
  "pf1": 3.0,
  "hull_blur": 0.4,
  "mid_blur": 1.6,
  "city_blur": 4.0,
  "blur_reach": 40.0,
  "neon_chroma": 0.8,
  "city_chroma": 0.3,
  "pivot": 0.16,
  "hull_value": 0.8,
  "city_value": 0.6,
  "tone_lo": 0.17,
  "tone_hi": 0.38,
  "tone_s": 0.09,
  "tone_blur": 14.0,
  "tone_gmax": 3.5,
  "tone_out": 0.45,
  "tone_d0": 1.5,
  "tone_d1": 2.6,
  "knee": 0.24,
  "ceil": 0.3523,
  "haze": 0.05,
  "haze_out": 0.5,
  "haze_rgb": [
   20,
   18,
   34
  ],
  "sp0": 1.0,
  "sp1": 2.6,
  "vignette": 0.1,
  "v0": 0.9,
  "v1": 2.6,
  "board_falloff": 0.08,
  "bx0": 700.0,
  "bx1": 1250.0,
  "chroma": 0.826,
  "contrast": 1.12,
  "pink_chroma": 0.55,
  "spill_rgb": [
   84,
   104,
   68
  ]
 },
 "shop_meridian": {
  "cx": 1500.0,
  "cy": 600.0,
  "rx": 330.0,
  "ry": 270.0,
  "f0": 0.85,
  "f1": 1.55,
  "hull_poly": [
   [
    1195,
    488
   ],
   [
    1465,
    338
   ],
   [
    1792,
    523
   ],
   [
    1792,
    672
   ],
   [
    1512,
    808
   ],
   [
    1195,
    632
   ]
  ],
  "pf0": 10.0,
  "pf1": 3.0,
  "hull_blur": 0.4,
  "mid_blur": 1.6,
  "city_blur": 4.0,
  "blur_reach": 40.0,
  "neon_chroma": 0.9,
  "city_chroma": 0.3,
  "pivot": 0.16,
  "hull_value": 0.8,
  "city_value": 0.6,
  "tone_lo": 0.17,
  "tone_hi": 0.38,
  "tone_s": 0.09,
  "tone_blur": 14.0,
  "tone_gmax": 3.5,
  "tone_out": 0.45,
  "tone_d0": 1.5,
  "tone_d1": 2.6,
  "knee": 0.24,
  "ceil": 0.3518,
  "haze": 0.05,
  "haze_out": 0.5,
  "haze_rgb": [
   20,
   18,
   34
  ],
  "sp0": 1.0,
  "sp1": 2.6,
  "vignette": 0.1,
  "v0": 0.9,
  "v1": 2.6,
  "board_falloff": 0.08,
  "bx0": 700.0,
  "bx1": 1250.0,
  "chroma": 1.05,
  "contrast": 1.12,
  "pink_chroma": 0.55,
  "hue_lo": 88.0,
  "hue_hi": 162.0,
  "hue_f": 14.0,
  "hue_to": 20.0,
  "hue_amt": 0.88,
  "spill_rgb": [
   106,
   97,
   70
  ]
 }
}
# <<< ROOMS_RB2


def params_for(room, corp='neutral'):
    """the grade parameters for a room under a skin: the corp variant when one exists, else the room's own"""
    return ROOMS.get('%s_%s' % (room, corp), ROOMS.get(room, ROOMS.get('bio')))


def room_key(path):
    """room_<n>_bare.png -> <n>"""
    import os
    b = os.path.basename(str(path))
    if b.startswith('room_') and b.endswith('_bare.png'):
        return b[5:-9]
    return 'bio'


def room_grade(opt='P'):
    """drop-in for r2_ground.grade(opt): the rb2-1 grade with the room's own parameters (room taken from the active bare path, corp
    variant from env CORP).  The board scrim is unchanged (r2_ground.scrim).  env BD_GRADE=step6 uses the step6-1 table instead."""
    import os
    import r2_ground as G2
    import o_ground as OG
    path = getattr(OG, 'BARE_PATH', None) or getattr(G2, 'BARE_PATH', None)
    rk = room_key(path)
    if os.environ.get('BD_GRADE') == 'step6':
        P = ROOMS_STEP61.get(rk, ROOMS_STEP61['bio'])
    else:
        P = params_for(rk, os.environ.get('CORP', 'neutral'))
    return grade(G2.bare().astype(np.float32), P)
