"""Round 36 -> node_backdrop.png + node_backdrop.gif: the dressed room as a node's backdrop.

From the HQ compound (overhead), the operative enters a Terminal node. The camera cuts to that node's close-up: one
dressed container room (r32_scene.py tower, view 'room': floor 2, slot 1, a Terminal with its desk and screen wall) and
that close-up IS the backdrop behind the node's screen (here the event ev_mer_manifest_glitch, real content).
For a fight node the same close-up sits behind the combat wheels (the round 30 'zoomed-in target' rule, per node).

python backdrop36.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL
import hq_views as HQ

EV_TITLE = "Manifest Glitch"
EV_TEXT = ["A shipping manifest lists your safehouse", "as a Meridian warehouse. Somebody made", "a mistake."]
CHOICES = [("Lean into it", [("schem", "+2", True), ("heat", "+2", False)]), ("Correct it quietly", [("heat", "-1", True)]),
           ("Walk on", [("none", "NO CHANGE", True)])]


def event_screen(room, alpha=1.0):
    img = room.convert("RGBA")
    img = L.darken_rect(img, (1040, 120, 1900, 1040), a=120, blur=40)
    c = L.CRT(780, 300, (255, 160, 60), "TERMINAL", tag="MERIDIAN YARD // 1-3", seed=81)
    c.text((22, 56), EV_TITLE.upper(), 30, (255, 220, 170), fnt=L.f_num(38))
    for i, ln in enumerate(EV_TEXT):
        c.text((22, 120 + i * 32), ln, 21, (235, 225, 210))
    img = L.paste(img, c.finish(), 1100, 150)
    y = 500
    for i, (lab, chips) in enumerate(CHOICES):
        sd = L.sticker_word([lab.upper()], 34, fills=[(236, 234, 244)], seed=90 + i, extrude=4)
        img = L.place_sticker(img, sd, 1290, y + 30, angle=(-1.5, 1.0, -0.5)[i])
        row = L.outcome_row(chips, size=20)
        img.alpha_composite(row, (1480, y + 10))
        y += 120
    img = L.place_sticker(img, L.sticker_word(["EVENT"], 60, fills=["yellow"], seed=80), 1240, 90, angle=-3)
    return img


def inset(img, comp, node_xy, box=(40, 40, 600, 355)):
    x0, y0, x1, y1 = box
    th = comp.resize((x1 - x0, y1 - y0), Image.LANCZOS)
    k = (x1 - x0) / 1920
    img = L.drop_shadow(img, th, x0, y0, blur=12, off=(8, 10), op=0.6)
    d = ImageDraw.Draw(img)
    d.rectangle(box, outline=U.CYAN + (255,), width=3)
    nx, ny = x0 + node_xy[0] * k, y0 + node_xy[1] * k
    p = L.pen(L.GP_YELLOW, seed=83)
    p.circle(nx, ny - 10, 26, 20, width=6)
    img = L.ink(img, p)
    img = U.chip(img, (x0 + 120, y1 + 22), "THE COMPOUND  //  NODE 1-3", U.CYAN, 14)
    return img


def main():
    import json
    A = json.load(open(os.path.join(U.BL, "compound_f00_anchors.json")))
    comp = HQ.compound(0, walked=("start",), current="start", ui=False)
    room = Image.open(os.path.join(U.FIN, "tower_room.png")).convert("RGBA")
    node = A["nodes"]["1_3"]["c"]
    ev = event_screen(room)
    final = inset(ev, comp, node)
    final = L.bloom(final, 0.12, 0.82, 8)
    L.save(final, "node_backdrop.png")
    # gif: compound -> zoom on the node -> the room -> the event builds on it
    frames, durs = [comp.convert("RGB")], [900]
    p = L.pen(L.GP_YELLOW, seed=84)
    p.circle(node[0], node[1] - 26, 60, 44, width=9)
    frames.append(L.ink(comp.copy(), p).convert("RGB"))
    durs.append(600)
    for z in (1.6, 2.6, 4.2):
        w, h = 1920 / z, 1080 / z
        cx = min(max(node[0], w / 2), 1920 - w / 2)
        cy = min(max(node[1], h / 2), 1080 - h / 2)
        fr = comp.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((1920, 1080), Image.LANCZOS)
        frames.append(fr.convert("RGB"))
        durs.append(110)
    flash = Image.new("RGB", (1920, 1080), (240, 250, 255))
    frames.append(Image.blend(flash, room.convert("RGB"), 0.5))
    durs.append(80)
    frames.append(room.convert("RGB"))
    durs.append(700)
    frames.append(Image.blend(room.convert("RGB"), ev.convert("RGB"), 0.5))
    durs.append(120)
    frames.append(ev.convert("RGB"))
    durs.append(2200)
    out = os.path.join(L.OUT, "node_backdrop.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=(800, 450)))


if __name__ == "__main__":
    main()
