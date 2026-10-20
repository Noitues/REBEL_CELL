class_name NetrunArtExport
extends RefCounted
## NA-02: the netrun-art data contract v1 (docs/handoff/plan2/NA02_FIELDS.md, which wins over
## PIPELINE_SPEC §2.0c / 2.3 / 3.5): `city.json`, `net.json`, `run_graph.json`,
## `key_locations.json` and the game keys of `derive_<run>.json`, built read-only from the
## city recording, the corporation's Grid, the Grid state and the run's map. Canonical text
## (`canonical`): UTF-8 unescaped, LF, sorted keys, indent 1, floats fixed at 1e-4, u64 as
## decimal strings; byte-identical to tools/netrun_art/io.py `canonical_dumps`.
##
## Pure: every input is a parameter (no Node, no autoload), nothing it reads is changed, and no
## RNG stream is read or advanced (art seeds come from ArtSeed). The city side takes the plain
## data of a FULL-city CityModel build (prisms, streets, plazas, hqs), so this file holds no
## view dependency; the caller builds the model.

## Contract version written in every file.
const VERSION: int = 1
## RG-01: `run_graph.json` is contract v2 (node types add rest, workshop, cache; schemas/run_graph.schema.json).
const RUN_GRAPH_VERSION: int = 2
## JSON ints stay within +-2^53 (u64 values are decimal strings).
const INT_LIMIT: int = 9007199254740992
## Grid status -> net.json node state (the home Site is "core").
const SITE_STATES := {GridState.SiteStatus.CORPORATE: "corporate", GridState.SiteStatus.CLEARED: "cleared",
	GridState.SiteStatus.CLAIMED: "owned", GridState.SiteStatus.TAKEN: "taken"}
const NODE_TYPES := {RC.InfilNodeType.ROUTER: "router", RC.InfilNodeType.TERMINAL: "terminal",
	RC.InfilNodeType.MAINFRAME: "mainframe", RC.InfilNodeType.SERVER_RACK: "server_rack",
	RC.InfilNodeType.REST: "rest", RC.InfilNodeType.WORKSHOP: "workshop", RC.InfilNodeType.CACHE: "cache"}
const EXPLOITS := {RC.ExploitType.INTEL: "intel", RC.ExploitType.BREACH: "breach", RC.ExploitType.VIRUS: "virus"}
## Scene-level art streams (no per-object keys; section 7 with the O6 city.* names).
const SCENE_STREAMS: Array[String] = ["beams", "cars", "city.beams", "city.build", "city.landmark", "city.post",
	"city.ring", "city.sea", "city.streaks", "city.zoning", "city_fill", "cycles", "downtown", "flicker",
	"glitch", "glows", "ground_glow", "plumes", "ring", "scene", "sky", "street_lanes", "windows_flicker"]
## Keyed streams whose base seed (keys omitted) the derive file carries.
const BASE_STREAMS: Array[String] = ["fauna.tethys", "terrain", "variance"]
## Per-corporation streams (`<prefix><corp>`): landmark detail (unkeyed) and the key-location
## landmark base seed.
const CORP_STREAMS: Array[String] = ["key_landmark.", "landmark."]

## Tooling hook (tools/netrun_art/export_contract.gd): called with the NetrunSession once a
## netrun has started. Empty in the game; it observes and never changes state.
static var sink: Callable = Callable()


## NetrunSession.start's hook: hands the started session to `sink` when one is set.
static func on_run_start(session: RefCounted) -> void:
	if sink.is_valid():
		sink.call(session)


# --- Files -----------------------------------------------------------------------------------

## The run-level files of a started netrun `session` against the exported `city` (a
## `city_json` dict; `index` its `lot_index`) and the corporation's Site layout points:
## {"files": {file name: canonical text}, "error": ""}. Reads the session, never changes it.
static func export_run(session: NetrunSession, city: Dictionary, index: Dictionary, site_points: Dictionary, reach_lots: int, keys: Dictionary = {}) -> Dictionary:
	var corp := session.corporation
	if corp == null or corp.city_grid == null or session.campaign.grid == null:
		return {"files": {}, "error": "export_run: the run has no corporation Grid"}
	var seed := ArtSeed.u64_from_str(city["layout_seed"])
	var origin := Vector2(city["origin_lot"][0], city["origin_lot"][1])
	var lot_bu: float = city["lot_bu"]
	var rid := run_id(session.run)
	var net := net_json(seed, lot_bu, origin, corp, session.campaign.grid, site_points)
	var key_doc := key_locations_json(seed, corp, site_points, index, reach_lots, keys)
	for d: Dictionary in [net, key_doc]:
		if d.has("error"):
			return {"files": {}, "error": d["error"]}
	var corps: Array = (city["hqs"] as Dictionary).keys()
	IdSort.sort_ids(corps)
	return {"error": "", "files": {
		"net.json": canonical(net),
		"run_graph.json": canonical(run_graph_json(session.run.map, rid)),
		"key_locations.json": canonical(key_doc),
		"derive_%s.json" % rid: canonical(derive_json(run_kind(session.run), seed, rid, corps)),
	}}


