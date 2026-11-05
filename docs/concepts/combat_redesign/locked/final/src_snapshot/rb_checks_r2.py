"""rb_checks_r2 (2026-11-04, round 2 of the rebuild; R1_REREVIEW calls C1-C11 as art-pass made them): the checks added to rb_checks a-e,
measured on the published PNG (CIE L* of sRGB luminance, dE76) with the capture masks of asm_render / rb_capture / rb4_patch.

  b+  C3  every board pixel inside r < UNCLASSED_R at L* >= UNCLASSED_L sits in a capture class (1 px of anti-aliasing allowed); the new
          structure classes (E cell outlines, K structure, K schedule lines, E ward arc, K arc marks and frames, the dying hatch, the pencil,
          FOCUS) get rows: p99 at least MARK_MARGIN under the HOT p95; E / K p95 under the tower p95 and no E / K peak (p99) over it
      C4  the A.1 token rule per disc: each unit's token disc p95 under the HOT p95 and under the tower p95, by MARK_MARGIN
  d+  C2  drawn colours: the modal colour of FOCUS, the pencil wax, the HOT fill, the gun tracers and the Adjuster track within DRAWN_DE of
          their token; every drawn mark class's modal colour >= DE_MIN from the skin's corp hue inks
      C16 Solace: the rim rope as drawn (median of the rope band) >= RIM_DE_MIN from GAIN and the hub HP ring green
  f   C1  the pencil on the plate: wax width, ink edge per side, wax grain (L* std inside the wax)
  g   C5  ticket edges: L* of each ticket's edge, the W6 -> W5 -> W4 steps >= TICKET_STEP_L, the W6 hazard ticks clear of the bomb's pips
  h   C8  HUD rows: the bill plate edge rows measured on the plate and the row record vs the hover grid formula (hud_rows)
  i   C11 HOT core: core width at 1x >= HOT_CORE_PX_MIN, core vs ring-NOW cell glass >= HOT_CORE_RATIO_MIN:1 (fill ratio reported)"""
import math
import numpy as np
from scipy import ndimage as ndi
import rb_tokens as T

CC = (536, 540)
GROUND = ('scrim',)                       # UI ground slabs: not a class for the unclassed test


def _get(M, k):
    return M.get(k, np.zeros((1080, 1920), bool))


def _row(Ls, m):
    v = Ls[m]
    return dict(p95=round(float(np.percentile(v, 95)), 1), p99=round(float(np.percentile(v, 99)), 1), median=round(float(np.median(v)), 1),
                px=int(m.sum()))


def pen_all(M):
    m = np.zeros((1080, 1920), bool)
    for k in M:
        if k.startswith('pen_') and k.endswith('_all'):
            m |= M[k]
    return m


def over_marks(M):
    """marks drawn on top of E / K / T marks (their own family): cut from the regions they cover"""
    m = _get(M, 'plan') | _get(M, 'leader') | _get(M, 'twist_badge') | _get(M, 'guns') | pen_all(M) | _get(M, 'focus')
    return ndi.binary_dilation(m, iterations=1) if m.any() else m


# ------------------------------------------------------------------------------------------------ b+ (C3, C4)
STRUCT_ROWS = (('E cell outlines (L3)', ('e_line',), 'E'), ('K structure (plate / bezel lines, cube discs)', ('k_struct',), 'K'),
               ('K schedule lines', ('k_sched',), 'K'), ('E ward arc', ('e_ward',), 'E'), ('K arc marks (discs, dots, wear, twist)', ('k_arcmark',), 'K'),
               ('K arc frames', ('k_arcframe',), 'K'), ('T arc outcome marks (brace, soak, check)', ('arc_outcome',), 'T'),
               ('E dying hatch (L7)', ('kill_hatch',), 'E'), ('N FOCUS', ('focus',), 'N'), ('N consumed ghost (pencil, stamp)', ('ghost',), 'N'),
               ('E skin cell detail (edge, rivets)', ('e_skin',), 'E'))


