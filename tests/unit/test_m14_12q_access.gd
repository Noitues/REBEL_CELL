extends GutTest
## M14 12Q-ACCESS (docs/handoff/m14_12q/qa_matrix_audit.md, pack B L78-L83): high contrast keeps
## its promise ("Opaque panels, 7:1 text and thick edges") on every screen through the kit
## (HighContrast, HighContrastWalk); the SAVED stamp and the tutorial's Next read at 7:1 under it;
## two home hits fly as one number; the DECRYPTED stamp stays in its slot at text 2.0.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"
const TITLE := "res://scenes/menu/title_scene.tscn"
const HARNESS := "res://tools/visual_qa/review_pack.gd"
const SCREEN := Rect2(0, 0, 1280, 720)
## The review pack's screens this test reaches headless (the rest need the harness's window:
## bakes, captures, scripted drags).
const SCREENS: Array[String] = ["title", "hq", "raid_setup", "route", "combat_start"]
## Text this see-through or less is fading (a motion), not resting: not measured.
const FADED := 0.99
## A box at least this opaque is a panel's fill.
const OPAQUE := 0.9

var _scale := 1.0
## Words and panels the sweep measured (it must not pass on an empty screen).
var _measured := 0
var _hc := false
var _reduce := false


func before_all() -> void:
	_scale = Settings.text_scale
	_hc = Settings.high_contrast
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_m14_12q_access"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false
	HighContrastWalk.install()


func after_each() -> void:
	Motion.force_live = false
	HighContrast.drawn = null
	if Settings.high_contrast != _hc:
		Settings.set_high_contrast(_hc)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
		Fx.apply_settings()
	Fx._set_jacking(false)
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


func _holder() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	return holder


func _scene(path: String) -> Control:
	var scene: Control = load(path).instantiate()
	_holder().add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _close(scene: Control) -> void:
	if is_instance_valid(scene) and scene.get_parent() != null:
		scene.get_parent().queue_free()
	await _frames(2)


# --- The kit's rules ---------------------------------------------------------------------------

func test_lift_reaches_seven_to_one_changing_as_little_as_it_must() -> void:
	var dims: Array[Color] = [Palette.TEXT_LO, Palette.TEXT_MID, Palette.HARM, Palette.CELL_PINK, Palette.NET_CYAN,
		Palette.CORP_SOLACE, Palette.CORP_MERIDIAN, Color(Palette.PAPER, 0.5), Palette.NIGHT_SKY]
	for c in dims:
		var up := HighContrast.lift(c)
		assert_gte(Palette.contrast(up, HighContrast.BG), HighContrast.HC_MIN_CONTRAST, "%s lifts to 7:1 on black" % c.to_html())
		assert_eq(up.a, 1.0, "opaque")
		assert_true(HighContrast.lift(up).is_equal_approx(up), "lifting twice changes nothing")
	assert_true(HighContrast.lift(Palette.TEXT_HI).is_equal_approx(Palette.TEXT_HI), "words already at 7:1 keep their colour")
	var ink := HighContrast.lift(Palette.TEXT_LO, Palette.PAPER)
	assert_gte(Palette.contrast(ink, Palette.PAPER), HighContrast.HC_MIN_CONTRAST, "on paper the words darken to 7:1")


func test_the_view_helpers_change_only_under_high_contrast() -> void:
	Settings.set_high_contrast(false)
	var glass := Color(Palette.NIGHT_SKY, 0.8)
	assert_eq(HighContrast.plate(glass), glass, "off: the glass as given")
	assert_eq(HighContrast.edge(1.5), 1.5)
	assert_eq(HighContrast.ink(Palette.TEXT_LO), Palette.TEXT_LO)
	Settings.set_high_contrast(true)
	assert_eq(HighContrast.plate(glass), HighContrast.BG, "hc: an opaque plate")
	assert_gte(HighContrast.edge(1.5), 3.0, "hc: a thick edge")
	assert_gte(HighContrast.edge(0.5), float(HighContrast.HC_EDGE_MIN))
	assert_gte(Palette.contrast(HighContrast.ink(Palette.TEXT_LO), HighContrast.BG), HighContrast.HC_MIN_CONTRAST)
	assert_gte(HighContrast.outline_px(12), HighContrast.HC_OUTLINE_MIN)
	assert_gte(HighContrast.outline_px(40), 10, "the outline grows with the words")


