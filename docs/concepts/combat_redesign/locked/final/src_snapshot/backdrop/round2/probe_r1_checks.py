"""probe_r1_checks.py -- print the structure of the round-1 (gate-1) backdrop checks.json snapshot and its room / as-seen numbers per plate."""
import sys, json
sys.dont_write_bytecode = True
ck = json.load(open('D:/rc_scratch/combat_redesign/locked/round2/backdrop/work/r1/checks.json', encoding='utf-8'))
print('keys', list(ck))
for n, p in ck['plates'].items():
    a = p['after']
    seen = [r for r in a.get('value_order', []) if r['family'].startswith('room')]
    print(n, 'after keys', list(a), '| L keys', list(a['L']))
    print('   room', a['L']['room'], 'seen', [(r['family'], r['mean'], r['p95']) for r in seen], 'ref', a.get('room_ref'))
print('real', ck.get('real_render_vs_composite'))
