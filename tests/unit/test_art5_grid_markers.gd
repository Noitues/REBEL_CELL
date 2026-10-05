extends GutTest
## ART-5 5d: the City Grid's Site markers v4 (bible §4.5): the marker is a pure function of
## the campaign state; Exploit badges on T2 Sites with the tag on hover; DOWN = the white
## bolt over a greyed marker; TAKEN = the SEIZURE NOTICE slip; fight-won lights (D17); the
## v4 map key in plain words, every entry apart in greyscale; the hidden-nodes rule with
## SHOW ALL; the projection seam and the label placement run headless on the spike camera;
## a Site that can't be run says why (Group 1 naive audit P2).

const HQ := "res://scenes/hq/hq_scene.tscn"
const CITY_CONFIG := preload("res://content/config/city_config.tres")
const CITY_SEED := 7
## Lots of city kept round the Sites for the headless model.
const MODEL_MARGIN := 6
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const SCREEN := Rect2(0, 0, 1280, 720)
const VIEW := Vector2(1920, 1080)
## A label's size at text scale 1.0 (px) for the headless placement sweep.
const LABEL_BOX := Vector2(84, 14)
const SETTLE := 12

var _text_scale_before: float = 1.0
var _legend_before: bool = true


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_legend_before = Settings.map_legend


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art5_markers"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	if Settings.map_legend != _legend_before:
		Settings.set_map_legend(_legend_before)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _open_all() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10


func _specs(c: CampaignState, corp: CorporationData) -> Dictionary:
	var open := {}
	for s in CampaignRules.launchable_sites(c, corp, RunManager.config()):
		open[s.id] = true
	var out := {}
	for sd in corp.city_grid.sites:
		if sd != null:
			out[sd.id] = SiteMarker.spec_for(c, corp.id, sd, open.has(sd.id))
	return out


func _first(corp: CorporationData, pred: Callable) -> SiteData:
	for sd in corp.city_grid.sites:
		if sd != null and pred.call(sd):
			return sd
	return null


# --- The marker is the state ------------------------------------------------------------

