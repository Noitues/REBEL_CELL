extends GutTest
## H22 screens (GAP_ANALYSIS H22 #7, #9, #10, #12, #14; DECISIONS "H22 screens"):
## subtitles that page in any language (no spaces, translated text) and never outgrow
## their band; the raid setup's forecast worded as a forecast, its legend clear of the
## nodes, its defence cards on screen and readable with a deploy cue; MORE BELOW over no
## control; every dossier's Loadout reachable by pad; event outcomes that name no rescued
## class and show capped amounts; stat tags that keep their words at big text; the route
## legend; route buttons and Grid runs with the map's own node icons and tier pips.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SLOT := "gut_s22_screens"
const CANVAS := Vector2(1280, 720)
const LONG_LINE := "Runner, the compliance office has flagged your cell for audit. Keep the needle off the Miss slice, bank the Rack before the auditors land, and do not let the Heat climb past the next threshold or the whole district locks down for a week."
## A long Japanese line (no spaces at all).
const CJK_LINE := "コンプライアンス部門があなたのセルを監査対象に指定しました。針をミスのスライスから外し、監査官が到着する前にラックを確保し、ヒートが次のしきい値を超えないようにしてください。さもないと地区全体が一週間封鎖されます。"
## One German-style word longer than a narrow dock.
const LONG_WORD := "Datenschutzgrundverordnungsbeauftragtenstellvertreterausweisnummernkontrollsystem ist aktiv."

var _text_scale_before: float = 1.0
var _pad_before: bool = false
var _legend_before: bool = true
var _pseudo_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_pad_before = Settings.pad_active
	_legend_before = Settings.map_legend


func before_each() -> void:
	AudioDirector.muted = true
	_pseudo_before = TranslationServer.pseudolocalization_enabled
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if TranslationServer.pseudolocalization_enabled != _pseudo_before:
		TranslationServer.pseudolocalization_enabled = _pseudo_before
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(_pad_before)
	if Settings.map_legend != _legend_before:
		Settings.set_map_legend(_legend_before)
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


## `r` clipped to every ScrollContainer view above `c` (the part of a control on screen).
func _shown_rect(c: Control) -> Rect2:
	var r := c.get_global_rect()
	var p := c.get_parent()
	while p != null:
		if p is ScrollContainer:
			r = r.intersection((p as Control).get_global_rect())
		p = p.get_parent()
	return r


## Every visible, usable control under `root`, as far as it shows.
func _controls(root: Node, except: Node = null) -> Array[Control]:
	var out: Array[Control] = []
	for n in _all(root):
		if n == except or (except != null and except.is_ancestor_of(n)):
			continue
		if not (n is Control) or not (n as Control).is_visible_in_tree():
			continue
		if (n is BaseButton and not (n as BaseButton).disabled and (n as Control).mouse_filter != Control.MOUSE_FILTER_IGNORE) or n is LineEdit or (n is Range and not (n is ScrollBar)):
			if _shown_rect(n as Control).has_area():
				out.append(n)
	return out


## Two claimed nodes beside the home server, an Armory, and a pending raid.
func _raid_campaign() -> CampaignState:
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var claimed := 0
	for sd in grid_data.sites:
		if sd.tier == 1 and sd.id != grid_data.home_site_id and sd.objective == RC.SiteObjective.NONE and claimed < 2:
			var s := c.grid.site(sd.id)
			s["status"] = GridState.SiteStatus.CLAIMED
			s["node_type"] = "firewall_relay"
			s["integrity"] = 30
			s["max_integrity"] = 30
			s["assets"] = ["turret"] if claimed == 0 else []
			claimed += 1
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	return c


func _netrun() -> Control:
	var scene := _open(NETRUN)
	scene.start_run(1)
	return scene


func _event(scene: Control, id: StringName = &"ev_leash_on_the_floor") -> void:
	var run := RunManager.netrun.run
	run.event_id = id
	run.phase = RunState.Phase.EVENT
	scene._show_current()


