extends GutTest
## Animation pass ANIM-R4, city, raid, Heat, route and HQ part (H1-H11; DECISIONS "Animation
## pass - ANIM-R4 city, raid, heat, route and HQ"). Views only: every expectation reads the
## resolved state or the view's own layout.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]

var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r4_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.simulate = false
	CityBakeCache.shutdown()
	Motion.force_live = false
	Motion.use_config(null)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
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


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


# --- H2 / H3 / H4: raid feed and verdicts -------------------------------------------------------------

## A campaign against `corp_id` (ICE `ice`, home variant `home_id`) with the first Site off
## home claimed as `node_type` and, when `defended`, two turrets on it; a raid pending;
## `home_integrity` > 0 sets home low (a lost raid).
func _raid_campaign(corp_id: StringName, defended: bool, home_integrity: int = -1, ice: int = 0,
		home_id: StringName = RunManager.DEFAULT_HOME, node_type: StringName = &"firewall_relay") -> void:
	RunManager.new_campaign(1)
	var corp := RunManager.lookup().get_content(corp_id) as CorporationData
	var home := RunManager.lookup().get_content(home_id) as HomeServerVariantData
	RunManager.corporation = corp
	RunManager.campaign = CampaignRules.new_campaign(corp, RunManager.config(), RunManager.lookup(), 1,
		RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, ice, home)
	var c := RunManager.campaign
	c.schematics = 400
	var first: StringName = corp.city_grid.get_site(c.grid.home_site_id).links[0]
	var run := RunState.new()
	run.site_id = first
	CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), first, node_type)
	if defended:
		c.armory = [&"turret", &"turret"]
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	if home_integrity > 0:
		c.grid.home_integrity = home_integrity
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


func _home_variants() -> Array[StringName]:
	var out: Array[StringName] = []
	for id in RunManager.lookup().ids_of_class(&"HomeServerVariantData"):
		out.append(id)
	out.sort()
	return out


func test_the_verdict_is_all_hold_only_when_nothing_is_lost_for_every_corporation_home_and_ice() -> void:
	var cases := 0
	var lossy_but_won := 0
	var ice_top := RunManager.config().ice_ladder.size()
	for corp in CORPORATIONS:
		for home_id in _home_variants():
			for ice in [0, ice_top]:
				for setup in [[true, -1], [false, -1], [false, 3]]:
					_raid_campaign(corp, setup[0], setup[1], ice, home_id)
					if RunManager.pending_raid().is_empty():
						continue
					var projection := RunManager.project_raid()
					var forecast := RaidVerdict.of_projection(projection)
					RunManager.fight_raid()
					var r: Dictionary = RunManager.campaign.last_raid
					var tag := "%s %s ICE %d %s" % [corp, home_id, ice, setup]
					cases += 1
					var verdict := RaidVerdict.of_result(r)
					assert_eq(forecast, verdict, "%s: the forecast is the result's verdict" % tag)
					assert_false(verdict.contains("HOME HIT"), "%s: no HOME HIT" % tag)
					var any_lost := bool(r["campaign_lost"]) or int(r["home_after"]) < int(r["home_before"]) \
						or not (r.get("disabled", []) as Array).is_empty() or not (r.get("seized", []) as Array).is_empty()
					assert_eq(verdict == CityMapOverlay.tr_word(RaidVerdict.ALL_HOLD), not any_lost, "%s: ALL HOLD only when nothing is lost (%s)" % [tag, verdict.replace("\n", " / ")])
					if bool(r["won"]) and any_lost:
						lossy_but_won += 1
					# ANIM-R5 P18: a node counts once, by its outcome (Disabled then Seized is SEIZED).
					for sid in (r.get("disabled", []) if not bool(r["campaign_lost"]) else []):
						var outcome := String((r["nodes"] as Dictionary).get(sid, {}).get("outcome", ""))
						var word := RaidVerdict.SEIZED if outcome == "seized" else RaidVerdict.DISABLED
						assert_string_contains(verdict, CityMapOverlay.tr_word(word).get_slice(" ", 1), "%s: a fallen node is named by its outcome (%s)" % [tag, outcome])
					if bool(r["campaign_lost"]):
						assert_eq(verdict, CityMapOverlay.tr_word(RaidVerdict.LOST))
					# The map's banner speaks the same words: HOLDS only when home held.
					var fx := _play(RunManager.campaign, r)
					if bool(r["campaign_lost"]):
						assert_eq(fx.banner_text(), CityMapOverlay.tr_word(RaidVerdict.LOST), "%s: the banner and the stamp both say CAMPAIGN LOST" % tag)
					else:
						assert_string_contains(fx.banner_text(), "HOLDS", "%s: home held" % tag)
					fx.get_parent().queue_free()
	assert_gt(cases, 40, "raids for every corporation, home and ICE level")
	gut.p("H3 sweep: %d raids, %d won with a loss" % [cases, lossy_but_won])


