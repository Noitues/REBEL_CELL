import sys, json
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont
OUT = 'D:/rc_scratch/combat_redesign/punk/card_titles/out/'
F = lambda s: ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', s)
opts = [('orig', 'F1 ORIGINAL  pink fill, chrome rim, pink drop (the hard-to-read one)'),
        ('A', 'A  BLACK MARKER TAG, white keyline, pink offset print'),
        ('B', 'B  WHITE CHISEL, black outline + hard black drop'),
        ('C', 'C  HIGHLIGHTER YELLOW, black outline + hard drop'),
        ('D', 'D  CREAM ON BLACK TAPE STRIP')]
order = ['A', 'B', 'C', 'D']
ims = {k: Image.open(OUT + 'hand2x_%s.png' % k).convert('RGB') for k, _ in opts}
W, H = ims['A'].size
BG = (18, 14, 26)
sh = Image.new('RGB', (W * 2 + 30, 60 + (H + 44) * 3 + 20 + 560), BG)
d = ImageDraw.Draw(sh)
d.text((16, 14), 'CARD TITLE LEGIBILITY: 4-card hand at 2x on the real combat backdrop (rows: orig | A B | C D), then 1x and 320 px', font=F(30), fill=(240, 236, 224))
y = 60
def put(k, x, y):
    d.text((x + 8, y + 6), dict(opts)[k], font=F(24), fill=(255, 230, 40))
    sh.paste(ims[k], (x, y + 40))
put('orig', 0, y); 
# beside the original: the legibility rules
d.rectangle([W + 30, y + 40, W * 2 + 30, y + 40 + H], fill=(30, 24, 42))
rules = ['LEGIBILITY RULES (see LAYOUT.md)', '',
         'cap height >= 30 px at 1920x1080 (26 px in card design units)',
         'letter fill vs its edge >= 7:1 (WCAG luminance)',
         'edge vs card paper / art band >= 4.5:1 on BOTH',
         'one keyline, hard, 2.5-3.2 px; no chrome, no rim glow',
         'drop = hard offset (3-4 px), never a blur',
         'title is NOT the owner colour: pink belongs to the icon',
         'yellow is reserved for plan marks: not a title fill',
         '<= 7 letters at full 42 px; longer names shrink, never',
         '  below 30 px cap; track +0.8 .. +1.2 px',
         'title zone y 119-163 of 250, x 14-162 of 176']
for i, t in enumerate(rules):
    d.text((W + 60, y + 70 + i * 52), t, font=F(30 if i == 0 else 27), fill=(255, 230, 40) if i == 0 else (235, 232, 224))
y += H + 44
for r in range(2):
    a, b = order[r * 2], order[r * 2 + 1]
    put(a, 0, y); put(b, W + 30, y)
    y += H + 44
# 1x and 320 rows
d.text((16, y + 4), 'LEGIBILITY CHECK: each option at 1x (1920x1080 pixels) and at 320 px wide (the whole hand strip shrunk to 320)', font=F(28), fill=(240, 236, 224))
y += 44
cw = (W * 2 + 30) // 4
for i, k in enumerate(['orig'] + order[:3]):
    pass
cols = ['orig', 'A', 'B', 'C', 'D']
cw = (W * 2 + 30) // 5
for i, k in enumerate(cols):
    x = i * cw
    d.text((x + 8, y), k.upper(), font=F(26), fill=(255, 230, 40))
    one = ims[k].resize((W // 2, H // 2), Image.LANCZOS)
    one = one.resize((cw - 16, int(one.height * (cw - 16) / one.width)), Image.LANCZOS) if one.width > cw - 16 else one
    sh.paste(one, (x + 8, y + 34))
    s320 = ims[k].resize((320, int(H * 320 / W)), Image.LANCZOS)
    sh.paste(s320, (x + 8, y + 34 + one.height + 12))
    d.text((x + 8, y + 34 + one.height + 12 + s320.height + 2), '1x (shown scaled to fit)  /  320 px actual', font=F(18), fill=(160, 156, 170))
sh = sh.crop((0, 0, sh.width, y + 34 + 330 + 12 + 130 + 40))
sh.save(OUT + 'sheet.jpg', quality=90)
print(sh.size)
# true 1x + 320 legibility strip
rows = []
for k in cols:
    one = ims[k].resize((W // 2, H // 2), Image.LANCZOS)
    rows.append((k, one))
oh = rows[0][1].height
L = Image.new('RGB', (W // 2 + 340, (oh + 30) * 5), BG)
dl = ImageDraw.Draw(L)
for i, (k, one) in enumerate(rows):
    yy = i * (oh + 30)
    dl.text((8, yy + 4), '%s  1x (actual pixels)  |  320 px wide (actual)' % k.upper(), font=F(20), fill=(255, 230, 40))
    L.paste(one, (0, yy + 28))
    s = ims[k].resize((320, int(H * 320 / W)), Image.LANCZOS)
    L.paste(s, (W // 2 + 10, yy + 28))
L.save(OUT + 'legibility_1x_320.jpg', quality=92)
