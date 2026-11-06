"""json_check.py: sanity of the published timings_MPST.json: every effect <= 600 ms with phases inside, every skin's flash passes,
loudness present, the beat block present and passing"""
import json
from mp_lib import OUTD
d = json.load(open(OUTD + 'timings_MPST.json'))
bad = []
for fid, e in d['effects'].items():
    if e['total_ms'] > 600 or max(p['end_ms'] for p in e['phases']) > e['total_ms'] or e['reduce_total_ms'] > 600:
        bad.append((fid, 'length'))
    for sk, f in e['flash_check'].items():
        if not (f['full']['passed'] and f['reduce']['passed'] and f['full']['max_flashes_per_s'] <= 3 and f['reduce']['max_flashes_per_s'] <= 3):
            bad.append((fid, sk, 'flash'))
        if sk not in e['loudness']:
            bad.append((fid, sk, 'loud'))
    if 'layer_check_neutral' not in e:
        bad.append((fid, 'layer'))
b = d['resolve_beat_e10']
print('effects', len(d['effects']), 'order pass', d['loudness_order']['pass'], d['loudness_order_solace']['pass'], d['loudness_order_meridian']['pass'])
print('beat total', b['total_ms'], 'skip', b['skip_ms'], 'full', b['flash_full']['max_flashes_per_s_beat'], b['flash_full']['max_flashes_per_s_skips'], b['flash_full']['passes'],
      'reduce', b['flash_reduce']['max_flashes_per_s_beat'], b['flash_reduce']['max_flashes_per_s_skips'], b['flash_reduce']['passes'], 'gif', b['gif'])
print('bad', bad)
