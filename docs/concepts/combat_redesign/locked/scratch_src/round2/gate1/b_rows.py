"""gate1: print every check-b row (family table, mark rows, structure rows, token discs) with p95/p99 for a plate from out/rb_checks_published.json"""
import sys, json
R = json.load(open('out/rb_checks_published.json'))
nm = sys.argv[1]
b = R[nm]['b_value_order']


def walk(o, path=''):
    if isinstance(o, dict):
        if 'p99' in o or 'p95' in o:
            nm_ = ' '.join(str(o.get(k)) for k in ('family', 'cls', 'class', 'name', 'mark', 'label') if o.get(k)) or path
            print('%-60s p95 %-6s p99 %-6s med %-6s px %s pass %s' % (str(nm_)[:60], o.get('p95'), o.get('p99'), o.get('median'), o.get('px'), o.get('pass_')))
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                walk(v, path + '.' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + '[%d]' % i)


walk(b)