## The resolved raid `r` played onto a fresh layer, all at once.
func _play(c: CampaignState, r: Dictionary) -> RaidFxLayer:
	var overlay := CityMapOverlay.new()
	add_child(overlay)
	var fx := RaidFxLayer.new(overlay)
	overlay.add_child(fx)
	fx.setup(r, c.grid.home_site_id, c.grid.home_max_integrity, Palette.corp_color(c.corporation_id))
	var events: Array[Dictionary] = [{"type": "raid_end", "won": r["won"], "steps": r.get("steps_run", 0)}]
	if bool(r["campaign_lost"]):
		events.push_front({"type": "home_lost", "step": 1})
	var at := 0.0
	for group in RaidBeats.group(events):
		var tl := RaidBeats.timeline(group)
		for b: Dictionary in tl["beats"]:
			fx.play_beat(b, at + float(b["t0"]))
		at += float(tl["seconds"])
	fx.clock = at + 100.0
	return fx


func test_the_verdict_names_each_loss() -> void:
	assert_eq(RaidVerdict.words(false, 0, 0, 0), CityMapOverlay.tr_word("ALL HOLD"))
	assert_eq(RaidVerdict.words(false, 0, 1, 0), CityMapOverlay.tr_word("%d DISABLED") % 1, "a node Disabled with every threat stopped is not ALL HOLD")
	assert_eq(RaidVerdict.words(false, 5, 1, 2), "%s\n%s\n%s" % [CityMapOverlay.tr_word("HOME %s") % "-5", CityMapOverlay.tr_word("%d DISABLED") % 1, CityMapOverlay.tr_word("%d SEIZED") % 2])
	assert_eq(RaidVerdict.words(true, 50, 0, 0), CityMapOverlay.tr_word("CAMPAIGN LOST"))
	var stamp: ForecastStamp = add_child_autofree(ForecastStamp.new("IF", RaidVerdict.words(false, 5, 1, 0)))
	stamp.size = Vector2(124, 124)
	assert_eq(stamp.verdict_lines().size(), 2, "one line per loss")
	var lay := stamp.layout()
	assert_true((lay["verdict"] as Rect2).size.y >= Palette.display().get_height(int(lay["verdict_size"])) * 2.0 - 0.5, "room for both lines")