def check_bright(Y, M, hot_p95, tower_p95):
    Ls = T.lstar(Y)
    yy, xx = np.mgrid[0:1080, 0:1920]
    rho = np.hypot(xx - CC[0], yy - CC[1])
    fails = []
    # C3: unclassed bright pixels
    cls = np.zeros((1080, 1920), bool)
    for k, m in M.items():
        if k in GROUND:
            continue
        cls |= m
    cls_d = ndi.binary_dilation(cls, iterations=1)
    bright = (Ls >= T.UNCLASSED_L) & (rho < T.UNCLASSED_R)
    unc = bright & ~cls_d
    lab, n = ndi.label(unc)
    clusters = []
    if n:
        objs = ndi.find_objects(lab)
        sizes = ndi.sum(unc, lab, range(1, n + 1))
        for i in np.argsort(-sizes)[:12]:
            sl = objs[i]
            mm = lab[sl] == i + 1
            clusters.append(dict(px=int(sizes[i]), box=[sl[1].start, sl[0].start, sl[1].stop - 1, sl[0].stop - 1],
                                 max_L=round(float(Ls[sl][mm].max()), 1)))
    if unc.sum():
        fails.append('%d unclassed bright px (L* >= %.0f, r < %.0f)' % (int(unc.sum()), T.UNCLASSED_L, T.UNCLASSED_R))
    # structure rows
    over = over_marks(M)
    rows = {}
    for nm, ks, fam in STRUCT_ROWS:
        m = np.zeros((1080, 1920), bool)
        for k in ks:
            m |= _get(M, k)
        if fam in ('E', 'K'):
            m &= ~over
        if m.sum() < 30:
            continue
        r = _row(Ls, m)
        r['family'] = fam
        rules = []
        if hot_p95 is not None:
            ok = r['p99'] + T.MARK_MARGIN <= hot_p95
            rules.append(('p99 under HOT p95', ok))
            if not ok:
                fails.append('%s p99 %.1f must sit under the HOT p95 %.1f by %.0f' % (nm, r['p99'], hot_p95, T.MARK_MARGIN))
        if tower_p95 is not None and fam in ('E', 'K'):
            ok = r['p95'] + T.MARK_MARGIN <= tower_p95
            rules.append(('p95 under the tower p95', ok))
            if not ok:
                fails.append('%s p95 %.1f must sit under the tower p95 %.1f by %.0f' % (nm, r['p95'], tower_p95, T.MARK_MARGIN))
        r['rules'] = rules
        rows[nm] = r
    # C4: per disc
    discs = {}
    for k in sorted(M):
        if not k.startswith('tok_u') or k.endswith('_dim'):
            continue
        m = M[k] & ~over
        if m.sum() < 30:
            continue
        r = _row(Ls, m)
        rules = []
        if hot_p95 is not None:
            ok = r['p95'] + T.MARK_MARGIN <= hot_p95
            rules.append(('p95 under HOT p95', ok))
            if not ok:
                fails.append('token disc %s p95 %.1f must sit under the HOT p95 %.1f' % (k[4:], r['p95'], hot_p95))
        if tower_p95 is not None:
            ok = r['p95'] + T.MARK_MARGIN <= tower_p95
            rules.append(('p95 under the tower p95', ok))
            if not ok:
                fails.append('token disc %s p95 %.1f must sit under the tower p95 %.1f' % (k[4:], r['p95'], tower_p95))
        r['rules'] = rules
        discs[k[4:]] = r
    return dict(pass_=not fails, failures=fails, unclassed_px=int(unc.sum()), unclassed_clusters=clusters, structure_rows=rows,
                token_discs=discs,
                rule='C3: every pixel inside r < %.0f at L* >= %.0f sits in a capture class (1 px dilation); structure rows p99 >= %.0f under the HOT '
                     'p95 (no class but SEND IT reaches the HOT marks), E / K p95 >= %.0f under the tower p95.  C4: each token disc p95 >= %.0f under '
                     'the HOT p95 and the tower p95'
                     % (T.UNCLASSED_R, T.UNCLASSED_L, T.MARK_MARGIN, T.MARK_MARGIN, T.MARK_MARGIN))


