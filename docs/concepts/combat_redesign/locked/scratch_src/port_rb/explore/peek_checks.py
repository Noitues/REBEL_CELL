"""peek_checks: shape of final/checks.json, backdrop/checks.json, grade.json, transitions/metrics.json (exploration)."""
import json, os

L = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'


def sh(v, n=300):
    return json.dumps(v)[:n]


c = json.load(open(L + 'final/checks.json', encoding='utf-8'))
print('top', list(c.keys()))
print('all_pass', sh(c['all_pass'], 800))
rb = c['rb_checks']
print('rb plates', list(rb.keys()))
p = rb['p1_decide']
for k, v in p.items():
    if isinstance(v, dict):
        print(' ', k, {kk: (sh(vv, 160)) for kk, vv in v.items() if kk not in ('rows',)})
    else:
        print(' ', k, sh(v, 200))
for k in ('stage2_measures', 'squint', 'squint_tower_zone', 'review_probes', 'cards', 'corp', 'room_grade', 'hand_vs_board', 'occlusion', 'dash_audit', 'draw_asserts', 'collisions_marks'):
    print('==', k, sh(c.get(k), 700))
b = json.load(open(L + 'backdrop/checks.json', encoding='utf-8'))
print('== backdrop top', list(b.keys()), sh(b.get('plates', {}).get('p1_bio'), 500))
g = json.load(open(L + 'backdrop/grade.json', encoding='utf-8'))
print('== grade', list(g.keys()), g.get('version'), sh(g.get('corp_room')), sh(g.get('order'), 500))
print('== grade bio', sh(g['rooms']['bio'], 1500))
t = L + 'transitions/metrics.json'
if os.path.exists(t):
    print('== trans', sh(json.load(open(t, encoding='utf-8')), 800))
