import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E10/src')
import pick10 as P
S = P.S; census = P.census
seed, turn = int(sys.argv[1]), int(sys.argv[2])
st0 = [x for x in P.run(seed, 3) if x[1] == turn][0][2]
print('hp', st0['hp'], 'ram', st0['ram'], 'turn', st0['turn'], 'hand', st0['hand'], 'sched', S.schedule(st0), 'trace', st0['trace'], 'adj', S.adjuster(st0)[:2], 'inrange', S.adj_in_range(st0))
for d, u in S.board_units(st0):
    print(d, u['id'], u['kind'], 'w', u['w'], 's', u['s'], 'hp', u['hp'], '/', u['mx'], 'sh', u['sh'], 'g', u['g'], 'hit', S.unit_hit(u), S.defense(st0, u, d), S.fate(st0).get(u['id']))
print('wheel', [(w['t'], w['hp'], w['mx']) for w in st0['wheel']], 'rot', st0['rot'])
outs, capped = census.enumerate_outcomes(S.g, S.clone(st0), cap=5000)
print('n', len(outs), capped)
for o in outs[:8]:
    print(round(o['score'], 1), o['taken'], o['slost'], o['dealt'], o['kills'], P.plan_of(o), P.end_of(o))
