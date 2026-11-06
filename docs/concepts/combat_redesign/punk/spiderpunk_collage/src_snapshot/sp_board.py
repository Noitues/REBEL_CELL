"""sp_board: style_board.jpg, wheel_crop.jpg, hand_crop.jpg from the rendered plates and cached card / tower images."""
import sys, os, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = 'D:/rc_scratch/combat_redesign/punk/spiderpunk_collage/'
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/spiderpunk_collage/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
ANTON = FD + 'Anton-Regular.ttf'
MARK = FD + 'PermanentMarker-Regular.ttf'
MONO = FD + 'ShareTechMono-Regular.ttf'
os.makedirs(OUT, exist_ok=True)


def F(p, s):
    return ImageFont.truetype(p, s)


def wheel_crop():
    a = Image.open(ROOT + 'out/p1_A.png').convert('RGB')
    b = Image.open(ROOT + 'out/p1_B.png').convert('RGB')
    box = (150, 150, 920, 920)       # the wheel body (centre 535,540)
    ca, cb = a.crop(box), b.crop(box)
    ca = ca.resize((ca.width * 2, ca.height * 2), Image.LANCZOS)
    cb = cb.resize((cb.width * 2, cb.height * 2), Image.LANCZOS)
    # keep the file below ~6 MP: crop each to the tower disc (r 250 around the centre)
    cx, cy = (535 - 150) * 2, (540 - 150) * 2
    r = 520
    ca = ca.crop((cx - r, cy - r, cx + r, cy + r))
    cb = cb.crop((cx - r, cy - r, cx + r, cy + r))
    W = Image.new('RGB', (ca.width * 2 + 30, ca.height + 70), (22, 18, 30))
    W.paste(ca, (10, 60))
    W.paste(cb, (ca.width + 20, 60))
    d = ImageDraw.Draw(W)
    d.text((20, 12), 'A  POSTER', font=F(ANTON, 36), fill=(255, 204, 0))
    d.text((ca.width + 30, 12), 'B  GIG FLYER', font=F(ANTON, 36), fill=(255, 204, 0))
    W.save(OUT + 'wheel_crop.jpg', quality=92)


def hand_crop():
    a = Image.open(ROOT + 'out/p1_A.png').convert('RGB')
    b = Image.open(ROOT + 'out/p1_B.png').convert('RGB')
    box = (840, 760, 1920, 1080)
    W = Image.new('RGB', (1080, 320 * 2 + 70), (22, 18, 30))
    W.paste(a.crop(box), (0, 30))
    W.paste(b.crop(box), (0, 30 + 320 + 10))
    d = ImageDraw.Draw(W)
    d.text((8, 2), 'A POSTER', font=F(MONO, 22), fill=(255, 204, 0))
    d.text((8, 30 + 320 + 10 + 320 - 2 + 0), 'B GIG FLYER', font=F(MONO, 22), fill=(255, 204, 0))
    W.save(OUT + 'hand_crop.jpg', quality=92)


if __name__ == '__main__':
    wheel_crop()
    hand_crop()
    print('crops ok')
