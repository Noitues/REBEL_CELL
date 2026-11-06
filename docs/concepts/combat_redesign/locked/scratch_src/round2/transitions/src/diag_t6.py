"""diag_t6.py: per-tile luma series of T6 at 25 fps for the worst tiles, with and without the pull-out, to find what flashes."""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fx3lib import *
import fx3 as M
import sbkit as SB
fn = sys.argv[1] if len(sys.argv) > 1 else 't6'
LEN = 0.8 if fn == 't6' else 1.2
times = [round(i / 25, 4) for i in range(int(LEN * 25) + 1)]
seqs = {}
for mode in (os.environ.get('MODES', 'full,nopull').split(',') if fn == 't6' else ('full',)):
    fr = []
    for t in times:
        a = to_pil(getattr(M, fn)(t))
        if fn == 't6' and mode == 'full':
            a = SB.pull_out(a, t)
        fr.append(np.asarray(a.convert('RGB').resize((960, 540), Image.BOX)).astype(np.float32))
    G = np.stack([(f * np.array([.2126, .7152, .0722])).sum(-1) / 255.0 for f in fr])
    n, h, w = G.shape
    Gt = G[:, :h // 60 * 60, :w // 60 * 60].reshape(n, h // 60, 60, w // 60, 60).mean((2, 4))
    d = np.diff(Gt, axis=0)
    big = (np.abs(d) > 0.10 * np.maximum(Gt[1:], Gt[:-1]).clip(0.02)) * np.sign(d)
    cnt = np.zeros(Gt.shape[1:], int)
    for i in range(Gt.shape[1]):
        for j in range(Gt.shape[2]):
            nz = [s for s in big[:, i, j] if s != 0]
            cnt[i, j] = (sum(1 for k in range(1, len(nz)) if nz[k] != nz[k - 1]) + 1) // 2 if nz else 0
    print(mode, 'tiles with >3:', int((cnt > 3).sum()), ' >=3:', int((cnt >= 3).sum()), ' max', int(cnt.max()))
    order = np.dstack(np.unravel_index(np.argsort(-cnt.ravel()), cnt.shape))[0][:6]
    for (i, j) in order:
        print('  tile x%d y%d (1080) pairs %d' % (j * 120, i * 120, cnt[i, j]), ' '.join('%+d' % s for s in big[:, i, j]))
        print('     luma', ' '.join('%.3f' % v for v in Gt[:, i, j]))
    print('  rows (pairs per tile):')
    for i in range(cnt.shape[0]):
        print('   ', ' '.join('%d' % v for v in cnt[i]))
