"""publish3 (2026-11-04 rebuild): copy the transitions deliverables into the repo folder, replace scripts/ with this generator's scripts,
and write metrics.json (both skins, the method, the previous O-30 verdicts and the old option A numbers for comparison)."""
import os, json, shutil, glob
WK = 'D:/rc_scratch/combat_redesign/locked/rebuild/transitions/'
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
           'lstar.py', 'measure_rooms.py', 'cmp_pub.py', 'diag_t6.py', 'crop.py']
os.makedirs(DST + 'scripts', exist_ok=True)
for f in glob.glob(DST + 'scripts/*.py'):
    if os.path.basename(f) not in SCRIPTS:
        os.remove(f)                      # the O-30 scripts (fx2lib, fx_a2, render2, build_sb, ...) are in git history; one generator here
for s in SCRIPTS:
    shutil.copy2(WK + 'src/' + s, DST + 'scripts/' + s)
old = json.load(open('D:/rc_art/art-pass/docs/concepts/transitions/bits_fx/metrics.json'))['A']
m = dict(
    version='2026-11-04 rebuild (review 1.7, 3.12), on the board published in locked/final/',
    method=('Every frame is rendered at 1920x1080 and measured at 25 fps; the GIFs are every other frame (12.5 fps, 80 ms) at 960 px. '
            'Frame values are CIE L* of the frame mean relative luminance (sRGB to L*, as the reviewer\'s measure.py). '
            'Flash, whole frame: (a) rel10 = the O-25 method (gamma luma, a swing is a change over 10 % of the brighter frame, a flash is an '
            'opposing pair of swings); (b) wcag_abs = WCAG 2.x general flash (relative luminance change of 0.10 or more with the darker '
            'frame under 0.80, opposing pairs). Flash, local: the same two tests on 120 px tiles (60 px at 960), worst tile in the clip and '
            'in any 1 s window. Limit: no more than 3 flashes in any 1 s. wheel_face: every bit draw is logged; inside the rim (r < 492) a '
            'bit may only sit on its own target angle (radial in or out), ART_BIBLE 1.2 "bits go round the rim".'),
    neutral=json.load(open(WK + 'out/neutral/metrics_neutral.json')),
    solace=json.load(open(WK + 'out/solace/metrics_solace.json')),
    previous_o30=dict((k, prev[k]['verdict']) for k in ('neutral', 'solace') if k in prev and 'verdict' in prev[k]),
    old_option_A_E10=old)
for k in ('neutral', 'solace'):
    v = m[k]
    lim = lambda d: d['tiles_25fps']['rel10']['worst_tile_flash_pairs_any_1s']
    v['verdict'] = dict(
        whole_frame_flashes_t5=dict(rel10=v['t5']['whole_25fps']['rel10_flash_pairs'], wcag_abs=v['t5']['whole_25fps']['wcag_abs_flash_pairs']),
        whole_frame_flashes_t6=dict(rel10=v['t6']['whole_25fps']['rel10_flash_pairs'], wcag_abs=v['t6']['whole_25fps']['wcag_abs_flash_pairs']),
        worst_tile_flashes_any_1s_t5=dict(rel10=lim(v['t5']), wcag_abs=v['t5']['tiles_25fps']['wcag_abs']['worst_tile_flash_pairs_any_1s']),
        worst_tile_flashes_any_1s_t6=dict(rel10=lim(v['t6']), wcag_abs=v['t6']['tiles_25fps']['wcag_abs']['worst_tile_flash_pairs_any_1s']),
        pass_3_per_s=bool(max(v['t5']['whole_25fps']['rel10_flash_pairs'], v['t6']['whole_25fps']['rel10_flash_pairs'], lim(v['t5']), lim(v['t6'])) <= 3),
        gifs_under_6mb=bool(v['t5']['gif_mb'] < 6 and v['t6']['gif_mb'] < 6),
        no_bit_across_wheel_face=bool(v['t5']['wheel_face']['draws_off_their_radial'] == 0 and v['t6']['wheel_face']['draws_off_their_radial'] == 0))
json.dump(m, open(DST + 'metrics.json', 'w'), indent=1)
print({k: m[k]['verdict'] for k in ('neutral', 'solace')})
print(sorted(os.listdir(DST)), sorted(os.listdir(DST + 'scripts')))
