"""P1 sequence 4 (response disc hover previews) and 5 (sealed / hunter inspection).   python ix_c.py [name ...]"""
import sys, time
from ix_lib import *
from ix_lib import _brackets

DISC_X = [780 + i * 185 for i in range(4)]
DISC_Y = 925
KINDS = ['DEPLOY', 'HOLD', 'MOVE', 'SACRIFICE']
MOVE12 = [B_, D_, H_, S_, H_, H_, S_, S_, D_, B_, B_, D_]
SAC12 = [S_, S_, B_, S_, H_, S_, S_, H_, S_, B_, S_, S_]
DEPLOY12 = with_guards(BASE12, d_at=True, n_at=True)
HOLD12 = with_guards(BASE12, d_at=True)          # the committed plan: the D guard is already placed
PIPS = {'DEPLOY': ['HOLDS', 'SITES_LOST', 'DAMAGED'], 'HOLD': ['HOLDS', 'SITES_LOST', 'DAMAGED'],
        'MOVE': ['HOLDS', 'SITES_LOST', 'DAMAGED'], 'SACRIFICE': ['HOLDS', 'SITES_LOST', 'BREACHED']}


def response_base(w, dim=.6, tiles=True):
    cv, stops = forecast_world(w)
    if tiles:
        tiles_at(cv, w, [('t1_c', 'HOLDS', None), ('t1_b', 'SITES_LOST', 1), ('t2_intel', 'UNTOUCHED', None)])
    locks(cv, w, k=.9)
    hunter(cv, w, k=.8)
    cv.img *= dim
    return cv, stops


def discs(cv, hov, others_k=.8):
    pos = []
    for i, kd in enumerate(KINDS):
        c = (DISC_X[i], DISC_Y)
        hy.stencil_disc(cv, c, kd, PIPS[kd], selected=(i == hov), word=(kd if i == hov else ''), seed=5 + i, k=(1.0 if i == hov else others_k))
        pos.append(c)
    return pos


def disc_frame(name, hov, title, sub, build, notes, new12, old12=HOLD12):
    w = World('default')
    cv, stops = response_base(w)
    build(cv, w)
    hm = w.home
    tray(cv, 100, 842, 650, 1004)
    tally_diff(cv, old12, new12, TALLY_C, row=64)
    pos = discs(cv, hov)
    hy.hud(cv, 44, 50, 80, 8, 0)
    a = Ann()
    a.title(title, sub)
    for n in notes(w, pos):
        a.note(*n[:2], to=n[2] if len(n) > 2 else None)
    emit(name, cv, a)


def f_04a_disc_deploy():
    def build(cv, w):
        tb = w.sites['t1_b']['B']
        P2 = PX(w.routes['K2']['path'])
        s2 = w.visit('K2', 't1_b')
        ui.firewall(cv, tb, 'N', mode='ghost')
        ui.firewall(cv, tb, 'N', mode='up', k=.55)
        old_ring(cv, tb, 'SITES_LOST', r=46)
        pv_ring(cv, tb, 'HOLDS', r=46)
        pv_block(cv, P2, s2 - 2, 'HOLDS')
        for sid in ('t2_breach', 't3_b'):          # other candidate Sites for the same card: their tier as a small chip
            B = w.sites[sid]['B']
            hy.hex_tile(cv, (B[0], B[1] - 108), 'HOLDS', None, r=17, k=.85)
            pad_ring(cv, B, TYPE_COL['N'], r=36, k=.7, fill=.08, w=2.6, dash=(6, 5))
        hy.vcard(cv, (DISC_X[0] - 22, DISC_Y - 150), 'GUARD', 'N', angle=-6, k=1.0, sc=.7)
        EB.grease_arrow(cv, (DISC_X[0] + 10, DISC_Y - 90), (700, 760), (tb[0] + 20, tb[1] + 40))

    def notes(w, pos):
        tb = w.sites['t1_b']['B']
        return [('1  DEPLOY previews the best placement of the card on the map:\nghost wall, new ring + block, old amber ring left as a ghost', (tb[0] + 400, tb[1] - 250), (tb[0] + 30, tb[1] - 10)),
                ('2  other legal Sites for the same card: tier chip only', (1140, 330), (w.sites['t3_b']['B'][0], w.sites['t3_b']['B'][1] - 108)),
                ('3  the card that would be played rides above the disc', (pos[0][0] - 250, pos[0][1] - 235), (pos[0][0] - 22, pos[0][1] - 150)),
                ('4  tally: 12 outcomes under DEPLOY vs the current plan', (520, 790), (330, 940))]
    disc_frame('04a_disc_deploy', 0, '04a  RESPONSE DISC  ·  DEPLOY hover', 'every disc previews its consequence on the map, uncommitted', build, notes, DEPLOY12)


