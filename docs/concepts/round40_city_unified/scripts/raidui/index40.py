"""Round 40: raid_gifs/index.md + index.jpg for the latest locked version of every raid interaction, re-run in the one
city. Removes the superseded gifs the round 21 builder still writes (02/03 drag, 05 remove, 06 move, 21 lost).
python index40.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GIFS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "raid_gifs")
SUPERSEDED = ["02_drag_valid.gif", "03_drag_invalid.gif", "05_remove_defence.gif", "06_move_swap.gif", "21_node_lost.gif"]

ROWS = [
    ("01_pick_up.gif", "R22", "Pick up a defence", "the card peels out of its slot and parks just above it; valid sockets pulse; the yellow pencil arrow starts from it", "STICKER + PENCIL + INLAY"),
    ("02_drag_dock_preview.gif", "R23", "Drag across nodes (dock preview)", "near a node the arrow stops just outside it and the circle draws on: yellow at a valid node, red circle + X at the full Firewall; moving away erases it", "PENCIL + INLAY + TERMINAL"),
    ("04_placed_ripple.gif", "R21", "Defence placed", "the card drops into the socket, its model stands up; a lime ripple; the forecast ring settles", "STICKER + 3D + INLAY"),
    ("05_remove_to_hand.gif", "R22", "Remove to hand", "the placed sticker peels off the node (model removed), flies to the parked zone and slots back into the hand: x1 > x2", "STICKER + 3D"),
    ("06_swap_one_motion.gif", "R23", "Move / swap in one motion", "press on the placed unit: the sticker peels off to its parking spot while the pencil arrow runs from it to the cursor and resolves on the new node", "STICKER + PENCIL + INLAY"),
    ("07_forecast_change.gif", "R21", "Forecast changes", "dashed ring = projected outcome, re-projects live; terminal numbers count", "INLAY + TERMINAL"),
    ("08_routes_revealed.gif", "R21", "Threat routes revealed", "entry sockets pulse; red grease pencil draws each route A/B/C to its target, along the streets", "INLAY + PENCIL"),
    ("09_decoy_setup.gif", "R21", "Decoy path rules (setup)", "SOLID = active route; hovering the DECOY scribbles out the part that would vanish and draws the new route DASHED; placing it commits", "PENCIL + STICKER"),
    ("10_link_frozen.gif", "R22", "Frozen link", "ice crystals grow inward along the link over a light-blue translucent fill; nothing routes or shoots across it", "INLAY + ICE + TERMINAL"),
    ("11_start_defense.gif", "R21", "START DEFENSE", "the one sticker button slaps down, the setup UI peels away", "STICKER"),
    ("12_wave_incoming.gif", "R21", "Wave incoming", "the entry socket rings red; pencil INCOMING writes, holds, wipes", "INLAY + PENCIL"),
    ("13_threat_moving.gif", "R21", "Threat moving", "the corp vehicle drives the street with its red ring (lit segments = HP)", "3D + INLAY"),
    ("14_defence_fires.gif", "R21", "Defence fires / hit", "tracer, binary 0/1 shards, a rising numeral; the ring loses segments", "FLOAT + INLAY"),
    ("15_threat_held_ice.gif", "R22", "Frozen unit (ICE LOCK)", "the unit is encased, crystals grow in from the border; HELD 2 > 1; it thaws and moves on", "3D + ICE + FLOAT"),
    ("16_decoy_destroyed_revert.gif", "R21", "Decoy destroyed: route reverts", "the decoy leg is erased and the original route is redrawn SOLID; the unit continues", "PENCIL + FLOAT"),
    ("17_unit_destroyed_wipe.gif", "R21", "Unit destroyed (DOWN wipe)", "shards, the ring breaks to a grey X; pencil X + DOWN writes, holds, cloth-wipes", "FLOAT + INLAY + PENCIL"),
    ("18_node_damage.gif", "R21", "Node health drain", "the lit fill drains north > south with each hit; numbers only on hover", "INLAY + FLOAT"),
    ("19_node_disabled_cascade.gif", "R21", "Node disabled + cascade", "last sliver goes; amber dashed frame; 50 % of the excess surges along the links", "INLAY"),
    ("20_node_seized.gif", "R22", "Node seized", "corp hatch + corp glyph, links die; pencil TAKEN writes then wipes", "INLAY + PENCIL"),
    ("21_node_taken.gif", "R23", "Node TAKEN", "grease-pencil TAKEN over the node, holds, wipes like DOWN; burnt socket", "INLAY + PENCIL"),
    ("21_node_taken_v2.gif", "R23", "Node TAKEN (v2)", "normal-weight TAKEN written ABOVE the node, holds, wipes; burnt socket", "INLAY + PENCIL"),
    ("22_reaches_home.gif", "R21", "Threat reaches home", "binary-bit explosion at CORE, CORE's fill drains from the north, HOME 50 > 41", "FLOAT + INLAY + TERMINAL"),
    ("23_wave_cleared.gif", "R21", "Wave cleared", "the wave's pencil routes wipe away, entries stop pulsing, packets flow home", "INLAY + PENCIL + TERMINAL"),
    ("24_raid_report.gif", "R21", "Raid report", "the intercepted corporate after-action report slides in; the Cell's pencil circles the gains, RIP on lost nodes; CELL HOLDS; Heat settled", "PAPER + PENCIL + STICKER"),
    ("25_speed_skip.gif", "R21", "Speed / skip", "live terminal strip; SKIP jumps to the result", "TERMINAL"),
    ("26_home_breached.gif", "R23", "Breached (slowed)", "CORE drains, slow bit explosion, CORE and its links de-power outward; BREACHED writes slowly, underlined", "INLAY + FLOAT + PENCIL + TERMINAL"),
    ("27_node_health.gif", "R21", "Node health combo", "lit part drains north > south; hover shows numbers; 0 = disabled colour + dashed", "INLAY + FLOAT"),
    ("28_bonus_slow.gif", "R23w", "Slow / freeze field (Ghost)", "ground layer under the units: blue dashed rings drift inward (SLOWED -1 STEP); levelled: ice crystals grow inward, the unit is iced over", "INLAY + FLOAT"),
    ("29_bonus_repair.gif", "R23w", "Field repair (Rigger)", "the locked health fill rises south > north; hovered: the number counts up; levelled: the linked CORE refills too", "INLAY + FLOAT"),
    ("30_unit_health.gif", "R22w", "Unit health + status (icons v4)", "corp-colour disc drains top-down under the unit; status pips on the dashed corp ring; heading on hover; the v4 icon carries the same", "INLAY + ICON"),
    ("31_spotlights.gif", "R19/35", "Heat spotlights (EXPOSED)", "a chopper circles the Relay, its spot wobbles on the node (EXPOSED ticks); drones circle with mini spots", "3D + INLAY"),
]


def font(sz):
    for f in ("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def main():
    for f in SUPERSEDED + ["index.md", "index.jpg", "_extra_index.json"]:
        p = os.path.join(GIFS, f)
        if os.path.exists(p) and f not in ("index.md", "index.jpg"):
            os.remove(p)
    md = ["# Round 40 raid gifs: every locked raid interaction, re-run in the ONE city", "",
          "Same unified model as the grid and netrun views (see-through buildings, dimmed lanes, x-ray network), at raid zoom. "
          "Each gif is the LATEST locked version (column `from`: R21/R22/R23 = round 21/22/23 raid UI, w = raid world). "
          "All <= 2 MB, shared multi-frame palette + dither (saturation kept).", "",
          "| gif | from | interaction | feedback | medium | size |", "|---|---|---|---|---|---|"]
    tiles = []
    for name, src, ttl, fb, med in ROWS:
        p = os.path.join(GIFS, name)
        if not os.path.exists(p):
            print("MISSING", name)
            continue
        kb = os.path.getsize(p) // 1024
        md.append("| [%s](%s) | %s | %s | %s | %s | %d KB |" % (name, name, src, ttl, fb, med, kb))
        g = Image.open(p)
        g.seek(int(g.n_frames * 0.6))
        tiles.append((name, g.convert("RGB")))
    v2 = [n for n in ("02_drag_dock_preview_v2.gif", "13_threat_moving_v2.gif", "14_defence_fires_v2.gif") if os.path.exists(os.path.join(GIFS, n))]
    if v2:
        md += ["", "**v2, a lighter city** (`LIGHT40=1`, see `../NOTES.md`): " + ", ".join("[%s](%s)" % (n, n) for n in v2) +
               ". These are representative; every other gif would be regenerated with the same setting."]
    md += ["", "Replaced (not shipped): 02 drag valid + 03 invalid -> 02 dock preview; 05 remove -> 05 remove to hand; "
           "06 move -> 06 swap in one motion; 21 node lost -> 21 node TAKEN.",
           "", "Rebuild: see `../NOTES.md` (Blender `scripts/run40.py`, then `scripts/raidui` builders through the compat layer)."]
    open(os.path.join(GIFS, "index.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    cols, tw, th = 5, 384, 216
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, 60 + rows * (th + 24)), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((12, 14), "ROUND 40  //  RAID GIFS IN THE ONE CITY (latest locked version of each)", font=font(26), fill=(255, 222, 30))
    for k, (name, im) in enumerate(tiles):
        x, y = (k % cols) * tw, 60 + (k // cols) * (th + 24)
        im.thumbnail((tw - 6, th))
        sheet.paste(im, (x + 3 + (tw - 6 - im.width) // 2, y + (th - im.height) // 2))
        d.text((x + 6, y + th + 3), name, font=font(15), fill=(92, 225, 255))
    sheet.save(os.path.join(GIFS, "index.jpg"), quality=86)
    print("index", len(tiles), "gifs")


if __name__ == "__main__":
    main()
