"""bd_collect.py <out.json> : gather work/solve_<room>.json params into one per-room params file (bd_tune format)."""
import sys, json
H = 'D:/rc_scratch/combat_redesign/locked/backdrop/work/'
out = {}
for r in ['bio', 'srv', 'gh', 'rec', 'lobby', 'event', 'shop']:
    out[r] = json.load(open(H + 'solve_%s.json' % r))['params']
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print(json.dumps({r: (p['hull_value'], p['chroma']) for r, p in out.items()}))
