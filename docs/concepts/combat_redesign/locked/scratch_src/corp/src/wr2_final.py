import sys, os, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr2_sheets as S
import wr2_config as C2
import wr_config as CFG, wr_crops as CR
from wr2_run import LABOF
from PIL import Image, ImageDraw
D = S.DEST
os.makedirs(D + 'crops', exist_ok=True)
res = {}
for eid in CFG.ORDER:
    label, st, specs = CR.STATES[eid][0]
    state = LABOF[eid] if st == 'lab' else st
    sp = [s for s in specs if s[0] != 'gproof']
    has_v = C2.EL2[eid][2] != '-'
    vers = [('R1', 'R1'), ('R2', 'R')] + ([('V_' + eid, 'V')] if has_v else [])
    for ver, tag in vers:
        if eid in ('unit_screen_bezel', 'unit_screen_code_text', 'screen_motif_skull') and ver != 'R2':
            continue
        im = S.crops(ver, state, sp, min(2.0, S.fit(sp, 3)))
        p = D + 'crops/%s_%s.png' % (eid, tag)
        im.save(p)
        res['%s_%s' % (eid, tag)] = p
json.dump(res, open('D:/rc_scratch/e10_design/wave_rings/out2/crops_r2.json', 'w'), indent=1)
# removed elements sheet: E10 vs R2
E10 = Image.open('D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png').convert('RGB')
R2p = Image.open(S.OUT2 + 'pl_R2_p1.png').convert('RGB')
boxes = [('unit_screen_bezel: cell ends 9 o clock', (170, 500, 330, 620)), ('unit_screen_bezel: inside a wide +2 cell', (430, 800, 650, 900)),
         ('unit_screen_code_text: +1 Packet next to the token', (370, 255, 560, 345)), ('unit_screen_code_text: +2 Packet sector 5', (190, 330, 350, 450)),
         ('screen_motif_skull: Payload screen 8 o clock', (330, 700, 500, 820))]
sh = Image.new('RGB', (1500, 60 + 330 * len(boxes)), S.BG)
d = ImageDraw.Draw(sh)
d.text((12, 8), 'REMOVED ELEMENTS (bezel corners, code text, programme skull): E10 vs R2', font=S.F_T, fill=(255, 255, 255))
y = 56
for lab, b in boxes:
    d.text((12, y), lab, font=S.F_L, fill=(230, 235, 245)); y += 28
    w, h = b[2] - b[0], b[3] - b[1]
    sc = min(2.5, 700 / w, 290 / h)
    for i, (nm, im) in enumerate((('E10 approved', E10), ('R2 (removed / none)', R2p))):
        c = im.crop(b).resize((int(w * sc), int(h * sc)), Image.LANCZOS)
        sh.paste(c, (10 + i * 740, y))
        d.text((14 + i * 740, y + 2), nm, font=S.F_S, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    y += 300
sh.crop((0, 0, 1500, y)).save(D + 'sheet_removed_elements.jpg', quality=88)
print(len(res))
