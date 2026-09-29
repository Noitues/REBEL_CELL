"""Probe Blender 5.2: EEVEE motion blur + material transparency props."""
import bpy
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
print("RENDER MB", [a for a in dir(sc.render) if "motion" in a])
print("EEVEE", [a for a in dir(sc.eevee) if any(k in a for k in ("motion","shadow","ray","sample","bloom"))])
m = bpy.data.materials.new("x")
print("MAT", [a for a in dir(m) if any(k in a for k in ("blend","render_method","shadow","transp","backface","thick"))])
l = bpy.data.lights.new("s","SUN")
print("SUN", [a for a in dir(l) if "shadow" in a or "angle" in a or "soft" in a])
