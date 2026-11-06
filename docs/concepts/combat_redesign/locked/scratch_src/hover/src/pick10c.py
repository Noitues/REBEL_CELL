"""E10 search 3: the BEST line has a Trigger kill (refund) AND a Twist that pays off: the same line without the Twist leaves a worse NEXT bill (HP through next turn, nothing more played).
usage: python pick10c.py LO HI"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E10/src')
import pick10 as P
S = P.S; census = P.census


def nxt(st_after):
    s3 = P.cl(st_after)
    if S.status(s3): return None
    S._advance(s3)
    pv = S.preview(s3)
    return pv['taken'], pv['slost'], pv['raw']


lo, hi = int(sys.argv[1]), int(sys.argv[2])
for seed in range(lo, hi):
    for sd, t, st in P.run(seed, 2):
        outs, capped = census.enumerate_outcomes(S.g, P.cl(st), cap=5000)
        if capped: continue
        top = outs[0]; pl = P.plan_of(top); en = P.end_of(top)
        if not any(a[0] == 'Twist' for a in pl): continue
        s2 = P.cl(st); ref = 0; ok = True
        for a in pl:
            if a[0] == 'Trigger' and any(e[0] == 'refund' for e in S.trigger_preview(s2, a[1])): ref += 1
            S.apply(s2, a)
        if not ref: continue
        sA = P.cl(st)
        for a in pl: S.apply(sA, a)
        pvA = S.preview(sA, en)
        nA = nxt(pvA['after'])
        sB = P.cl(st)
        for a in pl:
            if a[0] != 'Twist': S.apply(sB, a)
        pvB = S.preview(sB, en)
        nB = nxt(pvB['after'])
        units = S.board_units(st)
        wide = sum(1 for d, u in units if u['w'] >= 2); shj = sum(1 for d, u in units if u['kind'] == 'Jammer' and u['sh'] > 0)
        pay = sum(1 for d, u in units if u['kind'] == 'Payload'); grown = sum(1 for d, u in units if u['g'] > 0); zero = 0 in S.schedule(st)
        print('seed', sd, 't', t, 'nextWith', nA, 'nextWithout', nB, 'better', (nA is not None and nB is not None and (nA[0], nA[1]) < (nB[0], nB[1])), 'top', pl, 'end', en, 'taken', top['taken'], 'dealt', top['dealt'],
              'wide', wide, 'shJ', shj, 'pay', pay, 'grown', grown, 'zero', zero, 'brace', any(a[0] == 'Brace' for a in pl), flush=True)