func test_each_layer_answers_its_question_from_the_state() -> void:
	_open_all()
	var c := RunManager.new_campaign(1, &"meridian")
	var corp := RunManager.corporation
	var specs := _specs(c, corp)
	var home: Dictionary = specs[c.grid.home_site_id]
	assert_eq(home["kind"], SiteMarker.KIND_CORE, "CORE: the heart")
	assert_eq(home["avail"], SiteMarker.AV_YOURS, "CORE: lime ring")
	assert_eq(SiteMarker.pip_count(home), 0, "CORE: no pips")
	var open := RunManager.launchable_sites()
	assert_false(open.is_empty())
	var nxt: Dictionary = specs[open[0].id]
	assert_eq(nxt["avail"], SiteMarker.AV_NEXT, "selectable: orange ring")
	assert_eq(SiteMarker.ring_color(nxt), Palette.RING_AVAILABLE)
	assert_true(nxt["pinned"], "selectable Sites always show")
	var far := _first(corp, func(sd: SiteData) -> bool: return specs[sd.id]["kind"] == SiteMarker.KIND_SITE and specs[sd.id]["avail"] == SiteMarker.AV_NOT_YET)
	assert_not_null(far)
	assert_false(specs[far.id]["pinned"], "a regular Site not selectable is hidden by default")
	assert_eq(SiteMarker.ring_color(specs[far.id]), Palette.RING_UNAVAILABLE, "not yet: white ring")
	var ex := _first(corp, func(sd: SiteData) -> bool: return sd.objective == RC.SiteObjective.EXPLOIT)
	var exs: Dictionary = specs[ex.id]
	assert_eq(exs["kind"], SiteMarker.KIND_EXPLOIT, "Exploit Site: the gold keyring")
	assert_eq(ex.tier, 2, "Exploits sit on T2 Sites (GDD 4.1)")
	assert_eq(int(exs["exploit"]), int(ex.exploit_type), "its type sub-badge")
	assert_true(exs["pinned"], "Exploit Sites are pinned")
	var heat := _first(corp, func(sd: SiteData) -> bool: return sd.objective == RC.SiteObjective.HEAT_REDUCTION)
	assert_eq(specs[heat.id]["kind"], SiteMarker.KIND_HEAT, "Heat objective: the flame")
	var boss := _first(corp, func(sd: SiteData) -> bool: return sd.objective == RC.SiteObjective.CENTRAL_SERVER)
	assert_eq(specs[boss.id]["kind"], SiteMarker.KIND_CENTRAL_SERVER, "the boss: TARGET")
	assert_eq(SiteMarker.pip_count(specs[boss.id]), 0, "the boss has no pips")
	# Cleared, claimed, DOWN, TAKEN (the state written straight in: the marker only reads it).
	var a := open[0].id
	c.grid.sites[a]["status"] = GridState.SiteStatus.CLEARED
	var cl := SiteMarker.spec_for(c, corp.id, open[0], true)
	assert_eq(cl["status"], SiteMarker.ST_CLEARED)
	assert_eq(cl["avail"], SiteMarker.AV_YOURS, "visited: lime ring")
	assert_true(cl["won"], "a fight won there")
	c.grid.sites[a]["status"] = GridState.SiteStatus.CLAIMED
	c.grid.sites[a]["condition"] = GridState.Condition.DOWN
	var dn := SiteMarker.spec_for(c, corp.id, open[0], true)
	assert_eq(dn["status"], SiteMarker.ST_DOWN, "a claimed node at 0 integrity is DOWN")
	assert_false(dn["won"], "DOWN: no power, its lights go dark")
	c.grid.sites[a]["status"] = GridState.SiteStatus.TAKEN
	var tk := SiteMarker.spec_for(c, corp.id, open[0], true)
	assert_eq(tk["status"], SiteMarker.ST_TAKEN)
	assert_eq(tk["avail"], SiteMarker.AV_NEXT, "orange ring while a Reclaim run is possible")
	assert_eq(SiteMarker.pip_count(tk), open[0].tier, "the slip keeps its tier pips")
	assert_eq(SiteMarker.spec_for(c, corp.id, open[0], true), tk, "same state, same marker")


func test_the_exploit_badge_reads_its_type_from_the_glyph_atlas_and_its_tag_from_content() -> void:
	var t := GlyphIcon.table()
	for type in [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]:
		var glyph: StringName = t.ids.get(GlyphTableData.key_for_exploit(type), GlyphTableData.PENDING)
		assert_ne(glyph, GlyphTableData.PENDING, "%s has its own glyph" % RC.ExploitType.keys()[type])
		assert_true(t.cell_region(glyph).has_area(), "in the atlas")
	_open_all()
	RunManager.new_campaign(1, &"meridian")
	var tag := SiteMarker.exploit_tag(RunManager.corporation, RC.ExploitType.BREACH)
	assert_eq(tag["category"], "BREACH")
	assert_eq(tag["name"], "CUSTOMS OVERRIDE KEYS", "Meridian's Breach item")
	assert_ne(String(tag["effect"]), "", "what it does at the breach")
	var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, [], &"", true)
	var tagged := 0
	for n in g["nodes"]:
		if n.has("exploit_tag"):
			tagged += 1
			assert_string_starts_with(String(n["tip"]), "%s // " % n["exploit_tag"]["category"], "the hover leads with the tag")
	assert_eq(tagged, 3, "the three Exploit Sites carry their tag")


