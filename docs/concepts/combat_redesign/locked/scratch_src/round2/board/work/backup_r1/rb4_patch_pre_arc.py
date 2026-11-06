"""rb4_patch (2026-11-04, round 2 of the rebuild): the board items of the independent re-review (D:/Godot/rebel_cell/docs/reviews/
ad_review_overnight_2026-11-02/R1_REREVIEW.md, build order steps 1-2) as art-pass called them.  lw_render installs it after rb3_patch;
env RB4=0 skips it.  Every number is a named knob here or in rb_tokens.

  C14  render-order bug: wr2_units.library() (the consumed ghost loads the old e10 kglyph library mid-render) re-registered KA_* in
       crests15.CUSTOM, so every KA_twist (and Firewall, Hold, Nudge, Spin) glyph drawn after the first ghost of a process came from the old
       library, and which one a plate got depended on what the process had drawn before.  The library still loads (the ghost uses its module),
       but the registry is restored, so the asm_glyphs master is the one glyph source.  REGISTRY is checked after every render (INFO)
  C1   the one grease pencil (rb_pencil): every board PLAN / threat pencil stroke (trigger path, X caps, open arrowheads, the hover path, the
       ghost outlines, the bill's plan underline) is 7 px wax + 3 px ink each side with wax grain; pencil pixels reduce to 1x with BOX
  C2   FOCUS (rb_focus): the FOCUS token as four separate 12 px corners, one drawer (a2_kit.focus_brackets and the p2b hovered cell)
  C3   bright structure: E lines (unit cell outlines, token lane rings, the lane rings of the arc discs, the landing-arc frames) at E_LINE_L on
       ring NOW (graded per ring as before); the landing-arc disc glyphs, turn dots, NOW dot, wear slash and twist mark in K_TYPE (L* 84)
  C5   wave tickets: the edge carries its time value (W6 50, W5 70, W4 100 % of the skin's edge ink; the skin hook lost it to a two-state
       'nearest' flag); the W6 hazard ticks move to the top row, clear of the bomb's width pips
  C16  Solace in teal: the rim rope, the bezel lip, the cell edges, the crest strands, the token frame dot and the ticket edges leave leaf green
  C18  Solace rope with a long lay (LAY_TWISTS twists round the rim, heavier strands) on its light celadon body, so in luma it is a light band
       with slow dark twists, against Meridian's dark band with fine bright hazard stripes
  C7   the dying unit's glass: lifted by DYING_GLASS_LIFT so the cell keeps 3:1 against the brightest empty cell measured over its full glass
       (hatch included, guns cut), with margin for a gun tracer on top
  C6   the hand lift (rb_lift.LAYOUT, shared with the hover set): the fan keeps its slot positions, the hovered card lifts straight up
  C8   the HUD keeps the hover set's row grid at all times (hud_rows.py): hero room, four NEXT row slots"""
import math, sys, os
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import rb_tokens as T

# ------------------------------------------------------------------ knobs
DYING_GLASS_LIFT = 1.12            # C7: luminance factor on the dying unit's glass (over rb3's lit occupied glass)
LAY_TWISTS = 26                    # C18: Solace rope twists round the rim (round 1: 71)
LAY_W, LAY_AMP = 2.6, 3.4          # strand width, helix amplitude (round 1: 1.8, 3.0)
HAZ_PITCH, HAZ_W, HAZ_H = 6.0, 3.0, 6.5        # C5: the W6 hazard ticks in the ticket's top row
PLAN_BADGE_V = T.PLAN_BADGE_V      # the consumed ghost's Trigger stamp disc edge: PLAN at the badge value (as the twist badge)
INFO = {}
_REG = {}


def install(R, A, SKIN):
    _glyph_registry()
    _box_reduce()
    _pencil(A)
    _focus(A)
    _bright(A)
    _structure(A)
    _hot_core()
    _tickets(SKIN)
    _solace(SKIN)
    _dying(A)
    _render_hooks(R)
    import rb_lift
    rb_lift.install(R, A)
    import hud_rows
    hud_rows.install(R, A)


