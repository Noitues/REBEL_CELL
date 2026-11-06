p = 'D:/rc_art/art-pass/docs/concepts/netrun_cel/v2/scripts/nr_scene_v2.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)

# palette: darker plum/teal bodies
rep("body='#236b63', body2='#184a52'", "body='#2a5a62', body2='#2a2c58'")
rep("body='#5a43b0', body2='#3b2f86'", "body='#4a3a8a', body2='#33285e'")
rep("body='#3d5f86', body2='#2a4466'", "body='#34506f', body2='#2a3a5c'")
rep("body='#8a4538', body2='#5e2f33'", "body='#74363a', body2='#522a40'")
rep("body='#7a2a48', body2='#521d3c'", "body='#6a2444', body2='#481a3c'")
rep("body='#8a7664', body2='#5f5047'", "body='#6e5a5a', body2='#4a3d4c'")
rep("INK_PX = float(os.environ.get('NR_INKPX', '3.4'))", "INK_PX = float(os.environ.get('NR_INKPX', '2.0'))")

# selective neon
rep("    htop = h\n    if h > 26", "    htop = h\n    ACC_ON = R.random() < (0.42 if cn == 'solace' else 0.28) and dim >= 0.6\n    ACC_KIND = R.choice(['parapet', 'corner', 'crown'])\n    if h > 26")
rep("""        urim = hexc(P['rim'], 3.2)
        beam('flat', (x0 + ins, ufy, htop), (x1 - ins, ufy, htop), 0.16, urim)
        beam('flat', (x0 + ins, ufy, h), (x0 + ins, ufy, htop), 0.14, urim)
        beam('flat', (x1 - ins, ufy, h), (x1 - ins, ufy, htop), 0.14, urim)
        if R.random() < 0.5: beam('flat', (x0 + ins, ufy, h + (htop - h) * 0.5), (x1 - ins, ufy, h + (htop - h) * 0.5), 0.1, hexc(P['rim'], 2.0))""",
"""        urim = hexc(P['rim'], 3.2)
        if ACC_ON and ACC_KIND in ('crown', 'parapet'):
            beam('flat', (x0 + ins, ufy, htop), (x1 - ins, ufy, htop), 0.16, urim)
            if ACC_KIND == 'crown':
                beam('flat', (x0 + ins, ufy, htop - 1.6), (x1 - ins, ufy, htop - 1.6), 0.1, urim)
        if ACC_ON and ACC_KIND == 'corner':
            beam('flat', (x0 + ins, ufy, h), (x0 + ins, ufy, htop), 0.14, urim)""")
rep("""    beam('flat', (x0, fy, h), (x1, fy, h), th, rim)
    beam('flat', (x0, y_a, h), (x0, y_b, h), th, rim * 1.0 if False else rimdim)
    beam('flat', (x1, y_a, h), (x1, y_b, h), th, rimdim)
    if R.random() < 0.75:
        beam('flat', (x0 + 0.1, fy, 1.0), (x0 + 0.1, fy, h), th, rim)
    if R.random() < 0.6:
        beam('flat', (x1 - 0.1, fy, 1.0), (x1 - 0.1, fy, h), th, rim)
    # horizontal accent band at a tier
    if h > 18 and R.random() < 0.6:
        zb = R.choice([9.6, 13, 16.2, 22.5]); zb = min(zb, h - 3)
        beam('flat', (x0, fy, zb), (x1, fy, zb), 0.12, rimdim)""",
"""    if ACC_ON:
        if ACC_KIND == 'parapet':
            beam('flat', (x0, fy, h), (x1, fy, h), th, rim)
        elif ACC_KIND == 'corner':
            cxe = x0 + 0.1 if R.random() < .5 else x1 - 0.1
            beam('flat', (cxe, fy, 1.0), (cxe, fy, h), th, rim)
        else:
            beam('flat', (x0, fy, h), (x1, fy, h), th, rim); beam('flat', (x0, fy, h - 1.4), (x1, fy, h - 1.4), 0.1, rimdim)""")

