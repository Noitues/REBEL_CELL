"""peek4: loudness_order shapes in fx_timings.json (exploration)."""
import json

f = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/port/fx_timings.json', encoding='utf-8'))
for st, per in f['loudness_order'].items():
    print(st, type(per).__name__, list(per.keys()) if isinstance(per, dict) else len(per))
    for sk, v in (per.items() if isinstance(per, dict) else []):
        print('  ', sk, type(v).__name__, json.dumps(v)[:700])
