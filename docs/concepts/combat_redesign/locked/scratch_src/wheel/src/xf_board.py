"""xf_board: the style board (1920x1080) for the XEROX FLYER concept."""
import sys, math, os
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import xf_tower as XT
from xf_gfx import *

OUT = 'D:/rc_scratch/combat_redesign/locked/wheel/out/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
BGC = (21, 18, 28)
im = Image.new('RGB', (1920, 1080), BGC)
d = ImageDraw.Draw(im)


def F(n, px):
    return ImageFont.truetype(FD + n, px)


def tile(cv):
    return cv.to_image()


def paste(img, xy):
    im.paste(img.convert('RGB') if img.mode != 'RGBA' else img, xy, img if img.mode == 'RGBA' else None)


# ---- title
t = Image.new('RGBA', (900, 150), (0, 0, 0, 0))
cv = Cv(0, 0, 900, 150, 3)
xtext(cv, 'XEROX FLYER', 330, 78, 126, ANTON, fill=hx('FBFAF4'), off=(5, 5), off_col=MAG, off2=(-4, 4), off2_col=CYN, wob=0.3, seed=2, grain=0.0, track=2)
paste(cv.to_image(), (50, 20))
d.text((58, 172), 'PLAYER WHEEL + HAND  /  PUNK ROCK CONCEPT  /  A + B', font=F('ShareTechMono-Regular.ttf', 24), fill=(18, 169, 230))

# ---- manifesto
man = [
    ('1', 'THE CORP PRINTS IN CLEAN GLASS. THE CELL STEALS THE COPIER.'),
    ('2', 'BLACK TONER, THREE SPOT INKS, ALL SLAPPED ON CROOKED.'),
    ('3', 'IF IT IS HALFTONED AND OFF-REGISTER, IT IS OURS.'),
]
y = 222
for n, s in man:
    d.rectangle([54, y + 2, 84, y + 32], fill=(255, 61, 168))
    d.text((69, y + 17), n, font=F('Anton-Regular.ttf', 26), fill=(21, 18, 26), anchor='mm')
    d.text((100, y + 17), s, font=F('IBMPlexSansCondensed-Medium.ttf', 25), fill=(242, 238, 228), anchor='lm')
    y += 42

# ---- palette
d.text((54, 372), 'PALETTE', font=F('Anton-Regular.ttf', 26), fill=(251, 250, 244))
sw = [('TONER', (21, 18, 26), 'key, ground'), ('SHEET', (242, 238, 228), 'paper'), ('MAGENTA', (255, 61, 168), 'ours'),
      ('CYAN', (18, 169, 230), 'misprint only'), ('HARM', (255, 68, 51), 'enemy hatch'), ('GAIN', (123, 224, 123), 'your HP'), ('SOAK', (58, 126, 243), 'soak hatch')]
x = 54
for nm, c, note in sw:
    d.rectangle([x, 410, x + 96, 490], fill=c, outline=(251, 250, 244) if nm == 'TONER' else None, width=2)
    d.text((x, 498), nm, font=F('ShareTechMono-Regular.ttf', 17), fill=(251, 250, 244))
    d.text((x, 518), note, font=F('ShareTechMono-Regular.ttf', 13), fill=(160, 170, 190))
    x += 104

# ---- textures
d.text((54, 556), 'TEXTURE', font=F('Anton-Regular.ttf', 26), fill=(251, 250, 244))
cv = Cv(0, 0, 720, 150, 3)
cv.paint(np.ones((cv.H, cv.W), np.float32), SHEET * 0.82)
# 1 halftone ramp
cov = ramp(cv, (10, 0), (170, 0), 0.0, 0.95)
ht = halftone(cov * (cv.grid()[0] < 180) * (cv.grid()[1] > 12) * (cv.grid()[1] < 138), 7.0 * 3, 45, 0, 0, aa=3)
cv.paint(ht, TONER)
# 2 off-register
X, Y = cv.grid()
blk = ((X > 205) & (X < 335) & (Y > 18) & (Y < 132)).astype(np.float32)
cv.paint(plate_shift(blk, cv, -6, 5), CYN)
ink(cv, plate_shift(blk, cv, 4, -3), MAG, 0.07, 4)
key = np.clip(grow(blk, 3 * 3) - blk, 0, 1)
cv.paint(key, TONER)
xtext(cv, 'OFF', 270, 56, 44, ANTON, fill=TONER, off=(3, 3), off_col=MAG, wob=0.1, grain=0)
xtext(cv, 'REG', 270, 100, 44, ANTON, fill=hx('FBFAF4'), off=(3, 3), off_col=TONER, wob=0.1, grain=0)
# 3 dropout / grain
blk2 = ((X > 365) & (X < 495) & (Y > 18) & (Y < 132)).astype(np.float32)
ink(cv, blk2, TONER, 0.38, 9)
sp = toner_noise(cv, 5, 0.9, 0.9)
cv.paint(blur(sp, 0.3 * 3) * blk2, SHEET, 0.5)
ink(cv, ((X > 395) & (X < 465) & (Y > 45) & (Y < 105)).astype(np.float32), MAG, 0.25, 12)
# 4 copier-lid edge
pg = ((X > 530) & (X < 700) & (Y > 18) & (Y < 132)).astype(np.float32)
cl = copier_edge(cv, rough(pg, cv, 1.2, 6, 3), 4, 9, 0.95, (0.8, 0.8))
cv.paint(rough(pg, cv, 1.2, 6, 3) * 0.0, TONER)
cv.paint(cl, TONER)
cv.paint(halftone(np.clip((X - 560) / 120, 0, 1) * 0.0 + 0.0, 21, 45), TONER, 0)
paste(cv.to_image(), (54, 596))
for nm, xx in (('HALFTONE', 54), ('OFF-REGISTER', 54 + 205), ('TONER DROPOUT', 54 + 365), ('COPIER LID', 54 + 530)):
    d.text((xx, 752), nm, font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))

