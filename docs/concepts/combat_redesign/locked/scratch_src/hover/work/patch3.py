p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_core.py'
s = open(p, encoding='utf-8').read()
s = s.replace("HL.alpha_layer(", "alpha_img(")
s = s.replace("def ghost_units(", '''def alpha_img(im, a):
    im = im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    return im


def ghost_units(''', 1)
open(p, 'w', encoding='utf-8').write(s)
print(s.count('alpha_img('))
