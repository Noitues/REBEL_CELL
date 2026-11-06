import json, sys
from PIL import Image, ImageDraw
rows = json.load(open(sys.argv[1]))
img = Image.open(sys.argv[2]).convert("RGBA")
cols = {0:(120,120,120), 1:(60,110,255), 2:(255,150,40), 3:(255,40,190), 4:(40,230,215), 5:(160,110,255), 6:(235,240,255), 7:(0,0,0), 8:(255,255,255)}
names = {1:"cool dark",2:"warm amber",3:"neon magenta",4:"teal glass",5:"violet mid",6:"pale cold",7:"dark gap",8:"white tower"}
ov = Image.new("RGBA", img.size, (0,0,0,0))
d = ImageDraw.Draw(ov)
from collections import Counter
print(Counter(r[6] for r in rows))
for r in rows:
    t,h,x,y,yb,k,a = r
    c = cols[a]
    rad = 9 if a == 8 else 4
    d.ellipse((x-rad, y-rad, x+rad, y+rad), fill=c+(210,), outline=(0,0,0,255) if a in (7,) else None)
out = Image.alpha_composite(img, ov).convert("RGB")
d2 = ImageDraw.Draw(out)
y = 10
for k, n in names.items():
    d2.rectangle((10, y, 24, y+14), fill=cols[k], outline=(255,255,255)); d2.text((30, y), n, fill=(255,255,255)); y += 18
out.save(sys.argv[3])
