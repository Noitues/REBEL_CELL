"""f1_checks: squint / grey / CVD / crop sheets / before-after for the F1 plate set.  python f1_checks.py"""
import sys, os, json, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import wr2_lib as W2L

OUT = 'D:/rc_scratch/combat_redesign/locked/wheel/out/'
DEL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/xerox_flyer/'
E10F = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/'
E10A = 'D:/rc_tmp/combat_critic/plates/waves_e10/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
mo = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 18)
an = ImageFont.truetype(FD + 'Anton-Regular.ttf', 28)
C = (536, 540)


def load(n, base=OUT):
    return Image.open(base + n + '.png').convert('RGB')


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def squint(img, region=None):
    s = img.resize((img.width // 16, img.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    a = np.asarray(s, np.float32) / 255.0
    l = lum(a)
    if region is not None:
        yy, xx = np.mgrid[0:l.shape[0], 0:l.shape[1]]
        m = region(xx * 16 + 8, yy * 16 + 8)
        l = l[m]
    return dict(mean=round(float(l.mean()), 4), p95=round(float(np.percentile(l, 95)), 4), loud=round(float((l > 0.38).mean()), 4))


REG = {
    'plate': None,
    'board_disc_r<=490': lambda x, y: np.hypot(x - C[0], y - C[1]) <= 490,
    'tower_r<=212': lambda x, y: np.hypot(x - C[0], y - C[1]) <= 212,
    'rings_r214-430': lambda x, y: (np.hypot(x - C[0], y - C[1]) >= 214) & (np.hypot(x - C[0], y - C[1]) <= 430),
    'hand_zone': lambda x, y: (x >= 880) & (x <= 1660) & (y >= 780),
    'send_it': lambda x, y: (x >= 1660) & (x <= 1900) & (y >= 900) & (y <= 1020),
    'tower_r<=190': lambda x, y: np.hypot(x - C[0], y - C[1]) <= 190,
    'rings_r214-385': lambda x, y: (np.hypot(x - C[0], y - C[1]) >= 214) & (np.hypot(x - C[0], y - C[1]) <= 385),
    'hud': lambda x, y: (x >= 1070) & (y <= 400),
}


def label(im, text, xy=(8, 4), col=(255, 226, 0)):
    d = ImageDraw.Draw(im)
    d.text(xy, text, font=mo, fill=col)


def run():
    os.makedirs(DEL, exist_ok=True)
    rep = {}
    plates = ['p1_decide', 'p1_nowords', 'p2_preview', 'p2b_hover', 'p3_resolve']
    e10map = {'p1_decide': 'p1_decide', 'p1_nowords': 'p1_nowords', 'p2_preview': 'p2_preview', 'p2b_hover': 'p2b_hover', 'p3_resolve': 'p3_resolve'}
    # ---- squint metrics (1/16 BOX + 1 px blur, luminance; loud = cells above 0.38)
    sq = {}
    for n in plates:
        if not os.path.exists(OUT + n + '.png'):
            continue
        new = load(n)
        old = load(e10map[n], E10F)
        sq[n] = {rn: dict(f1=squint(new, rf), e10=squint(old, rf)) for rn, rf in REG.items()}
    rep['squint'] = sq
    # ---- 320 px squint (colour + grey) and the 1/16 blur image
    names = [n for n in plates if os.path.exists(OUT + n + '.png')]
    W3, H3 = 960, 540
    sheet = Image.new('RGB', (W3 * 2, 60 + len(names[:2]) * (H3 + 10)), (10, 12, 20))
    d = ImageDraw.Draw(sheet)
    d.text((16, 14), 'F1 squint: 320 px wide, colour (left) and luminance only (right), shown at 3x nearest', font=an, fill=(255, 255, 255))
    y = 60
    for n in names[:2]:
        im = load(n)
        s = im.resize((320, 180), Image.LANCZOS)
        col = s.resize((W3, H3), Image.NEAREST)
        gr = s.convert('L').convert('RGB').resize((W3, H3), Image.NEAREST)
        sheet.paste(col, (0, y)); sheet.paste(gr, (W3, y))
        label(sheet, n + ' 320 px colour', (8, y + 4)); label(sheet, n + ' 320 px grey', (W3 + 8, y + 4))
        y += H3 + 10
    sheet.save(DEL + 'squint_320_colour_grey.jpg', quality=90)
    s16 = Image.new('RGB', (1920, 560), (10, 12, 20))
    for i, n in enumerate(names[:2]):
        im = load(n)
        t = im.resize((120, 67), Image.BOX).filter(ImageFilter.GaussianBlur(1.0)).resize((960, 536), Image.NEAREST)
        s16.paste(t, (i * 960, 20))
        label(s16, n + ' 1/16 box + 1 px blur (what the metrics read)', (i * 960 + 8, 0))
    s16.save(DEL + 'squint_1_16_blur.jpg', quality=90)
    # ---- CVD sheet: deutan / protan / tritan on p1 and p2b
    cn = [n for n in ('p1_decide', 'p2b_hover') if os.path.exists(OUT + n + '.png')]
    sh = Image.new('RGB', (1920, 40 + len(cn) * 4 * 360), (10, 12, 20))
    d = ImageDraw.Draw(sh)
    d.text((16, 6), 'F1 colour-blind sheet (Machado 1.0): normal | deutan | protan | tritan', font=an, fill=(255, 255, 255))
    y = 40
    for n in cn:
        im = load(n)
        tiles = [im, W2L.sim_cb(im, 'deutan'), W2L.sim_cb(im, 'protan'), W2L.sim_cb(im, 'tritan')]
        names_ = ['normal', 'deutan', 'protan', 'tritan']
        for i, t in enumerate(tiles):
            tt = t.resize((960, 540), Image.LANCZOS)
            sh.paste(tt.crop((0, 0, 960, 360)) if False else tt.resize((960, 540)), (0, 0)) if False else None
        # 2 x 2 grid per plate at 960 x 540
        grid = Image.new('RGB', (1920, 1080), (10, 12, 20))
        for i, t in enumerate(tiles):
            grid.paste(t.resize((960, 540), Image.LANCZOS), ((i % 2) * 960, (i // 2) * 540))
            label(grid, n + ' ' + names_[i], ((i % 2) * 960 + 8, (i // 2) * 540 + 4))
        grid.save(DEL + 'cvd_%s.jpg' % n, quality=90)
    # ---- before / after
    if os.path.exists(OUT + 'p1_decide.png'):
        a = load('p1_decide', E10F)
        b = load('p1_decide')
        ba = Image.new('RGB', (1920, 580), (10, 12, 20))
        ba.paste(a.resize((960, 540), Image.LANCZOS), (0, 40))
        ba.paste(b.resize((960, 540), Image.LANCZOS), (960, 40))
        label(ba, 'BEFORE: E10 p1_decide (combat_e10_design/final)', (8, 8)); label(ba, 'AFTER: F1 black-book burner p1_decide', (968, 8))
        ba.save(DEL + 'before_after_p1.jpg', quality=92)
    # ---- 2x crop sheet: wheel / hand / HP / time marks (p1)
    if os.path.exists(OUT + 'p1_decide.png'):
        im = load('p1_decide')
        pan = [
            ('WHEEL  (tower r196, trim r200-210, rings NOW/+1/+2)', (296, 296, 776, 776), 2),
            ('HAND  (1.15x, 4 deg fan) + SEND IT', (850, 770, 1900, 1075), 2),
            ('HP  (hub ring r52-64 | YOU strip | slice pips)', (1066, 90, 1420, 150), 3),
            ('HP  hub ring + pips', (440, 440, 640, 640), 4),
            ('TIME MARKS  (END notch | pip | 2 pips on trim, tickets, arcs, tags)', (560, 60, 960, 360), 3),
            ('TICKETS  (W6 50 | W5 70 | W4 100 percent) + L5 feed', (14, 14, 340, 110), 4),
        ]
        tiles = []
        for t, box, k in pan:
            c = im.crop(box)
            c = c.resize((c.width * k, c.height * k), Image.LANCZOS)
            tiles.append((t, c))
        Wd = 3840
        rows = [[0], [1], [2, 3], [4, 5]]
        ys = 0
        parts = []
        for r in rows:
            rh = max(tiles[i][1].height for i in r) + 36
            parts.append((r, ys, rh))
            ys += rh
        sh = Image.new('RGB', (Wd, ys), (10, 12, 20))
        for r, y0, rh in parts:
            x = 0
            for i in r:
                t, c = tiles[i]
                sh.paste(c, (x, y0 + 30))
                label(sh, t, (x + 6, y0 + 4))
                x += c.width + 16
        sh.save(DEL + 'crops_2x.jpg', quality=92)
    # ---- greyscale proof: the tower reads as drawn, the board reads as clean glass (texture energy inside each, laplacian std)
    if os.path.exists(OUT + 'p1_decide.png'):
        im = load('p1_decide')
        g = np.asarray(im.convert('L'), np.float32)
        from scipy import ndimage as ndi
        lap = ndi.laplace(g)
        yy, xx = np.mgrid[0:1080, 0:1920]
        rr = np.hypot(xx - C[0], yy - C[1])
        # slices: pink areas only in r 71..177; board glass: ring cells r 216..270 away from tokens (std of laplacian over the empty glass)
        tw = (rr > 75) & (rr < 175)
        gl = (rr > 220) & (rr < 268)
        rep['grey_texture'] = dict(tower_laplace_std=round(float(lap[tw].std()), 2), board_glass_laplace_std=round(float(lap[gl].std()), 2),
                                   tower_edge_density=round(float((np.hypot(*np.gradient(g))[tw] > 14).mean()), 3), board_edge_density=round(float((np.hypot(*np.gradient(g))[gl] > 14).mean()), 3))
        a = im.crop((296, 296, 776, 776)).convert('L').convert('RGB').resize((960, 960), Image.LANCZOS)
        b = Image.open(OUT + 'p1_decide.png').convert('RGB').crop((520, 150, 1000, 630)).convert('L').convert('RGB').resize((960, 960), Image.LANCZOS)
        gp = Image.new('RGB', (1920 + 16, 1000), (10, 12, 20))
        gp.paste(a, (0, 40)); gp.paste(b, (976, 40))
        label(gp, 'GREY: the tower (rough line, single-direction hatch, block drop = drawn)', (8, 8)); label(gp, 'GREY: the board (perfect arcs, one enamel line, helix = clean glass)', (984, 8))
        gp.save(DEL + 'grey_proof.jpg', quality=92)
    # ---- hand vs machine: how far does an edge wander from a perfect circle?  (std of the edge radius along 30 degrees of arc, after removing the mean)
    if os.path.exists(OUT + 'p1_decide.png'):
        from scipy import ndimage as ndi
        g = np.asarray(load('p1_decide').convert('L'), np.float32)

        def wobble(r0, r1, centres, half=12.0, edge='any'):
            res = []
            for c0 in centres:
                angs = np.radians(np.linspace(c0 - half, c0 + half, 120))
                rs = np.linspace(r0, r1, 90)
                A_, R_ = np.meshgrid(angs, rs)
                xs = C[0] + R_ * np.sin(A_)
                ys = C[1] - R_ * np.cos(A_)
                prof = ndi.map_coordinates(g, [ys, xs], order=1)
                gr = np.abs(np.gradient(ndi.gaussian_filter1d(prof, 1.0, axis=0), axis=0))
                rr = rs[gr.argmax(0)]
                res.append(float(np.std(rr - np.polyval(np.polyfit(np.arange(len(rr)), rr, 1), np.arange(len(rr))))))
            return round(float(np.mean(res)), 2)
        # the tower: outer rim of the six slices (r 170-186); the board: the NOW ring inner edge (r 208-220) and the +1/+2 hairline (r 322-334)
        rep['edge_wobble_px'] = dict(tower_slice_rim=wobble(170, 186, [0, 60, 120, 180, 240, 300], 17), board_ring_now_inner=wobble(208, 220, [30, 90, 150, 210, 270, 330], 17), board_ring_p1_p2_hairline=wobble(322, 334, [30, 90, 150, 210, 270, 330], 17))
    # ---- peak values at 1x per region (luminance p99.5)
    if os.path.exists(OUT + 'p1_decide.png'):
        a = np.asarray(load('p1_decide'), np.float32) / 255.0
        L_ = lum(a)
        yy, xx = np.mgrid[0:1080, 0:1920]
        rr = np.hypot(xx - C[0], yy - C[1])
        regs = {'send_it_slab': (xx >= 1660) & (xx <= 1900) & (yy >= 905) & (yy <= 1015), 'hand_cards': (xx >= 880) & (xx <= 1650) & (yy >= 780) & (yy <= 1075),
                'tower_slices': (rr <= 180) & (rr >= 71), 'rings_cells': (rr >= 214) & (rr <= 385)}
        rep['peak_lum_p99_5_1x'] = {k: round(float(np.percentile(L_[m], 99.5)), 3) for k, m in regs.items()}
        rep['mean_lum_1x'] = {k: round(float(L_[m].mean()), 3) for k, m in regs.items()}
    json.dump(rep, open(DEL + 'checks.json', 'w'), indent=1)
    return rep


if __name__ == '__main__':
    r = run()
    print(json.dumps(r.get('grey_texture'), indent=1))
    for n, v in r['squint'].items():
        print(n, {k: v[k] for k in ('plate', 'board_disc_r<=490')})
