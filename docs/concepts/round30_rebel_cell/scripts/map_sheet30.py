"""Round 30: map deliverables -> ../map_<A|B|C>_<state>.jpg (city-wide, 2560 x 1440), ../map_<v>_<state>_crop.jpg,
../map_options_sheet.jpg (rows A/B/C; columns: city home | city DISPATCH | crop home | crop DISPATCH)."""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)
SC = os.path.join(R, "scratch")
F = "C:/Windows/Fonts/bahnschrift.ttf"
NAMES = {"A": "A  SMALLER RED-WINDOW FIST", "B": "B  RED-TINTED DISTRICT (no light: the buildings' colour draws the fist)",
         "C": "C  RED ROOFTOP BEACONS (aircraft warning lights trace the fist)"}


def font(s):
    return ImageFont.truetype(F, s)


def lab(im, t):
    im = im.copy()
    d = ImageDraw.Draw(im)
    f = font(max(18, im.width // 70))
    d.rectangle([0, 0, d.textlength(t, font=f) + 26, f.size + 16], fill=(10, 9, 16))
    d.text((12, 7), t, font=f, fill=(240, 236, 226))
    return im


cw, ch = 960, 540
cpw, cph = 600, 432
pad, head = 12, 46
W = pad * 5 + cw * 2 + cpw * 2
H = 64 + 3 * (head + ch + pad)
sh = Image.new("RGB", (W, H), (14, 12, 20))
d = ImageDraw.Draw(sh)
d.text((pad, 14), "ROUND 30 - THE CELL ON THE CITY MAP: smaller / subtler options   (city home | city DISPATCH | crop home | crop DISPATCH)",
       font=font(30), fill=(240, 236, 226))
y = 64
for v in "ABC":
    d.rectangle([pad, y, W - pad, y + head - 8], fill=(36, 24, 30))
    d.text((pad + 14, y + 6), NAMES[v], font=font(26), fill=(240, 236, 226))
    y += head
    x = pad
    for st in ("home", "dispatch"):
        full = Image.open(os.path.join(SC, "map30_%s_%s.png" % (v, st))).convert("RGB")
        lab(full.resize((2560, 1440), Image.LANCZOS), "CITY MAP %s - %s" % (v, st.upper())).save(
            os.path.join(R, "map_%s_%s.jpg" % (v, st)), quality=88, optimize=True)
        sh.paste(full.resize((cw, ch), Image.LANCZOS), (x, y))
        x += cw + pad
    for st in ("home", "dispatch"):
        cr = Image.open(os.path.join(SC, "map30_%s_%s_crop.png" % (v, st))).convert("RGB")
        lab(cr, "CROP %s - %s" % (v, st.upper())).save(os.path.join(R, "map_%s_%s_crop.jpg" % (v, st)), quality=88, optimize=True)
        k = max(cpw / cr.width, ch / cr.height)
        r = cr.resize((int(cr.width * k), int(cr.height * k)), Image.LANCZOS)
        ox, oy = (r.width - cpw) // 2, (r.height - ch) // 2
        sh.paste(r.crop((ox, oy, ox + cpw, oy + ch)), (x, y))
        x += cpw + pad
    y += ch + pad
sh.save(os.path.join(R, "map_options_sheet.jpg"), quality=90, optimize=True)
print("sheet", sh.size)
