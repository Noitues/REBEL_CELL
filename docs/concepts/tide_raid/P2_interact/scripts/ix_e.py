"""P1 sequence 7: 1280x720 layout, 4:3 and ultrawide safe areas, declutter rules.   python ix_e.py [name ...]"""
import sys, time
from ix_lib import *
from ix_lib import _brackets
from ix_b import SLOT_C, slots


def forecast_scene(f=1.0, tally_mode='marks', hand_mode='fan', hud=True, tally=True):
    """the forecast frame with every mark scaled by f (the UI floor for small screens). P2 marks, pictogram tally."""
    w = World('default')
    cv = plan_base(w, grade=0.0, ks={'K1': 1.0, 'K2': 1.0, 'K3': 1.0}, sealed_k=.85, lock_k=.9, hunter_k=.8, home_kw=dict(hp=44, preview=6),
                   programs=PROGRAMS, ends={r: w.visit(r, TARGET[r][0]) + 20 for r in KN})
    for r in KN:
        R = w.routes[r]
        P = PX(R['path'])
        s_stop = w.visit(r, TARGET[r][0])
        hy.dead_trail(cv, P, s_stop + 40, P.L - 4)
        hy.target_ring(cv, w.sites[TARGET[r][0]]['B'], TARGET[r][1])
        hy.stop_block(cv, P, s_stop - 2, TARGET[r][1])
    items = [('t1_c', 'HOLDS', None), ('t1_b', 'SITES_LOST', 1), ('t2_intel', 'UNTOUCHED', None)]
    anchors = [np.array(w.sites[i[0]]['crown']) + np.array([0, -58]) for i in items]
    pos = hy.fan(anchors, 66.0 * f)
    pts = np.vstack([w.routes[r]['path'][::3] for r in KN])
    for it, a_, p in zip(items, anchors, pos):
        p = np.array(p, float)
        for _ in range(4):
            if np.min(np.hypot(*(pts - p).T)) < 44 * f:
                p = p + np.array([0, -46])
        src = np.array(w.sites[it[0]]['crown'])
        hy.leader(cv, src + np.array([0, -4]), p + np.array([0, 22 * f]), k=.7)
        hy.hex_tile(cv, tuple(p), it[1], it[2], r=30 * f)
    hy.home_chip(cv, w.home, 6)
    if tally:
        tally12(cv, BASE12, TALLY_C, r=25 * (f if f < 1.2 else 1.0))
    if hud:
        hy.hud(cv, 44, 50, 80, 8, 0)
    if hand_mode == 'fan':
        hy.hand(cv, HAND, y=992, spread=108 * f, sc=.9 * f)
    elif hand_mode == 'strip':
        hy.hand(cv, HAND, y=1052, spread=108 * f, sc=.9 * f)
    return cv, w


def small(cv_or_img, size=(1280, 720)):
    im = to_img(finish(cv_or_img, vig=.38, scan=.07, fringe=1.5)) if isinstance(cv_or_img, Cv) else cv_or_img
    return im.resize(size, Image.LANCZOS)


