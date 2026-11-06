"""peek2: a few nested shapes in final/checks.json (exploration)."""
import json

L = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
c = json.load(open(L + 'final/checks.json', encoding='utf-8'))
a = c['rb_checks']['p1_decide']['a_cell_contrast']
print('a rings0', json.dumps(a['rings']['0'])[:900])
print('room_grade keys', list(c['room_grade'].keys()))
for k, v in c['room_grade'].items():
    if k not in ('params',):
        print('  ', k, json.dumps(v)[:500])
print('cards keys', list(c['cards'].keys()))
print('cards no_ram', json.dumps(c['cards'].get('no_ram_word'))[:300])
print('squint_tower_zone_note', c.get('squint_tower_zone_note'))
print('squint_note', c.get('squint_note'))
print('hand_rule', c.get('hand_rule'))
print('stage2_rule', json.dumps(c.get('stage2_rule'))[:400])
print('review_probes_note', c.get('review_probes_note'))
print('dash_audit_note', c.get('dash_audit_note'))
d = c['rb_checks']['p1_decide']['d_palette']['rows'][0]
print('d row0', d)
b = json.load(open(L + 'backdrop/checks.json', encoding='utf-8'))
print('bd targets', json.dumps(b['targets'])[:600])
print('bd plates', list(b['plates'].keys()))
print('bd after', json.dumps(b['plates']['p1_bio']['after']['L'])[:400])
print('bd pass', json.dumps(b['pass'])[:300], b['all_pass'])
