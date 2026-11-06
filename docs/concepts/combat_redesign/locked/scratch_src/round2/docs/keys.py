"""keys.py: print the key tree of a JSON file to a given depth (inspection only, writes nothing).
usage: python keys.py <json> [depth] [path.to.sub]"""
import sys, json


def walk(o, d, maxd, pre=''):
    if d > maxd:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            t = type(v).__name__
            extra = ''
            if isinstance(v, (int, float, str, bool)) or v is None:
                s = json.dumps(v)
                extra = ' = ' + (s if len(s) < 120 else s[:117] + '...')
            elif isinstance(v, list):
                extra = ' [%d]' % len(v)
                if v and not isinstance(v[0], (dict, list)):
                    s = json.dumps(v)
                    extra += ' ' + (s if len(s) < 120 else s[:117] + '...')
            print('  ' * d + str(k) + ' : ' + t + extra)
            if isinstance(v, dict):
                walk(v, d + 1, maxd)
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                print('  ' * (d + 1) + '[0]:')
                walk(v[0], d + 2, maxd)


o = json.load(open(sys.argv[1], encoding='utf-8'))
depth = int(sys.argv[2]) if len(sys.argv) > 2 else 1
if len(sys.argv) > 3:
    for p in sys.argv[3].split('.'):
        o = o[int(p)] if isinstance(o, list) else o[p]
walk(o, 0, depth)
