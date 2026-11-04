"""port_spec (port-2, 2026-11-04): regenerate every table and appendix of GODOT_PORT_SPEC.md (and the numbers block of
MAILBOX_DRAFT.md) from the data files, so no number in them is typed by hand.

Reads (read-only):
  port/fx_timings.json, port/skin_tables.json, port/cards_atlas.json   (made by norm_timings.py, skin_tables.py, bake_cards.py)
  backdrop/grade.json, backdrop/checks.json, final/checks.json, D:/rc_scratch/combat_redesign/locked/corp/src/card_render.py
Each generated block sits between  <!-- gen:NAME begin -->  and  <!-- gen:NAME end -->  in the target file.  Every marker in a file
must have a block here and every block named for a file must have its markers, or nothing is written.
usage: python port_spec.py            write the spliced copies to D:/rc_scratch/combat_redesign/locked/port_rb/work/spec_preview/
       python port_spec.py --write    splice in place"""
import sys, os, re, json, hashlib

LOCK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')).replace('\\', '/') + '/'
CARD_SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src/card_render.py'
PREVIEW = 'D:/rc_scratch/combat_redesign/locked/port_rb/work/spec_preview/'


def load(p):
    return json.load(open(LOCK + p, encoding='utf-8'))


FX = load('port/fx_timings.json')
SK = load('port/skin_tables.json')
CA = load('port/cards_atlas.json')
GR = load('backdrop/grade.json')
BC = load('backdrop/checks.json')
FC = load('final/checks.json')


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def hexof(h):
    return h['hex'] if isinstance(h, dict) else h


def lstar(h):
    h = hexof(h).lstrip('#')[:6]
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    return 116 * y ** (1 / 3) - 16 if y > 216 / 24389 else y * 24389 / 27


def rel_y(h):
    h = h.lstrip('#')[:6]
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    ya, yb = rel_y(a), rel_y(b)
    return (max(ya, yb) + 0.05) / (min(ya, yb) + 0.05)


def hl(h):
    return '%s (L* %.1f)' % (hexof(h), lstar(h))


def gd_color(h, a=None):
    h = hexof(h).lstrip('#')
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    if a is None and len(h) >= 8:
        a = int(h[6:8], 16) / 255.0
    return 'Color(%.4f, %.4f, %.4f, %.4f)' % (c[0], c[1], c[2], 1.0 if a is None else a)


def num(v):
    if isinstance(v, float):
        return ('%.4f' % v).rstrip('0').rstrip('.')
    return str(v)


def rng(vals, fmt='%.1f'):
    vals = [v for v in vals if v is not None]
    lo, hi = min(vals), max(vals)
    return (fmt % lo) if abs(hi - lo) < 1e-9 else (fmt % lo) + '-' + (fmt % hi)


def tok(group, key):
    return SK[group][key]['hex']


def card_text(role):
    for c in CA['cards']:
        for t in c['texts']:
            if t['role'] == role:
                return t
    raise KeyError(role)


INK = card_text('rules')['colour']
WHITE = card_text('title')['colour']
BLOCKS = {}


def block(fn):
    BLOCKS[fn.__name__] = fn
    return fn


# ------------------------------------------------------------------ header
@block
def files():
    f, b = FX, FX['resolve_beat']
    fam = ', '.join('%s %d' % kv for kv in f['families'].items())
    rows = [
        ('`port/fx_timings.json`', '%d effects (%s) merged from `effects/timings_CDHL.json` and `timings_MPST.json`; cap %d ms with %d per-effect '
         'overrides; the resolve beat %d ms against %d (section 8, Appendix A). Version %s.' % (f['count'], fam, f['cap_ms'],
         len(f['per_effect_overrides']), b['total_ms'], b['limit_ms'], f['version'])),
        ('`port/skin_tables.json`', 'Tokens, marks, slice inks, card types, cell fills, the time grade, the gunmetal clock and the three skins '
         'with their material layers read from the generator source (sections 3, 4.3, 4.4, 7, Appendix B). Version %s.' % SK['version']),
        ('`port/cards_atlas.json`, `port/cards_proof.jpg`', 'The card atlas baked from the module that renders `final/card_sheet.jpg`: cell rects, '
         'every text anchor logged from the real draw call, the rules-bar quads, the state recipes; the proof shows art | worded | liner per '
         'card at the in-hand size (sections 4.8, 6.2, Appendix D). Version %s.' % CA['version']),
        ('`port/src/`', '`norm_timings.py`, `skin_tables.py`, `bake_cards.py` make the three data files; `port_spec.py` writes every table and '
         'appendix of this spec from them (and from `backdrop/grade.json`, `backdrop/checks.json`, `final/checks.json`). Re-run all four after '
         'any change upstream; a hand edit inside a `gen:` block is overwritten.'),
    ]
    return '| File | What it is |\n|---|---|\n' + '\n'.join('| %s | %s |' % r for r in rows)


