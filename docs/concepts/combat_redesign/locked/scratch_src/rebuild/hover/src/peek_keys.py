import json, sys
c = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/%s.checks.json' % sys.argv[1]))
for k in ('hp_strip', 'ram', 'insets', 'options', 'slices', 'focus', 'collide', 'dashes', 'b_value', 'c_cap_height', 'd_palette'):
    v = c.get(k, {})
    print(k, sorted(v.keys()) if isinstance(v, dict) else type(v))
fc = c['focus'].get('calls', [])
print('focus call keys', sorted(fc[0].keys()) if fc else None)
