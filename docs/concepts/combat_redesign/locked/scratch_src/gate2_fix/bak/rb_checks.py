"""rb_checks (2026-11-03 rebuild): the five checks the AD review asked for (AD_REVIEW section 3 + REVIEW_RESPONSE "Process"), run on every
published plate from the PNG itself (L* = CIE L* of sRGB luminance, the reviewer's measure.py) plus the capture written by asm_render
(work/chk_<sfx>.json 'rb', work/masks_<sfx>.npz, work/probe_<sfx>.png).  A plate fails if any check fails.

  a  occupied vs empty cell contrast: per ring and per covered sector, mean luminance of the cell glass (marks cut out) vs the same ring's
     empty glass (the plate's own empties and the skin's empty probe), ratio >= 3.0; mean L* reported (target occupied NOW L* 40-45)
  b  family value order: p95 L* per family region, sorted table; VISUAL_PLAN A.1 (2026-11-03): SEND IT > HOT T marks > lifted card >
     P tower > P hand > E cells occupied > E cells empty; K clock p95 below the tower and its median in L* 45-55; token discs below HOT marks
  c  cap height of every text draw >= 16 px at 1080p
  d  palette collision dE76 >= 15: every pair of meaning tokens (VISUAL_PLAN E); slice inks, card type plates and the skin's hue inks against
     the tokens they sit next to; HOT / COLD marks against the skin's measured cell colours
  e  hand vs SEND IT / UNDO (0 px) and the lifted card vs every sibling card's cost hex and rules line (0 px)
run(name, png, sfx) -> dict with 'pass' per check."""
import os, sys, json, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import rb_tokens as T

HERE = 'D:/rc_scratch/combat_redesign/locked/corp/'
WORK = HERE + 'work/'
CC = (536, 540)
# mark classes cut out of the cell glass before it is measured; '_dim' = the same class drawn hover-dimmed (p2b), 'plan' = the pencil
# hover path / landing cell / trigger path, which sit on the glass but are not the glass
_CUT_BASE = ('chev0', 'chev1', 'chev2', 'arcT0', 'arcT1', 'arcT2', 'tokens', 'badges', 'tags', 'tickets', 'hand', 'hud', 'tape', 'plates',
             'digits', 'labels', 'leader')
CUT = _CUT_BASE + tuple(k + '_dim' for k in _CUT_BASE) + ('plan',)


def _L(Y):
    return float(T.lstar(Y))


def poly_mask(polys, shape=(1080, 1920)):
    m = Image.new('L', (shape[1], shape[0]), 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        if p and len(p) > 2:
            d.polygon([tuple(q) for q in p], fill=255)
    return np.asarray(m) > 0


def load_masks(sfx):
    fp = WORK + 'masks_%s.npz' % sfx
    if not os.path.exists(fp):
        return {}
    z = np.load(fp)
    return {k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) for k in z.files}


def dil(m, r):
    return ndi.binary_dilation(m, iterations=int(r)) if m is not None and m.any() else m


