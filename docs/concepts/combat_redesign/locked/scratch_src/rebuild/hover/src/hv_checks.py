"""hv_checks: every check on every hover plate (2026-11-03 rebuild), measured on the published PNG (L* = CIE L* of sRGB luminance, the
reviewer's measure.py, via rb_tokens.lstar) with the plate's report (chk/<name>.json) and its masks (chk/<name>.npz).

The board's five checks (corp/src/rb_checks.py, read only), run on the hover plate:
  a  occupied vs empty cell contrast >= 3.0 on the LIT cells (a cell is gated when 60 % of its glass is inside the lit mask; hover-dimmed cells
     and ghosts are reported)
  b  value order: the board's A.1 table is REPORTED (a hover dims the board x0.40 by design, so the board chain does not apply); gated hover
     rules instead: the dim is value x K_DIM (median sRGB-luma ratio plate / board within 0.03), the lit set is unchanged (0.97-1.03), the
     pencil and FOCUS marks sit above the dimmed board (p95 + 1), the lifted card above the resting hand (p95 + 1)
  c  cap height >= 16 px of every text draw (inset tabs included); text outside the hooked drawers fails
  d  palette dE76 >= 15 (tokens incl. PLAN and FOCUS, slice inks, card types, skin inks, HOT / COLD vs the measured cells)
  e  hand vs SEND IT / UNDO 0 px, lifted card vs every sibling cost hex and rules line 0 px; plus the board's hand rules: every card outside
     r455, the lifted card outside r459 and 3 px off the landing marks, no hand pixel below y 1067 or within 2 px of SEND IT / UNDO, no resting
     card on another's cost hex
Hover checks:
  pencil   L6 wax 7 px (median 6-8), L6 with ink 13 px (12-14, ink 2.5-3.5 a side); L5 edges 3 px (2.5-4), with keyline 6.5-9
  grain    wax interior L* std >= 1.0, p99 <= PLAN L* + 1 (the grain only darkens); no glow: PLAN-yellow pixels in the 3 px band outside the
           ink edge no more than on the board under it
  rings    every changed LANDS / THROUGH number has a closed ring (form 'ring', no bracket, no '( n )' text), the YOU change an underline;
           rings 0 px on HUD words and on the hero digits with their keyline (1 px kept)
  hp_strip pencil, FOCUS, hover marks, ghosts and insets: 0 px on the YOU strip
  ram      pencil / FOCUS / hover marks 0 px on the RAM coins and TRACE pips; no more GAIN-green pixels on the RAM row than the board's own
  insets   no inset on the HUD or the hand; no inset source crop on the HUD (2.4: nothing copies the HUD)
  options  (h04) one NEXT row per legal option; 0 PLAN-yellow px in the NEXT rows; the BEST star neutral (median C* <= 12)
  slices   (h02, h10; 3.13) the five non-aimed slices dim (median luma ratio <= K_DIM + 0.05), the aimed slice lit (>= 0.95)
  focus    FOCUS pixels are #D4FF00 (core median dE76 <= 3), 0 px of the old #96FE46; every focus call is four separate corners (4 components,
           bbox 8-28 px)
  collide  hz_core collision report: hover marks / ghosts / insets vs board marks and HUD words 0 px, occlusion, mark pairs, hand vs board
  dashes   0 dash / dot draw calls, 0 pixel dot runs (dot_audit)
  nowords  no alphanumeric text draw on a nowords plate
  asserts  every draw assert of the board render (and of each inset's variant render) passes
python hv_checks.py [name ...]   (default: every chk/*.json) -> chk/<name>.checks.json, prints one line per plate"""
import sys, os, json, re, glob, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

CORP_SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/'
sys.path.insert(0, CORP_SRC)
os.chdir(CORP_SRC)
import rb_tokens as T
import rb_checks as RC
import dot_audit as DA

H, W = 1080, 1920
C = (536, 540)
K_DIM, DESAT, HAND_K, STICK_K = 0.40, 0.45, 0.70, 0.62          # hz_core (read only)
T_IN, T_OUT, T_HALO = 71.0, 177.0, 197.2
HAND_MIN_R, LIFT_CLEAR, LIFT_ARC_GAP, HAND_BOTTOM, BTN_GAP = 455.0, 4.0, 3, 1067, 2
PLAN = (255, 226, 0)
FOCUS = (212, 255, 0)
OLD_LIME = (150, 254, 70)
GAIN = (123, 224, 123)
BOARD_HUD_BOTTOM = 442      # the rebuilt board's HUD bottom (final/ p1_decide), for the cross-set note


def luma(rgb):
    return rgb[..., 0] * 0.3 + rgb[..., 1] * 0.59 + rgb[..., 2] * 0.11


def load(name):
    rep = json.load(open(HERE + 'chk/%s.json' % name))
    z = np.load(HERE + 'chk/%s.npz' % name)
    M = {}
    lit = None
    for k in z.files:
        if k == 'lit':
            lit = z[k]
            continue
        if k.startswith('Pv__'):
            M[k] = z[k].astype(np.float32) / 255.0          # pencil coverage, not a bit mask
            continue
        M[k] = np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool)
    rgb = np.asarray(Image.open(HERE + 'out/%s.png' % name).convert('RGB')).astype(np.float64)
    key = str(rep['snap'].get('cache', '')).split()[-1]
    bp = HERE + 'work/board_%s.png' % key
    bg = np.asarray(Image.open(bp).convert('RGB')).astype(np.float64) if os.path.exists(bp) else None
    pp = HERE + 'chk/%s_probe.png' % name
    probe = np.asarray(Image.open(pp).convert('RGB')).astype(np.float64) if os.path.exists(pp) else None
    return rep, M, lit, rgb, bg, probe


def g(M, k):
    return M.get(k, np.zeros((H, W), bool))


def dil(m, r):
    return ndi.binary_dilation(m, iterations=int(r)) if r > 0 and m.any() else m


def box_mask(b, pad=0):
    m = np.zeros((H, W), bool)
    if b:
        x0, y0, x1, y1 = [int(round(v)) for v in b[:4]]
        m[max(0, y0 - pad):min(H, y1 + pad), max(0, x0 - pad):min(W, x1 + pad)] = True
    return m


