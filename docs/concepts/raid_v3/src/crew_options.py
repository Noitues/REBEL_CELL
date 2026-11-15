"""crew_options: context images for the CREW-column question (designer 2026-11-15: "CREW should show full roster, I think").

    python crew_options.py

Same plan state as r3_plan (round 1, KAI b3, VEX d3, MOTH b5 placed, RUNE on the bench).  The operatives on the map are drawn
as a stand-in for the bible 4.8 R3 class beacon (ring + emblem disc), because on the 3D city the operative on the map is the
beacon, not the sticker.  Only the CREW column changes between options:
  A  liner outline + pencil cell (as in r3_plan)
  B  full roster: the sticker stays, pencil cell + tick under it
  C  full roster, placed ones dimmed: the sticker stays at lower value, pencil cell under it; the bench sticker is full bright
Writes docs/concepts/raid_v3/crew_options/crew_{A,B,C}.png and crew_sheet.jpg.
"""
import os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
import raid_kit as K
import raid_v3 as R
from raid_kit import Wax, PEN_Y, PEN_R, S, text, Layer, comp, INK, PAPER, ANTON, F_all, base_image, stick, S_GAIN, S_HARM, S_HI, TEXT_MID

OUT = 'D:/rc_art/art-pass/docs/concepts/raid_v3/crew_options/'
WHERE = {'KAI': 'b3', 'VEX': 'd3', 'MOTH': 'b5'}


def beacon(img, oid, c, r):
    """top-down stand-in for the R3 class beacon: a role-colour cap ring, a dark emblem disc with the callsign initials"""
    x, y = R.G.cc(c, r)
    top, bot = K.OPS[oid]['col']
    L = Layer(); d = L.d
    for rr, a in ((40, 50), (33, 110)):
        d.ellipse([S(x - rr), S(y - rr), S(x + rr), S(y + rr)], outline=top + (a,), width=S(3))
    d.ellipse([S(x - 25), S(y - 25), S(x + 25), S(y + 25)], fill=(10, 12, 18, 235), outline=bot + (255,), width=S(4))
    text(d, (x, y + 1), oid[:2], ImageFont.truetype(ANTON, S(24)), top + (255,), anchor='mm')
    comp(img, L)


def dim(sd, k):
    im = sd['img']
    a = im.split()[3]
    rgb = ImageEnhance.Brightness(ImageEnhance.Color(im.convert('RGB')).enhance(0.55)).enhance(k).convert('RGBA')
    rgb.putalpha(a)
    return dict(sd, img=rgb)


def crew_full(img, F, where, mode):
    L = Layer(); text(L.d, (26, 182), 'CREW', F['m20'], TEXT_MID + (255,), anchor='lm'); comp(img, L)
    py = Wax(PEN_Y, 91)
    for oid, (x, y, ang) in K.CREW_POS.items():
        st = where.get(oid)
        o = K.OPS[oid]
        sd = K.op_sticker(oid)
        wd = K.wpn_sticker(o['wpn'], o['stars'])
        if st and mode == 'C':
            sd, wd = dim(sd, 0.62), dim(wd, 0.62)
        stick(img, sd, x, y, ang)
        stick(img, wd, x + K.WPN_OFF[0], y + K.WPN_OFF[1], K.WPN_OFF[2], scale=0.82)
        if st:
            py.text('on ' + st, x - 6, y + 104, 32, angle=-5)
            py.tick(x + 58, y + 102, 13, 6)
    py.ink_ss(img)


def plate(mode):
    F = F_all(); img = base_image()
    R.road_base(img, F)
    K.token(img, 'trooper', *R.G.cc(0, 0), 8, count=5)
    K.token(img, 'bike', *R.G.cc(6, 0), 6, count=3)
    R.road_objects(img, placed={})
    for oid, (c, r) in R.PLACED.items():
        beacon(img, oid, c, r)
    py, pr = Wax(PEN_Y, 1), Wax(PEN_R, 2)
    R.road_routes(pr)
    R.plan_pencil(py, pr)
    py.ink_ss(img); pr.ink_ss(img)
    K.core_tape(img, F, 'RAID: STATIC ALLEY', 8, 8, 2)
    K.rows(img, F, 1, 4, 7, 0)
    if mode == 'A':
        K.crew(img, F, WHERE)
    else:
        crew_full(img, F, WHERE, mode)
    K.left_foot(img, F, [('ON MAP', 3), ('BENCH', 1), ('DEVICES', 1)])
    R.right_col(img, F)
    K.hud_line(img, F, 'FORECAST', [('A holds at c2', S_GAIN), R.DOT, ('B 2 leak', S_HARM), R.DOT, ('Core 8 \u2192 6', S_HARM), R.DOT,
                                    ('6/8 killed', S_HI)])
    return img


LABEL = {'A': 'A  outline left behind (as r3_plan)', 'B': 'B  full roster, pencil cell + tick', 'C': 'C  full roster, placed ones dimmed'}


def main():
    os.makedirs(OUT, exist_ok=True)
    crops = []
    for m in 'ABC':
        im = K.finish(plate(m)) if hasattr(K, 'finish') else plate(m)
        if im.size != (1920, 1080):
            im = im.resize((1920, 1080), Image.LANCZOS)
        im = im.convert('RGB')
        im.save(OUT + 'crew_%s.png' % m)
        crops.append(im.crop((0, 0, 1370, 1080)).resize((685, 540), Image.LANCZOS))
        print('wrote crew_%s.png' % m, flush=True)
    sh = Image.new('RGB', (3 * 685 + 4 * 20, 540 + 110), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(ANTON, 34)
    for i, (m, c) in enumerate(zip('ABC', crops)):
        x = 20 + i * 705
        sh.paste(c, (x, 90))
        d.text((x, 30), LABEL[m], font=f, fill=(235, 235, 235))
    sh.save(OUT + 'crew_sheet.jpg', quality=90)
    print('wrote crew_sheet.jpg', flush=True)


if __name__ == '__main__':
    main()