# windows
rep("u = mn('DIVIDE', u, 2.3); v = mn('DIVIDE', sep.outputs['Z'], 3.0)", "u = mn('DIVIDE', u, 0.95); v = mn('DIVIDE', sep.outputs['Z'], 1.25)")
rep("""    inx = mn('MULTIPLY', mn('GREATER_THAN', fu, 0.2), mn('LESS_THAN', fu, 0.8))
    iny = mn('MULTIPLY', mn('GREATER_THAN', fv, 0.28), mn('LESS_THAN', fv, 0.74))""",
"""    cmb3 = N.new('ShaderNodeCombineXYZ'); L.new(cu, cmb3.inputs['X']); L.new(cv, cmb3.inputs['Y']); cmb3.inputs['Z'].default_value = 13.0
    wn3 = N.new('ShaderNodeTexWhiteNoise'); wn3.noise_dimensions = '3D'; L.new(cmb3.outputs[0], wn3.inputs['Vector'])
    lo = mn('ADD', 0.14, mn('MULTIPLY', wn3.outputs['Value'], 0.22)); hi = mn('SUBTRACT', 0.88, mn('MULTIPLY', wn3.outputs['Value'], 0.22))
    lov = mn('ADD', 0.16, mn('MULTIPLY', wn3.outputs['Value'], 0.2)); hiv = mn('SUBTRACT', 0.84, mn('MULTIPLY', wn3.outputs['Value'], 0.28))
    inx = mn('MULTIPLY', mn('GREATER_THAN', fu, lo), mn('LESS_THAN', fu, hi))
    iny = mn('MULTIPLY', mn('GREATER_THAN', fv, lov), mn('LESS_THAN', fv, hiv))""")
rep("warm.outputs[0].default_value = hexc('#FFD27A')", "warm.outputs[0].default_value = hexc('#FFA84A')")
rep("cyan.outputs[0].default_value = hexc('#8FF0FF')", "cyan.outputs[0].default_value = hexc('#C8F2FF')")
rep("L.new(mn('GREATER_THAN', wn2.outputs['Value'], 0.45), mx1.inputs['Factor'])", "L.new(mn('GREATER_THAN', wn2.outputs['Value'], 0.76), mx1.inputs['Factor'])")
rep("wcol.inputs['Scale'].default_value = 1.7", "wcol.inputs['Scale'].default_value = 1.9")
rep("for pos, val in ((0.04, 0.78), (0.09, 0.56), (0.17, 0.4), (0.3, 0.3), (0.6, 0.24)):", "for pos, val in ((0.04, 0.8), (0.09, 0.66), (0.17, 0.54), (0.3, 0.46), (0.6, 0.4)):")
rep("    shade = mn('MULTIPLY', mn('MULTIPLY', mn('MULTIPLY', side, roof), mn('MULTIPLY', band, col_line)), ramp.outputs['Color'])",
"""    mpg = N.new('ShaderNodeMapping'); mpg.inputs['Scale'].default_value = (0.7, 0.7, 0.10); L.new(geo.outputs['Position'], mpg.inputs['Vector'])
    ng = N.new('ShaderNodeTexNoise'); ng.inputs['Scale'].default_value = 2.2; ng.inputs['Detail'].default_value = 6; L.new(mpg.outputs[0], ng.inputs['Vector'])
    mps = N.new('ShaderNodeMapping'); mps.inputs['Scale'].default_value = (2.6, 2.6, 0.035); L.new(geo.outputs['Position'], mps.inputs['Vector'])
    nsg = N.new('ShaderNodeTexNoise'); nsg.inputs['Scale'].default_value = 3.0; nsg.inputs['Detail'].default_value = 3; L.new(mps.outputs[0], nsg.inputs['Vector'])
    grime = mn('ADD', 0.55, mn('ADD', mn('MULTIPLY', ng.outputs['Fac'], 0.6), mn('MULTIPLY', nsg.outputs['Fac'], 0.4)))
    shade = mn('MULTIPLY', mn('MULTIPLY', mn('MULTIPLY', mn('MULTIPLY', side, roof), mn('MULTIPLY', band, col_line)), ramp.outputs['Color']), grime)""")
rep("L.new(fog_mix(nt, fin2.outputs[2]), e.inputs['Color']); e.inputs['Strength'].default_value = 0.82", "L.new(fog_mix(nt, fin2.outputs[2]), e.inputs['Color']); e.inputs['Strength'].default_value = 0.5")
rep("def fog_mix(nt, col_sock, k=0.0065, fmax=0.75):", "def fog_mix(nt, col_sock, k=0.005, fmax=0.5):")
rep("fc.outputs[0].default_value = hexc('#5a2a78', 0.8)", "fc.outputs[0].default_value = hexc('#3a1a5a', 0.8)")
rep("band = mn('SUBTRACT', 1.0, mn('MULTIPLY', mn('LESS_THAN', fv, 0.09), 0.38))", "band = mn('SUBTRACT', 1.0, mn('MULTIPLY', mn('LESS_THAN', fv, 0.07), 0.25))")
rep("col_line = mn('SUBTRACT', 1.0, mn('MULTIPLY', mn('LESS_THAN', fu, 0.035), 0.2))", "col_line = mn('SUBTRACT', 1.0, mn('MULTIPLY', mn('LESS_THAN', fu, 0.04), 0.12))")
rep("    lit = R.uniform(0.2, 0.5) * (0.6 if dim < 1 else 1.0)", "    lit = R.uniform(0.1, 0.3) * (0.7 if dim < 1 else 1.0)")

