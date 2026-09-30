"""R2A LOW-POLY 3D: still 04, combat. Two faceted spinners face off in front of the night city.

blender -b --factory-startup --python still_combat.py -- <out.png> [scale%]
"""
import os
import sys
import math
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp_lib as L
import city as C
import hud as H
import ui3d as U

PLAYER = [(6, "atk", "4"), (4, "def", "3"), (5, "hack", "HACK"), (3, "crit", "x2"), (6, "atk", "6"),
          (3, "miss", ""), (3, "heal", "+2")]
ENEMY = [(7, "atk", "5"), (5, "def", "4"), (4, "miss", ""), (6, "atk", "3"), (4, "hack", "LOCK"),
         (4, "crit", "x2")]
HAND = [("util", "OVERCLOCK", 1, "Spin +3 ticks", "gear"),
        ("atk", "ICE PICK", 1, "Deal 4 damage", "blade"),
        ("def", "FIREWALL", 2, "Gain 5 shield", "shield"),
        ("hack", "BACKDOOR", 2, "Swap one slice", "chip"),
        ("atk", "SURGE", 3, "Deal 8 damage", "bolt")]


def main():
    a = L.args()
    out = a[0]
    pct = int(a[1]) if len(a) > 1 else 100
    sc = L.reset()
    L.setup_render(sc, samples=64 if pct == 100 else 16)
    sc.render.resolution_percentage = pct
    L.world(sc, "#2a2140", 0.55)
    L.sun("key", (52, 0, 30), "#8a94ff", 1.3, angle=10)
    L.sun("fill", (60, 0, 160), "#ff6fb8", 0.25, angle=30, shadow=False)
    pbf = L.PB()
    pbf.prism(L.ngon(8, 700), -2.45, -2.4, 0, 0)
    pbf.build("floor", [L.mat_flat("floor", "#2c2340", rough=1.0, spec=0.0)], tri=False)
    C.build_city("night")
    C.build_overlay("night")
    C.build_extras("night")
    for i in range(0, C.NX + 1, 2):
        for j in (1, 4, 6):
            L.point(f"st{i}{j}", (C.lx(i), C.ly(j), 2.5), ("#ff5fb0", "#3fe0ff", "#ffb050")[(i + j) % 3], 350,
                    radius=1.5)
    cam = L.camera("cam", (0.0, -70.0, 16.0), (0.0, 6.0, 2.0), lens=35.0, dof=(5.0, 0.9))
    bpy.context.view_layer.update()
    # haze plane: pushes the city back behind the UI
    haze = L.mat_emit("haze", "#2a2140", strength=1.0, alpha=0.5)
    pbh = L.PB()
    pbh.prism(L.rect(400, 400), 0, 0.001, 0, 0)
    hz = pbh.build("haze", [haze], shadow=False, tri=False)
    hz.parent = cam
    hz.location = (0, 0, -24)
    # UI key light (camera-attached, falls off long before the city)
    uisun = L.sun("uisun", (0, 0, 0), "#fff0e0", 4.0, angle=8)
    uisun.parent = cam
    uisun.rotation_euler = (math.radians(-38), math.radians(-32), 0)
    hud = L.HUD(cam, depth=5.0)
    u = hud.unit()
    R = 0.2 * u
    ps = U.spinner("pspin", R, PLAYER, "#39e0ff", rot_deg=14.0)
    hud.adopt(ps, 0.29, 0.6)
    es = U.spinner("espin", R, ENEMY, "#ff3f7a", rot_deg=-38.0)
    hud.adopt(es, 0.71, 0.6)
    hb = U.health_bar("php", 0.5 * u, 0.065 * u, 22 / 30, "#39e0ff", "CELL-9 (YOU)", "22/30")
    hud.adopt(hb, 0.29, 0.35)
    eb = U.health_bar("ehp", 0.5 * u, 0.065 * u, 17 / 30, "#ff3f7a", "WARDEN.ICE", "17/30")
    hud.adopt(eb, 0.71, 0.35)
    # tick counter chip (top centre)
    dark = L.mat_flat("chip_d", "#2c2538")
    edge = L.mat_flat("chip_e", "#f0b44a", emit="#f0b44a", emit_str=1.5)
    lab = L.mat_flat("chip_l", "#f3e6d4", emit="#f3e6d4", emit_str=0.6)
    ch = H.plate("tick", 0.3 * u, 0.09 * u, dark, edge, depth=0.012 * u, bevel=0.018 * u)
    hud.adopt(ch, 0.5, 0.9)
    t = L.text("tick_t", "TICK  12 / 30", (0, 0, 0), 0.05 * u, lab, extrude=0.003 * u)
    hud.adopt(t, 0.5, 0.898, dz=0.012 * u)
    vs = L.text("vs", "VS", (0, 0, 0), 0.09 * u, L.mat_flat("vs_m", "#f0b44a", emit="#f0b44a", emit_str=2.0),
                extrude=0.01 * u)
    hud.adopt(vs, 0.5, 0.6)
    # the hand
    n = len(HAND)
    cw = 0.185 * u
    for i, (kind, title, cost, desc, icon) in enumerate(HAND):
        k = i - (n - 1) / 2
        sel = i == 2
        cd = U.card(f"card{i}", cw, kind, title, cost, desc, icon, glow=3.0 if sel else 0.0)
        uu = 0.5 + k * 0.098
        vv = 0.168 - abs(k) ** 2 * 0.01 + (0.035 if sel else 0.0)
        hud.adopt(cd, uu, vv, dz=0.004 * u * (3 - abs(k)) + (0.03 * u if sel else 0), rot=(0, 0, math.radians(-k * 5)))
    # energy gem (bottom-left) and GO (bottom-right)
    g = H.gem("energy", 0.075 * u, L.mat_flat("en_a", "#39e0ff", emit="#39e0ff", emit_str=2.0),
              L.mat_flat("en_b", "#1f7f99", emit="#39e0ff", emit_str=0.5), n=6, h=0.05 * u)
    hud.adopt(g, 0.09, 0.14)
    et = L.text("en_t", "3", (0, 0, 0), 0.1 * u, L.mat_flat("en_tm", "#fff6e8", emit="#fff6e8", emit_str=1.0), extrude=0.004 * u)
    hud.adopt(et, 0.09, 0.14, dz=0.06 * u)
    el = L.text("en_l", "ENERGY 3/4", (0, 0, 0), 0.036 * u, lab, extrude=0.002 * u)
    hud.adopt(el, 0.09, 0.055)
    gob = U.button("go", 0.3 * u, 0.15 * u, "#f0b44a", "GO", glow=2.0)
    hud.adopt(gob, 0.895, 0.14)
    # light-link the UI sun to the UI only, so the city keeps its night lighting
    ui = bpy.data.collections.new("UI_recv")
    sc.collection.children.link(ui)
    stack = [hud.root]
    while stack:
        o = stack.pop()
        stack.extend(o.children)
        if o.type in ("MESH", "FONT", "CURVE"):
            ui.objects.link(o)
    try:
        if not os.environ.get("R2A_NOLINK"):
            uisun.light_linking.receiver_collection = ui
    except Exception as e:
        print("LIGHTLINK", e)
    L.compositor(sc, bloom=(0.9, 0.5, 7))
    L.render(sc, out)


if __name__ == "__main__":
    main()