# ======================================================================================== C14 the glyph registry
def _glyph_registry():
    import crests15 as C15
    import wr2_units as W2U
    _REG.update({k: v for k, v in C15.CUSTOM.items() if k.startswith('KA_')})
    _olib = W2U.library

    def library():
        if 'k' in W2U._LIB:
            return W2U._LIB['k']
        snap = dict(C15.CUSTOM)
        m = _olib()
        back = [k for k, v in snap.items() if C15.CUSTOM.get(k) is not v]
        for k in back:
            C15.CUSTOM[k] = snap[k]
        INFO['c14_library_restored'] = sorted(back)
        return m
    W2U.library = library


def registry_ok():
    """True when every KA_* glyph still maps to the asm_glyphs master entry it had after the import"""
    import crests15 as C15
    bad = sorted(k for k, v in _REG.items() if C15.CUSTOM.get(k) is not v)
    return not bad, bad


# ======================================================================================== C1 / C2 BOX reduction of pencil and focus pixels
def _box_reduce():
    """L2.done reduces 2x -> 1x with LANCZOS, which rings at the wax / ink edge and lifts the wax over its pigment.  Pixels a pencil or FOCUS
    stroke flagged (im._pen_mask, carried by Image.alpha_composite) are reduced with BOX instead; every other pixel is unchanged."""
    import cv_lib
    if getattr(cv_lib.L2.done, '_rb4', False):
        return
    _oac = Image.Image.alpha_composite

    def alpha_composite(self, im, dest=(0, 0), source=(0, 0)):
        r = _oac(self, im, dest, source)
        pm = getattr(im, '_pen_mask', None)
        if pm is not None and tuple(source) == (0, 0):
            import rb_pencil as PEN
            PEN.pen_mask(self).paste(255, tuple(int(v) for v in dest), pm)
        return r
    Image.Image.alpha_composite = alpha_composite

    def done(self):
        lan = self.im.resize((cv_lib.W, cv_lib.H), Image.LANCZOS)
        pm = getattr(self.im, '_pen_mask', None)
        if pm is None or not pm.getbbox():
            return lan
        box = self.im.resize((cv_lib.W, cv_lib.H), Image.BOX)
        m = pm.resize((cv_lib.W, cv_lib.H), Image.BOX)
        lan.paste(box, (0, 0), m.point(lambda v: 255 if v > 0 else 0))
        return lan
    done._rb4 = True
    cv_lib.L2.done = done


