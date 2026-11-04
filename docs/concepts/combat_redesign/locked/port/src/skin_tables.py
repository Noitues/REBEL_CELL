"""skin_tables (port-2, 2026-11-04): the numbers the Godot CombatLookData / CombatCorpSkin resources and corp_ring.gdshader need, read from
the locked generator itself, so nothing is retyped.

It imports corp/src read-only (rb_tokens, rb_patch, rb3_patch, cs_skin, lw_skin, gram, gramlib, bd_grade, card_render, lw_install) and the
C/D/H/L effect kit (fx_cdhl/src/fxk_lib, for the C-family scan ink per skin), installs only the skin overrides (rb_patch._skins(), which
patches the skin classes in memory and writes nothing), and then:
  - copies every colour token, slice ink, card type colour, value target and cell value knob from the modules (hex + CIE L*);
  - computes the occupied kind fills and the empty fills per ring with the generator's own functions (gram.kind_wash, rb_patch.at_lstar)
    and the knobs rb3_patch installs (OCC_L, EMPTY_L), with the kind ramp and the empty base colour read from rb_patch's source (AST);
  - lists, per skin and per method, the layers the method draws (acc.add colour + alpha formula; L.line / L.poly / L.ellipse / L.rect
    colours and widths), read from the method's own source with the AST and its colours evaluated in the method's namespace;
  - evaluates every band material (cell, bezel, annulus, rim) on a polar grid with the generator's own region code and records the mean
    (the golden for corp_ring.gdshader); the band radii are read from lw_install's source (AST);
  - copies the cell colours measured on the published plates (final/checks.json, check d rows).
Nothing in corp/src or fx_cdhl/src is written (sys.dont_write_bytecode; no generator entry point is run).
usage: python skin_tables.py <out_json>"""
import sys, os, json, ast, inspect, textwrap, hashlib
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
FXK = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/src'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'
sys.path.insert(0, SRC)
import numpy as np
from PIL import Image, ImageDraw
import rb_tokens as T
import rb_patch as RBP
import rb3_patch as RB3
import cs_skin as CS
import lw_skin as LS
import gram as G
import gramlib as GL
import bd_grade as BG
import card_render as CR
import wr_geo as WG
sys.path.insert(1, FXK)
import fxk_lib as FK

PLATES = ('p1_decide', 'p1_decide_solace', 'p1_decide_meridian')
SKIN_OF_PLATE = {'p1_decide': 'neutral', 'p1_decide_solace': 'solace', 'p1_decide_meridian': 'meridian'}
KINDS = ('Packet', 'Worm', 'Jammer', 'Payload', 'Ring')
METHODS_MAT = ('cell', 'bezel', 'annulus', 'arcframe', 'rim')
METHODS_VEC = ('rim_vector', 'crest', 'cell_detail', 'token_frame', 'disc_frame', 'ticket')
CTX = ({'empty': False, 'nearest': True, 'climax': False, 'dep': 0, 's': 1.0}, {'empty': True, 'nearest': False, 'climax': True, 'dep': 2, 's': 1.0})


# ---------------------------------------------------------------------------------------------------------- small helpers
def hexs(c):
    """#RRGGBB of a colour given as 0-255 ints, or as card_render's 0-1 float arrays (@A appended for a 4th channel)"""
    raw = np.asarray(c)
    a = raw.astype(np.float64).reshape(-1).copy()
    if raw.dtype.kind == 'f' and a[:3].max() <= 1.0:
        a[:3] = a[:3] * 255.0
    v = [max(0, min(255, int(round(x)))) for x in a]
    return '#' + ''.join('%02X' % x for x in v[:3]) + ('' if len(v) < 4 else '@%d' % v[3])


def lstar(c):
    return round(float(T.lstar(T.lum(np.array(c[:3], np.float64)))), 1)


def tok(c):
    return dict(hex=hexs(c), L=lstar(c))


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def is_colour(v):
    try:
        a = np.asarray(v, np.float64).reshape(-1)
    except Exception:
        return False
    if a.size not in (3, 4) or not np.all(np.isfinite(a)):
        return False
    return bool(np.all(a >= 0) and np.all(a <= 255))


