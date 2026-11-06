import json, sys
j = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/%s.checks.json' % sys.argv[1]))
keys = sys.argv[2:] or [k for k, v in j['pass'].items() if not v]
for k in keys:
    v = j.get(k)
    if isinstance(v, dict):
        v = {kk: vv for kk, vv in v.items() if kk not in ('rows',) or len(json.dumps(vv)) < 1500}
    print('==', k, json.dumps(v, default=str)[:2500])
print('PASS', j['pass'])
