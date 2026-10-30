"""Sheets and squint images. Usage: python nr_sheet.py  (reads frames from netrun_cel/)"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = 'D:/rc_art/art-pass/docs/concepts/netrun_cel/'
G = 'D:/rc_art/art-pass/docs/concepts/golden_plates/'
F = [D + 'frame1_city.png', D + 'frame2_district.png', D + 'frame3_netrun_street.png', D + 'frame4_solace_hq.png']
CAP = ['1  CITY VIEW  -  district picked', '2  DISTRICT ZOOM  -  rims + first street detail', '3  NETRUN STREET  -  playable, route on the ground', '4  SOLACE HQ NETRUN  -  helix + park at street level']
fb = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 26)
LIME = (150, 255, 70)
BG = (14, 8, 28)

def story():
    w, h = 940, 529; g = 20; top = 44
    S = Image.new('RGB', (2 * w + 3 * g, 2 * (h + top) + 3 * g), BG)
    d = ImageDraw.Draw(S)
    for i, p in enumerate(F):
        x = g + (i % 2) * (w + g); y = g + (i // 2) * (h + top + g)
        S.paste(Image.open(p).convert('RGB').resize((w, h), Image.LANCZOS), (x, y + top))
        d.text((x, y + 6), CAP[i], font=fb, fill=LIME)
        d.rectangle((x, y + top, x + w, y + top + h), outline=(150, 255, 70), width=2)
    # zoom arrows
    d.polygon([(2 * g + w - 6, g + top + h // 2 - 16), (2 * g + w + 14, g + top + h // 2), (2 * g + w - 6, g + top + h // 2 + 16)], fill=(255, 70, 150))
    y2 = g + (h + top + g) + top + h // 2
    d.polygon([(2 * g + w - 6, y2 - 16), (2 * g + w + 14, y2), (2 * g + w - 6, y2 + 16)], fill=(255, 70, 150))
    S.save(D + 'storyboard_sheet.jpg', quality=92)

def refs():
    w, h = 960, 540; top = 40
    S = Image.new('RGB', (2 * w, 2 * (h + top)), BG); d = ImageDraw.Draw(S)
    rows = [(G + 'street_overview.png', F[2], 'GOLDEN street_overview', 'NEW frame 3 netrun street'), (G + 'hq_rebel_cell_overview.png', F[3], 'GOLDEN hq_rebel_cell_overview', 'NEW frame 4 Solace HQ netrun')]
    for r, (a, b, ta, tb) in enumerate(rows):
        y = r * (h + top)
        for c, (p, t) in enumerate(((a, ta), (b, tb))):
            im = Image.open(p).convert('RGB'); im = im.resize((w, h), Image.LANCZOS) if abs(im.width / im.height - 16 / 9) < 0.01 else im.resize((w, int(w * im.height / im.width)), Image.LANCZOS).crop((0, 0, w, h))
            S.paste(im, (c * w, y + top)); d.text((c * w + 10, y + 6), t, font=fb, fill=LIME if c else (255, 200, 90))
    S.save(D + 'ref_vs_new.jpg', quality=92)

def squint():
    outs = []
    for i, p in enumerate(F):
        im = Image.open(p).convert('RGB'); sm = im.resize((im.width // 16, im.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.2))
        big = sm.resize((960, 540), Image.BICUBIC); big.save(D + 'squint_frame%d.png' % (i + 1)); outs.append(big)
    S = Image.new('RGB', (1920, 1080)); [S.paste(o, ((i % 2) * 960, (i // 2) * 540)) for i, o in enumerate(outs)]
    S.save(D + 'squint_sheet.jpg', quality=90)

if __name__ == '__main__':
    story(); refs(); squint(); print('sheets done')