func test_the_feed_names_a_stationed_operative_and_translated_threats() -> void:
	_raid_campaign(&"solace", false, -1, 0, RunManager.DEFAULT_HOME, &"safehouse")
	var c := RunManager.campaign
	var op := c.roster[0]
	var post: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
	CampaignRules.station(c, RunManager.lookup(), op.id, post)
	assert_eq(CampaignRules.stationed_site(c, op.id), post, "the operative guards the Site")
	# A threat name in the player's language (its TextDb key: the English display name had
	# no key of its own and never translated).
	var tr_x := Translation.new()
	tr_x.locale = "xx"
	var ids: Array = RunManager.lookup().ids_of_class(&"ThreatData")
	for id in ids:
		var td := RunManager.lookup().get_content(id) as ThreatData
		tr_x.add_message(TextDb.key_for(td, "display_name"), "XX-%s" % String(id).to_upper())
	TranslationServer.add_translation(tr_x)
	var locale := TranslationServer.get_locale()
	TranslationServer.set_locale("xx")
	var events := RunManager.fight_raid()
	var overlay := CityMapOverlay.new()
	add_child_autofree(overlay)
	var panel := RaidPlayoutPanel.new(overlay)
	add_child_autofree(panel)
	panel.results = c.last_raid
	panel.play(events, true)
	var text := panel.log_note.label.get_parsed_text()
	# Every event naming a threat carries its content id.
	for e in events:
		if e.has("threat"):
			assert_true(e.has("threat_content"), "%s carries the threat's content id" % e.get("type"))
	assert_string_contains(text, "XX-", "threat names are translated in the feed")
	assert_null(RegEx.create_from_string("(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % String(op.id)).search(text), "no operative id in the feed")
	# A recall line: the operative's name, never the id.
	var line := panel.feed_line({"type": "recalled", "step": 2, "operative": String(op.id), "site": post})
	assert_string_contains(line, op.name, "the feed names the operative")
	assert_false(line.contains(String(op.id)), "and never shows the id (%s)" % line)
	# The map's markers name the threats as the feed does, in the player's language.
	assert_false(panel._threat_names.is_empty())
	for id in panel._threat_names:
		assert_true(String(panel._threat_names[id]).begins_with("XX-"), "marker name %s translated" % panel._threat_names[id])
	# ANIM-R4 H7: the node's hover text is translated too.
	tr_x.add_message(CityMapOverlay.TIP_THREATS, "XX-MENACES %s.")
	tr_x.add_message(CityMapOverlay.TIP_HERE, "XX-ICI.")
	overlay.set_graph([{"id": post, "at": Vector2(3, 3), "label": "Site", "here": true}], [])
	overlay.threat_markers = {post: [panel._threat_names.values()[0]]}
	var tip := overlay.tip_of(post)
	assert_string_contains(tip, "XX-MENACES XX-", "Threats here, translated, with the translated name")
	assert_string_contains(tip, "XX-ICI.", "You are here, translated")
	TranslationServer.set_locale(locale)
	TranslationServer.remove_translation(tr_x)


# --- H5 / H6: Heat -----------------------------------------------------------------------------------

func test_heat_consequences_are_keyed_exported_translated_whole_sentences() -> void:
	RunManager.new_campaign(1)
	var file := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for t in RunManager.config().heat_thresholds:
		assert_ne(String(t.id), "", "threshold %d has an id" % t.heat)
		var key := TextDb.key_for(t, "event_text")
		assert_eq(key, "HeatThresholdData.%s.event_text" % t.id)
		assert_string_contains(file, key + ",", "strings.csv carries %s (tools/export_text.gd ran)" % key)
		var text := t.event_text
		assert_true(text.ends_with("."), "%s ends a sentence" % key)
		assert_eq(text.left(1), text.left(1).to_upper(), "%s starts a sentence" % key)
		assert_false(text.begins_with("Raid. "), "%s: not a fragment" % key)
	var tr_x := Translation.new()
	tr_x.locale = "xx"
	tr_x.add_message("HeatThresholdData.heat_25.event_text", "XX La corporation attaque.")
	TranslationServer.add_translation(tr_x)
	var locale := TranslationServer.get_locale()
	TranslationServer.set_locale("xx")
	assert_eq(HeatPoster.consequence(30), "XX La corporation attaque.", "the band's consequence in the player's language")
	TranslationServer.set_locale(locale)
	TranslationServer.remove_translation(tr_x)


func test_the_heat_banner_names_heat_band_and_threshold_and_the_band_word_follows_the_number() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var p := HeatPoster.new(false)
	holder.add_child(p)
	var marks: Array[int] = [25, 50, 75]
	p.set_heat(30, 100, marks)
	p._banner_at = 25
	assert_eq(p.banner_text(), "HEAT 30 · %s (25+)" % tr(HeatPoster.BAND_WORDS[1]).to_upper(), "the Heat now, the band crossed and where it starts")
	# While the number rolls up from 21 the band word is still the band of the number shown.
	p.shown_heat = 21.0
	assert_eq(p.shown_band(), 0, "21 shows COOL")
	p.shown_heat = 25.0
	assert_eq(p.shown_band(), 1, "25 shows NOTICED")
	p._banner_at = 0
	p.set_heat(5, 100, marks)
	assert_eq(p.banner_text(), "HEAT 5 · %s" % tr(HeatPoster.BAND_WORDS[0]).to_upper())


## The banner's whole tilted box (sub-lines included) inside `room` (local px).
func _box_inside(p: HeatPoster, room: Rect2) -> bool:
	for c in p.banner_corners():
		if not room.grow(0.75).has_point(c):
			return false
	return true


func test_the_heat_banner_box_fits_both_posters_at_every_text_size_and_long_words() -> void:
	RunManager.new_campaign(1)
	var tr_long := Translation.new()
	tr_long.locale = "xx"
	tr_long.add_message("hunted", "Überwachungsverfolgungsstufe")
	tr_long.add_message("HeatThresholdData.heat_75.event_text", "Die Konzernsicherheitsverwaltungsbehörde schickt Überfallkommandos. Solange die Hitze bei 75 oder mehr bleibt, sind Überfälle 25% stärker.")
	TranslationServer.add_translation(tr_long)
	var locale := TranslationServer.get_locale()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		for loc in [locale, "xx"]:
			TranslationServer.set_locale(loc)
			for kind in [true, false]:
				for height in ([0.0] if kind else [96.0, 134.0]):
					var p := HeatPoster.new(kind)
					holder.add_child(p)
					p.size = p.custom_minimum_size if kind else Vector2(170, height)
					p.heat = 80
					p._banner_at = 75
					var tag := "%.1f %s poster=%s h=%.0f" % [scale, loc, kind, p.size.y]
					assert_true(_box_inside(p, Rect2(Vector2.ZERO, p.size)), "%s: the whole banner stays on the poster" % tag)
					assert_true(_box_inside(p, p.banner_layout()["room"]), "%s: in its room (under the bar / over the header)" % tag)
					if not kind and p.size.y >= 134.0:
						assert_eq(p.banner_layout()["room"], p.banner_room(), "%s: the combat poster's banner hangs under the bar" % tag)
					var f := Palette.display()
					for line in p.banner_lines()["lines"]:
						assert_true(f.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, p.banner_font_size()).x <= p.size.x, "%s: '%s' fits across" % [tag, line])
					for line in p.sub_lines():
						assert_true(Palette.mono().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, p.sub_font_size()).x <= p.size.x - HeatPoster.BANNER_PAD * 2.0, "%s: sub-line '%s' fits (long words broken)" % [tag, line])
					var ll := p.letter_layout(3)
					var y := HeatPoster.POSTER_BLOCK_TOP if kind else 0.0
					var number := Rect2(Vector2(float(ll["num_x"]), y + 4.0), Vector2(float(ll["num_w"]), HeatPoster.NUMBER_FONT))
					for c in p.banner_corners():
						assert_false(number.grow(-1.0).has_point(c), "%s: never over the number" % tag)
					p.free()
	TranslationServer.set_locale(locale)
	TranslationServer.remove_translation(tr_long)


