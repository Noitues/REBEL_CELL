"""wheel_player.png and wheel_enemy.png (1920x1080)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from circ_lib import OUT, F_NUM, F_SILK, MERIDIAN, PROGRAMS, make_board, make_corp_board, render_tile, hexc  # noqa: E402
from wheel_lib import (backdrop, build_wheel, place, bloom, caption, hp_text, np_img, pointer)  # noqa: E402

SS = 2

PLAYER = [("EXPLOIT", 3, 6, 0.04), ("ZERO-DAY", 2, 12, 0.72), ("PROXY", 3, 4, 0.30), ("FIREWALL", 4, 5, 0.42),
          ("VIRUS", 3, 3, 0.55), ("PATCH", 3, 4, 0.56), ("SANDBOX", 3, 4, 0.30), ("TROJAN", 3, 2, 0.62),
          ("NULL", 3, None, 0.0), ("EXPLOIT", 3, 8, 0.55)]
ENEMY = [("EXPLOIT", 3, 6), ("PROXY", 3, 3), ("VIRUS", 4, 4), ("EXPLOIT", 3, 6), ("FIREWALL", 3, 6),
         ("ZERO-DAY", 2, 14), ("NULL", 3, None), ("EXPLOIT", 3, 8), ("FIREWALL", 3, 6), ("SANDBOX", 3, 4)]


def player_boards(ro=360, ri=130, ss=SS, lod=0):
    bs = []
    for i, (n, tk, v, _) in enumerate(PLAYER):
        bs.append(make_board(n, tk, ro, ri, ss, seed=100 + i, value=v, lod=lod))
    return bs, [p[3] for p in PLAYER]


def enemy_boards(ro=360, ri=130, ss=SS):
    return [make_corp_board(n, tk, ro, ri, ss, value=v, seed=200 + i) for i, (n, tk, v) in enumerate(ENEMY)]


def player_png():
    frame = backdrop()
    bs, ts = player_boards()
    rgb, a, g, P = build_wheel(bs, ts=ts, ss=SS, start_tick=-1.5)
    cx, cy = 960, 470
    frame = place(frame, rgb, a, g, cx, cy, SS)
    frame = bloom(frame)
    img = np_img(frame).convert("RGB")
    hp_text(img, cx, cy + 360 + 120, "60/60")
    pointer(img, cx, cy - 360 - 62, cy - 360 + 20, 1.6)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(F_SILK, 17)
    legend = ["EXPLOIT 6 / ZERO-DAY 12 / PROXY 4 / FIREWALL 5 (4-tick)", "VIRUS 3 / PATCH 4 / SANDBOX 4 / TROJAN 2 / NULL / EXPLOIT 8"]
    for i, s in enumerate(legend):
        d.text((1340, 40 + i * 24), s, font=f, fill=(170, 170, 185))
    caption(img, "s_a_circuit  PLAYER WHEEL  (CIRCUIT BOARD programs)",
            "PCB tiles, neon traces per program; bezel = gold edge-connector fingers; hub = CPU die")
    img.save(os.path.join(OUT, "wheel_player.png"))
    print("player ok", flush=True)


def enemy_png():
    frame = backdrop(seed=9, tint=(0.08, 0.045, 0.03))
    bs = enemy_boards()
    rgb, a, g, P = build_wheel(bs, t=0.3, ss=SS, enemy=True, hub_name="COLLECTIONS AGENT", hub_sub="Meridian Freight",
                               start_tick=-1.5)
    cx, cy = 690, 470
    frame = place(frame, rgb, a, g, cx, cy, SS)
    frame = bloom(frame)
    img = np_img(frame).convert("RGB")
    hp_text(img, cx, cy + 360 + 120, "40/40")
    pointer(img, cx, cy - 360 - 66, cy - 360 + 20, 1.6)
    # close-up panel: three corp tiles at 1.25x, same material, type by glyph + accent only
    d = ImageDraw.Draw(img, "RGBA")
    px, py = 1250, 120
    d.rectangle([px - 20, py - 60, 1900, 820], fill=(8, 6, 6, 200), outline=(255, 140, 26, 120))
    f1 = ImageFont.truetype(F_NUM, 30)
    f2 = ImageFont.truetype(F_SILK, 17)
    d.text((px, py - 50), "MERIDIAN CORPORATE PCB", font=f1, fill=(255, 160, 60))
    d.text((px, py - 12), "one machined board for every slice; type = glyph + thin accent", font=f2, fill=(200, 190, 180))
    x = px
    for n, v in (("EXPLOIT", 6), ("FIREWALL", 6), ("VIRUS", 4)):
        b = make_corp_board(n, 3, 320, 116, SS, value=v, seed=7)
        tile = render_tile(b, 0.3)
        tile = tile.resize((tile.width // SS, tile.height // SS), Image.LANCZOS)
        img.paste(tile, (x, py + 30), tile)
        col = tuple(int(c * 255) for c in hexc(PROGRAMS[n][1]))
        d.text((x + tile.width // 2, py + 30 + tile.height + 18), n, font=f2, anchor="mm", fill=col)
        x += tile.width + 10
    notes = ["substrate: charcoal, lathe-ring machined, no facets",
             "traces: concentric arcs + radial spokes on a fixed pitch",
             "pads: gold on a regular grid (every other node)",
             "outer band: 45-degree container-stripe silkscreen",
             "emissive: Meridian orange only; arcs clock inward",
             "  in lockstep (conveyor), no per-type behaviour",
             "accent: 3 px line on the inner edge in the type colour",
             "bezel: machined orange, stripes, notched edge"]
    for i, s in enumerate(notes):
        d.text((px, py + 330 + i * 32), s, font=f2, fill=(205, 195, 185))
    caption(img, "s_a_circuit  ENEMY WHEEL  Meridian Freight / Collections Agent",
            "corporate PCB: clean, machined, uniform orange; the player's boards are hand-routed, theirs are fabbed",
            accent=(255, 140, 26))
    img.save(os.path.join(OUT, "wheel_enemy.png"))
    print("enemy ok", flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("player", "both"):
        player_png()
    if which in ("enemy", "both"):
        enemy_png()
