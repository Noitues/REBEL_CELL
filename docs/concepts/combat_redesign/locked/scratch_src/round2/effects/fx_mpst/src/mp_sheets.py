"""mp_sheets.py: the family sheets fx_M_motion.png, fx_P_protect.png, fx_S_system.png, fx_T_commit.png and timings_MPST.json
(2026-11-03 rebuild) from work/res_<id>_<skin>.json and the strips (mp_run.py).  Optional: work/loud_order.json (mp_order.py)."""
import sys, os, json, textwrap
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import mp_eff as E
from mp_lib import *

SW = 2000
BG = (12, 12, 18)
_bvf = 'D:/rc_scratch/combat_redesign/locked/round2/effects/work/bases_vs_final.json'      # tools/share_bases.py
if os.path.exists(_bvf):
    _b = json.load(open(_bvf))
    BASE_MATCH = 'stock bases vs the published plates: max %d / 255, %d px over 8' % (max(v['max'] for v in _b.values()), sum(v['px_over_8'] for v in _b.values()))
else:
    BASE_MATCH = 'stock bases vs the published plates: not measured'
PSTK = P_STOCK
FAM = {
    'M': ('FX-M MOTION', 'motion', PINK,
          'THINGS MOVE // the eased move itself, plus one arrow stub that runs ahead of the mover',
          ['Material: the thing that moves is the generator\'s own cell, ring or tower, moved with easeInOut and a small overshoot. The arrow is an ink-cased 3 px stroke with an open 11 px V head; on the spin, twist, shove, rings step and Hold it is a stub (60 / 30 / 30 / 32 / 22 deg, mp_eff.ARROW_STUB) that runs ahead of the mover and is eaten when it arrives; the pull (88 px, ring +2 to ring +1) and the bump (22 deg, up to the occupied cell) keep their whole arrow. No echoes (review 2.10, 2026-11-03: on the shared gated meter the echo copies were the loudest light of every motion effect).',
           'Who moves it decides the colour (VISUAL_PLAN E): CELL_PINK = the Cell\'s card at resolve (pencil yellow is the hover / preview form only); SCHEDULE orange #FF8C1A = the clock (rings step, Hold\'s slide), with a lighter core line; the Hold stamp is the clock\'s gunmetal #6E7580 with the #969EAA lip. A wave entering is the enemy: the feed arrow is neutral ENAMEL (the queue is K) and the corp hue is only on the scan line that draws the new cell edges (DR-6: neutral ENAMEL, Solace teal #4FA6A2 (round 2, C16: it was leaf green #96FF46), Meridian #D88A4E).',
           'Layer (review 1.6): every M effect draws on the board, under the HUD and the hand.']),
    'P': ('FX-P PROTECT', 'protect', PSTK,
          'YOUR DEFENCE HOLDS // a plate of its own pink-tinted paper stock slams on: ink key line, rivets, fibre grain, hard offset shadow, no glow',
          ['Material (review 3.10): the P stock #F6C8DE, a pink-tinted paper (L* 85.1, nearest token K_TYPE at dE76 20.4), never the card bone; +-5 % fibre grain, a 3.4 px ink key line, ink rivets with a stock-shade head #D696B8, a hard offset shadow (3, 5) at 55 % ink in full motion. Sparks are P-stock paper ticks, never white and never a starburst (that is D); never red on the plate (that is H). The same stock is the shield break\'s shards on the C/D/H/L sheet.',
           'Review 2.10: a block sits under every kill and hit and over every state change, so the plate is small (shield r 186-204 x 26 deg on the trim band, clear of the icon and the pips), the brace is four clamp brackets on the wedge corners, and the flat wedge tint and the SOAK wash are retired.',
           'Layer (review 1.6): on the board, under the HUD and the hand.']),
    'S': ('FX-S SYSTEM', 'system', VIOLET,
          'TRACE // stepped violet glitch bands, 6 px shears, R/B split, scanlines',
          ['Material: one horizontal band 4-7 px tall per 33 ms step shears 6 px left or right, the red and blue channels split 3 px, a 35 % violet tint and dark scanlines on every second row; never smooth, a new row every step. Then the pip pops in stepped scales (1.45, 1.2, 1.0) and settles as the HUD\'s own lit pip.',
           'Violet #A03CFF means Trace only. fx_trace_add is the one M/P/S/T effect allowed to cross the HUD and the hand (review 1.6: hp_through, refund and trace_add).']),
    'T': ('FX-T COMMIT', 'commit', PINK,
          'PLAN BECOMES PAINT // pencil marks burn into pink paint along the path',
          ['Material: each pencil plan mark (round 2, C1: the board\'s one pencil, 7 px PLAN wax with a 3 px ink edge and wax grain, as the p2 plate draws it) turns into the generator\'s own pink resolve mark along its length, in geodesic order from the route start, behind a thin white-hot edge (1.8 % of the route length, 60 % white; it was 3.5 % and 75 %, louder than every block); a pink ping rings the route end; then the rest of the board, the HUD and the hand step from preview to resolve over 200 ms.',
           'Both ends are the generator\'s plates (p2 and p3 of each skin); the effect is only the path between them, drawn on the board under the HUD and the hand. After it no yellow is left.'])}


