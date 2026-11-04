"""rb_capture (2026-11-03 rebuild): capture hooks for asm_render.py, feeding the value / text / palette / hand checks in rb_checks.py.

install(R, A, FH, masks) adds, on top of asm_render's own mask classes:
  family masks   tower, chev0/chev1/chev2 (unit threat chevrons per ring), arcT0/arcT1/arcT2 (landing-arc chevrons and diamonds per time state),
                 tokens (unit token discs), hud (the terminal HUD layer), send, name, you (player stickers), undo (the UNDO tab),
                 hand_rest / hand_lift / hand_played (per placed card, plus the card list with its placement for the sibling test)
  text log       every text draw (board L2 text, arc text on the bezel, HUD text, sticker / tower lettering, card text) with its label,
                 font, screen px and cap height in screen px (cap = the font's 'H' box at that size)
  empty probe    the empty-cell painter of the installed skin on an empty frame (every ring, every sector), so each ring has an empty
                 reference even when no cell on that ring is empty in the state
dump() returns the JSON-able part; the masks land in the MASKS dict that asm_render already saves."""
import os, sys, math, copy
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageFont

FONT_DIRS = [os.path.dirname(os.path.abspath(__file__)) + '/fonts/', 'D:/rc_art/art-pass/assets/fonts/']
KIND_FILE = {'anton': 'Anton-Regular.ttf', 'mono': 'ShareTechMono-Regular.ttf', 'plex': 'IBMPlexSansCondensed-Medium.ttf'}
_CAP = {}
TEXT = []
CARDS = []
INFO = {}
_guard = [0]
MASKS = {}
DIM = [False]
UNCAPTURED = []


def _plex_path(bold=True):
    import bb_lib as BB
    try:
        return BB.plex(40, bold).path
    except Exception:
        return 'IBMPlexSans'


def font_path(name):
    if name is None:
        return None
    if hasattr(name, 'path'):
        return name.path
    name = str(name)
    if name in KIND_FILE:
        name = KIND_FILE[name]
    if os.path.exists(name):
        return name
    for d in FONT_DIRS:
        if os.path.exists(d + os.path.basename(name)):
            return d + os.path.basename(name)
    return None


def cap_ratio(name):
    """cap height / font px for a font (the 'H' ink box at 200 px)"""
    p = font_path(name)
    if p is None:
        return None
    if p not in _CAP:
        f = ImageFont.truetype(p, 200)
        b = f.getbbox('H')
        _CAP[p] = (b[3] - b[1]) / 200.0
    return _CAP[p]


def rec(label, font, px, where, scale=1.0):
    if _guard[0] or label is None:
        return
    if where in ('board/hud L2.text', 'hud2.txt', 'obj2.txt', 'bezel arc text'):
        import cv_lib
        if not cv_lib.NOW['words']:          # these drawers print nothing (or a tally) with words off
            return
    s = str(label)
    if not s.strip():
        return
    cr = cap_ratio(font)
    TEXT.append(dict(text=s, font=os.path.basename(font_path(font) or str(font)), px=round(px * scale, 2),
                     cap_px=None if cr is None else round(cr * px * scale, 2), where=where))


def _wrap_text(owner, name, where, getter, scale_fn=None):
    """wrap a text drawer: record (label, font, px) once, suppress the nested draws it makes"""
    orig = getattr(owner, name)
    if getattr(orig, '_rb', False):
        return

    def w(*a, **k):
        try:
            lab, fnt, px = getter(*a, **k)
            sc = scale_fn(*a, **k) if scale_fn else 1.0
            rec(lab, fnt, px, where, sc)
        except Exception as e:
            TEXT.append(dict(text='?', font='?', px=None, cap_px=None, where=where + ' (hook error %r)' % e))
        _guard[0] += 1
        try:
            return orig(*a, **k)
        finally:
            _guard[0] -= 1
    w._rb = True
    setattr(owner, name, w)


