"""bd_measure: compose a graded room under an extracted board (plate = F + T * backdrop) and measure it.
Squint = the locked final_checks metric: 1/16 BOX downscale + 1 px gaussian, Rec709 luma, loud = cells above 0.38."""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
if SRC not in sys.path:
    sys.path.insert(0, SRC)
import numpy as np
from PIL import Image, ImageFilter
import bd_grade as BG

HERE = 'D:/rc_scratch/combat_redesign/locked/backdrop/'
V31 = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/'
ROOMS = ['bio', 'srv', 'gh', 'rec', 'lobby', 'event', 'shop']
C = (536, 540)
_G2 = None


def G2():
    global _G2
    if _G2 is None:
        cwd = os.getcwd()
        os.chdir(SRC)
        import r2_ground
        os.chdir(cwd)
        _G2 = r2_ground
    return _G2


def bare(room):
    return np.asarray(Image.open(V31 + 'room_%s_bare.png' % room).convert('RGB'), np.float32)


def before_backdrop(room):
    """the locked board's current backdrop: r2_ground.grade('P') + scrim('P') on this room"""
    g = G2()
    g.G._bare = bare(room)
    a = g.scrim(g.grade('P'), 'P')
    g.G._bare = None
    return np.clip(a, 0, 255)


def after_backdrop(room, P):
    return np.clip(G2().scrim(BG.grade(bare(room), P), 'P'), 0, 255)


_FG = {}


def fg(corp):
    if corp not in _FG:
        z = np.load(HERE + 'work/fg_%s.npz' % corp)
        _FG[corp] = (z['F'].astype(np.float32), z['T'].astype(np.float32))
    return _FG[corp]


def compose(bd, corp='neutral'):
    F, T = fg(corp)
    return np.clip(F + T * bd, 0, 255)


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def squint_grid(img):
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    s = im.resize((im.width // 16, im.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    return lum(np.asarray(s, np.float32) / 255.0)


def cellmask(mask):
    """mask (H,W bool) -> (68,120) cells at least 90 % inside"""
    m = Image.fromarray((mask * 255).astype(np.uint8)).resize((120, 67), Image.BOX)
    return np.asarray(m, np.float32) / 255 >= 0.9


def regions(corp='neutral'):
    F, T = fg(corp)
    vis = T.mean(-1) > 0.5
    m, _ = BG.hull(BG.BASE)
    rr = np.hypot(BG.XX - C[0], BG.YY - C[1])
    return dict(room=vis & (m > 0.5), backdrop_visible=vis, board=rr <= 500, rings=(rr >= 214) & (rr <= 430),
                plate=np.ones_like(vis))


def sq_stats(l, cm=None):
    v = l if cm is None else l[cm]
    return dict(mean=round(float(v.mean()), 4), p95=round(float(np.percentile(v, 95)), 4), loud=round(float((v > 0.38).mean()), 4))


def detail(img, mask):
    """legibility: RMS of the luma high-pass (full res minus a 6 px blur) inside mask, 0-1 units; and mean HSV saturation"""
    l = lum(img) / 255.0
    lb = np.asarray(Image.fromarray(np.clip(l * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    hp = (l - lb)[mask]
    mx, mn = img.max(-1), img.min(-1)
    S = ((mx - mn) / np.maximum(mx, 1))[mask]
    a = img / 255.0
    pk = (BG.pinkw(a) > 0.5) & (a.max(-1) > 0.15) & (((a.max(-1) - a.min(-1)) / np.maximum(a.max(-1), 1e-4)) > 0.35)
    dr = float(np.sqrt((hp ** 2).mean()))
    return dict(detail_rms=round(dr, 4), detail_rel=round(dr / max(float(l[mask].mean()), 1e-4), 4), sat=round(float(S.mean()), 4),
                pink_share=round(float(pk[mask].mean()), 5),
                luma_mean=round(float(l[mask].mean()), 4),
                luma_p99=round(float(np.percentile(l[mask], 99)), 4))


def measure(plate, corp='neutral', reg=None):
    reg = reg or regions(corp)
    l = squint_grid(plate)
    out = {}
    for k in ('plate', 'board', 'rings', 'room', 'backdrop_visible'):
        out[k] = sq_stats(l, cellmask(reg[k]))
    out['room_detail'] = detail(plate, reg['room'])
    b, r = out['board'], out['room']
    out['board_vs_room'] = dict(mean_ratio=round((b['mean'] + 0.05) / (r['mean'] + 0.05), 3),
                                p95_ratio=round((b['p95'] + 0.05) / (r['p95'] + 0.05), 3),
                                loud_ratio=round(b['loud'] / max(r['loud'], 1e-3), 2))
    return out
