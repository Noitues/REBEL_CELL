import sys, json, os, re
sys.dont_write_bytecode = True
from PIL import ImageDraw
mode = sys.argv[1]
LOG = []
_orig = ImageDraw.ImageDraw.text
def _t(self, xy, text, *a, **k):
    LOG.append(str(text))
    return _orig(self, xy, text, *a, **k)
ImageDraw.ImageDraw.text = _t
OUT = {}
if mode == 'e10':
    import build10 as B
    os.makedirs('../out/e10_scratch/', exist_ok=True)
    B.OUT = '../out/e10_scratch/'
    from PIL import Image
    B.backdrop = lambda: Image.open('D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/room_bio_bare.png').convert('RGBA')
    _rb = B.render_board
    def rb(*a, **k):
        r = _rb(*a, **k); LOG.clear(); return r
    B.render_board = rb
    for b in ['p1', 'p2', 'p2b', 'p3', 'nowords']:
        LOG.clear(); B.make(b); OUT[b] = list(LOG)
else:
    import asm_r2 as A
    for b in ['p1', 'p2', 'p2b', 'p3', 'nowords']:
        import kscene2; kscene2._cache.clear(); LOG.clear(); A.render(b, check=False); OUT[b] = list(LOG)
json.dump(OUT, open('../out/text_%s.json' % mode, 'w'))
print('done', mode, {k: len(v) for k, v in OUT.items()})