def wrap(d, xy, s, f, fill, width_px):
    x, y = xy
    cw = f.getlength('n')
    n = max(20, int(width_px / cw))
    for line in textwrap.wrap(s, n):
        d.text((x, y), line, font=f, fill=fill)
        y += int(f.size * 1.32)
    return y


def fam_col(spec):
    if spec['id'] in ('fx_rings_step', 'fx_hold'):
        return SCHED
    return {'M': PINK, 'P': PSTK, 'S': VIOLET, 'T': PINK}[spec['fam']]


def gantt(spec, w=900):
    ph = spec['timing']['phases']
    tot = E.CAP_MS
    rph = spec['reduce_phases']
    f = font('mono', 13)
    fe = font('mono', 12)
    x0, x1 = 340, w - 20
    ncol = int((x0 - 16) / f.getlength('n'))
    rows = [(textwrap.wrap(nm, ncol), a_, b_, e_, False) for nm, a_, b_, e_ in ph] + [(['REDUCE MOTION'], None, None, None, True)] +            [(textwrap.wrap(nm, ncol), a_, b_, e_, True) for nm, a_, b_, e_ in rph]
    rhs = [max(22, 15 * len(r[0]) + 7) for r in rows]
    h = 30 + sum(rhs) + 26
    im = Image.new('RGB', (w, h), (20, 20, 28))
    d = ImageDraw.Draw(im)
    sx = lambda t: x0 + (x1 - x0) * t / tot
    for t in range(0, tot + 1, 100):
        d.line([(sx(t), 22), (sx(t), h - 6)], fill=(46, 46, 60), width=1)
        d.text((sx(t) - 10, 4), '%d' % t, font=f, fill=(150, 150, 170))
    d.line([(sx(tot), 22), (sx(tot), h - 6)], fill=(255, 90, 80), width=2)
    d.text((sx(tot) - 120, h - 20), 'T2 cap 600 ms', font=fe, fill=(255, 90, 80))
    col = fam_col(spec)
    y = 30
    for (lines, a_, b_, e_, red), rh in zip(rows, rhs):
        for k, ln in enumerate(lines):
            d.text((8, y + 2 + 15 * k), ln, font=f, fill=(255, 214, 0) if red else (220, 220, 232))
        if a_ is not None:
            ym = y + rh / 2
            if red:
                d.rectangle([sx(a_), ym - 4, max(sx(a_) + 2, sx(b_)), ym + 4], fill=(150, 150, 160))
            else:
                d.rectangle([sx(a_), ym - 7, max(sx(a_) + 2, sx(b_)), ym + 7], fill=col)
                el = fe.getlength(e_)
                ex = sx(b_) + 6 if sx(b_) + 6 + el <= x1 - 4 else sx(a_) - 6 - el
                if ex < x0:
                    ex = None
                if ex is not None:
                    d.text((ex, ym - 8), e_, font=fe, fill=(170, 176, 196))
        y += rh
    return im


