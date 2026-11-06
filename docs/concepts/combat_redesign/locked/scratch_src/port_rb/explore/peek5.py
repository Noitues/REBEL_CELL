"""peek5: one CDHL effect raw, and the port record for it (exploration)."""
import json

L = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
c = json.load(open(L + 'effects/timings_CDHL.json', encoding='utf-8'))
print(list(c.keys())[:20])
effs = c.get('effects', c)
k = 'fx_kill' if 'fx_kill' in effs else list(effs.keys())[0]
print(k, json.dumps(effs[k])[:1500])
p = json.load(open(L + 'port/fx_timings.json', encoding='utf-8'))
e = [x for x in p['effects'] if x['id'] == 'fx_kill'][0]
print({a: b for a, b in e.items() if a not in ('phases', 'loud_transient')})
