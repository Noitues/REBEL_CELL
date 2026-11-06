"""O-29 fix 3: hand kept outside wheel radius 455 (scale 1.10, step 170, shifted right 55 and down 20; hover push 16 so the last card clears UNDO)"""
P = 'D:/rc_scratch/combat_redesign/locked/corp/src/f1_hand.py'
s = open(P, newline='').read()
old = "CARD_SCALE = 1.15\nFAN_DEG = 4.0\nSTEP = 182\nLEFT_CX = 962\nCY0 = 910\nLIFT_S = 1.10\nLIFT_CY = 856\nHOV_PUSH = 30\n"
new = ("# O-29 fix 3: the hand stays outside wheel radius HAND_MIN_R (asserted in asm_checks).  Was 1.15 / 182 / 962 / 910 / push 30.\n"
       "HAND_MIN_R = 455.0\nCARD_SCALE = 1.10\nFAN_DEG = 4.0\nSTEP = 170\nLEFT_CX = 1017\nCY0 = 930\nLIFT_S = 1.10\nLIFT_CY = 866\nHOV_PUSH = 16\n")
nl = '\r\n' if '\r\n' in s else '\n'
assert s.count(old.replace('\n', nl)) == 1
open(P, 'w', newline='').write(s.replace(old.replace('\n', nl), new.replace('\n', nl)))
print('ok')
