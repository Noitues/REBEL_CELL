"""summary.py: the numbers for NOTES.md, read from the published metrics.json (and the staging check)."""
import json
m = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/transitions/metrics.json'))
for c in ('neutral', 'solace'):
    v = m[c]
    for fn in ('t5', 't6'):
        w = v[fn]['whole_25fps']; w12 = v[fn]['whole_12p5fps']; t = v[fn]['tiles_25fps']
        print(c, fn, 'L* %.1f-%.1f' % (w['min_frame_Lstar'], w['max_frame_Lstar']), 'step25 %.2f step12 %.2f' % (w['max_step_Lstar'], w12['max_step_Lstar']),
              'whole', w['rel10_flash_pairs'], w['wcag_abs_flash_pairs'], 'tile', t['rel10']['worst_tile_flash_pairs_any_1s'], t['wcag_abs']['worst_tile_flash_pairs_any_1s'],
              t['rel10']['worst_tile_xy_1080'], 'gif', v[fn]['gif_mb'], v[fn]['gif_frames'], 'face', v[fn]['wheel_face'],
              {k: v[fn][k] for k in v[fn] if 'maxdiff' in k})
    print(c, 'density', v['params']['density_c13'])
    print(c, 'verdict', v['verdict'])
print('staged', m['staged_vs_published_plate'])
pc = m['published_check']
for c in ('neutral', 'solace'):
    for fn in ('t5', 't6'):
        p = pc[c][fn]
        print('pub', c, fn, p['rel10'], p['wcag_abs'], p['whole_frame'], p.get('k1'), p['mb'], p['stored_frames'], p['timeline_frames'],
              'L* %.1f-%.1f' % (min(p['frame_mean_Lstar']), max(p['frame_mean_Lstar'])))
