s = open('p1_bl.py').read()
# per-object ghost factor (P3): 0 = ambient (hidden behind buildings), 0..1 scales the see-through gain
s = s.replace("""    add(ob, 'world', tex_emission_mat('blkm_' + b['id'], b['tex'], b.get('strength', 5.0), 1.0))
""", """    add(ob, 'world', tex_emission_mat('blkm_' + b['id'], b['tex'], b.get('strength', 5.0), 1.0))
    ob['p1ghost'] = float(b.get('ghost', 1.0))
""")
s = s.replace("""    q = quad_mesh('glow', (d_['pos'][0], d_['pos'][1], d_['pos'][2] + d_.get('z', 0.5)), (1, 0, 0), (0, 1, 0), d_['r'] * 2, d_['r'] * 2)
    add(q, d_.get('grp', 'world'), radial_mat('glowm', hexlin(d_['col']), d_['strength'], power=d_.get('power', 2.0)))
""", """    q = quad_mesh('glow', (d_['pos'][0], d_['pos'][1], d_['pos'][2] + d_.get('z', 0.5)), (1, 0, 0), (0, 1, 0), d_['r'] * 2, d_['r'] * 2)
    add(q, d_.get('grp', 'world'), radial_mat('glowm', hexlin(d_['col']), d_['strength'], power=d_.get('power', 2.0)))
    q['p1ghost'] = float(d_.get('ghost', 1.0))
""")
s = s.replace("""    ob = ring_mesh('ring_' + rg['id'], rg['pos'], rg['r'], rg['r'] - rg['w'], rg.get('z', 0.45), arc=rg.get('arc'))
    add(ob, rg.get('grp', 'world'), emission_mat('ringm_' + rg['id'], hexlin(rg['col']), rg.get('strength', 6.0), rg.get('alpha', 1.0)))
""", """    ob = ring_mesh('ring_' + rg['id'], rg['pos'], rg['r'], rg['r'] - rg['w'], rg.get('z', 0.45), arc=rg.get('arc'))
    add(ob, rg.get('grp', 'world'), emission_mat('ringm_' + rg['id'], hexlin(rg['col']), rg.get('strength', 6.0), rg.get('alpha', 1.0)))
    ob['p1ghost'] = float(rg.get('ghost', 1.0))
""")
s = s.replace("""    elif p == 'world_ghost':
        city.hide_render = True; set_vis('heads', False); set_vis('lights', False)
        cy.samples = max(16, S0 // 3)
""", """    elif p == 'world_ghost':
        city.hide_render = True; set_vis('heads', False); set_vis('lights', False)
        cy.samples = max(16, S0 // 3)
        # P3: ambient ground marks (ghost 0) are hidden behind buildings; the focused carrier shows through at a reduced gain
        for ob in bpy.data.objects:
            g_ = ob.get('p1ghost')
            if g_ is None or g_ >= 0.999:
                continue
            if g_ <= 0.001:
                ob.hide_render = True
            else:
                for m_ in ob.data.materials:
                    for n_ in m_.node_tree.nodes:
                        if n_.bl_idname == 'ShaderNodeEmission':
                            n_['p1orig'] = n_.inputs[1].default_value
                            n_.inputs[1].default_value = n_['p1orig'] * g_
""")
s = s.replace("""    dump(p)
    scene.render.resolution_percentage = 100
""", """    dump(p)
    if p == 'world_ghost':
        for ob in bpy.data.objects:
            g_ = ob.get('p1ghost')
            if g_ is None or g_ >= 0.999:
                continue
            if g_ <= 0.001:
                ob.hide_render = False
            else:
                for m_ in ob.data.materials:
                    for n_ in m_.node_tree.nodes:
                        if n_.bl_idname == 'ShaderNodeEmission' and 'p1orig' in n_:
                            n_.inputs[1].default_value = n_['p1orig']
    scene.render.resolution_percentage = 100
""")
open('p1_bl.py', 'w').write(s)
print('patched', s.count('p1ghost'))