func test_the_walk_restyles_a_views_own_colours_and_boxes_and_puts_them_back() -> void:
	Settings.set_high_contrast(false)
	var root := _holder()
	var panel := PanelContainer.new()
	var glass := StyleBoxFlat.new()
	glass.bg_color = Color(Palette.NIGHT_SKY, 0.6)
	glass.border_color = Palette.NET_CYAN
	glass.set_border_width_all(1)
	panel.add_theme_stylebox_override(&"panel", glass)
	root.add_child(panel)
	var box := VBoxContainer.new()
	panel.add_child(box)
	var dim := Label.new()
	dim.text = "LAST TURN: +3 BLOCK"
	dim.add_theme_color_override(&"font_color", Palette.TEXT_LO)
	box.add_child(dim)
	var paper := Label.new()
	paper.text = "SAVED"
	var sticker := StyleBoxFlat.new()
	sticker.bg_color = Palette.PAPER
	paper.add_theme_stylebox_override(&"normal", sticker)
	paper.add_theme_color_override(&"font_color", Palette.TEXT_MID)
	box.add_child(paper)
	var button := Button.new()
	button.text = "MAP KEY"
	var tint := StyleBoxFlat.new()
	tint.bg_color = Color(Palette.NET_CYAN, 0.7)
	button.add_theme_stylebox_override(&"normal", tint)
	button.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	box.add_child(button)
	var live := Label.new()
	live.text = "60/60"
	live.label_settings = UiTheme.live_number(UiTheme.HEADING, Palette.HARM)
	var shared := live.label_settings
	box.add_child(live)
	await _frames(1)
	Settings.set_high_contrast(true)
	var p := panel.get_theme_stylebox(&"panel") as StyleBoxFlat
	assert_eq(p.bg_color, HighContrast.BG, "a see-through panel goes opaque black")
	assert_gte(p.border_width_left, HighContrast.HC_EDGE_MIN, "and its edge thickens")
	assert_almost_eq(glass.bg_color.a, 0.6, 0.001, "the view's own box is never changed (a copy is restyled)")
	for l: Control in [dim, button]:
		var fc := l.get_theme_color(&"font_color")
		var back := HighContrastWalk.backing_of(l)
		assert_gte(Palette.contrast(fc, back), HighContrast.HC_MIN_CONTRAST, "%s: 7:1 on its backing" % l.name)
	assert_gte(dim.get_theme_constant(&"outline_size"), HighContrast.outline_px(dim.get_theme_font_size(&"font_size")), "light words get a thick black outline")
	assert_eq(dim.get_theme_color(&"font_outline_color"), HighContrast.BG)
	assert_eq((button.get_theme_stylebox(&"normal") as StyleBoxFlat).bg_color, HighContrast.BG, "a tinted button fill goes black, its tint the edge")
	assert_eq((paper.get_theme_stylebox(&"normal") as StyleBoxFlat).bg_color, Palette.PAPER, "an opaque sticker keeps its paper")
	assert_gte(Palette.contrast(paper.get_theme_color(&"font_color"), Palette.PAPER), HighContrast.HC_MIN_CONTRAST, "and its words reach 7:1 on it")
	assert_ne(live.label_settings, shared, "a live number gets a copy")
	assert_gte(Palette.contrast(live.label_settings.font_color, HighContrast.BG), HighContrast.HC_MIN_CONTRAST)
	assert_eq(shared.font_color, Palette.HARM, "the shared LabelSettings is untouched")
	# A view re-colouring its words under high contrast is restyled again.
	dim.add_theme_color_override(&"font_color", Palette.TEXT_LO)
	await _frames(1)
	HighContrastWalk.flush()
	assert_gte(Palette.contrast(dim.get_theme_color(&"font_color"), HighContrast.BG), HighContrast.HC_MIN_CONTRAST, "a re-colour is lifted again")
	Settings.set_high_contrast(false)
	assert_eq(panel.get_theme_stylebox(&"panel"), glass, "off: the view's own box back")
	assert_eq(dim.get_theme_color(&"font_color"), Palette.TEXT_LO, "its own colour back")
	assert_false(dim.has_theme_constant_override(&"outline_size"), "no outline it never had")
	assert_eq(live.label_settings, shared, "its own LabelSettings back")


# --- Every screen the review pack reaches headless ------------------------------------------------

