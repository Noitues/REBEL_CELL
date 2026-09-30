"""Two variants of the hidden (out-of-district) city, in colour instead of grey.

  A  city_day_hidden_lines.png    coloured, translucent, slightly desaturated, thin light ink
  B  city_day_hidden_nolines.png  coloured, translucent, slightly desaturated, no ink at all
The lit district, overlay, projection and boundary are untouched (same code path as wide.py).
If ../../r2_helix_blender/helix_rgba.png + anchor.json exist, the Blender helix replaces the Pillow one.
Usage: python hidden.py
"""
import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image
from lowpoly import SS, W, H, hexc, mix, hsh, facet, line2, finalize
import toon
import wide
from city import CityPainter, lot_rect, bil3, LX, LY, NBX, NBY, THEMES

ROOT = os.path.dirname(HERE)
BLENDER = os.path.join(os.path.dirname(ROOT), 'r2_helix_blender')
HIDDEN_INK = hexc('#6e665a')
MODE = {'lines': True}


def hidden_col(c):
    """Keep the district palette, lift and desaturate it a little."""
    lum = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    grey = (lum, lum, lum)
    c = mix(c, grey, 0.3)
    return mix(c, hexc('#cfc6ae'), 0.12)


def hidden_box(self, p):
    CityPainter.box(self, p)
    if not MODE['lines']:
        return
    cam = self.cam
    x0, y0, x1, y1, z0, z1 = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1']
    hp = toon.hull([cam.p(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])
    for k in range(len(hp)):
        line2(self.d, hp[k], hp[(k + 1) % len(hp)], 1.3, HIDDEN_INK)
    tp = [cam.p(x0, y1, z1), cam.p(x1, y1, z1), cam.p(x1, y0, z1)]
    line2(self.d, tp[0], tp[1], 0.9, HIDDEN_INK)
    line2(self.d, tp[1], tp[2], 0.9, HIDDEN_INK)
    line2(self.d, cam.p(x1, y1, z0), tp[1], 0.9, HIDDEN_INK)


def hidden_ground(gp):
    cam = gp.cam
    th = THEMES['day']
    q = [(-120, LY + 80, 0), (LX + 120, LY + 80, 0), (LX + 120, -120, 0), (-120, -120, 0)]
    facet(gp.d, lambda u, v: cam.p(*bil3(q, u, v)), 60, 50,
          lambda u, v, i, j, k, rc: hidden_col(wide.ramp(th['street'], 0.45 + rc.uniform(-0.06, 0.06))), 'gground', 0.35)
    for by in range(-12, NBY + 7):
        for bx in range(-9, NBX + 9):
            if 0 <= bx < NBX and 0 <= by < NBY:
                continue
            x0, y0, x1, y1 = lot_rect(bx, by)
            pts = [cam.p(x0, y1, 0.02), cam.p(x1, y1, 0.02), cam.p(x1, y0, 0.02), cam.p(x0, y0, 0.02)]
            if max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > W + 50 or max(p[1] for p in pts) < -50 \
                    or min(p[1] for p in pts) > H + 50:
                continue
            c = hidden_col(wide.ramp(th['lot'], 0.55 + 0.1 * hsh(bx, by, 3)))
            gp.d.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=c, outline=c)
            if MODE['lines']:
                for k in range(4):
                    line2(gp.d, pts[k], pts[(k + 1) % 4], 0.9, HIDDEN_INK)


# ---- optional Blender helix
def blender_helix():
    png, js = os.path.join(BLENDER, 'helix_rgba.png'), os.path.join(BLENDER, 'anchor.json')
    if not (os.path.exists(png) and os.path.exists(js)):
        return None
    with open(js) as f:
        return Image.open(png).convert('RGBA'), json.load(f)


BL = blender_helix()
_orig_hq = wide.DistrictPainter.hq


def hq_patch(self, p):
    if BL is None:
        return _orig_hq(self, p)
    im, a = BL
    ox, oy = a['paste_topleft_city_px']     # 1080p screen px, may be negative
    im2 = im.resize((im.width * SS, im.height * SS), Image.LANCZOS)
    self.img.alpha_composite(im2, (int(ox * SS), int(oy * SS)), (0, 0)) if ox >= 0 and oy >= 0 else         self.img.alpha_composite(im2.crop((max(0, -ox) * SS, max(0, -oy) * SS, im2.width, im2.height)),
                                 (max(0, ox) * SS, max(0, oy) * SS))
    bb = im.getbbox()
    bx, by = a['base_center_city_px']
    self.hq_top = (bx, oy + bb[1])
    self.hq_bbox = (ox + bb[0] - 60, oy + bb[1] - 90, ox + bb[2] + 60, by + 80)


def main():
    toon.ghost_col = hidden_col
    wide.GhostPainter.box = hidden_box
    wide.ghost_ground = hidden_ground
    wide.DistrictPainter.hq = hq_patch
    for lines, name in ((True, 'city_day_hidden_lines.png'), (False, 'city_day_hidden_nolines.png')):
        MODE['lines'] = lines
        finalize(wide.render()).save(os.path.join(ROOT, name), optimize=True)
        print('wrote', name, '(blender helix)' if BL else '(pillow helix)')


if __name__ == '__main__':
    main()
