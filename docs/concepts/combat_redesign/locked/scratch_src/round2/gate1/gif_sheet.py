"""gate1: contact sheets of every frame of a GIF (frame index printed on each).  usage: gif_sheet.py <gif> <out_prefix> <cols> <thumb_w> [per_sheet]"""
import sys
from PIL import Image, ImageSequence, ImageDraw
g = Image.open(sys.argv[1])
pre, cols, tw = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
per = int(sys.argv[5]) if len(sys.argv) > 5 else 60
frames = [fr.convert('RGB').copy() for fr in ImageSequence.Iterator(g)]
durs = [fr.info.get('duration') for fr in ImageSequence.Iterator(Image.open(sys.argv[1]))]
w, h = frames[0].size
th = int(h * tw / w)
print('frames', len(frames), 'size', (w, h), 'total ms', sum(d or 0 for d in durs), 'durations set', sorted(set(durs)))
for s in range(0, len(frames), per):
    chunk = frames[s:s + per]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * (th + 14)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, fr in enumerate(chunk):
        x = (i % cols) * tw; y = (i // cols) * (th + 14)
        sheet.paste(fr.resize((tw, th)), (x, y + 14))
        d.text((x + 2, y + 1), '%d' % (s + i), fill=(255, 255, 0))
    out = '%s_%02d.png' % (pre, s // per)
    sheet.save(out)
    print(out, sheet.size)
