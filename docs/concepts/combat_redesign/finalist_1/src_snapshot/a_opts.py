"""ACTIONS element table. views = (beat, cx, cy, hw, hh, scale, extra) ; extra keys: tgt, idle, sel (dict merged), reg (per-option region override {opt: (cx,cy,hw,hh)}), label.
keys(opt) -> sel for that option ('cur' -> {} = E10 as drawn)."""
import sys
sys.dont_write_bytecode = True

STK = (1705, 912, 215, 172, 2.0)         # the bottom-right stack
NAME_BL = (150, 1000, 150, 80, 2.0)


def V(beat, box, **ex):
    return (beat,) + tuple(box) + (ex,)


def cur_or(opt, d):
    return {} if opt == 'cur' else d


ELEMS = [
    dict(id='send_it', title='send_it  SEND IT sticker', keys=lambda o: cur_or(o, dict(send=o)), views=[V('p1', STK)]),
    dict(id='undo_chip', title='undo_chip  UNDO [Z] chip (ready, then locked = grey tick)', keys=lambda o: cur_or(o, dict(undo=o)),
         views=[V('p1', STK), V('p1', STK, sel=dict(locked=True), label='locked state')]),
    dict(id='nameplate', title='nameplate  CELL-9 // BREAKER', keys=lambda o: cur_or(o, dict(name=o)),
         views=[V('p1', NAME_BL, reg={'B': (1250, 395, 215, 70)}), V('p2', (1250, 400, 215, 110, 2.0), reg={'A': (150, 1000, 150, 80), 'C': (150, 1000, 150, 80)}, label='p2: B collides with the stars row')]),
    dict(id='sticker_material', title='sticker_material  die-cut, plate, ink, one shadow, vinyl', keys=lambda o: cur_or(o, dict(mat=o, send='A', name='A', undo='A', hint='A')),
         views=[V('p1', (1740, 960, 180, 110, 2.4)), V('p1', (130, 1010, 130, 60, 2.6))]),
    dict(id='stickers_nowords', title='stickers_nowords  verb, identity, UNDO with words off', beat='nowords', keys=lambda o: cur_or(o, dict(snw=o, undo=o, send='A')),
         views=[V('nowords', STK), V('nowords', NAME_BL)]),
    dict(id='bottom_hint', title='bottom_hint  > turn_resolve.exe', keys=lambda o: cur_or(o, dict(hint=o)),
         views=[V('p1', (1705, 975, 215, 105, 2.0)), V('p1', (1705, 975, 215, 105, 2.0), sel=dict(hover=True), label='SEND IT hovered', only=['C'])]),
    dict(id='card_targeting', title='card_targeting  valid targets + Tab focus (LATENT; Trigger to units, Brace to slices, Twist to rings, Spin to tower)', keys=lambda o: cur_or(o, dict(ctar=o)),
         views=[V('p1', (400, 720, 300, 230, 1.35), tgt=('unit', 4), label='Trigger held: unit 4 focused'),
                V('p1', (536, 540, 170, 170, 1.7), tgt=('slice', 2), label='Brace held: slice 2 focused'),
                V('p1', (640, 325, 130, 120, 2.0), tgt=('ring', 1), label='Twist held: ring +1 focused'),
                V('p1', (536, 540, 120, 120, 2.2), tgt=('tower', 0), label='Spin held: tower')]),
    dict(id='hover_tag', title='hover_tag  unit facts tag (p2b)', keys=lambda o: cur_or(o, dict(htag=o)),
         views=[V('p2b', (540, 540, 540, 540, 0.5), label='tag vs the hovered unit'),
                V('p2b', (200, 80, 280, 80, 1.5), reg={'A': (230, 980, 230, 100), 'B': (536, 980, 260, 100), 'C': (1300, 480, 280, 100)})]),
    dict(id='hover_path', title='hover_path  route through the cells to the slices (p2b)', keys=lambda o: cur_or(o, dict(hpath=o)),
         views=[V('p2b', (440, 720, 270, 200, 1.5))]),
    dict(id='hover_slice_highlight', title='hover_slice_highlight  slices the hovered unit hits (p2b)', keys=lambda o: cur_or(o, dict(hslice=o)),
         views=[V('p2b', (536, 540, 190, 190, 1.55))]),
    dict(id='hover_focus_dim', title='hover_focus_dim  unit screens of non-hovered units (p2b)', keys=lambda o: cur_or(o, dict(hfdim=o)),
         views=[V('p2b', (536, 540, 540, 540, 0.55)), V('p2b', (640, 330, 230, 150, 1.7))]),
    dict(id='hover_dim_overlay', title='hover_dim_overlay  marks and landing arcs of non-hovered units (p2b)', keys=lambda o: cur_or(o, dict(hodim=o)),
         views=[V('p2b', (536, 540, 540, 540, 0.55)), V('p2b', (200, 330, 210, 150, 1.7))]),
    dict(id='hovered_cell_outline', title='hovered_cell_outline  which unit is hovered (p2b)', keys=lambda o: cur_or(o, dict(hcell=o)),
         views=[V('p2b', (440, 720, 270, 200, 1.5)), V('p2b', (270, 650, 100, 90, 3.0))]),
    dict(id='trigger_path', title='trigger_path  Trigger pierce, X on each unit hit (p2)', keys=lambda o: cur_or(o, dict(tpath=o)),
         views=[V('p2', (450, 700, 150, 100, 2.0))]),
    dict(id='twist_badge', title='twist_badge  Twist played: ring +1 turns one extra sector (p2)', keys=lambda o: cur_or(o, dict(tbadge=o)),
         views=[V('p2', (700, 322, 100, 60, 3.2))]),
    dict(id='refund_burst', title='refund_burst  where the +1 RAM refund lands on the board (p2, p3)', keys=lambda o: cur_or(o, dict(rburst=o, rtoken='A')),
         views=[V('p2', (480, 705, 140, 85, 2.2)), V('p3', (480, 705, 140, 85, 2.2))]),
    dict(id='refund_token', title='refund_token  one +1 RAM token on a fixed size ladder: board 44, RAM row 30, chip 26, strip 20', keys=lambda o: cur_or(o, dict(rtoken=o)),
         views=[V('p2', (480, 705, 130, 80, 2.2)), V('p2', (1200, 482, 190, 30, 2.2)), V('p2', (1190, 340, 170, 55, 2.0)), V('p3', (1450, 318, 200, 30, 2.2))]),
    dict(id='resolve_fire_lines', title='resolve_fire_lines  the guns that fired (p3)', keys=lambda o: cur_or(o, dict(fire=o)),
         views=[V('p3', (536, 540, 540, 540, 0.5)), V('p3', (470, 640, 190, 160, 1.6))]),
    dict(id='no_target_tag', title='no_target_tag  idle gun at sector 4 (LATENT, hypothetical state)', keys=lambda o: {} if o == 'cur' else {}, idle=True,
         views=[V('p1', (400, 650, 140, 140, 2.2))]),
]
ELEMS_BY = {e['id']: e for e in ELEMS}
