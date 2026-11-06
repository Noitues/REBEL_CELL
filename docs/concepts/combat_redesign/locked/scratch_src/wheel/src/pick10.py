"""E10 state search (read-only import of the E10 sim; importing sim patches census.score to the HP-first score).
For each seed and turn 1..3: enumerate every line of the turn (END TURN soak choice included), take the planner's top line, and report
states whose BEST line plays a Trigger that KILLS a unit (refund in the Trigger preview), with the visual ingredients counted.
usage: python pick10.py LO HI"""
import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_tmp/combat_concepts/D4_E10')
sys.path.insert(0, 'D:/rc_tmp/combat_concepts/_common_K')
import sim as S
import census


def cl(x): return S.clone(x)


def plan_of(o): return [a for a in o['plan'] if a[0] != 'end']


def end_of(o): return [a for a in o['plan'] if a[0] == 'end'][0][1]


def run(seed, maxturn=3):
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
            outs, capped = census.enumerate_outcomes(S.g, cl(st), cap=5000)
            top = outs[0]
            pl = plan_of(top)
            s2 = cl(st)
            refund_trig = 0
            twist_before = False
            seen_twist = False
            for a in pl:
                if a[0] == 'Twist': seen_twist = True
                if a[0] == 'Trigger':
                    tp = S.trigger_preview(s2, a[1])
                    if any(e[0] == 'refund' for e in tp):
                        refund_trig += 1
                        twist_before = twist_before or seen_twist
                S.apply(s2, a)
            units = S.board_units(st)
            wide = sum(1 for d, u in units if u['w'] >= 2)
            shj = sum(1 for d, u in units if u['kind'] == 'Jammer' and u['sh'] > 0)
            pay = sum(1 for d, u in units if u['kind'] == 'Payload')
            grown = sum(1 for d, u in units if u['g'] > 0)
            zero = 0 in S.schedule(st)
            brace_h = 'Brace' in st['hand']
            bl = [o for o in outs if any(a[0] == 'Brace' for a in plan_of(o))]
            print('seed', sd, 't', t, 'cap', capped, 'n', len(outs), 'top', pl, 'end', end_of(top), 'taken', top['taken'], 'dealt', top['dealt'], 'refundTrig', refund_trig, 'twistBefore', twist_before,
                  'wide', wide, 'shJ', shj, 'pay', pay, 'grown', grown, 'zero', zero, 'braceHand', brace_h, 'bestBrace', (round(bl[0]['score'], 1), bl[0]['taken']) if bl else None, 'hp', st['hp'], 'hand', st['hand'], flush=True)
