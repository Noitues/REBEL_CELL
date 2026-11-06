"""style_board.jpg for the MURAL GRAFFITI concept: palette, textures, line samples, one slice, the hub, one card at large size, manifesto.
Crops come from real renders (hi-res tower canvas, real card renderer)."""
import sys, json, math, os
sys.dont_write_bytecode = True
sys.path.insert(0, '.')
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import asm_r2
asm_r2.setup()
import mu_art as MU
import mu_cards as MC
import f1_tower as T
import f1_lib as FL
import st_cards as K

WK = 'D:/rc_scratch/combat_redesign/punk/mural_graffiti/work_m/'
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/mural_graffiti/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
J = json.load(open('D:/rc_scratch/combat_redesign/punk/mural_graffiti/state_e10.json'))
BG = (22, 18, 34)


def F(name, px):
    return ImageFont.truetype(FD + name, px)


def hi_tower(v):
    fp = WK + 'hi_tower_%s.png' % v
    if os.path.exists(fp):
        return Image.open(fp).convert('RGBA')
    MU.VAR[0] = v
    im, cv = T.render_tower(J['f1'])
    hi = cv.rgba()
    hi.save(fp)
    return hi


def card(v, name, scale=3, seed=1):
    fp = WK + 'bigcard_%s_%s.png' % (v, name)
    if os.path.exists(fp):
        return Image.open(fp).convert('RGBA')
    K.NW[0] = False
    im = MC.render_card(name, v, seed=seed, ss=6, scale=scale)
    im.save(fp)
    return im


def shadow_paste(base, im, xy):
    a = im.split()[3]
    sh = Image.new('L', im.size, 0)
    sh.paste(a, (6, 10))
    sh = sh.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.6))
    b = Image.new('RGBA', im.size, (6, 4, 12, 0))
    b.putalpha(sh)
    base.alpha_composite(b, xy)
    base.alpha_composite(im, xy)


def txt(d, xy, s, f, fill=(240, 236, 228), anchor='la', stroke=0, sfill=(10, 8, 18)):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)


def swatch(d, x, y, col, label, w=118, h=64):
    d.rectangle([x, y, x + w, y + h], fill=col, outline=(10, 8, 18), width=3)
    txt(d, (x, y + h + 6), label, F('ShareTechMono-Regular.ttf', 15), (214, 208, 220))


