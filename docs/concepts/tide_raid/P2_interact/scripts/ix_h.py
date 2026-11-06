"""P2 flow filmstrip: one whole player turn, hover -> drag -> what-if -> drop -> response pick -> commit -> run.   python ix_h.py"""
import sys, time
from ix_lib import *
from ix_b import SLOT_C, slots, SHIFT_E
from ix_c import HOLD12, MOVE12, DEPLOY12
import ix_e

FLOW = FRD + 'flow/'
os.makedirs(FLOW, exist_ok=True)
os.makedirs(FLOW + 'clean/', exist_ok=True)


def committed(w, guard='t1_c', press=False, run=False, name='flow_08', title='', sub='', notes=()):
    progs = dict(SHIFT_E)
    progs[guard] = ('GUARD', 'D')
    runs = dict(RUN)
    if run:
        runs = {'K1': 60 + 330, 'K2': 400 + 330, 'K3': 215 + 330}
    stop_k1 = w.visit('K1', guard)
    ends = {'K1': stop_k1 + 20, 'K2': w.visit('K2', 't1_b') + 20, 'K3': w.visit('K3', 't2_intel') + 20}
    cv = plan_base(w, grade=0.0, ks={'K1': 1.0, 'K2': 1.0, 'K3': 1.0}, sealed_k=.8, lock_k=.8, hunter_k=.7, programs=progs, ends=ends, runs=runs,
                   bright={guard, 't1_b', 't2_intel'}, home_kw=dict(hp=44, preview=0 if guard == 't1_b' else 6))
    P1 = PX(w.routes['K1']['path'])
    hy.dead_trail(cv, P1, stop_k1 + 40, P1.L - 4, k=.8)
    tiles = []
    if guard == 't1_c':
        hy.target_ring(cv, w.sites['t1_c']['B'], 'HOLDS')
        hy.stop_block(cv, P1, stop_k1 - 2, 'HOLDS')
        tiles.append(('t1_c', 'HOLDS', None))
        hy.target_ring(cv, w.sites['t1_b']['B'], 'SITES_LOST')
    else:
        hy.target_ring(cv, w.sites['t1_b']['B'], 'SITES_LOST')
        PK.tier_ring(cv, w.sites['t1_b']['B'], 'HOLDS', r_bu=6.2)
        hy.stop_block(cv, P1, stop_k1 - 2, 'HOLDS')
        tiles.append(('t1_b', 'HOLDS', None))
    P2 = PX(w.routes['K2']['path'])
    hy.stop_block(cv, P2, w.visit('K2', 't1_b') - 2, 'SITES_LOST')
    P3 = PX(w.routes['K3']['path'])
    hy.target_ring(cv, w.sites['t2_intel']['B'], 'UNTOUCHED')
    hy.stop_block(cv, P3, w.visit('K3', 't2_intel') - 2, 'UNTOUCHED')
    if guard == 't1_c':
        tiles += [('t1_b', 'SITES_LOST', 1), ('t2_intel', 'UNTOUCHED', None)]
    else:
        tiles += [('t2_intel', 'UNTOUCHED', None)]
    if not run:
        anchors = [np.array(w.sites[i[0]]['crown']) + np.array([0, -58]) for i in tiles]
        pos = hy.fan(anchors, 70.0)
        for it, p in zip(tiles, pos):
            src = np.array(w.sites[it[0]]['crown'])
            hy.leader(cv, src + np.array([0, -4]), np.array(p) + np.array([0, 24]), k=.7)
            hy.hex_tile(cv, tuple(p), it[1], it[2], r=30)
        hy.home_chip(cv, w.home, 6 if guard == 't1_c' else 4)
        tally12(cv, HOLD12 if guard == 't1_c' else MOVE12, TALLY_C)
    hy.hud(cv, 44, 50, 80, 8, 0)
    hand_custom(cv, cards=[HAND[1], HAND[2], HAND[3], HAND[4]], y=992)
    slots(cv, SLOT_C, [('SHIFT', 'E'), ('GUARD', 'D')], k=.95)
    if press:
        halo_home(cv, w.home, k=.8)
        prompt_row(cv, (w.home[0] + 470, 760), [(('face', 'N'), 'forecast')], r=24)
    a = Ann()
    a.title(title, sub)
    for n in notes:
        a.note(*n[:2], to=n[2] if len(n) > 2 else None)
    emit(name, cv, a, folder=FLOW)


