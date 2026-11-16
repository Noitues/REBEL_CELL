"""Plate 1: street_branch.png. The approved staged street (golden_plates/street_overview.png framing) with a real
Campaign B fork -> two lanes -> rejoin, the hovered lane in round 7b pick B, the other lane dimmed but readable.

Data (not invented): port-campaign-b content/b/street_sample/b_street_sample_seed2_tier2.tres, layers 5-8:
  L5 51 r0 fight>61 | 52 r1 elite>61,62 (YOU) | 53 r2 fight>63 | 54 r3 shop>64
  L6 61 r0 fight>71 | 62 r1 event>72 | 63 r2 elite>71,72,73 | 64 r3 fight>73
  L7 71 r0 fight>81 | 72 r2 fight>81 | 73 r3 fight>81
  L8 81 r3 rack (final SERVER RACK, "roof relay")
Rows are stories (BStreetRulesData.story_labels: ground floor .. top floor), so a lane is a run of rooms on floors.
Run: python street_branch.py
"""
import json

from PIL import Image, ImageDraw

import sb_lib as B

SAMPLE = "b_street_sample_seed2_tier2.tres"
FIRST, LAST = 5, 8
CUR = 52
HOVER = 62                      # the option the player points at (lane 2)
COL_X = {5: 520, 6: 880, 7: 1130, 8: 1420}
RW, RH, PITCH, ROW0_TOP = 86, 50, 66, 786
STK = 40                        # sticker px (ZOOM_RULES 6.3: every available node >= 40 px tall)


def load():
    s = json.load(open(B.SCR + "/samples.json"))[SAMPLE]
    return {n["id"]: n for n in s["nodes"]}, s


