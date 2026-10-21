"""Street panel hook (netrun street, decision camera): runs inside r2_scene.py's exec of r2_cycles.py, before the frame loop.

Paints the frontage materials (SURF, PANELM, LITA) with the graffiti atlases at street scale, and adds soft neon haze
lights behind the frontage so the deep fog glows pink / cyan / violet. The fog colour itself comes from the job's
look.scatter (graf_run_street.py sets it).
"""
import json
import os

import graf_look as GL

CFG = json.loads(os.environ.get("GRAF_CFG", "{}"))


def patch_cycles(src):
    key = "for fr in OCJ[\"frames\"]:\n"
    assert key in src
    src = src.replace(key, "import graf_street as _GS\n_GS.apply_street(globals())\n" + key, 1)
    if os.environ.get("GRAF_CPU"):
        k2 = 'cy.device = "GPU"'
        assert k2 in src
        src = src.replace(k2, 'cy.device = "CPU"', 1)
    return src


def sign_mat(k):
    import bpy
    m = bpy.data.materials.new("graf_signs")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = GL._img("signs.png", "sRGB")
    uv = nt.nodes.new("ShaderNodeUVMap")
    nt.links.new(uv.outputs[0], t.inputs["Vector"])
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Strength"].default_value = k
    nt.links.new(t.outputs["Color"], e.inputs["Color"])
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


def add_signs(g, cfg):
    """Tokyo vertical shop signs on the frontage: one lit box every few BU along each front face, hung off the wall toward
    the camera (seeded per face). Each box's front face maps to one cell of signs.png (8 x 2 cells)."""
    import random

    import bmesh
    import bpy
    rng = random.Random(cfg.get("seed", 20261021) + 3)
    faces = list(g["PLAN"].get("front_faces", []))
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    n = 0
    for ff in sorted(faces, key=lambda f: (f["u0"], f.get("uid", ""))):
        u0, u1, fy, top = float(ff["u0"]), float(ff["u1"]), float(ff["face"]), float(ff.get("top", 12.0))
        out = float(ff.get("out", -1.0))
        # Tokyo vertical signs hang at the building corners (and keep clear of the centred shop signs)
        xs = [u0 + 0.75, u1 - 0.75] if u1 - u0 > 4.0 else [u0 + 0.75]
        for x in xs:
            if rng.random() < cfg.get("sign_p", 0.8):
                w = rng.uniform(0.8, 1.05)
                h = min(w * rng.uniform(3.6, 4.2), top - 4.5) if top > 8.0 else 0   # the sign cells are 1:4
                if h > 2.0:
                    z0 = rng.uniform(3.4, max(3.5, top - h - 1.0))
                    dpt, off = 0.25, cfg.get("sign_off", 0.45)
                    y0 = fy + out * off
                    y1 = y0 + out * dpt
                    cell = rng.randrange(16)
                    cu, cv = (cell % 8) / 8.0, (cell // 8) / 2.0
                    v = [bm.verts.new(p) for p in ((x - w / 2, y1, z0), (x + w / 2, y1, z0), (x + w / 2, y1, z0 + h), (x - w / 2, y1, z0 + h),
                                                   (x - w / 2, y0, z0), (x + w / 2, y0, z0), (x + w / 2, y0, z0 + h), (x - w / 2, y0, z0 + h))]
                    quads = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0)]
                    for qi, q in enumerate(quads):
                        f_ = bm.faces.new([v[i] for i in q])
                        uvs = [(cu + 0.004, 1 - (cv + 0.5) + 0.004), (cu + 0.121, 1 - (cv + 0.5) + 0.004), (cu + 0.121, 1 - cv - 0.004), (cu + 0.004, 1 - cv - 0.004)] \
                            if qi in (0, 1) else [(cu + 0.01, 1 - cv - 0.01)] * 4     # front + back show the sign; sides take its edge colour
                        for lp, uv_ in zip(f_.loops, uvs):
                            lp[uvl].uv = uv_
                    n += 1
    me = bpy.data.meshes.new("graf_signs")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(sign_mat(cfg.get("sign_k", 2.2)))
    ob = bpy.data.objects.new("graf_signs", me)
    ob.pass_index = 7
    g["scene"].collection.objects.link(ob)
    return n


def apply_street(g):
    if CFG.get("off"):
        return
    cfg = dict(dict(scale=24.0, heaven_scale=46.0, cell=12.0, heaven_cell=16.0, heaven_p=0.5, street_z=(7.0, 14.0), up_k=0.6,
                    glow_k=0.9, z_floor=0.05, haze_w=3.0e4, haze_r=20.0), **CFG)
    import bpy
    n = 0
    for k in ("SURF", "PANELM", "LITA"):
        n += GL.paint(g.get(k), cfg)
    # every other facade material the frontage kits use (not ground, emitters, glass, fog, signs)
    use = {}
    for o in g["scene"].objects:
        if o.type == "MESH" and not o.hide_render:
            for m in o.data.materials:
                if m is not None:
                    use.setdefault(m.name, []).append(o.name)
    skip = tuple(cfg.get("skip_mats", ("oc_wet", "oc_neon", "oc_win", "oc_panel", "oc_glane", "oc_lane", "oc_fog", "oc_haze", "graf_",
                                       "oc_ground", "r2_haze", "r2_glass")))
    extra = []
    for name in sorted(use):
        m = bpy.data.materials[name]
        if name.startswith(skip) or m.get("_graf_done") or not m.use_nodes:
            continue
        if any(nd.type == "BSDF_PRINCIPLED" for nd in m.node_tree.nodes):
            extra.append(name)
            n += GL.paint(m, cfg)
    print("[graf] mats", {k: len(v) for k, v in sorted(use.items())}, "extra painted", extra, flush=True)
    pts = [tuple(p) for p in cfg.get("haze_pts", [(x, y, z) for (x, y, z) in
                                                   ((105, 45, 18), (130, 70, 26), (155, 50, 14), (180, 80, 30), (205, 55, 20), (228, 75, 24))])]
    hl = GL.haze_lights(None, cfg, pts) if cfg.get("haze_w", 4.0e5) > 0 else []
    ns = add_signs(g, cfg) if cfg.get("signs", True) else 0
    print("[graf] street paint bsdf", n, "haze lights", len(hl), "signs", ns, "faces", len(g["PLAN"].get("front_faces", [])),
          [(round(f["u0"]), round(f["u1"]), round(f["face"], 1), round(f.get("top", 0)), f.get("out")) for f in g["PLAN"].get("front_faces", [])][:12], flush=True)
