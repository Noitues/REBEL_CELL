"""P1 deliverable strips: 2x hot-spot crops, pass-2 | P1 comparisons, squint (320 + blur4), deutan/tritan sims, 1:1 text crops, sheet.jpg.
python p1_post.py"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p1lib as L

OUT = L.OUT
PL = OUT + 'plates/'
P1D = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P1_plates/plates/'
BEATS = [('01', 'plan', '03_plan', (700, 640), 'PLAN'), ('02', 'forecast', '04_forecast', (640, 500), 'FORECAST'), ('03', 'reveal', '12_reveal_sealed_hunter', (1000, 520), 'SEALED / HUNTER REVEAL'),
         ('04', 'impact', '06_playout_impact', (560, 520), 'PLAYOUT IMPACT (SHIELD)'), ('05', 'home_hit', '07_playout_home', (400, 740), 'HOME HIT'),
         ('06', 'aftermath', '08_aftermath', (930, 760), 'AFTERMATH'), ('07', 'city_lost', '10_city_lost', (960, 470), 'CITY LOST')]
DEUT = np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]])
TRIT = np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]])
for d in ('crops2x', 'compare', 'squint', 'colorblind', 'text_1to1'):
    os.makedirs(OUT + d, exist_ok=True)


def lin(a):
    return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)


def unlin(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= .0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - .055)


def sim(im, M):
    a = lin(np.asarray(im.convert('RGB'), np.float32) / 255)
    return Image.fromarray((unlin(a @ M.T) * 255 + .5).astype(np.uint8))


def font(sz):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', sz)
    except Exception:
        return None


def crop_box(c, w, h):
    x0 = int(min(max(c[0] - w // 2, 0), 1920 - w)); y0 = int(min(max(c[1] - h // 2, 0), 1080 - h))
    return (x0, y0, x0 + w, y0 + h)


def main():
    rows = []
    for nn, name, p2, hot, title in BEATS:
        f = PL + '%s_%s.png' % (nn, name)
        if not os.path.exists(f):
            continue
        im = Image.open(f).convert('RGB')
        key = '%s_%s' % (nn, name)
        # 2x hot-spot crop: 960x540 window upscaled 2x
        bx = crop_box(hot, 960, 540)
        f4 = OUT + 'plates4k/%s.png' % key
        if os.path.exists(f4):
            Image.open(f4).convert('RGB').crop(tuple(v * 2 for v in bx)).save(OUT + 'crops2x/%s_hot2x.png' % key)     # TRUE 2x: rendered at 3840x2160, not upscaled
        else:
            im.crop(bx).resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 50, 2)).save(OUT + 'crops2x/%s_hot2x.png' % key)
        # pass-2 | P1
        if os.path.exists(P1D + key + '.png'):
            a = Image.open(P1D + key + '.png').convert('RGB').resize((960, 540), Image.LANCZOS)
            b = im.resize((960, 540), Image.LANCZOS)
            sh = Image.new('RGB', (1920, 570), (8, 6, 20))
            sh.paste(a, (0, 30)); sh.paste(b, (960, 30))
            d = ImageDraw.Draw(sh)
            d.text((8, 6), 'P1 - ' + title, fill=(160, 170, 200), font=font(18))
            d.text((968, 6), 'P2 golden plate - ' + title, fill=(127, 239, 255), font=font(18))
            sh.save(OUT + 'compare/%s_P1_vs_P2.jpg' % key, quality=92)
        # squint
        im.resize((320, 180), Image.LANCZOS).save(OUT + 'squint/%s_320.png' % key)
        im.filter(ImageFilter.GaussianBlur(4)).save(OUT + 'squint/%s_blur4.png' % key)
        # colour-blind sims
        sim(im, DEUT).save(OUT + 'colorblind/%s_deutan.png' % key)
        sim(im, TRIT).save(OUT + 'colorblind/%s_tritan.png' % key)
        # 1:1 text crops (HUD + the beat's main glyph/type)
        im.crop((0, 0, 440, 90)).save(OUT + 'text_1to1/%s_hud_left.png' % key)
        im.crop((1560, 0, 1920, 90)).save(OUT + 'text_1to1/%s_hud_right.png' % key)
        bx2 = crop_box(hot, 480, 270)
        im.crop(bx2).save(OUT + 'text_1to1/%s_hot_1to1.png' % key)
        rows.append((key, title, im))
    # squint strip (all beats at 320, then blur4) + sims strip
    if rows:
        n = len(rows)
        strip = Image.new('RGB', (n * 330 + 10, 2 * 200 + 10), (8, 6, 20))
        for i, (key, title, im) in enumerate(rows):
            strip.paste(im.resize((320, 180), Image.LANCZOS), (10 + i * 330, 10))
            strip.paste(im.filter(ImageFilter.GaussianBlur(4)).resize((320, 180), Image.LANCZOS), (10 + i * 330, 210))
        strip.save(OUT + 'squint/ALL_strip_320_and_blur4.png')
        sims = Image.new('RGB', (n * 330 + 10, 3 * 200 + 10), (8, 6, 20))
        for i, (key, title, im) in enumerate(rows):
            for j, im2 in enumerate((im, sim(im, DEUT), sim(im, TRIT))):
                sims.paste(im2.resize((320, 180), Image.LANCZOS), (10 + i * 330, 10 + j * 200))
        sims.save(OUT + 'colorblind/ALL_normal_deutan_tritan.png')
        # sheet.jpg
        cols, tw, th = 2, 940, 529
        rws = (n + cols - 1) // cols
        sheet = Image.new('RGB', (cols * (tw + 10) + 10, rws * (th + 32) + 10), (8, 6, 20))
        d = ImageDraw.Draw(sheet)
        for i, (key, title, im) in enumerate(rows):
            r, c = divmod(i, cols)
            x = 10 + c * (tw + 10); y = 10 + r * (th + 32)
            sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 24))
            d.text((x, y + 2), key + '  ' + title, fill=(127, 239, 255), font=font(18))
        sheet.save(OUT + 'sheet.jpg', quality=90)
    print('post done', len(rows))


def tier_strip():
    """greyscale 320 px tier strip: the tiers plate at 320 px grey + the five tier marks (ring + tile) cropped from the 320 px image, enlarged x6 (nearest)."""
    f = PL + 'T0_tiers.png'
    if not os.path.exists(f):
        return
    import p1lib as L_
    w = L_.load_world()
    im = Image.open(f).convert('RGB')
    g320 = im.resize((320, 180), Image.LANCZOS).convert('L')
    tiers = [('t1_a', 'UNTOUCHED'), ('t1_b', 'HOLDS'), ('t1_c', 'SITES LOST'), ('t1_d', 'DAMAGED'), ('t2_breach', 'BREACHED')]
    out = Image.new('RGB', (5 * 252 + 12, 700), (8, 6, 20))
    out.paste(g320.resize((640, 360), Image.NEAREST).convert('RGB'), (6, 6))
    d = ImageDraw.Draw(out)
    d.text((660, 20), 'tiers plate, greyscale, 320 px (left, x2)', fill=(160, 170, 200), font=font(16))
    y0 = 380
    for i, (sid, name) in enumerate(tiers):
        b = w.sites[sid]['B'] / 6.0
        cx, cy = b[0], b[1] - 14
        box = (int(cx - 19), int(cy - 20), int(cx + 19), int(cy + 20))
        c = g320.crop(box).resize((228, 240), Image.NEAREST).convert('RGB')
        out.paste(c, (6 + i * 252, y0))
        d.text((10 + i * 252, y0 + 244), name, fill=(127, 239, 255), font=font(16))
    out = out.crop((0, 0, out.width, y0 + 272))
    out.save(OUT + 'tier_strip_gray_320.png')
    # all seven plates in greyscale at 320
    rows = []
    for nn, name, p2, hot, title in BEATS:
        f2 = PL + '%s_%s.png' % (nn, name)
        if os.path.exists(f2):
            rows.append(Image.open(f2).convert('RGB').resize((320, 180), Image.LANCZOS).convert('L').convert('RGB'))
    if rows:
        st = Image.new('RGB', (len(rows) * 326 + 6, 192), (8, 6, 20))
        for i, r in enumerate(rows):
            st.paste(r, (6 + i * 326, 6))
        st.save(OUT + 'squint/ALL_gray_320.png')


if __name__ == '__main__':
    main()
    tier_strip()
