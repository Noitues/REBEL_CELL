import json
d = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
for p, v in d['squint'].items():
    print('%-22s' % p, ' | '.join('%s loud %.1f%% mean %.3f' % (k[:12], 100 * vv['final']['loud'], vv['final']['mean']) for k, vv in v.items()))
