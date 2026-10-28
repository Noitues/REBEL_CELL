import json, glob
for f in sorted(glob.glob('D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/tile_distances_*.json')):
    e = json.load(open(f))
    print(f.split('/')[-1], [(t['site'], t['dist_px']) for t in e], 'OK' if all(34 <= t['dist_px'] <= 64 for t in e) else 'FAIL')
