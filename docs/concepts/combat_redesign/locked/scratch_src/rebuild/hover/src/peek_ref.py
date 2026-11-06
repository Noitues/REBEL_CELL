import json, sys
j = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/%s.checks.json' % sys.argv[1]))
a = j['a_cell_contrast']
for k, v in (a.get("rings") or {}).items():
    print(k, json.dumps(v))
print([k for k in a.keys()])