func _shop(scene: Control) -> void:
	var s := RunManager.netrun
	s.run.cycles = 120
	s._open_shop()
	scene._show_current()


# --- #7 subtitles for any language ------------------------------------------------------------

## Shows `line` and walks every page: the bar stays in `band` and each page's words fit the
## text label (paging did the work; clipping is only the last resort).
func _assert_pages_fit(line: String, band: Rect2, label: String) -> void:
	Dialogue.clear()
	Dialogue.say(RC.Voice.DISPATCH, line)
	var pages := 0
	while Dialogue.is_showing() and pages < 40:
		await _frames(2)
		var bar := Rect2(Dialogue.bar.global_position, Dialogue.bar.size)
		assert_true(bar.position.y >= band.position.y - 0.5 and bar.end.y <= band.end.y + 0.5,
			"%s page %d: the bar %s stays in its band %s (text %.1f)" % [label, pages, bar, band, Settings.text_scale])
		var tl := Dialogue.text_label
		assert_true(tl.get_content_height() <= tl.size.y + 1.0,
			"%s page %d: its words fit (content %.1f in %.1f px, text %.1f): '%s'" % [label, pages, tl.get_content_height(), tl.size.y, Settings.text_scale, Dialogue.current_text()])
		pages += 1
		if Dialogue._queue.is_empty():
			break
		Dialogue._next()
	assert_true(pages >= 1, "%s: shown" % label)
	Dialogue.clear()


func test_subtitles_page_cjk_and_pseudolocalised_text_inside_the_band() -> void:
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		var hq := _open(HQ)
		await _frames()
		var band := (hq.subtitle_strip as Control).get_global_rect()
		await _assert_pages_fit(CJK_LINE, band, "CJK")
		await _assert_pages_fit(LONG_WORD, band, "a long word")
		TranslationServer.pseudolocalization_enabled = true
		await _frames()
		await _assert_pages_fit(LONG_LINE, band, "pseudolocalised")
		TranslationServer.pseudolocalization_enabled = false
		hq.get_parent().queue_free()
		await _frames(2)


func test_a_narrow_paged_dock_holds_cjk_and_long_words() -> void:
	# The combat dock (dock_at(rect, lines)): a narrow column, three lines a page.
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		var rect := Rect2(900, 90, 300, (20.0 + 3 * 20.0) * scale)
		Dialogue.dock_at(rect, 3)
		await _assert_pages_fit(CJK_LINE, rect, "narrow CJK")
		Dialogue.dock_at(rect, 3)
		await _assert_pages_fit(LONG_WORD, rect, "narrow long word")
	Dialogue.dock_default()


func test_paging_measures_the_translated_text_and_shows_it_once() -> void:
	assert_eq(Dialogue.text_label.auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "the label never translates a page again")
	TranslationServer.pseudolocalization_enabled = true
	await _frames()
	var shown := Dialogue.shown_text(LONG_LINE)
	assert_ne(shown, LONG_LINE, "pseudolocalisation changes the words")
	Dialogue.clear()
	Dialogue.say(RC.Voice.DISPATCH, LONG_LINE)
	await _frames(2)
	assert_true(shown.begins_with(Dialogue.current_text().strip_edges()), "the page shown is the translated line's first page: '%s'" % Dialogue.current_text())
	assert_eq(Dialogue.history[-1]["text"], LONG_LINE, "the history keeps the line as spoken")
	# A page with no spaces is broken by characters, never wider than the bar.
	var long_cjk := CJK_LINE + CJK_LINE + CJK_LINE
	var pages := Dialogue.pages_of(long_cjk)
	assert_true(pages.size() >= 2, "a long line without spaces pages")
	assert_eq("".join(pages), long_cjk, "no character lost or added")


# --- #9 raid setup ---------------------------------------------------------------------------

func _raid(scale: float) -> Control:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(1)
	_raid_campaign()
	var hq := _open(HQ)
	await _frames()
	hq.show_raid()
	await _frames(6)
	return hq


