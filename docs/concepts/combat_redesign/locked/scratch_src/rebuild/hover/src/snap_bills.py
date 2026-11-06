"""snap_bills.py <out.json> <name ...> : the sim-derived plan record of each plate (bill, marks, note, hud numbers) for a before/after compare"""
import sys, json
out = {}
for nm in sys.argv[2:]:
    r = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/%s.json' % nm))
    out[nm] = dict(bill=r.get('bill'), marks=r.get('marks'), note=r.get('note'), asserts=r.get('asserts', {}).get('passed'),
                   hud=r.get('hud2_R', {}).get('vals') if isinstance(r.get('hud2_R'), dict) else None, obj=(r.get('obj2_R') or {}).get('ram_pips'))
json.dump(out, open(sys.argv[1], 'w'), indent=1, sort_keys=True, default=str)
print('ok', len(out))