## Every visible panel's own fill opaque, every visible word at 7:1 on its backing (its own opaque
## box, its black outline or, for ink, the paper), every edge at least HC_EDGE_MIN; [] when so.
func _hc_violations(root: Node, where: String) -> Array[String]:
	var out: Array[String] = []
	for n in root.find_children("*", "Control", true, false):
		var c := n as Control
		if not c.is_visible_in_tree() or _alpha(c) < FADED:
			continue
		if c is Panel or c is PanelContainer:
			var sb := c.get_theme_stylebox(&"panel") as StyleBoxFlat
			if sb != null and sb.draw_center and sb.bg_color.a > 0.0 and sb.bg_color.a < OPAQUE:
				out.append("%s %s: panel fill alpha %.2f" % [where, c.get_path(), sb.bg_color.a])
		var text := _text_of(c)
		if text.strip_edges() == "" or (c is BaseButton and (c as BaseButton).disabled):
			continue
		var col := _font_color(c)
		if col.a < HighContrastWalk.HIDDEN_ALPHA:
			continue  # hidden words (a stand-in for layout)
		_measured += 1
		var back := HighContrastWalk.backing_of(c)
		var own := _own_box(c)
		if own.a <= 0.0 and HighContrastWalk.is_light(col):
			var need := HighContrast.outline_px(_font_px(c))
			if _outline(c) < need or not _outline_color(c).is_equal_approx(HighContrast.BG):
				out.append("%s %s \"%s\": outline %d < %d" % [where, c.get_path(), text.left(24), _outline(c), need])
				continue
		var r := Palette.contrast(Color(col, 1.0), back)
		if r < HighContrast.HC_MIN_CONTRAST - 0.01 or col.a < OPAQUE:
			out.append("%s %s \"%s\": %.2f:1 (%s on %s, alpha %.2f)" % [where, c.get_path(), text.left(24), r, col.to_html(false), back.to_html(false), col.a])
	return out


func _alpha(c: CanvasItem) -> float:
	var a := c.self_modulate.a
	var n: Node = c
	while n != null:
		if n is CanvasItem:
			a *= (n as CanvasItem).modulate.a
		n = n.get_parent()
	return a


## A campaign with a raid pending and an asset deployed (RAID SETUP has something to show).
func _raid_campaign() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	var g := RunManager.corporation.city_grid
	var first: StringName = g.get_site(g.home_site_id).links[0]
	DemoSetup.set_schematics(c, 100)
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	var armory: Array[StringName] = [&"turret", &"ice_lock", &"decoy"]
	DemoSetup.set_armory(c, armory)
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)


func _text_of(c: Control) -> String:
	if c is Label:
		return (c as Label).text
	if c is Button:
		return (c as Button).text
	if c is RichTextLabel:
		return (c as RichTextLabel).get_parsed_text()
	return ""


func _font_color(c: Control) -> Color:
	if c is Label and (c as Label).label_settings != null:
		return (c as Label).label_settings.font_color
	if c is RichTextLabel:
		return c.get_theme_color(&"default_color")
	return c.get_theme_color(&"font_color")


func _font_px(c: Control) -> int:
	if c is Label and (c as Label).label_settings != null:
		return (c as Label).label_settings.font_size
	if c is RichTextLabel:
		return c.get_theme_font_size(&"normal_font_size")
	return c.get_theme_font_size(&"font_size")


func _outline(c: Control) -> int:
	if c is Label and (c as Label).label_settings != null:
		return (c as Label).label_settings.outline_size
	return c.get_theme_constant(&"outline_size")


func _outline_color(c: Control) -> Color:
	if c is Label and (c as Label).label_settings != null:
		return Color((c as Label).label_settings.outline_color, 1.0)
	return c.get_theme_color(&"font_outline_color")


func _own_box(c: Control) -> Color:
	var name := &"normal" if (c is Label or c is BaseButton) else &""
	if name == &"":
		return Color(0, 0, 0, 0)
	var sb := c.get_theme_stylebox(name) as StyleBoxFlat
	if sb != null and sb.draw_center and sb.bg_color.a >= OPAQUE:
		return sb.bg_color
	return Color(0, 0, 0, 0)


func _settle_hc(root: Node) -> void:
	await _frames(4)
	HighContrastWalk.flush()
	PageTransition.settle(root)
	await _frames(2)
	HighContrastWalk.flush()


