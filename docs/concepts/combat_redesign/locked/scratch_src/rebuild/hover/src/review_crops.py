"""review_crops.py <name> ...  -> dbg/<name>_{hud,wheel,hand}.png at 1x (for looking at every plate at 1:1)"""
import sys, os
sys.dont_write_bytecode = True
from PIL import Image
HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/'
for nm in sys.argv[1:]:
    im = Image.open(HERE + 'out/' + nm + '.png').convert('RGB')
    im.crop((1060, 0, 1920, 600)).save(HERE + 'dbg/%s_hud.png' % nm)
    im.crop((20, 20, 1060, 1060)).save(HERE + 'dbg/%s_wheel.png' % nm)
    im.crop((900, 600, 1920, 1080)).save(HERE + 'dbg/%s_hand.png' % nm)
    print('ok', nm)
