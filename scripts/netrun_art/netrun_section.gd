class_name NetrunSection
extends RefCounted
## NA-21 twin of `tools/netrun_art/section.py`: the section cut by zoom and the HQ per-frame section params.


## The `section` config block.
static func _cfg() -> Dictionary:
	return NetrunArtConfigData.shipped().section


## Section constants (`CONSTS`): kit values x K_UNITS (x K_FIT for the HQ scene).
static func consts() -> Dictionary:
	var c: Dictionary = _cfg()
	var kf: float = NetrunArtUnits.k_fit()
	return {
		"k_units": NetrunArtUnits.k_units(),
		"k_fit": kf,
		"band_overview": NetrunArtUnits.kit(float(c["band_overview_kit"])) * kf,
		"band_rooms": NetrunArtUnits.kit(float(c["band_rooms_kit"])) * kf,
		"zref_margin": NetrunArtUnits.kit(float(c["zref_margin_kit"])) * kf,
		"plinth": NetrunArtUnits.kit(float(c["plinth_kit"])),
		"widen": float(c["widen"]),
	}


## Cut height (above local ground) at `zoom_dive`: log-interpolated zf -> zn over a smoothstep of a..b; `z` {} = config default.
static func zcut(zoom: float, z: Dictionary = {}) -> float:
	var cfg: Dictionary = _cfg()
	var c: Dictionary = z if not z.is_empty() else cfg["zcut"]
	var u: float = NetrunArtUnits.smoothstep01((zoom - float(c["a"])) / (float(c["b"]) - float(c["a"])))
	if u > 0.0:
		return exp(log(float(c["zf"])) + (log(float(c["zn"])) - log(float(c["zf"]))) * u)
	return float(cfg["no_cut"])


## Mainline -> AAA-2 look weight at `zoom_dive` (smoothstep over `blend`; `[]` = config look_blend).
static func look_w(zoom: float, blend: Array = []) -> float:
	var b: Array = blend if not blend.is_empty() else _cfg()["look_blend"]
	return NetrunArtUnits.smoothstep01((zoom - float(b[0])) / (float(b[1]) - float(b[0])))


## The per-pose HQ section cut. `keep` is `["rect", hx, hy]`, `["circ", r]` or `[]`; `zref` NAN = none. Returns the `sec_*` keys.
static func section_params(pose_loc: Array, keep: Array, rooms_pts: Array = [], zref: float = NAN, zref_k: float = 1.0) -> Dictionary:
	var cs: Dictionary = consts()
	var cx: float = pose_loc[0]
	var cy: float = pose_loc[1]
	var cz: float = pose_loc[2]
	var ox: float = 0.0
	var oy: float = 0.0
	var has_pts: bool = not rooms_pts.is_empty()
	if has_pts:
		var sx: float = 0.0
		var sy: float = 0.0
		for p: Array in rooms_pts:
			sx += float(p[0])
		for p: Array in rooms_pts:
			sy += float(p[1])
		ox = sx / float(rooms_pts.size())
		oy = sy / float(rooms_pts.size())
	var dx: float = cx - ox
	var dy: float = cy - oy
	var L: float = NetrunArtUnits.hypot(dx, dy)
	if L == 0.0:
		L = 1.0
	var ux: float = dx / L
	var uy: float = dy / L
	var s0: float = 0.0
	var w0: float = 0.0
	var zr: float = 0.0
	var no_zref: bool = is_nan(zref)
	if has_pts:
		var first: bool = true
		var wmax: float = 0.0
		var zmin: float = 0.0
		for p: Array in rooms_pts:
			var s: float = (float(p[0]) - ox) * ux + (float(p[1]) - oy) * uy
			var w: float = absf(-(float(p[0]) - ox) * uy + (float(p[1]) - oy) * ux)
			if first:
				s0 = s
				wmax = w
				zmin = float(p[2])
				first = false
			else:
				s0 = maxf(s0, s)
				wmax = maxf(wmax, w)
				zmin = minf(zmin, float(p[2]))
		w0 = wmax + float(cs["band_rooms"])
		zr = zmin if no_zref else zref
	else:
		var k: Array = keep if not keep.is_empty() else ["circ", 0.0]
		if String(k[0]) == "rect":
			s0 = float(k[1]) * absf(ux) + float(k[2]) * absf(uy)
			w0 = float(k[1]) * absf(uy) + float(k[2]) * absf(ux) + float(cs["band_overview"])
		else:
			s0 = float(k[1])
			w0 = float(k[1]) + float(cs["band_overview"])
		zr = 0.0 if no_zref else zref
	var slope: float = (cz - zr) / maxf(1.0, L - s0)
	if has_pts and no_zref:
		zr = zr * zref_k
	return {"sec_on": true, "sec_ox": ox, "sec_oy": oy, "sec_ux": ux, "sec_uy": uy, "sec_s0": s0, "sec_w0": w0,
		"sec_slope": slope, "sec_zref": zr - float(cs["zref_margin"]), "sec_widen": float(cs["widen"]),
		"sec_plinth": float(cs["plinth"])}


## The `section` block of poses_<run>.json: consts, `zcut`, `look_blend`, no_cut, poche, edge_col.
static func section_block() -> Dictionary:
	var c: Dictionary = _cfg()
	return {"consts": consts(), "zcut": (c["zcut"] as Dictionary).duplicate(), "look_blend": (c["look_blend"] as Array).duplicate(),
		"no_cut": c["no_cut"], "poche": (c["poche"] as Array).duplicate(), "edge_col": (c["edge_col"] as Array).duplicate()}
