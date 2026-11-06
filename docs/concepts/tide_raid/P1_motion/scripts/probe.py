import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/scripts')
import time
from common import *
t = time.time()
w = World('default')
print('world', time.time() - t)
for sid, s in w.sites.items():
    print(sid, s['tier'], s['B'].round(), s['crown'].round())
print('home', w.home, 'hq', w.hq)
for r, R in w.routes.items():
    print(r, R['typ'], R['sites'], plen(R['path']), R['ext'])
for h in w.hunters:
    print('hunter', h['sites'], plen(h['path']))
t = time.time()
cv = new_canvas(w)
print('canvas', time.time() - t)
