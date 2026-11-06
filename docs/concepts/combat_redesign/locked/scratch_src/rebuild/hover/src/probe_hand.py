"""the sim's own hand order (frame 'hand', sorted by (wave card, name)) for each hover plate's hand"""
import sys, os
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
os.chdir(SRC)
import hover_sim as HS
print('WAVE_CARDS', sorted(HS.S.WAVE_CARDS))
for c in ('Strike', 'Shove', 'Pull', 'Hold', 'Firewall'):
    hand = [c, 'Brace', 'Trigger', 'Twist']
    f, _, _ = HS.frame([], None, 'x', hand=hand)
    print(c, f['hand'])
f, _, _ = HS.frame([], None, 'x', hand=['Brace', 'Spin3', 'Trigger', 'Twist'])
print('H4', f['hand'])