def _layer_cap(owner, name, cls_fn, Lidx=0):
    """compose the drawer into a fresh L2, record its alpha (>= 128) under cls_fn(args)"""
    import cv_lib
    orig = getattr(owner, name)
    if getattr(orig, '_rbl', False):
        return

    def wrap(*a, **k):
        cls = cls_fn(*a, **k)
        if cls is None:
            return orig(*a, **k)
        if DIM[0]:
            cls = cls + '_dim'                    # drawn on the hover plate's dimmed layer (value x 0.38 by design): its own class
        L = a[Lidx]
        T = cv_lib.L2(L.k)
        a2 = list(a)
        a2[Lidx] = T
        r = orig(*a2, **k)
        L.im.alpha_composite(T.im)
        al = T.im.split()[3].resize((1920, 1080), Image.BOX)
        m = np.asarray(al) >= 128
        MASKS[cls] = MASKS.get(cls, np.zeros((1080, 1920), bool)) | m
        return r
    wrap._rbl = True
    setattr(owner, name, wrap)


def _placed_alpha(im, cx, cy, ang, scale):
    k = scale / 2.0
    w, h = max(1, int(im.width * k)), max(1, int(im.height * k))
    a = im.split()[3].resize((w, h), Image.LANCZOS)
    if ang:
        a = a.rotate(ang, resample=Image.BICUBIC, expand=True)
    m = Image.new('L', (1920, 1080), 0)
    m.paste(a, (int(round(cx - a.width / 2)), int(round(cy - a.height / 2))))
    return np.asarray(m) >= 128


