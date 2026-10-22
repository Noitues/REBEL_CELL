"""Shared helpers: fonts, the shipped sticker art, the state ring (a port of RouteOverlay.draw_state_ring), mock route map, legend."""
import math
import sys
sys.path.insert(0, "D:/rc_scratch/solace_v1/nodes/scripts")
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from vec import Doc, circle_pts, arc, rgba
import icons

GODOT = "D:/rc_art/godot_look_bloom"
FONTS = GODOT + "/assets/fonts/"
ROUTE = GODOT + "/assets/netrun/route/"
PLATE = "D:/rc_art/art-pass/docs/concepts/golden_plates/street_decision.png"
OUT = "D:/rc_scratch/solace_v1/nodes/"

# RouteInk / Palette tokens
RING_WALKED = (212, 255, 0)
RING_NEXT = (255, 140, 26)
RING_LATER = (242, 246, 255)
RING_CUT = (130, 138, 152)
KEYLINE = (17, 17, 17)
NIGHT_SKY = (6, 8, 22)
NET_CYAN = (92, 225, 255)
CELL_ACID = (212, 255, 0)
CELL_PINK = (255, 61, 168)
TEXT_HI = (242, 246, 255)
TEXT_MID = (175, 192, 214)
TEXT_LO = (122, 136, 156)
HARM = (255, 68, 51)
PAPER = (242, 238, 228)

STICKER_R = 26.0  # street_route.tres stickers.radius_px at 1080p (the die-cut art is 41.6 px wide)
RING_W = 3.2
KEYLINE_W = 3.0


def font(name, px):
    return ImageFont.truetype(FONTS + name, int(round(px)))


def anton(px):
    return font("Anton-Regular.ttf", px)


def mono(px):
    return font("ShareTechMono-Regular.ttf", px)


def plex(px, medium=False):
    return font("IBMPlexSansCondensed-%s.ttf" % ("Medium" if medium else "Regular"), px)


def marker(px):
    return font("PermanentMarker-Regular.ttf", px)


# ---------------------------------------------------------------------------------------------------------------------
# state ring, in vector form (the same numbers as RouteOverlay.draw_state_ring / StreetRouteOverlay._ring)
# ---------------------------------------------------------------------------------------------------------------------
def ring_doc(state, r=STICKER_R, k=1.0, size=None):
    """A Doc (canvas = 2*(r+14) k) with the state ring centred; returns (doc, centre)."""
    pad = 14 * k
    S = 2 * (r * k + pad)
    d = Doc(S, S, "ring")
    c = S / 2
    ring_r = (r - RING_W * 0.5) * k
    w = RING_W * k
    ink = rgba(KEYLINE + (230,))
    col = {"walked": RING_WALKED, "next": RING_NEXT, "later": RING_LATER, "cut": RING_CUT}[state]
    if state == "next":
        d.circle(c, c, ring_r, None, col + (72,), 9 * k)
        d.circle(c, c, ring_r, None, ink, w * 1.4 + KEYLINE_W * k)
        d.circle(c, c, ring_r, None, col, w * 1.4)
    elif state == "walked":
        for rr in (ring_r - w * 0.55, ring_r + w * 0.55):
            d.circle(c, c, rr, None, ink, w * 0.6 + KEYLINE_W * k * 0.6)
        for rr in (ring_r - w * 0.55, ring_r + w * 0.55):
            d.circle(c, c, rr, None, col, w * 0.55)
    elif state == "later":
        for q in range(12):
            a0 = 360 * q / 12
            a1 = a0 + 360 / 12 * 0.55
            pts = arc(c, c, ring_r, a0, a1, 6)
            d.line(pts, ink, w + KEYLINE_W * k)
            d.line(pts, col, w)
    else:
        for q in range(16):
            a = math.radians(360 * q / 16)
            p = (c + ring_r * math.cos(a), c + ring_r * math.sin(a))
            d.circle(p[0], p[1], w * 0.75 + k, ink)
            d.circle(p[0], p[1], w * 0.6, col)
        s = ring_r * 0.72
        d.line([(c - s, c + s), (c + s, c - s)], ink, w + KEYLINE_W * k)
        d.line([(c - s, c + s), (c + s, c - s)], col, w)
    return d, c


_png_cache = {}