def as_colour(v):
    a = np.asarray(v, np.float64).reshape(-1)
    if a[:3].max() <= 1.0 and np.asarray(v).dtype.kind == 'f':
        a = a.copy()
        a[:3] = a[:3] * 255.0
    return [int(round(x)) for x in a]


def try_eval(seg, ns):
    try:
        return eval(compile(seg, '<expr>', 'eval'), dict(ns))
    except Exception:
        return None


def colour_of(node, src, nss):
    """the colour an expression gives under each context namespace; a sub-expression when the whole needs runtime arrays"""
    seg = ast.get_source_segment(src, node)
    out = []
    for ns in nss:
        v = try_eval(seg, ns)
        if not is_colour(v):
            v = None
            for sub in ast.walk(node):
                if sub is node:
                    continue
                s2 = ast.get_source_segment(src, sub)
                if not s2:
                    continue
                v2 = try_eval(s2, ns)
                if is_colour(v2):
                    v = v2
                    break
        out.append(hexs(as_colour(v)) if v is not None else None)
    out = [o for i, o in enumerate(out) if o not in out[:i]]
    return out[0] if len(out) == 1 else out


def num_of(node, src, ns):
    if node is None:
        return None
    seg = ast.get_source_segment(src, node)
    v = try_eval(seg, ns)
    if isinstance(v, (int, float, np.floating)):
        return round(float(v), 3)
    return seg


def with_locals(src, fnode, nss):
    """the namespaces with the function's own simple top-level assignments evaluated in order (o = P['hazard_a'], INK = (...))"""
    out = []
    a = fnode.args
    pos = a.args[len(a.args) - len(a.defaults):] if a.defaults else []
    for ns in nss:
        ns = dict(ns)
        for arg, d in zip(pos, a.defaults):
            v = try_eval(ast.get_source_segment(src, d), ns)
            if v is not None and arg.arg not in ns:
                ns[arg.arg] = v
        for st in fnode.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                v = try_eval(ast.get_source_segment(src, st.value), ns)
                if v is not None:
                    ns[st.targets[0].id] = v
        out.append(ns)
    return out


def cell_value(v):
    if is_colour(v) and len(np.asarray(v).reshape(-1)) in (3, 4) and not isinstance(v, (int, float)):
        return hexs(as_colour(v))
    if isinstance(v, (int, float, np.floating)):
        return round(float(v), 3)
    return str(v)


def layers(src, fnode, nss, file_line0=0):
    """the drawing layers of one function: acc.add(colour, alpha) and L.<shape>(..., colour) calls, in source order; a for loop over a
    literal table is listed with its values (the colours and widths it feeds)"""
    nss = with_locals(src, fnode, nss)
    rows = []
    for n in ast.walk(fnode):
        if isinstance(n, ast.For):
            v = try_eval(ast.get_source_segment(src, n.iter), nss[0])
            if isinstance(v, (tuple, list)) and v and all(isinstance(e, (tuple, list)) for e in v):
                rows.append(dict(op='for', line=file_line0 + n.lineno, target=ast.get_source_segment(src, n.target),
                                 values=[[cell_value(x) for x in e] for e in v]))
            continue
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)):
            continue
        meth = n.func.attr
        owner = ast.get_source_segment(src, n.func.value) or ''
        line = file_line0 + n.lineno
        kw = {k.arg: k.value for k in n.keywords}
        if meth == 'add' and owner == 'acc' and len(n.args) >= 2:
            r = dict(op='add', line=line, colour=colour_of(n.args[0], src, nss), alpha=ast.get_source_segment(src, n.args[1]))
            if not isinstance(n.args[0], (ast.Tuple, ast.Name, ast.Subscript)):
                r['colour_expr'] = ast.get_source_segment(src, n.args[0])
            rows.append(r)
        elif owner in ('L', 'T', 'Tl') and meth in ('line', 'poly', 'ellipse', 'rect', 'glow'):
            r = dict(op=meth, line=line)
            if meth == 'line' and len(n.args) >= 2:
                r['colour'] = colour_of(n.args[1], src, nss)
                r['width'] = num_of(n.args[2] if len(n.args) > 2 else kw.get('w'), src, nss[0])
            for k in ('fill', 'outline'):
                if k in kw and not (isinstance(kw[k], ast.Constant) and kw[k].value is None):
                    r[k] = colour_of(kw[k], src, nss)
            if 'w' in kw:
                r['width'] = num_of(kw['w'], src, nss[0])
            if meth == 'glow':
                r['args'] = ast.get_source_segment(src, n)[:160]
            rows.append(r)
        elif owner == 'self' and meth not in ('pal',):
            rows.append(dict(op='call', line=line, call='self.' + meth))
    rows.sort(key=lambda r: r['line'])
    return rows


