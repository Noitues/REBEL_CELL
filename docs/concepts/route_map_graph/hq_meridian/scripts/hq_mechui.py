"""HQ Meridian v2: the shuttle containers' 2D language (proposal; the kit overlay calls these hooks).

SHUTTLE     a room in a moving container: a yellow-black hazard badge (a container glyph) on its sticker and a chip with
            where it is: IN THE WALL / ON THE TRAIN / LIFTING. Its ring stays in the locked state colour.
BY CONTAINER ONLY  the freight platform rooms (Q): a chip; they are only reachable by riding a shuttle.
LOCKED LINK a link a container's position switches off (the shuttle is away): a DASHED dim grease line + a padlock and
            "LANDS IN n" (turns until the container is back); it turns solid when the container lands (bible 4.7:
            de-power, then re-made from its source).
NEXT MOVE   the crane's next lifts, in yellow pencil (bible PENCIL_PLAN #FFE200, round 43's telegraph): a ring where the
            container will be + an arrow from where it is, "NEXT: N -> TRAIN".
THE SHUTTLES dial (top right): the four breaches, each WALL or TRAIN now and next, the crane's next pair.
"""
import math

from PIL import Image, ImageDraw

import hq_graph as G
import kit44 as KT
import r31lib as RL
import sidekit as S
import ui31 as K

HAZ = (255, 200, 20)
INK = (14, 12, 10)
LOCK_COL = (176, 150, 162)
WNAME = {"W": "WEST", "N": "NORTH", "E": "EAST", "S": "SOUTH"}
DISPATCH = {
    "start": "Meridian Freight. Four walls, four gaps. The crane plays them like a shell game: two turns in, two out.",
    "n1": "North gap's plugged right now. Step into the container while it sits in the wall, or go under through the port.",
    "sn": "You're in the box. Step out over the gap now, or stay put: the crane's coming, it takes you to the train.",
    "qn": "Platform. Only way here is in a box. Shop's open, then up the tower.",
    "e1": "East box just landed back in the wall. Gap's closed: go.",
    "s1": "South box is on the train. Gap's open. It's the port or nothing.",
}


def _badge():
    cache = {}

    def f(px):
        if px in cache:
            return cache[px]
        S2 = 4
        P = px * S2
        im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([2 * S2, 2 * S2, P - 2 * S2, P - 2 * S2], fill=HAZ + (255,), outline=INK + (255,), width=3 * S2)
        for k in range(8):
            a = math.radians(k * 45 + 22)
            r0, r1 = P * 0.40, P * 0.47
            d.line([(P / 2 + r0 * math.cos(a), P / 2 + r0 * math.sin(a)), (P / 2 + r1 * math.cos(a), P / 2 + r1 * math.sin(a))],
                   fill=INK + (255,), width=2 * S2)
        # a container (ribbed box) hanging from a hook line
        d.line([(P * 0.5, P * 0.16), (P * 0.5, P * 0.34)], fill=INK + (255,), width=int(P * 0.05))
        d.line([(P * 0.30, P * 0.36), (P * 0.70, P * 0.36)], fill=INK + (255,), width=int(P * 0.05))
        d.rectangle([P * 0.22, P * 0.40, P * 0.78, P * 0.70], fill=INK + (255,))
        for x in (0.32, 0.43, 0.54, 0.65):
            d.line([(P * x, P * 0.44), (P * x, P * 0.66)], fill=HAZ + (255,), width=int(P * 0.025))
        cache[px] = im.resize((px, px), Image.LANCZOS)
        return cache[px]
    return f


BADGE = _badge()
WHERE = {"wall": "IN THE WALL", "train": "ON THE TRAIN"}


def _shuttle(i):
    return len(i) == 2 and i[0] == "s" and i[1].upper() in G.WALLS


def node_mark(i, state, mech):
    if _shuttle(i) and state != "grey":
        w = i[1].upper()
        where = WHERE[mech["shuttles"][w]]
        if mech.get("lifting") == w:
            where = "LIFTING"
        return dict(badge=BADGE, chip=(where, HAZ) if state in ("option", "reach", "current") else None, chip_at="below")
    if i[0] == "q" and len(i) == 2 and state in ("option", "reach"):
        return dict(chip=("BY CONTAINER ONLY", HAZ), chip_at="below")
    return None


def _centre(poly):
    return (sum(q[0] for q in poly) / 4, sum(q[1] for q in poly) / 4)