# ------------------------------------------------------------------ 3 tokens
TOKEN_ROWS = [
    ('player_pink (CELL_PINK)', ('tokens', 'CELL_PINK'), 'Player-owned: tower halo, guns, resolve marks, D effects, the lifted-card print'),
    ('toner (ink)', INK, 'Key lines, hatch keyline (card_render INK, logged from the rules text)'),
    ('sheet (paper)', ('neutrals', 'PAPER'), 'Copier paper, card bone'),
    ('white', WHITE, 'Glyph white (card titles, logged)'),
    ('harm', ('tokens', 'HARM'), 'Red hatch = the enemy hits you'),
    ('harm_up (HOT)', ('marks', 'HARM_UP'), 'Threat chevrons and arcs, HOT'),
    ('harm_cold', ('marks', 'COLD_CHEV'), 'COLD threat marks (lifted; `f1_board`)'),
    ('harm_far', ('marks', 'FAR_CHEV'), 'FAR threat marks (lifted)'),
    ('hot_core', ('marks', 'HOT_CORE'), 'The HOT outline core'),
    ('soak', ('tokens', 'SOAK'), 'Blue hatch = soaked'),
    ('gain', ('tokens', 'GAIN'), 'Gains, the clear wash'),
    ('net_cyan', ('tokens', 'NET_CYAN'), 'RAM coin only (and the NO RAM word)'),
    ('trace_violet', ('tokens', 'TRACE_VIOLET'), 'Trace only (card tab, Trace pips, S glitch)'),
    ('boss_gold', ('tokens', 'BOSS_GOLD'), 'Ward and boss (re-picked 2026-11-03; was %s)' % SK['boss_gold_old']),
    ('boss_gold_hi', ('marks', 'BOSS_GOLD_HI'), 'Boss gold highlight'),
    ('resist_gold', ('tokens', 'RESIST_GOLD'), 'Stars (rb_tokens)'),
    ('plan_yellow', ('tokens', 'PLAN'), 'Hover and plan pencil (preview form only)'),
    ('plan_badge', None, 'The twist badge: plan_yellow x %s' % num(SK['plan_badge_v'])),
    ('focus_lime', ('tokens', 'FOCUS'), 'Hover focus corners'),
    ('amber (CRT_AMBER)', ('tokens', 'CRT_AMBER'), 'HOLD plates, Adjuster arc, Heat'),
    ('schedule', ('tokens', 'SCHEDULE'), 'The clock\'s LIVE step only: live cell edge, its chevrons, the rings-step and Hold motion (4.4); and the W6 climax ticket\'s three hazard ticks (VISUAL_PLAN F)'),
    ('clock_fill', SK['clock']['gun_fill']['hex'], 'Gunmetal clock: engraved band and cells (4.4); the same on every corp'),
    ('clock_light', SK['clock']['gun_light']['hex'], 'Gunmetal clock: lip and groove light'),
    ('clock_groove', SK['clock']['gun_groove']['hex'], 'Gunmetal clock: groove, Hold glyph body'),
    ('enamel', ('neutrals', 'ENAMEL'), 'Enemy cell outline, HOT (COLD / FAR in the time grade below)'),
    ('cream_hp', ('marks', 'CREAM_HP'), 'Enemy HP ticks on the board'),
    ('cream_faded', ('marks', 'CREAM_FADED'), 'HP ticks of hover-faded units only (p2b)'),
    ('k_type', ('marks', 'K_TYPE'), 'K type: sector digits, ring tags, W tags, ticket glyphs, nowords tallies (no glow)'),
    ('token_glyph', ('marks', 'TOKEN_GLYPH'), 'Unit glyph in its token frame'),
    ('hit_paper', ('marks', 'HIT_PAPER'), 'Gun hit star fill, tracer highlight, bit white-hot'),
    ('steel_hi', ('marks', 'STEEL_HI_E'), 'The armour rail\'s top edge on enemy HP trays'),
    ('text_hi / best_neutral', ('neutrals', 'TEXT_HI'), 'BEST LINE chip and selected option chips (type), filled star; never plan_yellow'),
    ('text_mid', ('neutrals', 'TEXT_MID'), 'BEST LINE chip edge, HUD mid text'),
    ('p_stock', FX['p_stock']['hex'], 'FX-P plate stock and break shards (%s)' % FX['p_stock']['why']),
]


@block
def tokens():
    out = ['| Token | Hex | L* | Meaning |', '|---|---|---|---|']
    for name, src, meaning in TOKEN_ROWS:
        if src is None:
            out.append('| `%s` | | | %s |' % (name, meaning))
            continue
        h = src if isinstance(src, str) else tok(*src)
        out.append('| `%s` | %s | %.1f | %s |' % (name, h, lstar(h), meaning))
    for k, v in SK['slice_inks'].items():
        out.append('| `slice_%s` | fill %s / texture ink %s | %.1f | Slice ink (`rb_tokens` SLICE_INK / SLICE_TEX) |' % (k.lower(), v['ink'], v['tex'], lstar(v['ink'])))
    for k, v in SK['card_types'].items():
        out.append('| `card_%s` | %s (dark %s, text %s) | %.1f | Card type plate (`card_render.TYPES`) |' % (k.lower(), v['col'], v['dk'], v['text'], lstar(v['col'])))
    out.append('')
    out.append('Retired, never drawn: the silver THIS TURN tape (`tape_lo` / `tape_hi`), the O-29 slice inks, BOSS_GOLD %s. Targets the '
               'tokens are held to (`port/skin_tables.json` `targets`): %s.' % (SK['boss_gold_old'], ', '.join('`%s` %s' % (k, json.dumps(v)) for k, v in SK['targets'].items())))
    return '\n'.join(out)


@block
def time_grade():
    t = SK['time_grade']
    out = ['Function: %s. bed %s, sat %s, val %s (HOT, COLD, FAR).' % (t['function'], t['bed'], t['sat'], t['val']), '',
           '| Mark | HOT | COLD | FAR |', '|---|---|---|---|']
    for k in ('harm', 'enamel', 'k_type', 'cream_hp'):
        out.append('| `%s` | %s |' % (k, ' | '.join(hl(h) for h in t[k])))
    out.append('')
    out.append('Bake these into the resource as three colours per mark; never compute them per frame.')
    return '\n'.join(out)


