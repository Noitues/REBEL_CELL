"""print a table of the published checks (for NOTES.md)"""
import json
d = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/hover/checks.json'))
print(d['all_pass'])
for k, v in d['summary'].items():
    f = d['full'][k]
    print(k, v['asserts'], v['inset_asserts'], 'lift', v['lift_dx'], f.get('lift_cy'), 'sq', v['squint_plate']['mean'], v['squint_plate']['loud'], 'tower', v['squint_tower']['loud'],
          'litdim', v['lit_vs_dim'], 'z', f.get('z_order'), 'drop', sum(1 for c in f.get('corners', []) if c['ok'] == 'dropped'),
          'bill', v['bill'], 'hmin', v['hand_min_r'])
