"""usage: python make_plate.py bd1_interior plate1_interior   -> plate + squint + stats"""
import sys, importlib, json
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/scripts')
from bd_common import *
mod = importlib.import_module(sys.argv[1])
name = sys.argv[2]
bd = mod.run()
save(bd, SCR + name + '_backdrop.png')
plate = compose(bd)
save(plate, OUT + name + '.png')
save(squint(plate), OUT + name + '_squint.png')
st = stats(plate, name)
print(json.dumps(st))
json.dump(st, open(SCR + name + '_stats.json', 'w'))
