p='D:/rc_art/art-pass/docs/concepts/netrun_cel/v2/scripts/mk_nr_dump.py'
s=open(p,encoding='utf-8').read()
a='''		var ic: CityIsoCamera = v.iso'''
b='''		var nr_gr: Array = []
		for jj2 in range(v.cfg.city_rect.position.y, v.cfg.city_rect.end.y):
			for ii2 in range(v.cfg.city_rect.position.x, v.cfg.city_rect.end.x):
				nr_gr.append(snappedf(v.model.ground_at(Vector2(ii2 + 0.5, jj2 + 0.5)), 0.01))
		var ic: CityIsoCamera = v.iso'''
assert a in s
s=s.replace(a,b,1)
s=s.replace('"parks": nr_pk, "hqs": nr_hq,','"parks": nr_pk, "hqs": nr_hq, "ground": nr_gr,')
open(p,'w',encoding='utf-8').write(s)