# ------------------------------------------------------------------ 4.1 room
@block
def room():
    out = ['Grade version **%s**. Skin to room (`bd_grade.CORP_ROOM`): %s.' % (GR['version'], ', '.join('%s → %s' % kv for kv in GR['corp_room'].items())), '',
           'Steps, in order (`backdrop/grade.json` `order`, verbatim):', '']
    for s in GR['order']:
        out.append('- ' + s)
    out += ['', 'Measured on the graded rooms (`backdrop/checks.json`, L* of the room region, after the grade):', '',
            '| Plate | Room | Skin | mean L* | p95 L* | passes |', '|---|---|---|---|---|---|']
    for pl, v in BC['plates'].items():
        r = v['after']['L']['room']
        ok = all(BC['pass'][pl].values())
        out.append('| `%s` | %s | %s | %.1f | %.1f | %s |' % (pl, v['grade_key'], v['corp'], r['mean'], r['p95'], 'yes' if ok else '**no**'))
    out += ['', 'Targets: %s.' % '; '.join('%s: %s' % kv for kv in BC['targets'].items())]
    # the shader path: uniforms with the bio defaults
    bio = GR['rooms']['bio']
    out += ['', 'Shader path uniforms (`shaders/combat/room_grade.gdshader`), defaults = the `bio` room; every room\'s values are in Appendix C:',
            '```glsl', 'shader_type canvas_item;']
    for k in room_keys():
        v = bio.get(k)
        if v is None:
            src = next(r for r in GR['rooms'] if k in GR['rooms'][r])
            v0 = GR['rooms'][src][k]
            if isinstance(v0, (int, float)):
                out.append('uniform float %s = 0.0;   // not set on bio (step off); set on %s' % (k, ', '.join(r for r in GR['rooms'] if k in GR['rooms'][r])))
            else:
                out.append('// %s: not set on bio; %s = %s (Appendix C)' % (k, src, json.dumps(v0)))
            continue
        if k == 'hull_poly':
            out.append('uniform sampler2D hull_sdf;   // hull_poly %s baked once to a signed distance texture (px, + outside)' % json.dumps(v))
        elif isinstance(v, list) and k.endswith('_rgb'):
            out.append('uniform vec3 %s = vec3(%s);   // %s / 255' % (k, ', '.join('%.4f' % (x / 255.0) for x in v), json.dumps(v)))
        elif isinstance(v, list):
            out.append('uniform vec%d %s = vec%d(%s);' % (len(v), k, len(v), ', '.join(num(float(x)) for x in v)))
        elif k == 'ceil':
            out.append('uniform float ceil_ = %s;   // grade.json "ceil"' % num(float(v)))
        else:
            out.append('uniform float %s = %s;' % (k, num(float(v))))
    out += ['uniform float grade_mix = 1.0;   // T5: 0 = bare room, 1 = graded', '```']
    return '\n'.join(out)


def room_keys():
    """every parameter of every room, in order of first appearance (some, like the corp light, are set on one room only)"""
    keys = []
    for r in GR['rooms'].values():
        for k in r:
            if k not in keys:
                keys.append(k)
    return keys


@block
def room_appendix():
    rooms = list(GR['rooms'].keys())
    keys = [k for k in room_keys() if k != 'hull_poly']
    out = ['`backdrop/grade.json` version %s. One row per parameter, one column per room.' % GR['version'], '',
           '| Parameter | ' + ' | '.join(rooms) + ' |', '|---|' + '---|' * len(rooms)]
    for k in keys:
        out.append('| `%s` | %s |' % (k, ' | '.join(json.dumps(GR['rooms'][r].get(k)) for r in rooms)))
    out += ['', 'Hull polygons (plate px):', '']
    for r in rooms:
        out.append('- `%s`: %s' % (r, json.dumps(GR['rooms'][r].get('hull_poly'))))
    return '\n'.join(out)


# ------------------------------------------------------------------ 4.3 cells
@block
def cells():
    c = SK['cells']
    out = ['Every skin draws the same cell fill (`kind_gain` 1.0 on every ring of every skin; `retired_skin_fields.kind_gain`: %s). '
           'The skin adds its material over it (section 7, Appendix B).' % SK['retired_skin_fields']['kind_gain'], '',
           '| Fill | ring NOW | ring +1 | ring +2 |', '|---|---|---|---|']
    for k, v in c['kind_fill'].items():
        out.append('| occupied, %s | %s |' % (k, ' | '.join(hl(h) for h in v)))
    out.append('| empty | %s |' % ' | '.join(hl(h) for h in c['empty_fill']))
    out += ['', 'Targets: occupied L* %s, empty L* %s per ring. Other cell numbers: %s.' % (c['occ_L'], c['empty_L'], ', '.join(
        '`%s` %s' % (k, json.dumps(v)) for k, v in c.items() if k not in ('kind_fill', 'kind_fill_L', 'empty_fill', 'empty_fill_L', 'occ_L', 'empty_L'))), '',
            'With the skin material composited (`skin_tables.py`, the material layers over the fill on a 2x canvas) and on the plates:', '',
            '| Skin | occupied mean L* (NOW / +1 / +2) | empty mean L* | data: luminance ratio occupied / empty, lowest ring (the check-a measure) | plate: ring NOW occupied L* | plate: lowest ratio |',
            '|---|---|---|---|---|---|']
    for nm, s in SK['skins'].items():
        mm = s['material_means']
        occ = [r['mean'] for r in mm['cell_occupied']]
        emp = [r['mean'] for r in mm['cell_empty']]
        rr = min(rel_y(a) / rel_y(b) for a, b in zip(occ, emp))
        m = s['measured_on_plates']
        out.append('| %s | %s | %s | %.2f | %s | %.2f |' % (nm, ' / '.join('%.1f' % lstar(h) for h in occ), ' / '.join('%.1f' % lstar(h) for h in emp),
                                                           rr, rng(m['occ_now_L']), m['lowest_ratio']))
    return '\n'.join(out)


# ------------------------------------------------------------------ 4.4 clock
@block
def clock():
    k = SK['clock']
    out = ['| Part | Colour |', '|---|---|']
    for nm in ('gun_fill', 'gun_light', 'gun_groove', 'schedule'):
        out.append('| `%s` | %s |' % (nm, hl(k[nm]['hex'])))
    out += ['', 'Band text %s px, label tracks %s, label to digit margin %s px.' % (k['bezel_txt_px'], k['label_tracks'], k['label_digit_margin']), '',
            'Draw calls, read from the generator source (`skin_tables.py`):', '', '| Function | Source | Layers |', '|---|---|---|']
    for nm, f in k['functions'].items():
        out.append('| `%s` | `%s` | %s |' % (nm, f['source'], '; '.join('`%s`' % json.dumps({a: b for a, b in L.items() if a != 'line'}) for L in f['layers'])))
    return '\n'.join(out)


# ------------------------------------------------------------------ 4.8 / 5.5 / 6.2 cards
def tdesc(t):
    return '%s %s px, track %s, rot %s°, %s' % (os.path.splitext(t['font'])[0], num(t['px']), num(t['track']), num(t['rot']), t['colour'])


