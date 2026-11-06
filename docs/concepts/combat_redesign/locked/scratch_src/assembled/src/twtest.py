import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_polish/E7_waves/E10/src')
import pick10 as P
S = P.S
seed, turn = int(sys.argv[1]), int(sys.argv[2])
st0 = [x for x in P.run(seed, 3) if x[1] == turn][0][2]
for plan in ([('Twist', (1, -1)), ('Trigger', 4), ('Brace', 4)], [('Trigger', 4), ('Brace', 4)]):
    st = P.cl(st0)
    for a in plan: S.apply(st, a)
    pv = S.preview(st, (3,))
    print(plan, 'taken', pv['taken'], 'dealt', pv['dealt'], 'sched', S.schedule(st))
    print('  tlog', st['tlog'])
    for e in pv['log']: print('   ', e)
    for d, u in S.board_units(st): print('   unit', d, u['id'], u['kind'], u['s'], u['w'], u['hp'], u['g'])
