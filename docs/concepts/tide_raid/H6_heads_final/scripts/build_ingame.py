"""in_game.png: four heads at 40/44/48 on the real city (normal/deutan/tritan), 4 px blur, leading a ribbon, card tab, 1280 row."""
from common import *

PW = 300
S2 = 2


def sizes_panel(sizes, k=1.0, pl=None):
    pl = pl if pl is not None else plate_at(k)
    rowh = int(58 * (1 if k == 1.0 else 1))
    rows = [(s, -26) for s in sizes] + [(sizes[1], 154)]
    im = crop(pl, int(CROP_GAME[0] * k), int(CROP_GAME[1] * k), PW, rowh * len(rows) + 6)
    for r, (sz, ang) in enumerate(rows):
        y = 30 + r * rowh
        for i, t in enumerate(TYPES):
            paste_head(im, head(t), 38 + i * 74, y, sz, ang, t)
    return im


def row3(rows, W, title, panel, blur=False):
    rows.append(label_row(title, W))
    row = Image.new('RGB', (W, panel.height * S2), BG)
    for j, v in enumerate(VIS):
        p = vis(panel, v)
        if blur:
            p = squint(p)
        row.paste(up(p, S2), (j * (PW * S2 + 20), 0))
    rows.append(row)


def main():
    W = PW * S2 * 3 + 60
    rows = []
    hd = Image.new('RGB', (W, 96), BG)
    d = ImageDraw.Draw(hd)
    d.text((20, 6), 'H6 HEADS IN GAME  |  D drone (worm)  N netrunner (thorn claw)  E enforcer (sea-mine, 15% smaller)  4th beetle (grey)', font=F(FONT_T, 34), fill=(120, 230, 255))
    d.text((20, 54), f'1920 raid view, real city plate (plan_placed). Head size = N footprint px (D long axis); E and X4 are 0.852 of it. Chosen size {CHOSEN} px, test range 40 / 44 / 48. All crops 2x nearest.', font=F(FONT_M, 14), fill=(235, 235, 250))
    d.text((20, 74), 'Rows of heads in each size panel: 40 px, 44 px, 48 px heading up-right (iso -26 deg), then 44 px heading down-left (154 deg).', font=F(FONT_M, 14), fill=(190, 200, 225))
    rows.append(hd)
    sp = sizes_panel((40, 44, 48))
    row3(rows, W, 'SIZES 40 / 44 / 48 px at 1920   |   normal  |  deutan  |  tritan', sp)
    row3(rows, W, '4 px BLUR of the same crops   |   normal  |  deutan  |  tritan', sp, blur=True)
    rb = head_on_ribbon_panel(crop(PLATE, CROP_RIB[0], CROP_RIB[1], PW, 220), CHOSEN)
    row3(rows, W, f'LEADING A RIBBON at {CHOSEN} px head, ribbon {CHOSEN*.35:.0f} px, type pattern D chain, N braid, E chevrons, 4th ticks   |   normal | deutan | tritan', rb)
    row3(rows, W, 'RIBBON at 4 px BLUR', rb, blur=True)
    cp = card_panel()
    row3(rows, W, 'CARD-TAB GLYPH 22 px: ink silhouette on the type tab (no outline, detail cut in the tab hue; E armour ring survives)   |   normal | deutan | tritan', cp)
    # 1280 scale row
    k = K1280
    pl = plate_at(k)
    s1280 = [round(s * k) for s in (40, 44, 48)]
    p1280 = sizes_panel(s1280, k, pl)
    row3(rows, W, f'1280x720 SCALE: heads {s1280[0]} / {s1280[1]} / {s1280[2]} px (= 40/44/48 x .667), plate downscaled, same layout (details under 40 px nominal, E ring + beetle split, switch off)   |   normal | deutan | tritan', p1280)
    rb2 = head_on_ribbon_panel(crop(pl, int(CROP_RIB[0] * k), int(CROP_RIB[1] * k), PW, 220), round(CHOSEN * k), k=k)
    row3(rows, W, f'1280 RIBBON, head {round(CHOSEN*k)} px, ribbon {CHOSEN*k*.35:.0f} px', rb2)
    out = stack(rows, W)
    out.save(os.path.join(OUT, 'in_game.png'))
    print(out.size)


if __name__ == '__main__':
    main()