def fn_layers(fn, skin):
    """layers of a skin method (a function object), evaluated in its own globals + closure + (P = self.pal, self)"""
    f = getattr(fn, '__func__', fn)
    path = inspect.getsourcefile(f)
    lines, l0 = inspect.getsourcelines(f)
    src = textwrap.dedent(''.join(lines))
    tree = ast.parse(src)
    fnode = tree.body[0]
    base = dict(f.__globals__)
    if f.__closure__:
        for name, cell in zip(f.__code__.co_freevars, f.__closure__):
            try:
                base[name] = cell.cell_contents
            except ValueError:
                pass
    base.update(P=skin.pal, self=skin, np=np)
    nss = [dict(base, **c) for c in CTX]
    return dict(source='%s:%d' % (os.path.basename(path), l0), layers=layers(src, fnode, nss, l0 - 1))


def module_fn_layers(mod, outer, inner_names):
    """layers of functions nested in mod.<outer> (not callable on their own): source-only, namespace = module globals + the outer
    function's simple assignments, evaluated in order"""
    path = inspect.getsourcefile(mod)
    src = open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == outer:
            ns = dict(vars(mod))
            for st in node.body:
                if isinstance(st, ast.ImportFrom) and st.module:
                    m = __import__(st.module, fromlist=[al.name for al in st.names])
                    for al in st.names:
                        if hasattr(m, al.name):
                            ns[al.asname or al.name] = getattr(m, al.name)
                if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                    v = try_eval(ast.get_source_segment(src, st.value), ns)
                    if v is not None:
                        ns[st.targets[0].id] = v
            for st in ast.walk(node):
                if isinstance(st, ast.FunctionDef) and st.name in inner_names:
                    out[st.name] = dict(source='%s:%d' % (os.path.basename(path), st.lineno),
                                        layers=layers(src, st, [dict(ns, **c) for c in CTX]))
    return out


def find_call_args(mod, fn_name, call_name):
    """literal arguments of every call to call_name inside mod.fn_name (AST, no execution)"""
    path = inspect.getsourcefile(mod)
    src = open(path, encoding='utf-8').read()
    tree = ast.parse(src)
    res = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (fn_name is None or node.name == fn_name):
            for c in ast.walk(node):
                if isinstance(c, ast.Call) and ((isinstance(c.func, ast.Name) and c.func.id == call_name) or
                                                (isinstance(c.func, ast.Attribute) and c.func.attr == call_name)):
                    res.append((c, src))
    return res


# ---------------------------------------------------------------------------------------------------------- probes
class FakeL:
    """a 2x canvas with the plate's L interface that region_apply composites onto (k = 2)"""
    def __init__(self, base):
        self.k = 2
        self.im = Image.new('RGBA', (1920 * 2, 1080 * 2), tuple(base[:3]) + (255,))


def poly_mean(L, poly):
    m = Image.new('L', L.im.size, 0)
    ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in poly], fill=255)
    mk = np.asarray(m) > 127
    a = np.asarray(L.im.convert('RGB'), np.float64)[mk]
    return [int(round(v)) for v in a.mean(0)]


def cell_composite(skin, base, dep, empty, strength):
    L = FakeL(base)
    poly = WG.cell_poly(dep, -30, 30, kind='empty' if empty else 'unit')
    CS.region_apply(L, [poly], lambda X, Y, RH, TH: skin.cell(X, Y, RH, TH, empty=empty), strength=strength)
    return poly_mean(L, poly)


