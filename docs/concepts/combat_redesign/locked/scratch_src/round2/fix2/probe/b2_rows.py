"""print the b2_bright structure / hover rows of a hover checks json"""
import json, sys
for f in sys.argv[1:]:
    j = json.load(open(f))
    b = j['b2_bright']
    print(f.split('/')[-1], 'hot', b.get('hot_p95_lit'), 'tower', b.get('tower_p95_lit'), 'unc', b.get('unclassed_px'))
    for k, v in list(b.get('structure_rows', {}).items()) + list(b.get('hover_rows', {}).items()):
        print('   %-45s p95 %s p99 %s px %s' % (k, v.get('p95'), v.get('p99'), v.get('px')))
    print('   failures', b.get('failures'), 'open', b.get('open_call_focus_vs_hot'))
    print('   keys', [k for k in b.keys()])
