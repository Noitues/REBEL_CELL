import sys, time
from stage import *
import importlib


def sheet(fn, frames, box, name, cols=4, tw=480, **kw):
    ims = []
    for f in frames:
        t = time.time()
        a = fn(f, **kw)
        ims.append(crop_scale(a, box, (tw, int(tw * (box[3] - box[1]) / (box[2] - box[0])))))
        print(name, f, round(time.time() - t, 1), flush=True)
    th = ims[0].size[1]
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new('RGB', (tw * cols, th * rows))
    for i, im in enumerate(ims):
        sh.paste(im, ((i % cols) * tw, (i // cols) * th))
    sh.save(WORKD + 'sh_%s.png' % name)


if __name__ == '__main__':
    which = sys.argv[1]
    import beats_a as A
    if which == 'jack':
        sheet(A.b_jack, (0, 2, 4, 6, 8, 10, 14, 18), (0, 0, 1920, 1080), 'jack')
    if which == 'jackr':
        sheet(A.b_jack, (0, 2, 4, 8, 10), (0, 0, 1920, 1080), 'jackr', reduce=True)
    if which == 'jackout':
        sheet(A.b_jack, (0, 1, 2, 3, 4, 6, 8, 10), (0, 0, 1920, 1080), 'jackout', out=True)
    if which == 'draw':
        sheet(A.b_draw, (0, 2, 4, 6, 8, 10, 12, 18), (700, 560, 1920, 1080), 'draw')
    if which == 'dragv':
        sheet(A.b_drag, (0, 3, 6, 10, 14, 20, 24, 30), (200, 300, 1300, 1080), 'dragv', valid=True)
    if which == 'dragi':
        sheet(A.b_drag, (0, 6, 10, 14, 16, 20, 26, 34), (200, 300, 1300, 1080), 'dragi', valid=False)
    import beats_b as B
    if which == 'daemon':
        D = B.dmn(); print('f_arr', D.f_arr, 'v0', D.v0, 's_stop', D.s_stop)
        sheet(B.b_daemon, (0, 30, 34, 44, 56, 68, 80, D.f_arr, D.f_arr + 2, D.f_arr + 6, D.f_arr + 12, D.f_arr + 26), (330, 300, 1290, 840), 'daemon', cols=4, tw=480)
    if which == 'shield':
        sheet(B.b_shield, (-2, 0, 1, 2, 4, 8, 12, 18, 22, 30), (330, 300, 1000, 760), 'shield', cols=5, tw=380)
    if which == 'lock':
        sheet(B.b_lock, (0, 15, 18, 20, 24, 28, 31, 34, 42, 60), (960, 260, 1920, 800), 'lock', cols=5, tw=380)
    if which == 'hunter':
        sheet(B.b_hunter, (0, 8, 14, 18, 22, 25, 30, 40, 70, 74), (700, 250, 1500, 800), 'hunter', cols=5, tw=380)
    if which == 'home':
        sheet(B.b_home, (30, 36, 38, 39, 40, 42, 44, 48, 52, 64), (0, 420, 960, 960), 'home', cols=5, tw=380)
