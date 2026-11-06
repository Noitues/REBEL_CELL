"""final_publish: copy the rendered plates (corp/out/as_*.png, written by asm_render.py) to locked/final/ under their plate names."""
import shutil, os, sys
OUT = 'D:/rc_scratch/combat_redesign/locked/hover/out/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
MAP = {'p1': 'p1_decide', 'p2': 'p2_preview', 'p2b': 'p2b_hover', 'p3': 'p3_resolve', 'nowords': 'p1_nowords',
       'p1_solace': 'p1_decide_solace', 'p2b_solace': 'p2b_hover_solace', 'p1_meridian': 'p1_decide_meridian', 'p2b_meridian': 'p2b_hover_meridian'}
os.makedirs(FINAL, exist_ok=True)
for k, v in MAP.items():
    src = OUT + 'as_%s.png' % k
    if os.path.exists(src):
        shutil.copyfile(src, FINAL + v + '.png')
        print(k, '->', v)
    else:
        print('MISSING', src)
