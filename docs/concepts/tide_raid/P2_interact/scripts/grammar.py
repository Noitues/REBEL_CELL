"""grammar.png: the legend board. Every mark of the system, each drawn at game size on a patch of the real purple city,
in NORMAL | DEUTAN | TRITAN.  python grammar.py
The words are labels for the designer, not game UI."""
import sys, math, time
import numpy as np
from PIL import Image, ImageDraw
from lib import *
import scene as SC
import ui
import hy
import hz
import eb as EB
from hy import PX
from glyphs import *
import cb

OUTP = OUT + 'grammar.png'
BG = None
C0 = np.array([1000.0, 800.0])
TS = 98
GAP = 5
COLS, ROWS = 6, 8
CW = TS * 3 + GAP * 2 + 10
RH = 128
X0, Y0 = 8, 52


def bg():
    global BG
    if BG is None:
        BG = base_city('default')
    return BG


def render(fn, cw=100, off=(0, 0)):
    cv = Cv(bg())
    fn(cv, C0.copy())
    a = to_img(cv.out())
    cx, cy = C0 + np.array(off)
    h = cw / 2
    return a.crop((int(cx - h), int(cy - h), int(cx + h), int(cy + h))).resize((TS, TS), Image.LANCZOS)


def street(a=(-70, 32), b=(70, -32)):
    return PX([C0 + np.array(a), C0 + np.array(b)])


# ------------------------------------------------------------------ mark drawers
def m_beam(typ):
    def f(cv, C):
        P = street((-78, 36), (78, -36))
        hy.ribbon(cv, P, typ, 0, P.L - 12, k=1.0)
        hy.head(cv, P, P.L - 22, typ, sc=1.5)
    return f


def m_heads(cv, C):
    for i, t in enumerate('DNE'):
        hy.head(cv, None, 0, t, sc=1.4, flat=((C[0] - 40 + i * 40, C[1]), (1, 0)))


def m_together(cv, C):
    for i, t in enumerate('DNE'):
        o = (i - 1) * 28
        P = PX([C + np.array([-70, 34 + o * 1.0]), C + np.array([70, -34 + o * 1.0])])
        hy.ribbon(cv, P, t, 0, P.L - 10, chev=True, k=1.0)
        hy.head(cv, P, P.L - 20, t, sc=1.2)


def m_lanes(cv, C):
    P = street((-80, 36), (80, -36))
    for t, o in (('D', 12), ('N', -12)):
        Q = PX([C + np.array([-80, 36 + o]), C + np.array([80, -36 + o])])
        hy.ribbon(cv, Q, t, 0, Q.L, k=1.0)


def m_fog(cv, C):
    pth = np.array([C + np.array([-80, 36]), C + np.array([80, -36])])
    ui.fog_band(cv, pth, 0, plen(pth), width=11, seed=3, k=.9)


def m_lock(letter, state='locked', typ=None):
    def f(cv, C):
        ui.lock(cv, C + np.array([0, 4]), letter, state, typ, r=26)
    return f


def m_hunter_eye(cv, C):
    c = C + np.array([0, -34])
    for sgn in (-1, 1):
        a = C + np.array([sgn * 38, 44])
        ln = Lyr(pbox([c, a], 10))
        ln.line([tuple(c + np.array([sgn * 8, 20])), tuple(a)], 2.4, 255, dash=(7, 6))
        cv.neonL(ln, WHITE * .85, core=.8, g1=(2, .4), g2=None)
        hy.head(cv, None, 0, 'E', sc=.9, flat=(a, (0.6 * sgn, .8)), mode='ghost', col=WHITE * .9)
    ui.hunter_eye(cv, c, 30, 1.0, col=WHITE * .92 + LATT * .08)


def m_hunter_lock(cv, C):
    c = C + np.array([0, -34])
    a = C + np.array([-38, 44])
    b = C + np.array([38, 44])
    ln = Lyr(pbox([c, a, b], 10))
    ln.line([tuple(c + np.array([-8, 20])), tuple(a)], 2.4, 255, dash=(7, 6))
    cv.neonL(ln, WHITE * .85, core=.8, g1=(2, .4), g2=None)
    ui.reticle(cv, a + np.array([0, -4]), 22, WHITE)
    st = Lyr(pbox([b], 30))
    st.line([(b[0] - 15, b[1] - 10), (b[0] + 15, b[1] + 10)], 4, 255)
    st.line([(b[0] - 15, b[1] + 10), (b[0] + 15, b[1] - 10)], 4, 255)
    cv.over(INK, blur(st.m, 2) * 1.6, .85, st.off)
    cv.neonL(st, WHITE * .75, core=.9, g1=None, g2=None)
    ui.hunter_eye(cv, c, 30, 1.0, col=WHITE * .92 + LATT * .08)


