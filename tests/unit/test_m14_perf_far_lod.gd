extends GutTest
## M14 perf slice "HQ idle and combat far-LOD" (art director's approach): outside a view's keep
## rect the city draws at the far LOD (no shadow, no roof props) and, on the HQ idle, without
## its ink edges. The HQ idle keeps the network rect and its vignette at full quality; a fight's
## close-up keeps its subject block and the blocks round it. LOD choice is a pure function of
## the keep rect (CityLod.prism_far), the keep rect is snapped with hysteresis
## (CityLod.keep_next), and every threshold comes from city_config.tres.

const CONFIG := preload("res://content/config/city_config.tres")
const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
## A part of the city (chunks of the real layout), as test_city3d_model.
const PART := Rect2i(20, -4, 40, 40)

var cfg: CityConfig = CONFIG
var model: CityModel


func before_all() -> void:
	model = CityModel.build(cfg, 7, PART)


func after_each() -> void:
	if RunManager.save_slot == "gut_m14_perf_far_lod":
		RunManager.delete_save()
		DirAccess.remove_absolute(RunManager.profile_path())
		RunManager.save_slot = RunManager.DEFAULT_SLOT
		RunManager.reset()
		RunManager.scene_switching_enabled = true
		AudioDirector.muted = false


## The footprint box (world X/Z) of prism `n`.
func _box(n: int) -> Rect2:
	var poly: PackedVector2Array = model.prisms[n]["poly"]
	var r := Rect2(poly[0], Vector2.ZERO)
	for q in poly:
		r = r.expand(q)
	return r


## The world X/Z box of the model's prisms.
func _city_box() -> Rect2:
	var r := _box(0)
	for n in model.prisms.size():
		r = r.merge(_box(n))
	return r


func _all() -> PackedInt32Array:
	var idx := PackedInt32Array()
	for n in model.prisms.size():
		idx.append(n)
	return idx


func test_buildings_inside_the_keep_rect_are_always_full_lod_and_outside_are_far() -> void:
	var city := _city_box()
	# A network rect in the middle of the part (a quarter of its width), as the HQ idle gives it.
	var keep := Rect2(city.get_center() - city.size * 0.125, city.size * 0.25)
	var lean := CityLod.lean_of(cfg.pitch_deg)
	var held := CityLod.keep_next(cfg, Rect2(), keep)
	assert_true(held.encloses(keep), "the held rect holds the asked one")
	var inside := 0
	var far := 0
	for n in model.prisms.size():
		var is_far := CityLod.prism_far(cfg, model.prisms[n], held, lean)
		if _box(n).intersects(keep, true):
			inside += 1
			assert_false(is_far, "prism %d stands in the network rect: full LOD" % n)
		if is_far:
			far += 1
			var top := float(model.prisms[n]["y0"]) + float(model.prisms[n]["h"])
			assert_false(_box(n).grow(top * lean).intersects(keep, true), "a far prism %d never reaches the rect on screen" % n)
	assert_gt(inside, 20, "buildings stand in the rect")
	assert_gt(far, model.prisms.size() / 2, "most of the city outside it takes the far LOD")
	# The lean: a tall building just outside the rect (its foot below it) leans into it on screen.
	var top_far := -1
	for n in model.prisms.size():
		var top := float(model.prisms[n]["y0"]) + float(model.prisms[n]["h"])
		if not _box(n).intersects(held, true) and _box(n).grow(top * lean).intersects(held, true):
			top_far = n
			break
	assert_gt(top_far, -1, "a building leaning into the rect exists in the part")
	assert_false(CityLod.prism_far(cfg, model.prisms[top_far], held, lean), "it keeps full LOD (its top is in the rect)")
	var split := CityLod.split_far(cfg, model.prisms, _all(), held, lean)
	assert_eq((split["near"] as PackedInt32Array).size() + (split["far"] as PackedInt32Array).size(), model.prisms.size(), "every prism once")
	assert_eq((split["far"] as PackedInt32Array).size(), far)
	# The far LOD level never goes finer than the view's own LOD.
	assert_eq(CityLod.far_level(cfg, 0), cfg.far_lod_level)
	assert_eq(CityLod.far_level(cfg, 2), maxi(2, cfg.far_lod_level))
	# No keep rect: everything full (the far LOD is only where a page asks for it).
	for n in [0, model.prisms.size() / 2, model.prisms.size() - 1]:
		assert_false(CityLod.prism_far(cfg, model.prisms[n], Rect2(), lean), "no keep rect: full LOD")


