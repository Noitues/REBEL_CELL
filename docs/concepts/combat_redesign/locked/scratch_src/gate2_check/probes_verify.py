"""probes_verify.py -- re-read every checks.json review_probes box with the reviewer's measure.py formula (percentile of L* over the whole box)
and compare with the stored L_box; also recompute the squint tower-zone share two ways (sRGB-encoded Rec.709 luma and linear luminance)."""
import json
import numpy as np
from PIL import Image, ImageFilter

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
ck = json.load(open(FINAL + 'checks.json', encoding='utf-8'))
PL = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p3': 'p3_resolve', 'p1_solace': 'p1_decide_solace', 'p1_meridian': 'p1_decide_meridian'}


def lum(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def lstar(y):
    return 116 * np.cbrt(y) - 16 if y > 0.008856 else 903.3 * y


worst = 0
for key, probes in ck['review_probes'].items():
    if key not in PL:
        continue
    rgb = np.asarray(Image.open(FINAL + PL[key] + '.png').convert('RGB')).astype(float)
    Y = lum(rgb)
    for nm, p in probes.items():
        if not isinstance(p, dict) or not p.get('box'):
            continue
        x0, y0, x1, y1 = p['box']
        r = Y[y0:y1, x0:x1]
        v = lstar(np.percentile(r, p['pct']))
        d = v - p['L_box']
        worst = max(worst, abs(d))
        flag = '' if abs(d) < 0.15 else '  <-- differs'
        print('%-12s %-48s box %-22s L_box stored %5.1f  re-read %5.1f%s' % (key, nm[:48], p['box'], p['L_box'], v, flag))
print('largest |difference| %.2f' % worst)
# squint
C = (536, 540)
for nm in ('p1_decide', 'p2_preview', 'p2b_hover', 'p3_resolve'):
    im = Image.open(FINAL + nm + '.png').convert('RGB')
    a = np.asarray(im).astype(float) / 255
    enc = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    lin = lum(a * 255)
    out = []
    for lab_, g in (('encoded', enc), ('linear', lin)):
        gi = Image.fromarray((g * 255).astype(np.uint8))
        sm = gi.resize((1920 // 16, 1080 // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1))
        s = np.asarray(sm).astype(float) / 255
        yy, xx = np.mgrid[0:s.shape[0], 0:s.shape[1]]
        cx, cy = (xx + 0.5) * 16, (yy + 0.5) * 16
        zone = np.hypot(cx - C[0], cy - C[1]) <= 212
        out.append('%s loud %.1f %%' % (lab_, 100 * float((s[zone] > 0.38).mean())))
    print('squint %-12s %s | checks.json %.1f %%' % (nm, ' / '.join(out), 100 * ck['squint_tower_zone'][nm]['final']))
