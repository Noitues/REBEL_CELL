"""skin_tables: the baked numbers the Godot CombatCorpSkin / CombatLook resources need, computed with the locked generator's
own formulas (gram.kind_wash, corp_kinds.gained_wash, gramlib.grade + the f1_board COLD/FAR overrides, cs_skin.Meridian.hazard_paint).
Re-implemented here line for line (the generator modules are not imported, so nothing in corp/src runs or writes).
usage: python skin_tables.py <out_json>"""
import sys, json
sys.dont_write_bytecode = True
import numpy as np

SLATE = {'Packet': (61, 84, 102), 'Worm': (75, 74, 110), 'Jammer': (45, 93, 105), 'Payload': (91, 85, 96), 'Ring': (85, 97, 122)}
KINDS4 = ['Packet', 'Worm', 'Jammer', 'Payload']
GAINS = {'neutral': (1.0, 1.0, 1.0), 'solace': (2.4, 2.1, 2.0), 'meridian': (1.0, 1.1, 1.2)}
BED = (7, 9, 18)
HARM_UP = (255, 100, 82)
ENAMEL = (217, 225, 234)
COLD_CHEV = (217, 135, 124)
FAR_CHEV = (150, 118, 122)
_D65 = np.array([0.95047, 1.0, 1.08883])
_M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])


def kind_wash(kind, dep):                       # gram.kind_wash (CFG colour on, default ramp)
    base = SLATE.get(kind) or SLATE['Ring']
    k = (0.0, 0.20, 0.38)[dep]
    sat = (1.0, 0.62, 0.38)[dep]
    lum = 0.2126 * base[0] + 0.7152 * base[1] + 0.0722 * base[2]
    g = tuple(lum + (base[i] - lum) * sat for i in range(3))
    return tuple(int(round(v + ((10, 8, 30)[i] - v) * k * 0.9)) for i, v in enumerate(g))


def rgb2lab(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = (c @ _M.T) / _D65
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def lab2rgb(lab):
    fy = (lab[0] + 16) / 116
    fx, fz = fy + lab[1] / 500, fy - lab[2] / 200
    f = np.array([fx, fy, fz])
    xyz = np.where(f ** 3 > 216 / 24389, f ** 3, (116 * f - 16) / (24389 / 27)) * _D65
    c = np.linalg.solve(_M, xyz)
    c = np.clip(c, 0, 1)
    c = np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)
    return tuple(int(round(v * 255)) for v in np.clip(c, 0, 1))


def gained(kind, dep, g):
    w = kind_wash(kind, dep)
    if abs(g - 1.0) < 1e-6 or kind not in KINDS4:
        return w
    labs = np.array([rgb2lab(kind_wash(k, dep)) for k in KINDS4])
    m = labs.mean(0)
    return lab2rgb(m + g * (rgb2lab(w) - m))


def grade(c, k, bed=BED):                        # gramlib.grade + f1_board.grade2
    if k == 1 and tuple(c[:3]) == HARM_UP:
        return COLD_CHEV
    if k == 2 and tuple(c[:3]) == HARM_UP:
        return FAR_CHEV
    if k <= 0:
        return tuple(c[:3])
    sat, val = (1.0, 0.45, 0.25)[k], (1.0, 0.70, 0.50)[k]
    lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    g = tuple(lum + (c[i] - lum) * sat for i in range(3))
    return tuple(int(round(bed[i] + (g[i] - bed[i]) * val)) for i in range(3))


def hexs(c):
    return '#%02X%02X%02X' % tuple(int(round(v)) for v in c)


def main(out):
    res = dict(kind_wash={}, time_grade={}, meridian_hazard_paint=None)
    for sk, gs in GAINS.items():
        res['kind_wash'][sk] = {k: [hexs(gained(k, d, gs[d])) for d in range(3)] for k in KINDS4 + ['Ring']}
    for nm, c in (('harm', HARM_UP), ('enamel', ENAMEL)):
        res['time_grade'][nm] = [hexs(grade(c, k)) for k in range(3)]
    c = np.array((255, 140, 26), np.float64)
    y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    res['meridian_hazard_paint'] = hexs(c * 0.75 + y * 0.25)
    json.dump(res, open(out, 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