def flash_panel(results, w=900):
    h = 30 + 108 * len(results)
    im = Image.new('RGB', (w, h), (20, 20, 28))
    d = ImageDraw.Draw(im)
    f = font('mono', 13)
    d.text((8, 6), 'FLASH CHECK 60 fps per skin (curve: mean luminance of the footprint; full pink, reduce grey) + LOUDNESS', font=f, fill=(220, 220, 232))
    for i, r in enumerate(results):
        y = 30 + i * 108
        fc, fr = r['flash'], r['flash_reduce']
        g = r['loud'].get('gated', {})
        d.text((8, y), r['skin'].upper(), font=font('anton', 18), fill=(255, 214, 0))
        txt = ['footprint %d px, %d frames' % (fc['footprint_px'], fc['frames']),
               'full: %d flash(es), max %d / s, area swing up %.0f %% down %.0f %%' % (fc['flashes'], fc['max_flashes_per_s'], 100 * fc['max_area_swing_up'], 100 * fc['max_area_swing_down']),
               'reduce: %d flash(es), max %d / s' % (fr['flashes'], fr['max_flashes_per_s']),
               'loudness (gated, shared): %.0f at %.0f ms (%d px)' % (g.get('peak', 0), g.get('t_ms', 0), g.get('area_px', 0)),
               'brighter-only: %.0f (%d px, mean L* %.0f)' % (r['loud']['av'], r['loud']['area_px'], r['loud']['mean_L']),
               'PASS (<= 3 / s)' if fc['passed'] and fr['passed'] else 'FAIL']
        for k, s_ in enumerate(txt):
            d.text((110, y + k * 16), s_, font=f, fill=(120, 230, 140) if s_.startswith('PASS') else ((255, 90, 80) if s_ == 'FAIL' else (200, 204, 220)))
        cx0, cx1, cy0, cy1 = 560, w - 12, y + 4, y + 96
        d.rectangle([cx0, cy0, cx1, cy1], outline=(60, 60, 76))
        allc = np.array(fc['mean_curve'] + fr['mean_curve'])
        lo, hi = allc.min(), allc.max()
        if hi - lo < 0.02:
            mid = (hi + lo) / 2
            lo, hi = mid - 0.01, mid + 0.01
        for curve, col in ((fr['mean_curve'], (150, 150, 160)), (fc['mean_curve'], PINK)):
            c = np.array(curve)
            pts = [(cx0 + (cx1 - cx0) * j / max(1, len(c) - 1), cy1 - 4 - (cy1 - cy0 - 8) * (v - lo) / (hi - lo)) for j, v in enumerate(c)]
            d.line(pts, fill=col, width=2)
        for fr_ in fc['flash_frames']:
            xx = cx0 + (cx1 - cx0) * fr_ / max(1, len(fc['mean_curve']) - 1)
            d.line([(xx, cy0), (xx, cy1)], fill=(255, 214, 0), width=1)
    return im


def fit(im, w):
    if im.width <= w:
        return im
    return im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)


