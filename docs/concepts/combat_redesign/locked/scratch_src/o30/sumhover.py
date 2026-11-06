import json
d = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/hover/checks.json'))
print(d['all_pass'])
for k, v in d['summary'].items():
    print(k, v['asserts'], 'dots', v['pixel_dot_runs'], 'hand', v['hand_min_r'], 'lift', v['lift_min_r'], v['lift_scale'], v['lift_dx'], v['lift_cy'],
          'near', v['lift_px_near_landing_marks'], 'tower', v['squint_tower']['loud'], 'rings', [(r.get('tag'), r.get('ry')) for r in v['hud_rings']])
    fl = d['full'][k]
    if fl.get('pixel_dot_run_list'):
        print('   RUNS', fl['pixel_dot_run_list'])
    fits = fl.get('hud_ring_fits', [])
    print('   fits', [(f.get('tag'), 'brackets' if 'brackets_half_deg' in f else ('open' if 'open_gap_deg' in f else 'ring'), f.get('ok')) for f in fits])
