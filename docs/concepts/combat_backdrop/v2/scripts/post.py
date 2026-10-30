"""Post for one cutaway room: wet-street reflection, bloom, strong under-UI grade, board composite, squint.
usage: python post.py <name> [grade_v]     reads D:/rc_scratch/cutaway_kit/<name>_{main,refl,mask}.png
writes <v2>/room_<name>.png, room_<name>_bare.png, squint_<name>.png ; prints stats json."""
import sys, json, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb

sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/scripts')
import bd_common as B

V2 = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/'
SCR = 'D:/rc_scratch/cutaway_kit/'
PX = 50.0
TARGET = (1500.0, 612.0)
W_, D_ = 9, 7
Z_ROOM = 4.4
ZC = Z_ROOM + 0.9
COSEL, SINEL = 0.81650, 0.57735


def proj(x, y, z):
    sx = TARGET[0] + ((x - W_ / 2) + (y - D_ / 2)) * 0.70711 * PX
    sy = TARGET[1] - ((z - ZC) * COSEL + ((y - D_ / 2) - (x - W_ / 2)) * 0.70711 * SINEL) * PX
    return sx, sy


def load(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.float32) / 255


def lum(a):
    return a @ np.array([0.299, 0.587, 0.114], np.float32)


def sky():
    h, w = 1080, 1920
    t = np.linspace(0, 1, h)[:, None, None]
    top = np.array([0.045, 0.025, 0.10], np.float32)
    hor = np.array([0.20, 0.09, 0.30], np.float32)
    return np.broadcast_to(top * (1 - t) + hor * t, (h, w, 3)).copy()


def focus_mask():
    im = Image.new('L', (1920, 1080), 0)
    d = ImageDraw.Draw(im)
    pts = []
    for z in (0.25, Z_ROOM + 3.4):
        for (x, y) in ((-0.3, -0.3), (W_ + 0.3, -0.3), (W_ + 0.3, D_ + 0.3), (-0.3, D_ + 0.3)):
            pts.append(proj(x, y, z))
    pts = np.array(pts)
    # convex hull
    from scipy.spatial import ConvexHull
    hull = ConvexHull(pts)
    d.polygon([tuple(pts[i]) for i in hull.vertices], fill=255)
    m = np.asarray(im).astype(np.float32) / 255
    return ndi.gaussian_filter(m, 26)


def grade(img, focus, v_out=0.58, v_in=0.84, neon_pull=0.55, bld_pull=0.18):
    hsv = rgb_to_hsv(np.clip(img, 0, 1))
    neon = (hsv[..., 1] > 0.45) & (hsv[..., 2] > 0.55)
    neon = ndi.gaussian_filter(ndi.binary_dilation(neon, iterations=1).astype(np.float32), 1.0)
    pull = bld_pull * (1 - neon) + neon_pull * neon
    hsv[..., 1] = hsv[..., 1] * (1 - pull * (1 - 0.6 * focus))
    v = v_out * (1 - focus) + v_in * focus
    v = v * (1 - 0.12 * neon * (1 - focus))
    hsv[..., 2] = hsv[..., 2] * v
    return hsv_to_rgb(np.clip(hsv, 0, 1))


def run(name, v_out=0.58, v_in=0.84):
    main = load(SCR + name + '_main.png')
    refl = load(SCR + name + '_refl.png')
    mask = load(SCR + name + '_mask.png')[..., 3]
    a = main[..., 3:4]
    img = main[..., :3] * a + sky() * (1 - a)
    # wet street: blurred vertical-streak reflection of the mirrored scene, only where the street is visible
    rf = refl[..., :3] * refl[..., 3:4]
    rf = ndi.uniform_filter1d(rf, 34, axis=0)
    rf = ndi.gaussian_filter(rf, (2.5, 1.2, 0))
    yy, xx = np.mgrid[0:1080, 0:1920]
    rip = np.sin(yy / 9.0 + xx / 140.0) * 0.5 + 0.5
    rf = rf * (0.7 + 0.5 * rip[..., None])
    m = ndi.gaussian_filter(mask, 0.8)[..., None]
    fade = np.clip(1.0 - (yy - 560) / 700.0, 0.25, 1.0)[..., None]
    img = img * (1 - 0.15 * m) + rf * 0.55 * m * fade
    # streak glints on wet ground: horizontal blur of bright street pixels
    br = np.clip(img - 0.55, 0, None) * m
    img = img + 0.5 * ndi.uniform_filter1d(br, 90, axis=1) * m
    # bloom
    b = np.clip(img - 0.55, 0, None)
    img = img + 0.55 * ndi.gaussian_filter(b, (5, 5, 0)) + 0.45 * ndi.gaussian_filter(b, (20, 20, 0))
    img = np.clip(img, 0, 1)
    foc = focus_mask()
    bd = grade(img, foc, v_out, v_in)
    B.save(bd, V2 + 'room_%s_bare.png' % name)
    plate = B.compose(bd)
    B.save(plate, V2 + 'room_%s.png' % name)
    sq = B.squint(plate)
    B.save(sq, V2 + 'squint_%s.png' % name)
    st = B.stats(plate, name)
    print(json.dumps(st))
    return st


if __name__ == '__main__':
    n = sys.argv[1]
    vo = float(sys.argv[2]) if len(sys.argv) > 2 else 0.58
    run(n, vo)