def f_04b_disc_hold():
    def build(cv, w):
        for r in KN:
            R = w.routes[r]
            P = PX(R['path'])
            hy.head(cv, P, R['ext'] + RUN[r] + 30, R['typ'], sc=2.0, k=1.0)

    def notes(w, pos):
        return [('1  HOLD = nothing changes: the plan stays lit as drawn,\nthe three heads wake (ready to run)', (1100, 760), tuple(PX(w.routes['K1']['path']).at(w.routes['K1']['ext'] + 330)[0])),
                ('2  tally rows identical: no hairlines, no underlines', (520, 790), (330, 940)),
                ('3  the word appears on hover only', (pos[1][0] + 150, pos[1][1] - 110), (pos[1][0] + 10, pos[1][1] + 62))]
    disc_frame('04b_disc_hold', 1, '04b  RESPONSE DISC  ·  HOLD hover', 'the control case: the preview equals the current forecast', build, notes, HOLD12)


def f_04c_disc_move():
    def build(cv, w):
        ta, tb = w.sites['t1_c']['B'], w.sites['t1_b']['B']
        P1 = PX(w.routes['K1']['path'])
        ui.firewall(cv, ta, 'D', mode='ghost')
        old_ring(cv, ta, 'HOLDS', r=46)
        EB.grease_arrow(cv, (ta[0] + 10, ta[1] - 84), ((ta[0] + tb[0]) / 2 + 10, min(ta[1], tb[1]) - 160), (tb[0] + 22, tb[1] - 76))
        ui.firewall(cv, tb, 'D', mode='up', k=.9)
        pv_ring(cv, tb, 'HOLDS', r=40)
        pv_block(cv, P1, w.visit('K1', 't1_b') - 2, 'HOLDS')

    def notes(w, pos):
        tb = w.sites['t1_b']['B']
        return [('1  MOVE: the guard slides along the curved arrow;\nold wall + ring left as ghosts', (tb[0] + 420, tb[1] - 260), (tb[0] + 20, tb[1] - 110)),
                ('2  its stop block and ring jump with it', (tb[0] + 400, tb[1] + 110), (tb[0] + 40, tb[1] + 30)),
                ('3  tally: some marks improve, one gets worse;\nhairlines go both ways', (520, 790), (330, 940))]
    disc_frame('04c_disc_move', 2, '04c  RESPONSE DISC  ·  MOVE hover', 'a trade is visible before it is made: better and worse marks both move', build, notes, MOVE12)


def f_04d_disc_sacrifice():
    def build(cv, w):
        d = w.sites['t1_d']['B']
        hm = w.home
        ui.grease_down(cv, (d[0], d[1] - 34), 26, seed=4, k=.95)
        hy.target_ring(cv, d, 'SITES_LOST', r=46)
        arc = EB.bez(np.array(hm) + np.array([60, -30]), ((hm[0] + d[0]) / 2 + 40, min(hm[1], d[1]) - 70), d + np.array([0, -20]))
        ly = Lyr(pbox(arc, 14))
        ly.line(arc, 3.0, 255, dash=(9, 6))
        cv.neonL(ly, TIER['SITES_LOST'], core=1.0, g1=(3, .7), g2=None)
        hy.hex_tile(cv, (d[0] + 84, d[1] + 8), 'SITES_LOST', 1, r=30)
        # clear HOME's preview ticks: redraw the ring clean over the chip's orange
        hy.hex_tile(cv, (hm[0] + 112, hm[1] - 74), 'UNTOUCHED', None, r=30)

    def notes(w, pos):
        d = w.sites['t1_d']['B']
        return [('1  SACRIFICE: this idle Site is given up (grease DOWN + amber ring + tile);\nthe amber dashed arc runs from HOME to it', (d[0] + 480, d[1] - 40), (d[0], d[1] - 60)),
                ('2  HOME chip turns mint, the ring ticks clear', (w.home[0] + 340, w.home[1] - 150), (w.home[0] + 112, w.home[1] - 74)),
                ('3  tally: milder tiers, but one BREACHED mark remains', (520, 790), (330, 940))]
    disc_frame('04d_disc_sacrifice', 3, '04d  RESPONSE DISC  ·  SACRIFICE hover', 'the cost is on the map: which Site, and what HOME stops losing', build, notes, SAC12)


