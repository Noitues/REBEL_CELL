"""mp_beat: the E10 p3 resolve beat on the rebuilt board (2026-11-03 rebuild), neutral skin, 1920x1080, 60 fps.

Review 2.11 (REVIEW_RESPONSE: "the whole beat runs under 4 s with skip; every effect fits the 0.6 s T2 cap; no per-effect overrides"):
  - every effect is the designers' own effect at its own (<= 600 ms) timing: M/P/S/T from mp_eff, C/D/H/L from the C/D/H/L designer's
    fx_cdhl (a read-only snapshot in ../cdhl_snap, of their 2026-11-04 03:35 source, re-taken 04:22; md5 in SNAPSHOT_TIME.txt);
  - effects run on concurrent tracks in the HUD chain order (1 TWIST, 2 TRIGGER, 3 BRACE, 4 GUNS, 5 LANDS, 6 RINGS STEP / W4 enters),
    each one starting while the one before it settles; the whole beat is TOTAL_MS (< 4000);
  - any input skips: the frame on screen dissolves to the settled frame over SKIP_MS (no on-screen word; open question for the designer).
Review 1.6: every effect draws on the board, under the HUD and the hand, except trace_add and refund, which may cross.
Review 1.8: kill marks in the cause colour (fx_kill draws CELL_PINK: our guns, our Trigger).

The board states are the generator's own renders (work/bases, f2 of state_e10):
  p2 (preview) -> commit -> p3_pre board with the board refund coin of p3 (the wheel keeps it from the preview on; fx_refund's own
  pre-state does the same) and the p3_pre HUD (Trace 3, RAM 2) -> trace_add (HUD to p3_mid: Trace 4) -> refund (HUD to p3: RAM 3 and
  the REFUND tab) -> kill (Worm 2's cell to p3_kill) -> settle (board to p3_after: ring NOW empty, gun marks, landing arcs and the board
  coin gone) -> rings_step (p3_after / p3_clean) -> wave_enter.

NOT TO SHIP (rules question, REVIEW_RESPONSE "Shove bump, Twist render"): f2 already holds ring +1 where Twist leaves it, so the beat
draws ring +1 one sector back (-60 deg) from SEND IT until Twist turns it.  The painted resolve marks inside ring +1 (gun tracer, hit
star, Trigger route) stay where the resolve paints them; only the cells turn.
"""
import sys, os, math, json
sys.dont_write_bytecode = True
ME = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/'
sys.path.insert(0, ME + 'src')
sys.path.insert(1, ME + 'cdhl_snap')
import numpy as np
from scipy import ndimage as ndi
import mp_eff as E
from mp_lib import *
import fxk_lib as K
import fx_cdhl as CD

SK = 'neutral'
FB = Box(0, 0, W, H)
SKIP_MS = 200            # skip: any input dissolves the frame on screen to the settled frame (e_io3)
TAIL_MS = 200            # settled frames after the last effect

