"""run rb_checks (with the round-2 checks) on corp/out/as_<sfx>.png and print a compact report.  python r2_check.py <sfx> [png]"""
import sys, os, json
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import rb_checks as RC
sfx = sys.argv[1]
png = sys.argv[2] if len(sys.argv) > 2 else 'D:/rc_scratch/combat_redesign/locked/corp/out/as_%s.png' % sfx
r = RC.run(sfx, png, sfx)
print(sfx, 'PLATE PASS' if r['plate_pass'] else 'PLATE FAIL', r['pass'])
print(RC.table_order(r))
b = r['b_value_order']
print('b fails', b['failures'])
bb = b['round2']
print('b unclassed px', bb['unclassed_px'], bb['unclassed_clusters'][:8])
for k, v in bb['structure_rows'].items():
    print('  struct %-44s p95 %5.1f p99 %5.1f med %5.1f px %d' % (k, v['p95'], v['p99'], v['median'], v['px']))
for k, v in bb['token_discs'].items():
    print('  disc %-8s p95 %5.1f p99 %5.1f px %d' % (k, v['p95'], v['p99'], v['px']))
for k, v in b['marks'].items():
    print('  mark %-36s p95 %5.1f p99 %5.1f px %d' % (k, v['p95'], v['p99'], v['px']))
a = r['a_cell_contrast']
for row in a['rows']:
    print('  a ring %d s%d u%s %-8s %-7s occ L* %5.1f empty L* %s ratio %s px %d' % (row['ring'], row['sector'], row['unit'], row['kind'], row['state'], row['occ_L'], row['empty_L'], row['ratio'], row['px']))
print('c fails', r['c_cap_height']['n_fail'], [(f['text'], f['cap_px'], f.get('where')) for f in r['c_cap_height']['failures']][:6], 'unc', r['c_cap_height']['uncaptured_text'][:4])
d = r['d_palette']
print('d fails', [(f['a'], f['b'], f['dE']) for f in d['failures']][:12])
for row in d['round2']['drawn_vs_token']:
    print('  drawn', row)
if d['round2']['solace_rim']:
    print('  rim', d['round2']['solace_rim'])
print('e', json.dumps({k: v for k, v in r['e_hand'].items() if k not in ('rule', 'rest_cards_covered_info')}))
for k in ('f_pencil', 'g_tickets', 'h_hud_rows', 'i_hot_core'):
    print(k, json.dumps({kk: vv for kk, vv in r[k].items() if kk != 'rule'})[:1500])
json.dump(r, open('D:/rc_scratch/combat_redesign/locked/round2/board/work/r2check_%s.json' % sfx, 'w'), indent=1, default=str)
