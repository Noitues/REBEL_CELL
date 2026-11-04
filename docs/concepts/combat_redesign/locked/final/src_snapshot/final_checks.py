"""final_checks: aggregate the O-29 final-pass checks into locked/final/checks.json and build grey_proof.jpg and before_after.jpg.
python final_checks.py      (after the plates are rendered with asm_render.py ... 1 and copied by final_publish.py, and final_cards.py checks)"""
import sys, os, json, re, colorsys
sys.dont_write_bytecode = True
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

HERE = 'D:/rc_scratch/combat_redesign/locked/corp/'
WORK = HERE + 'work/'
# 2026-11-03 rebuild: the plates are checked where rb_set.py publishes them (locked/rebuild/board/, not the repo); FINAL_DIR overrides
FINAL = os.environ.get('FINAL_DIR', 'D:/rc_scratch/combat_redesign/locked/rebuild/board/')
LOCK = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
CONC = 'D:/rc_art/art-pass/docs/concepts/'
E10F = CONC + 'combat_e10_design/final/'
FD = os.path.dirname(os.path.abspath(__file__)) + '/fonts/'
mo = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 22)
an = ImageFont.truetype(FD + 'Anton-Regular.ttf', 30)
J = json.load(open(HERE + 'state_e10.json'))
REP = {}
CC = (536, 540)

# plate name -> (asm_render suffix, first-pass file for comparison)
PL = [('p1_decide', 'p1', LOCK + 'assembled/p1_decide.png'), ('p2_preview', 'p2', LOCK + 'assembled/p2_preview.png'),
      ('p2b_hover', 'p2b', LOCK + 'assembled/p2b_hover.png'), ('p3_resolve', 'p3', LOCK + 'assembled/p3_resolve.png'),
      ('p1_nowords', 'nowords', LOCK + 'assembled/p1_nowords.png'),
      ('p1_decide_solace', 'p1_solace', LOCK + 'corp/p1_decide_solace.png'), ('p2b_hover_solace', 'p2b_solace', LOCK + 'corp/p2b_hover_solace.png'),
      ('p1_decide_meridian', 'p1_meridian', LOCK + 'corp/p1_decide_meridian.png'), ('p2b_hover_meridian', 'p2b_meridian', LOCK + 'corp/p2b_hover_meridian.png')]
# 2026-11-03 rebuild: every beat on every skin (15 plates)
for _c in ('solace', 'meridian'):
    for _n, _b in (('p2_preview', 'p2'), ('p3_resolve', 'p3'), ('p1_nowords', 'nowords')):
        PL.append(('%s_%s' % (_n, _c), '%s_%s' % (_b, _c), ''))
MARKS = ('digits', 'labels', 'tags', 'badges', 'tickets', 'leader')


def chk(sfx):
    fp = WORK + 'chk_%s.json' % sfx
    return json.load(open(fp)) if os.path.exists(fp) else None


# ------------------------------------------------------------------ 1. draw asserts, collisions, occluders, hand vs board, dashes
da, col, occ, hand, dash = {}, {}, {}, {}, {}
for name, sfx, _ in PL:
    c = chk(sfx)
    if not c:
        da[name] = 'missing'
        continue
    A_ = c['asserts']
    fails = [x for x in A_ if not x['ok']]
    da[name] = dict(total=len(A_), passed=len(A_) - len(fails), failures=[dict(name=x['name'], got=x['got'][:120], want=x['want'][:120]) for x in fails][:20])
    ov = c.get('overlap_px', {})
    mm = {k: v for k, v in ov.items() if all(p in MARKS for p in k.split(' x '))}
    col[name] = dict(pairs=mm, total_px=sum(mm.values()), pass_=sum(mm.values()) == 0)
    occ[name] = dict(pairs=c.get('occlusion_px'), pass_=c.get('occlusion_pass'),
                     note='marks (digits, labels, tags, badges, tickets) x occluders (THIS TURN tape, hold / +N plates, hand); labels x plates is allowed (a label is printed on its plate)')
    hand[name] = c.get('hand_vs_board')
    dash[name] = dict(dashed_line_calls=c['dash_calls'], dotted_mark_calls=c['dot_calls'])
