s = open('p2_build.py').read()
s = s.replace("import p2_press as PR\n", "import p2_press as PR\nimport p3_look as P3\n", 1)
s = s.replace("        _cache['P'] = C.load_plate()\n    return _cache['geo'], _cache['sg'], _cache['P']",
              "        _cache['P'] = C.load_plate()\n        _cache['Pw'] = np.load(L.WORK + C.REC)['P']\n        _cache['hp'] = P3.hero_pack(_cache['geo'], _cache['Pw'])\n    return _cache['geo'], _cache['sg'], _cache['P']")
s = s.replace("refl_k=0.9, e_bloom=0.6, home_bloom=1.0, burn=None, cap_occ=None, cap_spill=None):",
              "refl_k=1.2, e_bloom=0.6, home_bloom=1.0, burn=None, cap_occ=None, cap_spill=None, shaft_k=1.0, facade_k=1.0):")
s = s.replace("    img = r['img'] * (1 - sg['body'][..., None] * .7) + sg['emis']\n",
"""    img = r['img'] * (1 - sg['body'][..., None] * .7) + sg['emis']
    hp = _cache['hp']
    # P3 hero facades: real material (glass bands, lit atrium, rooftop sign), corner rim light, sharp ink outline
    img = img * (1 - hp['mul'][..., None] * facade_k) + (hp['emis'] + hp['rim']) * facade_k
    img = img * (1 - 0.8 * hp['ink'][..., None] * facade_k)
    shaft = P3.shafts(img, 0.0, np.array(ui['home_px']) if ui.get('home_px') else None, hp['src'], k=shaft_k) if shaft_k else 0.0
""")
s = s.replace("    img = img + lay['spill'][..., :3] * spill_k\n", "    img = img + lay['spill'][..., :3] * spill_k + shaft\n")
s = s.replace("    refl = G.wet_reflect(r['emis'] * 0.0 + rib_e * 0.55 + sg['emis'] * 0.0, r['wet'], k=refl_k)\n",
              "    refl = P3.wet2(rib_e * 0.55 + r['emis'] * 0.8 + sg['emis'] * 0.7 + hp['emis'] * 0.6, r['wet'], k=refl_k)\n")
open('p2_build.py', 'w').write(s)
print(s.count('P3.'))