func test_the_combat_heat_banner_never_spills_over_the_daemon_row() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var combat := _scene(COMBAT)
		combat.start_fight(&"triage_unit", 7)
		await _frames(4)
		var p: HeatPoster = combat.heat_poster
		p.heat = 80
		p._banner_at = 75
		var row: Rect2 = combat.daemon_row.get_global_rect()
		var xf := p.get_global_transform()
		for c in p.banner_corners():
			assert_true((xf * c).y <= row.position.y + 0.5, "%.1f: the banner ends above the Daemons (%.0f > %.0f)" % [scale, (xf * c).y, row.position.y])
		# ANIM-R5 P9: the consequence is the flat note beside the poster now.
		assert_false(p.note_lines().is_empty(), "%.1f: the consequence still shows, in the note" % scale)
		combat.get_parent().queue_free()
		await _frames(1)


## Every text control's box under `root` inside what clips it, across (a word cut at the
## column's edge); `out` gets "name 'text'" for each that is not.
func _clip_rect(c: Control) -> Rect2:
	var r := Rect2(-1e6, -1e6, 2e6, 2e6)
	var p := c.get_parent()
	while p != null and p is Control:
		if (p as Control).clip_contents or p is ScrollContainer:
			r = r.intersection((p as Control).get_global_rect())
		p = p.get_parent()
	return r


func _clipped(root: Node, out: Array) -> void:
	for n in root.get_children():
		if n is Control and (n as Control).is_visible_in_tree():
			var c := n as Control
			if c is Label or c is Button or c is Badge:
				var text := String(c.get("text"))
				if text != "":
					var fs := c.get_theme_font_size(&"font_size")
					var w := c.get_theme_font(&"font").get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
					var wraps: bool = c is Badge or c.get("autowrap_mode") != TextServer.AUTOWRAP_OFF
					var g := c.get_global_rect()
					var vis := _clip_rect(c)
					if (not wraps and w > c.size.x + 1.0) or g.position.x < vis.position.x - 1.0 or g.end.x > vis.end.x + 1.0 or g.end.x > SCREEN.end.x + 1.0:
						out.append("%s '%s'" % [c.name, text.left(40)])
		_clipped(n, out)