REP['draw_asserts'] = da
REP['collisions_marks'] = col
REP['occlusion'] = occ
REP['hand_vs_board'] = hand
REP['hand_rule'] = 'no hand pixel (alpha >= 128) inside wheel radius 455 of the board centre (536, 540), and 0 px over any board mark, tape or plate'
# O-30 fix 3: pixel audit for runs of evenly spaced dots (dot_audit.py), on every published plate, first pass alongside for reference
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dot_audit as DA
for name, sfx, first in PL:
    fp = FINAL + name + '.png'
    if name in dash and os.path.exists(fp):
        r = DA.audit(Image.open(fp))
        dash[name]['pixel_dot_runs'] = r['n_runs']
        dash[name]['pixel_dot_run_list'] = [dict(n=x['n'], spacing=x['spacing'], colour=x['colour'], bbox=x['bbox']) for x in r['runs']]
        if os.path.exists(first):
            dash[name]['pixel_dot_runs_first_pass'] = DA.audit(Image.open(first))['n_runs']
REP['dash_audit'] = dash
REP['dash_audit_note'] = ('dashed_line_calls / dotted_mark_calls count draw calls; pixel_dot_runs (O-30) finds, on the rendered pixels, chains of 5 or more '
                          'small spots (|DoG| > %.0f, area %d-%d px) with even spacing (CV <= %.2f, %.1f-%.0f px), same size and colour and a smooth path, '
                          'after dropping 2-D halftone fields; params in dot_audit.py' % (DA.SPOT_T, DA.SPOT_AREA[0], DA.SPOT_AREA[1], DA.SPACING_CV, DA.GAP[0], DA.GAP[1]))
REP['all_pass'] = dict(draw_asserts=all(isinstance(v, dict) and v['passed'] == v['total'] for v in da.values()),
                       collisions=all(v['pass_'] for v in col.values()), occlusion=all(v['pass_'] for v in occ.values()),
                       hand=all(v and v.get('pass') for v in hand.values()), dashes=all(v['dashed_line_calls'] == 0 and v['dotted_mark_calls'] == 0 for v in dash.values()),
                       pixel_dot_runs=all(v.get('pixel_dot_runs', 1) == 0 for v in dash.values()))

# ------------------------------------------------------------------ 1b. 2026-11-03 rebuild: the AD review's checks (rb_checks.py), each one fails the plate
#   a occupied vs empty cell contrast   b family value order (A.1 amended)   c cap height >= 16 px   d palette dE76 >= 15   e hand vs buttons / lifted vs siblings
import rb_checks as RBK
rbk, tables = {}, []
for name, sfx, _ in PL:
    fp = FINAL + name + '.png'
    if not os.path.exists(fp) or not chk(sfx) or 'rb' not in chk(sfx):
        rbk[name] = 'missing'
        continue
    r = RBK.run(name, fp, sfx)
    rbk[name] = r
    tables.append('== %s  %s' % (name, ' '.join('%s:%s' % (k[0], 'PASS' if v else 'FAIL') for k, v in r['pass'].items())))
    tables.append(RBK.table_order(r))
    for f_ in r['b_value_order']['failures']:
        tables.append('   order FAIL: ' + f_)
    a_ = r['a_cell_contrast']
    tables.append('   cells: occupied NOW L* %s; min ratio (live) %s; empty L* per ring %s' % (
        a_['occ_now_L_range'], min([x['ratio'] for x in a_['rows'] if x['gated']] or [None]),
        {k: (v['empty_L_probe'], v['empty_L_plate']) for k, v in a_['rings'].items()}))
    for x in r['c_cap_height']['failures']:
        tables.append('   cap FAIL %-22s %5.1f px  (%s)' % (x['text'][:22], x['cap_px'] or 0, x['where']))
    for x in r['d_palette']['failures']:
        tables.append('   dE FAIL  %-22s %s  x  %-22s %s  dE %.1f' % (x['a'], x['a_hex'], x['b'], x['b_hex'], x['dE']))
    e_ = r['e_hand']
    tables.append('   hand: x SEND IT %d px, x UNDO %d px, lifted over sibling cost/rules %s' % (
        e_['hand_x_send_px'], e_['hand_x_undo_px'], [(s_['sibling'], s_['cost_px'], s_['rules_px']) for s_ in e_['lifted_vs_sibling']]))
