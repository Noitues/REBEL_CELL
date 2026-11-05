"""measure_rooms.py: L* of the candidate T5 K1 rooms (v3.1 bare, rb2-1 graded without the board scrim, the plate's room) and of the
published plate, whole frame and in the reviewer's room box (1200-1800 x 450-800).  Saves 1/2-size previews for a look at 1x."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from lstar import mean_L, pct_L
HERE = 'D:/rc_scratch/combat_redesign/locked/round2/transitions/'
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
out = {}
for corp, pub in (('neutral', 'p1_decide.png'), ('solace', 'p1_decide_solace.png')):
    Z = np.load(HERE + 'layers/%s_p1.npz' % corp)
    rooms = dict(bare=Z['room_bare'][..., :3], graded=Z['room_graded'][..., :3], plate_room=Z['bg'][..., :3],
                 plate=np.asarray(Image.open(FIN + pub).convert('RGB')))
    r = {}
    for k, a in rooms.items():
        a = a.astype(np.float64)
        box = a[450:800, 1200:1800]
        left = a[:, :1100]
        r[k] = dict(frame_mean=round(mean_L(a), 1), frame_p95=round(pct_L(a, 95), 1), box_mean=round(mean_L(box), 1), box_p95=round(pct_L(box, 95), 1),
                    left_mean=round(mean_L(left), 1))
        if corp == 'neutral':
            Image.fromarray(a.astype(np.uint8)).save(HERE + 'probe/room_%s.png' % k)
    out[corp] = r
    print(corp)
    for k, v in r.items():
        print('  %-11s' % k, v)
json.dump(out, open(HERE + 'probe/rooms.json', 'w'), indent=1)
