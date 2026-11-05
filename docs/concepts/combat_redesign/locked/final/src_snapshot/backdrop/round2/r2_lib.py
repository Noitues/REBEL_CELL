"""r2_lib (2026-11-04 round 2, backdrop stage): compose a graded room under the extracted round-2 p1 board (plate = F + T * backdrop) and
measure it on the plate the way rb_checks does.

  room (gate)   rb_checks.family_regions 'room': x >= 1100, y >= 420, r > 505 from (536, 540), the HUD / hand / SEND IT / UNDO / nameplate /
                YOU / hover tag masks dilated 4 px cut out, and the UI scrim slabs where they darken the room by 15 % or more cut out
  room as seen  the same region with the UI scrim slabs kept ('room as seen (scrim kept, info)'), as the player sees it
L* is CIE L* of the region's mean luminance (reviewer measure.py); p95 is the 95th percentile of per-pixel L*.  The masks are the round-2
p1 captures of each skin, snapshotted from corp/work into round2/backdrop/work/caps/ (rb_checks.WORK points there in this process, so the
checks do not read files another stage may rewrite).  Nothing in corp/src is written."""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
BSRC = 'D:/rc_scratch/combat_redesign/locked/backdrop/src'
if SRC not in sys.path:
    sys.path.insert(0, SRC)
import numpy as np
from PIL import Image, ImageFilter
import bd_grade as BG
import rb_tokens as TK
import rb_checks as RC

HERE = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/'
CAPS = HERE + 'work/caps/'
RC.WORK = CAPS
V31 = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/'
ROOMS = ['bio', 'srv', 'gh', 'rec', 'lobby', 'event', 'shop']
SFX = {'neutral': 'p1', 'solace': 'p1_solace', 'meridian': 'p1_meridian'}
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
    """the backdrop layer as the board renders it: bd_grade.grade (rb2-1) then the board scrim r2_ground.scrim('P'), cast to uint8 the way
    r2_ground.backdrop casts it (np.clip then astype: truncation)"""
    return np.clip(G2().scrim(BG.grade(bare(room), P), 'P'), 0, 255).astype(np.uint8).astype(np.float32)


_FG = {}


def fg(corp):
    if corp not in _FG:
        z = np.load(HERE + 'work/fg_%s.npz' % corp)
        _FG[corp] = (z['F'].astype(np.float32), z['T'].astype(np.float32))
    return _FG[corp]


def compose(bd, corp='neutral'):
    F, T = fg(corp)
    return np.clip(np.rint(F + T * bd), 0, 255)


_REG = {}


def regions(sfx):
    if sfx not in _REG:
        M = RC.load_masks(sfx)
        assert M, 'no masks for ' + sfx
        z = np.zeros((1080, 1920), bool)
        fam = RC.family_regions(M, None, None, z, z)
        _REG[sfx] = (fam['room'], fam['room as seen (scrim kept, info)'])
    return _REG[sfx]


def _row(Y, Ls, sel):
    return dict(mean=round(float(TK.lstar(Y[sel].mean())), 2), p95=round(float(np.percentile(Ls[sel], 95)), 2),
                median=round(float(np.median(Ls[sel])), 2), px=int(sel.sum()))


def stats(plate, sfx='p1'):
    rgb = plate.astype(np.float64)
    Y = TK.lum(rgb)
    Ls = TK.lstar(Y)
    out = {}
    reg, seen = regions(sfx)
    out['room'] = _row(Y, Ls, reg)
    out['room_as_seen'] = _row(Y, Ls, seen)
    m, _ = BG.hull(BG.BASE)
    out['room_hull'] = _row(Y, Ls, reg & (m > 0.5))
    out['room_city'] = _row(Y, Ls, reg & (m <= 0.5))
    for nm, (x0, y0, x1, y1) in (('review_room_box', TK.REVIEW_ROOM_BOX), ('review_city_box', TK.REVIEW_CITY_BOX)):
        out[nm] = dict(mean=round(float(TK.lstar(Y[y0:y1, x0:x1].mean())), 2), p95=round(float(np.percentile(Ls[y0:y1, x0:x1], 95)), 2))
    # legibility in the room hull: detail_rel = RMS luma high-pass (full res minus a 6 px blur) / mean luma; saturation; pink share
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
                         pink_share=round(float(pk[hm].mean()), 5), hull_px=int(hm.sum()))
    # the room's hue identity at the box: median sRGB and Lab hue of the hull pixels in the gate region
    med = np.median(rgb[hm], 0)
    lab = TK.lab(med) if hasattr(TK, 'lab') else None
    out['hull_median_rgb'] = [int(round(v)) for v in med]
    if lab is not None:
        lab = [float(v) for v in np.ravel(lab)[:3]]
        out['hull_median_lab'] = dict(L=round(lab[0], 1), C=round(float(np.hypot(lab[1], lab[2])), 1),
                                      h=round(float(np.degrees(np.arctan2(lab[2], lab[1])) % 360), 1))
    return out


def squint(plate, corp):
    """the locked final_checks squint, reported (1/16 BOX + 1 px blur, Rec709 luma, loud > 0.38), with the backdrop-visible room from T"""
    sys.path.insert(1, BSRC)
    import bd_measure as M
    M._FG[corp] = fg(corp)
    return M.measure(plate, corp, M.regions(corp))
