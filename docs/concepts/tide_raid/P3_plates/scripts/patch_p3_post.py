s = open('p2_post.py').read()
s = s.replace("P1D = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P1_plates/plates/'", "P1D = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P2_plates/plates/'")
s = s.replace("d.text((8, 6), 'P1 - ' + title", "d.text((8, 6), 'P2 - ' + title").replace("'P2 golden plate - ' + title", "'P3 golden plate - ' + title")
s = s.replace("compare/%s_P1_vs_P2.jpg", "compare/%s_P2_vs_P3.jpg")
# P2 plates are keyed NN_beat; compare file name = key
s = s.replace("if os.path.exists(P1D + key + '.png'):", "if os.path.exists(P1D + key + '.png'):   # P2 plate of the same key")
# tier strip: crop around ring AND tile (tile sits 56 px above the tower top)
s = s.replace("""        b = w.sites[sid]['B'] / 6.0
        cx, cy = b[0], b[1] - 14
        box = (int(cx - 19), int(cy - 20), int(cx + 19), int(cy + 20))
        c = g320.crop(box).resize((228, 240), Image.NEAREST).convert('RGB')""", """        b = w.sites[sid]['B'] / 6.0
        cx, cy = b[0], b[1] - 30
        box = (int(cx - 19), int(cy - 20), int(cx + 19), int(cy + 20))
        c = g320.crop(box).resize((228, 240), Image.NEAREST).convert('RGB')""")
open('p2_post.py', 'w').write(s)
