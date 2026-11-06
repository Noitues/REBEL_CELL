"""peek_final_a.py : the board's published check a rows for ring 0 sector 0 on each final plate (art-pass final/checks.json, read only)"""
import json
j = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
def walk(o, path=''):
    if isinstance(o, dict):
        if 'rows' in o and isinstance(o['rows'], list) and o['rows'] and isinstance(o['rows'][0], dict) and 'ring' in o['rows'][0] and 'ratio' in o['rows'][0]:
            for r in o['rows']:
                if r['ring'] == 0 and r['sector'] in (0, 3):
                    print(path, r)
        for k, v in o.items():
            walk(v, path + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + '[%d]' % i)
walk(j)