# --- H11 a: raid readability ---------------------------------------------------------------------------

func _hud_value(hq: Control, tag: String) -> String:
	for it in hq.hud.stats.items:
		if String(it[0]) == tag:
			return String(it[1])
	return ""


func test_the_raids_top_bar_changes_with_the_line_that_changes_it() -> void:
	# A lost raid from Heat 1: the feed says where Heat went from and to, and the top bar
	# shows the old Heat and RAIDS until the lines that change them are told.
	_raid_campaign(&"solace", false)
	var c := RunManager.campaign
	c.heat = 1
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(2)
	hq.hud_heat_shown = c.heat
	hq.hud_raids_shown = c.pending_raids.size()
	var raids_before := c.pending_raids.size()
	var events := RunManager.fight_raid()
	hq._refresh_status()
	assert_eq(_hud_value(hq, "HEAT"), "1", "Heat holds before its line")
	assert_eq(_hud_value(hq, "RAIDS"), str(raids_before), "RAIDS holds before the raid's end line")
	var panel := RaidPlayoutPanel.new(null)
	add_child_autofree(panel)
	panel.results = c.last_raid
	panel.event_shown.connect(hq._on_raid_event_shown)
	var heat_line := ""
	for e in events:
		var t := String(e.get("type", ""))
		var line := panel.feed_line(e)
		if t == "heat" and int(e.get("amount", 0)) != 0:
			heat_line = line
			assert_eq(_hud_value(hq, "HEAT"), "1", "still the old Heat as its line comes")
		panel.event_shown.emit(e)
		if t == "heat" and int(e.get("amount", 0)) != 0:
			assert_eq(_hud_value(hq, "HEAT"), str(int(e["after"])), "the Heat changes with its line")
			assert_eq(int(e["before"]) + int(e["amount"]), int(e["after"]), "the line's arithmetic holds")
			assert_string_contains(line, "%d → %d" % [int(e["before"]), int(e["after"])], "it says from and to")
		if t == "raid_end":
			# ANIM-R6 C11: it drops with the verdict (the playout's end), not the "Raid over" line.
			assert_eq(_hud_value(hq, "RAIDS"), str(raids_before), "RAIDS holds through the raid's end line")
	assert_ne(heat_line, "", "a lost raid tells its Heat")
	assert_string_contains(heat_line, "1 → ", "from Heat 1")


func test_a_hit_line_says_the_hp_it_took_as_the_map_does() -> void:
	for corp in CORPORATIONS:
		_raid_campaign(corp, false)
		var c := RunManager.campaign
		var events := RunManager.fight_raid()
		var panel := RaidPlayoutPanel.new(null)
		add_child_autofree(panel)
		panel.results = c.last_raid
		panel.play(events, true)
		var r: Dictionary = c.last_raid
		for id in r["nodes"]:
			var n: Dictionary = r["nodes"][id]
			assert_eq(int(panel._hp.get(String(id), -1)), int(n["after"]), "%s %s: the feed's HP ends where the node's label does" % [corp, id])
		for e in events:
			if String(e.get("type", "")) == "node_hit":
				var hit_site := String(e["site"])
				assert_string_contains(panel.log_note.label.get_parsed_text(), "%s → " % int(r["nodes"][hit_site]["before"]), "%s: the first hit's line starts from the node's HP" % corp)
				break


## WCAG contrast of `a` against `b` (both opaque).
static func _contrast(a: Color, b: Color) -> float:
	var la := a.get_luminance()
	var lb := b.get_luminance()
	return (maxf(la, lb) + 0.05) / (minf(la, lb) + 0.05)