# ------------------------------------------------------------------ tracks: name -> (start ms, length ms).  Lengths are the effects' own.
L_ = {k: v['timing']['total'] for k, v in E.FX.items()}
C_ = {f['id']: f['timing']['total'] for f in CD.FX}
TRACKS = [
    ('commit', 0, L_['fx_commit'], 'T', 'SEND IT: pencil burns into paint'),
    ('twist', 420, L_['fx_twist'], 'M', '1 TWIST: ring +1 turns one sector'),
    ('trace_add', 600, L_['fx_trace_add'], 'S', '2 TRIGGER: Trace 3 -> 4'),
    ('trigger_hit', 760, C_['fx_trigger_hit'], 'D', '2 TRIGGER: hits Packet 1 (s3, s4)'),
    ('kill_p1', 1000, C_['fx_kill'], 'D', '2 TRIGGER: Packet 1 dies'),
    ('refund', 1100, C_['fx_refund'], 'L', '2 TRIGGER: refund, RAM 2 -> 3'),
    ('gun_hit', 1300, C_['fx_gun_hit'], 'D', '4 GUNS: s0 shot 1 on Worm 2'),
    ('gun_adj', 1360, C_['fx_gun_hit'], 'D', '4 GUNS: s2 TURRET on the Adjuster'),
    ('ricochet_gold', 1420, C_['fx_ricochet_gold'], 'D', '4 GUNS: s4 2 shots warded (Packet 6)'),
    ('kill', 1560, C_['fx_kill'], 'D', '4 GUNS: s0 shot 2, Worm 2 dies'),
    ('shield_block', 1900, L_['fx_shield_block'], 'P', '5 LANDS: Worm 3 on s1 SHIELD, absorbed 2'),
    ('brace_block', 1900, L_['fx_brace_block'], 'P', '3 BRACE / 5 LANDS: Worm 3 on s2, braced 3'),
    ('soak_take', 1930, L_['fx_soak_take'], 'P', '5 LANDS: s1 soaked 1 (under the plate)'),
    ('clear', 2400, C_['fx_clear'], 'L', '5 LANDS: THROUGH 0'),
    ('settle', 2640, 200, '-', 'board hand-off: ring NOW clears'),
    ('rings_step', 2800, L_['fx_rings_step'], 'M', '6 RINGS STEP'),
    ('wave_enter', 3200, L_['fx_wave_enter'], 'M', '6 W4 enters'),
]
for _n, _s, _d, _f, _c in TRACKS:
    assert _d <= E.CAP_MS, (_n, _d)
TL = {n: s for n, s, d, f, c in TRACKS}
DUR = {n: d for n, s, d, f, c in TRACKS}
END_MS = max(s + d for n, s, d, f, c in TRACKS)
TOTAL_MS = END_MS
assert TOTAL_MS < 4000, TOTAL_MS

# ------------------------------------------------------------------ bases
B2, U2 = below(SK, 'p2'), above(SK, 'p2')
B3p, U3p = below(SK, 'p3_pre'), above(SK, 'p3_pre')
U3m = above(SK, 'p3_mid')
B3, U3 = below(SK, 'p3'), above(SK, 'p3')
B3k = below(SK, 'p3_kill')
B3a, B3c = below(SK, 'p3_after'), below(SK, 'p3_clean')
P3FULL = comp(B3, U3)
P3PRE_FULL = None          # set below, once BFIX exists

# the board refund coin (the cyan plus star at the Trigger kill, CD.REFUND_AT): p3_pre has none, p2 and p3 have it
_cb = Box(380, 700, 500, 820)
_cm = np.zeros((H, W), np.float32)
_cm[_cb.y0:_cb.y1, _cb.x0:_cb.x1] = ndi.binary_dilation(np.abs(_cb.crop(B3p) - _cb.crop(B3)).max(2) > 6, iterations=2)
_cm = ndi.gaussian_filter(_cm, 0.7)
BFIX = B3p * (1 - _cm[..., None]) + B3 * _cm[..., None]
P3PRE_FULL = comp(BFIX, U3p)

# ------------------------------------------------------------------ twist (workaround, see the module doc)
RBOX = Box(205, 209, 868, 872)
TW3 = (210.0, 0.0)                         # f2 ring +1 units (Payload 4 s3-4, Packet 5 s0): their resolve positions
_mk = np.zeros((H, W), bool)
_mk |= E.cmask(SK, 'p3', 'guns')
_r1 = (FRHO > 268) & (FRHO < 331)
_pk = E.pinkish(B3) & _r1 & ~ndi.binary_dilation(E.cmask(SK, 'p3', 'adj_hp') | E.cmask(SK, 'p3', 'adj'), iterations=3)
_mk |= _pk
_mk = ndi.binary_dilation(_mk & _r1, iterations=2)
TW_MARKS = RBOX.crop(ndi.gaussian_filter(_mk.astype(np.float32), 0.7)[..., None])


