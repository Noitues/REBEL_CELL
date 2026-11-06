"""print the d (C2) drawn-vs-token rows per plate from a board checks.json"""
import sys, json
d = json.load(open(sys.argv[1]))
plates = d.get('plates', d)


def walk(o, path=''):
    if isinstance(o, dict):
        if 'drawn_vs_token' in o:
            yield path, o
        for k, v in o.items():
            yield from walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + '[%d]' % i)


for p, o in walk(d):
    print(p)
    for r in o['drawn_vs_token']:
        print('    %-18s %s dE %s px %s' % (r['cls'], r['drawn_hex'], r['dE'], r.get('px')))
