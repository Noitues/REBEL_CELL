"""wheels_compare.jpg (4 hero wheels) and cards_compare.jpg (4 detail Arc Flash cards)."""
from common import *
import wheels
import cards

img = sheet_bg().convert('RGB').resize((1920, 620)).convert('RGBA')
d = ImageDraw.Draw(img)
for k, v in enumerate('ABCD'):
    w = wheels.render_wheel(v, 170, PLAYER, 'player', rot=2.5, status={5})
    wheels.paste_wheel(img, w, 240 + k * 480, 300)
    label(d, 240 + k * 480, 600, ' '.join(wheels.NAMES[v]), 20)
img.convert('RGB').save(os.path.join(OUT, 'wheels_compare.jpg'), quality=90)
img = sheet_bg().convert('RGB').resize((1920, 560)).convert('RGBA')
d = ImageDraw.Draw(img)
for k, v in enumerate('ABCD'):
    c = cards.render_card(v, cards.CARDS[1], 260, 366)
    paste_c(img, c, 240 + k * 480, 260)
    label(d, 240 + k * 480, 530, ' '.join(cards.NAMES[v]), 20)
img.convert('RGB').save(os.path.join(OUT, 'cards_compare.jpg'), quality=90)
print('wrote compares')
