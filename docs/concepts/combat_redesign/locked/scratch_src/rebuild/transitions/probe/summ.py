"""summ.py: print the numbers the NOTES quote, from the published metrics.json."""
import json
m = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/transitions/metrics.json'))
def keys(d, p='', depth=0):
    if isinstance(d, dict) and depth < 3:
        for k, v in d.items():
            if isinstance(v, (dict,)):
                print('  ' * depth + p + k + ':')
                keys(v, '', depth + 1)
            elif isinstance(v, list):
                print('  ' * depth + p + k + ': list[%d] %s' % (len(v), str(v[:3])[:80]))
            else:
                print('  ' * depth + p + k + ': ' + str(v)[:100])
print(list(m.keys()))
keys(m['neutral'])
print('previous_o30', m['previous_o30'])
print('solace t5 gif', m['solace']['t5'].get('gif_mb'), 't6', m['solace']['t6'].get('gif_mb'))
for s in ('neutral', 'solace'):
    for c in ('t5', 't6'):
        w = m[s][c]['whole_25fps']
        print(s, c, {k: (v if not isinstance(v, list) else (round(min(v), 1), round(max(v), 1))) for k, v in w.items() if 'pairs' in k or 'Lstar' in k or 'step' in k or 'max' in k})
