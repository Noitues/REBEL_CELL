import numpy as np
from PIL import Image
F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
regions = {'board r<505': None, 'hud x>1060,y<450': (1060, 0, 1920, 450), 'hand x>900,y>740': (900, 740, 1660, 1080), 'room x>1100,y 450-760': (1100, 450, 1920, 760), 'send/undo': (1660, 850, 1900, 1010), 'tickets': (20, 20, 300, 100), 'nameplate': (30, 960, 250, 1060)}
yy, xx = np.mgrid[0:1080, 0:1920]
board = (xx - 536) ** 2 + (yy - 540) ** 2 < 505 ** 2
for beat in ['p1_decide', 'p2_preview', 'p2b_hover', 'p3_resolve', 'p1_nowords']:
    A = np.asarray(Image.open(F + beat + '.png').convert('RGB')).astype(int)
    for sk in ['solace', 'meridian']:
        B = np.asarray(Image.open(F + beat + '_' + sk + '.png').convert('RGB')).astype(int)
        D = np.abs(A - B).max(axis=2) > 6
        s = []
        for k, v in regions.items():
            if v is None: m = board
            else:
                m = np.zeros_like(board); m[v[1]:v[3], v[0]:v[2]] = True; m &= ~board
            s.append('%s %.1f%%' % (k, 100 * D[m].mean()))
        print(beat, sk, ' | '.join(s))
# beat-to-beat diffs (neutral)
P1 = np.asarray(Image.open(F + 'p1_decide.png').convert('RGB')).astype(int)
for beat in ['p2_preview', 'p2b_hover', 'p3_resolve', 'p1_nowords']:
    B = np.asarray(Image.open(F + beat + '.png').convert('RGB')).astype(int)
    D = np.abs(P1 - B).max(axis=2) > 6
    s = []
    for k, v in regions.items():
        if v is None: m = board
        else:
            m = np.zeros_like(board); m[v[1]:v[3], v[0]:v[2]] = True; m &= ~board
        s.append('%s %.1f%%' % (k, 100 * D[m].mean()))
    print('p1 vs', beat, ' | '.join(s))