# ground
rep("    beam('flat', (x0, Y_N - 5.5, 0.2), (x1, Y_N - 5.5, 0.2), .14, hexc('#8A5CFF', 2.4))\n    beam('flat', (x0, Y_S + 5.5, 0.2), (x1, Y_S + 5.5, 0.2), .14, hexc('#8A5CFF', 2.4))", "    beam('flat', (x0, Y_N - 5.5, 0.2), (x1, Y_N - 5.5, 0.2), .06, hexc('#5a3a9a', 0.8))")
rep("""    for k in range(34):
        x = R.uniform(-90, 200); lane = YC + R.choice([2.2, 4.4, 5.2, -9.5, -11.0])
        L = R.uniform(8, 26); c = R.choice([hexc('#FF3A2A', 3.2), hexc('#FFD060', 3.2), hexc('#FFFFFF', 2.5), hexc(PINK, 3.0), hexc(CYAN, 3.0)])""",
"""    for k in range(110):
        x = R.uniform(-110, 220)
        lane = (YC + R.choice([2.0, 3.0, 4.0, 5.0, 5.6, 2.6])) if k % 3 else (Y_S + R.choice([6.5, 7.6, 8.8, 10.0]))
        L = R.uniform(18, 80); c = R.choice([hexc('#FF2A22', 3.4), hexc('#FF2A22', 3.4), hexc('#FF4A30', 3.0), hexc('#FFFFFF', 3.0), hexc('#FFFFFF', 3.0), hexc('#FFD060', 2.6), hexc(PINK, 2.6)])""")

# route
rep("nrm = Vector((-d.y, d.x, 0)).normalized() * 0.55", "nrm = Vector((-d.y, d.x, 0)).normalized() * RW")
rep("def route():\n", "def route():\n    RW = {'f2': 0.8, 'f3': 0.34, 'f4': 0.34}[FRAME]; RS = {'f2': 2.4, 'f3': 1.0, 'f4': 1.0}[FRAME]\n    SEL = {'f2': 13, 'f3': 3, 'f4': 13}[FRAME]\n")
rep("beam('flat', p0, p1, 0.26, hexc(LIME, 4.5), hint=(0, 0, 1))", "beam('flat', p0, p1, 0.16 * RS, hexc(LIME, 4.5), hint=(0, 0, 1))")
i0 = s.index("    # nodes\n    for x, t in zip(NODE_X, NODE_TYPES):"); i1 = s.index("def street_furniture")
s = s[:i0] + """    # nodes: small ground discs; only the selected node gets a pole and marker
    for ni, (x, t) in enumerate(zip(NODE_X, NODE_TYPES)):
        y = route_y(x); c = NCOL[t]
        add_ring('flat', (x, y), 1.0 * RS, 1.4 * RS, hexc(c, 4.5), 32, z=0.08)
        add_ring('flat', (x, y), 0.0 + 0.1, 0.9 * RS, hexc(c, 1.2), 20, z=0.075)
        if ni == SEL:
            add_ring('flat', (x, y), 1.9 * RS, 2.1 * RS, hexc('#FFFFFF', 3.0), 32, z=0.085)
            beam('flat', (x, y, 0.1), (x, y, 5.5 * RS), 0.1 * RS, hexc('#EFFFE0', 4.0))
            ph = 5.5 * RS
            ACC['flat'].add_poly([(x, y, ph + 0.1 * RS), (x + 0.7 * RS, y, ph + 1.1 * RS), (x, y, ph + 2.1 * RS), (x - 0.7 * RS, y, ph + 1.1 * RS)], [(0, 1, 2, 3), (3, 2, 1, 0)], hexc('#EFFFE0', 4.0))

""" + s[i1:]

# layout / cameras
rep("'f2': ((40.0, -200.0, 135.0), (82.0, -6.0, 8.0), 40)", "'f2': ((-75.0, -8.0, 66.0), (112.0, -7.0, 40.0), 27)")
rep("'f2': (40.0, -200.0, 135.0)", "'f2': (-75.0, -8.0, 66.0)")
rep("'f3': ((-6.0, -58.0, 19.0), (0.0, 6.0, 13.0), 22)", "'f3': ((-6.0, -78.0, 22.0), (0.0, 6.0, 31.0), 24)")
rep("'f3': (-6.0, -58.0, 19.0)", "'f3': (-6.0, -78.0, 22.0)")
rep("'f4': ((4.0, -10.0, 9.0), (118.0, -7.0, 34.0), 18)", "'f4': ((-8.0, -9.5, 11.0), (118.0, -7.0, 40.0), 19)")
rep("'f4': (4.0, -10.0, 9.0)", "'f4': (-8.0, -9.5, 11.0)")
rep("'f3': (-4, YC, 75, 170)", "'f3': (-4, YC, 90, 190)")
rep("    row(Y_N, 18, -1, -75, 84, 18, 40)\n    row(Y_S, 18, 1, 60 if FRAME == 'f3' else -75, 84, 20, 56)",
    "    row(Y_N, 18, -1, -75, 84, 16, 34 if FRAME == 'f3' else 40)\n    row(Y_S, 18, 1, 60 if FRAME == 'f3' else -75, 84, 12 if FRAME == 'f2' else 20, 24 if FRAME == 'f2' else 56)")
