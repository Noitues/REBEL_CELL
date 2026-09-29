extends GutTest
## Art pass W9F (ART_BIBLE §12, §14, §4.3, §5.2, §6.8, §8, §9): the final accessibility and
## polish sweep. Every rule the sweep enforces has a test here: no mid-word wrap mode left in
## the UI, every layout test at Settings.TEXT_SCALE_MAX, input-aware words (a pad never reads
## "click" or a bracketed letter), a prompt bar on every page with a pad, the flatline (grey)
## city context, the settle hook, the subtitle band, the Polaroid's caption band, the spinner
## viewer (hub name, lettering, price on UPGRADE, marker circle), the Modem's CARDS window,
## the netrun hookups and the runtime lint's measures.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"
const REVIEW_PACK := "res://tools/visual_qa/review_pack.gd"
const SLOT := "gut_art_w9f"
const CANVAS := Vector2(1280, 720)
## The seven layout test scripts that were held to 1.6 (LayoutScales.VERIFIED_MAX).
const LAYOUT_TESTS: Array[String] = [
	"res://tests/unit/test_anim4b_run_drag_drop.gd", "res://tests/unit/test_anim_r2_combat.gd",
	"res://tests/unit/test_horizontal_pass20_screens.gd", "res://tests/unit/test_horizontal_pass21_screens.gd",
	"res://tests/unit/test_horizontal_pass22_screens.gd", "res://tests/unit/test_horizontal_pass23_screens.gd",
	"res://tests/unit/test_horizontal_pass24_screens.gd",
]