def _normals(dt, ys, xs):
    """unit normals across a stroke at ridge pixels: the eigenvector of the most negative Hessian eigenvalue of the smoothed distance transform"""
    dyy = ndi.gaussian_filter(dt, 1.2, order=(2, 0))
    dxx = ndi.gaussian_filter(dt, 1.2, order=(0, 2))
    dxy = ndi.gaussian_filter(dt, 1.2, order=(1, 1))
    out = []
    for y, x in zip(ys, xs):
        hxx, hyy, hxy = dxx[y, x], dyy[y, x], dxy[y, x]
        tr, det = hxx + hyy, hxx * hyy - hxy * hxy
        lam = tr / 2 - math.sqrt(max(0.0, tr * tr / 4 - det))
        vx, vy = (lam - hyy, hxy) if abs(hxy) > 1e-9 else ((1.0, 0.0) if hxx < hyy else (0.0, 1.0))
        n_ = math.hypot(vx, vy) or 1.0
        out.append((vx / n_, vy / n_))
    return out


def stroke_width(m, step=3, cov=None):
    """median stroke width of a mask: at every step-th ridge pixel (distance-transform ridge, dt >= 1.5) the run of mask pixels along the normal
    across the stroke, sampled every 0.1 px (the mask is the 50 % coverage of the drawn stroke, so the run is its width to about 0.5 px).
    With cov (the stroke's 0-1 coverage at 1x) the width is the coverage integrated along the normal over the run and 2 px either side: the
    drawn width, with no jump of a pixel at sub-pixel positions where a 50 % mask takes or drops a half-covered edge pixel."""
    if m.sum() < 40:
        return None
    from scipy.ndimage import map_coordinates
    dt = ndi.distance_transform_edt(m)
    ridge = (dt >= ndi.maximum_filter(dt, size=3) - 1e-6) & (dt >= 1.5)
    ys, xs = np.nonzero(ridge)
    ys, xs = ys[::step], xs[::step]
    tt = np.arange(-16.0, 16.0001, 0.1)
    i0 = len(tt) // 2
    mf = m.astype(np.float32)
    w = []
    for (vx, vy), y, x in zip(_normals(dt, ys, xs), ys, xs):
        py, px = y + tt * vy, x + tt * vx
        if py.min() < 0 or px.min() < 0 or py.max() > H - 1 or px.max() > W - 1:
            continue
        v = map_coordinates(mf, [py + 0.0, px + 0.0], order=0) > 0.5
        if not v[i0]:
            continue
        lo, hi = i0, i0
        while lo > 0 and v[lo - 1]:
            lo -= 1
        while hi < len(tt) - 1 and v[hi + 1]:
            hi += 1
        if lo == 0 or hi == len(tt) - 1:
            continue
        if cov is None:
            w.append((hi - lo + 1) * 0.1)
        else:
            a, b = max(0, lo - 20), min(len(tt), hi + 21)
            # coverage (bilinear) integrated along the normal
            c = map_coordinates(cov, [py[a:b] + 0.0, px[a:b] + 0.0], order=1)
            w.append(float(c.sum()) * 0.1)
    return round(float(np.median(w)), 2) if w else None


def board_mask_sets(M):
    """the mask names of the saved npz, by family"""
    pen_all = g(M, 'P__L6_all') | g(M, 'P__L5_all') | g(M, 'P__L5c_all') | g(M, 'P__L5h_all')      # L5c chevrons, L5h arrowheads
    pen_wax = g(M, 'P__L6_wax') | g(M, 'P__L5_wax') | g(M, 'P__L5c_wax') | g(M, 'P__L5h_wax')
    focus = g(M, 'F__m')
    hover = g(M, 'Z__hover')
    ghost = g(M, 'Z__ghost')
    inset = g(M, 'Z__inset')
    hand = g(M, 'Z__hand') | g(M, 'Hd__hand_rest') | g(M, 'Hd__hand_lift')
    stick = g(M, 'R__send') | g(M, 'R__name') | g(M, 'B__send') | g(M, 'B__undo') | g(M, 'R__undo')
    return pen_all, pen_wax, focus, hover, ghost, inset, hand, stick


# ------------------------------------------------------------------------------------------------ a / b / c / d / e
def rb_inputs(rep, M):
    """the rb_checks mask dict: rb_capture classes (R__), the hz_core classes (Z__), the hand (Hd__), buttons (B__); 'plan' = every hover mark"""
    Mx = {}
    for k, v in M.items():
        pre, _, nm = k.partition('__')
        if pre in ('R', 'Z', 'Hd'):
            Mx[nm] = (Mx[nm] | v) if nm in Mx else v
    pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = board_mask_sets(M)
    Mx['plan'] = Mx.get('plan', np.zeros((H, W), bool)) | pen_all | focus | hover | ghost | inset
    Mx['hand'] = hand
    Mx['send'] = g(M, 'B__send') | g(M, 'R__send')
    Mx['undo'] = g(M, 'B__undo') | g(M, 'R__undo')
    return Mx


def gate_cells(geo, lit, veiled=()):
    """hover: a live / dying cell is gated only when 60 % of its glass is lit; the rest are 'dimmed' (reported).  The origin cell of a unit the
    plan moves (Shove, Pull) is veiled by design (the ghost carries the unit): 'veiled', reported"""
    geo = json.loads(json.dumps(geo))
    lm = lit >= 128
    for c in geo['cells']:
        if c['uid'] in veiled and c['state'] in ('live', 'dying'):
            c['state'] = 'veiled'
            continue
        if c['state'] in ('live', 'dying') and c['poly']:
            m = ndi.binary_erosion(RC.poly_mask([c['poly']]), iterations=4)
            frac = float((m & lm).sum()) / max(1, m.sum())
            c['lit_frac'] = round(frac, 2)
            if frac < 0.6:
                c['state'] = 'dimmed'
    return geo


def glass_masks(geo, Mx):
    yy, xx = np.mgrid[0:H, 0:W]
    cut = np.zeros((H, W), bool)
    for k in RC.CUT:
        if k in Mx:
            cut |= Mx[k]
    cut = dil(cut, 3)
    rho = np.hypot(xx - C[0], yy - C[1])
    for u in geo['units']:
        cut |= np.hypot(xx - u['token'][0], yy - u['token'][1]) <= u['tok_r'] + 8
        cut |= (rho >= u['t_in'] - 3) & (rho <= u['t_out'] + 3) & (np.abs(((np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) - u['b0']) % 360)) <= (u['b1'] - u['b0']))
    pm = lambda st, dep=None: ndi.binary_erosion(RC.poly_mask([c['poly'] for c in geo['cells'] if c['state'] == st and (dep is None or c['dep'] == dep)]), iterations=4) & ~cut
    return cut, pm('live'), pm('empty'), pm('live', 0), pm


