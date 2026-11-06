p = 'hv_checks.py'
s = open(p, encoding='utf-8').read()
old = '''def gate_cells(geo, lit):
    """hover: a live / dying cell is gated only when 60 % of its glass is lit; the rest are 'dimmed' (reported)"""
    geo = json.loads(json.dumps(geo))
    lm = lit >= 128
    for c in geo['cells']:
        if c['state'] in ('live', 'dying') and c['poly']:'''
new = '''def gate_cells(geo, lit, veiled=()):
    """hover: a live / dying cell is gated only when 60 % of its glass is lit; the rest are 'dimmed' (reported).  The origin cell of a unit the
    plan moves (Shove, Pull) is veiled by design (the ghost carries the unit): 'veiled', reported"""
    geo = json.loads(json.dumps(geo))
    lm = lit >= 128
    for c in geo['cells']:
        if c['uid'] in veiled and c['state'] in ('live', 'dying'):
            c['state'] = 'veiled'
            continue
        if c['state'] in ('live', 'dying') and c['poly']:'''
assert old in s
s = s.replace(old, new, 1)
old2 = "    geo = gate_cells(geo, lit)\n"
assert old2 in s
s = s.replace(old2, "    mv = (rep.get('marks') or {}).get('moved')\n    geo = gate_cells(geo, lit, {mv[0]} if mv else ())\n", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
