import re
p='d1_specimen.py'
s=open(p,encoding='utf-8').read()
i=s.index('def run(win):')
head=s[:i]
head=head.replace("def polaroid(img, crop, caption, cx, cy, rot, w=210, h=250):","def polaroid(img, crop, caption, cx, cy, rot, w=160, h=196):")
head=head.replace("font('hand', 22), (30, 60, 130, 255), 'mm')","font('hand', 17), (30, 60, 130, 255), 'mm')")
head=head.replace("im = CITY.crop(crop).resize((int((w - 28) * K), int((h - 78) * K))","im = CITY.crop(crop).resize((int((w - 28) * K), int((h - 66) * K))")
head=head.replace("rect(L, [24, 24, 10 + w - 14, 24 + h - 78], outline=INK, width=2)","rect(L, [24, 24, 10 + w - 14, 24 + h - 66], outline=INK, width=2)")
tail='''def run(win):
    img = bench()
    petri(img, 320, 305, 225, win)
    if win:
        rng = random.Random(4)
        cols = [CYAN, PINK, CELLY]
        x, y = 470, 478
        for i in range(30):
            x += rng.uniform(8, 20)
            y += rng.uniform(6, 16) * (1 if i < 10 else -0.2)
            rr = max(3, 11 - i * 0.28)
            ellipse(img, [x - rr, y - rr, x + rr, y + rr], fill=cols[i % 3], outline=INK, width=2)
        text(img, (60, 40), 'CELL-03  //  NOT CONTAINED', font('mono', 22), CELLY)
        sticker(img, 'REBEL_CELL', 190, 540, 230, 46, (255, 62, 160, 255), (20, 8, 20, 255), rot=-4, size=32)
    else:
        text(img, (60, 40), 'CELL-03  //  TREATED', font('mono', 22), LIME)
        sticker(img, 'STERILE', 190, 540, 200, 50, (150, 255, 70, 255), (14, 40, 10, 255), rot=3, size=36)
    polaroid(img, (1560, 40, 1900, 400), 'HOME SERVER' + (' 50/50' if win else ' 0/50'), 610, 190, -6)
    polaroid(img, (1320, 540, 1700, 880), 'BEACON', 690, 360, 3)
    polaroid(img, (480, 330, 880, 700), 'NODES AT THE END', 610, 520, -3)
    personnel(img, win, 30, 640, 700)
    report(img, win)
    if win:
        stamp(img, 'CONTAINMENT FAILED', 1400, 405, (205, 40, 50, 235), rot=-7, size=70)
        postit(img, (1550, 120, 1860, 290), (170, 226, 255, 245), 'contaminant is\nin the supply\nline. who left\nthe lid off?', rot=4, size=27)
        postit(img, (1620, 760, 1890, 940), (170, 255, 120, 245), 'it hums the\nSolace jingle.\nflag it.', rot=-4, size=26, fg=(30, 70, 40, 255))
    else:
        stamp(img, 'STERILE', 1400, 405, (30, 140, 40, 240), rot=-7, size=96)
        postit(img, (1560, 100, 1870, 270), (200, 255, 150, 245), 'all strains\naccounted for.\nlid sealed.', rot=3, size=27, fg=(30, 70, 40, 255))
        postit(img, (1630, 770, 1890, 930), (255, 226, 80, 245), 'they will be\nback. log the\nPHANTOM.', rot=-4, size=26)
    return img


if __name__ == '__main__':
    for win in (True, False):
        img = run(win)
        buttons(img, main_xy=(1470, 1030), new_xy=(1740, 1032))
        img = vignette(img, 0.35)
        finish(img, OUT + ('d1_win.png' if win else 'd1_lose.png'), 5, 1 if win else 2)
        print('ok', win)
'''
open(p,'w',encoding='utf-8').write(head+tail)