func test_v4_graph_depowers_links_to_taken_and_down_nodes_and_shows_locked_links() -> void:
	_open_all()
	var c := RunManager.new_campaign(1, &"meridian")
	var corp := RunManager.corporation
	var first: StringName = corp.city_grid.get_site(c.grid.home_site_id).links[0]
	c.grid.sites[first]["status"] = GridState.SiteStatus.TAKEN
	var g := CityLayout.grid_graph(c, corp, [], &"", true)
	var dead := 0
	var locked := 0
	for e in g["edges"]:
		if bool(e.get("depowered", false)):
			dead += 1
			assert_true(e["a"] == first or e["b"] == first, "only links to the TAKEN node")
			assert_false(bool(e["flow"]), "no packets run on it")
		if bool(e.get("locked", false)):
			locked += 1
	assert_gt(dead, 0, "the TAKEN node's links are de-powered")
	assert_gt(locked, 0, "the locked cross-links show (padlock)")
	var plain := CityLayout.grid_graph(c, corp, [])
	assert_false(plain["nodes"][0].has("marker"), "other maps keep their own look (raid, netrun)")


# --- The key ---------------------------------------------------------------------------

func test_every_key_entry_differs_in_greyscale() -> void:
	# The Grid key (v4): every marker row apart without colour.
	var legend: MapLegend = add_child_autofree(MapLegend.new(&"meridian", true).use_site_markers())
	var seen := {}
	for r: Array in MapLegend.MARKER_ROWS:
		var k := SiteMarker.grey_key(legend.marker_spec(String(r[0])))
		assert_false(seen.has(k), "%s reads apart from %s in grey (%s)" % [r[0], seen.get(k, ""), k])
		seen[k] = r[0]
	# The other maps' key: every row has its own glyph (cleared was the corporate square).
	var glyphs := {}
	for r: Array in MapLegend.ROWS:
		assert_false(glyphs.has(r[0]), "%s has its own glyph, not %s's" % [r[2], glyphs.get(r[0], "")])
		glyphs[r[0]] = r[2]


func test_the_key_draws_the_maps_markers_says_each_in_plain_words_and_reveals_on_hover() -> void:
	Settings.set_text_scale(1.0)
	var legend: MapLegend = add_child_autofree(MapLegend.new(&"meridian", true).use_site_markers())
	await _frames(2)
	for r: Array in MapLegend.MARKER_ROWS:
		var row := legend.body.find_child("Marker_%s" % r[0], true, false) as Control
		assert_not_null(row, "row %s" % r[0])
		assert_ne(row.tooltip_text, "", "%s says what it means" % r[0])
		if r[0] != "target":
			assert_not_null(row.find_child("SiteMarker", true, false), "%s draws the map's marker" % r[0])
	assert_not_null(legend.body.find_child("Line_locked", true, false), "the locked link")
	assert_not_null(legend.show_all_cell, "SHOW ALL")
	watch_signals(legend)
	legend.show_all_cell.mouse_entered.emit()
	assert_signal_emitted_with_parameters(legend, "show_all_changed", [true])
	legend.show_all_cell.mouse_exited.emit()
	assert_signal_emitted_with_parameters(legend, "show_all_changed", [false])
	for l in legend.body.find_children("*", "Label", true, false):
		assert_eq((l as Label).get_theme_font_size("font_size"), legend.font_size(), "row text at the scale")
	for key in SiteMarker.MEANINGS:
		assert_ne(SiteMarker.meaning(key), "", key)


# --- Projection seam and placement (headless, on 5a's CityModel + CityIsoCamera) ----------

## The city model under corporation `corp`'s Sites (the lots they need, grown by a margin).
func _model_for(corp: CorporationData) -> CityModel:
	var probe := GridMarkerProjection.from_camera(CITY_CONFIG, corp, VIEW)
	return CityModel.build(CITY_CONFIG, CITY_SEED, probe.lots_rect(MODEL_MARGIN))


