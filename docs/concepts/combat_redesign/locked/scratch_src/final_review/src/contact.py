"""Contact sheet: tile N images at a fixed tile width, with filename labels.
Usage: python contact.py <out.jpg> <tile_w> <cols> img1 img2 ..."""
import sys, os
from PIL import Image, ImageDraw

def main():
    out, tw, cols = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    ims = sys.argv[4:]
    tiles = []
    for p in ims:
        im = Image.open(p).convert('RGB')
        h = round(im.height * tw / im.width)
        tiles.append((os.path.basename(p), im.resize((tw, h), Image.LANCZOS)))
    th = max(t[1].height for t in tiles) + 22
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * th), (16, 16, 22))
    d = ImageDraw.Draw(sheet)
    for i, (n, t) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(t, (x, y + 22))
        d.text((x + 6, y + 4), n, fill=(255, 226, 0))
    sheet.save(out, quality=90)
    print(out, sheet.size)

if __name__ == '__main__':
    main()