def band_stats(fn, r0, r1, feather):
    """the material's own output over its band: alpha-weighted mean rgb and the mean alpha (the corp_ring.gdshader golden)"""
    y, x = np.mgrid[0:1080, 0:1080].astype(np.float32) + 0.5
    X = x + 0.0
    Y = y + 0.0
    RHO, TH = CS.polar(X, Y)
    sel = (RHO >= r0 - 1) & (RHO <= r1 + 1)
    Xs, Ys, Rs, Ts = X[sel][None], Y[sel][None], RHO[sel][None], TH[sel][None]
    rgb, a = fn(Xs, Ys, Rs, Ts)
    rgb = np.broadcast_to(np.asarray(rgb, np.float64), Xs.shape + (3,))
    a = np.broadcast_to(np.asarray(a, np.float64), Xs.shape)
    band = np.clip((Rs - r0) / feather + 0.5, 0, 1) * np.clip((r1 - Rs) / feather + 0.5, 0, 1)
    w = a * band
    inside = band > 0.5
    mean_rgb = (rgb * w[..., None]).sum((0, 1)) / max(w.sum(), 1e-9)
    return dict(r=[r0, r1], feather=feather, mean_rgb=hexs([int(round(v)) for v in mean_rgb]), mean_alpha=round(float(a[inside].mean()), 3),
                L_of_mean=lstar(mean_rgb))


