"""crowd_test.png: the three beam types plus heads converging in the t1 cluster near HOME, at 40 / 44 / 48 px (1920 plate coords)."""
from common import *

BEAMS = {b['name']: b for b in COORDS['beams']}
PICK = {'D': 'cand1', 'N': 'cand2', 'E': 'cand0'}
SITES = {s['id']: s for s in COORDS['sites']}
HOME = COORDS['home']['xy']
LANE = {'D': 0.0, 'N': 0.0, 'E': 0.0}
HEX_R = 21.0     # site hex radius in the 1920 plate (measured off plan_placed_net: ~40 px wide)


def overlay_net(base):
    a = np.asarray(PLATE.convert('RGB'), np.int16)
    b = np.asarray(PLATE_NET.convert('RGB'), np.int16)
    m = (np.abs(a - b).max(axis=2) > 30)
    out = np.asarray(base.convert('RGB')).copy()
    nb = np.asarray(PLATE_NET.convert('RGB'))
    out[m] = nb[m]
    return Image.fromarray(out).convert('RGBA')


def scene(size, mode, box, S=2, lane=14.0):
    """mode 'home': heads staggered 24 / 62 / 100 px (arc) before HOME; mode 'sites': heads sitting on t1 sites."""
    base = overlay_net(PLATE)
    x0, y0, x1, y1 = box
    lay = Image.new('RGBA', (1920 * 1, 1080 * 1), (0, 0, 0, 0))
    big = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    lanes = {'D': -lane, 'N': 0.0, 'E': lane}
    dense, heads = {}, []
    for t in ('D', 'N', 'E'):
        pts = resample(BEAMS[PICK[t]]['polyline'], 1.0)
        pts = offset_poly(pts, lanes[t])
        dense[t] = pts
    layS = 2
    lay = Image.new('RGBA', (1920 * layS, 1080 * layS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rw = 11.0
    for t in ('D', 'N', 'E'):
        draw_ribbon(d, [(x * layS, y * layS) for x, y in dense[t]], t, layS, rw)
    glow = lay.filter(ImageFilter.GaussianBlur(5 * layS)).resize((1920, 1080), Image.LANCZOS)
    lay = lay.resize((1920, 1080), Image.LANCZOS)
    base.alpha_composite(glow)
    base.alpha_composite(lay)
    # heads
    placed = []
    if mode == 'home':
        # end of each lane = HOME; place heads a staggered arc length back
        for t, back in (('D', 24), ('N', 62), ('E', 100)):
            i = len(dense[t]) - 1 - back
            placed.append((t, dense[t][i], heading_at(dense[t], i)))
        # reference beetle: a 4th unit at the next stagger on an N lane copy (neutral)
        pts = offset_poly(resample(BEAMS['cand2']['polyline'], 1.0), 0.0)
        # (no ribbon for the future unit, head only)
        i = len(pts) - 1 - 138
        placed.append(('X', pts[i], heading_at(pts, i)))
    else:
        # head on the polyline point nearest to the site's route anchor (where a beam crosses it)
        for t, sid in (('E', 't1_a'), ('N', 't1_b'), ('D', 't1_c')):
            sx, sy = SITES[sid]['xy']
            pts = dense[t]
            i = min(range(len(pts)), key=lambda j: math.hypot(pts[j][0] - sx, pts[j][1] - (sy + 36)))
            placed.append((t, pts[i], heading_at(pts, i)))
    for t, (x, y), a in placed:
        paste_head(base, head(t), x, y, size, a, t)
    return base.crop((x0, y0, x1, y1)).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS), placed


def hidden(size, placed, sid):
    """(hex disc hidden %, pip strip hidden %) of site sid by the heads in placed."""
    sx, sy = SITES[sid]['xy']
    yy, xx = np.mgrid[0:1080, 0:1920]
    disc = ((xx - sx) ** 2 + (yy - sy) ** 2) <= HEX_R ** 2
    pips = (np.abs(xx - sx) <= 20) & (yy >= sy + 22) & (yy <= sy + 34)
    hid = np.zeros_like(disc)
    for t, (x, y), a in placed:
        m = mask_at(head(t), size, a) > .5
        h, w = m.shape
        ox, oy = int(round(x - w / 2)), int(round(y - h / 2))
        full = np.zeros((1080, 1920), bool)
        full[max(oy, 0):min(oy + h, 1080), max(ox, 0):min(ox + w, 1920)] = m[max(-oy, 0):h - max(oy + h - 1080, 0), max(-ox, 0):w - max(ox + w - 1920, 0)]
        hid |= full
    return round(float((disc & hid).sum() / disc.sum()), 2), round(float((pips & hid).sum() / pips.sum()), 2)


def worst(size):
    """every head type parked on the route anchor (site xy + 36 px down) of every T1/T2 site, heading toward HOME (down-left): worst disc / pip hide."""
    wd, wp = (0, None), (0, None)
    for t in ('D', 'N', 'E'):
        for sid in ('t1_a', 't1_b', 't1_c', 't1_d', 't2_breach', 't2_intel', 't2_virus'):
            sx, sy = SITES[sid]['xy']
            for ang in (154, -26, 0, 90):
                dd, pp = hidden(size, [(t, (sx, sy + 36), ang)], sid)
                if dd > wd[0]:
                    wd = (dd, f'{t}@{sid}')
                if pp > wp[0]:
                    wp = (pp, f'{t}@{sid}')
    return wd, wp


def main():
    W = 1300
    rows = []
    hd = Image.new('RGB', (W, 92), BG)
    d = ImageDraw.Draw(hd)
    d.text((20, 6), 'H6 CROWD TEST  |  3 beams + heads in the T1 cluster by HOME', font=F(FONT_T, 34), fill=(120, 230, 255))
    d.text((20, 52), 'Plate coords from default_forecast.json (D = cand1, N = cand2, E = cand0, lanes offset +-14 px, ribbon 11 px since the three share the streets). Site hexes/tier tags composited from plan_placed_net.', font=F(FONT_M, 13), fill=(235, 235, 250))
    d.text((20, 70), 'Left: heads staggered at 24 / 62 / 100 px before HOME (+ beetle at 138). Right: worst case, a head sitting on each of t1_a (E), t1_b (N), t1_c (D). 2x.', font=F(FONT_M, 13), fill=(190, 200, 225))
    rows.append(hd)
    cov = {}
    for size in (40, 44, 48):
        bh = (250, 540, 540, 700)       # HOME stretch
        bs = (330, 395, 640, 600)       # t1 sites
        sh, ph = scene(size, 'home', bh)
        ss, ps = scene(size, 'sites', bs)
        c = {sid: hidden(size, ps, sid) for sid in ('t1_a', 't1_b', 't1_c')}
        wc = worst(size)
        cov[size] = {'scene': c, 'worst_disc': wc[0], 'worst_pips': wc[1]}
        rowim = Image.new('RGB', (W, max(sh.height, ss.height) + 4), BG)
        rowim.paste(sh.convert('RGB'), (0, 0))
        rowim.paste(ss.convert('RGB'), (sh.width + 20, 0))
        dd = ImageDraw.Draw(rowim)
        dd.text((6, 4), f'{size} px  (N/D {size}, E/X4 {round(size*.852)})', font=F(FONT_M, 16), fill=(255, 235, 120))
        dd.text((sh.width + 26, 4), f'{size} px  hex/pips hidden by heads: t1_a {c["t1_a"][0]:.0%}/{c["t1_a"][1]:.0%} t1_b {c["t1_b"][0]:.0%}/{c["t1_b"][1]:.0%} t1_c {c["t1_c"][0]:.0%}/{c["t1_c"][1]:.0%}', font=F(FONT_M, 16), fill=(255, 235, 120))
        dd.text((sh.width + 26, 22), f'worst case, any head type parked on any T1/T2 route anchor: hex {wc[0][0]:.0%} ({wc[0][1]}), pips {wc[1][0]:.0%} ({wc[1][1]})', font=F(FONT_M, 14), fill=(255, 200, 120))
        rows.append(label_row(f'SIZE {size} px', W))
        rows.append(rowim)
    out = stack(rows, W)
    out.save(os.path.join(OUT, 'crowd_test.png'))
    json.dump(cov, open(os.path.join(HERE, 'crowd_metrics.json'), 'w'), indent=1)
    print(out.size, cov)


if __name__ == '__main__':
    main()