var _text_scale_before: float = 1.0
var _pad_before: bool = false
var _re_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_pad_before = Settings.pad_active
	_re_before = Settings.reduce_effects


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
	Settings.reduce_effects = _re_before
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	get_tree().paused = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _open(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = CANVAS
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	return scene


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


func _files(dir: String) -> PackedStringArray:
	var out := PackedStringArray()
	var d := DirAccess.open(dir)
	if d == null:
		return out
	for f in d.get_files():
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for sub in d.get_directories():
		out.append_array(_files(dir.path_join(sub)))
	return out


# --- §4.3 rule 3: no mid-word breaks --------------------------------------------------------------

func test_no_mid_word_wrap_mode_left_in_game_code() -> void:
	for p in _files("res://scripts"):
		var src := FileAccess.get_file_as_string(p)
		assert_false(src.contains("AUTOWRAP_WORD_SMART"), "%s: WORD_SMART breaks a word that doesn't fit mid-word" % p)
		assert_false(src.contains("AUTOWRAP_ARBITRARY"), "%s: ARBITRARY breaks anywhere" % p)


func test_whole_words_keeps_a_label_as_wide_as_its_longest_word() -> void:
	var box: VBoxContainer = add_child_autofree(VBoxContainer.new())
	box.size = Vector2(40, 200)
	var l := Label.new()
	l.text = "a BREAKER b"
	UiWrap.whole_words(l)
	box.add_child(l)
	await _frames(3)
	assert_eq(l.autowrap_mode, TextServer.AUTOWRAP_WORD, "whole words")
	var need := UiWrap.longest_word_px("BREAKER", l.get_theme_font(&"font"), l.get_theme_font_size(&"font_size"))
	assert_true(l.custom_minimum_size.x >= need - 0.5, "never narrower than BREAKER (%.0f < %.0f)" % [l.custom_minimum_size.x, need])
	# A width the view sets later is kept when wider.
	l.custom_minimum_size.x = 300.0
	l.add_theme_font_size_override(&"font_size", 20)
	await _frames(3)
	assert_eq(l.custom_minimum_size.x, 300.0, "the view's own width stays")


func test_crew_card_class_tag_never_breaks_mid_word_at_two() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var box: HBoxContainer = add_child_autofree(HBoxContainer.new())
	var card := CrewCard.new("BREAKER 1", "Breaker", 0, 50, 50, "", 0.0)
	box.add_child(card)
	await _frames(4)
	var tag := card.find_child("ClassTag", true, false) as Label
	assert_eq(tag.autowrap_mode, TextServer.AUTOWRAP_WORD)
	assert_true(tag.size.x + 0.5 >= UiWrap.longest_word_px("BREAKER", tag.get_theme_font(&"font"), tag.get_theme_font_size(&"font_size")), "BREAKER fits whole")


# --- §12 text scale 2.0 in the layout tests --------------------------------------------------------

func test_every_layout_test_runs_at_the_text_scale_ceiling() -> void:
	assert_false(ResourceLoader.exists("res://tests/helpers/layout_scales.gd"), "LayoutScales.VERIFIED_MAX is gone")
	for p in LAYOUT_TESTS:
		var src := FileAccess.get_file_as_string(p)
		assert_false(src.contains("VERIFIED_MAX"), "%s still holds screens to 1.6" % p)
		assert_true(src.contains("Settings.TEXT_SCALE_MAX"), "%s checks up to Settings.TEXT_SCALE_MAX" % p)
	assert_eq(Settings.TEXT_SCALE_MAX, 2.0, "the ceiling is 2.0 (Q5)")


# --- §6.8 / §12 input-aware words ------------------------------------------------------------------

## Game-code lines that say a mouse word in a player-facing string must pick the device's words:
## UiTip.for_input, a pad branch on the same statement, or a mouse-only table that for_input reads.
func test_mouse_words_in_player_strings_go_through_for_input() -> void:
	var mouse := RegEx.create_from_string("(?i)\\b(click|clicks|clicked|clicking|right-click|right click|left click|drag|drags|dragged|dragging|hover|hovering)\\b")
	var literal := RegEx.create_from_string("\"([^\"\\\\]|\\\\.)*\"")
	var allowed_tables := ["DRAG_TIPS := {", "DRAG_TIPS_MORE := {"]
	for p in _files("res://scripts"):
		if p.ends_with("ui_tip.gd") or p.ends_with("settings.gd") or p.ends_with("audio_director.gd") or p.ends_with("ui_motion_data.gd"):
			continue
		var lines := FileAccess.get_file_as_string(p).split("\n")
		var in_table := false
		for i in lines.size():
			var line := lines[i]
			var code := line.split("#")[0] if not line.contains("\"") else line
			if line.strip_edges().begins_with("#"):
				continue
			for t in allowed_tables:
				if line.contains(t):
					in_table = true
			if in_table and line.contains("}"):
				in_table = false
				continue
			if in_table:
				continue
			for m in literal.search_all(code):
				var s := m.get_string()
				if not mouse.search(s):
					continue
				if code.contains("print(") or code.contains("play_sfx") or code.contains("stylebox") or code.contains("&\"hover\"") or s == "\"hover\"":
					continue
				var context := "\n".join(lines.slice(maxi(0, i - 2), i + 2))
				var ok := context.contains("for_input(") or context.contains("if pad") or context.contains("pad_active") or context.contains("if Settings.pad_active")
				assert_true(ok, "%s:%d: %s is mouse wording with no pad variant" % [p, i + 1, s.left(60)])


## With a pad in use, no words shown or tipped on a page say "click", "drag" or "hover", and no
## key is a bracketed letter (§12: glyphs, never letters in brackets).
func _assert_pad_words(root: Node, where: String) -> void:
	var bracket := RegEx.create_from_string("\\[(A|B|X|Y|LB|RB|LT|RT|L3|R3|Menu|View)\\]")
	for n in _all(root):
		if not (n is Control) or not (n as Control).is_visible_in_tree():
			continue
		var c := n as Control
		var words := String(c.get(&"text")) if (c is Label or c is Button) else ""
		for w in [words, c.tooltip_text]:
			if w == "":
				continue
			assert_false(UiTip.has_mouse_words(w), "%s: '%s' (%s) says a mouse word to a pad player" % [where, w.left(60), c.name])
			assert_null(bracket.search(w), "%s: '%s' (%s) names a pad button in brackets" % [where, w.left(60), c.name])


func test_pad_pages_speak_pad_and_show_their_prompt_bar() -> void:
	Settings.set_pad_active(true)
	var hq := _open(HQ)
	await _frames(4)
	hq.new_campaign(1)
	await _frames(4)
	_assert_pad_words(hq, "hq")
	assert_true(hq.pad_prompts.visible and not hq.pad_prompts.glyphs().is_empty(), "hq: prompt bar with glyphs")
	hq.show_grid()
	await _frames(4)
	_assert_pad_words(hq, "grid")
	assert_true(hq.pad_prompts.visible, "grid: prompt bar")
	hq.get_parent().queue_free()
	await _frames(2)
	var scene := _open(NETRUN)
	scene.start_run(1)
	await _frames(4)
	_assert_pad_words(scene, "route")
	assert_true(scene.pad_prompts.visible and not scene.pad_prompts.glyphs().is_empty(), "route: prompt bar")
	var s := RunManager.netrun
	s.run.cycles = 120
	s._open_shop()
	scene._show_current()
	await _frames(4)
	_assert_pad_words(scene, "modem")
	assert_true(scene.pad_prompts.visible, "modem: prompt bar")
	scene.open_remove()
	await _frames(3)
	var deck := scene.get_node("DeckView") as DeckView
	_assert_pad_words(deck, "deck viewer")
	assert_true(deck.prompts.visible and not deck.prompts.glyphs().is_empty(), "the deck viewer's own prompt bar")
	deck.close()
	await _frames(2)


func test_a_fight_has_a_pad_prompt_bar_and_glyphs_not_brackets() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = CANVAS
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"compliance_officer", 5)
	await _frames()
	Settings.set_pad_active(true)
	await _frames(3)
	assert_true(scene.pad_prompts.visible and scene.pad_prompts.glyphs().size() >= 4, "the fight's prompt bar")
	assert_eq(scene._end_turn_button.pad_glyph(), PadGlyph.button_for_action(&"end_turn"), "SEND IT draws its glyph")
	_assert_pad_words(scene, "fight")
	Settings.set_pad_active(false)
	await _frames(3)
	assert_false(scene.pad_prompts.visible, "no prompt bar for keys and mouse")
	assert_string_contains(scene._end_turn_button.key_hint, "[", "keys read their bracketed key")