def install(R, A, FH, masks, beat):
    global MASKS
    MASKS = masks
    INFO['beat'] = beat
    import cv_lib, hud2, obj2, o_sched, r2_sched
    import card_render as CR
    import gram as G
    import wr2_units as W2U
    import asm_units as AU
    # ------------------------------------------------------------------ text
    _wrap_text(cv_lib.L2, 'text', 'board/hud L2.text', lambda self, xy, s, font_px, kind='anton', *a, **k: (s, kind, font_px))
    _wrap_text(hud2, 'txt', 'hud2.txt', lambda L, x, y, s, px, col, kind='mono', *a, **k: (s, kind, px))
    _wrap_text(obj2, 'txt', 'obj2.txt', lambda L, x, y, s, px, col, kind='mono', *a, **k: (s, kind, px)) if hasattr(obj2, 'txt') else None
    at = o_sched.arc_text2
    for m_ in list(sys.modules.values()):
        if m_ is not None and getattr(m_, 'arc_text2', None) is at:
            _wrap_text(m_, 'arc_text2', 'bezel arc text', lambda L, r, a_mid, s, px, col, kind='mono', *a, **k: (s, kind, px))
    # card text: design px; the hand places cards at CARD_SCALE (lifted LIFT_S x CARD_SCALE): the smallest on-screen scale is used
    cur = {'card': None}
    _orb = CR.render_base

    def rb(spec, *a, **k):
        cur['card'] = spec.get('name') if isinstance(spec, dict) else str(spec)
        return _orb(spec, *a, **k)
    CR.render_base = rb
    _wrap_text(CR, 'text', 'card', lambda cv, txt, x, y, px, name=CR.ANTON, *a, **k: (txt, name, px), lambda *a, **k: FH.CARD_SCALE)
    import xf_gfx, st_gfx
    for mod in (xf_gfx, st_gfx):
        if hasattr(mod, 'text_mask'):
            _wrap_text(mod, 'text_mask', 'sticker/tower lettering', lambda cv, txt, x, y, fontname, px, *a, **k: (txt, fontname, px))
    import f1_lib
    _wrap_text(f1_lib, 'text_mask', 'f1 lettering', lambda cv, text, fnt, px, *a, **k: (text, fnt, px))
    # ------------------------------------------------------------------ family masks
    _layer_cap(W2U, 'stack', lambda L, u, *a, **k: 'chev%d' % u['dep'])
    _layer_cap(G, 'arc_chevrons', lambda L, r, th, x0, ns, ng, opt, k, *a, **kk: 'arcT%d' % k)
    _layer_cap(G, 'arc_diamonds', lambda L, r, th, x0, n, opt, k, *a, **kk: 'arcT%d' % k)
    _layer_cap(AU, 'token', lambda L, u, *a, **k: 'tokens')
    _layer_cap(R.hud2, 'draw_hud', lambda L, *a, **k: 'hud')
    # stage 2: the UI scrim slabs (hud_scrim: the HUD column and the hand slab) are UI ground laid over the room; where they darken the room
    # by 15 % or more the pixel is UI, not room, for the room numbers of check b
    _osc = hud2.scrim_layers

    def scrim_layers(base, col_bottom, *a, **k):
        T_ = Image.new('RGBA', base.size, (0, 0, 0, 0))
        r_ = _osc(T_, col_bottom, *a, **k)
        base.alpha_composite(T_)
        MASKS['scrim'] = np.asarray(T_.split()[3]) >= int(round(0.15 * 255))
        return r_
    hud2.scrim_layers = scrim_layers
    # 2026-11-04 (gate 1): the E and K marks get their own classes for the value-order table (check b) and the Adjuster check (check a):
    # enemy HP ticks, the Adjuster HP track and diamond plate, the ring tags (also in asm_render's 'tags'), the guns layer (tracers, hit stars)
    import wr2_boss as W2B
    import r2_misc as M2_
    import f1_guns as FG_
    _layer_cap(W2U, 'hp_row', lambda L, u, *a, **k: 'hp')
    _layer_cap(W2B, 'hp_bar', lambda L, a, ang, *x, **k: 'adj_hp')
    _layer_cap(W2B, 'diamond', lambda L, a, ang, *x, **k: 'adj')
    _layer_cap(M2_, 'ring_tags', lambda L, f, opt, *a, **k: 'ring_tags')
    _layer_cap(A.P2, 'twist_badge', lambda L, *a, **k: 'twist_badge')
    if A.M2 is not M2_:
        _layer_cap(A.M2, 'ring_tags', lambda L, f, opt, *a, **k: 'ring_tags')
    _omg = FG_.make_guns

    def make_guns(*a, **k):
        g, info = _omg(*a, **k)
        m_ = np.zeros((1080, 1920), bool)
        ga = np.asarray(g.split()[3]) >= 128            # the guns layer is composited at (0, 0); it may be narrower than the plate
        m_[:ga.shape[0], :ga.shape[1]] = ga[:1080, :1920]
        MASKS['guns'] = MASKS.get('guns', np.zeros((1080, 1920), bool)) | m_
        return g, info
    FG_.make_guns = make_guns
    # the hover tag text (parked by designer note 8: kept in its E10 form and content) is drawn by a_hover.rtext straight on the layer; it is
    # recorded with where='hover tag (parked, note 8)' so check c reports it (and does not gate it)
    import a2_hover as H2V_
    _wrap_text(H2V_, 'rtext', 'hover tag (parked, note 8)', lambda L, xy, s, px, col=None, bold=True, *a, **k: (s, _plex_path(bold), px))
    # coverage: every PIL text draw that no hooked drawer above made (a drawer the capture does not know) is listed in UNCAPTURED
    from PIL import ImageDraw as _ID
    _oidt = _ID.ImageDraw.text
    if not getattr(_oidt, '_rbu', False):
        def _idt(self, xy, text, *a, **k):
            if not _guard[0] and str(text).strip():
                f_ = k.get('font') if 'font' in k else (a[1] if len(a) > 1 else None)
                UNCAPTURED.append(dict(text=str(text)[:40], font=os.path.basename(getattr(f_, 'path', '') or '?'), size=getattr(f_, 'size', None),
                                       canvas=list(getattr(self, '_image', None).size) if getattr(self, '_image', None) is not None else None))
            return _oidt(self, xy, text, *a, **k)
        _idt._rbu = True
        _ID.ImageDraw.text = _idt
    # N family (pencil / plan marks) on the board: cut out of the cell glass
    _layer_cap(A.H2, 'hover_path', lambda L, *a, **k: 'plan')
    _layer_cap(A.H2, 'hover_cell', lambda L, *a, **k: 'plan')
    _layer_cap(A.PL, 'trigger_path', lambda L, *a, **k: 'plan')
    # hover plates: everything drawn for the other units goes on the dimmed layer; mark it so its masks get a '_dim' class
    hid = A.J['hover']['id'] if beat == 'p2b' else None
    _odu = R.draw_units

    def draw_units(L, f, b, only=None, skip=None):
        DIM[0] = bool(hid is not None and skip and hid in skip)
        try:
            return _odu(L, f, b, only=only, skip=skip)
        finally:
            DIM[0] = False
    R.draw_units = draw_units
    import r2_arcs as A2
    _ola = A2.landing_arcs

    def landing_arcs(L, f, sel, only=None, extra=None):
        DIM[0] = bool(hid is not None and only is not None and hid not in only)
        try:
            return _ola(L, f, sel, only, extra)
        finally:
            DIM[0] = False
    A2.landing_arcs = landing_arcs
    _otw = R.tower_img

    def tower_img(*a, **k):
        im = _otw(*a, **k)
        ox, oy = int(R.C[0] - R.FT.CT[0]), int(R.C[1] - R.FT.CT[1])
        m = Image.new('L', (1920, 1080), 0)
        m.paste(im.split()[3], (ox, oy))
        MASKS['tower'] = np.asarray(m) >= 128
        return im
    R.tower_img = tower_img
    _opu = FH.place_ui

    def place_ui(base, kind, nw, f=None, *a, **k):
        im, (x0, y0) = FH.ui_img(kind, nw, f)
        m = Image.new('L', (1920, 1080), 0)
        m.paste(im.split()[3], (x0, y0))
        MASKS[kind] = np.asarray(m) >= 128
        return _opu(base, kind, nw, f, *a, **k)
    FH.place_ui = place_ui
    _out = R.AS.undo_tab                     # the slate UNDO tab is erased by lw_render (the paper UNDO replaces it): its text is not on the plate

    def undo_tab(*a, **k):
        _guard[0] += 1
        try:
            return _out(*a, **k)
        finally:
            _guard[0] -= 1
    R.AS.undo_tab = undo_tab
    # 2026-11-04: the stack layer's own slate SEND IT and nameplate are drawn and then cut away by f1_render (only the UNDO box and the hint
    # line are kept; lw_ui draws the paper stickers): their words are not on the plate, so they are not text draws of the plate
    for nm_ in ('send_base', 'nameplate'):
        _of = getattr(R.AS, nm_, None)
        if _of is None or getattr(_of, '_rbg', False):
            continue

        def _g(*a, _of=_of, **k):
            _guard[0] += 1
            try:
                return _of(*a, **k)
            finally:
                _guard[0] -= 1
        _g._rbg = True
        setattr(R.AS, nm_, _g)
    _ost = R.AS.stack_layer

    def stack_layer(words, sel):
        lay, info = _ost(words, sel)
        a = np.asarray(lay.split()[3]) >= 128
        box = np.zeros_like(a)
        box[850:900, 1655:1896] = True            # f1_render keeps only this box of the stack layer for UNDO
        MASKS['undo'] = a & box
        return lay, info
    R.AS.stack_layer = stack_layer
    # hand: one record per placed card (name, placement, mask), so the lifted card can be tested against each sibling's cost hex and rules line
    _oput = FH.put
    _odh = FH.draw_hand
    order = []

    def put(base, im, cx, cy, ang=0.0, scale=1.0, *a, **k):
        nm, role = order.pop(0) if order else ('?', '?')
        m = _placed_alpha(im, cx, cy, ang, scale)
        CARDS.append(dict(name=nm, role=role, cx=float(cx), cy=float(cy), ang=float(ang), scale=float(scale), w2=im.width, h2=im.height))
        cls = 'hand_' + role
        MASKS[cls] = MASKS.get(cls, np.zeros((1080, 1920), bool)) | m
        MASKS['card_%d' % (len(CARDS) - 1)] = m
        return _oput(base, im, cx, cy, ang, scale, *a, **k)
    FH.put = put

    def draw_hand(base, J, beat_, nw=False, lift=None, dim_others=None):
        hand, played, hov = FH.hand_lists(J, beat_)
        if lift is not None:
            hov = hand.index(lift)
        order[:] = [(nm, 'rest') for i, nm in enumerate(hand) if i != hov] + [(nm, 'played') for nm in played] + ([(hand[hov], 'lift')] if hov is not None else [])
        return _odh(base, J, beat_, nw, lift, dim_others)
    FH.draw_hand = draw_hand