def m_hunter_fired(cv, C):
    P = street((-78, 36), (78, -36))
    la = Lyr(pbox(P.sub(P.L * .6, P.L, 3), 10))
    t = P.L * .6
    while t < P.L:
        la.line([tuple(x) for x in P.sub(t, min(t + 9, P.L), 3)], 2.6, 255)
        t += 16
    cv.neonL(la, WHITE * .85, core=.8, g1=(3, .4), g2=None)
    hy.ribbon(cv, P, 'E', 0, P.L * .55, k=1.0)
    hy.head(cv, P, P.L * .6, 'E', sc=1.6)


def m_tier(t):
    def f(cv, C):
        hy.hex_tile(cv, C, t, None, r=34)
    return f


def m_skull(cv, C):
    pl = Lyr((C[0] - 70, C[1] - 70, C[0] + 70, C[1] + 70))
    g_skull(pl, C, 36)
    ring = Lyr((C[0] - 70, C[1] - 70, C[0] + 70, C[1] + 70))
    ring.ell(C, 52, v=255, outline=True, ow=4)
    cv.add(PLUM, blur(pl.m, 20), 1.2, pl.off)
    cv.over(INK, blur(pl.m, 8), .6, pl.off)
    cv.neonL(pl, HOT, core=1.0, g1=(4, 1.0), g2=(14, .7), white=.6)
    cv.neonL(ring, VEIN, core=.9, g1=(3, .8), g2=(9, .5))


def tower_at(cv, C, tier=1, state='healthy', alpha=.9, hs=1.0, dy=36, dx=0):
    B = C + np.array([dx, dy])
    SC.tower(cv, B, tier, state, alpha=alpha, seed=4, hs=hs)
    return B


def m_site_healthy(cv, C):
    tower_at(cv, C)


def m_site_shield(cv, C):
    B = tower_at(cv, C, dy=40)
    hz.sentry_dome(cv, B, 'charged', r=46, h=78)


def m_site_down(cv, C):
    B = tower_at(cv, C, state='DOWN')
    ui.decay_ring(cv, B, frac=.55)
    ui.grease_down(cv, (B[0], B[1] - 34), 26, seed=4)


def m_site_taken(cv, C):
    B = C + np.array([0, 36])
    SC.bloom(cv, [B + np.array([0, -10])], [60], seed=5)
    SC.tower(cv, B, 1, 'TAKEN', seed=4, alpha=.9)
    ui.grease_taken(cv, (B[0], B[1] - 30), 26, seed=4)


def m_site_infected(cv, C):
    B = C + np.array([0, 20])
    SC.bloom(cv, [B + np.array([-30, -10]), B + np.array([30, 0])], [70, 50], seed=6)


def m_towers(cv, C):
    for i, t in enumerate((1, 2, 3)):
        SC.tower(cv, C + np.array([-52 + i * 52, 44]), t, 'healthy', alpha=.9, seed=3 + i)


def m_prog_guard(typ):
    def f(cv, C):
        B = C + np.array([-18, 24])
        SC.tower(cv, B, 1, 'healthy', alpha=.55, seed=2)
        ui.firewall(cv, B, typ)
    return f


def m_prog_shift(cv, C):
    B = C + np.array([20, 20])
    SC.tower(cv, B, 1, 'healthy', alpha=.55, seed=2)
    ui.decoy(cv, B, 'E', 1)


def m_prog_jam(cv, C):
    B = C + np.array([0, 14])
    SC.tower(cv, B, 1, 'healthy', alpha=.55, seed=2)
    ui.tracer(cv, B, 'N')


