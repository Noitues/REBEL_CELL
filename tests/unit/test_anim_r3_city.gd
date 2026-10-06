extends GutTest
## Animation pass ANIM-R3 (the third fix batch), city, raid, jack, Heat and route: route
## twins only when the whole road ahead is the same; raid verdicts, numbers and the feed agree
## with the resolved raid for every corporation; SAVED keeps off titles; the route frames
## where the player is and the next choices; the Heat banner wraps before it shrinks and sits
## beside its number; the frame-signal lambda rule's forms; pad prompts leave no orphans;
## stale prebakes give the build slot back; the city's silhouette while it bakes; the
## CONNECTING line's reading time under reduce effects; the Cell's territory colour; the
## claimed Site's card. Headless (no renderer): `CityBakeCache.simulate` where a bake path is
## needed.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const IntegrityScript := preload("res://tests/unit/test_suite_integrity.gd")
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
## Maps generated for the twin check.
const TWIN_SEEDS := 60

var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r3_city"
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
	Fx.saved_screen = Rect2()
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


# --- B3: route twins ------------------------------------------------------------------------------

## Whether the roads from `a` and `b` are the same (kind, Heat, and the same multiset of
## roads after), worked out by plain recursion: the check the signatures must agree with.
func _same_road(map: MapGraph, a: StringName, b: StringName, memo: Dictionary) -> bool:
	if a == b:
		return true
	var key := "%s|%s" % [a, b] if String(a) < String(b) else "%s|%s" % [b, a]
	if memo.has(key):
		return memo[key]
	var na := map.get_node(a)
	var nb := map.get_node(b)
	var same := int(na["type"]) == int(nb["type"]) and NetrunScript._is_elite(na) == NetrunScript._is_elite(nb) \
		and int(na.get("heat", 0)) == int(nb.get("heat", 0)) and (na["next"] as Array).size() == (nb["next"] as Array).size()
	if same:
		# Match every child of `a` with its own child of `b` (a multiset match).
		var left: Array = (nb["next"] as Array).duplicate()
		for x in na["next"]:
			var found := -1
			for k in left.size():
				if _same_road(map, x, left[k], memo):
					found = k
					break
			if found < 0:
				same = false
				break
			left.remove_at(found)
	memo[key] = same
	return same


func test_route_twins_share_the_whole_road_ahead_over_many_seeds() -> void:
	RunManager.new_campaign(1)
	var cfg := RunManager.config()
	var pairs := 0
	var twins := 0
	var near_miss := 0
	for seed in TWIN_SEEDS:
		var map := MapGenerator.generate(1 + seed % 3, cfg, RngStreams.make_stream(1000 + seed, &"map"))
		var heat_of := func(id: StringName) -> int: return int(map.get_node(id).get("heat", 0))
		var signs := NetrunScript.subgraph_signatures(map, heat_of)
		var memo := {}
		for layer: Array in map.layers:
			for i in layer.size():
				for j in range(i + 1, layer.size()):
					var a: StringName = layer[i]["id"]
					var b: StringName = layer[j]["id"]
					var same_sign: bool = signs[a] == signs[b]
					assert_eq(same_sign, _same_road(map, a, b, memo), "seed %d: %s and %s are twins exactly when their whole roads are the same" % [seed, a, b])
					pairs += 1
					if same_sign:
						twins += 1
					elif NetrunScript.node_word(layer[i]) == NetrunScript.node_word(layer[j]) and NetrunScript.ahead_words(map, layer[i]) == NetrunScript.ahead_words(map, layer[j]):
						near_miss += 1
	assert_gt(pairs, 100, "many choices compared")
	assert_gt(twins, 0, "some choices really are twins")
	assert_gt(near_miss, 0, "and some that the old label called twins differ further on (no label now)")


