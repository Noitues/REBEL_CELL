"""publish3 (2026-11-04 round 2; first written for the rebuild): copy the transitions deliverables into the repo folder, replace scripts/
with this generator's scripts, and write metrics.json (both skins, the method, the C13 density sweep and pull-out attempts as measured by
fdiag.py, the round-1 verdicts, the O-30 verdicts and the old option A numbers for comparison).  verify_pub.py then measures the published
files and adds metrics.json 'published_check'."""
import os, json, shutil, glob
WK = 'D:/rc_scratch/combat_redesign/locked/round2/transitions/'
DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/transitions/'
prev = json.load(open(DST + 'metrics.json'))
cp = [('out/neutral/t5_A.gif', 't5_A.gif'), ('out/neutral/t6_A.gif', 't6_A.gif'),
      ('out/neutral/strip_t5.jpg', 'strip_t5.jpg'), ('out/neutral/strip_t6.jpg', 'strip_t6.jpg'),
      ('out/solace/strip_t5.jpg', 'strip_t5_solace.jpg'), ('out/solace/strip_t6.jpg', 'strip_t6_solace.jpg'),
      ('sb/t02_raid_to_select_jackin.jpg', 't02_raid_to_select_jackin.jpg'), ('sb/t03_jackin_zoom.jpg', 't03_jackin_zoom.jpg'),
      ('sb/t05_room_to_combat.jpg', 't05_room_to_combat.jpg'), ('sb/t05_room_to_combat_solace.jpg', 't05_room_to_combat_solace.jpg'),
      ('sb/t06_combat_to_netrun_or_fail.jpg', 't06_combat_to_netrun_or_fail.jpg'), ('sb/sheet.jpg', 'sheet.jpg')]
for a, b in cp:
    shutil.copy2(WK + a, DST + b)
SCRIPTS = ['staged.py', 'fx3lib.py', 'fx3.py', 'render3.py', 'sbkit.py', 'build_sb3.py', 'publish3.py', 'quick3.py', 'bitstats.py',
           'lstar.py', 'measure_rooms.py', 'cmp_pub.py', 'diag_t6.py', 'crop.py', 'fdiag.py', 'fshow.py', 'verify_pub.py', 'diffmap.py']
os.makedirs(DST + 'scripts', exist_ok=True)
for f in glob.glob(DST + 'scripts/*.py'):
    if os.path.basename(f) not in SCRIPTS:
        os.remove(f)
for s in SCRIPTS:
    shutil.copy2(WK + 'src/' + s, DST + 'scripts/' + s)
old = json.load(open('D:/rc_art/art-pass/docs/concepts/transitions/bits_fx/metrics.json'))['A']

# ---- C13: what fdiag.py measured for each setting (25 fps, 120 px tiles, rel10 worst tile in any 1 s; WCAG worst tile in any 1 s)
RUNS = [  # (corp, tag, what was set)
    ('neutral', 'base', 'round-1 density (every bit)'), ('solace', 'base', 'round-1 density (every bit)'),
    ('neutral', 'k0.5', 'T5 far 50 %; T6 near 100 % far 50 %'), ('solace', 'k0.5', 'T5 far 50 %; T6 near 100 % far 50 %'),
    ('neutral', 'k0.3', 'T5 far 30 %; T6 near 100 % far 30 %'), ('solace', 'k0.3', 'T5 far 30 %; T6 near 100 % far 30 %'),
    ('neutral', 't6a', 'T6 near 60 % far 30 %'), ('neutral', 't6d', 'T6 near 50 % far 25 %'),
    ('neutral', 't6b', 'T6 near 45 % far 25 % (adopted)'), ('solace', 't6b', 'T6 near 45 % far 25 % (adopted)'),
    ('neutral', 't6c', 'T6 near 35 % far 20 %'),
    ('neutral', 't6b_pr1', 'pull-out: round-1 T4 iris (lime ring) + zoom, at the adopted T6 density'),
    ('neutral', 't6b_pink', 'pull-out: ink iris edge, street HUD 40 -> 100 %, zoom blurred over 40 ms (5 samples)'),
    ('neutral', 't6b_psoft', 'pull-out: soft iris edge (24 px), the same street and zoom'),
    ('neutral', 't6b_psmear', 'pull-out: soft edge, zoom blurred over 120 ms (11 samples)'),
    ('neutral', 't6c_psmear', 'pull-out as above, T6 near 35 % far 20 %'),
    ('neutral', 't6e_psmear', 'pull-out as above, T6 near 25 % far 15 %'),
    ('neutral', 't6z_psmear', 'pull-out as above, with no ring, spinner or ticket bits at all (card bits only)'),
]
sweep = []
for corp, tag, what in RUNS:
    p = WK + 'out/fdiag_%s_%s.json' % (corp, tag)
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    row = dict(corp=corp, tag=tag, setting=what)
    for fn in ('t5', 't6'):
        if fn in d:
            row[fn] = dict(rel10_worst_any_1s=d[fn]['worst_rel10_any_1s'], wcag_worst_any_1s=d[fn]['worst_wcag_any_1s'],
                           tiles_at_3_or_more=d[fn]['tiles_at_or_over_3'], tiles_at_2=d[fn]['tiles_at_2'],
                           worst_tile_1080=[d[fn]['worst'][0]['x'], d[fn]['worst'][0]['y']])
    sweep.append(row)