def twist_board(board, t, red, marks):
    out = E.twist_core(t, red, marks, board, RBOX, SK, d0=-60.0, units=TW3)
    out = mix(out, RBOX.crop(board), TW_MARKS)
    return out


# ------------------------------------------------------------------ C/D/H/L effect layers (their draw functions, their timing)
def _cd(fid, box=None, **kw):
    fx = dict(CD.BYID[fid])
    if box is not None:
        fx['box'] = box
    fx.update(kw)
    return fx


def d_trigger_hit_seq(lay, t, c):
    """fx_trigger_hit in the beat: SEND IT has already burned the pencil route into paint (fx_commit), so the ignite and the pencil X
    are not drawn again; the two hit frames run on fx_trigger_hit's own clock (sector 3 at 120 ms, sector 4 at 240 ms)."""
    red = c.reduce
    for (x, y), t0, sd in ((CD.X3, 120, 3), (CD.X4, 240, 4)):
        if t >= t0 or red:
            tt = t - t0
            k = 1.0 if red else CD.eback(CD.seg(tt, 0, 60))
            fd = 1 - CD.seg(tt, 200, 340) if not red else 1 - CD.seg(t, 300, 500)
            if not red:
                CD.speed_lines(lay, x, y, CD.TRIG_R * 0.7, CD.TRIG_R * 2.2, 12, math.sin(math.pi * CD.seg(tt, 0, 220)), op=fd, seed=sd)
                CD.shards(lay, x, y, CD.seg(tt, 20, 300), n=7, dist=CD.TRIG_R * 1.5, size=7, op=1 - CD.seg(tt, 230, 300), seed=sd + 20)
            CD.burst(lay, x, y, CD.TRIG_R, k, n=11, seed=sd, op=fd)


GUN_ADJ = ((681.0, 651.0), (789.0, 706.0))     # p3 'guns' mask, sector 2 TURRET mark: inner end -> the hit star on the Adjuster


def d_gun_adj(lay, t, c):
    """fx_gun_hit on the sector 2 TURRET shot at the Adjuster (h 1, 10 -> 9): d_gun_hit's tracer, hit frame, speed lines and shards on the
    TURRET mark.  The Adjuster's lost segment is already drawn by the board (its pink hatched segment), so no tick is drawn here."""
    (p0, p1) = GUN_ADJ
    red = c.reduce
    u = 1.0 if red else CD.eout(CD.seg(t, 0, 80))
    CD.tracer(lay, p0, p1, u, op=1 - CD.seg(t, 300, 460))
    if t >= 80 or red:
        k = 1.0 if red else CD.eback(CD.seg(t, 80, 140))
        fade = 1 - CD.seg(t, 300, 520) if not red else 1 - CD.seg(t, 300, 500)
        if not red:
            CD.speed_lines(lay, p1[0], p1[1], CD.GUN_R * 0.7, CD.GUN_R * 2.3, 14, math.sin(math.pi * CD.seg(t, 80, 300)), op=fade, seed=6)
            CD.shards(lay, p1[0], p1[1], CD.seg(t, 100, 420), n=8, dist=CD.GUN_R * 1.6, size=8, op=1 - CD.seg(t, 330, 420), seed=8)
        CD.burst(lay, p1[0], p1[1], CD.GUN_R, k * (1 - 0.25 * CD.seg(t, 300, 520)), n=11, seed=4, op=fade)


def d_kill_at(tok):
    def d(lay, t, c):
        old = CD.KILL_TOK
        CD.KILL_TOK = tok
        try:
            CD.d_kill(lay, t, c)
        finally:
            CD.KILL_TOK = old
    return d


