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


def hull(P):
    d = np.hypot((XX - P['cx']) / P['rx'], (YY - P['cy']) / P['ry'])
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


def grade(bare, P):
    P = dict(BASE, **P)
    m, d = hull(P)
    m3 = m[..., None]
    a = blur(bare, P['hull_blur']) * m3 + blur(bare, P['city_blur']) * (1 - m3)
    a = a / 255.0
    # chroma
    mx, mn = a.max(-1), a.min(-1)
    S = (mx - mn) / np.maximum(mx, 1e-4)
    neon = (smooth(0.35, 0.60, S) * smooth(0.35, 0.65, mx))[..., None]
    k = P['chroma'] * (1 - (1 - P['neon_chroma']) * neon) * (1 - (1 - P['pink_chroma']) * pinkw(a)[..., None])
    l = luma(a)[..., None]
    a = l + (a - l) * k
    # contrast
    a = P['pivot'] + (a - P['pivot']) * P['contrast']
    a = np.clip(a, 0, None)
    # value
    a = a * (P['hull_value'] * m3 + P['city_value'] * (1 - m3))
    # highlight shoulder on luma
    kn, ce = P['knee'], P['ceil']
    if kn < ce:
        l = luma(a)
        span = ce - kn
        l2 = np.where(l > kn, kn + span * (1 - np.exp(-(l - kn) / span)), l)
        a = a * (l2 / np.maximum(l, 1e-4))[..., None]
    # haze
    hz = np.array(P['haze_rgb'], np.float32) / 255.0
    a = a * (1 - P['haze']) + hz * P['haze']
    # vignette + board falloff
    v = (1 - P['vignette'] * smooth(P['v0'], P['v1'], d)) * (1 - P['board_falloff'] * (1 - smooth(P['bx0'], P['bx1'], XX)))
    a = a * v[..., None]
    return np.clip(a * 255.0, 0, 255)


# ------------------------------------------------------------------------------------------------ O-30 fix 2: the default room grade of corp/src
# Per-room parameters as published in locked/backdrop/grade.json (version step6-1), solved by backdrop/src/bd_solve.py.
GRADE_VERSION = 'step6-1'
ROOMS = {
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


def room_key(path):
    """room_<n>_bare.png -> <n>"""
    import os
    b = os.path.basename(str(path))
    if b.startswith('room_') and b.endswith('_bare.png'):
        return b[5:-9]
    return 'bio'


def room_grade(opt='P'):
    """drop-in for r2_ground.grade(opt): the step-6 grade with the room's own parameters (room taken from the active bare path).
    The board scrim is unchanged (r2_ground.scrim).  Unknown rooms fall back to the bio parameters."""
    import r2_ground as G2
    import o_ground as OG
    path = getattr(OG, 'BARE_PATH', None) or getattr(G2, 'BARE_PATH', None)
    P = ROOMS.get(room_key(path), ROOMS['bio'])
    return grade(G2.bare().astype(np.float32), P)
