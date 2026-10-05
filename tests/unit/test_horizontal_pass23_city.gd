extends GutTest
## H23 city: the HQ mini-map's labels never pile up (#1); a Grid label is drawn near its
## node or not at all (#2); the Grid's key is on screen and follows the text size (#3); no
## two Grid labels overlap (#4); every Grid node shows beside the side column (#5); node
## tooltips name the kind (#6); the runs open now and the Site steps carry their Site's
## map icon (#7). At text scale 1.0 and TEXT_SCALE_MAX, for every corporation. The Grid checks share
## one Grid per corporation and text size (a headless city draw is slow).
## The #2-#5 and #7 Grid checks run in test_city_map_sweeps.gd, on one Grid per
## corporation, text size and stage (Test suite optimization, docs/TEST_SUITE.md).

const HQ := "res://scenes/hq/hq_scene.tscn"
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
const SCALES: Array[float] = [1.0, Settings.TEXT_SCALE_MAX]
const SCREEN := Rect2(0, 0, 1280, 720)
## The HQ mini-map's least size (hq_scene's CITY GRID monitor).
const MINI_SIZE := Vector2(420, 170)
## Frames for the Grid map to settle (the fit waits for the city to redraw each pass).
const SETTLE := 12

var _text_scale_before: float = 1.0
var _legend_before: bool = true


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_legend_before = Settings.map_legend


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_c23_city"
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
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## A 1280x720 holder (the headless window is tiny) with `path` instanced in it.
func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _open_all() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10


## The HQ on corporation `corp`'s Grid at text scale `scale`, settled.
func _hq_grid(corp: StringName, scale: float) -> Control:
	RunManager.reset()
	Settings.set_text_scale(scale)
	var hq := _scene(HQ)
	_open_all()
	hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp)
	hq.show_grid()
	await _frames(SETTLE)
	return hq


func _close(hq: Control) -> void:
	hq.get_parent().queue_free()
	await _frames(1)


## Asserts no two rects of `rects` (key -> Rect2) overlap.
func _assert_apart(rects: Dictionary, what: String) -> void:
	var keys := rects.keys()
	keys.sort()
	for i in keys.size():
		for j in range(i + 1, keys.size()):
			var a: Rect2 = rects[keys[i]]
			var b: Rect2 = rects[keys[j]]
			assert_false(a.intersects(b), "%s: labels %s %s and %s %s overlap" % [what, keys[i], a, keys[j], b])


## Screen centre of `overlay`'s node `n` icon.
func _screen_at(overlay: CityMapOverlay, n: Dictionary) -> Vector2:
	return overlay.get_global_transform() * overlay.icon_pos(n)


## The legend's rect on screen (its scale included).
func _legend_rect(legend: MapLegend) -> Rect2:
	return Rect2(legend.get_global_rect().position, legend.size * legend.scale)


# --- #1 The HQ mini-map ---------------------------------------------------------------------

func test_mini_map_labels_never_overlap_and_keep_their_tooltips() -> void:
	for corp in CORPS:
		RunManager.reset()
		_open_all()
		RunManager.new_campaign(1, corp)
		var c := RunManager.campaign
		for scale in SCALES:
			Settings.set_text_scale(scale)
			var mini: GridMapView = add_child_autofree(GridMapView.new())
			mini.custom_minimum_size = MINI_SIZE
			mini.size = MINI_SIZE
			mini.show_grid(c, RunManager.corporation)
			await _frames(2)
			var what := "%s x%.1f" % [corp, scale]
			assert_false(mini.label_rects.is_empty(), "%s: the mini-map labels some Sites" % what)
			_assert_apart(mini.label_rects, what)
			for id in mini.label_rects:
				assert_true(Rect2(Vector2.ZERO, mini.size).encloses(mini.label_rects[id]), "%s: %s's label inside the mini-map" % [what, id])
			# Pips only where a label was placed (they are part of it, never on another).
			for id in mini.drawn_tiers:
				assert_true(mini.label_rects.has(id), "%s: %s's pips sit in its label" % [what, id])
			# Every Site keeps a tooltip naming its kind, labelled or not.
			for sd in RunManager.corporation.city_grid.sites:
				if sd == null:
					continue
				var tip: String = String(mini._get_tooltip(mini.position_of(sd.id))).replace("\n", " ")
				var word := CityMapOverlay.kind_word(CityLayout.site_kind(c, sd))
				assert_string_contains(tip, word, "%s: %s's tooltip names its kind" % [what, sd.id])
			mini.free()
	# CORE comes first: it always has its label.
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var m: GridMapView = add_child_autofree(GridMapView.new())
	m.size = MINI_SIZE
	m.show_grid(RunManager.campaign, RunManager.corporation)
	await _frames(2)
	assert_true(m.label_rects.has(RunManager.campaign.grid.home_site_id), "CORE is labelled")