func test_the_raid_stamp_is_a_forecast() -> void:
	var hq: Control = await _raid(1.0)
	var stamp: Node = hq._panel.find_child("Projection", true, false)
	assert_true(stamp is ForecastStamp, "a dashed forecast, not a result stamp")
	var fs := stamp as ForecastStamp
	var projection := RunManager.project_raid()
	assert_string_contains(fs.caption, "IF THE RAID")
	assert_string_contains(fs.caption, "RUNS NOW")
	assert_eq(fs.verdict, hq.raid_verdict(projection), "the verdict is the projection's")
	# ANIM-R4 H3 (updated on purpose): the verdict names the losses, never "HOME HIT".
	assert_false(fs.verdict.contains("HOME HIT"))
	assert_true(fs.tooltip_text.begins_with("Forecast, not a result"), "the tooltip says it is a projection")
	if projection.home_after < projection.home_before and not projection.campaign_lost:
		assert_string_contains(fs.verdict, "HOME -%d" % (projection.home_before - projection.home_after), "home damage reads as its number, beside rows such as 50 > 40 HOLDS")
	for n in _all(hq._panel):
		if n is ZineStamp:
			assert_ne((n as ZineStamp).stamp_text, "BREACHED", "no result stamp before the raid runs")


func test_the_raid_legend_covers_no_node_and_stays_on_screen() -> void:
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		var hq: Control = await _raid(scale)
		var legend: MapLegend = hq.raid_legend
		assert_not_null(legend)
		assert_true(legend.is_visible_in_tree(), "the legend shows")
		var lr := legend.get_global_rect()
		assert_true(Rect2(Vector2.ZERO, CANVAS).encloses(lr), "on screen at %.1f: %s" % [scale, lr])
		var area := (legend.get_parent() as Control).get_global_rect()
		assert_true(area.grow(0.5).encloses(lr), "inside the map area at %.1f: %s in %s" % [scale, lr, area])
		var rects: Array[Rect2] = hq.raid_node_rects()
		assert_false(rects.is_empty(), "the raid map has nodes")
		for r in rects:
			assert_false(lr.intersects(r), "the legend %s covers a node or label at %s (text %.1f)" % [lr, r, scale])
		hq.get_parent().queue_free()
		await _frames(2)


func test_defence_cards_are_on_screen_readable_and_say_how_to_deploy() -> void:
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		var hq: Control = await _raid(scale)
		var cards: Node = hq._panel.find_child("AssetCards", true, false)
		assert_eq(cards.get_child_count(), 3)
		for card in cards.get_children():
			var r := _shown_rect(card as Control)
			assert_true(r.is_equal_approx((card as Control).get_global_rect()) and Rect2(Vector2.ZERO, CANVAS).encloses(r),
				"the %s card is whole on screen at %.1f: %s" % [(card as AssetCard).display_name, scale, (card as Control).get_global_rect()])
			if hq.more_hint.visible:
				assert_false(hq.more_hint.get_global_rect().intersects(r), "MORE BELOW covers no card")
		var steps: Node = hq._panel.find_child("DeploySteps", true, false)
		assert_not_null(steps, "the deploy steps show")
		var marks := 0
		for n in _all(steps):
			if n is IconMark:
				marks += 1
		assert_eq(marks, 2, "each step has its icon")
		assert_string_contains((steps.find_child("DeployTarget", true, false) as Label).text, hq.site_name(hq.selected_site), "the target is named")
		hq.get_parent().queue_free()
		await _frames(2)
	assert_eq(AssetCard.DISABLED_SHADE.a < 0.45, true, "a lighter shade over a disabled card")


# --- #10 MORE BELOW and the crew ----------------------------------------------------------

func _assert_hint_clear(hint: ScrollHint, root: Node, label: String) -> void:
	if hint == null or not is_instance_valid(hint) or not hint.visible:
		return
	var hr := hint.get_global_rect()
	for c in _controls(root, hint):
		assert_false(hr.intersects(_shown_rect(c)), "%s: MORE BELOW %s covers %s '%s' at %s (text %.1f)" % [label, hr, c.get_class(), c.get("text"), _shown_rect(c), Settings.text_scale])