# =============================================================== 05 sealed / hunter information affordances
OUT_A = lambda j: j // 4          # sealed A index of outcome j (illustrative: 4 outcomes per real route)
OUT_H = lambda j: j % 2           # hunter street of outcome j


LIFT = 34.0


def hot_path(w, r):
    """an inspected sealed route is lifted off the street (+34 px lane) so it never hides under a known ribbon."""
    return lane(w.routes[r]['path'], LIFT)


def fog_route(cv, w, r, k=1.0, width=15, s_to=None, lift=False):
    p = hot_path(w, r) if lift else w.routes[r]['path']
    e = plen(p) - 6 if s_to is None else s_to
    ui.fog_band(cv, p, w.routes[r]['ext'] + 10, e, width=width, seed=3 + 'ABC'.index(r), k=k)


def ghost_types(cv, c, k=1.0):
    """the three type silhouettes fanned and overlapping, all in fog hue outline: 'it could be any of the three'."""
    for i, t in enumerate('DNE'):
        p = (c[0] + (i - 1) * 46, c[1] + (1 - abs(i - 1)) * -8)
        hy.head(cv, None, 0, t, sc=1.9, mode='ghost', k=k * .9, col=FOGC, flat=(p, (1, 0)))


def sealed_scene(w, hot, grade=.5, hunter_k=.45, lock_hot=None, tally_lit=None, title=None):
    hole = None
    for r in hot:
        P = PX(w.routes[r]['path'])
        h = hole_path(P.sub(w.routes[r]['ext'], P.L, 6), 150)
        hole = h if hole is None else np.maximum(hole, h)
    cv = new_canvas(w)
    grade_base(cv, grade, hole)
    for r in 'ABC':
        fog_route(cv, w, r, k=(1.6 if r in hot else .28), width=(17 if r in hot else 12), lift=(r in hot))
    beams_layer(cv, w, {'K1': .3, 'K2': .3, 'K3': .3})
    draw_sites(cv, w, {'t1_a': 'DOWN'}, SHIFT_E_P, {s: (1.0 if any(s in w.routes[r]['sites'] for r in hot) else .35) for s in w.sites}, home_kw=dict(hp=44), home_k=.9)
    heads_layer(cv, w, {'K1': .3, 'K2': .3, 'K3': .3})
    return cv


SHIFT_E_P = {'t2_intel': ('SHIFT', 'E')}


def tally_block(cv, w, lit, tiers=BASE12, k=1.0):
    hm = w.home
    tray(cv, 100, 912, 650, 1004)
    pos = tally12(cv, tiers, TALLY_C, lit=lit, k=k)
    tally_underlines(cv, tiers, lit, TALLY_C)
    return pos


