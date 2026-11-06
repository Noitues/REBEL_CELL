"""P1 interactivity concepts, sequence 1: hover / focus states.   python ix_a.py [name ...]"""
import sys, time
from ix_lib import *


def f_01a_site():
    """FOCUS on a Site (t1_b, where K1 / K2 and every sealed route cross). Lights: the beams that reach it, its ring+block.
    Dims: the city and the beams that do not. Preview: one pair per beam: [beam head] -> [what it does here]."""
    w = World('default')
    tb = w.sites['t1_b']['B']
    hole = np.maximum(hole_disc(tb, 360, 300), hole_path(PX(w.routes['K2']['path']).sub(1500, 1800, 6), 130))
    cv = plan_base(w, grade=.55, hole=hole, ks={'K1': 1.0, 'K2': 1.0, 'K3': .24}, sealed_k=.4, lock_k=.45, hunter_k=.35, home_k=.9,
                   site_k={s: (.35 if s not in ('t1_b', 't1_c') else 1.0) for s in w.sites})
    P2 = PX(w.routes['K2']['path'])
    s2 = w.visit('K2', 't1_b')
    hy.target_ring(cv, tb, 'SITES_LOST', r=46)
    hy.stop_block(cv, P2, s2 - 2, 'SITES_LOST')
    P1 = PX(w.routes['K1']['path'])
    pp = P1.at(w.visit('K1', 't1_b'))[0]
    ui.glyph_disc(cv, pp, 11, TIER['UNTOUCHED'], lambda l, c_, r_: g_tier(l, 'UNTOUCHED', c_, r_), gscale=.62, k=.9, ring_w=2)
    halo_site(cv, tb)
    base = np.array([tb[0] + 6, tb[1] - 215])
    ui.crt_chip(cv, base[0] - 108, base[1] - 66, base[0] + 108, base[1] + 78, k=.8, r=12)
    pair_chip(cv, base + np.array([0, -34]), 'N', 'SITES_LOST', 1)
    pair_chip(cv, base + np.array([0, 4]), 'D', 'UNTOUCHED', None, passthrough=True)
    for i, L in enumerate('ABC'):
        ui.lock(cv, (base[0] - 44 + i * 44, base[1] + 50), L, 'locked', r=12, k=.8)
    hy.leader(cv, tb + np.array([0, -70]), base + np.array([0, 78]), k=.8)
    hy.hud(cv, 44, 50, 80, 8, 0)
    hand_custom(cv)
    a = Ann()
    a.title('01a  HOVER / FOCUS  ·  a Site', 'lime halo = the focus; the rest of the city drops to a graded night')
    a.note('1  lime halo: the only lime on screen', (tb[0] - 360, tb[1] + 120), to=(tb[0] - 44, tb[1] - 2))
    a.note('2  world grade: city -45% value, -60% sat\nbeams that do not reach the Site: 24%', (1380, 250), to=(1220, 392))
    a.note('3  readout: one row per beam\n[beam head] -> [what it does here]\nthe dot = passes through, untouched', (tb[0] + 330, tb[1] - 290), to=(base[0] + 100, base[1] - 4))
    a.note('4  the beam that lands here keeps its\nring + stop block lit (the intent stays on the map)', (tb[0] + 320, tb[1] + 90), to=(tb[0] + 48, tb[1] + 6))
    a.note('5  sealed routes: three locks, outcome unknown', (tb[0] - 150, tb[1] - 330), to=(base[0] - 44, base[1] + 46))
    emit('01a_focus_site', cv, a)


def f_01b_beam():
    """FOCUS on a beam (K2, N). Lights: its whole ribbon (lime casing), its target ring/block/tile, the cards that can stop it.
    Dims: other beams, sealed corridors, the city off its street. Preview: pass dots + the dead trail it would run."""
    w = World('default')
    R = w.routes['K2']
    P2 = PX(R['path'])
    hole = hole_path(P2.sub(R['ext'], P2.L, 6), 150)
    cv = plan_base(w, grade=.6, hole=hole, ks={'K1': .26, 'K2': 1.0, 'K3': .26}, sealed_k=.3, lock_k=.4, hunter_k=.3, home_k=.8,
                   site_k={s: (1.0 if s in ('t3_b', 't2_breach', 't1_b') else .3) for s in w.sites}, heads=False)
    s_t = w.visit('K2', 't1_b')
    tb = w.sites['t1_b']['B']
    halo_beam(cv, P2, R['ext'], s_t + 24)
    hy.dead_trail(cv, P2, s_t + 40, P2.L - 4, k=.9)
    hy.target_ring(cv, tb, 'SITES_LOST', r=46)
    hy.stop_block(cv, P2, s_t - 2, 'SITES_LOST')
    for sid in ('t3_b', 't2_breach'):
        q = P2.at(w.visit('K2', sid))[0]
        ui.glyph_disc(cv, q, 11, TIER['UNTOUCHED'], lambda l, c_, r_: g_tier(l, 'UNTOUCHED', c_, r_), gscale=.62, k=.95, ring_w=2)
    hy.head(cv, P2, R['ext'] + RUN['K2'], 'N', sc=2.2)
    tp = (tb[0] + 50, tb[1] - 160)
    hy.leader(cv, tb + np.array([0, -60]), np.array(tp) + np.array([0, 24]), k=.8)
    hy.hex_tile(cv, tp, 'SITES_LOST', 1, r=30)
    hy.hud(cv, 44, 50, 80, 8, 0)
    cs = hand_custom(cv, lifts={1: 26, 3: 26}, ks={0: .5, 2: .5, 4: .5}, glow={1: 'N', 3: 'N'})
    p1 = PX(w.routes['K1']['path']).at(1500)[0]
    a = Ann()
    a.title('01b  HOVER / FOCUS  ·  a beam', 'the ribbon keeps its pure type hue; the lime is a thin casing either side')
    a.note('1  lime casing, ribbon untouched\n(type hue never recoloured)', (1000, 330), to=tuple(P2.at(R['ext'] + 700)[0]))
    a.note('2  other beams: 26%  (still a readable silhouette)', (560, 330), to=tuple(p1))
    a.note('3  pass-through dots on the Sites it crosses', (1160, 700), to=tuple(P2.at(w.visit('K2', 't2_breach'))[0]))
    a.note('4  the dead trail: what it would run on to HOME if nothing stops it', (320, 690), to=tuple(P2.at(s_t + 260)[0]))
    a.note('5  cards that answer N lift and glow\nin the N hue (the answer is shown, not told)', (1470, 880), to=(cs[3][0] + 40, cs[3][1] - 50))
    emit('01b_focus_beam', cv, a)


