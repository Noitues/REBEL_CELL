"""rb_checks on rebuild/board plates with the round-2 details printed (b2 FOCUS row, d2 rows, e hand, f pencil rows, g tickets, i HOT core)
python rb_detail.py job ...      job = beat[:corp]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import os
os.chdir('D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_checks as RC
import rb_set as RS
for x in sys.argv[1:]:
    beat, corp = (x.split(':') + ['neutral'])[:2]
    nm = RS.plate_name(beat, corp)
    r = RC.run(nm, RS.BOARD + nm + '.png', RS.sfx(beat, corp))
    print('=' * 100)
    print(nm, 'PLATE PASS' if r['plate_pass'] else 'PLATE FAIL', r['pass'])
    print(RC.table_order(r))
    b = r['b_value_order']
    print('b fails', b['failures'])
    b2 = b['round2']
    print('b2 send95', b2.get('send_p95'), 'unclassed', b2['unclassed_px'], b2['unclassed_clusters'][:4])
    for k, v in b2['structure_rows'].items():
        print('   row %-48s p95 %5.1f p99 %5.1f %s %s' % (k, v['p95'], v['p99'], v.get('rules'), {q: v[q] for q in ('vs_hot_reported', 'vs_tower_reported') if q in v}))
    d = r['d_palette']['round2']
    for row in d['drawn_vs_token']:
        print('   d2 %-18s %s dE %s (plain modal %s dE %s)' % (row['cls'], row['drawn_hex'], row['dE'], row['modal_hex_info'], row['dE_modal_info']))
    print('d fails', [(f['a'], f['dE']) for f in r['d_palette']['failures']])
    e = r['e_hand']
    print('e', json.dumps({k: v for k, v in e.items() if k not in ('rule', 'rest_cards_covered_info')})[:1500])
    f = r['f_pencil']
    for row in f['rows']:
        print('   f %-6s gated %s pass %s wax %s stroke %s ink/side %s grain %s px %s' % (row['cls'], row.get('gated'), row['pass_'], row['wax_w'], row['stroke_w'],
                                                                                 row['ink_per_side'], row['grain_L_std'], row['px']))
    print('f fails', f['failures'])
    g = r['g_tickets']
    print('g', g['pass_'], json.dumps({k: v for k, v in g.items() if k not in ('rule',)})[:900])
    i = r['i_hot_core']
    print('i', i['pass_'], json.dumps({k: i.get(k) for k in ('core_w_px', 'core_w_per_stroke', 'core_vs_cell', 'fill_vs_cell_reported', 'strokes_under_min', 'failures')})[:1200])
    print('h', r['h_hud_rows']['pass_'], r['h_hud_rows'].get('failures'))
