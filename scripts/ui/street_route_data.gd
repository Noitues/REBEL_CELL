class_name StreetRouteData
extends RefCounted
## NA-23: the data the street netrun view draws from: the laid-out city (`city.json`), the corporation's net, the run's graph
## (`run_graph.json`) and the street derive v2 with its camera poses and occlusion cones, all from the game's own city
## model and the started netrun (the NA-02 exporter and the NA-21 twins). View-side and read-only: it changes no game state
## and draws no random number. A failed derive leaves `error` set (the caller keeps the old route page).

## The derive of the run's Site (`NetrunArtDeriver.derive_street`), `{}` after an error.
var derive: Dictionary = {}
var city: Dictionary = {}
var net: Dictionary = {}
var run_graph: Dictionary = {}
## The pose-builder context (rooms, occluder boxes).
var ctx: Dictionary = {}
var error: String = ""
## Building id -> prism indices of the model (`model.prisms`), by the exporter's id rule.
var bid_prisms: Dictionary = {}
## The run graph's node ids (as in `run_graph.json`).
var node_ids: Array = []

static var _city_cache: Dictionary = {}
var _states: Dictionary = {}


## Builds the data for the run of `session` on `model` (the game's full city). `site_points` are the corporation's Site layout
## points (`CityLayout.site_points`). Check `error` before use.
static func build(session: NetrunSession, model: CityModel, cfg: CityConfig, site_points: Dictionary) -> StreetRouteData:
	var d := StreetRouteData.new()
	var key := "%s|%d" % [cfg.resource_path, model.city_seed]
	if not _city_cache.has(key):
		var cj := NetrunArtExport.city_json(model.city_seed, cfg.lot_bu, cfg.district_centre, model.prisms, model.streets, model.plazas, model.hqs)
		_city_cache[key] = {"city": cj, "index": NetrunArtExport.lot_index(cj["buildings"])}
	var cached: Dictionary = _city_cache[key]
	d.city = cached["city"]
	var res := NetrunArtExport.export_run(session, d.city, cached["index"], site_points, cfg.art_site_bid_reach_lots)
	if String(res["error"]) != "":
		d.error = String(res["error"])
		return d
	var files: Dictionary = res["files"]
	var net: Dictionary = JSON.parse_string(files["net.json"])
	var rg: Dictionary = JSON.parse_string(files["run_graph.json"])
	var rid := NetrunArtExport.run_id(session.run)
	var partial := NetrunArtDeriver.game_partial(str(d.city["layout_seed"]), rid, "street", [])
	d.net = net
	d.run_graph = rg
	d._derive_from(String(session.run.site_id), partial)
	if d.error == "":
		d.bid_prisms = bid_index(model.prisms)
	return d


## The data from its parts (the exporter's `city`, `net`, `run_graph` as parsed JSON; the Site id; the game's partial derive file):
## the derive, the pose context and the node ids. Tests build it from the NA-21 fixtures. `error` is set when the derive fails.
static func from_parts(p_city: Dictionary, p_net: Dictionary, p_run_graph: Dictionary, site: String, partial: Dictionary = {}) -> StreetRouteData:
	var d := StreetRouteData.new()
	d.city = p_city
	d.net = p_net
	d.run_graph = p_run_graph
	d._derive_from(site, partial)
	return d


func _derive_from(site: String, partial: Dictionary) -> void:
	derive = NetrunArtDeriver.derive_street(city, net, run_graph, site, partial)
	if derive.has("error"):
		error = String(derive["error"])
		derive = {}
		return
	ctx = NetrunPoseBuilder.make_ctx(derive, city, run_graph, net)
	if ctx.has("error"):
		error = String(ctx["error"])
		return
	for n: Dictionary in run_graph["nodes"]:
		node_ids.append(String(n["id"]))



## Building id -> PackedInt32Array of prism indices (the exporter's id rule: the cell's origin lot, `hq:<terr>` for an HQ).
static func bid_index(prisms: Array) -> Dictionary:
	var out: Dictionary = {}
	for i in prisms.size():
		var pr: Dictionary = prisms[i]
		var cell: Rect2i = pr["cell"]
		var bid := "hq:%s" % pr["terr"] if bool(pr.get("hq", false)) else "%d:%d" % [cell.position.x, cell.position.y]
		var list: PackedInt32Array = out.get(bid, PackedInt32Array())
		list.append(i)
		out[bid] = list
	return out


## The derive's rooms by node id.
func rooms() -> Dictionary:
	return derive["rooms"]


## The route building ids (never occluders).
func route_bids() -> Array:
	var out: Array = []
	for r: Dictionary in rooms().values():
		if not out.has(r["bld"]):
			out.append(r["bld"])
	IdSort.sort_ids(out)
	return out


## Node ids ahead of `current` ("" = at the street, before the first layer): the options.
func options_after(current: String) -> Array:
	return NetrunPoseBuilder.successors(run_graph, current)


## The street OVERVIEW state: `{pose: NetrunPose, rec: Dictionary}` (the record holds `occlusion`, `zoom_detail`).
func overview_state() -> Dictionary:
	if not _states.has("ov"):
		var ids: Array = rooms().keys()
		IdSort.sort_ids(ids)
		var pose := NetrunPose.from_json(derive["overview"])
		_states["ov"] = {"pose": pose, "rec": NetrunPoseBuilder.state_record(ctx, pose, ids)}
	return _states["ov"]


## The DECISION state on `current` with its `options`: `{pose, rec, ids}` (`ids` = current + options).
func decision_state(current: String, options: Array) -> Dictionary:
	var key := "dec|%s|%s" % [current, ",".join(PackedStringArray(options))]
	if not _states.has(key):
		var pose := NetrunPoseBuilder.decision_pose(ctx, current, options)
		var ids: Array = []
		if current != "":
			ids.append(current)
		ids.append_array(options)
		_states[key] = {"pose": pose, "rec": NetrunPoseBuilder.state_record(ctx, pose, ids, true), "ids": ids}
	return _states[key]


## The HOVER state on `node` from the DECISION state `dec`: `{pose, rec}`.
func hover_state(dec: Dictionary, node: String) -> Dictionary:
	var key := "hov|%s|%s" % [JSON.stringify(dec["pose"].to_json()), node]
	if not _states.has(key):
		var pose := NetrunPoseBuilder.hover_pose(ctx, dec["pose"], node)
		_states[key] = {"pose": pose, "rec": NetrunPoseBuilder.state_record(ctx, pose, dec["ids"], true)}
	return _states[key]


## NA-25: the HQ page's camera as a perspective pose, the dive's first frame (PIPELINE_SPEC 6.3); null when the run has none
## (an HQ run enters through its compound, not the street dive).
func hq_pose() -> NetrunPose:
	return ctx.get("hq") as NetrunPose
