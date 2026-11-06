"""rb5_patch (2026-11-04, round 2 gate-1 fixes): the board items the independent gate of round 2 failed
(round2/gate1: S2-1 h02 lift, S3 C11 side arcs, NOW tag box line, Solace crest on the turn pips, p2b tower hover arc, p2b hover path grammar,
L5 dash read).  lw_render installs it after rb4_patch; env RB5=0 skips it.  Every number is a named knob here or in rb_tokens / rb_lift.

  C6   the lift geometry is rb_lift's (one opening, one button column, the fan offsets FAN_OFF (8, 3, 3, 0), the print and drop under the card); this
       file only records it (INFO)
  C11  HOT landing-arc chevrons on top: gram.landing_arcs draws its items one after another, so a later arc's frame (its 6.4 px ink line and
       its lane-coloured line) crossed an earlier arc's HOT chevrons and cut the white-hot core to 2.0-2.5 px.  The HOT (k 0) chevrons of a
       landing_arcs call are drawn again at its end, over every frame of that call, without their glow (the glow is drawn once)
  C3   the ring-tag boxes: the box line is the E line (E_LINE_L, graded per ring as the other E lines), the type stays K type; the tag layer
       keeps nothing above K type and reduces from 2x with BOX (the 2.6 px NOW box line read L* 91-95 after the LANCZOS overshoot)
  C5   Solace tickets: the crest roundel sits on the nearest ticket (W4) only; on W5 / W6 it covered the turn pips
  C1   p2b: the tower hover arc (the slices the hovered unit lands on) is the one pencil (rb_pencil.wax_stroke, 7 px wax + 3 px ink), at the
       h11 radius; the tower renderer's own thin hover arc (f1_tower.draw_hover_arcs, 5.4 px marker) is retired
  B    p2b: the hover path is the L5 arrowed outline in pencil (rb_pencil.channel), the same mark as h11 (VISUAL_PLAN B: "Hover path: L5")"""
import math, sys, os
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import rb_tokens as T

T_HALO = 197.2                     # hz_core.T_HALO: the tower's outer halo radius (the h11 pencil arc sits between it and ring NOW)
HOVER_ARC_HALF = 25.0              # deg each side of the sector centre (h11 pencil_arc)
HOVER_ARC_SEED = 40                # h11: seed = sector + 40
PATH_W, PATH_HEAD = 12.0, 18.0     # h11: pc(L, pts, w=12, head=18, tail_dot=True)
INFO = {}


def install(R, A, SKIN):
    _hot_arcs()
    _ring_tags(A)
    _tickets()
    _p2b(A)
    import rb_lift as RL
    INFO['lift'] = dict(open_px=RL.OPEN_PX, btn_dx=RL.BTN_DX, lift_cy=dict(RL.LIFT_CY), fan_off=list(RL.FAN_OFF), print_off=RL.PRINT_OFF,
                        drop_off=RL.DROP_OFF)


# ======================================================================================== C11 HOT arc chevrons over the frames
def _hot_arcs():
    import gram as G
    import r2_arcs as A2
    if getattr(A2.landing_arcs, '_rb5', False):
        return
    REC = {'on': False, 'calls': []}
    _oac = G.arc_chevrons

    def arc_chevrons(L, r, th, x0, ns, ng, opt, k):
        if REC['on'] and k == 0 and ns > 0:
            # the layer is NOT recorded: on the publish path asm_render's capture (rb_capture._layer_cap) hands arc_chevrons a temp layer that
            # is composited and dropped right after the call; the replay goes onto the layer landing_arcs itself was given
            REC['calls'].append((r, th, x0, ns, ng, opt, k))
        return _oac(L, r, th, x0, ns, ng, opt, k)
    G.arc_chevrons = arc_chevrons
    _ola = A2.landing_arcs

    def landing_arcs(L, f, sel, only=None, extra=None):
        REC['on'], REC['calls'] = True, []
        try:
            out = _ola(L, f, sel, only, extra)
        finally:
            REC['on'] = False
        calls = list(REC['calls'])
        if calls:
            og = G.glow_line
            G.glow_line = lambda *a, **k: None
            try:
                for (r, th, x0, ns, ng, opt, k) in calls:
                    # hollow (growth) chevrons are not HOT; replay only the solid ones: ng = 0.  G.arc_chevrons is looked up now: on the
                    # publish path it is rb_capture's wrapper, so the replayed px land in the arcT0 class too
                    G.arc_chevrons(L, r, th, x0, ns, 0, opt, k)
            finally:
                G.glow_line = og
            INFO['hot_arc_replays'] = INFO.get('hot_arc_replays', 0) + len(calls)
        return out
    landing_arcs._rb5 = True
    A2.landing_arcs = landing_arcs
    G.A2.landing_arcs = landing_arcs


