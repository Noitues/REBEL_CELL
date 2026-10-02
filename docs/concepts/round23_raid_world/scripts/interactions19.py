"""Round 19: one example crop per raid interaction (interactions.md), on two sheets.

Every tactical mark follows GDD 7 / raid_resolver.gd:
  - only DECOY / HONEYPOT (decoy_pull) change threat routing; guns never do;
  - threats stop at each live node they enter; a disabled node hit again is seized;
  - disabling spreads 50 % of the excess damage to adjacent claimed nodes (cascade);
  - a threat still on a node when the raid ends seizes it; damage reaching home lowers home integrity.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import finish19 as FN  # noqa: E402
import netdecal19 as ND  # noqa: E402
import ui19 as U  # noqa: E402
import screens19 as SC  # noqa: E402

TW, TH = 440, 248          # tile size on the sheet
CW, CH = 520, 293          # crop size from the 1920 frame
P = SC.P
N = LY.NODES


def at(key):
    if key in N:
        return P(*N[key][:2])
    return P(*LY.ENTRIES[key])


def tile(tag, decorate, centre, over=None, mode="night", frame_pre=None):
    img = FN.finish(tag, mode, decorate=decorate, seed=1)
    if frame_pre:
        img = frame_pre(img)
    if over:
        img = over(img)
    cx, cy = centre
    x0 = int(min(max(0, cx - CW / 2), 1920 - CW))
    y0 = int(min(max(0, cy - CH / 2), 1080 - CH))
    return SC.crop(img, (x0, y0, x0 + CW, y0 + CH), (TW, TH)), (x0, y0)


def pencil(fn, seed=7):
    def over(img):
        L = U.pencil_layer(seed)
        fn(L)
        return U.pencil_composite(img, L)
    return over


def chain(*fs):
    def over(img):
        for f in fs:
            img = f(img)
        return img
    return over


def sticker_at(sd, x, y, angle=0.0, **kw):
    return lambda img: U.place(img, sd, x, y, angle=angle, **kw)


def panel_at(pn, x, y):
    return lambda img: U.put_panel(img, pn, x, y)


SET = SC.setup_decor
WAVE = SC.wave_decor


def card(name, gloss_k=0.22):
    t = next(t for t in U.TRAY if t[0] == name)
    return U.asset_card(*t[:5], t[5], 60, gloss_k=gloss_k)


# ------------------------------------------------------------------ the interactions (id, title, medium line, builder)
def setup_tiles():
    vx, vy = at("vault")
    rx, ry = at("relay")
    px, py = at("proxy")
    fx, fy = at("firewall")
    T = []

    # 1 pick up a card
    def d1(net):
        ND.setup_state(net, skip=("relay", "firewall", "safe", "vault"))
        for k in ("relay", "firewall", "safe", "vault"):
            net.pad(k, "holds" if k != "vault" else "holds", 1.0, flash="hover")
    T.append(("PICK UP A DEFENCE", "sticker peels off the tray; every valid socket lights white",
              tile("setup_h1", d1, (vx - 120, vy + 150), chain(sticker_at(card("ICE LOCK", 1.0), vx - 40, vy + 250, -10, hover=0.8)))))

    # 2 hover a valid node
    def d2(net):
        ND.setup_state(net, skip=("vault",))
        net.pad("vault", "holds", 1.0, forecast="holds", flash="hover")
    T.append(("HOVER A VALID NODE", "white frame + forecast ring turns green; pencil arrow + circle; IF PLACED terminal",
              tile("setup_h1", d2, (vx + 40, vy + 60), chain(
                  pencil(lambda L: (U.pen_circle(L, vx, vy, 76, 50, U.Y_PEN, 7.0, 1.2), U.pen_arrow(L, [(vx + 150, vy + 170), (vx + 110, vy + 90), (vx + 66, vy + 50)], U.Y_PEN))),
                  sticker_at(card("ICE LOCK"), vx + 200, vy + 210, -9, hover=0.7)))))

    # 3 route redirect preview (DECOY pulls route B to the relay)
    old = LY.route_points("r2")
    new = [LY.ENTRIES["e_west"], (N["proxy"][0], N["proxy"][1]), (N["relay"][0], N["relay"][1])]

    def d3(net):
        ND.setup_state(net, routes=("r1", "r3"), skip=("relay",))
        ND.lanes_on_street(net, old, style="ghost")
        ND.lanes_on_street(net, new, style="dashed")
        net.pad("relay", "holds", 1.0, forecast="disabled", flash="hover")

    def p3(L):
        U.pen_circle(L, rx, ry, 74, 48, U.Y_PEN, 7.0)
        a = P(-60, 0)
        b = P(-60, -32)
        U.pen_arrow(L, [P(-95, 20), P(-62, 14), a, b], U.R_PEN, 5.5, 16, dashed=True)
    T.append(("ROUTE REDIRECT PREVIEW", "DECOY (pull 3) on RELAY: route B leaves the firewall road (ghost) for the relay (dashed)",
              tile("setup_h1", d3, ((rx + px) / 2 + 60, (ry + py) / 2 - 20), chain(pencil(p3), sticker_at(card("DECOY"), rx + 190, ry + 60, 8, hover=0.7)))))

    # 4 invalid drop (seized proxy)
    def d4(net):
        ND.setup_state(net, skip=("proxy",))
        net.pad("proxy", "seized", 0.0, flash="invalid")
    T.append(("INVALID DROP", "red frame + X on a seized / full socket; the card snaps back to the tray",
              tile("setup_h1", d4, (px + 60, py + 60), chain(sticker_at(card("TURRET"), px + 150, py + 130, 12, hover=0.5)))))

    # 5 placed
    def d5(net):
        ND.setup_state(net, skip=("vault",))
        net.pad("vault", "holds", 1.0, flash="place")
    T.append(("DEFENCE PLACED", "lime ripple out of the socket, the model drops in, tray count x1 > x0",
              tile("setup_h1", d5, (vx, vy + 40), panel_at(U.terminal("IF IT RAN NOW", [("kv", "VAULT", "DISABLED > HOLDS", U.GREEN), ("kv", "HOME", "42 > 45", U.PINK)], w=270, accent=U.GREEN), vx - 300, vy + 70))))

    # 6 remove placed
    def d6(net):
        ND.setup_state(net, skip=("safe",))
        net.pad("safe", "holds", 1.0, forecast="disabled")
    sx, sy = at("safe")
    T.append(("REMOVE A DEFENCE", "drag the unit off its socket back to the tray; forecast ring re-projects (amber)",
              tile("setup_h1", d6, (sx - 40, sy + 30), chain(
                  pencil(lambda L: U.pen_arrow(L, [(sx, sy - 10), (sx - 70, sy + 50), (sx - 150, sy + 90)], U.Y_PEN, 6.0, 18, dashed=True)),
                  sticker_at(U.asset_card("SENTRY", "picto_target", 12, 1, ["3 dmg x2", "own node only"], U.GREEN, 61), sx - 190, sy + 120, -8, hover=0.6)))))

    # 7 move / swap between nodes
    def d7(net):
        ND.setup_state(net, skip=("firewall", "relay"))
        net.pad("firewall", "holds", 1.0, forecast="holds")
        net.pad("relay", "holds", 1.0, forecast="holds", flash="hover")
    T.append(("MOVE / SWAP", "drag a placed unit from node to node; both forecasts update; dropping on an occupied slot swaps",
              tile("setup_h1", d7, ((fx + rx) / 2 + 40, (fy + ry) / 2 + 20), pencil(lambda L: (U.pen_arrow(L, [(fx - 10, fy + 10), (fx - 90, fy + 160), (rx + 20, ry - 30)], U.Y_PEN, 6.5, 20, dashed=True),
                                                                                   U.pen_circle(L, rx, ry, 70, 46, U.Y_PEN, 6.0))))))

    # 8 forecast change
    def d8(net):
        ND.setup_state(net, skip=("vault",))
        net.pad("vault", "holds", 1.0, forecast="disabled")
    T.append(("FORECAST CHANGES", "dashed ring = projected outcome (amber > green); numbers tick in the terminal",
              tile("setup_h1", d8, (vx, vy + 40), panel_at(U.terminal("RAID INCOMING", [("kv", "HOME", "42 > 45", U.PINK), ("kv", "DISABLED", "1 > 0", U.AMBER)], w=240, accent=U.HARM), vx + 60, vy + 70))))

    # 9 link frozen at setup (Lockdown Unit)
    def d9(net):
        ND.setup_state(net, link_states={("core", "firewall"): "frozen"})
    T.append(("LINK FROZEN (SETUP)", "LOCKDOWN UNIT freezes the busiest link to home: the inlay frosts over; nothing crosses it",
              tile("setup_h1", d9, ((fx + 960) / 2, (fy + 590) / 2))))

    # 10 threat routes revealed
    def p10(L):
        SC.routes_pencil(L)
    T.append(("THREAT ROUTES REVEALED", "red trace lanes from each corp entry socket; pencil circles + letters match THREAT INTEL",
              tile("setup_h1", SET(), (1300, 560), pencil(p10))))

    # 11 start defense
    T.append(("START DEFENSE", "the one sticker button; press = slap-down squash, then the tray peels away",
              tile("setup_h1", SET(), (1600, 900), chain(SC.start_button))))

    # 12 day read
    T.append(("DAY READ", "no fog at this zoom by day; the inlay keeps its lime and status colours",
              tile("setup_h1", SET(), (960, 560), mode="day")))
    return T


def wave_tiles():
    sp = SC.wave_spots()
    T = []

    def sp2(k):
        return P(*sp[k][:2], sp[k][2])

    def base_wave(**kw):
        return WAVE(**kw)

    # 13 wave incoming
    ex, ey = at("e_west")
    T.append(("WAVE INCOMING", "entry socket pulses red rings; pencil INCOMING (static state); feed + countdown in the terminal",
              tile("wave_h2", base_wave(), (ex + 140, ey - 60), pencil(lambda L: (U.pen_circle(L, ex, ey, 50, 33, U.R_PEN), U.pen_text(L, "INCOMING", ex + 20, ey - 58, 18, U.R_PEN, 4.2))))))

    # 14 threat moving
    bx, by = sp2("bailiff")
    T.append(("THREAT MOVING", "red ring under the unit (lit segments = HP), its lane lights ahead; corp vehicle model",
              tile("wave_h2", base_wave(), (bx - 30, by + 40))))

    # 15 defence fires
    hx, hy = sp2("hauler")
    rng = np.random.default_rng(3)
    T.append(("DEFENCE FIRES / HIT", "tracer + binary shards + rising numeral (live, L3); the feed logs it",
              tile("wave_h2", base_wave(), (hx + 60, hy + 20), lambda img: U.float_number(U.shards(img, hx, hy - 10, rng, 24), hx + 26, hy - 44, "-6", size=30))))

    # 16 threat held (ICE LOCK)
    ix, iy = sp2("inspector")

    def d16(net):
        WAVE(rings=False)(net)
        net.threat_ring(sp["inspector"][0], sp["inspector"][1], 0.5, "held")
        for k, hp in (("bailiff", 0.35), ("hauler", 0.6), ("customs", 0.6), ("lander", 1.0)):
            net.threat_ring(sp[k][0], sp[k][1], hp)
    T.append(("THREAT HELD (ICE LOCK)", "the ring freezes into an ice crystal for its 2 steps",
              tile("wave_h2", d16, (ix + 20, iy + 40))))

    # 17 threat lured by a decoy
    def d17(net):
        WAVE()(net)
        net.lane([(sp["customs"][0], sp["customs"][1]), (-60, -120)], style="dashed", trim=(False, False))
        net.lane([(-60, -120), (-60, -50)], style="dashed", trim=(False, True))
    cx, cy = sp2("customs")
    T.append(("THREAT LURED (DECOY)", "a DECOY on the RELAY pulls the customs unit off its lane: a dashed lane bends to the decoy's node",
              tile("wave_h2", d17, (cx - 150, cy - 20))))

    # 18 unit destroyed
    ux, uy = sp2("courier")
    T.append(("UNIT DESTROYED", "ring breaks into a grey X on the street; pencil X + DOWN stays (static)",
              tile("wave_h2", base_wave(), (ux, uy + 30), pencil(lambda L: (U.pen_x(L, ux, uy, 20), U.pen_text(L, "DOWN", ux + 4, uy - 44, 17, U.R_PEN, 4.0))))))

    # 19 node hit / damaged
    sx, sy = at("safe")

    def d19(net):
        WAVE(extra=lambda n: n.link("safe", "core", "hot"))(net)
    T.append(("NODE HIT", "integrity track drains clockwise, cracks spread, a surge runs down its link",
              tile("wave_h2", d19, (sx, sy - 20))))

    # 20 node disabled + cascade
    pxx, pyy = at("proxy")

    def d20(net):
        st = dict(SC.WAVE_ST)
        ND.setup_state(net, forecast=False, statuses=st, integ=dict(SC.WAVE_INTEG, firewall=0.62, relay=0.7), routes=(),
                       link_states={("proxy", "firewall"): "hot", ("relay", "proxy"): "hot"})
    T.append(("NODE DISABLED + CASCADE", "dashed amber frame, pins dark, riser dims; 50% excess surges to neighbours",
              tile("setup_h1", d20, (pxx + 90, pyy + 10))))

    # 21 node seized
    def d21(net):
        st = dict(SC.WAVE_ST)
        st["proxy"] = "seized"
        ND.setup_state(net, forecast=False, statuses=st, integ=SC.WAVE_INTEG, routes=())
    T.append(("NODE SEIZED", "a threat on a disabled node: violet corp hatch + corp mark, links go dead; pencil LOST",
              tile("setup_h1", d21, (pxx + 90, pyy + 10), pencil(lambda L: U.pen_text(L, "LOST", pxx, pyy - 60, 22, U.R_PEN, 4.8)))))

    # 22 node destroyed (removed after the raid)
    def d22(net):
        st = dict(SC.WAVE_ST)
        st["proxy"] = "burnt"
        ND.setup_state(net, forecast=False, statuses=st, integ=SC.WAVE_INTEG, routes=())
    T.append(("NODE LOST (REPORT)", "seized node removed: burnt socket with embers until reclaimed + reinstalled",
              tile("setup_h1", d22, (pxx + 90, pyy + 10))))

    # 23 threat reaches home
    def d23(net):
        WAVE(extra=lambda n: n.pad("core", "home", 0.82))(net)
    T.append(("THREAT REACHES HOME", "CORE track drops, pink flash; HOME 50 > 41 in the terminal",
              tile("wave_h2", d23, (960, 590), panel_at(U.terminal("RAID", [("kv", "HOME", "50 > 41", U.PINK)], w=200, accent=U.HARM), 1030, 640))))

    # 24 spotlight on a node (PROPOSAL)
    vx, vy = at("vault")

    def d24(net):
        WAVE(extra=lambda n: n.pad("vault", "damaged", 0.3, exposed=True))(net)
    T.append(("SPOTLIGHT: EXPOSED*", "*PROPOSAL: a spotlit node takes extra damage; white hazard ticks round the socket",
              tile("wave_h2", d24, (vx, vy - 40))))

    # 25 heat escalation mid-raid
    T.append(("HEAT ESCALATION", "a threshold crossed: another chopper enters from the frame edge; terminal banner",
              tile("setup_h3", SET(routes=("r1", "r2", "r3")), (1560, 300), panel_at(U.terminal("HEAT 75", [("t", "THRESHOLD: RAID STRENGTH +25%", U.HARM)], w=280, accent=U.HARM), 1440, 420))))

    # 26 wave cleared
    def d26(net):
        ND.setup_state(net, forecast=False, statuses=SC.WAVE_ST, integ=SC.WAVE_INTEG, routes=(), packets=True)
    T.append(("WAVE CLEARED", "lanes drain, entry sockets dim, packets flow home again",
              tile("wave_h2", d26, (960, 600), panel_at(U.terminal("WAVE 1 / 2", [("t", "CLEARED  //  NEXT AT STEP 9", U.GREEN)], w=260, accent=U.GREEN), 1000, 660))))

    # 27 defended
    def d27(net):
        st = {k: ("home" if k == "core" else "holds") for k in N}
        ND.setup_state(net, forecast=False, statuses=st, routes=(), packets=True)
    T.append(("SUCCESSFULLY DEFENDED", "every socket green, a pulse runs the whole network; result stamp sticker (final, static)",
              tile("setup_h1", d27, (960, 590), sticker_at(U.word_sticker(["CELL HOLDS"], 40, [U.FILL_YELLOW], seed=31, border=12), 1050, 470, -4))))

    # 28 raid lost / home breached
    def d28(net):
        st = dict(SC.WAVE_ST)
        st["core"] = "home"
        ND.setup_state(net, forecast=False, statuses=st, integ=dict(SC.WAVE_INTEG, core=0.0), routes=("r1", "r2", "r3"))
        net.pad("core", "burnt", 0.0)
    T.append(("HOME BREACHED / LOST", "CORE socket burns out; pencil BREACHED; terminal CAMPAIGN LOST",
              tile("wave_h2", d28, (960, 590), chain(pencil(lambda L: U.pen_text(L, "BREACHED", 980, 500, 26, U.R_PEN, 5.5)),
                                                     panel_at(U.terminal("RAID RESULT", [("t", "HOME 0  //  CAMPAIGN LOST", U.HARM)], w=280, accent=U.HARM), 990, 640)))))

    # 29 playout speed / skip
    T.append(("SPEED / SKIP", "live terminal strip: 1x 2x 4x SKIP + step counter (changes, so never a sticker)",
              tile("wave_h2", base_wave(), (960, 920), panel_at(U.speed_terminal("4x"), 745, 1000))))
    return T


def sheet(tiles, name, head, sub):
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    cv = np.zeros((1080, 1920, 3), np.float32) + SC.BG
    cv = SC.title(cv, head, sub)
    for i, (t, desc, (img, _)) in enumerate(tiles):
        r, c = divmod(i, cols)
        x, y = 40 + c * (TW + 23), 136 + r * (TH + 56)
        cv = SC.paste(cv, img, x, y)
        cv = SC.label(cv, x, y + TH + 4, "%02d  %s" % (TILE_NO[0], t), 16, (230, 236, 245), font=U.SL.ANTON)
        TILE_NO[0] += 1
        lines, cur = [], ""
        for wd in desc.split(" "):
            if len(cur) + len(wd) + 1 > 72:
                lines.append(cur)
                cur = ""
            cur += wd + " "
        lines.append(cur)
        for li, ln in enumerate(lines[:2]):
            cv = SC.label(cv, x, y + TH + 26 + li * 13, ln, 11, (160, 175, 195))
    SC.save(cv, name)


TILE_NO = [1]


def build():
    TILE_NO[0] = 1
    sheet(setup_tiles(), "interactions_sheet.png", "RAID SETUP", "INTERACTIONS 01-12  //  see interactions.md  //  pencil = static states + plans only, all true to GDD 7")
    w = wave_tiles()
    sheet(w[:12], "interactions_sheet_2.png", "RAID IN PROGRESS", "INTERACTIONS 13-24  //  live info in terminals, the inlay and floats; pencil only for static states")
    sheet(w[12:], "interactions_sheet_3.png", "RAID END", "INTERACTIONS 25-29  //  escalation, wave cleared, defended, breached, speed")


if __name__ == "__main__":
    build()
