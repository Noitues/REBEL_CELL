"""Builds tools/look_parity/nr_dump.gd(+tscn) in the tide clone (untracked, not committed there): parity_capture plus a full
city-data JSON (prism polygons, heights, territory, streets, plazas, parks, hqs, camera) written when --lot-dump is given."""
src = 'D:/rc_art/godot_look_tide/tools/look_parity/parity_capture.gd'
dst = 'D:/rc_art/godot_look_tide/tools/look_parity/nr_dump.gd'
s = open(src, encoding='utf-8').read()
marker = "		var lf := FileAccess.open(_lot_dump, FileAccess.WRITE)\n		lf.store_string(JSON.stringify(lrows))\n		lf.close()\n"
assert marker in s
extra = marker + '''		# --- netrun_cel: the real city data of this frame
		var nr_pr: Array = []
		for pr1: Dictionary in v.model.prisms:
			var poly1: PackedVector2Array = pr1["poly"]
			var pp: Array = []
			for q1 in poly1:
				pp.append([snappedf(q1.x, 0.01), snappedf(q1.y, 0.01)])
			var cell1: Rect2i = pr1["cell"]
			nr_pr.append({"poly": pp, "y0": snappedf(float(pr1["y0"]), 0.01), "h": snappedf(float(pr1["h"]), 0.01), "taper": float(pr1["taper"]),
				"terr": String(pr1.get("terr", &"")), "key": int(pr1["key"]), "ak": int(CityCorpColor.kinds.get(int(pr1["key"]), 0)),
				"cell": [cell1.position.x, cell1.position.y, cell1.size.x, cell1.size.y], "hq": bool(pr1.get("hq", false)), "building": int(pr1.get("building", -1))})
		var nr_st: Array = []
		for s1: Dictionary in v.model.streets:
			var l1: Vector2i = s1["lot"]
			nr_st.append([l1.x, l1.y, int(s1.get("along_i", 0)), int(s1.get("along_j", 0)), snappedf(float(s1.get("traffic", 0.0)), 0.01), (s1["col"] as Color).to_html(false) if s1.has("col") else ""])
		var nr_pl: Array = []
		for p1: Dictionary in v.model.plazas:
			var pl1: Vector2i = p1["lot"]
			nr_pl.append([pl1.x, pl1.y, String(p1.get("terr", &""))])
		var nr_pk: Array = []
		for q2 in CityParkKit.parks_in(v.city_seed, v.cfg.city_rect):
			nr_pk.append([q2.x, q2.y])
		var nr_hq: Dictionary = {}
		for hc1 in v.model.hqs:
			var hr1: Rect2i = v.model.hqs[hc1]
			nr_hq[String(hc1)] = [hr1.position.x, hr1.position.y, hr1.size.x, hr1.size.y]
		var nr_gr: Array = []
		for jj2 in range(v.cfg.city_rect.position.y, v.cfg.city_rect.end.y):
			for ii2 in range(v.cfg.city_rect.position.x, v.cfg.city_rect.end.x):
				nr_gr.append(snappedf(v.model.ground_at(Vector2(ii2 + 0.5, jj2 + 0.5)), 0.01))
		var ic: CityIsoCamera = v.iso
		var nr_cam := {"yaw": ic.yaw_deg, "pitch": ic.pitch_deg, "target": [ic.target.x, ic.target.y, ic.target.z], "ortho": ic.ortho, "viewport": [ic.viewport.x, ic.viewport.y],
			"distance": ic.distance, "fov": ic.fov_deg, "lot_bu": v.cfg.lot_bu, "district_centre": [v.cfg.district_centre.x, v.cfg.district_centre.y],
			"city_rect": [v.cfg.city_rect.position.x, v.cfg.city_rect.position.y, v.cfg.city_rect.size.x, v.cfg.city_rect.size.y], "seed": v.city_seed}
		var nf := FileAccess.open(_lot_dump.replace(".json", "_city.json"), FileAccess.WRITE)
		nf.store_string(JSON.stringify({"prisms": nr_pr, "streets": nr_st, "plazas": nr_pl, "parks": nr_pk, "hqs": nr_hq, "ground": nr_gr, "camera": nr_cam}))
		nf.close()
'''
s = s.replace(marker, extra, 1)
open(dst, 'w', encoding='utf-8').write(s)
open('D:/rc_art/godot_look_tide/tools/look_parity/nr_dump.tscn', 'w', encoding='utf-8').write('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://tools/look_parity/nr_dump.gd" id="1"]\n\n[node name="NrDump" type="Node"]\nscript = ExtResource("1")\n')
print('ok')
