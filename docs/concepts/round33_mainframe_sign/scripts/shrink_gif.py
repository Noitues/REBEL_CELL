"""Re-encode GIFs (next to NOTES.md) with a 96-colour palette taken across the sequence, to stay under 3 MB.
Usage: python shrink_gif.py <name.gif> [...]"""
import os
import sys
from PIL import Image, ImageSequence
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for name in sys.argv[1:]:
    p = os.path.join(D, name)
    im = Image.open(p)
    fr, du = [], []
    for f in ImageSequence.Iterator(im):
        fr.append(f.convert('RGB'))
        du.append(f.info.get('duration', 83))
    picks = fr[::max(1, len(fr) // 12)]
    mont = Image.new('RGB', (picks[0].width * len(picks), picks[0].height))
    for i, f in enumerate(picks):
        mont.paste(f, (i * f.width, 0))
    pal = mont.quantize(colors=96, method=Image.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in fr]
    q[0].save(p, save_all=True, append_images=q[1:], duration=du, loop=0, optimize=True, disposal=1)
    print(name, round(os.path.getsize(p) / 1e6, 2), 'MB')
