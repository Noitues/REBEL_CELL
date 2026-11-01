"""old_vs_new.jpg (r42 left, r42b right, plus 1:1 feed crops) and squint_<plate>.png like r42 (plate left, 1/16 + blur right)."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
OLD = os.path.join(os.path.dirname(OUT), "supporting_r42")
names = ["01_terminal_event.png", "01b_terminal_event_memo.png", "07_heat_strip_by_page.png"]
sheet = Image.new("RGB", (1920, 1020), (10, 10, 14))
d = ImageDraw.Draw(sheet)
a = Image.open(os.path.join(OLD, names[0])).convert("RGB"); b = Image.open(os.path.join(OUT, names[0])).convert("RGB")
sheet.paste(a.resize((960, 540), Image.LANCZOS), (0, 20)); sheet.paste(b.resize((960, 540), Image.LANCZOS), (960, 20))
d.text((6, 4), "01 terminal event   OLD (r42)  |  NEW (r42b, CAM option A)", fill=(220, 220, 230))
box = (110, 174, 690, 574)
sheet.paste(a.crop(box).resize((650, 448), Image.LANCZOS), (150, 565)); sheet.paste(b.crop(box).resize((650, 448), Image.LANCZOS), (1120, 565))
d.text((150, 552), "feed, old", fill=(220, 220, 230)); d.text((1120, 552), "feed, new", fill=(220, 220, 230))
sheet.save(os.path.join(OUT, "old_vs_new.jpg"), quality=90)
for new in names[:2]:
    im = Image.open(os.path.join(OUT, new)).convert("RGB")
    sq = im.resize((120, 67), Image.BOX).filter(ImageFilter.GaussianBlur(1.2)).resize((960, 540), Image.BICUBIC)
    c = Image.new("RGB", (1920, 540)); c.paste(im.resize((960, 540), Image.LANCZOS), (0, 0)); c.paste(sq, (960, 0))
    c.save(os.path.join(OUT, "squint_" + os.path.splitext(new)[0] + ".png"))
for n in names:
    x = Image.open(os.path.join(OLD, n)).convert("RGB")
    y = Image.open(os.path.join(OUT, n)).convert("RGB")
    print(n, ImageChops.difference(x, y).getbbox())