func test_a_choice_that_differs_further_on_shows_what_only_it_reaches() -> void:
	RunManager.new_campaign(1)
	var nr := _scene(NETRUN)
	await _frames(1)
	nr.start_run(1)
	await _frames(2)
	# B3 (bible 4.6, round 44): the route on the map shows no "then:" rows (its ROUTE window holds
	# GRID VIEW and Save & quit only); the list (GRID VIEW's) still says what only a choice reaches.
	assert_null(nr._panel.find_child("Ahead1", true, false), "no then: row on the map's route")
	nr._grid_zoomed = true
	nr._show_map()
	await _frames(2)
	var s := RunManager.netrun
	var twins: Dictionary = NetrunScript.choice_twins(s)
	var differs: Dictionary = NetrunScript.choice_differences(s)
	var open := s.available_nodes()
	for i in open.size():
		var id: StringName = open[i]
		var row: Node = nr._panel.find_child("Ahead%d" % (i + 1), true, false)
		var kinds: Array = differs.get(id, [])
		if twins.has(id):
			assert_null(row, "a twin shows no difference")
			continue
		if kinds.is_empty() and s.node_heat(id) == 0:
			assert_null(row, "nothing differs: no row")
		else:
			assert_not_null(row, "choice %d shows what only it reaches" % (i + 1))
			for k: StringName in kinds:
				assert_not_null(row.find_child("Ahead_%s" % k, true, false), "the %s icon" % k)
	# What differs is never what every choice reaches.
	for id in differs:
		for k in differs[id]:
			var everyone := true
			for other in open:
				if not NetrunScript.ahead_kinds(s.run.map, s.run.map.get_node(other), s.node_heat).has(k):
					everyone = false
			assert_false(everyone, "%s is not reached by every choice" % k)


# --- B8: route framing ------------------------------------------------------------------------------

func test_the_route_frames_the_marker_and_the_next_choices_at_every_text_size() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.new_campaign(1)
		var nr := _scene(NETRUN)
		await _frames(1)
		nr.start_run(1)
		await BoundedWait.until(get_tree(), func() -> bool: return nr._route_area != null and nr.city_overlay != null and nr.city_overlay.here_marker_rects().size() == 1, 3.0)
		await _frames(8)
		var overlay: CityMapOverlay = nr.city_overlay
		assert_eq(overlay.here_id(), &"", "at the start no node is here")
		assert_ne(overlay.here_at.x, INF, "the marker stands at the street (%.1f)" % scale)
		var area: Rect2 = nr._route_area.get_global_rect().intersection(SCREEN)
		var rects := LegendSpot.node_rects(overlay, false, nr.route_focus_ids())
		rects.append_array(overlay.here_marker_rects())
		assert_eq(rects.size(), nr.route_focus_ids().size() * 2 + 1 - _pipless(overlay, nr.route_focus_ids()), "the choices and the marker are measured (%.1f)" % scale)
		for r in rects:
			assert_true(area.grow(1.0).encloses(r), "%s inside the map area %s at %.1f" % [r, area, scale])
			assert_true(r.position.x >= area.position.x + NetrunScript.ROUTE_MARGIN * 0.5, "off the screen's left edge with a margin at %.1f" % scale)
		nr.get_parent().queue_free()
		await _frames(1)


## How many of `ids` have no tier pips (node_rects adds a pip rect for the rest).
func _pipless(overlay: CityMapOverlay, ids: Array) -> int:
	var n := 0
	for d: Dictionary in overlay.nodes:
		if ids.has(d["id"]) and not overlay.tier_pips_rect(d).has_area():
			n += 1
	return n


# --- B5: raid verdicts, numbers and the feed ----------------------------------------------------------

## A campaign against `corp` with the first Site off home claimed and defended, a raid
## pending; `home_integrity` > 0 sets home low (a lost raid).
func _raid_campaign(corp_id: StringName, defended: bool, home_integrity: int = -1) -> void:
	RunManager.new_campaign(1)
	var corp := RunManager.lookup().get_content(corp_id) as CorporationData
	var home := RunManager.lookup().get_content(RunManager.DEFAULT_HOME) as HomeServerVariantData
	RunManager.corporation = corp
	RunManager.campaign = CampaignRules.new_campaign(corp, RunManager.config(), RunManager.lookup(), 1,
		RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, 0, home)
	var c := RunManager.campaign
	c.schematics = 200
	var first: StringName = corp.city_grid.get_site(c.grid.home_site_id).links[0]
	CampaignRules.on_run_completed(c, corp, RunManager.config(), _cleared_run(first))
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	if defended:
		c.armory = [&"turret", &"turret"]
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	if home_integrity > 0:
		c.grid.home_integrity = home_integrity


