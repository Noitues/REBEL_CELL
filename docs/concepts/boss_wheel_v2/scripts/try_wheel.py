"""Debug: render one direction. python try_wheel.py roman A [S] [key=value...] -> D:/rc_scratch/boss_wheel_v2/try_<corp>_<key>.png"""
import os
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bw_kit as K  # noqa: E402
import directions  # noqa: E402
import wheel_v2 as W  # noqa: E402


class _M:
    pass


def get_dir(corp, key):
    D, slots = directions.get(corp, key)
    m = _M()
    m.SLOTS = slots
    return D, m


def main():
    corp, key = sys.argv[1], sys.argv[2]
    S = float(sys.argv[3]) if len(sys.argv) > 3 else 1.2
    kw = dict(forecast=0, gesture=0.0, still=True)
    for a in sys.argv[4:]:
        k, v = a.split("=")
        kw[k] = eval(v)
    D, M = get_dir(corp, key)
    t0 = time.time()
    ctx = W.Ctx(S, t=kw.pop("t", 0.0), phase=kw.pop("phase", 1), hp=kw.pop("hp", 0.9), rot=kw.pop("rot", 0.0), **kw)
    im = W.compose(D, ctx, M.SLOTS)
    bg = K.rgba(im.size, (14, 12, 18), 255)
    bg.alpha_composite(im)
    p = os.path.join(K.SCR, "try_%s_%s.png" % (corp, key))
    bg.convert("RGB").save(p)
    print(p, "%.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
