"""Build locked/review_rebuild.jpg: one row per area, before (the 090ad870 plate, extracted with git show into
final_review/before/) vs after (the published plate now), labelled with the AD review finding numbers and the
final-review status and numbers (CIE L* on the published PNGs)."""
import os
from PIL import Image, ImageDraw, ImageFont

LOCKED = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
BEFORE = 'D:/rc_scratch/combat_redesign/locked/final_review/before/'
FONTS = 'D:/rc_scratch/combat_redesign/locked/corp/src/fonts/'
OUT = LOCKED + 'review_rebuild.jpg'

PW = 900          # panel width
PH_MAX = 760      # panel height cap
LW = 470          # label column
GAP = 16
BG = (14, 14, 20)
INK = (236, 236, 240)
DIM = (150, 156, 170)
COL = {'FIXED': (123, 224, 123), 'DOC': (154, 107, 255), 'NOT': (255, 68, 51), 'PART': (255, 196, 40)}

F_H = ImageFont.truetype(FONTS + 'Anton-Regular.ttf', 30)
F_T = ImageFont.truetype(FONTS + 'IBMPlexSansCondensed-Medium.ttf', 19)
F_S = ImageFont.truetype(FONTS + 'ShareTechMono-Regular.ttf', 22)
F_TITLE = ImageFont.truetype(FONTS + 'Anton-Regular.ttf', 44)

