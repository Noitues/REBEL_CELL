"""Copy the deliverables into the repo folder and write metrics.json (both skins + the old option A numbers for comparison)."""
import os, json, shutil
WK = 'D:/rc_scratch/combat_redesign/locked/transitions_work/'
DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/transitions/'
os.makedirs(DST + 'scripts', exist_ok=True)
cp = [('out/neutral/t5_A.gif', 't5_A.gif'), ('out/neutral/t6_A.gif', 't6_A.gif'),
      ('out/neutral/strip_t5.jpg', 'strip_t5.jpg'), ('out/neutral/strip_t6.jpg', 'strip_t6.jpg'),
      ('out/solace/strip_t5.jpg', 'strip_t5_solace.jpg'), ('out/solace/strip_t6.jpg', 'strip_t6_solace.jpg'),
      ('sb/t02_raid_to_select_jackin.jpg', 't02_raid_to_select_jackin.jpg'), ('sb/t03_jackin_zoom.jpg', 't03_jackin_zoom.jpg'),
      ('sb/t05_room_to_combat.jpg', 't05_room_to_combat.jpg'), ('sb/t05_room_to_combat_solace.jpg', 't05_room_to_combat_solace.jpg'),
      ('sb/t06_combat_to_netrun_or_fail.jpg', 't06_combat_to_netrun_or_fail.jpg'), ('sb/sheet.jpg', 'sheet.jpg')]
for a, b in cp:
    shutil.copy2(WK + a, DST + b)
for s in ['staged.py', 'fx2lib.py', 'fx_a2.py', 'render2.py', 'build_sb.py', 'quick2.py', 'publish.py']:
    shutil.copy2(WK + 'src/' + s, DST + 'scripts/' + s)
old = json.load(open('D:/rc_art/art-pass/docs/concepts/transitions/bits_fx/metrics.json'))['A']
m = dict(method=('Same as transitions/bits_fx/metrics.json: mean frame luma (Rec.709 weights) per GIF frame at 12.5 fps (80 ms), the largest '
                 'frame-to-frame change, and every change over 10 % of the brighter frame counted as a swing; a flash is an opposing pair '
                 'of swings (flash_pairs). Added here: the same at 25 fps (denser sampling of the same motion) and a local check on 60 px '
                 'tiles at 25 fps (worst tile, opposing 10 % swings paired). Limit: no more than 3 flashes in any 1 s.'),
         neutral=json.load(open(WK + 'out/neutral/metrics_neutral.json')),
         solace=json.load(open(WK + 'out/solace/metrics_solace.json')),
         old_option_A_E10=old)
for k in ('neutral', 'solace'):
    v = m[k]
    v['verdict'] = dict(
        whole_frame_flashes_t5=v['t5']['flash_pairs'], whole_frame_flashes_t6=v['t6']['flash_pairs'],
        worst_local_tile_flashes_t5_in_1_2s=v['t5_local_25fps']['worst_tile_flash_pairs'],
        worst_local_tile_flashes_t6_in_0_8s=v['t6_local_25fps']['worst_tile_flash_pairs'],
        pass_3_per_s=bool(v['t5']['flash_pairs'] <= 3 and v['t6']['flash_pairs'] <= 3 and v['t5_local_25fps']['worst_tile_flash_pairs'] <= 3 and v['t6_local_25fps']['worst_tile_flash_pairs'] <= 3),
        gifs_under_6mb=bool(v['t5_gif_mb'] < 6 and v['t6_gif_mb'] < 6))
json.dump(m, open(DST + 'metrics.json', 'w'), indent=1)
print({k: m[k]['verdict'] for k in ('neutral', 'solace')})
print(sorted(os.listdir(DST)))