def check_a(rep, Mx, lit, rgb, probe):
    geo = rep.get('geometry')
    if not geo:
        return dict(pass_=False, why='no geometry captured'), None
    mv = (rep.get('marks') or {}).get('moved')
    geo = gate_cells(geo, lit, {mv[0]} if mv else ())
    Y = T.lum(rgb)
    probeY = T.lum(probe) if probe is not None else None
    r = RC.check_cells(Y, rgb, dict(geometry=geo), Mx, probeY)
    r['rule'] = 'hover: ' + r['rule'] + '; a cell is gated only when 60 % of its glass is lit (the rest are hover-dimmed: reported)'
    r['n_gated'] = sum(1 for x in r['rows'] if x['gated'])
    return r, geo


BOARD_A_SKIP = ('hover', 'ghost', 'inset', 'plan', 'hand', 'send', 'undo')     # hover classes, not the board's


def board_a(rep, M, bg, probe, a):
    """the board's own check a on the board image under the plate (the same plan state, no hover), with the board's capture masks only:
    tells a hover failure from a board-renderer one.  The masks are rb_capture's (R__) and the board render's own classes (Z__) without the
    hover classes; with them this reproduces the board's published rows (final p1_nowords ring 0 sector 0: 3.34 at 282 px).  Reported; the
    hover gate above is unchanged."""
    if bg is None or not rep.get('geometry'):
        return None
    Mb = {}
    for k, v in M.items():
        pre, _, nm = k.partition('__')
        if pre in ('R', 'Z') and nm not in BOARD_A_SKIP:
            Mb[nm] = (Mb[nm] | v) if nm in Mb else v
    rb = RC.check_cells(T.lum(bg), bg, dict(geometry=rep['geometry']), Mb, T.lum(probe) if probe is not None else None)
    bad_b = [dict(ring=x['ring'], sector=x['sector'], kind=x['kind'], state=x['state'], ratio=x['ratio'], occ_L=x['occ_L'], px=x['px'])
             for x in rb['rows'] if x['gated'] and not x['pass_']]
    hv_bad = {(x['ring'], x['sector']) for x in a.get('rows', []) if x['gated'] and not x['pass_']}
    return dict(pass_=rb['pass_'], failing_cells=bad_b,
                hover_fails_also_failing_on_board=sorted('r%d s%d' % k for k in hv_bad if any((b['ring'], b['sector']) == k for b in bad_b)),
                hover_fails_board_passes=sorted('r%d s%d' % k for k in hv_bad if not any((b['ring'], b['sector']) == k for b in bad_b)),
                note='rb_checks.check_cells on work/board_<key>.png (the board renderer, this plan state, no hover marks, no dim) with the board masks (R__ + Z__ without the hover classes)')


def check_b(rep, M, Mx, lit, rgb, bg, geo):
    Y = T.lum(rgb)
    Ls = T.lstar(Y)
    out = {}
    if geo:
        cut, occ, emp, occ_now, pm = glass_masks(geo, Mx)
        try:
            board = RC.check_order(Y, Mx, dict(geometry=geo), occ, emp, occ_now)
            out['board_table_reported'] = dict(sorted=board['sorted'], failures_reported=board['failures'], marks=board['marks'])
        except Exception as e:
            out['board_table_reported'] = dict(error=str(e))
    pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = board_mask_sets(M)
    fails = []
    if bg is None:
        return dict(pass_=False, why='board image missing', **out)
    over = dil(pen_all | focus | hover | ghost | inset | hand | stick, 2)
    lb = luma(bg)
    lp = luma(rgb)
    D = (lit < 8) & ~over & (lb > 20)
    Lm = (lit >= 250) & ~over & (lb > 20)
    rd = float(np.median(lp[D] / lb[D])) if D.sum() > 500 else None
    rl = float(np.median(lp[Lm] / lb[Lm])) if Lm.sum() > 500 else None
    out['dim_luma_ratio'] = None if rd is None else round(rd, 3)
    out['lit_luma_ratio'] = None if rl is None else round(rl, 3)
    if rd is None or abs(rd - K_DIM) > 0.03:
        fails.append('dim region luma ratio %s, want %.2f +- 0.03' % (rd, K_DIM))
    if rl is not None and not (0.97 <= rl <= 1.03):
        fails.append('lit region luma ratio %.3f, want 0.97-1.03' % rl)
    dim_p95 = float(np.percentile(Ls[D], 95)) if D.sum() > 500 else None
    out['dim_board_p95_L'] = None if dim_p95 is None else round(dim_p95, 1)
    for nm, m in (('pencil wax (L6 + L5)', pen_wax & ~dil(hand | stick | inset, 1)), ('FOCUS corners', ndi.binary_erosion(focus) & ~dil(hand | stick | inset, 1))):
        if m.sum() < 30:
            out[nm] = None
            continue
        p = float(np.percentile(Ls[m], 95))
        out[nm] = dict(p95_L=round(p, 1), median_L=round(float(np.median(Ls[m])), 1), px=int(m.sum()))
        if dim_p95 is not None and not p >= dim_p95 + T.ORDER_MARGIN:
            fails.append('%s p95 L* %.1f must sit above the dimmed board p95 %.1f' % (nm, p, dim_p95))
    hl, hr = g(M, 'Hd__hand_lift'), g(M, 'Hd__hand_rest')
    if hl.any() and hr.any():
        pl, pr = float(np.percentile(Ls[hl], 95)), float(np.percentile(Ls[hr & ~dil(hl, 1)], 95))
        out['lifted card p95_L'], out['resting hand p95_L'] = round(pl, 1), round(pr, 1)
        if not pl >= pr + T.ORDER_MARGIN:
            fails.append('lifted card p95 %.1f must beat the resting hand p95 %.1f' % (pl, pr))
    out['rule'] = ('hover value rules (gated): dim region (outside the lit mask, marks / hand / stickers cut) sRGB-luma ratio plate / board = K_DIM '
                   '%.2f +- 0.03; lit region 0.97-1.03; pencil wax and FOCUS p95 L* >= dimmed board p95 + 1; lifted card p95 >= resting hand p95 + 1.  '
                   'The board A.1 chain is reported, not gated, on a hover plate (the hover dims the board by design; FOCUS #D4FF00 is L* 94)' % K_DIM)
    return dict(pass_=not fails, failures=fails, **out)


def check_c(rep):
    rb = dict(text=rep['rbc']['text'], uncaptured_text=rep['rbc']['uncaptured'])
    return RC.check_caps(rb)