def main():
    W, H = 1920, 1680
    bd = Image.new('RGBA', (W, H), BG + (255,))
    d = ImageDraw.Draw(bd)
    txt(d, (40, 22), 'MURAL GRAFFITI', F('Anton-Regular.ttf', 96), (255, 255, 255), stroke=5)
    txt(d, (46, 150), 'wheel + card hand, punk concept: A brick, B concrete', F('ShareTechMono-Regular.ttf', 18), (190, 184, 204))
    man = ['The Cell does not draw on a board: it paints a wall. Saturated spray, sunset light, a white-outlined throw-up in the middle of a corp-clean grid.',
           'Solace is flat enamel on slate glass; the Cell is wet paint on brick, with drips, overspray and the mortar showing through. Hand against machine.',
           'Pink paint is ours, ink + white keyline is the Cell outline, and nothing the corp owns is ever painted: ownership reads from material.']
    f = F('PermanentMarker-Regular.ttf', 20)
    y = 22
    for i, m in enumerate(man):
        txt(d, (880, y - 4), str(i + 1), F('Anton-Regular.ttf', 34), (255, 61, 168))
        words = m.split()
        line = ''
        lines = []
        for w_ in words:
            if f.getlength(line + ' ' + w_) > 930:
                lines.append(line)
                line = w_
            else:
                line = (line + ' ' + w_).strip()
        lines.append(line)
        for k, l in enumerate(lines):
            txt(d, (922, y + k * 24), l, f, (244, 240, 232))
        y += max(2, len(lines)) * 24 + 14
    # ---- palette rows
    txt(d, (40, 196), 'PALETTE', F('Anton-Regular.ttf', 34), (255, 61, 168))
    pa = [((255, 61, 168), 'CELL PINK'), ((255, 150, 84), 'WARM LIGHT'), ((255, 214, 72), 'SUN YELLOW'), ((124, 30, 158), 'SHADE VIOLET'), ((70, 214, 250), 'RIM CYAN'),
          ((24, 190, 176), 'TEAL'), ((150, 56, 44), 'BRICK'), ((84, 92, 124), 'CONCRETE'), ((239, 227, 200), 'PLASTER'), ((12, 10, 22), 'INK'), ((255, 252, 244), 'KEYLINE'), ((123, 224, 123), 'HP GREEN')]
    for i, (c, l) in enumerate(pa):
        swatch(d, 40 + (i % 6) * 150, 244 + (i // 6) * 108, c, l, w=134, h=62)
    txt(d, (40, 470), 'game colours kept: HP green, harm red, soak blue, Trace violet, RAM cyan', F('ShareTechMono-Regular.ttf', 16), (160, 154, 176))
    # ---- textures: brick tile, concrete tile (from the real wall generator), spray edge sample, outline stack, drips
    txt(d, (960, 196), 'TEXTURES AND LINE', F('Anton-Regular.ttf', 34), (255, 61, 168))
    cvt = FL.Canvas(470, 470, 3, seed=1)
    tiles = []
    for v in 'AB':
        MU.VAR[0] = v
        tex, seam = MU.wall_tex(cvt)
        t_ = Image.fromarray(np.clip(tex[500:860, 500:860] * 0.9, 0, 255).astype(np.uint8)).resize((200, 200), Image.LANCZOS)
        tiles.append(t_)
    for i, t_ in enumerate(tiles):
        bd.paste(t_, (960 + i * 216, 244))
        txt(d, (960 + i * 216, 450), ['brick wall (A)', 'concrete wall (B)'][i], F('ShareTechMono-Regular.ttf', 15), (214, 208, 220))
    # sample strokes drawn with the real tools
    sc = FL.Canvas(420, 200, 3, seed=5)
    S = sc.S
    FL.marker(sc, [(20, 40), (120, 30), (220, 44), (310, 34)], (255, 61, 168), w=14, alpha=1.0, wob=1.0, grain=0.2)
    from scipy import ndimage as ndi
    m_, x0_, y0_ = FL.stroke_mask(sc, [(20, 100), (120, 90), (220, 104), (310, 94)], 14, 'round', 0, 1.0, 40, (0.05, 0.1))
    mm = ndi.gaussian_filter(m_, 1.2 * S)
    sc.over(np.clip(FL.outline_mask(m_, S, 5.4), 0, 1), (12, 10, 22), 1.0, x0_, y0_)
    sc.over(np.clip(FL.outline_mask(m_, S, 2.4), 0, 1), (255, 252, 244), 1.0, x0_, y0_)
    sc.over(np.clip(mm * 1.1, 0, 1), (255, 61, 168), 1.0, x0_, y0_)
    out = sc.down()
    pnl = Image.new('RGBA', (420, 200), (84, 40, 36, 255))
    pnl.alpha_composite(out)
    bd.alpha_composite(pnl, (1400, 244))
    txt(d, (1400, 450), 'soft spray stroke / ink + white keyline + pink fill', F('ShareTechMono-Regular.ttf', 15), (214, 208, 220))
    # ---- big pieces: per variant a row (slice, hub, one card at large size, the hand at 0.72x)
    txt(d, (40, 508), 'ONE SLICE, THE HUB, ONE CARD, THE HAND', F('Anton-Regular.ttf', 34), (255, 61, 168))
    S = 3
    cx, cy = T.CT
    for vi, v in enumerate('AB'):
        y0 = 560 + vi * 560
        hi = hi_tower(v)
        px, py = int(cx * S), int((cy + 128) * S)
        sl = hi.crop((px - 345, py - 345, px + 345, py + 345)).resize((440, 440), Image.LANCZOS)
        panel = Image.new('RGBA', (440, 440), (30, 26, 44, 255))
        panel.alpha_composite(sl)
        bd.alpha_composite(panel, (40, y0))
        mono = F('ShareTechMono-Regular.ttf', 15)
        txt(d, (40, y0 + 446), '%s  slice: ink + white keyline, %s' % (v, 'airbrushed warm / cool light, brick through paint' if v == 'A' else 'hard cel shadow, cyan rim, warm sliver'), mono, (214, 208, 220))
        txt(d, (40, y0 + 468), 'drips off the outer rim, white stencil icon with a %s drop' % ('orange' if v == 'A' else 'cyan'), mono, (214, 208, 220))
        hub = hi.crop((int(cx * S - 190), int(cy * S - 190), int(cx * S + 190), int(cy * S + 190))).resize((300, 300), Image.LANCZOS)
        panel = Image.new('RGBA', (300, 300), (30, 26, 44, 255))
        panel.alpha_composite(hub)
        bd.alpha_composite(panel, (500, y0))
        txt(d, (500, y0 + 306), '%s  hub: a painted %s, HP ring round it' % (v, 'sun' if v == 'A' else 'blue bubble'), mono, (214, 208, 220))
        cd = card(v, 'Trigger', 3, seed=7)
        cd = cd.resize((int(cd.width * 0.6), int(cd.height * 0.6)), Image.LANCZOS)
        shadow_paste(bd, cd, (830, y0 - 4))
        txt(d, (830, y0 + 520), '%s  card: ink title slab, %s title' % (v, 'white' if v == 'A' else 'yellow'), mono, (214, 208, 220))
        for i, nm in enumerate(['Brace', 'Spin3', 'Trigger', 'Twist']):
            fp = WK + 'card_%s_%s_0.png' % (v, nm)
            if os.path.exists(fp):
                ci = Image.open(fp).convert('RGBA')
                ci = ci.resize((int(ci.width * 0.36), int(ci.height * 0.36)), Image.LANCZOS)
                bd.alpha_composite(ci, (1250 + i * 160, y0 + 10 + (i % 2) * 6))
        txt(d, (1250, y0 + 220), 'the hand as it sits on the plate (A and B share one layout)', mono, (160, 154, 176))
        # a spray-stroke note
        bd.convert('RGB').save(DEL + 'style_board.jpg', quality=92)
    print('board ok')


if __name__ == '__main__':
    os.makedirs(DEL, exist_ok=True)
    main()
