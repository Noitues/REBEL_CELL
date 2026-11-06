import json, sys
d = json.load(open(sys.argv[1]))
def walk(o, pre, depth, maxd):
    if depth > maxd: return
    if isinstance(o, dict):
        for k, v in o.items():
            t = type(v).__name__
            ln = len(v) if hasattr(v, '__len__') and not isinstance(v, str) else ''
            print('  ' * depth + f'{k}: {t} {ln}' + (f' = {v!r}'[:120] if not isinstance(v, (dict, list)) else ''))
            walk(v, pre + '.' + k, depth + 1, maxd)
    elif isinstance(o, list) and o and depth < maxd:
        print('  ' * depth + f'[0] of {len(o)}: {type(o[0]).__name__} ' + (repr(o[0])[:150] if not isinstance(o[0], (dict,list)) else ''))
        walk(o[0], pre + '[0]', depth + 1, maxd)
walk(d, '', 0, int(sys.argv[2]) if len(sys.argv) > 2 else 2)
