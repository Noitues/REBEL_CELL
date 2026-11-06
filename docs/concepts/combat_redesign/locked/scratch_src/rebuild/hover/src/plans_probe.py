"""print the Twist options and the NEXT row of each (sim, read only), and the plan summaries of hz_plans"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import hover_sim as HS
H4 = ['Brace', 'Spin3', 'Trigger', 'Twist']
live, _, _ = HS.frame([], None, 'live', hand=H4)
print('live next', live['next'], 'eq', live['pv']['eq'], 'hp_after', live['pv']['hp_after'])
for a in HS.legal(hand=['Twist'], ram=9):
    f, st, pv = HS.frame([a], None, 'tw', hand=H4)
    print('Twist', a, 'next', f['next'], 'eq lands/through', f['pv']['eq']['lands'], f['pv']['eq']['through'], 'hp_after', f['pv']['hp_after'], 'twr', f['twr'])
for nm, cards in (('trig', [('Trigger', 4)]), ('twist+trig', [('Twist', (1, 1)), ('Trigger', 4)])):
    f, st, pv = HS.frame(cards, None, nm, hand=H4)
    print(nm, 'next', f['next'], 'eq', f['pv']['eq']['lands'], f['pv']['eq']['through'], 'ram', f['ram'], 'trace', f['trace'], 'refunds', f['refunds'])
for c in ['Nudge', 'Spin2', 'Spin3', 'Brace', 'Firewall', 'Pull', 'Shove', 'Twist', 'Hold', 'Trigger', 'Strike']:
    print(c, HS.legal(hand=[c], ram=9))
