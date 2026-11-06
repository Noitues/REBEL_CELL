"""motion.png: 4-frame idle and travel cycle per head at 128 px and at game size (44 px on the city, 3x)."""
from common import *

CELL = 180
FR = (0.0, 0.5, 1.0, 1.5)
AMP = {'idle': 0.35, 'travel': 1.0}


def cell_dark(t, f, amp, size, ang=0):
    im = Image.new('RGBA', (CELL, CELL), (30, 24, 50, 255))
    d = ImageDraw.Draw(im)
    for g in range(0, CELL, 30):
        d.line([(g, 0), (g, CELL)], fill=(38, 32, 62))
        d.line([(0, g), (CELL, g)], fill=(38, 32, 62))
    d.line([(0, CELL // 2), (CELL, CELL // 2)], fill=(60, 50, 96))
    paste_head(im, head(t, f, amp), CELL // 2, CELL // 2, size, ang, t)
    return im


def cell_game(t, f, amp, size, ang, j):
    S = 3
    n = CELL // S
    base = crop(PLATE, CROP_GAME[0] + 30 + j * 15, CROP_GAME[1] + 10, n, n)
    paste_head(base, head(t, f, amp), n // 2, n // 2, size, ang, t)
    return up(base, S)


def main():
    cols = 8
    gap = 14
    W = cols * CELL + (cols - 1) * 2 + gap + 20
    rows = []
    hd = Image.new('RGB', (W, 90), BG)
    d = ImageDraw.Draw(hd)
    d.text((20, 6), 'H6 MOTION  |  4-frame idle and travel cycle per head', font=F(FONT_T, 34), fill=(120, 230, 255))
    d.text((20, 52), 'idle = 35 % amplitude, travel = 100 %. Frames are f = 0, .5, 1, 1.5 of a full cycle (smooth loop). Cells 1: 128 px on the grid.  Cells 2: 44 px game size on the city, 3x nearest, heading -26 deg.', font=F(FONT_M, 13), fill=(235, 235, 250))
    d.text((20, 70), 'D worm: S-wave runs tail to head, head and dot steady.  N claw: pincers open/close, hub steady.  E mine: alternate spikes pulse, lead spike longest, ring steady.  4th beetle: antennae sweep.', font=F(FONT_M, 13), fill=(190, 200, 225))
    rows.append(hd)
    for t in TYPES:
        for size, game in ((128, False), (CHOSEN, True)):
            tit = NAMES[t] + ('   |   128 px' if not game else f'   |   game size {CHOSEN} px')
            rows.append(label_row(tit + '   idle f0 f1 f2 f3  |  travel f0 f1 f2 f3', W, 24))
            row = Image.new('RGB', (W, CELL), BG)
            x = 0
            for mode in ('idle', 'travel'):
                for j, f in enumerate(FR):
                    c = cell_game(t, f, AMP[mode], size, -26, j) if game else cell_dark(t, f, AMP[mode], size)
                    row.paste(c.convert('RGB'), (x, 0))
                    x += CELL + 2
                x += gap - 2
            rows.append(row)
    out = stack(rows, W)
    out.save(os.path.join(OUT, 'motion.png'))
    print(out.size)


if __name__ == '__main__':
    main()