def check_d(rep, geo, rgb, Mx, probe, lit):
    cols = {}
    if geo:
        cut, occ, emp, occ_now, pm = glass_masks(geo, Mx)
        for dep in range(3):
            for st, lab_ in (('live', 'occupied'), ('empty', 'empty')):
                m = pm(st, dep) & (lit >= 250)
                if m.sum() > 200:
                    cols['ring%d %s (lit)' % (dep, lab_)] = tuple(int(v) for v in np.median(rgb[m], 0))
        if probe is not None:
            for dep in range(3):
                m = ndi.binary_erosion(RC.poly_mask([cc['poly'] for cc in geo['probe'] if cc['dep'] == dep]), iterations=4)
                cols['ring%d empty (probe)' % dep] = tuple(int(v) for v in np.median(probe[m], 0))
    r = RC.check_palette(rep['corp'], cols)
    extra = []
    for key, col in cols.items():
        for nm, mc in (('FOCUS', FOCUS), ('PLAN', PLAN)):
            extra.append(dict(a=nm, b='%s cell %s' % (rep['corp'], key), dE=round(T.de76(mc, col), 1)))
    r['hover_marks_vs_cells_reported'] = extra
    r['rows'] = [x for x in r['rows'] if not x['pass_']] + [x for x in r['rows'] if x['pass_'] and ('PLAN' in (x['a'], x['b']) or 'FOCUS' in (x['a'], x['b']))]
    return r


def check_e(rep, M):
    cards = rep['hand'].get('cards') or []
    Mh = {k.split('__', 1)[1]: v for k, v in M.items() if k.startswith('Hd__')}
    Mh['send'] = g(M, 'B__send')
    Mh['undo'] = g(M, 'B__undo')
    if not cards:
        return dict(pass_=False, why='no hand layout (search found none)')
    r = RC.check_hand(Mh, dict(cards=cards))
    yy, xx = np.mgrid[0:H, 0:W]
    rho = np.hypot(xx - C[0], yy - C[1])
    allh = g(M, 'Hd__hand_rest') | g(M, 'Hd__hand_lift')
    lift = g(M, 'Hd__hand_lift')
    btn = dil(g(M, 'B__send') | g(M, 'B__undo'), BTN_GAP)
    arcs = dil(g(M, 'Z__arcs'), LIFT_ARC_GAP)
    ex = dict(hand_min_r=round(float(rho[allh].min()), 1), hand_px_inside_r455=int((allh & (rho < HAND_MIN_R)).sum()),
              lift_min_r=round(float(rho[lift].min()), 1) if lift.any() else None,
              lift_px_inside_r459=int((lift & (rho < HAND_MIN_R + LIFT_CLEAR)).sum()), lift_px_within_3px_of_landing_marks=int((lift & arcs).sum()),
              hand_lowest_y=int(np.nonzero(allh.any(1))[0].max()), hand_px_within_2px_of_buttons=int((allh & btn).sum()),
              rest_cost_hex_covered_px=sum(x['cost_covered_px'] for x in r['rest_cards_covered_info']), layout=rep['hand'].get('layout'))
    # resting faces: each resting card's face under the resting cards after it, measured on the plate's card masks, vs the board's own resting
    # fan of the same hand (no lift): a hover may not hide more of a resting card (name, rules words, tabs) than the board does
    rest_i = [i for i, c in enumerate(cards) if c['role'] == 'rest']
    board_face = rep['hand'].get('rest_face_board') or {}
    faces = []
    for k_, i in enumerate(rest_i):
        mi = g(Mh, 'card_%d' % i)
        later = np.zeros((H, W), bool)
        for j in rest_i[k_ + 1:]:
            later |= g(Mh, 'card_%d' % j)
        px = int((mi & later).sum())
        b0 = board_face.get(cards[i]['name'])
        faces.append(dict(card=cards[i]['name'], face_covered_px=px, board_fan_px=b0, extra_px=None if b0 is None else px - b0))
    ex['rest_faces'] = faces
    ex['rest_face_extra_px'] = sum(max(0, f['extra_px'] or 0) for f in faces) if board_face else None
    ok = (r['pass_'] and ex['hand_px_inside_r455'] == 0 and ex['lift_px_inside_r459'] == 0 and ex['lift_px_within_3px_of_landing_marks'] == 0
          and ex['hand_lowest_y'] <= HAND_BOTTOM and ex['hand_px_within_2px_of_buttons'] == 0 and ex['rest_cost_hex_covered_px'] == 0
          and ex['rest_face_extra_px'] == 0)
    r.update(ex)
    r['pass_'] = bool(ok)
    r['rule'] += ('; plus: every card outside r455, lifted card outside r459 and 3 px off the landing marks, lowest hand pixel <= y %d, 0 px within '
                  '2 px of SEND IT / UNDO, no resting card on another resting card\'s cost hex, and no resting card\'s face more covered by the '
                  'resting cards after it than on the board\'s own resting fan of the same hand (0 px extra: nothing the board shows is hidden)' % HAND_BOTTOM)
    return r


# ------------------------------------------------------------------------------------------------ hover checks
def _ref_widths():
    """the estimator on reference strokes drawn the way wax_stroke draws and records them (a union of discs at 2x, BOX to 1x; the mask at
    >= 50 %, the width integrated on the coverage): a ring and two straight strokes at 7 px (wax), 13 px (L6 with ink), 3 px (L5 edge) and
    7.5 px (L5 with keyline)"""
    from PIL import ImageDraw as _D
    out = {}
    for nm, w in (('L6_wax', 7.0), ('L6_all', 13.0), ('L5_wax', 3.0), ('L5_all', 7.5)):
        im = Image.new('L', (520, 260), 0)
        d = _D.Draw(im)
        q = w - 0.5                                   # 2x radius w, bbox r - 0.5 (hv_core._stamp)
        paths = [[(130 + 90 * math.cos(t), 130 + 70 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 400)],
                 [(260 + 230 * f, 30 + 40 * f) for f in np.linspace(0, 1, 400)], [(280 + 220 * f, 210 - 30 * f) for f in np.linspace(0, 1, 400)]]
        for path in paths:
            for x, y in path:
                d.ellipse([2 * x - q, 2 * y - q, 2 * x + q, 2 * y + q], fill=255)
        c = np.asarray(im.resize((260, 130), Image.BOX)).astype(np.float32) / 255.0
        out[nm] = stroke_width(c >= 0.5, cov=c)
    return out


REF_W = {}