def main():
    timings = {}
    order = json.load(open(ME + 'work/loud_order.json')) if os.path.exists(ME + 'work/loud_order.json') else None
    for F, (name, word, col, tag, rules) in FAM.items():
        specs = [s for s in E.FX.values() if s['fam'] == F]
        blocks = []
        for s in specs:
            res = []
            for sk in s['skins']:
                fp = ME + 'work/res_%s_%s.json' % (s['id'], sk)
                if not os.path.exists(fp):
                    raise SystemExit('missing ' + fp)
                res.append(json.load(open(fp)))
            timings[s['id']] = dict(
                family=F, title=s['title'], tier=s['tier'], total_ms=s['timing']['total'], cap_ms=E.CAP_MS,
                phases=[dict(name=p[0], start_ms=p[1], end_ms=p[2], easing=p[3]) for p in s['timing']['phases']],
                reduce_phases=[dict(name=p[0], start_ms=p[1], end_ms=p[2], easing=p[3]) for p in s['reduce_phases']],
                reduce_total_ms=max(p[2] for p in s['reduce_phases']),
                keyframes_ms=[k[0] for k in s['keys']], skins=s['skins'], reduce_motion=s['reduce_note'], layer='over the HUD and the hand (allowed, review 1.6)' if s['id'] == 'fx_trace_add' else 'board: under the HUD and the hand (review 1.6)',
                flash_check={r['skin']: dict(full=dict((k, r['flash'][k]) for k in ('footprint_px', 'frames', 'flashes', 'flash_frames', 'max_flashes_per_s', 'max_area_swing_up', 'max_area_swing_down', 'passed')),
                                             reduce=dict((k, r['flash_reduce'][k]) for k in ('flashes', 'max_flashes_per_s', 'passed'))) for r in res},
                loudness={r['skin']: dict(gated_peak=r['loud']['gated']['peak'], gated_area_px=r['loud']['gated']['area_px'], gated_t_ms=r['loud']['gated']['t_ms'],
                                          brighter_only_peak=r['loud']['av'], brighter_only_area_px=r['loud']['area_px'], brighter_only_mean_L=r['loud']['mean_L']) for r in res},
                strips={r['skin']: 'strips/' + os.path.basename(r['strip']) for r in res})
            g = gantt(s)
            fpn = flash_panel(res)
            tmp = Image.new('RGB', (SW, 4000), BG)
            d = ImageDraw.Draw(tmp)
            d.rectangle([0, 0, 8, 60], fill=fam_col(s))
            d.text((22, 0), s['id'], font=font('mono', 30), fill=(255, 255, 255))
            d.text((22 + font('mono', 30).getlength(s['id']) + 20, 4), s['title'].upper(), font=font('anton', 30), fill=fam_col(s))
            d.text((SW - 560, 10), '%s  |  %s  |  %d ms' % (name, ', '.join(s['skins']), s['timing']['total']), font=font('mono', 16), fill=(170, 176, 196))
            y = 50
            y = wrap(d, (22, y), 'STILL: ' + s['still'], font('plex', 19), (232, 232, 240), SW - 980)
            y = wrap(d, (22, y + 4), 'SOURCE: ' + s['src'], font('plex', 17), (160, 166, 186), SW - 980)
            y = wrap(d, (22, y + 4), 'STYLE MUST KEEP: ' + s['keep'], font('plex', 18), (255, 214, 0), SW - 980)
            y = wrap(d, (22, y + 4), 'REDUCE MOTION: ' + s['reduce_note'], font('plex', 17), (255, 214, 0), SW - 980)
            y = wrap(d, (22, y + 4), 'NOTE: ' + s['notes'], font('plex', 17), (160, 166, 186), SW - 980)
            tmp.paste(g, (SW - 930, 50))
            tmp.paste(fpn, (SW - 930, 50 + g.height + 8))
            y = max(y, 50 + g.height + 8 + fpn.height) + 14
            stp = {r['skin']: Image.open(r['strip']).convert('RGB') for r in res}
            if 'neutral' in stp:
                im = fit(stp['neutral'], SW - 20)
                tmp.paste(im, (10, y))
                y += im.height + 10
            corp = [stp[k] for k in ('solace', 'meridian') if k in stp]
            if corp:
                cw = (SW - 30) // 2
                ims = [fit(c, cw) for c in corp]
                for i, im in enumerate(ims):
                    tmp.paste(im, (10 + i * (cw + 10), y))
                y += max(i_.height for i_ in ims) + 10
            blocks.append(tmp.crop((0, 0, SW, y + 16)))
        hdr = Image.new('RGB', (SW, 4000), BG)
        d = ImageDraw.Draw(hdr)
        d.rectangle([14, 16, 24, 110], fill=col)
        d.text((40, 6), name, font=font('anton', 64), fill=col)
        d.text((40, 84), tag, font=font('mono', 22), fill=(230, 230, 240))
        d.text((SW - 760, 14), 'combat redesign / locked / effects / 2026-11-04 round 2 / %d effect%s' % (len(specs), '' if len(specs) == 1 else 's'), font=font('mono', 16), fill=(150, 150, 170))
        y = 130
        for r_ in rules:
            y = wrap(d, (40, y), r_, font('plex', 19), (210, 212, 226), SW - 80) + 4
        if order is not None:
            y = wrap(d, (40, y + 4), 'LOUDNESS ORDER (review 2.10, shared gated meter, neutral): ' + order['line'], font('mono', 15), (120, 230, 140) if order['pass'] else (255, 90, 80), SW - 80) + 4
        y = wrap(d, (40, y + 6), 'Board: the round-2 board (2026-11-04, locked/final), base plates rendered from corp/src with the published plates\' own hooks (%s). Strips: keyframes with ms; the yellow-framed tile is reduce motion. Every total <= 600 ms (VfxTier T2, no override). Flash method in NOTES_MPST.md.' % BASE_MATCH,
                 font('mono', 14), (150, 150, 170), SW - 80)
        hdr = hdr.crop((0, 0, SW, y + 16))
        Ht = hdr.height + sum(b.height + 6 for b in blocks)
        sheet = Image.new('RGB', (SW, Ht), BG)
        sheet.paste(hdr, (0, 0))
        yy = hdr.height
        for b in blocks:
            ImageDraw.Draw(sheet).line([(0, yy + 2), (SW, yy + 2)], fill=(44, 44, 58), width=2)
            sheet.paste(b, (0, yy + 6))
            yy += b.height + 6
        fp = OUTD + 'fx_%s_%s.png' % (F, word)
        sheet.quantize(colors=224, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG).save(fp, optimize=True)
        print('sheet', fp, sheet.size, os.path.getsize(fp), flush=True)
    out = dict(scope='M motion, P protect, S system, T commit', rebuild='2026-11-03 rebuild (rebuilt board, gate 1): review 1.6, 2.10, 2.11, 3.10, 1.8',
               round2='2026-11-04 round 2 (R1_REREVIEW build order step 4): re-rendered on the round-2 board (locked/final); %s; C12 SKIP key hint in the resolve beat; '
                      'C1 the commit burns the board\'s one pencil (the p2 plate); C16 the Solace wave scan line takes the teal cell-edge ink #4FA6A2; '
                      'C8 trace_add lights the TRACE pip on the round-2 HUD rows (p1 y 543.5, p3 y 645.5); C15 P_STOCK from rb_tokens' % BASE_MATCH,
               fps=60, cap_ms=E.CAP_MS,
               flash_method='NOTES_MPST.md (unchanged): WCAG relative luminance, 2x2 decimated; footprint = px moving > 0.02 from frame 0; per-pixel extremum tracker logs a swing at >= 0.10; a region event = >= 25 % of the footprint swinging the same way inside 100 ms; a flash = two opposite region events; pass = <= 3 flashes in any 1 s window',
               loudness_method='shared gated meter (the C/D/H/L designer\'s fxk_lib.loud_frame, read-only snapshot): per frame, px whose CIE Lab differs by dE76 > 5 from the same frame with the effect\'s marks off AND from the settled frame, weighted by their L* / 100; the peak over the full-motion frames. brighter_only = px >= 5 L* above max(pre, post, marks-off), x mean L* / 100 (the M/P/S/T measure before the rebuild).',
               loudness_order=order, effects=timings)
    for sk in ('solace', 'meridian'):
        fp = ME + 'work/loud_order_%s.json' % sk
        if os.path.exists(fp):
            out['loudness_order_' + sk] = json.load(open(fp))
    before = json.load(open(ME + 'work/timings_MPST_before_rebuild.json'))['effects']
    for fid, e in timings.items():
        e['total_ms_before_rebuild'] = before[fid]['total_ms'] if fid in before else None
        fp = ME + 'work/layer_%s_neutral.json' % fid
        if os.path.exists(fp):
            lc = json.load(open(fp))
            e['layer_check_neutral'] = dict(full=lc['full'], reduce=lc['reduce'], method=lc['method'].split('\n')[0] + ' (src/layer_check.py)')
    mf, mr = ME + 'work/beat/meter_full.json', ME + 'work/beat/meter_red.json'
    B_SKIP = json.load(open(ME + 'work/skip_tab.json'))
    if os.path.exists(mf) and os.path.exists(mr):
        a, b = json.load(open(mf)), json.load(open(mr))
        go = json.load(open(ME + 'work/beat/out.json')) if os.path.exists(ME + 'work/beat/out.json') else None
        gd = json.load(open(ME + 'work/beat/guard.json')) if os.path.exists(ME + 'work/beat/guard.json') else None

        def summ(m):
            return dict(whole_frame=dict(flashes=m['beat']['whole']['flashes'], max_flashes_per_s=m['beat']['whole']['max_flashes_per_s']),
                        track_boxes_max_flashes_per_s=max(v['max_flashes_per_s'] for v in m['beat']['boxes'].values()),
                        tiles={k: dict(n=v['n'], max_flashes_per_s=v['max_flashes_per_s'], worst=v['worst'][:2]) for k, v in m['beat']['tiles'].items()},
                        max_flashes_per_s_beat=m['max_flashes_per_s_beat'], max_flashes_per_s_skips=m['max_flashes_per_s_skips'],
                        skips={k: v['max_flashes_per_s_any_region'] for k, v in m['skips'].items()}, passes=m['passes'])
        out['resolve_beat_e10'] = dict(
            files=['resolve_beat_strip.jpg', 'resolve_beat.gif'], skin='neutral', total_ms=a['total_ms'], limit_ms=4000, skip_ms=a['skip_ms'],
            skip='any input: the frame dissolves (easeInOutCubic) to the settled frame in skip_ms',
            skip_hint=dict(call='C12 (round 2)', words='ANY KEY  SKIP', spec='HUD label spec: Share Tech Mono %d px, tracking %s (hud2.LBL_PX / LBL_TRK)' % (B_SKIP['label_px'], B_SKIP['label_track']),
                           where='a terminal tab (hud2.P) hung under the p3 HUD foot at its right end, x %s-%s, y %s-%s, like the REFUND tab' % (B_SKIP['tab'][0], B_SKIP['tab'][2], B_SKIP['tab'][1], B_SKIP['tab'][3]),
                           shows='for the length of the beat: fades in over 100 ms after SEND IT, out over the beat\'s last 100 ms; a skip dissolves it with the frame; not in the settled frame',
                           measured=json.load(open(ME + 'work/beat/skip_measure.json')) if os.path.exists(ME + 'work/beat/skip_measure.json') else None),
            tracks=a['tracks'], order='concurrent tracks in the HUD chain order (SEND IT, 1 TWIST, 2 TRIGGER, 4 GUNS, 3 BRACE + 5 LANDS, 6 RINGS STEP, W4 enters); every effect at its own designer\'s timing, each <= 600 ms',
            not_to_ship='ring +1 drawn one sector back from SEND IT until Twist turns it (f2 holds ring +1 where Twist leaves it): a RULES question (REVIEW_RESPONSE "Shove bump, Twist render"); the strip and the GIF caption say so',
            flash_full=summ(a), flash_reduce=summ(b), flash_method=a['method'], gif=go['gif'] if go else None, strip=go['strip'] if go else None,
            kill_colour_check=gd)
    json.dump(out, open(OUTD + 'timings_MPST.json', 'w'), indent=1)
    print('timings ok', flush=True)


if __name__ == '__main__':
    main()
