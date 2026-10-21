"""Contact sheet 2560 wide: a top strip (Godot now, plate night, plate day) and rows A/B/C x (cel map | AAA-2 night).
python sheet.py <district_dir> <out.jpg>   (reads A_map.png A_night.png B_* C_* from the district dir)"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

D, OUT = sys.argv[1], sys.argv[2]
SC = r"D:\rc_scratch\solace_v1"
W = 2560
CW, CH = W // 2, 720
BAR = 78
BG = (14, 12, 22)
FG = (232, 238, 228)
LIME = (150, 255, 70)
PINK = (255, 70, 150)


def font(sz, bold=False):
    for f in (r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


rows = [
    ("A  CAPSULE GROVE", "plate+: round capsule towers, ribbon windows, domed caps, grow-light interiors, bubble skybridges, greenhouse domes in the greenbelt"),
    ("B  CULTURE CELLS", "buildings as glass-sphere clusters budding off cores, pink nuclei, petri-dish plazas with ring lights"),
    ("C  CLEAN WARD", "porcelain clinic towers, leaf-green glass bands, terraced greenhouses, helix-twisted crowns; pink only as small accents"),
]
STRIP_H = 405
H = 56 + STRIP_H + 40 + len(rows) * (BAR + CH) + 20
sheet = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(sheet)
d.text((24, 8), "SOLACE DISTRICT concept round 1: same lot plan, same helix, same hospital Site; three building kits", font=font(34, True), fill=FG)
# top strip
pw = W // 3
now = Image.open(os.path.join(SC, "now.jpg")).convert("RGB").crop((0, 24, 960, 564))
pn = Image.open(os.path.join(SC, "plate_n_solace.jpg")).convert("RGB")
pd_ = Image.open(os.path.join(SC, "plate_d_solace.jpg")).convert("RGB")
y0 = 56
for k, (im, cap) in enumerate(((now, "Godot today (raid zoom): generic purple boxes, no Solace material"), (pn, "city plate, night (Cycles): green-glass capsule towers round the helix"), (pd_, "city plate, day"))):
    sheet.paste(cover(im, pw - 6, STRIP_H - 34), (k * pw + 3, y0 + 34))
    d.text((k * pw + 10, y0 + 4), cap, font=font(22), fill=LIME if k else PINK)
y = y0 + STRIP_H + 40
for key, (title, sub) in zip("ABC", rows):
    d.rectangle((0, y, W, y + BAR), fill=(24, 20, 36))
    d.text((18, y + 4), title, font=font(32, True), fill=LIME)
    d.text((18 + 420, y + 12), "cel map view: Eevee ortho, raid zoom, 3 toon bands + ink", font=font(22), fill=(190, 190, 215))
    d.text((W // 2 + 18, y + 12), "AAA-2 night hero: Cycles, 1920x1080, volume fog, wet ground", font=font(22), fill=(190, 190, 215))
    d.text((18, y + 44), sub, font=font(22), fill=FG)
    for c, nm in enumerate(("map", "night")):
        p = os.path.join(D, "%s_%s.png" % (key, nm))
        if os.path.exists(p):
            im = Image.open(p).convert("RGB").resize((CW, CH), Image.LANCZOS)
            sheet.paste(im, (c * CW, y + BAR))
    y += BAR + CH
sheet.save(OUT, quality=88)
print("sheet", sheet.size)
