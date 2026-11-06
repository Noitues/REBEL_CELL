"""numbers_final2.py: room means (gated and as seen), squint, dying-glass extras and the c14 record from final/checks.json.
Reads only.  usage: python numbers_final2.py"""
import json

F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'
C = json.load(open(F, encoding='utf-8'))
RB = C['rb_checks']
gm, sm = [], []
for p, v in RB.items():
    s = {x['family']: x for x in v['b_value_order']['sorted']}
    r, a = s.get('room'), s.get('room as seen (scrim kept, info)')
    print('%-22s room mean %.1f p95 %.1f | as seen mean %.1f p95 %.1f' % (p, r['mean'], r['p95'], a['mean'], a['p95']))
    gm.append(r['mean'])
    sm.append(a['mean'])
print('room mean %.1f-%.1f ; as seen %.1f-%.1f' % (min(gm), max(gm), min(sm), max(sm)))
st = C['squint_tower_zone']
print('squint', {k: round(100 * v['final'], 1) for k, v in st.items()})
print('c14', json.dumps(C['c14_determinism'])[:1500])
txt = json.dumps(C)
for needle in ('hatch_cut', 'between_hatch', 'glass_px', '3.82', '5.25', 'dying_glass'):
    i = txt.find(needle)
    print(needle, i, txt[max(0, i - 200):i + 300] if i >= 0 else '')
a = RB['p1_decide']['a_cell_contrast']
print('a keys', list(a.keys()))
print('a rows p1', json.dumps(a['rows'])[:3000])