func test_every_screen_the_pack_reaches_headless_keeps_the_promise_under_high_contrast() -> void:
	var listed: Array = (load(HARNESS) as GDScript).get_script_constant_map()["SCREENS"]
	var names: Array = listed.map(func(s: Array) -> String: return String(s[0]))
	for screen in SCREENS:
		assert_has(names, screen, "%s is one of the review pack's screens" % screen)
	Settings.set_high_contrast(true)
	var found: Array[String] = []
	for k in [1.0, 2.0]:
		Settings.set_text_scale(k)
		var where := "x%.1f" % k
		# title
		var title := _scene(TITLE)
		await _settle_hc(title)
		found.append_array(_hc_violations(title, where + " title"))
		await _close(title)
		# hq (the Grid), then raid_setup
		_raid_campaign()
		var hq := _scene(HQ)
		await _settle_hc(hq)
		found.append_array(_hc_violations(hq, where + " hq"))
		hq.show_raid()
		await _settle_hc(hq)
		found.append_array(_hc_violations(hq, where + " raid_setup"))
		await _close(hq)
		RunManager.reset()
		# route
		var net := _scene(NETRUN)
		RunManager.new_campaign(1)
		net.start_run(1)
		await _settle_hc(net)
		found.append_array(_hc_violations(net, where + " route"))
		await _close(net)
		RunManager.reset()
		# combat_start
		RunManager.new_campaign(1)
		var holder := _holder()
		var combat: Control = load(COMBAT).instantiate()
		combat.auto_start = false
		holder.add_child(combat)
		combat.start_fight(&"collections_agent", 5)
		await _settle_hc(combat)
		combat.skip_motion()
		await _frames(2)
		HighContrastWalk.flush()
		found.append_array(_hc_violations(combat, where + " combat_start"))
		holder.queue_free()
		await _frames(2)
		RunManager.reset()
	assert_gt(_measured, 100, "the sweep read the screens' words (%d)" % _measured)
	assert_eq(found, [] as Array[String], "high contrast: opaque panels and 7:1 words on every screen reached")


# --- Drawn words (a view's own _draw) ----------------------------------------------------------------

## Every word HighContrast.draw_text / draw_lines drew under high contrast: light words at 7:1 on
## a BG outline at least outline_px thick, ink at 7:1 on PAPER; [] when so.
func _drawn_violations(drawn: Array) -> Array[String]:
	var out: Array[String] = []
	for d: Dictionary in drawn:
		var col: Color = d["color"]
		var fs: int = d["fs"]
		if int(d["outline"]) > 0:
			if int(d["outline"]) < HighContrast.outline_px(fs) or not Color(d["outline_color"], 1.0).is_equal_approx(HighContrast.BG):
				out.append("\"%s\": outline %d < %d" % [d["text"], d["outline"], HighContrast.outline_px(fs)])
			elif Palette.contrast(Color(col, 1.0), HighContrast.BG) < HighContrast.HC_MIN_CONTRAST - 0.01:
				out.append("\"%s\": %.2f:1 on its outline" % [d["text"], Palette.contrast(Color(col, 1.0), HighContrast.BG)])
		elif Palette.contrast(Color(col, 1.0), Palette.PAPER) < HighContrast.HC_MIN_CONTRAST - 0.01:
			out.append("\"%s\": ink %.2f:1 on paper" % [d["text"], Palette.contrast(Color(col, 1.0), Palette.PAPER)])
	return out


func _redraw_all(root: Node) -> void:
	for n in root.find_children("*", "CanvasItem", true, false):
		(n as CanvasItem).queue_redraw()
	if root is CanvasItem:
		(root as CanvasItem).queue_redraw()


func test_drawn_words_keep_the_promise_under_high_contrast_combat_numbers_and_card_names() -> void:
	Settings.set_high_contrast(true)
	for k in [1.0, 2.0]:
		Settings.set_text_scale(k)
		RunManager.new_campaign(1)
		var holder := _holder()
		var combat: Control = load(COMBAT).instantiate()
		combat.auto_start = false
		holder.add_child(combat)
		combat.start_fight(&"collections_agent", 5)
		await _settle_hc(combat)
		combat.skip_motion()
		Motion.force_live = true
		var drawn: Array = []
		HighContrast.drawn = drawn
		combat.fx_layer.number(Vector2(400, 300), "-11", Palette.HARM, &"number_float")
		combat.fx_layer.number(Vector2(800, 300), "+3", Palette.CELL_ACID, &"number_float")
		_redraw_all(combat)
		await _frames(2)
		HighContrast.drawn = null
		Motion.force_live = false
		var texts: Array = drawn.map(func(d: Dictionary) -> String: return String(d["text"]))
		assert_has(texts, "-11", "x%.1f: the FX damage number is drawn through the kit" % k)
		assert_has(texts, "+3", "x%.1f: and a gain" % k)
		var cards: Array[Node] = combat.find_children("*", "ZineCard", true, false)
		assert_gt(cards.size(), 0, "a hand to read")
		for c: Node in cards:
			if (c as CanvasItem).is_visible_in_tree():
				assert_has(texts, String(c.card_title).to_upper(), "x%.1f: card name %s drawn through the kit" % [k, c.card_title])
		assert_gt(drawn.size(), 30, "x%.1f: the fight's drawn words were read (%d)" % [k, drawn.size()])
		assert_eq(_drawn_violations(drawn), [] as Array[String], "x%.1f: every drawn word at 7:1 on its backing" % k)
		combat.skip_motion()
		holder.queue_free()
		await _frames(2)
		RunManager.reset()


