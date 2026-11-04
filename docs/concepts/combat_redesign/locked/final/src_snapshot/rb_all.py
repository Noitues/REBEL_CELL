"""rb_all (2026-11-03 rebuild): run rb_checks on the published plates in locked/rebuild/board/ and print one block per plate.
python rb_all.py [job ...]      job = beat[:corp]; default all 15"""
import sys
sys.dont_write_bytecode = True
import rb_checks as RC
import rb_set as RS

a = sys.argv[1:] or ['%s:%s' % (b, c) for c in RS.CORPS for b in RS.BEATS]
summary = []
for x in a:
    beat, corp = (x.split(':') + ['neutral'])[:2]
    nm = RS.plate_name(beat, corp)
    r = RC.run(nm, RS.BOARD + nm + '.png', RS.sfx(beat, corp))
    summary.append((nm, r['pass'], r['plate_pass']))
    print('=' * 100)
    print(nm, 'PLATE PASS' if r['plate_pass'] else 'PLATE FAIL', r['pass'])
    print(RC.table_order(r))
    ac = r['a_cell_contrast']
    worst = min((row for row in ac['rows'] if row['gated']), key=lambda q: q['ratio'] or 0, default=None)
    print('a occ NOW L*', ac['occ_now_L_range'], 'rings', ac['rings'], 'worst', worst and (worst['ring'], worst['sector'], worst['kind'], worst['occ_L'], worst['ratio']))
    for row in ac['rows']:
        if row['gated'] and not row['pass_']:
            print('  a FAIL', row)
    print('b fails', r['b_value_order']['failures'])
    print('c fails', r['c_cap_height']['n_fail'], [(f['text'], f['cap_px'], f.get('where')) for f in r['c_cap_height']['failures']])
    print('d fails', [(f['a'], f['b'], f['dE']) for f in r['d_palette']['failures']])
    print('e', {k: v for k, v in r['e_hand'].items() if k not in ('rule', 'rest_cards_covered_info')})
print('=' * 100)
for nm, p, pp in summary:
    print('%-24s %s %s' % (nm, 'PASS' if pp else 'FAIL', ' '.join('%s=%s' % (k[0], 'ok' if v else 'X') for k, v in p.items())))
