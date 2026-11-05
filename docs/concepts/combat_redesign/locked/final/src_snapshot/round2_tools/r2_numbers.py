"""r2_numbers (round 2): pull the numbers NOTES needs out of rebuild/board/checks.json (measured on the plates by rb_checks / final_checks).
python r2_numbers.py [keys]   keys: top | pencil | dying | rim | hot | focus | hand | room | tickets | drawn | cells"""
import sys, json
sys.dont_write_bytecode = True
ck = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))
want = sys.argv[1:] or ['top']
RB = ck['rb_checks']


def short(v, n=1600):
    s = json.dumps(v, default=str)
    return s if len(s) <= n else s[:n] + ' ...'


if 'top' in want:
    print('top keys', list(ck.keys()))
    nm0 = next(iter(RB))
    print('rb keys', list(RB[nm0].keys()))
    for k, v in RB[nm0].items():
        if isinstance(v, dict):
            print(' ', k, list(v.keys())[:40])
for nm, r in RB.items():
    if 'pencil' in want and r['f_pencil'].get('rows'):
        print(nm, short(r['f_pencil']['rows']))
    if 'dying' in want:
        a = r['a_cell_contrast']
        rows = [x for x in a.get('rows', a.get('cells', [])) if isinstance(x, dict) and (x.get('dying') or x.get('dies'))]
        print(nm, short(rows, 2400))
    if 'cells' in want:
        a = r['a_cell_contrast']
        print(nm, short({k: v for k, v in a.items() if k not in ('rule',)}, 3000))
    if 'hot' in want:
        h = r['i_hot_core']
        if h.get('present'):
            arcs = [s['w'] for s in h['strokes'] if s['mark'] == 'landing-arc chevron' and s['w'] is not None]
            cells = [s['w'] for s in h['strokes'] if s['mark'] == 'cell chevron' and s['w'] is not None]
            print(nm, 'cell', len(cells), min(cells), max(cells), 'arc', len(arcs), min(arcs), max(arcs),
                  'under', [(s['mark'][:4], s['w'], s['px'], s['box']) for s in h['strokes_under_min']])
    if 'focus' in want:
        d = r['b_value_order'].get('round2', {}).get('structure_rows', {}).get('N FOCUS')
        if d:
            print(nm, 'FOCUS row', d)
        f = r.get('d_palette', {}).get('round2', r.get('d_palette', {}))
    if 'hand' in want:
        print(nm, short(r['e_hand'], 1500))
    if 'tickets' in want:
        print(nm, short(r['g_tickets'], 1500))
    if 'drawn' in want:
        print(nm, short({k: v for k, v in r['d_palette'].items() if k not in ('pairs',)}, 2500))
if 'rim' in want:
    print(short(ck.get('corp', {}).get('rim_luma_C18'), 5000))
if 'room' in want:
    for nm, r in RB.items():
        b = r['b_value_order']
        print(nm, short({k: v for k, v in b.items() if 'room' in k.lower() or 'scrim' in k.lower()}, 600))
