"""Round 39: the three views at real scope WITH their latest locked UI, + car LODs.

NET36=net_scope.json python screens39.py [city raid transit cars three contact]
"""
import json
import math
import os
import sys

os.environ.setdefault("NET36", "net_scope.json")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout36 as L  # noqa: E402
import post39 as P  # noqa: E402
import screens38_base as B  # noqa: E402
import r31lib as RL  # noqa: E402
import r32ui as U32  # noqa: E402
import r35ui as R  # noqa: E402
import ui19 as U  # noqa: E402
import ui20 as V  # noqa: E402
import ui21 as V2  # noqa: E402
import icons22 as IC  # noqa: E402
import beacon39 as BC  # noqa: E402
import sticker_lib19 as SL  # noqa: E402

OUT = os.path.dirname(HERE)
W, H = 1920, 1080
NET, NODES = P.NET, P.NODES
to_rgba, prj, prj_w = B.to_rgba, B.prj, B.prj_w
MER, LIME, WHITE, GOLD = R.MER, R.LIME, R.WHITE, R.GOLD
GREY = (118, 114, 128)


def save(img, name):
    img.convert("RGB").save(os.path.join(OUT, name), optimize=True)
    print("saved", name, flush=True)


def scene(tag):
    return json.load(open(os.path.join(P.SRC, tag + "_scene.json")))


def f2p(img):
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