def f_07a_1280():
    cv0, w = forecast_scene(1.0)
    naive = small(cv0)
    cv1, w = forecast_scene(1.3, hand_mode='strip')
    ruled = small(cv1)
    ruled.save(CLD + '07a_1280_clean.jpg', quality=93, subsampling=0)
    naive.save(CLD + '07a_1280_naive.jpg', quality=93, subsampling=0)
    # the board: 1:1 crops of the 1280 renders side by side + the rules list
    box = (150, 250, 1050, 720)
    cn, cr = naive.crop(box), ruled.crop(box)
    sheet = Image.new('RGB', (W, H), (8, 6, 20))
    sheet.paste(cn, (40, 120))
    sheet.paste(cr, (980, 120))
    d = ImageDraw.Draw(sheet)
    f1, f2, f3 = font(34, False, 800, 75), font(24, False, 560, 78), font(22, False, 560, 78)
    d.text((40, 24), '07a  1280 x 720  ·  1:1 crops (HOME, the t1 cluster, the hand)', font=f1, fill=(240, 243, 255))
    d.text((40, 76), 'LEFT: the 1920 frame shrunk to 1280 (marks 67%)     RIGHT: 1280 layout with the UI floors applied', font=f2, fill=(160, 170, 205))
    rules = ['FLOORS (px at 1280):  glyph >= 24   tile >= 52 wide   ribbon >= 12 wide   head >= 30   text >= 24   tap/stick target >= 44',
             '1  marks scale x1.3 against the city, so the world shrinks to 67% but the grammar does not',
             '2  tile fan min distance 66 -> 86 px; two lanes max; idle Sites collapse (H2 rules, unchanged)',
             '3  the 12-mark tally becomes 4 glyph x count groups (the full row returns on HOME focus)',
             '4  the hand is a tab strip (type tab + verb glyph visible, 62 px); the focused card lifts to full',
             '5  pass-through dots, "?" chips, pair read-outs and prompt pills exist only on focus, never idle',
             '6  at most two dashed previews at once; the second replaces the first on scrub']
    y = 120 + 470 + 30
    for i, t in enumerate(rules):
        d.text((40, y + i * 40), t, font=(f2 if i else f1), fill=((240, 243, 255) if i else (255, 255, 255)))
    d.text((40, 120 + 470 + 6), '', font=f3)
    d.rounded_rectangle((38, 118, 40 + 900, 120 + 470), 6, outline=(160, 170, 205), width=2)
    d.rounded_rectangle((978, 118, 980 + 900, 120 + 470), 6, outline=(255, 255, 255), width=2)
    sheet.save(FRD + '07a_layout_1280_board.jpg', quality=93, subsampling=0)
    # annotated native 1280 frame
    an = Ann()
    an.title('07a-2  1280 x 720 native (rules applied)')
    img = ruled
    img = ImageDraw.Draw(img)  # no-op: keep clean; annotations live on the board
    ruled.save(FRD + '07a_layout_1280_native.jpg', quality=93, subsampling=0)
    print('saved 07a')


import extcity as EX


def finish_arr(a, vig=.38, scan=.07, fringe=1.5, seed=3):
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = a * (1 - vig * np.clip(d - .55, 0, 1.2) ** 1.6)[..., None]
    sh = int(round(fringe))
    k = np.clip(np.clip(d - .75, 0, 1) * 2.2, 0, 1)
    r_ = np.roll(a[..., 0], sh, 1); b_ = np.roll(a[..., 2], -sh, 1)
    a[..., 0] = a[..., 0] * (1 - k) + r_ * k
    a[..., 2] = a[..., 2] * (1 - k) + b_ * k
    a = a * (1 - scan * (np.mod(yy, 3) == 0))[..., None]
    return np.clip(a, 0, 1)


def put(dst, src, x, y):
    """add src (h,w,3) into dst at (x,y), clipped."""
    h, w = src.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    dst[y0:y1, x0:x1] += src[y0 - y:y1 - y, x0 - x:x1 - x]


def scale_delta(d, s):
    im = Image.fromarray(np.clip(d * .5 + .5, 0, 1).__mul__(255).astype(np.uint8))
    h, w = d.shape[:2]
    im = im.resize((int(round(w * s)), int(round(h * s))), Image.LANCZOS)
    return (np.asarray(im, np.float32) / 255 - .5) * 2


def chipnote(dr, xy, text):
    f2 = font(22, False, 560, 78)
    wd = dr.textlength(text, font=f2) + 22
    dr.rounded_rectangle((xy[0], xy[1], xy[0] + wd, xy[1] + 36), 8, fill=(10, 12, 30), outline=(246, 241, 228), width=2)
    dr.text((xy[0] + 11, xy[1] + 7), text, font=f2, fill=(240, 243, 255))


