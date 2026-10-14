"""Build street39.py from the locked unified39.py (copied kit): the same city, plus a PERSPECTIVE camera spec
(street level, family S). python make_street39.py   (idempotent; never edits unified39.py)
Spec keys added: persp = {loc: [x, y, z], look: [x, y, z], lens: mm}; passes = "lite" renders beauty, glow, normal, pos
only (enough for the street finish + the facade bloom)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "unified39.py"), encoding="utf-8").read()
old = '''def shoot(spec):
    c = LY36.cam(spec["t"], spec["ortho"])
    r_, u_, f_ = LY36.basis(c)
    t = c["target"]
    cam.location = (t[0] - f_[0] * c["dist"], t[1] - f_[1] * c["dist"], t[2] - f_[2] * c["dist"])
    cam.rotation_euler = Vector(f_).to_track_quat("-Z", "Y").to_euler()
    cam_data.ortho_scale = c["ortho"]'''
new = '''def shoot(spec):
    if "persp" in spec:
        pp = spec["persp"]
        cam_data.type = "PERSP"
        cam_data.lens = pp["lens"]
        cam_data.sensor_fit = "HORIZONTAL"
        cam_data.sensor_width = 36.0
        cam_data.clip_start = 0.2
        cam.location = tuple(pp["loc"])
        f_ = (Vector(pp["look"]) - Vector(pp["loc"])).normalized()
        cam.rotation_euler = f_.to_track_quat("-Z", "Y").to_euler()
        c = dict(persp=pp, target=pp["look"], dist=0.0, ortho=0.0)
    else:
        cam_data.type = "ORTHO"
        c = LY36.cam(spec["t"], spec["ortho"])
        r_, u_, f_ = LY36.basis(c)
        t = c["target"]
        cam.location = (t[0] - f_[0] * c["dist"], t[1] - f_[1] * c["dist"], t[2] - f_[2] * c["dist"])
        cam.rotation_euler = Vector(f_).to_track_quat("-Z", "Y").to_euler()
        cam_data.ortho_scale = c["ortho"]'''
assert old in s
s = s.replace(old, new)
# lite passes: stop after pos for street frames (no ghost/ground passes)
old2 = '''    arr = np.round(load_exr(P("pos_hi.exr"))) * 16.0 + load_exr(P("pos_lo.exr")) - 4000.0
    np.save(P("pos.npy"), arr.astype(np.float32))'''
new2 = old2 + '''
    if spec.get("passes") == "lite":
        bpy.context.view_layer.material_override = None
        scene.render.image_settings.file_format = "PNG"
        json.dump(dict(cam=c, res=spec["res"]), open(P("scene.json"), "w"), indent=1)
        print("SHOT", spec["tag"], flush=True)
        return'''
assert old2 in s
s = s.replace(old2, new2)
open(os.path.join(HERE, "street39.py"), "w", encoding="utf-8").write(s)
print("street39.py written")
