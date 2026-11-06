"""P1 sequence 7: 1280x720 layout, 4:3 and ultrawide safe areas, declutter rules.   python ix_e.py [name ...]"""
import sys, time
from ix_lib import *
from ix_lib import _brackets
from ix_b import SLOT_C, slots


def tally_grouped(cv, c, tiers, r=20, k=1.0, gap=64):
    """the 1280 form of the tally: one glyph per tier GROUP with its count (12 marks -> 4 glyphs), grease numerals."""
    cnt = counts_of(tiers)
    groups = [t for t in TIERS if cnt.get(t)]
    x0 = c[0] - (len(groups) - 1) * gap / 2
    for i, t in enumerate(groups):
        p = (x0 + i * gap, c[1])
        hy.waxy_glyph(cv, (p[0] - 12, p[1]), lambda l, c_, r_, t=t: g_tier(l, t, c_, r_), r, TIER[t], 3 + i, k)
        ui.ntext(cv, (p[0] + 18, p[1] + 2), str(cnt[t]), int(r * 1.5), TIER[t], anchor='lm', stroke=3, k=k)


def forecast_scene(f=1.0, tally_mode='marks', hand_mode='fan'):
    """the forecast frame (as H2 04) with every mark scaled by f (the UI floor for small screens)."""
    w = World('default')
    cv = new_canvas(w)
    sealed_layers(cv, w, k=.85)
    stops = {}
    for r in KN:
        R = w.routes[r]
        P = PX(R['path'])
        s_stop = w.visit(r, TARGET[r][0])
        stops[r] = s_stop
        hy.ribbon(cv, P, R['typ'], R['ext'], s_stop + 20, k=1.0, w=9.0 * f)
        hy.dead_trail(cv, P, s_stop + 40, P.L - 4)
    for r in KN:
        hy.target_ring(cv, w.sites[TARGET[r][0]]['B'], TARGET[r][1], r=46 * f)
    draw_world(cv, w, {'t1_a': 'DOWN'}, PROGRAMS, home_kw=dict(hp=44, preview=6), idle=IDLE)
    for r in KN:
        R = w.routes[r]
        P = PX(R['path'])
        hy.stop_block(cv, P, stops[r] - 2, TARGET[r][1], length=44 * f, half=17 * f)
        hy.head(cv, P, R['ext'] + RUN[r], R['typ'], sc=1.8 * f)
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
    hm = w.home
    if tally_mode == 'marks':
        hy.tally(cv, (hm[0] + 10, hm[1] + 150), TALLY, r=17 * f, gap=34 * f, group_gap=14 * f)
    else:
        tally_grouped(cv, (hm[0] + 60, hm[1] + 150), BASE12, r=20 * f, gap=int(92 * f))
    locks(cv, w)
    hunter(cv, w)
    hy.hud(cv, 44, 50, 80, 8, 0)
    if hand_mode == 'none':
        pass
    elif hand_mode == 'fan':
        hy.hand(cv, HAND, y=992, spread=108 * f, sc=.9 * f)
    else:
        hy.hand(cv, HAND, y=1052, spread=108 * f, sc=.9 * f)
    return cv, w


def small(cv_or_img, size=(1280, 720)):
    im = to_img(finish(cv_or_img, vig=.38, scan=.07, fringe=1.5)) if isinstance(cv_or_img, Cv) else cv_or_img
    return im.resize(size, Image.LANCZOS)


def f_07a_1280():
    cv0, w = forecast_scene(1.0)
    naive = small(cv0)
    cv1, w = forecast_scene(1.3, tally_mode='groups', hand_mode='strip')
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


def ultrawide_from(im, extra=320):
    """mock the extra world at the sides of a 16:9 frame: mirrored, blurred, darkened, fading to the night. NOT game content:
    the real build shows more of the city there. Returns a (W + 2 extra) x H image."""
    out = Image.new('RGB', (W + 2 * extra, H), (7, 5, 21))
    out.paste(im, (extra, 0))
    for side in (0, 1):
        strip = im.crop((0, 0, extra, H)) if side == 0 else im.crop((W - extra, 0, W, H))
        strip = strip.transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(5))
        a = np.asarray(strip, np.float32)
        x = np.linspace(0, 1, extra)[None, :, None]
        fade = (1 - x) if side == 0 else x
        fade = (1 - (1 - fade)) if False else fade
        k = (.62 * (1 - fade) + .1 * fade) if True else fade
        # fade from 62% at the seam to 10% at the screen edge
        seam = (np.linspace(0, 1, extra)[None, :, None])
        if side == 0:
            k = .62 - .52 * (1 - seam)          # left: x=0 is the screen edge (flipped strip: edge at 0)
            k = .1 + .52 * seam
        else:
            k = .62 - .52 * seam
        a = a * k
        out.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), (0 if side == 0 else extra + W, 0))
    return out


