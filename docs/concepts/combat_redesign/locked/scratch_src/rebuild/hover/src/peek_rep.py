import json, sys
j = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/%s.json' % sys.argv[1]))
for k in sys.argv[2:]:
    print(k, '=', json.dumps(j.get(k), default=str)[:3000])
