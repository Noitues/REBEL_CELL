"""v2 contact sheet: composites (left) and squints (right) for the three rooms. usage: python sheet_v2.py"""
import json
from PIL import Image, ImageDraw, ImageFont
V2 = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/'
f = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/ShareTechMono-Regular.ttf', 22)
rooms = [('bio', 'BIO-LAB seed 11 (Elite Router)'), ('srv', 'SERVER ROOM seed 23 (Server Rack)'), ('gh', 'GREENHOUSE seed 37 (Virus-exploit Site)')]
W, H = 960, 540
im = Image.new('RGB', (W * 2, (H + 36) * 3), (8, 6, 18))
d = ImageDraw.Draw(im)
for i, (n, t) in enumerate(rooms):
    y = i * (H + 36)
    d.text((10, y + 6), 'COMBAT CUTAWAY v2   ' + t + '   composed (left) / squint 1/16 (right)', font=f, fill=(150, 255, 70))
    im.paste(Image.open(V2 + 'room_%s.png' % n).convert('RGB').resize((W, H), Image.LANCZOS), (0, y + 36))
    im.paste(Image.open(V2 + 'squint_%s.png' % n).convert('RGB').resize((W, H), Image.LANCZOS), (W, y + 36))
im.save(V2 + 'sheet.jpg', quality=92)