def m_domes(cv, C):
    for i, st in enumerate(('charged', 'hit', 'spent')):
        B = C + np.array([-74 + i * 74, 40])
        hz.sentry_dome(cv, B, st, hit_at=(B[0] + 20, B[1] - 34) if st == 'hit' else None, r=34, h=58)


def m_card(verb, typ):
    def f(cv, C):
        hy.vcard(cv, C, verb, typ, angle=-4, sc=.82)
    return f


def m_disc(kind, outs):
    def f(cv, C):
        hy.stencil_disc(cv, C + np.array([0, 4]), kind, outs, selected=False, word=kind, r=40, seed=5)
    return f


def m_ring(tier):
    def f(cv, C):
        hy.target_ring(cv, C + np.array([0, 20]), tier, r=40)
    return f


def m_stop(cv, C):
    P = street((-60, 27), (60, -27))
    hy.ribbon(cv, P, 'D', 0, P.L * .5 - 16, k=1.0)
    hy.stop_block(cv, P, P.L * .5, 'HOLDS')
    hy.dead_trail(cv, P, P.L * .5 + 28, P.L)


def m_home(hp=44, preview=0, hit=0, spark=False, chip=None):
    def f(cv, C):
        B = C + np.array([0, 16])
        SC.home_deck(cv, B, hp=hp, preview=preview, hit=hit)
        if spark:
            hy.spark_ticks(cv, B, hit, hp)
        if chip:
            hy.hex_tile(cv, (B[0] + 82, B[1] - 56), chip[0], chip[1], r=22)
    return f


def m_tile_num(cv, C):
    hy.hex_tile(cv, C + np.array([-14, 0]), 'SITES_LOST', 1, r=28)


def m_tally(cv, C):
    hy.tally(cv, C, {'UNTOUCHED': 2, 'HOLDS': 2, 'SITES_LOST': 2, 'DAMAGED': 1}, r=8.5, gap=17, group_gap=7)


def m_decay_clock(cv, C):
    B = C + np.array([0, 24])
    SC.tower(cv, B, 1, 'DOWN', alpha=.9, seed=4)
    ui.decay_ring(cv, B, frac=.3)
    ui.grease_down(cv, (B[0], B[1] - 34), 26, seed=4)


def m_hand_off(cv, C):
    B = C + np.array([10, 24])
    ui.decoy(cv, B, 'N', 1)


T3 = ['UNTOUCHED', 'HOLDS', 'SITES_LOST']