# ======================================================================================== C1 the pencil
def _pencil(A):
    import rb_pencil as PEN
    import a_kit, a_plan, hud2
    import wr2_units as W2U
    PLAN = tuple(T.TOKENS['PLAN'])
    THREAT = tuple(a_plan.PTHREAT)
    _owax, _owx, _owv = a_kit.wax, a_kit.wax_x, a_plan.wax_v

    def _is_pencil(col):
        return tuple(col[:3]) in (PLAN, THREAT, tuple(a_kit.YEL))

    def wax(L, pts, col=a_kit.YEL, w=7, seed=1, wobble=0.8, ink=True, grain=1.0, taper=False):
        if not _is_pencil(col) or not ink:
            return _owax(L, pts, col, w, seed, wobble, ink, grain, taper)
        return PEN.wax(L, pts, col, w, seed)

    def wax_x(L, x, y, r=12, col=a_kit.YEL, seed=3, w=5, circle=False):
        if not _is_pencil(col):
            return _owx(L, x, y, r, col, seed, w, circle)
        return PEN.wax_x(L, x, y, r, col, seed, w, circle)

    def wax_v(L, tip, ang, size=16, col=a_kit.YEL, seed=5, w=6):
        if not _is_pencil(col):
            return _owv(L, tip, ang, size, col, seed, w)
        return PEN.wax_v(L, tip, ang, max(size, PEN.V_ARM), col, seed)
    for m in list(sys.modules.values()):
        if m is None:
            continue
        try:
            if getattr(m, 'wax', None) is _owax:
                m.wax = wax
            if getattr(m, 'wax_x', None) is _owx:
                m.wax_x = wax_x
            if getattr(m, 'wax_v', None) is _owv:
                m.wax_v = wax_v
        except Exception:
            pass
    _ohw = hud2.wax

    def hud_wax(L, pts, col, w=7, seed=3, ink=True, wob=0.9):
        if not _is_pencil(col):
            return _ohw(L, pts, col, w, seed, ink, wob)
        return PEN.hud_wax(L, pts, col, w, seed)
    hud2.wax = hud_wax
    _owo = W2U.wax_outline

    def wax_outline(L, poly, col, w=4.0, seed=3):
        """the ghost cell outline in pencil (p2 / p2b); on p3 the plan has turned to P paint (f1_render sets PLAN pink) and keeps its stroke"""
        if not _is_pencil(col):
            return _owo(L, poly, col, w, seed)
        PEN.wax_stroke(L, list(poly), col=tuple(col[:3]), seed=seed, closed=True, cls='L6')
    W2U.wax_outline = wax_outline
    # the consumed ghost (wr2_units.ghost 'consumed'): its 3 px PLAN vector outline becomes the pencil; the Trigger stamp disc takes PLAN at
    # the badge value (an N badge, as the twist badge)
    _og = W2U.ghost

    def ghost(L, u, kind, beat='p2'):
        if kind != 'consumed' or not _is_pencil(W2U.PLAN):
            return _og(L, u, kind, beat)
        import wr_units as WU
        import e8lib as E8
        poly = WU.u_poly(u)
        ghostc = W2U.mix(W2U.kind_wash(u['kind'], u['dep']), W2U.BED, 0.62)
        L.poly(poly, fill=ghostc + (255,))
        PEN.wax_stroke(L, list(poly), col=tuple(W2U.PLAN[:3]), seed=u['id'] * 7 + 2, closed=True, cls='L6')
        x, y = E8.token_pos(u)
        Rr = W2U.TOK_R
        L.ellipse([x - Rr - 1.5, y - Rr - 1.5, x + Rr + 1.5, y + Rr + 1.5], fill=W2U.INKC)
        L.ellipse([x - Rr, y - Rr, x + Rr, y + Rr], fill=(58, 54, 66))
        W2U.ring(L, x, y, Rr, u['dep'], dead=True)
        W2U.gly(L, W2U.KIND[u['kind']][1], 34, (x, y), (176, 172, 186))
        bx, by = W2U._side(u, Rr + 14)
        r = 14
        pb = tuple(int(round(c * PLAN_BADGE_V)) for c in W2U.PLAN[:3])
        L.ellipse([bx - r - 2.5, by - r - 2.5, bx + r + 2.5, by + r + 2.5], fill=W2U.INKC)
        L.ellipse([bx - r, by - r, bx + r, by + r], fill=(30, 26, 6), outline=pb, w=2.4)
        W2U.library()
        W2U.gly(L, 'KA_trigger', 20, (bx, by), pb)
    W2U.ghost = ghost


# ======================================================================================== C2 FOCUS
def _focus(A):
    import rb_focus as FOC
    import a2_kit
    import a_hover as HV
    _ofb = a2_kit.focus_brackets
    for m in list(sys.modules.values()):
        if m is not None and getattr(m, 'focus_brackets', None) is _ofb:
            try:
                m.focus_brackets = FOC.brackets_compat
            except Exception:
                pass

    def hover_cell(L, f, fopt='A', w=None):
        """hovered_cell_outline: the FOCUS corners on the hovered unit's cell (aimed weight), rb_focus geometry"""
        FOC.cell(L, HV.hv_unit(f), aimed=True)
    A.H2.hover_cell = hover_cell


# ======================================================================================== C3 bright structure and arc marks
def RBP_at_lstar(col, L_):
    import rb_patch as RBP
    return RBP.at_lstar(col, L_)


def e_line(dep):
    import gramlib as GL
    return GL.grade(RBP_at_lstar((217, 225, 234), T.E_LINE_L), dep)


