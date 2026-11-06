"""peek.py: print selected sub-trees of a JSON file as compact JSON (inspection only, writes nothing).
usage: python peek.py <json> <path> [<path> ...]   path = dot-separated keys; list index as a number; '*' = every key (first level)"""
import sys, json

o = json.load(open(sys.argv[1], encoding='utf-8'))


def get(o, path):
    for p in path.split('.'):
        if p == '':
            continue
        o = o[int(p)] if isinstance(o, list) else o[p]
    return o


for path in sys.argv[2:]:
    lim = 3000
    if '@' in path:
        path, lim = path.split('@')
        lim = int(lim)
    try:
        v = get(o, path)
    except Exception as e:
        print(path, '-> ERR', repr(e))
        continue
    s = json.dumps(v, ensure_ascii=False)
    print('##', path, '->', s[:lim] + (' ...(%d chars)' % len(s) if len(s) > lim else ''))
