"""probe_pub_json.py -- print the published backdrop checks.json summary keys (pass, all_pass, ui_scrim_rows, c14, provenance diff) and
grade.json's round2 block."""
import sys, json
sys.dont_write_bytecode = True
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
ck = json.load(open(D + 'checks.json', encoding='utf-8'))
print('all_pass', ck['all_pass'])
print('pass', json.dumps(ck['pass']))
print('ui_scrim_rows', ck['ui_scrim_rows'])
print('c14', {k: v for k, v in ck['c14_determinism'].items() if k != 'steps'})
print('provenance', {k: v for k, v in ck['provenance']['transfers'].items()})
for n, p in ck['plates'].items():
    print(n, 'r1', p['before_round1']['room'], p['before_round1']['room_as_seen'], '| r2', p['after']['L']['room']['mean'], p['after']['L']['room_as_seen']['mean'],
          p.get('real_render_vs_composite', ''))
g = json.load(open(D + 'grade.json', encoding='utf-8'))
print('grade version', g['version'], list(g))
print(json.dumps(g['round2'], indent=1))
