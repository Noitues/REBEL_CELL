"""Render the Cell's voice layer (marker, drips, stickers, tape) with Grease Pencil v3.

blender -b --factory-startup --python gp_overlay.py -- <spec.json> [<spec.json> ...]
Each spec: {"out": png, "res": [w, h], "items": [...]} in PIXEL coordinates (y down).
Item types: marker (strokes with pressure), drip, poly (filled, optional stroke), line.
The layer renders flat (no scene lights) on a transparent film and is composited on top in post.
"""
import bpy, sys, os, json, math

argv = sys.argv[sys.argv.index("--") + 1:]


def hexcol(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), a)


def setup(w, h):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.eevee.taa_render_samples = 16
    try:
        sc.view_settings.view_transform = "Standard"
    except TypeError:
        pass
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = w / 100.0
    cam = bpy.data.objects.new("cam", cd)
    cam.location = (0, -10, 0)
    cam.rotation_euler = (math.pi / 2, 0, 0)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return sc


MATS = {}


def gp_mat(gp, stroke=None, fill=None):
    key = (stroke, fill)
    if key not in MATS:
        m = bpy.data.materials.new(f"gp_{len(MATS)}")
        bpy.data.materials.create_gpencil_data(m)
        g = m.grease_pencil
        if stroke:
            g.show_stroke = True
            g.color = hexcol(stroke[0], stroke[1])
        else:
            g.show_stroke = False
        if fill:
            g.show_fill = True
            g.fill_color = hexcol(fill[0], fill[1])
        else:
            g.show_fill = False
        MATS[key] = m
    m = MATS[key]
    names = [x.name for x in gp.materials]
    if m.name not in names:
        gp.materials.append(m)
        names.append(m.name)
    return names.index(m.name)


def render_spec(spec):
    MATS.clear()
    w, h = spec["res"]
    sc = setup(w, h)
    gp = bpy.data.grease_pencils.new("voice")
    ob = bpy.data.objects.new("voice", gp)
    sc.collection.objects.link(ob)
    layer = gp.layers.new("voice")
    layer.use_lights = False
    frame = layer.frames.new(sc.frame_current)
    dr = frame.drawing

    def to3(px, py):
        return ((px - w / 2) / 100.0, 0.0, (h / 2 - py) / 100.0)

    def add_stroke(pts, radii, mat_idx, cyclic=False, opac=None):
        dr.add_strokes([len(pts)])
        s = dr.strokes[len(dr.strokes) - 1]
        s.material_index = mat_idx
        s.cyclic = cyclic
        s.fill_opacity = 1.0
        for k, (p, r) in enumerate(zip(pts, radii)):
            pt = s.points[k]
            pt.position = to3(*p)
            pt.radius = r / 100.0
            pt.opacity = 1.0 if opac is None else opac[k]
        return s

    for it in spec["items"]:
        t = it["type"]
        if t == "marker":
            mi = gp_mat(gp, stroke=(it["color"], it.get("alpha", 1.0)))
            wpx = it["width"]
            for st in it["strokes"]:
                if len(st) < 2:
                    continue
                add_stroke([(p[0], p[1]) for p in st], [wpx * 0.5 * p[2] for p in st], mi)
        elif t == "drip":
            mi = gp_mat(gp, stroke=(it["color"], it.get("alpha", 1.0)))
            x, y, L, wpx = it["x"], it["y"], it["len"], it["width"]
            n = max(3, int(L / 3))
            pts, rad = [], []
            for k in range(n + 1):
                f = k / n
                wob = math.sin(f * 5 + x) * 0.8 + (math.sin(f * 17 + x * 0.3) * 2.5 + math.sin(f * 41 + x) * 1.2 if it.get("streak") else 0)
                pts.append((x + wob, y + L * f))
                # joint at the letter, thin run, fat bulb at the tip
                r = wpx * (0.5 - 0.2 * min(1, f * 2.5) + 0.2 * max(0, (f - 0.8) / 0.2) ** 1.2)
                if it.get("streak"):
                    r *= 0.8
                rad.append(r)
            # round the bulb
            pts.append((x + 0.3, y + L + wpx * 0.25))
            rad.append(wpx * 0.4)
            add_stroke(pts, rad, mi)
        elif t == "poly":
            mi = gp_mat(gp, stroke=(it["stroke"], it.get("stroke_alpha", 1.0)) if it.get("stroke") else None,
                        fill=(it["fill"], it.get("alpha", 1.0)) if it.get("fill") else None)
            r = it.get("stroke_w", 0.0) * 0.5
            s = add_stroke(it["pts"], [max(r, 0.01)] * len(it["pts"]), mi, cyclic=True)
            s.fill_id = len(dr.strokes)  # Blender 5.x: fill_id 0 means "no fill"
        elif t == "line":
            mi = gp_mat(gp, stroke=(it["color"], it.get("alpha", 1.0)))
            add_stroke(it["pts"], [it["width"] * 0.5] * len(it["pts"]), mi)
    dr.tag_positions_changed()
    sc.render.filepath = spec["out"]
    bpy.ops.render.render(write_still=True)
    print("GP DONE", spec["out"], len(dr.strokes))


for path in argv:
    with open(path) as f:
        render_spec(json.load(f))
