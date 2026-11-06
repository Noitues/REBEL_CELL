"""gate1: print the key tree of a json file (depth-limited) and optionally a dotted path.  usage: peek_json.py <file> [path.to.key] [depth]"""
import sys, json
d = json.load(open(sys.argv[1]))
path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else ''
depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
for k in [p for p in path.split('.') if p]:
    d = d[int(k)] if isinstance(d, list) else d[k]


def show(o, ind, dep):
    if dep < 0:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            s = type(v).__name__
            if isinstance(v, (int, float, str, bool)) or v is None:
                print(' ' * ind + '%s: %s' % (k, str(v)[:160]))
            else:
                print(' ' * ind + '%s: <%s %d>' % (k, s, len(v)))
                show(v, ind + 2, dep - 1)
    elif isinstance(o, list):
        for i, v in enumerate(o[:6]):
            if isinstance(v, (dict, list)):
                print(' ' * ind + '[%d] <%s %d>' % (i, type(v).__name__, len(v)))
                show(v, ind + 2, dep - 1)
            else:
                print(' ' * ind + '[%d] %s' % (i, str(v)[:160]))
        if len(o) > 6:
            print(' ' * ind + '... (%d items)' % len(o))


show(d, 0, depth)
