"""city_ambient_night_v2.gif / city_ambient_day_v2.gif: calm Heat on the v3 map with the round 26 road
network. 48-frame seamless loop at 80 ms."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cm

N = 48
MS = 80
TOL = {'night': 28, 'day': 20}


def main(themes):
    for th in themes:
        s = cm.Scene(th)
        frames = [s.frame(f, N) for f in range(N)]
        d = os.path.join(cm.SCR, 'amb_' + th)
        os.makedirs(d, exist_ok=True)
        for k in (0, 12, 24, 36):
            frames[k].save(os.path.join(d, 'f%02d.png' % k))
        size = cm.save_gif(frames, os.path.join(cm.ROOT, 'city_ambient_%s_v2.gif' % th), MS, tol=TOL[th])
        print(th, round(size / 1e6, 2), 'MB')


if __name__ == '__main__':
    main(sys.argv[1:] or ['night', 'day'])
