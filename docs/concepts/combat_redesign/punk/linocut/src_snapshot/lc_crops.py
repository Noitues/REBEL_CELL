import sys
sys.dont_write_bytecode = True
from PIL import Image
from cv_lib import C
O = 'D:/rc_scratch/combat_redesign/punk/linocut/out/'
def wheel(tag='p1'):
    A = Image.open(O + 'plate_A_%s.png' % tag); B = Image.open(O + 'plate_B_%s.png' % tag)
    r = 232
    box = (int(C[0] - r), int(C[1] - r), int(C[0] + r), int(C[1] + r))
    a = A.crop(box).resize((r * 4, r * 4), Image.LANCZOS); b = B.crop(box).resize((r * 4, r * 4), Image.LANCZOS)
    s = Image.new('RGB', (a.width * 2 + 8, a.height), (10, 10, 14)); s.paste(a, (0, 0)); s.paste(b, (a.width + 8, 0))
    return s
def hand(tag='p1'):
    A = Image.open(O + 'plate_A_%s.png' % tag); B = Image.open(O + 'plate_B_%s.png' % tag)
    box = (830, 740, 1920, 1080)
    a = A.crop(box); b = B.crop(box)
    s = Image.new('RGB', (a.width, a.height * 2 + 6), (10, 10, 14)); s.paste(a, (0, 0)); s.paste(b, (0, a.height + 6))
    return s
if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'p1'
    wheel(tag).save(O + 'wheel_crop.jpg', quality=92)
    hand(tag).save(O + 'hand_crop.jpg', quality=92)
    print('ok', C)
