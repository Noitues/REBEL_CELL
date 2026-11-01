"""Search E8 seeds/turns for: Trigger saves you, wide unit, shielded Jammer + armored Payload, Twist line-up. Read-only import of the E8 sim."""
import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_tmp/combat_concepts/D4_E8')
sys.path.insert(0, 'D:/rc_tmp/combat_concepts/_common_K')
import sim as S
import census

def cl(x): return S.clone(x)

def run(seed, maxturn=4):
    st = S.new(seed); rng = random.Random(seed); S.start_turn(st, rng)
    out = []
    for t in range(1, maxturn + 1):
        out.append((seed, t, cl(st)))
        outs, capped = census.enumerate_outcomes(S.g, cl(st))
        plan = [a for a in outs[0]['plan'] if a[0] != 'end']
        for a in plan: S.apply(st, a)
        S.end_turn(st, None)
        if S.status(st): break
        S.start_turn(st, rng)
    return out

def nunit(tp): return sum(1 for e in tp if e[0] == 'unit')

def evaluate(st):
    base = S.preview(st)
    units = S.board_units(st)
    kinds = {}
    for d, u in units: kinds.setdefault(u['kind'], []).append((d, u))
    shj = [1 for d, u in kinds.get('Jammer', []) if u['sh'] > 0]
    pay = len(kinds.get('Payload', []))
    wide = sum(1 for d, u in units if u['w'] >= 2)
    best = None
    for a in S.actions(st):
        if a[0] != 'Trigger': continue
        tp = S.trigger_preview(st, a[1])
        kills = [e for e in tp if e[0] == 'unit' and e[7] == 0 and e[2] == 0]
        s2 = cl(st); S.apply(s2, a); pv = S.preview(s2)
        sv = base['taken'] - pv['taken']
        if kills and sv > 0 and (best is None or sv > best[0]): best = (sv, a, pv['taken'], base['taken'])
    # twist line-up: next-turn trigger unit-hits gained by a twist
    tw = 0
    nxt0 = None
    for a in S.actions(st):
        if a[0] != 'Twist': continue
        s2 = cl(st); S.apply(s2, a); s3 = S.preview(s2)['after']
        s3 = cl(s3); S._advance(s3)
        m = 0
        for b in S.actions(s3) if False else []: pass
        # trigger options next turn (cards ignored: any unit on ring 1/2)
        for d, r in enumerate(s3['rings']):
            if d not in (1, 2): continue
            for u in r['units']:
                if S.sealed(s3, d, u): continue
                try: m = max(m, nunit(S.trigger_preview(s3, u['id'])))
                except Exception: pass
        tw = max(tw, m)
    return best, len(shj), pay, wide, len(units), tw

if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    for seed in range(lo, hi):
        ring = S.new(seed)['lineup'][-1][0][0] == 'Ring'
        for sd, t, st in run(seed):
            if t < 2: continue
            best, shj, pay, wide, nu, tw = evaluate(st)
            if not best: continue
            print('seed', seed, 't', t, 'ring', ring, 'shJ', shj, 'pay', pay, 'wide', wide, 'units', nu, 'twistlineup', tw, 'ntrig', st['hand'].count('Trigger'), 'twist', 'Twist' in st['hand'],
                  'saved', best[0], 'taken', best[2], 'vs', best[3], 'hp', st['hp'], 'adj_range', S.adj_in_range(st), 'hand', st['hand'], flush=True)
