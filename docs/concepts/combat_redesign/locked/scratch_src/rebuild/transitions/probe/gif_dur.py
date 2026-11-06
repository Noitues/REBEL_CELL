"""gif_dur.py: per-frame durations of the published GIFs."""
from PIL import Image, ImageSequence
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/transitions/'
for g in ('t5_A.gif', 't6_A.gif'):
    d = [f.info.get('duration') for f in ImageSequence.Iterator(Image.open(D + g))]
    print(g, d, sum(d))
