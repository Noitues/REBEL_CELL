class_name DressFrontage
extends RefCounted
## NA-24: the city signage of the route-side frontage (PIPELINE_SPEC 9.1 rule 2) as placement lists: blade signs, shopfront strips,
## roof billboards and steam plume vents. A pure function of the street derive v2, the exporter's city and the config: a building
## takes a class when `DressDistricts.hash01(class, bid) < share * band multiplier` (a hash of the building id, no RNG stream), so the
## same layout seed gives identical items. Lots are axis aligned: a face is the building box edge nearest the street line.
## Items carry plan positions (x, y, height above ground) and palette ids only.


## `{signs, shops, billboards, plumes}` for the street of `derive` over `city`.
static func plan(derive: Dictionary, city: Dictionary, dist: DressDistricts) -> Dictionary:
	var cfg := DressingConfigData.shipped()
	var fr: Dictionary = cfg.frontage
	var caps: Dictionary = cfg.caps
	var f: Dictionary = NetrunArtDress.frame(derive)
	var ax: int = int(f["ax"])
	var a: Array = f["a"]
	var route: Array = derive["route_keys"]
	var half: float = float(NetrunArtDress.PRESET["street_width"]) / 2.0
	var cands: Array = []
	for b: Dictionary in city["buildings"]:
		if bool(b["hq"]) or route.has(b["bid"]):
			continue
		var lo := INF
		var hi := -INF
		var clo := INF
		var chi := -INF
		var top := -INF
		for pt: Dictionary in b["parts"]:
			for q: Array in pt["poly"]:
				lo = minf(lo, float(q[ax]))
				hi = maxf(hi, float(q[ax]))
				clo = minf(clo, float(q[1 - ax]))
				chi = maxf(chi, float(q[1 - ax]))
			top = maxf(top, float(pt["z0"]) + float(pt["h"]))
		var ua: float = (lo - float(a[ax])) * float(f["sgn"])
		var ub: float = (hi - float(a[ax])) * float(f["sgn"])
		var u0: float = minf(ua, ub)
		var u1: float = maxf(ua, ub)
		var cc: float = (clo + chi) * 0.5
		if (cc - float(f["cline"])) * float(f["ncross"]) <= 0.0:
			continue
		var face: float = chi if float(f["ncross"]) < 0.0 else clo
		var depth: float = absf(face - float(f["cline"]))
		if depth < half - 0.5 or depth > float(fr["depth_max"]):
			continue
		if u1 < -float(fr["along_pad"]) or u0 > float(f["length"]) + float(fr["along_pad"]) or top < float(fr["min_top"]):
			continue
		cands.append({"bid": String(b["bid"]), "u0": u0, "u1": u1, "face": face, "depth": depth, "top": top, "cross_c": cc})
	cands.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		if float(x["depth"]) != float(y["depth"]):
			return float(x["depth"]) < float(y["depth"])
		return IdSort.less(x["bid"], y["bid"]))
	var signs: Array = []
	var shops: Array = []
	var bills: Array = []
	var plumes: Array = []
	var nrm: Array = f["nrm"]
	for c: Dictionary in cands:
		var bid: String = c["bid"]
		var u0: float = c["u0"]
		var u1: float = c["u1"]
		var face: float = c["face"]
		var top: float = c["top"]
		var mid: Array = NetrunArtDress.world(f, (u0 + u1) * 0.5, face, 0.0)
		var band: Dictionary = dist.band_at(float(mid[0]), float(mid[1]))
		var sm: float = float(band["sign_mul"])
		var em: float = float(band["emit_mul"])
		var pal_i: int = 1 if DressDistricts.hash01("pal", bid) < 0.5 else 0
		var pal: String = NetrunArtDress.SIGN_PAL[pal_i]
		var other: String = NetrunArtDress.SIGN_PAL[1 - pal_i]
		if signs.size() < int(caps["city_signs"]) and u1 - u0 > 2.0 and DressDistricts.hash01("sign", bid) < float(fr["sign_share"]) * sm:
			var h: float = lerpf(float(fr["sign_h_min"]), float(fr["sign_h_max"]), DressDistricts.hash01("sign_h", bid))
			h = minf(h, top - 2.0 - float(NetrunArtDress.PRESET["sign_z0"]))
			var u: float = lerpf(u0 + 0.8, u1 - 0.8, DressDistricts.hash01("sign_u", bid))
			var p: Array = NetrunArtDress.world(f, u, face - 0.25 * float(f["ncross"]), float(NetrunArtDress.PRESET["sign_z0"]))
			signs.append({"bid": bid, "pos": p, "nrm": nrm.duplicate(), "w": float(fr["sign_w"]), "h": h,
				"panels": maxi(int(NetrunArtDress.PRESET["sign_min_panels"]), int(h / float(NetrunArtDress.PRESET["sign_panel"]))),
				"pal": pal, "band_pal": other, "emit_mul": em, "seed": DressDistricts.hash01("sign_s", bid),
				"phase": DressDistricts.hash01("sign_p", bid)})
		if shops.size() < int(caps["shopfronts"]) and u1 - u0 > 2.0 and DressDistricts.hash01("shop", bid) < float(fr["shop_share"]) * sm:
			shops.append({"bid": bid, "u0": u0 + 0.4, "u1": u1 - 0.4, "face": face, "z": float(fr["shop_z"]), "h": float(fr["shop_h"]),
				"nrm": nrm.duplicate(), "pal": other if DressDistricts.hash01("shop_p", bid) < 0.5 else "accent_warm", "emit_mul": em})
		if bills.size() < int(caps["billboards"]) and u1 - u0 > 4.0 and top > 14.0 and DressDistricts.hash01("bill", bid) < float(fr["billboard_share"]) * sm:
			var bu: float = (u0 + u1) * 0.5
			bills.append({"bid": bid, "pos": NetrunArtDress.world(f, bu, face - 0.5 * float(f["ncross"]), top + float(fr["billboard_up"])),
				"nrm": nrm.duplicate(), "w": minf(float(fr["billboard_w"]), u1 - u0 - 1.0), "h": float(fr["billboard_h"]),
				"pal": pal, "emit_mul": em, "phase": DressDistricts.hash01("bill_p", bid)})
		if plumes.size() < int(caps["plumes"]) and top > 12.0 and DressDistricts.hash01("plume", bid) < float(fr["plume_share"]) * float(band["plume_mul"]):
			var pu: float = lerpf(u0 + 1.0, maxf(u0 + 1.0, u1 - 1.0), DressDistricts.hash01("plume_u", bid))
			var pc: float = face + (1.5 + 3.0 * DressDistricts.hash01("plume_c", bid)) * float(f["ncross"])
			plumes.append({"bid": bid, "pos": NetrunArtDress.world(f, pu, pc, top), "phase": DressDistricts.hash01("plume_p", bid)})
	return {"signs": signs, "shops": shops, "billboards": bills, "plumes": plumes}