## `city.json` v1 from a full-city CityModel's data: `city_seed` (signed), `lot_bu`, the
## origin lot (CityConfig.district_centre), the world prisms, street and plaza lots and the
## HQ rects. One building per cell (`bid` "i:j" of the cell's origin lot; HQ stand-ins
## "hq:<corp>"), parts sorted by (z0, recorded order).
## NA-12 r2: `sections` adds the optional v1 sections of a generated city (CityPlan.city_sections: `coast`, `terrain`;
## {} for the fixed city, so its file is unchanged).
static func city_json(city_seed: int, lot_bu: float, origin: Vector2, prisms: Array, streets: Array, plazas: Array, hqs: Dictionary,
		sections: Dictionary = {}) -> Dictionary:
	var by_bid := {}
	for pr: Dictionary in prisms:
		var cell: Rect2i = pr["cell"]
		var hq := bool(pr.get("hq", false))
		var bid := "hq:%s" % pr["terr"] if hq else "%d:%d" % [cell.position.x, cell.position.y]
		if not by_bid.has(bid):
			by_bid[bid] = {"bid": bid, "cell": _rect(cell), "terr": String(pr["terr"]), "hq": hq, "parts": [],
				"ground": float(pr.get("ground", 0.0))}
		var poly := []
		for q: Vector2 in pr["poly"]:
			poly.append([q.x, -q.y])
		var parts: Array = by_bid[bid]["parts"]
		parts.append({"poly": poly, "z0": float(pr["y0"]) - float(pr.get("ground", 0.0)), "h": float(pr["h"]), "taper": float(pr["taper"]),
			"_ord": parts.size(), "_key": int(pr["key"])})
	var bids: Array = by_bid.keys()
	bids.sort()
	var buildings := []
	for bid: String in bids:
		var b: Dictionary = by_bid[bid]
		var parts: Array = b["parts"]
		parts.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
			return x["z0"] < y["z0"] if x["z0"] != y["z0"] else x["_ord"] < y["_ord"])
		b["key"] = parts[0]["_key"]
		for p: Dictionary in parts:
			p.erase("_ord")
			p.erase("_key")
		buildings.append(b)
	var st := []
	for s: Dictionary in streets:
		st.append({"lot": _lot(s["lot"]), "along_i": bool(s["along_i"]), "along_j": bool(s["along_j"]),
			"traffic": float(s["traffic"])})
	st.sort_custom(_by_lot)
	var pl := []
	for p: Dictionary in plazas:
		pl.append({"lot": _lot(p["lot"]), "terr": String(p["terr"])})
	pl.sort_custom(_by_lot)
	var hq_out := {}
	for cid: Variant in hqs:
		hq_out[String(cid)] = _rect(hqs[cid])
	var out := {"version": VERSION, "layout_seed": ArtSeed.u64_str(city_seed), "units": "BU", "lot_bu": lot_bu,
		"origin_lot": [origin.x, origin.y], "buildings": buildings, "streets": st, "plazas": pl, "hqs": hq_out,
		"hq_overlaps": hq_overlaps(buildings, hqs)}
	for k: String in sections:
		out[k] = sections[k]
	return out


## Diagnostic: every non-HQ building whose cell intersects an HQ rect, as {bid, corp}, sorted
## by (bid, corp). Empty for a sound layout (an HQ rect is exclusive); never drops a building.
static func hq_overlaps(buildings: Array, hqs: Dictionary) -> Array:
	var out := []
	var corps: Array = []
	for cid: Variant in hqs:
		corps.append(String(cid))
	corps.sort()
	for b: Dictionary in buildings:
		if bool(b["hq"]):
			continue
		var c: Array = b["cell"]
		var cell := Rect2i(int(c[0]), int(c[1]), int(c[2]), int(c[3]))
		for cid: Variant in hqs:
			if (hqs[cid] as Rect2i).intersects(cell):
				out.append({"bid": b["bid"], "corp": String(cid)})
	out.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		return x["bid"] < y["bid"] if x["bid"] != y["bid"] else x["corp"] < y["corp"])
	return out


