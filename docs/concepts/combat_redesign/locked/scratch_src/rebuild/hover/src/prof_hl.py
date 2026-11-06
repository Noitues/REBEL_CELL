import cProfile, pstats, sys
sys.argv = ['dbg_hl.py', 'h02', 'Brace']
cProfile.run(open('dbg_hl.py').read(), 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/dbg/hl.prof')
p = pstats.Stats('D:/rc_scratch/combat_redesign/locked/rebuild/hover/dbg/hl.prof')
p.sort_stats('cumulative').print_stats(25)
