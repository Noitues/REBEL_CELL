"""fx_sheets.py : family sheets, per-effect strips, timings_CDHL.json and fx_block_vs_break.png from work/kf + work/flash"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import fx_cdhl as F
from fxk_lib import W, anton, mono, plex, PINK, HARM, GAIN, GOLD, INK

OUT = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
os.makedirs(OUT + 'strips', exist_ok=True)
BG = (12, 12, 18)
TXT = (232, 236, 246)
MID = (150, 160, 178)
YEL = (255, 226, 0)
FAM = {'C': ('CORP', 'THE ENEMY CHANGES STATE', 'the corp\'s own frame enamel as a flat shutter slab with a hard lip (neutral steel, Solace porcelain + lime membrane lip, Meridian stencil paint + notched oxide lip), one flat flash, no texture', (200, 210, 226)),
       'D': ('DAMAGE', 'WE HURT THEM', 'player-owned comic hit frame: painted pink tracer, ink-keylined pink starburst with a white core, converging speed lines, flat vector shards', PINK),
       'H': ('HARM', 'THE ENEMY HURTS YOU', 'misregistered red print: X-only halftone flood (never round dots, so it never reads as the spinner\'s Ben-Day), black krackle with a 2 px red offset, red stencil X', HARM),
       'L': ('LIFE', 'YOU GAIN', 'the one soft rising glow: brush strokes, plus signs and four-point sparkles; GAIN green, mint on the green REPAIR wedge, NET_CYAN for RAM', GAIN),
       'P': ('PROTECT', '', '', (240, 236, 224))}
IHO = {'fx_grow': (250, 67, 333, 'in ease-in-out cubic wipe; hold = 4-frame flat flash; out ease-in-out open + ease-out ping'),
       'fx_ward_on': (450, 67, 233, 'in sine pulse + ease-in-out scan; hold = 4-frame gold flash; out ease-out ping'),
       'fx_gun_hit': (170, 160, 270, 'in ease-out tracer + ease-out-back burst; out linear fade'),
       'fx_strike': (200, 180, 320, 'in ease-out slash + ease-out-back burst; out linear'),
       'fx_trigger_hit': (420, 230, 250, 'in linear ignition front to back; bursts ease-out back; out linear'),
       'fx_kill': (110, 220, 270, 'in 2-frame step flare + ease-out-back burst; out linear, cell empties ease-in-out'),
       'fx_ricochet': (100, 150, 250, 'in ease-out tracer; glint sine; out linear'),
       'fx_ricochet_gold': (100, 220, 200, 'in ease-out tracer; streak ease-out; out linear'),
       'fx_firewall_burn': (460, 240, 300, 'in ease-out rise, 130 ms ring stagger; hold with a 7 Hz height flicker; out linear'),
       'fx_hit_land': (160, 170, 370, 'in ease-in chevrons, 2-frame frame flash, ease-out flood; out linear'),
       'fx_hit_land_worm': (160, 170, 370, 'as fx_hit_land; hook ease-out back'),
       'fx_hit_land_adjuster': (160, 170, 370, 'as fx_hit_land; one sine gold flash'),
       'fx_shield_break': (190, 190, 320, 'in ease-out load + crack; shards ease-out + gravity; dark ease-in-out (stays)'),
       'fx_slice_crack': (260, 40, 200, 'in ease-out crack; flood linear'),
       'fx_slice_break': (200, 180, 270, 'in ease-out-back stamp; black-out ease-in-out (stays)'),
       'fx_hp_through': (880, 100, 170, 'in ease-out lift + ease-in-out flight, 30 ms stagger; hold = sine slap; out linear'),
       'fx_refund': (650, 0, 250, 'in ease-out-back pop + ease-in-out flight; out ease-out ring'),
       'fx_clear': (300, 100, 400, 'in ease-in-out wash + ease-out-back check; out linear'),
       'fx_repair_mend': (560, 0, 340, 'in ease-out rise, sine width; pip ease-in-out; out linear glow'),
       'fx_shield_block': (100, 260, 200, 'in ease-out chevrons; sparks ease-out; out linear')}


def flash_line(fid, skins):
    parts = []
    worst = 0
    for sk in skins:
        r = json.load(open(W + 'flash/%s_%s.json' % (fid, sk)))
        f = r['full']
        worst = max(worst, f['max_flashes_per_s_footprint'], f['max_flashes_per_s_crop'])
        parts.append('%s %d/s' % (sk[:3], max(f['max_flashes_per_s_footprint'], f['max_flashes_per_s_crop'])))
    r = json.load(open(W + 'flash/%s_neutral.json' % fid))
    f = r['full']
    rd = r.get('reduce', {})
    s = 'FLASH (60 fps, measured): max %d flash/s (%s); footprint %d px = %d %% of crop; peak swing share %d %% up / %d %% down; mean-lum max step %.2f; reduce %d/s  ->  %s' % (
        worst, ', '.join(parts), f['footprint_px'], round(f['footprint_share'] * 100), round(f['peak_up_share_footprint'] * 100), round(f['peak_down_share_footprint'] * 100),
        f['mean_lum_max_step'], rd.get('max_flashes_per_s_footprint', 0), 'PASS (<= 3/s)' if worst <= 3 else 'FAIL')
    return s, worst


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


def block(fx, page_w, cell_w=None, big=False):
    """one effect block: header text + a keyframe row (+ reduce) per skin"""
    fid = fx['id']
    fam = FAM[fx['fam']]
    bw, bh = fx['box'][2] - fx['box'][0], fx['box'][3] - fx['box'][1]
    n = len(fx['keys']) + 1
    margin, lab, gap = 24, 34, 8
    avail = page_w - 2 * margin - lab
    per_row = n if bw / bh <= 2.2 else 3
    cw = cell_w or int((avail - gap * (per_row - 1)) / per_row)
    if cell_w:
        per_row = n if bw / bh <= 2.2 else 3
    sc = cw / bw
    ch = int(bh * sc)
    rows_per_skin = math.ceil(n / per_row)
    page_w = max(page_w, 2 * margin + lab + per_row * cw + (per_row - 1) * gap)
    tmp = Image.new('RGB', (page_w, 10))
    d = ImageDraw.Draw(tmp)
    fs = 18 if big else 16
    fl, worst = flash_line(fid, fx['skins'])
    i_, h_, o_, ez = IHO[fid]
    timing = 'TIMING: in %d ms, hold %d ms, out %d ms (total %d ms); %s. Phases: %s' % (i_, h_, o_, fx['timing']['total'], ez,
                                                                                    ', '.join('%s %d-%d' % (k, v[0], v[1]) for k, v in fx['timing']['phases'].items()))
    texts = [('STILL: ' + fx['still'], TXT), (timing, MID), (fl, (140, 230, 160) if worst <= 3 else HARM), ('REDUCE MOTION: ' + fx['reduce_note'], YEL),
             ('STYLE MUST KEEP: ' + fx['keep'], (255, 214, 120)), ('SOURCE: ' + fx['source'], MID)]
    lines = []
    for t, c in texts:
        for ln in wrap(d, t, plex(fs), page_w - 2 * margin):
            lines.append((ln, c))
    head_h = 46 + len(lines) * (fs + 5) + 10
    rows_h = len(fx['skins']) * rows_per_skin * (ch + 24 + gap)
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
            yy = y + rr * (ch + 24 + gap)
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
                while d.textlength(cap, font=capf) > cw and len(cap) > 8:
                    cap = cap[:-2]
                d.text((xx + 2, yy + ch + 4), cap, font=capf, fill=col)
        y += rows_per_skin * (ch + 24 + gap)
    d.line([(margin, H - 4), (page_w - margin, H - 4)], fill=(40, 42, 54), width=1)
    return im


def family_sheet(letter, fname):
    fam = FAM[letter]
    fxs = [f for f in F.FX if f['fam'] == letter]
    page_w = 1920
    blocks = [block(f, page_w) for f in fxs]
    hdr = 120
    H = hdr + sum(b.height for b in blocks) + 20
    im = Image.new('RGB', (page_w, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([18, 18, 30, 100], fill=fam[3])
    d.text((44, 10), 'FX-%s %s' % (letter, fam[0]), font=anton(60), fill=TXT)
    d.text((44, 84), '%s  //  %s' % (fam[1], fam[2]), font=mono(16), fill=MID)
    d.text((page_w - 24, 20), 'combat redesign / locked final board / effects (step 4) / %d effects' % len(fxs), font=mono(16), fill=MID, anchor='ra')
    d.text((page_w - 24, 44), 'board: locked/final (E10 state), player skin + Solace + Meridian where the effect touches corp rings', font=mono(14), fill=MID, anchor='ra')
    y = hdr
    for b in blocks:
        im.paste(b, (0, y))
        y += b.height
    im.save(OUT + fname, optimize=True)
    print('sheet', fname, im.size, os.path.getsize(OUT + fname) // 1024, 'KB')


def strip(fx):
    bw = fx['box'][2] - fx['box'][0]
    cw = min(520, bw) if bw / (fx['box'][3] - fx['box'][1]) <= 1.55 else min(900, bw)
    b = block(fx, 1920, cell_w=cw, big=True)
    p = OUT + 'strips/%s.jpg' % fx['id']
    q = 90
    while True:
        b.save(p, quality=q, optimize=True)
        if os.path.getsize(p) < 1900 * 1024 or q < 60:
            break
        q -= 6
    print('strip', fx['id'], b.size, os.path.getsize(p) // 1024, 'KB', 'q', q)


def timings():
    out = dict(_doc='Effects C/D/H/L (+ P shield_block, comparison only) on the locked final board. Times in ms at 60 fps. in/hold/out from IHO; phases are [start, end] ms; flash = measured (see NOTES_CDHL.md, method).',
               effects={})
    for fx in F.FX + [F.SHIELD_BLOCK]:
        fid = fx['id']
        i_, h_, o_, ez = IHO[fid]
        fl = {}
        for sk in fx['skins']:
            r = json.load(open(W + 'flash/%s_%s.json' % (fid, sk)))
            fl[sk] = {k: v for k, v in r['full'].items() if k not in ('mean_series_footprint', 't_ms')}
            if 'reduce' in r:
                fl[sk + '_reduce'] = {k: v for k, v in r['reduce'].items() if k not in ('mean_series_footprint', 't_ms')}
        out['effects'][fid] = dict(family=fx['fam'], title=fx['title'], variant_of=fx['variant_of'], tier=fx['tier'], scope=fx['scope'], skins=list(fx['skins']),
                                   total_ms=fx['timing']['total'], in_ms=i_, hold_ms=h_, out_ms=o_, easing_summary=ez, easing=fx['timing']['easing'],
                                   phases=fx['timing']['phases'], keyframes=[dict(ms=t, caption=c) for t, c in fx['keys']], reduce_motion=fx['reduce_note'],
                                   source=fx['source'], board_crop=list(fx['box']), base=dict(pre=fx['pre'], post=fx['post']), flash=fl)
    json.dump(out, open(OUT + 'timings_CDHL.json', 'w'), indent=1)
    print('timings ok')


def block_vs_break():
    b, k = F.SHIELD_BLOCK, F.BYID['fx_shield_break']
    pb = Image.open(W + 'kf/fx_shield_block_neutral_2.png')
    pk = Image.open(W + 'kf/fx_shield_break_neutral_2.png')
    sc = 2.0
    cw, ch = int(pb.width * sc), int(pb.height * sc)
    page_w = 1920
    top = 130
    im = Image.new('RGB', (page_w, top + ch + 60), BG)
    d = ImageDraw.Draw(im)
    d.text((24, 10), 'BLOCK vs BREAK, on the locked final board', font=anton(52), fill=TXT)
    d.text((24, 78), 'Same slice (sector 1 SHIELD), same paper plate, peak frame, colour and luma.  Block = ONE intact plate, white sparks, flat pink tint off the icon seat, no red.  Break = the plate in 5 shards, red X-halftone flood, black krackle, the wedge ends dark.', font=plex(17), fill=MID)
    d.text((24, 102), 'Block is P protect (drawn here only for the comparison; the P family sheet belongs to the M/P/S/T designer). Break is H harm.', font=plex(17), fill=MID)
    x = 24
    for lab_, f, col in (('SHIELD BLOCK  (P)  180 ms', pb, (240, 236, 224)), ('SHIELD BREAK  (H)  180 ms', pk, HARM)):
        big = f.resize((cw, ch), Image.LANCZOS)
        im.paste(big, (x, top))
        d.text((x, top + ch + 8), lab_, font=mono(20), fill=col)
        x += cw + 16
    gw = (page_w - x - 24 - 12) // 2
    for lab_, f in (('block, luma', pb), ('break, luma', pk)):
        g = f.convert('L').convert('RGB').resize((gw, int(gw * f.height / f.width)), Image.LANCZOS)
        im.paste(g, (x, top))
        d.text((x, top + g.height + 6), lab_, font=mono(16), fill=MID)
        x += gw + 12
    # strips under it
    sb = block(b, page_w)
    sk = block(k, page_w)
    H = im.height + sb.height + sk.height + 10
    out = Image.new('RGB', (page_w, H), BG)
    out.paste(im, (0, 0))
    out.paste(sb, (0, im.height))
    out.paste(sk, (0, im.height + sb.height))
    out.save(OUT + 'fx_block_vs_break.png', optimize=True)
    print('block_vs_break', out.size, os.path.getsize(OUT + 'fx_block_vs_break.png') // 1024, 'KB')


if __name__ == '__main__':
    what = sys.argv[1:] or ['all']
    if 'all' in what or 'sheets' in what:
        for L_, nm in (('C', 'fx_C_corp.png'), ('D', 'fx_D_damage.png'), ('H', 'fx_H_harm.png'), ('L', 'fx_L_life.png')):
            family_sheet(L_, nm)
    if 'all' in what or 'strips' in what:
        for fx in F.FX:          # shield_block (P) belongs to the M/P/S/T designer; it appears only inside fx_block_vs_break.png
            strip(fx)
    if 'all' in what or 'timings' in what:
        timings()
    if 'all' in what or 'bvb' in what:
        block_vs_break()