def _locked(img, A, ov, mech, pose, walked, mt):
    """Dashed dim links + a padlock with LANDS IN n (the container's return), for gated links that are off now."""
    import hq_cam as CR
    cab = S.Cables()
    marks = []
    for (a, b) in G.locked_edges(walked, int(mt)):
        path = G.edge_path(a, b, mt)
        vis = []
        for k in range(len(path) - 1):
            mid = [(path[k][j] + path[k + 1][j]) / 2 for j in range(3)]
            vis.append(CR.visible_n(G.seg_normal(mid), mid, pose, -0.05))
        if not any(vis):
            continue
        q = [pose.proj(p) for p in path]
        if any(v is None for v in q):
            continue
        cab.dashed(q, LOCK_COL, 3, on=12, off=10, casing=2, a=230)
        L = [math.hypot(q[k + 1][0] - q[k][0], q[k + 1][1] - q[k][1]) for k in range(len(q) - 1)]
        tot, acc, half = sum(L), 0.0, sum(L) / 2
        mid = q[0]
        for k, l_ in enumerate(L):
            if acc + l_ >= half and l_ > 0:
                f = (half - acc) / l_
                mid = (q[k][0] + (q[k + 1][0] - q[k][0]) * f, q[k][1] + (q[k + 1][1] - q[k][1]) * f)
                break
            acc += l_
        w = (a if _shuttle(a) else b)[1].upper()
        marks.append((mid, mech["lands_in"].get(w, 1)))
    img = cab.comp(img)
    for (mx, my), n in marks:
        r = 12
        d = ImageDraw.Draw(img)
        d.ellipse([mx - r, my - r, mx + r, my + r], fill=(24, 22, 32, 255), outline=LOCK_COL + (255,), width=2)
        g = RL.glyph("state_locked", int(r * 1.3), fill=(220, 216, 232), ow=0)
        img.alpha_composite(g, (int(mx - g.width / 2), int(my - g.height / 2)))
        img, _ = KT.chip(img, (mx + 18, my), "LANDS IN %d" % n, LOCK_COL, 12, anchor="lm", pad=5)
    return img


def marks(img, A, ov, mech, pose):
    walked = ov["walked"]
    mt = A.get("mt", len(walked) - 1)
    if not ov.get("extra", {}).get("no_locks"):
        img = _locked(img, A, ov, mech, pose, walked, mt)
    if ov.get("extra", {}).get("no_telegraph"):
        return img
    t = int(math.floor(mt + 1e-6))
    pr = KT.pencil(KT.PEN_Y, 611)
    drew = False
    for w in G.mover_order(t):
        s_ = "s" + w.lower()
        now = [pose.proj(p) for p in G.room_front(s_, t)]
        nxt = [pose.proj(p) for p in G.room_front(s_, t + 1)]
        if any(q is None for q in now + nxt):
            continue
        c0, c1 = _centre(now), _centre(nxt)
        if not (60 < c1[0] < 1860 and 160 < c1[1] < 1020) or not (0 < c0[0] < 1920 and 0 < c0[1] < 1080):
            continue
        if math.hypot(c1[0] - c0[0], c1[1] - c0[1]) < 20:
            continue
        rx = abs(nxt[1][0] - nxt[0][0]) / 2 + 20
        ry = abs(nxt[0][1] - nxt[3][1]) / 2 + 16
        pr.circle(c1[0], c1[1], max(rx, 26), max(ry, 20), width=5)
        dx, dy = c1[0] - c0[0], c1[1] - c0[1]
        L = math.hypot(dx, dy)
        a0 = (c0[0] + dx / L * 30, c0[1] + dy / L * 30 - 20)
        a1 = (c1[0] - dx / L * (max(rx, 26) + 6), c1[1] - dy / L * (max(ry, 20) + 6))
        if math.hypot(a1[0] - a0[0], a1[1] - a0[1]) > 30:
            mid = ((a0[0] + a1[0]) / 2, min(a0[1], a1[1]) - 0.25 * L - 20)
            pr.arrow([a0, mid, a1], width=4, head=16)
        word = "NEXT: %s %s" % (WNAME[w], "-> TRAIN" if G.shuttle_at(w, t + 1) == "train" else "-> WALL")
        pr.text(word, c1[0], c1[1] - max(ry, 20) - 20, 22, angle=-4)
        drew = True
    if drew:
        img = S.finish_pencil(img, pr, col=KT.PEN_Y)
    return img


