"""summarise rebuild/board/checks.json per plate: room numbers, ref, cell ratio, smallest cap, palette min dE, stage-2 measures"""
import sys, json
sys.dont_write_bytecode = True
J = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))
R = J['rb_checks']
S = J.get('stage2_measures', {})
print('all_pass', J['all_pass'])
for nm, r in R.items():
    b = r['b_value_order']
    room = [f for f in b['sorted'] if f['family'] == 'room']
    room = room[0] if room else None
    occ = [f for f in b['sorted'] if f['family'] == 'E cells occupied (glass)']
    a = r['a_cell_contrast']
    c = r['c_cap_height']
    d = r['d_palette']
    mind = min((x['dE'] for x in d['rows'] if x.get('pass_') is not None and not x.get('report_only')), default=None)
    s2 = S.get(nm, {})
    print('%-22s room mean %s p95 %s ref %s (%s) | occ p95 %s | box %s | cap n %d fail %d min %.1f | pal n %d min %s | hand %s tickets %s | pass %s' % (
        nm, room and room['mean'], room and room['p95'], b['room_ref']['value'], b['room_ref']['source'][:12], occ and occ[0]['p95'],
        b['probes']['review room box'], c['n'], c['n_fail'], min((x['cap_px'] for x in c['smallest']), default=0.0), d['n_pairs'], mind,
        s2.get('hand_margin_px'), min(g['ink_h'] for t in s2.get('ticket_glyphs', [[{'ink_h': 0}]]) for g in t) if s2 else None,
        r.get('pass')))
    if a.get('worst'):
        print('    a worst', a.get('worst'), 'occ NOW', a.get('occ_now_L'))