@block
def cards():
    out = ['Logged from the real `text()` calls while each card is drawn (`bake_cards.py`; per-card values in Appendix D). Coordinates are '
           'card design px (the card is %d x %d; cell px = (design + %d) x %s).' % (CA['design_card'][0], CA['design_card'][1], CA['design_margin'],
                                                                                   num(CA['scale_vs_design'])), '',
           '| Text | Font, size, tracking, rotation, colour | Anchor (design px, centre of the cap height) | Cards |', '|---|---|---|---|']
    seen = {}
    for c in CA['cards']:
        for t in c['texts'] + c['liner_texts']:
            key = (t['role'], t['font'], t['px'], t['track'], t['rot'], t['colour'], t['x'], t['y'] if t['role'] != 'rules' else None)
            seen.setdefault(key, (t, []))[1].append(c['id'])
    for key, (t, ids) in seen.items():
        if t['role'] == 'rules':
            continue
        out.append('| %s | %s | (%s, %s) | %s |' % (t['role'], tdesc(t), num(t['x']), num(t['y']), 'all' if len(ids) == len(CA['cards']) else ', '.join(ids)))
    r = CA['rules']
    rt = card_text('rules')
    out.append('| rules | %s; never shrunk; wider than %s px wraps to two lines (%s) | one line (%s, %s); two lines (%s, %s) and (%s, %s) | all |' % (
        tdesc(rt), num(r['fit_w']), r['wrap'], num(r['cx']), num(r['ly1'][0]), num(r['cx']), num(r['ly2'][0]), num(r['cx']), num(r['ly2'][1])))
    out.append('| rules bar | %s quad under the last line, from the label width; drawn by Godot, not in the art atlas | y band below the last line: one line %s, two lines %s (quads per card in Appendix D) | all |' % (
        r['bar_colour'], r['bar_band']['0'], r['bar_band']['1']))
    out += ['', 'The title\'s plate, keyline and drop, the type plate and the tab plates are art (in the atlas); their drawing code is in Appendix D, verbatim. '
            'Hand scale %s: the card is %s px wide on screen.' % (num(CA['hand_scale']), num(CA['design_card'][0] * CA['hand_scale']))]
    return '\n'.join(out)


@block
def unaffordable():
    n = CA['no_ram']
    nr = FC['cards']['no_ram_word']
    rec = CA['state_recipes']
    return '\n'.join([
        '- Dim glass, `card_render._unaffordable` (`%s:%d`), verbatim:' % (rec['unaffordable_dim']['file'], rec['unaffordable_dim']['line']),
        '  ```python', '\n'.join('  ' + s for s in rec['unaffordable_dim']['source'].rstrip().split('\n')), '  ```',
        '- Over the glass at full value (`unaffordable_marks`, `%s:%d`): the "%s" tab (design rect x %s-%s, y %s-%s, visible from x %s; '
        'word centre x %s; Anton %s px, track %s, in %s; measured cap %s px at the hand scale, fits the tab: %s), the cost badge redrawn '
        '(centre %s), and the padlock (`lock_glyph`, `%s:%d`). nowords keeps the badge and the padlock only. These are sprites on the card, '
        'not shader work.' % (rec['unaffordable_marks']['file'], rec['unaffordable_marks']['line'], n['word'], num(n['tab_design_px'][0]),
                              num(n['tab_design_px'][1]), num(n['tab_design_px'][2]), num(n['tab_design_px'][3]), num(n['vis_x0']), num(n['cx']),
                              num(n['px']), num(n['track']), nr['colour'], num(nr['cap_screen_px_at_1p10']), nr['fits_tab'], n['cost_c'],
                              rec['lock_glyph']['file'], rec['lock_glyph']['line'])])


