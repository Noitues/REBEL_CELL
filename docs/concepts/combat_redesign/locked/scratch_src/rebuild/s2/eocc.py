"""eocc.py <checks.json> : print E cells occupied p95 and room stats per plate from a board checks.json"""
import sys, json
sys.dont_write_bytecode = True
J = json.load(open(sys.argv[1]))
plates = J.get('plates', J)
for nm, r in plates.items():
    if not isinstance(r, dict):
        continue
    b = r.get('b_value_order') or r.get('checks', {}).get('b_value_order')
    if not b:
        continue
    tab = {row['family']: row for row in b['sorted']}
    eo = tab.get('E cells occupied (glass)', {})
    rm = tab.get('room', {})
    print('%-24s Eocc p95 %5s  room mean %5s p95 %5s' % (nm, eo.get('p95'), rm.get('mean'), rm.get('p95')))