func test_markers_project_place_apart_and_pick_on_the_city_model() -> void:
	_open_all()
	for corp_id in CORPS:
		var c := RunManager.new_campaign(1, corp_id)
		var corp := RunManager.corporation
		var model := _model_for(corp)
		var cam := CityIsoCamera.make(CITY_CONFIG, Vector3.ZERO, CITY_CONFIG.grid_ortho, VIEW)
		var proj := GridMarkerProjection.from_model(model, cam, corp)
		proj.aim_at_sites()
		var anchors := proj.anchors()
		assert_eq(anchors.size(), corp.city_grid.sites.filter(func(s: SiteData) -> bool: return s != null).size(), "%s: every Site projects" % corp_id)
		var roofs := 0
		for id in anchors:
			var back := proj.lot_under(anchors[id], id)
			assert_almost_eq(back.x, (proj.lots[id] as Vector2).x, 0.01, "%s: projection round-trips (%s)" % [corp_id, id])
			assert_almost_eq(back.y, (proj.lots[id] as Vector2).y, 0.01)
			if proj.height_of(id) > 0.0:
				roofs += 1
		assert_gt(roofs, 0, "%s: pads stand on the Site buildings' roofs" % corp_id)
		var specs := _specs(c, corp)
		var discs := SiteMarkerLayout.place_discs(anchors, specs, 1.0)
		var ids := discs.keys()
		for i in ids.size():
			var a := SiteMarker.box(specs[ids[i]], discs[ids[i]])
			for j in range(i + 1, ids.size()):
				assert_false(a.intersects(SiteMarker.box(specs[ids[j]], discs[ids[j]])), "%s: %s and %s apart" % [corp_id, ids[i], ids[j]])
		for id in ids:
			assert_eq(SiteMarkerLayout.pick(discs, specs, discs[id]), id, "%s: its disc picks %s" % [corp_id, id])
		for scale in SCALES:
			var sizes := {}
			for id in ids:
				sizes[id] = LABEL_BOX * scale
			var labels := SiteMarkerLayout.place_labels(discs, specs, sizes, {}, Rect2(Vector2.ZERO, VIEW))
			assert_false(labels.is_empty(), "%s x%.1f: labels placed" % [corp_id, scale])
			var lk := labels.keys()
			for i in lk.size():
				var r: Rect2 = labels[lk[i]]
				assert_true(Rect2(Vector2.ZERO, VIEW).encloses(r), "inside the view")
				for j in range(i + 1, lk.size()):
					assert_false(r.intersects(labels[lk[j]]), "%s x%.1f: labels apart" % [corp_id, scale])
				for id in ids:
					assert_false(r.intersects(SiteMarker.box(specs[id], discs[id])), "%s x%.1f: a label never covers a marker" % [corp_id, scale])


func test_the_marker_layer_follows_the_camera_hides_and_picks() -> void:
	_open_all()
	var c := RunManager.new_campaign(1, &"meridian")
	var corp := RunManager.corporation
	var model := _model_for(corp)
	var cam := CityIsoCamera.make(CITY_CONFIG, Vector3.ZERO, CITY_CONFIG.grid_ortho, VIEW)
	var proj := GridMarkerProjection.from_model(model, cam, corp)
	proj.aim_at_sites()
	var layer: SiteMarkerLayer = add_child_autofree(SiteMarkerLayer.new())
	layer.size = VIEW
	var specs := _specs(c, corp)
	var labels := {}
	for id in specs:
		labels[id] = String(id)
	layer.attach(proj, specs, labels)
	var hidden := specs.keys().filter(func(id: Variant) -> bool: return not bool(specs[id]["pinned"]))
	assert_false(hidden.is_empty())
	assert_null(layer.view_of(hidden[0]), "a hidden Site has no marker")
	layer.show_all = true
	assert_not_null(layer.view_of(hidden[0]), "SHOW ALL shows it")
	var before: Vector2 = layer.discs[hidden[0]]
	cam.pan_px(Vector2(40, 0))
	layer.replace()
	assert_almost_eq(absf((layer.discs[hidden[0]] as Vector2).x - before.x), 40.0, 1.0, "markers follow the camera")
	assert_not_null(layer.target, "the boss has its pencil TARGET")
	var t := Vector2(CityMapOverlay.TARGET_RADIUS, CityMapOverlay.TARGET_RADIUS * CityMapOverlay.TARGET_FLAT)
	var pencil := Rect2(layer.target.position - t, t * 2.0)
	for id in layer.label_rects:
		assert_false((layer.label_rects[id] as Rect2).intersects(pencil), "no label on the pencil (%s)" % id)
		for other in layer.discs:
			assert_false((layer.label_rects[id] as Rect2).intersects(SiteMarker.box(specs[other], layer.discs[other])), "labels clear of markers")