c13 = dict(
    limit='the worst 120 px tile flashes at most 2 times in any 1 s (rel10 and WCAG), in T5 and T6, both skins (was 3 in round 1)',
    rule=('fx3.far_keep: a ring, spinner or ticket bit whose route goes d degrees round the rim from the lab is kept with probability '
          'p = near - (near - far) * clamp((d - 90) / 90), from its own random stream (every kept bit is the bit it was). T5: near 100 %, '
          'far 50 %. T6: near 45 %, far 25 % (in T6 the board is eaten first, so the whole wheel then sits over the dark city). Card bits '
          'are not thinned.'),
    sweep=sweep,
    pull_out_call=('Not composited. Every pull-out variant measured (lime, ink and soft iris edge, the street HUD coming up from 40 %, the '
                   'zoom motion-blurred over 40 or 120 ms, the T6 density down to no ring bits at all) puts at least one 120 px tile at 3 '
                   'flashes in the 0.8 s and adds a WCAG tile flash. So T6 holds on the room (C13 call).'))
m = dict(
    version='2026-11-04 round 2 (re-review C13; review 1.7 and 3.12 re-measured), on the round-2 board published in locked/final/',
    method=('Every frame is rendered at 1920x1080 and measured at 25 fps; the GIFs are every other frame (12.5 fps, 80 ms) at 960 px. '
            'Frame values are CIE L* of the frame mean relative luminance (sRGB to L*, as the reviewer\'s measure.py). '
            'Flash, whole frame: (a) rel10 = the O-25 method (gamma luma, a swing is a change over 10 % of the brighter frame, a flash is an '
            'opposing pair of swings); (b) wcag_abs = WCAG 2.x general flash (relative luminance change of 0.10 or more with the darker '
            'frame under 0.80, opposing pairs). Flash, local: the same two tests on 120 px tiles (60 px at 960), worst tile in the clip and '
            'in any 1 s window (25 frame steps). Limit (round 2, C13): no more than 2 flashes in any 1 s. wheel_face: every bit draw is '
            'logged; inside the rim (r < 492) a bit may only sit on its own target angle (radial in or out), ART_BIBLE 1.2 "bits go round '
            'the rim". bits (3.12): each drawn bit colour against the published plate at the bit\'s point (bitstats.py). published_check: '
            'the same tests on the decoded published GIFs at 12.5 fps (verify_pub.py).'),
    neutral=json.load(open(WK + 'out/neutral/metrics_neutral.json')),
    solace=json.load(open(WK + 'out/solace/metrics_solace.json')),
    c13=c13,
    staged_vs_published_plate={c: json.load(open(WK + 'layers/%s_p1.json' % c))['compose_vs_published'] for c in ('neutral', 'solace')},
    previous_round1=dict((k, prev[k]['verdict']) for k in ('neutral', 'solace') if k in prev and 'verdict' in prev[k]),
    previous_o30=prev.get('previous_o30'),
    old_option_A_E10=old)
for k in ('neutral', 'solace'):
    v = m[k]
    lim = lambda d: d['tiles_25fps']['rel10']['worst_tile_flash_pairs_any_1s']
    worst = max(v['t5']['whole_25fps']['rel10_flash_pairs'], v['t6']['whole_25fps']['rel10_flash_pairs'], lim(v['t5']), lim(v['t6']),
                v['t5']['tiles_25fps']['wcag_abs']['worst_tile_flash_pairs_any_1s'], v['t6']['tiles_25fps']['wcag_abs']['worst_tile_flash_pairs_any_1s'])
    v['verdict'] = dict(
        whole_frame_flashes_t5=dict(rel10=v['t5']['whole_25fps']['rel10_flash_pairs'], wcag_abs=v['t5']['whole_25fps']['wcag_abs_flash_pairs']),
        whole_frame_flashes_t6=dict(rel10=v['t6']['whole_25fps']['rel10_flash_pairs'], wcag_abs=v['t6']['whole_25fps']['wcag_abs_flash_pairs']),
        worst_tile_flashes_any_1s_t5=dict(rel10=lim(v['t5']), wcag_abs=v['t5']['tiles_25fps']['wcag_abs']['worst_tile_flash_pairs_any_1s']),
        worst_tile_flashes_any_1s_t6=dict(rel10=lim(v['t6']), wcag_abs=v['t6']['tiles_25fps']['wcag_abs']['worst_tile_flash_pairs_any_1s']),
        pass_2_per_s=bool(worst <= 2),
        gifs_under_6mb=bool(v['t5']['gif_mb'] < 6 and v['t6']['gif_mb'] < 6),
        no_bit_across_wheel_face=bool(v['t5']['wheel_face']['draws_off_their_radial'] == 0 and v['t6']['wheel_face']['draws_off_their_radial'] == 0),
        t6_pull_out_composited=bool(v['t6'].get('pull_out_composited')))
json.dump(m, open(DST + 'metrics.json', 'w'), indent=1)
print({k: m[k]['verdict'] for k in ('neutral', 'solace')})
for r in sweep:
    print(r['corp'], r['tag'], {fn: (r[fn]['rel10_worst_any_1s'], r[fn]['wcag_worst_any_1s'], r[fn]['tiles_at_3_or_more']) for fn in ('t5', 't6') if fn in r})
print(sorted(os.listdir(DST)), sorted(os.listdir(DST + 'scripts')))