# --- L80, L81: SAVED and the tutorial's Next --------------------------------------------------------

func test_under_high_contrast_saved_holds_still_at_seven_to_one_then_goes() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
		Fx.apply_settings()
	Settings.set_high_contrast(true)
	Fx.saved_screen = SCREEN
	Fx.show_saved()
	await _frames(4)
	var l := Fx.saved_label
	assert_eq(l.modulate.a, 1.0, "shown whole, never a faint fade")
	assert_gte(Palette.contrast(l.get_theme_color(&"font_color"), HighContrast.BG), HighContrast.HC_MIN_CONTRAST, "7:1")
	assert_eq(l.get_theme_color(&"font_outline_color"), HighContrast.BG, "on an opaque keyline")
	assert_gte(l.get_theme_constant(&"outline_size"), HighContrast.outline_px(UiTheme.font_px(Fx.SAVED_FONT)))
	# Stepped through its time (no frame waits): whole until it goes, then gone.
	var hold := Motion.delay_of(&"saved_stamp")
	var fade := Motion.seconds(&"saved_stamp")
	Fx._saved_tween.custom_step(hold + fade * 0.5)
	assert_eq(l.modulate.a, 1.0, "mid-way through the fade time: still whole")
	Fx._saved_tween.custom_step(fade)
	assert_eq(l.modulate.a, 0.0, "then not shown")
	Fx._saved_tween.kill()
	l.modulate.a = 0.0
	Fx.saved_screen = Rect2()


func test_under_high_contrast_next_stays_whole_at_seven_to_one() -> void:
	Motion.force_live = true
	Settings.set_high_contrast(true)
	var host := _holder()
	host.theme = UiTheme.build(Settings.text_scale)
	var t := TutorialOverlay.new(Vector2(300, 400))
	host.add_child(t)
	t.step = 5  # RESISTANCE: only Next moves it on (it pulses out of high contrast)
	t.page = 0
	t.fit(Vector2(300, 400))
	await _frames(2)
	HighContrastWalk.flush()
	assert_false(t.next_pulsing(), "no alpha pulse under high contrast")
	assert_eq(t.next_button.modulate.a, 1.0)
	var fc := t.next_button.get_theme_color(&"font_color")
	assert_gte(Palette.contrast(fc, HighContrastWalk.backing_of(t.next_button)), HighContrast.HC_MIN_CONTRAST, "Next at 7:1")
	Settings.set_high_contrast(false)
	t.fit(Vector2(300, 400))
	assert_true(t.next_pulsing(), "off: it pulses as before")


# --- 12Q-HQ: the DECRYPTED stamp stays in its slot -----------------------------------------------

func test_the_decrypted_stamp_fits_its_slot_at_every_text_size() -> void:
	var slot := DecryptedHoloPanel.STAMP_SLOT
	assert_eq(DecryptedHoloPanel.stamp_px(slot, 1.0), UiTheme.font_px_at(UiTheme.HEADING, 1.0), "at 1.0 the stamp's own size")
	for k in [1.0, 1.6, 2.0]:
		var px := DecryptedHoloPanel.stamp_px(slot, k)
		var sz := Palette.display().get_string_size(DecryptedHoloPanel.STAMP_WORD, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
		assert_lte(DecryptedHoloPanel.stamp_width(sz), slot.x, "x%.1f: the tilted stamp inside its slot" % k)
	assert_lte(DecryptedHoloPanel.stamp_px(slot, 2.0), UiTheme.font_px_at(UiTheme.HEADING, 2.0))
