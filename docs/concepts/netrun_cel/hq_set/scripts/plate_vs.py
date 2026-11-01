"""Usage: python plate_vs.py <plate.png> <hero.png> <out.jpg> : plate | hero side by side (each 960x540) over their squints (1/16 + blur), labelled."""
import sys
from PIL import Image, ImageDraw, ImageFilter
sys.dont_write_bytecode = True
plate = Image.open(sys.argv[1]).convert("RGB").resize((1920, 1080), Image.LANCZOS)
hero = Image.open(sys.argv[2]).convert("RGB").resize((1920, 1080), Image.LANCZOS)


def sq(im):
    return im.resize((120, 68), Image.BOX).filter(ImageFilter.GaussianBlur(0.6)).resize((1920, 1080), Image.BICUBIC)


sheet = Image.new("RGB", (1920, 1080 + 40))
for i, (im, label) in enumerate([(plate, "golden plate hq_rebel_cell_overview"), (hero, "HQ netrun hero (Godot, hq_on)")]):
    sheet.paste(im.resize((960, 540), Image.LANCZOS), (i * 960, 20))
    sheet.paste(sq(im).resize((960, 540), Image.LANCZOS), (i * 960, 20 + 540))
    ImageDraw.Draw(sheet).text((i * 960 + 8, 4), label, fill=(255, 255, 255))
sheet.save(sys.argv[3], quality=90)
print(sys.argv[3])
