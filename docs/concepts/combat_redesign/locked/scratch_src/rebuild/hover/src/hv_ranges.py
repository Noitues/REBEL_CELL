"""hv_ranges.py : the ranges over every plate of the numbers hover/NOTES.md quotes (prints only)"""
import sys, json, glob, os
sys.dont_write_bytecode = True
HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/'
names = sorted(os.path.basename(p)[:-12] for p in glob.glob(HERE + 'chk/h*.checks.json'))
C = {n: json.load(open(HERE + 'chk/%s.checks.json' % n)) for n in names}
R = {n: json.load(open(HERE + 'chk/%s.json' % n)) for n in names}


def rng(vals):
    v = [x for x in vals if x is not None]
    return (min(v), max(v)) if v else None


print('plates', len(names), 'pass', sum(1 for n in names if C[n]['plate_pass']))
print('fails', {n: [k for k, v in C[n]['pass'].items() if not v] for n in names if not C[n]['plate_pass']})
allk = sorted({k for c in C.values() for k in c['pass']})
print('per check passing plates', {k: sum(1 for c in C.values() if c['pass'].get(k)) for k in allk})
print('dim', rng([c['b_value'].get('dim_luma_ratio') for c in C.values()]), 'lit', rng([c['b_value'].get('lit_luma_ratio') for c in C.values()]))
print('dim board p95 L', rng([c['b_value'].get('dim_board_p95_L') for c in C.values()]),
      'pencil p95', rng([(c['b_value'].get('pencil wax (L6 + L5)') or {}).get('p95_L') for c in C.values()]),
      'focus p95', rng([(c['b_value'].get('FOCUS corners') or {}).get('p95_L') for c in C.values()]),
      'lifted p95', rng([c['b_value'].get('lifted card p95_L') for c in C.values()]), 'rest p95', rng([c['b_value'].get('resting hand p95_L') for c in C.values()]))
for k in ('L6_wax', 'L6_all', 'L6_ink_each_side', 'L5_wax', 'L5_all'):
    print('pencil', k, rng([c['pencil']['mask'].get(k) for c in C.values()]))
print('chevrons', rng([(c['pencil'].get('L5_chevrons_reported') or {}).get('wax') for c in C.values()]),
      rng([(c['pencil'].get('L5_chevrons_reported') or {}).get('all') for c in C.values()]))
print('png wax', rng([(c['pencil'].get('png_L6') or {}).get('wax_px') for c in C.values()]), 'png ink', rng([(c['pencil'].get('png_L6') or {}).get('ink_px') for c in C.values()]))
print('grain std', rng([c['grain'].get('L_std') for c in C.values()]), 'p99', rng([c['grain'].get('L_p99') for c in C.values()]), 'plan L', rng([c['grain'].get('plan_L') for c in C.values()]),
      'band', [(n, c['grain'].get('glow_band_yellow_px'), c['grain'].get('board_band_yellow_px')) for n, c in C.items() if c['grain'].get('glow_band_yellow_px')])
print('focus dE', rng([c['focus'].get('core_median_dE') for c in C.values()]), 'hex', sorted({c['focus'].get('core_median_hex') for c in C.values() if c['focus'].get('core_median_hex')}),
      'old lime', rng([c['focus'].get('old_lime_px') for c in C.values()]), 'corners', sorted({x['corners'] for c in C.values() for x in c['focus'].get('calls', [])}),
      'bbox', rng([b for c in C.values() for x in c['focus'].get('calls', []) for b in (x.get('bbox_px') or [])]))
print('rings', {n: [(f['tag'], f.get('form'), f.get('n')) for f in c['rings'].get('fits', [])] for n, c in C.items() if c['rings'].get('fits')})
print('ring px on hero / words', rng([c['rings'].get('pencil_on_hero_px') for c in C.values()]), rng([c['rings'].get('pencil_on_hud_words_px') for c in C.values()]),
      'bracket text', sum(len(c['rings'].get('bracket_text') or []) for c in C.values()))
print('hp strip', rng([sum(c['hp_strip']['px'].values()) if isinstance(c['hp_strip']['px'], dict) else c['hp_strip']['px'] for c in C.values()]))
print('ram', {k: rng([c['ram']['px'].get(k) for c in C.values()]) for k in C[names[0]]['ram']['px']})
print('insets', {n: c['insets']['rows'] for n, c in C.items() if c['insets'].get('rows')})
for n in names:
    o = C[n]['options']
    if o.get('applies'):
        print('options', n, o.get('n_rows'), o.get('plan_px_in_rows'), o.get('stars'))
    s = C[n]['slices']
    if s.get('applies'):
        rows = s.get('rows') or []
        print('slices', n, [(r['sector'], r['aimed'], r['luma_ratio'], r['median_L']) for r in rows])
print('cap min', rng([((c['c_cap_height'].get('smallest') or [{}])[0]).get('cap_px') for c in C.values()]), 'cap fails', sum(c['c_cap_height'].get('n_fail', 0) for c in C.values()))
print('palette fails', sum(len(c['d_palette']['failures']) for c in C.values()), 'pairs', rng([c['d_palette'].get('n_pairs') for c in C.values()]))
tot = lambda v: sum(v.values()) if isinstance(v, dict) else v
print('collide', rng([tot(c['collide'].get('hover_vs_marks_px')) for c in C.values()]), rng([tot(c['collide'].get('occlusion_px')) for c in C.values()]),
      rng([tot(c['collide'].get('mark_pairs_px')) for c in C.values()]))
print('dashes', rng([c['dashes']['dash_calls'] for c in C.values()]), rng([c['dashes']['dot_calls'] for c in C.values()]), rng([c['dashes']['pixel_dot_runs'] for c in C.values()]))
print('nowords text', rng([len(c['nowords'].get('alnum_text_calls') or []) for n, c in C.items() if n.endswith('nowords')]))
for n in names:
    e = C[n]['e_hand']
    print('hand %-24s send/undo %s/%s btn2 %s minr %s lift_r %s r459 %s arcs %s low %s rest hex %s lift-sib %s faces %s extra %s' % (
        n, e.get('hand_x_send_px'), e.get('hand_x_undo_px'), e.get('hand_px_within_2px_of_buttons'), e.get('hand_min_r'), e.get('lift_min_r'), e.get('lift_px_inside_r459'),
        e.get('lift_px_within_3px_of_landing_marks'), e.get('hand_lowest_y'), e.get('rest_cost_hex_covered_px'),
        [(s['sibling'], s['cost_px'], s['rules_px']) for s in e.get('lifted_vs_sibling', [])], [(f['card'], f['face_covered_px'], f['board_fan_px']) for f in e.get('rest_faces', [])],
        e.get('rest_face_extra_px')))
for n in names:
    a = C[n]['a_cell_contrast']
    g = [x for x in a.get('rows', []) if x['gated']]
    print('a %-24s gated %d min %s fails %s board_img %s' % (n, len(g), min([x['ratio'] for x in g]) if g else None,
          [(x['ring'], x['sector'], x['kind'], x['state'], x['ratio'], x['occ_L'], x['empty_L'], x['px']) for x in g if not x['pass_']],
          {k: v for k, v in (a.get('board_image_same_state') or {}).items() if k != 'note'}))
print('hud bottom', sorted({(c['hud_room_info'].get('hover_hud_bottom')) for c in C.values()}))
print('asserts', sorted({c['asserts']['board'] for c in C.values()}), [c['asserts']['insets'] for c in C.values() if c['asserts']['insets']])
print('squint', rng([(c.get('squint_info') or {}).get('mean') for c in C.values()]))
