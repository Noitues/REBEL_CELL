"""peek3: cells and clock functions of skin_tables.json (exploration)."""
import json

s = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/port/skin_tables.json', encoding='utf-8'))
for k, v in s['cells'].items():
    print('cells', k, json.dumps(v)[:300])
for k, v in s['clock']['functions'].items():
    print('clock fn', k, json.dumps(v)[:500])
print('methods neutral', {k: (v or {}).get('source') for k, v in s['skins']['neutral']['methods'].items()})
m = s['skins']['meridian']['methods']['rim']
print('meridian rim', json.dumps(m)[:800])