REP['rb_checks'] = rbk
REP['rb_plate_pass'] = {k: (v['plate_pass'] if isinstance(v, dict) else False) for k, v in rbk.items()}
for k_ in ('a_cell_contrast', 'b_value_order', 'c_cap_height', 'd_palette', 'e_hand'):
    REP['all_pass']['rb_' + k_] = all(isinstance(v, dict) and v['pass'][k_] for v in rbk.values())
# 1c. 2026-11-03 stage 2: measured IMPL items that are not one of the five checks, per plate
#   2.7 the whole hand visible with >= 12 px above y = 1080 (hand mask, alpha >= 128); 2.14 ticket kind glyphs >= 16 px ink at full value
s2 = {}
for name, sfx, _ in PL:
    fp = FINAL + name + '.png'
    if not os.path.exists(fp):
        continue
    M_ = RBK.load_masks(sfx)
    row = {}
    if 'hand' in M_ and M_['hand'].any():
        ys_ = np.nonzero(M_['hand'].any(1))[0]
        row['hand_bottom_y'] = int(ys_.max())
        row['hand_margin_px'] = int(1079 - ys_.max())
        row['hand_margin_pass'] = row['hand_margin_px'] >= 12
    a_ = np.asarray(Image.open(fp).convert('RGB')).astype(np.float64)
    Ls_ = RBK.T.lstar(RBK.T.lum(a_))
    tk = []
    x_ = 24
    for i_ in range(3):
        band = Ls_[50:82, x_ + 2:x_ + 82]
        lab_, n_ = ndi.label(ndi.binary_dilation(band > 70, iterations=1))
        parts = []
        for k_ in range(1, n_ + 1):
            yy_, xx_ = np.nonzero(lab_ == k_)
            if len(yy_) >= 25:
                parts.append([int(xx_.min()), int(xx_.max()), int(yy_.min()), int(yy_.max()), lab_ == k_])
        # one glyph may be several parts (the Jammer's sparks): parts whose column ranges overlap are one glyph
        parts.sort(key=lambda p: p[0])
        glyphs = []
        for p in parts:
            if glyphs and p[0] <= glyphs[-1][1] + 1:
                g = glyphs[-1]
                g[1], g[2], g[3], g[4] = max(g[1], p[1]), min(g[2], p[2]), max(g[3], p[3]), g[4] | p[4]
            else:
                glyphs.append(p)
        hs = [dict(ink_h=g[3] - g[2] + 1, p90_L=round(float(np.percentile(band[g[4]], 90)), 1)) for g in glyphs]
        tk.append(hs)
        x_ += 92
    row['ticket_glyphs'] = tk
    # 2026-11-04 (gate 1, review 1.2): 'full value' for a ticket glyph is the K type value (rb_tokens.K_TYPE_L, L* 84), the same on W4, W5 and W6;
    # time stays on the ticket edge value and pips.  The glyphs sat at L* 98, above the HOT marks and the tower (K must sit under the tower).
    row['ticket_pass'] = all(g['ink_h'] >= 16 and RBK.T.K_TYPE_L - 4 <= g['p90_L'] <= RBK.T.K_TYPE_L + 4 for t_ in tk for g in t_) and all(tk)
    s2[name] = row
