import json, sys
j = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/%s.checks.json' % sys.argv[1]))
for r in j['a_cell_contrast'].get('rows', []):
    print(('FAIL ' if r['gated'] and not r['pass_'] else '     ') + json.dumps(r))
