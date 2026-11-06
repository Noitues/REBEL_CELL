"""Pass 2 new frames: 14 response preview, 15 hunter playout, 16 sentry shield.  python hb3.py [14 15 16]"""
import sys, time
from hb import *
import hz


def crop_world(cv, box=(110, 330, 1070, 870)):
    a = finish(cv, vig=.2, scan=.05, fringe=0)
    return to_img(a).crop(box)


def f_14():
    """RESPONSE beat, the consequence of each disc drawn ON THE MAP (a 2x2 board of the t1 cluster: HOLD = baseline,
    DEPLOY, MOVE, SACRIFICE). Each quadrant: the disc, the changed marks, and the new tier tiles."""
    w = World('default')
    quads = []
    # ---- HOLD (baseline): nothing changes
    cv, st = forecast_world(w)
    tiles_at(cv, w, [('t1_c', 'HOLDS', None), ('t1_b', 'SITES_LOST', 1), ('t2_intel', 'UNTOUCHED', None)])
    hy.home_chip(cv, w.home, 6)
    quads.append(('HOLD', ['HOLDS', 'SITES_LOST', 'DAMAGED'], crop_world(cv)))
    # ---- DEPLOY: the N guard card is placed on t1_b -> K2 is stopped there (SITES_LOST -> HOLDS)
    prog = dict(PROGRAMS)
    prog['t1_b'] = ('GUARD', 'N')
    cv, st = forecast_world(w, programs=prog, target={'K2': ('t1_b', 'HOLDS')})
    tiles_at(cv, w, [('t1_c', 'HOLDS', None), ('t1_b', 'HOLDS', None), ('t2_intel', 'UNTOUCHED', None)])
    hy.home_chip(cv, w.home, 6)
    quads.append(('DEPLOY', ['UNTOUCHED', 'HOLDS', 'DAMAGED'], crop_world(cv)))
    # ---- MOVE: the D guard slides from t1_c to t1_b: K1 now stops at t1_b (its stop block moves), K2 still lands there
    prog = {'t1_b': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}
    cv, st = forecast_world(w, programs=prog, target={'K1': ('t1_b', 'HOLDS')}, ring_r={'K1': 40, 'K2': 58})
    a, b = w.sites['t1_c']['B'], w.sites['t1_b']['B']
    ui.firewall(cv, a, 'D', mode='ghost')
    EB.grease_arrow(cv, (a[0] + 10, a[1] - 80), ((a[0] + b[0]) / 2 + 10, min(a[1], b[1]) - 150), (b[0] + 20, b[1] - 74))
    tiles_at(cv, w, [('t1_b', 'HOLDS', None), ('t1_b', 'SITES_LOST', 1), ('t2_intel', 'UNTOUCHED', None)])
    hy.home_chip(cv, w.home, 6)
    quads.append(('MOVE', ['UNTOUCHED', 'HOLDS', 'SITES_LOST'], crop_world(cv)))
    # ---- SACRIFICE: t1_d is given up (DOWN) so HOME takes nothing: preview ticks clear, HOME chip goes mint
    cv, st = forecast_world(w, home_prev=0)
    d = w.sites['t1_d']['B']
    ui.grease_down(cv, (d[0], d[1] - 34), 26, seed=4, k=.9)
    hy.target_ring(cv, d, 'SITES_LOST', r=46)
    hm = w.home
    cvh = np.array(hm) + np.array([60, -30])
    arc = EB.bez(cvh, ((hm[0] + d[0]) / 2 + 40, min(hm[1], d[1]) - 70), d + np.array([0, -20]))
    ly = Lyr(pbox(arc, 14))
    ly.line(arc, 3.0, 255, dash=(9, 6))
    cv.neonL(ly, TIER['SITES_LOST'], core=1.0, g1=(3, .7), g2=None)
    tiles_at(cv, w, [('t1_c', 'HOLDS', None), ('t1_b', 'SITES_LOST', 1), ('t2_intel', 'UNTOUCHED', None)])
    hy.hex_tile(cv, (d[0] + 84, d[1] + 8), 'SITES_LOST', 1, r=30)
    hy.hex_tile(cv, (hm[0] + 112, hm[1] - 74), 'UNTOUCHED', None, r=30)
    quads.append(('SACRIFICE', ['HOLDS', 'SITES_LOST', 'BREACHED'], crop_world(cv)))
    sheet = Image.new('RGB', (1920, 1080), (8, 6, 20))
    for i, (word, outs, im) in enumerate(quads):
        x, y = (i % 2) * 960, (i // 2) * 540
        sheet.paste(im.resize((960, 540)), (x, y))
    cv2 = Cv(np.asarray(sheet, np.float32) / 255)
    for i, (word, outs, im) in enumerate(quads):
        x, y = (i % 2) * 960, (i // 2) * 540
        hy.stencil_disc(cv2, (x + 840, y + 420), word, outs, selected=(word == 'HOLD'), word=word, r=46, seed=5 + i)
    ln = Lyr(ss=1)
    ln.line([(960, 0), (960, 1080)], 4, 255)
    ln.line([(0, 540), (1920, 540)], 4, 255)
    cv2.over(INK, ln.m, 1.0)
    to_img(cv2.out()).save(FR + '14_response_preview.png')
    print('saved 14')


def f_15():
    """HUNTER playout: the eye has locked street 0 (reticle), the unchosen street is struck out; the beam it spawns
    is an E ram, so it is yellow only now. Impact on the Site at the street's end (no guard): SITES_LOST."""
    w = World('default')
    cv = new_canvas(w)
    sealed_layers(cv, w, k=.35)
    H0 = w.hunters[0]
    P0 = PX(H0['path'])
    tgt = H0['sites'][-1]
    tB = w.sites[tgt]['B']
    s_t = nearest_s(H0['path'], tB)
    H1 = w.hunters[1]
    P1 = PX(H1['path'])
    pts = P1.sub(0, P1.L, 4)
    ly = Lyr(pbox(pts, 10))
    t = 0.0
    while t < P1.L:
        ly.line([tuple(x) for x in P1.sub(t, min(t + 9, P1.L), 3)], 1.6, 255)
        t += 16
    cv.neonL(ly, WHITE * .7, core=.55, g1=None, g2=None)
    m = P1.at(P1.L * .5)[0]
    st = Lyr((m[0] - 40, m[1] - 30, m[0] + 40, m[1] + 30))
    st.line([(m[0] - 26, m[1] - 17), (m[0] + 26, m[1] + 17)], 5, 255)
    st.line([(m[0] - 26, m[1] + 17), (m[0] + 26, m[1] - 17)], 5, 255)
    cv.over(INK, blur(st.m, 2) * 1.6, .85, st.off)
    cv.neonL(st, WHITE * .9, core=1.0, g1=(2, .4), g2=None)
    head_s = s_t - 70
    la = Lyr(pbox(P0.sub(head_s, s_t + 5, 3), 10))
    t = head_s
    while t < s_t:
        la.line([tuple(x) for x in P0.sub(t, min(t + 9, s_t), 3)], 2.6, 255)
        t += 16
    cv.neonL(la, WHITE * .85, core=.8, g1=(3, .4), g2=None)
    hy.ribbon(cv, P0, 'E', 0, head_s, k=1.0)
    for r in KN:
        R = w.routes[r]
        P = PX(R['path'])
        hy.dead_trail(cv, P, R['ext'], P.L - 4, k=.35)
    draw_world(cv, w, {'t1_a': 'DOWN'}, {'t1_c': ('GUARD', 'D'), 't2_intel': ('SHIFT', 'E')}, home_kw=dict(hp=44), idle=IDLE)
    hy.target_ring(cv, tB, 'SITES_LOST')
    ui.flash(cv, tB + np.array([0, -30]), 90, TIER['SITES_LOST'] * .4 + WHITE * .6, .5)
    ui.shock(cv, tB, 60, TIER['SITES_LOST'], w=3.5, k=.9)
    ui.bits(cv, tB + np.array([0, -30]), TYPE_COL['E'] * .7 + WHITE * .3, n=45, r=130, seed=7)
    for off, kk in ((70, .6), (140, .35)):
        hy.head(cv, P0, head_s - off, 'E', sc=2.0, mode='ghost', k=kk)
    hy.head(cv, P0, head_s, 'E', sc=2.2)
    cs = [P0.at(P0.L * .72)[0], P1.at(P1.L * .72)[0]]
    c = (np.mean([p[0] for p in cs]), min(p[1] for p in cs) - 120)
    ui.hunter_eye(cv, c, 54, .9, col=WHITE * .92 + LATT * .08)
    ui.reticle(cv, tB + np.array([0, -30]), 62, WHITE, k=.9)
    hy.hex_tile(cv, (tB[0] + 70, tB[1] - 150), 'SITES_LOST', 1, r=30)
    hy.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '15_hunter_playout')


def f_16():
    """SENTRY shield (H7c): a Site-local dome that absorbs ONE beam. Three states in one raid: t2_virus SPENT (D hit it
    earlier), t2_breach HIT now (N beam lands, ripple, pip empties), t1_d CHARGED (full pip). The beam stops at the dome."""
    w = World('default')
    cv = new_canvas(w)
    k1, k2 = w.routes['K1'], w.routes['K2']
    P1, P2 = PX(k1['path']), PX(k2['path'])
    s1 = w.visit('K1', 't2_virus')
    s2 = w.visit('K2', 't2_breach')
    hy.ribbon(cv, P1, 'D', k1['ext'], s1, k=.32, glow=.3)
    hy.ribbon(cv, P2, 'N', k2['ext'], s2, k=1.15)
    draw_world(cv, w, {'t1_a': 'DOWN'}, {}, home_kw=dict(hp=44), idle=('t1_b', 't1_c'))
    ui.focus_dim(cv, w.sites['t2_breach']['B'], 520, .45)
    hz.sentry_dome(cv, w.sites['t2_virus']['B'], 'spent')
    hz.sentry_dome(cv, w.sites['t1_d']['B'], 'charged')
    bB = w.sites['t2_breach']['B']
    hit = (bB[0] + 28, bB[1] - 36)
    hz.sentry_dome(cv, bB, 'hit', hit_at=hit)
    ui.bits(cv, np.array(hit), TYPE_COL['N'] * .6 + WHITE * .4, n=50, r=120, seed=6)
    ui.shock(cv, np.array(hit) + np.array([0, 28]), 50, TIER['HOLDS'], w=3.0, k=.8)
    hy.head(cv, P2, s2 - 38, 'N', sc=2.0)
    hy.target_ring(cv, bB, 'HOLDS')
    hy.hex_tile(cv, (bB[0] + 60, bB[1] - 170), 'HOLDS', None, r=28)
    sB = w.sites['t2_virus']['B']
    hy.hex_tile(cv, (sB[0] + 56, sB[1] - 160), 'HOLDS', None, r=24, k=.55)
    hy.hud(cv, 44, 50, 80, 8, 0)
    save(cv, '16_sentry_shield')


if __name__ == '__main__':
    want = sys.argv[1:] or ['14', '15', '16']
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
