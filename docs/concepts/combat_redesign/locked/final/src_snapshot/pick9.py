"""E9 state search (read-only import of the E9 sim). For each seed/turn: enumerate every line with the planner (census.enumerate_outcomes, END TURN soak choice included);
report states whose planner-best line plays a Trigger that hits a unit, has a Brace card in hand, shows growth/wide/shield/armor, and (best) a non-empty soak mark.
usage: python pick9.py LO HI"""
import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_tmp/combat_concepts/D4_E9')
sys.path.insert(0, 'D:/rc_tmp/combat_concepts/_common_K')
import sim as S
import census


def cl(x): return S.clone(x)


def plan_of(o): return [a for a in o['plan'] if a[0] != 'end']


def end_of(o): return [a for a in o['plan'] if a[0] == 'end'][0][1]


def run(seed, maxturn=4):
    st = S.new(seed); rng = random.Random(seed); S.start_turn(st, rng)
    for t in range(1, maxturn + 1):
        yield seed, t, cl(st)
        outs, capped = census.enumerate_outcomes(S.g, cl(st))
        for a in plan_of(outs[0]):
            S.apply(st, a)
        S.end_turn(st, end_of(outs[0]))
        if S.status(st): break
        S.start_turn(st, rng)


if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    for seed in range(lo, hi):
        for sd, t, st in run(seed):
            if t < 2:
                continue
            outs, capped = census.enumerate_outcomes(S.g, cl(st), cap=5000)
            top = outs[0]
            pl = plan_of(top)
            trig = [a for a in pl if a[0] == 'Trigger']
            brace_in_hand = 'Brace' in st['hand']
            if not trig or not brace_in_hand:
                continue
            units = S.board_units(st)
            wide = sum(1 for d, u in units if u['w'] >= 2)
            shj = sum(1 for d, u in units if u['kind'] == 'Jammer' and u['sh'] > 0)
            pay = sum(1 for d, u in units if u['kind'] == 'Payload')
            grown = sum(1 for d, u in units if u['g'] > 0)
            tp = S.trigger_preview(st, trig[0][1])
            hitu = sum(1 for e in tp if e[0] == 'unit')
            soak = end_of(top)
            # best Brace line
            bl = [o for o in outs if any(a[0] == 'Brace' for a in plan_of(o))]
            print('seed', sd, 't', t, 'cap', capped, 'top', pl, 'end', soak, 'taken', top['taken'], 'score', round(top['score'], 1), 'wide', wide, 'shJ', shj, 'pay', pay, 'grown', grown,
                  'trigHitUnits', hitu, 'bestBrace', (round(bl[0]['score'], 1), bl[0]['taken'], plan_of(bl[0])) if bl else None, 'hp', st['hp'], flush=True)