## `net.json` v1: the corporation's Sites (BU plan points of `site_points`, ruling O3) with
## their Grid state, and every link with its state and straight 2-point polyline.
## Returns {"error": ...} when a Site has no layout point.
static func net_json(city_seed: int, lot_bu: float, origin: Vector2, corp: CorporationData, grid: GridState, site_points: Dictionary) -> Dictionary:
	var sites := _sites(corp)
	var nodes := []
	var pts := {}
	for sd in sites:
		if not site_points.has(sd.id):
			return {"error": "net.json: Site %s has no layout point" % sd.id}
		pts[sd.id] = plan_point(site_points[sd.id], lot_bu, origin)
		var state: String = "core" if grid.is_home(sd.id) else SITE_STATES.get(grid.status_of(sd.id), "corporate")
		nodes.append({"id": String(sd.id), "lot": pts[sd.id], "state": state})
	var open := {}
	var locked := {}
	for sd in sites:
		for l in sd.links:
			open[GridState.link_key(sd.id, l)] = true
		for l in sd.locked_links:
			locked[GridState.link_key(sd.id, l)] = true
	var keys := {}
	for k: String in open:
		keys[k] = "open"
	for k: String in locked:
		if not keys.has(k):
			keys[k] = "opened" if grid.opened_links.has(k) else "locked"
	var sorted_keys: Array = keys.keys()
	sorted_keys.sort()
	var links := []
	for k: String in sorted_keys:
		var ab := k.split("|")
		if not pts.has(StringName(ab[0])) or not pts.has(StringName(ab[1])):
			return {"error": "net.json: link %s names a Site outside the Grid" % k}
		links.append({"a": ab[0], "b": ab[1], "state": keys[k], "pts": [pts[StringName(ab[0])], pts[StringName(ab[1])]]})
	return {"version": VERSION, "layout_seed": ArtSeed.u64_str(city_seed), "nodes": nodes, "links": links}


## `run_graph.json` v2 (RG-01): the run's MapGraph 1:1 (nodes by layer then index, forward edges).
static func run_graph_json(map: MapGraph, run_id: String) -> Dictionary:
	var nodes := []
	var edges := []
	for layer in range(1, map.layer_count() + 1):
		var row: Array = map.nodes_in_layer(layer).duplicate()
		row.sort_custom(func(x: Dictionary, y: Dictionary) -> bool: return int(x["index"]) < int(y["index"]))
		for n: Dictionary in row:
			nodes.append({"id": String(n["id"]), "layer": int(n["layer"]), "index": int(n["index"]),
				"type": NODE_TYPES.get(int(n["type"]), "router"), "elite": bool(n.get("elite", false))})
			for nx: Variant in n.get("next", []):
				edges.append({"a": String(n["id"]), "b": String(nx)})
	edges.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		return x["a"] < y["a"] if x["a"] != y["a"] else x["b"] < y["b"])
	return {"version": RUN_GRAPH_VERSION, "run": run_id, "layers": map.layer_count(), "nodes": nodes, "edges": edges}


## `key_locations.json` v1: every Exploit Site (exploit_type != NONE, ruling O8) of `corp`
## with the building under it (`site_bid`, ruling O7). `index` is `lot_index` of the city's
## buildings. Returns {"error": ...} naming a Site with no building within `reach_lots`.
## EX-02: `keys` (KeyLots.export_keys of the corporation) moves each Exploit's `bid` to its key building and adds the
## building kind (`building`) and the run's start street lot (`start`); empty = the Site's own building as before.
static func key_locations_json(city_seed: int, corp: CorporationData, site_points: Dictionary, index: Dictionary, reach_lots: int, keys: Dictionary = {}) -> Dictionary:
	var locs := []
	for sd in _sites(corp):
		if sd.exploit_type == RC.ExploitType.NONE:
			continue
		var name: String = EXPLOITS[sd.exploit_type]
		if keys.has(name):
			var k: Dictionary = keys[name]
			locs.append({"site": String(sd.id), "corp": String(corp.id), "bid": k["bid"], "exploit": name, "building": k["building"], "start": k["start"]})
			continue
		var bid := site_bid(site_points.get(sd.id, Vector2.INF), index, reach_lots)
		if bid == "":
			return {"error": "key_locations.json: Exploit Site %s has no building within %d lots" % [sd.id, reach_lots]}
		locs.append({"site": String(sd.id), "corp": String(corp.id), "bid": bid, "exploit": name})
	return {"version": VERSION, "layout_seed": ArtSeed.u64_str(city_seed), "locations": locs}


