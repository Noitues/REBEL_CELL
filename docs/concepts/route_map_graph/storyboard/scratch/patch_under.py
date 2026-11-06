import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = "m44/onecity_cycles.py"
s = open(p, encoding="utf-8").read()
old = '''nt.links.new(add.outputs[0], out.inputs["Volume"])
me = bpy.data.meshes.new("oc_fog")'''
new = '''# r3 underlight: the strata glow faintly from below in the palette by height (the city's light caught in the layers;
# r3 underlight ramp + underlight_k), so they read against the night sky without lifting the whole frame
ramp = nt.nodes.new("ShaderNodeValToRGB")
_el = ramp.color_ramp.elements
_el[0].position, _el[0].color = 0.0, (1.0, 0.16, 0.6, 1)
_el[1].position, _el[1].color = 1.0, (0.62, 0.38, 1.0, 1)
for _p, _c in ((0.3, (0.16, 0.8, 1.0, 1)), (0.55, (1.0, 0.16, 0.6, 1)), (0.8, (0.16, 0.8, 1.0, 1))):
    _e = _el.new(_p)
    _e.color = _c
nt.links.new(_m("DIVIDE", zw, 2.2 * HF), ramp.inputs["Fac"])
emv = nt.nodes.new("ShaderNodeEmission")
nt.links.new(ramp.outputs["Color"], emv.inputs["Color"])
nt.links.new(_m("MULTIPLY", dens, float(LKA.get("underlight_k", 0.06))), emv.inputs["Strength"])
add2 = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(add.outputs[0], add2.inputs[0])
nt.links.new(emv.outputs[0], add2.inputs[1])
nt.links.new(add2.outputs[0], out.inputs["Volume"])
me = bpy.data.meshes.new("oc_fog")'''
assert old in s
s = s.replace(old, new)
old = "wisp = _m(\"SUBTRACT\", 1.0, _smooth(_m(\"ABSOLUTE\", _m(\"SUBTRACT\", zw, 1.08 * HF), 0), 0.0, 0.07 * HF))"
assert old in s
s = s.replace(old, old.replace("0.07 * HF", "0.12 * HF"))
open(p, "w", encoding="utf-8").write(s)
p = "sb_ocjobs.py"
s = open(p, encoding="utf-8").read()
s = s.replace("wisp_k=0.7, fog_front=7.0, fog_peak=0.02,", "wisp_k=1.2, fog_front=7.0, fog_peak=0.03, underlight_k=0.06,")
assert "underlight_k=0.06" in s
open(p, "w", encoding="utf-8").write(s)
print("ok")