# ---------------------------------------------------------------------------------------------------------- main
def main(out):
    RBP._skins()                                     # the rebuild's skin overrides (in memory only)
    skins = {'neutral': LS.NeutralSkin(), 'solace': CS.SKINS['solace'], 'meridian': CS.SKINS['meridian']}
    occ_L, empty_L = RB3.OCC_L, RB3.EMPTY_L          # rb3_patch.install sets rb_patch.OCC_L / EMPTY_L to these

    # the kind ramp and the empty base, read from rb_patch._cells (AST)
    ramp = None
    for c, src in find_call_args(RBP, 'screen', 'kind_wash'):
        for k in c.keywords:
            if k.arg == 'ramp':
                ramp = ast.literal_eval(k.value)
    empty_base = None
    for c, src in find_call_args(RBP, 'empty_cell', 'at_lstar'):
        empty_base = ast.literal_eval(c.args[0])
    assert ramp is not None and empty_base is not None, 'rb_patch cell source changed: kind ramp / empty base not found'

    kind_fill = {k: [RBP.at_lstar(G.kind_wash(k, d, ramp=ramp), occ_L[d]) for d in range(3)] for k in KINDS}
    empty_fill = [RBP.at_lstar(empty_base, empty_L[d]) for d in range(3)]

    # the time grade factors, read from gramlib.grade (AST), and the graded colours from the generator's own grade functions
    gsat = gval = None
    for c in ast.walk(ast.parse(textwrap.dedent(inspect.getsource(GL.grade)))):
        if isinstance(c, ast.Assign) and isinstance(c.targets[0], ast.Tuple):
            vals = ast.literal_eval(c.value.elts[0].value), ast.literal_eval(c.value.elts[1].value)
            gsat, gval = vals
    import f1_board as FB
    time_grade = dict(
        function='gramlib.grade: g = lum + (c - lum) * sat (lum Rec709 on 0-255), out = bed + (g - bed) * val; f1_board.grade2 replaces '
                 'the threat red by the lifted COLD_CHEV / FAR_CHEV',
        bed=hexs(GL.BED), sat=list(gsat), val=list(gval),
        harm=[hexs(FB.grade2(T.HARM_UP, k)) for k in range(3)], enamel=[hexs(GL.grade(GL.ENAMEL, k)) for k in range(3)],
        k_type=[hexs(GL.grade(T.K_TYPE, k)) for k in range(3)], cream_hp=[hexs(GL.grade(T.CREAM_HP, k)) for k in range(3)])

    # band radii (lw_install, AST)
    import lw_install as LI
    bands = {}
    for c, src in find_call_args(LI, None, '_band_fn'):
        nm = c.args[0].attr
        bands[nm] = [ast.literal_eval(a) for a in c.args[1:]] + ([0.8] if len(c.args) < 4 else [])

    res = dict(version='port-2',
               doc='Generated by port/src/skin_tables.py from the locked generator (corp/src) with the rebuild patches as installed. '
                   'Colours are #RRGGBB (@A = alpha 0-255); L is CIE L* of the sRGB colour. Layer lists come from each method\'s own '
                   'source (file:line); alpha entries are the source formulas over (X, Y, RHO, TH) in plate px, angle 0 at 12 o\'clock '
                   'clockwise. material_means are the material functions evaluated with the generator\'s region code: the golden for '
                   'corp_ring.gdshader. measured_on_plates are read from final/checks.json (check d).',
               sources={os.path.basename(p): md5(p) for p in (RBP.__file__, RB3.__file__, T.__file__, CS.__file__, LS.__file__,
                                                               GL.__file__, CR.__file__, LI.__file__, FK.__file__, BG.__file__)})
    res['tokens'] = {k: tok(v) for k, v in T.TOKENS.items()}
    res['neutrals'] = {k: tok(v) for k, v in T.NEUTRALS.items()}
    res['marks'] = {k: tok(getattr(T, k)) for k in ('HARM_UP', 'HOT_CORE', 'COLD_CHEV', 'FAR_CHEV', 'CREAM_HP', 'K_TYPE', 'HIT_PAPER',
                                                     'STEEL_HI_E', 'CREAM_FADED', 'BOSS_GOLD_HI')}
    res['marks']['TOKEN_GLYPH'] = tok(RBP.TOKEN_GLYPH)
    res['plan_badge_v'] = T.PLAN_BADGE_V
    res['boss_gold_old'] = hexs(T.BOSS_GOLD_OLD)
    res['slice_inks'] = {k: dict(ink=hexs(T.SLICE_INK[k]), tex=hexs(T.SLICE_TEX[k]), L=lstar(T.SLICE_INK[k])) for k in T.SLICE_INK}
    res['slice_inks_retired'] = {k: hexs(v) for k, v in T.SLICE_INK_OLD.items()}
    res['card_types'] = {k: dict(col=hexs(v['col']), dk=hexs(v['dk']), text=hexs(v['text']), L=lstar(np.asarray(v['col']) * 255))
                         for k, v in CR.TYPES.items()}
    res['trace_tab'] = hexs(CR.TRACE_VIOLET)
    res['targets'] = dict(cell_ratio_min=T.CELL_RATIO_MIN, clock_L=list(T.CLOCK_L), slice_ink_L=list(T.SLICE_INK_L), cap_min_px=T.CAP_MIN_PX,
                          de_min=T.DE_MIN, order_margin=T.ORDER_MARGIN, room_mean_L=list(T.ROOM_MEAN_L), e_mark_L=T.E_MARK_L,
                          k_type_L=T.K_TYPE_L, mark_margin=T.MARK_MARGIN, ring_val=list(T.RING_VAL),
                          cell_tint_max_chroma=T.CELL_TINT_MAX_CHROMA, review_room_box=list(T.REVIEW_ROOM_BOX))
    res['cells'] = dict(occ_L=list(occ_L), empty_L=list(empty_L), occ_grad=list(RBP.OCC_GRAD), screen_lift=RBP.SCREEN_LIFT,
                        screen_inset=RBP.SCREEN_INSET, skin_unit_k=RBP.SKIN_UNIT_K, skin_empty_k=RBP.SKIN_EMPTY_K, pip_h=RBP.PIP_H,
                        empty_edge_mix=RB3.EMPTY_EDGE_MIX, hot_core_w=RB3.HOT_CORE_W, kind_ramp=list(ramp), empty_base=hexs(empty_base),
                        kind_fill={k: [hexs(c) for c in v] for k, v in kind_fill.items()},
                        kind_fill_L={k: [lstar(c) for c in v] for k, v in kind_fill.items()},
                        empty_fill=[hexs(c) for c in empty_fill], empty_fill_L=[lstar(c) for c in empty_fill],
                        dying=dict(chev_dim=RB3.DYING_CHEV_DIM, hatch_pitch=RB3.KILL_HATCH_PITCH, hatch_w=RB3.KILL_HATCH_W,
                                   hatch_alpha=RB3.KILL_HATCH_A, edge_w=RB3.KILL_EDGE_W, inset=RB3.KILL_INSET),
                        adjuster=dict(seg=RB3.ADJ_SEG, gap=RB3.ADJ_GAP, clear=RB3.ADJ_CLEAR, track_h=RBP.BOSS_SEG_H))
    res['time_grade'] = time_grade
    res['clock'] = dict(gun_fill=tok(RBP.GUN_FILL), gun_light=tok(RBP.GUN_LIGHT), gun_groove=tok(RBP.GUN_GROOVE), schedule=tok(RBP.SCHED),
                        bezel_txt_px=RBP.BEZEL_TXT, label_tracks=list(RBP.LABEL_TRACKS), label_digit_margin=RBP.LABEL_DIGIT_MARGIN,
                        functions=module_fn_layers(RBP, '_clock', ('engraved', 'groove', 'live_cell', 'chevrons', 'hold_glyph')))
    res['bands'] = bands
    res['rooms'] = dict(BG.CORP_ROOM)

    # measured cell colours on the published plates (check d rows)
    fin = json.load(open(FINAL, encoding='utf-8'))
    meas = {}
    for pl in PLATES:
        sk = SKIN_OF_PLATE[pl]
        d = fin['rb_checks'][pl]['d_palette']['rows']
        cells = {}
        for r in d:
            if r['group'] == 'mark x skin cell' and r['a'] == 'HOT mark':
                cells[r['b'][len(sk) + 6:]] = r['b_hex']
        meas[sk] = dict(plate=pl, cells=cells,
                        occ_now_L=fin['rb_checks'][pl]['a_cell_contrast'].get('occ_now_L_range'),
                        lowest_ratio=min((x['ratio'] for x in fin['rb_checks'][pl]['a_cell_contrast']['rows'] if x.get('gated')), default=None))

    res['skins'] = {}
    for nm, s in skins.items():
        cls = type(s)
        methods = {}
        for m in METHODS_MAT + METHODS_VEC:
            fn = getattr(cls, m, None)
            if fn is None or getattr(fn, '__qualname__', '').startswith('Skin.'):
                methods[m] = None
                continue
            methods[m] = fn_layers(fn, s)
        mm = dict(cell_occupied=[], cell_empty=[])
        for d in range(3):
            base = kind_fill['Packet'][d]
            c = cell_composite(s, base, d, False, RBP.SKIN_UNIT_K)
            mm['cell_occupied'].append(dict(ring=d, base=hexs(base), mean=hexs(c), L=lstar(c)))
            c = cell_composite(s, empty_fill[d], d, True, RBP.SKIN_EMPTY_K)
            mm['cell_empty'].append(dict(ring=d, base=hexs(empty_fill[d]), mean=hexs(c), L=lstar(c)))
        for band in ('bezel', 'annulus', 'rim'):
            if band in bands:
                r0, r1, fe = bands[band]
                mm[band] = band_stats(getattr(s, band), r0, r1, fe)
        scan, scan_key = FK.CORP_ENAMEL[nm]
        res['skins'][nm] = dict(
            cls='%s.%s' % (cls.__module__, cls.__name__), kind_gain=list(getattr(s, 'kind_gain', (1.0, 1.0, 1.0))),
            pal={k: hexs(v) for k, v in s.pal.items() if is_colour(v)}, inks={k: tok(v) for k, v in T.SKIN_INKS.get(nm, {}).items()},
            room=BG.CORP_ROOM[nm], c_scan_ink=tok(scan), c_scan_key=tok(scan_key), methods=methods, material_means=mm,
            measured_on_plates=meas.get(nm))
    res['retired_skin_fields'] = dict(
        kind_gain='every skin is 1.0 on every ring (rb_patch._skins): the cell fill is the neutral slate kind wash at the ring value, the skin '
                  'only adds its material, so no per-skin Lab push is baked',
        shutter_slab='C family is one 1.6 px scan line in c_scan_ink (fxk_lib.CORP_ENAMEL), no slab and no lip',
        shutter_lip='as shutter_slab', shutter_lip_shape='as shutter_slab',
        motion_tint='M print echoes are retired (effects/NOTES_MPST.md 2.10); the corp hue in motion is only the wave_enter scan line',
        bits_rings='T5 / T6 bits read the colour of their source from the board (ART_BIBLE 1.2, review 3.12)', bits_accent='as bits_rings',
        hazard_paint='Meridian HAZ_DESAT is 0: the rim stripes and the outer lip are container rust (SKIN_INKS meridian rust), off SCHEDULE')
    json.dump(res, open(out, 'w', encoding='utf-8'), indent=1)
    print('skins', list(res['skins']), 'bands', bands, 'ramp', ramp, 'empty_base', empty_base)
    for nm, sk in res['skins'].items():
        print(nm, {k: (v['source'] if v else None) for k, v in sk['methods'].items()})
        print('  means', json.dumps(sk['material_means'])[:600])


if __name__ == '__main__':
    main(sys.argv[1])
