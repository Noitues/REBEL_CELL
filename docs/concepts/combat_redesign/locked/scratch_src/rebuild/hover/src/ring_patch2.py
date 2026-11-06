p = 'hv_core.py'
s = open(p, encoding='utf-8').read()
s = s.replace("""    if 'hud_hero' in MASKS:
        forb |= Z.hero_core()
    if 'you' in YOU_MASK:
        forb |= YOU_MASK['you']
    return ndi.binary_dilation(forb, iterations=1)""", """    if 'hud_hero' in MASKS:
        forb |= MASKS['hud_hero']          # the digit with its black keyline: the ring's ink never merges with the digit's keyline
    if 'you' in YOU_MASK:
        forb |= YOU_MASK['you']
    return ndi.binary_dilation(forb, iterations=1)""", 1)
s = s.replace("    hm = Z.hero_core() if 'hud_hero' in MASKS else None\n    for key, seed in (('through', 3), ('lands', 4)):",
              "    hm = MASKS['hud_hero'] if 'hud_hero' in MASKS else None\n    for key, seed in (('through', 3), ('lands', 4)):", 1)
s = s.replace("            sub = hm[int(cy - 40):int(cy + 40), int(x0 - 2):int(x0 + wd + 2)]\n            ys_, xs_ = np.nonzero(sub)\n            if ys_.size:\n                box = (x0 - 2 + xs_.min(), cy - 40 + ys_.min(), x0 - 2 + xs_.max() + 1, cy - 40 + ys_.max() + 1)",
              "            sub = hm[int(cy - 44):int(cy + 44), int(x0 - 4):int(x0 + wd + 4)]\n            ys_, xs_ = np.nonzero(sub)\n            if ys_.size:\n                box = (x0 - 4 + xs_.min(), cy - 44 + ys_.min(), x0 - 4 + xs_.max() + 1, cy - 44 + ys_.max() + 1)", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count("MASKS['hud_hero']"))
