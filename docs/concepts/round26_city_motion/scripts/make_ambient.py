"""city_ambient_<theme>_<ver>.gif: calm Heat on the v3 map with the round 26 road network.
48-frame seamless loop at 80 ms.

  python scripts/make_ambient.py            -> v2 (physical decks), night + day
  python scripts/make_ambient.py v3 [night|day]  -> v3: same shapes as fast sky lanes, no decks
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cm
import roads

N = 48
MS = 80
TOL = {'v2': {'night': 28, 'day': 20}, 'v3': {'night': 36, 'day': 22}, 'v4': {'night': 36, 'day': 22}}


def main(ver, themes):
    roads.Network.sky = ver in ('v3', 'v4')
    roads.Network.mixed = ver == 'v4'
    for th in themes:
        s = cm.Scene(th)
        frames = [s.frame(f, N) for f in range(N)]
        d = os.path.join(cm.SCR, 'amb_%s_%s' % (ver, th))
        os.makedirs(d, exist_ok=True)
        for k in (0, 1, 24):
            frames[k].save(os.path.join(d, 'f%02d.png' % k))
        size = cm.save_gif(frames, os.path.join(cm.ROOT, 'city_ambient_%s_%s.gif' % (th, ver)), MS, tol=TOL[ver][th])
        print(ver, th, round(size / 1e6, 2), 'MB')


if __name__ == '__main__':
    args = sys.argv[1:]
    ver = 'v2'
    if args and args[0] in ('v2', 'v3', 'v4'):
        ver = args.pop(0)
    main(ver, args or ['night', 'day'])