def empty_probe(R, A, f, beat):
    """the installed skin's empty cell on all 18 cells of an empty frame, over black: the per-ring empty reference"""
    import cv_lib
    L = cv_lib.L2()
    g = copy.deepcopy(f)
    g['units'] = []
    _guard[0] += 1
    try:
        R.paint_cells(L, g, 'p1' if beat in ('p2b', 'nowords') else beat)
    finally:
        _guard[0] -= 1
    bg = Image.new('RGBA', (1920, 1080), (0, 0, 0, 255))
    bg.alpha_composite(L.done())
    return bg.convert('RGB')


def geometry(A, f, beat, hover_id=None):
    """per (ring, sector): the cell polygon as drawn (unit sector slice or empty cell), who is in it and its state; per unit the token disc and the HP tray band"""
    from wr_geo import cell_poly, unit_bounds
    import wr2_lib, wr2_units as W2U, e8lib as E8
    WCL = A.WCL
    cov = WCL.covered(f)
    live = {u['id'] for u in WCL.live_units(f)}
    cells, units = [], []
    owner = {}
    for u in f['units']:
        if u['w'] == 6:
            continue
        for q in range(u['w']):
            owner[(u['dep'], (u['s'] + q) % 6)] = u
    adj = f.get('adj') or {}
    for dep in range(3):
        for s in range(6):
            b0, b1 = 60 * s - 30, 60 * s + 30
            u = owner.get((dep, s))
            if u is not None:
                ub0, ub1 = unit_bounds(u)
                # the unit's cell is one stretched body: take this sector's slice of it (sector boundaries, unwrapped into the unit's span)
                q = (s - u['s']) % 6
                sb0, sb1 = ub0 + 60 * q, ub0 + 60 * (q + 1)
                poly = cell_poly(dep, max(ub0, sb0), min(ub1, sb1), kind='unit')
                if u['consumed'] or u['trigdead']:
                    st = 'ghost'
                elif hover_id is not None and u['id'] != hover_id:
                    st = 'dimmed'            # 2026-11-04: the hover dim wins (a dying unit on p2b is dimmed like every other unit not hovered)
                elif u['fate']['kind'] == 'dies':
                    st = 'dying'
                else:
                    st = 'live'
                cells.append(dict(dep=dep, s=s, uid=u['id'], kind=u['kind'], state=st, poly=[(round(x, 2), round(y, 2)) for x, y in poly]))
            elif (dep, s) in cov:
                st = 'adjuster' if adj and adj.get('ring') == dep else 'covered'
                cells.append(dict(dep=dep, s=s, uid=None, kind='Adjuster' if st == 'adjuster' else '?', state=st, poly=[]))
            else:
                poly = cell_poly(dep, b0, b1, kind='empty')
                cells.append(dict(dep=dep, s=s, uid=None, kind=None, state='empty', poly=[(round(x, 2), round(y, 2)) for x, y in poly]))
    for u in f['units']:
        if u['w'] == 6:
            continue
        x, y = E8.token_pos(u)
        ly = W2U.cell_layout(u)
        b0, b1 = unit_bounds(u)
        units.append(dict(id=u['id'], dep=u['dep'], s=u['s'], w=u['w'], token=(round(x, 2), round(y, 2)), tok_r=wr2_lib.TOK_R,
                          t_in=round(ly['t_in'], 2), t_out=round(ly['t_out'], 2), b0=b0, b1=b1))
    probe = []
    for dep in range(3):
        for s in range(6):
            probe.append(dict(dep=dep, s=s, poly=[(round(x, 2), round(y, 2)) for x, y in cell_poly(dep, 60 * s - 30, 60 * s + 30, kind='empty')]))
    return dict(cells=cells, units=units, probe=probe)


def dump():
    try:
        import rb3_patch as RB3
        INFO['rb3'] = RB3.INFO
    except Exception:
        pass
    return dict(text=TEXT, cards=CARDS, info=INFO, uncaptured_text=UNCAPTURED)
