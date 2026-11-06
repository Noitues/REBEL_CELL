"""fx_check: print the merged port-2 fx table compactly (exploration)."""
import json, sys

d = json.load(open(sys.argv[1], encoding='utf-8'))
for r in d['effects']:
    print(r['id'], r['family'], r['kind'], r['total_ms'], 'o30', r['total_ms_o30'], 'red', r['reduce_total_ms'], r['layer'],
          'fl', r['max_flashes_per_s'], r['reduce_max_flashes_per_s'], 'loud', r['loud_transient'].get('neutral'),
          [(p['name'][:14], p['ease'], p['ease_raw']) for p in r['phases']][:3])
print(d['resolve_beat']['flash'])
print(json.dumps(d['loudness_order']['mpst'], indent=0)[:600])
