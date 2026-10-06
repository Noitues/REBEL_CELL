extends GutTest
## ART-7 7w (ART_BIBLE v2 §4.1, §4.6; round 38 transit v3, round 40 cars_lod): the netrun route
## on the unified 3D city. The cable router (45° / 90° turns only, streets crossed not ridden,
## crossings avoided, the rest hopped; deterministic), the route's cables from it (every link
## and entry run, ends on the nodes' lots, drawn from sticker to sticker), the route page on
## the 3D city at the NETRUN band (GRID VIEW at the Grid's, other pages on the 2D city), the
## see-through look the band holds, the player's camera (a view: no game state changes).
## Headless (the 3D city keeps its projection and placement; nothing renders).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const CFG := preload("res://content/config/city_config.tres")


func before_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art7_netrun_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _netrun() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	return scene


## A street row along lot x at j == `row` (every i).
static func _row_street(row: int) -> Callable:
	return func(_i: int, j: int) -> bool: return j == row


static func _no_street() -> Callable:
	return func(_i: int, _j: int) -> bool: return false


## True when every segment of `pts` (lot points) runs in one of the eight directions and no
## turn is sharper than 90°.
static func _octilinear(pts: PackedVector2Array) -> bool:
	var prev := Vector2.ZERO
	for k in pts.size() - 1:
		var d := pts[k + 1] - pts[k]
		if d.length() < 0.0001:
			return false
		var ang := rad_to_deg(d.angle())
		if absf(ang / 45.0 - roundf(ang / 45.0)) > 0.001:
			return false
		var dir := d.normalized()
		if k > 0 and dir.dot(prev) < -0.001:
			return false  # sharper than 90°
		prev = dir
	return true


## Lots of cable `pts` that run along street row `row` (lot units).
static func _riding(pts: PackedVector2Array, row: int) -> float:
	var out := 0.0
	for k in pts.size() - 1:
		var a := pts[k]
		var b := pts[k + 1]
		if is_equal_approx(a.y, b.y) and a.y > row and a.y < row + 1:
			out += absf(b.x - a.x)
	return out


# --- The router ---------------------------------------------------------------------------------

func test_cables_turn_only_by_45_or_90_degrees_and_end_on_their_points() -> void:
	var pairs := [{"a": Vector2(0.5, 0.5), "b": Vector2(9.5, 4.5)}, {"a": Vector2(3.5, 7.5), "b": Vector2(-4.5, 1.5)},
		{"a": Vector2(2.5, 2.5), "b": Vector2(2.5, 11.5)}]
	var out := RouteCableRouter.route_all(pairs, _row_street(5))
	assert_eq(out.size(), pairs.size())
	for k in out.size():
		var pts: PackedVector2Array = out[k]["points"]
		assert_true(pts[0].is_equal_approx(pairs[k]["a"]) and pts[pts.size() - 1].is_equal_approx(pairs[k]["b"]), "cable %d ends on its points" % k)
		assert_true(_octilinear(pts), "cable %d: straight runs, 45° / 90° turns only (%s)" % [k, pts])
	assert_eq(RouteCableRouter.turn_steps(0, 2), 2, "a 90° turn is two steps")
	assert_eq(RouteCableRouter.turn_steps(7, 1), 2, "turns wrap")


func test_cables_cross_streets_rather_than_ride_them() -> void:
	# Both ends on one long street: the cable leaves it for the blocks beside it.
	var along := RouteCableRouter.route_all([{"a": Vector2(0.5, 5.5), "b": Vector2(14.5, 5.5)}], _row_street(5))
	var pts: PackedVector2Array = along[0]["points"]
	assert_lt(_riding(pts, 5), 14.0 * 0.5, "most of the run is off the street (%s)" % pts)
	# Across the street: it crosses it, it does not run along it.
	var across := RouteCableRouter.route_all([{"a": Vector2(2.5, 1.5), "b": Vector2(6.5, 9.5)}], _row_street(5))
	assert_lt(_riding(across[0]["points"], 5), 1.0, "a crossing rides at most a step (%s)" % across[0]["points"])


func test_crossings_are_avoided_and_the_rest_hopped() -> void:
	# A detour exists: the second cable goes round the first (no hop).
	var round_it := RouteCableRouter.route_all([{"a": Vector2(4.5, 4.5), "b": Vector2(6.5, 4.5)},
		{"a": Vector2(5.5, 2.5), "b": Vector2(5.5, 6.5)}], _no_street())
	assert_true(RouteCableRouter.crossings(round_it[1]["points"], round_it[0]["points"]).is_empty(),
		"a crossing that can be avoided is avoided (%s)" % round_it[1]["points"])
	assert_true(round_it[1]["hops"].is_empty())
	# No way round inside the search box: the later cable hops the earlier one, once.
	var wall := RouteCableRouter.route_all([{"a": Vector2(-12.5, 5.5), "b": Vector2(24.5, 5.5)},
		{"a": Vector2(5.5, 0.5), "b": Vector2(5.5, 10.5)}], _no_street())
	assert_true(wall[0]["hops"].is_empty(), "the first cable laid never hops")
	assert_eq(wall[1]["hops"].size(), 1, "the later cable bridges the earlier one with a hop")
	var hop: Dictionary = wall[1]["hops"][0]
	assert_almost_eq(Vector2(hop["at"]).y, 5.5, 0.01, "the hop sits on the crossing")


