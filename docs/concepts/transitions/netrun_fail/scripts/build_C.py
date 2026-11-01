"""Design C: Solace security-ops intrusion printout (the corp's own trace report) over the dimmed street."""
from nf_lib import *

PAPER = (233, 238, 224, 255)
BAR = (208, 226, 200, 255)
PINK_INK = (255, 62, 160, 255)
INKD = (22, 36, 28, 255)
RED_INK = (205, 40, 40, 255)


def backdrop():
    a = to_f(street_img(1.55, 0.62, 0.60))
    a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.5)), np.float32) / 255
    a = grade(a, 0.52, 0.45, (1.12, 0.86, 0.98))
    # two slow searchlight beams from the top (Heat feedback, GDD 9.4), red and pink
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for (x_top, x_bot, wid, col, k) in ((300, 120, 90, (1.0, .18, .22), .20), (1630, 1850, 80, (1.0, .24, .62), .16)):
        xc = x_top + (x_bot - x_top) * yy / H
        w_ = wid * (0.5 + yy / H)
        beam = np.exp(-((xx - xc) / w_) ** 2) * k * (1 - 0.45 * yy / H)
        a = a + beam[..., None] * np.array(col, np.float32)
    a = scan_f(a, 0.07)
    a = vignette_f(a, 0.55, 0.5)
    return a


def burn(L, cx, cy, R):
    h, w = L.size[1], L.size[0]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - cx * K, yy - cy * K
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    rr = R * K * (1 + 0.22 * np.sin(3 * th + 1) + 0.14 * np.sin(5 * th + 2) + 0.08 * np.sin(9 * th + .5))
    hole = r < rr
    band = 42 * K
    t = np.clip((rr + band - r) / band, 0, 1)
    rim = (r >= rr) & (r < rr + band)
    arr = np.asarray(L).astype(np.float32).copy()
    char = np.array([34, 20, 12], np.float32)
    tt = (t ** 1.3)[..., None]
    arr[..., :3] = np.where(rim[..., None], arr[..., :3] * (1 - tt) + char * tt, arr[..., :3])
    ember = (r >= rr) & (r < rr + 4.5 * K)
    arr[..., :3] = np.where(ember[..., None], np.array([255, 130, 36], np.float32), arr[..., :3])
    arr[..., 3] = np.where(hole, 0, arr[..., 3])
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')