func test_more_below_covers_no_control() -> void:
	for scale in [1.0, 1.3, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		_raid_campaign()
		var hq := _open(HQ)
		await _frames(6)
		_assert_hint_clear(hq.more_hint, hq, "HQ")
		hq.show_grid()
		await _frames(6)
		_assert_hint_clear(hq.side_hint, hq, "Grid")
		_assert_hint_clear(hq.more_hint, hq, "Grid page")
		hq.show_raid()
		await _frames(6)
		_assert_hint_clear(hq.more_hint, hq, "raid")
		hq.get_parent().queue_free()
		await _frames(2)


## The controls the D-pad reaches from the focus owner (the four directions only).
func _dpad_reachable() -> Dictionary:
	var start := get_viewport().gui_get_focus_owner()
	var seen := {}
	if start == null:
		return seen
	seen[start] = true
	var queue: Array = [start]
	while not queue.is_empty():
		var c: Control = queue.pop_front()
		for side in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]:
			var n := c.find_valid_focus_neighbor(side)
			if n != null and not seen.has(n):
				seen[n] = true
				queue.append(n)
	return seen


func test_every_dossier_loadout_is_pad_reachable_and_has_its_icon() -> void:
	var c := RunManager.campaign
	assert_true(c.living_operatives().size() >= 2, "two rookies")
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		Settings.set_pad_active(true)
		var hq := _open(HQ)
		await _frames(6)
		var reach := _dpad_reachable()
		var loadouts := 0
		for n in _all(hq._panel):
			if n is Button and n.name == &"Loadout":
				loadouts += 1
				assert_true(reach.has(n), "dossier Loadout %d reachable by D-pad at %.1f" % [loadouts, scale])
				assert_eq(IconMark.kind_of(n), StatIcon.CARDS, "the Loadout button has its icon")
		assert_eq(loadouts, c.living_operatives().size(), "one Loadout a dossier")
		# The crew shows side by side or says there is more (H22 #10: one dossier at 1.6).
		var roster: Control = hq._panel.find_child("Roster", true, false)
		var view := (hq.get_node("PageScroll") if hq.has_node("PageScroll") else hq.find_child("PageScroll", true, false)) as ScrollContainer
		for card in roster.get_children():
			var top := (card as Control).get_global_rect().position.y
			assert_true(top < view.get_global_rect().end.y or hq.more_hint.visible,
				"a dossier under the fold has MORE BELOW (text %.1f)" % scale)
		var jack := hq._panel.find_child("JackIn", true, false) as ZineStamp
		assert_eq(jack.icon_kind, StatIcon.JACK_IN, "JACK IN carries the plug")
		hq.get_parent().queue_free()
		await _frames(2)


# --- #12 event outcomes ---------------------------------------------------------------------

func _choice(effects: Array, reward: Resource = null) -> EventChoiceData:
	var ch := EventChoiceData.new()
	var list: Array[EffectData] = []
	for e in effects:
		var ed := EffectData.new()
		ed.type = int(e[0])
		ed.amount = int(e[1])
		list.append(ed)
	ch.effects = list
	ch.reward = reward
	return ch


