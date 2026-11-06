"""E10 search 2: BEST line kills with a Trigger (refund) and a Twist is strictly needed (every Twist-free line scores lower). usage: python pick10b.py LO HI"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E10/src')
import pick10 as P
S = P.S; census = P.census
lo, hi = int(sys.argv[1]), int(sys.argv[2])
for seed in range(lo, hi):
    for sd, t, st in P.run(seed, 2):
        outs, capped = census.enumerate_outcomes(S.g, P.cl(st), cap=5000)
        if capped: continue
        top = outs[0]; pl = P.plan_of(top)
        if not any(a[0] == 'Trigger' for a in pl): continue
        s2 = P.cl(st); ref = 0
        for a in pl:
            if a[0] == 'Trigger' and any(e[0] == 'refund' for e in S.trigger_preview(s2, a[1])): ref += 1
            S.apply(s2, a)
        if not ref: continue
        notw = [o for o in outs if not any(a[0] == 'Twist' for a in P.plan_of(o))]
        tw_matters = notw[0]['score'] < top['score'] - 1e-9
        units = S.board_units(st)
        wide = sum(1 for d, u in units if u['w'] >= 2)
        shj = sum(1 for d, u in units if u['kind'] == 'Jammer' and u['sh'] > 0)
        pay = sum(1 for d, u in units if u['kind'] == 'Payload')
        grown = sum(1 for d, u in units if u['g'] > 0)
        zero = 0 in S.schedule(st)
        nobrace = [o for o in outs if not any(a[0] == 'Brace' for a in P.plan_of(o))]
        brace = [o for o in outs if any(a[0] == 'Brace' for a in P.plan_of(o))]
        print('seed', sd, 't', t, 'twMatters', tw_matters, 'twistIn', any(a[0] == 'Twist' for a in pl), 'top', pl, 'end', P.end_of(top), 'taken', top['taken'], 'slost', top['slost'], 'dealt', top['dealt'],
              'wide', wide, 'shJ', shj, 'pay', pay, 'grown', grown, 'zero', zero, 'braceInHand', 'Brace' in st['hand'], 'bestBraceTaken', brace[0]['taken'] if brace else None, 'bestNoBraceTaken', nobrace[0]['taken'], 'hand', st['hand'], flush=True)
