"""hv_b2.py name ...: the b2_bright block of round2/hover/chk/<name>.checks.json (failures, refs, hover rows)"""
import sys, json
for nm in sys.argv[1:]:
    c = json.load(open('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/%s.checks.json' % nm))
    b = c.get('b2_bright') or c.get('checks', {}).get('b2_bright')
    if b is None:
        print(nm, 'keys', list(c)[:40]); continue
    print('=' * 30, nm, 'pass', b.get('pass_'))
    print(' failures_gated', b.get('failures_gated'))
    print(' failures', b.get('failures'))
    print(' hot_p95_lit', b.get('hot_p95_lit'), 'tower_p95_lit', b.get('tower_p95_lit'), 'send', b.get('send_p95'), 'focus_margin', b.get('focus_margin_under_send'), 'focus_vs_hot', b.get('focus_vs_hot_reported'))
    for k, v in (b.get('hover_rows') or {}).items():
        print('  row', k, {q: v.get(q) for q in ('p95', 'p99', 'px', 'gated')})
    print(' unclassed', b.get('unclassed_px'), (b.get('unclassed_clusters') or [])[:5])
