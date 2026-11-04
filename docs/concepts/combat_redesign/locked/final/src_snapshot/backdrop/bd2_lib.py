"""bd2_lib (2026-11-03 rebuild stage 2, review 2.8): compose a graded room under the extracted current board (plate = F + T * backdrop) and
measure it the way rb_checks does on the published plates: the room region of rb_checks.family_regions (x >= 1100, y >= 420, outside the
HUD / hand / SEND IT / UNDO / nameplate / YOU / hover tag masks dilated 4 px, the UI scrim slabs, r > 505 from the board centre; taken
from rb_checks.family_regions, so it follows that definition), L* of the region's mean luminance and
its p95 L*; plus the reviewer's two probe boxes and the step-6 legibility numbers (detail_rel, saturation, pink share)."""
import sys, os, json
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
if SRC not in sys.path:
    sys.path.insert(0, SRC)
import numpy as np
from PIL import Image, ImageFilter
import bd_grade as BG
import rb_tokens as TK
import rb_checks as RC

HERE = 'D:/rc_scratch/combat_redesign/locked/backdrop/'
V31 = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/'
ROOMS = ['bio', 'srv', 'gh', 'rec', 'lobby', 'event', 'shop']
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


_BARE = {}


def bare(room):
    if room not in _BARE:
        _BARE[room] = np.asarray(Image.open(V31 + 'room_%s_bare.png' % room).convert('RGB'), np.float32)
    return _BARE[room]


def backdrop(room, P):
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


_REG = {}


def room_region(sfx='p1'):
    if sfx not in _REG:
        M = RC.load_masks(sfx)
        z = np.zeros((1080, 1920), bool)
        _REG[sfx] = RC.family_regions(M, None, None, z, z)['room']
    return _REG[sfx]


def spill_rgb(room, top=0.85, lum_target=0.30, P=None):
    """the room's own key light: mean colour of the brightest 15 % of hull pixels of the bare render (after the corp light, if any),
    scaled to luma lum_target (0-1)"""
    a = bare(room) / 255.0
    if P and P.get('hue_amt'):
        a = BG.corp_light(a, dict(BG.BASE, **P))
    m, _ = BG.hull(BG.BASE)
    l = BG.luma(a)
    sel = (m > 0.8)
    th = np.quantile(l[sel], top)
    c = a[sel & (l >= th)].mean(0)
    c = c * lum_target / max(float(BG.luma(c[None])[0]), 1e-4)
    return [int(round(v)) for v in np.clip(c * 255, 0, 255)]


def stats(plate, sfx='p1'):
    rgb = plate.astype(np.float64)
    Y = TK.lum(rgb)
    Ls = TK.lstar(Y)
    out = {}
    reg = room_region(sfx)
    out['room'] = dict(mean=round(float(TK.lstar(Y[reg].mean())), 2), p95=round(float(np.percentile(Ls[reg], 95)), 2))
    m, _ = BG.hull(BG.BASE)
    for nm, sel in (('room_hull', reg & (m > 0.5)), ('room_city', reg & (m <= 0.5))):
        out[nm] = dict(mean=round(float(TK.lstar(Y[sel].mean())), 2), p95=round(float(np.percentile(Ls[sel], 95)), 2))
    for nm, (x0, y0, x1, y1) in (('review_room_box', TK.REVIEW_ROOM_BOX), ('review_city_box', TK.REVIEW_CITY_BOX)):
        out[nm] = dict(mean=round(float(TK.lstar(Y[y0:y1, x0:x1].mean())), 2), p95=round(float(np.percentile(Ls[y0:y1, x0:x1], 95)), 2))
    # legibility inside the room hull (step-6 numbers): detail_rel = RMS luma high-pass / mean luma
    hm = reg & (m > 0.5)
    l = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    lb = np.asarray(Image.fromarray(np.clip(l * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float64) / 255
    hp = (l - lb)[hm]
    dr = float(np.sqrt((hp ** 2).mean()))
    mx, mn = rgb.max(-1), rgb.min(-1)
    S = ((mx - mn) / np.maximum(mx, 1))[hm]
    a = rgb / 255.0
    pk = (BG.pinkw(a) > 0.5) & (a.max(-1) > 0.15) & (((a.max(-1) - a.min(-1)) / np.maximum(a.max(-1), 1e-4)) > 0.35)
    out['detail'] = dict(detail_rms=round(dr, 4), detail_rel=round(dr / max(float(l[hm].mean()), 1e-4), 3), sat=round(float(S.mean()), 3),
                         pink_share=round(float(pk[hm].mean()), 5))
    return out
