import sys, json, copy, time
sys.dont_write_bytecode = True
import asm_r2 as A0
A0.setup()
import sp_tower as T
import sps2_slices
from PIL import Image
ROOT = 'D:/rc_scratch/combat_redesign/punk_slices/spiderpunk_collage/'
J = json.load(open(ROOT + 'state_e10.json'))
f = J['f1']
modes = {'n': f}
fi = copy.deepcopy(f)
for w in fi['wheel']:
    w['hp'] = 2
    w['hp_after'] = 2
fh = copy.deepcopy(f)
for w in fh['wheel']:
    w['hp'] = 2
    w['hp_after'] = 0
modes['i'] = fi
modes['h'] = fh
t0 = time.time(); TWX = 1000
import os
MODES = os.environ.get('MODES', 'nih')
for v in sys.argv[1:] or ('A', 'B'):
    T.VARIANT[0] = v
    for tag, st in [(k, x) for k, x in modes.items() if k in MODES]:
        im, cv = T.render_tower(st, with_trim=False)
        im = cv.rgba()
        bg0 = Image.new('RGBA', im.size, (24, 22, 36, 255)); bg0.alpha_composite(im); bg0.convert('RGB').save(ROOT + 'work/_k_%s_%s.png' % (v, tag))
        im = im.resize((TWX, TWX), Image.LANCZOS)
        bg = Image.new('RGBA', im.size, (38, 36, 56, 255))
        bg.alpha_composite(im)
        bg.convert('RGB').save(ROOT + 'work/_s2_%s_%s.png' % (v, tag))
        print(v, tag, round(time.time() - t0), flush=True)