# ======================================================================================== C3 ring-tag boxes
def _ring_tags(A):
    import f1_board as FB
    import r2_misc as M2
    import gram_render as GR
    import cv_lib
    import rb_pencil as PEN
    from cv_lib import NOW
    import rb4_patch as RB4
    import rb3_patch as RB3
    K = T.K_TYPE
    INK = RB3.INK
    TMID = RB3.TMID

    def draw(L, f, opt):
        for d in range(3):
            w_ = f['rings_wave'][d]
            x, y, wd, depth, wv = M2.tag_geom(L, d, w_, opt)
            box = [x - wd / 2, y - 13, x + wd / 2, y + 13]
            if not NOW['words']:
                L.rect(box, fill=(8, 10, 18, 250), outline=INK, w=2.4, r=6)
                M2.lane_swatch(L, x - 16, x + 16, y - 5, d)
                if w_ >= 0:
                    M2.tally_bars(L, x, y + 6, w_ + 1, FB.grade2(K, d), h=8, pitch=5.4, w=2.6)
                continue
            c = FB.grade2(K, d)
            L.rect(box, fill=(8, 10, 18, 250), outline=INK, w=5.0, r=6)
            L.rect(box, outline=RB4.e_line(d), w=(2.6, 1.8, 1.4)[d], r=6)       # the box: E line (A.2), not K type
            tx0 = x - wd / 2 + 9
            if depth.startswith('+'):
                FB.OM.plus_glyph(L, tx0 + 3, y, c, 4.2, 2.4)
                tx0 += 10
                txt = depth[1:] + ((' ' + wv) if wv else '')
            else:
                txt = depth + ((' ' + wv) if wv else '')
            L.text((tx0, y + 1), txt, 20, 'anton', fill=c, anchor='lm', stroke=1.4)
            if d == 0:
                FB.end_notch(L, box[0] - 9, y, 90, col=c, s=5.2)
            else:
                for i in range(d):
                    xx = box[0] - 8 - 10 * i
                    L.ellipse([xx - 4.6, y - 4.6, xx + 4.6, y + 4.6], fill=INK)
                    L.ellipse([xx - 3.0, y - 3.0, xx + 3.0, y + 3.0], fill=TMID)

    def ring_tags(L, f, opt):
        """draw on a fresh layer, cap at K type (STRUCT_CAP_L) and flag the bright px for the BOX reduce (rb4 L2.done)"""
        Tl = cv_lib.L2(L.k)
        r = draw(Tl, f, opt)
        arr = np.asarray(Tl.im).astype(np.float32)
        arr, hit = RB4.vcap(arr, T.STRUCT_CAP_L)
        c = arr[..., :3] / 255.0
        lin = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
        Y = lin @ np.array([0.2126, 0.7152, 0.0722])
        bright = (Y >= ((T.STRUCT_CLASS_L - 8.0 + 16.0) / 116.0) ** 3) & (arr[..., 3] > 0)
        Tl.im = Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), 'RGBA')
        pm = PEN.pen_mask(Tl.im)
        pm.paste(Image.fromarray((bright * 255).astype(np.uint8), 'L'), (0, 0))
        INFO['ring_tag_capped_px'] = INFO.get('ring_tag_capped_px', 0) + int((hit & (arr[..., 3] > 0)).sum())
        L.im.alpha_composite(Tl.im)
        return r
    M2.ring_tags = ring_tags
    GR.A.M2.ring_tags = ring_tags
    A.M2.ring_tags = ring_tags


