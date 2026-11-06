"""gate1 (round 2): run corp/src rb_checks on the PUBLISHED final/ plates (read only; rb_checks.run writes nothing).
Also byte-compare published vs rebuild/board. Output: gate1/out/rb_checks_published.json + printed summary."""
import sys, os, json, hashlib
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import rb_checks as RC

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
BOARD = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
OUT = 'D:/rc_scratch/combat_redesign/locked/round2/gate1/out/'
os.makedirs(OUT, exist_ok=True)
NAME = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords'}
CORPS = ['neutral', 'solace', 'meridian']


def h(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    try:
        import numpy as np
        if isinstance(o, np.generic):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
    except Exception:
        pass
    return o


allres = {}
for corp in CORPS:
    for beat in NAME:
        nm = NAME[beat] + ('' if corp == 'neutral' else '_' + corp)
        sfx = beat + ('' if corp == 'neutral' else '_' + corp)
        pub = FINAL + nm + '.png'
        same = h(pub) == h(BOARD + nm + '.png')
        r = RC.run(nm, pub, sfx)
        allres[nm] = jsonable(r)
        print('=' * 90)
        print(nm, 'byte-identical to rebuild/board:', same, 'PLATE', 'PASS' if r['plate_pass'] else 'FAIL', r['pass'])
        print(RC.table_order(r))
        b = r['b_value_order']
        print('b failures', b['failures'])
        bb = b.get('round2', {})
        print('b round2 keys', list(bb.keys()))
        for k in ('unclassed_bright_px', 'unclassed', 'rows'):
            if k in bb:
                v = bb[k]
                print('  ', k, v if not isinstance(v, list) else v[:60])
        print('d failures', r['d_palette']['failures'])
        dd = r['d_palette'].get('round2', {})
        print('d round2', {k: v for k, v in dd.items() if k != 'rows'} if isinstance(dd, dict) else dd)
        print('e', {k: v for k, v in r['e_hand'].items() if k not in ('rule', 'rest_cards_covered_info')})
        print('f', {k: v for k, v in r['f_pencil'].items() if k != 'rule'})
        print('g', {k: v for k, v in r['g_tickets'].items() if k != 'rule'})
        print('h', {k: v for k, v in r['h_hud_rows'].items() if k != 'rule'})
        print('i', {k: v for k, v in r['i_hot_core'].items() if k != 'rule'})
json.dump(allres, open(OUT + 'rb_checks_published.json', 'w'), indent=1, default=str)
print('SUMMARY')
for nm, r in allres.items():
    print('%-26s %s %s' % (nm, 'PASS' if r['plate_pass'] else 'FAIL', r['pass']))