# (label, drawer, crop_w, offset)
CELLS = [
    ('BEAM D drone: dart + chain links', m_beam('D'), 130, (0, 0)),
    ('BEAM N netrunner: block + braid', m_beam('N'), 130, (0, 0)),
    ('BEAM E enforcer: ram + hazard band', m_beam('E'), 130, (0, 0)),
    ('HEADS at game size 31px D N E', m_heads, 120, (0, 0)),
    ('all three beams together', m_together, 150, (0, 0)),
    ('two lanes max (D +13, N -13)', m_lanes, 120, (0, 0)),
    ('SEALED route: fog corridor', m_fog, 130, (0, 0)),
    ('LOCKED: hex padlock + letter', m_lock('A'), 90, (0, 0)),
    ('REVEALED as D (lock -> dart)', m_lock('A', 'open', 'D'), 90, (0, 0)),
    ('REVEALED as N (lock -> block)', m_lock('B', 'open', 'N'), 90, (0, 0)),
    ('REVEALED as E (lock -> ram)', m_lock('C', 'open', 'E'), 90, (0, 0)),
    ('HUNTER: white eye, 2 streets', m_hunter_eye, 144, (0, 0)),
    ('HUNTER locked: reticle / strike', m_hunter_lock, 144, (0, 0)),
    ('HUNTER fired: white -> yellow E', m_hunter_fired, 130, (0, 0)),
    ('TIER UNTOUCHED / EVADED', m_tier('UNTOUCHED'), 90, (0, 0)),
    ('TIER HOLDS', m_tier('HOLDS'), 90, (0, 0)),
    ('TIER SITES LOST (+ count)', m_tile_num, 100, (0, 0)),
    ('TIER DAMAGED (solid plate)', m_tier('DAMAGED'), 90, (0, 0)),
    ('TIER BREACHED (solid, double hex)', m_tier('BREACHED'), 100, (0, 0)),
    ('CITY LOST: skull', m_skull, 120, (0, 0)),
    ('SITE healthy (ICE tower)', m_site_healthy, 120, (0, -6)),
    ('SITE towers T1 T2 T3', m_towers, 170, (0, -6)),
    ('SITE shielded (sentry dome)', m_site_shield, 130, (0, -22)),
    ('SITE DOWN + DECAY clock', m_decay_clock, 120, (0, -10)),
    ('SITE TAKEN (plum stump, red X)', m_site_taken, 130, (0, -8)),
    ('SITE INFECTED (plum body, hot front)', m_site_infected, 150, (0, -4)),
    ('PROGRAM GUARD vs D', m_prog_guard('D'), 130, (0, -8)),
    ('PROGRAM GUARD vs N', m_prog_guard('N'), 130, (0, -8)),
    ('PROGRAM GUARD vs E', m_prog_guard('E'), 130, (0, -8)),
    ('PROGRAM SHIFT (decoy + hand-off)', m_hand_off, 150, (0, -34)),
    ('PROGRAM JAM (tracer)', m_prog_jam, 130, (0, -4)),
    ('SENTRY charged / hit / spent', m_domes, 220, (0, -10)),
    ('CARD GUARD answers D', m_card('GUARD', 'D'), 130, (0, 0)),
    ('CARD GUARD answers N', m_card('GUARD', 'N'), 130, (0, 0)),
    ('CARD SHIFT answers E', m_card('SHIFT', 'E'), 130, (0, 0)),
    ('CARD JAM answers N', m_card('JAM', 'N'), 130, (0, 0)),
    ('DISC DEPLOY', m_disc('DEPLOY', ['UNTOUCHED', 'SITES_LOST', 'DAMAGED']), 150, (0, -22)),
    ('DISC HOLD', m_disc('HOLD', ['HOLDS', 'SITES_LOST', 'DAMAGED']), 150, (0, -22)),
    ('DISC MOVE', m_disc('MOVE', T3), 150, (0, -22)),
    ('DISC SACRIFICE', m_disc('SACRIFICE', ['HOLDS', 'SITES_LOST', 'BREACHED']), 150, (0, -22)),
    ('TIER CARRIER 1: target ring', m_ring('SITES_LOST'), 120, (0, 14)),
    ('TIER CARRIER 2: stop block + dead trail', m_stop, 130, (0, 0)),
    ('HOME ring full 44/50', m_home(), 190, (0, -6)),
    ('HOME ring preview (-6 ticks)', m_home(preview=6, chip=('DAMAGED', None)), 190, (0, -26)),
    ('HOME ring hit (ticks fly off)', m_home(hit=6, spark=True), 190, (0, -26)),
    ('HOME cleared (mint, SACRIFICE)', m_home(chip=('UNTOUCHED', None)), 190, (0, -26)),
    ('TALLY (odds as a row of marks)', m_tally, 120, (0, 0)),
]


def main():
    sheet = Image.new('RGB', (1920, 1080), (8, 6, 20))
    d = ImageDraw.Draw(sheet)
    fT = font(22, False, 700, 75)
    fL = font(12, False, 500, 80)
    d.text((10, 8), 'GRAMMAR BOARD  |  every mark at game size on the real city  |  each shown NORMAL  |  DEUTAN  |  TRITAN', font=fT, fill=(127, 239, 255))
    d.text((10, 34), 'hue = type (D blue dart, N magenta block, E yellow ram) | tier = ring / block / tile (never on the beam) | towers = quiet slate | labels are for the designer, not game UI', font=fL, fill=(150, 160, 190))
    t0 = time.time()
    for i, (label, fn, cw, off) in enumerate(CELLS):
        r, c = divmod(i, COLS)
        x = X0 + c * (CW + 4)
        y = Y0 + r * RH
        im = render(fn, cw, off)
        sims = [im, cb.sim(im, cb.DEUT), cb.sim(im, cb.TRIT)]
        for j, s in enumerate(sims):
            sheet.paste(s, (x + j * (TS + GAP), y))
        d.text((x, y + TS + 3), label, font=fL, fill=(190, 198, 222))
    print('cells', len(CELLS), round(time.time() - t0, 1), 's')
    sheet.save(OUTP)
    print('saved grammar.png')


if __name__ == '__main__':
    main()
