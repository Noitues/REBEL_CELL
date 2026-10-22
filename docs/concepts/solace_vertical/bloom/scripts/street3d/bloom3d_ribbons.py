"""Solace THE BLOOM v2, A Necrosis street decals: pink vein ribbons (thin emissive quad strips) that crawl ahead of the front on the
walk / road and climb the facade, forking now and then. exec'd by r2_cycles.py (BLOOM_CFG env, cfg["ribbons"]).
Keep-outs (solace.md occlusion rule): never inside a route room box or a link box (cfg["boxes"], margin already included); the
ribbons live on the ground band and the lowest facade metres only, so they never touch the cutaway openings.
Deterministic: random.Random(seed) per ribbon id; no render-time randomness.
"""
import json
import math
import os
import random

import bmesh
import bpy


def _inside(boxes, x, y, z, m=0.0):
    for b in boxes:
        if b[0] - m < x < b[1] + m and b[2] - m < y < b[3] + m and b[4] - m < z < b[5] + m:
            return True
    return False


def make(cfg):
    R = cfg.get("ribbons")
    if not R:
        return 0
    boxes = cfg["boxes"]
    rnd = random.Random(int(R.get("seed", 11)))
    fx = float(cfg["front_x"])
    mat = bpy.data.materials.new("bl_ribbon")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple(cfg["pink"]) + (1,)
    em.inputs["Strength"].default_value = float(R["strength"])
    nt.links.new(em.outputs[0], out.inputs[0])
    mat["bl_on"] = True
    bm = bmesh.new()
    w0 = float(R["width"])
    n_made = 0

    def walk(p, d, length, depth, plane):
        nonlocal n_made
        pts = [p]
        step = 0.6
        ang = d
        for _ in range(int(length / step)):
            ang += rnd.gauss(0, 0.22)
            ang *= 0.93
            if plane == "ground":
                q = (pts[-1][0] - math.cos(ang) * step, pts[-1][1] + math.sin(ang) * step, pts[-1][2])
            else:                                    # facade: x along the street (toward -x), z up
                q = (pts[-1][0] - math.cos(ang) * step * 0.7, pts[-1][1], pts[-1][2] + abs(math.sin(ang)) * step * 0.9)
            if _inside(boxes, q[0], q[1], q[2], 0.0) or q[2] > float(R["facade_h"]):
                break
            pts.append(q)
            if depth < 2 and rnd.random() < float(R["fork"]):
                walk(q, ang + rnd.choice((-1, 1)) * 0.7, length * 0.5, depth + 1, plane)
        if len(pts) < 3:
            return
        w = w0 * (1.0 if depth == 0 else 0.65)
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            t = 1.0 - i / len(pts)                  # taper toward the tip
            if plane == "ground":
                nx, ny = -(b[1] - a[1]), (b[0] - a[0])
                L_ = math.hypot(nx, ny) or 1.0
                nx, ny = nx / L_ * w * t * 0.5, ny / L_ * w * t * 0.5
                v = [bm.verts.new((a[0] - nx, a[1] - ny, a[2])), bm.verts.new((a[0] + nx, a[1] + ny, a[2])),
                     bm.verts.new((b[0] + nx, b[1] + ny, b[2])), bm.verts.new((b[0] - nx, b[1] - ny, b[2]))]
            else:
                nz = w * t * 0.5
                v = [bm.verts.new((a[0], a[1], a[2] - nz)), bm.verts.new((a[0], a[1], a[2] + nz)),
                     bm.verts.new((b[0], b[1], b[2] + nz)), bm.verts.new((b[0], b[1], b[2] - nz))]
            try:
                bm.faces.new(v)
            except ValueError:
                pass
        n_made += 1

    for i in range(int(R["n_ground"])):                 # on the walk / road, from just behind the front out ahead of it
        x0 = fx + rnd.uniform(-1.0, 6.0)
        y0 = rnd.uniform(float(R["y0"]), float(R["y1"]))
        walk((x0, y0, float(R["z_ground"])), rnd.gauss(0, 0.25), rnd.uniform(6.0, float(R["reach"])), 0, "ground")
    for i in range(int(R["n_facade"])):                 # up the facade face, rooted at the kerb
        x0 = fx + rnd.uniform(-2.0, 8.0)
        walk((x0, float(R["facade_y"]), 0.3), rnd.gauss(0.5, 0.3), rnd.uniform(2.0, float(R["facade_h"])), 0, "facade")
    me = bpy.data.meshes.new("bl_ribbons")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("bl_ribbons", me)
    me.materials.append(mat)
    bpy.context.scene.collection.objects.link(ob)
    ob.pass_index = 2
    return n_made


if os.environ.get("BLOOM_CFG"):
    _cfg = json.load(open(os.environ["BLOOM_CFG"]))
    print("BLOOM ribbons", make(_cfg), flush=True)
