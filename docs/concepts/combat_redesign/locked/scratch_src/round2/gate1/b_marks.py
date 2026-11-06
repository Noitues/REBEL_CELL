"""gate1: per plate, check-b mark rows and structure rows by name (p95 / p99 / median), with HOT and tower p95."""
import sys, json
R = json.load(open('out/rb_checks_published.json'))
names = sys.argv[1:] or list(R)
for nm in names:
    b = R[nm]['b_value_order']
    tab = {x['family']: x for x in b['sorted']}
    print('==', nm, 'HOT', tab.get('T HOT marks', {}).get('p95'), 'tower', tab.get('P tower', {}).get('p95'))
    for k, v in b['marks'].items():
        print('   %-36s p95 %-6s p99 %-6s med %-6s px %s' % (k, v.get('p95'), v.get('p99'), v.get('median'), v.get('px')))
    for k, v in b['round2']['structure_rows'].items():
        print('   S %-34s p95 %-6s p99 %-6s med %-6s px %s' % (k, v.get('p95'), v.get('p99'), v.get('median'), v.get('px')))