# ------------------------------------------------------------------------------------------------ d+ (C2, C16)
def modal(rgb, m, q=6):
    """the modal colour of the masked pixels: the most common colour after quantising each channel to q levels' bins, then the median of that
    bin's pixels"""
    px = rgb[m]
    if len(px) == 0:
        return None
    b = (px // q).astype(np.int64)
    key = b[:, 0] * 1000000 + b[:, 1] * 1000 + b[:, 2]
    u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    top = np.argmax(cnt)
    sel = px[inv == top]
    return tuple(int(v) for v in np.median(sel, 0)), round(float(cnt[top]) / len(px), 3)


DRAWN = (('N FOCUS', ('focus',), 'FOCUS'), ('N pencil wax', ('pen_wax',), 'PLAN'), ('T HOT fill', ('chev0', 'arcT0'), 'HARM_UP'),
         ('P gun tracers', ('guns',), 'CELL_PINK'), ('E Adjuster track', ('adj_hp',), 'BOSS_GOLD'))
# the corp-ink test covers the marks.  Not tested: k_struct / e_skin (the plate, bezel, rim and cell decoration ARE the skin), and the ticket
# and token-frame edges, which carry the skin ink by DR-6 (VISUAL_PLAN E: "skin ink on the bezel lip, rim, crest roundel, token frames and
# ticket edges"); the K type on the tickets and the token glyphs are achromatic
DRAWN_CLASSES = ('focus', 'pen_wax', 'chev0', 'arcT0', 'chev1', 'arcT1', 'chev2', 'arcT2', 'guns', 'adj_hp', 'adj', 'hp', 'digits',
                 'ring_tags', 'badges', 'twist_badge', 'e_line', 'k_arcmark', 'k_arcframe', 'kill_hatch', 'arc_outcome', 'ghost')


def pigment(rgb, m, cmin=25.0, grain=False):
    """the colour a mark is drawn in, robust to keylines: the class pixels with Lab chroma > cmin (the INK keyline, the white-hot core and
    grey anti-aliasing drop out), then their modal colour.  grain=True (the pencil: its grain and drag streaks only darken the wax, by design):
    the median of the brightest tenth of those pixels, the un-grained wax"""
    px = rgb[m]
    if len(px) == 0:
        return None
    lab = T.lab(px.astype(np.float64))
    ch = np.hypot(lab[:, 1], lab[:, 2])
    sel = ch > cmin
    if sel.sum() < 10:
        return None
    if grain:
        p, L = px[sel], lab[sel, 0]
        top = L >= np.percentile(L, 90)
        return tuple(int(v) for v in np.median(p[top], 0)), round(float(sel.mean()), 3)
    mm = np.zeros(m.shape, bool)
    ys, xs = np.nonzero(m)
    mm[ys[sel], xs[sel]] = True
    return modal(rgb, mm)[0], round(float(sel.mean()), 3)


def _token(nm):
    return tuple(T.TOKENS[nm]) if nm in T.TOKENS else tuple(getattr(T, nm))


def check_drawn(rgb, M, corp, beat=None):
    fails, rows, hue_rows = [], [], []
    pen_wax = np.zeros((1080, 1920), bool)
    for k in M:
        if k.startswith('pen_') and k.endswith('_wax'):
            pen_wax |= M[k]
    MM = dict(M)
    MM['pen_wax'] = pen_wax
    over = _get(M, 'hud') | _get(M, 'hand') | _get(M, 'send') | _get(M, 'undo')
    for nm, ks, tok in DRAWN:
        if 'guns' in ks and beat in ('p2', 'p2b'):
            continue                              # the tracers are a 58 % preview (p2) / hover-dimmed (p2b) by design: not drawn at the token
        m = np.zeros((1080, 1920), bool)
        for k in ks:
            m |= _get(MM, k)
        m = m & ~over
        if m.sum() < 20:
            continue
        mc, share = modal(rgb, m)
        pg = pigment(rgb, m, grain=('pen_wax' in ks))
        if pg is None:
            continue
        pc, csh = pg
        d = T.de76(pc, _token(tok))
        r = dict(cls=nm, token=tok, token_hex='#%02X%02X%02X' % _token(tok), drawn_hex='#%02X%02X%02X' % pc, chromatic_share=csh, dE=round(d, 1),
                 modal_hex_info='#%02X%02X%02X' % mc, modal_share_info=share, dE_modal_info=round(T.de76(mc, _token(tok)), 1),
                 px=int(m.sum()), pass_=d <= T.DRAWN_DE)
        rows.append(r)
        if not r['pass_']:
            fails.append('%s drawn %s is dE %.1f from %s %s' % (nm, r['drawn_hex'], d, tok, r['token_hex']))
    inks = T.SKIN_INKS.get(corp, {})
    for k in DRAWN_CLASSES:
        m = _get(MM, k) & ~over
        if m.sum() < 20 or not inks:
            continue
        pg = pigment(rgb, m)
        if pg is None:
            continue
        mc = pg[0]
        for ik, ic in inks.items():
            if ik == 'barcode':
                continue
            d = T.de76(mc, ic)
            r = dict(cls=k, modal_hex='#%02X%02X%02X' % mc, ink=corp + ' ' + ik, ink_hex='#%02X%02X%02X' % tuple(ic), dE=round(d, 1), pass_=d >= T.DE_MIN)
            hue_rows.append(r)
            if not r['pass_']:
                fails.append('drawn %s %s is dE %.1f from the corp ink %s' % (k, r['modal_hex'], d, r['ink']))
    rim = None
    if corp == 'solace':
        yy, xx = np.mgrid[0:1080, 0:1920]
        rho = np.hypot(xx - CC[0], yy - CC[1])
        band = (rho >= 491) & (rho <= 498) & (yy < 1080) & ~over
        med = tuple(int(v) for v in np.median(rgb[band], 0))
        mc, share = modal(rgb, band)
        rim = dict(median_hex='#%02X%02X%02X' % med, modal_hex='#%02X%02X%02X' % mc, px=int(band.sum()), rows=[])
        for nm, c in (('GAIN', T.TOKENS['GAIN']), ('hub HP ring green', T.HUB_HP_GREEN)):
            for lab_, col in (('median', med), ('modal', mc)):
                d = T.de76(col, c)
                rim['rows'].append(dict(vs=nm, of=lab_, dE=round(d, 1), pass_=d >= T.RIM_DE_MIN))
                if d < T.RIM_DE_MIN:
                    fails.append('Solace rim %s %s is dE %.1f from %s (needs %.0f)' % (lab_, '#%02X%02X%02X' % col, d, nm, T.RIM_DE_MIN))
        lab = T.lab(np.array(med, np.float64))
        rim['lch'] = dict(L=round(float(lab[0]), 1), C=round(float(math.hypot(lab[1], lab[2])), 1), h=round(math.degrees(math.atan2(lab[2], lab[1])) % 360, 1))
    return dict(pass_=not fails, failures=fails, drawn_vs_token=rows, drawn_vs_corp_ink=hue_rows, solace_rim=rim,
                rule='C2: the drawn colour of FOCUS / HOT fill / gun tracers / Adjuster track (the modal colour of its chromatic pixels, C* > 25: '
                     'keylines and the white-hot core drop out) and of the pencil wax (its brightest tenth: the grain only darkens) within dE76 %.0f '
                     'of its token, the plain modal reported beside it; every '
                     'drawn mark class (same measure) >= %.0f from the skin hue inks.  C16: the Solace rim (r 491-498) >= %.0f from GAIN and the hub HP green'
                     % (T.DRAWN_DE, T.DE_MIN, T.RIM_DE_MIN))


# ------------------------------------------------------------------------------------------------ f (C1)
def _width(m, s=4):
    """stroke width of a binary mask at 1x: the mask is upsampled s x (nearest), its distance transform taken, and the width is 2 x the median
    distance on the ridge (pixels that are the 3 x 3 maximum of the distance), / s"""
    if m.sum() < 20:
        return None
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = max(0, ys.min() - 2), ys.max() + 3, max(0, xs.min() - 2), xs.max() + 3
    c = m[y0:y1, x0:x1]
    u = np.repeat(np.repeat(c, s, 0), s, 1)
    dt = ndi.distance_transform_edt(u)
    mx = ndi.maximum_filter(dt, size=3)
    ridge = (dt >= mx) & (dt >= s)
    v = dt[ridge]
    if len(v) == 0:
        return None
    return round(float(2 * np.median(v) / s), 2)


def check_pencil(rgb, Y, M):
    Ls = T.lstar(Y)
    rows, fails = [], []
    plan_lab = T.lab(np.array(T.TOKENS['PLAN'], np.float64))
    lab = T.lab(rgb)
    over = _get(M, 'hud') | _get(M, 'hand') | _get(M, 'send') | _get(M, 'undo') | _get(M, 'focus') | _get(M, 'twist_badge')
    for k in sorted(M):
        if not (k.startswith('pen_') and k.endswith('_all')):
            continue
        cls = k[4:-4]
        allm = M[k] & ~ndi.binary_dilation(over, iterations=2)
        if allm.sum() < 40:
            continue
        # classify on the PNG: wax = within dE 30 of PLAN (the grain and drag darken it), ink = L* < 30
        dpl = np.linalg.norm(lab - plan_lab, axis=-1)
        wax = allm & (dpl < 30)
        ink = allm & (Ls < 30)
        stroke = wax | ink
        w_wax = _width(ndi.binary_opening(wax, iterations=1) if wax.sum() > 200 else wax)
        w_all = _width(ndi.binary_closing(stroke, iterations=1))
        ink_side = None if (w_wax is None or w_all is None) else round((w_all - w_wax) / 2.0, 2)
        core = ndi.binary_erosion(wax, iterations=1)
        grain = round(float(Ls[core].std()), 2) if core.sum() > 20 else None
        r = dict(cls=cls, px=int(allm.sum()), wax_px=int(wax.sum()), ink_px=int(ink.sum()), wax_w=w_wax, stroke_w=w_all, ink_per_side=ink_side,
                 grain_L_std=grain, wax_L_median=round(float(np.median(Ls[wax])), 1) if wax.any() else None)
        ok = (w_wax is not None and T.PEN_WAX_PX[0] <= w_wax <= T.PEN_WAX_PX[1] and ink_side is not None
              and T.PEN_INK_PX[0] <= ink_side <= T.PEN_INK_PX[1] and grain is not None and grain >= T.PEN_GRAIN_L_STD)
        r['pass_'] = bool(ok)
        rows.append(r)
        if not ok:
            fails.append('pencil %s: wax %s px, ink %s px per side, grain L* std %s' % (cls, w_wax, ink_side, grain))
    return dict(pass_=not fails, failures=fails, rows=rows, present=bool(rows),
                rule='C1 on the plate: wax width %.0f-%.0f px, ink edge %.1f-%.1f px per side, wax grain L* std >= %.1f (wax = within dE 30 of PLAN, '
                     'ink = L* < 30, inside the pencil classes; widths from the medial axis)' % (T.PEN_WAX_PX + T.PEN_INK_PX + (T.PEN_GRAIN_L_STD,)))


# ------------------------------------------------------------------------------------------------ g (C5)
def check_tickets(Y, M, info):
    import rb2_patch as RB2
    Ls = T.lstar(Y)
    tm = _get(M, 'tickets')
    if tm.sum() < 100:
        return dict(pass_=True, present=False, rows=[], rule='no ticket queue on this plate')
    vals = (info.get('rb4') or {}).get('ticket_vals', [])
    # the queue geometry (rb4 queue_tickets: x from 24, pitch TICKET_W + 8, y 24), one box per ticket drawn, kept where the ticket class is
    boxes = []
    for i in range(len(vals)):
        x0 = int(24 + i * (RB2.TICKET_W + 8))
        b = (x0, 24, x0 + int(RB2.TICKET_W), 24 + int(RB2.TICKET_H))
        if tm[b[1]:b[3], b[0]:b[2]].mean() > 0.5:
            boxes.append(b)
    rows = []
    for (x0, y0, x1, y1) in boxes:
        # the edge line is drawn centred on the ticket outline: the 3 px band on the outline (chamfer corners excluded), p90 L*
        ring = np.zeros((1080, 1920), bool)
        ring[y0 - 1:y0 + 2, x0 + 10:x1 - 10] = True
        ring[y1 - 1:y1 + 2, x0 + 10:x1 - 10] = True
        ring[y0 + 10:y1 - 10, x0 - 1:x0 + 2] = True
        ring[y0 + 10:y1 - 10, x1 - 1:x1 + 2] = True
        v = Ls[ring]
        rows.append(dict(box=[x0, y0, x1, y1], edge_L_p90=round(float(np.percentile(v, 90)), 1), edge_L_max=round(float(v.max()), 1)))
    fails = []
    if vals and len(rows) != len(vals):
        fails.append('%d tickets drawn, %d found on the plate' % (len(vals), len(rows)))
    for r, v in zip(rows, vals):
        r['edge_val_drawn'] = v
    order = sorted(rows, key=lambda r: r['edge_L_p90'])
    if len(rows) >= 2:
        for a, b in zip(order, order[1:]):
            if b['edge_L_p90'] - a['edge_L_p90'] < T.TICKET_STEP_L:
                fails.append('ticket edge step %.1f -> %.1f under %.0f L*' % (a['edge_L_p90'], b['edge_L_p90'], T.TICKET_STEP_L))
    haz = (info.get('rb4') or {}).get('hazard_ticks')
    return dict(pass_=not fails, present=True, failures=fails, rows=rows, edge_vals_drawn=vals, hazard_ticks=haz,
                rule='C5: each ticket edge L* (p90 of the 3 px ring inside the keyline); the W6 / W5 / W4 edges differ step to step by >= %.0f L*; '
                     'the W6 hazard ticks sit in the top row (tag to turn pips), clear of the bomb glyph and its width pips' % T.TICKET_STEP_L)


# ------------------------------------------------------------------------------------------------ h (C8)
def check_hud_rows(rgb, info, beat):
    import hud_rows as HR
    rows = info.get('hud_rows') or {}
    # measured: the bill plate's left keyline column (x = 34..40): the rows where the plate edge colour is lit (cyan keyline)
    lab = T.lab(rgb[:, 1072:1082].astype(np.float64))
    lit = (lab[..., 0] > 55) & (np.hypot(lab[..., 1], lab[..., 2]) > 25)
    col = lit.any(1)
    runs = []
    y = 0
    while y < 1080:
        if col[y]:
            y0 = y
            while y < 1080 and col[y]:
                y += 1
            runs.append([y0, y - 1])
        y += 1
    import rb2_patch as RB2
    fails = []
    bill = [r for r in runs if abs(r[0] - 76) <= 3]
    reserve = rows.get('reserve', beat != 'p3')
    # the hover grid (hv_core.bill_box): BILL_H + HERO_ROOM_T + HERO_ROOM_B + OPT_PITCH x (option rows - 1); with the board's reserved slots
    # (OPT_SLOTS) the two are the same box whenever a hover shows up to OPT_SLOTS - 1 options
    hover_bill_h = RB2.BILL_H + HR.HERO_ROOM_T + HR.HERO_ROOM_B + HR.OPT_PITCH * (HR.OPT_SLOTS - 1)
    exp_h = HR.bill_h(reserve)
    meas = None
    if bill:
        meas = dict(bill_top=bill[0][0], bill_bottom=bill[0][1] + 1, bill_h=bill[0][1] + 1 - bill[0][0])
        if abs(meas['bill_h'] - exp_h) > 1:
            fails.append('bill plate %d px tall on the plate, the grid says %d' % (meas['bill_h'], exp_h))
        if reserve and abs(meas['bill_h'] - hover_bill_h) > 1:
            fails.append('bill plate %d px vs the hover grid %d' % (meas['bill_h'], hover_bill_h))
    else:
        fails.append('bill plate edge not found at x 1072-1081')
    rec = {k: v for k, v in rows.items() if k in ('bill_top', 'hero_label_y', 'hero_digit_y', 'eq_label_y', 'eq_y', 'split_label_y', 'split_y',
                                                  'next_y', 'bill_bottom', 'obj_top', 'ram_top', 'hud_bottom', 'chain_top')}
    hover = dict(hero_label_y=76 + 14, hero_digit_y=76 + 54 + HR.HERO_ROOM_T, eq_label_y=76 + HR.HERO_ROOM_T + HR.HERO_ROOM_B + RB2.EQ_LY,
                 split_label_y=76 + HR.HERO_ROOM_T + HR.HERO_ROOM_B + RB2.SP_LY, next_y=76 + HR.HERO_ROOM_T + HR.HERO_ROOM_B + RB2.NX_YY,
                 bill_bottom=76 + hover_bill_h)
    for k, v in hover.items():
        if k in rec and rec[k] != v and not (k == 'bill_bottom' and not reserve):
            fails.append('%s %s on the board, %s on the hover grid' % (k, rec[k], v))
    return dict(pass_=not fails, present=bool(rows), failures=fails, beat=beat, reserve=reserve, measured=meas, row_record=rec, hover_grid=hover,
                plate_edge_runs_x1072=runs[:12],
                rule='C8: the bill plate measured on the plate (x 1072-1081 lit keyline rows) is the grid height (BILL_H + HERO_ROOM_T + HERO_ROOM_B '
                     '+ OPT_PITCH x 3 reserved slots; p3 without the slots) and, with the slots, the hover grid; every row of the board record equals '
                     'the hover grid row (hv_core constants)')


# ------------------------------------------------------------------------------------------------ i (C11)
def check_hot_core(rgb, Y, M, occ_now):
    hot = _get(M, 'chev0') | _get(M, 'arcT0')
    hot &= ~over_marks(M)
    if hot.sum() < 30:
        return dict(pass_=True, present=False, rule='no HOT marks on this plate')
    core_lab = T.lab(np.array(T.HOT_CORE, np.float64))
    lab = T.lab(rgb)
    core = hot & (np.linalg.norm(lab - core_lab, axis=-1) < 14)
    fill = hot & (np.linalg.norm(lab - T.lab(np.array(T.HARM_UP, np.float64)), axis=-1) < 14)
    # core width: per connected core stroke, 2 x the medial-axis distance (median), at 1x
    w = _width(core)
    lab_, n = ndi.label(core)
    per, strokes = [], []
    objs = ndi.find_objects(lab_)
    c0 = _get(M, 'chev0')
    for i in range(1, n + 1):
        m = lab_ == i
        if m.sum() < 8:
            continue
        wi = _width(m)
        per.append(wi)
        sl = objs[i - 1]
        # reported per stroke (round 2): which HOT mark, its medial width and box
        strokes.append(dict(mark='cell chevron' if (m & c0).any() else 'landing-arc chevron', w=wi, px=int(m.sum()),
                            box=[sl[1].start, sl[0].start, sl[1].stop - 1, sl[0].stop - 1]))
    per = [p for p in per if p is not None]
    yc = float(Y[core].mean()) if core.any() else None
    yf = float(Y[fill].mean()) if fill.any() else None
    yg = float(Y[occ_now].mean()) if occ_now is not None and occ_now.sum() > 100 else None
    ratio = None if (yc is None or yg is None) else (yc + 0.05) / (yg + 0.05)
    fratio = None if (yf is None or yg is None) else (yf + 0.05) / (yg + 0.05)
    fails = []
    if w is None or w < T.HOT_CORE_PX_MIN:
        fails.append('HOT core width %s px under %.0f' % (w, T.HOT_CORE_PX_MIN))
    if ratio is None or ratio < T.HOT_CORE_RATIO_MIN:
        fails.append('HOT core vs ring-NOW cell %s:1 under %.1f:1' % (None if ratio is None else round(ratio, 2), T.HOT_CORE_RATIO_MIN))
    return dict(pass_=not fails, present=True, failures=fails, core_px=int(core.sum()), core_w_px=w,
                core_w_per_stroke=dict(n=len(per), min=min(per) if per else None, median=float(np.median(per)) if per else None),
                strokes_under_min=[s for s in strokes if s['w'] is not None and s['w'] < T.HOT_CORE_PX_MIN], strokes=strokes,
                core_L=round(float(T.lstar(yc)), 1) if yc is not None else None, cell_L=round(float(T.lstar(yg)), 1) if yg is not None else None,
                core_vs_cell=None if ratio is None else round(ratio, 2), fill_vs_cell_reported=None if fratio is None else round(fratio, 2),
                rule='C11: HOT core (pixels within dE 14 of HOT_CORE inside the HOT classes) medial width >= %.0f px at 1x; core vs ring-NOW occupied '
                     'glass (Y + 0.05 ratio) >= %.1f:1; the fill ratio is reported only' % (T.HOT_CORE_PX_MIN, T.HOT_CORE_RATIO_MIN))