def f_05a_lock_hover():
    """HOVER A SEALED LOCK (A). Lights: corridor A (brighter fog, a pip on every link = its length), the Sites on it, the
    A outcomes in the tally (4 of 12, underlined). Shows: what is knowable (route, length, share of the odds) and what is not (type)."""
    w = World('default')
    hot = ['A']
    cv = sealed_scene(w, hot)
    RA = w.routes['A']
    PA = PX(hot_path(w, 'A'))
    # link pips: one dot per street segment between Sites (its length, countable)
    prev = RA['ext']
    for sid in RA['sites'][1:]:
        if sid in w.sites:
            s = w.visit('A', sid)
            for t in np.linspace(prev + 30, s - 30, 3):
                p = PA.at(t)[0]
                d = Lyr((p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8))
                d.ell(p, 3.4, v=255)
                cv.neonL(d, FOGC * .6 + WHITE * .4, core=1.0, g1=(2, .5), g2=None)
            prev = s
    for sid in RA['sites']:
        if sid in w.sites:
            B = w.sites[sid]['B']
            ui.glyph_disc(cv, (B[0], B[1] - 100), 14, FOGC, g_qmark, gscale=.62, k=.95, ring_w=2.2)
    # unknown type: three ghost silhouettes at the corridor's mouth
    hq = np.array(PA.at(RA['ext'] + 330)[0])
    ghost_types(cv, hq + np.array([-20, -90]))
    # lock lifts and takes the focus brackets
    lp = lock_pos(w, 0)
    ui.lock(cv, lp + np.array([0, -16]), 'A', 'locked', r=26, k=1.0)
    ly = Lyr((lp[0] - 60, lp[1] - 90, lp[0] + 60, lp[1] + 40))
    P = hy.hexpts(lp + np.array([0, -16]), 40)
    ly.line(P + [P[0]], 4, 255)
    cv.neonL(ly, LIME, core=1.0, g1=(4, .9), g2=(12, .6))
    for i, L in enumerate('BC'):
        ui.lock(cv, lock_pos(w, i + 1), L, 'locked', r=21, k=.4)
    hunter(cv, w, k=.3)
    lit = {j for j in range(12) if OUT_A(j) == 0}
    tally_block(cv, w, lit)
    hy.hud(cv, 44, 50, 80, 8, 0)
    hand_custom(cv, ks={i: .5 for i in range(5)})
    a = Ann()
    a.title('05a  SEALED  ·  hover a lock', 'what you can know about a hidden route, wordlessly')
    a.note('1  lime on the lock only; corridor A brightens, B and C sink', (lp[0] - 330, lp[1] - 190), (lp[0] - 30, lp[1] - 40))
    a.note('2  one pip per street segment: its length is countable', (900, 840), tuple(PA.at(w.visit('A', 't2_breach') - 60)[0]))
    a.note('3  "?" on every Site it crosses: it can reach them,\nthe tier is unknown', (1290, 790), (w.sites['t1_b']['B'][0] + 0, w.sites['t1_b']['B'][1] - 100))
    a.note('4  three overlapping outline silhouettes: the type\nis hidden, any of D / N / E', (1330, 250), tuple(hq + np.array([-20, -90])))
    a.note('5  tally: the 4 outcomes where A is the real route are\nunderlined, the other 8 sink to 32%', (760, 790), (250, 950))
    emit('05a_sealed_lock_hover', cv, a)