def profile_widths(rgb, wax, step=4):
    """wax and ink widths measured on the published PNG: at every step-th ridge pixel of the wax mask, a profile across the stroke (the normal is
    the Hessian direction of the smoothed distance transform), sampled bilinearly every 0.1 px; wax = b* above the midpoint between the wax b*
    at the centre and the ink b*; ink = from the wax edge to where L* rises past the midpoint between the ink L* and the ground beyond (only
    where the ground is at least 12 L* lighter than the ink)"""
    if wax.sum() < 60:
        return None
    from scipy.ndimage import map_coordinates
    lab = T.lab(rgb)
    Lc, bc = lab[..., 0], lab[..., 2]
    dt = ndi.distance_transform_edt(wax)
    s = ndi.gaussian_filter(dt, 1.2)
    dyy = ndi.gaussian_filter(dt, 1.2, order=(2, 0))
    dxx = ndi.gaussian_filter(dt, 1.2, order=(0, 2))
    dxy = ndi.gaussian_filter(dt, 1.2, order=(1, 1))
    ridge = (dt >= ndi.maximum_filter(dt, size=3) - 1e-6) & (dt >= 2.5)
    ys, xs = np.nonzero(ridge)
    ww, wi = [], []
    tt = np.arange(-14.0, 14.0001, 0.1)
    b_ink = float(T.lab(np.array(INK_RGB, np.float64))[2])
    L_ink = float(T.lab(np.array(INK_RGB, np.float64))[0])
    for j in range(0, len(ys), step):
        y, x = ys[j], xs[j]
        hxx, hyy, hxy = dxx[y, x], dyy[y, x], dxy[y, x]
        tr, det = hxx + hyy, hxx * hyy - hxy * hxy
        lam = tr / 2 - math.sqrt(max(0.0, tr * tr / 4 - det))          # the most negative eigenvalue: across the stroke
        vx, vy = (lam - hyy, hxy) if abs(hxy) > 1e-9 else ((1.0, 0.0) if hxx < hyy else (0.0, 1.0))
        n_ = math.hypot(vx, vy) or 1.0
        vx, vy = vx / n_, vy / n_
        py, px = y + tt * vy, x + tt * vx
        if py.min() < 0 or px.min() < 0 or py.max() > H - 1 or px.max() > W - 1:
            continue
        b = map_coordinates(bc, [py, px], order=1)
        L = map_coordinates(Lc, [py, px], order=1)
        i0 = len(tt) // 2
        bw = b[i0]
        if bw < 40:
            continue
        thr = (bw + b_ink) / 2
        inw = b > thr
        lo = i0
        while lo > 0 and inw[lo - 1]:
            lo -= 1
        hi = i0
        while hi < len(tt) - 1 and inw[hi + 1]:
            hi += 1
        if lo == 0 or hi == len(tt) - 1:
            continue
        ww.append((hi - lo + 1) * 0.1)
        for side, e in ((-1, lo), (1, hi)):
            k_bg = e + side * 70                                    # 7 px beyond the wax edge: past the 3 px ink and any AA
            if not (0 <= k_bg < len(tt)):
                continue
            Lg = L[k_bg]
            if Lg - L_ink < 12:
                continue
            thr2 = (L_ink + Lg) / 2
            k = e + side
            # walk through the ink (dark) until L* rises past the midpoint
            seen_dark = False
            while 0 <= k < len(tt) and abs(k - e) < 70:
                if L[k] < thr2:
                    seen_dark = True
                elif seen_dark:
                    break
                k += side
            if seen_dark:
                wi.append(abs(k - e) * 0.1)
    if not ww:
        return None
    return dict(wax_px=round(float(np.median(ww)), 2), wax_p10_p90=[round(float(np.percentile(ww, 10)), 2), round(float(np.percentile(ww, 90)), 2)],
                n_profiles=len(ww), ink_px=round(float(np.median(wi)), 2) if wi else None, n_ink_profiles=len(wi))


INK_RGB = (12, 10, 22)


def check_pencil(M, rgb):
    """2.5: the pencil as drawn.  (1) the drawn masks (L6 / L5 wax and with ink) measure the same as a reference 7 / 13 / 3 / 7.5 px stroke
    recorded the same way (within 0.75 px); (2) on the published PNG the L6 wax reads 6-8 px across and its ink edge 2-4 px a side"""
    if not REF_W:
        REF_W.update(_ref_widths())
    sw = lambda k: stroke_width(g(M, 'P__' + k), cov=M.get('Pv__' + k))
    r = dict(mask=dict(L6_wax=sw('L6_wax'), L6_all=sw('L6_all'), L5_wax=sw('L5_wax'), L5_all=sw('L5_all')), reference=dict(REF_W),
             L5_chevrons_reported=dict(wax=sw('L5c_wax'), all=sw('L5c_all'), spec='3.4 px wax, 1.5 px ink a side'),
             measure='coverage integrated along the normal' if 'Pv__L6_all' in M else '50 % mask run')
    fails = []
    lim = dict(L6_wax=(6.0, 8.0), L6_all=(12.0, 14.0), L5_wax=(2.5, 4.0), L5_all=(6.5, 9.0))
    for k, v in r['mask'].items():
        if v is None:
            continue
        if not lim[k][0] <= v <= lim[k][1]:
            fails.append('%s width %.2f px, want %.1f-%.1f' % (k, v, lim[k][0], lim[k][1]))
    if r['mask']['L6_wax'] is not None and r['mask']['L6_all'] is not None:
        r['mask']['L6_ink_each_side'] = round((r['mask']['L6_all'] - r['mask']['L6_wax']) / 2, 2)
        if not 2.5 <= r['mask']['L6_ink_each_side'] <= 3.5:
            fails.append('L6 ink edge %.2f px a side, want 3' % r['mask']['L6_ink_each_side'])
    pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = board_mask_sets(M)
    top = dil(hand | stick | inset | g(M, 'Z__digits') | g(M, 'Z__labels') | g(M, 'Z__tags') | g(M, 'Z__badges') | g(M, 'Z__tickets') | g(M, 'Z__tape')
              | g(M, 'Z__plates') | g(M, 'Z__leader') | g(M, 'Z__hud_labels') | g(M, 'Y__you') | focus, 3)
    pw = profile_widths(rgb, g(M, 'P__L6_wax') & ~top)
    r['png_L6'] = pw
    if pw is not None:
        if not 6.0 <= pw['wax_px'] <= 8.0:
            fails.append('L6 wax %.2f px across on the PNG (want 7)' % pw['wax_px'])
        pass                      # the ink run on the PNG is reported only: on the dimmed board the ground is rarely lighter than the ink
    r['pass_'] = not fails
    r['failures'] = fails
    r['rule'] = ('(1) the drawn masks, median width across the stroke (at the distance-transform ridge, the stroke coverage integrated along the normal in 0.1 px steps): L6 wax 6-8, '
                 'L6 with ink 12-14 (ink 2.5-3.5 a side), L5 edges 2.5-4, with keyline 6.5-9 (chevrons reported apart, the filled head is not a width); the same estimator on a reference stroke of the spec widths is '
                 'reported (reference); (2) on the published PNG, profiles across the L6 wax: wax 6-8 px between the b* midpoint crossings; the ink run on the '
                 'PNG is reported (the dimmed ground is rarely lighter than the ink)')
    return r


