"""r2_more (round 2): squint tower zone, room rows, rim luma, draw asserts, text draws and C2 pair counts from rebuild/board/checks.json.
python r2_more.py"""
import sys, json
sys.dont_write_bytecode = True
ck = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))
print('squint_tower_zone', json.dumps(ck.get('squint_tower_zone'), default=str)[:900])
print('rim', json.dumps(ck['corp'].get('rim_luma_C18', {}).get('solace_vs_meridian')),
      {k: (v.get('band_mean_L'), v.get('dominant_cycles_per_turn'), v.get('dominant_amp_L')) for k, v in ck['corp'].get('rim_luma_C18', {}).items()
       if isinstance(v, dict) and 'band_mean_L' in v})
if '--marks' in sys.argv:
    for nm, r in ck['rb_checks'].items():
        b = r['b_value_order']
        mk = b.get('marks')
        rows = []
        if isinstance(mk, dict):
            for k, v in mk.items():
                if isinstance(v, dict) and 'p99' in v:
                    rows.append((v['p99'], k, v.get('p95')))
        for k, v in b.get('round2', {}).get('structure_rows', {}).items():
            rows.append((v['p99'], 'r2 ' + k, v['p95']))
        for k, v in b.get('round2', {}).get('token_discs', {}).items():
            rows.append((v['p99'], 'disc ' + k, v['p95']))
        rows.sort(reverse=True)
        print(nm, rows[:4])
    raise SystemExit(0)
for nm, r in ck['rb_checks'].items():
    b = r['b_value_order']
    room = [x for x in b.get('sorted', []) if isinstance(x, (list, tuple)) and str(x[0]).startswith('room')]
    c = r['c_cap_height']
    d = r['d_palette']
    da = ck['draw_asserts'].get(nm)
    print(nm, 'room', room, '| text n', c.get('n'), 'fail', c.get('n_fail'), 'smallest', c.get('smallest'), '| d pairs', d.get('n_pairs'),
          '| asserts', da.get('passed') if isinstance(da, dict) else da, '/', da.get('total') if isinstance(da, dict) else '',
          '| dots', ck['dash_audit'].get(nm, {}).get('pixel_dot_runs'))
