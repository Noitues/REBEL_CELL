p = 'hv_plates.py'
s = open(p, encoding='utf-8').read()
old = """        hb = K.SNAP.get('hud_bottom') or A.INFO.get('hud_bottom') or 442
        x = INSET_X0
        for ins in insets:"""
new = """        hb = K.SNAP.get('hud_bottom') or A.INFO.get('hud_bottom') or 442
        # right-aligned under the HUD (the lifted card of a slot-0 / slot-1 hover rises at the left of the hand, under x ~1340)
        tot = sum(ins['crop'].width + 12 for ins in insets) + INSET_SEP * (len(insets) - 1)
        x = int(V.hud_box('bill')[2]) - tot + 6
        for ins in insets:"""
assert old in s
s = s.replace(old, new, 1)
s = s.replace("            x = box[2] + 22\n", "            x = box[2] + INSET_SEP + 6\n", 1)
s = s.replace("INSET_X0 = 1104\n", "INSET_SEP = 22             # px between two insets\n", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count('INSET_X0'))
