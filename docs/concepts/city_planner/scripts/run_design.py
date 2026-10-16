import importlib, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from panel import compose, make_panel
OUT = os.path.join(os.path.dirname(__file__), '..')
key = sys.argv[1]
mod = importlib.import_module('design_' + key)
t0 = time.time()
m = mod.build()
M = mod.META
mp = m.final(2000)
mp.save(os.path.join(OUT, 'map_' + M['slug'] + '.png'))
pn = make_panel(M['title'], M['subtitle'], M['blurb'], M['notes'], M['skip'], M.get('extras', ()), M.get('evo', ()))
compose(mp, pn, os.path.join(OUT, 'plan_' + M['slug'] + '.png'))
print('ok', M['slug'], round(time.time() - t0, 1))
