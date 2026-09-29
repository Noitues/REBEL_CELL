extends GutTest
## Art pass W8c (ART_BIBLE §11 Route / Loot / Modem / Events / Raid interlude / Run failed,
## §6.4–§6.8, §8 T4, §12): the netrun's pages. The route leads with the map and a compact
## list; the loot modal is 70% of the screen with a graffiti title that fits; the Modem's
## sign is baked art, its chips at `body`, slot tiles for the sockets, one Cycles readout;
## the event's story on paper with the speaker once and no subtitle repeat; the raid
## interlude with tile pickers; FLATLINED staged over a grey city with a hero stamp and a
## receipt; tips that follow the device; every page fitting at text scale 2.0.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SLOT := "gut_art_w8c"
const CANVAS := Vector2(1280, 720)

var _text_scale_before: float = 1.0
var _pad_before: bool = false
var _reduce_motion_before: bool = false
var _hc_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_pad_before = Settings.pad_active
	_reduce_motion_before = Settings.reduce_motion
	_hc_before = Settings.high_contrast


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(_pad_before)
	if Settings.reduce_motion != _reduce_motion_before:
		Settings.set_reduce_motion(_reduce_motion_before)
	if Settings.high_contrast != _hc_before:
		Settings.set_high_contrast(_hc_before)
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	get_tree().paused = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _open() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = CANVAS
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	return scene


func _netrun() -> Control:
	var scene := _open()
	scene.start_run(1)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)


func _shop(scene: Control, cycles: int = 120) -> void:
	var s := RunManager.netrun
	s.run.cycles = cycles
	s._open_shop()
	scene._show_current()


func _event(scene: Control, id: StringName = &"ev_leash_on_the_floor") -> void:
	var run := RunManager.netrun.run
	run.event_id = id
	run.phase = RunState.Phase.EVENT
	scene._show_current()


func _loot(scene: Control, kind: String = "card", options: Array = ["twist", "jam", "cache"]) -> void:
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": kind, "options": options})
	run.phase = RunState.Phase.REWARD
	scene._show_current()


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


