extends GutTest
## Change plan 1, W2-A3: labels in place, the combat legend, status definitions wherever a status is
## named (R2) and what hovering a loot slot says (R3).

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = "gut_w2_a3"
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func test_a_named_status_comes_with_its_definition() -> void:
	var fw := load("res://content/firmware/hardened.tres") as FirmwareData
	var tip := Codex.describe(fw)
	assert_true(tip.contains(String(Codex.STATUS_TEXT[RC.Status.ENCRYPTED])), "HARDENED's tooltip says what ENCRYPTED does")
	assert_eq(Codex.with_status_defs(String(Codex.STATUS_TEXT[RC.Status.ENCRYPTED])), String(Codex.STATUS_TEXT[RC.Status.ENCRYPTED]), "a definition adds nothing to itself")
	assert_eq(Codex.with_status_defs("Deals damage."), "Deals damage.", "no status named: unchanged")
	var loot := NetrunScript.loot_tip(fw)
	assert_true(loot.contains(String(Codex.STATUS_TEXT[RC.Status.ENCRYPTED])), "the loot sticker's hover too")


func test_the_legend_lists_every_slice_status_tier_and_readout() -> void:
	var rows := CombatLegend.entries()
	var codes := PackedStringArray()
	for r in rows:
		codes.append(String(r["code"]))
		assert_ne(String(r["text"]), "", "%s says what it is" % r["code"])
	for t in Palette.SLICE_NAMES:
		var code := "1/0" if t == RC.SliceType.NULL else String(Palette.SLICE_NAMES[t])
		assert_true(codes.has(code), "slice %s" % code)
	for st in Codex.STATUS_TEXT:
		assert_true(codes.has(String(Palette.STATUS_GLYPHS[st])), "status %d" % st)
	for tier in Codex.TIER_TEXT:
		assert_true(codes.has(String(Palette.TIER_NAMES[tier])), "tier %d" % tier)
	for want in ["D 0", "HP -11", "RAM (-1 THIS PLAY)"]:
		assert_true(codes.has(want), want)


func test_chips_are_labelled_in_place() -> void:
	var dmg := {"kind": ResultChipModel.DAMAGE, "value": 6, "icon": "", "good": false}
	assert_eq(String(HudResultChips.parts(dmg)["words"]), "HP -6")
	var absorbed := {"kind": ResultChipModel.ABSORBED, "value": 4, "icon": "", "good": true}
	assert_eq(String(HudResultChips.parts(absorbed)["words"]), "BLOCKED (4")
	var ram := {"kind": ResultChipModel.RAM, "value": 1, "icon": "", "good": false}
	assert_eq(String(HudResultChips.parts(ram)["words"]), "RAM -1")
	var odds := ResultChipModel.odds_chip()
	assert_eq(String(HudResultChips.parts(odds)["words"]), "?", "a glyph-only chip keeps its mark")


func test_the_ram_header_says_what_the_negative_number_is() -> void:
	var bar := RamBar.new()
	add_child_autofree(bar)
	bar.set_ram(6, 12)
	bar.pending = -1
	assert_true(bar._label().contains("THIS PLAY"), bar._label())


func test_the_legend_opens_with_its_key_and_closes_again_at_every_text_scale() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var holder: Control = add_child_autofree(Control.new())
		holder.size = Vector2(1280, 720)
		var scene: Control = load(COMBAT).instantiate()
		scene.auto_start = false
		holder.add_child(scene)
		scene.start_fight(&"collections_agent", 7)
		await _frames()
		var ev := InputEventAction.new()
		ev.action = CombatLegend.ACTION
		ev.pressed = true
		scene._unhandled_input(ev)
		await _frames()
		var legend := scene.find_child("CombatLegend", true, false) as CombatLegend
		assert_not_null(legend, "x%.1f: L opens the legend" % scale)
		if legend != null:
			assert_true(Rect2(Vector2.ZERO, Vector2(1280, 720)).encloses(legend.get_global_rect()), "x%.1f: it sits on the screen" % scale)
			assert_not_null(scene._legend_button, "the chip is there for the pad's focus")
			scene._unhandled_input(ev)
			await _frames()
			assert_null(scene.find_child("CombatLegend", true, false), "x%.1f: the key closes it" % scale)
		holder.queue_free()
		await _frames(1)
		RunManager.reset()


func test_hovering_a_loot_slot_says_the_slice_and_its_firmware() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	DemoSetup.offer_loot(RunManager.netrun, ["barbed_wire"], "firmware")
	await _frames(2)
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(4)
	var op := RunManager.netrun.run.operative
	var mini := scene._panel.find_child("SpinnerMini", true, false) as SpinnerMini
	assert_not_null(mini)
	for k in op.slot_slice_ids.size():
		var tip := mini.pad(k).tooltip_text.replace("\n", " ")
		var sd := RunManager.lookup().get_content(op.slot_slice_ids[k]) as SliceData
		assert_true(tip.contains(Codex.SLICE_TYPE_TEXT[sd.slice_type].get_slice(": ", 1).left(20)) or tip.contains(sd.display_name), "slot %d names its slice: %s" % [k, tip])
		if op.slot_firmware_ids[k] == &"":
			assert_true(tip.contains("No Firmware installed"), "slot %d: none installed" % k)
	holder.queue_free()