# ======================================================================================== C11 the HOT core
HOT_CORE_W = 4.2                   # px at 1x, the white-hot core of a HOT cell chevron (rb3 3.2: it measured 2.0 px solid on the plate)
HOT_FILL_W = 7.2                   # the HOT cell chevron's fill under it (gram 6.0), so the HARM_UP fill keeps ~1.5 px each side
HOT_ARC_CORE_W = 3.9               # the landing-arc HOT chevron core (rb3 2.9)
HOT_ARC_FILL_ADD = 1.2             # the landing-arc HOT chevron fill over gram's width


def _hot_core():
    import gram as G
    import wr2_units as W2U
    import cv_board as CB
    import e8lib as E8
    _ost = W2U.stack

    def stack(L, u, ang, n_solid, n_hollow, dim=0.0):
        r_ = _ost(L, u, ang, n_solid, n_hollow, dim)
        if u['dep'] != 0 or u['fate']['kind'] == 'dies':
            return r_
        st = W2U.chev_params(u, n_solid + n_hollow)
        ri, ro = CB.ring_geom(u['dep'])
        col = G.grade(T.HARM_UP, 0)
        for i in range(n_solid):
            r = ri + st['start'] + i * st['pitch']
            p = [E8.pt(r + st['depth'], ang, -st['half']), E8.pt(r, ang, 0), E8.pt(r + st['depth'], ang, st['half'])]
            L.line(p, col, HOT_FILL_W)
            q = [E8.pt(r + st['depth'], ang, -st['half'] * 0.86), E8.pt(r, ang, 0), E8.pt(r + st['depth'], ang, st['half'] * 0.86)]
            L.line(q, T.HOT_CORE, HOT_CORE_W)
        return r_
    W2U.stack = stack
    _oac = G.arc_chevrons

    def arc_chevrons(L, r, th, x0, ns, ng, opt, k):
        r_ = _oac(L, r, th, x0, ns, ng, opt, k)
        if k != 0:
            return r_
        p = G.A2.CH[opt]
        col = G.grade(T.HARM_UP, 0)
        for i in range(ns):
            xc = x0 + p['pitch'] / 2 + i * p['pitch']
            fr = G.A2.Fr(r, th, xc)
            q0 = [fr.q(-p['hw'], p['dp'] / 2), fr.q(0, -p['dp'] / 2), fr.q(p['hw'], p['dp'] / 2)]
            L.line(q0, col, p['col'] + HOT_ARC_FILL_ADD)
            q = [fr.q(-p['hw'] * 0.82, p['dp'] / 2 * 0.82), fr.q(0, -p['dp'] / 2 * 0.82), fr.q(p['hw'] * 0.82, p['dp'] / 2 * 0.82)]
            L.line(q, T.HOT_CORE, HOT_ARC_CORE_W)
        return r_
    G.arc_chevrons = arc_chevrons


def _bright(A):
    import wr2_lib
    import cv_lib
    import r2_arcs as RA
    import r2_glyphs as RG
    import lw_install as LI
    for i in range(3):
        wr2_lib.LANE_COL[i] = e_line(i)
        cv_lib.LANE[i]['col'] = e_line(i)
    RA.WHITE = tuple(T.K_TYPE)
    # gram draws the unit cell outlines, the token lane rings, the arc discs' lane rings and the landing-arc frames in ENAMEL (graded per ring;
    # ring NOW at full ENAMEL with a glow, L* 95-100 at the 1 px peak): its ENAMEL is the E line value
    import gram as G
    import f1_board as FB
    E_ = tuple(RBP_at_lstar((217, 225, 234), T.E_LINE_L))
    G.ENAMEL = E_
    FB.ENAMEL = E_              # f1_board's outline / tok_ring / a2_frame / ring-tag boxes / queue feed (the live ones) read its own ENAMEL
    INFO['e_line_rgb'] = list(E_)
    _okg = RG.kind_glyph

    def disc(L, r, th, px, u, lane, opt):
        """arc_glyph_disc with the kind glyph in K type (it was white, L* 100: the brightest mark on the bezel)"""
        s = LI.SK[0]
        fr = RA.Fr(r, th, px)
        Rr = 13.5 if opt == 'P' else 12.0
        s.disc_frame(L, fr.x, fr.y, Rr)
        kc = RA.KCOL[u['kind']]
        L.ellipse([fr.x - Rr - 1.4, fr.y - Rr - 1.4, fr.x + Rr + 1.4, fr.y + Rr + 1.4], fill=RA.INK)
        RA.lane_base_style(L, fr.x, fr.y, Rr, u['dep'], kc)
        _okg(L, u['kind'], 21 if opt == 'P' else 18.5, (fr.x, fr.y), tuple(T.K_TYPE))
        return 2 * Rr + 6
    A.A2.disc = disc
    RA.disc = disc