func test_the_hq_idles_keep_rect_is_the_network_rect_and_its_vignette() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_m14_perf_far_lod"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"firewall_relay", &"safehouse"]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	c.pending_raids.clear()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for i in 6:
		await get_tree().process_frame
	var dim: Dictionary = hq.hq_map_dim()
	assert_false(dim.is_empty(), "the HQ idle has a network rect")
	var keep: Rect2 = hq.far_lod_rect()
	var look := UiScrimPools.LOOK
	var k := hq.get_viewport_rect().size.y / look.reference_height
	var grow := (look.map_dim_margin_px + look.map_dim_feather_px + cfg.far_lod_pad_px) * k
	assert_almost_eq(keep.position, (dim["rect"] as Rect2).position - Vector2(grow, grow), Vector2(0.01, 0.01), "the rect grown by the vignette and the pad (config)")
	assert_almost_eq(keep.size, (dim["rect"] as Rect2).size + Vector2(grow, grow) * 2.0, Vector2(0.01, 0.01))
	# The network's nodes and the whole vignette lie inside it.
	for id in c.grid.claimed_ids():
		var r: Rect2 = hq._map_node_rect(id)
		if r.has_area():
			assert_true(keep.encloses(r), "%s's marker in the keep rect" % id)
	assert_true(keep.encloses((dim["rect"] as Rect2).grow((look.map_dim_margin_px + look.map_dim_feather_px) * k)), "the vignette's falloff inside")
	assert_true(hq.wireframe.city.far_lod_source.is_valid(), "the HQ's city reads it")
	# The raid setup is a raid view: full quality everywhere (no keep rect).
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	hq.show_raid()
	for i in 2:
		await get_tree().process_frame
	assert_false(hq.far_lod_rect().has_area(), "no far LOD off the idle")


func test_the_hq_rect_maps_onto_the_ground_under_the_view() -> void:
	var cam := CityIsoCamera.make(cfg, Vector3(40.0, 0.0, -20.0), 640.0, Vector2(1920, 1080))
	var px := Rect2(400, 200, 600, 400)
	var g := NeonCity.ground_rect(cam, px)
	for p: Vector2 in [px.position, px.end, px.get_center()]:
		var w := cam.unproject(p, 0.0)
		assert_true(g.grow(0.01).has_point(Vector2(w.x, w.z)), "the ground under %s is in the rect" % p)
	# Every ground point of the rect projects back inside the screen rect's box or its hull.
	var back := cam.project(Vector3(g.get_center().x, 0.0, g.get_center().y))
	assert_almost_eq(back, px.get_center(), Vector2(1.0, 1.0), "centre to centre")


func test_the_combat_target_building_and_its_neighbours_are_full_lod() -> void:
	var cam := CityIsoCamera.make(cfg, Vector3.ZERO, 200.0, Vector2(1142, 640))
	cam.fov_deg = cfg.backdrop_close_fov_deg
	# The subject: a tall prism in the middle of the part, as BackdropCatalog.site_shot measures it.
	var city := _city_box()
	var best := 0
	var best_d := INF
	for n in model.prisms.size():
		var d := _box(n).get_center().distance_to(city.get_center())
		if d < best_d:
			best_d = d
			best = n
	var b := _box(best)
	var top := float(model.prisms[best]["y0"]) + float(model.prisms[best]["h"])
	var shot := {"subject": AABB(Vector3(b.position.x, 0.0, b.position.y), Vector3(b.size.x, top, b.size.y)), "camera": cam}
	var keep := CombatBackdrop.far_keep(cfg, shot)
	assert_almost_eq(keep.size, b.size + Vector2.ONE * cfg.backdrop_far_lod_reach_bu * 2.0, Vector2(0.01, 0.01), "the subject grown by the config's reach")
	var held := CityLod.keep_next(cfg, Rect2(), keep)
	assert_false(CityLod.prism_far(cfg, model.prisms[best], held, 0.0), "the target building is full LOD")
	var near := 0
	var far := 0
	for n in model.prisms.size():
		var c := _box(n).get_center()
		if b.grow(cfg.backdrop_far_lod_reach_bu).has_point(c):
			near += 1
			assert_false(CityLod.prism_far(cfg, model.prisms[n], held, 0.0), "neighbour %d within the reach is full LOD" % n)
		elif not _box(n).intersects(held, true):
			far += 1
			assert_true(CityLod.prism_far(cfg, model.prisms[n], held, 0.0), "distant block %d is far LOD" % n)
	assert_gt(near, 5, "neighbours round the subject")
	assert_gt(far, 50, "distant blocks take the far LOD")
	# An orthographic or subject-less shot keeps everything full.
	var ortho := CityIsoCamera.make(cfg, Vector3.ZERO, 200.0, Vector2(1142, 640))
	assert_false(CombatBackdrop.far_keep(cfg, {"subject": shot["subject"], "camera": ortho}).has_area(), "ortho: no far LOD")
	assert_false(CombatBackdrop.far_keep(cfg, {"camera": cam}).has_area(), "no subject: no far LOD")


