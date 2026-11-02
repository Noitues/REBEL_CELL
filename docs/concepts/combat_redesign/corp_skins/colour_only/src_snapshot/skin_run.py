"""skin_run.py <corp> [beat] [out]: the linocut plate A with the enemy layers re-skinned by corp_skin tokens"""
import sys, os, re, time
sys.dont_write_bytecode = True
import lc_run
import f1_render as R
import corp_skin as SK

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'f1_render.py'), encoding='utf-8').read()
i = src.index('def _render(')
j = src.index("\nif __name__")
fn = src[i:j]
subs = [
    ("bg.alpha_composite(A.G2.plate('P').convert('RGBA'))", "bg.alpha_composite(SK.plate(A.G2.plate('P').convert('RGBA')))"),
    ("bg.alpha_composite(A.G2.bezel_layer('P').convert('RGBA'))", "bg.alpha_composite(SK.bezel(A.G2.bezel_layer('P').convert('RGBA')))"),
    ("bg.alpha_composite(L.done())", "bg.alpha_composite(SK.layer(L.done(), 'cells'))"),
    ("bg.alpha_composite(La.done())", "bg.alpha_composite(SK.layer(La.done(), 'arcs'))"),
    ("bg.alpha_composite(Llb.done())", "bg.alpha_composite(SK.layer(Llb.done(), 'tickets'))"),
    ("bg.alpha_composite(Lq.done())", "bg.alpha_composite(SK.layer(Lq.done(), 'tickets'))"),
    ("bg.alpha_composite(Ltag.done())", "bg.alpha_composite(SK.layer(Ltag.done(), 'tickets'))"),
]
for a, b in subs:
    assert a in fn, a
    fn = fn.replace(a, b)
R.SK = SK
exec(compile(fn, 'f1_render_skin', 'exec'), R.__dict__)

if __name__ == '__main__':
    corp = sys.argv[1]
    beat = sys.argv[2] if len(sys.argv) > 2 else 'p1'
    out = sys.argv[3] if len(sys.argv) > 3 else 'D:/rc_scratch/corp_skin/colour_only/out/p1_%s.png' % corp
    SK.CORP[0] = corp
    lc_run.setup('A')
    t = time.time()
    im = R.render(beat, check=True) if corp != 'none' else None
    im.save(out)
    print('ok', out, round(time.time() - t))
