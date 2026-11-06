from PIL import Image, ImageDraw, ImageFont
O = 'D:/rc_scratch/combat_redesign/punk_slices/wpap_faceted/out/'
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/wpap_faceted/'
cx, cy, r = 537, 547, 205
src = [D + 'plate_A.png', O + 'plate_A.png', O + 'plate_B.png']
labs = ['OLD: one pink for every slice', 'A  RIOT SET', 'B  NIGHT SHIFT']
w = Image.new('RGB', (r * 12 + 24, r * 4 + 40), (22, 8, 38))
d = ImageDraw.Draw(w)
f = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 22)
for i, s in enumerate(src):
    im = Image.open(s).convert('RGB').crop((cx - r, cy - r, cx + r, cy + r)).resize((r * 4, r * 4), Image.LANCZOS)
    w.paste(im, (i * (r * 4 + 12), 40))
    d.text((i * (r * 4 + 12) + 8, 8), labs[i], font=f, fill=(255, 250, 240))
w = w.crop((0, 0, 3 * (r * 4 + 12) - 12, r * 4 + 40))
w.save('D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/wpap_faceted/slices/wheel_crop.jpg', quality=92)
print(w.size)