func test_the_hq_mini_map_on_the_hq_page_keeps_labels_apart() -> void:
	for scale in SCALES:
		RunManager.reset()
		Settings.set_text_scale(scale)
		var hq := _scene(HQ)
		hq.new_campaign(1)
		await _frames(4)
		var minis := hq.find_children("*", "GridMapView", true, false).filter(func(n: Node) -> bool: return (n as Control).is_visible_in_tree())
		assert_eq(minis.size(), 1, "the HQ shows its mini-map")
		var mini: GridMapView = minis[0]
		_assert_apart(mini.label_rects, "HQ x%.1f" % scale)
		assert_false(mini.label_rects.is_empty())
		await _close(hq)


# --- #2-#5 and #7 The Grid screen -------------------------------------------------------------

# (#2-#5 and #7 on every corporation's Grid: test_city_map_sweeps.gd.)


func test_a_hidden_node_has_no_floating_label_and_the_fit_is_measured() -> void:
	var hq: Control = await _hq_grid(&"solace", 1.0)
	var overlay: CityMapOverlay = hq.city_overlay
	var n: Dictionary = {}
	for m in overlay.nodes:
		if m.get("big", false) and m["id"] != RunManager.campaign.grid.home_site_id:
			n = m
	assert_false(n.is_empty(), "the boss Site")
	overlay.selected_id = n["id"]
	assert_true(overlay.label_rects().has(String(n["id"])), "labelled while it shows")
	# A panel over the node (Renewal Engine floated over PREV SITE): no label anywhere.
	var at := _screen_at(overlay, n)
	overlay.set_blocked_rects([Rect2(at - Vector2(60, 60), Vector2(120, 120))])
	assert_false(overlay.label_rects().has(String(n["id"])), "a hidden node's label is left out, not moved away")
	overlay.set_blocked_rects([])
	# The fit: nothing to do with room enough; a small room asks to zoom out.
	var area := (hq.find_child("GridMapArea", true, false) as Control).get_global_rect()
	assert_true(LegendSpot.fit_into(overlay, SCREEN.grow(4000.0)).is_empty(), "room enough: no change")
	var fit := LegendSpot.fit_into(overlay, Rect2(area.position, area.size * 0.3))
	assert_false(fit.is_empty(), "a small room asks for a new frame")
	assert_true(float(fit["zoom"]) < 1.0, "zoomed out")
	# The legend switch: off, the key hides and the map may use its room; on, the key
	# covers no node again.
	Settings.set_map_legend(false)
	await _frames(SETTLE)
	assert_false(hq.grid_legend.visible, "the key hides")
	Settings.set_map_legend(true)
	await _frames(SETTLE)
	assert_eq(LegendSpot.covered(_legend_rect(hq.grid_legend), LegendSpot.node_rects(overlay, false)), 0.0, "back on, it covers no node")
	await _close(hq)


# --- #6 Tooltips name the kind ---------------------------------------------------------------

func test_every_node_tooltip_names_its_kind_and_what_it_does() -> void:
	for corp in CORPS:
		RunManager.reset()
		_open_all()
		RunManager.new_campaign(1, corp)
		var c := RunManager.campaign
		var g := CityLayout.grid_graph(c, RunManager.corporation, [])
		var overlay: CityMapOverlay = autofree(CityMapOverlay.new())
		overlay.set_graph(g["nodes"], g["edges"])
		var kinds := {}
		for n in g["nodes"]:
			var kind := String(n["kind"])
			kinds[kind] = true
			var tip := overlay.tip_of(n["id"])
			assert_ne(tip, "", "%s %s: a tooltip" % [corp, n["id"]])
			assert_string_contains(tip, CityMapOverlay.kind_word(kind), "%s %s: names its kind" % [corp, n["id"]])
			assert_string_contains(tip, String(CityLayout.KIND_TIPS[kind]), "%s %s: says what it does" % [corp, n["id"]])
		assert_true(kinds.has(CityMapOverlay.KIND_HOME) and kinds.has(CityMapOverlay.KIND_TIER), "%s: CORE and plain Sites checked" % corp)
	for kind in [CityMapOverlay.KIND_TIER, CityMapOverlay.KIND_EXPLOIT, CityMapOverlay.KIND_HEAT, CityMapOverlay.KIND_CENTRAL_SERVER, CityMapOverlay.KIND_HOME]:
		assert_true(String(CityLayout.KIND_TIPS[kind]).begins_with(CityMapOverlay.kind_word(kind)), "%s: the tip leads with its word" % kind)