# (title, before file, after file, box or None, [(status, text), ...])
ROWS = [
    ('1.1  1.8  2.13  enemy cells, kill marks, Adjuster',
     'final_p1_decide.png', 'final/p1_decide.png', (420, 430, 1000, 960),
     [('FIXED', '1.1 occupied glass L* 43.1-44.2 (NOW), 38.6-39.2 (+1), 34.0-34.8 (+2) vs brightest empty on the plate 20.5 (+1) / 16.8 (+2); lowest gated ratio 3.15 with the skin probe cells (was 29.7 vs 30.1)'),
      ('FIXED', '1.8 dying cell = CELL_PINK L7 hatch, kill X pink; 0 GAIN px on kill marks'),
      ('FIXED', '2.13 solid gold track, square segments, no beads; 0 of 2860 px covered')]),
    ('1.2  2.9  2.15  2.12  value order, clock, tower, FAR',
     'final_p1_decide.png', 'final/p1_decide.png', (380, 60, 980, 560),
     [('FIXED', '1.2 reviewer boxes: THIS TURN tape p95 82.4 -> 61.2, sweep 93.4 -> 74.3; HOT class p95 94.2 second under SEND IT 98.2; token disc class 84.7 (box was 100)'),
      ('FIXED', '2.9 one gunmetal #6E7580, K median L* 47.8; orange on the live step only'),
      ('FIXED', '2.15 slice ink median L* 62.7-70.4, tower p95 89.5 (was 96.1 / 95.4); squint 59-69 % loud, reported, designer'),
      ('FIXED', '2.12 FAR marks carry Anton 19 numbers'),
      ('NOT', 'new: bezel cube glyphs (x 981-994 y 563-578 etc.) L* 99 and 1 px ring / band lines L* 95-100 sit above HOT 94.2, outside every check-b class')]),
    ('1.3  1.4  Solace skin',
     'final_p1_decide_solace.png', 'final/p1_decide_solace.png', (40, 520, 560, 1040),
     [('DOC', '1.3 DR-6 recorded (ART_BIBLE 2.4 note). IMPL: cell fills neutral slate, corp hue on rim, lip, crest, cell edges only'),
      ('FIXED', 'occupied 43.4-44.2 vs empty <= 19.4; lowest gated ratio 3.32; leaf #96FF46 vs GAIN dE76 36.3')]),
    ('1.4  Meridian skin, COLD',
     'final_p1_decide_meridian.png', 'final/p1_decide_meridian.png', (40, 520, 560, 1040),
     [('FIXED', '1.4 COLD vs every skin cell dE76 >= 45.1; lowest gated cell ratio 4.12; rust is the rim and lip only')]),
    ('1.5  3.5  3.7  3.8  3.14  HUD bill (p2)',
     'final_p2_preview.png', 'final/p2_preview.png', (1070, 0, 1910, 460),
     [('FIXED', '1.5 labels Mono 23 (cap 16.1 px); counts are Anton 24 / 22 digits + tally; NEXT COLD at 70 %; SPLIT written ABSORBED + SOAK + YOU'),
      ('FIXED', '3.5 atlas Heat glyph; 3.7 WITHOUT TWIST "2 -> 1"; 3.8 neutral BEST LINE + star; 3.14 YOU 13.6 x 22 px, 2-way hatch')]),
    ('2.14  wave tickets (DR-1 keeps them)',
     'final_p1_decide.png', 'final/p1_decide.png', (0, 0, 340, 110),
     [('DOC', '2.14 tickets stay (DR-1); "full value" = K type L* 84'),
      ('FIXED', 'W tag Mono 23, glyph ink 23-27 px, p90 L* 86-88; count shown once (WAVES 6 LEFT)'),
      ('PART', 'minor, new: on W6 the hazard-tick ink key notches the bomb glyph\'s two width pips (x 33-47, y 84-89), every plate')]),
    ('2.5  board pencil (p2 Trigger path)',
     'final_p2_preview.png', 'final/p2_preview.png', (180, 500, 700, 900),
     [('NOT', '2.5 on the board: the p2 / p3 Trigger path and X caps are 2-4 px vector yellow (ridge width), wax L* std 1-3; A.5 asks 7 px wax + 3 px ink + grain. Fixed on hover only (7.0-7.35 px)')]),
    ('2.6  2.7  2.2  hand on p2',
     'final_p2_preview.png', 'final/p2_preview.png', (900, 700, 1920, 1080),
     [('FIXED', '2.6 board: lifted Trigger covers 0 px of Brace / Spin 3 / Twist cost hex and rules; 0 px under SEND IT and UNDO'),
      ('FIXED', '2.7 lowest hand px y 1067 (12 px margin); 2.2 TOWER teal / WAVE lilac plates')]),
    ('3.6  3.8  3.11  resolve log, REFUND (p3)',
     'final_p3_resolve.png', 'final/p3_resolve.png', (1070, 280, 1910, 700),
     [('FIXED', '3.11 log Mono 23, cap >= 16.1 px, digits before tallies; 3.6 REFUND is a tab under the RAM coin on the HUD; 3.8 neutral chips')]),
    ('2.3  played slots (p3)',
     'final_p3_resolve.png', 'final/p3_resolve.png', (900, 760, 1920, 1080),
     [('FIXED', '2.3 flat, upright torn dark-paper liners with a paper rim and ghost glyph; name over PLAYED in Mono 21; no cage, no skew')]),
    ('2.1  2.2  3.1  3.2  3.3  3.4  card sheet',
     'final_card_sheet.jpg', 'final/card_sheet.jpg', None,
     [('DOC', '2.1 DR-8 (one technique per card band); 3.4 DR-5 (no reserved fill colours)'),
      ('FIXED', '2.2 TOWER #006E66, WAVE #B4AAFF, Spin 3 band #FF00F0; min dE76 30.8 to any token or slice ink (was 2.0 / 6.5 / 0.0)'),
      ('FIXED', '3.1 HOLD clamp; 3.2 Firewall brick-fire, Twist ring bands; 3.3 NO RAM tab + padlock at full value')]),
    ('2.4  3.9  h03 Trigger hover',
     'hover_h03_trigger.png', 'hover/h03_trigger.png', None,
     [('FIXED', '2.4 no second HUD; 3.9 one RAM treatment (0 px of pencil / ring on coins)'),
      ('NOT', 'h03 x2 fail check a on one cell: the dying NOW Packet under a tracer reads 2.62:1 (board renderer, no board plate shows this state)')]),
    ('2.5  2.6  3.13  h02 Brace hover',
     'hover_h02_brace.png', 'hover/h02_brace.png', None,
     [('FIXED', '3.13 five non-aimed slices dimmed to luma ratio 0.394-0.397; 2.5 pencil wax 7.0-7.35 px, ink 3.0-3.2 px, grain std 3.9-6.2'),
      ('NOT', '2.6 on h02 x4: slot-0 lift covers 24,980 px more of the resting faces than the board fan; designer call (a) or (b)')]),
    ('2.6  h05 Strike hover',
     'hover_h05_strike.png', 'hover/h05_strike.png', None,
     [('FIXED', '2.6 on h01, h03-h11 (22 of 26 plates): 0 px under or within 2 px of SEND IT / UNDO; lifted card 0 px on siblings')]),
    ('1.6  2.10  3.10  block vs break',
     'effects_fx_block_vs_break.png', 'effects/fx_block_vs_break.png', None,
     [('FIXED', '1.6 every effect under the HUD (0 px above) except hp_through, refund, trace_add'),
      ('FIXED', '3.10 P stock #F6C8DE L* 85.1, dE76 24.2 from PAPER; 2.10 damage > kill > block > state on all 3 skins (thinnest: soak 841 > hold 761)')]),
    ('2.10  C corp effects',
     'effects_fx_C_corp.png', 'effects/fx_C_corp.png', (0, 0, 1920, 1000),
     [('FIXED', '2.10 grow 650 -> 400 ms, one scan line + 4-frame flash on the new chevron; ward_on 750 -> 400 ms, no slab, no pulse')]),
    ('2.11  resolve beat',
     'effects_resolve_beat_strip.jpg', 'effects/resolve_beat_strip.jpg', None,
     [('FIXED', '2.11 beat 3800 ms with skip (was 12.7 s); every effect <= 600 ms, no override; flash worst tile 3 / s (limit)')]),
    ('2.8  room (neutral, bio lab)',
     'final_p1_decide.png', 'final/p1_decide.png', (1040, 420, 1920, 820),
     [('DOC', '2.8 camera: DR-9 cutaway (ART_BIBLE 3.14 note)'),
      ('FIXED', 'room gate mean L* 31.2-32.2; reviewer box mean 21.3 -> 34.4; seam: one blur ramp, 30 % city chroma'),
      ('PART', 'as seen with the UI scrim on p2 / p3: 24.7-25.6, under 28 (art-pass DOC call, not a designer ruling)')]),
    ('2.8  Meridian room',
     'backdrop_p1_bio_meridian.png', 'backdrop/p1_shop_meridian.png', (1040, 420, 1920, 820),
     [('FIXED', '2.8 Meridian fights in the shop under an amber corp light (was the Solace bio lab); mean L* 32.2')]),
    ('1.7  3.12  transitions',
     'transitions_sheet.jpg', 'transitions/sheet.jpg', None,
     [('FIXED', '1.7 no CONCEPT badge on any frame; T5 K1 frame mean L* 28.2 (was black, 20.1)'),
      ('FIXED', '3.12 bits take their source colour (L* 55-80), white-hot 80 ms'),
      ('NOT', 'T6 pull-out iris not composited (fails the tile flash test); worst tile at the 3 / s limit')]),
]


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def panel(path, box):
    im = Image.open(path).convert('RGB')
    if box:
        im = im.crop(box)
    s = min(PW / im.width, PH_MAX / im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS), s