## A finished run at `site_id` (the HQ's demo run: it clears the Site).
func _cleared_run(site_id: StringName) -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	return r


## Plays `events` of the raid resolved into campaign.last_raid onto a fresh layer, all at once.
func _play(events: Array[Dictionary]) -> RaidFxLayer:
	var c := RunManager.campaign
	var overlay := CityMapOverlay.new()
	add_child_autofree(overlay)
	var fx := RaidFxLayer.new(overlay)
	overlay.add_child(fx)
	fx.setup(c.last_raid, c.grid.home_site_id, c.grid.home_max_integrity, Palette.corp_color(c.corporation_id))
	var at := 0.0
	for group in RaidBeats.group(events):
		var tl := RaidBeats.timeline(group)
		for b: Dictionary in tl["beats"]:
			fx.play_beat(b, at + float(b["t0"]))
		at += float(tl["seconds"])
	fx.clock = at + 100.0
	return fx


func _sum(values: Array[int]) -> int:
	var t := 0
	for v in values:
		t += v
	return t


func test_raid_verdicts_and_numbers_agree_with_the_resolved_raid_for_every_corporation() -> void:
	var cases := 0
	for corp in CORPORATIONS:
		for setup in [[true, -1], [false, -1], [false, 3]]:
			_raid_campaign(corp, setup[0], setup[1])
			if RunManager.pending_raid().is_empty():
				continue
			var events := RunManager.fight_raid()
			var r: Dictionary = RunManager.campaign.last_raid
			var home := RunManager.campaign.grid.home_site_id
			var fx := _play(events)
			cases += 1
			var tag := "%s %s" % [corp, setup]
			for id in r["nodes"]:
				var sid := StringName(String(id))
				var n: Dictionary = r["nodes"][id]
				var nums := fx.numbers_at(sid)
				if sid == home:
					assert_eq(fx.stamp_word(sid), "", "%s: home has no stamp (its banner is its verdict)" % tag)
					assert_eq(_sum(nums), int(r["home_after"]) - int(r["home_before"]), "%s: home's numbers add up to what it lost %s" % [tag, nums])
					continue
				assert_eq(fx.stamp_word(sid), RaidFxLayer.stamp_text(String(n["outcome"])), "%s: %s stamps its resolved outcome" % [tag, id])
				assert_eq(_sum(nums), int(n["after"]) - int(n["before"]), "%s: %s's numbers add up to its change %s" % [tag, id, nums])
				for v in nums:
					assert_ne(v, 0, "%s: no empty number" % tag)
			var lost := int(r["home_before"]) - int(r["home_after"])
			var want := CityMapOverlay.tr_word(RaidFxLayer.BANNER_BREACHED) if bool(r["campaign_lost"]) else \
				(CityMapOverlay.tr_word(RaidFxLayer.BANNER_HOME) % TextDb.signed(-lost) if lost > 0 else CityMapOverlay.tr_word(RaidFxLayer.BANNER_HOLDS))
			assert_eq(fx.banner_text(), want, "%s: the banner is home's one verdict" % tag)
	assert_gt(cases, 8, "raids against every corporation")