func test_fight_won_lights_light_only_won_site_buildings_in_cell_colours() -> void:
	_open_all()
	var c := RunManager.new_campaign(1, &"meridian")
	var corp := RunManager.corporation
	var model := _model_for(corp)
	var proj := GridMarkerProjection.from_model(model, CityIsoCamera.make(CITY_CONFIG, Vector3.ZERO, CITY_CONFIG.grid_ortho, VIEW), corp)
	var won := {}
	for id in proj.lots:
		if proj.height_of(id) > 0.0:
			won[id] = proj.lots[id]
			break
	assert_false(won.is_empty(), "a Site with a building")
	var wins := SiteWonLights.windows_for(model, won)
	assert_false(wins.is_empty(), "its building's windows light up")
	for w in wins:
		assert_true(w["color"] == Palette.CELL_PINK or w["color"] == Palette.CELL_ACID, "in Cell colours")
	assert_eq(SiteWonLights.windows_for(model, won), wins, "deterministic")
	var lights: SiteWonLights = autofree(SiteWonLights.new())
	lights.build(model, won)
	assert_eq(lights.multimesh.instance_count, wins.size(), "one window quad each, for the fx layer")


# --- On the Grid page -------------------------------------------------------------------

func _hq_grid(corp: StringName) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_open_all()
	hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp)
	return hq


func test_the_grid_draws_v4_markers_hides_unselectable_sites_and_lights_won_fights() -> void:
	Settings.set_map_legend(true)
	Settings.set_text_scale(1.0)
	var hq := _hq_grid(&"meridian")
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var open := RunManager.launchable_sites()
	# A fight won (cleared), a DOWN node and a TAKEN Site.
	var won: StringName = open[0].id
	c.grid.sites[won]["status"] = GridState.SiteStatus.CLEARED
	var down: StringName = c.grid.home_site_id
	for sd in corp.city_grid.sites:
		if sd != null and sd.id != won and sd.id != c.grid.home_site_id and c.grid.is_corporate(sd.id) and sd.tier == 1:
			c.grid.sites[sd.id]["status"] = GridState.SiteStatus.CLAIMED
			c.grid.sites[sd.id]["condition"] = GridState.Condition.DOWN
			c.grid.sites[sd.id]["node_type"] = &"firewall_relay"
			down = sd.id
			break
	hq.selected_site = c.grid.home_site_id
	hq.show_grid()
	await _frames(SETTLE)
	var overlay: CityMapOverlay = hq.city_overlay
	var hidden := 0
	for n in overlay.nodes:
		assert_true(n.has("marker"), "%s is a v4 marker" % n["id"])
		var spec: Dictionary = n["marker"]
		var shown := overlay.marker_shown(n)
		if spec["kind"] == SiteMarker.KIND_CENTRAL_SERVER:
			continue
		if shown:
			assert_not_null(overlay.marker_view(n["id"]), "%s shows its marker" % n["id"])
		else:
			hidden += 1
			assert_null(overlay.marker_view(n["id"]), "%s is hidden" % n["id"])
			assert_ne(overlay.node_at(overlay.icon_pos(n)), n["id"], "a hidden Site is not picked")
	assert_gt(hidden, 0, "regular Sites not yet reachable are hidden")
	var dv := overlay.marker_view(down)
	assert_not_null(dv, "the DOWN node shows")
	assert_eq(dv.sticker.state, VinylSticker.State.DISABLED, "DOWN: the grey sticker under the white bolt")
	assert_eq(dv.spec["status"], SiteMarker.ST_DOWN)
	assert_true(overlay.lit_sites.has(won), "the fight won lights its building in Cell colours (D17)")
	assert_false(overlay.lit_sites.has(down), "a DOWN node's lights are out")
	assert_ne(overlay.boss_chip_rect, Rect2(), "the boss chip shows")
	assert_not_null(overlay._target_mark, "the boss has its pencil TARGET")
	# SHOW ALL from the key reveals the hidden Sites.
	assert_not_null(hq.grid_legend.show_all_cell, "the Grid's key is the v4 key")
	hq.grid_legend.show_all_cell.mouse_entered.emit()
	await _frames(3)
	assert_true(overlay.show_all)
	for n in overlay.nodes:
		if n["marker"]["kind"] != SiteMarker.KIND_CENTRAL_SERVER:
			assert_not_null(overlay.marker_view(n["id"]), "SHOW ALL: %s shows" % n["id"])
	hq.grid_legend.show_all_cell.mouse_exited.emit()
	await _frames(2)
	assert_false(overlay.show_all, "and hides again")


