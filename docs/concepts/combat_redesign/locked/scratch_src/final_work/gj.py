import json
r = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/work/grammar_check.json'))
for k in ('chevrons_sector3', 'chevrons_sector0'):
    for n, v in r[k].items():
        print(k, n, [(e['grammar'], e['luma_contrast'], e['dE2000'], e['chevron_rgb'], e['cell_rgb']) if e else None for e in v])
for n, v in r['hatch_on_cell'].items():
    print(n, v['cell_rgb'], {k: (x['luma_contrast'], x['dE2000']) for k, x in v.items() if k != 'cell_rgb'})