def box_of(n):
    x = COL_X[n["layer"]]
    top = ROW0_TOP - PITCH * n["row"]
    return (x - RW // 2, top, x + RW // 2, top + RH)


def stk_xy(n):
    x0, y0, x1, y1 = box_of(n)
    return (x0 + 2, (y0 + y1) / 2)


def main(variant="A"):
    """variant A (band): pick B from the fork through the hovered lane to the rejoin, beam from the rejoin.
    variant B (next only): pick B on the hovered next room only, beam from that room; the rest of the lane is plain
    'ahead' (white dashes, full rooms)."""
    N, s = load()
    win = {i: n for i, n in N.items() if FIRST <= n["layer"] <= LAST}
    opts = N[CUR]["links"]                                    # [61, 62]
    lanes = {}
    for o in opts:                                            # follow each option to the rejoin
        p = [CUR, o]
        while N[p[-1]]["links"]:
            nx = N[p[-1]]["links"]
            p.append(nx[0] if len(nx) == 1 else min(nx))
        lanes[o] = p
    reach = set()
    for p in lanes.values():
        reach.update(p[2:])
    lane_hi = lanes[HOVER]
    lane_lo = [p for o, p in lanes.items() if o != HOVER][0]
    print("lanes", lanes)

    def state(i):
        if i == CUR:
            return "current"
        if i in opts:
            return "option"
        if i in reach:
            return "ahead"
        return "grey"

    img = Image.open(B.GOLDEN).convert("RGBA")

    # pick B lane band: from the fork through the hovered lane to the rejoin (the street-level twin of the
    # city band's segment highlight); band is wider than a room so its edge runs clear of the rooms
    cen = lambda i: ((box_of(N[i])[0] + box_of(N[i])[2]) / 2, (box_of(N[i])[1] + box_of(N[i])[3]) / 2)
    pts = [cen(i) for i in lane_hi]
    band_pts = [(pts[0][0] - 30, pts[0][1])] + B.link_path(pts[0], pts[1])[1:]
    for a, b in zip(pts[1:], pts[2:]):
        band_pts += B.link_path(a, b)[1:]
    band_pts.append((pts[-1][0] + 30, pts[-1][1]))
    if variant == "A":
        mask = B.lane_mask(img.size, band_pts, RH + 30)
    else:
        # B: a pick B pad round the hovered next room only (a rounded block one slab wider than the room)
        hb = box_of(N[HOVER])
        cx, cy = (hb[0] + hb[2]) / 2, (hb[1] + hb[3]) / 2
        # a rounded pad 14 px proud of the room's cut edge sideways, 8 px up and down (the slab gap to the rooms
        # stacked above / below is 16 px, so the pink edge stays visible between them)
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([hb[0] - 34, hb[1] - 16, hb[2] + 16, hb[3] + 12], radius=10, fill=255)
    img = B.grade(img, mask, k_out=0.86, desat_out=0.12)

    # rooms: every node of the window is a real room (whole graph shown, bible 4.6)
    lo_set = set(lane_lo[1:-1]) - set(lane_hi)
    # the fill sits on the facade (as it sits on the road lots in the city band); the rooms stay clear
    img = B.pick_b(img, mask)
    if variant == "B":
        # beam from the hovered room, drawn before the rooms so the rooms stacked above occlude it
        hb = box_of(N[HOVER])
        img = B.beam(img, (hb[0] + hb[2]) / 2, 0, hb[1] - 8, k=3.0)
    for i, n in sorted(win.items()):
        st = state(i)
        mode = "grey" if st == "grey" else ("dim" if i in lo_set else "full")
        img = B.room(img, n["type"], box_of(n), mode)
    if variant == "A":
        # beam (pick B beam_k 3.0) from the lane's end: the final SERVER RACK on the top floor, rising to the sky
        end = box_of(N[lane_hi[-1]])
        img = B.beam(img, (end[0] + end[2]) / 2, 0, end[1] - 8, k=3.0)

    # room frames in the state colour (route view: the room's cut edge carries the state)
    for i, n in win.items():
        st = state(i)
        col = {"current": B.LIME, "option": B.ORANGE, "ahead": B.WHITE, "grey": B.GREY}[st]
        dim = i in lo_set
        al = {"grey": 0.35, "ahead": 0.75}.get(st, 1.0) * (0.6 if dim else 1.0)
        img = B.frame_room(img, box_of(n), col, 3 if st in ("current", "option") else 2, al,
                           glow=st in ("current", "option") and not dim)

    # wax links (wax_r2 grammar): walked lime, options orange (hovered solid, other dimmed),
    # ahead white dashes (solid on the hovered branch), cut off grey translucent
    clear = [(stk_xy(n)[0], stk_xy(n)[1], STK * 0.62 + 7) for n in win.values()]
    grey_paths, ahead_lo, ahead_hi = [], [], []
    for i, n in win.items():
        for j in n["links"]:
            if j not in win:
                continue
            p = B.link_path(stk_xy(n), stk_xy(N[j]))
            if i == CUR:
                continue
            on_hi = i in lane_hi and j in lane_hi
            on_lo = i in lane_lo and j in lane_lo
            if on_hi:
                ahead_hi.append(p)
            elif on_lo:
                ahead_lo.append(p)
            else:
                grey_paths.append(p)
    img = B.wax(img, grey_paths, B.GREY, 4.0, alpha=0.38, seed=504, clear=clear)
    img = B.wax(img, ahead_lo, B.WHITE, 5.0, alpha=0.55, dash=(14.0, 9.0), seed=503, clear=clear)
    if variant == "A":
        img = B.wax(img, ahead_hi, B.WHITE, 5.6, alpha=1.0, seed=505, clear=clear)
    else:
        img = B.wax(img, ahead_hi, B.WHITE, 5.2, alpha=1.0, dash=(14.0, 9.0), seed=505, clear=clear)
    # walked: in from layer 4 (node 42 r2 rack, off frame left) to the current node
    cxy = stk_xy(N[CUR])
    walked = B.link_path((-20, ROW0_TOP - PITCH * 2 + RH / 2), cxy, bend=0.7)
    img = B.wax(img, [walked], B.LIME, 8.0, seed=501, clear=clear, glow=95)
    for o in opts:
        p = B.link_path(cxy, stk_xy(N[o]))
        if o == HOVER:
            img = B.wax(img, [p], B.ORANGE, 8.5, seed=502, clear=clear, glow=110)
        else:
            img = B.wax(img, [p], B.ORANGE, 7.0, alpha=0.55, seed=506, clear=clear)

    # stickers
    order = {"grey": 0, "ahead": 1, "option": 2, "current": 3}
    for i, n in sorted(win.items(), key=lambda kv: (order[state(kv[0])], kv[0])):
        st = state(i)
        x, y = stk_xy(n)
        if st == "grey":
            t = B.node_tile(n["type"], STK, "grey", grey=True, alpha=0.5, ring_w=2)
        elif i in lo_set:
            t = B.node_tile(n["type"], STK, st, alpha=0.78, ring_w=3)
        else:
            lift = 0.55 if i == HOVER else (0.25 if st == "option" else 0.0)
            t = B.node_tile(n["type"], STK, st, ring_w=4 if st in ("current", "option") else 3, hover=lift)
        img = B.put(img, t, x, y - (4 if i == HOVER else 0))
    for k, o in enumerate(opts):
        x, y = stk_xy(N[o])
        img = B.number_chip(img, x - STK / 2 - 18, y - STK * 0.32, k + 1, alpha=1.0 if o == HOVER else 0.7)
    hx, hy = stk_xy(N[HOVER])
    img = B.KT.cursor(img, hx + 8, hy + 6)

    # in-game key strip (bible 4.6 legend; collapsed, terminal): the six Campaign B words + the ring states
    def ic(kind):
        return lambda px: B.node_tile(kind, int(px * 0.8), None).resize((px, px), Image.LANCZOS)

    def ring_ic(col):
        def f(px):
            t = Image.new("RGBA", (px, px), (0, 0, 0, 0))
            ImageDraw.Draw(t).ellipse([3, 3, px - 4, px - 4], outline=col + (255,), width=3)
            return t
        return f

    items = [(ic(k), B.KINDS[k]["word"]) for k in B.ORDER] + [
        (ring_ic(B.LIME), "you / walked"), (ring_ic(B.ORANGE), "next"), (ring_ic(B.WHITE), "ahead"), (ring_ic(B.GREY), "cut off")]
    _, kb = B.KT.key_strip(Image.new("RGBA", img.size, (0, 0, 0, 0)), 0, 0, items, hint="HOVER: SHOW ALL", scale=0.82)
    kw = kb[2] - kb[0]
    img, kb = B.KT.key_strip(img, int((B.W - kw) / 2), B.H - 62, items, hint="HOVER: SHOW ALL", scale=0.82)
    return img, N, lanes, win, opts, reach


if __name__ == "__main__":
    import street_branch_compose
    street_branch_compose.run()
