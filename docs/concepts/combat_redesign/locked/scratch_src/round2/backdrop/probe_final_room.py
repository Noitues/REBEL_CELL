"""probe_final_room.py -- read locked/final/checks.json (round 2 board) and print the room gate row and the room-as-seen info row per plate."""
import sys, json
sys.dont_write_bytecode = True
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'
ck = json.load(open(FIN, encoding='utf-8'))
print('top keys', list(ck.keys())[:40])


def walk(o, path, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ('room', 'room as seen (scrim kept, info)') and isinstance(v, dict) and 'mean' in v:
                out.append((path + '/' + k, v))
            elif isinstance(v, (dict, list)):
                walk(v, path + '/' + str(k), out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, dict) and v.get('family') in ('room', 'room as seen (scrim kept, info)'):
                out.append((path + '[%d]' % i, v))
            elif isinstance(v, (dict, list)):
                walk(v, path + '[%d]' % i, out)


out = []
walk(ck, '', out)
for p, v in out:
    print(p, {k: v[k] for k in ('family', 'mean', 'p95', 'median', 'px') if k in v})