# ------------------------------------------------------------------------------------------------ a. cell contrast
def check_cells(Y, rgb, rb, M, probeY):
    g = rb['geometry']
    yy, xx = np.mgrid[0:1080, 0:1920]
    # marks cut out of the glass: chevrons, tokens, badges, arcs, tags, HP trays, tracers (pink), anything the hand / HUD covers
    cut = np.zeros((1080, 1920), bool)
    for k in CUT:
        if k in M:
            cut |= M[k]
    cut = dil(cut, 3)
    tray = np.zeros((1080, 1920), bool)
    rho = np.hypot(xx - CC[0], yy - CC[1])
    for u in g['units']:
        tx, ty = u['token']
        cut |= np.hypot(xx - tx, yy - ty) <= u['tok_r'] + 8
        tray |= (rho >= u['t_in'] - 3) & (rho <= u['t_out'] + 3)
    # gun tracers and other saturated pink marks crossing the glass
    mx, mn = rgb.max(2), rgb.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    pinkish = (sat > 0.45) & (rgb[..., 0] > 150) & (rgb[..., 2] > 90) & (rgb[..., 1] < 140)
    cut |= dil(pinkish, 2)
    rows, ok = [], True
    ring_ref = {}
    for dep in range(3):
        # probe: the skin's empty cell on this ring (all six sectors), plus the plate's own empty cells on this ring
        pm = [c['poly'] for c in g['probe'] if c['dep'] == dep]
        pr = ndi.binary_erosion(poly_mask(pm), iterations=4)
        ref_probe = float(probeY[pr].mean()) if probeY is not None and pr.any() else None
        em = [c['poly'] for c in g['cells'] if c['dep'] == dep and c['state'] == 'empty']
        ref_plate = None
        if em:
            m = ndi.binary_erosion(poly_mask(em), iterations=4) & ~cut
            ref_plate = float(Y[m].mean()) if m.any() else None
        refs = [v for v in (ref_probe, ref_plate) if v is not None]
        ring_ref[dep] = dict(empty_L_probe=None if ref_probe is None else round(_L(ref_probe), 1),
                             empty_L_plate=None if ref_plate is None else round(_L(ref_plate), 1), n_empty_on_plate=len(em))
        ref = max(refs) if refs else None          # the brighter empty is the harder reference
        for c in g['cells']:
            if c['dep'] != dep or c['state'] not in ('live', 'dying', 'dimmed'):
                continue
            m = ndi.binary_erosion(poly_mask([c['poly']]), iterations=4) & ~cut & ~tray
            if not m.any():
                continue
            yo = float(Y[m].mean())
            ratio = yo / ref if ref else None
            gate = c['state'] == 'live'
            r_ok = (ratio is not None and ratio >= T.CELL_RATIO_MIN) if gate else None
            if gate and not r_ok:
                ok = False
            rows.append(dict(ring=dep, sector=c['s'], unit=c['uid'], kind=c['kind'], state=c['state'], occ_L=round(_L(yo), 1),
                             empty_L=None if ref is None else round(_L(ref), 1), ratio=None if ratio is None else round(ratio, 2),
                             gated=gate, pass_=r_ok, px=int(m.sum())))
    now = [r['occ_L'] for r in rows if r['ring'] == 0 and r['gated']]
    return dict(pass_=ok, rows=rows, rings=ring_ref, occ_now_L_range=[min(now), max(now)] if now else None,
                rule='glass mean luminance occupied / empty >= %.1f per ring, per covered sector, live units (dying = veiled by the gone state, '
                     'dimmed = hover dim, ghosts: reported, not gated); marks, token disc, HP tray and tracers cut out' % T.CELL_RATIO_MIN)


# ------------------------------------------------------------------------------------------------ b. family value order
def family_regions(M, rb, Y, glass_occ, glass_empty):
    yy, xx = np.mgrid[0:1080, 0:1920]
    rho = np.hypot(xx - CC[0], yy - CC[1])
    get = lambda k: M.get(k, np.zeros((1080, 1920), bool))
    hand_all = get('hand_rest') | get('hand_lift') | get('hand_played')
    # stage 2: the hover tag and its leader (p2b) sit over the room; they are UI, not room.  So are the UI scrim slabs (hud_scrim) where they
    # darken the room by 15 % or more (captured by rb_capture as 'scrim')
    ui = get('hud') | hand_all | get('send') | get('undo') | get('name') | get('you') | get('tags') | get('leader')
    room = (xx >= 1100) & (yy >= 420) & ~dil(ui, 4) & (rho > 505) & ~get('scrim')
    fam = {
        'SEND IT': get('send'),
        'T HOT marks': get('chev0') | get('arcT0'),
        'P lifted card': get('hand_lift'),
        'P tower': get('tower'),
        'P hand (rest)': get('hand_rest'),
        'E cells occupied (glass)': glass_occ,
        'E cells empty (glass)': glass_empty,
        'E token discs': get('tokens'),
        'K clock (tape, sweep, plates)': get('tape') | get('plates'),
        'S HUD': get('hud'),
        'room': room,
    }
    return fam


