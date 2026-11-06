"""Crop specs (plate px, 1920x1080 frame, board at C=(536,540)) for each element's sheet rows."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import e8lib as E8
J = json.load(open('D:/rc_scratch/e10_design/wave_rings/state_e10.json'))
import wr_latent as WLT
_LAB = {}


def _unit(uid, lab=None):
    if lab:
        if lab not in _LAB:
            _LAB[lab] = WLT.lab_frame(J, lab)
        us = _LAB[lab]['units']
    else:
        us = J['f1']['units']
    return [u for u in us if u['id'] == uid][0]


def box_of(sp):
    if sp[0] == 'box':
        return tuple(sp[1:5])
    if sp[0] == 'tok':
        lab = sp[3] if len(sp) > 3 else None
        x, y = E8.token_pos(_unit(sp[1], lab))
        h = sp[2]
        return (int(x - h), int(y - h), int(x + h), int(y + h))
    if sp[0] == 'gproof':
        return (0, 0, 150, 150)
    raise ValueError(sp)


B = lambda *a: ('box',) + a
T = lambda uid, h=46, lab=None: ('tok', uid, h, lab) if lab else ('tok', uid, h)

# eid -> [(row label, plate key, [specs])]   plate keys: p1 | p2 | p2b | lab
STATES = {
 'empty_cell': [('p1 DECIDE | ring +2 and +1 empties, top', 'p1', [B(400, 180, 680, 300)]), ('p1 DECIDE | ring +1 and NOW empties, right', 'p1', [B(650, 330, 830, 470)])],
 'ring_separators': [('p1 DECIDE | spokes and ring gutters at the two top boundaries', 'p1', [B(330, 215, 470, 335), B(590, 215, 730, 335)]),
                     ('p1 DECIDE | gutters through the three rings, bottom-left', 'p1', [B(230, 590, 430, 760)])],
 'unit_cell_screen': [('p1 DECIDE | +1 Packet and NOW wash', 'p1', [B(400, 235, 670, 335)]), ('p1 DECIDE | NOW / +1 / +2 depth ramp, bottom-left', 'p1', [B(230, 590, 470, 780)]),
                      ('p2b HOVER | the dimmed units', 'p2b', [B(230, 590, 470, 780)])],
 'unit_screen_bezel': [('p1 DECIDE | cell ends (9 o clock)', 'p1', [B(170, 500, 330, 620)]), ('p1 DECIDE | inside a wide +2 cell', 'p1', [B(430, 800, 650, 900)])],
 'unit_screen_code_text': [('p1 DECIDE | +1 Packet (hex columns next to the token)', 'p1', [B(370, 255, 560, 345)]), ('p1 DECIDE | +2 Packet, sector 5', 'p1', [B(190, 330, 350, 450)])],
 'unit_cell_outline': [('p1 DECIDE | NOW, +1, +2 outlines at sector 4', 'p1', [B(230, 590, 430, 760)]), ('p1 DECIDE | +1 Packet top', 'p1', [B(400, 235, 670, 335)]),
                       ('p2b HOVER | hovered +2 Packet (yellow outline)', 'p2b', [B(720, 610, 900, 760)])],
 'token_disc': [('p1 DECIDE | NOW, +1, +2 tokens', 'p1', [T(1), T(5), T(6)]), ('p2 PREVIEW | ghost tokens (killed Packet, consumed Payload)', 'p2', [T(1), T(4)])],
 'token_lane_base': [('p1 DECIDE | NOW, +1, +2 token rings', 'p1', [T(2), T(5), T(7)])],
 'token_halo': [('p1 DECIDE | warded NOW Worm, +1 Packet, +1 Payload', 'p1', [T(3), T(5), T(4)])],
 'glyph_packet': [('p1 DECIDE | token +1, token +2, arc disc', 'p1', [T(5, 40), T(7, 40), B(759, 124, 827, 192)]), ('glyph at size and large', 'p1', [('gproof', 'Packet')])],
 'glyph_worm': [('p1 DECIDE | tokens NOW and arc disc', 'p1', [T(2, 40), T(3, 40), B(741, 154, 809, 222)]), ('glyph at size and large', 'p1', [('gproof', 'Worm')])],
 'glyph_payload': [('p1 DECIDE | token +1, arc disc', 'p1', [T(4, 40), B(76, 474, 144, 542)]), ('glyph at size and large', 'p1', [('gproof', 'Payload')])],
 'glyph_jammer': [('LAB | Jammer token NOW (no Jammer in the E10 state)', 'lab', [T(41, 46, 'glyphs')]), ('glyph at size and large', 'p1', [('gproof', 'Jammer')])],
 'glyph_ring': [('LAB | Ring-unit token (climax Ring, width 6)', 'lab', [T(21, 46, 'wide6')]), ('glyph at size and large', 'p1', [('gproof', 'Ring')])],
 'unit_hp_row': [('p1 DECIDE | +1 Packet (2 of 3)', 'p1', [B(410, 238, 660, 305)]), ('p1 DECIDE | NOW Packet (5 of 6, 2 lost this turn)', 'p1', [B(390, 715, 660, 790)]),
                 ('p1 DECIDE | +2 Packet, width 3 (9 of 9)', 'p1', [B(420, 840, 660, 905)])],
 'chev_solid_stack': [('p1 DECIDE | sector 3 column and +1 Packet', 'p1', [B(490, 690, 590, 880), B(490, 262, 586, 332)])],
 'chev_hollow': [('p1 DECIDE | +2 hollow growth (sector 3 and sector 5)', 'p1', [B(490, 800, 590, 900), B(210, 330, 310, 430)])],
 'chev_sector_column': [('p1 DECIDE | the sector-3 spine through three rings', 'p1', [B(470, 690, 610, 900)])],
 'armor_cap': [('p1 DECIDE | armored +1 Payload (cap, HP, lane)', 'p1', [B(380, 755, 650, 850)]), ('p1 DECIDE | token cue', 'p1', [T(4, 46)])],
 'warded_mark': [('p1 DECIDE | warded NOW Worm and warded +2 Packet', 'p1', [T(3, 60), T(6, 60)])],
 'dead_x': [('p1 DECIDE | the shot-dead NOW Worm', 'p1', [B(300, 330, 560, 520)]), ('p2 PREVIEW | same unit under the plan', 'p2', [B(300, 330, 560, 520)])],
 'adjuster_cell': [('p1 DECIDE | Adjuster cell, ring +1 sector 2', 'p1', [B(650, 560, 830, 780)])],
 'adjuster_diamond': [('p1 DECIDE | Adjuster body', 'p1', [B(690, 600, 830, 735)])],
 'adjuster_hp_bar': [('p1 DECIDE | Adjuster HP 10, 1 lost this turn', 'p1', [B(735, 555, 830, 760)])],
 'ward_arc': [('p1 DECIDE | ward at the Adjuster sector (NOW ring, 4 o clock)', 'p1', [B(612, 520, 740, 690)])],
 'consumed_unit': [('p2 PREVIEW | consumed Payload (Trigger)', 'p2', [B(300, 640, 640, 880)])],
 'trigger_killed_unit': [('p2 PREVIEW | Trigger-killed Packet + refund burst', 'p2', [B(300, 560, 640, 780)])],
 'screen_motif_skull': [('p1 DECIDE | Payload screen, 8 o clock', 'p1', [B(330, 700, 500, 820)]), ('p2 PREVIEW | the dimmed consumed Payload', 'p2', [B(330, 700, 500, 820)])],
 'shield_bracket': [('LAB | shielded Jammers (E reference = approved bracket)', 'lab', [B(240, 610, 420, 735), B(430, 185, 650, 265)])],
 'adjuster_armor_strike': [('LAB | armoured boss in its strike phase', 'lab', [B(600, 540, 850, 800)])],
 'ring_unit_wide6': [('LAB | full-ring unit, the start and the seam', 'lab', [B(330, 215, 600, 345)])],
}
EXTRA = {'token_disc': ['p2'], 'screen_motif_skull': ['p2'], 'dead_x': ['p2'], 'unit_cell_outline': ['p2b'], 'unit_cell_screen': ['p2b'], 'consumed_unit': [], 'trigger_killed_unit': []}
