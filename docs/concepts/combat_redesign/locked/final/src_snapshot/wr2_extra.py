"""R2 extra sheets: twin check (unit glyphs vs the library), kind_colour_set, token_placement, removed elements, squint / deutan / nowords checks.
usage: wr2_extra.py twin|kinds|place|removed|checks"""
import sys, os, json, math, textwrap
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import e8lib as E8
ORIG_TP = E8.token_pos
import wr2_glyphs
import wr2_lib as W2
import wr2_sets as S
import wr2_units as W2U
from wr2_sheets import F_T, F_L, F_C, F_S, BG, glyph_strip, wrap, OUT2, DEST
import slicelib as SL

SIZES = (16, 20, 28, 37, 44, 70)
UNIT = {'Packet': 'WR_PACKET_R', 'Worm': 'WR_WORM_R', 'Payload': 'WR_PAYLOAD_R', 'Jammer': 'WR_JAMMER_R', 'Ring': 'WR_RING_R'}
UNIT_V = {'Packet': 'WR_PACKET_V', 'Worm': 'WR_WORM_V', 'Payload': 'WR_PAYLOAD_V', 'Jammer': 'WR_JAMMER_V', 'Ring': 'WR_RING_V'}
UNIT_R1 = {'Packet': 'WR_PACKET_A', 'Worm': 'WR_WORM_B', 'Payload': 'WR_PAYLOAD_A', 'Jammer': 'WR_JAMMER_B', 'Ring': 'WR_RING_C'}


def mask(name, n=128):
    m = SL.glyph_mask(name)
    return (np.asarray(m.resize((n, n))) > 127)


def iou(a, b):
    return float((a & b).sum() / max(1, (a | b).sum()))


def twin():
    lib = W2U.library()
    nb = {'Spin (KA_nudge)': 'KA_nudge', 'Brace plate (KA_brace)': 'KA_brace', 'Twist (KA_twist)': 'KA_twist', 'Hold (KA_hold)': 'KA_hold', 'Trigger (KA_trigger)': 'KA_trigger',
          'Strike (KA_strike)': 'KA_strike', 'Firewall (KA_firewall)': 'KA_firewall', 'Pull (KA_pull)': 'KA_pull', 'Shove (KA_shove)': 'KA_shove', 'Skull (X_SKULL)': 'X_SKULL'}
    mu = {k: mask(v) for k, v in UNIT.items()}
    mv = {k: mask(v) for k, v in UNIT_V.items()}
    m1 = {k: mask(v) for k, v in UNIT_R1.items()}
    mn = {k: mask(v) for k, v in nb.items()}
    rows = []
    for k in UNIT:
        cands = [(iou(mu[k], v), n) for n, v in mn.items()] + [(iou(mu[k], mu[o]), 'unit ' + o) for o in UNIT if o != k]
        cands.sort(reverse=True)
        c1 = [(iou(m1[k], v), n) for n, v in mn.items()] + [(iou(m1[k], m1[o]), 'unit ' + o) for o in UNIT if o != k]
        c1.sort(reverse=True)
        rows.append((k, cands[:2], c1[:1]))
    W = 1700
    rowh = 150
    sh = Image.new('RGB', (W, 220 + rowh * len(rows) * 2 + 100 * 6), BG)
    d = ImageDraw.Draw(sh)
    d.text((12, 8), 'UNIT GLYPH TWIN CHECK (R2)', font=F_T, fill=(255, 255, 255))
    d.text((12, 48), 'Silhouette overlap (IoU of the 512-grid fill masks, as drawn) against the card library neighbours and the other unit glyphs; a coarse screen, judge by eye at 28 px too. Sizes 16 / 20 / 28 / 37 / 44 / 70 px, white + 7.5% ink on the unit mauve.', font=F_C, fill=(200, 208, 222))
    d.text((12, 74), 'Library glyphs: card_icon_set A (kglyph KA_*), imported read-only. The cracked-ring crest and the unit masters (Packet, Worm, Payload, Jammer, Ring) are not in that library yet: the unit masters are owned here.', font=F_C, fill=(200, 208, 222))
    nmap = {**nb, **{'unit ' + o: UNIT[o] for o in UNIT}}
    y = 110
    for (k, c2, c1) in rows:
        for lab, names, c in (('R1 pick', UNIT_R1[k], c1), ('R2 pick (R)', UNIT[k], c2)):
            d.text((12, y + 4), '%s  %s' % (k.upper(), lab), font=F_L, fill=(255, 255, 255))
            sh.paste(glyph_strip(names, SIZES), (12, y + 34))
            for n_, (v, n) in enumerate(c):
                flag = (120, 230, 150) if v < 0.55 else (255, 150, 110)
                d.text((420, y + 40 + n_ * 26), 'closest %d: %s   IoU %.2f' % (n_ + 1, n, v), font=F_C, fill=flag)
                nm = nmap.get(n)
                if nm:
                    sh.paste(glyph_strip(nm, (28, 70)), (900 + n_ * 260, y + 34))
            y += rowh - 10
        y += 12
    d.text((12, y), 'VARIANT (V) glyphs', font=F_L, fill=(120, 190, 255))
    y += 32
    for k in UNIT:
        d.text((12, y + 34), k.upper() + ' V', font=F_C, fill=(255, 255, 255))
        sh.paste(glyph_strip(UNIT_V[k], SIZES), (150, y))
        y += 100
    sh = sh.crop((0, 0, W, y + 10))
    sh.save(DEST + 'sheet_twin_check_unit_glyphs.jpg', quality=88)
    print('twin', sh.size)
    return rows