def check_order(Y, M, rb, glass_occ, glass_empty, glass_now=None):
    fam = family_regions(M, rb, Y, glass_occ, glass_empty)
    Ls = T.lstar(Y)
    tab = {}
    for k, m in fam.items():
        if m is None or not m.any():
            tab[k] = None
            continue
        v = Ls[m]
        tab[k] = dict(p95=round(float(np.percentile(v, 95)), 1), median=round(float(np.median(v)), 1), mean=round(_L(float(Y[m].mean())), 1), px=int(m.sum()))
    chain = ['SEND IT', 'T HOT marks', 'P lifted card', 'P tower', 'P hand (rest)', 'E cells occupied (glass)', 'E cells empty (glass)']
    chain = [c for c in chain if tab.get(c)]
    fails = []
    for a, b in zip(chain, chain[1:]):
        if not tab[a]['p95'] >= tab[b]['p95'] + T.ORDER_MARGIN:
            fails.append('%s (%.1f) must beat %s (%.1f) by %.0f' % (a, tab[a]['p95'], b, tab[b]['p95'], T.ORDER_MARGIN))
    k_ = tab.get('K clock (tape, sweep, plates)')
    if k_ and tab.get('P tower'):
        if not k_['p95'] + T.ORDER_MARGIN <= tab['P tower']['p95']:
            fails.append('K clock p95 %.1f must sit below P tower p95 %.1f' % (k_['p95'], tab['P tower']['p95']))
        if not (T.CLOCK_L[0] <= k_['median'] <= T.CLOCK_L[1]):
            fails.append('K clock median L* %.1f outside gunmetal %.0f-%.0f' % (k_['median'], *T.CLOCK_L))
    tk = tab.get('E token discs')
    if tk and tab.get('T HOT marks') and not tk['p95'] + T.ORDER_MARGIN <= tab['T HOT marks']['p95']:
        fails.append('token discs p95 %.1f must sit below HOT marks p95 %.1f' % (tk['p95'], tab['T HOT marks']['p95']))
    # stage 2 (review 2.8): the room is readable (mean L* 28-34) and the board still comes first: the room's p95 sits below the occupied
    # glass of ring NOW (live cells).  When no ring-NOW cell is live (p2b: the hover dims ring NOW; the only full-value live unit sits on
    # ring +2, whose glass is L* 32 by the ring-depth grammar) the reference is the floor of the occupied-NOW glass band, L* 40 (A.1 /
    # rb_tokens CELL_OCC_L).
    rm = tab.get('room')
    Ls_ = T.lstar(Y)
    room_ref = None
    if glass_now is not None and glass_now.sum() > 200:
        room_ref = dict(source='ring NOW occupied glass p95 (live cells)', value=round(float(np.percentile(Ls_[glass_now], 95)), 1))
    else:
        room_ref = dict(source='no live ring-NOW cell on this plate: occupied-NOW glass band floor (CELL_OCC_L[0])', value=T.CELL_OCC_L[0])
    if rm:
        if not (T.ROOM_MEAN_L[0] <= rm['mean'] <= T.ROOM_MEAN_L[1]):
            fails.append('room mean L* %.1f outside %.0f-%.0f' % (rm['mean'], *T.ROOM_MEAN_L))
        if not rm['p95'] + T.ORDER_MARGIN <= room_ref['value']:
            fails.append('room p95 %.1f must sit below %s %.1f by %.0f' % (rm['p95'], room_ref['source'], room_ref['value'], T.ORDER_MARGIN))
    probes = {}
    for nm_, (x0, y0, x1, y1) in (('review room box', T.REVIEW_ROOM_BOX), ('review left city box', T.REVIEW_CITY_BOX)):
        probes[nm_] = dict(mean=round(_L(float(Y[y0:y1, x0:x1].mean())), 1), p95=round(float(np.percentile(Ls_[y0:y1, x0:x1], 95)), 1))
    srt = sorted([(k, v) for k, v in tab.items() if v], key=lambda kv: -kv[1]['p95'])
    return dict(pass_=not fails, failures=fails, sorted=[dict(family=k, **v) for k, v in srt], probes=probes, room_ref=room_ref,
                rule='p95 L* per family region; A.1 chain ' + ' > '.join(chain) + '; K below the tower, K median in L* 45-55; token discs below HOT marks; '
                     'room (x >= 1100, y >= 420, r > 505, UI / hand / hover tag and the UI scrim slabs cut out) mean L* %.0f-%.0f with its p95 below the ring-NOW occupied '
                     'glass p95 (live cells; L* 40 when no ring-NOW cell is live)' % T.ROOM_MEAN_L)


