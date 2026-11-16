"""B-107 item 4 (T5 advance choice): a STAY sticker on the original site, a GO sticker on the newly taken one, on the
city map page (hq_idle, r42, Solace). Nothing else. Run: python advance.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

ORIG = (923, 557)    # CULTURE INTAKE (the site the run left from; the map's link start)
NEW = (1130, 390)    # SEED VAULT EXCHANGE (just claimed)


def patch(img, dst, src, feather=26):
    """Cover pre-run chrome with another piece of the same city (feathered), dimmed a touch."""
    x0, y0, x1, y1 = dst
    w, h = x1 - x0, y1 - y0
    pc = img.crop(tuple(S([src[0], src[1], src[0] + w, src[1] + h])))
    pc = ImageEnhance.Brightness(pc).enhance(.82)
    m = Image.new('L', pc.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([S(feather), S(feather), pc.size[0] - S(feather), pc.size[1] - S(feather)], radius=S(30), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(S(feather * .6)))
    img.paste(pc, (S(x0), S(y0)), m)


def advance():
    img = load_bg('cohesion/map_pages_r42/hq_idle.png')
    # the site-file slot now shows the claimed site (same chrome as the r42 site file, lime = ours); JACK IN is gone
    glass(img, (1462, 585, 1905, 875), edge=LIME, title=None, fill=(10, 22, 14, 246))
    text(img, (1486, 604), "T2  //  SEED VAULT EXCHANGE", font("plex", 30), WHITE)
    text(img, (1488, 646), "SOLACE BIOSYSTEMS  //  SITE FILE 207", font("mono", 16), (150, 200, 150, 255))
    stamp(img, "TAKEN", 1790, 700, LIME, rot=-8, size=40)
    chip(img, 1488, 700, "CREW HERE  RIG-4", font("mono", 20), WHITE, (8, 20, 12, 240), LIME)
    chip(img, 1488, 746, "+12 SCHEM", font("mono", 20), LIME, (8, 20, 12, 240), LIME)
    chip(img, 1488, 800, "STAY  hold the intake", font("mono", 20), WHITE, (8, 12, 24, 240), WHITE)
    chip(img, 1488, 834, "GO  move up to the vault", font("mono", 20), INK, LIME, LIME)
    patch(img, (1545, 885, 1915, 1066), (30, 560), feather=12)
    # the claimed site: lime ring + check (T5 K9 state)
    ellipse(img, [NEW[0] - 46, NEW[1] - 46, NEW[0] + 46, NEW[1] + 46], outline=LIME, width=6)
    tick(img, NEW[0] + 30, NEW[1] - 30, 30, LIME, 7)
    # the two stickers: each one sits on its site with a die-cut tail onto the node
    arrow_hand(img, [(ORIG[0] + 40, ORIG[1] - 46), (ORIG[0] + 110, ORIG[1] - 130), (NEW[0] - 62, NEW[1] + 40)], YEL, 6, head=26)
    poly(img, [(ORIG[0] - 16, ORIG[1] + 40), (ORIG[0] + 16, ORIG[1] + 40), (ORIG[0], ORIG[1] + 22)], fill=WHITE)
    sticker(img, 'STAY', ORIG[0], ORIG[1] + 84, 150, 66, WHITE, None, rot=-4, size=52)
    chip(img, ORIG[0] - 82, ORIG[1] + 128, "hold the intake", font("hand", 24), WHITE, (8, 10, 18, 220), None)
    # GO is hovered: lifted, lime glow, bigger
    gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).rounded_rectangle(S([NEW[0] + 40, NEW[1] - 160, NEW[0] + 230, NEW[1] - 60]), radius=S(20), fill=LIME)
    img = glow(img, gl, 22, 1.0)
    poly(img, [(NEW[0] + 52, NEW[1] - 70), (NEW[0] + 84, NEW[1] - 64), (NEW[0] + 40, NEW[1] - 36)], fill=WHITE)
    sticker(img, 'GO', NEW[0] + 135, NEW[1] - 110, 150, 76, LIME, None, rot=6, size=62)
    chip(img, NEW[0] + 236, NEW[1] - 128, "move up", font("hand", 26), LIME, (8, 10, 18, 220), None)
    # the one-line DISPATCH strip that names the choice (existing chrome, bottom centre)
    rrect(img, [690, 1026, 1430, 1068], 4, fill=(20, 10, 4, 235), outline=(255, 140, 40, 255), width=3)
    text(img, (712, 1047), 'DISPATCH // the vault is ours. move the crew up, or hold the intake?', font('mono', 19), (255, 200, 140, 255), 'lm')
    chip(img, 1520, 1030, 'G  go   .   S  stay', font('mono', 18), WHITE, (8, 12, 24, 230), CYAN)
    frame_caption(img, 'B-107 item 4  T5 advance choice: STAY on the original site, GO on the new one (hover GO)')
    return finish_save(img, 'advance_choice.png', vig=.25)


if __name__ == '__main__':
    advance()
