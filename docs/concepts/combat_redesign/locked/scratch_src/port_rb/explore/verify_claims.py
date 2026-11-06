"""verify_claims: check prose claims in the rebuilt spec / bible draft against the data (exploration)."""
import json, re

L = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
f = json.load(open(L + 'port/fx_timings.json', encoding='utf-8'))
board = [e for e in f['effects'] if e['layer'] == 'board']
print('board effects', len(board), 'px_on_hud_max values', sorted({e.get('px_on_hud_max') for e in board}, key=str))
print('max total', max(e['total_ms'] for e in f['effects']), 'reduce max', max((e['reduce_total_ms'] or 0) for e in f['effects']))
print('hud', [e['id'] for e in f['effects'] if e['layer'] == 'hud'])
kill = [e for e in f['effects'] if e['id'] == 'fx_kill'][0]
print('kill phases', [(p['name'], p['ease_raw']) for p in kill['phases']][:2])
c = json.load(open(L + 'final/checks.json', encoding='utf-8'))
print('squint tower', {k: round(100 * v['final'], 1) for k, v in c['squint_tower_zone'].items() if '_' not in k.split('p1_')[-1] or k in ('p1_nowords',)})
print('p1 squint plate', c['squint']['p1_decide']['plate']['final'])
print('corp readback', c['corp']['kind_dE2000_plate_readback'])
for fn in ('GODOT_PORT_SPEC.md', 'MAILBOX_DRAFT.md', 'ART_BIBLE_COMBAT_DRAFT.md'):
    t = open(L + fn, encoding='utf-8').read()
    print(fn, 'lines', t.count('\n'), 'None-cells', len(re.findall(r'\| None \||`None`', t)), 'nan', t.count('nan '),
          'DRAFT', ('DRAFT, not posted' in t, 'DRAFT, waiting for designer sign-off' in t))
