"""fx_sheets.py [sheets] [strips] [timings] [bvb] [order] : family sheets, per-effect strips, timings_CDHL.json and fx_block_vs_break.png
from work/kf + work/flash (fx_build.py), on the rebuilt board (2026-11-03 rebuild as published in locked/final)."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import fx_cdhl as F
from fxk_lib import W, anton, mono, plex, PINK, HARM, GAIN, GOLD, INK, P_STOCK, T2_CAP_MS, CROSS_OK

OUT = 'D:/rc_scratch/combat_redesign/locked/round2/effects/out/'
os.makedirs(OUT + 'strips', exist_ok=True)
BG = (12, 12, 18)
TXT = (232, 236, 246)
MID = (150, 160, 178)
YEL = (255, 226, 0)
OKC = (140, 230, 160)
FAM = {'C': ('CORP', 'THE ENEMY CHANGES STATE', 'one clean vector scan line in the skin\'s own enamel ink (neutral ENAMEL, Solace celadon, Meridian rust; BOSS_GOLD for the ward), then one 4-frame flash on the new mark only; no slab, no texture; the quietest family', (200, 210, 226)),
       'D': ('DAMAGE', 'WE HURT THEM', 'player-owned comic hit frame: painted pink tracer, ink-keylined pink starburst with a white core (cell-sized), converging speed lines that stop at the tower rim, flat vector shards; kills in the cause colour', PINK),
       'H': ('HARM', 'THE ENEMY HURTS YOU', 'misregistered red print: X-only halftone flood (never round dots), black krackle with a 2 px red offset, red stencil X; the broken shield is the P plate on its own stock, in shards', HARM),
       'L': ('LIFE', 'YOU GAIN', 'the one soft glow: brush strokes, plus signs, a painted check, four-point sparkles; GAIN green, mint on the green REPAIR wedge, NET_CYAN for RAM; ranked with the state changes', GAIN),
       'P': ('PROTECT', '', '', P_STOCK)}
KIND_LABEL = {'damage': 'DAMAGE', 'kill': 'KILL', 'block': 'BLOCK', 'state': 'STATE', 'gain': 'GAIN (ranked with state)'}
ALL = F.FX + [F.SHIELD_BLOCK]


def fl(fid, sk):
    return json.load(open(W + 'flash/%s_%s.json' % (fid, sk)))


def order_table(skin='neutral'):
    """review 2.10: loudness (peak area x value, transient) per effect, sorted, with the tier rule damage > kill > block > state (gain with state)"""
    rows = []
    for fx in ALL:
        sk = skin if skin in fx['skins'] else 'neutral'
        f = fl(fx['id'], sk)['full']
        rows.append(dict(id=fx['id'], fam=fx['fam'], kind=fx['kind'], tier=('state' if fx['kind'] == 'gain' else fx['kind']), loud=f['loud_peak'],
                         at_ms=f['loud_peak_ms'], area=f['loud_peak_area_px'], mean_L=f['loud_peak_mean_L'], total=f['loud_total_peak'], skin=sk))
    rows.sort(key=lambda r: -r['loud'])
    for i, r in enumerate(rows):
        r['rank'] = i + 1
    tiers = ['damage', 'kill', 'block', 'state']
    chk = []
    ok = True
    for a, b in zip(tiers, tiers[1:]):
        lo = min(r['loud'] for r in rows if r['tier'] == a)
        hi = max(r['loud'] for r in rows if r['tier'] == b)
        lo_id = [r['id'] for r in rows if r['tier'] == a and r['loud'] == lo][0]
        hi_id = [r['id'] for r in rows if r['tier'] == b and r['loud'] == hi][0]
        chk.append(dict(upper=a, lower=b, upper_min=lo, upper_min_id=lo_id, lower_max=hi, lower_max_id=hi_id, ok=bool(lo > hi)))
        ok &= lo > hi
    return rows, chk, ok


def flash_line(fid, skins):
    parts = []
    worst = 0
    for sk in skins:
        f = fl(fid, sk)['full']
        w_ = max(f['max_flashes_per_s_footprint'], f['max_flashes_per_s_crop'])
        worst = max(worst, w_)
        parts.append('%s %d/s' % (sk[:3], w_))
    r = fl(fid, 'neutral')
    f = r['full']
    rd = r.get('reduce', {})
    s = 'FLASH (60 fps, measured): max %d flash/s (%s); footprint %d px = %d %% of crop; peak swing share %d %% up / %d %% down; mean-lum max step %.2f; reduce %d/s  ->  %s' % (
        worst, ', '.join(parts), f['footprint_px'], round(f['footprint_share'] * 100), round(f['peak_up_share_footprint'] * 100), round(f['peak_down_share_footprint'] * 100),
        f['mean_lum_max_step'], rd.get('max_flashes_per_s_footprint', 0), 'PASS (<= 3/s)' if worst <= 3 else 'FAIL')
    return s, worst


def loud_line(fx, ranks):
    vals = []
    for sk in fx['skins']:
        f = fl(fx['id'], sk)['full']
        vals.append('%s %.0f' % (sk[:3], f['loud_peak']))
    f = fl(fx['id'], 'neutral')['full']
    rk = ranks.get(fx['id'])
    return ('LOUDNESS (review 2.10, peak area x value of the transient, full-value px): %s; neutral peak at %d ms over %d px at mean L* %.0f; rank %s of %d; tier %s; '
            'total incl. the mark it leaves %.0f' % (', '.join(vals), f['loud_peak_ms'], f['loud_peak_area_px'], f['loud_peak_mean_L'], rk, len(ALL),
                                                     KIND_LABEL[fx['kind']], f['loud_total_peak']))


def layer_line(fx):
    hid = max(fl(fx['id'], sk)['full']['under_px_hidden_by_hud_max'] for sk in fx['skins'])
    cross = max(fl(fx['id'], sk)['full']['over_px_on_hud_max'] for sk in fx['skins'])
    settle = max((fl(fx['id'], sk)['full']['settles_ms'] or 0) for sk in fx['skins'])
    g = {}
    for sk in fx['skins']:
        for k, v in fl(fx['id'], sk)['full']['guard_px'].items():
            g[k] = max(g.get(k, 0), v)
    if fx['id'] in CROSS_OK:
        lay = 'LAYER: crosses the HUD (allowed, review 1.6): %d px drawn on the HUD at most' % cross
    else:
        lay = 'LAYER: under the HUD and the hand (ART_BIBLE 6.4, review 1.6): 0 px above the HUD (%d px of it sit under the HUD / hand and are hidden)' % hid
    lay += '; settles at %.0f ms (T2 cap %d ms)' % (settle, T2_CAP_MS)
    if fx['fam'] != 'L':
        lay += '; GAIN / FOCUS / lime px drawn: %d / %d / %d' % (g.get('GAIN', 0), g.get('FOCUS', 0), g.get('LIME', 0))
    return lay, settle


def wrap(d, text, fnt, width):
    words = text.split(' ')
    lines, cur = [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=fnt) > width and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def block(fx, page_w, ranks, cell_w=None, big=False):
    """one effect block: header text + a keyframe row (+ reduce) per skin"""
    fid = fx['id']
    fam = FAM[fx['fam']]
    bw, bh = fx['box'][2] - fx['box'][0], fx['box'][3] - fx['box'][1]
    n = len(fx['keys']) + 1
    margin, lab, gap = 24, 34, 8
    avail = page_w - 2 * margin - lab
    per_row = n if bw / bh <= 2.2 else 3
    cw = cell_w or int((avail - gap * (per_row - 1)) / per_row)
    sc = cw / bw
    ch = int(bh * sc)
    rows_per_skin = math.ceil(n / per_row)
    page_w = max(page_w, 2 * margin + lab + per_row * cw + (per_row - 1) * gap)
    tmp = Image.new('RGB', (page_w, 10))
    d = ImageDraw.Draw(tmp)
    fs = 18 if big else 16
    fl_, worst = flash_line(fid, fx['skins'])
    i_, h_, o_, ez = fx['iho']
    lay_, settle = layer_line(fx)
    timing = 'TIMING: in %d ms, hold %d ms, out %d ms (total %d ms, T2 cap %d ms, no override); %s. Phases: %s' % (
        i_, h_, o_, fx['timing']['total'], T2_CAP_MS, ez, ', '.join('%s %d-%d' % (k, v[0], v[1]) for k, v in fx['timing']['phases'].items()))
    texts = [('STILL: ' + fx['still'], TXT), (timing, MID), (fl_, OKC if worst <= 3 else HARM), (loud_line(fx, ranks), (180, 200, 255)),
             (lay_, OKC if settle <= T2_CAP_MS else HARM), ('REDUCE MOTION: ' + fx['reduce_note'], YEL),
             ('STYLE MUST KEEP: ' + fx['keep'], (255, 214, 120)), ('SOURCE: ' + fx['source'], MID)]
    lines = []
    for t, c in texts:
        for ln in wrap(d, t, plex(fs), page_w - 2 * margin):
            lines.append((ln, c))
    head_h = 46 + len(lines) * (fs + 5) + 10
    CAPH = 44                                   # two caption lines under each keyframe (no caption is cut)
    rows_h = len(fx['skins']) * rows_per_skin * (ch + CAPH + gap)
    H = head_h + rows_h + 14
    im = Image.new('RGB', (page_w, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([margin - 14, 8, margin - 8, 40], fill=fam[3])
    d.text((margin, 10), fid, font=mono(24), fill=TXT)
    x = margin + d.textlength(fid, font=mono(24)) + 18
    d.text((x, 8), fx['title'].upper(), font=anton(28), fill=fam[3])
    tag = '%s  |  FX-%s %s  |  %s  |  %s' % (fx['tier'].upper(), fx['fam'], fam[0], fx['scope'], ' / '.join(s.upper() for s in fx['skins']))
    if fx['variant_of']:
        tag = 'VARIANT OF %s  |  ' % fx['variant_of'] + tag
    d.text((page_w - margin, 14), tag, font=mono(15), fill=MID, anchor='ra')
    y = 46
    for ln, c in lines:
        d.text((margin, y), ln, font=plex(fs), fill=c)
        y += fs + 5
    y = head_h
    for sk in fx['skins']:
        for rr in range(rows_per_skin):
            yy = y + rr * (ch + CAPH + gap)
            if rr == 0:
                lbl = Image.new('RGBA', (ch, lab - 6), (0, 0, 0, 0))
                ImageDraw.Draw(lbl).text((ch / 2, 2), sk.upper(), font=mono(16), fill=(200, 206, 220), anchor='ma')
                im.paste(lbl.rotate(90, expand=True), (margin, yy), lbl.rotate(90, expand=True))
            for k in range(per_row):
                idx = rr * per_row + k
                if idx >= n:
                    break
                xx = margin + lab + k * (cw + gap)
                if idx < n - 1:
                    f = Image.open(W + 'kf/%s_%s_%d.png' % (fid, sk, idx))
                    cap = '%d  %d ms  %s' % (idx + 1, fx['keys'][idx][0], fx['keys'][idx][1])
                    col = (190, 196, 210)
                else:
                    f = Image.open(W + 'kf/%s_%s_r.png' % (fid, sk))
                    cap = 'REDUCE MOTION still (%d ms)' % fx['keys'][fx.get('peak', 2)][0]
                    col = YEL
                im.paste(f.resize((cw, ch), Image.LANCZOS), (xx, yy))
                if idx == n - 1:
                    d.rectangle([xx - 2, yy - 2, xx + cw + 1, yy + ch + 1], outline=YEL, width=2)
                capf = mono(14 if not big else 15)
                cl = wrap(d, cap, capf, cw - 4)
                if len(cl) > 2:
                    capf = mono(12)
                    cl = wrap(d, cap, capf, cw - 4)
                assert len(cl) <= 2, (fid, cap)
                for j, ln in enumerate(cl):
                    d.text((xx + 2, yy + ch + 4 + j * 18), ln, font=capf, fill=col)
        y += rows_per_skin * (ch + CAPH + gap)
    d.line([(margin, H - 4), (page_w - margin, H - 4)], fill=(40, 42, 54), width=1)
    return im


def ranks_of():
    rows, chk, ok = order_table('neutral')
    return {r['id']: r['rank'] for r in rows}


PENCIL_INSET = {}
PEN_BOX = (245, 632, 566, 872)       # plate px: the Trigger route's pencil (trig_yel.png alpha bbox + 10), fx_trigger_hit's box starts at (240, 600)


def pen_measure(crop, box):
    """round 2 (C1): the board's own check f (rb_checks_r2.check_pencil) on a 1x crop placed back at its plate position; the pencil class is
    the pencil layer's own coverage (trig_yel.png alpha >= 128), as rb_pencil records it for the board"""
    sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/corp/src')
    import rb_checks_r2 as RC2
    import rb_tokens as RT_
    x0, y0, x1, y1 = box
    rgb = np.zeros((1080, 1920, 3), np.float64)
    rgb[y0:y1, x0:x1] = np.asarray(crop.convert('RGB'), np.float64)
    ty = np.asarray(Image.open(W + 'trig_yel.png').convert('RGBA'))
    m = np.zeros((1080, 1920), bool)
    m[y0:y1, x0:x1] = ty[y0:y1, x0:x1, 3] >= 128
    r = RC2.check_pencil(rgb, RT_.lum(rgb), {'pen_L6_all': m})
    return r


