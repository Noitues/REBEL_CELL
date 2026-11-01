import sys, importlib
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/transitions/netrun_fail/scripts')
from nf_lib import *
n = sys.argv[1]
m = importlib.import_module('build_' + n)
bg, full, ph = m.build()
full.save(OUT + 'scratch_' + n + '.png')
bg.save(OUT + 'scratch_' + n + '_bg.png')
ph_overlay(full, ph).save(OUT + 'scratch_' + n + '_ph.png')
print('ok', full.size, len(ph))
