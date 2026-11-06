import sys, json, copy, time
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/punk_slices/wpap_faceted/src')
import wp_lib as L
import wp_tower as T
import asm_r2 as A
from PIL import Image
ROOT = 'D:/rc_scratch/combat_redesign/punk_slices/wpap_faceted/'
J = json.load(open(ROOT + 'state_e10.json'))
TYPES = ['BURST', 'SHIELD', 'TURRET', 'REPAIR', 'BURST', 'SHIELD']

def state(mode):
    f = copy.deepcopy(J['f1'])
    for i, w in enumerate(f['wheel']):
        w['t'] = TYPES[i]
        if mode == 'ok':
            w['hp_after'] = w['hp'] = w['mx']
        elif mode in ('harm', 'soak'):
            w['hp'] = w['mx']; w['hp_after'] = 0; w['soaked'] = 1 if mode == 'soak' else 0
    return f

if __name__ == '__main__':
    var, mode, S = sys.argv[1], sys.argv[2], int(sys.argv[3])
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    if K > 1:
        import f1_lib
        from PIL import Image as _I
        import numpy as _np
        def _down(s_, K=K):
            P = _I.fromarray(_np.clip(s_.P, 0, 255).astype(_np.uint8), 'RGB'); Al = _I.fromarray(_np.clip(s_.A * 255, 0, 255).astype(_np.uint8), 'L')
            sz = (s_.w * K, s_.h * K)
            P2 = _np.asarray(P.resize(sz, _I.LANCZOS), _np.float32); A2 = _np.asarray(Al.resize(sz, _I.LANCZOS), _np.float32) / 255.0
            rgb = P2 / _np.maximum(A2, 1e-4)[..., None]
            return _I.fromarray(_np.dstack([_np.clip(rgb, 0, 255), A2 * 255]).astype(_np.uint8), 'RGBA')
        f1_lib.Canvas.down = _down
    L.VAR[0] = var
    A.setup()
    t = time.time()
    im, _ = T.render_tower(state(mode), S=S)
    bg = Image.new('RGBA', im.size, (20, 18, 32, 255)); bg.alpha_composite(im)
    bg.convert('RGB').save(ROOT + 'out/tw_%s_%s_%d%s.png' % (var, mode, S, 'k' if K > 1 else ''))
    print('ok', round(time.time() - t, 1))
