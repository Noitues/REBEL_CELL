"""style_board.jpg for the linocut concept"""
import sys, json, math, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import asm_r2 as A
A.setup()
import lc_tower as LT
import lc_cards as LC
import f1_tower as FT
from f1_lib import Canvas, font, ANTON_F, pol
from lc_lib import *

ROOT = 'D:/rc_scratch/combat_redesign/punk/linocut/'
J = json.load(open(ROOT + 'state_e10.json'))
PLEX = LC.PLEX
BG = (20, 16, 28)


def tower_S4(v):
    LT.VARIANT[0] = v
    im, cv = FT._orig_tower(J['f1'], S=4) if hasattr(FT, '_orig_tower') else FT.render_tower(J['f1'], S=4)
    big = cv.rgba()
    return print_texture(big, seed=3, dens=0.004, pink_dens=0.002), cv


def crop_at(big, c, half, S=4):
    x, y = c[0] * S, c[1] * S
    return big.crop((int(x - half * S), int(y - half * S), int(x + half * S), int(y + half * S)))


def on_bg(im, col=BG):
    b = Image.new('RGBA', im.size, col + (255,))
    b.alpha_composite(im)
    return b.convert('RGB')


def main():
    t0 = time.time()
    W, H = 2400, 1520
    bd = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(bd)
    fa = lambda px: font(ANTON_F, px)
    fp = lambda px: font(PLEX, px)
    # header
    d.text((50, 30), 'LINOCUT', font=fa(120), fill=KEY)
    d.text((54, 34), 'LINOCUT', font=fa(120), fill=(255, 46, 160))
    d.text((52, 32), 'LINOCUT', font=fa(120), fill=(255, 46, 160))
    d.text((460, 60), 'REBEL CELL combat screen - player wheel, cards, SEND IT, nameplate.  Two blocks, one scissors.', font=fp(34), fill=BONE)
    d.text((460, 118), 'Variant A = black key plate, pink slices.   Variant B = the reverse pull: pink plate, black slices.', font=fp(28), fill=(190, 182, 196))
    man = [('1', 'We cut it ourselves. One carved black key block, one hot-pink pull printed 1.5 px off register. Nothing the corp owns is hand-cut.'),
           ('2', 'Solace is clean lime vectors. The Cell is scissor-cut paper and gouged ink, so owned pieces read in grey and in a squint.'),
           ('3', 'One tool for everything we own: wheel, cards, SEND IT, nameplate and YOU strip. Game colours stay flat and unstyled.')]
    y = 190
    for n, t in man:
        d.text((50, y - 8), n, font=fa(44), fill=(255, 46, 160))
        d.text((100, y), t, font=fp(30), fill=BONE)
        y += 54
    # palette
    px0, py0 = 50, 380
    d.text((px0, py0 - 44), 'PALETTE', font=fa(36), fill=BONE)
    sw = [('HOT PINK  #FF2EA0', HOT, KEY), ('KEY INK  #0D0B11', KEY, BONE), ('BONE PAPER  #F0E9D6', BONE, KEY), ('PINK SHADE  #C4126C', HOT_D, BONE)]
    for i, (nm, c, tc) in enumerate(sw):
        x = px0 + i * 175
        d.rectangle([x, py0, x + 165, py0 + 150], fill=c, outline=(80, 70, 90))
        d.text((x + 8, py0 + 120), nm.split('  ')[0], font=fp(20), fill=tc)
        d.text((x + 8, py0 + 96), nm.split('  ')[1], font=fp(20), fill=tc)
    info = [('RAM', (92, 225, 255)), ('TRACE', (160, 60, 255)), ('HARM', (255, 68, 51)), ('SOAK', (58, 126, 243)), ('HP', (123, 224, 123))]
    d.text((px0, py0 + 170), 'GAME COLOURS (flat, never styled)', font=fp(22), fill=(190, 182, 196))
    for i, (nm, c) in enumerate(info):
        x = px0 + i * 140
        d.rectangle([x, py0 + 205, x + 128, py0 + 250], fill=c)
        d.text((x + 6, py0 + 256), nm, font=fp(20), fill=BONE)
    # textures from the S=4 tower renders
    LT.VARIANT[0] = 'A'
    tA, cvA = tower_S4('A')
    tB, cvB = tower_S4('B')
    print('towers', round(time.time() - t0), flush=True)
    CT = FT.CT
    tx0, ty0 = 800, 380
    d.text((tx0, ty0 - 44), 'TEXTURES', font=fa(36), fill=BONE)
    s_hatch = on_bg(crop_at(tA, pol(CT, 125, 180 + 12), 30)).resize((230, 230), Image.LANCZOS)         # hatching on the shadow side (sector 3)
    s_edge = on_bg(crop_at(tA, pol(CT, 192, 300), 30)).resize((230, 230), Image.LANCZOS)               # scissor-cut halo + plate edge
    s_reg = on_bg(crop_at(tA, pol(CT, 120, 180), 30)).resize((230, 230), Image.LANCZOS)                 # icon with off-register shade
    for i, (im, cap) in enumerate(((s_hatch, 'single-pass gouge hatch'), (s_edge, 'scissor-cut halo, ink grain'), (s_reg, 'off-register second block'))):
        bd.paste(im, (tx0 + i * 245, ty0))
        d.text((tx0 + i * 245, ty0 + 236), cap, font=fp(20), fill=BONE)
    # line samples
    lx0, ly0 = 1600, 380
    d.text((lx0, ly0 - 44), 'LINE SAMPLES', font=fa(36), fill=BONE)
    cvl = Canvas(760, 270, 3, seed=5)
    r = cvl.r
    cvl.over(np.ones((cvl.H, cvl.W), np.float32), KEY, 1.0)
    # gouge lenses (bone on black)
    sp = [(20 + i * 22, 30, 38 + i * 22 + r.uniform(-4, 4), 66, 2.0 + 0.3 * (i % 3), 1.2) for i in range(14)]
    cvl.over(lens_mask(cvl, sp), BONE, 0.95)
    # hatch run (key on pink)
    pink_band = cvl.poly_mask([(340, 14), (740, 14), (740, 90), (340, 90)])
    cvl.over(pink_band, HOT, 1.0)
    hs = [(350 + i * 6.2, 84, 372 + i * 6.2, 24, 1.8, 0.8) for i in range(62)]
    cvl.over(lens_mask(cvl, hs) * pink_band, KEY, 0.97)
    # scissor edge
    pts = jag_path((20, 130), (360, 130), r, (9, 17), 1.6)
    cvl.over(lens_mask(cvl, [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 5.0, 0) for i in range(len(pts) - 1)], 0.3), HOT, 1.0)
    pts = jag_path((20, 150), (360, 150), r, (9, 17), 1.6)
    cvl.over(lens_mask(cvl, [(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 2.4, 0) for i in range(len(pts) - 1)], 0.3), BONE, 1.0)
    # key outline with off-register fill
    shape = cvl.poly_mask(jag_disc((470, 180), 34, r, (8, 13), 1.4))
    cvl.over(np.roll(np.roll(shape, 7, 0), -8, 1), HOT, 1.0)
    cvl.over(np.clip(ndi.binary_dilation(shape > 0.5, iterations=7).astype(np.float32) - shape, 0, 1), BONE, 1.0)
    cvl.over(shape, KEY, 1.0)
    # pending hatch cross (grammar: hatch colour = cause)
    for k, col in enumerate(((255, 68, 51), (58, 126, 243), HOT)):
        x0 = 560 + k * 66
        blk = cvl.poly_mask([(x0, 140), (x0 + 54, 140), (x0 + 54, 220), (x0, 220)])
        cvl.over(blk, (30, 24, 36), 1.0)
        yy, xx = np.mgrid[0:cvl.H, 0:cvl.W].astype(np.float32)
        hx = (((xx + yy) % 15) < 4.5) | (((xx - yy) % 15) < 4.5)
        cvl.over(hx.astype(np.float32) * ndi.binary_erosion(blk > 0.5, iterations=4), col, 1.0)
        cvl.over(np.clip(blk - ndi.binary_erosion(blk > 0.5, iterations=4), 0, 1), col, 1.0)
    li = print_texture(cvl.down(), seed=8)
    bd.paste(on_bg(li), (lx0, ly0))
    d.text((lx0, ly0 + 276), 'gouge | hatch | scissor cut | off-register | pending hatch', font=fp(19), fill=BONE)
    # big slice, hub, card
    ry0 = 740
    d.text((50, ry0 - 46), 'ONE SLICE', font=fa(36), fill=BONE)
    # wedge sector 3 (SHIELD, intact) in A and B
    for i, (big, nm) in enumerate(((tA, 'A'), (tB, 'B'))):
        im = on_bg(crop_at(big, pol(CT, 124, 180), 70))
        bd.paste(im, (50 + i * 580, ry0))
        d.text((50 + i * 580, ry0 + 566), 'slice, variant %s' % nm, font=fp(22), fill=BONE)
    d.text((1230, ry0 - 46), 'THE HUB', font=fa(36), fill=BONE)
    for i, big in enumerate((tA, tB)):
        im = on_bg(crop_at(big, CT, 45)).resize((360, 360), Image.LANCZOS)
        bd.paste(im, (1230, ry0 + i * 380))
    d.text((1230, ry0 + 368), '', font=fp(20), fill=BONE)
    d.text((1650, ry0 - 46), 'ONE CARD', font=fa(36), fill=BONE)
    LT.VARIANT[0] = 'A'
    cvc = LC.card('Spin3', 'A', 4, 4)
    ci = print_texture(LC.down(cvc, 4), seed=9, dens=0.004, pink_dens=0.002)
    ci = ci.crop((int(8 * 4), int(8 * 4), ci.width - 32, ci.height - 32))
    ci = ci.resize((int(ci.width * 0.62), int(ci.height * 0.62)), Image.LANCZOS)
    bg = Image.new('RGBA', ci.size, BG + (255,))
    bg.alpha_composite(ci)
    bd.paste(bg.convert('RGB'), (1650, ry0))
    # small B card beside
    cvc = LC.card('Trigger', 'B', 7, 4)
    cb = print_texture(LC.down(cvc, 4), seed=11, dens=0.004, pink_dens=0.002)
    cb = cb.crop((32, 32, cb.width - 32, cb.height - 32))
    cb = cb.resize((int(cb.width * 0.27), int(cb.height * 0.27)), Image.LANCZOS)
    bg = Image.new('RGBA', cb.size, BG + (255,))
    bg.alpha_composite(cb)
    bd.paste(bg.convert('RGB'), (2170, ry0 + 20))
    d.text((2170, ry0 + 340), 'B', font=fa(30), fill=BONE)
    bd.save(ROOT + 'out/style_board.jpg', quality=92)
    print('ok', round(time.time() - t0))


if __name__ == '__main__':
    main()