def vcap(a, cap_l):
    """float RGBA array (0-255): every pixel whose CIE L* is above cap_l is scaled in linear light to cap_l (hue and chroma ratio kept)"""
    c = a[..., :3] / 255.0
    lin = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    Y = lin @ np.array([0.2126, 0.7152, 0.0722])
    Yc = ((cap_l + 16.0) / 116.0) ** 3
    k = np.where(Y > Yc, Yc / np.maximum(Y, 1e-9), 1.0)
    lin = lin * k[..., None]
    a = a.copy()
    a[..., :3] = np.where(lin > 0.0031308, 1.055 * np.clip(lin, 0, None) ** (1 / 2.4) - 0.055, 12.92 * lin) * 255.0
    return a, Y > Yc


def _structure(A):
    """C3: the plate and bezel images and the schedule / ward-arc layers keep nothing above K type (STRUCT_CAP_L); their capped and bright
    pixels reduce with BOX (no LANCZOS overshoot on the 1 px lines)"""
    import rb_pencil as PEN
    import cv_lib

    def img_wrap(owner, name):
        orig = getattr(owner, name)
        if getattr(orig, '_rb4s', False):
            return

        def w(*a, **k):
            im = orig(*a, **k).convert('RGBA')
            arr, hit = vcap(np.asarray(im).astype(np.float32), T.STRUCT_CAP_L)
            INFO.setdefault('struct_capped_px', {})[name] = int((hit & (arr[..., 3] > 0)).sum())
            return Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), 'RGBA')
        w._rb4s = True
        setattr(owner, name, w)
    img_wrap(A.G2, 'plate')
    img_wrap(A.G2, 'bezel_layer')

    def layer_wrap(owner, name):
        orig = getattr(owner, name)
        if getattr(orig, '_rb4s', False):
            return

        def w(L, *a, **k):
            Tl = cv_lib.L2(L.k)
            r = orig(Tl, *a, **k)
            arr = np.asarray(Tl.im).astype(np.float32)
            arr, hit = vcap(arr, T.STRUCT_CAP_L)
            c = arr[..., :3] / 255.0
            lin = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
            Y = lin @ np.array([0.2126, 0.7152, 0.0722])
            bright = (Y >= ((T.STRUCT_CLASS_L - 8.0 + 16.0) / 116.0) ** 3) & (arr[..., 3] > 0)
            Tl.im = Image.fromarray(np.clip(np.round(arr), 0, 255).astype(np.uint8), 'RGBA')
            pm = PEN.pen_mask(Tl.im)
            pm.paste(Image.fromarray((bright * 255).astype(np.uint8), 'L'), (0, 0))
            INFO.setdefault('struct_capped_px', {})[name] = INFO.get('struct_capped_px', {}).get(name, 0) + int((hit & (arr[..., 3] > 0)).sum())
            L.im.alpha_composite(Tl.im)
            return r
        w._rb4s = True
        setattr(owner, name, w)
    layer_wrap(A.S2, 'schedule')
    layer_wrap(A.W2B, 'ward_arc')


# ======================================================================================== C5 wave tickets
def _ticket_val(edge):
    import gram as G
    K, B = np.array(T.K_TYPE, float), np.array(G.BED, float)
    e = np.array(edge[:3], float)
    v = np.median((e - B) / np.maximum(K - B, 1e-6))
    return float(np.clip(v, 0.0, 1.0))