def dial(img, x, y, mech, ov):
    x = x - 30
    box = (x, y, x + 306, y + 176)
    img = KT.term(img, box, "THE SHUTTLES", accent=HAZ, seed=29)
    f = K.F(K.MONO, 13)
    K.text(img, (x + 16, y + 46), "TURN %d   crane next: %s" % (mech["turn"], " + ".join(WNAME[w] for w in mech["crane_next"])),
           f, HAZ, "lm", 0.2)
    for k, w in enumerate(G.WALLS):
        yy = y + 72 + k * 22
        now, nxt = mech["shuttles"][w], mech["shuttles_next"][w]
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        cx = x + 26
        if now == "wall":
            ld.rectangle([cx - 8, yy - 7, cx + 8, yy + 7], fill=HAZ + (230,))
        else:
            ld.rectangle([cx - 8, yy - 7, cx + 8, yy + 7], outline=HAZ + (200,), width=2)
        img.alpha_composite(lay)
        K.text(img, (x + 44, yy), "%-6s %-5s" % (WNAME[w], now.upper()), f, HAZ if now == "wall" else (210, 200, 160),
               "lm", 0.2)
        tail = ("-> %s" % nxt.upper()) if nxt != now else ("in %d" % mech["lands_in"].get(w, 0))
        K.text(img, (x + 196, yy), tail, f, (255, 236, 150) if nxt != now else (150, 168, 190), "lm", 0.2)
    K.text(img, (x + 16, y + 164), "2 turns in the wall, 2 on the train", K.F(K.MONO, 12), (150, 168, 190), "lm", 0.3)
    return img


def rule_note(i, walked, mech):
    if i[0] == "q" and len(i) == 2:
        return ("RIDE THE CONTAINER: the crane lifts it (and you) to the train this turn; step off onto the freight "
                "platform: a %s you can only reach by container" % ("RACK" if G.KIND[i] == "rack" else "SHOP"), HAZ)
    if _shuttle(i):
        return ("STEP INTO THE CONTAINER: it sits in the wall this turn; next turn step out over the gap or ride it out",
                HAZ)
    if i[0] == "b" and len(i) == 2:
        return ("THE SALLY PORT: under the gap, always open (a fight)", (140, 255, 170))
    return ("STEP OUT OVER THE GAP: live while the container sits in the wall", (140, 255, 170))


def legend_items():
    def ringy(px):
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse([3, 3, px - 4, px - 4], outline=KT.PEN_Y + (255,), width=4)
        return im

    def lock(px):
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for k in range(3):
            d.line([(2 + k * px / 3, px / 2), (2 + k * px / 3 + px / 6, px / 2)], fill=LOCK_COL + (255,), width=3)
        return im
    return [(BADGE, "container"), (lock, "locked: container away"), (ringy, "next move")]


SHEET = {
    "title": "MERIDIAN FREIGHT v2  //  THE SHUTTLES: links switched by container position (design-language proposal)",
    "sub": "Row 1: rooms of the decision render in each state (the real overlay code). A shuttle = a room in a container "
           "the crane moves between the WALL and the TRAIN; dashed + padlock = a link that container switched off.",
    "tiles": [("OPEN (next)", "n2", "option", S.ORANGE), ("SHUTTLE (current)", "sn", "current", S.LIME),
              ("BY CONTAINER ONLY", "qn", "option", S.ORANGE), ("WALKED", "n1", "walked", S.LIME),
              ("AHEAD", "t2", "reach", S.WHITE), ("PAST", "bn", "grey", S.GREY)],
    "shots": [("S_link_live", ["TURN 5  the north container sits IN THE WALL:", "n1 -> container is live (solid)."]),
              ("S_in_transit", ["TURN 6 -> 7  you stayed in: the crane lifts the", "container (and you) to the train."]),
              ("S_link_dead", ["TURN 13  the south container is ON THE TRAIN:", "the gap is open, link dashed: the port."])],
    "cards": [("THE SHUTTLES  (designer review 2026-10-15; PROPOSAL)", [
        "The route rings all four walls. One BREACH per wall; its container",
        "sits 2 turns IN THE WALL, 2 ON THE TRAIN (the crane swaps the N/S",
        "pair one turn, the E/W pair the next).",
        "In the wall: P -> container -> N live (cross the gap).",
        "Lifted / on the train: container -> platform live (the RIDE):",
        "the platform's SHOP / RACK is reachable ONLY by container.",
        "The sally port under each gap is always open (a fight)."], HAZ, 1020),
        ("WHAT IS REAL (GDD) AND WHAT IS PROPOSED", [
            "GDD 11.7: the boss Site is Meridian's Central Server, THE MASTER",
            "MANIFEST (8.4b still says 'The Manifest': flagged). Netrun = GDD 4.2.",
            "Not in the GDD: the HQ compound, the shuttles, the ride.",
            "Bible 4.4 / 4.7: container fortress, crane keep, rail yard, train;",
            "links that change de-power and are re-made (kept: dashed + lock).",
            "Yellow pencil = the next move (round 43). Route colours unchanged."], (140, 200, 255), 1030)],
}