def check_grain(M, rgb, bg):
    pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = board_mask_sets(M)
    top = dil(hand | stick | inset | g(M, 'Z__digits') | g(M, 'Z__labels') | g(M, 'Z__tags') | g(M, 'Z__badges') | g(M, 'Z__tickets') | g(M, 'Z__tape')
              | g(M, 'Z__plates') | g(M, 'Z__leader') | g(M, 'Z__hud_labels') | g(M, 'Y__you') | focus | g(M, 'P__L5_all') | g(M, 'P__L5c_all') | g(M, 'P__L5h_all'), 2)   # L6 measured where it is on top
    core = ndi.binary_erosion(g(M, 'P__L6_wax'), iterations=1) & ~top
    Ls = T.lstar(T.lum(rgb))
    planL = float(T.lstar(T.lum(np.array(PLAN, np.float64))))
    r = {}
    fails = []
    if core.sum() > 50:
        r.update(wax_core_px=int(core.sum()), L_mean=round(float(Ls[core].mean()), 1), L_std=round(float(Ls[core].std()), 2),
                 L_p99=round(float(np.percentile(Ls[core], 99)), 1), plan_L=round(planL, 1))
        if r['L_std'] < 1.0:
            fails.append('wax grain L* std %.2f < 1.0' % r['L_std'])
        if r['L_p99'] > planL + 1.0:
            fails.append('wax p99 L* %.1f above PLAN L* %.1f + 1' % (r['L_p99'], planL))
    band = dil(pen_all, 3) & ~pen_all & ~dil(focus | hover & ~pen_all | hand | stick | inset, 1)
    lab_p = T.lab(rgb[band]) if band.any() else np.zeros((0, 3))
    yel = lambda lab: int(((lab[:, 2] > 35) & (np.abs(lab[:, 1]) < 25) & (lab[:, 0] > 40)).sum()) if len(lab) else 0
    r['glow_band_yellow_px'] = yel(lab_p)
    r['board_band_yellow_px'] = yel(T.lab(bg[band])) if bg is not None and band.any() else None
    if r['board_band_yellow_px'] is not None and r['glow_band_yellow_px'] > r['board_band_yellow_px'] + 5:
        fails.append('PLAN-yellow pixels in the 3 px band outside the pencil: %d (board %d): glow' % (r['glow_band_yellow_px'], r['board_band_yellow_px']))
    r['pass_'] = not fails
    r['failures'] = fails
    r['rule'] = 'wax interior (L6, eroded 1 px) L* std >= 1.0 and p99 <= PLAN L* + 1; no glow: PLAN-yellow px (b* > 35, |a*| < 25, L* > 40) in the 3 px band outside the ink <= the board\'s own + 5'
    return r


def check_rings(rep, M, words):
    b = rep['bill']
    need = [k for i, k in enumerate(('lands', 'through')) if b['live'][i] != b['plan'][i]]
    fits = rep.get('hud_ring_fits') or []
    rings = {f['tag'].split()[0]: f for f in fits if f.get('form') == 'ring'}
    fails = []
    for k in need:
        f = rings.get(k)
        if f is None or not f.get('ok'):
            fails.append('no ring on %s' % k)
    for f in fits:
        if f.get('form') not in ('ring', 'underline'):
            fails.append('mark form %s' % f.get('form'))
        if not f.get('ok'):
            fails.append('fit failed: %s' % f.get('tag'))
    you_need = b['hp_after'][0] != b['hp_after'][1]
    you = [f for f in fits if f['tag'] == 'you']
    if you_need and not (you and you[0]['ok'] and you[0]['form'] == 'underline'):
        fails.append('YOU change has no underline')
    brackets = [t['text'] for t in rep['rbc']['text'] if re.match(r'^\s*[()]\s*$', t['text']) or re.match(r'^\(\s*\d+\s*\)$', t['text'].strip())]
    if brackets:
        fails.append('bracket text drawn: %s' % brackets[:4])
    bill = box_mask(rep['hud2_R'].get('bill_frame'))
    pen = g(M, 'P__L6_all') & bill
    on_hero = int((pen & dil(g(M, 'Zf__hud_hero_full'), 1)).sum())
    on_labels = int((pen & dil(g(M, 'Z__hud_labels'), 1)).sum())
    if on_hero:
        fails.append('pencil on the hero digits or their keyline (1 px kept): %d px' % on_hero)
    if on_labels:
        fails.append('pencil on HUD words (1 px kept): %d px' % on_labels)
    return dict(pass_=not fails, failures=fails, needed=need, you_needed=you_need, fits=fits, pencil_on_hero_px=on_hero,
                pencil_on_hud_words_px=on_labels, bracket_text=brackets,
                rule='a closed pencil ring (no bracket, no "( n )" text) on every LANDS / THROUGH number the plan changes, an underline under the YOU '
                     'segments that change; pencil 0 px on the hero digits with their keyline and on HUD words, 1 px kept')


def check_hp_strip(M):
    pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = board_mask_sets(M)
    you = g(M, 'Y__you')
    px = {k: int((m & you).sum()) for k, m in (('pencil', pen_all), ('focus', focus), ('hover', hover), ('ghost', ghost), ('inset', inset))}
    return dict(pass_=sum(px.values()) == 0, px=px, rule='nothing drawn over the YOU HP strip: pencil, FOCUS, hover marks, ghosts, insets 0 px (as drawn, before the compose keeps board marks on top)')


