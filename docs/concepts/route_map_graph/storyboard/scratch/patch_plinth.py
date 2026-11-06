import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = r"m44/onecity_build.py"
s = open(p, encoding="utf-8").read()
s = s.replace('''_PAD = float(OC.get("corridor_pad", 30.0))''', '''_PAD = float(OC.get("corridor_pad", 30.0))
_PLINTH_OFF = float(OC.get("plinth_off", 4.2))      # beyond the street's camera-side kerb (half the border street width)
_PLINTH = OC.get("plinth", dict(albedo=0.012, edge=0.12, edge_k=0.18))''', 1)
old = '''    above = M("GREATER_THAN", Z, zc.outputs["Fac"])
    cut = M("MULTIPLY", M("MULTIPLY", side, along), above)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(cut, mx.inputs[0])
    nt.links.new(src, mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])'''
new = '''    above = M("GREATER_THAN", Z, zc.outputs["Fac"])
    cut = M("MULTIPLY", M("MULTIPLY", side, along), above)
    # the plinth rule: what stays of the cut blocks (camera side, beyond the kerb, below z_cut) goes near-black,
    # no trims or emissive roofs, only a faint cool top edge just under the cut plane
    if abs(_NRM[1]) > 0.5:
        beyond = M("LESS_THAN", M("MULTIPLY", M("SUBTRACT", Y, _SA[1]), _NRM[1]), -_PLINTH_OFF)
    else:
        beyond = M("LESS_THAN", M("MULTIPLY", M("SUBTRACT", X, _SA[0]), _NRM[0]), -_PLINTH_OFF)
    plinth = M("MULTIPLY", M("MULTIPLY", beyond, along), M("LESS_THAN", Z, zc.outputs["Fac"]))
    edge = M("GREATER_THAN", Z, M("SUBTRACT", zc.outputs["Fac"], float(_PLINTH["edge"])))
    dk = nt.nodes.new("ShaderNodeBsdfDiffuse")
    a_ = float(_PLINTH["albedo"])
    dk.inputs["Color"].default_value = (a_, a_, a_ * 1.2, 1)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.45, 0.55, 0.75, 1)
    em.inputs["Strength"].default_value = float(_PLINTH["edge_k"])
    mxe = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(edge, mxe.inputs[0])
    nt.links.new(dk.outputs[0], mxe.inputs[1])
    nt.links.new(em.outputs[0], mxe.inputs[2])
    mxp = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(plinth, mxp.inputs[0])
    nt.links.new(src, mxp.inputs[1])
    nt.links.new(mxe.outputs[0], mxp.inputs[2])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(cut, mx.inputs[0])
    nt.links.new(mxp.outputs[0], mx.inputs[1])
    nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])'''
assert old in s
s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
p = "sb_ocjobs.py"
s = open(p, encoding="utf-8").read()
old = 'hero_sign_rule=OC.LAYOUT_RULES["hero_sign_rule"])'
assert old in s
s = s.replace(old, 'hero_sign_rule=OC.LAYOUT_RULES["hero_sign_rule"],\n             plinth_off=OC.LAYOUT_RULES["border_street_width"] / 2 + 0.2)')
open(p, "w", encoding="utf-8").write(s)
print("ok")