def p2f(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


# ------------------------------------------------------------------ round 37 netrun node markers (option A)
def site_icon(kind, px):
    S = 3
    Pp = px * S
    im = Image.new("RGBA", (Pp, Pp), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([S, S, Pp - S, Pp - S], fill=(30, 22, 18, 255), outline=(12, 10, 14, 255), width=2 * S)
    if kind == "key":
        d.ellipse([3 * S, 3 * S, Pp - 3 * S, Pp - 3 * S], fill=(70, 50, 8, 255))
        g = RL.glyph("placeholder_key", int(Pp * 0.62), fill=GOLD, ow=0)
        im.alpha_composite(g, ((Pp - g.width) // 2, (Pp - g.height) // 2))
    else:  # a Meridian Site: the crane-A crest in the corp orange
        s = Pp * 0.3
        c = (Pp / 2, Pp / 2 + S)
        d.line([(c[0] - s * 0.8, c[1] + s * 0.7), (c[0], c[1] - s), (c[0] + s * 0.8, c[1] + s * 0.7)], fill=MER + (255,), width=3 * S)
        d.line([(c[0] - s * 0.45, c[1] + s * 0.1), (c[0] + s * 0.45, c[1] + s * 0.1)], fill=MER + (255,), width=2 * S)
        d.line([(c[0] - s * 1.1, c[1] - s * 0.55), (c[0] + s * 1.2, c[1] - s * 0.75)], fill=MER + (255,), width=2 * S)
    return im.resize((px, px), Image.LANCZOS)


def ring(img, x, y, r, col, w=4, glow=0.7):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([x - r, y - r, x + r, y + r], outline=255, width=w)
    if glow:
        img = SL.over(img, col, SL.scale_mask(m.filter(ImageFilter.GaussianBlur(5)), glow))
    img = SL.over(img, (6, 5, 10), SL.shift(m, 1, 2))
    return SL.over(img, col, m)


def cursor(img, x, y):
    d = ImageDraw.Draw(img)
    pts = [(x, y), (x, y + 30), (x + 8, y + 23), (x + 14, y + 36), (x + 20, y + 33), (x + 14, y + 21), (x + 24, y + 21)]
    d.polygon([(px + 2, py + 3) for px, py in pts], fill=(0, 0, 0, 140))
    d.polygon(pts, fill=(250, 250, 250, 255), outline=(10, 10, 14, 255))
    return img


def pan_cues(img):
    d = ImageDraw.Draw(img)
    for (x, y, ang) in ((960, 18, -90), (1902, 540, 0), (960, 1062, 90), (18, 540, 180)):
        a = math.radians(ang)
        for k in (0, 14):
            px, py = x - math.cos(a) * k, y - math.sin(a) * k
            pts = [(px + math.cos(a) * 10, py + math.sin(a) * 10), (px + math.cos(a + 2.4) * 12, py + math.sin(a + 2.4) * 12),
                   (px + math.cos(a - 2.4) * 12, py + math.sin(a - 2.4) * 12)]
            d.polygon(pts, fill=U32.CYAN + (200 - k * 6,))
    return img


def minimap(view_cam, w=320, h=180):
    """The whole-city render as the minimap (round 37 terminal), with the view box, you (lime) and the target (red)."""
    full = Image.open(os.path.join(P.SRC, "g_full_beauty_night.png")).convert("RGB")
    fc = scene("g_full")["cam"]
    mm = full.resize((w, h), Image.BILINEAR)
    from PIL import ImageEnhance
    mm = ImageEnhance.Brightness(ImageEnhance.Color(mm).enhance(0.45)).enhance(0.6).convert("RGBA")
    d = ImageDraw.Draw(mm)
    cx, cy = prj_w(fc, *view_cam["target"][:2], 0, w, h)
    k = view_cam["ortho"] / fc["ortho"]
    d.rectangle([cx - w * k / 2, cy - h * k / 2, cx + w * k / 2, cy + h * k / 2], outline=LIME + (255,), width=2)
    for n in NET["nodes"]:
        if n["state"] in ("owned", "core"):
            x, y = prj(fc, n["lot"], 0, w, h)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=LIME + (230,))
    hx, hy = prj(fc, NET["hq"]["meridian"], 0, w, h)
    d.ellipse([hx - 6, hy - 6, hx + 6, hy + 6], outline=(255, 60, 60, 255), width=2)
    c = RL.CRT(w + 24, h + 70, U32.CYAN, "MINIMAP", tag="DRAG / WASD", seed=353)
    c.paste(mm, 12, 46)
    c.text((12, h + 52), "lime = you   red = target   box = view", 13, (170, 200, 210))
    return c.finish()


def legend(img, hot=False):
    c = RL.CRT(1080, 46, U32.LIME if hot else U32.CYAN, None, header=False, seed=354)
    x0 = 16
    for col, s in ((LIME, "owned / visited"), (MER, "selectable"), (WHITE, "not yet (hidden)")):
        c.d.ellipse([x0 + 2, 13, x0 + 22, 33], outline=col + (255,), width=3)
        x0 += 30 + int(c.text((x0 + 30, 13), s, 15, (215, 225, 230))) + 24
    c.text((x0 + 10, 13), "|   HOVER HERE: SHOW ALL NODES", 15, U32.CYAN)
    return RL.paste(img, c.finish(scan=0.15), 400, 1026)


def options_inset(img, on=False):
    c = RL.CRT(400, 74, U32.CYAN, None, header=False, seed=355)
    c.text((14, 12), "OPTIONS > MAP", 14, (150, 190, 200))
    c.text((14, 38), "Always show all nodes", 19, (225, 235, 240))
    c.d.rounded_rectangle([318, 34, 384, 62], radius=14, outline=U32.CYAN + (255,), width=2, fill=(LIME if on else (30, 34, 44)) + (255,))
    c.d.ellipse([352 if on else 322, 38, 378 if on else 348, 58], fill=(240, 240, 240, 255))
    return RL.paste(img, c.finish(scan=0.15), 1498, 970)


# ------------------------------------------------------------------ 1. city grid (zoomed in, panning, meandering links)
VIS = ("owned", "core", "available", "grey")


def city_grid():
    cam = scene("g_zoom")["cam"]

    def deco(net):
        for l in NET["links"]:
            a, b = NODES[l["a"]], NODES[l["b"]]
            if a["state"] not in VIS or b["state"] not in VIS:
                continue                                  # round 37: hidden nodes take their links with them
            st = l["state"]
            net.link(l["pts"], P.LINK_COL[st], style="dashed" if st == "border" else "solid",
                     k={"owned": 1.2, "border": 1.15, "grey": 0.5, "white": 0.4}[st], packets=st == "owned")
        for n in NET["nodes"]:
            if n["state"] in ("owned", "core"):
                net.node(n)
    hq = NET["hq"]["meridian"]
    hx, hy = L.W(hq)
    pools = [(hx + 10, hy - 6, 22.0, 0.45)]               # calm Heat B: one slow sweep near the target
    img, cam = P.finish("g_zoom", decorate=deco, pools=pools, fog=0.3, t=0.15)
    cv = to_rgba(img)
    cv = B.hq_tags(cv, cam, 2.0, size=34)
    # option A node markers: the Site icon in its normal colours; the state is the ring
    sel = sorted(n["id"] for n in NET["nodes"] if n["state"] == "available")[0]
    patrol = sorted(n["id"] for n in NET["nodes"] if n["state"] == "grey")[0]
    for n in sorted(NET["nodes"], key=lambda n: prj(cam, n["lot"])[1]):
        st = n["state"]
        if st not in ("available", "grey"):
            continue
        x, y = prj(cam, n["lot"], 0)
        kd = "key" if n["kind"] == "key" else "site"
        ic = site_icon(kd, 30)
        cv = U32.pad(cv, [(x, y - 13), (x + 26, y), (x, y + 13), (x - 26, y)], (90, 86, 100), lit=0.5, glow=0.0, fill_a=200, k=0.7, pins=False)
        cv.alpha_composite(ic, (int(x - ic.width / 2), int(y - 14 - ic.height / 2)))
        col = MER if st == "available" else LIME
        cv = ring(cv, x, y - 14, ic.width / 2 + 5, col, w=4, glow=0.9 if st == "available" else 0.6)
        cv = U32.chip(cv, (x + 22, y - 30), "T%d" % n["tier"], col, 11, fill_a=225)
    # TARGET: Meridian HQ (red pencil circle + the central server chip)
    tx, ty = prj(cam, hq, 12)
    if 120 < tx < W - 120 and 120 < ty < H - 120:
        pr = RL.pen(RL.GP_RED, seed=351)
        pr.circle(tx, ty - 10, 150, 96, width=10)
        pr.text("TARGET", tx - 170, ty + 110, 40, angle=-8)
        cv = RL.ink(cv, pr)
        cv = U32.chip(cv, (tx + 40, ty + 112), "CENTRAL SERVER  //  EXPLOITS 0 / 3", GOLD, 14)
    else:                                               # off-screen: an edge marker points at the TARGET (pan to it)
        cx_, cy_ = W / 2, H / 2
        dx_, dy_ = tx - cx_, ty - cy_
        k_ = min((W / 2 - 70) / max(1e-6, abs(dx_)), (H / 2 - 70) / max(1e-6, abs(dy_)))
        ex, ey = cx_ + dx_ * k_, cy_ + dy_ * k_
        ang = math.atan2(dy_, dx_)
        pr = RL.pen(RL.GP_RED, seed=351)
        pr.circle(ex, ey, 46, 40, width=8)
        cv = RL.ink(cv, pr)
        d_ = ImageDraw.Draw(cv)
        tip = (ex + math.cos(ang) * 64, ey + math.sin(ang) * 64)
        d_.polygon([tip, (ex + math.cos(ang + 2.6) * 22 + math.cos(ang) * 40, ey + math.sin(ang + 2.6) * 22 + math.sin(ang) * 40),
                    (ex + math.cos(ang - 2.6) * 22 + math.cos(ang) * 40, ey + math.sin(ang - 2.6) * 22 + math.sin(ang) * 40)], fill=(255, 40, 50, 255))
        g_ = site_icon("site", 34)
        cv.alpha_composite(g_, (int(ex - 17), int(ey - 17)))
        cv = U32.chip(cv, (ex - 150, ey + 60), "TARGET: MERIDIAN HQ  //  EXPLOITS 0 / 3", GOLD, 14)
    # patrol affordance on a cleared Site
    x, y = prj(cam, NODES[patrol]["lot"], 0)
    d = ImageDraw.Draw(cv)
    r_ = 26
    d.arc([x - r_, y - 14 - r_, x + r_, y - 14 + r_], 200, 470, fill=U32.CYAN + (255,), width=3)
    bx, by = int(x + 46), int(y - 40)
    cv = U32.term_button(cv, (bx, by, bx + 330, by + 60), "PATROL  [P]", "loot, Heat, Rank; no objective")
    cv = U32.chip(cv, (x, y + 22), "CLEARED", LIME, 12)
    # the selected Site (corner brackets) + its info window
    x, y = prj(cam, NODES[sel]["lot"], 0)
    d = ImageDraw.Draw(cv)
    for (cx, cy, sx, sy) in ((x - 30, y - 46, 1, 1), (x + 30, y - 46, -1, 1), (x - 30, y + 14, 1, -1), (x + 30, y + 14, -1, -1)):
        d.line([(cx, cy), (cx + sx * 12, cy)], fill=LIME + (255,), width=3)
        d.line([(cx, cy), (cx, cy + sy * 12)], fill=LIME + (255,), width=3)
    cv = pan_cues(cv)
    cv = RL.place_sticker(cv, RL.sticker_word(["THE GRID"], 58, fills=["yellow"], seed=31), 168, 56, angle=-3)
    dz = R.dossier(heat_stamp="HEAT 52: HUNTED")
    dz = dz.resize((int(dz.width * 0.86), int(dz.height * 0.86)), Image.LANCZOS)
    cv = RL.drop_shadow(cv, dz, 22, 112, blur=14, off=(8, 12), op=0.6)
    cv = RL.paste(cv, minimap(cam), 22, 812)
    nm = NODES[sel].get("name", "SITE").upper()[:22]
    cv = R.node_info(cv, (1480, 560, 1898, 770), nm, "T%d" % NODES[sel]["tier"], ["+9 Schematics, Firmware", "1 armory asset"], "Logistics depot")
    cv = RL.place_sticker(cv, RL.sticker_word(["JACK IN"], 78, fills=["pink"], seed=8), 1690, 880, angle=-3)
    cv = legend(cv)
    cv = options_inset(cv)
    return RL.bloom(cv, 0.1, 0.84, 8), cam


# ------------------------------------------------------------------ 2. raid view with the locked raid UI
KIND_NAME = {"core": "CORE (home)", "relay": "RELAY", "firewall": "FIREWALL RELAY", "vault": "VAULT TERMINAL", "proxy": "PROXY RELAY",
             "safehouse": "SAFEHOUSE"}
KIND_GLYPH = {"core": "picto_hp", "relay": "picto_all_targets", "firewall": "slice_firewall", "vault": "placeholder_vault",
              "proxy": "placeholder_spoof", "safehouse": "placeholder_key"}
RAID_STATE = {"m1_d": ("disabled", 0.0), "m1_f": ("holds", 0.35), "m2_virus": ("holds", 0.7)}


def raid_routes():
    """Three threat routes (A/B/C) from available Sites on the Meridian side to CORE, along the real streets."""
    import citydata as CD
    import grid27
    d = CD.load()
    grid27.patch(d)
    cells = L.street_graph(d)
    hq = NET["hq"]["meridian"]
    av = sorted((n for n in NET["nodes"] if n["state"] == "available"), key=lambda n: (math.hypot(n["lot"][0] - hq[0], n["lot"][1] - hq[1]), n["id"]))
    picks = [av[0], av[3], av[6]]
    targets = ["m2_virus", "core", "m1_d"]
    out = []
    for s, t in zip(picks, targets):
        p = L.bfs(tuple(s["cell"]), tuple(NODES[t]["cell"]), cells)
        out.append(dict(start=s["id"], target=t, pts=L.simplify(p)))
    return out


def mer_sprite(unit, head):
    """Intel holo silhouettes: crop the Meridian unit from the v2 vehicle matrix render (vehicles20.py)."""
    lay = json.load(open(os.path.join(P.SRC, "veh_layout.json")))
    want = {"BAILIFF": "HAULER", "INSPECTOR": "COURIER"}.get(unit, unit)
    it = next(d for d in lay["items"] if d["corp"] == "MERIDIAN" and d["unit"] == want and not d["up"])
    beauty = Image.open(os.path.join(P.SRC, "veh_beauty.png")).convert("RGB")
    R_ = 70
    sb = beauty.crop((int(it["px"] - R_), int(it["py"] - R_), int(it["px"] + R_), int(it["py"] + R_)))
    a = np.asarray(sb, np.float32)
    bgc = a[2, 2]
    m = (np.abs(a - bgc).sum(axis=2) > 40).astype(np.uint8) * 255
    im = sb.convert("RGBA")
    im.putalpha(Image.fromarray(m).filter(ImageFilter.MaxFilter(3)))
    im = im.resize((90, 90), Image.LANCZOS)
    return im, im.convert("RGB"), (45, 45)


V.sprite = mer_sprite


def raid_view():
    cam0 = scene("r_raid")["cam"]
    routes = raid_routes()
    vault = next(n for n in NET["nodes"] if n["kind"] == "vault" and n["state"] == "owned")

    def deco(net):
        for l in NET["links"]:
            a, b = NODES[l["a"]], NODES[l["b"]]
            if l["state"] == "owned":
                dead = RAID_STATE.get(l["a"], ("", 1))[0] == "disabled" or RAID_STATE.get(l["b"], ("", 1))[0] == "disabled"
                net.link(l["pts"], P.LINK_COL["owned"], k=0.45 if dead else 1.2, packets=not dead)
            elif l["state"] == "border":
                net.link(l["pts"], P.LINK_COL["border"], style="dashed", k=0.5, packets=False)
        for n in NET["nodes"]:
            if n["state"] in ("owned", "core"):
                st, hp = RAID_STATE.get(n["id"], ("holds", 1.0))
                if st == "disabled":
                    nn = dict(n, state="grey")
                    net.node(nn)
                else:
                    net.node(n, exposed=n["state"] == "core", flash="hover" if n["id"] == vault["id"] else None)
                    if hp < 1:
                        net.health(n, hp)
            elif n["state"] == "available":
                net.node(n, scale=0.8)
        net.forecast(vault, P.GREEN)
    hx, hy = L.W(NODES["core"]["lot"])
    img, cam = P.finish("r_raid", decorate=deco, pools=[(hx + 1, hy - 1, 12.0, 0.8)], t=0.2)
    fr = V.Frame(img)
    # red grease-pencil routes (locked): solid lines along the streets, circles + letters at the entry Sites
    pen = V.Pencil(fr, 3901)
    for i, r in enumerate(routes):
        pts = [prj(cam, p, 0) for p in r["pts"]]
        pen.arrow(pts, V.R_PEN, 6.0, 22)
        ex, ey = pts[0]
        pen.circle(ex, ey, 44, 29, V.R_PEN, 6.0)
        pen.text("ABC"[i], ex + (-60 if ex > 960 else 60), ey - 40, 30, V.R_PEN, 5.5)
    fr = pen.composite()
    img = fr.img
    cv = f2p(img)
    # the Meridian convoy at the entries: v4 icons with health discs (locked round 22)
    for i, r in enumerate(routes):
        x, y = prj(cam, r["pts"][0], 0)
        for j, (ui, hp) in enumerate(((1, 1.0), (0, 0.7))):
            ic = IC.unit_icon("MERIDIAN", ui, up=(i == 0 and j == 0), size=38, hp=hp, statuses=(("SLOWED",) if i == 1 and j == 1 else ()))
            cv.alpha_composite(ic, (int(x - ic.width / 2 + (j - 0.5) * 34), int(y - ic.height / 2 - 34)))
    # the stationed operative: R3 class beacon on the Safehouse's uplink pad (locked)
    safe = next(n for n in NET["nodes"] if n["kind"] == "safehouse")
    nb = scene("r_raid")["node_bld"].get(safe["id"])
    img = p2f(cv)
    if nb:
        px_, py_ = prj_w(cam, nb["centre"][0], nb["centre"][1], nb["top"] + 0.4)
        x0, y0 = int(px_ - 140), int(py_ - 230)
        if 0 <= x0 and x0 + 280 <= W and 0 <= y0 and y0 + 270 <= H:
            sub = img[y0:y0 + 270, x0:x0 + 280].copy()
            img[y0:y0 + 270, x0:x0 + 280] = BC.beacon(sub, px_ - x0, py_ - y0 - 2, "breaker", 0.55, scale=0.7)
    # panels by fiction (locked E): network terminal, the work order paper, the decrypted holo intel
    rows = []
    for n in sorted((n for n in NET["nodes"] if n["state"] in ("owned", "core")), key=lambda n: (n["kind"] != "core", n["id"])):
        st, hp = RAID_STATE.get(n["id"], ("home" if n["kind"] == "core" else "holds", 1.0))
        chip = {"holds": "HOLDS", "disabled": "DISABLED", "home": "HOME -8"}[st]
        col = {"holds": U.GREEN, "disabled": U.AMBER, "home": U.PINK}[st]
        rows.append(("node", KIND_GLYPH[n["kind"]], KIND_NAME[n["kind"]], chip, col, "INT %d%%" % int(hp * 100)))
    img = U.put_panel(img, U.terminal("YOUR NETWORK", rows[:8], w=330), 22, 130)
    V.MEMO_SEAL, V.MEMO_FOOT = (200, 110, 40), "MERIDIAN FREIGHT  //  INTERNAL  //  DO NOT FORWARD"
    order = [("big", "MANIFEST AUDIT", (230, 240, 255)), ("t", "MERIDIAN FREIGHT  //  WORK ORDER 52-MF-207", (255, 160, 70)), ("sep",),
             ("kv", "TARGET", "CORE (CELL)", (230, 240, 255)), ("kv", "UNITS", "6 IN 1 WAVE", U.HARM), ("kv", "ENTRY SITES", "3", (230, 240, 255)),
             ("sep",), ("kv", "IF IT RAN NOW: HOME", "50 > 41", U.PINK), ("kv", "DISABLED / SEIZED", "1 / 0", U.AMBER)]
    img = U.put_panel(img, V.memo_glass("WORK ORDER", order, w=290), 1574, 96)

    def mer_symbol(size=120, col=(255, 160, 70)):
        g = Image.open(os.path.join(BC.EMBLEMS, "meridian.png")).split()[3].resize((size * 2, size * 2), Image.LANCZOS)
        im = Image.new("RGBA", g.size, col + (0,))
        im.putalpha(g)
        return im
    V2.CORP_SYMBOL = mer_symbol
    V2.INTEL_CORP = "MERIDIAN FREIGHT  //  YARD SECURITY NET"
    V.SPRITE_LABELS = ["A1 HAULER", "B2 COURIER", "A1 (rear)"]
    intel = [("t", "6 THREATS  //  STRENGTH +52% (HEAT)", (255, 160, 70)),
             ("route", "A", "HAULER +  +  COURIER", "> weakest node  /  > VAULT"),
             ("route", "B", "HAULER  +  COURIER", "> CORE (home)"),
             ("route", "C", "HAULER  +  COURIER", "> weakest node")]
    img = U.put_panel(img, V2.intel_holo(intel, w=330, col=(255, 160, 70)), 22, 520)
    img = U.put_panel(img, U.terminal("IF PLACED", [("t", "ICE LOCK > VAULT TERMINAL", (190, 225, 240)), ("kv", "VAULT", "HOLDS > HOLDS +2", U.GREEN),
                                                    ("kv", "HOME", "41 > 44", U.PINK)], w=300, accent=U.GREEN), 1600, 600)
    # the defence tray (stickers), the parked ICE LOCK + the yellow pencil targeting arrow, START + speed
    x = 560
    for i, (nm, gl, hp, cp, ds, col) in enumerate(U.TRAY):
        if nm == "ICE LOCK":
            x += 162
            continue
        sd = U.asset_card(nm, gl, hp, cp, ds, col, 50 + i)
        img = U.place(img, sd, x, 985, angle=[-2, 1.5, -1, 2, -1.5, 1][i])
        x += 162
    vx, vy = prj(cam, vault["lot"], 0)
    f2 = V.Frame(img)
    f2 = V2.parking(f2, 1395, 760)
    sd = U.asset_card(*U.TRAY[2][:5], U.TRAY[2][5], 52, gloss_k=1.0)
    f2.img = U.place(f2.img, sd, 1395, 760, angle=2, hover=0.15, scale=0.8)
    p2 = V.Pencil(f2, 3902)
    V2.target_arrow(p2, (1365, 680), (vx + 20, vy + 30), "valid", node_xy=(vx, vy))
    f2 = p2.composite()
    f2 = V2.cursor(f2, vx + 20, vy + 30)
    img = f2.img
    sd = U.word_sticker(["START DEFENSE"], 40, [U.FILL_PINK], seed=21, border=13)
    img = U.place(img, sd, 1700, 960, angle=-2)
    img = U.put_panel(img, U.speed_terminal("2x", "-- / 30"), 1478, 1018)
    sd = U.word_sticker(["RAID SETUP"], 50, [U.FILL_YELLOW], seed=11, border=14)
    img = U.place(img, sd, 40 + sd["img"].size[0] / U.S / 2 - 20, 62, angle=-1.5)
    return f2p(img), cam


# ------------------------------------------------------------------ 3. netrun transit (locked round 37 netrun details)
import runmap39 as RM  # noqa: E402


def run_transit():
    run = RM.load()
    nodes = {n["id"]: n for n in run["nodes"]}
    cam0 = scene("t_run")["cam"]
    COLS = {"walked": P.LIME, "current": P.LIME, "option": P.ORANGE}

    def deco(net):
        for l in NET["links"]:                           # the Cell's own network stays (dim); other Site links hidden
            if l["state"] == "owned":
                net.link(l["pts"], P.LINK_COL["owned"], k=0.45, packets=False)
        for e in run["edges"]:
            if e["state"] in COLS:
                net.runpath(e["pts"], COLS[e["state"]], k=1.3 if e["state"] != "option" else 1.5)
        for n in run["nodes"]:
            if n["state"] in ("walked", "current", "option", "target"):
                net.runsocket(n["lot"], COLS.get(n["state"], P.HARM))
        for n in NET["nodes"]:
            if n["state"] in ("owned", "core"):
                net.node(n)
    pools = [(L.W(nodes["L3_0"]["lot"])[0] + 6, L.W(nodes["L3_0"]["lot"])[1] - 4, 14.0, 0.35)]     # calm heat: one soft sweep
    img, cam = P.finish("t_run", decorate=deco, pools=pools, t=0.2)
    cv = to_rgba(img)
    # node-type stickers (normal colours), option A rings by state; hidden nodes are not drawn
    KIND_STK = {"router": "router", "elite": "elite", "terminal": "terminal", "modem": "modem", "rack": "rack"}
    for n in sorted(run["nodes"], key=lambda n: prj(cam, n["lot"])[1]):
        st = n["state"]
        if st in ("hidden",) or n["kind"] == "start":
            continue
        x, y = prj(cam, n["lot"], 0)
        px = {"walked": 46, "current": 54, "option": 62, "target": 70}[st]
        sd = U32.node_sd(KIND_STK.get(n["kind"], "router"), px)
        lift = 30 if st != "target" else 40
        cv = RL.place_sticker(cv, sd, x, y - lift, angle=((sum(map(ord, n["id"])) % 9) - 4) * 0.8, hover=0.35 if st == "option" else 0.0)
        col = {"walked": LIME, "current": LIME, "option": MER, "target": (255, 60, 60)}[st]
        if st != "target":
            cv = ring(cv, x, y - lift, px / 2 + 8, col, w=5 if st in ("option", "current") else 3,
                      glow={"option": 0.9, "current": 0.9, "walked": 0.5}[st])
    cur = next(n for n in run["nodes"] if n["state"] == "current")
    x, y = prj(cam, cur["lot"], 0)
    cv = RL.place_sticker(cv, U32.token_sd(54), x + 30, y - 86, angle=-14, hover=0.6)
    tgt = next(n for n in run["nodes"] if n["state"] == "target")
    site = NODES[run["link"][1]]
    tx, ty = prj(cam, tgt["lot"], 0)
    pr = RL.pen(RL.GP_RED, seed=391)
    pr.circle(tx, ty - 40, 80, 64, width=9)
    pr.text("TARGET", tx - 120, ty + 50, 32, angle=-6)
    cv = RL.ink(cv, pr)
    sx, sy = prj(cam, NODES[run["link"][0]]["lot"], 0)
    cv = U32.chip(cv, (sx + 80, sy + 40), "CORE (start)", LIME, 14, bright=True)
    cv = RL.place_sticker(cv, RL.sticker_word(["NETRUN"], 64, fills=["yellow"], seed=63), 170, 62, angle=-3)
    dz = R.dossier(heat_stamp="HEAT 52: HUNTED")
    dz = dz.resize((int(dz.width * 0.8), int(dz.height * 0.8)), Image.LANCZOS)
    cv = RL.drop_shadow(cv, dz, 22, 116, blur=14, off=(8, 12), op=0.6)
    cv = R.node_info(cv, (1480, 820, 1898, 1030), site.get("name", "SITE").upper()[:22], "T%d" % site.get("tier", 1),
                     ["+9 Schematics, Firmware", "1 armory asset"], "Logistics depot")
    cv = U32.term_button(cv, (24, 980, 230, 1050), "DECK", "[D]")
    cv = U32.term_button(cv, (242, 980, 448, 1050), "MENU", "[ESC]")
    # key strip: what the stickers are (sword = COMBAT)
    c = RL.CRT(1000, 46, U32.CYAN, None, header=False, seed=357)
    x0 = 16
    for kind, lab in (("router", "COMBAT"), ("elite", "ELITE"), ("terminal", "EVENT"), ("modem", "SHOP"), ("rack", "SERVER RACK")):
        ic = U32.icon(kind, 30)
        c.im.alpha_composite(ic, (x0, 8))
        x0 += 36 + int(c.text((x0 + 36, 13), lab, 15, (215, 225, 230))) + 22
    c.text((x0 + 4, 13), "|  next nodes only", 15, U32.CYAN)
    cv = RL.paste(cv, c.finish(scan=0.15), 470, 1022)
    return RL.bloom(cv, 0.12, 0.82, 8), cam


# ------------------------------------------------------------------ 4. cars by zoom (LOD)
def cars_lod():
    cv = Image.new("RGBA", (W, H), (8, 7, 14, 255))
    cv = RL.place_sticker(cv, RL.sticker_word(["CARS BY ZOOM"], 50, fills=["yellow"], seed=66), 210, 54, angle=-3)
    d = ImageDraw.Draw(cv)
    d.text((440, 40), "one car, three LODs swapped by camera zoom (like the buildings): FAR = a dot + its lane-colour line;",
           font=RL.f_mono(16), fill=(92, 225, 255, 255))
    d.text((440, 62), "MEDIUM = a small grey box + line; CLOSE = the full low-poly model (lights, stripe) + a THICK speed line.",
           font=RL.f_mono(16), fill=(92, 225, 255, 255))
    tiles = []
    P.CAR_STYLE = "dot"
    img, cam = P.finish("g_zoom", decorate=None, rain=False, t=0.15, fog=0.2)
    tiles.append(("FAR  (city grid, ortho %d)" % cam["ortho"], to_rgba(img), cam))
    P.CAR_STYLE = "box"
    img, cam = P.finish("r_raid", decorate=None, rain=False, t=0.15)
    tiles.append(("MEDIUM  (raid, ortho %d)" % cam["ortho"], to_rgba(img), cam))
    P.CAR_STYLE = "model"
    _op = P.opacity
    P.opacity = lambda lod: 1.0
    img, cam = P.finish("c_close", decorate=None, rain=False, t=0.15, fog=0.0)
    P.opacity = _op
    tiles.append(("CLOSE  (netrun close-up, ortho %d)" % cam["ortho"], to_rgba(img), cam))
    import skylanes as SK
    for i, (lab, im, cam) in enumerate(tiles):
        pts = [prj_w(cam, c["x"], c["y"], c["z"]) for c in SK.cars(0.15)]
        span = {0: 120, 1: 220, 2: 960}[i]
        pts = [(min(max(p[0], span), W - span), min(max(p[1], span * 9 / 16), H - span * 9 / 16)) for p in pts if 0 < p[0] < W and 0 < p[1] < H]
        best = max(pts, key=lambda p: sum(1 for q in pts if abs(q[0] - p[0]) < span and abs(q[1] - p[1]) < span * 9 / 16)) if pts else (960, 540)
        box = (int(best[0] - span), int(best[1] - span * 9 / 16), int(best[0] + span), int(best[1] + span * 9 / 16))
        crop = im.crop(box).resize((600, 338), Image.LANCZOS)
        x = 24 + i * 628
        cv.alpha_composite(crop, (x, 120))
        d.text((x, 470), lab, font=RL.font(RL.ANTON, 24), fill=(235, 240, 250, 255))
        d.text((x, 504), "crop x%.1f" % (W / (box[2] - box[0])), font=RL.f_mono(13), fill=(150, 165, 185, 255))
    rows = [("FAR", "ortho > 400", "streak billboard: head dot + lane-colour line; ~950 cars in view; 1 MultiMesh of quads"),
            ("MEDIUM", "ortho 150-400", "grey box mesh (6 faces) + lane-colour line; reads as a vehicle, no detail cost"),
            ("CLOSE", "ortho < 150", "the low-poly model (~40 faces: wedge, cabin, flank stripe, under-glow, head / tail lights) + a thick speed line"),
            ("RULES", "", "LOD by camera ortho with hysteresis (like the buildings); cars are NOT part of the see-through building material")]
    y = 560
    for a, b, c_ in rows:
        d.text((40, y), a, font=RL.font(RL.ANTON, 22), fill=(255, 222, 30, 255))
        d.text((200, y + 4), b, font=RL.f_mono(16), fill=(92, 225, 255, 255))
        d.text((380, y + 4), c_, font=RL.f_mono(16), fill=(210, 220, 232, 255))
        y += 48
    P.CAR_STYLE = "dot"
    return cv


if __name__ == "__main__":
    which = sys.argv[1:] or ["city", "raid", "transit", "cars"]
    if "city" in which:
        save(city_grid()[0], "city_grid.png")
    if "raid" in which:
        save(raid_view()[0], "raid_view.png")
    if "transit" in which:
        save(run_transit()[0], "run_transit.png")
    if "cars" in which:
        save(cars_lod(), "cars_lod.png")


def three_views():
    cv = Image.new("RGBA", (W, H), (8, 7, 14, 255))
    cv = RL.place_sticker(cv, RL.sticker_word(["ONE CITY"], 52, fills=["yellow"], seed=64), 150, 54, angle=-3)
    d = ImageDraw.Draw(cv)
    d.text((300, 40), "real scope (the shipped Meridian campaign: 32 Sites, mid-campaign network) with each view's LOCKED UI.",
           font=RL.f_mono(17), fill=(92, 225, 255, 255))
    d.text((300, 64), "Same model, one camera; A = the Cell's CORE, B = the run's border link, at every zoom.", font=RL.f_mono(17),
           fill=(92, 225, 255, 255))
    shots = [("city_grid.png", "g_zoom", "CITY GRID  (zoomed in + pan)"), ("raid_view.png", "r_raid", "RAID  (fitted to the network)"),
             ("run_transit.png", "t_run", "NETRUN TRANSIT  (run on the streets)")]
    tw, th = 616, 347
    run = RM.load()
    lk = run["link"]
    l = next(l for l in NET["links"] if [l["a"], l["b"]] == lk or [l["b"], l["a"]] == lk)
    mid = l["pts"][len(l["pts"]) // 2]
    for i, (fn, tagn, lab) in enumerate(shots):
        x = 16 + i * (tw + 8)
        im = Image.open(os.path.join(OUT, fn)).convert("RGBA")
        cam = scene(tagn)["cam"]
        dd = ImageDraw.Draw(im)
        for key, p, col in (("A", NODES["core"]["lot"], (255, 222, 30)), ("B", mid, (92, 225, 255))):
            px, py = prj(cam, p, 0)
            if 0 < px < W and 0 < py < H:
                dd.ellipse([px - 30, py - 30, px + 30, py + 30], outline=col + (255,), width=5)
                dd.rectangle([px + 34, py - 50, px + 70, py - 14], fill=col + (255,))
                dd.text((px + 52, py - 32), key, font=RL.font(RL.ANTON, 28), fill=(14, 12, 20, 255), anchor="mm")
        cv.alpha_composite(im.resize((tw, th), Image.LANCZOS), (x, 104))
        d.text((x, 460), lab, font=RL.font(RL.ANTON, 24), fill=(235, 240, 250, 255))
        d.text((x, 494), "ortho %d" % cam["ortho"], font=RL.f_mono(14), fill=(150, 165, 185, 255))
    rows = [("CITY GRID", "zoomed in (ortho ~440) with pan chevrons + MINIMAP (view box, you, target); links meander through side streets;",
             "round 37 netrun map UI: option A rings, hidden nodes, dossier (Heat on the stamp), PATROL, TARGET (edge marker when off-screen)."),
            ("RAID", "fitted to the player network + entries (ortho ~380); red grease-pencil routes A/B/C, panels by fiction (CRT network,",
             "work order under glass, decrypted holo intel), health v2, v4 icons with health discs, R3 class beacon, sticker tray, parked card."),
            ("NETRUN", "the run's 7-layer map on the streets as THIN double dashed paths; only walked / current / next / target show;",
             "node-type stickers (sword = COMBAT), option A rings, the token, corp-paper dossier, calm heat, TARGET circle.")]
    y = 540
    for a, b_, c_ in rows:
        d.text((24, y), a, font=RL.font(RL.ANTON, 24), fill=(255, 222, 30, 255))
        d.text((220, y + 4), b_, font=RL.f_mono(15), fill=(210, 220, 232, 255))
        d.text((220, y + 26), c_, font=RL.f_mono(15), fill=(210, 220, 232, 255))
        y += 70
    cars = Image.open(os.path.join(OUT, "cars_lod.png")).convert("RGBA").crop((0, 110, W, 530)).resize((1500, 328), Image.LANCZOS)
    cv.alpha_composite(cars, (16, 748))
    d.text((1540, 760), "CARS by zoom:", font=RL.font(RL.ANTON, 22), fill=(255, 222, 30, 255))
    for i, t_ in enumerate(("FAR: dot + line", "MEDIUM: grey box + line", "CLOSE: model + thick line")):
        d.text((1540, 800 + i * 30), t_, font=RL.f_mono(16), fill=(210, 220, 232, 255))
    return cv


if __name__ == "__main__" and "three" in sys.argv[1:]:
    save(three_views(), "three_views.png")
