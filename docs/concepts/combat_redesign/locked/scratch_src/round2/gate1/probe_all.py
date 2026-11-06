"""gate1 independent probes on every published board + hover plate (and the backdrop plates for the rim):
  focus   : px within dE76 8 of FOCUS #D4FF00 and of the round-1 lime #96FE46; FOCUS components (count, bbox w/h)
  rim     : Solace rim band r 491-498: median rgb, dE76 to GAIN #7BE07B and hub HP green #7BD37B, share of green-hue px (LCh h 100-160, C* > 20)
  hud     : lit plate-edge runs on the column band x 1072-1081 (NET_CYAN-ish or bright), bill top/bottom
  buttons : right edge of the SEND IT and UNDO plates (column profile)
  frame   : PLAN-wax px (dE < 30 of #FFE200) at r 480-500 and r 500-540 (x < 1060)
  bright  : px inside r < 480 at L* > 89.5 (the tower p95): clustered, each cluster classed by colour (warm white = HOT core, yellow, lime, other)
Output out/probe_all.json + text."""
import json, glob, os
import numpy as np
from scipy import ndimage as ndi
import glib as G

r_, th_, xx, yy = G.polar()
files = [G.FINAL + n + '.png' for b, c, n in G.plates()] + sorted(glob.glob(G.HOVER + 'h*.png'))
files += sorted(glob.glob(G.ROOT + 'backdrop/p1_*.png'))
out = {}
for f in files:
    nm = os.path.relpath(f, G.ROOT).replace('\\', '/')
    rgb = G.load(f)
    L = G.Lstar(rgb)
    lab = G.lab(rgb)
    o = {}
    # focus
    dF = G.de(lab, '#D4FF00'); dLm = G.de(lab, '#96FE46')
    fm = dF < 8
    o['focus_px'] = int(fm.sum()); o['lime96_px'] = int((dLm < 8).sum())
    lb, n = ndi.label(fm, structure=np.ones((3, 3)))
    comps = []
    for sl in ndi.find_objects(lb):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if (lb[sl] > 0).sum() >= 8:
            comps.append((sl[1].start, sl[0].start, w, h))
    o['focus_comps'] = len(comps)
    o['focus_comp_maxdim'] = max([max(c[2], c[3]) for c in comps], default=0)
    o['focus_comp_list'] = comps[:40]
    if fm.sum():
        o['focus_L_p50_p99'] = (G.pct(L[fm], 50), G.pct(L[fm], 99))
        o['focus_median'] = G.hexof(np.median(rgb[fm], 0))
    # rim
    band = (r_ >= 491) & (r_ <= 498)
    med = np.median(rgb[band], 0)
    C = np.hypot(lab[..., 1], lab[..., 2]); H = np.degrees(np.arctan2(lab[..., 2], lab[..., 1])) % 360
    green = band & (C > 20) & (H >= 100) & (H <= 160)
    o['rim_median'] = G.hexof(med); o['rim_dE_gain'] = G.de_cols(med, '#7BE07B'); o['rim_dE_hp'] = G.de_cols(med, '#7BD37B')
    o['rim_green_share'] = float(green.sum() / band.sum())
    o['rim_L_mean'] = float(G.lstar_y(G.lum(rgb)[band].mean()))
    # hud runs at x 1072-1081
    col = rgb[:, 1072:1082]
    dC = G.de(G.lab(col), '#5CE1FF')
    lit = ((dC < 45) | (G.Lstar(col) > 55)).any(1)
    runs = []; i = 0
    while i < 1080:
        if lit[i]:
            j = i
            while j + 1 < 1080 and lit[j + 1]:
                j += 1
            if j - i >= 1:
                runs.append((i, j))
            i = j + 1
        else:
            i += 1
    o['hud_runs'] = runs[:12]
    # buttons: SEND IT plate = pink (dE<40 of CELL_PINK) in rows 930-990; UNDO = bright paper L*>70 rows 866-892
    dP = G.de(lab, '#FF3DA8')
    sp = (dP[930:990, 1600:1920] < 40).sum(0)
    xs = np.nonzero(sp >= 3)[0]
    o['sendit_right'] = int(1600 + xs.max()) if len(xs) else None
    o['sendit_left'] = int(1600 + xs.min()) if len(xs) else None
    up = (L[866:892, 1600:1920] > 70).sum(0)
    xs = np.nonzero(up >= 3)[0]
    o['undo_right'] = int(1600 + xs.max()) if len(xs) else None
    o['undo_left'] = int(1600 + xs.min()) if len(xs) else None
    # frame band PLAN
    dPl = G.de(lab, '#FFE200')
    o['plan_r480_500'] = int(((dPl < 30) & (r_ >= 480) & (r_ <= 500)).sum())
    o['plan_r500_540'] = int(((dPl < 30) & (r_ > 500) & (r_ <= 540) & (xx < 1060)).sum())
    # bright clusters inside r < 480 above 89.5
    bm = (L > 89.5) & (r_ < 480)
    lb, n = ndi.label(ndi.binary_dilation(bm, iterations=1) & (r_ < 480))
    cl = {'hot_white': 0, 'yellow': 0, 'lime': 0, 'other': 0}
    others = []
    for k, sl in enumerate(ndi.find_objects(lb)):
        m = (lb[sl] == k + 1) & bm[sl]
        if m.sum() == 0:
            continue
        px = rgb[sl][m]
        mr = px.mean(0)
        if mr[0] > 235 and mr[1] > 200 and mr[2] > 180 and mr[0] - mr[2] > 6:
            c = 'hot_white'
        elif mr[0] > 200 and mr[1] > 180 and mr[2] < 120 and mr[0] >= mr[1] - 10:
            c = 'yellow'
        elif mr[1] > 220 and mr[2] < 120 and mr[0] < mr[1] - 10:
            c = 'lime'
        else:
            c = 'other'
        cl[c] += int(m.sum())
        if c == 'other' and m.sum() >= 3:
            others.append(dict(x=int(sl[1].start), y=int(sl[0].start), w=int(sl[1].stop - sl[1].start), h=int(sl[0].stop - sl[0].start),
                               px=int(m.sum()), Lmax=round(float(L[sl][m].max()), 1), rgb=G.hexof(mr)))
    o['bright_gt_tower_px'] = cl
    o['bright_other_clusters'] = sorted(others, key=lambda q: -q['px'])[:12]
    out[nm] = o
    print('%-40s F %5d (comps %2d max %2d) lime %4d | rim %s gain %.1f hp %.1f green %.3f L %.1f | hud %s | SEND %s-%s UNDO %s-%s | PLANfb %d/%d | bright %s other %d' % (
        nm, o['focus_px'], o['focus_comps'], o['focus_comp_maxdim'], o['lime96_px'], o['rim_median'], o['rim_dE_gain'], o['rim_dE_hp'], o['rim_green_share'],
        o['rim_L_mean'], o['hud_runs'][:5], o['sendit_left'], o['sendit_right'], o['undo_left'], o['undo_right'], o['plan_r480_500'], o['plan_r500_540'],
        cl, len(others)))
json.dump(out, open('out/probe_all.json', 'w'), indent=1)
