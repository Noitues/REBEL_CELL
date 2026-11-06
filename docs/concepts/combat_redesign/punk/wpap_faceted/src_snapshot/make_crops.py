from PIL import Image
O = 'D:/rc_scratch/combat_redesign/punk/wpap_faceted/out/'
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/wpap_faceted/'
A = Image.open(O + 'plate_A.png').convert('RGB'); B = Image.open(O + 'plate_B.png').convert('RGB')
cx, cy, r = 537, 547, 205
def wh(im):
    return im.crop((cx - r, cy - r, cx + r, cy + r)).resize((r * 4, r * 4), Image.LANCZOS)
w = Image.new('RGB', (r * 8 + 12, r * 4), (22, 8, 38))
w.paste(wh(A), (0, 0)); w.paste(wh(B), (r * 4 + 12, 0))
w.save(O + 'wheel_crop.jpg', quality=92)
hb = (830, 750, 1650, 1080)
h = Image.new('RGB', (820, 330 * 2 + 10), (22, 8, 38))
h.paste(A.crop(hb), (0, 0)); h.paste(B.crop(hb), (0, 340))
h.save(O + 'hand_crop.jpg', quality=92)
