"""R2A LOW-POLY 3D: stills 01-03, the city diorama by day, by night, under high suspicion.

blender -b --factory-startup --python still_city.py -- <day|night|alert> <out.png> [scale%]
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

MODES = {
    "day": dict(world="#d9c8b4", wstr=0.85, floor="#d6c3ad", sun=("#ffe4c4", 3.6, (48, 0, -38)),
                fill=("#b9c7e6", 0.6), bloom=(1.4, 0.25, 5), exposure=0.0, pips=1, pipcol="#39e0ff"),
    "night": dict(world="#2a2140", wstr=0.55, floor="#2c2340", sun=("#8a94ff", 1.3, (52, 0, 30)),
                  fill=("#ff6fb8", 0.25), bloom=(0.9, 0.55, 7), exposure=0.0, pips=2, pipcol="#39e0ff"),
    "alert": dict(world="#3a1626", wstr=0.55, floor="#35162a", sun=("#ff8a9a", 1.2, (52, 0, 30)),
                  fill=("#ff2040", 0.35), bloom=(0.9, 0.7, 7), exposure=0.0, pips=5, pipcol="#ff3f5a"),
}

CAM_LOC = (0.0, -45.0, 50.0)
CAM_TGT = (0.0, 3.5, 0.0)
CAM_LENS = 31.0


def main():
    a = L.args()
    mode = a[0]
    out = a[1]
    pct = int(a[2]) if len(a) > 2 else 100
    cfg = MODES[mode]
    sc = L.reset()
    L.setup_render(sc, samples=64 if pct == 100 else 16)
    sc.render.resolution_percentage = pct
    L.world(sc, cfg["world"], cfg["wstr"])
    L.sun("key", cfg["sun"][2], cfg["sun"][0], cfg["sun"][1], angle=10)
    L.sun("fill", (60, 0, 160), cfg["fill"][0], cfg["fill"][1], angle=30, shadow=False)
    # the floor the diorama sits on, soft shadow underneath
    pbf = L.PB()
    pbf.prism(L.ngon(8, 160), -2.45, -2.4, 0, 0)
    pbf.build("floor", [L.mat_flat("floor", cfg["floor"], rough=1.0, spec=0.0)], tri=False)

    C.build_city(mode)
    C.build_overlay(mode)
    C.build_extras(mode)
    cam = L.camera("cam", CAM_LOC, CAM_TGT, lens=CAM_LENS)
    bpy.context.view_layer.update()
    _here_tag(mode, cam)
    _hud(mode, cam, cfg)
    if mode != "day":
        _night_lights(mode)
    L.compositor(sc, bloom=cfg["bloom"])
    L.render(sc, out)


def _here_tag(mode, cam):
    """A floating faceted tag above the 'you are here' pin, facing the camera."""
    p = C.node_world(C.HERE) + Vector((0, 0, 7.8))
    face = L.mat_flat("tag_face", "#2b2436", emit="#2b2436", emit_str=0.0)
    edge = L.mat_flat("tag_edge", "#ffc34d", emit="#ffc34d", emit_str=1.5 if mode == "day" else 5.0)
    txt = L.mat_flat("tag_txt", "#ffe2a0", emit="#ffe2a0", emit_str=1.2 if mode == "day" else 5.0)
    pl = H.plate("tag", 7.4, 1.9, face, edge, depth=0.16, bevel=0.3)
    pl.location = p
    pl.rotation_euler = cam.rotation_euler
    t = L.text("tag_t", "YOU ARE HERE", (0, -0.02, 0.1), 1.45, txt, extrude=0.03, parent=pl, shadow=False)
    t.location = (0, 0, 0.1)


def _hud(mode, cam, cfg):
    hud = L.HUD(cam, depth=5.0)
    u = hud.unit()  # world units per screen height
    dark = L.mat_flat("hud_dark", "#2b2436", emit="#2b2436", emit_str=0.25)
    edge = L.mat_flat("hud_edge", "#e7d6c2", emit="#e7d6c2", emit_str=0.25 if mode == "day" else 0.5)
    lab = L.mat_flat("hud_lab", "#efe2cf", emit="#efe2cf", emit_str=0.6 if mode == "day" else 1.6)
    hot = L.mat_flat("hud_hot", cfg["pipcol"], emit=cfg["pipcol"], emit_str=2.0 if mode == "day" else 6.0)
    off = L.mat_flat("hud_off", "#4a4258")
    side = L.mat_flat("hud_side", "#1c1826")
    pl = H.plate("hud_plate", 0.52 * u, 0.15 * u, dark, edge, depth=0.012 * u, bevel=0.012 * u)
    hud.adopt(pl, 0.165, 0.9)
    t = L.text("hud_t", "SUSPICION", (0, 0, 0), 0.06 * u, lab, extrude=0.002 * u, align="LEFT")
    hud.adopt(t, 0.033, 0.918, dz=0.01 * u)
    t2 = L.text("hud_t2", "DISTRICT 07  //  LOWER GRID", (0, 0, 0), 0.03 * u, lab, extrude=0.001 * u,
                align="LEFT", font=L.FONT_BODY)
    hud.adopt(t2, 0.033, 0.868, dz=0.01 * u)
    for k in range(5):
        on = k < cfg["pips"]
        pip = H.hexpip(f"pip{k}", 0.022 * u, hot if on else off, side, depth=0.008 * u)
        hud.adopt(pip, 0.19 + k * 0.026, 0.918, dz=0.01 * u)
    if mode == "alert":
        w = L.mat_flat("hud_warn", "#ff3f5a", emit="#ff3f5a", emit_str=6.0)
        wf = L.mat_flat("hud_warnf", "#3a1020", emit="#3a1020", emit_str=0.2)
        pw = H.plate("warn", 0.62 * u, 0.09 * u, wf, w, depth=0.01 * u, bevel=0.012 * u)
        hud.adopt(pw, 0.5, 0.92)
        tw = L.text("warn_t", "LOCKDOWN  -  CITY SWEEP IN PROGRESS", (0, 0, 0), 0.05 * u, w,
                    extrude=0.002 * u)
        hud.adopt(tw, 0.5, 0.918, dz=0.012 * u)


def _night_lights(mode):
    """A few warm/neon pools so the facets pick up coloured light at night (shadows off)."""
    cols = ["#ff5fb0", "#3fe0ff", "#ffb050"] if mode == "night" else ["#ff3050", "#ff6040", "#ffb050"]
    k = 0
    for i in range(0, C.NX + 1, 2):
        for j in (1, 4, 6):
            L.point(f"street{k}", (C.lx(i), C.ly(j), 2.5), cols[k % 3], 350, radius=1.5)
            k += 1
    here = C.node_world(C.HERE)
    L.point("here_glow", (here.x, here.y, 2.0), "#ffc34d", 600, radius=1.0)


if __name__ == "__main__":
    main()