def f_05b_hunter_hover():
    """HOVER THE HUNTER EYE. Lights: both streets in white, with the street under the pointer in full; the tile each street
    would deliver (E ram, so yellow only once it fires); 6 of 12 tally marks per street."""
    w = World('default')
    hot = []
    cv = sealed_scene(w, hot, grade=.55)
    sc, ec = None, None
    cs = []
    for i, h in enumerate(w.hunters):
        p = h['path']
        pt, _ = at(p, plen(p) * .72)
        cs.append(pt)
    c = (np.mean([p[0] for p in cs]), min(p[1] for p in cs) - 120)
    for i, h in enumerate(w.hunters):
        P = PX(h['path'])
        kk = 1.25 if i == 0 else .55
        pts = P.sub(0, P.L, 4)
        pl = Lyr(pbox(pts, 10))
        t = 0.0
        while t < P.L:
            pl.line([tuple(x) for x in P.sub(t, min(t + 9, P.L), 3)], 3.0 if i == 0 else 2.0, 255)
            t += 16
        cv.neonL(pl, WHITE * .9, core=.85 * kk, g1=(3, .5 * kk), g2=None)
        hy.head(cv, P, P.L * .72, 'E', sc=1.2 if i == 0 else .9, mode='ghost', k=kk, col=WHITE * .95)
        tgt = w.sites[h['sites'][-1]]['B']
        hy.hex_tile(cv, (tgt[0] + 56, tgt[1] - 140), 'SITES_LOST' if i == 0 else 'UNTOUCHED', 1 if i == 0 else None, r=26, k=(1.0 if i == 0 else .5))
        hy.leader(cv, tgt + np.array([0, -60]), np.array((tgt[0] + 56, tgt[1] - 114)), k=.6)
    ln = Lyr(pbox(cs + [c], 10))
    for p in cs:
        ln.line([tuple(np.array(c) + np.array([0, 24])), tuple(p)], 1.8, 255, dash=(3, 5))
    cv.neonL(ln, WHITE * .8, core=.8, g1=(2, .4), g2=None)
    ui.hunter_eye(cv, c, 62, 1.0, col=WHITE * .95 + LATT * .05)
    ly = Lyr((c[0] - 120, c[1] - 90, c[0] + 120, c[1] + 90))
    _brackets(cv, np.array(c) + np.array([0, 0]), 112, 1.0, frac=.34, w=5)
    # two eye pips: 'one of two streets'
    for i in range(2):
        pp = (c[0] - 22 + i * 44, c[1] - 112)
        d = Lyr((pp[0] - 14, pp[1] - 14, pp[0] + 14, pp[1] + 14))
        d.ell(pp, 7, v=255, outline=(i != 0), ow=2.2)
        cv.neonL(d, WHITE, core=1.0, g1=(2, .5), g2=None)
    locks(cv, w, k=.3)
    lit = {j for j in range(12) if OUT_H(j) == 0}
    tally_block(cv, w, lit)
    hy.hud(cv, 44, 50, 80, 8, 0)
    hand_custom(cv, ks={i: .5 for i in range(5)})
    a = Ann()
    a.title('05b  HUNTER  ·  hover the eye', 'the corp hunts: two streets, one will be locked at the reveal')
    a.note('1  two pips: this is street 1 of 2', (c[0] + 250, c[1] - 120), (c[0] + 22, c[1] - 112))
    a.note('2  street under the pointer: bright white dashes and a ghost ram;\nthe other street at 45%', (c[0] - 360, c[1] + 330), tuple(cs[0]))
    a.note('3  each street previews its own tile (E ram: yellow only once it fires)', (c[0] + 330, c[1] + 220), (w.sites['t3_c']['B'][0] + 56, w.sites['t3_c']['B'][1] - 140))
    a.note('4  tally: 6 of 12 outcomes belong to this street', (760, 790), (250, 950))
    emit('05b_hunter_hover', cv, a)


def f_05c_site_to_locks():
    """HOVER A SITE, read the hidden routes: which sealed routes can reach it. t2_virus: only lock B lights, a fog thread
    runs from the lock to the Site, and the 4 B outcomes are underlined."""
    w = World('default')
    cv = sealed_scene(w, ['B'])
    sid = 't2_virus'
    B = w.sites[sid]['B']
    lp = [lock_pos(w, i) for i in range(3)]
    for i, L in enumerate('ABC'):
        hot = (L == 'B')
        ui.lock(cv, lp[i], L, 'locked', r=21, k=(1.0 if hot else .32))
    ln = Lyr(pbox([lp[1], B], 30))
    pts = EB.bez(lp[1] + np.array([0, 20]), ((lp[1][0] + B[0]) / 2 + 60, min(lp[1][1], B[1]) - 90), B + np.array([0, -90]))
    ln.line(pts, 2.4, 255, dash=(4, 6))
    cv.neonL(ln, FOGC * .6 + WHITE * .4, core=.95, g1=(3, .6), g2=None)
    ui.glyph_disc(cv, (B[0], B[1] - 100), 14, FOGC, g_qmark, gscale=.62, k=1.0, ring_w=2.2)
    halo_site(cv, B)
    # known beam that crosses here too, shown as a pair chip
    base = np.array([B[0] + 30, B[1] + 150])
    hunter(cv, w, k=.3)
    lit = {j for j in range(12) if OUT_A(j) == 1}
    tally_block(cv, w, lit)
    hy.hud(cv, 44, 50, 80, 8, 0)
    hand_custom(cv, ks={i: .5 for i in range(5)})
    a = Ann()
    a.title('05c  SEALED  ·  hover a Site, read the locks', 'the answer to "who can hit this Site": locks light, a fog thread links them')
    a.note('1  only lock B lights (A and C cannot reach this Site)', (lp[1][0] - 330, lp[1][1] - 170), (lp[1][0] - 8, lp[1][1] - 30))
    a.note('2  fog thread lock -> Site, "?" = reachable, tier unknown', (B[0] + 400, B[1] - 330), (B[0] + 10, B[1] - 150))
    a.note('3  tally: the 4 B outcomes underlined', (760, 790), (250, 950))
    emit('05c_sealed_site_locks', cv, a)


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_0')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
