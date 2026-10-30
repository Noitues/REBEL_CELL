"""v2 frame 1 (real r43 capture + real lot polygon highlight), sheets and squints. Usage: python nr_sheet_v2.py  (frames 2-4 must exist in v2/)"""
import json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
D = 'D:/rc_art/art-pass/docs/concepts/netrun_cel/v2/'
G = 'D:/rc_art/art-pass/docs/concepts/golden_plates/'
SRC = 'D:/rc_scratch/netrun_cel/city/nr_plan.png'
LIME = (150, 255, 70); BG = (14, 8, 28)
d = json.load(open('D:/rc_scratch/netrun_cel/city/lots_city.json')); cam = d['camera']
yaw = math.radians(cam['yaw']); pit = math.radians(cam['pitch'])
f = (math.cos(yaw) * math.cos(pit), -math.sin(pit), -math.sin(yaw) * math.cos(pit)); r = (math.sin(yaw), 0, math.cos(yaw))
u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0])
T = cam['target']; O = cam['ortho']; vp = cam['viewport']; LB = cam['lot_bu']; DC = cam['district_centre']
def proj_lot(i, j, y=0.0):
    w = ((i - DC[0]) * LB, y, (j - DC[1]) * LB); dx = [w[k] - T[k] for k in range(3)]
    xc = sum(dx[k] * r[k] for k in range(3)); yc = sum(dx[k] * u[k] for k in range(3)); oh = O * vp[1] / vp[0]
    return ((xc / O + .5) * vp[0], (.5 - yc / oh) * vp[1])

def frame1():
    im = Image.open(SRC).convert('RGB').resize((1920, 1080), Image.LANCZOS)
    # the real lot rectangle of the netrun street block: boulevard lots i -46..-30, j -31..-17 (ground level)
    POLY = [proj_lot(-47, -31, 2), proj_lot(-29, -31, 2), proj_lot(-29, -17, 2), proj_lot(-47, -17, 2)]
    mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).polygon(POLY, fill=255)
    arr = np.asarray(im).astype(np.float32); m = np.asarray(mask).astype(np.float32)[..., None] / 255
    dim = arr * 0.55
    res = arr * m + dim * (1 - m)
    img = Image.fromarray(np.clip(res, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(img, 'RGBA')
    for w, a in ((9, 40), (5, 90), (2, 255)): dr.line(POLY + [POLY[0]], fill=LIME + (a,), width=w, joint='curve')
    for (x, y) in POLY: dr.ellipse((x - 8, y - 8, x + 8, y + 8), outline=LIME + (255,), width=3)
    # the frame-2 zoom rectangle (x3)
    zr = (1330 - 320, 560 - 180, 1330 + 320, 560 + 180); dr.rectangle(zr, outline=(255, 255, 255, 230), width=2)
    fb = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 30); fs = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 20)
    dr.rectangle((40, 40, 700, 132), fill=(10, 4, 24, 215), outline=LIME + (255,), width=2)
    dr.text((56, 50), 'SOLACE  /  NETRUN DISTRICT (placeholder name)', font=fb, fill=LIME)
    dr.text((56, 92), 'real r43 lots  -  white box = frame 2 zoom x3', font=fs, fill=(255, 70, 150))
    dr.line([(700, 86), (POLY[0][0], POLY[0][1])], fill=LIME + (200,), width=2)
    img.save(D + 'frame1_city.png')

F = [D + 'frame1_city.png', D + 'frame2_district.png', D + 'frame3_netrun_street.png', D + 'frame4_solace_hq.png']
CAP = ['1  CITY VIEW  -  real r43 capture, block picked', '2  DISTRICT ZOOM  -  same lots, x3, street detail starts', '3  NETRUN STREET  -  real boulevard, route on the ground', '4  SOLACE HQ NETRUN  -  authored helix set, real avenue + city']
fb = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 26)

def story():
    w, h = 940, 529; g = 20; top = 44
    S = Image.new('RGB', (2 * w + 3 * g, 2 * (h + top) + 3 * g), BG); dd = ImageDraw.Draw(S)
    for i, p in enumerate(F):
        x = g + (i % 2) * (w + g); y = g + (i // 2) * (h + top + g)
        S.paste(Image.open(p).convert('RGB').resize((w, h), Image.LANCZOS), (x, y + top))
        dd.text((x, y + 6), CAP[i], font=fb, fill=LIME); dd.rectangle((x, y + top, x + w, y + top + h), outline=LIME, width=2)
    S.save(D + 'storyboard_sheet.jpg', quality=92)

def refs():
    w, h = 960, 540; top = 40
    S = Image.new('RGB', (2 * w, 2 * (h + top)), BG); dd = ImageDraw.Draw(S)
    rows = [(G + 'street_overview.png', F[2], 'GOLDEN street_overview', 'v2 frame 3 netrun street'), (G + 'hq_rebel_cell_overview.png', F[3], 'GOLDEN hq_rebel_cell_overview', 'v2 frame 4 Solace HQ netrun')]
    for rr, (a, b, ta, tb) in enumerate(rows):
        y = rr * (h + top)
        for c, (p, t) in enumerate(((a, ta), (b, tb))):
            im = Image.open(p).convert('RGB'); im = im.resize((w, h), Image.LANCZOS) if abs(im.width / im.height - 16 / 9) < 0.01 else im.resize((w, int(w * im.height / im.width)), Image.LANCZOS).crop((0, 0, w, h))
            S.paste(im, (c * w, y + top)); dd.text((c * w + 10, y + 6), t, font=fb, fill=LIME if c else (255, 200, 90))
    S.save(D + 'ref_vs_new.jpg', quality=92)

def squint():
    outs = []
    for i, p in enumerate(F):
        im = Image.open(p).convert('RGB'); sm = im.resize((im.width // 16, im.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.2))
        big = sm.resize((960, 540), Image.BICUBIC); big.save(D + 'squint_frame%d.png' % (i + 1)); outs.append(big)
    S = Image.new('RGB', (1920, 1080)); [S.paste(o, ((i % 2) * 960, (i // 2) * 540)) for i, o in enumerate(outs)]
    S.save(D + 'squint_sheet.jpg', quality=90)

if __name__ == '__main__':
    frame1(); story(); refs(); squint(); print('v2 sheets done')