func test_lod_choice_is_deterministic_and_stable_across_frames() -> void:
	var city := _city_box()
	var raw := Rect2(city.get_center() - Vector2(60, 40), Vector2(120, 80))
	var lean := CityLod.lean_of(cfg.pitch_deg)
	var held := CityLod.keep_next(cfg, Rect2(), raw)
	var first := CityLod.split_far(cfg, model.prisms, _all(), held, lean)
	# Frame after frame the same rect, read with a drift's or a pan's float noise, holds.
	var drift := [Vector2(0.3, -0.2), Vector2(-2.5, 1.7), Vector2(4.9, -3.1), Vector2(0.0001, 0.0)]
	for d: Vector2 in drift:
		var next := CityLod.keep_next(cfg, held, Rect2(raw.position + d, raw.size))
		assert_eq(next, held, "a drift of %s keeps the held rect (no popping)" % d)
	var again := CityLod.split_far(cfg, model.prisms, _all(), held, lean)
	assert_eq(again["far"], first["far"], "same rect, same far set")
	assert_eq(CityView3D.far_signature(again["far"]), CityView3D.far_signature(first["far"]), "same signature: no chunk rebuilds")
	assert_eq(CityView3D.far_signature(PackedInt32Array()), 0)
	# Snapped to the grid, the same world rect read twice snaps the same.
	var s := CityLod.snap_keep(cfg, raw)
	assert_eq(CityLod.snap_keep(cfg, Rect2(raw.position + Vector2(0.001, -0.001), raw.size)), s, "noise below a step snaps alike")
	assert_true(s.encloses(raw), "snapped outward")
	assert_almost_eq(fmod(absf(s.position.x), cfg.far_lod_snap_bu), 0.0, 0.0001, "on the grid")
	# A real move (the page frames another place) takes the new rect.
	var moved := Rect2(raw.position + Vector2(200, 0), raw.size)
	assert_true(CityLod.keep_next(cfg, held, moved).encloses(moved), "a moved rect is taken")
	assert_false(CityLod.keep_next(cfg, held, Rect2()).has_area(), "no rect: off")


func test_the_ink_runs_in_the_keep_box_and_fades_past_it() -> void:
	var v: CityView3D = autofree(CityView3D.new())
	v.size = Vector2i(1920, 1080)
	var box := Rect2(400, 200, 600, 400)
	v.set_ink_keep(box)
	assert_eq(v.ink_keep, box if cfg.far_lod_skip_ink else Rect2(), "the box (config far_lod_skip_ink)")
	if not cfg.far_lod_skip_ink:
		return
	var feather := cfg.far_ink_feather_share * 1080.0
	assert_almost_eq(v.ink_weight(box.get_center()), 1.0, 0.0001, "full ink in the network rect")
	assert_almost_eq(v.ink_weight(box.end), 1.0, 0.0001, "and on its edge")
	assert_almost_eq(v.ink_weight(box.end + Vector2(feather + 1.0, 0.0)), 0.0, 0.0001, "none past the feather")
	var mid := v.ink_weight(Vector2(box.end.x + feather * 0.5, box.get_center().y))
	assert_true(mid > 0.0 and mid < 1.0, "a fade, not a seam (%f)" % mid)
	v.set_ink_keep(Rect2())
	assert_almost_eq(v.ink_weight(Vector2(5000, 5000)), 1.0, 0.0001, "no box: ink everywhere")


