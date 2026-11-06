import json, sys
for n in sys.argv[1:]:
    d = json.load(open('D:/rc_scratch/combat_redesign/locked/hover/chk/%s.json' % n))
    c = d['collisions']
    print(n, 'hand', c['hand_vs_board'])
    print('  lift', d.get('lift_dx'), d.get('lift_cy'), d.get('lift_scale'))
    print('  fits', d.get('hud_ring_fits'))
    print('  hov', {k: v for k, v in c['hover_vs_marks_px'].items() if v}, c.get('hover_overlap_bbox'))
    print('  mask', {k: v for k, v in c['mask_px'].items() if k.startswith('hud')})
