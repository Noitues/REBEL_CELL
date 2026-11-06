import sys, time
sys.dont_write_bytecode=True
t=time.time()
import build10 as B
print('import', time.time()-t); t=time.time()
f=B.J['f1']
b=B.render_board(B.board_frame(f), B.CONS)
print('board', time.time()-t); t=time.time()
g=B.grade_units(b,f)
print('grade', time.time()-t)