def shipped(kind, past=False):
    n = {"fight": "router", "elite": "elite", "event": "terminal", "shop": "shop", "rack": "rack"}[kind]
    key = (n, past)
    if key not in _png_cache:
        _png_cache[key] = Image.open(ROUTE + "node_%s%s.png" % (n, "_past" if past else "")).convert("RGBA")
    return _png_cache[key]


def sticker_image(kind, direction, k=1.0, r=STICKER_R, state="later"):
    """The sticker (art + ring) as an RGBA image, centre at image centre. `k` scales the whole thing (1 = 1080p map)."""
    cut = (r - (RING_W + 2.0 + 2.4)) + 2.4  # the die-cut radius used by the overlay
    cut *= k
    dim = int(round(2 * (r * k + 14 * k)))
    if dim % 2:
        dim += 1
    img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    if kind in icons.KINDS:
        art = icons.make(direction, kind).render(scale=(cut * 2) / 130.0, ss=6)
    else:
        a = shipped(kind, state == "cut")
        w = int(round(cut * 2))
        art = a.resize((w, max(1, int(round(w * a.height / a.width)))), Image.LANCZOS)
    img.alpha_composite(art, (int(round(dim / 2 - art.width / 2)), int(round(dim / 2 - art.height / 2))))
    rd, c = ring_doc(state, r, k)
    ri = rd.render(1.0, ss=6)
    off = int(round(dim / 2 - ri.width / 2))
    if off >= 0:
        img.alpha_composite(ri, (off, off))
    else:
        img = Image.new("RGBA", ri.size, (0, 0, 0, 0))
        img.alpha_composite(art, (int(round(ri.width / 2 - art.width / 2)), int(round(ri.height / 2 - art.height / 2))))
        img.alpha_composite(ri)
    return img


def paste_c(bg, im, cx, cy):
    bg.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


# ---------------------------------------------------------------------------------------------------------------------
# the mock route map
# ---------------------------------------------------------------------------------------------------------------------
NODES = {
    "n1": ("fight", (150, 760), "walked"),
    "n2": ("event", (400, 650), "walked"),
    "n3": ("rest", (690, 540), "next"),
    "n4": ("workshop", (690, 660), "next"),
    "n5": ("cache", (690, 780), "next"),
    "n6": ("shop", (980, 430), "later"),
    "n7": ("elite", (980, 570), "later"),
    "n8": ("fight", (980, 730), "later"),
    "n9": ("rest", (1270, 330), "later"),
    "n10": ("cache", (1270, 520), "later"),
    "n11": ("workshop", (1270, 700), "later"),
    "n12": ("event", (1270, 880), "later"),
    "n13": ("rack", (1580, 600), "later"),
}
LINKS = [("n1", "n2"), ("n2", "n3"), ("n2", "n4"), ("n2", "n5"), ("n3", "n6"), ("n3", "n7"), ("n4", "n7"), ("n4", "n8"), ("n5", "n8"),
         ("n6", "n9"), ("n7", "n10"), ("n7", "n11"), ("n8", "n11"), ("n8", "n12"), ("n9", "n13"), ("n10", "n13"), ("n11", "n13"), ("n12", "n13")]
NUMBERS = {"n3": 1, "n4": 2, "n5": 3}


def bez(a, b, n=40):
    ax, ay = a
    bx, by = b
    dx = (bx - ax) * 0.5
    p1 = (ax + dx, ay)
    p2 = (bx - dx, by)
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u ** 3 * ax + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * bx,
                    u ** 3 * ay + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * by))
    return pts


def draw_pencil(layer_doc, pts, col, w, dash=None):
    """wax line with a dark under-shadow; `dash` = (on, off) px."""
    ink = (17, 12, 26, 150)
    segs = []
    if dash is None:
        segs = [pts]
    else:
        carry = 0.0
        cur = []
        on, off = dash
        acc = 0.0
        drawing = True
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            L = math.dist(a, b)
            t = 0.0
            while t < L:
                step = min((on if drawing else off) - acc, L - t)
                p0 = (a[0] + (b[0] - a[0]) * t / L, a[1] + (b[1] - a[1]) * t / L)
                p1 = (a[0] + (b[0] - a[0]) * (t + step) / L, a[1] + (b[1] - a[1]) * (t + step) / L)
                if drawing:
                    segs.append([p0, p1])
                t += step
                acc += step
                if acc >= (on if drawing else off) - 1e-6:
                    drawing = not drawing
                    acc = 0.0
    for s in segs:
        layer_doc.line([(x + 1.5, y + 2.5) for x, y in s], ink, w + 3)
    for s in segs:
        layer_doc.line(s, col, w)


