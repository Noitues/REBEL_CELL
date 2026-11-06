"""print the d2_drawn section (drawn_vs_token rows and failures) of one or more plates.  python d2_show.py <name> [name...]"""
import sys, json
HV = 'D:/rc_scratch/combat_redesign/locked/round2/hover/chk/'
for n in sys.argv[1:]:
    c = json.load(open(HV + '%s.checks.json' % n))
    d = c.get('d2_drawn') or {}
    print('==', n, 'pass', d.get('pass_'), 'failures', d.get('failures'))
    for r in d.get('drawn_vs_token') or []:
        print('   ', {k: v for k, v in r.items() if k not in ('hist',)})
    for k in sorted(d):
        if k not in ('drawn_vs_token', 'failures', 'pass_', 'rule', 'drawn_vs_corp_ink', 'solace_rim'):
            print('   %s: %s' % (k, json.dumps(d[k])[:400]))
