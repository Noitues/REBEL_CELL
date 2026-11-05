"""sbkit: the netrun street frame (v3 storyboard: the r6 street render with the mock room tags, COMP) and the T4 iris / zoom, read-only
from transitions/v3/scripts (helpers3).  Used for the T6 pull-out (T4 reversed) and the storyboard."""
import sys
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/transitions/v3/scripts')
import helpers3 as H3
import numpy as np
from PIL import Image, ImageDraw

W, H = H3.W, H3.H
ROOMS = [(.378, 'FIGHT'), (.592, 'EVENT'), (.823, 'SHOP')]
street_raw = H3.L('netrun_cel/zoom_rules/round6/street_frame.png')


def street(sel=None, ribbon=True, cleared=None):
    """build_sb / build3 street(): unchanged"""
    im = H3.glow_line(street_raw, [(.02, .96), (.3, .92), (.5, .90), (.72, .92), (.98, .96)]) if ribbon else street_raw.copy()
    d = ImageDraw.Draw(im)
    for i, (xr, tag) in enumerate(ROOMS):
        x = xr * W
        d.rectangle((x - 78, 742, x + 78, 858), outline=H3.LIME, width=5)
        d.rectangle((x - 78, 706, x + 78, 742), fill=(10, 40, 20))
        d.text((x - 62, 710), tag, font=H3.MF(24), fill=H3.LIME)
        if cleared == i:
            d.line((x + 30, 716, x + 42, 732, x + 62, 706), fill=H3.LIME, width=6)
    if sel is not None:
        x = ROOMS[sel][0] * W
        d.rectangle((x - 90, 694, x + 90, 868), outline=(255, 255, 255), width=8)
        d.rectangle((x - 94, 690, x + 94, 872), outline=(255, 46, 158), width=3)
    return im


STREET_CLEARED = street(cleared=0)


def zoom_street(z):
    """the street framed on the FIGHT room at zoom z (v3 T4: zc on the room box), with the v3 zoom blur while moving"""
    im = H3.zc(STREET_CLEARED, ROOMS[0][0], .73, z) if z > 1.001 else STREET_CLEARED.copy()
    return im


STREET_BARE = street_raw.copy()                     # the r6 street with no street HUD (no ribbon, no room tags)
PULL_T = (0.48, 0.66, 0.62, 0.80)                   # iris closes 0.48-0.66 s; pull-out 0.62-0.80 s (the v3 / round-1 timing)
HUD_LOW = 0.40                                      # T4 dims the street HUD to 40 % as it pushes in; T6 (T4 reversed) brings it back up


def _zoom_at(t):
    u = float(min(max((t - PULL_T[2]) / (PULL_T[3] - PULL_T[2]), 0), 1))
    return 3.4 + (1.0 - 3.4) * (1 - (1 - u) ** 3)


def _hud_at(t):
    u = float(min(max((t - PULL_T[2]) / (PULL_T[3] - PULL_T[2]), 0), 1))
    return HUD_LOW + (1 - HUD_LOW) * u * u * (3 - 2 * u)


import os as _os
SHUTTER = float(_os.environ.get('PULL_SHUTTER', '0.04'))
SHUTTER_N = int(_os.environ.get('PULL_N', '5'))


def street_view(t, shutter=None, n=None):
    """round 2 (C13): the street as the camera pulls back, T4 reversed.  The street HUD (ribbon, room tags) at _hud_at(t) over the bare
    street; the zoom is motion-blurred over the frame's exposure (n samples across `shutter` s, centred on t, clipped to the pull-out).
    t >= the end: exactly STREET_CLEARED (the framing T4 started from)."""
    shutter = SHUTTER if shutter is None else shutter
    n = SHUTTER_N if n is None else n
    if t >= PULL_T[3] - 1e-9:
        return STREET_CLEARED.copy()
    a = _hud_at(t)
    acc = None
    ts = [t] if n <= 1 else [min(max(t + shutter * (k / (n - 1) - 0.5), 0.0), PULL_T[3]) for k in range(n)]
    for ti in ts:
        z = _zoom_at(ti)
        s0 = np.asarray(H3.zc(STREET_BARE, ROOMS[0][0], .73, z) if z > 1.001 else STREET_BARE).astype(np.float32)
        s1 = np.asarray(zoom_street(z)).astype(np.float32)
        f = s0 + (s1 - s0) * a
        acc = f if acc is None else acc + f
    return Image.fromarray(np.clip(acc / len(ts) + 0.5, 0, 255).astype(np.uint8))


def iris2(street_im, room_view, r, edge='ink', feather=24.0):
    """the T4 iris without its bright ring: room_view inside the circle (radius r * W round the frame centre), the street outside.
    edge 'ink': a 6 px INK #0C0A16 ring; 'soft': a feathered edge (feather px), no ring; 'lime': the v3 lime ring (round 1)"""
    if edge == 'lime':
        return H3.iris(street_im, room_view, r, col=H3.LIME)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot(xx - W / 2, yy - H / 2)
    R_ = r * W
    if edge == 'soft':
        m = np.clip((R_ - d) / feather + 0.5, 0, 1)
    else:
        m = np.clip(R_ - d + 0.5, 0, 1)
    a = np.asarray(street_im).astype(np.float32); b = np.asarray(room_view).astype(np.float32)
    out = a + (b - a) * m[..., None]
    if edge == 'ink':
        ring = np.clip(3.0 + 0.5 - np.abs(d - R_), 0, 1)
        out = out + (np.array([12, 10, 22], np.float32) - out) * ring[..., None]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8))


def pull_out2(room_view, t, edge='ink'):
    """round 2 (C13) attempt at the T4-reverse inside T6: the iris closes 0.48-0.66 s with no bright ring, over the street at 3.4x with its
    HUD at 40 %; 0.62-0.80 s the camera pulls back to 1x (motion-blurred) while the street HUD comes back to 100 %"""
    if t < PULL_T[0]:
        return room_view
    v = float(min(max((t - PULL_T[0]) / (PULL_T[1] - PULL_T[0]), 0), 1))
    r = (1 - v ** 2) * 0.575
    st = street_view(t)
    if r <= 0.002:
        return st
    return iris2(st, room_view, r, edge)


def pull_out(room_view, t):
    """T6 after the dissolve: T4 run in reverse.  0.48-0.66 s the room view closes in the T4 iris (lime ring) over the street at 3.4x;
    0.62-0.80 s the camera pulls back from 3.4x to the street framing T4 started from.  room_view: RGB uint8 PIL image."""
    if t < 0.48:
        return room_view
    u = float(min(max((t - 0.62) / 0.18, 0), 1))
    z = 3.4 + (1.0 - 3.4) * (1 - (1 - u) ** 3)
    st = zoom_street(z)
    if z > 1.05:
        st = H3.zblur(st, 0.05 * (z - 1) / 2.4)
    v = float(min(max((t - 0.48) / 0.18, 0), 1))
    r = (1 - v ** 2) * 0.575                         # iris radius / W: 0.575 W covers the frame (half diagonal 1101 px), then closes
    if r <= 0.002:
        return st
    return H3.iris(st, room_view, r, col=H3.LIME)