rep("((Y_N + 22, 0, -1, 34, 74), (Y_N + 52, 0, -1, 46, 100),", "((Y_N + 22, 0, -1, 28, 52 if FRAME == 'f3' else 74), (Y_N + 52, 0, -1, 36, 66 if FRAME == 'f3' else 100),")
i0 = s.index("    for k in range(7):\n        bx = -90"); i1 = s.index("    # far skyline ring")
s = s[:i0] + """    BEAMS = {'f3': [(-58, Y_N + 52, 56, PINK), (-20, Y_N + 22, 40, CYAN), (24, Y_N + 52, 60, LIME), (58, Y_N + 22, 46, '#FFFFFF')],
             'f4': [(60, Y_N + 22, 40, PINK), (105, Y_S - 16, 50, CYAN), (150, Y_N + 40, 60, LIME), (20, Y_S - 16, 40, PINK)],
             'f2': [(20, Y_N + 22, 60, PINK), (140, Y_N + 22, 60, CYAN), (-30, Y_N + 52, 70, LIME)]}[FRAME]
    for (bx, by, bz, bc) in BEAMS:
        light_beam((bx, by, bz), (R.uniform(-.25, .25), -0.12, 1.0), 120, 1.7, hexc(bc, 3.0), a0=0.5)
""" + s[i1:]
rep("    for k in range(70):\n        x = R.uniform(-160, 300); side = R.choice([-1, 1]); y = YC + side * R.uniform(120, 260)", "    for k in range(34):\n        x = R.uniform(-160, 300); side = R.choice([-1, 1]); y = YC + side * R.uniform(120, 260)")
rep("R.uniform(70, 170), -side, lod=0, dim=0.45)", "R.uniform(50, 120), -side, lod=0, dim=0.4)")

# sky + mist
rep("el = ramp.color_ramp.elements; el[0].position = 0.0; el[0].color = hexc('#b04aa0'); el[1].position = 1.0; el[1].color = hexc('#3d1a70')",
"""el = ramp.color_ramp.elements; el[0].position = 0.0; el[0].color = hexc('#d0568a'); el[1].position = 1.0; el[1].color = hexc('#150a34')
    e2 = el.new(0.10); e2.color = hexc('#8a3a90'); e3 = el.new(0.45); e3.color = hexc('#3a1a6e')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.4; nz.inputs['Detail'].default_value = 5
    mpn = N.new('ShaderNodeMapping'); mpn.inputs['Scale'].default_value = (1.0, 1.0, 3.2); L.new(ge.outputs['Incoming'], mpn.inputs['Vector']); L.new(mpn.outputs[0], nz.inputs['Vector'])
    adn = N.new('ShaderNodeMath'); adn.operation = 'ADD'; L.new(mr.outputs[0], adn.inputs[0]); sbn = N.new('ShaderNodeMath'); sbn.operation = 'MULTIPLY'; sbn.inputs[1].default_value = 0.22; L.new(nz.outputs['Fac'], sbn.inputs[0])
    L.new(sbn.outputs[0], adn.inputs[1])
    L.new(adn.outputs[0], ramp.inputs['Fac'])""")
rep("vs.inputs['Density'].default_value = float(os.environ.get('NR_FOG', '0.0035'))", "vs.inputs['Density'].default_value = float(os.environ.get('NR_FOG', '0.0018'))")
rep("def camera():", """def mist():
    me = bpy.data.meshes.new('mist'); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('mist', me); ob.scale = (460, 150, 9.0); ob.location = (50, -20, 4.5); bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new('mist'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    v = nt.nodes.new('ShaderNodeVolumeScatter'); v.inputs['Density'].default_value = float(os.environ.get('NR_MIST', '0.028')); v.inputs['Color'].default_value = hexc('#c88adf'); v.inputs['Anisotropy'].default_value = 0.4
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(v.outputs[0], o.inputs['Volume']); me.materials.append(m)

def camera():""")
rep("    world(); camera(); render_setup()", "    world(); mist(); camera(); render_setup()")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
