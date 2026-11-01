"""hv_final: insets, slip frames, overview sheet.  Reads ../out/v2/*.png + slips.json, writes the deliverable folder."""
import sys, os, json, math, shutil
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD = 'D:/rc_art/art-pass/assets/fonts/'
IN = 'D:/rc_scratch/combat_redesign/hover2/out/v2/'
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/hover_final/'
C = (536, 540)
INK = (12, 10, 22)
CYAN = (92, 225, 255)
NAVY = (5, 13, 28)
PLANC = (255, 226, 0)
_f = {}


def font(n, px):
    k = (n, px)
    if k not in _f:
        _f[k] = ImageFont.truetype(FD + n, px)
    return _f[k]


anton = lambda px: font('Anton-Regular.ttf', px)
mono = lambda px: font('ShareTechMono-Regular.ttf', px)
plex = lambda px: font('IBMPlexSansCondensed-Medium.ttf', px)

NAMES = [('h01_tower_turn', 'h01', 'SPIN 3 / SPIN 2 / NUDGE', 'turn the tower'), ('h02_brace', 'h02', 'BRACE', 'protect a slice'),
         ('h03_trigger', 'h03', 'TRIGGER', 'resolve a unit now'), ('h04_twist', 'h04', 'TWIST', 'turn one ring'),
         ('h05_strike', 'h05', 'STRIKE', 'damage a unit'), ('h06_shove', 'h06', 'SHOVE', 'move a unit sideways'),
         ('h07_pull', 'h07', 'PULL', 'move a unit inward'), ('h08_hold', 'h08', 'HOLD', 'stop the rings this turn'),
         ('h09_firewall', 'h09', 'FIREWALL', 'burn a sector'), ('h10_soak', 'h10', 'SOAK', 'END TURN soak toggle (not a card)'),
         ('h11_unit', 'h11', 'UNIT', 'inspect a unit (p2b form)')]


def panel(img, crop, x, y, cap, pad=8, bar=28):
    w, h = crop.size
    d = ImageDraw.Draw(img, 'RGBA')
    d.rounded_rectangle([x + 4, y + 5, x + w + 2 * pad + 4, y + h + bar + pad + 5], radius=8, fill=(0, 0, 0, 110))
    d.rounded_rectangle([x, y, x + w + 2 * pad, y + h + bar + pad], radius=8, fill=NAVY + (240,), outline=CYAN, width=2)
    if cap:
        d.text((x + pad + 2, y + bar / 2 + 1), cap, font=mono(17), fill=(175, 192, 214), anchor='lm')
    img.paste(crop, (x + pad, y + bar))
    d.rectangle([x + pad, y + bar, x + pad + w, y + bar + h], outline=INK, width=2)


def tower_crop(path, half=232, size=300):
    im = Image.open(path).convert('RGB')
    c = im.crop((C[0] - half, C[1] - half, C[0] + half, C[1] + half))
    return c.resize((size, size), Image.LANCZOS)


def add_insets(pid, img, words, meta):
    if not words:
        return img
    img = img.copy()
    if pid == 'h01_tower_turn':
        panel(img, tower_crop(IN + 'h01_spin2.png'), 1092, 408, 'SPIN 2')
        panel(img, tower_crop(IN + 'h01_nudge.png'), 1092 + 332, 408, 'NUDGE')
    elif pid == 'h03_trigger':
        im = Image.open(IN + 'h03_f2.png').convert('RGB')
        c = im.crop((1072, 76, 1896, 386)).resize((494, 186), Image.LANCZOS)
        panel(img, c, 1092, 408, 'TRIGGER AFTER TWIST')
    elif pid == 'h06_shove' and 'bump_xy' in meta:
        im = Image.open(IN + 'h06_bump.png').convert('RGB')
        x, y = meta['bump_xy']
        hw = 120
        x = min(max(x, hw), 1920 - hw); y = min(max(y, hw), 1080 - hw)
        c = im.crop((int(x - hw), int(y - hw), int(x + hw), int(y + hw))).resize((300, 300), Image.LANCZOS)
        panel(img, c, 1092, 408, 'SHOVE INTO A NEIGHBOUR')
    return img


def wrap(txt, fnt, wmax, d):
    words = txt.split(' ')
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=fnt) > wmax and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def slip_frame(plate, slip):
    """plate (1920x1080) with the review slip under the frame; the plate itself stays clean"""
    tmp = Image.new('RGB', (10, 10))
    d0 = ImageDraw.Draw(tmp)
    fnt = mono(17)
    body = []
    for ln in slip['lines']:
        body += wrap(ln, fnt, 1780, d0)
    h = 62 + 25 * len(body) + 20
    out = Image.new('RGB', (1920, 1080 + 24 + h), (16, 14, 24))
    out.paste(plate, (0, 0))
    d = ImageDraw.Draw(out)
    y0 = 1080 + 24
    d.rectangle([0, 1080, 1920, 1080 + 24], fill=(16, 14, 24))
    d.rounded_rectangle([40, y0, 1880, y0 + h], radius=5, fill=(242, 238, 228), outline=INK, width=2)
    d.rectangle([60, y0 - 12, 214, y0 + 10], fill=(255, 226, 0), outline=INK, width=2)
    d.text((137, y0 - 1), 'REVIEW SLIP', font=mono(14), fill=INK, anchor='mm')
    d.text((60, y0 + 30), slip['title'], font=anton(24), fill=INK, anchor='lm')
    for i, ln in enumerate(body):
        d.text((60, y0 + 62 + 25 * i), ln, font=fnt, fill=(34, 30, 48), anchor='lm')
    return out


def sheet(tiles, key_img=None):
    W, TW = 1980, 624
    TH = 351
    gut = 24
    rows = math.ceil((len(tiles) + (1 if key_img else 0)) / 3)
    CH = TH + 92
    Hh = 130 + rows * (CH + 14) + 20
    im = Image.new('RGB', (W, Hh), (9, 10, 20))
    d = ImageDraw.Draw(im)
    d.text((30, 18), 'HOVER PLATES  |  one per card effect type, Shifting Waves', font=anton(46), fill=(242, 246, 255))
    d.text((32, 78), 'round 2: lit what the card touches, dim the rest (value x0.40, chroma x0.45)  |  PLAN pencil = every proposal and move  |  lime corners = legal / aimed target  |  hatch: pink = ours, red = yours to lose',
           font=mono(17), fill=(175, 192, 214))
    d.text((32, 102), 'stand-in board = the redesigned grammar board (queue, time grammar, no dashes) with the E10 tower and cards; waits for the finalist p1 art', font=mono(17), fill=(122, 136, 156))
    items = list(tiles) + ([key_img] if key_img else [])
    for i, t in enumerate(items):
        r, c = divmod(i, 3)
        x = gut + c * (TW + gut)
        y = 130 + r * (CH + 14)
        pic, hid, nm, sub, rule = t
        im.paste(pic.resize((TW, TH), Image.LANCZOS), (x, y + 34))
        d.rectangle([x - 1, y + 33, x + TW, y + 34 + TH], outline=(60, 70, 96), width=1)
        d.text((x, y + 17), nm, font=anton(26), fill=(242, 246, 255), anchor='lm')
        d.text((x + TW, y + 17), '%s   %s' % (hid, sub), font=mono(16), fill=(122, 136, 156), anchor='rm')
        yy = y + 34 + TH + 10
        for ln in wrap(rule, mono(15), TW, d)[:3]:
            d.text((x, yy), ln, font=mono(15), fill=(175, 192, 214))
            yy += 20
    return im
