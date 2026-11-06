"""jkeys.py <json> : top-level keys and the keys of one effect entry (to see hand edits to preserve)"""
import sys, json
j = json.load(open(sys.argv[1]))
print(list(j.keys()))
for k, v in j.items():
    if not isinstance(v, dict) or k == 'effects':
        print(k, ':', str(v)[:300])
    else:
        print(k, ':', json.dumps(v)[:600])
e = j['effects']
for fid, d in e.items():
    extra = [k for k in d if k not in ('family', 'title', 'variant_of', 'tier', 'scope', 'skins', 'total_ms', 'in_ms', 'hold_ms', 'out_ms', 'easing_summary',
                                       'easing', 'phases', 'keyframes', 'reduce_motion', 'source', 'board_crop', 'base', 'flash')]
    if extra:
        print(fid, 'extra keys', {k: d[k] for k in extra})