func test_outcomes_name_no_rescued_class_and_show_capped_amounts() -> void:
	var scene := _netrun()
	await _frames()
	var s := RunManager.netrun
	var cls := s.lookup.get_content(RunManager.DEFAULT_CLASS) as ClassData
	var rescue := OutcomeRow.of_choice(s, _choice([], cls))
	assert_eq(rescue.size(), 1)
	assert_eq(rescue[0]["kind"], StatIcon.OPERATIVE)
	assert_eq(String(rescue[0]["name"]), "", "no class named (the class is rolled from the roster)")
	for id in s.lookup.ids_of_class(&"ClassData"):
		var name := TextDb.t(s.lookup.get_content(id), "display_name")
		assert_false(OutcomeRow.describe(rescue).contains(name), "the tooltip names no class (%s)" % name)
		assert_false(OutcomeRow.words(rescue).contains(name), "the button names no class (%s)" % name)
	assert_string_contains(OutcomeRow.words(rescue), "an operative")
	# Heal at full HP: nothing to heal.
	var op := s.run.operative
	op.hp = op.max_hp
	var heal := OutcomeRow.of_choice(s, _choice([[RC.EffectType.HEAL, 10]]))
	assert_eq(int(heal[0]["amount"]), 0, "+0 HP at full HP")
	assert_string_contains(OutcomeRow.describe(heal), "HP is full")
	op.hp = op.max_hp - 4
	heal = OutcomeRow.of_choice(s, _choice([[RC.EffectType.HEAL, 10]]))
	assert_eq(int(heal[0]["amount"]), 4, "the heal stops at max HP")
	# Heat sink at Heat 1: -1, not -3.
	s.campaign.heat = 1
	var sink := OutcomeRow.of_choice(s, _choice([[RC.EffectType.MODIFY_HEAT, -3]]))
	assert_eq(int(sink[0]["amount"]), maxi(-1, HeatRules.scaled_delta(s.campaign, -3, s.config)), "Heat stops at 0")
	assert_true(bool(sink[0]["capped"]))
	# Preview == result: the amounts are what applying the choice really does.
	op.hp = op.max_hp - 4
	var ch := _choice([[RC.EffectType.HEAL, 10], [RC.EffectType.MODIFY_HEAT, -3]])
	var items := OutcomeRow.of_choice(s, ch)
	var hp_before := op.hp
	var heat_before := s.campaign.heat
	# Apply the effects the way the session does (its own effect step).
	for e in ch.effects:
		s._apply_run_effect(e)
	assert_eq(op.hp - hp_before, int(items[0]["amount"]), "HP preview == result")
	assert_eq(s.campaign.heat - heat_before, int(items[1]["amount"]), "Heat preview == result")
	# On screen: the choice's words carry the capped amounts too.
	op.hp = op.max_hp
	_event(scene)
	await _frames()
	var shown := s.current_event()
	for i in shown.choices.size():
		var b := scene._panel.find_child("Choice%d" % (i + 1), true, false) as Button
		var want := OutcomeRow.words(OutcomeRow.of_choice(s, shown.choices[i]))
		if want != "":
			assert_string_contains(b.text, want, "choice %d's words are the capped outcome" % i)


# --- #14 words that stay, legends and map icons ------------------------------------------------

func test_stat_tags_keep_their_words_at_big_text() -> void:
	Settings.set_text_scale(LayoutScales.VERIFIED_MAX)
	RunManager.new_campaign(1)
	_raid_campaign()
	var hq := _open(HQ)
	await _frames()
	for screen in ["hq", "grid", "raid"]:
		match screen:
			"grid":
				hq.show_grid()
			"raid":
				hq.show_raid()
		await _frames()
		var st: HudStats = hq.hud.stats
		# Art pass W8b (ART_BIBLE §6.9): from HudStats.FOLD_SCALE up the labels fold into the
		# tooltip; the values stay at the text size and the words stay on hover.
		assert_eq(st.compact, LayoutScales.VERIFIED_MAX >= HudStats.FOLD_SCALE, "%s: the labels fold at big text only" % screen)
		assert_ne(st._get_tooltip(st.tag_rects()[0].get_center()), "", "%s: the words stay in the tooltip" % screen)
		assert_true(st.tag_scale >= LayoutScales.VERIFIED_MAX - 0.01, "%s: the tags follow the text size (%.2f)" % [screen, st.tag_scale])
		for r in st.tag_rects():
			assert_true(r.end.x <= st.size.x + 0.5, "%s: a tag stays in the row" % screen)
	hq.get_parent().queue_free()
	await _frames(2)
	var scene := _netrun()
	await _frames()
	for screen in ["route", "modem", "event"]:
		match screen:
			"modem":
				_shop(scene)
			"event":
				_event(scene)
		await _frames()
		var st: HudStats = scene.hud.stats
		assert_eq(st.compact, LayoutScales.VERIFIED_MAX >= HudStats.FOLD_SCALE, "%s: the labels fold at big text only" % screen)
		for r in st.tag_rects():
			assert_true(r.end.x <= st.size.x + 0.5, "%s: a tag stays in the row" % screen)
	# A fight keeps its height (compact tags are still allowed there).
	var fight := HudStats.new()
	fight.max_height = HudBar.BAND_HEIGHT
	fight.size = Vector2(500, 60)
	fight.items = scene.hud.stats.items
	assert_true(fight.get_combined_minimum_size().y <= HudBar.BAND_HEIGHT + 0.5, "a fight's tags keep the band's height")
	fight.free()