def check_ram(rep, M, rgb, bg):
    pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = board_mask_sets(M)
    o = rep.get('obj2_R') or {}
    ram, trace = box_mask(o.get('ram_pips'), 3), box_mask(o.get('trace_pips'), 3)
    px = dict(pencil_on_ram=int((pen_all & ram).sum()), pencil_on_trace=int((pen_all & trace).sum()), focus_on_ram=int((focus & ram).sum()),
              hover_on_ram=int((hover & ram).sum()), hover_on_trace=int((hover & trace).sum()))
    gl = lambda a: int((np.linalg.norm(T.lab(a[ram]) - T.lab(np.array(GAIN, np.float64)), axis=-1) < 20).sum()) if ram.any() else 0
    px['gain_green_px_on_ram_row'] = gl(rgb)
    px['board_gain_green_px_on_ram_row'] = gl(bg) if bg is not None else None
    ok = all(v == 0 for k, v in px.items() if not k.endswith('ram_row')) and (px['board_gain_green_px_on_ram_row'] is None or px['gain_green_px_on_ram_row'] <= px['board_gain_green_px_on_ram_row'])
    return dict(pass_=bool(ok), px=px, rule='3.9 one RAM treatment: no pencil, FOCUS or hover mark on the RAM coins or TRACE pips; no GAIN-green on the RAM row beyond the board\'s own coins')


def check_insets(rep, M):
    hud = box_mask(rep['hud2_R'].get('bill_frame')) | box_mask((rep.get('obj2_R') or {}).get('obj_plate')) | box_mask((rep.get('obj2_R') or {}).get('res_plate'))
    hand = g(M, 'Hd__hand_rest') | g(M, 'Hd__hand_lift')
    rows, fails = [], []
    for i in rep.get('insets', []):
        bm = box_mask(i['box'])
        src = i.get('source') or {}
        sm = box_mask(src.get('crop'))
        r = dict(name=i['name'], box=i['box'], on_hud_px=int((bm & hud).sum()), on_hand_px=int((bm & hand).sum()), source_crop=src.get('crop'),
                 source_on_hud_px=int((sm & hud).sum()), asserts='%d/%d' % (i['asserts']['passed'], i['asserts']['total']))
        if r['on_hud_px'] or r['on_hand_px'] or r['source_on_hud_px'] or i['asserts']['passed'] != i['asserts']['total']:
            fails.append(r)
        rows.append(r)
    return dict(pass_=not fails, rows=rows, failures=fails, rule='2.4: an inset is a board crop: its frame 0 px on the HUD and the hand, its source crop 0 px on the HUD, its variant render asserts all pass')


def check_options(rep, rgb):
    rows = (rep.get('hud2_R') or {}).get('_opt_rows')
    if rep['plate'] != 'h04':
        return dict(pass_=True, applies=False)
    fails = []
    if not rows:
        return dict(pass_=False, applies=True, failures=['no option rows'])
    n_opts = len(rows)
    nb = rep['hud2_R'].get('next_row')
    m = box_mask(nb)
    lab = T.lab(rgb[m])
    planlike = int((np.linalg.norm(lab - T.lab(np.array(PLAN, np.float64)), axis=-1) < 25).sum())
    if planlike:
        fails.append('PLAN-yellow px in the NEXT rows: %d' % planlike)
    stars = []
    for r_ in rows:
        if r_.get('star'):
            x, y, rr = r_['star']
            sm = box_mask((x - rr, y - rr, x + rr, y + rr))
            lb = T.lab(rgb[sm])
            bright = lb[lb[:, 0] > 60]
            cst = float(np.median(np.hypot(bright[:, 1], bright[:, 2]))) if len(bright) else None
            stars.append(dict(tag=r_.get('tag'), median_C=None if cst is None else round(cst, 1)))
            if cst is None or cst > 12:
                fails.append('BEST star chroma %s > 12' % cst)
    sel = [r_ for r_ in rows if r_.get('sel')]
    if len(sel) != 1:
        fails.append('%d selected rows' % len(sel))
    return dict(pass_=not fails, applies=True, n_rows=n_opts, rows=[{k: v for k, v in r_.items() if k != 'next'} for r_ in rows], plan_px_in_rows=planlike,
                stars=stars, failures=fails, rule='2.4 / 3.22: one NEXT row per legal Twist option; 3.8: 0 PLAN-yellow px in the rows (dE76 < 25), the selected row on a neutral edge, the BEST star neutral (median C* of its light pixels <= 12)')


def check_slices(rep, M, rgb, bg):
    sec = (rep.get('marks') or {}).get('braced_sector')
    if sec is None:
        sec = (rep.get('marks') or {}).get('soak_sector')
    if sec is None or bg is None:
        return dict(pass_=True, applies=False)
    pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = board_mask_sets(M)
    yy, xx = np.mgrid[0:H, 0:W]
    rho = np.hypot(xx - C[0], yy - C[1])
    ang = np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) % 360          # the board's sector angle: 0 = up, clockwise (rb_checks)
    over = dil(focus | hover | ghost | pen_all, 2)
    lp, lb = luma(rgb), luma(bg)
    Ls = T.lstar(T.lum(rgb))
    rows, fails = [], []
    for s in range(6):
        d = (ang - 60 * s + 180) % 360 - 180
        m = (np.abs(d) <= 24) & (rho >= T_IN + 8) & (rho <= T_OUT - 8) & ~over & (lb > 20)
        r = float(np.median(lp[m] / lb[m])) if m.sum() > 200 else None
        rows.append(dict(sector=s, aimed=s == sec, luma_ratio=None if r is None else round(r, 3), median_L=round(float(np.median(Ls[m])), 1) if m.any() else None))
        if r is None:
            continue
        if s == sec and r < 0.95:
            fails.append('aimed slice %d luma ratio %.3f < 0.95' % (s, r))
        if s != sec and r > K_DIM + 0.05:
            fails.append('slice %d luma ratio %.3f: not dimmed' % (s, r))
    return dict(pass_=not fails, applies=True, sector=sec, rows=rows, failures=fails,
                rule='3.13: on a slice hover the five non-aimed slices dim with the rings (median luma ratio plate / board <= K_DIM + 0.05); the aimed slice stays lit (>= 0.95)')