def kinds():
    tabs = {o: S.table_for(o) for o in ('R', 'V', 'C')}
    tabs['E'] = dict(S.R1_TABLE)
    export = S.export(DEST + 'kind_colour_set.json', {'R2_pick_R': tabs['R'], 'variant_V': tabs['V'], 'variant_C_value_ladder': tabs['C'], 'R1_current': tabs['E']})
    scores = {o: S._score(t) for o, t in tabs.items()}
    names = list(S.KINDS)
    W = 1900
    sh = Image.new('RGB', (W, 1500), BG)
    d = ImageDraw.Draw(sh)
    d.text((12, 8), 'KIND COLOUR SET (R2)', font=F_T, fill=(255, 255, 255))
    d.text((12, 46), 'One wash table for Packet, Worm, Payload, Jammer, Ring and the Adjuster. The cell wash (ring ramp 0 / 20 / 38 %), the token disc (kind colour = wash x 1.4, drawn at 26 %) and the landing-arc kind disc (arc_glyph_disc) read this table; the bible token table lists the R values.', font=F_C, fill=(200, 208, 222))
    d.text((12, 70), 'Search: hill-climb inside each kind\'s E10 family hue window (rose, violet, indigo, wine, grey-lilac) maximising the minimum pairwise colour distance over normal + deutan + protan + tritan, on the NOW and +2 washes. Score = min distance (Lab dE, deutan etc. weighted 1.25).', font=F_C, fill=(200, 208, 222))
    y = 110
    labels = {'R': 'R2 PICK (R): optimised mauve ladder', 'V': 'VARIANT (V): R1 values, only the unseen Ring moved', 'C': 'VARIANT (C): value ladder, one hue, five values', 'E': 'R1 / E10 current (Ring == Payload colour)'}
    for o in ('R', 'V', 'C', 'E'):
        d.text((12, y), '%s    min dE %.1f' % (labels[o], scores[o]), font=F_L, fill=(120, 230, 150) if o == 'R' else (230, 235, 245))
        y += 32
        for sim in ('none', 'deutan', 'protan', 'tritan'):
            d.text((12, y + 30), {'none': 'normal', 'deutan': 'deutan', 'protan': 'protan', 'tritan': 'tritan'}[sim], font=F_S, fill=(170, 180, 200))
            x = 110
            for k in names + ['Adjuster']:
                wash = tabs[o].get(k, (70, 52, 14))
                for ramp in (0.0, 0.20, 0.38):
                    c = tuple(int(round(v + ((10, 8, 30)[i] - v) * ramp)) for i, v in enumerate(wash))
                    c = c if sim == 'none' else W2.sim_rgb(c, sim)
                    d.rectangle([x, y, x + 40, y + 62], fill=c)
                    x += 42
                # token disc: kind colour at 26 percent, white ring, glyph
                kc = tuple(min(255, int(v * S.TOK_F)) for v in wash) if k != 'Adjuster' else S.BOSS
                tc = tuple(int(v * 0.26) for v in kc)
                tc = tc if sim == 'none' else W2.sim_rgb(tc, sim)
                d.ellipse([x + 4, y + 4, x + 58, y + 58], fill=tc, outline=(236, 240, 255), width=3)
                nm = UNIT.get(k) or 'X_SKULL'
                g = glyph_strip(nm, (28,))
                gi = g.crop((16, 8 + (80 - 28) // 2, 16 + 28, 8 + (80 - 28) // 2 + 28))
                sh.paste(gi, (x + 16, y + 17))
                x += 70
            y += 70
        y += 14
    d.text((12, y), 'LANE_PLUS1 vs TRACE_VIOLET vs SOAK (#6A6CFF): colour distance (Lab dE) per vision type. Shapes carry the meaning (outline vs square vs chevron notch); this is the value / hue floor.', font=F_C, fill=(200, 208, 222))
    y += 28
    pairs = {'LANE_PLUS1 vs TRACE_VIOLET': ((120, 170, 255), (160, 60, 255)), 'SOAK vs LANE_PLUS1': ((106, 108, 255), (120, 170, 255)), 'SOAK vs TRACE_VIOLET': ((106, 108, 255), (160, 60, 255))}
    rep = {}
    for n, (a, b) in pairs.items():
        row = []
        for sim in ('none', 'deutan', 'protan', 'tritan'):
            sa = a if sim == 'none' else W2.sim_rgb(a, sim)
            sb = b if sim == 'none' else W2.sim_rgb(b, sim)
            row.append((sim, W2.dE(sa, sb), sa, sb))
        rep[n] = row
        d.text((12, y + 14), n, font=F_C, fill=(255, 255, 255))
        x = 330
        for (sim, e, sa, sb) in row:
            d.rectangle([x, y, x + 44, y + 44], fill=sa)
            d.rectangle([x + 44, y, x + 88, y + 44], fill=sb)
            d.text((x + 96, y + 14), '%s %.0f' % (sim, e), font=F_S, fill=(200, 208, 222))
            x += 220
        y += 56
    # in-situ
    y += 10
    ims = []
    for o in ('R', 'V', 'C', 'E'):
        im = Image.open(OUT2 + 'pl_kinds_%s_kinds.png' % o).convert('RGB').crop((150, 150, 930, 930))
        ims.append(im)
    d.text((12, y), 'In situ on room_bio_bare: R | V | C | R1-current (lab frame: Packet / Worm / Payload / Jammer on NOW and +1, a Ring on +2, the Adjuster).', font=F_C, fill=(200, 208, 222))
    y += 28
    s = 0.5
    x = 12
    for im in ims:
        sh.paste(im.resize((int(780 * s * 1.1), int(780 * s * 1.1)), Image.LANCZOS), (x, y))
        x += int(780 * s * 1.1) + 8
    y += int(780 * s * 1.1) + 10
    # deutan of the R pick
    dd = W2.sim_cb(ims[0], 'deutan')
    sh.paste(dd.resize((int(780 * s * 1.1), int(780 * s * 1.1)), Image.LANCZOS), (12, y))
    tt = W2.sim_cb(ims[0], 'tritan')
    sh.paste(tt.resize((int(780 * s * 1.1), int(780 * s * 1.1)), Image.LANCZOS), (12 + int(780 * s * 1.1) + 8, y))
    d.text((12 + 2 * (int(780 * s * 1.1) + 8), y + 6), 'left: R pick under deutan; right: under tritan.\nKinds also differ by glyph shape, which no colour-blind view removes.', font=F_C, fill=(200, 208, 222))
    y += int(780 * s * 1.1) + 10
    sh = sh.crop((0, 0, W, y))
    sh.save(DEST + 'sheet_kind_colour_set.jpg', quality=88)
    print('kinds', sh.size, scores)
    return scores, rep


def place():
    from wr2_sheets import wrap
    names = {'E': 'E10 / R1 rule: 58 px CCW of the first axis (arc length constant, so the gap to the start cap grows with the ring)', 'R': 'R2 PICK (R): token centre 38 px (+4 gutter) from the start cap, mid-line of the cell',
             'V': 'V: flush, the disc 5 px from the start cap', 'C': 'C: centred on the first sector axis'}
    W = 2400
    sh = Image.new('RGB', (W, 1500), BG)
    d = ImageDraw.Draw(sh)
    d.text((12, 8), 'TOKEN PLACEMENT (R2)', font=F_T, fill=(255, 255, 255))
    y = wrap(d, 'RULE: a unit\'s token sits at the START CAP of its cell: centre = 4 px (half gutter) + 27 px (disc radius) + 7 px = 38 px along the cell mid-line from the cell\'s counter-clockwise end (60 x s - 30 degrees), on the cell\'s radial middle. The distance is the same on every ring and for every width (1, 2, 3 and the 6-wide Ring, whose start is its seam). It is never tied to a sector axis, so chevrons, HP trays and the trigger pencil X end cap (all on axes) stay clear of it; hover, trigger path and the refund burst keep their axis anchors.', F_C, W - 40, (12, 48))
    y += 6
    cols = ['E', 'R', 'V', 'C']
    cw = 580
    for i, o in enumerate(cols):
        im = Image.open(OUT2 + 'pl_place_%s_place.png' % o).convert('RGB').crop((150, 150, 930, 930))
        im = im.resize((cw, cw), Image.LANCZOS)
        sh.paste(im, (10 + i * (cw + 8), y + 56))
        d.text((10 + i * (cw + 8), y + 6), '', font=F_S)
        yy = wrap(d, names[o], F_C, cw - 6, (10 + i * (cw + 8), y), fill=(120, 230, 150) if o == 'R' else (200, 208, 222))
    y += 56 + cw + 10
    d.text((12, y), 'Measured on the lab frame (px from the cell start edge to the token centre,  the E10 value grows with the ring, the rule does not):', font=F_C, fill=(255, 255, 255))
    y += 28
    import wr_build as WB
    import wr_latent as WLT
    f = WLT.lab_frame(WB.J, 'place')
    tab = []
    for u in f['units']:
        import wr_geo as G
        from cv_lib import ppx, C
        b0 = 60 * u['s'] - 30
        res = {}
        for o, fn in (('E10', ORIG_TP), ('R', lambda u_: W2.token_pos_r2(u_, 'R')), ('V', lambda u_: W2.token_pos_r2(u_, 'V')), ('C', lambda u_: W2.token_pos_r2(u_, 'C'))):
            x, yv = fn(u)
            ang = math.degrees(math.atan2(x - C[0], -(yv - C[1])))
            rr = math.hypot(x - C[0], yv - C[1])
            da = (ang - b0) % 360
            res[o] = round(math.radians(da) * rr)
        tab.append((u['kind'], u['dep'], u['w'], res))
    for (k, dep, w, res) in tab:
        d.text((24, y), '%-8s ring %d width %d :  E10 %3d   R %3d   V %3d   C %3d' % (k, dep, w, res['E10'], res['R'], res['V'], res['C']), font=F_S, fill=(200, 208, 222))
        y += 22
    sh = sh.crop((0, 0, W, y + 10))
    sh.save(DEST + 'sheet_token_placement.jpg', quality=88)
    print('place', sh.size)
    return tab


if __name__ == '__main__':
    for a in sys.argv[1:]:
        globals()[a]()