def _tickets(SKIN):
    import f1_board as FB
    import lw_install as LI
    import r2_glyphs as RG
    import rb2_patch as RB2
    import rb_patch as RBP
    import cs_skin as CS
    from gram import INK as GINK, TMID as GTMID, SCHED as GSCHED
    from cv_lib import NOW
    MR = T.SKIN_INKS['meridian']
    SL = T.SKIN_INKS['solace']

    def vk(c, fill, val):
        return tuple(int(round(fill[q] + (c[q] - fill[q]) * val)) for q in range(3))

    def ticket(L, box, edge, cut, fill=None):
        """the skin's ticket with its edge at the time value of the wave (W6 50, W5 70, W4 100 %, of the skin's edge ink over the ticket fill)"""
        val = _ticket_val(edge)
        INFO.setdefault('ticket_vals', []).append(round(val, 3))
        s = LI.SK[0]
        x0, y0, x1, y1 = box
        if s.name == 'solace':
            f_, ink_, e_, ch = (30, 36, 36), (8, 14, 12), SL['teal_hi'], 7
        elif s.name == 'meridian':
            f_, ink_, e_, ch = (34, 33, 34), (10, 8, 7), MR['rust_hi'], 2
        else:
            f_, ink_, e_, ch = (26, 32, 41), (8, 9, 12), s.pal['line'], 3
        pts = [(x0 + ch, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1 - ch), (x1 - ch, y1), (x0 + ch, y1), (x0, y1 - ch), (x0, y0 + ch)]
        L.poly(pts, fill=f_ + (255,))
        L.line(pts + [pts[0]], ink_, 4.4)
        L.line(pts + [pts[0]], vk(e_, f_, val), 1.8)
        if s.name == 'solace':
            s.crest(L, x1 - 13, y0 + 13, 0.62)
        elif s.name == 'meridian':
            for (cx, cy) in ((x0 + 5, y0 + 5), (x1 - 5, y0 + 5), (x0 + 5, y1 - 5), (x1 - 5, y1 - 5)):
                s._rivet(L, cx, cy, 1.2)
    FB.ticket = ticket
    K = T.K_TYPE
    import gram as G
    BED = G.BED

    def queue_tickets(L, f, arcs):
        """rb3 queue_tickets with the W6 (climax) hazard ticks in the ticket's top row between the W tag and the turn pips (they sat on the
        bomb glyph's width pips)"""
        fut = [a for a in arcs if a['state'] == 'future']
        order = list(reversed(fut))
        x, y0 = 24, 24
        tw_, th_ = RB2.TICKET_W, RB2.TICKET_H
        vals = dict(enumerate(reversed(T.TICKET_EDGE_VALS)))         # 0 = next to enter: 100 %, then 70 %, then 50 %
        for i, a in enumerate(order):
            n = a['wave'] + 1
            j = len(order) - 1 - i
            val = vals.get(j, T.TICKET_EDGE_VALS[0])
            box = [x, y0, x + tw_, y0 + th_]
            FB.ticket(L, box, tuple(int(round(BED[q] + (K[q] - BED[q]) * val)) for q in range(3)), bool(a.get('climax')))
            tag_e = x + 8
            if NOW['words']:
                tag_e = x + 8 + L.tw('W%d' % n, RBP.TICKET_TXT, 'mono')
                L.text((x + 8, y0 + RB2.TICKET_TAG_Y), 'W%d' % n, RBP.TICKET_TXT, 'mono', fill=K, anchor='lm')
            units = a['units']
            slot = (tw_ - 10) / max(1, len(units))
            for ui, (kind, wd) in enumerate(units):
                cx = x + 5 + slot * ui + slot / 2
                RG.kind_glyph(L, kind, RB2.TICKET_GLYPH_PX, (cx, y0 + RB2.TICKET_GLYPH_Y), K)
                bw = 4
                bx0 = cx - (wd * bw + (wd - 1) * 1.6) / 2
                for b in range(wd):
                    L.rect([bx0 + b * (bw + 1.6), y0 + RB2.TICKET_BAR_Y, bx0 + b * (bw + 1.6) + bw, y0 + RB2.TICKET_BAR_Y + 3.4], fill=K + (255,), r=1)
            pip_l = x + tw_ - 12 - max(0, j - 1) * 10 - 4.6
            for p in range(j):
                px = x + tw_ - 12 - p * 10
                L.ellipse([px - 4.6, y0 + RB2.TICKET_TAG_Y - 4.6, px + 4.6, y0 + RB2.TICKET_TAG_Y + 4.6], fill=GINK)
                L.ellipse([px - 3.0, y0 + RB2.TICKET_TAG_Y - 3.0, px + 3.0, y0 + RB2.TICKET_TAG_Y + 3.0], fill=GTMID)
            if a.get('climax'):
                # three hazard ticks centred in the free run of the top row (W tag end -> first turn pip)
                xr = pip_l if j else x + tw_ - 8
                n_ = 3
                span = (n_ - 1) * HAZ_PITCH + HAZ_W + 3.5
                bx = (tag_e + xr) / 2 - span / 2
                yc = y0 + RB2.TICKET_TAG_Y
                INFO['hazard_ticks'] = dict(x0=round(bx, 1), x1=round(bx + span, 1), free=(round(tag_e, 1), round(xr, 1)))
                for t in range(n_):
                    b_ = bx + t * HAZ_PITCH
                    L.poly([(b_, yc + HAZ_H / 2), (b_ + HAZ_W, yc + HAZ_H / 2), (b_ + HAZ_W + 3.5, yc - HAZ_H / 2), (b_ + 3.5, yc - HAZ_H / 2)],
                           fill=GSCHED, outline=(12, 10, 22), w=1.0)
            x += tw_ + 8
        return x
    FB.queue_tickets = queue_tickets


