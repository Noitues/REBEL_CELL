import json, sys
for nm in sys.argv[1:]:
    p = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/%s.checks.json' % nm))['pencil']
    print('%-24s %s %s' % (nm, p['mask'], p['failures']))
