"""numbers_final.py: read final/checks.json (the round-2 board, measured on the published PNGs) and print every number
final/NOTES.md "2026-11-04 round 2" quotes, as ranges over the plates, so the NOTES text can be checked against it.
Reads only; writes nothing.  usage: python numbers_final.py"""
import json

F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'
C = json.load(open(F, encoding='utf-8'))
RB = C['rb_checks']
PL = list(RB.keys())


def skin(p):
    return 'solace' if p.endswith('_solace') else 'meridian' if p.endswith('_meridian') else 'neutral'


def beat(p):
    return p.replace('_solace', '').replace('_meridian', '')


def rng(v, f='%.1f'):
    v = [x for x in v if x is not None]
    if not v:
        return '-'
    lo, hi = min(v), max(v)
    return (f % lo) if lo == hi else (f % lo) + '-' + (f % hi)


print('plates:', len(PL), PL)
print('all_pass:', C['all_pass'])
print('plate_pass:', {p: RB[p].get('plate_pass') for p in PL})
print('\n# draw asserts')
for p, v in C['draw_asserts'].items():
    print('  ', p, v.get('passed'), '/', v.get('total'))
print('\n# c text draws')
for p in PL:
    c = RB[p]['c_cap_height']
    sm = c['smallest'][0]['cap_px'] if c['smallest'] else None
    print('  ', p, 'n', c['n'], 'fail', c['n_fail'], 'smallest', sm, 'parked', json.dumps(c.get('parked'))[:120])
print('\n# d pairs')
print('  n_pairs', rng([RB[p]['d_palette']['n_pairs'] for p in PL], '%d'), 'failures', sum(len(RB[p]['d_palette']['failures']) for p in PL),
      'lowest dE', min(r['dE'] for p in PL for r in RB[p]['d_palette']['rows']))
for p in PL:
    r2 = RB[p]['d_palette'].get('round2') or {}
    dv = r2.get('drawn_vs_token', [])
    print('  ', p, 'drawn:', '; '.join('%s %s dE %.1f' % (d['cls'], d['drawn_hex'], d['dE']) for d in dv))
    ci = r2.get('drawn_vs_corp_ink', [])
    if ci:
        m = min(ci, key=lambda d: d.get('dE', 999))
        print('      corp ink min', json.dumps(m)[:300])
    if r2.get('solace_rim'):
        print('      solace_rim', json.dumps(r2['solace_rim'])[:600])
print('\n# a cell contrast')
for p in PL:
    a = RB[p]['a_cell_contrast']
    gated = [r for r in a['rows'] if r.get('gated')]
    live = [r for r in gated if r['state'] != 'dying']
    dying = [r for r in gated if r['state'] == 'dying']
    lo = min(gated, key=lambda r: r['ratio']) if gated else None
    lol = min(live, key=lambda r: r['ratio']) if live else None
    print('  ', p, 'occ_now', a['occ_now_L_range'], 'lowest', lo and (lo['ring'], lo['kind'], lo['state'], lo['ratio']),
          'lowest live', lol and (lol['ring'], lol['kind'], lol['ratio']),
          'dying', [(r['kind'], r['occ_L'], r['empty_L'], r['ratio'], r['px']) for r in dying],
          'refs', {k: v['reference_L'] for k, v in a['rings'].items()})
    for k in a:
        if k not in ('rows', 'rings', 'occ_now_L_range', 'adjuster_hp', 'rule', 'pass_'):
            print('      extra key', k, json.dumps(a[k])[:400])
print('\n# b value order: sorted p95, HOT, structure rows, token discs, unclassed')
for p in PL:
    b = RB[p]['b_value_order']
    s = {x['family']: x['p95'] for x in b['sorted']}
    r2 = b.get('round2', {})
    st = r2.get('structure_rows', {})
    td = r2.get('token_discs', {})
    print('  ', p, 'chain', ' > '.join('%s %.1f' % (k, v) for k, v in s.items()))
    print('      unclassed', r2.get('unclassed_px'), 'struct', '; '.join('%s %.1f/%.1f' % (k, v['p95'], v['p99']) for k, v in st.items()))
    if td:
        print('      discs p95', rng([v['p95'] for v in td.values()]), 'p99', rng([v['p99'] for v in td.values()]),
              'max', max(td.items(), key=lambda kv: kv[1]['p95'])[0], max(v['p95'] for v in td.values()), max(v['p99'] for v in td.values()))
    mk = b.get('marks', {})
    others = [(k, v['p99']) for k, v in mk.items() if isinstance(v, dict) and 'p99' in v]
    if others:
        mx = max(others, key=lambda kv: kv[1])
        print('      highest mark p99', mx)
    print('      room_ref', b.get('room_ref'))
print('\n# e hand')
for p in PL:
    e = RB[p]['e_hand']
    print('  ', p, 'send', e['hand_x_send_px'], 'undo', e['hand_x_undo_px'], 'sib', json.dumps(e['lifted_vs_sibling']), 'lift', json.dumps(e.get('lift')))
print('\n# f pencil')
for p in PL:
    f = RB[p]['f_pencil']
    if f['present']:
        print('  ', p, json.dumps(f['rows']))
print('\n# g tickets')
for p in PL:
    g = RB[p]['g_tickets']
    if g['present']:
        print('  ', p, [r['edge_L_p90'] for r in g['rows']], 'hz', g['hazard_ticks'])
print('\n# h hud rows')
for p in PL:
    h = RB[p]['h_hud_rows']
    print('  ', p, h.get('measured'), h.get('row_record'), 'reserve', h.get('reserve'))
print('\n# i hot core')
for p in PL:
    i = RB[p]['i_hot_core']
    if i['present']:
        print('  ', p, 'w', i['core_w_px'], 'L', i['core_L'], 'cell', i['cell_L'], 'core/cell', i['core_vs_cell'], 'fill/cell', i['fill_vs_cell_reported'],
              'under', [(s['w'], s['box']) for s in i['strokes_under_min']], 'per stroke', json.dumps(i['core_w_per_stroke'])[:300])
print('\n# squint tower zone')
print('  ', json.dumps(C['squint_tower_zone'])[:1500])
print('\n# room grade')
print('  ', json.dumps(C['room_grade'])[:2500])
print('\n# corp')
for k, v in C['corp'].items():
    print('  ', k, json.dumps(v)[:700])
print('\n# c14')
print('  ', json.dumps(C['c14_determinism'])[:800])
print('\n# dash audit')
print('  ', {p: (v['dashed_line_calls'], v['dotted_mark_calls'], v['pixel_dot_runs']) for p, v in C['dash_audit'].items()})
print('\n# stage2')
for p, v in C['stage2_measures'].items():
    print('  ', p, 'margin', v['hand_margin_px'], 'glyph ink', rng([g['ink_h'] for row in v['ticket_glyphs'] for g in row], '%d'),
          'p90', rng([g['p90_L'] for row in v['ticket_glyphs'] for g in row]))
print('\n# hand vs board')
print('  ', {p: (v['hand_min_r_px'], v['hand_px_inside_r455']) for p, v in C['hand_vs_board'].items()})
