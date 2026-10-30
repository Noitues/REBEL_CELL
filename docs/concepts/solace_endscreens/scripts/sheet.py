"""Contact sheet: 3 directions x (WIN, LOSE)."""
from PIL import Image, ImageDraw, ImageFont

D = 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/'
F = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/ShareTechMono-Regular.ttf', 26)
rows = [('D1  SPECIMEN FILE   (lab bench, Petri dish, biosafety paper)', 'd1'),
        ('D2  THE HELIX FROM THE CITY   (hacked to Cell colours / the Bloom spreads)', 'd2'),
        ('D3  SOLACE LIVE BROADCAST   (seized feed / "contamination contained")', 'd3')]
tw_, th_ = 944, 531
sheet = Image.new('RGB', (1920, 3 * (th_ + 52) + 70), (8, 10, 18))
d = ImageDraw.Draw(sheet)
d.text((24, 18), 'SOLACE END SCREENS   win (left)  /  lose (right)   1920x1080 concepts', font=F, fill=(150, 255, 70))
y = 70
for title, k in rows:
    d.text((24, y), title, font=F, fill=(0, 229, 255))
    y += 40
    for i, kind in enumerate(('win', 'lose')):
        im = Image.open(D + f'{k}_{kind}.png').convert('RGB').resize((tw_, th_), Image.LANCZOS)
        sheet.paste(im, (12 + i * (tw_ + 8), y))
    y += th_ + 12
sheet.save(D + 'sheet.jpg', quality=90)
print('ok')