func test_a_threat_token_stands_out_on_every_node_colour() -> void:
	var nodes: Array[Color] = [Palette.CELL_PINK, Palette.CELL_ACID, Palette.RESIST_GOLD, Palette.NET_CYAN, Palette.CELL_TURF]
	for corp in CORPORATIONS:
		nodes.append(Palette.corp_color(corp))
	var halo := RaidFxLayer.TOKEN_HALO_COLOR
	assert_eq(halo.a, 1.0, "an opaque halo: no node colour shows through (red over pink read pink)")
	assert_gt(_contrast(Palette.PAPER, halo), 7.0, "the paper rim stands out on the halo")
	for col in nodes:
		# WCAG non-text contrast (3:1): the token's edge (its paper rim or its dark halo)
		# stands out on the node under it.
		var edge := maxf(_contrast(halo, col), _contrast(Palette.PAPER, col))
		assert_gt(edge, 3.0, "the token stands out on %s (%.1f)" % [col.to_html(false), edge])
		assert_gt(_contrast(halo, col) + _contrast(Palette.PAPER, col), 7.0, "halo and rim together on %s" % col.to_html(false))
	assert_gt(RaidFxLayer.TOKEN_HALO, 1.0, "the halo is wider than the diamond")


func test_raid_incoming_is_a_large_amber_stamp_naming_the_corporation_held_a_second() -> void:
	_raid_campaign(&"meridian", false)
	RunManager._before_switch = func() -> void: pass
	var note := RunManager.jack_note()
	RunManager._before_switch = Callable()
	var corp_name := TextDb.t(RunManager.corporation, "display_name")
	assert_string_contains(note, corp_name, "the stamp names the corporation")
	assert_string_contains(note, tr("RAID INCOMING\n%s").get_slice("\n", 0), "and says RAID INCOMING")
	assert_true(Fx.note_hold() >= 1.0, "held at least a second (%.2f s)" % Fx.note_hold())
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		Fx._note = note
		Fx._show_note(SCREEN.size)
		assert_true(Fx.note_label.visible)
		assert_eq(Fx.note_label.get_theme_color(&"font_color"), Palette.CRT_AMBER, "amber")
		assert_true(Fx.note_label.get_theme_font_size(&"font_size") >= roundi(Fx.NOTE_FONT * scale), "large")
		assert_string_contains(Fx.note_label.text, corp_name.to_upper())
		assert_true(SCREEN.grow(1.0).encloses(Fx.note_label.get_global_rect()), "on the screen at %.1f" % scale)
		Fx._hide_connect()
		assert_false(Fx.note_label.visible, "gone with the cover")


# --- H11 b: the asset drop and the forecast ------------------------------------------------------------

func test_a_drop_runs_its_road_to_core_and_every_forecast_change_reads_as_arrows() -> void:
	assert_eq(CityMapOverlay.change_text(45, 50), "45 → 50 ▲", "a gain")
	assert_eq(CityMapOverlay.change_text(50, 45), "50 → 45 ▼", "a loss")
	assert_true(Palette.mono_arrows().has_char(0x2192) and Palette.mono_arrows().has_char(0x25B2), "the arrows' lettering draws them (display fallback)")
	assert_eq(Palette.mono_for("HP 50 → 40"), Palette.mono_arrows(), "text with an arrow takes it")
	assert_eq(Palette.mono_for("HP 50"), Palette.mono(), "other text keeps the plain face (its line height)")
	var hq := _scene(HQ)
	await _frames(1)
	_raid_campaign(&"solace", false)
	hq.show_raid()
	await _frames(3)
	var c := RunManager.campaign
	var site: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
	var road: Array = hq.threat_road(site)
	assert_eq(road.front(), site, "the road starts at the defence's node")
	assert_eq(road.back(), c.grid.home_site_id, "and ends at CORE")
	c.armory = [&"turret"]
	hq.deploy_asset(0, site)
	await _frames(2)
	var overlay: CityMapOverlay = hq.city_overlay
	assert_eq(overlay._drop.get("road", []), road, "the drop carries the road")
	assert_eq(overlay.road_t, 1.0, "headless: the pulse at its end at once")
	assert_eq(overlay.change_t, 1.0)
	for ch: Dictionary in overlay.drop_changes():
		if StringName(ch["site"]) == c.grid.home_site_id:
			var core: Dictionary = overlay._node_dict(c.grid.home_site_id)
			assert_string_contains(String(core.get("result", "")), "→ %d" % int(ch["to"]), "CORE's label and the float show the same number")
	# The raid setup's rows use the arrows too.
	var arrows := 0
	for b in hq._panel.find_children("*", "Badge", true, false):
		if (b as Badge).text.contains(" > "):
			fail_test("a forecast still reads 'a > b': %s" % (b as Badge).text)
		if (b as Badge).text.contains("→"):
			arrows += 1
			assert_true((b as Badge)._font().has_char(0x2192), "a badge writing a change draws its arrow")
	assert_gt(arrows, 0, "the forecast badges read a → b")


