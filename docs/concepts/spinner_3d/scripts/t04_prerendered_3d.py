"""04 pre-rendered 3D: a true 3D wheel (machined bezel, recessed emissive slice inlays,
needle with counterweight, hub screen), lit and rendered the way it would be baked to
sprites. Also renders the separate transparent sprite layers a bake would produce."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

TILT = 18.0
L.reset()
sc = L.setup((1200, 1200), samples=48)
cam = L.camera(3.3, -0.15, tilt_deg=TILT)
bd = L.backdrop(cam)
parts = L.spinner_3d("op")
L.studio_lights()
L.render(os.path.join(L.REN, "04_prerendered_3d.png"))

# sprite bake: each part alone on transparent film
sc.render.film_transparent = True
sc.render.image_settings.color_mode = "RGBA"
sc.render.resolution_x = sc.render.resolution_y = 520
sc.compositing_node_group = None
bd.hide_render = True
groups = {
    "bezel": ["op_bezel"],
    "wheel": ["op_inlay"] + [f"op_div{k}" for k in range(10)],
    "hub": ["op_hub", "op_screen"],
    "needle": ["arm", "stripe", "tail", "cweight", "cap", "post"],
}
allmesh = [o for o in L.bpy.data.objects if o.type == "MESH" and o.name != "backdrop"]
for g, names in groups.items():
    for o in allmesh:
        o.hide_render = o.name not in names
    L.render(os.path.join(L.REN, f"04_sprite_{g}.png"))