CDX = {
    'trigger_hit': _cd('fx_trigger_hit', draw=d_trigger_hit_seq),
    'kill_p1': _cd('fx_kill', box=(470, 610, 790, 930), draw=d_kill_at(CD.TOK3['1'])),
    'gun_hit': _cd('fx_gun_hit'),
    'gun_adj': _cd('fx_gun_hit', box=(600, 570, 880, 800), draw=d_gun_adj),
    'ricochet_gold': _cd('fx_ricochet_gold'),
    'kill': _cd('fx_kill', draw=d_kill_at(CD.TOK3['2'])),
    'refund': _cd('fx_refund'),
    'clear': _cd('fx_clear'),
}
KILL_MASK = None


def kill_mask():
    """fx_kill's own state region x the p3 -> p3_kill change (as fxk_lib._smask), full frame"""
    global KILL_MASK
    if KILL_MASK is None:
        fx = CDX['kill']
        x0, y0, x1, y1 = fx['box']
        m = K.poly_mask_full(fx['state_region'], fx['box'], 1.2)
        d = (np.abs(B3k[y0:y1, x0:x1] - B3[y0:y1, x0:x1]).max(2) > 6).astype(np.float32)
        d = ndi.gaussian_filter(ndi.maximum_filter(d, 5), 1.2)
        full = np.zeros((H, W), np.float32)
        full[y0:y1, x0:x1] = m * d
        KILL_MASK = full[..., None]
    return KILL_MASK


def cd_layer(name, t, red, over_hud=False):
    fx = CDX[name]
    lay = K.Lay(fx['box'], 2)
    ctx = K.Ctx(fx, SK, red)
    if over_hud:
        fx['draw_over'](lay, t, ctx)
    else:
        fx['draw'](lay, t, ctx)
    return fx['box'], np.asarray(lay.done(), np.float32)


def paste_over(img, box, rgba, op=1.0):
    x0, y0, x1, y1 = box
    a = rgba[..., 3:4] / 255.0 * op
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - a) + rgba[..., :3] * a


# ------------------------------------------------------------------ M/P/S boxes in the beat
SHBOX = E.FX['fx_shield_block']['_box']
BRBOX = E.FX['fx_brace_block']['_box']
SOBOX = E.FX['fx_soak_take']['_box']
RSBOX = Box(36, 40, 1036, 1040)
WVBOX = E.FX['fx_wave_enter']['_box']
TRBOX = Box(1240, 560, 1620, 1080)
TR_PIP = (E.TR_X0['p3'] + 3 * E.TR_PITCH, E.TR_ROW['p3'])     # pip 4 of the p3 TRACE row
TR_SLOT = (1275, 769, 1466, 1041)                              # the TRIGGER PLAYED slot of the p3 hand (generator mask card_2)
UA3 = E.unit_alpha(B3a, B3c, ('ua_p3after', SK))
_RS_END = None


def rs_end():
    global _RS_END
    if _RS_END is None:
        b = B3a.copy()
        b[RSBOX.y0:RSBOX.y1, RSBOX.x0:RSBOX.x1] = E.rings_step_core(600, True, False, B3a, B3c, RSBOX, UA3)
        _RS_END = b
    return _RS_END


def act(name, T):
    """local time of a track and whether it is running"""
    t = T - TL[name]
    return t, (0 <= t < DUR[name])