def build_map(direction, plate=None, size=(1920, 1080)):
    bg = Image.open(PLATE).convert("RGBA") if plate is None else plate.copy()
    bg = bg.resize(size, Image.LANCZOS)
    # a mild grade so the sticker row is the brightest thing (the game dims the street when the sticker row leads)
    bg = Image.blend(bg, Image.new("RGBA", bg.size, (6, 8, 22, 255)), 0.30)
    W, H = size
    if "links" in _cache:
        bg.alpha_composite(_cache["links"])
        return _finish_map(bg, direction)
    d = Doc(W, H, "links")
    for a, b in LINKS:
        pa = NODES[a][1]
        pb = NODES[b][1]
        pts = bez(pa, pb)
        # clear pad round the stickers
        pts = [p for p in pts if math.dist(p, pa) > 34 and math.dist(p, pb) > 34]
        sa, sb = NODES[a][2], NODES[b][2]
        if sa == "walked" and sb == "walked":
            draw_pencil(d, pts, RING_WALKED + (245,), 3.6)
        elif sa == "walked" and sb == "next":
            draw_pencil(d, pts, RING_NEXT + (245,), 3.0, (16, 9))
        else:
            draw_pencil(d, pts, RING_LATER + (190,), 1.8, (9, 9))
    _cache["links"] = d.render(1.0, ss=2)
    bg.alpha_composite(_cache["links"])
    return _finish_map(bg, direction)


_cache = {}


def _finish_map(bg, direction):
    for nid, (kind, (x, y), st) in NODES.items():
        im = sticker_image(kind, direction, 1.0, STICKER_R, st)
        paste_c(bg, im, x, y)
    # number chips (orange square, left of the sticker)
    dr = ImageDraw.Draw(bg)
    for nid, n in NUMBERS.items():
        x, y = NODES[nid][1]
        box = (x - 62, y - 13, x - 36, y + 13)
        dr.rectangle((box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1), fill=KEYLINE + (230,))
        dr.rectangle(box, fill=RING_NEXT)
        f = mono(24)
        dr.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + 1), str(n), font=f, fill=KEYLINE, anchor="mm")
    # the operative token at the current room
    tok = Image.open(ROUTE + "token_operative.png").convert("RGBA")
    side = STICKER_R * 1.05 * 2
    tok = tok.resize((int(side), int(side * tok.height / tok.width)), Image.LANCZOS)
    cx, cy = NODES["n2"][1]
    paste_c(bg, tok, cx + 0.75 * STICKER_R, cy - 1.45 * STICKER_R)
    return bg.convert("RGB")


def squint(img, w=320):
    s = img.resize((w, int(round(img.height * w / img.width))), Image.LANCZOS)
    return s


def blur_strip(img, box=(0, 280, 1920, 940), radius=4):
    return img.crop(box).filter(ImageFilter.GaussianBlur(radius))


# ---------------------------------------------------------------------------------------------------------------------
# the legend strip (RouteLegend): kind swatches (the die-cut at k = 0.5, the dashed white ring), words, the two ring keys, the cue
# ---------------------------------------------------------------------------------------------------------------------
LEGEND_X = {}
WORDS = [("fight", "FIGHT"), ("elite", "ELITE"), ("event", "EVENT"), ("shop", "SHOP"), ("rack", "RACK"),
         ("rest", "REST"), ("workshop", "WORKSHOP"), ("cache", "CACHE")]