func test_focus_tip_never_shows_mouse_words_to_a_pad() -> void:
	Settings.set_pad_active(true)
	var b: Button = add_child_autofree(Button.new())
	b.text = "x"
	b.tooltip_text = "Drag it onto a slot, or click it."
	FocusTip.attach(b)
	await _frames(1)
	b.grab_focus()
	await _frames(2)
	var tip := FocusTip.tip_of(b)
	assert_not_null(tip, "the focus tip shows")
	if tip != null:
		assert_false(UiTip.has_mouse_words(tip.text), "pad words: '%s'" % tip.text)


# --- §5.2.4: the netrun hookups (W8b's hand-off) --------------------------------------------------

func test_netrun_hookups() -> void:
	var scene := _open(NETRUN)
	scene.start_run(1)
	await _frames(4)
	assert_true(scene.drops.carry_changed.is_connected(scene.hud._on_carry), "hud.watch_drops(drops): CARDS/DAEMONS get their brackets")
	assert_eq(scene.city_overlay.corp_id, RunManager.campaign.corporation_id, "threat routes carry the corp pattern")
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	scene._show_current()
	await _frames(4)
	if scene.route_key_foldable():
		var was: bool = scene.route_legend.opened
		var ev := InputEventAction.new()
		ev.action = &"cycle_target"
		ev.pressed = true
		scene._unhandled_input(ev)
		assert_ne(scene.route_legend.opened, was, "cycle_target folds / opens the route key")
		var named := false
		for p in scene.pad_prompts.prompts:
			named = named or StringName(p[0]) == &"cycle_target"
		assert_true(named, "the route key has its pad prompt")
	HeatRules.add_heat(RunManager.campaign, RunManager.config().major_heat_levels()[0] + 1, RunManager.config(), "test")
	RunManager.netrun._maybe_raid_interlude()
	scene._show_current()
	await _frames(4)
	var start := scene._panel.find_child("StartDefense", true, false) as Button
	assert_not_null(start)
	if start != null:
		assert_eq(start.theme_type_variation, UiTheme.PRIMARY, "START DEFENSE is the primary")
		assert_eq(start.get_meta(&"icon_kind", StatIcon.PLAY) if start.has_meta(&"icon_kind") else StatIcon.PLAY, StatIcon.PLAY)
		assert_true(FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd").contains("IconMark.attach(run_btn, StatIcon.PLAY)"), "with the PLAY icon")


# --- A4: the flatline (grey) city context ---------------------------------------------------------

func test_flatline_is_a_city_context_that_blends_and_gives_the_colour_back() -> void:
	assert_true(CityLookData.CONTEXTS.has(&"flatline"))
	var cfg := CityLookData.shipped()
	var g := cfg.grade_of(&"flatline")
	assert_eq(float(g["saturation"]), 0.0, "grey")
	assert_eq(float(g[CityLookData.LEAN_KEY]), 0.0, "no corp lean")
	var state := CityState.new()
	state.context = &"net"
	state.corp_id = &"solace"
	state.progress = 1.0
	var coloured := CityGrade.params(state, cfg)
	state.context_from = &"net"
	state.context = &"flatline"
	state.context_mix = 0.5
	var half := CityGrade.params(state, cfg)
	state.context_mix = 1.0
	var grey := CityGrade.params(state, cfg)
	assert_almost_eq(float(half["saturation"]), lerpf(float(coloured["saturation"]), 0.0, 0.5), 0.001, "the blend runs half way")
	assert_eq(float(grey["saturation"]), 0.0)
	assert_eq(float(grey["tint_amount"]), 0.0, "the flatline keeps none of the corp's lean")
	assert_gt(float(coloured["tint_amount"]), 0.0)


func test_run_end_greys_the_whole_city_and_hands_it_back() -> void:
	var scene := _open(NETRUN)
	scene.start_run(1)
	await _frames(3)
	var atmo: CityAtmosphere = scene.background.city.atmosphere()
	var before := atmo.state.context
	RunManager.netrun.run.outcome = RunState.Outcome.DIED
	RunManager.netrun.run.phase = RunState.Phase.ENDED
	scene._show_current()
	await _frames(3)
	var stage := scene._panel as RunEndStage
	assert_not_null(stage)
	stage.finish_now()
	assert_eq(stage.atmosphere, atmo, "the stage greys the city itself")
	assert_eq(atmo.state.context, &"flatline", "the city's context is the flatline")
	assert_almost_eq(atmo.blend_amount(), RunEndStage.GREY_AMOUNT, 0.01)
	assert_false(stage.grade.visible, "no second grade over the page's rect")
	stage.queue_free()
	await _frames(2)
	assert_eq(atmo.state.context, before, "the city gets its own context back")
	assert_eq(atmo.blend_amount(), 0.0)


func test_clear_campaign_progress_forgets_the_lean() -> void:
	var city := NeonCity.new()
	add_child_autofree(city)
	await _frames(2)
	var atmo := city.atmosphere()
	atmo.set_campaign_progress(0.8, &"solace")
	atmo.clear_campaign_progress()
	assert_eq(atmo.state.progress, 0.0)
	assert_eq(atmo.state.corp_id, &"")
	assert_false(atmo._set.has("progress"), "a followed city reads the campaign again")


# --- A5: PageTransition.settle's generic hook ------------------------------------------------------

class _Settles:
	extends Control
	var settled := false

	func settle_motion() -> void:
		settled = true


func test_settle_calls_any_settle_motion_and_the_stages_leave_typing_meta() -> void:
	var root: Control = add_child_autofree(Control.new())
	var a := _Settles.new()
	var b := _Settles.new()
	root.add_child(a)
	a.add_child(b)
	PageTransition.settle(root)
	assert_true(a.settled and b.settled, "every node with settle_motion() ends its motion")
	for p in ["res://scripts/ui/kit/run_end_stage.gd", "res://scripts/ui/kit/campaign_end_stage.gd"]:
		assert_false(FileAccess.get_file_as_string(p).contains("Typing.META"), "%s no longer rides Typing.META" % p)
	Settings.reduce_effects = false
	var stage := RunEndStage.new(RunState.Outcome.DIED, "FLATLINED")
	root.add_child(stage)
	stage.play()
	PageTransition.settle(root)
	assert_false(stage.running(), "a settle ends the run end's sequence")
	assert_false(Typing.any_typing(get_tree()), "and it never counts as words typing")


# --- A3: the subtitle band and the caption floor ---------------------------------------------------

func test_empty_subtitle_band_holds_one_line_and_grows_when_a_line_comes() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	Dialogue.clear()
	var hq := _open(HQ)
	await _frames(4)
	var strip := hq.subtitle_strip as SubtitleStrip
	Dialogue.clear()
	strip.in_use = false
	strip._fit()
	await _frames(2)
	assert_almost_eq(strip.size.y, Dialogue.band_height(1), 1.0, "empty: one line")
	assert_almost_eq(strip.dock_rect().size.y, Dialogue.band_height(2), 1.0, "the dock keeps its full height")
	Dialogue.say(RC.Voice.DISPATCH, "Jacking you in. Keep the Heat down and bank at the first Rack before the auditors land.")
	await _frames(3)
	assert_almost_eq(strip.size.y, Dialogue.band_height(2), 1.0, "a line: the band grows to two")


func test_a_subtitle_page_never_shrinks_under_caption() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	Dialogue.dock_at(Rect2(100, 90, 500, 60), 1)
	Dialogue.say(RC.Voice.DISPATCH, "Datenschutzgrundverordnungsbeauftragtenstellvertreterausweisnummernkontrollsystem ist aktiv.")
	await _frames(2)
	assert_true(Dialogue.text_label.get_theme_font_size(&"normal_font_size") >= Dialogue.caption_px(), "never under caption x text scale")
	Dialogue.dock_default()


# --- A2: the Polaroid's caption band and the spinner's hub ----------------------------------------

func test_polaroid_caption_band_keeps_the_floor_caption() -> void:
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var p := Polaroid.new("R0")
	p.size = Vector2(60, 72)
	add_child_autofree(p)
	await _frames(1)
	assert_true(p.caption_room().y + 0.5 >= p.caption_floor_height(), "the band holds the caption at its floor")
	var cl := p.caption_layout()
	assert_true(float(cl["size"].y) <= p.caption_room().y + 0.5, "the caption never runs over the photo")


func test_spinner_hub_name_fits_the_disc_whole() -> void:
	var lay := SpinnerView.hub_name_layout("BREAKER CORE MK2", 30, 24)
	for line in lay["lines"]:
		var w := Palette.marker().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, int(lay["px"])).x * float(lay.get("squeeze", 1.0))
		assert_true(w <= SpinnerView.HUB_TEXT_W + 0.5, "'%s' fits (%.0f px)" % [line, w])
		assert_true("BREAKER CORE MK2".split(" ").has(String(line).split(" ")[0]), "whole words only")
	assert_true(int(lay["px"]) >= 24, "never under the small step")