@block
def atlas():
    out = ['| File | Size | md5 | Opaque px | What |', '|---|---|---|---|---|']
    what = {'cards_art_atlas.png': 'normal state, art only: every word and the rules bar left out',
            'cards_ref_atlas.png': 'the same with words and bar: what the Labels plus the bar must reproduce',
            'cards_liner_atlas.png': 'the played-slot liner, art only (Godot labels the name and PLAYED)'}
    for nm, f in CA['files'].items():
        out.append('| `%s` | %d x %d | `%s` | %d | %s |' % (nm, f['size'][0], f['size'][1], f['md5'], f['alpha_px'], what.get(nm, '')))
    sw = CA['design_card'][0] * CA['hand_scale']
    out += ['', '%d x %d cells of **%d x %d** (the card %d px wide = %sx design, plus %d px margin each side), in `card_render.ORDER`. '
            'Sources: %s. On screen at %s the card is %s px wide, so the atlas is %.2fx screen.' % (
                CA['cols'], -(-len(CA['cards']) // CA['cols']), CA['cell'][0], CA['cell'][1], CA['size_px'], num(CA['scale_vs_design']),
                CA['margin_px'], ', '.join('`%s` md5 `%s`' % kv for kv in CA['sources'].items()), num(CA['hand_scale']), num(sw), CA['size_px'] / sw),
            '', 'Note: %s.' % CA['note_snapshot']]
    return '\n'.join(out)


# ------------------------------------------------------------------ 7 skins
MATERIAL_KIND = {'neutral': 'ENAMEL_LINES', 'solace': 'MEMBRANE', 'meridian': 'RIBS'}
EMPTY_MARKS = {'meridian': 'stencilled container numbers on empty cells: hook only, art not drawn'}
PIECES = {'neutral': 'rim: degree ticks on steel; crest: dark roundel with pale ring and bar (section 6.3 textures)',
          'solace': 'rim_texture (helix turns), crest (porcelain roundel, lime helix S), token_frame (porcelain ring, lime dot at 12), '
                    'ticket (chamfered lab slide) (section 6.3 textures)',
          'meridian': 'rim: stripes in container rust, crest crane-A, token_frame steel octagon with 4 corner castings, ticket square-cut '
                      'shipping tag with barcode (section 6.3 textures)'}


@block
def skins():
    out = ['| Skin | Class | Room | `kind_gain` | Hue inks (rim, lip, crest, cell edges) | C scan line ink | Material means, occupied L* (NOW / +1 / +2) |',
           '|---|---|---|---|---|---|---|']
    for nm, s in SK['skins'].items():
        out.append('| %s | `%s` | %s | %s | %s | %s (%s) | %s |' % (
            nm, s['cls'], s['room'], s['kind_gain'], ', '.join('%s %s' % (k, hl(v['hex'])) for k, v in s['inks'].items()) or '(none)',
            hl(s['c_scan_ink']), 'key ' + hl(s['c_scan_key']), ' / '.join('%.1f' % r['L'] for r in s['material_means']['cell_occupied'])))
    out += ['', 'Palettes (`pal`), as installed by `rb_patch._skins()`:', '', '| Skin | ' + ' | '.join(sorted({k for s in SK['skins'].values() for k in s['pal']})) + ' |']
    keys = sorted({k for s in SK['skins'].values() for k in s['pal']})
    out.append('|---|' + '---|' * len(keys))
    for nm, s in SK['skins'].items():
        out.append('| %s | %s |' % (nm, ' | '.join(str(s['pal'].get(k, '')) for k in keys)))
    out += ['', 'Retired skin fields (never port them):', '']
    for k, v in SK['retired_skin_fields'].items():
        out.append('- `%s`: %s' % (k, v))
    out += ['', '**The three `.tres` files** (`content/combat/skins/<id>.tres`), generated; the ShaderMaterials and textures are filled from '
            'Appendix B and section 6.3:', '```']
    for nm, s in SK['skins'].items():
        out += ['# content/combat/skins/%s.tres   (%s; room %s)' % (nm, s['cls'], s['room']),
                '[gd_resource type="Resource" script_class="CombatCorpSkin" load_steps=2 format=3]',
                '[ext_resource type="Script" path="res://scripts/data/combat_corp_skin.gd" id="1"]', '[resource]', 'script = ExtResource("1")',
                'id = &"%s"' % nm, 'material_kind = %d   # %s' % (list(MATERIAL_KIND.values()).index(MATERIAL_KIND[nm]), MATERIAL_KIND[nm]),
                'room = &"%s"' % s['room'], 'c_scan_ink = %s   # %s' % (gd_color(s['c_scan_ink']), hexof(s['c_scan_ink']))]
        if s['inks']:
            out.append('inks = {%s}' % ', '.join('&"%s": %s' % (k, gd_color(v['hex'])) for k, v in s['inks'].items()))
        out.append('pal = {%s}' % ', '.join('&"%s": %s' % (k, gd_color(v)) for k, v in s['pal'].items() if isinstance(v, str) and v.startswith('#')))
        if nm in EMPTY_MARKS:
            out.append('empty_marks = true   # %s' % EMPTY_MARKS[nm])
        out.append('# + cell_material / bezel_material / annulus_material / arcframe_material (ShaderMaterial sub-resources, Appendix B)')
        out.append('# + %s' % PIECES[nm])
        out.append('')
    out.append('```')
    return '\n'.join(out)


@block
def skin_appendix():
    out = ['Each material method of each skin, read from the generator source by `skin_tables.py` (AST of the method body: `acc.add`, '
           '`L.line` / `poly` / `ellipse` / `rect` / `glow`, and `for` loops over literal tables). `colour` is the evaluated value, '
           '`colour_expr` the source expression where it is not a constant. These are the layers `corp_ring.gdshader` and the 6.3 bakes reproduce.']
    for nm, s in SK['skins'].items():
        out += ['', '**%s** (`%s`)' % (nm, s['cls']), '```']
        for m, v in s['methods'].items():
            if not v:
                continue
            out.append('%s  %s' % (m, v['source']))
            for L in v['layers']:
                out.append('    ' + json.dumps(L))
        out.append('```')
    return '\n'.join(out)


# ------------------------------------------------------------------ 8 effects
@block
def fx_counts():
    f = FX
    out = ['`port/fx_timings.json` holds **%d effects**: %s.' % (f['count'], ', '.join('%s %d' % kv for kv in f['families'].items())), '',
           '- Cap: every total, every phase end and every reduce form at most **%d ms**; per-effect overrides: %d. Tier: %s.' % (
               f['cap_ms'], len(f['per_effect_overrides']), f['tier_vfx']),
           '- Layer: %s.' % f['layer_rule'],
           '- Frames: %d fps. Loudness: %s, measured as %s.' % (f['fps'], f['loudness_rule'], f['loudness_metric']), '',
           '| Effect | Family | Kind | Layer | Total ms (O-30 → now) | Reduce ms | Flashes/s full / reduce |', '|---|---|---|---|---|---|---|']
    for e in f['effects']:
        out.append('| `%s` | %s | %s | %s | %s → **%d** | %s | %s / %s |' % (e['id'], e['family'], e['kind'], e['layer'], e.get('total_ms_o30'), e['total_ms'],
                                                                     red(e), e['max_flashes_per_s'], e['reduce_max_flashes_per_s']))
    return '\n'.join(out)


@block
def beat():
    b = FX['resolve_beat']
    out = ['**%d ms against a %d ms limit** (skin %s). Skip: %s; %d ms. Order: %s.' % (b['total_ms'], b['limit_ms'], b['skin'], b['skip'], b['skip_ms'], b['order']), '',
           '| Track | Effect | Family | Start ms | Length ms | End ms | What |', '|---|---|---|---|---|---|---|']
    for t in b['tracks']:
        out.append('| %s | `%s` | %s | %d | %d | %d | %s |' % (t['name'], t['effect'] or '(none)', t['family'] or '-', t['start_ms'], t['dur_ms'], t['end_ms'], t['what']))
    out += ['', 'Flash over the whole beat: `%s`.' % json.dumps(b.get('flash')), '', '**Not to ship:** %s.' % b['not_to_ship']]
    for k in ('kill_colour', 'gif'):
        if b.get(k):
            out.append('%s: %s.' % (k.replace('_', ' ').capitalize(), b[k] if isinstance(b[k], str) else json.dumps(b[k])))
    return '\n'.join(out)


@block
def loudness():
    out = ['Rule: %s. Two meters, one per designer set (same metric):' % FX['loudness_rule'], '',
           '| Set | Skin | Passes | Tier boundaries (quietest of the louder kind > loudest of the quieter kind) |', '|---|---|---|---|']
    for st, per in FX['loudness_order'].items():
        for sk, v in per.items():
            if 'tiers' in v:
                tt = [(t['upper'], t['upper_min'], t['upper_min_id'], t['lower'], t['lower_max'], t['lower_max_id']) for t in v['tiers']]
            else:
                tt = [(t['louder'], t['min_louder'][1], t['min_louder'][0], t['quieter'], t['max_quieter'][1], t['max_quieter'][0]) for t in v['checks']]
            tiers = '; '.join('%s %s (`%s`) > %s %s (`%s`)' % t for t in tt)
            out.append('| %s | %s | %s | %s |' % (st, sk, 'yes' if v['passes'] else '**no**', tiers))
    return '\n'.join(out)


@block
def eases():
    seen = {}
    for e in FX['effects']:
        for p in e['phases'] + e.get('reduce_phases', []):
            k = (p['ease_raw'], p['ease'])
            seen.setdefault(k, set()).add(e['id'])
    out = ['Every raw ease string in the data, the code it maps to, and where it is used. A raw string with more than the code '
           '(an overshoot value, a step quantum, a wobble, gravity, a stagger, a width curve) needs a sampled Curve built from the string.', '',
           '| Raw (source) | Code | Effects |', '|---|---|---|']
    for (raw, code), ids in sorted(seen.items(), key=lambda kv: (str(kv[0][1]), str(kv[0][0]))):
        out.append('| %s | `%s` | %s |' % ('`%s`' % raw if raw is not None else '(no ease given in the source; norm_timings reads it as LINEAR)', code, ', '.join('`%s`' % i for i in sorted(ids))))
    return '\n'.join(out)


def red(e):
    """the reduce form's length, or where it is only described (CDHL: one still per effect, timed in the reduce_motion text)"""
    if e['reduce_total_ms'] is not None:
        return str(e['reduce_total_ms'])
    return 'in `reduce_motion` (one still per effect)'


def phases_txt(ph):
    return '; '.join('%s %d-%d %s' % (p['name'], p['start_ms'], p['end_ms'], p['ease']) for p in ph)


@block
def fx_appendix():
    out = ['| id | fam | kind | layer | total ms | phases (name start-end ease) | reduce ms | reduce motion | flashes/s full / reduce |',
           '|---|---|---|---|---|---|---|---|---|']
    for e in FX['effects']:
        out.append('| `%s` | %s | %s | %s | %d | %s | %s | %s | %s / %s |' % (e['id'], e['family'], e['kind'], e['layer'], e['total_ms'], phases_txt(e['phases']),
                                                                    red(e),
                                                                    (e['reduce_motion'] or '').replace('|', '/'), e['max_flashes_per_s'],
                                                                    e['reduce_max_flashes_per_s']))
    out += ['', 'Phases with equal start and end are instant events at that time. Sources (md5): %s.' % ', '.join('`%s` `%s`' % kv for kv in FX['sources'].items())]
    return '\n'.join(out)


# ------------------------------------------------------------------ Appendix D cards
def card_sections():
    src = open(CARD_SRC, encoding='utf-8').read().split('\n')
    marks = [i for i, s in enumerate(src) if s.strip().startswith('# ----------------') and s.startswith('    ')]
    out = []
    for j, i in enumerate(marks):
        head = src[i].strip()
        if not any(w in head for w in ('title', 'type plate', 'rules text', 'cost badge', 'loud tab')):
            continue
        k = marks[j + 1] if j + 1 < len(marks) else next(n for n in range(i + 1, len(src)) if src[n].startswith('    return'))
        out.append((i + 1, '\n'.join(src[i:k]).rstrip()))
    return out


@block
def card_appendix():
    assert md5(CARD_SRC) == CA['sources']['corp/src/card_render.py'], 'card_render changed since bake_cards ran: re-run bake_cards.py'
    out = ['| Card | Type | Cost | Trace | Mult | Text draws (role "text" @ design x, y) | Rules bar quad (design px) |', '|---|---|---|---|---|---|---|']
    for c in CA['cards']:
        tx = '; '.join('%s "%s" @ %s, %s' % (t['role'], t['txt'], num(t['x']), num(t['y'])) for t in c['texts'])
        out.append('| %s | %s | %s | %s | %s | %s | %s |' % (c['id'], c['type'], c['cost'], c['trace'], c['mult'] or '', tx.replace('|', '/'),
                                                            ' '.join('(%s, %s)' % (num(x), num(y)) for x, y in c['rules_bar']['quad_design_px'])))
    lt = CA['cards'][0]['liner_texts']
    out += ['', 'Played liner text (every card): %s.' % '; '.join('%s "%s" @ %s, %s, %s' % (t['role'], t['txt'], num(t['x']), num(t['y']), tdesc(t)) for t in lt),
            'Liner art numbers: %s.' % json.dumps(CA['liner']), '', 'Card text plates, verbatim from `corp/src/card_render.py` `render_base` (md5 `%s`):' % CA['sources']['corp/src/card_render.py']]
    for line, s in card_sections():
        out += ['', 'Line %d:' % line, '```python', s, '```']
    for k in ('liner', 'draw_card'):
        r = CA['state_recipes'][k]
        out += ['', '`%s`, `%s:%d` (the state switch; the hover print and drop offsets of 5.5 are read from it):' % (k, r['file'], r['line'])
                if k == 'draw_card' else '`_liner`, `%s:%d`:' % (r['file'], r['line']), '```python', r['source'].rstrip(), '```']
    return '\n'.join(out)


# ------------------------------------------------------------------ 13 checks
def plates():
    return FC['rb_checks'].items()


def check_rows():
    T = SK['targets']
    R = []
    occ = [x for _, p in plates() for x in (p['a_cell_contrast']['occ_now_L_range'] or [])]
    low = [s['measured_on_plates']['lowest_ratio'] for s in SK['skins'].values()]
    R.append(('rb a: cell contrast', FC['rb_checks']['p1_decide']['a_cell_contrast']['rule'], 'ratio >= %s' % T['cell_ratio_min'],
              'all %d plates pass; ring NOW occupied L* %s; lowest ratio per skin %s' % (len(FC['rb_checks']), rng(occ), ', '.join('%.2f' % v for v in low)),
              '`test_waves_cell_contrast.gd`: for each skin and ring, the composited occupied fill over the brightest empty fill (section 4.3 data) >= `cell_ratio_min`'))
    R.append(('rb b: value order', FC['rb_checks']['p1_decide']['b_value_order']['rule'], 'chain holds, margin %s L*' % T['order_margin'],
              '%d failures on %d plates; ring NOW glass p95 reference L* %s' % (sum(len(p['b_value_order']['failures']) for _, p in plates()), len(FC['rb_checks']),
                                                                               rng([p['b_value_order']['room_ref']['value'] for _, p in plates()])),
              '`test_combat_look_values.gd`: clock fill L* in `clock_L`, slice inks in `slice_ink_L`, K type and CREAM_HP at `e_mark_L` / `k_type_L` ± `mark_margin`, cell tint chroma <= `cell_tint_max_chroma`; the pixel order itself is a capture check (13.2)'))
    caps = [p['c_cap_height']['smallest'][0]['cap_px'] for _, p in plates() if p['c_cap_height']['smallest']]
    R.append(('rb c: cap height', FC['rb_checks']['p1_decide']['c_cap_height']['rule'], '>= %s px' % num(T['cap_min_px']),
              '%d text draws, %d fail; smallest cap %s px' % (sum(int(p['c_cap_height']['n']) for _, p in plates()), sum(int(p['c_cap_height']['n_fail']) for _, p in plates()), rng(caps)),
              '`test_waves_text_caps.gd`: every Label in the combat scene (instanced headless): font cap height of "H" x the node\'s scale at 1080p >= `cap_min_px` (card Labels at the hand scale)'))
    des = [r['dE'] for _, p in plates() for r in p['d_palette']['rows']]
    R.append(('rb d: palette dE76', FC['rb_checks']['p1_decide']['d_palette']['rule'], '>= %s' % num(T['de_min']),
              '%s pairs per plate; lowest dE76 %.1f' % (rng([p['d_palette']['n_pairs'] for _, p in plates()], '%d'), min(des)),
              '`test_combat_palette_de.gd`: the same pair groups computed in Lab from `CombatLookData`, the skins\' inks and the card types >= `de_min`'))
    e = [p['e_hand'] for _, p in plates()]
    R.append(('rb e: hand clearance', FC['rb_checks']['p1_decide']['e_hand']['rule'], '0 px',
              'hand under SEND IT / UNDO %d / %d px; lifted card over a sibling\'s cost hex / rules %d / %d px (%d pairs measured)' % (
                  max(int(x['hand_x_send_px']) for x in e), max(int(x['hand_x_undo_px']) for x in e),
                  sum(int(q['cost_px']) for x in e for q in x['lifted_vs_sibling']), sum(int(q['rules_px']) for x in e for q in x['lifted_vs_sibling']),
                  sum(len(x['lifted_vs_sibling']) for x in e)),
              '`test_waves_hand_layout.gd`: card rects (fan, lift, slot-0 shift) against the SEND IT / UNDO rects and each sibling\'s cost-hex and rules rects: 0 overlap'))
    s2 = FC['stage2_measures']
    R.append(('stage 2: hand margin, ticket glyphs', FC['stage2_rule'], 'as the rule',
              'hand margin %s px; ticket glyph ink height %s px, p90 L* %s' % (rng([v['hand_margin_px'] for v in s2.values()], '%d'),
                                                                          rng([g['ink_h'] for v in s2.values() for row in v['ticket_glyphs'] for g in row], '%d'),
                                                                          rng([g['p90_L'] for v in s2.values() for row in v['ticket_glyphs'] for g in row])),
              '`test_waves_hand_layout.gd` (lowest card pixel vs y 1080); `test_combat_look_values.gd` (ticket glyph colour = `k_type` on every ticket, glyph size from the ticket layout)'))
    hb = FC['hand_vs_board'].values()
    R.append(('hand vs board', FC['hand_rule'], 'as the rule', 'min hand radius %s px; %d px inside' % (rng([v['hand_min_r_px'] for v in hb]), sum(v['hand_px_inside_r455'] for v in hb)),
              '`test_waves_board_collisions.gd` (hand min radius)'))
    da = FC['draw_asserts'].values()
    R.append(('draw asserts', 'game-mark asserts from the draw log', 'all pass', '%d / %d' % (sum(v['passed'] for v in da), sum(v['total'] for v in da)), '`test_waves_board_draw_asserts.gd`'))
    R.append(('mark collisions, occlusion', 'marks x marks; marks x occluders', '0 px',
              '%d px; %d px' % (sum(v['total_px'] for v in FC['collisions_marks'].values()), sum(sum(v['pairs'].values()) for v in FC['occlusion'].values())),
              '`test_waves_board_collisions.gd`'))
    dsh = FC['dash_audit'].values()
    R.append(('dash and dot audit', FC['dash_audit_note'], '0', 'dashed calls %d, dotted calls %d, pixel dot runs %d' % (
        sum(v['dashed_line_calls'] for v in dsh), sum(v['dotted_mark_calls'] for v in dsh), sum(v['pixel_dot_runs'] for v in dsh)),
              '`test_waves_no_dashes.gd` (source grep and draw log); the pixel dot-run finder is a capture check'))
    cd = FC['cards']['type_colours']
    R.append(('card type plates', 'type word vs its plate', ', '.join('%s %s' % (k, v['text_rule']) for k, v in cd.items()),
              ', '.join('%s %s:1' % (k, v['text_vs_plate']) for k, v in cd.items()), '`test_combat_palette_de.gd` (WCAG ratio from the card type colours)'))
    f, b = FX, FX['resolve_beat']
    R.append(('effects', 'cap, overrides, layer, beat, flashes', '<= %d ms; 0 overrides; HUD layer only %s; beat < %d ms; <= 3 flashes/s' % (
        f['cap_ms'], ', '.join(f['hud_layer_effects']), b['limit_ms']),
              'longest %d ms; %d overrides; beat %d ms; flash %s' % (max(e['total_ms'] for e in f['effects']), len(f['per_effect_overrides']), b['total_ms'], json.dumps(b.get('flash'))),
              '`test_combat_fx_timings.gd`: 32 effects load; every total, phase end and reduce phase <= `cap_ms`; no override; only the three HUD-layer effects ask for the HUD slot; the sequenced beat ends before `limit_ms`; `FlashLimiter.stream_is_safe` on each effect and on the beat'))
    lo = [v['passes'] for per in f['loudness_order'].values() for v in per.values()]
    R.append(('effect loudness order', f['loudness_rule'], 'order holds', '%d of %d meters pass' % (sum(lo), len(lo)), 'capture check (13.2): the transient meter on 60 fps captures'))
    rm = [v['after']['L']['room']['mean'] for v in BC['plates'].values()]
    rp = [v['after']['L']['room']['p95'] for v in BC['plates'].values()]
    R.append(('room grade', BC['targets']['room_mean'], 'L* %s' % T['room_mean_L'], 'mean L* %s, p95 L* %s on %d rooms; all pass: %s' % (rng(rm), rng(rp), len(rm), BC['all_pass']),
              '`test_room_grade_data.gd`: `RoomGradeData` equals `backdrop/grade.json` (version, every room, every parameter); the L* gate is a capture check'))
    st = [v['final'] for v in FC['squint_tower_zone'].values()]
    R.append(('squint, tower zone (reported, not gated)', FC['squint_tower_zone_note'], 'reported', 'loud share %s %% over %d plates' % (rng([100 * v for v in st]), len(st)),
              'capture check, reported only (open question, section 14)'))
    pk = [FC['corp'][k] for k in FC['corp'] if k.startswith('pink_pct_enemy_zone')]
    tm = [FC['corp'][k] for k in FC['corp'] if k.startswith('tape_match_pct')]
    R.append(('corp: pink in the enemy zone, clock match (reported)', 'pink share in r 214-500; the clock pixels equal across skins', 'reported',
              'pink %s %%; clock match %s %%' % (rng(pk, '%.2f'), rng(tm)), 'capture check, reported'))
    return R


@block
def checks():
    out = ['Every check the art ran on the published plates, its rule (as `final/checks.json` states it), what it measured, and its '
           'GUT-test equivalent. A pixel-level check stays a capture check (13.2); its data-level half is the GUT test.', '',
           '| Check | Rule | Threshold | Measured on the plates | GUT equivalent |', '|---|---|---|---|---|']
    for r in check_rows():
        out.append('| %s |' % ' | '.join(str(x).replace('|', '/').replace('\n', ' ') for x in r))
    out += ['', 'All-pass flags (`final/checks.json` `all_pass`): %s.' % ', '.join('`%s` %s' % (k, v) for k, v in FC['all_pass'].items())]
    return '\n'.join(out)


# ------------------------------------------------------------------ mailbox
@block
def mailbox_numbers():
    f, b, k = FX, FX['resolve_beat'], SK['clock']
    st = [v['final'] for v in FC['squint_tower_zone'].values()]
    pk = [FC['corp'][x] for x in FC['corp'] if x.startswith('pink_pct_enemy_zone')]
    return '\n'.join([
        '- Effects: %d, every one at most %d ms (T2) with %d overrides, drawn under the HUD and the hand except %s.' % (
            f['count'], f['cap_ms'], len(f['per_effect_overrides']), ', '.join('`%s`' % x for x in f['hud_layer_effects'])),
        '- Resolve beat: %d ms against %d, skip on any input in %d ms; loudness order %s holds on every skin.' % (b['total_ms'], b['limit_ms'], b['skip_ms'], f['loudness_rule']),
        '- One gunmetal clock on every corp: fill %s, lip %s, groove %s; SCHEDULE %s on the live step only.' % (
            hl(k['gun_fill']['hex']), hl(k['gun_light']['hex']), hl(k['gun_groove']['hex']), k['schedule']['hex']),
        '- Corp skins: material plus corp hue on the rim, lip, crest and cell edges; neutral slate cell fills, `kind_gain` 1.0 everywhere; rooms %s.' % (
            ', '.join('%s %s' % kv for kv in GR['corp_room'].items())),
        '- Room grade %s; graded room mean L* %s.' % (GR['version'], rng([v['after']['L']['room']['mean'] for v in BC['plates'].values()])),
        '- Plate checks: %s all true; pink in the enemy zone %s %% and the tower-zone squint %s %% are reported, not gated.' % (
            ', '.join(FC['all_pass'].keys()), rng(pk, '%.2f'), rng([100 * v for v in st])),
        '- Card atlas: %s.' % ', '.join('`%s` %d x %d' % (n, v['size'][0], v['size'][1]) for n, v in CA['files'].items()),
    ])


TARGETS = {'GODOT_PORT_SPEC.md': ['files', 'tokens', 'time_grade', 'room', 'cells', 'clock', 'cards', 'unaffordable', 'atlas', 'skins', 'fx_counts',
                                  'eases', 'beat', 'loudness', 'checks', 'fx_appendix', 'skin_appendix', 'room_appendix', 'card_appendix'],
           'MAILBOX_DRAFT.md': ['mailbox_numbers']}
MARK = re.compile(r'(<!-- gen:(\w+) begin -->)(.*?)(<!-- gen:\2 end -->)', re.S)


def splice(text, names):
    found = [m.group(2) for m in MARK.finditer(text)]
    missing = [n for n in names if n not in found]
    extra = [n for n in found if n not in names]
    assert not missing and not extra and len(found) == len(set(found)), 'markers: missing %s, unknown %s, dup %s' % (missing, extra, found)
    return MARK.sub(lambda m: m.group(1) + '\n' + BLOCKS[m.group(2)]() + '\n' + m.group(4), text)


def main(write):
    os.makedirs(PREVIEW, exist_ok=True)
    for fn, names in TARGETS.items():
        p = LOCK + fn
        txt = open(p, encoding='utf-8').read()
        new = splice(txt, names)
        dst = p if write else PREVIEW + fn
        open(dst, 'w', encoding='utf-8', newline='\n').write(new)
        print(fn, '->', dst, len(txt.split('\n')), '->', len(new.split('\n')), 'lines')


if __name__ == '__main__':
    main('--write' in sys.argv[1:])
