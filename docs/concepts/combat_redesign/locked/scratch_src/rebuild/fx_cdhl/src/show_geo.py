"""show_geo.py <skin> <var> : print the base geometry (tokens, HP ticks, units)"""
import sys, json
g = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/geo_%s_%s.json' % (sys.argv[1], sys.argv[2])))
print('vs_final', g.get('vs_final'), 'hud_bottom', g.get('hud_bottom'))
for k, u in g['units'].items():
    print(k, u, 'tok', [round(v, 1) for v in g['tokens'][k]])
for k, v in g['pips'].items():
    print('pips', k, [[round(x, 1) for x in p[:4]] + [p[4]] for p in v])
print('adj', g['adj'])