# ======================================================================================== C16 / C18 Solace in teal, long-lay rope
def _solace(SKIN):
    import cs_skin as CS
    from cs_skin import Acc, sstep, vor, mixc
    from cv_lib import C, ppx
    SL = T.SKIN_INKS['solace']
    S = CS.Solace
    S.pal = dict(S.pal, primary=SL['teal'], edge=SL['teal'], strand_a=SL['teal'], strand_b=SL['teal_deep'], porcelain=SL['porcelain'])
    _obz = S.bezel

    def s_bezel(self, X, Y, RHO, TH):
        acc = Acc(X.shape)
        u = np.clip((RHO - 388) / 34.0, 0, 1)
        acc.add((20, 26, 26), 1.0)
        acc.add((44, 54, 52), 0.35 + 0.25 * np.sin(np.pi * u))
        f1, f2, ids, pts = vor(X, Y, 26.0, 5)
        acc.add((120, 140, 132), (1 - sstep(0.0, 1.4, f2 - f1)) * 0.10)
        lip = (1 - sstep(0.0, 1.2, np.abs(RHO - 389.2))) + (1 - sstep(0.0, 1.2, np.abs(RHO - 420.8)))
        acc.add(SL['teal_deep'], np.clip(lip, 0, 1) * 0.85)                 # the corp hue on the bezel lip (teal, C16)
        return acc.rgb, acc.a
    S.bezel = s_bezel

    def s_cell_detail(self, L, poly, dep, empty, seed):
        pp = poly + [poly[0]]
        L.line(pp, mixc(SL['teal_deep'], (10, 20, 16), 0.15 if not empty else 0.45) + (200 if not empty else 130,), 1.3)
    S.cell_detail = s_cell_detail
    _otf = S.token_frame

    def s_token_frame(self, L, x, y, R, kind, dep):
        Ro = R + 6.0
        L.ellipse([x - Ro - 1.6, y - Ro - 1.6, x + Ro + 1.6, y + Ro + 1.6], fill=(8, 14, 12))
        L.ellipse([x - Ro, y - Ro, x + Ro, y + Ro], fill=(96, 108, 104))
        L.line(L.arc_pts((x, y), Ro - 1.6, 280, 360 + 40, 14), (150, 162, 158), 1.6)
        L.ellipse([x - R - 1.8, y - R - 1.8, x + R + 1.8, y + R + 1.8], fill=(8, 14, 12))
        L.ellipse([x - 2.2, y - Ro + 0.2, x + 2.2, y - Ro + 4.6], fill=SL['teal'], outline=(8, 14, 12), w=0.8)
    S.token_frame = s_token_frame

    def s_rim(self, X, Y, RHO, TH):
        """C18: the rope's body is a glazed celadon tube: light, continuous, with a darker groove under the lay and a glaze line on its outer
        third (Meridian's rim is a dark band with fine bright hazard stripes)"""
        P = self.pal
        acc = Acc(X.shape)
        u = np.clip((RHO - 489.0) / 11.0, 0, 1)
        k = 0.84 + 0.18 * np.sin(np.pi * u) + 0.08 * np.cos(np.radians(TH - 315))
        acc.add(np.array(P['porcelain'], np.float32)[None, None] * k[..., None], 1.0)
        acc.add((255, 255, 250), (1 - sstep(0.0, 0.18, np.abs(u - 0.80))) * np.clip(np.cos(np.radians(TH - 315)), 0, 1) * 0.20)
        return acc.rgb, acc.a
    S.rim = s_rim

    def rim_vector(self, L):
        r = 494.5
        self.helix(L, r, 0, 360, amp=LAY_AMP, wl=2 * math.pi * r / LAY_TWISTS, w=LAY_W)
        for k in range(6):
            x, y = ppx(C, r, 30 + 60 * k)
            self.crest(L, x, y, 1.25)
    S.rim_vector = rim_vector