## The game keys of `derive_<run>.json` v1 (ruling O4; NA-03's derive.street fills the rest):
## `kind` ("street", or "hq" for an HQ breach), the layout seed, the run id and the scene-level
## art seeds (plus the base seeds of the keyed streams) for `corp_ids`.
static func derive_json(kind: String, city_seed: int, run_id: String, corp_ids: Array) -> Dictionary:
	return {"version": VERSION, "kind": kind, "layout_seed": ArtSeed.u64_str(city_seed), "run": run_id,
		"art_seeds": art_seeds(city_seed, corp_ids)}


## Stream name -> u64 decimal seed for every scene-level stream, the keyed streams' base seeds
## and the per-corporation streams of `corp_ids`.
static func art_seeds(city_seed: int, corp_ids: Array) -> Dictionary:
	var out := {}
	for s in SCENE_STREAMS + BASE_STREAMS:
		out[s] = ArtSeed.derive_str(city_seed, s)
	for c: Variant in corp_ids:
		for prefix in CORP_STREAMS:
			out[prefix + String(c)] = ArtSeed.derive_str(city_seed, prefix + String(c))
	return out


## The run id the derive file name carries: "<site id>-<run seed as u64>" (seed only when the
## run has no Site).
static func run_id(run: RunState) -> String:
	var s := ArtSeed.u64_str(run.run_seed)
	return s if run.site_id == &"" else "%s-%s" % [run.site_id, s]


## "street" for a netrun, "hq" for an HQ breach (a "boss" run).
static func run_kind(run: RunState) -> String:
	return "hq" if run.kind == "boss" or run.kind == NetrunSession.HQ_LADDER_KIND else "street"


## Collisions `city_json` would merge silently: a bid reached by two different cells, or a
## non-HQ prism with an empty cell. Empty for a sound recording (acceptance 5).
static func bid_conflicts(prisms: Array) -> PackedStringArray:
	var out := PackedStringArray()
	var cells := {}
	for pr: Dictionary in prisms:
		var cell: Rect2i = pr["cell"]
		var hq := bool(pr.get("hq", false))
		if not hq and (cell.size.x <= 0 or cell.size.y <= 0):
			out.append("empty cell %s" % str(cell))
			continue
		var bid := "hq:%s" % pr["terr"] if hq else "%d:%d" % [cell.position.x, cell.position.y]
		if cells.has(bid) and cells[bid] != cell:
			out.append("%s: %s and %s" % [bid, str(cells[bid]), str(cell)])
		cells[bid] = cell
	return out


# --- Site -> building (ruling O7) ------------------------------------------------------------

## Lot -> [bid, i, j] (the cell's origin) for every lot of every `city.json` building. An HQ
## stand-in's rect can reach over a city building's lot at its edge; that lot stays the city
## building's (cells first, then the HQ rects on the lots left).
static func lot_index(buildings: Array) -> Dictionary:
	var out := {}
	for hq_pass in [false, true]:
		for b: Dictionary in buildings:
			if bool(b["hq"]) != hq_pass:
				continue
			var c: Array = b["cell"]
			var entry := [b["bid"], int(c[0]), int(c[1])]
			for i in range(int(c[0]), int(c[0]) + int(c[2])):
				for j in range(int(c[1]), int(c[1]) + int(c[3])):
					if not out.has(Vector2i(i, j)):
						out[Vector2i(i, j)] = entry
	return out


## The bid under Site lot point `lot` (ruling O7): the building whose cell holds floor(lot);
## else the nearest by Chebyshev lot distance, ties by the cell's (i, j) ascending, within
## `reach_lots`; else "". Pure on its inputs.
static func site_bid(lot: Vector2, index: Dictionary, reach_lots: int) -> String:
	if not lot.is_finite():
		return ""
	var p := Vector2i(lot.floor())
	if index.has(p):
		return index[p][0]
	for d in range(1, reach_lots + 1):
		var best: Array = []
		for i in range(p.x - d, p.x + d + 1):
			for j in range(p.y - d, p.y + d + 1):
				if absi(i - p.x) != d and absi(j - p.y) != d:
					continue
				var e: Variant = index.get(Vector2i(i, j))
				if e != null and (best.is_empty() or e[1] < best[1] or e[1] == best[1] and e[2] < best[2]):
					best = e
		if not best.is_empty():
			return best[0]
	return ""


## Lot point `p` as a BU plan point [x, y] (x east = world X, y north = -world Z).
static func plan_point(p: Vector2, lot_bu: float, origin: Vector2) -> Array:
	return [(p.x - origin.x) * lot_bu, -(p.y - origin.y) * lot_bu]