def main():
    tmp = Image.new('RGB', (10, 10))
    dt = ImageDraw.Draw(tmp)
    blocks = []
    for title, bf, af, box, notes in ROWS:
        b, sb = panel(BEFORE + bf, box)
        a, sa = panel(LOCKED + af, box)
        lines = []
        for st, txt in notes:
            ls = wrap(dt, txt, F_T, LW - 40)
            lines.append((st, ls))
        text_h = 12 + 38 * len(wrap(dt, title, F_H, LW - 2 * GAP)) + sum(26 * len(ls) + 10 for _, ls in lines)
        h = max(b.height, a.height, text_h) + 40
        blocks.append((title, b, a, sb, sa, box, lines, h))
    W = LW + 2 * PW + 4 * GAP
    head = 150
    H = head + sum(bl[-1] for bl in blocks) + GAP
    sheet = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((GAP, 18), 'REBEL_CELL combat rebuild vs AD review 2026-11-02: before (090ad870) | after (published 2026-11-04)', font=F_TITLE, fill=INK)
    d.text((GAP, 84), 'Labels = AD_REVIEW finding numbers. FIXED green, DOC (ruling recorded) violet, PART amber, NOT FIXED / new defect red. '
           'Values are CIE L* (sRGB luminance) measured on the published PNGs; crops scaled to fit, scale shown.', font=F_S, fill=DIM)
    y = head
    for title, b, a, sb, sa, box, lines, h in blocks:
        d.line((GAP, y - 6, W - GAP, y - 6), fill=(50, 52, 64), width=2)
        tl = wrap(d, title, F_H, LW - 2 * GAP)
        for i, ln in enumerate(tl):
            d.text((GAP, y + 4 + 38 * i), ln, font=F_H, fill=INK)
        ty = y + 12 + 38 * len(tl)
        for st, ls in lines:
            key = 'NOT' if st == 'NOT' else st
            d.rectangle((GAP, ty + 4, GAP + 12, ty + 16), fill=COL[key])
            for i, ln in enumerate(ls):
                d.text((GAP + 22, ty + 26 * i), ln, font=F_T, fill=INK if i == 0 else (205, 206, 214))
            ty += 26 * len(ls) + 10
        x0 = LW + 2 * GAP
        x1 = x0 + PW + GAP
        bx = f' box {box}' if box else ' whole'
        d.text((x0, y + 4), f'BEFORE 090ad870{bx}  x{sb:.2f}', font=F_S, fill=DIM)
        d.text((x1, y + 4), f'AFTER now{bx}  x{sa:.2f}', font=F_S, fill=DIM)
        sheet.paste(b, (x0, y + 32))
        sheet.paste(a, (x1, y + 32))
        y += h
    sheet.save(OUT, quality=88, optimize=True)
    print(OUT, sheet.size, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()