func test_routing_is_deterministic() -> void:
	var pairs := [{"a": Vector2(0.5, 0.5), "b": Vector2(7.5, 3.5)}, {"a": Vector2(7.5, 3.5), "b": Vector2(1.5, 8.5)},
		{"a": Vector2(0.5, 8.5), "b": Vector2(8.5, 0.5)}]
	var a := RouteCableRouter.route_all(pairs, _row_street(4))
	var b := RouteCableRouter.route_all(pairs, _row_street(4))
	assert_eq(a, b, "same city, same pairs: same cables and hops")


# --- The route on the 3D city -------------------------------------------------------------------

func test_the_route_page_is_the_3d_city_at_the_netrun_band() -> void:
	var scene := _netrun()
	await _frames()
	var bg: WireframeBackground = scene.background
	assert_true(bg.city3d, "the route page is on the unified 3D city")
	assert_true(bg.city.city3d)
	assert_eq(bg.city.band_lock, CityLod.Band.NETRUN, "it holds the NETRUN band")
	assert_not_null(scene.route_controls, "the player's camera is on the route")
	# GRID VIEW: the whole Grid, at the Grid's band.
	scene._grid_zoomed = true
	scene._show_map()
	await _frames()
	assert_eq(bg.city.band_lock, CityLod.Band.GRID, "GRID VIEW holds the Grid's band")
	scene._grid_zoomed = false
	scene._show_map()
	await _frames()
	# Another page (an event) keeps the 2D city.
	DemoSetup.open_event(RunManager.netrun, &"ev_leash_on_the_floor")
	scene._show_current()
	await _frames()
	assert_false(bg.city3d, "pages that have not moved keep the 2D city")
	assert_eq(bg.city.band_lock, -1)


## The 2D bake's stand-in silhouette (flat roof slabs) never draws over the 3D city: the route
## page turns the 3D city on after the page's first 2D frames.
func test_the_bake_silhouette_goes_when_the_3d_city_comes_on() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	holder.add_child(city)
	await _frames()
	var sil := city.get_node(^"CityView/CitySilhouette") as Control
	sil.visible = true  # what a 2D frame with no bake yet leaves
	city.city3d = true
	assert_false(sil.visible, "no 2D silhouette over the 3D city")


func test_the_netrun_band_is_see_through_at_any_zoom() -> void:
	for ortho in [60.0, 160.0, 440.0, 900.0]:
		assert_lte(CityLod.opacity(CFG, CityView3D.view_lod(CFG, ortho, CityLod.Band.NETRUN)), CFG.see_through_opacity + 0.0001,
			"NETRUN at ortho %d: see-through" % ortho)
		assert_almost_eq(CityLod.opacity(CFG, CityView3D.view_lod(CFG, ortho, CityLod.Band.GRID)), 1.0, 0.0001,
			"GRID at ortho %d: solid" % ortho)


func test_every_link_rides_its_routed_cable_from_sticker_to_sticker() -> void:
	var scene := _netrun()
	await _frames()
	var ov: RouteOverlay = scene.city_overlay
	var cs := ov.cables()
	assert_eq(cs.size(), ov.edges.size(), "one cable per link")
	for k in cs.size():
		var e: Dictionary = ov.edges[k]
		var pts: PackedVector2Array = cs[k]["points"]
		assert_true(pts[0].is_equal_approx(ov.cable_end(e["a"])) and pts[pts.size() - 1].is_equal_approx(ov.cable_end(e["b"])),
			"link %d runs from its node's lot to the other's" % k)
		assert_true(_octilinear(pts), "link %d: 45° / 90° turns only" % k)
		var px: PackedVector2Array = ov._route_px(k)
		assert_true(px[0].is_equal_approx(ov.icon_at(e["a"])) and px[px.size() - 1].is_equal_approx(ov.icon_at(e["b"])),
			"link %d is drawn sticker to sticker" % k)
		# Its ground run goes through the city's own projection (the 3D camera's).
		assert_true(px[1].is_equal_approx(ov.grid_point_local(pts[0])), "link %d leaves its node from the ground" % k)
	# The entry runs (the street to the first choices) are routed too.
	var nexts := 0
	for n in ov.nodes:
		if n.get("next", false):
			nexts += 1
	assert_eq(ov._entry_cables.size(), nexts, "an entry cable per first choice")


func test_the_route_camera_is_a_view() -> void:
	var scene := _netrun()
	await _frames()
	var s := RunManager.netrun
	var before := [s.run.current_node_id, s.run.visited.duplicate(), s.run.phase]
	var z0: float = scene.background.city.scale.x
	scene.route_controls.zoom_at(SCREEN.size * 0.5, -2.0)
	await _frames(1)
	assert_gt(scene.background.city.scale.x, z0, "the wheel zooms in")
	scene.route_controls.pan_by(Vector2(40, 0))
	await _frames(1)
	assert_eq([s.run.current_node_id, s.run.visited, s.run.phase], before, "the camera changes no game state")