def build():
    ph = PHR()
    bgf = backdrop()
    bg_only = to_img(bgf)
    img = up2(bg_only)

    # ---------------- paper (800 x 1060, hangs from the printer slot, runs off the bottom). One 33 px line grid.
    PW, PH_ = 800, 1060
    G, Y0 = 33, 196
    P = layer(PW, PH_)
    rect(P, [0, 0, PW, PH_], fill=PAPER)
    for k in range(0, 40):                       # greenbar: 3 lines on, 3 lines off, aligned to the text grid
        if k % 2 == 1:
            rect(P, [44, Y0 - 2 + k * 3 * G, PW - 44, Y0 - 2 + (k + 1) * 3 * G], fill=BAR)
    a_ = np.asarray(P).astype(np.float32)
    n = V2.noise_img(a_.shape[1], a_.shape[0], 5, 1.0) * 26
    a_[..., :3] = np.clip(a_[..., :3] + n[..., None], 0, 255)
    P = Image.fromarray(a_.astype(np.uint8), 'RGBA')
    for side in (22, PW - 22):                   # tractor strips
        for y in range(40, PH_, 36):
            ellipse(P, [side - 7, y - 7, side + 7, y + 7], fill=(40, 52, 46, 255))
            ellipse(P, [side - 7, y - 7, side + 7, y + 7], outline=(120, 130, 120, 255), width=1)
    for xline in (44, PW - 44):
        for y in range(0, PH_, 8):
            line(P, [xline, y, xline, y + 4], (150, 160, 150, 255), 1)

    fb = font('courierb', 23)
    fr = font('courier', 22)
    xL = 66
    CW = 13.2
    V2.crest(P, xL + 28, 66, 26, color=(30, 120, 40, 255), w=3)
    text(P, (xL + 70, 36), 'SOLACE BIOSYSTEMS', font('anton', 44), INKD)
    text(P, (xL + 70, 88), 'SECURITY OPS // INTRUSION TRACE REPORT', fb, INKD)
    line(P, [xL, 138, PW - 66, 138], INKD, 2)
    text(P, (xL, 146), 'INTRUSION TERMINATED', font('anton', 56), INKD)
    vx = xL + 16 * CW + 6

    def R(n):
        return Y0 + n * G

    def rowt(n, l, v, col=INKD, bold=False):
        text(P, (xL, R(n)), l.ljust(15, '.') + ' ', fr, INKD)
        text(P, (vx, R(n)), v, fb if bold else fr, col)

    def hdr(n, s_):
        text(P, (xL, R(n)), s_, fb, INKD)
        line(P, [xL, R(n) + 29, xL + len(s_) * 13.9, R(n) + 29], INKD, 1.5)

    def phv(n, nch, k):
        ph.add([vx - 4, R(n) - 3, vx + nch * CW + 6, R(n) + 29], k)

    rowt(2, 'SITE', 'SEED VAULT EXCHANGE')
    rowt(3, 'SUBJECT', 'CELL-9 // BREAKER  R1'); phv(3, 21, 9)
    rowt(4, 'STATUS', 'FLATLINED  HP 0/60', RED_INK, bold=True)
    rowt(5, 'REACHED', 'ELITE ROUTER 5 OF 7'); phv(5, 19, 1)
    rowt(6, 'CAUSE', 'THE ADJUSTER, TURN 2'); phv(6, 20, 2)
    hdr(8, 'LOST WITH SUBJECT (UNBANKED)')
    for i, (l, v) in enumerate(FACTS['lost']):
        rowt(9 + i, l, v)
    ph.add([xL - 6, R(9) - 4, xL + 24 * CW, R(13) + 29], 3)
    hdr(15, 'NOT REACHED')
    rowt(16, 'BANKED ASSETS', 'SCHEMATICS, ARMORY'); phv(16, 18, 9)
    rowt(17, 'HOME SERVER', '50/50  NOT BREACHED'); phv(17, 19, 6)
    rowt(18, 'CELL ROSTER', '4 -> 3 OPERATIVES'); phv(18, 17, 5)
    text(P, (xL, R(20)), 'EXPOSURE (HEAT)  52 -> 63   +10 +1 TIER', fb, INKD)
    ph.add([xL + 17 * 13.9, R(20) - 3, xL + 40 * 13.9, R(20) + 29], 4)
    bx0, bx1 = xL, PW - 70
    bw = bx1 - bx0
    yb = R(21) + 6
    rect(P, [bx0, yb, bx1, yb + 26], outline=INKD, width=2)
    rect(P, [bx0 + 2, yb + 2, bx0 + bw * .52, yb + 24], fill=INKD)
    xa, xb = bx0 + bw * .52, bx0 + bw * .63
    rect(P, [xa, yb + 2, xb, yb + 24], fill=RED_INK)
    for kx in range(int(xa), int(xb) + 24, 7):
        line(P, [kx, yb + 24, kx + 22, yb + 2], (233, 238, 224, 255), 2)
    for v in (25, 50, 75):
        line(P, [bx0 + bw * v / 100, yb - 6, bx0 + bw * v / 100, yb + 32], INKD, 2)
        text(P, (bx0 + bw * v / 100, yb + 33), str(v), font('courier', 20), INKD, 'ma')
    line(P, [xL, R(23) - 4, PW - 66, R(23) - 4], INKD, 2)
    text(P, (xL, R(23) + 4), 'FILED AUTOMATICALLY. NO APPEAL OFFERED.', fr, INKD)
    yk = R(24) + 12
    for i in range(70):                                       # barcode
        bwid = 2 + (i * 7 % 5)
        xk = xL + i * 9
        if xk + bwid < PW - 70 and i % 3 != 2:
            rect(P, [xk, yk, xk + bwid, yk + 56], fill=INKD)

    # one stamp in red ink, over the short rows
    stamp(P, 'TRACE BURNED', 578, R(11) + 6, RED_INK, rot=-8, size=46)
    # lamp-lit paper: bright at the top where it leaves the printer, falling off down the sheet and at the edges
    arr = np.asarray(P).astype(np.float32)
    hh, ww = arr.shape[:2]
    gy = (0.90 - 0.52 * np.linspace(0, 1, hh) ** 1.2)[:, None]
    gx = (1.0 - 0.22 * (np.abs(np.linspace(-1, 1, ww)) ** 2.2))[None, :]
    arr[..., :3] *= (gy * gx)[..., None]
    P = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    # the burn, then paste (printer slot cut-in at the top, soft drop shadow)
    P = burn(P, PW - 56, 84, 50)
    cx, cy = 960, 40 + PH_ / 2
    sh = P.split()[3].filter(ImageFilter.GaussianBlur(S(18)))
    s_ = Image.new('RGBA', P.size, (0, 0, 0, 0))
    s_.putalpha(sh.point(lambda v: int(v * 0.60)))
    r_ = s_.rotate(-1.2, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(r_, (int(cx * K - r_.width / 2 + S(16)), int(cy * K - r_.height / 2 + S(22))))
    rotate_paste(img, P, cx, cy, -1.2, shadow=False)

    # printer mouth over the top of the paper
    rect(img, [440, -10, 1480, 46], fill=(8, 8, 14, 255))
    rect(img, [440, 40, 1480, 52], fill=(30, 32, 44, 255))
    rect(img, [440, 52, 1480, 58], fill=(0, 0, 0, 120))
    ellipse(img, [470, 16, 486, 32], fill=(255, 60, 70, 255))
    text(img, (502, 12), 'TRACE PRINTER  //  SB-SEC', font('mono', 20), LO)
    text(img, (1450, 12), 'DONE', font('mono', 20), LO, 'ra')

    # the Cell's note, taped to the report (ours: yellow pencil on a post-it)
    V2.postit(img, [1300, 600, 1560, 760], (255, 226, 80, 255), 'one down.\nthe cell holds.', rot=5, size=34, fg=(40, 40, 140, 255))
    V2.tape(img, 1430, 600, rot=-8, w=100, h=30)
    ph.add([1316, 622, 1546, 744], 7)

    # exit
    sticker(img, 'GRID VIEW', 1650, 960, 270, 58, PINK, None, rot=-1.5, size=38)
    text(img, (1862, 950), '[G]', font('mono', 22), LO, 'ra')
    ph.add([1508, 926, 1800, 996], 8)

    full = down(grain(img, 3, 1))
    full = to_img(scan_f(to_f(full), 0.06))
    return bg_only, full, ph.items