# ------------------------------------------------------------------------------------------------ c. cap height
def check_caps(rb):
    rows = []
    for t in rb['text']:
        cap = t.get('cap_px')
        rows.append(dict(text=t['text'][:40], font=t['font'], px=t['px'], cap_px=cap, where=t['where'], pass_=cap is not None and cap >= T.CAP_MIN_PX - 0.05))
    fails = [r for r in rows if not r['pass_']]
    return dict(pass_=not fails, n=len(rows), n_fail=len(fails), failures=fails, smallest=sorted(rows, key=lambda r: r['cap_px'] or 0)[:5],
                rule='cap height (font H box x px) of every text draw >= %.0f px at 1080p; card text at the hand scale' % T.CAP_MIN_PX)


# ------------------------------------------------------------------------------------------------ d. palette collision
def check_palette(corp, cell_cols):
    import card_render as CR
    fails, rows = [], []

    def add(group, a, ca, b, cb, floor=T.DE_MIN):
        d = T.de76(ca, cb)
        r = dict(group=group, a=a, b=b, a_hex='#%02X%02X%02X' % tuple(ca), b_hex='#%02X%02X%02X' % tuple(cb), dE=round(d, 1), pass_=d >= floor)
        rows.append(r)
        if not r['pass_']:
            fails.append(r)
    ks = list(T.TOKENS)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            add('token x token', ks[i], T.TOKENS[ks[i]], ks[j], T.TOKENS[ks[j]])
    for s, c in T.SLICE_INK.items():
        for n in T.SLICE_NEIGHBOURS:
            add('slice ink x token', 'slice ' + s, c, n, T.TOKENS[n])
    for fam, tdef in CR.TYPES.items():
        col = tuple(int(round(v)) for v in tdef['col'][:3])
        for n in T.CARD_NEIGHBOURS:
            add('card type x token', 'card ' + fam, col, n, T.TOKENS[n])
    for k, c in T.SKIN_INKS.get(corp, {}).items():
        for n in T.SKIN_NEIGHBOURS:
            add('skin ink x token', corp + ' ' + k, c, n, T.TOKENS[n])
    if corp == 'solace':
        add('skin ink x Cell lime (2.4)', 'solace leaf', T.SKIN_INKS['solace']['leaf'], 'CELL_LIME', T.CELL_LIME)
    for key, col in cell_cols.items():
        for mk, mc in (('HOT', T.HARM_UP), ('COLD', T.COLD_CHEV)):
            add('mark x skin cell', '%s mark' % mk, mc, '%s cell %s' % (corp, key), col)
        add('mark x skin cell (FAR, reported)', 'FAR mark', T.FAR_CHEV, '%s cell %s' % (corp, key), col, floor=0.0)
    return dict(pass_=not fails, failures=fails, n_pairs=len(rows), rows=rows,
                rule='dE76 >= %.0f: token pairs; slice inks, card type plates, skin hue inks vs the tokens they sit next to; HOT / COLD marks vs the measured cell colours' % T.DE_MIN)


