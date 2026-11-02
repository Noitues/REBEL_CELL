"""probe: geometry + frame shapes on the final board"""
import sys, os, time, json
sys.dont_write_bytecode = True
t = time.time()
import lw_render as LW
R = LW.R
A = R.A
import cv_board as CB
import hover_sim as HS
print('import', round(time.time() - t, 1))
for d in range(3):
    print('ring', d, CB.ring_geom(d))
J = A.J
f1 = J['f1']
print('J keys', sorted(J.keys()))
print('f1 keys', sorted(f1.keys()))
fl, st, pv = HS.frame([], None, 'live', hand=['Brace', 'Spin3', 'Trigger', 'Twist'])
print('hs keys', sorted(fl.keys()))
print('missing in hs', set(f1) - set(fl), 'extra', set(fl) - set(f1))
for k in ('hp', 'ram', 'trace', 'schedule', 'rot', 'twr', 'twist', 'hand', 'fw', 'hold'):
    print(k, f1.get(k), fl.get(k))
print('units f1', [(u['id'], u['kind'], u['dep'], u['s'], u['w'], u['hp'], u['fate']['kind'], u.get('land_sectors')) for u in f1['units']])
print('units hs', [(u['id'], u['kind'], u['dep'], u['s'], u['w'], u['hp'], u['fate']['kind'], u.get('land_sectors')) for u in fl['units']])
print('eq f1', f1['pv']['eq'])
print('eq hs', fl['pv']['eq'])
print('hover', {k: v for k, v in J['hover'].items() if k != 'fate'})
print('legal', {c: HS.legal(hand=[c], ram=9) for c in ['Nudge', 'Spin2', 'Spin3', 'Brace', 'Firewall', 'Pull', 'Shove', 'Twist', 'Hold', 'Trigger', 'Strike']})
# compare whole unit records
def strip(u):
    return {k: v for k, v in u.items()}
diffs = []
for a, b in zip(f1['units'], fl['units']):
    for k in a:
        if a.get(k) != b.get(k):
            diffs.append((a['id'], k, a.get(k), b.get(k)))
print('unit diffs', diffs[:20])
for k in f1:
    if k in fl and f1[k] != fl[k] and k not in ('units',):
        print('DIFF', k, str(f1[k])[:160], '|', str(fl[k])[:160])
