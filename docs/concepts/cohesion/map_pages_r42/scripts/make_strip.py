"""grade_strengths.jpg: hq_idle at the three grade strengths, side by side (960 wide each)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import r42lib as R
names = ["light", "mid", "strong"]
w, h = 960, 540
sheet = Image.new("RGB", (w * 3, h + 44), (10, 10, 14))
f = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
d = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    im = Image.open(os.path.join(OUT, "scratch", "hq_idle_%s.png" % n)).resize((w, h), Image.LANCZOS)
    sheet.paste(im, (i * w, 44))
    vo, vi, sb, sn = R.GRADES[n]
    d.text((i * w + 12, 10), "%s   value x%.2f out / x%.2f in   sat pull %.2f bldg / %.2f neon" % (n.upper(), vo, vi, sb, sn), font=f, fill=(230, 235, 240))
sheet.save(os.path.join(OUT, "grade_strengths.jpg"), quality=90)
print("ok")