REP['stage2_measures'] = s2
REP['stage2_rule'] = ('2.7: hand bottom (alpha >= 128) at least 12 px above y = 1080; 2.14: every kind glyph on the three wave tickets has an ink '
                      'height of 16 px or more and p90 L* within 4 of the K type value (L* %.0f, the same full value on every ticket; time is on the ticket edge and pips)' % RBK.T.K_TYPE_L)
REP['all_pass']['stage2_hand_margin'] = all(v.get('hand_margin_pass', False) for v in s2.values())
REP['all_pass']['stage2_tickets'] = all(v['ticket_pass'] for v in s2.values())
for n_, v in s2.items():
    tables.append('   %s stage2: hand margin %s px, ticket glyph ink %s' % (n_, v.get('hand_margin_px'), [[g['ink_h'] for g in t_] for t_ in v['ticket_glyphs']]))
open(FINAL + 'checks_tables.txt', 'w').write('\n'.join(tables) + '\n')
print('\n'.join(tables), flush=True)

# ------------------------------------------------------------------ 2. squint
lum = lambda a: 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def squint(img, region=None):
    s = img.resize((img.width // 16, img.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    l = lum(np.asarray(s, np.float32) / 255.0)
    if region is not None:
        yy, xx = np.mgrid[0:l.shape[0], 0:l.shape[1]]
        l = l[region(xx * 16 + 8, yy * 16 + 8)]
    return dict(mean=round(float(l.mean()), 4), p95=round(float(np.percentile(l, 95)), 4), loud=round(float((l > 0.38).mean()), 4))


d_ = lambda x, y: np.hypot(x - CC[0], y - CC[1])
REG = {'plate': None, 'tower_r<=212': lambda x, y: d_(x, y) <= 212, 'rings_r214-430': lambda x, y: (d_(x, y) >= 214) & (d_(x, y) <= 430),
       'hand_zone': lambda x, y: (x >= 840) & (x <= 1660) & (y >= 780), 'hud': lambda x, y: (x >= 1070) & (y <= 400),
       'room_x>=1100_y>=420_no_hand': lambda x, y: (x >= 1100) & (y >= 420) & ~((x <= 1660) & (y >= 780)) & ~((x >= 1650) & (y >= 840))}
sq = {}
for name, sfx, first in PL:
    fp = FINAL + name + '.png'
    if not os.path.exists(fp):
        continue
    imgs = {'final': fp, 'first_pass': first}
    if name in ('p1_decide', 'p2_preview', 'p2b_hover', 'p3_resolve', 'p1_nowords'):
        imgs['e10'] = E10F + name + '.png'
    sq[name] = {rn: {k: squint(Image.open(v).convert('RGB'), rf) for k, v in imgs.items() if os.path.exists(v)} for rn, rf in REG.items()}
REP['squint'] = sq
import bd_grade as _BG
REP['room_grade'] = dict(source='corp/src/bd_grade.py room_grade() = locked/backdrop/grade.json (%s), installed as the default by lw_render' % _BG.GRADE_VERSION,
                         rooms={c: _BG.CORP_ROOM[c] for c in ('neutral', 'solace', 'meridian')},
                         params={c: _BG.params_for(_BG.CORP_ROOM[c], c) for c in ('neutral', 'solace', 'meridian')},
                         note='2026-11-03 stage 2 (review 2.8): neutral and Solace plates on the bio lab, Meridian plates on the shop (the kit room without a '
                              'Solace sign) under the Meridian corp light; room mean L* 28-34 is gated per plate in rb_checks b; the board scrim is unchanged')
REP['squint_note'] = '1/16 BOX downscale + 1 px blur, luma; loud = share of 16 px cells above 0.38. Target from O-29 fix 9: tower zone loud < 50 %.'
# 2026-11-04 (gate 1): the tower-zone loud share, reported per plate against the E10 plates the review measured (it went UP in the rebuild:
# the slices sit lower in L* but the icon discs, the lit HOT chevrons at r 214 and the hub keep more 16 px cells above 0.38).  Not gated.
REP['squint_tower_zone'] = {n: dict(final=v['tower_r<=212'].get('final', {}).get('loud'), e10=v['tower_r<=212'].get('e10', {}).get('loud'),
                                    first_pass=v['tower_r<=212'].get('first_pass', {}).get('loud'))
                            for n, v in sq.items()}
REP['squint_tower_zone_note'] = ('loud share (0-1) of the tower zone r <= 212; target < 0.50 (O-29 fix 9) is NOT met on p1 / p2 / p3: see final/NOTES.md '
                                 '"2026-11-04 gate 1"; reported, not gated')
# 2026-11-04 (gate 1): the reviewer's measure.py boxes re-aimed on the rebuilt plates (rb_probes), next to the old box read on the same plate
try:
    import rb_probes as _RP
    REP['review_probes'] = {sfx: _RP.run(sfx, FINAL + name + '.png') for name, sfx, _ in PL
                            if sfx in ('p1', 'p2', 'p3', 'p1_solace', 'p1_meridian') and os.path.exists(FINAL + name + '.png')}
    REP['review_probes_note'] = ('corp/src/rb_probes.py: each box is derived from the capture masks or the geometry of that plate, so it lands on what it '
                                 'names; old_box / old_L = the 2026-11-02 measure.py box read on the same plate, for comparison')
except Exception as e:
    REP['review_probes'] = 'failed: %r' % e

# ------------------------------------------------------------------ 3. cards
cf = WORK + 'card_checks.json'
REP['cards'] = json.load(open(cf)) if os.path.exists(cf) else 'missing (run final_cards.py checks)'

# ------------------------------------------------------------------ 4. corp skins: tape match, pink share, kind dE, Meridian hazard
Y, X = np.mgrid[0:1080, 0:1920]
rho = np.hypot(X - CC[0], Y - CC[1])
ring = (rho > 214) & (rho < 500)


def hsv(a):
    mx, mn = a.max(2), a.min(2)
    s = (mx - mn) / np.maximum(mx, 1)
    dd = np.maximum(mx - mn, 1e-6)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    return h, s, mx / 255


corp = {}
ims = {n: np.asarray(Image.open(FINAL + f).convert('RGB')).astype(np.float32) for n, f in
       (('neutral', 'p1_decide.png'), ('solace', 'p1_decide_solace.png'), ('meridian', 'p1_decide_meridian.png')) if os.path.exists(FINAL + f)}
if 'neutral' in ims:
    base = ims['neutral']
    h, s, v = hsv(base)
    tape = ring & (s < 0.18) & (v > 0.62)
    corp['tape_px'] = int(tape.sum())
    for n, a in ims.items():
        dmax = np.abs(a - base).max(2)
        corp['tape_match_pct_%s' % n] = round(float((dmax[tape] <= 6).mean() * 100), 1)
        hh, ss, vv = hsv(a)
        pink = ring & (hh > 315) & (hh < 350) & (ss > 0.40) & (vv > 0.5)
        corp['pink_pct_enemy_zone_%s' % n] = round(float(pink.sum() / ring.sum() * 100), 3)
# real-plate unit wash read-back (median colour per unit cell, dE2000 between kinds in one ring)
try:
    os.environ['LW_SKIN'] = '0'
    import de_kinds as DK
    from wr_geo import cell_poly, unit_bounds
    rb = {}
    for n, a in ims.items():
        med = {}
        for u in J['f1']['units']:
            b0, b1 = unit_bounds(u)
            m = Image.new('L', (1920, 1080), 0)
            ImageDraw.Draw(m).polygon(cell_poly(u['dep'], b0, b1, kind='unit'), fill=255)
            m = np.asarray(m) > 0
            med[u['id']] = (u['kind'], u['dep'], np.median(a[m], 0))
        o = {}
        for p in med:
            for q in med:
                if p < q and med[p][1] == med[q][1] and med[p][0] != med[q][0]:
                    o['%d%s-%d%s ring%d' % (p, med[p][0], q, med[q][0], med[p][1])] = round(DK.de2000(DK.rgb2lab(med[p][2]), DK.rgb2lab(med[q][2])), 1)
        rb[n] = o
    corp['kind_dE2000_plate_readback'] = rb
except Exception as e:
    corp['kind_dE2000_plate_readback'] = 'failed: %r' % e
corp['kind_dE2000_note'] = ('2026-11-03 rebuild: the cell fills are neutral slate with a low-chroma skin tint and kind_gain is 1.0 on every skin, so the '
                            'first-pass swatch table no longer applies; the plate read-back above is the measure')
# Meridian hazard: stripe saturation (first pass vs final) and the black gap between hazard paint and amber game marks
mer = {}
for tag, fp in (('first_pass', LOCK + 'corp/p1_decide_meridian.png'), ('final', FINAL + 'p1_decide_meridian.png')):
    if not os.path.exists(fp):
        continue
    a = np.asarray(Image.open(fp).convert('RGB')).astype(np.float32)
    hh, ss, vv = hsv(a)
    rim = (rho >= 490) & (rho <= 499.5)
    stripe = rim & (hh >= 15) & (hh <= 40) & (vv > 0.55) & (ss > 0.3)
    bez = (rho >= 386) & (rho <= 424)
    haz = ((rim | bez) & (hh >= 18) & (hh <= 36) & (ss > 0.45) & (vv > 0.55))
    amber = (rho >= 214) & (rho <= 430) & (hh >= 38) & (hh <= 56) & (ss > 0.55) & (vv > 0.6)
    dist = ndi.distance_transform_edt(~haz)
    mer[tag] = dict(rim_stripe_mean_sat=round(float(ss[stripe].mean()), 3) if stripe.any() else None,
                    bezel_hazard_px=int((haz & bez).sum()), amber_px=int(amber.sum()),
                    min_gap_amber_to_hazard_px=round(float(dist[amber].min()), 1) if amber.any() else None)
corp['meridian_hazard'] = mer
corp['meridian_rule'] = 'O-29 fix 5: hazard paint chroma -25 % (rim and bezel lip), inner bezel lip black (no stripe), gap amber mark to hazard paint >= 2 px'
REP['corp'] = corp

# ------------------------------------------------------------------ 5. game information (draw-call text vs state)
info = {}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_render as CR
norm = lambda s: re.sub(r'[^A-Z0-9]', '', str(s).upper().replace('\u00d7', 'X'))
hands = {'p1': J['f1']['hand'], 'p2': J['f2']['hand'], 'p2b': J['f1']['hand'],
         'p3': [c for c in J['f1']['hand'] if c not in [a[0] for a in J['f2']['played']]]}
req = ['TURN', 'SHIFTING WAVES', 'WAVES %d LEFT' % J['f1']['waves_left'], 'W4', 'W5', 'W6', 'NOW W1', '+1 W2', '+2 W3', 'YOU', 'LANDS', 'THROUGH', 'RAW', 'SHOT', 'BRACE', 'RIDER',
       'SPLIT', 'ABSORBED', 'SOAK', 'NEXT', 'WIN', 'SLICES KEPT', 'KILL ADJUSTER', 'TRACE LOW', 'RAM', 'TRACE', 'ENDS = HEAT', 'BREAKER', 'SEND IT', 'UNDO', 'CELL-9']
cards_ok, words_missing = {}, {}
for name, sfx, _ in PL:
    c = chk(sfx)
    if not c or sfx.startswith('nowords'):
        continue
    beat = sfx.split('_')[0]
    cl = c['cardlog']
    r = {}
    for card in hands[beat]:
        keys = [k for k in cl if k.startswith(card + '|0')]
        strs = cl[keys[0]] if keys else []
        sp = CR.CARDS[card]
        exp = [sp['nm'], sp['fam'], sp['txt'], str(sp['cost'])] + (['+' + str(sp['loud'])] if sp['loud'] else []) + (['\u00d7' + sp['mult']] if sp.get('mult') else [])
        # 2026-11-04 (gate 1): the rules text wraps to two lines at a word break (stage 2), so it is drawn as two strings; it counts as drawn when
        # the card's strings, joined, contain it (letters and digits only)
        joined = norm(' '.join(str(x_) for x_ in strs))
        r[card] = dict(missing=[e for e in exp if e not in strs and not (e == sp['txt'] and norm(e) in joined)], state_cost=J['cards'][card][0], state_trace=J['cards'][card][1],
                       rules_lines=[x_ for x_ in strs if norm(x_) and norm(x_) in norm(sp['txt'])])
    if beat == 'p3':
        # played slots: the liner draws the card name (fix 4); text from the liner render is not hooked, so read it from the state
        r['played_slots_named'] = [a[0] for a in J['f2']['played']]
    cards_ok[name] = r
    jn = norm(''.join(c['textlog']))
    words_missing[name] = [w for w in req if norm(w) not in jn]
info['cards_drawn'] = cards_ok
info['cards_all_fields_drawn'] = all(not v['missing'] for b in cards_ok.values() for k, v in b.items() if isinstance(v, dict))
info['required_words_missing'] = words_missing
info['state_cards_table'] = {n: dict(state=v, drawn=[CR.CARDS[n]['cost'], CR.CARDS[n]['loud']], ok=v == [CR.CARDS[n]['cost'], CR.CARDS[n]['loud']]) for n, v in J['cards'].items()}
nw = chk('nowords')
if nw:
    info['nowords_alnum_text_calls'] = len([t for t in nw['textlog'] if any(ch.isalnum() for ch in t)])
REP['game_info'] = info
nf = WORK + 'numbers.json'
if os.path.exists(nf):
    REP['game_info']['tower_numbers'] = json.load(open(nf))

gf = WORK + 'grammar_check.json'
if os.path.exists(gf):
    REP['grammar_step3'] = json.load(open(gf))
json.dump(REP, open(FINAL + 'checks.json', 'w'), indent=1, default=str)
print('checks.json written', REP['all_pass'], flush=True)


# ------------------------------------------------------------------ 6. grey proof (real WPAP cards) and before / after
def grey(im):
    a = np.asarray(im.convert('RGB'), np.float32)
    g = lum(a)
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert('RGB')


def lab(im, t, xy=(10, 6), c=(255, 226, 0)):
    ImageDraw.Draw(im).text(xy, t, font=mo, fill=c, stroke_width=2, stroke_fill=(0, 0, 0))


p1 = Image.open(FINAL + 'p1_decide.png').convert('RGB')
W2 = 1900
# every panel label sits in its own band above the panel (2026-11-03 stage 2: labels drawn over the plate hid the W6 ticket and card tops)
y2 = 60 + 640                          # corp rows start (their labels sit in the 30 px band above)
gp = Image.new('RGB', (W2, y2 + 523 + 10), (20, 20, 20))
d = ImageDraw.Draw(gp)
d.text((16, 12), 'GREY PROOF (luma only): final p1 neutral with the real WPAP cards, then hand and wheel at 1x, then Solace and Meridian', font=an, fill=(255, 255, 255))
gp.paste(grey(p1).resize((960, 540), Image.LANCZOS), (10, 60))
hand_c = grey(p1.crop((880, 760, 1920, 1080)))
gp.paste(hand_c.resize((920, int(320 * 920 / 1040)), Image.LANCZOS), (975, 90))
lab(gp, 'hand 1x (cropped, scaled 0.88)', (985, 60))
wh = grey(p1.crop((300, 300, 772, 780)))
gp.paste(wh.resize((250, 254), Image.LANCZOS), (980, 412))
lab(gp, 'tower', (986, 382))
cs = FINAL + 'card_sheet.jpg'
if os.path.exists(cs):
    # TOWER (Spin 3, Brace) and WAVE (Twist, Trigger) from the card sheet's normal row: the type plates in grey
    sh_ = Image.open(cs).convert('RGB')
    import card_render as _CRd
    bw = int(round(176 * 1.10 * 1.5)); mg_ = _CRd.margin_px(int(bw * 1.1)); cw_ = int(bw * 1.1) + 2 * mg_ + 6
    ch_ = int(250 * bw / 176 * 1.1) + 2 * mg_ + 6
    strip = Image.new('RGB', (cw_ * 4, ch_))
    for k_, idx in enumerate((2, 3, 8, 10)):
        strip.paste(sh_.crop((250 + idx * cw_, 120, 250 + (idx + 1) * cw_, 120 + ch_)), (k_ * cw_, 0))
    strip = grey(strip)
    s_ = min(650 / strip.width, 250 / strip.height)
    gp.paste(strip.resize((int(strip.width * s_), int(strip.height * s_)), Image.LANCZOS), (1245, 412))
    lab(gp, 'TOWER teal | WAVE lilac, grey', (1250, 382))
for i, (n, f) in enumerate((('solace', 'p1_decide_solace.png'), ('meridian', 'p1_decide_meridian.png'))):
    if os.path.exists(FINAL + f):
        g = grey(Image.open(FINAL + f)).resize((930, 523), Image.LANCZOS)
        lab(gp, n, (14 + i * 945, y2 - 30))
        gp.paste(g, (10 + i * 945, y2))
gp.save(FINAL + 'grey_proof.jpg', quality=90)
print('grey_proof written')

first = Image.open(LOCK + 'assembled/p1_decide.png').convert('RGB')
cols = [('locked first pass (ART CALL 53)', first), ('rebuild 2026-11-03', p1)]
Wc = 940
crops = [((830, 740, 1910, 1080), 'hand'), ((440, 110, 640, 200), 'digit 0 + tape'), ((430, 880, 680, 960), 'digit 3 + HOLD THEN'), ((300, 300, 772, 780), 'wheel'),
         ((1068, 0, 1910, 300), 'bill'), ((1100, 420, 1910, 800), 'room')]
# every label sits in its own 30 px band above its panel (2026-11-03 stage 2: labels drawn over the crops hid the bill header and the room)
LB = 30
rows_h = [529] + [int((c[0][3] - c[0][1]) * min(Wc / (c[0][2] - c[0][0]), 2.4 if i in (1, 2) else 1.0)) for i, c in enumerate(crops)]
sheet = Image.new('RGB', (Wc * 2 + 30, 56 + sum(rows_h) + (10 + LB) * (len(rows_h) + 1) + 280), (14, 12, 22))
dd = ImageDraw.Draw(sheet)
dd.text((12, 10), 'before / after, p1_decide neutral: locked first pass | 2026-11-03 rebuild.  Rows: plate, hand, digit 0, digit 3, wheel, bill, room, squint', font=an, fill=(255, 255, 255))
for i, (t, im) in enumerate(cols):
    x = 10 + i * (Wc + 10)
    y = 56
    a = im.resize((Wc, 529), Image.LANCZOS)
    lab(sheet, t, (x + 4, y))
    sheet.paste(a, (x, y + LB)); y += LB + 529 + 10
    for j, (box, nm) in enumerate(crops):
        c = im.crop(box)
        k = min(Wc / c.width, 2.4 if j in (1, 2) else 1.0) if j != 0 else Wc / c.width
        c = c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
        lab(sheet, nm, (x + (Wc - c.width) // 2 + 4, y))
        sheet.paste(c, (x + (Wc - c.width) // 2, y + LB)); y += LB + rows_h[j + 1] + 10
    s = im.resize((120, 67), Image.BOX).filter(ImageFilter.GaussianBlur(1.0)).resize((480, 268), Image.NEAREST)
    lab(sheet, 'squint (1/16 box, 1 px blur)', (x + (Wc - 480) // 2 + 4, y))
    sheet.paste(s, (x + (Wc - 480) // 2, y + LB))
sheet.save(FINAL + 'before_after.jpg', quality=90)
print('before_after written')