func test_the_route_view_has_its_legend() -> void:
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene := _netrun()
		await _frames()
		# H23 S7 (updated on purpose): the route's own key (its node kinds), not the map's.
		var legend: RouteLegend = null
		for n in _all(scene._panel):
			if n is RouteLegend:
				legend = n
		assert_not_null(legend, "the route view mounts the route key")
		if legend != null:
			assert_true(legend.is_visible_in_tree())
			var lr := legend.get_global_rect()
			assert_true(Rect2(Vector2.ZERO, CANVAS).encloses(lr), "the legend is on screen at %.1f: %s" % [scale, lr])
			for c in _controls(scene._panel):
				if legend.is_ancestor_of(c):
					continue  # W8b: its own ROUTE KEY fold button
				assert_false(lr.intersects(c.get_global_rect()), "the legend covers '%s'" % c.get("text"))
		scene.get_parent().queue_free()
		await _frames(2)


func test_route_buttons_draw_the_map_icon_of_their_node() -> void:
	var scene := _netrun()
	await _frames()
	var s := RunManager.netrun
	var g: Dictionary = scene.route_graph()
	var kinds := {}
	for n in g["nodes"]:
		kinds[n["id"]] = String(CityMapOverlay.route_kind(int(s.run.map.get_node(n["id"])["type"]), bool(s.run.map.get_node(n["id"])["elite"])))
	var available := s.available_nodes()
	for i in available.size():
		var b := scene._panel.find_child("Node%d" % (i + 1), true, false) as Button
		assert_ne(IconMark.map_kind_of(b), "", "a map icon")
		assert_eq(IconMark.map_kind_of(b), kinds[available[i]], "the same icon kind as its node on the map")
		var mark := b.get_node("IconMark") as IconMark
		assert_eq(mark.color, scene.ROUTE_NEXT_COLOR, "the map's colour for a next node")


func test_grid_runs_show_the_map_icon_and_tier_pips() -> void:
	var hq := _open(HQ)
	await _frames()
	hq.show_grid()
	await _frames()
	var runs: Node = hq._panel.find_child("RunsOpen", true, false)
	assert_not_null(runs)
	var nodes := {}
	for n in hq.grid_graph()["nodes"]:
		nodes[n["id"]] = n
	var checked := 0
	for b in _all(runs):
		if b is Button and String(b.name).begins_with("Run_"):
			var id := StringName(String(b.name).trim_prefix("Run_"))
			var site := CampaignRules.site_data(RunManager.corporation, id)
			assert_eq(IconMark.map_kind_of(b), String(nodes[id]["kind"]), "%s: the map's icon kind" % id)
			assert_eq(int(b.get_meta(&"tier_pips")), site.tier, "%s: a pip a tier" % id)
			assert_true((b as Button).text.begins_with("T%d" % site.tier), "the tier in words too")
			checked += 1
	assert_true(checked > 0, "runs checked")
	var pick: Node = hq._panel.find_child("OperativeIcon", true, false)
	assert_not_null(pick, "the operative dropdown has its icon")