func test_the_flow_dashes_are_batched_by_default() -> void:
	# The same picture is checked windowed (perf_pack flow_diff_hq); here the switch's default.
	var o: CityMapOverlay = autofree(CityMapOverlay.new())
	assert_true(o.flow_batched, "the dashes draw as one multiline per edge")
	assert_true(o.flow_shader, "the dashes and chevrons are a still mesh the shader crawls")


## The CPU path's chevron spacing round corners (CityMapOverlay._chevrons): the carry into each
## segment, segment by segment.
func _cpu_carries(phase: float, step: float, lengths: Array[float]) -> Array[float]:
	var out: Array[float] = []
	var carry := phase
	for length in lengths:
		out.append(carry)
		var n := ceili(maxf(0.0, length - carry) / step)
		carry = maxf(0.0, carry + n * step - length)
	return out


func test_the_flow_mesh_slides_dashes_and_chevrons_as_the_cpu_lays_them() -> void:
	# The shader's shift per track (CityFlowMesh.shift_of) is the CPU's phase and carry, so the
	# still mesh slid by it puts every dash and chevron where the CPU drew it (the picture: 0
	# pixels apart in perf_pack flow_diff_hq, windowed).
	var step := 34.0 * 0.8
	var lengths: Array[float] = [100.0, 12.5, 73.3, 0.4, 160.0]
	for phase: float in [0.0, 5.5, 15.9, 27.1]:
		var carries := _cpu_carries(phase, step, lengths)
		var before := 0.0
		for j in lengths.size():
			assert_almost_eq(CityFlowMesh.shift_of(phase, step, -before, 1.0), carries[j], 0.001,
				"phase %.1f: segment %d's chevrons start where the CPU's carry put them" % [phase, j])
			before += lengths[j]
		assert_almost_eq(CityFlowMesh.shift_of(phase, 16.0, 0.0, 1.0), fmod(phase, 16.0), 0.0001, "the dashes' phase")
		assert_eq(CityFlowMesh.shift_of(phase, 16.0, 0.0, 0.0), 0.0, "a still route's dashes do not crawl")


func test_the_flow_mesh_lays_each_element_once_on_its_track() -> void:
	var m := CityFlowMesh.new()
	var pts := PackedVector2Array([Vector2(0, 0), Vector2(100, 0), Vector2(100, 70)])
	var edges: Array[Dictionary] = [{"pts": pts, "color": Color.RED, "width": 4.0, "flow": true, "dashed": true, "arrows": true}]
	assert_true(m.build(edges, 9.0, 16.0, 34.0, 6.0, 1.0, 400), "fits")
	assert_eq(m.track_count, 4, "two segments, a dash track and a chevron track each")
	var arrays := m.mesh.surface_get_arrays(0)
	var verts: PackedVector2Array = arrays[Mesh.ARRAY_VERTEX]
	# Dashes: ceil(100/16) + ceil(70/16) quads; chevrons: ceil(100/34) + ceil(70/34), two strips of 6.
	assert_eq(verts.size(), (7 + 5) * 4 + (3 + 3) * 2 * 6, "every dash a quad, every chevron its keyline and colour strips")
	assert_not_null(m.material, "the crawl shader")
	assert_true(m.build([] as Array[Dictionary], 9.0, 16.0, 34.0, 6.0, 1.0, 400), "nothing to lay")
	assert_null(m.mesh, "no mesh")


func test_the_chevron_strip_keeps_its_width_round_the_tip() -> void:
	var wing := PackedVector2Array([Vector2(-6, 6), Vector2(6, 0), Vector2(-6, -6)])
	var s := CityFlowMesh.polyline_strip(wing, 4.0)
	assert_eq(s.size(), 6, "two vertices per point")
	var n0 := (wing[1] - wing[0]).normalized().orthogonal()
	assert_almost_eq((s[0] - wing[0]).dot(n0), 2.0, 0.0001, "the start squares to its segment, half the width out")
	# The tip's mitre: on the bisector, the strip's edge half the width off each segment.
	assert_almost_eq((s[2] - wing[1]).dot(n0), 2.0, 0.0001, "the mitre keeps the width")
	var m := CityFlowMesh.polyline_strip(wing, 4.0, -1.0)
	assert_almost_eq(m[0], s[1], Vector2(0.0001, 0.0001), "a mirrored frame swaps each pair (Godot's order)")


