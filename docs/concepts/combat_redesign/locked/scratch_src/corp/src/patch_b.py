p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/dump10.py'
t = open(p).read()
i = t.index("print('LINES'")
j = t.index('\n', i)
add = "\nA('hero line takes 0 HP; the Trigger-only and Brace+soak-only lines each take 1 HP and lose more slice pips', (pv2['taken'], pv2t['taken'], pv2b['taken'], pv2t['slost'] > pv2['slost'], pv2b['slost'] > pv2['slost']), (0, 1, 1, True, True))\nA('Trigger-only option still earns the refund (its Trigger kills), Brace-only does not', (pv2t['after']['refn'], pv2b['after']['refn']), (1, 0))"
t = t[:j] + add + t[j:]
open(p, 'w').write(t)
