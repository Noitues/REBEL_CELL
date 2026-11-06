"""peek_hchk.py <checks.json> <plate> [key]: print one plate's check entries (read only)"""
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
p = d.get('plates', d)
if sys.argv[2] not in p:
    print('keys', list(p)[:40]); raise SystemExit
e = p[sys.argv[2]]
if len(sys.argv) > 3:
    print(json.dumps(e.get(sys.argv[3]), indent=1)[:6000])
else:
    for k, v in e.items():
        s = json.dumps(v)
        print(k, s[:300])
