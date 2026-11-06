import sys
sys.dont_write_bytecode=True
import time; t=time.time()
for m in ['build10','kglyph2','hud2','obj2','kcard2','kscene2','wc2','wc2_run','wr2_units','wr2_cells','wr2_boss','r2_ground','r2_sched','r2_arcs','r2_misc','a2_kit','a2_stick','a2_hover','a2_plan','a2_tgt']:
    try:
        __import__(m); print('ok',m, round(time.time()-t,1))
    except Exception as e:
        import traceback; print('FAIL',m, repr(e)); traceback.print_exc(limit=3)