# ======================================================================================== C5 the Solace crest off the turn pips
S_TICKET_FILL = (30, 36, 36)       # rb4_patch.ticket's Solace branch: the lab-slide fill, its ink, the chamfer
S_TICKET_INK = (8, 14, 12)
S_TICKET_CH = 7


def s_ticket(self, L, box, nearest, climax, val=None):
    """the Solace ticket as the round-2 board draws it (rb4_patch.ticket's Solace branch, moved here as the skin's ticket method so that the
    port spec's skin table lists the op that is drawn): the chamfered lab slide, its 4.4 px ink, the 1.8 px edge in teal_hi at the wave's time
    value over the fill (W4 100, W5 70, W6 50 %, rb_tokens.TICKET_EDGE_VALS; C5, C16), and the crest roundel on the nearest ticket only (W4:
    its top row has no turn pips; on W5 / W6 it covered them, round 2 gate 1)"""
    import rb_tokens as T_
    SLI = T_.SKIN_INKS['solace']
    v = (1.0 if nearest else T_.TICKET_EDGE_VALS[0]) if val is None else val
    x0, y0, x1, y1 = box
    ch = S_TICKET_CH
    pts = [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch), (x0, y0 + ch)]
    L.poly(pts, fill=S_TICKET_FILL + (255,))
    L.line(pts + [pts[0]], S_TICKET_INK, 4.4)
    L.line(pts + [pts[0]], tuple(int(round(S_TICKET_FILL[q] + (SLI['teal_hi'][q] - S_TICKET_FILL[q]) * v)) for q in range(3)), 1.8)
    if v >= 0.999:
        self.crest(L, x1 - 13, y0 + 13, 0.62)


def solace_ticket():
    """the skin step (also run by round2/docs/port/skin_tables_r2.py after rb4_patch._solace): Solace's ticket method is s_ticket"""
    import cs_skin as CS
    CS.Solace.ticket = s_ticket


def _tickets():
    import f1_board as FB
    import lw_install as LI
    import rb4_patch as RB4
    solace_ticket()
    _ot = FB.ticket

    def ticket(L, box, edge, cut, fill=None):
        """rb4's ticket; on Solace the skin's ticket method (s_ticket) at the edge's time value"""
        s = LI.SK[0]
        if s.name != 'solace':
            return _ot(L, box, edge, cut, fill)
        val = RB4._ticket_val(edge)
        RB4.INFO.setdefault('ticket_vals', []).append(round(val, 3))
        return s.ticket(L, box, val >= 0.999, cut, val=val)
    FB.ticket = ticket


# ======================================================================================== C1 / B the p2b hover marks
def _p2b(A):
    import f1_tower as FT
    import cv_board as CB
    import rb_pencil as PEN
    import hv_lib_h2 as HL
    import a_hover as HV
    FT.draw_hover_arcs = lambda cv, sectors: None          # the tower image carries no hover arc (it is drawn below, in screen space)
    _ohp = A.H2.hover_path

    def hover_path(L, f, opt='A'):
        """p2b: the hovered unit's route as the L5 pencil outline (as h11) and the pencil arc on the slices it lands on (as h11)"""
        pts = HV.path_pts(f)
        PEN.channel(L, pts, w=PATH_W, head=PATH_HEAD, tail_dot=True)
        r = (T_HALO + CB.ring_geom(0)[0]) / 2.0
        for s in sorted(set(HV.hover_sectors(f))):
            PEN.wax_stroke(L, HL.arc(r, 60 * s - HOVER_ARC_HALF, 60 * s + HOVER_ARC_HALF), seed=s + HOVER_ARC_SEED, cap=True)
        INFO['p2b_hover'] = dict(path_w=PATH_W, head=PATH_HEAD, arc_r=round(r, 1), sectors=sorted(set(HV.hover_sectors(f))))
    A.H2.hover_path = hover_path
