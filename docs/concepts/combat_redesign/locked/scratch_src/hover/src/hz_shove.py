"""all legal Shoves and Strikes: what the sim does (bumps included)"""
import sys
sys.dont_write_bytecode = True
import hover_sim as HS
from hz_plans import us

H = ['Shove', 'Brace', 'Trigger', 'Twist']
live, _, _ = HS.frame([], None, 'live', hand=H)
L = us(live)
for a in HS.legal(hand=['Shove'], ram=9) + HS.legal(hand=['Strike'], ram=9) + HS.legal(hand=['Firewall'], ram=9):
    hand = [a[0], 'Brace', 'Trigger', 'Twist']
    f, st, pv = HS.frame([a], None, 'x', hand=hand)
    P = us(f)
    print('==', a, 'eq', f['pv']['eq']['lands'], f['pv']['eq']['through'], 'hp_after', f['pv']['hp_after'], 'ram', f['ram'], 'trace', f['trace'], 'adj', f['adj']['hp'], f['adj']['hp_after'], f['adj']['s'], 'fw', f['fw'])
    print('   tlog', f['tlog'], 'log', [e for e in f['log'] if e[0] in ('fw', 'lock')])
    for k in sorted(set(L) | set(P)):
        if L.get(k) != P.get(k):
            print('   unit', k, L.get(k), '->', P.get(k))
print(HS.S.CARDS['Shove'] if hasattr(HS.S, 'CARDS') else '')
import inspect
for nm in ('apply',):
    src = inspect.getsource(getattr(HS.S, nm))
    print(src[:6000])
