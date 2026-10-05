"""Round 36 -> node-state options, Heat B with per-node markers, patrol affordance, EXPLOITS chip.

  city_states_a.png    (a) every node keeps its normal icon colours; the STATE is an outline circle:
                           white = unavailable, ORANGE = selectable (the path colour), LIME = visited (its line colour)
  city_states_b.png    (b) the round 35 scheme (state-coloured pads) with a much lighter white wash on the icons
  transit_states_a.png / transit_states_b.png   the same two options on the run map (past = never revisited)
  city_heat_b.png + city_heat_b.gif   Heat B (darker orange): the city reacts (searchlights, strobes) AND circling
                           lights centred on the nodes Heat has made harder, each with its effect chip
Every city view: the TARGET chip reads EXPLOITS 0 / 3 (the T3 key nodes carry the Exploits) and a cleared grey Site
shows the PATROL affordance (cleared Sites can be patrolled: loot, Heat, Rank, no objective).

python states36.py [a|b|ta|tb|heat|all]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL
import city_view as CV
import transit_view as TV

HEATC = (206, 84, 18)  # Heat B: darker orange
STATE_RING = {"owned": R.LIME, "available": R.MER, "white": R.WHITE, "past": R.LIME}


# ------------------------------------------------------------------ city icons (normal colours)
def site_icon(kind, px):
    S = 3
    P = px * S
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([S, S, P - S, P - S], fill=(30, 22, 18, 255), outline=(12, 10, 14, 255), width=2 * S)
    if kind == "key":
        d.ellipse([3 * S, 3 * S, P - 3 * S, P - 3 * S], fill=(70, 50, 8, 255))
        g = L.glyph("placeholder_key", int(P * 0.62), fill=R.GOLD, ow=0)
        im.alpha_composite(g, ((P - g.width) // 2, (P - g.height) // 2))
    elif kind == "heat":
        g = L.glyph("placeholder_burn", int(P * 0.62), fill=(255, 150, 60), ow=0)
        im.alpha_composite(g, ((P - g.width) // 2, (P - g.height) // 2))
    else:  # a Meridian Site: the crane-A crest in the corp orange
        s = P * 0.3
        c = (P / 2, P / 2 + S)
        d.line([(c[0] - s * 0.8, c[1] + s * 0.7), (c[0], c[1] - s), (c[0] + s * 0.8, c[1] + s * 0.7)], fill=R.MER + (255,), width=3 * S)
        d.line([(c[0] - s * 0.45, c[1] + s * 0.1), (c[0] + s * 0.45, c[1] + s * 0.1)], fill=R.MER + (255,), width=2 * S)
        d.line([(c[0] - s * 1.1, c[1] - s * 0.55), (c[0] + s * 1.2, c[1] - s * 0.75)], fill=R.MER + (255,), width=2 * S)
    return im.resize((px, px), Image.LANCZOS)


def wash(im, k):
    a = im.split()[3]
    w = Image.blend(im.convert("RGB"), Image.new("RGB", im.size, (246, 244, 250)), k).convert("RGBA")
    w.putalpha(a)
    return w


def grey(im, k=0.75):
    a = im.split()[3]
    g = ImageEnhance.Brightness(im.convert("L").convert("RGB")).enhance(k).convert("RGBA")
    g.putalpha(a)
    return g


def ring(img, x, y, r, col, w=4, glow=0.7):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([x - r, y - r, x + r, y + r], outline=255, width=w)
    if glow:
        img = SL.over(img, col, SL.scale_mask(m.filter(ImageFilter.GaussianBlur(5)), glow))
    img = SL.over(img, (6, 5, 10), SL.shift(m, 1, 2))
    return SL.over(img, col, m)


def kind_of(k, n):
    if n.get("key"):
        return "key"
    return "heat" if (hash_k(k) % 11 == 0) else "site"


def hash_k(k):
    return (k[0] * 31 + k[1] * 17) & 0xFFFF


def city_layer(base, option="a", selected=None, patrol=True):
    nodes, links = CV.NET
    img = base.copy()
    inl = U.Inlay()
    for a, b in links:
        st = CV.link_state(nodes, a, b)
        pa, pb = nodes[a]["xy"], nodes[b]["xy"]
        if st == "owned":
            inl.trace([pa, pb], R.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0, pads=False)
        elif st == "border":
            inl.trace([pa, pb], R.MER, width=2.6, lanes=3, gap=4.5, glow=0.9, pads=False)
        elif st == "past":
            col = R.LIME if option == "a" else R.GREY
            inl.trace([pa, pb], col, width=2.0, lanes=2, gap=4.0, glow=0.3 if option == "a" else 0.0, alpha=0.7, pads=False)
        else:
            inl.trace([pa, pb], R.WHITE, width=1.4, lanes=2, gap=3.5, glow=0.0, alpha=0.45 if option == "a" else 0.6, pads=False)
    img = inl.lay(img)
    for k in sorted(nodes, key=lambda k: nodes[k]["xy"][1]):
        n = nodes[k]
        x, y = n["xy"]
        st = n["state"]
        if st == "owned":  # the Cell's raid nodes: lime pads, unchanged
            img = U.pad(img, CV.diamond(x, y, 20), R.LIME, lit=1.0, glow=0.7, fill_a=215, k=0.85)
            continue
        kd = kind_of(k, n)
        ic = site_icon(kd, 30 if kd != "key" else 34)
        if option == "a":
            img = U.pad(img, CV.diamond(x, y, 16), (90, 86, 100), lit=0.5, glow=0.0, fill_a=200, k=0.7, pins=False)
            img.alpha_composite(ic, (int(x - ic.width / 2), int(y - 14 - ic.height / 2)))
            img = ring(img, x, y - 14, ic.width / 2 + 5, STATE_RING[st], w=4 if st != "white" else 3,
                       glow={"available": 0.9, "past": 0.6, "white": 0.0}[st])
        else:
            img = U.pad(img, CV.diamond(x, y, 18), CV.COL[st], lit={"available": 1.0, "white": 0.85, "past": 0.6}[st],
                        glow={"available": 0.9}.get(st, 0.1), fill_a=215, k=0.85)
            ic2 = wash(ic, 0.2) if st == "white" else (grey(ic) if st == "past" else ic)
            img.alpha_composite(ic2, (int(x - ic2.width / 2), int(y - 16 - ic2.height / 2)))
        img = U.chip(img, (x + 22, y - 30), "T%d" % n["tier"], (200, 196, 210) if st == "white" else (R.LIME if (st == "past" and option == "a") else
                     (R.GREY if st == "past" else R.MER)), 11, fill_a=225)
    hx, hy = CV.HQ
    img = U.pad(img, CV.diamond(hx, hy + 70, 110), (255, 120, 90), lit=0.6, glow=0.3, fill_a=0, k=1.4)
    pr = L.pen(L.GP_RED, seed=351)
    pr.circle(hx, hy + 30, 190, 120, width=10)
    pr.text("TARGET", hx - 210, hy + 160, 40, angle=-8)
    img = L.ink(img, pr)
    img = U.chip(img, (hx, hy + 170), "CENTRAL SERVER  //  EXPLOITS 0 / 3", R.GOLD, 14)
    if patrol:
        img = patrol_affordance(img, option)
    if selected:
        x, y = nodes[selected]["xy"]
        d = ImageDraw.Draw(img)
        for (cx, cy, sx, sy) in ((x - 30, y - 46, 1, 1), (x + 30, y - 46, -1, 1), (x - 30, y + 14, 1, -1), (x + 30, y + 14, -1, -1)):
            d.line([(cx, cy), (cx + sx * 12, cy)], fill=R.LIME + (255,), width=3)
            d.line([(cx, cy), (cx, cy + sy * 12)], fill=R.LIME + (255,), width=3)
    return img


def patrol_affordance(img, option):
    nodes, _ = CV.NET
    past = sorted([k for k in nodes if nodes[k]["state"] == "past"], key=lambda k: (nodes[k]["xy"][0], k))
    k = past[-1]
    x, y = nodes[k]["xy"]
    d = ImageDraw.Draw(img)
    # hover: a circular-arrows patrol mark over the cleared Site + a terminal button
    r = 26
    d.arc([x - r, y - 14 - r, x + r, y - 14 + r], 200, 470, fill=U.CYAN + (255,), width=3)
    d.polygon([(x + r * 0.95, y - 14 + 4), (x + r * 0.95 + 8, y - 14 - 8), (x + r * 0.95 - 9, y - 14 - 6)], fill=U.CYAN + (255,))
    bx, by = int(x + 46), int(y - 40)
    img = U.term_button(img, (bx, by, bx + 330, by + 60), "PATROL  [P]", "loot, Heat, Rank; no objective")
    d = ImageDraw.Draw(img)
    d.line([(x + 26, y - 14), (bx, by + 30)], fill=U.CYAN + (200,), width=2)
    img = U.chip(img, (x, y + 22), "CLEARED", R.LIME if option == "a" else R.GREY, 12)
    return img


def city_png(option, label=True):
    sel = CV.pick_selected()
    img = city_layer(CV.base_map(), option, selected=sel)
    img = CV.pan_cues(img)
    img = CV.hud(img, sel)
    nodes, _ = CV.NET
    # the key strip states for this option
    c = L.CRT(1080, 46, U.CYAN, None, header=False, seed=354)
    x0 = 16
    items = ((R.LIME, "owned / visited"), (R.MER, "selectable"), (R.WHITE, "not yet")) if option == "a" else \
        ((R.LIME, "owned"), (R.MER, "selectable"), (R.WHITE, "not yet"), (R.GREY, "cleared"))
    for col, s in items:
        if option == "a":
            c.d.ellipse([x0 + 2, 13, x0 + 22, 33], outline=col + (255,), width=3)
        else:
            c.d.polygon(CV.diamond(x0 + 12, 23, 12), fill=col + (255,))
        x0 += 30 + int(c.text((x0 + 30, 13), s, 15, (215, 225, 230))) + 24
    c.text((x0 + 10, 13), "|   DRAG / WASD  pan    WHEEL  zoom    TAB  next", 15, U.CYAN)
    ImageDraw.Draw(img).rectangle([396, 1022, 1484, 1076], fill=(8, 8, 14, 255))
    img = L.paste(img, c.finish(scan=0.15), 400, 1026)
    if label:
        img = L.place_sticker(img, L.sticker_word(["OPTION " + option.upper()], 40, fills=[(232, 230, 238)], seed=7, extrude=4), 960, 118, angle=-2)
    return L.bloom(img, 0.12, 0.82, 8)


# ------------------------------------------------------------------ transit options
def transit_png(option, label=True):
    A = TV.load()
    bg = Image.open(os.path.join(U.FIN, "iso_transit.png"))
    walked, current = TV.WALKED, "2_1"
    if option == "b":
        TV._wsd.clear()
        _orig = TV.white_sd

        def light(kind, px):
            sd = dict(U.node_sd(kind, px))
            sd["img"] = wash(sd["img"], 0.2)
            return sd
        TV.white_sd = light
        img = TV.compose(bg, A, walked, current)
        TV.white_sd = _orig
    else:
        st, opts = TV.states(A, walked, current)
        # draw with every sticker in its normal colours, then rings by state
        _w, _g = TV.white_sd, U.node_sd
        TV.white_sd = lambda kind, px: U.node_sd(kind, px)
        img = TV.compose(bg, A, walked, current, ui=0.0)
        TV.white_sd = _w
        nodes = A["nodes"]
        for k, s in st.items():
            if k == "start":
                continue
            cx, cy = nodes[k]["c"]
            lift = 44 if k == "final" else 26
            px = 96 if k == "final" else {"walked": 46, "current": 54, "option": 62, "white": 50, "past": 46}[s]
            col = {"walked": R.LIME, "current": R.LIME, "option": R.MER, "white": R.WHITE, "past": (110, 106, 120)}[s]
            img = ring(img, cx, cy - lift, px / 2 + 8, col, w=5 if s in ("option", "current") else 3,
                       glow={"option": 0.9, "current": 0.9, "walked": 0.5}.get(s, 0.0))
        img = TV.hud(img, "A", 1.0)
    if label:
        img = L.place_sticker(img, L.sticker_word(["OPTION " + option.upper()], 40, fills=[(232, 230, 238)], seed=7, extrude=4), 960, 130, angle=-2)
    return L.bloom(img, 0.14, 0.8, 8)


# ------------------------------------------------------------------ Heat B: per-node circling lights + the city reacting
HOT = None


def hot_nodes():
    nodes, _ = CV.NET
    av = sorted([k for k in nodes if nodes[k]["state"] in ("available", "white") and 0.2 < nodes[k]["p"] < 0.62 and nodes[k]["xy"][0] > 760 and nodes[k]["xy"][1] > 200], key=lambda k: (nodes[k]["p"], k))
    picks = [av[1], av[len(av) // 2], av[-3]]
    return list(zip(picks, ["+1 ELITE", "SHOP STOCK -1", "+1 RESISTANCE"]))


def police_ring(img, x, y, ang, r=40):
    W, H = img.size
    for col, off in (((255, 40, 50), 0.0), ((60, 120, 255), math.pi)):
        a = ang + off
        px, py = x + r * math.cos(a), y + r * 0.55 * math.sin(a)
        g = Image.new("L", (W, H), 0)
        ImageDraw.Draw(g).ellipse([px - 22, py - 14, px + 22, py + 14], fill=230)
        img = SL.over(img, col, g.filter(ImageFilter.GaussianBlur(8)))
        g = Image.new("L", (W, H), 0)
        ImageDraw.Draw(g).ellipse([px - 6, py - 4, px + 6, py + 4], fill=255)
        img = SL.over(img, (255, 255, 255), g.filter(ImageFilter.GaussianBlur(1.5)))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([x - r, y - r * 0.55, x + r, y + r * 0.55], outline=170, width=2)
    return SL.over(img, HEATC, m)


def heat_frame(base, t, nodes_xy, ui=True):
    img = base.copy()
    # city-wide: searchlight sweeps (the locked H1 language), dark orange heat haze at the edges
    beams = []
    for i, (sx, sy) in enumerate(((1800, -60), (300, -80), (1100, -90))):
        ang = t * 2 * math.pi + i * 2.1
        tx = 300 + (i * 520 + 380 * math.sin(ang)) % 1500
        ty = 380 + 220 * math.cos(ang * 0.8 + i)
        beams.append((sx, sy, tx, ty, 90))
    # and one searchlight locked onto each hardened node
    for (x, y) in nodes_xy:
        beams.append((x + 260, -80, x, y - 10, 60))
    img = R.heat_diegetic(img, beams, [], k=1.1)
    img = L.vignette(img, 0.35, color=(60, 18, 4))
    for (x, y) in nodes_xy:
        g = Image.new("L", img.size, 0)
        ImageDraw.Draw(g).ellipse([x - 60, y - 46, x + 60, y + 22], fill=150)
        img = SL.over(img, HEATC, g.filter(ImageFilter.GaussianBlur(14)))
    for i, (x, y) in enumerate(nodes_xy):
        img = police_ring(img, x, y - 12, t * 2 * math.pi + i, r=54)
    return img


def heat_png_and_gif():
    nodes, _ = CV.NET
    sel = CV.pick_selected()
    base = city_layer(CV.base_map(), "a", selected=sel)
    base = CV.pan_cues(base)
    hot = hot_nodes()
    xy = [nodes[k]["xy"] for k, _ in hot]
    frames = []
    for f in range(8):
        img = heat_frame(base, f / 8, xy)
        for (k, lab), (x, y) in zip(hot, xy):
            img = U.chip(img, (x, y + 30), "HEAT: " + lab, HEATC, 13, bright=True)
        img = hud_heat_b(img, sel)
        frames.append(img)
    L.save(L.bloom(frames[0], 0.12, 0.82, 8), "city_heat_b.png")
    out = os.path.join(L.OUT, "city_heat_b.gif")
    print("wrote", out, U.save_gif([f.convert("RGB") for f in frames], [140] * 8, out, size=(960, 540)))


def hud_heat_b(img, sel):
    """The city HUD without the Heat strip: the number lives on the dossier stamp (Heat B)."""
    nodes, _ = CV.NET
    img = L.place_sticker(img, L.sticker_word(["THE GRID"], 58, fills=["yellow"], seed=31), 168, 56, angle=-3)
    dz = R.dossier(heat_stamp="HEAT 52: HUNTED")
    dz = dz.resize((int(dz.width * 0.86), int(dz.height * 0.86)), Image.LANCZOS)
    img = L.drop_shadow(img, dz, 22, 112, blur=14, off=(8, 12), op=0.6)
    img = L.paste(img, CV.minimap(), 22, 812)
    x, y = nodes[sel]["xy"]
    img = R.node_info(img, (1480, 560, 1898, 770), "DEPOT 15", "T%d" % nodes[sel]["tier"], ["+9 Schematics, Firmware", "1 armory asset"],
                      "Logistics depot")
    img = L.place_sticker(img, L.sticker_word(["JACK IN"], 78, fills=["pink"], seed=8), 1690, 880, angle=-3)
    return img


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    if w in ("a", "all"):
        L.save(city_png("a"), "city_states_a.png")
    if w in ("b", "all"):
        L.save(city_png("b"), "city_states_b.png")
    if w in ("ta", "all"):
        L.save(transit_png("a"), "transit_states_a.png")
    if w in ("tb", "all"):
        L.save(transit_png("b"), "transit_states_b.png")
    if w in ("heat", "all"):
        heat_png_and_gif()
