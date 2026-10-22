extends GutTest
## RAID-FIX B (Raid Setup display): the chip's never-folding outcome block (B1), threat stats on the
## THREAT INTEL rows (B2), effect words before placing (B3/B4), and the A-079 fixes (B5, B6).
## Views read the rules' own numbers (RaidOutcome), so the display equals the result.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
## The A-079 gap: the focus bracket stands 10 px outside the STATION line, so the warning keeps 8 px more.
const BRACKET_OUT := 10.0
const GAP_MIN := 8.0

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	Settings.set_text_scale(1.0)
	AudioDirector.muted = true
	RunManager.save_slot = "gut_raid_fix_b"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


## A solace campaign with the first Site off home claimed as a safehouse (one station slot), two
## turrets in the Armory (undeployed), `heat`, a raid pending; `home_integrity` > 0 sets home low.
func _campaign(heat: int, home_integrity: int = -1) -> StringName:
	RunManager.new_campaign(1)
	var corp := RunManager.lookup().get_content(&"solace") as CorporationData
	var home := RunManager.lookup().get_content(RunManager.DEFAULT_HOME) as HomeServerVariantData
	RunManager.corporation = corp
	RunManager.campaign = CampaignRules.new_campaign(corp, RunManager.config(), RunManager.lookup(), 1,
		RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, 0, home)
	var c := RunManager.campaign
	c.schematics = 400
	var first: StringName = corp.city_grid.get_site(c.grid.home_site_id).links[0]
	var run := RunState.new()
	run.site_id = first
	CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), first, &"safehouse")
	c.armory = [&"turret", &"turret"]
	c.heat = heat
	if home_integrity > 0:
		c.grid.home_integrity = home_integrity
	CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")
	return first


func _raid_page(site: StringName) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(1)
	hq.selected_site = site
	hq.show_raid()
	await _frames(6)
	return hq


func _labels(chip: Control) -> Dictionary:
	var out := {}
	for l in chip.find_children("*", "Label", true, false):
		out[l.name] = l
	return out


func test_the_chip_prints_the_whole_outcome_at_heat_75_and_never_folds_it() -> void:
	var site := _campaign(75, 12)
	var hq := await _raid_page(site)
	var chip := hq._panel.get_node_or_null("Projection") as ForecastChip
	assert_not_null(chip, "the forecast chip")
	var projection := RunManager.project_raid()
	var out := RaidOutcome.project(projection, RunManager.config())
	var labels := _labels(chip)
	assert_true(labels.has("ForecastVerdict"), "the verdict word")
	assert_eq((labels["ForecastVerdict"] as Label).text, RaidVerdict.of_projection(projection).get_slice("\n", 0), "A's one verdict word")
	assert_true(labels.has("HomeForecast"), "Home delta")
	assert_string_contains((labels["HomeForecast"] as Label).text, str(int(out["home_after"])))
	if int(out["down"]) + int(out["taken"]) > 0:
		assert_true(labels.has("NodesForecast"), "nodes DOWN / TAKEN")
	if int(out["heat_delta"]) != 0:
		assert_true(labels.has("HeatForecast"), "Heat delta")
		assert_string_contains((labels["HeatForecast"] as Label).text, TextDb.signed(int(out["heat_delta"])))
	if int(out["schematics_delta"]) != 0:
		assert_true(labels.has("SchematicsForecast"), "Schematics delta")
	# The work order may fold its flavour rows (the MORE tab); the outcome block is on the chip and shows.
	for n in ["ForecastVerdict", "HomeForecast"]:
		assert_true((labels[n] as Control).is_visible_in_tree(), "%s shows" % n)
	# Every verdict word fits the chip (no word cut at the chip's edge).
	for l: Label in labels.values():
		if l.is_visible_in_tree() and l.text != "":
			var fs := l.get_theme_font_size(&"font_size")
			var w := l.get_theme_font(&"font").get_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			assert_true(w <= l.size.x + 1.0 or l.autowrap_mode != TextServer.AUTOWRAP_OFF, "'%s' is not cut" % l.text)
	assert_true(chip.get_global_rect().end.x <= SCREEN.end.x, "chip on screen")


func test_a_lost_raid_shows_its_severity_colour_not_green() -> void:
	var site := _campaign(75, 5)
	var hq := await _raid_page(site)
	var chip := hq._panel.get_node("Projection") as ForecastChip
	var out := RaidOutcome.project(RunManager.project_raid(), RunManager.config())
	if int(out["tier"]) != RaidOutcome.Tier.CLEAN:
		assert_ne(chip.color, Palette.CELL_ACID, "a lost raid is never the green of HOLDS")
	assert_eq(chip.color, RaidVerdict.tier_color_projection(RunManager.project_raid(), RunManager.config()), "A's tier colour")