# --- H11 c: the route ---------------------------------------------------------------------------------

func test_a_move_shows_the_new_choices_at_once_the_marker_off_them_and_the_trail() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	RunManager.new_campaign(1)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	await _frames(3)
	var s := RunManager.netrun
	var to: StringName = s.available_nodes()[0]
	scene.enter_node(to)
	var overlay: CityMapOverlay = scene.city_overlay
	var next: Array[StringName] = []
	for n in s.run.current_node().get("next", []):
		next.append(n)
	assert_eq(NetrunScript.view_choices(s), next, "the view's choices are the node's next ones while it plays")
	if overlay != null and is_instance_valid(overlay) and scene._travelling:
		var labelled: Array[StringName] = []
		for n in overlay.nodes:
			if n.get("next", false):
				labelled.append(n["id"])
		labelled.sort()
		var want := next.duplicate()
		want.sort()
		assert_eq(labelled, want, "the map's [1] / [2] labels are on the new choices as the move starts")
		var row: Node = scene._panel.find_child("RouteNodes", true, false)
		var buttons := 0
		for b in row.get_children():
			if b is Button and (b as Button).visible and not b.is_queued_for_deletion():
				buttons += 1
		assert_eq(buttons, next.size(), "the ROUTE window lists the new choices")
		for u in [0.0, 0.5, 1.0]:
			overlay.travel_t = u
			var here := overlay.here_marker_pos()
			for id in next:
				assert_true(here.distance_to(overlay.icon_at(id)) > overlay.icon_radius(overlay._node_dict(id)), "the marker is never on a choice (t %.1f)" % u)
		scene._end_travel()
	else:
		fail_test("the move did not play on the route map")
	# The walked route stays as a faint trail: one move on, the link walked is the trail.
	if not s.run.visited.has(to):
		s.run.visited.append(to)
	s.run.current_node_id = next[0]
	var g: Dictionary = scene.route_graph()
	var trail: Array = []
	for e: Dictionary in g["edges"]:
		if e.get("trail", false):
			trail.append([e["a"], e["b"]])
			assert_lt((e["color"] as Color).a, 0.6, "faint")
			assert_false(bool(e.get("dashed", true)), "a solid line")
	assert_eq(trail, [[to, next[0]]], "the walked link is the trail")


# --- H11 d: territory -----------------------------------------------------------------------------------

func test_the_claimed_stamp_keeps_off_the_sites_name_and_the_side_panel_never_clips() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		_raid_campaign(&"solace", true)
		var c := RunManager.campaign
		var hq := _scene(HQ)
		await _frames(1)
		var site: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
		for sid in [site, &""]:
			hq.selected_site = sid
			hq.show_grid()
			await _frames(3)
			var out := []
			_clipped(hq._panel, out)
			assert_eq(out, [], "%.1f %s: no word cut at the side panel's edge" % [scale, sid])
		hq.show_raid()
		await _frames(3)
		var cut := []
		_clipped(hq._panel, cut)
		assert_eq(cut, [], "%.1f raid setup: no word cut" % scale)
		hq.selected_site = site
		hq.show_grid()
		await _frames(3)
		# A claim's stamp beside or below the Site's name, never on it.
		var city: NeonCity = hq.wireframe.city
		var before := c.duplicate_state()
		before.grid.site(site)["status"] = GridState.SiteStatus.CORPORATE
		city.mark_changes(CityInfluence.of(before, RunManager.corporation), CityInfluence.of(c, RunManager.corporation))
		var overlay: CityMapOverlay = hq.city_overlay
		city.stamp_avoid = overlay.stamp_avoid_rects()
		var labels := overlay.label_rects()
		var checked := 0
		for m: Dictionary in city.marks:
			var spot := NeonCity._tilted_bounds(city.stamp_rect(m), NeonCity.MARK_TILT)
			for key in labels:
				if String(key) == String(site):
					checked += 1
					assert_false(spot.intersects(overlay.get_transform() * (labels[key] as Rect2)), "%.1f: CLAIMED keeps off %s's name" % [scale, site])
		assert_gt(checked, 0, "%.1f: the claimed Site's label was checked" % scale)
		hq.get_parent().queue_free()
		await _frames(1)