# ---- line samples
d.text((54, 782), 'LINE', font=F('Anton-Regular.ttf', 26), fill=(251, 250, 244))
cv = Cv(0, 0, 720, 130, 3)
cv.paint(np.ones((cv.H, cv.W), np.float32), SHEET * 0.82)
X, Y = cv.grid()
# key stroke with off-register colour
s1 = rough(((abs(Y - 36) < 4.5) & (X > 14) & (X < 180)).astype(np.float32), cv, 1.0, 5, 2)
cv.paint(plate_shift(s1, cv, 1.8, -1.6), MAG)
cv.paint(s1, TONER)
# double rule (protect)
for yy in (78, 87):
    cv.paint(rough(((abs(Y - yy) < 2.2) & (X > 14) & (X < 180)).astype(np.float32), cv, 0.6, 5, 3), TONER)
# hatch
reg = ((X > 215) & (X < 330) & (Y > 16) & (Y < 112)).astype(np.float32)
cv.paint(reg, hx('120E16'))
cv.paint(hatch_field(cv, (45, 135), 6, 1.7, 7) * reg, HARMC)
cv.paint(np.clip(reg - shrink(reg, 2.4 * 3), 0, 1), HARMC)
# stencil X + reg mark + burst
xm = np.zeros((cv.H, cv.W), np.float32)
for sg in (1, -1):
    xm = np.maximum(xm, poly(cv, [(380 - 20, 64 - sg * 20 - 5), (380 - 20, 64 - sg * 20 + 5), (380 + 20, 64 + sg * 20 + 5), (380 + 20, 64 + sg * 20 - 5)]))
cv.paint(plate_shift(xm, cv, 3, 3), MAG)
ink(cv, xm, TONER, 0.02, 3)
XT.reg_mark(cv, (470, 64), 14, col=TONER)
bs = starburst_mask(cv, (590, 64), 46, 20, 9, 3, 10)
cv.paint(grow(bs, 2.4 * 3), TONER)
ink(cv, bs, hx('FBFAF4'), 0.02, 4)
cv.paint(circle(cv, 592, 66, 13), MAG)
paste(cv.to_image(), (54, 822))
for nm, xx in (('KEY = OURS', 54), ('DOUBLE RULE = PROTECT', 54 + 0), ):
    pass
for nm, xx, yy in (('KEY STROKE = OURS', 54, 958), ('TWO RULES = PROTECT', 54, 976), ('HATCH = LOST', 54 + 215, 958), ('AT END TURN', 54 + 215, 976), ('X = SLICE LOST', 54 + 345, 958), ('REG MARK', 54 + 470, 958), ('BURST = OUR HIT', 54 + 560, 958)):
    d.text((xx, yy), nm, font=F('ShareTechMono-Regular.ttf', 13), fill=(160, 170, 190))

# ---- big pieces (right side)
bigA = Image.open(OUT + 'big_tower_A.png').convert('RGBA')
bigB = Image.open(OUT + 'big_tower_B.png').convert('RGBA')
cA = Image.open(OUT + 'big_card_A_Trigger.png').convert('RGBA')
cB = Image.open(OUT + 'big_card_B_Trigger.png').convert('RGBA')
panel = Image.new('RGBA', (1080, 1080), (0, 0, 0, 0))
# cards
cA2 = cA.resize((int(cA.width * 1.12), int(cA.height * 1.12)), Image.LANCZOS)
cB2 = cB.resize((int(cB.width * 1.12), int(cB.height * 1.12)), Image.LANCZOS)
im.paste(cA2, (830, 30), cA2)
im.paste(cB2, (830 + cA2.width - 20, 30), cB2)
d.text((870, 650), 'CARD A: WHITE SHEET', font=F('ShareTechMono-Regular.ttf', 15), fill=(160, 170, 190))
d.text((1340, 650), 'CARD B: BLACK TONER', font=F('ShareTechMono-Regular.ttf', 15), fill=(160, 170, 190))
sl = bigA.crop((260, 90, 680, 420)).resize((525, 412), Image.LANCZOS)
bg = Image.new('RGBA', sl.size, BGC + (255,))
bg.alpha_composite(sl)
im.paste(bg.convert('RGB'), (850, 672))
d.text((852, 1086 - 20 - 0), '', font=F('ShareTechMono-Regular.ttf', 15), fill=(160, 170, 190))
for k, big in enumerate((bigA, bigB)):
    h = big.crop((330, 330, 610, 610)).resize((250, 250), Image.LANCZOS)
    bg = Image.new('RGBA', h.size, BGC + (255,))
    bg.alpha_composite(h)
    im.paste(bg.convert('RGB'), (1420 + k * 260, 690))
d.text((1420, 950), 'HUB A: RANSOM TILES ON BLACK', font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))
d.text((1680, 950), 'HUB B: ON A WHITE DISC', font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))
d.text((852, 1090 - 14), '', font=F('ShareTechMono-Regular.ttf', 12), fill=(160, 170, 190))
d.text((1420, 985), 'ONE SLICE (A, LEFT): FLAT MAGENTA, BLACK KEY, HALFTONE SHADE.', font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))
d.text((1420, 1008), 'EVERY LETTER OF THE CELL IS CUT FROM A DIFFERENT SCRAP.', font=F('ShareTechMono-Regular.ttf', 14), fill=(160, 170, 190))
im.save(OUT + '../style_board_draft.png')
im.save('D:/rc_scratch/combat_redesign/locked/wheel/out/style_board.png')
print('board ok')
