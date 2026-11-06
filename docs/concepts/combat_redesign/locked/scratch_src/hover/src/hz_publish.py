"""hz_publish: copy the plates to locked/hover/, build contact_sheet.jpg (all 11 at small size + the key) and checks.json (every chk/*.json summarised + full)."""
import sys, os, json, shutil, glob
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

SRC = 'D:/rc_scratch/combat_redesign/locked/hover/'
DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/hover/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
os.makedirs(DST, exist_ok=True)
NAMES = ['h01_tower_turn', 'h02_brace', 'h03_trigger', 'h04_twist', 'h05_strike', 'h06_shove', 'h07_pull', 'h08_hold', 'h09_firewall', 'h10_soak', 'h11_unit']
TITLE = {'h01_tower_turn': 'SPIN 3 | SPIN 2 | NUDGE', 'h02_brace': 'BRACE', 'h03_trigger': 'TRIGGER', 'h04_twist': 'TWIST', 'h05_strike': 'STRIKE', 'h06_shove': 'SHOVE',
         'h07_pull': 'PULL', 'h08_hold': 'HOLD', 'h09_firewall': 'FIREWALL', 'h10_soak': 'SOAK (no card)', 'h11_unit': 'UNIT HOVER'}


def font(name, px):
    for f in glob.glob(FD + '*'):
        if f.lower().endswith('.ttf') and name.lower() in os.path.basename(f).lower():
            return ImageFont.truetype(f, px)
    return ImageFont.load_default()


def main():
    files = sorted(glob.glob(SRC + 'out/h*.png'))
    for f in files:
        shutil.copy(f, DST + os.path.basename(f))
    # contact sheet: 4 columns x 3 rows (11 plates + key), 640 x 360 each
    tw, th, pad, top = 640, 360, 16, 46
    cols, rows = 4, 3
    sheet = Image.new('RGB', (cols * (tw + pad) + pad, 110 + rows * (th + top + pad)), (8, 10, 22))
    d = ImageDraw.Draw(sheet)
    an, mo = font('anton', 44), font('mono', 22)
    an2 = font('anton', 28)
    d.text((pad, 18), 'HOVER PLATES  |  final locked board (neutral), one per card effect type', font=an, fill=(242, 246, 255))
    d.text((pad + 2, 76), 'dim value x0.40 chroma x0.45  |  ghosts and landings from the sim plan  |  corners = focus, PLAN arrow = movement, hatch = lost at END TURN', font=mo, fill=(175, 192, 214))
    items = NAMES + ['h00_key']
    for i, nm in enumerate(items):
        p = SRC + 'out/' + nm + '.png'
        if not os.path.exists(p):
            continue
        c, r = i % cols, i // cols
        x, y = pad + c * (tw + pad), 110 + r * (th + top + pad)
        d.text((x, y + 4), TITLE.get(nm, 'GRAMMAR KEY'), font=an2, fill=(242, 246, 255))
        d.text((x + tw - 4, y + 12), nm[:3], font=mo, fill=(175, 192, 214), anchor='ra')
        im = Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (x, y + top))
    sheet.save(DST + 'contact_sheet.jpg', quality=90)
    chk = {}
    for f in sorted(glob.glob(SRC + 'chk/*.json')):
        chk[os.path.basename(f)[:-5]] = json.load(open(f))
    summ = {}
    for k, v in chk.items():
        c = v['collisions']
        summ[k] = dict(asserts='%d/%d' % (v['asserts']['passed'], v['asserts']['total']),
                       inset_asserts=['%s %d/%d' % (i['name'], i['asserts']['passed'], i['asserts']['total']) for i in v.get('insets', [])],
                       mark_pairs=c['mark_pairs_pass'], occlusion=c['occlusion_pass'], hover_vs_marks=c['hover_vs_marks_pass'],
                       hover_vs_marks_px={a: b for a, b in c['hover_vs_marks_px'].items() if b}, hand_vs_board=c['hand_vs_board'].get('pass'),
                       hand_min_r=c['hand_vs_board'].get('hand_min_r_px'), lift_dx=v.get('lift_dx'), dashes=v['dash_calls'], dots=v['dot_calls'],
                       alnum_text_nowords=v.get('alnum_text_calls'), squint_plate=v['squint']['plate'], squint_tower=v['squint']['tower'],
                       lit_vs_dim=v['squint']['lit_vs_dim'], bill=v['bill'])
    allp = dict(draw_asserts=all(v['asserts']['passed'] == v['asserts']['total'] and all(i['asserts']['passed'] == i['asserts']['total'] for i in v.get('insets', [])) for v in chk.values()),
                mark_pairs=all(v['collisions']['mark_pairs_pass'] for v in chk.values()), occlusion=all(v['collisions']['occlusion_pass'] for v in chk.values()),
                hover_vs_marks=all(v['collisions']['hover_vs_marks_pass'] for v in chk.values()),
                hand=all(v['collisions']['hand_vs_board'].get('pass') for v in chk.values()),
                dashes=all(v['dash_calls'] == 0 and v['dot_calls'] == 0 for v in chk.values()),
                nowords_text=all(not v.get('alnum_text_calls') for v in chk.values() if not v['words']))
    json.dump(dict(all_pass=allp, summary=summ, notes=dict(
        squint='1/16 BOX downscale + 1 px blur, luma; loud = share of 16 px cells above 0.38; lit_vs_dim = mean luma of lit cells / dim cells',
        hover_vs_marks='hover marks (corners, PLAN arrows, pencil, bursts), ghosts and insets vs digits, labels, tags, badges, tickets, leader, tape, plates and hand: 0 px required',
        units_arcs='hover over units and arcs is reported as info (hover_over_units_arcs_px_info), since corners and arrows sit on cells by design'),
        full=chk), open(DST + 'checks.json', 'w'), indent=1, default=str)
    print('published', len(files), 'plates; all_pass', allp)


if __name__ == '__main__':
    main()