def pencil_inset(page_w=1920):
    """round 2 (C1): the effects' pencil at 1x on the D sheet: fx_trigger_hit at 0 ms (the anticipate frame: the route as the p2 plate draws
    it, rb_pencil 7 px wax + 3 px ink edge + wax grain), 1x and 2x; the numbers are the board's check f on the 1x crop"""
    k0 = Image.open(W + 'kf/fx_trigger_hit_neutral_0.png').convert('RGB')
    bx0, by0 = F.BYID['fx_trigger_hit']['box'][:2]
    x0, y0, x1, y1 = PEN_BOX
    c1 = k0.crop((x0 - bx0, y0 - by0, x1 - bx0, y1 - by0))
    r = pen_measure(c1, PEN_BOX)
    row = r['rows'][0] if r['rows'] else {}
    tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    txt = ('C1 PENCIL AT 1x (round 2): the effects draw the board\'s one pencil (corp/src rb_pencil: 7 px PLAN wax, a 3 px ink edge each side, wax grain), '
           'the same pixels as the published p2 plate (max 0 / 255 on the pencil\'s opaque px).  Left: fx_trigger_hit at 0 ms at 1x; right: the same at 2x.  '
           'Measured on this 1x crop with the board\'s check f: whole stroke %s px, wax %s px, ink %s px per side, grain L* std %s, wax L* median %s -> %s.  '
           'fx_commit starts on the p2 plate itself (its pencil is that plate\'s, check f in final/checks.json).  No effect draws FOCUS.'
           % (row.get('stroke_w'), row.get('wax_w'), row.get('ink_per_side'), row.get('grain_L_std'), row.get('wax_L_median'), 'PASS' if r['pass_'] else 'FAIL'))
    lines = wrap(tmp, txt, plex(17), page_w - 48)
    ty = 50 + 24 * len(lines) + 8
    w, h = c1.size
    im = Image.new('RGB', (page_w, ty + 2 * h + 24), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([10, 10, 16, 40], fill=YEL)
    d.text((24, 8), 'C1 PENCIL AT 1x', font=anton(30), fill=YEL)
    for j, ln in enumerate(lines):
        d.text((24, 50 + 24 * j), ln, font=plex(17), fill=TXT)
    im.paste(c1, (24, ty))
    im.paste(c1.resize((2 * w, 2 * h), Image.NEAREST), (24 + w + 24, ty))
    d.line([(24, im.height - 4), (page_w - 24, im.height - 4)], fill=(40, 42, 54), width=1)
    PENCIL_INSET.clear()
    PENCIL_INSET.update(plate_box=list(PEN_BOX), inset_xy_1x=[24, ty], size=[w, h], measured_on_frame=r)
    return im


def family_sheet(letter, fname, ranks):
    fam = FAM[letter]
    fxs = [f for f in F.FX if f['fam'] == letter]
    page_w = 1920
    blocks = [block(f, page_w, ranks) for f in fxs]
    tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    sub = wrap(tmp, '%s  //  %s' % (fam[1], fam[2]), mono(15), page_w - 44 - 24)      # the family line wraps (it ran off the page)
    hdr = 92 + 20 * len(sub) + 12
    H = hdr + sum(b.height for b in blocks) + 20
    im = Image.new('RGB', (page_w, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([18, 18, 30, hdr - 20], fill=fam[3])
    d.text((44, 10), 'FX-%s %s' % (letter, fam[0]), font=anton(60), fill=TXT)
    for j, ln in enumerate(sub):
        d.text((44, 88 + 20 * j), ln, font=mono(15), fill=MID)
    d.text((page_w - 24, 16), 'combat redesign / round-2 board (2026-11-04, locked/final) / effects C D H L / %d effects' % len(fxs), font=mono(16), fill=MID, anchor='ra')
    d.text((page_w - 24, 40), 'every frame composited under the HUD and the hand (hp_through and refund may cross); every effect 600 ms or less', font=mono(14), fill=MID, anchor='ra')
    d.text((page_w - 24, 60), 'loudness order damage > kill > block > state (measured, see the LOUDNESS line and NOTES_CDHL.md)', font=mono(14), fill=MID, anchor='ra')
    ins = pencil_inset() if letter == 'D' else None
    if ins is not None:
        H += ins.height
        im2 = Image.new('RGB', (page_w, H), BG)
        im2.paste(im.crop((0, 0, page_w, hdr)), (0, 0))
        im = im2
        d = ImageDraw.Draw(im)
    y = hdr
    if ins is not None:
        im.paste(ins, (0, y))
        y += ins.height
    for b in blocks:
        im.paste(b, (0, y))
        y += b.height
    im.save(OUT + fname, optimize=True)
    if ins is not None:
        json.dump(dict(PENCIL_INSET, sheet=fname, y0=hdr), open(W + 'pencil_inset.json', 'w'), indent=1)
    print('sheet', fname, im.size, os.path.getsize(OUT + fname) // 1024, 'KB', flush=True)


def strip(fx, ranks):
    bw = fx['box'][2] - fx['box'][0]
    cw = min(520, bw) if bw / (fx['box'][3] - fx['box'][1]) <= 1.55 else min(900, bw)
    b = block(fx, 1920, ranks, cell_w=cw, big=True)
    p = OUT + 'strips/%s.jpg' % fx['id']
    q = 90
    while True:
        b.save(p, quality=q, optimize=True)
        if os.path.getsize(p) < 1900 * 1024 or q < 60:
            break
        q -= 6
    print('strip', fx['id'], b.size, os.path.getsize(p) // 1024, 'KB', 'q', q, flush=True)


KEEP = {'fx_trigger_hit': dict(in_sequence='In the resolve beat fx_commit has already burned the pencil route and Xs into paint, so the sequenced fx_trigger_hit draws only the hit frames and speed lines (same clock: s3 at 120, s4 at 240); the pencil burn plays only when the effect runs without a commit before it (O-30, retimed 2026-11-03 rebuild; round 2: the pencil is the one board pencil, C1).')}


def timings():
    R2K = 'round2_2026_11_04'
    out = dict(_doc='Effects C/D/H/L (+ P shield_block, comparison only) on the round-2 board (2026-11-04, locked/final; R1_REREVIEW build order step 4). Times in ms at 60 fps; phases are [start, end] ms; '
                    'flash, loudness, settle, layer and guard are measured per skin on the 60 fps frames the published keyframes are cut from (see NOTES_CDHL.md "2026-11-04 round 2", method). '
                    'The key round2_2026_11_04 replaces rebuild_2026_11_03 (round 1, in git history).',
               round2_2026_11_04=dict(
                   board='locked/final as published 2026-11-04 round 2 (C1 pencil, C2 FOCUS, C3 / C4 bright marks, C5 tickets, C6 lift, C8 HUD rows, C16 Solace teal); bases rendered from corp/src with the published plates\' own hooks',
                   t2_cap_ms=T2_CAP_MS, per_effect_overrides=[],
                   layer='every effect draws under the HUD and the hand (f1_render.SPLIT below / above); only %s may draw above the HUD (review 1.6)' % ', '.join(CROSS_OK),
                   loudness_metric='peak over the 60 fps frames of sum(L*/100) over the pixels where the frame differs (dE76 > 5) from both the frame without the effect and the settled frame (the transient); unit full-value px',
                   pencil='C1: fx_trigger_hit draws the board\'s one pencil (rb_pencil via a_plan.trigger_path, the p2 plate\'s pixels) and burns it front to back, sector 3 then sector 4, into the paint; no other pencil is drawn',
                   focus='C2: no C/D/H/L effect draws FOCUS (guard px within dE76 15 of #D4FF00: 0 on every frame)',
                   hud_rows='C8: hp_through finds the YOU strip at its round-2 rows (y 132-152); refund lands on the round-2 RAM row (coin y 645.5) and its REFUND tab (96 px)',
                   p_stock=dict(hex='#%02X%02X%02X' % P_STOCK, token='rb_tokens.P_STOCK (C15)', why='review 3.10: the FX-P plate on its own stock, a pink-tinted paper, not the card bone PAPER #F2EEE4')),
               effects={})
    if os.path.exists(W + 'pencil_inset.json'):
        out[R2K]['pencil_inset_D_sheet'] = json.load(open(W + 'pencil_inset.json'))
    for sk in ('neutral', 'solace', 'meridian'):
        rows, chk, ok = order_table(sk)
        out[R2K]['loudness_order_' + sk] = dict(rule='damage > kill > block > state (gain ranks with state)', passes=ok, tiers=chk,
                                                                 rows=[dict(rank=r['rank'], id=r['id'], kind=r['kind'], loud=r['loud'], at_ms=r['at_ms'], area_px=r['area'],
                                                                            mean_L=r['mean_L'], total=r['total'], skin=r['skin']) for r in rows])
    for fx in ALL:
        fid = fx['id']
        i_, h_, o_, ez = fx['iho']
        flr, meas = {}, {}
        for sk in fx['skins']:
            r = fl(fid, sk)
            flr[sk] = {k: v for k, v in r['full'].items() if k not in ('mean_series_footprint', 't_ms', 'loud_series') and not k.startswith('loud') and k not in ('settles_ms', 'under_px_hidden_by_hud_max', 'over_px_on_hud_max', 'guard_px')}
            if 'reduce' in r:
                flr[sk + '_reduce'] = {k: v for k, v in r['reduce'].items() if k not in ('mean_series_footprint', 't_ms')}
            f = r['full']
            meas[sk] = dict(loud_peak=f['loud_peak'], loud_peak_ms=f['loud_peak_ms'], loud_peak_area_px=f['loud_peak_area_px'], loud_peak_mean_L=f['loud_peak_mean_L'],
                            loud_total_peak=f['loud_total_peak'], loud_total_peak_ms=f['loud_total_peak_ms'],
                            settles_ms=f['settles_ms'], under_px_hidden_by_hud_max=f['under_px_hidden_by_hud_max'], over_px_on_hud_max=f['over_px_on_hud_max'], guard_px=f['guard_px'])
        e = dict(family=fx['fam'], title=fx['title'], variant_of=fx['variant_of'], tier=fx['tier'], kind=fx['kind'], scope=fx['scope'], skins=list(fx['skins']),
                 total_ms=fx['timing']['total'], in_ms=i_, hold_ms=h_, out_ms=o_, easing_summary=ez, easing=fx['timing']['easing'],
                 phases=fx['timing']['phases'], keyframes=[dict(ms=t, caption=c) for t, c in fx['keys']], reduce_motion=fx['reduce_note'],
                 source=fx['source'], board_crop=list(fx['box']), base=dict(pre=fx['pre'], post=fx['post']),
                 layer='above the HUD (allowed)' if fid in CROSS_OK else 'under the HUD and the hand', measured=meas, flash=flr)
        e.update(KEEP.get(fid, {}))
        out['effects'][fid] = e
    json.dump(out, open(OUT + 'timings_CDHL.json', 'w'), indent=1)
    print('timings ok', flush=True)


def block_vs_break(ranks):
    b, k = F.SHIELD_BLOCK, F.BYID['fx_shield_break']
    pb = Image.open(W + 'kf/fx_shield_block_neutral_2.png')
    pk = Image.open(W + 'kf/fx_shield_break_neutral_2.png')
    sc = 2.0
    cw, ch = int(pb.width * sc), int(pb.height * sc)
    page_w = 1920
    tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    desc = wrap(tmp, 'Same slice (sector 1 SHIELD), same plate on its own P stock (pink-tinted paper #%02X%02X%02X, review 3.10; not the card bone), peak frame, colour and luma.  '
                     'Block = ONE intact plate, P-stock spark ticks (the real P block\'s sparks; round 1 threw white ones here), no red.  Break = the plate in 5 shards, red X-halftone flood, black krackle, the wedge ends dark.  '
                     'Block is P protect (drawn here only for the comparison; the real block is on fx_P_protect.png). Break is H harm.  '
                     'Both under the HUD and the hand, both 600 ms or less.' % P_STOCK, plex(17), page_w - 48)
    top = 80 + 24 * len(desc) + 10
    im = Image.new('RGB', (page_w, top + ch + 44), BG)
    d = ImageDraw.Draw(im)
    d.text((24, 10), 'BLOCK vs BREAK, on the round-2 board', font=anton(52), fill=TXT)
    for j, ln in enumerate(desc):
        d.text((24, 78 + 24 * j), ln, font=plex(17), fill=MID)
    x = 24
    for lab_, f, col, g_ in (('SHIELD BLOCK  (P)  %d ms' % b['keys'][2][0], pb, P_STOCK, False), ('SHIELD BREAK  (H)  %d ms' % k['keys'][2][0], pk, HARM, False),
                             ('block, luma', pb, MID, True), ('break, luma', pk, MID, True)):
        big = (f.convert('L').convert('RGB') if g_ else f).resize((cw, ch), Image.LANCZOS)     # all four panels the same size
        im.paste(big, (x, top))
        d.text((x, top + ch + 8), lab_, font=mono(20 if not g_ else 16), fill=col)
        x += cw + 16
    assert x - 16 <= page_w - 24, x
    sb = block(b, page_w, ranks)
    sk = block(k, page_w, ranks)
    H = im.height + sb.height + sk.height + 10
    out = Image.new('RGB', (page_w, H), BG)
    out.paste(im, (0, 0))
    out.paste(sb, (0, im.height))
    out.paste(sk, (0, im.height + sb.height))
    out.save(OUT + 'fx_block_vs_break.png', optimize=True)
    print('block_vs_break', out.size, os.path.getsize(OUT + 'fx_block_vs_break.png') // 1024, 'KB', flush=True)


def print_order():
    for sk in ('neutral', 'solace', 'meridian'):
        rows, chk, ok = order_table(sk)
        print('==== loudness order', sk, 'PASS' if ok else 'FAIL')
        for r in rows:
            print('%2d  %8.0f  %-22s %-7s @%4.0f ms  area %6d  mean L* %5.1f  total %6.0f  (%s)' % (r['rank'], r['loud'], r['id'], r['kind'], r['at_ms'], r['area'], r['mean_L'], r['total'], r['skin']))
        for c in chk:
            print('   %s min %.0f (%s) > %s max %.0f (%s): %s' % (c['upper'], c['upper_min'], c['upper_min_id'], c['lower'], c['lower_max'], c['lower_max_id'], c['ok']))


if __name__ == '__main__':
    what = sys.argv[1:] or ['all']
    ranks = ranks_of()
    if 'all' in what or 'order' in what:
        print_order()
    if 'all' in what or 'sheets' in what:
        for L_, nm in (('C', 'fx_C_corp.png'), ('D', 'fx_D_damage.png'), ('H', 'fx_H_harm.png'), ('L', 'fx_L_life.png')):
            family_sheet(L_, nm, ranks)
    if 'all' in what or 'strips' in what:
        for fx in F.FX:          # shield_block (P) belongs to the M/P/S/T designer; it appears only inside fx_block_vs_break.png
            strip(fx, ranks)
    if 'all' in what or 'timings' in what:
        timings()
    if 'all' in what or 'bvb' in what:
        block_vs_break(ranks)
