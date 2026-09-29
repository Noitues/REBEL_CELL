"""Dumps chosen frames of one variant as full-size PNGs, for review.
  python bd_debug_frames.py <backdrop.png> <variant> <outdir> f1 f2 ...
"""
import os, sys
sys.argv, args = sys.argv[:2], sys.argv[2:]
import bd_render as R

name, outdir, fr = args[0], args[1], [int(x) for x in args[2:]]
base = R.make_backdrop().convert("RGBA"); R.draw_spinner(base); base = base.convert("RGB")
seed = 1000 + list(R.VARIANTS).index(name)
v = R.VARIANTS[name](R.random.Random(seed))
for f in fr:
    R.render_frame(base, v, f).save(os.path.join(outdir, "%s_f%02d.png" % (name, f)))
