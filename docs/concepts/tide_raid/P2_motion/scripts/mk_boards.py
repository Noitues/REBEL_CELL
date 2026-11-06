"""Derive spec2.py / boards2.py / table2.py from the iteration-1 sources (read-only) with the P2 patches. Run once: python mk_boards.py"""
import re, os
P1 = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P1_motion/scripts/'
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'

# ---------------------------------------------------------------- spec
s = open(P1 + 'spec.py', encoding='utf8').read()
rep = [
    ("total=120, ready=34", "total=150, ready=34"),
    ("34, 83, 'OUT_QUAD'", "34, 72, 'OUT_QUAD'"),
    ("34, 103, 'OUT_QUAD'", "34, 92, 'OUT_QUAD'"),
    ("57, 64, 'OUT_CUBIC'", "45, 53, 'OUT_CUBIC'"),
    ("83, 85, 'STEP'", "72, 74, 'STEP'"),
]
for a, b in rep:
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b)
open(HERE + 'spec2.py', 'w', encoding='utf8').write(s)

# ---------------------------------------------------------------- boards
b = open(P1 + 'boards.py', encoding='utf8').read()
head_end = b.index("BOARDS_DIR = ")
new_head = '''"""Build the 12 storyboard sheets on the P2 look: frame strip + Gantt timing ruler + beat table.  python boards2.py [slug ...]"""
import sys, os, math, time
sys.dont_write_bytecode = True
H2 = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/scripts'
sys.path.insert(0, H2)
sys.path.append('D:/rc_art/art-pass/docs/concepts/tide_raid/P1_motion/scripts')
import numpy as np
from PIL import Image, ImageDraw
from lib import font
import spec2 as SP
import boardscenes as BS
import scenes as S1

OUTDIR = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P2_motion/'
WORKD = 'D:/rc_scratch/tide_concepts/p2m_work/'


def crop_scale(a, box, size):
    x0, y0, x1, y1 = [int(v) for v in box]
    im = Image.fromarray(a).crop((x0, y0, x1, y1))
    return im.resize(tuple(size), Image.LANCZOS) if im.size != tuple(size) else im


'''
b = new_head + b[head_end:]
# renderers
r0 = b.index("# ------------------------------------------------------------------ renderers per board")
r1 = b.index("def thumb(rkey, f, tw):")
RT = '''BOX = {
    'jackin': (0, 0, 1920, 1080), 'jackout': (0, 0, 1920, 1080), 'draw': (700, 560, 1900, 1080),
    'dragv': (330, 300, 1230, 1010), 'dragi': (330, 300, 1230, 1010), 'daemon': (330, 300, 1290, 840),
    'lock': (1100, 330, 1700, 668), 'hunter': (700, 250, 1500, 800), 'shield': (330, 300, 1000, 760),
    'home': (0, 420, 960, 960), 'poster': (580, 300, 1280, 900), 'bloom': (100, 230, 1180, 905), 'lost': (0, 0, 1920, 1080),
}
_R = BS.board_renderers()
RENDER = {k: (_R[k], BOX[k]) for k in _R}


'''
b = b[:r0] + RT + b[r1:]
b = b.replace("VER = {'bloom': '_v2', 'lost': '_v2', 'home': '_v2', 'daemon': '_v2', 'shield': '_v2'}", "VER = {k: '_p2b' for k in ['jackin', 'jackout', 'draw', 'dragv', 'dragi', 'daemon', 'lock', 'hunter', 'shield', 'home', 'poster', 'bloom', 'lost']}")
b = b.replace("from tl import EASE", "from tl import EASE")
b = b.replace("            D = B.dmn()", "            D = S1.dmn()")
b = b.replace('bd["frames"] = [0, 32, 40, 50, 60, 72, D.f_arr, D.f_arr + 2, D.f_arr + 6, D.f_arr + 20]', 'bd["frames"] = [0, 30, 36, 45, 58, D.f_arr - 3, D.f_arr, D.f_arr + 2, D.f_arr + 8, D.f_arr + 40]')
b = b.replace("'BOARD %s' % bd['id']", "'BOARD %s' % bd['id']")
open(HERE + 'boards2.py', 'w', encoding='utf8').write(b)
print('ok')
