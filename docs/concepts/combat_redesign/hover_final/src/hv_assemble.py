"""hv_assemble: builds D:/rc_art/.../combat_redesign/hover_final from out/v2 (+ key.png, + v2_F1/v2_F2 lifts)"""
import sys, os, json, shutil
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
import hv_final as HF

IN, OUT = HF.IN, HF.OUT
os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT + 'slips', exist_ok=True)
meta = json.load(open(IN + 'slips.json'))
bump = meta.get('bump_xy')
SRC = {'h01_tower_turn': 'h01', 'h02_brace': 'h02', 'h03_trigger': 'h03', 'h04_twist': 'h04', 'h05_strike': 'h05', 'h06_shove': 'h06', 'h07_pull': 'h07',
       'h08_hold': 'h08', 'h09_firewall': 'h09', 'h10_soak': 'h10', 'h11_unit': 'h11'}
RULE = {
    'h01_tower_turn': 'The tower is drawn at its plan angle; one PLAN arrow round the hub turns the right number of sectors; guns, tracers and landing marks go to plan values. Spin 2 and Nudge are the two insets.',
    'h02_brace': 'Every slice gets lime corners (legal); the aimed slice gets thick corners and a clamp-plate ghost with the L10 double edge; a pencil bar sits on the landing arc that now stops.',
    'h03_trigger': 'Legal units get corners; PLAN arrows run the aimed unit inward down the sectors it resolves; pink hatch and burst on the victim; refund coin; pencil ring on TRACE. Inset: the refund after Twist.',
    'h04_twist': 'Rings +1 and +2 stay lit with the bezel; one PLAN arrow along the aimed ring; the twist pill on its tag; pencil-edged arcs show the landings after the turn.',
    'h05_strike': 'Every unit in range gets corners; the aimed unit gets thick corners, pink hatch on the HP it loses, a pink hit burst with speed lines, and its landing arc is gone.',
    'h06_shove': 'Veiled origin, ghost with a pencil edge at the new cell, one PLAN arrow along the ring, new landing arc. Inset: the bump, a burst at the shared edge and 1 HP hatched on each unit.',
    'h07_pull': 'Only the unit with a free inner cell is legal: veiled origin, ghost one ring in, one PLAN arrow inward; the rest of the board stays dim and takes no corners.',
    'h08_hold': 'The bezel and all rings stay lit; a PLAN arrow outside the bezel slides the step one slot later; a pencil outline marks the live cell that becomes HOLD; arcs recomputed.',
    'h09_firewall': 'Legal columns get corners, the aimed column is thick; a pink wash with pencil flame strokes marks the burn; bursts on the two units that step in and pink hatch on the HP they lose.',
    'h10_soak': 'No card: a slice soak toggle. Corners on every slice, thick on the hovered one; a SOAK funnel at the rim, its pip hatches in indigo; pencil ring on the new THROUGH and on the HP it saves.',
    'h11_unit': 'The kept p2b form: PLAN route arrow, thick corners on the cell, pencil rim arcs on the slices it lands on, the E10 hover tag on a pencil leader. Content parked (note 8).',
}
SUB = {'h01_tower_turn': 'turn the tower', 'h02_brace': 'protect a slice', 'h03_trigger': 'resolve a unit now', 'h04_twist': 'turn one ring', 'h05_strike': 'damage a unit',
       'h06_shove': 'move sideways', 'h07_pull': 'move inward', 'h08_hold': 'stop the rings', 'h09_firewall': 'burn a sector', 'h10_soak': 'soak toggle (no card)', 'h11_unit': 'inspect a unit'}
NM = {'h01_tower_turn': 'SPIN 3 | SPIN 2 | NUDGE', 'h02_brace': 'BRACE', 'h03_trigger': 'TRIGGER', 'h04_twist': 'TWIST', 'h05_strike': 'STRIKE', 'h06_shove': 'SHOVE', 'h07_pull': 'PULL',
      'h08_hold': 'HOLD', 'h09_firewall': 'FIREWALL', 'h10_soak': 'SOAK', 'h11_unit': 'UNIT HOVER'}

tiles = []
for pid, src in SRC.items():
    im = Image.open(IN + src + '.png').convert('RGB')
    meta_ = {'bump_xy': bump} if bump else {}
    im = HF.add_insets(pid, im, True, meta_)
    im.save(OUT + pid + '.png')
    sl = dict(meta[pid])
    if pid == 'h01_tower_turn':
        sl['lines'] = sl['lines'] + ['insets: SPIN 2 (two sectors) and NUDGE (one sector) are the same plate with a shorter arrow; the hand is swapped for them']
    if pid == 'h03_trigger':
        sl['lines'] = sl['lines'] + ['inset: TRIGGER AFTER TWIST (approved best line f2): the same hover with the refund live; the bill shows RAM returning']
    if pid == 'h06_shove':
        sl['lines'] = sl['lines'] + ['inset: SHOVE INTO A NEIGHBOUR, the bump: a burst at the shared edge, neither unit moves, 1 HP pink-hatched on each']
    HF.slip_frame(im, sl).save(OUT + 'slips/' + pid + '_slip.png')
    tiles.append((im, src, NM[pid], SUB[pid], RULE[pid]))
for pid, src in (('h01_tower_turn', 'h01_nw'), ('h02_brace', 'h02_nw'), ('h03_trigger', 'h03_nw'), ('h04_twist', 'h04_nw')):
    Image.open(IN + src + '.png').convert('RGB').save(OUT + pid + '_nowords.png')
key = None
if os.path.exists(IN + 'key.png'):
    kim = Image.open(IN + 'key.png').convert('RGB')
    kim.save(OUT + 'h00_key.png')
    key = (kim, 'key', 'GRAMMAR KEY', 'marks used on every plate', 'lit / dim, corners-only focus, PLAN arrow, pencil rings, ghost, hatch, lifted card, hit burst, drawn at use size.')
HF.sheet(tiles, key).save(OUT + 'hover_overview.png')
# lift styles
rows = []
for nm, d_ in (('BASE (stand-in)', IN), ('F1 BLACK-BOOK BURNER: wheat-paste slab, ink drop, kraft tape', IN.rstrip('/') + '_F1/'), ('F2 ZAUN PRESS: pink plate 4 px off, press-cyan plate peeks 3 px', IN.rstrip('/') + '_F2/')):
    if os.path.exists(d_ + 'h02.png'):
        rows.append((nm, Image.open(d_ + 'h02.png').convert('RGB').crop((990, 730, 1700, 1070))))
if rows:
    S = Image.new('RGB', (1500, 60 + len(rows) * 372), (9, 10, 20))
    dd = ImageDraw.Draw(S)
    dd.text((24, 14), 'LIFTED CARD PRINT, per finalist (the hover re-skin hook)', font=HF.anton(30), fill=(242, 246, 255))
    for i, (nm, c) in enumerate(rows):
        y = 60 + i * 372
        S.paste(c, (24, y + 26))
        dd.text((24, y + 6), nm, font=HF.mono(17), fill=(175, 192, 214))
        dd.text((760, y + 190), 'the same card, the same hover; only the P-family print behind it changes with the finalist', font=HF.mono(15), fill=(122, 136, 156))
    S.save(OUT + 'lift_styles.png')
print('assembled', OUT)