def f_07b_safe():
    cv, w = forecast_scene(1.15, tally_mode='groups', hand_mode='none')
    clean_cv = cv
    im16 = to_img(finish(cv, vig=.38, scan=.07, fringe=1.5))
    # ---- 4:3 (1440 x 1080): the map zoomed out to fit the route's width, the freed 270 px under it carry the hand
    map43 = im16.resize((1440, 810), Image.LANCZOS)
    cvh = Cv(np.zeros((H, W, 3), np.float32) + np.array([.03, .02, .08], np.float32))
    hy.hand(cvh, HAND, y=948, spread=120, sc=1.0)
    slots(cvh, (1560, 948), [('SHIFT', 'E'), None], k=.95)
    band = to_img(cvh.out()).crop((240, 810, 1680, 1080))
    im43 = Image.new('RGB', (1440, 1080), (7, 5, 21))
    im43.paste(map43, (0, 0))
    im43.paste(band, (0, 810))
    d = ImageDraw.Draw(im43)
    d.line([(0, 810), (1440, 810)], fill=(60, 70, 110), width=2)
    im43.save(CLD + '07b_43_clean.jpg', quality=93, subsampling=0)
    a43 = Ann()
    a43.items = []
    # ---- ultrawide (2560 x 1080)
    cvu, w = forecast_scene(1.0)
    im_u = ultrawide_from(to_img(finish(cvu, vig=.38, scan=.07, fringe=1.5)))
    im_u.save(CLD + '07c_ultrawide_clean.jpg', quality=93, subsampling=0)
    # annotated 4:3
    f2 = font(22, False, 560, 78)
    def chip(dr, xy, text):
        wd = dr.textlength(text, font=f2) + 22
        dr.rounded_rectangle((xy[0], xy[1], xy[0] + wd, xy[1] + 36), 8, fill=(10, 12, 30), outline=(246, 241, 228), width=2)
        dr.text((xy[0] + 11, xy[1] + 7), text, font=f2, fill=(240, 243, 255))
    a = im43.copy()
    dr = ImageDraw.Draw(a)
    chip(dr, (20, 80), '4:3 1440 x 1080: the camera zooms OUT x0.75 so HQ and HOME both fit')
    chip(dr, (20, 826), 'the freed 270 px band carries the hand + guard slots: nothing overlaps the map')
    chip(dr, (20, 1032), 'HUD chips stay pinned to the 1440 box corners')
    a.save(FRD + '07b_safe_4x3.jpg', quality=93, subsampling=0)
    # annotated ultrawide
    au = im_u.copy()
    dr = ImageDraw.Draw(au)
    for x in (320, 2240):
        for y in range(0, H, 16):
            dr.line([(x, y), (x, y + 8)], fill=(255, 255, 255), width=2)
    chip(dr, (360, 80), 'central 16:9 (1920) = the design frame: every interaction lives here')
    chip(dr, (20, 520), 'extra world: mood only')
    chip(dr, (2290, 520), 'extra world: mood only')
    chip(dr, (360, 1032), 'HUD pinned to the 16:9 box, not to the screen edge (eyes stay near the action)')
    au.save(FRD + '07c_safe_ultrawide.jpg', quality=93, subsampling=0)
    # the nesting diagram: ultrawide scaled to 1920 wide, boxes for 16:9, 4:3 and the 1280 minimum
    s = 1920 / 2560
    board = Image.new('RGB', (W, H), (8, 6, 20))
    uw = im_u.resize((1920, 810), Image.LANCZOS)
    board.paste(uw, (0, 135))
    dr = ImageDraw.Draw(board)
    def dbox(x0, y0, x1, y1, col, text, ty):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        for a_, b_ in zip(pts[:-1], pts[1:]):
            L = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
            u = ((b_[0] - a_[0]) / L, (b_[1] - a_[1]) / L)
            t = 0
            while t < L:
                dr.line([(a_[0] + u[0] * t, a_[1] + u[1] * t), (a_[0] + u[0] * min(t + 10, L), a_[1] + u[1] * min(t + 10, L))], fill=col, width=3)
                t += 18
        if text:
            chip(dr, (x0 + 10, ty), text)
    dbox(240, 135, 1680, 945, (255, 255, 255), '', 0)
    dbox(420, 135, 1500, 945, (127, 239, 255), '', 0)
    dbox(120, 135 + 40, 1800, 945 - 40, (246, 241, 228), '', 0)
    dr.text((20, 20), '07d  SAFE AREAS  ·  one design frame, three screens', font=font(34, False, 800, 75), fill=(240, 243, 255))
    chip(dr, (250, 150), '16:9 design frame  (1920 x 1080, also scaled to 1280 x 720)')
    chip(dr, (430, 196), '4:3 guaranteed box: HOME, all Sites, HUD chips')
    chip(dr, (130, 960), 'ultrawide 21:9 / 32:9: the world continues, no UI')
    chip(dr, (20, 1020), 'title safe 5%: no text or chip outside the white box on TVs; cards and discs sit inside the 4:3 box x-range')
    board.save(FRD + '07d_safe_areas.jpg', quality=93, subsampling=0)
    print('saved 07b-d')


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_0')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
