"""peek_json: print the key structure of a JSON file to a given depth (lists show length and first item).
usage: python peek_json.py <file> [depth] [path.to.sub]"""
import json, sys


def show(o, d, maxd, ind=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)) and d < maxd:
                tag = 'dict(%d)' % len(v) if isinstance(v, dict) else 'list(%d)' % len(v)
                print('%s%s: %s' % (ind, k, tag))
                show(v, d + 1, maxd, ind + '  ')
            else:
                s = json.dumps(v, ensure_ascii=True)
                print('%s%s: %s' % (ind, k, s[:160]))
    elif isinstance(o, list):
        if o:
            print('%s[0] of %d:' % (ind, len(o)))
            show(o[0], d + 1, maxd, ind + '  ')


def main():
    o = json.load(open(sys.argv[1], encoding='utf-8'))
    maxd = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    if len(sys.argv) > 3:
        for p in sys.argv[3].split('.'):
            o = o[int(p)] if isinstance(o, list) else o[p]
    show(o, 0, maxd)


if __name__ == '__main__':
    main()
