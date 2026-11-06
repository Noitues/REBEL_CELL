"""cmp_bills.py <before.json> <after.json> : the plan records that differ (names present in both)"""
import sys, json
a, b = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
for nm in sorted(set(a) & set(b)):
    d = [k for k in a[nm] if a[nm][k] != b[nm].get(k)]
    print(nm, 'SAME' if not d else 'DIFF %s' % d)
    for k in d:
        print('   before', k, json.dumps(a[nm][k], default=str)[:400])
        print('   after ', k, json.dumps(b[nm].get(k), default=str)[:400])