# --- A6: the spinner viewer --------------------------------------------------------------------------

func test_spinner_viewer_price_on_upgrade_lettering_and_circle() -> void:
	var s := RunManager
	var op := s.campaign.living_operatives()[0]
	var slices: Array[StringName] = op.slot_slice_ids if "slot_slice_ids" in op else [&"seg_echo"]
	var view := SpinnerView.new(slices, [] as Array[StringName], RunManager.lookup(), "UPGRADE", "UPGRADE")
	add_child_autofree(view)
	await _frames(2)
	view.set_prices(func(_k: int) -> int: return 150, 100)
	Settings.reduce_effects = true
	view.select(0)
	assert_true(view.action_text().contains("150"), "the price is on UPGRADE: '%s'" % view.action_text())
	assert_true(view.price_label.visible and view.price_label.text.contains("NEED"), "short: NEED n · HAVE m")
	assert_eq(view.price_label.get_theme_color(&"font_color"), Palette.HARM, "in HARM (§6.7)")
	assert_true(view.circle_drawn, "reduce effects: the circle at once (its end state)")
	view.draw_scale = 0.7
	assert_true(view.letter_px(UiTheme.CAPTION) * 0.7 >= UiTheme.CAPTION - 0.01, "the wheel's caption reads at 12 px or more on screen however far it's scaled")


