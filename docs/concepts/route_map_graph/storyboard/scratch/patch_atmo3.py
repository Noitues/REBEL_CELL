import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
p = "m44/onecity_cycles.py"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)


# beams: a wide soft cone and a narrow core at <= 30 % (art director r3 note), both fully soft-edged
rep('''    for part, ang, e in (("soft", float(LKA.get("beam_cone", 6.0)), 1.5),):     # v3-r2b: one soft cone, no core line''',
    '''    for part, ang, e in (("soft", float(LKA.get("beam_cone", 16.0)), 1.0),
                         ("core", float(LKA.get("beam_core", 3.0)), float(LKA.get("beam_core_k", 0.3)))):   # v3-r2c''')

# fog: the low ground bank over the foreground slabs and mid-ground banks between the rows behind the frontage
rep('''dens = _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", body, hf), floor_), where), float(LKA.get("fog_peak", 0.021)) * S)
''', '''dens = _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", body, hf), floor_), where), float(LKA.get("fog_peak", 0.021)) * S)
# v3-r2c (art director): visible banks.
#  ground bank  a low layer (thick to gb_top x 0.2, gone at gb_top) over the cut slabs on the camera side, from the
#               near kerb outward; broken by a low-frequency noise so it reads as banks, never a flat sheet
#  mid banks    low banks between the building rows behind the frontage (0.05 .. 0.8 H), banks-octave noise
_kerb = float(OCJ.get("plinth_off", 4.2))
gb_side = _smooth(_m("MULTIPLY", _fd, -1.0), _kerb + 0.5, _kerb + 4.0)
_gt = float(LKA.get("gb_top", 2.2))
gb_z = _m("SUBTRACT", 1.0, _smooth(Z, 0.2 * _gt, _gt))
gb_n = _smooth(_noise((0.018 * S, 0.03 * S, 0.25 * S), 2.0, 21.3), 0.35, 0.68)
gb = _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", gb_side, gb_z), _m("ADD", 0.25, _m("MULTIPLY", gb_n, 0.75))),
        float(LKA.get("ground_bank", 0.05)) * S)
mb_z = _m("MULTIPLY", _smooth(Z, 0.05 * HF, 0.15 * HF), _m("SUBTRACT", 1.0, _smooth(Z, 0.5 * HF, 0.8 * HF)))
mb = _m("MULTIPLY", _m("MULTIPLY", _m("MULTIPLY", mb_z, where), _smooth(banks, 0.42, 0.62)), float(LKA.get("mid_bank", 0.03)) * S)
dens = _m("ADD", dens, mb)
dens_all = _m("ADD", dens, gb)
''')
rep('nt.links.new(dens, vs.inputs["Density"])', 'nt.links.new(dens_all, vs.inputs["Density"])')
# haze thins with altitude above the skyline so the beams dissolve along their length
rep('''haze.inputs["Density"].default_value = float(LKA.get("haze", 0.0016)) * S
''', '''haze.inputs["Density"].default_value = float(LKA.get("haze", 0.0016)) * S
_hz = _m("MULTIPLY", _m("EXPONENT", _m("MULTIPLY", _m("MAXIMUM", _m("SUBTRACT", Z, H_SKY), 0.0), -1.0 / float(LKA.get("haze_efold", 40.0))), 0),
         float(LKA.get("haze", 0.0016)) * S)
nt.links.new(_hz, haze.inputs["Density"])
''')
# the ground bank glows in the district pair (picks up the street neon), mixed by a slow noise along the street
rep('''add2 = nt.nodes.new("ShaderNodeAddShader")''', '''gramp = nt.nodes.new("ShaderNodeValToRGB")
_gl = gramp.color_ramp.elements
_gl[0].position, _gl[0].color = 0.3, (1.0, 0.16, 0.6, 1)
_gl[1].position, _gl[1].color = 0.7, (0.16, 0.8, 1.0, 1)
nt.links.new(_noise((0.012 * S, 0.012 * S, 0.05 * S), 1.0, 33.0), gramp.inputs["Fac"])
gem = nt.nodes.new("ShaderNodeEmission")
nt.links.new(gramp.outputs["Color"], gem.inputs["Color"])
nt.links.new(_m("MULTIPLY", gb, float(LKA.get("ground_glow", 0.35))), gem.inputs["Strength"])
add3 = nt.nodes.new("ShaderNodeAddShader")
nt.links.new(emv.outputs[0], add3.inputs[0])
nt.links.new(gem.outputs[0], add3.inputs[1])
emv = add3
add2 = nt.nodes.new("ShaderNodeAddShader")''')
open(p, "w", encoding="utf-8").write(s)

p = "sb_ocjobs.py"
s = open(p, encoding="utf-8").read()
rep("beam=5.0e6, beams=6", "beam=1.5e6, beams=6, beam_core=3.0, beam_core_k=0.3, haze_efold=40.0, gb_top=2.2, ground_bank=0.05, ground_glow=0.35, mid_bank=0.03")
rep("fog_peak=0.039, beam_cone=10.0, underlight_k=0.06", "fog_peak=0.05, beam_cone=16.0, underlight_k=0.12")
open(p, "w", encoding="utf-8").write(s)
print("ok")
