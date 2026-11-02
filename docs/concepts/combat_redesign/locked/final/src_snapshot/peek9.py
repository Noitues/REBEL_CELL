import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E9/src')
import pick9 as P
S = P.S; census = P.census
seed, turn = int(sys.argv[1]), int(sys.argv[2])
st = [x for x in P.run(seed, 5) if x[1] == turn][0][2]
print('hand', st['hand'], 'ram', st['ram'], 'hp', st['hp'], 'rot', st['rot'], 'trace', st['trace'], 'turn', st['turn'])
print('lineup', st['lineup'])
print('challenges', st['challenges'], 'sched', S.schedule(st), 'rsched', st['rsched'][turn - 1:turn + 2], 'adj cell', S.adj_cell(st), 'hp', S.adj_hp(st), 'phase', S.adj_phase(st['turn']), 'nfut', st['nfut'], 'waves_left', S.waves_left(st))
for d, r in enumerate(st['rings']):
    print('ring', d, 'wave', r['wave'], [(u['id'], u['kind'], 'w', u['w'], 's', u['s'], 'hp', u['hp'], u['mx'], 'sh', u['sh'], 'g', u['g'], 'hit', S.unit_hit(u), 'df', S.defense(st, u, d), 'warded', S.warded(st, u)) for u in r['units']])
print('wheel', [(w['t'], w['hp'], w['jam']) for w in st['wheel']], 'rot', st['rot'])
print('fate', S.fate(st))
outs, capped = census.enumerate_outcomes(S.g, P.cl(st), cap=5000)
print(len(outs), capped)
for o in outs[:8]:
    print(round(o['score'], 1), 'taken', o['taken'], 'slost', o['slost'], 'dealt', o['dealt'], P.plan_of(o), 'END', P.end_of(o))
print('--- best with Trigger only (no Brace), best with Brace')
for lab, f in (('trigger-no-brace', lambda pl: any(a[0] == 'Trigger' for a in pl) and not any(a[0] == 'Brace' for a in pl)), ('brace-no-trigger', lambda pl: any(a[0] == 'Brace' for a in pl) and not any(a[0] == 'Trigger' for a in pl))):
    c = [o for o in outs if f(P.plan_of(o))]
    if c:
        o = c[0]
        print(lab, round(o['score'], 1), 'taken', o['taken'], 'slost', o['slost'], P.plan_of(o), 'END', P.end_of(o))