def f_01c_card():
    """FOCUS on a hand card (D GUARD). The card lifts with the lime halo; the map pre-lights the Sites that can take it
    (the matching beam's street glows, MATCH pads in the D hue), a soft version of the drag preview."""
    w = World('default')
    R = w.routes['K1']
    P1 = PX(R['path'])
    hole = hole_path(P1.sub(R['ext'], P1.L, 6), 140)
    cv = plan_base(w, grade=.5, hole=hole, ks={'K1': 1.0, 'K2': .45, 'K3': .45}, sealed_k=.5, lock_k=.5, hunter_k=.4, home_k=.9,
                   site_k={s: (1.0 if s in ('t3_c', 't2_virus', 't1_c', 't1_b') else .4) for s in w.sites})
    for sid in ('t3_c', 't2_virus', 't1_c', 't1_b'):
        mk_match(cv, w.sites[sid]['B'], 'D', k=.72, strong=False, r=40)
    hy.hud(cv, 44, 50, 80, 8, 0)
    cs = hand_custom(cv, lifts={0: 40}, lime=0, ks={1: .8, 2: .8, 3: .8, 4: .8})
    a = Ann()
    a.title('01c  HOVER / FOCUS  ·  a card', 'hover = soft pre-drag preview; nothing moves until the card is picked up')
    a.note('1  card lifts 40 px, lime halo', (cs[0][0] - 230, cs[0][1] - 90), to=(cs[0][0] - 44, cs[0][1] - 40))
    a.note('2  the D street glows; other beams 45%', (1000, 540), to=tuple(P1.at(R['ext'] + 760)[0]))
    a.note('3  MATCH pads (D hue + dart) on every Site\nthe D beam crosses, at 70%', (480, 330), to=(w.sites['t1_b']['B'][0] - 20, w.sites['t1_b']['B'][1] - 100))
    a.note('4  Sites off the D street stay dark', (1020, 800), to=(w.sites['t2_intel']['B'][0], w.sites['t2_intel']['B'][1] - 20))
    emit('01c_focus_card', cv, a)


def f_01e_home():
    """FOCUS on HOME. Lights: the last stretch of every beam, the integrity ring with its likely loss (orange) and worst
    case (red), the 12-outcome tally. Dims: everything not about HOME's odds."""
    w = World('default')
    hm = w.home
    hole = hole_disc(hm, 520, 360)
    for r in KN:
        P = PX(w.routes[r]['path'])
        hole = np.maximum(hole, hole_path(P.sub(P.L - 520, P.L, 6), 110))
    cv = plan_base(w, grade=.55, hole=hole, ks={'K1': .8, 'K2': .8, 'K3': .8}, sealed_k=.35, lock_k=.4, hunter_k=.3,
                   home_kw=dict(hp=44, preview=6), site_k={s: .45 for s in w.sites}, heads=True)
    home_range(cv, hm)
    for r in KN:
        P = PX(w.routes[r]['path'])
        halo_beam(cv, P, P.L - 420, P.L - 4, k=.55)
    halo_home(cv, hm)
    tray(cv, 120, 912, 640, 1000)
    tally12(cv, BASE12, TALLY_C)
    hy.home_chip(cv, hm, 6)
    hy.hud(cv, 44, 50, 80, 8, 0)
    hand_custom(cv, ks={i: .5 for i in range(5)})
    a = Ann()
    a.title('01d  HOVER / FOCUS  ·  HOME', 'HOME answers one question: how bad can it get, and how likely')
    a.note('1  lime ring', (hm[0] + 330, hm[1] - 150), to=(hm[0] + 98, hm[1] - 28))
    a.note('2  ring ticks: orange = likely loss, red = worst case', (hm[0] + 400, hm[1] + 60), to=(hm[0] + 70, hm[1] + 20))
    a.note('3  the 12-outcome tally lights up (it is HOME\'s odds)\none mark per outcome, grouped by tier', (hm[0] + 175, hm[1] + 62), to=(hm[0] + 100, 940))
    a.note('4  last stretch of every beam gets a thin casing', (hm[0] + 520, hm[1] - 330), to=tuple(PX(w.routes['K1']['path']).at(PX(w.routes['K1']['path']).L - 300)[0]))
    a.note('5  Sites and sealed routes sink to 45%', (900, 800), to=(w.sites['t2_virus']['B'][0], w.sites['t2_virus']['B'][1] - 20))
    emit('01d_focus_home', cv, a)


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_0')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
