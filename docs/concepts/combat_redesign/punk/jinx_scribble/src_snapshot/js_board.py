import sys, os
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import asm_r2 as AA
AA.setup()
import js_cards as JC
ROOT = 'D:/rc_scratch/combat_redesign/punk/jinx_scribble/'
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/jinx_scribble/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
AN = lambda s: ImageFont.truetype(FD + 'Anton-Regular.ttf', s)
MK = lambda s: ImageFont.truetype(FD + 'PermanentMarker-Regular.ttf', s)
MO = lambda s: ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', s)
B = Image.new('RGBA', (1920, 1080), (14, 9, 30, 255))
d = ImageDraw.Draw(B)
CY, PK, CH = (46, 235, 255), (255, 46, 154), (246, 242, 255)
def title(t, x, y, f, col=CH):
    d.text((x + 3, y + 3), t, font=f, fill=PK); d.text((x - 2, y - 1), t, font=f, fill=CY); d.text((x, y), t, font=f, fill=col)
title('JINX SCRIBBLE', 40, 22, AN(64))
d.text((46, 96), 'punk concept  /  player wheel + cards  /  Rebel Cell combat screen', font=MO(18), fill=(190, 180, 230))
# palette
sw = [('NIGHT', '#120A26', (18, 10, 38)), ('VIOLET', '#2A1654', (42, 22, 84)), ('PLUM', '#5A1A6E', (90, 26, 110)), ('NEON PINK  ours', '#FF2E9A', PK), ('PINK HI', '#FF8CCB', (255, 140, 203)), ('NEON CYAN  chalk', '#2EEBFF', CY), ('CHALK', '#F6F2FF', CH), ('INK', '#0A0716', (10, 7, 22))]
for i, (n, h, c) in enumerate(sw):
    x = 40 + (i % 4) * 150; y = 140 + (i // 4) * 96
    d.rectangle([x, y, x + 138, y + 62], fill=c, outline=(240, 240, 255) if i < 3 or i == 7 else None, width=1)
    d.text((x, y + 66), n, font=MO(14), fill=CH); d.text((x, y + 82), h, font=MO(13), fill=(170, 160, 210))
# textures + line samples
ls = Image.open(ROOT + 'work/lines_strip.png').convert('RGBA')
B.alpha_composite(ls.resize((570, 173), Image.LANCZOS), (40, 350))
d.text((40, 528), 'LINE: chalk + marker, plates off the key, doodles, mist, glitch', font=MO(14), fill=(190, 180, 230))
bA = Image.open(ROOT + 'work/big_tower_A.png').convert('RGBA'); bB = Image.open(ROOT + 'work/big_tower_B.png').convert('RGBA')
S = 3
def crop(im, cx, cy, w, h): return im.crop((int(cx * S - w / 2), int(cy * S - h / 2), int(cx * S + w / 2), int(cy * S + h / 2)))
cT = 235
# textures: wall page, wedge A, wedge B
tx = [(crop(bA, cT + 95, cT + 140, 300, 190), 'WALL + MIST'), (crop(bA, cT + 80, cT - 70, 300, 190), 'VIOLET WEDGE'), (crop(bB, cT + 80, cT - 70, 300, 190), 'PINK PAINT')]
for i, (im, n) in enumerate(tx):
    x = 40 + i * 190
    t = im.resize((180, 114), Image.LANCZOS); B.alpha_composite(t, (x, 575)); d.rectangle([x, 575, x + 180, 689], outline=(120, 100, 180))
    d.text((x, 692), n, font=MO(13), fill=(190, 180, 230))
# manifesto
d.text((40, 735), 'MANIFESTO', font=AN(30), fill=CY)
mf = ['1  The corp is clean enamel and glass. We are paint: night wall, neon chalk, marks that do not line up.',
      '2  Every card and slice is signed in the same hand: pink key, cyan plate shifted off it, a doodle in the margin.',
      '3  Grammar stays loud: parallel runs = pending loss, scribbles = ours. Nothing of ours is ever ruled.']
import textwrap
y = 775
for m in mf:
    for ln in textwrap.wrap(m, 40):
        d.text((40, y), ln, font=MK(20), fill=CH); y += 25
    y += 8
# big slice + hub + cards
sA = crop(bA, cT + 70, cT - 60, 560, 400).resize((560, 400), Image.LANCZOS); B.alpha_composite(sA, (620, 140)); d.text((620, 545), 'ONE SLICE (A): painted wedge, scribble loops, plates, glitch icon', font=MO(14), fill=(190, 180, 230))
hA = crop(bA, cT, cT, 300, 300); B.alpha_composite(hA, (1210, 140)); d.text((1210, 445), 'HUB + HP RING (A)', font=MO(14), fill=(190, 180, 230))
hB = crop(bB, cT, cT, 300, 300); B.alpha_composite(hB, (1210, 470)); d.text((1210, 775), 'HUB (B)', font=MO(14), fill=(190, 180, 230))
sB = crop(bB, cT + 70, cT - 60, 560, 400).resize((560, 400), Image.LANCZOS); B.alpha_composite(sB, (620, 580)); d.text((620, 985), 'ONE SLICE (B): hot paint, cyan plate, ink key', font=MO(14), fill=(190, 180, 230))
for i, v in enumerate('AB'):
    JC.V_IS_A[0] = v == 'A'; JC.CUR[0] = v
    c = JC.render_card('Trigger', v, seed=7, ss=4, scale=2)
    c = c.resize((int(c.width * 0.78), int(c.height * 0.78)), Image.LANCZOS)
    B.alpha_composite(c, (1555, 100 + i * 460))
d.text((1555, 1056), 'CARD A / CARD B', font=MO(13), fill=(190, 180, 230))
B.convert('RGB').save(DEL + 'style_board.jpg', quality=92)
print('ok')