func test_the_wheel_radius_memo_follows_its_inputs() -> void:
	var v: WheelView = autofree(WheelView.new())
	v.size = Vector2(900, 700)
	assert_almost_eq(v._radius(), v._radius_fit(), 0.0001, "the memo is the fit")
	v.size = Vector2(600, 500)
	assert_almost_eq(v._radius(), v._radius_fit(), 0.0001, "a new size: fitted again")
	v.hud_results = not v.hud_results
	assert_almost_eq(v._radius(), v._radius_fit(), 0.0001, "the HUD's nudge room: fitted again")
	var was := Settings.text_scale
	Settings.text_scale = 1.6
	assert_almost_eq(v._radius(), v._radius_fit(), 0.0001, "a new text scale: fitted again")
	Settings.text_scale = was


func test_the_hud_buttons_redraw_only_when_what_they_draw_changes() -> void:
	var layer: HudWheelLayer = add_child_autofree(HudWheelLayer.new())
	var a := layer.draw_signature()
	assert_eq(layer.draw_signature(), a, "nothing changed: no redraw")


func test_the_raid_routes_relay_only_when_what_they_show_changes() -> void:
	var layer := RaidRouteLayer.new()
	autofree(layer)
	var a := layer.lay_signature()
	assert_eq(layer.lay_signature(), a, "the same state: the same signature (no relay at rest)")
	layer.write_u = 0.5
	assert_ne(layer.lay_signature(), a, "the write-on moves: relay")
	var b := layer.lay_signature()
	layer.routes = [[&"a", &"b"]] as Array[Array]
	assert_ne(layer.lay_signature(), b, "new routes: relay")


func test_a_pencil_mark_set_to_the_same_values_keeps_its_strokes() -> void:
	var m: GreasePencilMark = autofree(GreasePencilMark.new())
	m.add_stroke(PackedVector2Array([Vector2(0, 0), Vector2(100, 0), Vector2(100, 50)]))
	m.progress = 0.5
	var lines := m.find_children("*", "Line2D", true, false)
	assert_false(lines.is_empty(), "a stroke")
	var before: PackedVector2Array = (lines[0] as Line2D).points
	m.progress = 0.5
	m.wiped_share = 0.0
	m.ink = m.ink
	assert_eq((lines[0] as Line2D).points, before, "unchanged values: the same stroke")
	m.progress = 1.0
	assert_ne((lines[0] as Line2D).points, before, "a new progress: the stroke follows")


func test_the_thresholds_come_from_the_config() -> void:
	# The shipped values are in city_config.tres (read, not hardcoded).
	var text := FileAccess.get_file_as_string(CONFIG.resource_path)
	for key in ["far_lod_on", "far_lod_level", "far_lod_shadows", "far_lod_snap_bu", "far_lod_pad_px", "far_lod_skip_ink", "far_ink_feather_share",
			"backdrop_far_lod_reach_bu"]:
		assert_string_contains(text, key + " = ", "%s is set in city_config.tres" % key)
	# Changing a copy changes the rule (the loaded resource is never written).
	var c2 := CONFIG.duplicate() as CityConfig
	c2.far_lod_level = 1
	assert_eq(CityLod.far_level(c2, 0), 1, "far_lod_level read")
	c2.far_lod_snap_bu = 50.0
	assert_almost_eq(fmod(absf(CityLod.snap_keep(c2, Rect2(3, 7, 10, 10)).position.x), 50.0), 0.0, 0.0001, "far_lod_snap_bu read")
	c2.backdrop_far_lod_reach_bu = 10.0
	var cam := CityIsoCamera.make(c2, Vector3.ZERO, 200.0, Vector2(1142, 640))
	cam.fov_deg = 40.0
	var keep := CombatBackdrop.far_keep(c2, {"subject": AABB(Vector3.ZERO, Vector3(5, 5, 5)), "camera": cam})
	assert_almost_eq(keep.size, Vector2(25, 25), Vector2(0.001, 0.001), "backdrop_far_lod_reach_bu read")
	c2.far_lod_on = false
	assert_false(CityLod.prism_far(c2, model.prisms[0], Rect2(1e6, 1e6, 1, 1), 0.0), "far_lod_on off: full LOD everywhere")
	assert_eq(CONFIG.far_lod_level, 2, "the shipped far LOD is the plain extrusion")
	assert_false(CONFIG.far_lod_shadows, "far buildings cast no shadow")