# --- A7: the Modem's CARDS window ---------------------------------------------------------------------

func test_modem_cards_window_is_never_a_quarter_empty_in_one_column() -> void:
	for scale in [1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.new_campaign(1)
		var scene := _open(NETRUN)
		scene.start_run(1)
		await _frames(2)
		RunManager.netrun.run.cycles = 120
		RunManager.netrun._open_shop()
		scene._show_current()
		await _frames(5)
		var stickers := scene._panel.find_child("Stickers", true, false) as Control
		var win := stickers.get_parent().get_parent() as Control
		while win != null and not (win is TerminalWindow):
			win = win.get_parent() as Control
		assert_not_null(win)
		if win != null:
			var row_w := stickers.size.x
			var body_w := win.size.x
			assert_true(row_w >= body_w * 0.75 - UiTheme.PANEL_PAD_H * 2.0, "CARDS at %.1f: cards %.0f of %.0f px" % [scale, row_w, body_w])
		scene.get_parent().queue_free()
		await _frames(2)


# --- A8: the runtime lint's measures ------------------------------------------------------------------

func test_lint_export_cuts_text_to_its_scroll_view_and_sees_modals() -> void:
	var pack: Node = load(REVIEW_PACK).new()
	var layer: CanvasLayer = add_child_autofree(CanvasLayer.new())
	var root := Control.new()
	layer.add_child(root)
	root.size = CANVAS
	var sc := ScrollContainer.new()
	sc.position = Vector2(100, 100)
	sc.size = Vector2(200, 100)
	root.add_child(sc)
	var box := VBoxContainer.new()
	sc.add_child(box)
	var inside := Label.new()
	inside.text = "SHOWN"
	box.add_child(inside)
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(10, 400)
	box.add_child(spacer)
	var below := Label.new()
	below.text = "SCROLLED OUT"
	box.add_child(below)
	var modal := PanelContainer.new()
	root.add_child(modal)
	await _frames(3)
	var r1: Rect2 = pack.call(&"_visible_rect", inside, inside.get_global_rect())
	var r2: Rect2 = pack.call(&"_visible_rect", below, below.get_global_rect())
	assert_gt(r1.size.y, 0.0, "the visible label keeps its rect")
	assert_eq(r2.size, Vector2.ZERO, "the scrolled-out label has no visible rect")
	pack.set(&"_modals", [modal] as Array[Control])
	assert_true(pack.call(&"_under_modal", inside), "text drawn before an open modal is under it")
	assert_false(pack.call(&"_under_modal", modal), "the modal itself is not under itself")
	pack.free()


func test_lint_report_uses_on_screen_size_and_leaves_out_hidden_text() -> void:
	var src := FileAccess.get_file_as_string("res://tools/visual_qa/lint_report.py")
	assert_true(src.contains("px = float(c.get(\"screen_px\""), "the size judged is the on-screen size (font x ancestor scales)")
	assert_true(src.contains("under_modal"), "text under an open modal is left out")
	assert_true(src.contains("visible_rect"), "text is cut to its scroll view")
	var harness := FileAccess.get_file_as_string(REVIEW_PACK)
	assert_true(harness.contains("\"under_modal\": _under_modal(c)") and harness.contains("\"visible_rect\""), "the harness exports both")


# --- §12 reduce motion: no shake, no camera move ------------------------------------------------

func test_reduce_motion_shakes_nothing() -> void:
	var was := Settings.reduce_motion
	Settings.set_reduce_motion(true)
	assert_eq(Fx.shake_px(&"hit_shake"), 0.0, "no hit shake")
	var n: Control = add_child_autofree(Control.new())
	n.position = Vector2(10, 10)
	Motion.force_live = true
	var tw := Motion.shake(n, &"button_refused")
	Motion.force_live = false
	assert_null(tw, "no refusal shake")
	assert_eq(n.position, Vector2(10, 10), "it rests where it was")
	assert_false(Motion.camera_moves_allowed(), "and the camera holds (the jack cross-fades)")
	Settings.set_reduce_motion(was)
