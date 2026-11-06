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