# ======================================================================================== C7 the dying unit's glass
def _dying(A):
    import rb3_patch as RB3
    import rb_patch as RBP
    _okh = RB3.kill_hatch

    def kill_hatch(L, u):
        """lift the dying cell's glass (under the hatch) by DYING_GLASS_LIFT before the L7 hatch: the glass is measured whole (hatch included,
        guns cut) and must keep 3:1 with a gun tracer crossing it"""
        from wr_geo import cell_poly, unit_bounds
        from cv_lib import L2
        from PIL import ImageDraw
        b0, b1 = unit_bounds(u)
        poly = cell_poly(u['dep'], b0, b1, RB3.KILL_INSET, RB3.KILL_INSET, kind='unit', tin=RB3.KILL_INSET)
        k = L.k
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        x0, y0 = max(0, int(min(xs)) - 2) * k, max(0, int(min(ys)) - 2) * k
        x1, y1 = min(L.im.width, (int(max(xs)) + 3) * k), min(L.im.height, (int(max(ys)) + 3) * k)
        mk = Image.new('L', (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(mk).polygon([(px * k - x0, py * k - y0) for px, py in poly], fill=255)
        m = np.asarray(mk, np.float32) / 255.0
        crop = L.im.crop((x0, y0, x1, y1))
        a = np.asarray(crop, np.float32)
        c = a[..., :3] / 255.0
        lin = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
        lin = np.clip(lin * (1.0 + (DYING_GLASS_LIFT - 1.0) * m)[..., None], 0, 1)
        srgb = np.where(lin > 0.0031308, 1.055 * lin ** (1 / 2.4) - 0.055, 12.92 * lin) * 255.0
        a[..., :3] = srgb
        L.im.paste(Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), 'RGBA'), (x0, y0))
        INFO.setdefault('dying_lift', []).append(dict(unit=u['id'], k=DYING_GLASS_LIFT))
        return _okh(L, u)
    RB3.kill_hatch = kill_hatch


# ======================================================================================== per-render bookkeeping
def _render_hooks(R):
    import f1_render as F1
    import rb_pencil as PEN
    import rb_focus as FOC
    _orr = F1._render

    def _render(beat='p1', *a, **k):
        PEN.reset()
        FOC.reset()
        INFO.pop('ticket_vals', None)
        try:
            return _orr(beat, *a, **k)
        finally:
            ok, bad = registry_ok()
            INFO['glyph_registry_ok'] = ok
            INFO['glyph_registry_bad'] = bad
            INFO['pencil_strokes'] = list(PEN.STROKES)
            INFO['focus_calls'] = list(FOC.CALLS)
            try:
                import rb_capture as RBC
                M = RBC.MASKS
                for cls, m in PEN.MASKS.items():
                    M['pen_' + cls] = m.copy()
                if 'm' in FOC.MASK:
                    M['focus'] = FOC.MASK['m'].copy()
            except Exception as e:
                INFO['mask_merge_error'] = repr(e)
    F1._render = _render