func test_the_raid_feed_names_places_and_never_shows_an_id() -> void:
	for corp in CORPORATIONS:
		_raid_campaign(corp, true)
		if RunManager.pending_raid().is_empty():
			continue
		var events := RunManager.fight_raid()
		var panel := RaidPlayoutPanel.new(null)
		add_child_autofree(panel)
		panel.attach_fx(RunManager.campaign.last_raid, RunManager.campaign.grid.home_site_id, 50, Palette.CORP_SOLACE)
		panel.play(events, true)
		var text := panel.log_note.label.get_parsed_text()
		assert_true(text.length() > 20, "%s: the feed tells the raid" % corp)
		# The ids a line could leak: Site ids ("t1_a", "home") and threat ids ("t1"). A plain
		# word id ("home", "turret") can be a word of the sentence or of a display name
		# ("Reached home", "Firewall turret"): only ids with a digit or an underscore count.
		var ids: Array = []
		for sd in RunManager.corporation.city_grid.sites:
			ids.append(String(sd.id))
		for e in events:
			if e.has("threat"):
				ids.append(String(e["threat"]))
			if e.has("asset"):
				ids.append(String(e["asset"]))
		var raw := RegEx.create_from_string("[0-9_]")
		for id in ids:
			if raw.search(String(id)) == null:
				continue
			var re := RegEx.create_from_string("(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % id)
			assert_null(re.search(text), "%s: no raw id '%s' in the feed" % [corp, id])
		assert_false(text.contains(" home,"), "%s: the end is a sentence, not 'reached home, 0 DOWN'" % corp)
		assert_string_contains(text, CityMapOverlay.tr_word("Threats destroyed: %d. Reached home: %d. DOWN: %d. TAKEN: %d.").get_slice(":", 0), "%s: the tally" % corp)


func test_a_drop_carries_the_forecast_numbers_it_changed() -> void:
	RunManager.new_campaign(1)
	var hq := _scene(HQ)
	await _frames(1)
	_raid_campaign(&"solace", false)
	hq.show_raid()
	await _frames(3)
	var c := RunManager.campaign
	var site: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
	var was: Dictionary = hq.forecast_values()
	c.armory = [&"turret"]
	hq.deploy_asset(0, site)
	await _frames(2)
	var now: Dictionary = hq.forecast_values()
	var changes: Array = hq.city_overlay.drop_changes()
	var want := 0
	for id in now:
		if was.has(id) and int(was[id]) != int(now[id]):
			want += 1
	assert_eq(changes.size(), want, "one change per forecast number that moved")
	for ch: Dictionary in changes:
		assert_eq(int(ch["from"]), int(was[String(ch["site"])]))
		assert_eq(int(ch["to"]), int(now[String(ch["site"])]))
	assert_eq(hq.city_overlay.change_t, 1.0, "headless: the end state at once (no chip left)")


func test_the_jack_names_the_run_and_a_raid_before_the_run_exists() -> void:
	_raid_campaign(&"solace", false)
	var site: StringName = RunManager.launchable_sites()[0].id
	var sd := CampaignRules.site_data(RunManager.corporation, site)
	assert_eq(RunManager.jack_destination(site), TextDb.t(sd, "display_name"), "named from the Site before the run is built")
	RunManager._before_switch = func() -> void: pass
	# ANIM-R4 H11a (updated on purpose): the stamp names the corporation that raids.
	assert_eq(RunManager.jack_note(), tr("RAID INCOMING\n%s") % TextDb.t(RunManager.corporation, "display_name"), "a queued raid interrupts the run")
	RunManager._before_switch = Callable()


func test_launch_builds_the_run_at_the_switch_and_saves_it() -> void:
	RunManager.new_campaign(1)
	var hq := _scene(HQ)
	await _frames(1)
	hq.new_campaign(1)
	var site: StringName = RunManager.launchable_sites()[0].id
	var op: StringName = RunManager.campaign.living_operatives()[0].id
	RunManager.delete_save()
	assert_true(hq.launch(site, op), "launched")
	assert_not_null(RunManager.netrun, "no jack plays: built at once")
	assert_true(RunManager.has_save(), "and saved")


# --- B6: territory ---------------------------------------------------------------------------------

func test_the_cells_territory_is_its_own_colour_and_the_claimed_card_says_so() -> void:
	assert_ne(Palette.CELL_TURF, Palette.CELL_PINK, "territory is never the damage pink")
	assert_eq(CityInfluence.color_for({"corp": &"solace"}, 0.5), Palette.CELL_TURF)
	for corp in CORPORATIONS:
		var gap := absf(Palette.CELL_TURF.h - Palette.corp_color(corp).h)
		gap = minf(gap, 1.0 - gap)
		# ART_BIBLE v2 §2.4 (LOCKED round 18): Solace's leaf green sits near the Cell's lime by design;
		# its separation is the territory hatch and stamp word, and Solace never on a link or ring.
		assert_gt(gap, 0.05 if corp == &"solace" else 0.1, "apart from %s's colour (%.3f)" % [corp, gap])
	RunManager.new_campaign(1)
	var hq := _scene(HQ)
	await _frames(1)
	hq.new_campaign(1)
	var c := RunManager.campaign
	var first: StringName = RunManager.corporation.city_grid.get_site(c.grid.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), _cleared_run(first))
	c.schematics = 500
	hq.selected_site = first
	hq.show_grid()
	await _frames(2)
	assert_not_null(_claim_button(hq), "a cleared Site offers CLAIM")
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	hq._on_territory_marked([])
	await _frames(1)
	assert_null(_claim_button(hq), "claimed: no CLAIM any more")
	var badge := hq._panel.find_child("StatusBadge", true, false) as Badge
	assert_eq(badge.text, CityMapOverlay.tr_word("claimed").to_upper(), "the card says CLAIMED")
	assert_eq(badge.icon_kind, StatIcon.CLAIM, "with the claim mark")