func test_threat_rows_show_hp_and_damage() -> void:
	var site := _campaign(25)
	var hq := await _raid_page(site)
	var projection := RunManager.project_raid()
	var groups: Array = hq.raid_route_groups(projection)
	assert_gt(groups.size(), 0, "the raid has a route")
	# One kind on the route: its numbers ride on the threat's line; several kinds get a ThreatStats_ line.
	var line := hq._panel.find_child("ThreatStats_A", true, false) as Label
	if line == null:
		line = hq._panel.find_child("Threats_A", true, false) as Label
	assert_not_null(line, "route A carries its threats' numbers")
	assert_string_contains(line.text, "HP ")
	assert_string_contains(line.text, "DMG ")
	# The numbers are the threats' own at this raid (the event's integrity).
	for e in projection.events:
		if String(e.get("type", "")) == "threat_enters":
			assert_string_contains(line.text, "HP %d" % int(e["integrity"]))
			break


func test_a_placeable_asset_says_what_it_changes_before_placing() -> void:
	var site := _campaign(25)
	var hq := await _raid_page(site)
	var card := hq._panel.find_child("Asset_turret", true, false) as Control
	assert_not_null(card, "the turret card")
	var words: String = hq.asset_effect_words(0, site)
	assert_ne(words, "", "the effect words")
	assert_true(card.has_meta(&"effect_words"), "the card carries them")
	assert_string_contains(card.tooltip_text.replace("
", " "), words)
	# Pointed at (hover or focus), the words show beside the cards, whatever else crowds the column.
	hq.point_card(0)
	var plate := hq._panel.find_child("HandEffect", true, false) as Control
	assert_not_null(plate, "the hand's effect plate")
	assert_true(plate.visible, "it shows while a card is pointed at")
	assert_string_contains((hq._panel.find_child("HandEffectWords", true, false) as Label).text, words)
	hq.hide_if_placed()
	assert_false(plate.visible, "and hides when the card is left")
	# Exact: placing it gives the words' verdict (preview equals result).
	var c := RunManager.campaign
	var now := RunManager.project_raid()
	var copy := c.duplicate_state()
	CampaignRules.deploy_asset(copy, RunManager.config(), RunManager.lookup(), 0, site)
	var then := CampaignRules.project_raid(copy, RunManager.corporation, RunManager.config(), RunManager.lookup(), RunManager.pending_raid())
	assert_eq(words, RaidVerdict.if_placed_words(RaidOutcome.if_placed(now, then, site, &"turret"), hq.outcome_word))


func test_the_no_crew_confirm_says_to_station_from_here_and_what_it_gains() -> void:
	var site := _campaign(25, 12)
	var hq := await _raid_page(site)
	var best: String = hq.best_station_words()
	var who: OperativeState = hq.selected_op()
	var e: Dictionary = hq.station_effect(who.id, site)
	if String(e["words"]) != "":
		assert_ne(best, "", "a post that helps is named")
		assert_string_contains(best, String(e["words"]).left(4))
	hq.request_start_defense()
	await _frames(2)
	var d := hq._defense_confirm as ConfirmDialog
	assert_not_null(d, "the confirm opens with nobody stationed")
	var texts := PackedStringArray()
	for l in d.find_children("*", "Label", true, false):
		texts.append((l as Label).text)
	var all := "\n".join(texts)
	assert_string_contains(all.to_upper(), "STATION")
	if best != "":
		assert_string_contains(all, best)


func test_the_warning_has_a_backing_plate_and_clear_gap_under_the_station_line() -> void:
	var site := _campaign(25, 12)
	var hq := await _raid_page(site)
	var station := hq._panel.find_child("StationCrew", true, false) as Control
	var warn := hq._panel.find_child("NoCrewWarning", true, false) as Control
	assert_not_null(station, "the STATION line")
	assert_not_null(warn, "the NO CREW warning")
	var plate := warn.get_parent() as PanelContainer
	assert_not_null(plate, "the warning stands on a plate")
	var box := plate.get_theme_stylebox("panel") as StyleBoxFlat
	assert_eq(box.bg_color, PaletteSkins.chrome(Palette.TERMINAL_BG), "TERMINAL_BG backing")
	var below := station.get_global_rect().end.y
	var eff := hq._panel.find_child("StationEffect", true, false) as Control
	if eff != null:
		below = eff.get_global_rect().end.y
	assert_gte(plate.get_global_rect().position.y - below, GAP_MIN, "the warning clears the line above it by 8 px")
	assert_gte(plate.get_global_rect().position.y - station.get_global_rect().end.y, BRACKET_OUT + GAP_MIN - 0.5 if eff == null else GAP_MIN, "and the focus bracket's bottom by 8 px")


func test_the_claimed_wash_is_about_half_the_fill() -> void:
	assert_almost_eq(CityMapOverlay.MARK_FILL_ALPHA_CLAIMED, CityMapOverlay.MARK_FILL_ALPHA * 0.5, 0.01)
	assert_almost_eq(NeonCity.MARK_FILL_CLAIMED, NeonCity.MARK_FILL * 0.5, 0.01)
	assert_eq(Palette.CELL_TURF, Color("#D4FF00"), "the token is unchanged")