func test_pointing_at_an_exploit_site_opens_its_decrypted_file() -> void:
	Settings.set_text_scale(1.0)
	var hq := _hq_grid(&"meridian")
	hq.show_grid()
	await _frames(SETTLE)
	var overlay: CityMapOverlay = hq.city_overlay
	var ex: StringName = &""
	for n in overlay.nodes:
		if n.has("exploit_tag"):
			ex = n["id"]
			break
	assert_ne(ex, &"")
	overlay._point_at(ex)
	await _frames(3)
	assert_not_null(overlay.exploit_file, "the file opens")
	var tag := overlay.exploit_file.find_child("Tag", true, false) as Label
	assert_string_contains(tag.text, " // ", "CATEGORY // ITEM")
	assert_eq(overlay.marker_view(ex).type_glyph(), GlyphIcon.table().ids[GlyphTableData.key_for_exploit(int(overlay._node_dict(ex)["marker"]["exploit"]))],
		"the badge is its type's atlas glyph")
	overlay._point_at(&"")
	await _frames(3)
	assert_null(overlay.exploit_file, "and closes")


func test_a_site_that_cannot_be_run_says_why_and_what_to_do_first() -> void:
	Settings.set_text_scale(1.0)
	var hq := _hq_grid(&"solace")
	var corp := RunManager.corporation
	var open := {}
	for s in RunManager.launchable_sites():
		open[s.id] = true
	var t2 := _first(corp, func(sd: SiteData) -> bool: return sd.tier == 2 and not open.has(sd.id))
	hq.selected_site = t2.id
	hq.show_grid()
	await _frames(SETTLE)
	var card := hq.find_child("SelectedSite", true, false) as Control
	assert_null(card.find_child("Launch", true, false), "no JACK IN on a Site not reachable")
	var why := card.find_child("WhyNot", true, false) as Label
	assert_not_null(why, "it says why")
	var linked := PackedStringArray()
	for sd in corp.city_grid.sites:
		if sd != null and sd.links.has(t2.id):
			linked.append(hq.site_name(sd.id))
	assert_false(linked.is_empty())
	assert_string_contains(why.text, linked[0], "and names the Site to clear first")
	hq.selected_site = (RunManager.launchable_sites()[0] as SiteData).id
	hq.show_grid()
	await _frames(SETTLE)
	card = hq.find_child("SelectedSite", true, false) as Control
	assert_not_null(card.find_child("Launch", true, false), "a reachable Site has JACK IN")
	assert_null(card.find_child("WhyNot", true, false), "and no note")
