"""d_groups: list the check-d row groups and the lowest pairs per plate (exploration)."""
import json

F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'


def main():
    c = json.load(open(F, encoding='utf-8'))
    for pl in ('p1_decide', 'p1_decide_solace', 'p1_decide_meridian'):
        d = c['rb_checks'][pl]['d_palette']
        groups = {}
        for r in d['rows']:
            groups.setdefault(r['group'], []).append(r)
        print(pl, d['n_pairs'], {g: len(v) for g, v in groups.items()})
        for g, v in groups.items():
            if 'cell' in g or 'skin' in g:
                for r in v[:40]:
                    print('   ', g, r['a'], r['a_hex'], r['b'], r['b_hex'], r['dE'], r.get('pass_'), {k: r[k] for k in r if k not in ('group', 'a', 'b', 'a_hex', 'b_hex', 'dE', 'pass_')})
        low = sorted(d['rows'], key=lambda r: r['dE'])[:6]
        print('  lowest', [(r['group'], r['a'], r['b'], r['dE']) for r in low])
    print(json.dumps(c['all_pass']))
    print(json.dumps(c['cards'], indent=0)[:1500])
    print(json.dumps(c['corp'], indent=0)[:1200])
    print(json.dumps(c['room_grade'], indent=0)[:800])
    print(json.dumps(c['stage2_rule'])[:400])


if __name__ == '__main__':
    main()