def f_flow_01():
    cv, w = ix_e.forecast_scene(1.0)
    a = Ann()
    a.title('F1  PLAN  ·  the board at rest', 'plan, forecast row and hand: nothing is focused')
    emit('flow_01', cv, a, folder=FLOW)


def f_flow_08():
    w = World('default')
    committed(w, 't1_c', name='flow_08', title='F8  PLACED  ·  the plan after the drop', sub='carriers are solid now (no hatch, no dashes); the tally is the committed odds',
              notes=[('1  solid ring + block: committed', (560, 380), (542, 572)), ('2  tally: committed counts, no ghost row', (520, 800), (330, 1000))])


def f_flow_11():
    w = World('default')
    committed(w, 't1_b', press=True, name='flow_11', title='F11  COMMIT  ·  MOVE chosen, second press launches',
              sub='the face-N prompt follows HOME; HOME takes the lime brackets',
              notes=[('1  guard now at t1_b (teal ring inside amber)', (900, 420), (630, 520)), ('2  one prompt glyph, no words', (1200, 700), (w.home[0] + 470, 760))])


def f_flow_12():
    w = World('default')
    committed(w, 't1_b', run=True, name='flow_12', title='F12  RUN  ·  heads released along their streets',
              sub='the forecast row and tiles clear; the dread shadow moves with each head',
              notes=[('1  heads leave the HQ stub', (1200, 740), tuple(PX(w.routes['K1']['path']).at(w.routes['K1']['ext'] + 390)[0]))])


FILM = [('flow_01', 'F1', FLOW + 'clean/flow_01.jpg', 'rest'), ('f2', 'F2', CLD + '01c_focus_card.jpg', 'hover card: matching streets light'),
        ('f3', 'F3', CLD + '02a_drag_pickup.jpg', 'pick up: legal targets by class'), ('f4', 'F4', CLD + '02b_drag_over_match.jpg', 'over a match: hatch + pulse preview'),
        ('f5', 'F5', CLD + '03a_whatif_t3c.jpg', 'scrub: before > after columns'), ('f6', 'F6', CLD + '03c_whatif_t1c.jpg', 'scrub back: settle'),
        ('f7', 'F7', CLD + '02e_drag_snap.jpg', 'drop: solidifies'), ('f8', 'F8', FLOW + 'clean/flow_08.jpg', 'placed: committed odds'),
        ('f9', 'F9', CLD + '04a_disc_deploy.jpg', 'disc hover DEPLOY'), ('f10', 'F10', CLD + '04c_disc_move.jpg', 'disc hover MOVE'),
        ('f11', 'F11', FLOW + 'clean/flow_11.jpg', 'commit: second press'), ('f12', 'F12', FLOW + 'clean/flow_12.jpg', 'run')]


def f_board():
    cols, tw, th = 3, 640, 360
    rows = 4
    sheet = Image.new('RGB', (cols * tw + 40, rows * (th + 44) + 90), (8, 6, 20))
    d = ImageDraw.Draw(sheet)
    d.text((20, 18), 'FLOW  ·  one player turn, hover to run (clean frames; the number is the step)', font=font(34, False, 800, 75), fill=(240, 243, 255))
    for i, (k, n, f, cap) in enumerate(FILM):
        im = Image.open(f).convert('RGB').resize((tw - 12, th - 7), Image.LANCZOS)
        x, y = 20 + (i % cols) * tw, 80 + (i // cols) * (th + 44)
        sheet.paste(im, (x, y))
        d.rounded_rectangle((x, y, x + tw - 12, y + th - 7), 4, outline=(246, 241, 228), width=2)
        d.ellipse((x + 8, y + 8, x + 52, y + 52), fill=(246, 241, 228), outline=(10, 10, 28), width=3)
        d.text((x + 30, y + 31), n[1:], font=font(26, False, 800, 75), fill=(10, 10, 28), anchor='mm')
        d.text((x + 6, y + th), cap, font=font(22, False, 560, 78), fill=(200, 208, 232))
    sheet.save(OUT + 'boards/00_flow_board.jpg', quality=92)
    print('saved flow board')


if __name__ == '__main__':
    want = sys.argv[1:] or ['flow_01', 'flow_08', 'flow_11', 'flow_12', 'board']
    for n in want:
        globals()['f_' + n]()
