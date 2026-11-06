p = 'D:/rc_art/art-pass/docs/concepts/netrun_cel/v2/scripts/nr_scene_v2.py'
s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b) if n == 0 else s.replace(a, b, 1)

# beam fade stored in Win.r
rep("        ACC['glow'].w += [(0, 0, 0, 0.5)] * 4", "        ACC['glow'].w += [(a0, 0, 0, 1), (a0, 0, 0, 1), (0, 0, 0, 1), (0, 0, 0, 1)]")
rep("    at = N.new('ShaderNodeAttribute'); at.attribute_name = 'Col'; tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.0\n    L.new(at.outputs['Color'], em.inputs['Color']); mx = N.new('ShaderNodeMixShader'); L.new(at.outputs['Alpha'], mx.inputs['Fac'])",
    "    at = N.new('ShaderNodeAttribute'); at.attribute_name = 'Col'; aw = N.new('ShaderNodeAttribute'); aw.attribute_name = 'Win'; sc_ = N.new('ShaderNodeSeparateColor'); L.new(aw.outputs['Color'], sc_.inputs[0])\n    tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.0\n    L.new(at.outputs['Color'], em.inputs['Color']); mx = N.new('ShaderNodeMixShader'); L.new(sc_.outputs['Red'], mx.inputs['Fac'])")
rep("light_beam((bx, by, bz), (R.uniform(-.25, .25), -0.12, 1.0), 120, 1.7, hexc(bc, 3.0), a0=0.5)", "light_beam((bx, by, bz), (R.uniform(-.25, .25), -0.12, 1.0), 120, 1.1, hexc(bc, 3.2), a0=0.42)")
# sky direction from texture coordinates
rep("ge = N.new('ShaderNodeNewGeometry'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(ge.outputs['Incoming'], sp.inputs[0])", "ge = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(ge.outputs['Generated'], sp.inputs[0])")
rep("L.new(ge.outputs['Incoming'], mpn.inputs['Vector'])", "L.new(ge.outputs['Generated'], mpn.inputs['Vector'])")
rep("mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.9", "mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.8")
rep("'f3': ((-6.0, -78.0, 22.0), (0.0, 6.0, 31.0), 24)", "'f3': ((-6.0, -68.0, 22.0), (0.0, 6.0, 17.0), 25)")
rep("'f3': (-6.0, -78.0, 22.0)", "'f3': (-6.0, -68.0, 22.0)")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