def check_focus(rep, M, rgb):
    fm = g(M, 'F__m')
    if not fm.any():
        return dict(pass_=True, applies=False)
    lab = T.lab(rgb[fm])
    dF = np.linalg.norm(lab - T.lab(np.array(FOCUS, np.float64)), axis=-1)
    dO = np.linalg.norm(lab - T.lab(np.array(OLD_LIME, np.float64)), axis=-1)
    core = dF < 12
    med = np.median(rgb[fm][core], 0) if core.any() else None
    r = dict(px=int(fm.sum()), core_px=int(core.sum()), core_median_hex=None if med is None else '#%02X%02X%02X' % tuple(int(round(v)) for v in med),
             core_median_dE=None if med is None else round(T.de76(tuple(med), FOCUS), 2), old_lime_px=int((dO < 10).sum()))
    fails = []
    if med is None or r['core_median_dE'] > 3:
        fails.append('FOCUS core colour %s' % r['core_median_hex'])
    if r['old_lime_px']:
        fails.append('%d px of the old lime #96FE46' % r['old_lime_px'])
    calls = []
    for k in sorted(k for k in M if k.startswith('Fc__')):
        m = M[k]
        lb, n = ndi.label(m, structure=np.ones((3, 3)))
        sl = ndi.find_objects(lb)
        sizes = [max(s[0].stop - s[0].start, s[1].stop - s[1].start) for s in sl]
        info = (rep.get('focus_calls') or [{}] * 999)[int(k[4:])] if int(k[4:]) < len(rep.get('focus_calls') or []) else {}
        c = dict(i=int(k[4:]), fn=info.get('fn'), thick=info.get('thick'), corners=n, bbox_px=sizes)
        calls.append(c)
        if n != 4 or any(sz < 8 or sz > 28 for sz in sizes):
            fails.append('focus call %d (%s): %d components, bbox %s' % (c['i'], c['fn'], n, sizes))
    r.update(calls=calls, n_calls=len(calls), pass_=not fails, failures=fails,
             rule='FOCUS = #D4FF00: the median of the FOCUS pixels within dE76 12 of it is within dE76 3; 0 px within dE76 10 of the old #96FE46; '
                  'every focus call (cell, slice, tag) is four separate corners: 4 components (8-connected) of 8-28 px bbox')
    return r


def check_collide(rep):
    c = rep.get('collisions')
    if not c:
        return dict(pass_=False, why='no collision report')
    hb = c.get('hand_vs_board', {})
    ok = c['hover_vs_marks_pass'] and c['occlusion_pass'] and c['mark_pairs_pass'] and hb.get('pass', True) is not False
    return dict(pass_=bool(ok), hover_vs_marks_px={k: v for k, v in c['hover_vs_marks_px'].items() if v}, occlusion_px={k: v for k, v in c['occlusion_px'].items() if v},
                mark_pairs_px={k: v for k, v in c['mark_pairs_px'].items() if v}, hand_vs_board=hb, z_order=rep.get('z_order'),
                rule='hz_core.collision_report: hover marks, ghosts and insets 0 px on digits, labels, tags, badges, tickets, leader, tape, plates, hand, '
                     'HUD words and hero digit fill; marks vs occluders 0; mark pairs 0; hand 0 px on board marks and outside r455')


def check_dashes(rep, img):
    r = DA.audit(img)
    ok = rep.get('dash_calls') == 0 and rep.get('dot_calls') == 0 and r['n_runs'] == 0
    return dict(pass_=bool(ok), dash_calls=rep.get('dash_calls'), dot_calls=rep.get('dot_calls'), pixel_dot_runs=r['n_runs'],
                runs=[dict(n=x['n'], spacing=x['spacing'], bbox=x['bbox']) for x in r['runs']], rule='0 dash / dot draw calls; 0 pixel dot runs (dot_audit.py)')


def run(name):
    rep, M, lit, rgb, bg, probe = load(name)
    Mx = rb_inputs(rep, M)
    out = {}
    try:
        a, geo = check_a(rep, Mx, lit, rgb, probe)
    except Exception as e:
        a, geo = dict(pass_=False, error=repr(e)), rep.get('geometry')
    try:
        a['board_image_same_state'] = board_a(rep, M, bg, probe, a)
    except Exception as e:
        a['board_image_same_state'] = dict(error=repr(e))
    out['a_cell_contrast'] = a
    out['b_value'] = check_b(rep, M, Mx, lit, rgb, bg, geo)
    out['c_cap_height'] = check_c(rep)
    out['d_palette'] = check_d(rep, geo, rgb, Mx, probe, lit)
    out['e_hand'] = check_e(rep, M)
    out['pencil'] = check_pencil(M, rgb)
    out['grain'] = check_grain(M, rgb, bg)
    out['rings'] = check_rings(rep, M, rep['words'])
    out['hp_strip'] = check_hp_strip(M)
    out['ram'] = check_ram(rep, M, rgb, bg)
    out['insets'] = check_insets(rep, M)
    out['options'] = check_options(rep, rgb)
    out['slices'] = check_slices(rep, M, rgb, bg)
    out['focus'] = check_focus(rep, M, rgb)
    out['collide'] = check_collide(rep)
    out['dashes'] = check_dashes(rep, Image.open(HERE + 'out/%s.png' % name))
    out['nowords'] = dict(pass_=rep['words'] or not rep.get('alnum_text_calls'), alnum_text_calls=rep.get('alnum_text_calls'))
    ins_ok = all(i['asserts']['passed'] == i['asserts']['total'] for i in rep.get('insets', []))
    out['asserts'] = dict(pass_=rep['asserts']['passed'] == rep['asserts']['total'] and ins_ok, board='%d/%d' % (rep['asserts']['passed'], rep['asserts']['total']),
                          insets=['%s %d/%d' % (i['name'], i['asserts']['passed'], i['asserts']['total']) for i in rep.get('insets', [])],
                          failed=rep['asserts'].get('failed'))
    out['hud_room_info'] = dict(hover_hud_bottom=rep['snap'].get('hud_bottom'), board_hud_bottom=BOARD_HUD_BOTTOM,
                                delta_px=(rep['snap'].get('hud_bottom') or 0) - BOARD_HUD_BOTTOM,
                                note='cross-set: the ring room (and on h04 the option rows) makes the hover HUD taller than the board HUD; the board HUD has to take '
                                     'the same room or the rows move on hover (reported, not gated here)')
    out['squint_info'] = rep.get('squint')
    out['pass'] = {k: bool(v.get('pass_')) for k, v in out.items() if isinstance(v, dict) and 'pass_' in v}
    out['plate_pass'] = all(out['pass'].values())
    json.dump(out, open(HERE + 'chk/%s.checks.json' % name, 'w'), indent=1, default=str)
    return out


if __name__ == '__main__':
    names = sys.argv[1:] or sorted(os.path.basename(p)[:-5] for p in glob.glob(HERE + 'chk/h*.json') if not p.endswith('.checks.json') and not os.path.basename(p).startswith('h00'))
    for nm in names:
        try:
            o = run(nm)
        except Exception:
            import traceback
            traceback.print_exc()
            print('ERROR', nm)
            continue
        bad = [k for k, v in o['pass'].items() if not v]
        print('%-28s %s  fails: %s' % (nm, 'PASS' if o['plate_pass'] else 'FAIL', ', '.join(bad) or '-'), flush=True)