def f_07b_safe():
    base = base_city('default')
    # world-only and ui-only deltas from the 1920 design frame (scale 1.15 for 4:3, 1.0 for ultrawide)
    out = {}
    for tag, f in (('43', 1.15), ('uw', 1.0)):
        cw, w = forecast_scene(f, hud=False, hand_mode='none')
        cu, w = forecast_scene(f, hud=True, hand_mode='fan' if tag == 'uw' else 'none')
        out[tag] = (cw.img - base, cu.img - cw.img)
    # ---- 4:3 1440x1080
    city, box = EX.extended(722, 500, 1.125, 1440, 1080)
    img = city.copy()
    wd, ud = out['43']
    put(img, scale_delta(wd, .75), 0, 135)
    # HUD chips pinned to the 1440 box corners: left chips as is, right chips shifted -480
    put(img, ud[0:90, 0:430], 0, 0)
    put(img, ud[0:90, 1580:1920], 1440 - 340, 0)
    # hand band on the freed rows (soft ink floor so the cards read)
    cvh = Cv(np.zeros((H, W, 3), np.float32))
    cvh.img[:, 240:1680] = img
    yy = np.clip((np.arange(H) - 880) / 160.0, 0, 1)[:, None, None]
    cvh.img *= (1 - .55 * yy)
    hy.hand(cvh, HAND, y=968, spread=120, sc=1.0)
    slots(cvh, (1560, 968), [('SHIFT', 'E'), None], k=.95)
    im43 = Image.fromarray((finish_arr(cvh.img[:, 240:1680].copy()) * 255 + .5).astype(np.uint8))
    im43.save(CLD + '07b_43_clean.jpg', quality=93, subsampling=0)
    a = im43.copy(); dr = ImageDraw.Draw(a)
    chipnote(dr, (20, 100), '4:3 1440 x 1080: real city, camera zoom x0.75 so HQ and HOME both fit')
    chipnote(dr, (20, 800), 'the freed band under the map carries the hand and guard slots')
    chipnote(dr, (20, 1032), 'HUD chips pinned to the 1440 box corners')
    a.save(FRD + '07b_safe_4x3.jpg', quality=93, subsampling=0)
    # ---- ultrawide 2560x1080: raw window [0,1707]; the P2 centre sits at x+123
    city, box = EX.extended(853.5, 500, 1.5, 2560, 1080)
    img = city.copy()
    wd, ud = out['uw']
    put(img, wd, box[0], 0)
    put(img, ud, 320, 0)
    imu = Image.fromarray((finish_arr(img) * 255 + .5).astype(np.uint8))
    imu.save(CLD + '07c_ultrawide_clean.jpg', quality=93, subsampling=0)
    au = imu.copy(); dr = ImageDraw.Draw(au)
    for x in (320, 2240):
        for y in range(0, H, 16):
            dr.line([(x, y), (x, y + 8)], fill=(255, 255, 255), width=2)
    chipnote(dr, (360, 100), 'central 16:9 = the design frame; HUD and hand pinned to it')
    chipnote(dr, (20, 520), 'real city continues (left: the river bank)')
    chipnote(dr, (2250 - 330, 520), 'real city continues (right: district)')
    au.save(FRD + '07c_safe_ultrawide.jpg', quality=93, subsampling=0)
    # ---- nesting diagram
    board = Image.new('RGB', (W, H), (8, 6, 20))
    board.paste(imu.resize((1920, 810), Image.LANCZOS), (0, 135))
    dr = ImageDraw.Draw(board)
    def dbox(x0, y0, x1, y1, col):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        for a_, b_ in zip(pts[:-1], pts[1:]):
            L = math.hypot(b_[0] - a_[0], b_[1] - a_[1]); u = ((b_[0] - a_[0]) / L, (b_[1] - a_[1]) / L); t = 0
            while t < L:
                dr.line([(a_[0] + u[0] * t, a_[1] + u[1] * t), (a_[0] + u[0] * min(t + 10, L), a_[1] + u[1] * min(t + 10, L))], fill=col, width=3); t += 18
    dbox(240, 135, 1680, 945, (255, 255, 255)); dbox(420, 135, 1500, 945, (127, 239, 255))
    dr.text((20, 20), '07d  SAFE AREAS  ·  one design frame, three screens', font=font(34, False, 800, 75), fill=(240, 243, 255))
    chipnote(dr, (250, 150), '16:9 design frame (1920 x 1080; also 1280 x 720)')
    chipnote(dr, (430, 196), '4:3 guaranteed box: HOME, all Sites, HUD chips')
    chipnote(dr, (130, 960), 'ultrawide: the real city continues, no UI')
    board.save(FRD + '07d_safe_areas.jpg', quality=93, subsampling=0)
    print('saved 07b-d')


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_0')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