## HQ-B (d, Q11): CLAIM is the verb slot's sticker.
func _claim_button(hq: Control) -> Button:
	var slot: Node = hq._panel.get_node_or_null("VerbSlot")
	if slot == null:
		return null
	var b := slot.get_node_or_null("Claim") as Button
	return b if b != null and not b.is_queued_for_deletion() else null


# --- B7: the Heat banner -----------------------------------------------------------------------------

func test_the_heat_banner_wraps_sits_beside_its_number_and_warns() -> void:
	RunManager.new_campaign(1)
	var tr_long := Translation.new()
	tr_long.locale = "xx"
	tr_long.add_message("hunted", "activement recherché")
	tr_long.add_message("HEAT %d - %s", "CHALEUR %d - %s")
	TranslationServer.add_translation(tr_long)
	var locale := TranslationServer.get_locale()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		for loc in [locale, "xx"]:
			TranslationServer.set_locale(loc)
			for poster_kind in [true, false]:
				var poster := HeatPoster.new(poster_kind)
				holder.add_child(poster)
				poster.size = poster.custom_minimum_size
				poster.heat = 80
				poster._banner_at = 75
				var lay := poster.banner_lines()
				var fs: int = lay["fs"]
				var span := HeatPoster.banner_span(Palette.display(), lay["lines"], fs)
				var tag := "%s at %.1f (%s, poster %s)" % [poster.banner_text(), scale, loc, poster_kind]
				assert_true(span <= poster.size.x - HeatPoster.BANNER_MARGIN * 2.0 + 0.5, "%s fits: %.0f in %.0f" % [tag, span, poster.size.x])
				if (lay["lines"] as PackedStringArray).size() == 1:
					assert_true(fs >= HeatPoster.BANNER_FONT_MIN, "%s: one line only at a readable size" % tag)
				# Never over the number: the banner's box and the number's block apart.
				var ll := poster.letter_layout(3)
				var y := HeatPoster.POSTER_BLOCK_TOP if poster_kind else 0.0
				var number := Rect2(Vector2(float(ll["num_x"]), y + 4.0), Vector2(float(ll["num_w"]), HeatPoster.NUMBER_FONT))
				assert_false(poster.banner_rect().grow(-1.0).intersects(number), "%s: beside the number, not over it" % tag)
				poster.free()
	TranslationServer.set_locale(locale)
	TranslationServer.remove_translation(tr_long)
	var p := HeatPoster.new(true)
	holder.add_child(p)
	p._banner_at = 25
	assert_eq(p.banner_color(), HeatPoster.BAND_COLORS[1], "NOTICED warns in amber, not the corporation's green")
	assert_ne(p.banner_color(), Palette.CORP_SOLACE)
	assert_ne(HeatPoster.consequence(25), "", "the band says what it brings")
	assert_string_contains(p.tooltip_words("Heat"), HeatPoster.consequence(0) if HeatPoster.consequence(0) != "" else "Heat", "the tooltip carries the band in force")
	p.free()


func test_the_heat_banner_fades_after_its_hold() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var p := HeatPoster.new(true)
	holder.add_child(p)
	p.size = p.custom_minimum_size
	p._banner_at = 25
	p._stamp_banner()
	assert_eq(p.banner_alpha, 1.0, "it stamps on")
	var gone := await BoundedWait.until(get_tree(), func() -> bool: return p.banner_alpha <= 0.0, BoundedWait.motion_limit([&"heat_banner", &"poster_stamp"], Motion.delay_of(&"heat_banner")))
	assert_true(gone, "and fades after its hold (nothing stays over the poster)")