# --- Canonical text ---------------------------------------------------------------------------

## `v` as canonical contract JSON (NA02_FIELDS section 1, ruling O12), ending in one LF.
## Byte-identical to tools/netrun_art/io.py `canonical_dumps`.
static func canonical(v: Variant) -> String:
	var out := PackedStringArray()
	_emit(v, 0, out)
	out.append("\n")
	return "".join(out)


## A float as fixed 1e-4 text: trailing zeros trimmed to at least one decimal, "0.0" for
## -0.0; NaN / Inf are refused (push_error, "0.0").
static func float_str(x: float) -> String:
	if is_nan(x) or is_inf(x):
		push_error("NetrunArtExport: NaN or Inf in a contract file.")
		return "0.0"
	var s := "%.4f" % (floorf(x * 1e4 + 0.5) / 1e4)  # half up first (spec 12.8 rule 1), as io.py round_half_up
	s = s.rstrip("0")
	if s.ends_with("."):
		s += "0"
	return "0.0" if s == "-0.0" else s


static func _emit(v: Variant, depth: int, out: PackedStringArray) -> void:
	match typeof(v):
		TYPE_NIL:
			out.append("null")
		TYPE_BOOL:
			out.append("true" if v else "false")
		TYPE_INT:
			if absi(v) > INT_LIMIT:
				push_error("NetrunArtExport: int %d outside +-2^53; write u64 as a decimal string." % v)
			out.append(str(v))
		TYPE_FLOAT:
			out.append(float_str(v))
		TYPE_STRING, TYPE_STRING_NAME:
			out.append(_quote(String(v)))
		TYPE_ARRAY:
			var a: Array = v
			if a.is_empty():
				out.append("[]")
				return
			out.append("[\n")
			var pad := " ".repeat(depth + 1)
			for i in a.size():
				out.append(pad)
				_emit(a[i], depth + 1, out)
				out.append(",\n" if i < a.size() - 1 else "\n")
			out.append(" ".repeat(depth) + "]")
		TYPE_DICTIONARY:
			var d: Dictionary = v
			if d.is_empty():
				out.append("{}")
				return
			var keys: Array = d.keys()
			keys.sort_custom(func(x: Variant, y: Variant) -> bool: return String(x) < String(y))
			out.append("{\n")
			var pad := " ".repeat(depth + 1)
			for i in keys.size():
				out.append(pad + _quote(String(keys[i])) + ": ")
				_emit(d[keys[i]], depth + 1, out)
				out.append(",\n" if i < keys.size() - 1 else "\n")
			out.append(" ".repeat(depth) + "}")
		_:
			push_error("NetrunArtExport: unsupported type %s in a contract file." % type_string(typeof(v)))
			out.append("null")


## A JSON string literal as io.py writes it: UTF-8 kept (ensure_ascii off), `"` `\` and
## \n \r \t \b \f escaped, other controls as \u00XX.
static func _quote(s: String) -> String:
	if not _needs_escape(s):
		return "\"" + s + "\""
	var out := "\""
	for i in s.length():
		var c := s.unicode_at(i)
		match c:
			0x22:
				out += "\\\""
			0x5c:
				out += "\\\\"
			0x0a:
				out += "\\n"
			0x0d:
				out += "\\r"
			0x09:
				out += "\\t"
			0x08:
				out += "\\b"
			0x0c:
				out += "\\f"
			_:
				out += "\\u%04x" % c if c < 0x20 else String.chr(c)
	return out + "\""


static func _needs_escape(s: String) -> bool:
	for i in s.length():
		var c := s.unicode_at(i)
		if c < 0x20 or c == 0x22 or c == 0x5c:
			return true
	return false


static func _sites(corp: CorporationData) -> Array[SiteData]:
	var out: Array[SiteData] = []
	if corp == null or corp.city_grid == null:
		return out
	for sd in corp.city_grid.sites:
		if sd != null:
			out.append(sd)
	out.sort_custom(func(x: SiteData, y: SiteData) -> bool: return String(x.id) < String(y.id))
	return out


static func _rect(r: Rect2i) -> Array:
	return [r.position.x, r.position.y, r.size.x, r.size.y]


static func _lot(v: Vector2i) -> Array:
	return [v.x, v.y]


static func _by_lot(x: Dictionary, y: Dictionary) -> bool:
	return x["lot"][0] < y["lot"][0] if x["lot"][0] != y["lot"][0] else x["lot"][1] < y["lot"][1]