def frame(T, red=False):
    """the beat at T ms (full frame, RGB float)"""
    # ---- board state
    t_rf, _ = act('refund', T)
    k_rf = CD.refund_state(max(0.0, t_rf), K.Ctx(CDX['refund'], SK, red)) if t_rf >= 0 else 0.0
    board = BFIX if k_rf <= 0 else (BFIX * (1 - k_rf) + B3 * k_rf)
    t_k, _ = act('kill', T)
    if t_k >= 0:
        kk = CD.kill_state(min(t_k, DUR['kill']), K.Ctx(CDX['kill'], SK, red))
        board = board * (1 - kill_mask() * kk) + B3k * (kill_mask() * kk)
    t_s, _ = act('settle', T)
    k_set = e_io3(seg(t_s, 0, DUR['settle'])) if t_s >= 0 else 0.0
    if k_set > 0:
        board = board * (1 - k_set) + B3a * k_set
    board = board.copy()
    hud = U3p
    t_c, on_c = act('commit', T)
    if on_c:
        bc, uc = E.commit_core(t_c, red, True, B2, BFIX, U2, U3p, FB, ('beat',), E.FX['fx_commit']['seed'], split=True)
        board, hud = bc, uc
    # ---- twist (ring +1 one sector back until Twist turns it: not to ship, see the doc)
    t_tw, on_tw = act('twist', T)
    if t_tw < DUR['twist']:
        tt = min(max(t_tw, 0.0), DUR['twist'])
        board[RBOX.y0:RBOX.y1, RBOX.x0:RBOX.x1] = twist_board(board, tt, red, on_tw)
    # ---- C/D/H/L layers under the HUD
    for nm in ('trigger_hit', 'kill_p1', 'gun_hit', 'gun_adj', 'ricochet_gold', 'kill'):
        t, on = act(nm, T)
        if on:
            box, rgba = cd_layer(nm, t, red)
            paste_over(board, box, rgba)
    t_cl, _ = act('clear', T)
    if t_cl >= 0 and k_set < 1:                     # the check stays (its still) until the board hand-off takes the arc away
        box, rgba = cd_layer('clear', min(t_cl, DUR['clear']), red)
        paste_over(board, box, rgba, 1 - k_set)
    # ---- P blocks (Worm 3 lands 3: s1 SHIELD absorbed 2 + soaked 1, s2 TURRET braced 3)
    # the soak funnel goes first, so the shield plate stays whole on top of it (the third hit of the same landing overflows under the plate)
    for nm, box, core in (('soak_take', SOBOX, E.soak_core), ('shield_block', SHBOX, E.shield_core), ('brace_block', BRBOX, E.brace_core)):
        t, on = act(nm, T)
        if on:
            board[box.y0:box.y1, box.x0:box.x1] = core(t, red, True, board, box)
    # ---- rings step, then W4 enters
    t_r, on_r = act('rings_step', T)
    if t_r >= 0:
        if on_r:
            board[RSBOX.y0:RSBOX.y1, RSBOX.x0:RSBOX.x1] = E.rings_step_core(t_r, red, True, B3a, B3c, RSBOX, UA3)
        else:
            board = rs_end().copy()
    t_w, on_w = act('wave_enter', T)
    if t_w >= 0:
        tw_ = min(t_w, DUR['wave_enter'])
        board[WVBOX.y0:WVBOX.y1, WVBOX.x0:WVBOX.x1] = E.wave_core(tw_, red if on_w else True, on_w, board, B3a, B3c, P3FULL, WVBOX, SK)
    # ---- HUD and hand
    t_tr, on_tr = act('trace_add', T)
    if t_tr >= 166:
        hud = U3m
    if k_rf > 0:
        hud = hud * (1 - k_rf) + U3 * k_rf
    img = comp(board, hud)
    # ---- the two effects allowed over the HUD
    if on_tr:
        img[TRBOX.y0:TRBOX.y1, TRBOX.x0:TRBOX.x1] = E.trace_core(t_tr, red, True, TRBOX.crop(img), TRBOX, P3PRE_FULL, TR_PIP, TR_SLOT)
    t_rf2, on_rf = act('refund', T)
    if on_rf:
        box, rgba = cd_layer('refund', t_rf2, red, over_hud=True)
        paste_over(img, box, rgba)
    return img


_END = {}


def settled(red=False):
    """the settled frame (after W4 enters): the skip target"""
    if red not in _END:
        _END[red] = frame(END_MS + 1, red)
    return _END[red]


def skip_frame(T, Ts, live, red=False):
    """the frame at T when the player skipped at Ts: live = frame(T) (still running under the dissolve)"""
    k = e_io3(seg(T - Ts, 0, SKIP_MS))
    return live * (1 - k) + settled(red) * k