def legend(direction, scale=1.0, with_new=True):
    """RouteLegend at text scale 1.0 as the game lays it out; drawn at `scale` x. Returns an RGBA image (strip on a dark pad)."""
    S = 3  # internal supersample
    sw = 22.0
    gap = 8.0
    fs = 12
    f = mono(fs * S)
    words = WORDS if with_new else WORDS[:5]
    # measure
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    x = 14.0
    items = []
    for kind, word in words:
        wd = tmp.textlength(word, font=f) / S
        items.append(("kind", kind, word, x, wd))
        LEGEND_X[kind] = x
        x += sw + gap / 2 + wd + gap
    x += 9
    items.append(("bar", x))
    x += 10
    for key, word, st in (("walked", "walked", "walked"), ("next", "next", "next")):
        wd = tmp.textlength(word, font=f) / S
        items.append(("ring", st, word, x, wd))
        x += sw + gap / 2 + wd + gap
    x += 9
    items.append(("bar", x))
    x += 10
    cue = "HOVER: SHOW ALL LINKS"
    cw = tmp.textlength(cue, font=f) / S
    items.append(("cue", cue, x, cw))
    x += cw + 14
    W = int(math.ceil(x))
    H = 40
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    # navy glass, cyan edge, corner brackets
    dr.rectangle((0, 0, W * S - 1, H * S - 1), fill=(8, 14, 34, 235))
    dr.rectangle((0, 0, W * S - 1, H * S - 1), outline=NET_CYAN + (170,), width=S)
    for (cx, cy, sx, sy) in ((0, 0, 1, 1), (W * S - 1, 0, -1, 1), (W * S - 1, H * S - 1, -1, -1), (0, H * S - 1, 1, -1)):
        dr.line((cx, cy, cx + 12 * S * sx, cy), fill=NET_CYAN, width=2 * S)
        dr.line((cx, cy, cx, cy + 12 * S * sy), fill=NET_CYAN, width=2 * S)
    for y in range(0, H * S, 3 * S):
        dr.line((S, y, W * S - S, y), fill=(0, 0, 0, 40), width=S)
    cyc = H / 2.0
    for it in items:
        if it[0] == "kind":
            _, kind, word, x0, wd = it
            sx = x0 + sw / 2
            ring_r = (sw * 0.5) - RING_W * 0.5 * 0.5
            # sticker: die-cut art at k = 0.5 of the 11 px reach
            cut = (11 - (RING_W + 2 + 2.4) * 0.5) + 2.4 * 0.5
            if kind in icons.KINDS:
                art = icons.make(direction, kind).render(scale=(cut * 2 * S) / 130.0, ss=6)
            else:
                a = shipped(kind)
                w_ = int(round(cut * 2 * S))
                art = a.resize((w_, int(round(w_ * a.height / a.width))), Image.LANCZOS)
            img.alpha_composite(art, (int(round(sx * S - art.width / 2)), int(round(cyc * S - art.height / 2))))
            rd, c = ring_doc("later", 11, 0.5 * S / S)
            ri = rd.render(S, ss=4)
            img.alpha_composite(ri, (int(round(sx * S - ri.width / 2)), int(round(cyc * S - ri.height / 2))))
            dr.text(((x0 + sw + gap / 2) * S, cyc * S + 1), word, font=f, fill=TEXT_HI, anchor="lm")
        elif it[0] == "ring":
            _, st, word, x0, wd = it
            sx = x0 + sw / 2
            side = sw
            rd, c = ring_doc(st, side * 0.36 / 0.8 * 0.8 + 0.0, 0.8)
            # the legend draws the ring at side*0.36 with k = 0.8
            d2 = Doc(60, 60)
            rr = side * 0.36
            w = RING_W * 0.8
            ink = rgba(KEYLINE + (230,))
            col = RING_WALKED if st == "walked" else RING_NEXT
            if st == "walked":
                for q in (rr - w * 0.55, rr + w * 0.55):
                    d2.circle(30, 30, q, None, ink, w * 0.6 + KEYLINE_W * 0.8 * 0.6)
                for q in (rr - w * 0.55, rr + w * 0.55):
                    d2.circle(30, 30, q, None, col, w * 0.55)
            else:
                d2.circle(30, 30, rr, None, ink, w * 1.4 + KEYLINE_W * 0.8)
                d2.circle(30, 30, rr, None, col, w * 1.4)
            ri = d2.render(S, ss=4)
            img.alpha_composite(ri, (int(round(sx * S - ri.width / 2)), int(round(cyc * S - ri.height / 2))))
            dr.text(((x0 + sw + gap / 2) * S, cyc * S + 1), word, font=f, fill=TEXT_HI, anchor="lm")
        elif it[0] == "bar":
            x0 = it[1]
            dr.rectangle((x0 * S, (cyc - 9) * S, (x0 + 1) * S, (cyc + 9) * S), fill=CELL_ACID + (128,))
        else:
            _, cue_t, x0, cw_ = it
            dr.text((x0 * S, cyc * S + 1), cue_t, font=f, fill=CELL_ACID, anchor="lm")
    out = img.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    return out