# --- B11: the frame-signal lambda rule -----------------------------------------------------------------

func test_the_lambda_rule_catches_spaced_named_and_held_lambdas() -> void:
	assert_true(IntegrityScript.frame_lambda("\tget_tree().process_frame.connect( func(): pass)"))
	assert_true(IntegrityScript.frame_lambda("\tget_tree().connect(\"process_frame\", func(): pass)"))
	var lines := PackedStringArray(["\tvar f := func(): pass", "\tget_tree().process_frame.connect(f)"])
	assert_eq(IntegrityScript.frame_lambda_lines(lines), [1] as Array[int])
	assert_false(IntegrityScript.frame_lambda("\tget_tree().process_frame.connect(_warm_step)"), "a method callable passes")


# --- B12: no orphans ------------------------------------------------------------------------------------

func test_pad_prompts_free_their_old_labels_on_a_relabel() -> void:
	var holder: Control = add_child_autofree(Control.new())
	var prompts := PadPrompts.new()
	holder.add_child(prompts)
	prompts.set_prompts([[&"ui_accept", "Select"], [&"open_settings", "Settings"]])
	var old: Array[WeakRef] = []
	for child in prompts.get_children():
		old.append(weakref(child))
	assert_gt(old.size(), 0, "prompts were built")
	Settings.changed.emit()
	Settings.hints_changed.emit()
	for w in old:
		assert_null(w.get_ref(), "an old prompt label is freed at once (never an orphan)")


# --- B10: stale prebakes --------------------------------------------------------------------------------

func test_a_bake_nobody_waits_for_gives_the_build_slot_back() -> void:
	var gone := Node.new()
	var alive: Node = add_child_autofree(Node.new())
	var gone_id := gone.get_instance_id()
	gone.free()
	var stale_painter := NeonCity.new()
	var queued_painter := NeonCity.new()
	var kept_painter := NeonCity.new()
	var rec := {"painter": stale_painter, "holding": true}
	CityBakeCache._live["stale"] = rec
	CityBakeCache._building = 1
	CityBakeCache._pending["stale"] = {"waiters": [gone_id], "look": "L", "region": Rect2()}
	CityBakeCache._queue.append({"key": "queued", "look": "L", "painter": queued_painter})
	CityBakeCache._pending["queued"] = {"waiters": [gone_id], "look": "L", "region": Rect2()}
	CityBakeCache._queue.append({"key": "kept", "look": "L", "painter": kept_painter})
	CityBakeCache._pending["kept"] = {"waiters": [alive.get_instance_id()], "look": "L", "region": Rect2()}
	var dropped := CityBakeCache.drop_stale()
	assert_eq(dropped, 2, "the running bake and the queued one of the scene left behind")
	assert_false(CityBakeCache._live.has("stale"), "the stale build stopped")
	assert_false(is_instance_valid(stale_painter), "its painter freed")
	assert_false(is_instance_valid(queued_painter), "the queued painter freed")
	assert_eq(CityBakeCache._building, 0, "the build slot is free")
	assert_eq(CityBakeCache._queue.size(), 1, "a bake someone waits for stays")
	assert_true(CityBakeCache._pending.has("kept"))
	CityBakeCache._queue.clear()
	CityBakeCache._pending.clear()
	kept_painter.free()
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/city_bake_cache.gd")
	assert_false(src.contains("if not _live.has(key):\n"), "a bake's coroutine checks its own record, never just the key")
	assert_true(src.contains("is_same(_live.get(key), rec)"), "(its record)")


# --- B4: the silhouette while a view bakes ---------------------------------------------------------------

