import json
d = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
print(json.dumps(d['squint']['p1_decide'])[:800])
for p, v in d['squint'].items():
    z = v.get('zones', v)
    print(p, json.dumps({k: (vv if not isinstance(vv, dict) else {kk: vvv for kk, vvv in vv.items() if kk in ('loud', 'loud_pct', 'mean', 'p95')}) for k, vv in z.items()})[:400])
print(d['squint_note'])