# ------------------------------------------------------------------------------------------------ e. hand
def card_regions(card):
    """screen polygons of a placed card's cost hex and rules line (design coords from card_render, placement from the capture)"""
    import card_render as CR
    sp = CR.CARDS[card['name']]
    rules = CR.rules_box(sp['txt'])          # stage 2: the rules block as drawn (one or two lines at 21 px, never shrunk) plus its bar
    hx_, hy_ = CR.COST_C
    cost = [(hx_ + 22 * math.cos(math.radians(30 + 60 * k)), hy_ + 22 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    m2 = CR.margin_px(card['w2'] - 2 * CR.margin_px(352)) if False else CR.margin_px(352)
    k = card['scale'] / 2.0
    W2, H2 = card['w2'] * k, card['h2'] * k
    a = math.radians(card['ang'])

    def tr(p):
        x, y = (m2 + 2 * p[0]) * k - W2 / 2, (m2 + 2 * p[1]) * k - H2 / 2
        return (card['cx'] + x * math.cos(a) + y * math.sin(a), card['cy'] - x * math.sin(a) + y * math.cos(a))
    return [tr(p) for p in cost], [tr(p) for p in rules]


def check_hand(M, rb):
    get = lambda k: M.get(k, np.zeros((1080, 1920), bool))
    hand = get('hand_rest') | get('hand_lift') | get('hand_played')
    res = dict(hand_x_send_px=int((hand & get('send')).sum()), hand_x_undo_px=int((hand & get('undo')).sum()))
    sib = []
    cards = rb.get('cards', [])
    lift = [i for i, c in enumerate(cards) if c['role'] == 'lift']
    for li in lift:
        lm = M.get('card_%d' % li)
        for j, c in enumerate(cards):
            if j == li or c['role'] != 'rest':
                continue
            cost, rules = card_regions(c)
            sib.append(dict(lifted=cards[li]['name'], sibling=c['name'], cost_px=int((lm & poly_mask([cost])).sum()), rules_px=int((lm & poly_mask([rules])).sum())))
    # resting cards over each other's cost hex / rules line (reported)
    rest_info = []
    for i, c in enumerate(cards):
        if c['role'] != 'rest':
            continue
        cost, rules = card_regions(c)
        later = np.zeros((1080, 1920), bool)
        for j in range(i + 1, len(cards)):
            if cards[j]['role'] == 'rest':
                later |= M.get('card_%d' % j, np.zeros((1080, 1920), bool))
        rest_info.append(dict(card=c['name'], cost_covered_px=int((later & poly_mask([cost])).sum()), rules_covered_px=int((later & poly_mask([rules])).sum())))
    res['lifted_vs_sibling'] = sib
    res['rest_cards_covered_info'] = rest_info
    res['pass_'] = res['hand_x_send_px'] == 0 and res['hand_x_undo_px'] == 0 and all(s['cost_px'] == 0 and s['rules_px'] == 0 for s in sib)
    res['rule'] = 'hand pixels under SEND IT / UNDO: 0; lifted card over a sibling card cost hex or rules line: 0 px'
    return res


# ------------------------------------------------------------------------------------------------ all
def run(name, png, sfx):
    chk = json.load(open(WORK + 'chk_%s.json' % sfx))
    rb = chk['rb']
    M = load_masks(sfx)
    rgb = np.asarray(Image.open(png).convert('RGB')).astype(np.float64)
    Y = T.lum(rgb)
    pf = WORK + 'probe_%s.png' % sfx
    probeY = T.lum(np.asarray(Image.open(pf).convert('RGB')).astype(np.float64)) if os.path.exists(pf) else None
    a = check_cells(Y, rgb, rb, M, probeY)
    # glass masks for the order table and the cell colours for the palette check
    g = rb['geometry']
    yy, xx = np.mgrid[0:1080, 0:1920]
    cut = np.zeros((1080, 1920), bool)
    for k in CUT:
        if k in M:
            cut |= M[k]
    cut = dil(cut, 3)
    rho = np.hypot(xx - CC[0], yy - CC[1])
    for u in g['units']:
        cut |= np.hypot(xx - u['token'][0], yy - u['token'][1]) <= u['tok_r'] + 8
        cut |= (rho >= u['t_in'] - 3) & (rho <= u['t_out'] + 3) & (np.abs(((np.degrees(np.arctan2(xx - CC[0], -(yy - CC[1]))) - u['b0']) % 360)) <= (u['b1'] - u['b0']))
    occ = ndi.binary_erosion(poly_mask([c['poly'] for c in g['cells'] if c['state'] == 'live']), iterations=4) & ~cut
    emp = ndi.binary_erosion(poly_mask([c['poly'] for c in g['cells'] if c['state'] == 'empty']), iterations=4) & ~cut
    occ_now = ndi.binary_erosion(poly_mask([c['poly'] for c in g['cells'] if c['state'] == 'live' and c['dep'] == 0]), iterations=4) & ~cut
    b = check_order(Y, M, rb, occ, emp, occ_now)
    c = check_caps(rb)
    cols = {}
    for dep in range(3):
        for st, lab_ in (('live', 'occupied'), ('empty', 'empty')):
            m = ndi.binary_erosion(poly_mask([cc['poly'] for cc in g['cells'] if cc['state'] == st and cc['dep'] == dep]), iterations=4) & ~cut
            if m.sum() > 200:
                cols['ring%d %s' % (dep, lab_)] = tuple(int(v) for v in np.median(rgb[m], 0))
    if probeY is not None:
        prgb = np.asarray(Image.open(pf).convert('RGB')).astype(np.float64)
        for dep in range(3):
            m = ndi.binary_erosion(poly_mask([cc['poly'] for cc in g['probe'] if cc['dep'] == dep]), iterations=4)
            cols['ring%d empty (probe)' % dep] = tuple(int(v) for v in np.median(prgb[m], 0))
    d = check_palette(rb.get('corp', 'neutral'), cols)
    e = check_hand(M, rb)
    out = dict(a_cell_contrast=a, b_value_order=b, c_cap_height=c, d_palette=d, e_hand=e)
    out['pass'] = {k: v['pass_'] for k, v in out.items()}
    out['plate_pass'] = all(out['pass'].values())
    return out


def table_order(res):
    lines = ['%-30s %6s %6s %6s' % ('family', 'p95', 'median', 'mean')]
    for r in res['b_value_order']['sorted']:
        lines.append('%-30s %6.1f %6.1f %6.1f' % (r['family'], r['p95'], r['median'], r['mean']))
    return '\n'.join(lines)


if __name__ == '__main__':
    nm, png, sfx = sys.argv[1], sys.argv[2], sys.argv[3]
    r = run(nm, png, sfx)
    print(nm, r['pass'])
    print(table_order(r))
    a = r['a_cell_contrast']
    for row in a['rows']:
        print('  ring %d s%d u%s %-8s %-7s occ L* %5.1f  empty L* %s  ratio %s' % (row['ring'], row['sector'], row['unit'], row['kind'], row['state'], row['occ_L'], row['empty_L'], row['ratio']))
    print('  rings', a['rings'])
    print('caps fail', r['c_cap_height']['n_fail'], [(f['text'], f['cap_px']) for f in r['c_cap_height']['failures']])
    print('palette fails', [(f['a'], f['b'], f['dE']) for f in r['d_palette']['failures']])
    print('hand', {k: v for k, v in r['e_hand'].items() if k != 'rule'})
    print('order fails', r['b_value_order']['failures'])