## Every visible text control under `root`.
func _texts(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for n in _all(root):
		if (n is Label or n is Button or n is RichTextLabel) and (n as Control).is_visible_in_tree():
			out.append(n as Control)
	return out


# --- 1. Route -------------------------------------------------------------------------------------

func test_route_list_is_compact_icons_and_short_words() -> void:
	var scene := _netrun()
	await _frames(6)
	var s := RunManager.netrun
	var open := s.available_nodes()
	assert_true(open.size() > 0)
	for i in open.size():
		var b := scene._panel.find_child("Node%d" % (i + 1), true, false) as Button
		var node := s.run.map.get_node(open[i])
		assert_eq(String(b.get_meta(&"route_base")), scene.node_word(node), "choice %d's button says only what the node is" % (i + 1))
		assert_false(b.text.contains(">"), "no '>' in the button: %s" % b.text)
		assert_false(b.text.contains("("), "no '(same as' in the button: %s" % b.text)
		var row := scene._panel.find_child("Ahead%d" % (i + 1), true, false) as Control
		for k in scene.next_kinds(s.run.map, node):
			var pair := row.find_child("Next_%s" % k, true, false)
			assert_not_null(pair, "choice %d: where it leads, as an icon and its word" % (i + 1))
			assert_not_null(pair.get_node_or_null(^"Icon"))
			assert_ne((pair.get_node(^"Word") as Label).text, "")
		for n in _all(row):
			if n is Label:
				assert_false((n as Label).text.contains("then:"), "no bare 'then:' word")
	assert_eq((scene._panel.find_child("GridZoom", true, false) as Button).theme_type_variation, UiTheme.TERTIARY, "the view switch recedes")
	assert_eq((scene._panel.find_child("SaveQuit", true, false) as Button).theme_type_variation, UiTheme.TERTIARY, "Save & quit recedes")
	await _close(scene)


func test_route_dims_the_city_as_a_map_and_other_pages_do_not() -> void:
	var scene := _netrun()
	await _frames(4)
	var atmo: CityAtmosphere = scene.background.city.atmosphere()
	assert_true(atmo.state.map_mode, "the route is a map over the city (§9.5)")
	_shop(scene)
	await _frames(2)
	assert_false(atmo.state.map_mode, "the Modem is not a map")
	await _close(scene)


func test_route_cuts_to_its_framing_under_reduce_motion() -> void:
	Settings.set_reduce_motion(true)
	var scene := _netrun()
	await _frames(6)
	assert_false(scene.background.camera_easing(), "no held frame or camera ease under reduce motion")
	await _close(scene)


# --- 2. Loot --------------------------------------------------------------------------------------

func test_loot_modal_is_seventy_percent_wide_with_cards_at_hover_size() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.new_campaign(1)
		var scene := _netrun()
		_loot(scene)
		await _frames(4)
		var win := scene._panel.find_child("LootWindow", true, false) as Control
		assert_almost_eq(win.size.x, CANVAS.x * scene.LOOT_MODAL_SHARE, 2.0, "the loot modal is 70%% of the screen at %.1f" % scale)
		var tag := scene._panel.find_child("LootTag", true, false) as GraffitiTag
		assert_true(win.get_global_rect().encloses(tag.get_global_rect()), "the LOOT graffiti fits inside the modal at %.1f" % scale)
		var slack: float = tag.words_width() * scene.LOOT_TAG_SLACK + GraffitiTag.LEFT + GraffitiTag.MASCOT_ROOM
		assert_true(slack <= win.size.x, "the graffiti keeps 140%% width slack at %.1f (%.0f > %.0f)" % [scale, slack, win.size.x])
		var stickers: Node = scene._panel.find_child("Stickers", true, false)
		for c in stickers.get_children():
			var card := c as ZineCard
			assert_true(card.size.x >= scene.LOOT_CARD.x * ZineCard.HOVER_SCALE - 0.5, "offers at hover size or more (%.0f)" % card.size.x)
			assert_true(win.get_global_rect().grow(1.0).encloses(card.get_global_rect()), "an offer inside the modal at %.1f" % scale)
			assert_false(card.get_global_rect().intersects(tag.get_global_rect()), "the LOOT drips keep off the cards at %.1f" % scale)
			# Tooltips never fold one word per line (§6.8: 26-36 columns).
			var lines := card.tooltip_text.split("\n")
			var widest := 0
			for l in lines:
				widest = maxi(widest, l.length())
			assert_true(widest <= UiTip.COLUMNS, "the tip keeps within 36 columns")
			assert_true(lines.size() <= 2 or widest >= UiTip.MIN_COLUMNS - 10, "the tip is not a one-word column")
		await _close(scene)


func test_firmware_loot_picks_its_slot_on_tiles_not_a_dropdown() -> void:
	var scene := _netrun()
	_loot(scene, "firmware", [String(RunManager.lookup().ids_of_class(&"FirmwareData")[0])])
	await _frames(3)
	var pick: Node = scene._panel.find_child("SlotPick", true, false)
	assert_true(pick is SlotPicker, "the slot is picked on tiles")
	assert_eq((pick as SlotPicker).tiles.size(), RunManager.netrun.run.operative.slot_slice_ids.size(), "one tile per slot")
	for n in _all(scene._panel):
		assert_false(n is OptionButton, "no native dropdown on the loot page")
	await _close(scene)


func test_the_picked_loot_is_stamped_before_it_flies() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd")
	assert_true(src.contains("&\"loot_pick\", tr(LOOT_PICK_STAMP)"), "the pick flies with its TAKEN stamp (T2)")
	assert_true(ZineStamp.word_count(tr("TAKEN")) <= ZineStamp.MAX_WORDS)