func test_a_view_shows_the_citys_silhouette_until_its_image_lands() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	await BoundedWait.until(get_tree(), func() -> bool: return city.silhouette_done and city.silhouette_roofs > 0, 5.0)
	assert_true(city._sil.visible, "the sky shows the silhouette layer")
	assert_gt(city.silhouette_roofs, 20, "blocks drawn from the placement (%d)" % city.silhouette_roofs)
	var look := city.look_key()
	var region := city.bake_region()
	CityBakeCache.store(look + "@" + var_to_str(Rect2i(region)), {"look": look, "region": region, "texture": ImageTexture.create_from_image(Image.create(8, 8, false, Image.FORMAT_RGBA8)), "scale": 1.0,
		"roofs": {}, "beacons": [] as Array[Dictionary], "lights": [] as Array[Dictionary], "trails": [] as Array[Dictionary], "signs": [] as Array[Dictionary]})
	var replaced := await BoundedWait.until(get_tree(), func() -> bool: return not city._sil.visible, 2.0)
	assert_true(replaced and city.view_covered(), "the image replaces it")
	assert_true(Motion.seconds(&"city_bake_fade") >= 0.6, "the image fades in slowly enough not to pop")


# --- B2: the CONNECTING line's reading time -------------------------------------------------------------

func test_reduce_effects_holds_the_connecting_line_its_reading_time() -> void:
	await _frames(1)
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	var limit := BoundedWait.motion_limit([&"jack_fade_reduced", Fx.ARRIVAL_WAIT_MOTION, Fx.CONNECT_MOTION])
	Fx.jack_in(func() -> void: pass, -1.0, "Test Site")
	var saw := await BoundedWait.until(get_tree(), Fx.connecting, limit)
	assert_true(saw, "CONNECTING shows on the reduced fade")
	# ANIM-R6: the line's own measure (wall time from showing to going); measured from when
	# the test first saw it, a slow frame before that under a loaded shard read it short.
	var gone := await BoundedWait.until(get_tree(), func() -> bool: return not Fx.connecting(), limit)
	assert_true(gone, "the line goes")
	assert_true(Fx.last_connect_shown >= Motion.seconds(Fx.CONNECT_MOTION) * 0.99, "it stays up its reading time, not ~2 frames (%.2f s, want %.2f)" % [Fx.last_connect_shown, Motion.seconds(Fx.CONNECT_MOTION)])
	await BoundedWait.until(get_tree(), func() -> bool: return not Fx.transitioning(), limit)


# --- B13: SAVED keeps off titles; the side column ends on a whole row -----------------------------------

func test_saved_keeps_off_titles_and_buttons_on_the_map_screens() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		var hq := _scene(HQ)
		await _frames(1)
		_raid_campaign(&"solace", true)
		for page in ["grid", "raid"]:
			if page == "grid":
				hq.show_grid()
			else:
				hq.show_raid()
			await _frames(4)
			var r := Fx.place_saved(SCREEN)
			var titles: Array[Rect2] = [hq.hud.title_box.get_global_rect()]
			for t in hq.find_children("TerminalTitle", "Label", true, false):
				if (t as Control).is_visible_in_tree():
					# ART-0 C: the part its scroll views show (at 2.0 the raid's side column
					# scrolls; a title below its view is not on the screen).
					var shown := Fx._shown_rect((t as Control).get_parent() as Control)
					if shown.has_area():
						titles.append(shown)
			for t in titles:
				assert_false(r.intersects(t), "%s at %.1f: SAVED %s off the title %s" % [page, scale, r, t])
			for b in hq.find_children("*", "BaseButton", true, false):
				var btn := b as BaseButton
				if btn.is_visible_in_tree() and btn.mouse_filter != Control.MOUSE_FILTER_IGNORE:
					assert_false(r.intersects(Fx._shown_rect(btn)), "%s at %.1f: SAVED off %s" % [page, scale, btn.name])
		hq.get_parent().queue_free()
		await _frames(1)
	# All edges covered: the whole screen is searched.
	var covered: Array[Rect2] = [Rect2(0, 0, 1280, 120), Rect2(0, 600, 1280, 120), Rect2(0, 0, 120, 720), Rect2(1160, 0, 120, 720)]
	var at := Fx.saved_spot(Vector2(60, 20), SCREEN, covered)
	for c in covered:
		assert_false(Rect2(at, Vector2(60, 20)).intersects(c), "a free spot inside the screen when every edge is taken")


