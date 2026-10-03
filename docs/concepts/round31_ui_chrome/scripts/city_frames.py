"""Title-screen backdrop: the round 26 v4 night city motion (locked), re-rendered at 1920x1080
with NO map labels (the title must not name territories, least of all REBEL_CELL).

Uses this round's copies of round 26's cm.py / roads.py / fx.py / bases.py (unchanged code,
read-only on earlier rounds). Writes scratch/city/fNN.png (48-frame seamless loop, 80 ms).

  python scripts/city_frames.py [first last]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cm      # noqa: E402
import roads   # noqa: E402

N = 48


def main(a=0, b=N):
    roads.Network.sky = True
    roads.Network.mixed = True
    out = os.path.join(cm.SCR, 'city')
    os.makedirs(out, exist_ok=True)
    s = cm.Scene('night')
    for f in range(a, b):
        p = os.path.join(out, 'f%02d.png' % f)
        if os.path.exists(p):
            continue
        img = s.frame(f, N, opts=dict(labels=False, hires=True))
        img.save(p)
        print('frame', f, flush=True)


if __name__ == '__main__':
    args = [int(v) for v in sys.argv[1:]]
    main(*args) if args else main()
