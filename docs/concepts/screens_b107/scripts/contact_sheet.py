"""screens_b107/sheet.jpg: every B-107 plate on one page, labelled. Run: python contact_sheet.py"""
import os
from PIL import Image, ImageDraw, ImageFont

R = 'D:/rc_art/art-pass/docs/concepts/screens_b107/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
ROWS = [
    ('RAID (brief a-e + result), one design with the vertical slice raid look brief', [
        ('raid/raid_a_review_route.png', '1 REVIEW = (a) route announced'),
        ('raid/raid_b_setup_armory.png', '2 SHOP + 3 PLACE = (b) armory'),
        ('raid/raid_c_round_running.png', '4 EXECUTE = (c) round running'),
        ('raid/raid_d_site_falls.png', '(d) site falls, raid walks on'),
    ]),
    ('', [
        ('raid/raid_e_hq_stop.png', '(e) HQ stop, -1 per unit in'),
        ('raid/raid_f_result_held.png', '5 RESULT held'),
        ('raid/raid_f_result_lost.png', '5 RESULT lost: TARGET ACQUIRED'),
        ('raid/raid_marks.png', 'raid mark sheet'),
    ]),
    ('HQ WORKSHOP over hq_idle . ADVANCE (T5) . BLOCK SERVER v2', [
        ('hq_recruit.png', 'RECRUIT'), ('hq_weapons.png', 'WEAPONS'), ('hq_talents.png', 'TALENTS'),
        ('advance_choice.png', 'T5 advance: STAY / GO'),
    ]),
    ('', [
        ('block_server_v2.png', 'BLOCK SERVER v2'), ('block_server_v2_beaten.png', 'BLOCK SERVER v2 beaten'),
        ('block_server_kit.png', 'BLOCK SERVER kit breakdown'),
    ]),
]
TW, TH, G, MX = 560, 315, 22, 30


def main():
    af = ImageFont.truetype(FD + 'Anton-Regular.ttf', 34)
    lf = ImageFont.truetype(FD + 'IBMPlexSansCondensed-Medium.ttf', 22)
    hf = ImageFont.truetype(FD + 'Anton-Regular.ttf', 26)
    h = 90 + sum((44 if t else 0) + TH + 40 + G for t, _ in ROWS)
    W_ = MX * 2 + 4 * TW + 3 * G
    S = Image.new('RGB', (W_, h), (14, 15, 20)); d = ImageDraw.Draw(S)
    d.text((MX, 22), 'B-107 screens (DRAFT, art concept plates, 2026-11-16): raid, HQ workshop, advance, BLOCK SERVER v2', font=af, fill=(212, 255, 0))
    y = 90
    for title, items in ROWS:
        if title:
            d.text((MX, y), title, font=hf, fill=(255, 176, 0)); y += 44
        for k, (f, lab) in enumerate(items):
            x = MX + k * (TW + G)
            im = Image.open(R + f).convert('RGB')
            im.thumbnail((TW, TH), Image.LANCZOS)
            S.paste(im, (x + (TW - im.width) // 2, y + (TH - im.height) // 2))
            d.rectangle((x - 1, y - 1, x + TW, y + TH), outline=(70, 74, 90), width=2)
            d.text((x, y + TH + 8), lab + '   ' + os.path.basename(f), font=lf, fill=(230, 232, 240))
        y += TH + 40 + G
    S.save(R + 'sheet.jpg', quality=88)
    print('wrote sheet.jpg', S.size)


if __name__ == '__main__':
    main()
