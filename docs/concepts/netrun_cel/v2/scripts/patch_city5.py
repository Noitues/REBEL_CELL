p='mk_nr_city.py'
s=open(p,encoding='utf-8').read()
s=s.replace("s += '\n' + open(base + 'nr_city_part.py'","""rep("    b.inputs['Metallic'].default_value = 0.0", "    b.inputs['Metallic'].default_value = 0.0\n    L.new(at.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = float(os.environ.get('NR_GEMIT', '0.0'))")
s += '\n' + open(base + 'nr_city_part.py'""",1)
open(p,'w',encoding='utf-8').write(s)
q='nr_city_part.py'
t=open(q,encoding='utf-8').read()
t=t.replace("    os.environ['NR_BODYK'] =","    os.environ['NR_GEMIT'] = os.environ.get('NR_GEMIT', '0.55' if FRAME == 'f2' else '0.06')\n    os.environ['NR_BODYK'] =",1)
open(q,'w',encoding='utf-8').write(t)
