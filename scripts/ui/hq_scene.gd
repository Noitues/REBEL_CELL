extends Control
## HQ scene: start screen (seed, ICE, home server, profile), HQ (roster, recruit, station,
## boosts, unlocks, Rank 3 segment swaps, Armory, story, pending raids), City Grid (Site
## status and actions, node install with unlock gating, upgrades), raid setup with exact
## projection, the raid playout with speed controls, the summary, campaign end. Every
## action goes through RunManager and CampaignRules; the scene only displays state.

## H24 S3/S4: the words in these constants are translation keys (the "# TR" marker exports
## them), translated where they are shown; every panel shows its words as given
## (TextDb.shown_as_given), translated once where it is built.
const STATUS_NAMES := {GridState.SiteStatus.CORPORATE: "corporate", GridState.SiteStatus.CLEARED: "cleared", # TR
	GridState.SiteStatus.CLAIMED: "claimed", GridState.SiteStatus.SEIZED: "SEIZED"} # TR

## Screen numbers on the HUD strip, by panel name (STYLE_GUIDE 4, "Neon city"); the
## titles are `screen_title`.
const SCREEN_NUMBERS := {"start": "00", "hq": "01", "grid": "02", "raid": "03", "raid_playout": "03", "raid_summary": "03"}

## The home server's name on the Grid, the raid map and the orders (never its id).
const HOME_LABEL := "CORE" # TR
## Event types that pop a toast (H20: the log strip is optional): refusals in pink,
## news in acid.
const TOAST_WARN_EVENTS: Array[String] = ["refused", "deploy_failed", "undock_failed"]
const TOAST_NEWS_EVENTS: Array[String] = ["unlocked"]
## The Grid's side column and the raid setup column (px).
const GRID_SIDE_WIDTH := 440.0
const RAID_SIDE_WIDTH := 380.0
## W8b: the raid setup's side column at big text (it holds the loadout, px).
const RAID_SIDE_BIG := 650.0
## Room for the Grid side column's scroll bar (px).
const SIDE_SCROLLBAR := 14.0
## Glyphs for Site objectives and facts on badges (the map uses the same).
const GLYPH_EXPLOIT := "◈"
const GLYPH_HEAT := "❄"
const GLYPH_BOSS := "✦"
const GLYPH_HOME := "⌂"
const GLYPH_NODE := "⬡"
const GLYPH_RULE := "!"
const GLYPH_UPGRADE := "▲"
const GLYPH_GUARD := "☻"
const GLYPH_THREAT := "◆"
const GLYPH_ENTRY := ">"
const GLYPH_LINK := "⛓"
## Raid setup: the projection stamp's side and a node's target button width (px).
const PROJECTION_STAMP := 124.0
## The pause menu's least top (px); it opens under the subtitle band.
const PAUSE_TOP := 100.0
## How much of the text scale the forecast stamp's size follows.
const PROJECTION_FOLLOW := 0.3
## The forecast stamp's words (H22 #9): a caption over the verdict.
const FORECAST_CAPTION := "IF THE RAID\nRUNS NOW:" # TR
## ANIM-5: the playout's forecast stamp, resolved: the caption over the real verdict.
const RESULT_CAPTION := "RAID\nRESULT:" # TR
## Art pass W8b (ART_BIBLE §11 Raid): the playout's stamp says LIVE while the raid plays
## (never the setup's "IF THE RAID RUNS NOW"), and RESULT the moment it ends.
const LIVE_CAPTION := "RAID\nLIVE:" # TR
## The raid setup's big button (H24 S14: "RUN THE RAID" read like attacking).
const START_DEFENSE := "START DEFENSE" # TR
## Art pass W9F: the text scale from which the new campaign's START and SHARE CODES stack.
const START_STACK_SCALE := 1.8
## Words the screens translate that sit in the core's data (H24 S1: exported by the "# TR"
## marker): run kinds, raid outcomes, Exploit types and rule modifier names.
const RUN_KIND_WORDS := ["netrun", "patrol", "reclaim", "boss"] # TR
const OUTCOME_WORDS := ["HOLDS", "DISABLED", "SEIZED", "PASSED"] # TR
const EXPLOIT_WORDS := ["Intel", "Breach", "Virus"] # TR
const MODIFIER_WORDS := ["Heat Gain", "Heat Sink", "Heat Objective Sites", "Elite Frequency", "Cycle Price", "Shop Stock", # TR
	"Raid Strength", "Raid Extra Wave", "Enemy Resistance", "Death Heat", "Exploit Heat", "Boss Phase Early", # TR
	"Boss Extra Pointer", "Starting Bug Card", "No First Turn Free Nudge", "Repair Cost", "Seized Raid Strength", # TR
	"Purge Threshold", "Boss Strength"] # TR
## Passes framing the raid map beside its legend (each on the positions the last one gave).
const RAID_REFRAMES_MAX := 10
## Passes fitting the Grid map into the screen beside its column and legend (H23 #5).
const GRID_FITS_MAX := 4
## The Grid map's own framing (the city's zoom, and where the graph's centre lands as a
## screen fraction) before it is fitted to the screen.
const GRID_ZOOM := 0.72
const GRID_ANCHOR := Vector2(0.31, 0.54)
## The smallest the fit may make the Grid map (the city's zoom).
const GRID_MIN_ZOOM := 0.3
## H24 K1: from this text scale the Grid's step buttons show their icons (and "<" / ">")
## without words, their words in the tooltip, so the column keeps its width (the same
## scale the map key folds at).
const STEP_ICONS_SCALE := MapLegend.FOLD_SCALE
## The deploy steps' icons, a little larger than a button's.
const DEPLOY_ICON_GROW := 1.2
## The raid orders list's least height at text scale 1.0 (px).
const ORDERS_MIN_HEIGHT := 70.0
const TARGET_BUTTON_WIDTH := 150.0
## Entry Sites shown one badge each up to this many; more collapse into a count.
const MAX_ENTRY_BADGES := 3
## Height of the raid's node orders list (px); more nodes scroll inside it.
## PIRATE RADIO: width, room for its title and foot (px) and the lines it shows at once.
const RADIO_WIDTH := 230.0
const RADIO_TOP := 24.0
const RADIO_BOTTOM := 8.0
const RADIO_LINES := 4
## The launch button on a Site's card: the same words as the HQ's JACK IN stamp (H21 #21).
const JACK_IN := "JACK IN" # TR
## Art pass W8b (ART_BIBLE §11 HQ): the HQ's JACK IN stamp's side and how far it grows with
## the text (px; the page's first focal point), the menu column's least width, the deck
## monitor's map at text scale 1.0 and its growth, and the crew grid's columns (fewer at
## big text: §5.3 3 -> 2).
const JACK_SIDE := 140.0
const JACK_GROW_MAX := 1.3
const HQ_LEFT_WIDTH := 300.0
const MONITOR_MAP := Vector2(420, 170)
const MONITOR_GROW_MAX := 1.3
const MONITOR_MAP_LOW := 110.0
const CREW_COLUMNS := 3
const CREW_COLUMNS_BIG := 2
## The Grid Site card's node tiles (the node to build) at text scale 1.0 (px).
const NODE_TILE := Vector2(132, 60)
## W8b: the Site card's fixed body height at text scale 1.0 (px; its content scrolls inside).
const SITE_CARD_HEIGHT := 240.0
const SITE_CARD_BODY_MIN := 140.0
## W8b: a Rank 3 dossier's button to its ring swaps (the loadout's SPINNER tab).
const RING_SWAPS := "RING SWAPS" # TR
const RING_SWAPS_TIP := "Rank 3: swap the inner ring's segments on the SPINNER tab, beside the wheel." # TR
## Art pass W8b (§11 New campaign): the planning table's width the pickers fill (px), the
## corporation dossier and small tiles at text scale 1.0, the ICE line's and the profile
## records' widths, the share code field's, and the highest seed.
const PLAN_WIDTH := 1200.0
const PLAN_CORP_TILE := Vector2(208, 84)
const PLAN_SMALL_TILE := Vector2(172, 76)
const PLAN_ICE_TEXT := 420.0
const PLAN_RECORDS_WIDTH := 360.0
const PLAN_CODE_WIDTH := 300.0
const SEED_MAX := 999999
## Gap round a price's currency icon at a button's right end (px).
const PRICE_ICON_GAP := 8.0
## What each Site status means (the selected Site card's status badge).
const STATUS_TIPS := {GridState.SiteStatus.CORPORATE: "Corporate: run it to clear it.", # TR
	GridState.SiteStatus.CLEARED: "Cleared: claim it to build a node of your network.", # TR
	GridState.SiteStatus.CLAIMED: "Claimed: part of your network; it defends in raids.", # TR
	GridState.SiteStatus.SEIZED: "Seized by a raid: run it again to take it back."} # TR

var _status: Label
## Top strip: screen title and the status line (`_status`).
var hud: HudBar
## The subtitles' band under the top bar (H21 #11).
var subtitle_strip: SubtitleStrip
## "More below" at the foot of a page that scrolls on (H21 #15: the HQ's BLACK MARKET),
## and at the foot of the Grid's side column (freed with the Grid).
var more_hint: ScrollHint
var side_hint: ScrollHint = null
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var panel_name: String = ""
var background: CyberdeckBackground
var wireframe: WireframeBackground
## Art pass W8b: the HQ page's cyberdeck frame (DeckFrame; shown on the HQ page only).
var deck_frame: DeckFrame
var grid_view: GridMapView = null
var playout: RaidPlayoutPanel = null
## The raid setup's map key (placed clear of the nodes).
var raid_legend: MapLegend = null
## How many times the raid map was framed to clear the legend's column (at most
## RAID_REFRAMES_MAX: labels keep their size as the map zooms, so a second pass settles it).
var _raid_reframes: int = 0
## The Grid map's key, on the map (H23 #3), and the passes fitting the map so far.
var grid_legend: MapLegend = null
var _grid_fits: int = 0
## ANIM-5: the Grid camera has leaned toward the selected Site on this page.
var _grid_leaned: bool = false
## Leans shorter than this (screen px) are not worth a new frame.
const GRID_LEAN_MIN := 1.0
## The key's size the last fit laid the map out for.
var _grid_legend_size: Vector2 = Vector2.ZERO
## The map drawn on the city (Grid, raids); freed when another panel opens.
var city_overlay: CityMapOverlay = null
var _settings_panel: PauseMenu = null
var _last_warned_raid: String = ""
## Site picked on the Grid map (its card and actions show in the side column) or the
## raid target node.
var selected_site: StringName = &""
## Operative picked on a dossier: VIEW LOADOUT and the Daemon tray show them.
var selected_operative: StringName = &""
## Buttons carrying a key hint (relabelled on Settings.hints_changed).
var _hint_buttons: Array[Button] = []
## Pad button prompts at the foot of the screen (H23 S11).
var pad_prompts: PadPrompts
## ANIM-4: the page's prompts (restored when a carry ends).
var _page_prompts: Array = []
## ANIM-4: drag and drop on the HQ, the Grid and the raid setup (DropLayer).
var drops: DropLayer
## ANIM-4: the Grid's Site card crew chips and its JACK IN (drop targets and sources).
var _grid_chips: Array[CrewChip] = []
var _jack_button: Button = null
## ANIM-4: map-node target size on the HQ's mini-map (px, as GridMapView.site_at's reach).
const MINI_TARGET_R := 24.0
## ANIM-4: pages whose items the pick-up key takes (the pad prompt names it).
const DRAG_PANELS: Array[String] = ["hq", "grid", "raid"]
## Whether the last page entered a new panel (its entrance plays) or rebuilt the same one.
var entering: bool = false


func _ready() -> void:
	UiTheme.apply(self)
	# Capture variants (ANIM-6): --demo-set / --demo-speed tune a copy of the motion table.
	MotionDemo.apply_args()
	# Subtitles sit in the top band, clear of every control on these screens (H20).
	Dialogue.dock_default()
	Settings.hints_changed.connect(_relabel_hints)
	_build_ui()
	var args := OS.get_cmdline_user_args()
	for a in args:
		# Design review: portrait and slice-icon styles.
		if a.begins_with("--demo-portrait="):
			PortraitArt.style = int(a.trim_prefix("--demo-portrait="))
		elif a.begins_with("--demo-iconstyle="):
			SliceIcon.style = int(a.trim_prefix("--demo-iconstyle="))
		elif a.begins_with("--demo-text-scale="):
			# ANIM-R2 R13 captures: the screen at a text size (1.3, 1.6). ANIM-R3 B9: this run
			# only, never saved to the player's settings (like --demo-scale).
			Settings.text_scale = float(a.trim_prefix("--demo-text-scale="))
			Settings.changed.emit()
	if args.has("--demo-start"):
		RunManager.save_slot = "demo"
		show_start()
		return
	if args.has("--demo-hq") or args.has("--demo-grid") or args.has("--demo-raid") or args.has("--demo-playout"):
		# Dev shortcut for screenshots: godot --path . -- --demo-grid (own save slot)
		RunManager.save_slot = "demo"
		new_campaign(1)
		for a in args:
			if a.begins_with("--demo-corp="):
				# Screenshot campaign against another corporation (bypasses Profile unlocks,
				# campaign-only).
				var corp := RunManager.lookup().get_content(StringName(a.trim_prefix("--demo-corp="))) as CorporationData
				if corp != null:
					var home := RunManager.lookup().get_content(RunManager.DEFAULT_HOME) as HomeServerVariantData
					RunManager.corporation = corp
					RunManager.campaign = CampaignRules.new_campaign(corp, RunManager.config(), RunManager.lookup(), 1,
						RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, 0, home)
					show_hq()
		if args.has("--demo-classes"):
			# Screenshot roster: one operative of every class (bypasses Profile unlocks,
			# campaign-only, never saved to the profile).
			RunManager.campaign.roster.clear()
			for id in [&"ghost", &"rigger", &"botnet", &"wrecker", &"phantom", &"overclocker", &"hivemind"]:
				RunManager.campaign.recruit(RunManager.lookup().get_content(id) as ClassData)
			show_hq()
		for a in args:
			# ANIM-R2 R1 / R9 profiling: from the HQ page the Grid opens N frames in, the HQ comes
			# back N frames later and the Grid opens again N frames after that (a re-open).
			if a.begins_with("--demo-grid-open="):
				var n := int(a.trim_prefix("--demo-grid-open="))
				MotionDemo.after_frames(self, n, show_grid)
				MotionDemo.after_frames(self, n * 2, show_hq)
				MotionDemo.after_frames(self, n * 3, show_grid)
		if args.has("--demo-grid") or args.has("--demo-raid") or args.has("--demo-playout"):
			var c := RunManager.campaign
			c.schematics = 100
			var grid_data := RunManager.corporation.city_grid
			var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
			CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), _demo_run(first))
			CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
			c.armory = [&"turret", &"ice_lock", &"decoy"]
			if args.has("--demo-raid") or args.has("--demo-playout"):
				CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
				show_raid()
				if args.has("--demo-playout"):
					fight_raid()
				for a in args:
					# ANIM-R1 M2 profiling: the setup shows, START DEFENSE is pressed N frames in.
					if a.begins_with("--demo-playout-delay="):
						MotionDemo.after_frames(self, int(a.trim_prefix("--demo-playout-delay=")), fight_raid)
			else:
				for sd in grid_data.sites:
					if sd.objective == RC.SiteObjective.EXPLOIT:
						selected_site = sd.id
						break
				show_grid()
		# ANIM-5 frame capture: `--demo-anim=<id>` plays one motion once the city has baked.
		for a in args:
			if a.begins_with("--demo-anim="):
				_demo_anim.call_deferred(a.trim_prefix("--demo-anim="))
		return
	if RunManager.campaign == null and RunManager.has_save():
		RunManager.resume()
	if RunManager.campaign == null:
		show_start()
	elif RunManager.campaign.is_over():
		show_end()
	else:
		show_hq()


# --- Public API (buttons and the integration tests) ---------------------------------------

## Best ICE per corporation (GDD 3.4) and the road to REBEL_CELL.
func ice_records_text() -> String:
	var p := RunManager.profile
	var lookup := RunManager.lookup()
	var parts := PackedStringArray()
	var cleared := 0
	var total := 0
	var need := RunManager.config().rebel_cell_unlock_ice
	var corp_ids := lookup.ids_of_class(&"CorporationData")
	for id in corp_ids:
		var corp := lookup.get_content(id) as CorporationData
		if corp == null:
			continue
		if corp.generated_from_profile and not CampaignRules.corporation_available(p, lookup, corp):
			continue
		parts.append("%s %s" % [TextDb.t(corp, "display_name"), HudStats.ice_value(p.best_ice_for(corp.id))])
		if not corp.generated_from_profile:
			total += 1
			if p.best_ice_for(corp.id) >= need:
				cleared += 1
	var tail := (tr("Something opens at ICE %d everywhere (%d/%d).") % [need, cleared, total]) if cleared < total else ""
	return tr("Best ICE: %s. %s") % [", ".join(parts), tail]


## Starts the campaign a share code describes (GAP_ANALYSIS P2 12). Locked choices fall
## back like the start panel (RunManager.new_campaign). Returns false for a bad code.
func start_from_code(code: String) -> bool:
	var d := CampaignCode.decode(code)
	if d.is_empty():
		var refused: Array[Dictionary] = [{"type": "refused", "text": tr("That is not a campaign code.")}]
		_report(refused)
		return false
	new_campaign(int(d["seed"]), int(d["ice"]), d["home"], d["class"], d["corporation"])
	return true


func new_campaign(seed: int, ice: int = 0, home_variant_id: StringName = RunManager.DEFAULT_HOME, class_id: StringName = RunManager.DEFAULT_CLASS, corporation_id: StringName = RunManager.DEFAULT_CORPORATION) -> void:
	RunManager.new_campaign(seed, corporation_id, ice, home_variant_id, class_id)
	# Art pass W9F (W8d request): a new campaign starts from no corp lean; the cities read
	# the new campaign's own progress again.
	for bg in [background, wireframe]:
		if bg != null and bg.city != null:
			bg.city.atmosphere().clear_campaign_progress()
	_log.append_text("[b]New campaign[/b] (seed %d, ICE %d, %s) against %s. Story path: %s.\n" % [seed, RunManager.campaign.ice_level,
		RunManager.campaign.home_variant_id, TextDb.t(RunManager.corporation, "display_name"), RunManager.campaign.story_path_id])
	show_hq()


func resume() -> void:
	if RunManager.scene_change_pending():
		return
	if RunManager.resume():
		_log.append_text("[b]Resumed.[/b]\n")
		if RunManager.has_active_run():
			RunManager.go_to_netrun()
		else:
			show_hq()
	else:
		_log.append_text("[color=orange]Nothing to resume.[/color]\n")
		notify(tr("Nothing to resume."), true)


## ANIM-R1 M8: whether the screen a jack out lands on is built and framed (Fx keeps its
## cover up until then): a page is on, the city behind it was drawn under the current
## camera (its placement: every map node and label in place), and no map fit or legend
## placement is still waiting for a redraw. ANIM-R2 R1: the city's image is not waited for;
## it fades in over the night sky when its bake lands.
func arrival_ready() -> bool:
	if _panel == null or not is_instance_valid(_panel) or not _panel.is_inside_tree():
		return false
	var city: NeonCity = background.city if background.visible else wireframe.city
	if city != null and city.is_visible_in_tree():
		if not city.camera_settled():
			return false
		if city.rebuilt.is_connected(fit_grid_map) or get_tree().process_frame.is_connected(fit_grid_map) \
				or get_tree().process_frame.is_connected(place_raid_legend):
			return false
	return true


func launch(site_id: StringName, operative_id: StringName) -> bool:
	# ANIM-R1 M1: a press during the jack (a second JACK IN) does nothing.
	if RunManager.scene_change_pending():
		return false
	var err := RunManager.launch_error(operative_id, site_id)
	if err != "":
		_log.append_text("[color=orange]%s[/color]\n" % err)
		notify(err, true)
		return false
	# ANIM-R3 B1: the run is built (and saved) at the jack's scene switch, under its opaque
	# cover (at once when no jack plays): it took ~45 ms of the cover's first frame.
	RunManager.go_to_netrun(_start_launched.bind(operative_id, site_id), site_id)
	return RunManager.netrun != null or RunManager.scene_change_pending()


## ANIM-R3 B1: starts the launched run (RunManager.go_to_netrun calls it at the switch).
func _start_launched(operative_id: StringName, site_id: StringName) -> void:
	var s := RunManager.start_run(operative_id, site_id)
	if s == null:
		return
	_report(s.last_events)
	# H24 S15: the briefing belongs to the run's route (it ends when the player leaves it).
	Dialogue.briefing(RunManager.campaign.corporation_id, site_id, RunManager.campaign.campaign_seed, "route")


func claim(site_id: StringName, node_type_id: StringName) -> void:
	_report(CampaignRules.claim(RunManager.campaign, RunManager.corporation, RunManager.config(), RunManager.lookup(), site_id, node_type_id, RunManager.profile))
	RunManager.autosave()
	show_grid()


func repair(site_id: StringName) -> void:
	_report(CampaignRules.repair(RunManager.campaign, RunManager.config(), RunManager.lookup(), site_id))
	RunManager.autosave()
	show_grid()


func upgrade(site_id: StringName) -> void:
	_report(CampaignRules.upgrade_node(RunManager.campaign, RunManager.config(), RunManager.lookup(), site_id))
	RunManager.autosave()
	show_grid()


func repair_home() -> void:
	_report(CampaignRules.repair_home(RunManager.campaign, RunManager.config()))
	RunManager.autosave()
	show_hq()


func recruit(class_id: StringName = RunManager.DEFAULT_CLASS) -> void:
	var before := RunManager.campaign.roster.size()
	_report(RunManager.recruit(class_id))
	RunManager.autosave()
	show_hq()
	# ANIM-6: the new operative's dossier drops onto the crew with its tape.
	var c := RunManager.campaign
	if c.roster.size() > before and _panel != null:
		var card := _panel.find_child("Crew_%s" % c.roster[c.roster.size() - 1].id, true, false) as Control
		if card != null:
			PageTransition.enter(card, PageTransition.Look.PAPER)


func station(operative_id: StringName, site_id: StringName) -> void:
	_report(CampaignRules.station(RunManager.campaign, RunManager.lookup(), operative_id, site_id))
	RunManager.autosave()
	show_hq()


func recall(operative_id: StringName) -> void:
	CampaignRules.recall(RunManager.campaign, operative_id)
	RunManager.autosave()
	show_hq()


func buy_heat_reduction() -> void:
	_report(CampaignRules.buy_heat_reduction(RunManager.campaign, RunManager.config()))
	RunManager.autosave()
	show_hq()


func buy_boost(boost_id: StringName) -> void:
	var spent := RunManager.campaign.schematics
	var button := _market_button("Boost_%s" % boost_id)
	_report(CampaignRules.buy_boost(RunManager.campaign, RunManager.config(), boost_id))
	_stamp_sold(button, spent)
	RunManager.autosave()
	show_hq()


func purchase_unlock(unlock_id: StringName) -> void:
	var spent := RunManager.campaign.schematics
	var button := _market_button("Unlock_%s" % unlock_id)
	_report(CampaignRules.purchase_unlock(RunManager.campaign, RunManager.profile, RunManager.lookup(), unlock_id))
	_stamp_sold(button, spent)
	RunManager.save_profile()
	RunManager.autosave()
	show_hq()


## A Black Market button on the page on screen (null when none).
func _market_button(button_name: String) -> Control:
	return _panel.find_child(button_name, true, false) as Control if _panel != null else null


## ANIM-6: a Black Market buy stamps SOLD where its button was (when Schematics were spent).
func _stamp_sold(button: Control, schematics_before: int) -> void:
	if button != null and RunManager.campaign.schematics < schematics_before:
		FlightFx.stamp_on(self, button, tr("SOLD"))


func swap_segment(operative_id: StringName, index: int, segment_id: StringName) -> void:
	_report(CampaignRules.swap_ring_segment(RunManager.campaign, RunManager.lookup(), operative_id, index, segment_id))
	RunManager.autosave()
	show_hq()


func deploy_asset(armory_index: int, site_id: StringName) -> void:
	# ANIM-R3 B5: the forecast before, so the drop can show what it changed.
	var was := forecast_values()
	var events := CampaignRules.deploy_asset(RunManager.campaign, RunManager.config(), RunManager.lookup(), armory_index, site_id)
	_report(events)
	RunManager.autosave()
	if panel_name == "raid":
		wireframe.hold_camera()  # ANIM-5: the map holds still while the page rebuilds
	show_raid()
	if not events.is_empty() and String(events[0].get("type", "")) != "refused":
		play_asset_drop(site_id, was)


## ANIM-R4 H10: the Sites' clear previews (CampaignRules.clear_preview: a copy of the
## campaign runs each Site's clear; ~4 ms a Site, ~44 ms of the Grid's first frame) kept for
## the campaign state they were worked out for (`_previews_key`: the state's serialised hash),
## worked out ahead on the HQ page a Site a frame, else when the Grid needs them.
var _previews: Dictionary = {}
var _previews_key: int = 0
var _warm_sites: Array[StringName] = []


## The campaign state's key for the preview cache (its serialised form's hash).
static func campaign_key(c: CampaignState) -> int:
	return var_to_str(c.to_dict()).hash() if c != null else 0


## Drops the cached previews when the campaign changed since they were worked out.
func _sync_previews() -> void:
	var key := campaign_key(RunManager.campaign)
	if key != _previews_key:
		_previews.clear()
		_previews_key = key


## Site `s`'s clear preview for the campaign as it stands (cached: `_sync_previews` first).
func clear_preview_of(s: SiteData) -> Dictionary:
	if not _previews.has(s.id):
		_previews[s.id] = CampaignRules.clear_preview(RunManager.campaign, RunManager.corporation, RunManager.config(), s, RunManager.lookup())
	return _previews[s.id]


## ANIM-R4 H10: works out the open runs' previews ahead, one a frame, while the HQ page shows
## (the Grid opens with them ready). Stops when the page changes.
func _warm_previews() -> void:
	if RunManager.campaign == null:
		return
	_sync_previews()
	_warm_sites.clear()
	var sites := RunManager.launchable_sites()
	sites.append_array(RunManager.patrol_sites())
	for s in sites:
		if not _previews.has(s.id):
			_warm_sites.append(s.id)
	if not _warm_sites.is_empty() and is_inside_tree() and not get_tree().process_frame.is_connected(_warm_preview_step):
		get_tree().process_frame.connect(_warm_preview_step, CONNECT_ONE_SHOT)


func _warm_preview_step() -> void:
	if panel_name != "hq" or RunManager.campaign == null or _warm_sites.is_empty() or not is_inside_tree():
		return
	_sync_previews()
	var sd := CampaignRules.site_data(RunManager.corporation, _warm_sites.pop_front())
	if sd != null:
		clear_preview_of(sd)
	if not _warm_sites.is_empty() and not get_tree().process_frame.is_connected(_warm_preview_step):
		get_tree().process_frame.connect(_warm_preview_step, CONNECT_ONE_SHOT)


## ANIM-R3 B5: the raid forecast's integrity after the raid per node (site id -> int; home
## included); {} with no raid pending.
func forecast_values() -> Dictionary:
	var out := {}
	var projection := RunManager.project_raid() if RunManager.campaign != null else null
	if projection == null:
		return out
	for id in projection.nodes:
		out[String(id)] = int(projection.nodes[id].get("after", 0))
	return out


## ANIM-R3 B5: the forecast numbers that moved since `was` (forecast_values), by Site id:
## [{"site", "from", "to"}].
func forecast_changes(was: Dictionary) -> Array:
	var out: Array = []
	if was.is_empty():
		return out
	var now := forecast_values()
	var ids := now.keys()
	ids.sort()
	for id in ids:
		if was.has(id) and int(was[id]) != int(now[id]):
			out.append({"site": StringName(id), "from": int(was[id]), "to": int(now[id])})
	return out


## ANIM-5 (4.14): the asset just deployed on `site_id` drops onto its node with a stamp
## (the hook drag-and-drop deploying calls; the end state at once without motion).
## ANIM-R3 B5: `was` (forecast_values before the change) lets the landing show the forecast
## numbers it changed.
func play_asset_drop(site_id: StringName, was: Dictionary = {}) -> void:
	if city_overlay != null and is_instance_valid(city_overlay):
		# ANIM-R2 R6: it drops once the camera has panned to the page's new frame, and keeps its
		# name under it.
		var placed: Array = RunManager.campaign.grid.site(site_id).get("assets", []) if RunManager.campaign != null else []
		var label := _display(StringName(placed[placed.size() - 1])) if not placed.is_empty() else ""
		var bg := wireframe
		city_overlay.drop_asset(site_id, func() -> bool: return not is_instance_valid(bg) or not bg.camera_easing(), label, forecast_changes(was), threat_road(site_id))


## ANIM-R4 H11b: the road threats take from `site_id` to CORE (the Grid's next hops toward
## home, as the threat routes are drawn): the drop's pulse runs it. [] when there is none.
func threat_road(site_id: StringName) -> Array:
	var c := RunManager.campaign
	if c == null or RunManager.corporation == null:
		return []
	var road: Array = [site_id]
	var cur := site_id
	var guard := 0
	while cur != c.grid.home_site_id and guard < ROAD_HOPS_MAX:
		guard += 1
		cur = c.grid.next_hop(cur, c.grid.home_site_id, RunManager.corporation.city_grid)
		if cur == &"" or road.has(cur):
			return []
		road.append(cur)
	return road if cur == c.grid.home_site_id else []


## The most hops a drop's road to CORE may take (as CityLayout.threat_paths).
const ROAD_HOPS_MAX := 12


func move_asset(from_site: StringName, index: int, to_site: StringName) -> void:
	_report(CampaignRules.move_asset(RunManager.campaign, RunManager.config(), RunManager.lookup(), from_site, index, to_site))
	RunManager.autosave()
	show_raid()


func fight_raid() -> void:
	# ANIM-5: the playout starts from the Grid as it stood (a view copy, read only) and the
	# city holds its pre-raid tint until the raid has played; the result spreads at the end.
	var before := RunManager.campaign.duplicate_state() if RunManager.campaign != null else null
	wireframe.city.pin_influence(CityInfluence.of(RunManager.campaign, RunManager.corporation))
	if Motion.animating() and RunManager.campaign != null:
		hud_home_shown = RunManager.campaign.grid.home_integrity  # ANIM-R1 M4: HOME rolls down as hits land
		# ANIM-R4 H11a: Heat and RAIDS hold too, until the feed tells what changes them.
		hud_heat_shown = RunManager.campaign.heat
		hud_raids_shown = RunManager.campaign.pending_raids.size()
	var events := RunManager.fight_raid()
	_report(events)
	if events.is_empty():
		wireframe.city.release_influence()
	show_raid_playout(events, before)
	# ANIM-R1 M2: the post-raid look bakes while the raid plays (the pre-raid one stays
	# pinned), so the result spreads at the end without the ~2 s freeze of a bake then.
	if before != null and not events.is_empty():
		_prebake_playout(before, CityInfluence.of(RunManager.campaign, RunManager.corporation))


# --- Drag and drop (Animation pass ANIM-4) --------------------------------------------------
# Every drop mirrors a button: the layer emits the intent, and `_on_dropped` makes the same
# call that button makes. Whether a target takes an item is the rules' own answer, asked of
# a copy of the campaign (`_dry`), so nothing here decides a rule.

## Sets the page's pad prompts (kept, so a carry can swap them and put them back).
func set_page_prompts(list: Array) -> void:
	_page_prompts = list
	if drops == null or drops.mode != DropLayer.Mode.CARRY:
		pad_prompts.set_prompts(list)


func _on_carry_changed(carrying: bool) -> void:
	pad_prompts.set_prompts([[&"ui_accept", "Drop"], [&"ui_cancel", "Cancel"]] if carrying else _page_prompts) # TR


## HQ: the crew's posts on the mini-map (claimed nodes: station; CORE: recall), the crew
## window (recruits land there) and the next run's kit (boosts).
func _register_hq_drops(crew: Control, mini: GridMapView, queue: Control) -> void:
	var c := RunManager.campaign
	for site_id in c.grid.claimed_ids():
		var sid: StringName = site_id
		var kind := "recall" if sid == c.grid.home_site_id else "station"
		drops.add_target("%s:%s" % [kind, sid], ["crew"], kind, sid, _mini_rect.bind(weakref(mini), sid))
	drops.add_target("roster", ["recruit"], "roster", null, DropLayer.rect_of(crew))
	drops.add_target("queue", ["boost"], "queue", null, DropLayer.rect_of(queue))


## Site `site_id`'s spot on the HQ mini-map `mini_ref` (global; empty when not shown).
func _mini_rect(mini_ref: WeakRef, site_id: StringName) -> Rect2:
	var mini: GridMapView = mini_ref.get_ref()
	if mini == null or not mini.is_visible_in_tree() or mini.is_queued_for_deletion():
		return Rect2()
	var at := mini.get_global_transform() * mini.position_of(site_id)
	return Rect2(at - Vector2.ONE * MINI_TARGET_R, Vector2.ONE * MINI_TARGET_R * 2.0)


## Grid: the Site card's crew chips drag onto its JACK IN.
func _register_grid_drops(site: SiteData) -> void:
	if _jack_button == null or site == null:
		return
	for chip in _grid_chips:
		drops.add_source(chip, {"kind": "crew", "op": chip.operative_id, "motion": &"crew_assign", "prefer": site.id})  # W8b: a press picks (pick_operative)
	drops.add_target("jack", ["crew"], "jack", site.id, DropLayer.rect_of(_jack_button))


## Raid setup: every claimed node on the map and in YOUR NODES takes assets; the DEFENSE
## LOADOUT takes a placed asset back; the target node's assets drag off the map too.
func _register_raid_drops(claimed: Array[StringName], loadout: Control) -> void:
	for site_id in claimed:
		var sid: StringName = site_id
		var on_map := _map_node_rect(sid).has_area()
		# The node's own asset drop (ANIM-5's hook) is the landing on the map.
		drops.add_target("node:%s" % sid, ["asset", "placed"], "node", sid, _map_node_rect.bind(sid), true, false)
		var row := _panel.find_child("Order_%s" % sid, true, false) as Control
		if row != null:
			drops.add_target("row:%s" % sid, ["asset", "placed"], "node", sid, DropLayer.rect_of(row), not on_map)
	drops.add_target("armory", ["placed"], "armory", &"", DropLayer.rect_of(loadout))
	var overlay := city_overlay
	overlay.set_drag_forwarding(func(at: Vector2) -> Variant:
		var id := overlay.node_at(at)
		var assets := RunManager.campaign.grid.assets_on(id) if id != &"" else []
		if id == &"" or id != selected_site or assets.is_empty():
			return null
		return drops.begin_drag(null, _placed_payload(id, assets.size() - 1, assets[assets.size() - 1]), _map_node_rect(id), overlay), Callable(), Callable())


## Node `site_id`'s icon on the city map (global; empty when it is not on the map).
func _map_node_rect(site_id: StringName) -> Rect2:
	if city_overlay == null or not is_instance_valid(city_overlay) or not city_overlay.is_inside_tree():
		return Rect2()
	for n in city_overlay.nodes:
		if n["id"] == site_id:
			var p := city_overlay.icon_at(site_id)
			if p.x == INF:
				return Rect2()
			var xf := city_overlay.get_global_transform()
			var r := city_overlay.icon_radius(n) * xf.get_scale().x
			var c := xf * p
			return Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0)
	return Rect2()


## Whether `target` takes `payload`: "" yes, a reason (the rules' own refusal) no, or
## DropLayer.SKIP when the target is no place for it (where it already is).
func drop_error(payload: Dictionary, target: Dictionary) -> String:
	var c := RunManager.campaign
	if c == null:
		return DropLayer.SKIP
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var value: Variant = target.get("value")
	match [String(payload.get("kind", "")), String(target.get("kind", ""))]:
		["asset", "node"]:
			return _named(_dry(func(d: CampaignState) -> Array[Dictionary]: return CampaignRules.deploy_asset(d, cfg, lookup, int(payload["index"]), value)), [value])
		["placed", "node"]:
			if value == payload["site"]:
				return DropLayer.SKIP
			return _named(_dry(func(d: CampaignState) -> Array[Dictionary]: return CampaignRules.move_asset(d, cfg, lookup, payload["site"], int(payload["index"]), value)), [value, payload["site"]])
		["placed", "armory"]:
			return _dry(func(d: CampaignState) -> Array[Dictionary]: return CampaignRules.move_asset(d, cfg, lookup, payload["site"], int(payload["index"]), &""))
		["crew", "station"]:
			if CampaignRules.stationed_site(c, payload["op"]) == value:
				return DropLayer.SKIP
			return _named(_dry(func(d: CampaignState) -> Array[Dictionary]: return CampaignRules.station(d, lookup, payload["op"], value)), [value])
		["crew", "recall"]:
			var op := c.get_operative(payload["op"])
			if CampaignRules.stationed_site(c, payload["op"]) == &"":
				return tr("%s is at HQ already.") % (op.name if op != null else String(payload["op"]))
			return ""
		["crew", "jack"]:
			# ANIM-R1 (designer ruling 2026-09-27): a chip on JACK IN only picks who runs
			# it; the operative's own eligibility, not whether a run could start now.
			return _pick_error(payload["op"], value)
		["recruit", "roster"]:
			var cls := lookup.get_content(payload["cls"]) as ClassData
			return _dry(func(d: CampaignState) -> Array[Dictionary]: return CampaignRules.recruit(d, cfg, cls))
		["boost", "queue"]:
			return _dry(func(d: CampaignState) -> Array[Dictionary]: return CampaignRules.buy_boost(d, cfg, payload["boost"]))
		["segment", "ring"]:
			var op := c.get_operative(payload["op"])
			var current: StringName = op.ring_segment_ids[int(value)] if op != null and int(value) < op.ring_segment_ids.size() else &""
			if current == payload["segment"]:
				return DropLayer.SKIP
			return _dry(func(d: CampaignState) -> Array[Dictionary]: return CampaignRules.swap_ring_segment(d, lookup, payload["op"], int(value), payload["segment"]))
	return DropLayer.SKIP


## ANIM-R1 (designer ruling): picks operative `operative_id` in the Site card's list (a
## crew chip dropped on JACK IN) and puts focus on JACK IN; nothing starts.
func pick_operative(operative_id: StringName) -> void:
	var c := RunManager.campaign
	var op := c.get_operative(operative_id) if c != null else null
	if op == null or not op.alive:
		return
	_launch_op = operative_id
	# W8b (§10.2): the pick shows: the chip is stamped, the Polaroid beside JACK IN changes.
	for chip in _grid_chips:
		if is_instance_valid(chip):
			chip.picked = chip.operative_id == operative_id
	var rider := _panel.find_child("JackOperative", true, false) as CrewChip if _panel != null else null
	if rider != null:
		rider.show_operative(op.class_id, op.id, op.name)
		Motion.pop(rider, &"sticky_bump")
	var go := _panel.find_child("Launch", true, false) as Control if _panel != null else null
	if go != null and go.is_visible_in_tree():
		go.grab_focus.call_deferred()


## The operative JACK IN on the Grid's Site card launches: the one picked (a chip pressed or
## dropped on JACK IN), else the first living operative.
func launch_operative() -> StringName:
	var c := RunManager.campaign
	if c == null:
		return &""
	var living := c.living_operatives()
	for op in living:
		if op.id == _launch_op:
			return op.id
	return living[0].id if not living.is_empty() else &""


## W8b: the operative picked to run from the Grid (see launch_operative).
var _launch_op: StringName = &""


## Why operative `operative_id` can't run Site `site_id` ("" when they can), whatever
## else is under way (a pick is not a launch).
func _pick_error(operative_id: StringName, site_id: StringName) -> String:
	var c := RunManager.campaign
	var site := CampaignRules.site_data(RunManager.corporation, site_id)
	var op := c.get_operative(operative_id)
	if site == null or op == null:
		return DropLayer.SKIP
	var cls := RunManager.lookup().get_content(op.class_id) as ClassData
	return CampaignRules.launch_error(c, RunManager.corporation, RunManager.config(), op, cls, site)


## Runs rule call `f` on a copy of the campaign: its refusal text, or "" when it would go
## through. The real campaign is never touched.
func _dry(f: Callable) -> String:
	var events: Array[Dictionary] = f.call(RunManager.campaign.duplicate_state())
	for e in events:
		if String(e.get("type", "")) == "refused":
			return String(e.get("text", "refused"))
	return ""


## `text` (a rules refusal) with the Site ids in `ids` written as the screens name them
## (the rules speak in ids: "t1_a has no free asset slot").
func _named(text: String, ids: Array) -> String:
	for id in ids:
		if String(id) != "" and text.contains(String(id)):
			text = text.replace(String(id), site_name(StringName(String(id))))
	return text


## What a dragged item looks like (its ghost and flying copies): an asset card, a crew
## Polaroid, or a note with the item's name.
func drop_ghost(payload: Dictionary, _source: Control) -> Control:
	var c := RunManager.campaign
	var lookup := RunManager.lookup()
	match String(payload.get("kind", "")):
		"asset", "placed":
			var aid := StringName(String(payload["asset"]))
			var data := lookup.get_content(aid) as DefenseAssetData
			var card := AssetCard.new(aid, TextDb.t(data, "display_name") if data != null else String(aid), data.integrity if data != null else 0, 1)
			card.set_effect(data)
			card.size = card.custom_minimum_size
			return card
		"crew":
			var op := c.get_operative(payload["op"]) if c != null else null
			var chip := CrewChip.new(op.class_id if op != null else &"", payload["op"], op.name if op != null else "")
			chip.size = chip.custom_minimum_size
			return chip
		"recruit":
			var cls := lookup.get_content(payload["cls"]) as ClassData
			var rookie := CrewChip.new(payload["cls"], &"", TextDb.t(cls, "display_name") if cls != null else "")
			rookie.size = rookie.custom_minimum_size
			return rookie
		"boost":
			for b in RunManager.config().netrun_boosts:
				if b != null and b.id == payload["boost"]:
					return _note_ghost(TextDb.t(b, "display_name"))
		"segment":
			var seg := lookup.get_content(payload["segment"]) as RingSegmentData if payload["segment"] != &"" else null
			return _note_ghost(TextDb.t(seg, "display_name") if seg != null else tr("Class default"))
	return null


## A taped note with `text` (already translated): the ghost of a boost or a segment.
func _note_ghost(text: String) -> Control:
	var b := Button.new()
	b.theme_type_variation = &"NoteButton"
	b.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	b.text = text
	b.size = b.get_combined_minimum_size()
	return b


## A valid drop: the same call the item's button makes (the layer already flies the copy).
func _on_dropped(payload: Dictionary, target: Dictionary) -> void:
	var value: Variant = target.get("value")
	var flight: Dictionary = drops.last_flight
	match [String(payload.get("kind", "")), String(target.get("kind", ""))]:
		["asset", "node"]:
			# The button path: pick the node as the target, then press the card.
			selected_site = value
			deploy_asset(int(payload["index"]), value)
			_focus_named.call_deferred("Target_%s" % value)
		["placed", "node"]:
			var was := forecast_values()
			move_asset(payload["site"], int(payload["index"]), value)
			play_asset_drop(value, was)
			_focus_named.call_deferred("Target_%s" % value)
		["placed", "armory"]:
			move_asset(payload["site"], int(payload["index"]), &"")
		["crew", "station"]:
			station(payload["op"], value)
			drops.reveal_on_land(flight, _panel.find_child("Crew_%s" % payload["op"], true, false) as Control, false)
			_focus_in.call_deferred("Crew_%s" % payload["op"])
		["crew", "recall"]:
			recall(payload["op"])
			drops.reveal_on_land(flight, _panel.find_child("Crew_%s" % payload["op"], true, false) as Control, false)
			_focus_in.call_deferred("Crew_%s" % payload["op"])
		["crew", "jack"]:
			# ANIM-R1 (designer ruling 2026-09-27: "prefer select, then jack in"): the drop
			# picks the operative in the list; only pressing JACK IN starts the run.
			pick_operative(payload["op"])
		["recruit", "roster"]:
			_market_apply(payload, flight, func() -> void: recruit(payload["cls"]))
		["boost", "queue"]:
			_market_apply(payload, flight, func() -> void: buy_boost(payload["boost"]))
		["segment", "ring"]:
			swap_segment(payload["op"], int(value), payload["segment"])
			var view := get_node_or_null("LoadoutView") as LoadoutView
			if view != null:
				view.show_spinner()
				view.focus_ring(int(value))


## A drop the target refuses: nothing changes; the rules' reason shows, as a button's
## refusal does.
func _on_refused(_payload: Dictionary, _target: Dictionary, reason: String) -> void:
	_log.append_text("[color=orange]%s[/color]\n" % reason)
	notify(reason, true)


## A Black Market purchase by click: it buys as before, then the item flies from the
## button to where it went (the new operative in the crew, the boost in the next run's
## kit), which shows as the copy lands.
func _market_buy(button: Control, payload: Dictionary, apply: Callable) -> void:
	var from := button.get_global_rect() if button != null and button.is_inside_tree() else Rect2()
	var before := _market_count(payload)
	apply.call()
	if _market_count(payload) > before and from.has_area():
		var f := drops.buy_flight(payload, from, _market_rect.bind(payload))
		drops.reveal_on_land(f, _market_node(payload))


## A purchase dropped on its target: bought as by the button; the new item shows as the
## landing copy stamps down.
func _market_apply(payload: Dictionary, flight: Dictionary, apply: Callable) -> void:
	var before := _market_count(payload)
	apply.call()
	if _market_count(payload) > before:
		drops.reveal_on_land(flight, _market_node(payload))


func _market_count(payload: Dictionary) -> int:
	var c := RunManager.campaign
	if c == null:
		return 0
	return c.roster.size() if String(payload.get("kind", "")) == "recruit" else c.pending_boosts.size()


## Where a purchase shows on the page now: the newest dossier, or the next run's kit.
func _market_node(payload: Dictionary) -> Control:
	if _panel == null:
		return null
	if String(payload.get("kind", "")) == "recruit":
		var c := RunManager.campaign
		return _panel.find_child("Crew_%s" % c.roster[c.roster.size() - 1].id, true, false) as Control if c != null and not c.roster.is_empty() else null
	return _panel.find_child("QueuedBoosts", true, false) as Control


func _market_rect(payload: Dictionary) -> Rect2:
	var n := _market_node(payload)
	return n.get_global_rect() if n != null and n.is_inside_tree() else Rect2()


## Focus on the first usable control inside `node_name` (an operative's dossier).
func _focus_in(node_name: String) -> void:
	var n := _panel.find_child(node_name, true, false) if _panel != null else null
	var first := UiFocus.first_focusable(n) if n != null else null
	if first != null:
		first.grab_focus()


func _focus_named(node_name: String) -> void:
	var n := _panel.find_child(node_name, true, false) as Control if _panel != null else null
	if n != null and n.is_visible_in_tree():
		n.grab_focus()



# --- Panels ---------------------------------------------------------------------------------

func _set_panel(p: Control, name: String) -> void:
	# ANIM-4: the old page's drop targets go with it (a flight in the air keeps going).
	if drops != null:
		drops.reset()
	if _panel != null:
		_panel.queue_free()
	if side_hint != null and is_instance_valid(side_hint):
		side_hint.queue_free()
	side_hint = null
	_clear_city_map()
	# City map screens: clicks fall through the empty panel area to the map.
	var on_city := name in ["grid", "raid", "raid_playout", "raid_summary"] or name.begins_with("city")
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE if on_city else Control.MOUSE_FILTER_STOP
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel = p
	# ANIM-6: a new page enters (glass slides in, back to the HQ from the left); the same page
	# rebuilt after an action just shows.
	entering = name != panel_name
	var back := name == "hq" and panel_name != ""
	panel_name = name
	# ANIM-5: only the Grid and the playout ease their camera; any other page shows its
	# frame at once.
	if wireframe != null and not name in ["grid", "raid", "raid_playout"]:
		wireframe.settle_camera()
	# H24 S4: the page shows its words as given (translated once, where they are built).
	TextDb.shown_as_given(p)
	_panel_host.add_child(p)
	# Screens built from terminal windows let the city show between them.
	_panel_host.theme_type_variation = &"" if name in ["hq", "start", "grid", "raid", "raid_playout", "raid_summary"] or name.begins_with("city") else &"GlassPanel"
	hud.set_screen(String(SCREEN_NUMBERS.get(name, "")), screen_title(name))
	# H24 S15: lines tied to the screen being left end here.
	Dialogue.enter_screen(name)
	set_page_prompts(prompts_for(name))
	UiWrap.fit(p)
	UiFocus.link_layout(p)
	# ANIM-R3 B5: the raid playout goes on from the raid setup's map: it shows whole at once
	# (a page entrance showed a dim, half-drawn map for its first frames).
	if entering and name != "raid_playout":
		if _panel_host.theme_type_variation == &"" and name != "start":
			PageTransition.glass_is_windows(p)  # ANIM-R1 M11: the roll band crosses the windows only
		PageTransition.enter(p, PageTransition.look_of(p), UiFocus.focus_first.bind(p), -1 if back else 1)
	else:
		UiFocus.focus_first(p)
	_scroll_to_top.call_deferred()
	# Worlds (STYLE_GUIDE 1): the room is a cyberdeck, the Grid and raids are wireframe.
	var net := name in ["grid", "raid", "raid_playout", "raid_summary"] or name.begins_with("city")
	background.visible = not net
	wireframe.visible = net
	# Art pass W8b: W7's hookups (§9.1 grades, §9.5 maps over the city dim 40% and blur) and
	# the HQ's deck frame (§2 DECK, the HQ page only).
	background.set_context(&"hq")
	wireframe.set_context(&"net")
	wireframe.set_map_mode(net)
	deck_frame.visible = name == "hq"
	# §5.2: two subtitle lines at big text on every page (with one, a speaker's name on its own
	# row left the line no room and Dialogue shrank it under caption).
	subtitle_strip.set_big_lines(SubtitleStrip.BIG_LINES)
	deck_frame.keys_row.visible = name == "hq"
	if name != "hq":
		var none: Array[Control] = []
		background.set_calm_controls(none)
	AudioDirector.play_music("raid" if name.begins_with("raid") else ("grid" if name == "grid" else "hq"),
		RunManager.campaign.corporation_id if RunManager.campaign != null else &"")
	if RunManager.campaign != null:
		var band := RunManager.campaign.heat_majors_crossed(RunManager.config())
		background.heat_band = band
		wireframe.corp_creep = band / 3.0
		wireframe.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
		background.set_district(RunManager.campaign.corporation_id)
		wireframe.set_district(RunManager.campaign.corporation_id)
	_refresh_status()


## Panel `p_name`'s title on the HUD strip, translated (H24 S3: the drawn titles never
## were).
static func screen_title(p_name: String) -> String:
	match p_name:
		"start":
			return TranslationServer.translate("JACK A CAMPAIGN IN")
		"hq":
			return TranslationServer.translate("CYBERDECK HQ")
		"grid":
			return TranslationServer.translate("CITY GRID")
		"raid":
			return TranslationServer.translate("CELL DEFENSE RAID SETUP")
		"raid_playout":
			return TranslationServer.translate("RAID IN PROGRESS")
		"raid_summary":
			return TranslationServer.translate("RAID REPORT")
		"codex":
			return TranslationServer.translate("CODEX")
		"end":
			return TranslationServer.translate("CAMPAIGN END")
	return ""


## A new panel opens at its top (the first focus lands before layout and can
## otherwise leave the scroll part-way down, hiding the header row).
func _scroll_to_top() -> void:
	var scroll := _panel_host.get_parent() as ScrollContainer
	if scroll != null:
		scroll.scroll_vertical = 0
		# Again next frame, without awaiting: a page freed meanwhile just drops the call
		# (an await resumed on a freed HQ and logged "class instance is gone").
		# A bound method, not a lambda (DECISIONS "Animation pass - bake crash"): a freed HQ drops
		# the call, a freed scroll is only skipped (the lambda logged "capture was freed").
		_scroll_later = scroll
		if not get_tree().process_frame.is_connected(_reset_scroll):
			get_tree().process_frame.connect(_reset_scroll, CONNECT_ONE_SHOT)


## The scroll `_scroll_to_top` resets again next frame (null when none).
var _scroll_later: ScrollContainer = null


func _reset_scroll() -> void:
	if is_instance_valid(_scroll_later):
		_scroll_later.scroll_vertical = 0
	_scroll_later = null


## VIEW LOADOUT: an operative's deck and spinner. A dossier's Loadout button opens its
## operative (and selects them); the top bar opens the selected one, and NEXT OPERATIVE
## in the view cycles through the living crew (H20).
func open_loadout(op: OperativeState = null, spinner: bool = false) -> void:
	var c := RunManager.campaign
	if c == null or has_node("LoadoutView"):
		return
	if op == null:
		op = selected_op()
		if op == null:
			return
	select_operative(op.id)
	var view := LoadoutView.new(op, RunManager.lookup(), RunManager.config().shop_slices, c.living_operatives())
	view.operative_changed.connect(select_operative)
	add_child(view)
	_wire_drops(view.drops)  # ANIM-4: ring segment swaps dropped in the view come here
	if spinner:
		view.show_spinner()  # W8b: a dossier's RING SWAPS opens on the wheel


## The Daemon tray of the selected operative (top bar DAEMONS icon).
func open_daemons() -> void:
	var op := selected_op()
	if op == null or has_node("DaemonTray"):
		return
	add_child(DaemonTray.new(op.daemon_ids, RunManager.lookup(), hud.daemon_button.get_global_rect().end.x, op.name))


## Makes `operative_id` the operative the top bar's VIEW LOADOUT and DAEMONS show.
func select_operative(operative_id: StringName) -> void:
	selected_operative = operative_id
	_refresh_status()


func open_settings() -> void:
	if _settings_panel != null:
		_settings_panel.queue_free()
		_settings_panel = null
		return
	_settings_panel = PauseMenu.new()
	_settings_panel.position = Vector2((size.x - PauseMenu.MENU_SIZE.x) / 2.0, SubtitleStrip.top_below(PAUSE_TOP))  # under the subtitle band (H22: the top bar grows with its words)
	_settings_panel.resumed.connect(open_settings)
	_settings_panel.quit_to_title.connect(func() -> void: open_settings(); PageTransition.after_modals(self, RunManager.go_to_title))
	add_child(_settings_panel)
	get_tree().paused = false


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_settings"):
		open_settings()
		get_viewport().set_input_as_handled()
		return
	# H24 K1: the pad's key button (Y) opens and folds the Grid's map key at big text.
	if event.is_action_pressed("cycle_target") and panel_name == "grid" and grid_legend != null \
			and is_instance_valid(grid_legend) and grid_legend.visible and grid_legend.foldable():
		grid_legend.set_opened(not grid_legend.opened)
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("cycle_target") and panel_name == "raid" and raid_legend != null \
			and is_instance_valid(raid_legend) and raid_legend.visible and raid_legend.foldable():
		# ANIM-R2 R13: the raid's folding key opens and folds as the Grid's does.
		raid_legend.set_opened(not raid_legend.opened)
		get_viewport().set_input_as_handled()
		return
	# B goes back to the HQ from the Grid and the raid setup (H23 S11). H24 S6: only a pad's
	# B: a keyboard's Esc is ui_cancel too and must not leave when open_settings is bound
	# elsewhere.
	if event is InputEventJoypadButton and event.is_action_pressed("ui_cancel") and not event.is_action("open_settings") and panel_name in BACK_PANELS \
			and _settings_panel == null and not has_node("LoadoutView") and not has_node("DaemonTray"):
		PageTransition.after_modals(self, show_hq)
		get_viewport().set_input_as_handled()


## Panels B leaves for the HQ (their "Back to HQ" button).
const BACK_PANELS: Array[String] = ["grid", "raid"]


## The pad prompts of panel `p_name` (H23 S11): A presses the focused control, B goes back
## where the panel has a Back to HQ, Menu opens the settings.
static func prompts_for(p_name: String) -> Array:
	var out: Array = [[&"ui_accept", "Select"]] # TR
	# ANIM-4: the pick-up key carries the focused item to a target (D-pad, A drops).
	if p_name in DRAG_PANELS:
		out.append([&"end_turn", "Pick up"]) # TR
	if p_name in BACK_PANELS:
		out.append([&"ui_cancel", "Back"]) # TR
	out.append([&"open_settings", "Settings"]) # TR
	return out


func show_start() -> void:
	var lookup := RunManager.lookup()
	var profile := RunManager.profile
	var ts := Settings.text_scale
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	var head := HBoxContainer.new()
	head.add_theme_constant_override("separation", 24)
	# W8a baked art (§4.3.5): the logo and the TRUST NO ONE scrawl, never live text.
	head.add_child(LogoArt.new())
	head.add_child(ScrawlArt.new(SvgArt.SCRAWL_TRUST_NO_ONE, "TRUST\nNO ONE"))
	box.add_child(head)
	# Art pass W8b (ART_BIBLE §11 New campaign, §6.5; critique 03, 04): a planning table:
	# the target as corporation dossiers (the locked ones greyed with their lock and unlock),
	# ICE as a stepper, the home server as tiles, the crew as Polaroids, the seed and share
	# codes in a folded drawer, and one primary: START.
	var setup := TerminalWindow.new(tr("NEW CAMPAIGN // [HQ] the deck is warm. Jack a campaign in."))
	setup.name = "PlanningTable"
	box.add_child(setup)
	var cols := func(tile_w: float, n: int) -> int:
		return clampi(floori((PLAN_WIDTH + TilePicker.TILE_GAP) / (tile_w * minf(ts, PlanningPicker.WIDTH_GROW_MAX) + TilePicker.TILE_GAP)), 1, maxi(1, n))
	# TARGET: every corporation the profile can see (REBEL_CELL stays a secret while locked).
	var corps: Array[CorporationData] = []
	var corp_tiles: Array[Dictionary] = []
	var locked_corps: Array[Dictionary] = []
	var available := RunManager.available_corporations()
	for corp in available:
		corps.append(corp)
		corp_tiles.append({"name": TextDb.t(corp, "display_name"), "meta": tr("Best ICE: %s") % HudStats.ice_value(profile.best_ice_for(corp.id)), "corp": corp.id})
	for id in lookup.ids_of_class(&"CorporationData"):
		var corp := lookup.get_content(id) as CorporationData
		if corp == null or available.has(corp) or corp.generated_from_profile:
			continue
		locked_corps.append({"name": TextDb.t(corp, "display_name"), "corp": corp.id, "locked": true, "unlock": _unlock_words(corp)})
	corp_tiles.append_array(locked_corps)
	setup.body.add_child(_plan_header(tr("Target:"), StatIcon.MAP))
	var corp_pick := PlanningPicker.new(corp_tiles, 0, PLAN_CORP_TILE)
	corp_pick.columns = cols.call(PLAN_CORP_TILE.x, corp_tiles.size())
	corp_pick.name = "CorporationPicker"
	setup.body.add_child(corp_pick)
	# ICE (a stepper; each corporation has its own ICE ladder, GDD 3.4) beside the home server.
	var mid := HFlowContainer.new()
	mid.add_theme_constant_override("h_separation", roundi(UiTheme.SP_L * ts))
	mid.add_theme_constant_override("v_separation", roundi(UiTheme.SP_S * ts))
	setup.body.add_child(mid)
	var ice_col := VBoxContainer.new()
	mid.add_child(ice_col)
	var cap := RunManager.ice_cap(corps[0].id if not corps.is_empty() else RunManager.DEFAULT_CORPORATION)
	var ice_head := _plan_header(tr("ICE (0-%d):") % cap, StatIcon.ICE)
	ice_col.add_child(ice_head)
	var ice_spin := Stepper.new(0, cap, 1, 0)
	ice_spin.name = "IceSpin"
	ice_spin.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	ice_col.add_child(ice_spin)
	var ice_text := _para(_ice_description(0))
	ice_text.name = "IceText"
	ice_text.custom_minimum_size.x = PLAN_ICE_TEXT * ts
	ice_col.add_child(ice_text)
	ice_spin.value_changed.connect(func(v: float) -> void: ice_text.text = _ice_description(int(v)))
	corp_pick.tile_chosen.connect(func(i: int) -> void:
		var corp_cap := RunManager.ice_cap(corps[i].id)
		ice_spin.max_value = corp_cap
		(ice_head.get_child(1) as Label).text = tr("ICE (0-%d):") % corp_cap)
	var home_col := VBoxContainer.new()
	mid.add_child(home_col)
	home_col.add_child(_plan_header(tr("Home server:"), StatIcon.HOME))
	var variants := RunManager.available_home_variants()
	var home_tiles: Array[Dictionary] = []
	for v in variants:
		home_tiles.append({"name": TextDb.t(v, "display_name"), "icon": StatIcon.HOME})
	for id in lookup.ids_of_class(&"HomeServerVariantData"):
		var v := lookup.get_content(id) as HomeServerVariantData
		if v != null and not variants.has(v):
			home_tiles.append({"name": TextDb.t(v, "display_name"), "icon": StatIcon.HOME, "locked": true, "unlock": _unlock_words(v)})
	var home_pick := PlanningPicker.new(home_tiles, 0, PLAN_SMALL_TILE)
	home_pick.columns = cols.call(PLAN_SMALL_TILE.x, home_tiles.size())
	home_pick.name = "HomePicker"
	home_col.add_child(home_pick)
	# CREW: the first operative's class, as Polaroids.
	setup.body.add_child(_plan_header(tr("Crew:"), StatIcon.OPERATIVE))
	var classes := RunManager.available_classes()
	var class_tiles: Array[Dictionary] = []
	for cls in classes:
		class_tiles.append({"name": TextDb.t(cls, "display_name"), "class": cls.id})
	for id in lookup.ids_of_class(&"ClassData"):
		var cls := lookup.get_content(id) as ClassData
		if cls != null and not classes.has(cls):
			class_tiles.append({"name": TextDb.t(cls, "display_name"), "class": cls.id, "locked": true, "unlock": _unlock_words(cls)})
	var class_pick := PlanningPicker.new(class_tiles, 0, PLAN_SMALL_TILE)
	class_pick.columns = cols.call(PLAN_SMALL_TILE.x, class_tiles.size())
	class_pick.name = "ClassPicker"
	setup.body.add_child(class_pick)
	# START, the one primary; the drawer of seed and codes beside it, folded.
	var go := BoxContainer.new()
	# Art pass W9F (§12): at the biggest text START and SHARE CODES stack (side by side, with
	# the tracked lettering, the head ran 1 px past the screen at 2.0).
	go.vertical = ts >= START_STACK_SCALE - 0.001
	go.add_theme_constant_override("separation", roundi(UiTheme.SP_M * ts) if not go.vertical else UiTheme.SP_XS)
	# START sits up top beside the graffiti: the one primary, always on the first screen.
	var gap := Control.new()
	gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(gap)
	go.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	head.add_child(go)
	var seed_spin := Stepper.new(0, SEED_MAX, 1, 1)
	seed_spin.name = "SeedSpin"
	seed_spin.value_sample = str(SEED_MAX)
	var start_btn := _button(tr("START"), func() -> void:
		new_campaign(int(seed_spin.value), int(ice_spin.value), variants[home_pick.selected()].id if not variants.is_empty() else RunManager.DEFAULT_HOME,
			classes[class_pick.selected()].id if not classes.is_empty() else RunManager.DEFAULT_CLASS,
			corps[corp_pick.selected()].id if not corps.is_empty() else RunManager.DEFAULT_CORPORATION))
	start_btn.name = "StartCampaign"
	start_btn.theme_type_variation = UiTheme.PRIMARY
	start_btn.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	start_btn.tooltip_text = UiTip.fold(tr("New campaign"))
	_icon(start_btn, StatIcon.PLAY)
	go.add_child(start_btn)
	var drawer_btn := _button(tr("SHARE CODES"), func() -> void: set_codes_open(not codes_open()))
	drawer_btn.name = "CodesToggle"
	drawer_btn.theme_type_variation = UiTheme.TERTIARY
	drawer_btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_icon(drawer_btn, StatIcon.MORE)
	go.add_child(drawer_btn)
	# The drawer (GLASS): the seed (a stepper and a field to type it) and the share code.
	var codes := TerminalWindow.new(tr("SHARE CODES"), Palette.CELL_ACID)
	codes.name = "CodesDrawer"
	codes.visible = false
	codes.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	setup.body.add_child(codes)
	var seed_row := HFlowContainer.new()
	seed_row.add_theme_constant_override("h_separation", roundi(UiTheme.SP_S * ts))
	codes.body.add_child(seed_row)
	seed_row.add_child(_label(tr("Campaign seed:")))
	seed_row.add_child(seed_spin)
	var seed_field := CodeField.new("1")
	seed_field.name = "SeedField"
	seed_field.text_changed.connect(func(t: String) -> void:
		if t.strip_edges().is_valid_int():
			seed_spin.value = clampi(t.strip_edges().to_int(), 0, SEED_MAX))
	seed_spin.value_changed.connect(func(v: float) -> void:
		if seed_field.value.strip_edges() != str(int(v)):
			seed_field.value = str(int(v)))
	seed_row.add_child(seed_field)
	var code_row := HFlowContainer.new()
	code_row.add_theme_constant_override("h_separation", roundi(UiTheme.SP_S * ts))
	codes.body.add_child(code_row)
	var code_field := CodeField.new("")
	code_field.name = "CodeField"
	var code_edit := code_field.field
	code_edit.name = "CodeEdit"
	code_edit.placeholder_text = tr("RC1-corporation-ice-seed-home-class")
	code_edit.custom_minimum_size.x = PLAN_CODE_WIDTH * ts
	# Esc leaves the field (a focused LineEdit would otherwise swallow it).
	code_edit.gui_input.connect(func(ev: InputEvent) -> void:
		if ev.is_action_pressed("ui_cancel") or ev.is_action_pressed("open_settings"):
			code_edit.release_focus()
			code_edit.accept_event()
			UiFocus.focus_first(_panel))
	code_row.add_child(code_field)
	var from_code := _icon(_button(tr("Start from code"), func() -> void: start_from_code(code_edit.text)), StatIcon.PLAY)
	from_code.theme_type_variation = UiTheme.SECONDARY
	code_row.add_child(from_code)
	# The day's run, the deck menu and the profile's records, each as big as its words.
	var lower := HFlowContainer.new()
	lower.add_theme_constant_override("h_separation", 14)
	lower.add_theme_constant_override("v_separation", 12)
	box.add_child(lower)
	var menu := TerminalWindow.new(tr("CYBERDECK"))
	menu.custom_minimum_size.x = HQ_LEFT_WIDTH
	menu.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	lower.add_child(menu)
	var daily := TerminalWindow.new(tr("TODAY'S RUN"), Palette.CELL_ACID)
	daily.name = "DailyRun"
	daily.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	lower.add_child(daily)
	var today := Time.get_date_dict_from_system()
	var daily_seed := CampaignCode.daily_seed(today["year"], today["month"], today["day"])
	daily.tag_label.text = "%04d-%02d-%02d" % [today["year"], today["month"], today["day"]]
	for line in daily_lines(daily_seed):
		daily.body.add_child(_label(line))
	var daily_btn := _icon(_button(tr("Daily run"), func() -> void: new_campaign(daily_seed)), StatIcon.PLAY)
	daily_btn.theme_type_variation = UiTheme.SECONDARY
	daily_btn.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	daily.body.add_child(daily_btn)
	var records := TerminalWindow.new(tr("PROFILE // RECORDS"), Palette.CELL_PINK)
	records.name = "ProfileRecords"
	records.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	lower.add_child(records)
	if RunManager.has_save():
		menu.body.add_child(_icon(_button(tr("Resume saved campaign"), resume), StatIcon.CONTINUE))
	for text in [tr("Profile: %d campaigns started, %d won, %d lost; %d runs completed, %d operatives lost, raids %d/%d; best ICE %s.") % [
			profile.campaigns_started, profile.campaigns_won, profile.campaigns_lost, profile.runs_completed, profile.operatives_lost, profile.raids_won, profile.raids_lost, HudStats.ice_value(profile.best_ice)],
			ice_records_text()]:
		var p := _para(text)
		p.custom_minimum_size.x = PLAN_RECORDS_WIDTH * ts
		records.body.add_child(p)
	var unlock_names := PackedStringArray()
	for uid in profile.unlocks:
		var ud := lookup.get_content(uid) as ProfileUnlockData
		unlock_names.append(TextDb.t(ud, "display_name") if ud != null else String(uid))
	var unlocked := _para(tr("Unlocks: %s") % (", ".join(unlock_names) if not unlock_names.is_empty() else tr("none yet (buy them at HQ with campaign Schematics)")))
	unlocked.custom_minimum_size.x = PLAN_RECORDS_WIDTH * ts
	records.body.add_child(unlocked)
	var options_btn := _hint_button(tr("Options"), &"open_settings", open_settings)
	options_btn.name = "OptionsButton"
	menu.body.add_child(_icon(options_btn, StatIcon.SETTINGS))
	menu.body.add_child(_icon(_button(tr("Codex"), show_codex), StatIcon.CODEX))
	menu.body.add_child(_icon(_button(tr("Back to title"), RunManager.go_to_title), StatIcon.EXIT))
	_as_menu(menu.body)
	_set_panel(box, "start")


## W8b: the words of what unlocks `res` (a class, home server or corporation): the Black
## Market group and its price ("UNLOCKS · 80"), or "Needs ..." for a free, earned one.
func _unlock_words(res: Resource) -> String:
	var u := CampaignRules.unlock_for(RunManager.lookup(), res)
	if u == null:
		return tr(MARKET_UNLOCKS)
	if u.schematic_cost > 0:
		return "%s · %d" % [tr(MARKET_UNLOCKS), u.schematic_cost]
	return tr(MARKET_CLASS_LOCKED) % TextDb.t(u, "display_name")


## A planning-table header: the group's icon and words.
func _plan_header(words: String, icon: StringName) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", roundi(UiTheme.SP_S * Settings.text_scale))
	row.add_child(IconMark.standalone(icon, UiTheme.font_px(UiTheme.LABEL), Palette.CELL_ACID))
	var l := _label(words)
	l.add_theme_color_override("font_color", Palette.CELL_ACID)
	row.add_child(l)
	return row


## True when the new campaign's seed and codes drawer is open.
func codes_open() -> bool:
	var d := _panel.find_child("CodesDrawer", true, false) as Control if _panel != null else null
	return d != null and d.visible


## Opens (or folds) the new campaign's seed and codes drawer.
func set_codes_open(open: bool) -> void:
	var d := _panel.find_child("CodesDrawer", true, false) as Control if _panel != null else null
	if d == null:
		return
	d.visible = open
	var toggle := _panel.find_child("CodesToggle", true, false) as Button
	if toggle != null:
		IconMark.attach(toggle, StatIcon.CLOSE if open else StatIcon.MORE)
	if open:
		var field := d.find_child("SeedField", true, false) as CodeField
		if field != null:
			field.field.grab_focus.call_deferred()


## Today's daily run as display lines: the fixed setup, then the day's modifiers (the
## list is empty until daily modifiers are designed; DECISIONS.md open question).
func daily_lines(seed: int) -> PackedStringArray:
	var lines := PackedStringArray()
	lines.append(tr("> SEED     %d") % seed)
	lines.append(tr("> TARGET   %s") % TextDb.t(RunManager.lookup().get_content(RunManager.DEFAULT_CORPORATION), "display_name"))
	lines.append(tr("> ICE      0"))
	lines.append(tr("> HOME     %s") % TextDb.t(RunManager.lookup().get_content(RunManager.DEFAULT_HOME), "display_name"))
	lines.append(tr("> CREW     %s") % TextDb.t(RunManager.lookup().get_content(RunManager.DEFAULT_CLASS), "display_name"))
	var mods := daily_modifiers(seed)
	lines.append(tr("> MODIFIERS"))
	if mods.is_empty():
		lines.append(tr("    none today"))
	for m in mods:
		lines.append("    + %s" % m)
	return lines


## The day's modifier descriptions (none yet: the daily run fixes only the seed).
func daily_modifiers(_seed: int) -> PackedStringArray:
	return PackedStringArray()


## The cumulative ICE ladder up to `level`, one line.
func _ice_description(level: int) -> String:
	if level <= 0:
		return tr("ICE 0: the baseline rules.")
	var parts := PackedStringArray()
	for l in RunManager.config().ice_ladder:
		if l != null and l.level <= level and l.description != "":
			parts.append("%d %s" % [l.level, TextDb.t(l, "description")])
	return tr("ICE %d: %s") % [level, " | ".join(parts)]


func show_hq() -> void:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var ts := Settings.text_scale
	# Art pass W8b (ART_BIBLE §11 HQ): at big text the page stacks in two rows (the three
	# columns ran past the screen at 2.0).
	var narrow := ts >= HudStats.FOLD_SCALE - 0.001
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	var cols := HBoxContainer.new()
	cols.add_theme_constant_override("separation", 14)
	box.add_child(cols)
	var poster := HeatPoster.new(true)
	poster.hot_color = Palette.corp_color(c.corporation_id)
	poster.set_heat(c.heat, cfg.heat_max, cfg.major_heat_levels())
	poster.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	poster.tooltip_text = heat_tip()
	var lead := selected_op()
	if lead != null:
		poster.wanted = PortraitArt.operative_subject(lead.class_id, lead.id, lead.name)
	# The note shows whole lines at any text size (H21 #15: at 1.6 its last line was cut in
	# half); the rest scrolls. W1: the line height rounded up (MSDF heights are fractional).
	var line_h := ceilf(Palette.mono().get_height(UiTheme.font_px(UiTheme.BODY)))
	var radio := ZineNote.new(tr("PIRATE RADIO"), Vector2(RADIO_WIDTH, RADIO_TOP + RADIO_BOTTOM + line_h * RADIO_LINES))
	radio.name = "PirateRadio"
	var dj_line := Dialogue.line("dj", RC.Voice.NARRATOR, c.corporation_id, &"", c.runs_started + c.runs_completed * 7)
	# H24 S3: the DJ's words in the player's language (the voice line's TextDb key).
	var dj_text := Dialogue.voice_text(dj_line) if dj_line != null else tr("lo-fi loop: HQ")
	radio.append(dj_text)
	radio.append(tr("vs %s | ICE %d%s") % [TextDb.t(RunManager.corporation, "display_name"), c.ice_level, tr(" | ASSIST") if c.is_assisted() else ""])
	# H24 S11: the share code read like debug output on the lore note: it is in the note's
	# tooltip and on the Settings menu's seed line (PauseMenu.code_line).
	radio.tooltip_text = UiTip.fold("%s\n%s" % [dj_text, campaign_code_line()])
	radio.label.scroll_following = false
	# H23 S6: the note grows to its words (at 1.0 and 1.6 its text was cut, a scroll bar in
	# the corner); RADIO_LINES is its least height.
	radio.label.fit_content = true
	radio.label.scroll_active = false
	radio.label.minimum_size_changed.connect(_fit_radio.bind(radio, line_h))
	_fit_radio.call_deferred(radio, line_h)
	# No key hint: JACK IN is pressed by click or focus (Space does nothing here). It is the
	# same JACK IN as on a Site's card (H21 #21): here it opens the Grid to pick the Site.
	# W8b (§11 HQ focal order): the first thing the eye meets, the page's largest stamp.
	var jack := ZineStamp.new(tr(JACK_IN), Palette.CELL_PINK)
	jack.name = "JackIn"
	jack.custom_minimum_size = Vector2.ONE * JACK_SIDE * minf(ts, JACK_GROW_MAX)
	jack.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	jack.tooltip_text = UiTip.fold(tr("JACK IN: pick a Site on the City Grid, then JACK IN on its card to start the netrun."))
	jack.icon_kind = StatIcon.JACK_IN  # H22 #14: the plug, as on the Site card's JACK IN
	if RunManager.has_active_run():
		# ANIM-R1 M1: a run saved and left (Save & quit) waits: JACK IN goes back into it (a
		# second run can't start over it).
		jack.tooltip_text = UiTip.fold(tr("JACK IN: back into the run you left."))
		jack.pressed.connect(func() -> void:
			if not RunManager.scene_change_pending():
				RunManager.go_to_netrun())
	else:
		jack.pressed.connect(show_grid)
	# ANIM-R4 H10: what the pages this one leads to need is made ahead (their first frames
	# made it): the Grid's and a raid's music, a run's, and the open runs' previews.
	AudioDirector.prewarm_music(["grid", "raid", "netrun", "combat"], c.corporation_id)
	_warm_previews.call_deferred()
	var left := VBoxContainer.new()
	left.add_theme_constant_override("separation", 12)
	left.custom_minimum_size.x = HQ_LEFT_WIDTH
	# The deck menu (reference: "> OPERATIVES / NETWORK / LOADOUT").
	var deck := TerminalWindow.new(tr("CYBERDECK"))
	left.add_child(deck)
	var actions := deck.body
	# Each item carries its icon (H21 #13): the map, the raid shield, the flame (Heat), the
	# house (home), the book, the gear, the floppy.
	var grid_btn := _icon(_button(tr("City Grid"), show_grid), StatIcon.MAP)
	grid_btn.name = "CityGrid"
	_add_tip(actions, grid_btn, tr("The campaign map: pick a Site and JACK IN, claim and upgrade nodes."))
	if not c.pending_raids.is_empty():
		var raid := CampaignRules.raid_data(c.pending_raids[0], lookup)
		# W8b (critique 05): one line, never wrapped: the raid's name and count with the raids
		# icon in WARN (§3.3: a pending raid); "RAID PENDING" and its warning in the tooltip
		# ("RAID PENDING: Collections: Trespass (6)" wrapped to three lines in the menu).
		var raid_btn := _icon(_button("%s (%d)" % [TextDb.t(raid, "display_name"), c.pending_raids.size()], show_raid), StatIcon.RAIDS)
		raid_btn.name = "RaidPending"
		raid_btn.add_theme_color_override("font_color", Palette.WARN)
		_add_tip(actions, raid_btn, "%s\n%s" % [tr("RAID PENDING: %s (%d)") % [TextDb.t(raid, "display_name"), c.pending_raids.size()], TextDb.t(raid, "warning_text")])
	var scrub := HeatRules.scaled_delta(c, -cfg.heat_purchase_amount, cfg)
	# H23 S13: the price says what it is: "pay 25" and the Schematics icon after it.
	var scrub_price := CampaignRules.heat_purchase_price(c, cfg)
	var scrub_btn := _icon(_button(tr("Scrub Heat %d · pay %d") % [scrub, scrub_price], buy_heat_reduction), StatIcon.HEAT)
	scrub_btn.name = "ScrubHeat"
	_add_tip(actions, scrub_btn, tr("Costs %d Schematics (you have %d): Heat changes by %d.") % [scrub_price, c.schematics, scrub])
	if c.grid.home_integrity < c.grid.home_max_integrity:
		_add_tip(actions, _icon(_button(tr("Patch home %s (%d)") % [TextDb.signed(c.grid.home_max_integrity - c.grid.home_integrity), CampaignRules.home_repair_price(c, cfg)], repair_home), StatIcon.HOME),
			tr("Repair the home server to full integrity."))
	_add_tip(actions, _icon(_button(tr("Codex"), show_codex), StatIcon.CODEX), tr("Everything the Cell knows: slices, cards, Firmware, Daemons, rules."))
	var settings_btn := _hint_button(tr("Settings"), &"open_settings", open_settings)
	settings_btn.name = "SettingsButton"
	_add_tip(actions, _icon(settings_btn, StatIcon.SETTINGS), tr("Options: text size, sound, controls, subtitles."))
	var save_btn := _icon(_button(tr("Save"), func() -> void: RunManager.autosave(); _log.append_text("Saved.\n"); notify(tr("Saved."))), StatIcon.SAVE)
	save_btn.name = "SaveButton"
	_add_tip(actions, save_btn, tr("Save the campaign now (it also saves after every action)."))
	_as_menu(actions)
	_price_icon(scrub_btn, StatIcon.SCHEMATICS)
	# The Cell at a glance (H20: badges, not a text readout): home, Exploits, Armory and the
	# rules the Heat thresholds added; each badge's tooltip says what it means.
	var status := TerminalWindow.new(tr("CELL STATUS"))
	status.name = "CellStatus"
	left.add_child(status)
	status.body.add_child(cell_badges())
	# The deck monitor (W8b, §2 DECK, §11 HQ): the City Grid at a glance on a CRT with amber
	# readouts (click a Site, or JACK IN, to open it).
	var monitor := DeckMonitor.new(tr("CITY GRID // %s") % TextDb.t(RunManager.corporation, "display_name"))
	monitor.name = "GridMonitor"
	monitor.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	monitor.set_readouts(tr("STATUS: %s") % (tr("RAID INBOUND") if not c.pending_raids.is_empty() else tr("STABLE")),
		"%s · %s" % [tr("SITES %d") % maxi(0, c.grid.claimed_ids().size() - 1), tr("EXPLOITS %d/%d") % [c.exploits.size(), cfg.min_exploits_for_breach]])
	# ANIM-5 (4.1): the deck monitor is the CRT jack in pushes into and jack out leaves.
	monitor.add_to_group(Fx.JACK_FOCUS_GROUP)
	var mini := GridMapView.new()
	# Stacked at big text the monitor is a wide, low screen, so the crew under it stays on
	# the first screen (H22: a dossier's Loadout in view at 1.6).
	mini.custom_minimum_size = MONITOR_MAP * minf(ts, MONITOR_GROW_MAX) if not narrow else Vector2(MONITOR_MAP.x, MONITOR_MAP_LOW)
	mini.track_seen = true  # ANIM-5: a Site whose status changed since last seen pulses once
	mini.show_grid(c, RunManager.corporation, _threat_paths())
	mini.site_clicked.connect(func(id: StringName) -> void: selected_site = id; show_grid())
	mini.tooltip_text = UiTip.for_input(tr("Click a Site to open it on the City Grid."), tr("Press a Site to open it on the City Grid."))
	monitor.set_content(mini)
	# The crew (W8b, §5.3 / §11 HQ): the dossiers fill a grid of CREW_COLUMNS columns (fewer
	# at big text), the window as wide as its dossiers (critique 05: 40% of it was empty).
	var crew := TerminalWindow.new(tr("CREW // ROSTER"), Palette.CELL_PINK)
	crew.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	var roster_box := GridContainer.new()
	roster_box.columns = maxi(1, mini(CREW_COLUMNS if not narrow else CREW_COLUMNS_BIG, c.roster.size()))
	roster_box.add_theme_constant_override("h_separation", 18)
	roster_box.add_theme_constant_override("v_separation", 14)
	crew.body.add_child(roster_box)
	if not narrow:
		# Three columns: the menu | the monitor over the crew | JACK IN, the poster, the radio.
		var center := VBoxContainer.new()
		center.add_theme_constant_override("separation", 12)
		center.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var right := VBoxContainer.new()
		right.add_theme_constant_override("separation", 10)
		right.add_child(jack)
		right.add_child(poster)
		right.add_child(radio)
		cols.add_child(left)
		cols.add_child(center)
		cols.add_child(right)
		center.add_child(monitor)
		center.add_child(crew)
	else:
		# Two rows: JACK IN, the poster and the monitor | the menu (and radio) beside the crew.
		cols.add_child(jack)
		cols.add_child(poster)
		cols.add_child(monitor)
		var lower := HBoxContainer.new()
		lower.add_theme_constant_override("separation", 14)
		box.add_child(lower)
		left.add_child(radio)
		lower.add_child(left)
		lower.add_child(crew)
		jack.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		poster.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	for op in c.roster:
		# A crew dossier: Polaroid, name, tags, HP, kit, then orders.
		var where := CampaignRules.stationed_site(c, op.id)
		var cls_data := lookup.get_content(op.class_id) as ClassData
		var row := CrewCard.new(op.name, TextDb.t(cls_data, "display_name") if cls_data != null else String(op.class_id), op.rank, op.hp, op.max_hp,
			tr("HP %d/%d · DECK %d · DAEMONS %d%s") % [op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size(),
			"" if op.alive else tr(" · [DEAD]")], -1.5 if c.roster.find(op) % 2 == 0 else 1.5)
		row.name = "Crew_%s" % op.id
		row.set_operative(op.class_id, op.id)
		row.tooltip_text = UiTip.fold("%s%s%s" % [TextDb.t(cls_data, "description") if cls_data != null else "", (tr("\nStationed on %s.") % site_name(where)) if where != &"" else "",
			("\n" + UiTip.for_input(tr("Drag the dossier onto one of your nodes on the City Grid monitor to station them there, or onto CORE to bring them back."),
				tr("Pick the dossier up and move it onto one of your nodes on the City Grid monitor to station them there, or onto CORE to bring them back."))) if op.alive else ""])
		row.polaroid.glitch = not op.alive or op.hp * 4 <= op.max_hp
		row.dead = not op.alive
		if op.alive:
			# ANIM-4: the dossier drags onto a post on the mini-map (station) or CORE (recall);
			# a click picks it up, and so does the pick-up key on any of its orders.
			drops.add_source(row, {"kind": "crew", "op": op.id, "motion": &"crew_assign", "prefer": where}, true)
		if where != &"" and op.alive:
			row.stamp_text = tr("ON %s") % site_name(where).to_upper()
		var orders := row.orders
		if op.alive:
			var view_row := HBoxContainer.new()
			var op_ref := op
			var loadout_btn := _icon(_button(tr("Loadout"), func() -> void: open_loadout(op_ref)), StatIcon.CARDS)
			loadout_btn.name = "Loadout"
			loadout_btn.tooltip_text = UiTip.fold(tr("%s's deck, spinner, hub core and inner ring. VIEW LOADOUT and DAEMONS in the top bar follow them.") % op.name)
			view_row.add_child(loadout_btn)
			orders.add_child(view_row)
			if where != &"":
				var id := op.id
				_add_tip(orders, _icon(_button(tr("Recall"), func() -> void: recall(id)), StatIcon.BACK), tr("Bring %s back from %s.") % [op.name, site_name(where)])
			else:
				for site_id in c.grid.claimed_ids():
					var node := lookup.get_content(c.grid.node_type_of(site_id)) as NetworkNodeData
					if node != null and node.station_slots > 0 and c.grid.stationed_on(site_id) == &"" and c.grid.is_active_node(site_id):
						var oid := op.id
						var sid := site_id
						_add_tip(orders, _icon(_button(tr("Station on %s") % site_name(site_id), func() -> void: station(oid, sid)), StatIcon.RAIDS),
							tr("%s guards %s (%s): the class's station bonus helps it hold in raids.") % [op.name, site_name(site_id), TextDb.t(node, "display_name")])
			# Rank 3 Inner Ring segment swaps (GDD 6.4). Art pass W8b (§6.5, critique 13): the
			# three native lists are gone: RING SWAPS opens the loadout's SPINNER tab, where the
			# swaps sit beside the wheel (press one, pick the segment; or drag it) and a swap
			# fills and pulses its segment (§10.2).
			var cls := lookup.get_content(op.class_id) as ClassData
			var options := CampaignRules.ring_segment_options(op, cls)
			if not options.is_empty():
				var op_ring := op
				var ring_btn := _icon(_button(tr(RING_SWAPS), func() -> void: open_loadout(op_ring, true)), StatIcon.SLOTS)
				ring_btn.name = "RingSwaps"
				ring_btn.tooltip_text = UiTip.fold(tr(RING_SWAPS_TIP))
				orders.add_child(ring_btn)
		roster_box.add_child(row)
	roster_box.name = "Roster"
	# The market (W8b, §11 HQ, critique 06/09): recruits, next-run boosts (GDD 11.4) and
	# Profile unlocks (GDD 3.4), each group under its header, each item with its icon and a
	# price tag; what can't be bought now says why.
	var market := TerminalWindow.new(tr("BLACK MARKET // SCHEMATICS %d") % c.schematics, Palette.CELL_ACID)
	market.name = "BlackMarket"
	box.add_child(market)
	var queue := _market_sections(market.body)
	var beats := CampaignRules.revealed_beats(c, RunManager.corporation)
	if not beats.is_empty():
		var story := TerminalWindow.new(tr("Story so far:"), Palette.CRT_AMBER)
		box.add_child(story)
		for b in beats:
			var t := RichTextLabel.new()
			t.fit_content = true
			t.custom_minimum_size = Vector2(700, 0)
			t.text = "  [%s] %s" % [TextDb.t(b, "title"), TextDb.t(b, "text")]
			story.body.add_child(t)
	# W8b (§2 DECK, ruling Q4): the page sits inside the deck's frame, never under it.
	var framed := MarginContainer.new()
	framed.name = "DeckPage"
	framed.add_theme_constant_override("margin_left", DeckFrame.INSET_SIDE)
	framed.add_theme_constant_override("margin_right", DeckFrame.INSET_SIDE)
	framed.add_theme_constant_override("margin_bottom", DeckFrame.INSET_BOTTOM)
	framed.add_child(box)
	_set_panel(framed, "hq")
	# W7 hookup (§9.1): the city dims and calms behind the HQ's text panels.
	var calm: Array[Control] = [deck, status, crew, market, radio]
	background.set_calm_controls(calm)
	_link_crew_focus(roster_box, jack, market)
	_register_hq_drops(crew, mini, queue)
	# HQ idle (ANIM-6, 4.13): the deck monitor hums, JACK IN breathes, and on arrival the
	# pirate radio types in.
	CrtHum.attach(monitor.screen)
	jack.breathe()
	if entering:
		Typing.type_in(radio.label, &"radio_type")
	# ANIM-R2 R1: the Grid is a press away: its city bakes now, behind the HQ (while a jack out
	# still covers the screen too), so the Grid opens on its image.
	_prebake_grid.call_deferred()


# --- The Black Market (art pass W8b: ART_BIBLE §11 HQ, §3.7, §6.4; critique 06/09, scr/05) ---

## The market's group headers, in order (translated where shown).
const MARKET_RECRUIT := "RECRUIT" # TR
const MARKET_BOOSTS := "BOOSTS" # TR
const MARKET_UNLOCKS := "UNLOCKS" # TR
## Why a locked item can't be bought yet (its unlock condition).
const MARKET_CLASS_LOCKED := "Needs %s" # TR
const MARKET_NEEDS := MARKET_CLASS_LOCKED
## A market item's words and its price ("Scanner · 25", the Schematics icon after it).
const MARKET_ITEM := "%s · %d"
## The market's sections: gap between them and between items (px at text scale 1.0).
const MARKET_GAP := UiTheme.SP_S
const MARKET_ITEM_GAP := UiTheme.SP_M


## The Black Market's three groups under `body`: RECRUIT (every class, locked ones with
## their unlock), BOOSTS (and the next run's kit, their drop target) and UNLOCKS. Each item
## is its icon, its name and a price tag; one that can't be bought now is disabled (W2's
## locked look: DISABLED outline, a lock, the label still 4.5:1) with the reason under it
## ("NEED 25 · HAVE 10", the unlock it waits for). Returns the next run's kit label.
func _market_sections(body: VBoxContainer) -> Label:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var profile := RunManager.profile
	body.add_theme_constant_override("separation", roundi(MARKET_GAP * Settings.text_scale))
	# RECRUIT: every class; a locked one shows its lock and the unlock it waits for.
	var recruits := _market_section(body, "Recruits", MARKET_RECRUIT, StatIcon.OPERATIVE)
	var price := CampaignRules.rookie_price(c, cfg)
	for id in lookup.ids_of_class(&"ClassData"):
		var cls := lookup.get_content(id) as ClassData
		if cls == null:
			continue
		var cid := cls.id
		# ANIM-4: a click buys as before and the new operative flies to the crew; or drag the
		# item onto CREW // ROSTER.
		var pay := {"kind": "recruit", "cls": cid, "motion": &"crew_assign"}
		var ref: Array = [null]
		var rb := _market_item(recruits, "Recruit_%s" % cid, TextDb.t(cls, "display_name"), StatIcon.OPERATIVE, price,
			func() -> void: _market_buy(ref[0], pay, func() -> void: recruit(cid)))
		ref[0] = rb
		rb.tooltip_text = UiTip.fold(TextDb.t(cls, "description"))
		if not CampaignRules.class_available(profile, lookup, cls):
			var u := CampaignRules.unlock_for(lookup, cls)
			_market_locked(rb, tr(MARKET_CLASS_LOCKED) % (TextDb.t(u, "display_name") if u != null else TextDb.t(cls, "display_name")))
		elif c.schematics < price:
			_market_short(rb, price, c.schematics)
		else:
			drops.add_source(rb, pay)
	# BOOSTS: the next run's kit (always shown: the boosts' drop target).
	var boosts := _market_section(body, "Boosts", MARKET_BOOSTS, StatIcon.PLUS)
	for b in cfg.netrun_boosts:
		if b == null:
			continue
		var bid := b.id
		var pay := {"kind": "boost", "boost": bid}
		var ref: Array = [null]
		var btn := _market_item(boosts, "Boost_%s" % b.id, TextDb.t(b, "display_name"), boost_icon(b), b.cost,
			func() -> void: _market_buy(ref[0], pay, func() -> void: buy_boost(bid)))
		ref[0] = btn
		btn.tooltip_text = UiTip.fold(TextDb.t(b, "description"))
		if c.pending_boosts.has(b.id):
			_market_locked(btn, tr("queued: %s") % TextDb.t(b, "display_name"), false)
		elif c.schematics < b.cost:
			_market_short(btn, b.cost, c.schematics)
		drops.add_source(btn, pay)
	var queued := PackedStringArray()
	for bid in c.pending_boosts:
		for b in cfg.netrun_boosts:
			if b != null and b.id == bid:
				queued.append(TextDb.t(b, "display_name"))
	var queue := _label(tr("queued: %s") % (", ".join(queued) if not queued.is_empty() else "-"))
	queue.name = "QueuedBoosts"
	queue.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	queue.mouse_filter = Control.MOUSE_FILTER_PASS
	queue.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	queue.tooltip_text = UiTip.fold(UiTip.for_input(tr("The boosts bought for the next run. Drag a boost here to buy it."), tr("The boosts bought for the next run. Pick a boost up and move it here to buy it.")))
	boosts.add_child(queue)
	# UNLOCKS: Profile unlocks for sale; one waiting on another unlock shows its lock.
	var unlocks := _market_section(body, "Unlocks", MARKET_UNLOCKS, StatIcon.LOCK)
	var any_unlock := false
	for id in lookup.ids_of_class(&"ProfileUnlockData"):
		var u := lookup.get_content(id) as ProfileUnlockData
		if u == null or profile.has_unlock(u.id):
			continue
		# Free unlocks (REBEL_CELL) open by themselves once their requirements are met.
		if u.schematic_cost == 0:
			continue
		any_unlock = true
		var uid := u.id
		var btn := _market_item(unlocks, "Unlock_%s" % u.id, TextDb.t(u, "display_name"), unlock_icon(u), u.schematic_cost, func() -> void: purchase_unlock(uid))
		btn.tooltip_text = UiTip.fold(TextDb.t(u, "description"))
		var missing := PackedStringArray()
		for need in u.requires_unlock_ids:
			if not profile.has_unlock(need):
				var nu := lookup.get_content(need) as ProfileUnlockData
				missing.append(TextDb.t(nu, "display_name") if nu != null else String(need))
		if not missing.is_empty():
			_market_locked(btn, tr(MARKET_NEEDS) % ", ".join(missing))
		elif c.schematics < u.schematic_cost:
			_market_short(btn, u.schematic_cost, c.schematics)
	if not any_unlock:
		unlocks.add_child(_label(tr("everything unlocked")))
	return queue


## A market group under `body`: its header (icon and words at `title`) and the flow its
## items fill (named `flow_name`; returned).
func _market_section(body: VBoxContainer, flow_name: String, words: String, icon: StringName) -> HFlowContainer:
	var s := Settings.text_scale
	var head := HBoxContainer.new()
	head.name = "%sHeader" % flow_name
	head.add_theme_constant_override("separation", roundi(UiTheme.SP_S * s))
	head.add_child(IconMark.standalone(icon, UiTheme.font_px(UiTheme.TITLE), Palette.CELL_ACID))
	var l := _label(tr(words))
	l.theme_type_variation = &"HeaderLabel"
	l.add_theme_color_override("font_color", Palette.CELL_ACID)
	head.add_child(l)
	body.add_child(head)
	var flow := HFlowContainer.new()
	flow.name = flow_name
	flow.add_theme_constant_override("h_separation", roundi(MARKET_ITEM_GAP * s))
	flow.add_theme_constant_override("v_separation", roundi(MARKET_GAP * s))
	body.add_child(flow)
	return flow


## A market item in `flow`: a cell with the item's button (its icon, `words` and a price
## tag of `price` Schematics; named `button_name`) and the line saying why it can't be
## bought (hidden until `_market_short` / `_market_locked`). Returns the button.
func _market_item(flow: HFlowContainer, button_name: String, words: String, icon: StringName, price: int, on_pressed: Callable) -> Button:
	var cell := VBoxContainer.new()
	cell.name = "Cell_%s" % button_name
	cell.add_theme_constant_override("separation", 0)
	var b := _icon(_button(MARKET_ITEM % [words, price], on_pressed), icon)
	b.name = button_name
	b.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	cell.add_child(b)
	var why := _label("")
	why.name = "Why"
	why.visible = false
	why.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	why.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	why.add_theme_color_override("font_color", Palette.TEXT_MID)
	cell.add_child(why)
	flow.add_child(cell)
	_price_icon(b, StatIcon.SCHEMATICS)
	return b


## §3.7: an item the Cell can't afford: W2's disabled look and "NEED n · HAVE m" under it
## (the words never faded; TEXT_MID is 4.5:1 on glass).
func _market_short(b: Button, price: int, have: int) -> void:
	b.disabled = true
	_market_why(b, tr("NEED %d · HAVE %d") % [price, have])


## §3.7 / §6.5: a locked item (or one already queued, `lock` false: disabled without the
## lock reason): disabled with the words `why` under it.
func _market_locked(b: Button, why: String, lock: bool = true) -> void:
	b.disabled = true
	if lock:
		b.set_meta(&"market_locked", true)
	_market_why(b, why)


func _market_why(b: Button, text: String) -> void:
	var why := b.get_parent().get_node_or_null(^"Why") as Label
	if why != null:
		why.text = text
		why.visible = true
	b.tooltip_text = UiTip.fold("%s\n%s" % [b.tooltip_text.strip_edges(), text]) if b.tooltip_text != "" else UiTip.fold(text)


## A boost's icon: what it gives (Cycles, cards, RAM as a chip).
static func boost_icon(b: NetrunBoostData) -> StringName:
	if b.cycles > 0:
		return StatIcon.CYCLES
	if not b.temp_cards.is_empty():
		return StatIcon.CARDS
	return StatIcon.FIRMWARE


## A Profile unlock's icon: what kind of thing it opens.
static func unlock_icon(u: ProfileUnlockData) -> StringName:
	match u.kind:
		RC.UnlockKind.CLASS, RC.UnlockKind.CLASS_ALTERNATIVE:
			return StatIcon.OPERATIVE
		RC.UnlockKind.CORPORATION:
			return StatIcon.MAP
		RC.UnlockKind.HOME_SERVER:
			return StatIcon.HOME
		RC.UnlockKind.NODE_TYPE:
			return StatIcon.LINKS
	return StatIcon.BADGES


## ANIM-R2 R1 (view memory): the bake region the Grid was last framed at, per campaign.
static var _grid_views: Dictionary = {}


func _grid_memory_key() -> String:
	var c := RunManager.campaign
	return "%d|%s" % [c.campaign_seed, c.corporation_id] if c != null else ""


## ANIM-R2 R1: bakes, ahead, the net city's current look over the region the Grid was last
## framed at in this campaign (nothing the first time: the Grid then bakes its own view).
func _prebake_grid() -> void:
	if wireframe == null or not is_inside_tree() or RunManager.campaign == null:
		return
	var region: Variant = _grid_views.get(_grid_memory_key())
	if region is Rect2:
		wireframe.city.prebake(region)
	# The Grid's placement (its buildings and street routes) worked out now too: the Grid's
	# first frame then only draws (~35 ms less in it).
	if wireframe.city.is_baked():
		var warm := CityMapOverlay.new(wireframe.city)
		var g := grid_graph()
		warm.set_graph(g["nodes"], g["edges"])
		warm.free()


## PIRATE RADIO as tall as its words (at least RADIO_LINES lines of `line_h`).
func _fit_radio(note: Variant, line_h: float) -> void:
	if not is_instance_valid(note) or not (note is ZineNote):
		return
	var radio := note as ZineNote
	var h := RADIO_TOP + RADIO_BOTTOM + maxf(line_h * RADIO_LINES, radio.label.get_combined_minimum_size().y)
	if not is_equal_approx(radio.custom_minimum_size.y, h):
		radio.custom_minimum_size.y = h


## D-pad through the crew (H22 #10: the second dossier's Loadout could not be reached; the
## page's row links saw only each column's first control): each dossier's orders top to
## bottom, left / right to the same line of the dossier beside it (JACK IN after the last),
## and down from a dossier's last order to the next dossier, then to the Black Market.
func _link_crew_focus(roster: Control, jack: Control, market: Control) -> void:
	var cards: Array = []
	for card in roster.get_children():
		var list: Array[Control] = []
		_usable_in(card, list)
		if not list.is_empty():
			cards.append(list)
	var after := UiFocus.first_focusable(market)
	for k in cards.size():
		var list: Array = cards[k]
		for i in list.size():
			var c: Control = list[i]
			if i > 0:
				c.focus_neighbor_top = c.get_path_to(list[i - 1])
			if i + 1 < list.size():
				c.focus_neighbor_bottom = c.get_path_to(list[i + 1])
			elif k + 1 < cards.size():
				c.focus_neighbor_bottom = c.get_path_to(cards[k + 1][0])
			elif after != null:
				c.focus_neighbor_bottom = c.get_path_to(after)
			if k + 1 < cards.size():
				var nxt: Array = cards[k + 1]
				c.focus_neighbor_right = c.get_path_to(nxt[mini(i, nxt.size() - 1)])
			elif jack != null:
				c.focus_neighbor_right = c.get_path_to(jack)
			if k > 0:
				var prv: Array = cards[k - 1]
				c.focus_neighbor_left = c.get_path_to(prv[mini(i, prv.size() - 1)])
		if k == 0 and jack != null:
			jack.focus_neighbor_left = jack.get_path_to(list[0])


## The focusable controls under `node`, in tree order.
func _usable_in(node: Node, out: Array[Control]) -> void:
	for child in node.get_children():
		if child is Control and (child as Control).is_visible_in_tree() and (child as Control).focus_mode != Control.FOCUS_NONE \
				and (child is BaseButton and not (child as BaseButton).disabled):
			out.append(child)
			continue
		_usable_in(child, out)


## Node types the player can install, in id order (home cores excluded); locked ones
## are listed but disabled.
func _node_choices() -> Array[NetworkNodeData]:
	var out: Array[NetworkNodeData] = []
	for id in RunManager.lookup().ids_of_class(&"NetworkNodeData"):
		var node := RunManager.lookup().get_content(id) as NetworkNodeData
		if node != null and node.node_type != RC.NetworkNodeType.HOME_SERVER and node.install_cost > 0:
			out.append(node)
	return out


func show_grid() -> void:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	_sync_previews()
	# ANIM-R4 H10: the run a JACK IN here starts, and a raid, have their music made ahead.
	AudioDirector.prewarm_music(["netrun", "combat", "raid"], c.corporation_id)
	_grid_chips.clear()
	_jack_button = null
	# The Grid lives on the city (M3: the rest of the city greyed out); the side column
	# holds the plan, the legend and the Site list. `grid_view` stays as the (hidden)
	# summary map model: its clicks and selection mirror the city map's.
	var outer := HBoxContainer.new()
	outer.add_theme_constant_override("separation", 0)
	outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var spacer := Control.new()
	spacer.name = "GridMapArea"
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	outer.add_child(spacer)
	# H23 #3: the map key sits on the map (in the side column's foot it fell below the fold),
	# a strip along the map's foot; the map is framed above it (`fit_grid_map`).
	grid_legend = MapLegend.pin_to(spacer, c.corporation_id, true)
	# W8b (§6.10, §10.5; critique gifs/07, gifs/20): a rebuilt Grid puts its key where the
	# last one stood (a new key laid out at its corner first popped mid-map for a frame).
	_restore_grid_legend()
	grid_view = GridMapView.new()
	grid_view.visible = false
	grid_view.show_grid(c, corp, _threat_paths())
	grid_view.selected_id = selected_site
	grid_view.site_clicked.connect(select_site)
	outer.add_child(grid_view)
	var side := VBoxContainer.new()
	side.name = "GridSide"
	side.custom_minimum_size.x = GRID_SIDE_WIDTH
	side.add_theme_constant_override("separation", 10)
	# The column scrolls on its own (H21 #15: at 1.6, or with a raid pending and many
	# claimed nodes, RUNS OPEN NOW went off the screen; the city page itself never scrolls):
	# by mouse wheel over it, and by pad as focus moves down (follow_focus).
	var side_scroll := ScrollContainer.new()
	side_scroll.name = "GridSideScroll"
	side_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	side_scroll.follow_focus = true
	side_scroll.custom_minimum_size.x = GRID_SIDE_WIDTH + SIDE_SCROLLBAR
	side_scroll.add_child(side)
	side_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	# The site navigation stays pinned above the scrolling part (merge fix: a taller legend
	# let follow_focus scroll the nav row under the subtitle band).
	var column := VBoxContainer.new()
	column.name = "GridColumn"
	column.add_theme_constant_override("separation", 10)
	column.add_child(side_scroll)
	outer.add_child(column)
	# H20: no plan note or Site list; the map carries status and objectives, the side
	# column holds the picked Site's card with its actions, the runs open now, the legend.
	var launchable := RunManager.launchable_sites()
	launchable.append_array(RunManager.patrol_sites())
	if (selected_site == &"" or CampaignRules.site_data(corp, selected_site) == null) and not launchable.is_empty():
		selected_site = launchable[0].id
	if selected_site == &"" or CampaignRules.site_data(corp, selected_site) == null:
		selected_site = c.grid.home_site_id
	# The card over the full column, then the runs open now (the legend is on the map).
	var top := GridContainer.new()
	top.columns = 1
	side.add_child(top)
	var site := CampaignRules.site_data(corp, selected_site)
	if site != null:
		var card := _site_card(site, launchable, c.living_operatives(), _node_choices())
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		card.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		_fix_card_height(card)
		top.add_child(card)
	# Every Site stays reachable without the mouse: step through them, or jump to a run.
	# First in the column: the city screens don't scroll by mouse wheel, so Back to HQ
	# must stay on screen at text scale 1.6.
	# H23 #5: the row wraps inside the column (as one row, with RAID SETUP at text scale 1.6
	# it widened the column over most of the map).
	var nav := HFlowContainer.new()
	nav.name = "SiteNav"
	nav.add_theme_constant_override("h_separation", 8)
	nav.add_theme_constant_override("v_separation", 6)
	# H24 K2: the row keeps inside the column's windows (the scroll bar's strip is not
	# theirs: Back to HQ reached past their border).
	var nav_box := MarginContainer.new()
	nav_box.name = "SiteNavBox"
	nav_box.add_theme_constant_override("margin_right", int(SIDE_SCROLLBAR))
	nav_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	nav_box.add_child(nav)
	column.add_child(nav_box)
	column.move_child(nav_box, 0)
	# H23 #7: every Site row and step button carries the map icon of its Site (kind, map
	# colour, tier pips), so the list and the map read alike.
	var map_nodes := {}
	for n in grid_graph()["nodes"]:
		map_nodes[n["id"]] = n
	var prev := _step_button(tr("< PREV SITE"), "<", func() -> void: step_site(-1))
	prev.name = "PrevSite"
	_site_mark(prev, map_nodes.get(stepped_site(-1), {}), false)
	_add_tip(nav, prev, tr("PREV SITE: select the previous Site on the Grid: %s (the map follows).") % _site_kind_name(stepped_site(-1)))
	var next := _step_button(tr("NEXT SITE >"), ">", func() -> void: step_site(1))
	next.name = "NextSite"
	_site_mark(next, map_nodes.get(stepped_site(1), {}), false)
	_add_tip(nav, next, tr("NEXT SITE: select the next Site on the Grid: %s (the map follows).") % _site_kind_name(stepped_site(1)))
	var back := _icon(_step_button(tr("Back to HQ"), "", show_hq), StatIcon.BACK)
	back.name = "BackToHq"
	_add_tip(nav, back, tr("Back to the HQ: crew, Black Market, Cell status."))
	if not c.pending_raids.is_empty():
		var raid_btn := _icon(_step_button(tr("RAID SETUP"), "", show_raid), StatIcon.RAIDS)
		raid_btn.name = "RaidSetup"
		raid_btn.theme_type_variation = UiTheme.PRIMARY  # W8b §11: the primary while a raid is pending
		_add_tip(nav, raid_btn, tr("RAID SETUP: a raid is coming along the dashed routes: set up the defence."))
	if not launchable.is_empty():
		var runs := TerminalWindow.new(tr("RUNS OPEN NOW"), Palette.CELL_ACID)
		runs.name = "RunsOpen"
		side.add_child(runs)
		# One run a row (H23 #7: wrapped side by side they read as a jumble).
		var rows := VBoxContainer.new()
		rows.name = "RunRows"
		rows.add_theme_constant_override("separation", 6)
		runs.body.add_child(rows)
		_run_buttons.clear()
		for s in launchable:
			var sid := s.id
			var mn: Dictionary = map_nodes.get(s.id, {})
			var kind := String(mn.get("kind", CityMapOverlay.KIND_TIER))
			# H24 K7: the words translated here, once (the button does not translate them again).
			var words := "%s %s" % [CityMapOverlay.tier_text(s.tier), site_name(s.id)]
			if kind != CityMapOverlay.KIND_TIER:
				words += " · %s" % CityMapOverlay.kind_word(kind).to_upper()  # kind_word translates
			var b := _button(words, func() -> void: select_site(sid))
			b.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
			b.name = "Run_%s" % s.id
			b.alignment = HORIZONTAL_ALIGNMENT_LEFT
			b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			b.autowrap_mode = TextServer.AUTOWRAP_WORD  # a long name wraps in the column, at words
			# H22 #14: the Site's own map icon (objective or tier, the map's colour) and its tier
			# as pips (the harder the run, the more bars).
			_site_mark(b, mn)
			if s.id == selected_site:
				b.add_theme_color_override("font_color", Palette.CELL_ACID)
			# H24 K4: what clearing it gives and risks, as icons under the row (the rows
			# looked alike), and the row lights its node on the map (and the node its row).
			var preview := clear_preview_of(s)
			var gains := run_gains(s, preview)
			var said := PackedStringArray()
			for g: Badge in gains:
				said.append(g.tooltip_text.replace("\n", " "))
			# W8b (§11 City Grid, critique 19): a run is one framed row holding its button and its
			# chips (they floated between rows).
			var run_row := PanelContainer.new()
			run_row.name = "Row_%s" % s.id
			run_row.add_theme_stylebox_override("panel", UiTheme.box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, 1, UiTheme.SP_XS, UiTheme.SP_XS))
			rows.add_child(run_row)
			# A one-column grid, not a box: the column's row snap (ScrollHint) sees the framed row as
			# the row, never its button alone.
			var row_box := GridContainer.new()
			row_box.columns = 1
			row_box.add_theme_constant_override("v_separation", UiTheme.SP_XS)
			run_row.add_child(row_box)
			_add_tip(row_box, b, tr("%s %s: %s. %s %s Select it, then %s on its card.") % [CityMapOverlay.tier_text(s.tier), site_name(s.id), tr(CampaignRules.run_kind_for(c, s)),
				CityMapOverlay.tr_word(String(CityLayout.KIND_TIPS.get(kind, ""))), " ".join(said), tr(JACK_IN)])
			var gain_row := HFlowContainer.new()
			gain_row.name = "Gains_%s" % s.id
			gain_row.add_theme_constant_override("h_separation", 10)
			gain_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
			for g: Badge in gains:
				gain_row.add_child(g)
			row_box.add_child(gain_row)
			b.set_meta(&"site_id", s.id)
			b.mouse_entered.connect(_light_site.bind(s.id))
			b.focus_entered.connect(_light_site.bind(s.id))
			b.mouse_exited.connect(_unlight_site.bind(s.id))
			b.focus_exited.connect(_unlight_site.bind(s.id))
			_run_buttons[s.id] = b
	_set_panel(outer, "grid")
	_fit_steps(nav)
	# More below in the column (the runs at big text): the same tag as the HQ page's.
	side_hint = ScrollHint.new(side_scroll)
	side_hint.snap_rows = true  # ANIM-R3 B13: the runs list never ends in a half row
	side_hint.name = "SideHint"
	add_child(side_hint)
	UiFocus.link_layout(column)  # the side column row by row (nav, card actions, runs)
	var g := grid_graph()
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, GRID_ANCHOR, GRID_ZOOM)
	city_overlay.selected_id = selected_site
	city_overlay.node_clicked.connect(func(id: StringName) -> void: grid_view.site_clicked.emit(id))
	city_overlay.node_hovered.connect(light_run_row)
	city_overlay.avoid_controls([column, grid_legend])  # map labels stay clear of the column and the key
	_grid_fits = 0
	_grid_leaned = false
	_fit_next_frame()
	spacer.resized.connect(_refit_grid)
	grid_legend.minimum_size_changed.connect(_on_grid_legend_resized)
	grid_legend.visibility_changed.connect(_refit_grid)
	# H24 K1: the folded key opens over the map (no refit) and folds back.
	grid_legend.fold_changed.connect(_place_grid_legend)
	if grid_legend.foldable():
		set_page_prompts(prompts_for("grid") + [[&"cycle_target", "Key"]])
	_register_grid_drops(site)


## The Grid map fitted to the part of the screen it shows through (H23 #5: at 1.6 a T3
## Site sat under the side column; H23 #3: the key sits on the map): the legend is a strip
## along the map's foot, as wide as the map, its rows in columns. Then, when a node (icon
## or tier pips) lies outside the part above it, the camera pans and zooms out to fit
## them, and checks again once the city has redrawn (at most GRID_FITS_MAX passes).
func fit_grid_map() -> void:
	if panel_name != "grid" or city_overlay == null or not is_instance_valid(city_overlay) \
			or grid_legend == null or not is_instance_valid(grid_legend) or not grid_legend.is_inside_tree():
		return
	var city := wireframe.city
	if not city.camera_settled():
		# The icons move once the city has drawn under the new camera: measure then.
		_fit_after_redraw()
		return
	var area_ctl := grid_legend.get_parent() as Control
	var area := area_ctl.get_global_rect()
	if area.size.x <= LegendSpot.MARGIN * 2.0 or area.size.y <= LegendSpot.MARGIN * 2.0 or not get_global_rect().grow(1.0).encloses(area):
		return  # laid out later: the area's `resized` fits it again
	# H24 K1: map labels stay on the map's own area (under the top bar, beside the column).
	city_overlay.screen_rect = area
	var free := area.grow(-LegendSpot.MARGIN)
	if grid_legend.visible:
		# The key runs along the map's foot, in as many columns as the width holds; the
		# nodes fit above it (above its folded MAP KEY line at big text, H24 K1).
		_grid_legend_size = Vector2.INF  # the width set here is not a text size change
		grid_legend.set_strip_width(free.size.x)
		var own := grid_legend.fit_size()
		_grid_legend_size = own
		_place_grid_legend()
		free.size.y = maxf(1.0, area.size.y - own.y - LegendSpot.MARGIN * 2.0 - LegendSpot.MARGIN)
	if _grid_fits >= GRID_FITS_MAX:
		_grid_settled(free)
		return
	var fit: Dictionary = wireframe.unrigged(func() -> Dictionary:
		return LegendSpot.fit_into(city_overlay, free, GRID_ZOOM / city.scale.x, GRID_MIN_ZOOM / city.scale.x))
	if fit.is_empty():
		_grid_settled(free)
		return
	_grid_fits += 1
	var k := float(fit["zoom"])
	var screen := get_global_rect()
	var focus_at := screen.position + city.focus_anchor * screen.size
	# Zooming by k about the focus point moves the nodes' centre to focus + (from - focus) * k;
	# the focus then goes where that centre lands in the free part of the map.
	var to: Vector2 = fit["to"]
	var from: Vector2 = fit["from"]
	var anchor := (to - (from - focus_at) * k - screen.position) / screen.size
	_frame_city(city.scale.x * k, city.focus_grid, anchor)
	_fit_after_redraw()  # check again under the new camera


## ANIM-5 (4.14): the Grid map has settled into `free`: the camera leans toward the
## selected Site once (`grid_lean`), then the picture eases from the frame it held.
func _grid_settled(free: Rect2) -> void:
	# W8b (§12 reduce motion): no lean when camera moves are off (the fitted frame is the end).
	if not _grid_leaned and panel_name == "grid" and city_overlay != null and is_instance_valid(city_overlay) and Motion.camera_moves_allowed():
		_grid_leaned = true
		var lean: Vector2 = wireframe.unrigged(func() -> Vector2: return grid_lean(free))
		if lean.length() >= GRID_LEAN_MIN:
			var city := wireframe.city
			_frame_city(city.scale.x, city.focus_grid, city.focus_anchor + lean / get_global_rect().size)
			if city.is_baked():
				city.update_camera()
				_grid_settled(free)
				return
			if not city.rebuilt.is_connected(_grid_settled):
				city.rebuilt.connect(_grid_settled.bind(free), CONNECT_ONE_SHOT | CONNECT_DEFERRED)
			return
	# ANIM-R2 R1: remembered, so the next visit's city is baked ahead (`_prebake_grid`).
	if panel_name == "grid" and RunManager.campaign != null:
		wireframe.city.update_camera()
		_grid_views[_grid_memory_key()] = wireframe.city.bake_region()
	wireframe.ease_camera()


## ANIM-5 (4.14): how far (screen px) the Grid camera leans so the selected Site moves
## toward the middle of `free`: at most `map_camera_ease`'s amplitude, and only as far as
## keeps every node (icon and tier pips) inside the area the fit aims at, so the H23/H24
## framing holds at the end.
func grid_lean(free: Rect2) -> Vector2:
	if city_overlay == null or not is_instance_valid(city_overlay) or selected_site == &"":
		return Vector2.ZERO
	var at := city_overlay.icon_at(selected_site)
	var rects := LegendSpot.node_rects(city_overlay, false)
	if at.x == INF or rects.is_empty():
		return Vector2.ZERO
	var box := rects[0]
	for r in rects:
		box = box.merge(r)
	var aim := free.grow(-LegendSpot.FIT_INSET) if free.size.x > LegendSpot.FIT_INSET * 4.0 and free.size.y > LegendSpot.FIT_INSET * 4.0 else free
	var want := aim.get_center() - city_overlay.get_global_transform() * at
	var lo := aim.position - box.position
	var hi := aim.end - box.end
	var out := Vector2.ZERO
	for axis in 2:
		if lo[axis] <= 0.0 and hi[axis] >= 0.0:
			out[axis] = clampf(want[axis], lo[axis], hi[axis])
	return out.limit_length(Motion.amplitude(&"map_camera_ease"))


## H24 K4: what clearing Site `s` gives and risks (`preview` = CampaignRules.clear_preview),
## one Badge each with its icon and a tooltip: the Exploit, the Heat change (a drop:
## the cooling icon), a raid it brings, the win, Schematics, the Sites it opens (names
## and kinds in the tooltip), and whether it can be claimed; "no gain" for a patrol.
func run_gains(_site: SiteData, preview: Dictionary) -> Array[Badge]:
	var out: Array[Badge] = []
	if bool(preview.get("won", false)):
		out.append(Badge.new(CityMapOverlay.tr_word("WIN"), Palette.CELL_ACID, "", CityMapOverlay.tr_word("Clearing it wins the campaign.")).with_icon(StatIcon.WON))
	var ex := int(preview.get("exploit", -1))
	if ex >= 0:
		var ename := String(RC.ExploitType.keys()[ex]).capitalize()
		out.append(Badge.new(CityMapOverlay.tr_word("EXPLOIT"), Palette.CELL_ACID, "", CityMapOverlay.tr_word("Clearing it gives the %s Exploit for the boss breach.") % ename).with_icon(StatIcon.EXPLOITS))
	var heat := int(preview.get("heat", 0))
	if heat != 0:
		out.append(Badge.new(CityMapOverlay.tr_word("HEAT %+d") % heat, Palette.NET_CYAN if heat < 0 else StatIcon.color_of(StatIcon.HEAT), "",
			CityMapOverlay.tr_word("Clearing it changes Heat by %+d.") % heat).with_icon(StatIcon.COOLING if heat < 0 else StatIcon.HEAT))
	if bool(preview.get("raid", false)):
		out.append(Badge.new(CityMapOverlay.tr_word("RAID"), Palette.CELL_PINK, "", CityMapOverlay.tr_word("Clearing it now brings a raid on your network.")).with_icon(StatIcon.RAIDS))
	var sch := int(preview.get("schematics", 0))
	if sch != 0:
		out.append(Badge.new("%+d" % sch, Palette.NET_CYAN, "", CityMapOverlay.tr_word("Clearing it gives %+d Schematics.") % sch).with_icon(StatIcon.SCHEMATICS))
	var opens: Array = preview.get("opens", [])
	if not opens.is_empty():
		var named := PackedStringArray()
		for id in opens:
			named.append(_site_kind_name(id))
		out.append(Badge.new(CityMapOverlay.tr_word("OPENS %d") % opens.size(), Palette.NET_CYAN, "",
			CityMapOverlay.tr_word("Clearing it opens %d more Sites to runs: %s.") % [opens.size(), "; ".join(named)]).with_icon(StatIcon.LINKS))
	if bool(preview.get("claimable", false)):
		out.append(Badge.new(CityMapOverlay.tr_word("CLAIM"), Palette.CELL_TURF, "", CityMapOverlay.tr_word("Once cleared you can claim it: a node of your network.")).with_icon(StatIcon.CLAIM))
	if out.is_empty():
		out.append(Badge.new(CityMapOverlay.tr_word("NO GAIN"), Color(Palette.PAPER, 0.6), "", CityMapOverlay.tr_word("A patrol: loot, Heat and Rank from the run, no objective.")).with_icon(StatIcon.RUNS))
	for b in out:
		b.name = "Gain_%d" % out.find(b)
	return out


## H24 K4: the run rows by Site id (the Grid's RUNS OPEN NOW).
var _run_buttons: Dictionary = {}


## H24 K4: a run row is hovered or has the pad's focus: light its node on the map.
func _light_site(id: StringName) -> void:
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.hover_id = id


func _unlight_site(id: StringName) -> void:
	if city_overlay != null and is_instance_valid(city_overlay) and city_overlay.hover_id == id:
		city_overlay.hover_id = &""


## H24 K4: the pointer is on node `id` of the Grid map: its run row looks hovered (the
## others as they are); &"" lights none.
func light_run_row(id: StringName) -> void:
	for sid in _run_buttons:
		var b := _run_buttons[sid] as Button
		if b == null or not is_instance_valid(b):
			continue
		var lit: bool = sid == id
		b.set_meta(&"lit", lit)
		if lit:
			b.add_theme_stylebox_override(&"normal", b.get_theme_stylebox(&"hover"))
		else:
			b.remove_theme_stylebox_override(&"normal")


## H24 K1: the Grid's key at the foot of the map area, growing upward (open, its rows sit
## over the map; the map is framed for the folded line).
func _place_grid_legend() -> void:
	if grid_legend == null or not is_instance_valid(grid_legend):
		return
	var area_ctl := grid_legend.get_parent() as Control
	if area_ctl.size.y <= LegendSpot.MARGIN * 2.0:
		return  # not laid out yet: the key stays where it was put (never mid-map)
	var own := grid_legend.get_combined_minimum_size()
	grid_legend.size = own
	grid_legend.position = Vector2(LegendSpot.MARGIN, maxf(LegendSpot.MARGIN, area_ctl.size.y - own.y - LegendSpot.MARGIN))
	_grid_legend_last = {"scale": Settings.text_scale, "width": grid_legend.strip_width, "position": grid_legend.position, "size": own, "opened": grid_legend.opened}


## W8b: where the Grid's key last stood ({scale, width, position, size, opened}; view memory).
var _grid_legend_last: Dictionary = {}


## W8b (§6.10): a new Grid key takes the last key's width and place at once (the same text
## size), so a rebuilt page never moves it; the fit then confirms it.
func _restore_grid_legend() -> void:
	if _grid_legend_last.is_empty() or not is_equal_approx(float(_grid_legend_last["scale"]), Settings.text_scale):
		return
	grid_legend.set_anchors_preset(Control.PRESET_TOP_LEFT)
	grid_legend.set_strip_width(float(_grid_legend_last["width"]))
	grid_legend.size = _grid_legend_last["size"]
	grid_legend.position = _grid_legend_last["position"]


## H24 K1 / K2: a Grid step button that carries its full words and its short form (icon
## and arrow only; `short` "" = the icon alone), see `_fit_steps`.
func _step_button(full: String, short: String, on_pressed: Callable) -> Button:
	var b := _button(full, on_pressed)
	b.set_meta(&"full_text", full)
	b.set_meta(&"short_text", short)
	return b


## H24 K1 / K2: the step row fits the column: at big text (STEP_ICONS_SCALE) or when a
## button's words (translated) are wider than the column, it shows its short form (the
## words stay in its tooltip); a button still too wide wraps its words inside the column.
func _fit_steps(nav: HFlowContainer) -> void:
	var room := GRID_SIDE_WIDTH
	for b in nav.get_children():
		if not (b is Button) or not b.has_meta(&"full_text"):
			continue
		var btn := b as Button
		btn.text = String(btn.get_meta(&"full_text"))
		btn.autowrap_mode = TextServer.AUTOWRAP_OFF
		btn.custom_minimum_size.x = 0.0
		if Settings.text_scale >= STEP_ICONS_SCALE - 0.001 or btn.get_combined_minimum_size().x > room:
			btn.text = String(btn.get_meta(&"short_text"))
		if btn.get_combined_minimum_size().x > room:
			btn.autowrap_mode = TextServer.AUTOWRAP_WORD
			btn.custom_minimum_size.x = room
func _fit_after_redraw() -> void:
	var city := wireframe.city
	if city.is_baked():
		# ANIM-R2 R1: a baked city's placement follows the camera at once: the next pass
		# measures now (each pass waited for a redraw, all of them in one long frame).
		city.update_camera()
		fit_grid_map()
		return
	if not city.rebuilt.is_connected(fit_grid_map):
		city.rebuilt.connect(fit_grid_map, CONNECT_ONE_SHOT | CONNECT_DEFERRED)


## The key's size changed (its text size): fit the map again. The fit itself sets the
## key's width, so a size it has already fitted to is ignored.
func _on_grid_legend_resized() -> void:
	if _grid_legend_size == Vector2.INF:
		return
	if grid_legend != null and is_instance_valid(grid_legend) and not grid_legend.fit_size().is_equal_approx(_grid_legend_size):
		_refit_grid.call_deferred()


## The Grid map's area or key changed size (text scale, legend switch): fit it again. A
## fit is worked out from where the nodes are now, so fits never compound.
func _refit_grid() -> void:
	if panel_name != "grid" or city_overlay == null or not is_instance_valid(city_overlay):
		return
	_grid_fits = 0
	_fit_next_frame()


## Runs `fit_grid_map` once at the next frame, when the page's layout has settled (a fit
## during the containers' first sorts would frame the map for a size it never keeps).
func _fit_next_frame() -> void:
	if not get_tree().process_frame.is_connected(fit_grid_map):
		get_tree().process_frame.connect(fit_grid_map, CONNECT_ONE_SHOT)


## Mounts the map overlay on the net city and frames the camera on it. `zoom` > 1 moves
## the camera in; `focus` (grid) overrides the graph's centre.
func _mount_city_map(nodes: Array[Dictionary], edges: Array[Dictionary], look: int, anchor: Vector2, zoom: float = 1.0, focus: Vector2 = Vector2.INF) -> void:
	_clear_city_map()
	var city := wireframe.city
	city_overlay = CityMapOverlay.new(city)
	# H24 S4: the node tips come translated (the screens build them), shown as given.
	city_overlay.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	city.add_child(city_overlay)
	city_overlay.set_look(look)
	if RunManager.campaign != null:
		city_overlay.corp_id = RunManager.campaign.corporation_id  # W8b §3.6: threat routes in its pattern
	city_overlay.set_graph(nodes, edges)
	_frame_city(zoom, city_overlay.centre() if focus == Vector2.INF else focus, anchor)


## Camera on the net city: zoom and put grid point `focus` at screen fraction `anchor`.
func _frame_city(zoom: float, focus: Vector2, anchor: Vector2) -> void:
	var city := wireframe.city
	city.scale = Vector2(zoom, zoom)
	city.offset_left = 0
	city.offset_top = 0
	city.offset_right = size.x / zoom - size.x
	city.offset_bottom = size.y / zoom - size.y
	city.focus_grid = focus
	city.focus_anchor = anchor
	city.refresh()
	wireframe.sync_hold()  # ANIM-5: a held frame stays on screen through the change


func _clear_city_map() -> void:
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.queue_free()
	city_overlay = null
	var city := wireframe.city
	if city.focus_grid != Vector2.INF or city.scale != Vector2.ONE:
		city.focus_grid = Vector2.INF
		city.scale = Vector2.ONE
		city.offset_right = 0
		city.offset_bottom = 0
		city.refresh()


## The campaign's Grid as a graph for the city overlay (CityLayout.grid_graph).
func grid_graph() -> Dictionary:
	return CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, _threat_paths(), selected_site)


## Pending raids' routes, entry -> home, for the map's corporate arrows.
func _threat_paths() -> Array[Array]:
	return CityLayout.threat_paths(RunManager.campaign, RunManager.corporation)


## Selects a Site clicked on the Grid map and redraws the Grid with its actions first.
## ANIM-5 (4.14): the picture holds the old frame while the page refits and then eases
## to the new one (the camera leans toward the Site, `grid_lean`).
func select_site(site_id: StringName) -> void:
	if panel_name == "grid":
		wireframe.hold_camera()
	selected_site = site_id
	show_grid()


## Selects the Site `step` places after the selected one in the Grid's order (wraps), so a
## pad reaches every Site without the map (H20).
func step_site(step: int) -> void:
	var to := stepped_site(step)
	if to != &"":
		select_site(to)


## The Site `step` places after the selected one in the Grid's order (wraps; &"" when the
## Grid has none).
func stepped_site(step: int) -> StringName:
	var sites := RunManager.corporation.city_grid.sites.filter(func(s: SiteData) -> bool: return s != null)
	if sites.is_empty():
		return &""
	var i := 0
	for k in sites.size():
		if sites[k].id == selected_site:
			i = k
	return sites[posmod(i + step, sites.size())].id


## Puts map node `mn`'s icon on button `b` (H22 #14, H23 #7): its kind in the map's
## colour, the tier inside a plain Site's hexagon and, with `pips`, the tier pips after it.
func _site_mark(b: Button, mn: Dictionary, pips: bool = true) -> void:
	var kind := String(mn.get("kind", CityMapOverlay.KIND_TIER))
	IconMark.attach(b, StatIcon.MAP)
	IconMark.attach_map(b, kind, mn.get("color", Palette.NET_CYAN), String(mn.get("glyph", "")) if kind == CityMapOverlay.KIND_TIER else "",
		CityMapOverlay.tier_of(mn) if pips else 0)


## Site `id`'s name and kind for a tooltip ("Kill-Switch Authority, a T2 Exploit Site").
func _site_kind_name(id: StringName) -> String:
	var sd := CampaignRules.site_data(RunManager.corporation, id)
	if sd == null:
		return site_name(id)
	var kind := CityLayout.site_kind(RunManager.campaign, sd)
	if kind == CityMapOverlay.KIND_HOME:
		return tr("%s, your home server") % tr(CityLayout.HOME_LABEL)
	var word := CityMapOverlay.kind_word(kind)  # already translated
	return tr("%s, a T%d %s") % [site_name(id), sd.tier, word if kind == CityMapOverlay.KIND_TIER else tr("%s Site") % word]


## The glyph the map puts on a Site (objective, tier, CORE).
func _site_glyph(site: SiteData) -> String:
	var c := RunManager.campaign
	if site.id == c.grid.home_site_id:
		return GLYPH_HOME
	match CampaignRules.site_objective(c, site):
		RC.SiteObjective.EXPLOIT:
			return GLYPH_EXPLOIT
		RC.SiteObjective.HEAT_REDUCTION:
			return GLYPH_HEAT
		RC.SiteObjective.BOSS:
			return GLYPH_BOSS
	return CityMapOverlay.tier_text(site.tier)


## W8b (§10.5, §11 City Grid; critique gifs/20): the Site card keeps one height whatever Site
## is picked: its content scrolls inside the card body (at least SITE_CARD_BODY_MIN) under the
## card's title (the card SITE_CARD_HEIGHT tall), so the column never jumps when the
## selection changes.
func _fix_card_height(card: TerminalWindow) -> void:
	var inner := VBoxContainer.new()
	inner.name = "CardContent"
	inner.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	inner.add_theme_constant_override("separation", card.body.get_theme_constant("separation"))
	for child in card.body.get_children():
		card.body.remove_child(child)
		inner.add_child(child)
	var sc := ScrollContainer.new()
	sc.name = "CardScroll"
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.follow_focus = true
	sc.custom_minimum_size.y = SITE_CARD_BODY_MIN * Settings.text_scale
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.add_child(inner)
	card.body.add_child(sc)
	card.body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	# The whole card holds one height: a Site name on two title lines takes it from the body.
	card.custom_minimum_size.y = SITE_CARD_HEIGHT * Settings.text_scale


## The picked Site as a card (H20, replacing the Site list): its facts as badges (status,
## objective, node and integrity, upgrades, assets, station) and the actions it allows now
## (launch, claim, repair, upgrade). Named "SelectedSite".
func _site_card(site: SiteData, launchable: Array[SiteData], living: Array[OperativeState], choices: Array[NetworkNodeData]) -> TerminalWindow:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var s := c.grid.site(site.id)
	var status := int(s["status"])
	var accent := Palette.CELL_TURF if status == GridState.SiteStatus.CLAIMED else (Palette.NET_CYAN if status == GridState.SiteStatus.CLEARED else Palette.corp_color(c.corporation_id))
	var card := TerminalWindow.new(site_name(site.id), accent)
	card.name = "SelectedSite"
	card.set_meta(&"shows", [site.id, int(status)])  # ANIM-R3 B6: what refresh_site_card compares
	# H24 K7: tier and status words translated here, once.
	card.tag_label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	card.tag_label.text = "%s // %s" % [CityMapOverlay.tier_text(site.tier), CityMapOverlay.tr_word(String(STATUS_NAMES.get(status, "?"))).to_upper()]
	var facts := HFlowContainer.new()
	facts.name = "SiteFacts"
	facts.add_theme_constant_override("h_separation", 10)
	facts.add_theme_constant_override("v_separation", 4)
	card.body.add_child(facts)
	var status_badge := Badge.new(CityMapOverlay.tr_word(String(STATUS_NAMES.get(status, "?"))), accent, _site_glyph(site), tr(String(STATUS_TIPS.get(status, ""))))
	status_badge.name = "StatusBadge"
	if status == GridState.SiteStatus.CLAIMED:
		# ANIM-R3 B6: a claimed Site says so plainly (CLAIMED with the claim mark), and offers
		# no CLAIM.
		status_badge.text = CityMapOverlay.tr_word(String(STATUS_NAMES[status])).to_upper()
		status_badge.with_icon(StatIcon.CLAIM)
	elif CityLayout.site_kind(c, site) == CityMapOverlay.KIND_HEAT:
		status_badge.with_icon(StatIcon.COOLING)  # H24 K5: the Heat reduction Site's own icon
	facts.add_child(status_badge)
	var objective := CampaignRules.site_objective(c, site)
	if objective == RC.SiteObjective.EXPLOIT:
		var ename := exploit_name(site.exploit_type)
		facts.add_child(Badge.new(ename, Palette.CELL_ACID, GLYPH_EXPLOIT, tr("Clear this Site for the %s Exploit (%d/%d for the breach).") % [ename, c.exploits.size(), cfg.min_exploits_for_breach]).with_icon(StatIcon.EXPLOITS))
	elif objective == RC.SiteObjective.HEAT_REDUCTION:
		var dh := HeatRules.scaled_delta(c, site.heat_change, cfg)
		facts.add_child(Badge.new(CityMapOverlay.tr_word("Heat %s") % TextDb.signed(dh), Palette.NET_CYAN, GLYPH_HEAT, tr("Clearing this Site changes Heat by %d.") % dh).with_icon(StatIcon.COOLING if dh < 0 else StatIcon.HEAT))
	elif objective == RC.SiteObjective.BOSS:
		facts.add_child(Badge.new(tr("BOSS"), Palette.corp_color(c.corporation_id), GLYPH_BOSS, tr("The corporation's core. The breach needs %d Exploits.") % cfg.min_exploits_for_breach))
	elif site.objective == RC.SiteObjective.HEAT_REDUCTION:
		facts.add_child(Badge.new(CityMapOverlay.tr_word("off"), Color(Palette.NET_CYAN, 0.6), GLYPH_HEAT, tr("This Site's Heat objective is switched off at this ICE level.")).with_icon(StatIcon.COOLING))
	if c.grid.is_claimed(site.id):
		var node_col := Palette.CELL_TURF if int(s["condition"]) != GridState.Condition.DISABLED else Palette.RESIST_GOLD
		var node_text := "%s %d/%d" % [_display(c.grid.node_type_of(site.id)), int(s["integrity"]), int(s["max_integrity"])]
		if int(s["condition"]) == GridState.Condition.DISABLED:
			node_text += tr(" DISABLED")
		var node_data := lookup.get_content(c.grid.node_type_of(site.id)) as NetworkNodeData
		facts.add_child(Badge.new(node_text, node_col, GLYPH_NODE, TextDb.t(node_data, "description") if node_data != null else "").with_meter(int(s["integrity"]), int(s["max_integrity"])))
		if c.grid.upgrade_level_of(site.id) > 0:
			facts.add_child(Badge.new(TextDb.signed(c.grid.upgrade_level_of(site.id)), Palette.CELL_ACID, GLYPH_UPGRADE, tr("Node upgrade level %d.") % c.grid.upgrade_level_of(site.id)))
		for aid in c.grid.assets_on(site.id):
			var data := lookup.get_content(aid) as DefenseAssetData
			facts.add_child(Badge.new(_display(aid), Palette.CELL_PINK, "", TextDb.t(data, "description") if data != null else "", aid))
		var guard := c.grid.stationed_on(site.id)
		if guard != &"":
			var guard_op := c.get_operative(guard)
			facts.add_child(Badge.new(guard_op.name if guard_op != null else tr("guarded"), Palette.PAPER, GLYPH_GUARD, tr("An operative is stationed here: their class's station bonus helps the node in raids.")))
	var row := HFlowContainer.new()
	row.name = "SiteActions"
	row.add_theme_constant_override("h_separation", 8)
	card.body.add_child(row)
	var launchable_here := false
	for l in launchable:
		if l.id == site.id:
			launchable_here = true
	if launchable_here and not living.is_empty():
		# Art pass W8b (§10.2, critique gifs/09): who runs it is picked on the crew's own
		# Polaroids (a press, or a drop on JACK IN; the native list is gone); the picked one
		# is stamped and rides beside JACK IN, so the choice is seen, not only listed.
		var who_runs := launch_operative()
		var who := IconMark.standalone(StatIcon.OPERATIVE, UiTheme.font_px(UiTheme.BODY) * IconMark.SIZE_FACTOR, Palette.CELL_PINK)
		who.name = "OperativeIcon"
		who.tooltip_text = tr("Who runs it.")
		who.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(who)
		var sid := site.id
		var kind := CampaignRules.run_kind_for(c, site)
		# One name for one idea (H21 #21): JACK IN, as on the HQ's stamp.
		var go := _icon(_button(tr(JACK_IN), func() -> void: launch(sid, launch_operative())), StatIcon.JACK_IN)
		go.add_to_group(Fx.JACK_FOCUS_GROUP)  # ANIM-5: jack in pushes into this JACK IN
		go.name = "Launch"
		# W8b (§11 City Grid): one primary per state: JACK IN, unless a raid is pending (then
		# RAID SETUP is the primary and JACK IN a secondary).
		go.theme_type_variation = UiTheme.PRIMARY if c.pending_raids.is_empty() else UiTheme.SECONDARY
		_add_tip(row, go, tr("JACK IN to %s: start a %s here with the picked operative.") % [site_name(site.id), tr(kind)])
		_jack_button = go
		# The picked operative beside JACK IN: their Polaroid, stamped.
		var chosen_op := c.get_operative(who_runs)
		var rider := CrewChip.new(chosen_op.class_id if chosen_op != null else &"", who_runs, chosen_op.name if chosen_op != null else "")
		rider.name = "JackOperative"
		rider.picked = true
		rider.disabled = true
		rider.focus_mode = Control.FOCUS_NONE
		rider.mouse_filter = Control.MOUSE_FILTER_IGNORE
		rider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(rider)
		# ANIM-4: the crew as small Polaroids: press one to pick them, or drag one onto JACK IN
		# (ANIM-R1: a drop picks; only the press on JACK IN launches).
		var chips := HFlowContainer.new()
		chips.name = "CrewChips"
		chips.add_theme_constant_override("h_separation", 6)
		chips.add_theme_constant_override("v_separation", 6)
		for op in living:
			var chip := CrewChip.new(op.class_id, op.id, op.name)
			chip.name = "Chip_%s" % op.id
			chip.picked = op.id == who_runs
			var post := CampaignRules.stationed_site(c, op.id)
			chip.tooltip_text = UiTip.fold("%s\n%s" % [tr("%s R%d%s") % [op.name, op.rank, (tr(" (leaves %s)") % site_name(post)) if post != &"" else ""],
				UiTip.for_input(tr("%s: drag onto JACK IN to pick them for %s (or pick them in the list), then press JACK IN."),
					tr("%s: pick them up and move them onto JACK IN to pick them for %s (or pick them in the list), then press JACK IN.")) % [op.name, site_name(site.id)]])
			var oid := op.id
			chip.pressed.connect(func() -> void: pick_operative(oid))
			chips.add_child(chip)
			_grid_chips.append(chip)
		card.body.add_child(chips)
		card.body.move_child(chips, row.get_index())
	if c.grid.is_cleared(site.id) and site.claimable:
		# W8b (§6.5): the node to build as tiles (a locked one greyed with its lock and unlock).
		var node_list: Array[NetworkNodeData] = []
		var node_tiles: Array[Dictionary] = []
		for locked_pass in [false, true]:
			for node in choices:
				var available := CampaignRules.node_available(RunManager.profile, lookup, node)
				if available == locked_pass:
					continue
				node_list.append(node)
				var tile := {"name": TextDb.t(node, "display_name"), "meta": "%d" % node.install_cost, "icon": StatIcon.LINKS}
				if not available:
					tile["locked"] = true
					tile["unlock"] = _unlock_words(node)
				node_tiles.append(tile)
		var node_pick := PlanningPicker.new(node_tiles, 0, NODE_TILE)
		node_pick.name = "NodePick"
		node_pick.columns = clampi(floori((GRID_SIDE_WIDTH - UiTheme.SP_L) / (NODE_TILE.x * minf(Settings.text_scale, PlanningPicker.WIDTH_GROW_MAX) + TilePicker.TILE_GAP)), 1, maxi(1, node_tiles.size()))
		node_pick.tooltip_text = UiTip.fold(tr("Build the picked node here: it joins your network and defends in raids."))
		card.body.add_child(node_pick)
		card.body.move_child(node_pick, row.get_index())
		var sid2 := site.id
		_add_tip(row, _icon(_button(tr("Claim"), func() -> void: claim(sid2, node_list[node_pick.selected()].id)), StatIcon.CLAIM), tr("Build the picked node here: it joins your network and defends in raids."))
	if c.grid.is_claimed(site.id) and int(s["condition"]) == GridState.Condition.DISABLED:
		var sid3 := site.id
		_add_tip(row, _button(tr("Repair (%d)") % CampaignRules.repair_cost(c, cfg, lookup, sid3), func() -> void: repair(sid3)), tr("Bring the disabled node back online."))
	if c.grid.is_active_node(site.id) and site.id != c.grid.home_site_id:
		var cost := CampaignRules.upgrade_cost(c, cfg, site.id)
		if cost >= 0:
			var sid4 := site.id
			_add_tip(row, _button(tr("Upgrade (%d)") % cost, func() -> void: upgrade(sid4)), tr("Upgrade the node one level (level %d now).") % c.grid.upgrade_level_of(site.id))
	return card


func show_raid() -> void:
	var c := RunManager.campaign
	var pending := RunManager.pending_raid()
	if pending.is_empty():
		show_hq()
		return
	var lookup := RunManager.lookup()
	var cfg := RunManager.config()
	var raid := CampaignRules.raid_data(pending, lookup)
	var projection := RunManager.project_raid()
	var claimed := c.grid.claimed_ids()
	if not claimed.has(selected_site):
		selected_site = claimed[claimed.size() - 1] if not claimed.is_empty() else &""
	# Raid setup on the city (rest of the city greyed out): the network and the threat
	# routes on real streets, each node's projected outcome on the map; the raid card, the
	# node orders and the Armory in the side column and below (H20: no text wall).
	# H22 #9: the side column takes the page's full height and the Armory sits under the
	# map beside it (full width under both, it went off the screen at 1.6).
	var outer := HBoxContainer.new()
	outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var map_col := VBoxContainer.new()
	map_col.name = "RaidMapColumn"
	map_col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	map_col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	outer.add_child(map_col)
	var spacer := Control.new()
	spacer.name = "RaidMapArea"
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	map_col.add_child(spacer)
	# The raid map has its key too (H20 #22), placed where it covers no node (H22 #9); one
	# key, listing only what this map shows (H23 S4: all its rows took a quarter of the
	# screen).
	var g := raid_graph(projection, {})
	# H24 S5: the key is a column at the map's left, or a strip along its foot when the
	# nodes cannot fit beside the column (kept for this layout once chosen).
	# ANIM-R2 R13: at big text (MapLegend.FOLD_SCALE and up) the key is the Grid's folding
	# strip from the start (its column covered about half the map at 1.6).
	_raid_strip = (_raid_strip_key != "" and _raid_strip_key == raid_layout_key()) or Settings.text_scale >= MapLegend.FOLD_SCALE - 0.001
	raid_legend = MapLegend.pin_to(spacer, c.corporation_id, _raid_strip).show_only(MapLegend.keys_of(g, c.grid))
	if _raid_strip:
		raid_legend.minimum_size_changed.disconnect(raid_legend._repin)
		raid_legend.fold_changed.connect(_place_raid_strip)
	_raid_reframes = 0
	_raid_passes = 0
	_raid_checks = 0
	_raid_free = Rect2()
	_raid_step = {}
	_raid_box = Rect2()
	_raid_same = 0
	var side := VBoxContainer.new()
	side.name = "RaidSide"
	# W8b: at big text the side column holds the three defence cards in a row (RAID_SIDE_BIG).
	side.custom_minimum_size.x = RAID_SIDE_WIDTH if Settings.text_scale < RAID_BIG_SCALE - 0.001 else RAID_SIDE_BIG
	side.add_theme_constant_override("separation", UiTheme.SP_S if Settings.text_scale < RAID_HUGE_SCALE - 0.001 else UiTheme.SP_XS)
	outer.add_child(side)
	# H23 S5: what the raid is and what to do, in one plain sentence.
	var intro := _para(TextDb.ui_text("ui.raid_intro"))
	intro.name = "RaidIntro"
	intro.custom_minimum_size.x = RAID_SIDE_WIDTH  # wrapped at the column's width from the start
	intro.add_theme_color_override("font_color", Palette.PAPER)
	side.add_child(intro)
	# W8b (§5.3): at big text the sentence moves into the raid card's tooltip, so the column
	# (and the defence cards under the map) stay on the first screen.
	intro.visible = Settings.text_scale < RAID_BIG_SCALE - 0.001
	var raid_card := _raid_card(raid, pending, projection)
	if not intro.visible:
		raid_card.tooltip_text = UiTip.fold("%s
%s" % [intro.text, TextDb.t(raid, "warning_text")])
	side.add_child(raid_card)
	var orders_win := TerminalWindow.new(tr("YOUR NODES // pick the target"), Palette.CELL_PINK)
	orders_win.name = "NodeOrders"
	side.add_child(orders_win)
	# A fixed-height list (many claimed nodes scroll inside it; follow_focus for the pad).
	# H22 #9: the list takes the column's spare height (at least ORDERS_MIN_HEIGHT at the
	# text scale), so the Armory's cards under it stay on screen at big text.
	var orders_scroll := ScrollContainer.new()
	orders_scroll.name = "OrdersScroll"
	orders_scroll.custom_minimum_size = Vector2(0, ORDERS_MIN_HEIGHT * Settings.text_scale)
	orders_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	orders_win.size_flags_vertical = Control.SIZE_EXPAND_FILL
	orders_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	orders_scroll.follow_focus = true
	orders_win.body.add_child(orders_scroll)
	var orders := VBoxContainer.new()
	orders.name = "Orders"
	orders.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	orders.add_theme_constant_override("separation", 4)
	orders_scroll.add_child(orders)
	for site_id in claimed:
		orders.add_child(_node_order_row(site_id, projection, claimed))
	var go := HBoxContainer.new()
	go.name = "RaidGo"
	go.add_theme_constant_override("separation", 10)
	side.add_child(go)
	# W8b (§5.3 one primary, on the first screen at big text): START DEFENSE heads the column.
	side.move_child(go, 0)
	if Settings.text_scale >= RAID_HUGE_SCALE - 0.001:
		# At the largest text the row sits in the raid card under its facts, beside the stamp
		# (the room the stamp leaves there), so the card, the loadout and every node stay on
		# the first screen.
		var facts_box := raid_card.find_child("RaidFacts", true, false) as Control
		if facts_box != null:
			var holder := facts_box.get_parent()
			var col := VBoxContainer.new()
			col.name = "FactsAndGo"
			col.add_theme_constant_override("separation", 0)
			col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			var at := facts_box.get_index()
			holder.remove_child(facts_box)
			col.add_child(facts_box)
			side.remove_child(go)
			col.add_child(go)
			holder.add_child(col)
			holder.move_child(col, at)
	# H24 S14: "RUN THE RAID" read like attacking; the Cell defends.
	var run_btn := _icon(_button(tr(START_DEFENSE), fight_raid), StatIcon.PLAY)
	run_btn.name = "RunRaid"
	run_btn.theme_type_variation = &"HotButton"
	_add_tip(go, run_btn, tr("Start the defence: the raid plays out on the map; the result matches the forecast."))
	var back := _add_tip(go, _icon(_button(tr("Back to HQ"), show_hq), StatIcon.BACK), tr("Back to the HQ; the raid waits until you start the defence.")) as Button
	back.name = "RaidBack"
	# Art pass W1: the HotButton now scales with the text (ART_BIBLE §4.3.1). At big text
	# the secondary Back shows its icon only (its words stay in the tooltip), like the
	# Grid's step buttons (STEP_ICONS_SCALE), so the row keeps the column on screen.
	if Settings.text_scale >= STEP_ICONS_SCALE - 0.001:
		back.text = ""
	# H24 S14: the same words and tooltip as the HQ's ARMORY badge (assets banked, not
	# deployed, of the Armory's room).
	var loadout := TerminalWindow.new(tr("DEFENSE LOADOUT // %s") % armory_words(), Palette.CELL_PINK)
	loadout.name = "DefenseLoadout"
	loadout.tooltip_text = UiTip.fold(armory_tip())
	# W8b: at big text the target is named in the deploy steps only (the tag wrapped the title bar).
	loadout.tag_label.text = tr("TARGET: %s") % site_name(selected_site) if Settings.text_scale < STEP_ICONS_SCALE - 0.001 else ""
	if Settings.text_scale >= RAID_BIG_SCALE - 0.001:
		# W8b (§5.3, big text): the map keeps the column's height: the defence loadout sits in
		# the side column under the raid card and YOUR NODES moves under the map as a short
		# strip (it scrolls inside), so every node, card and START DEFENSE is on the first
		# screen at 2.0.
		side.add_child(loadout)
		side.remove_child(orders_win)
		map_col.add_child(orders_win)
		orders_win.size_flags_vertical = Control.SIZE_SHRINK_END
		orders_scroll.size_flags_vertical = Control.SIZE_FILL
	else:
		map_col.add_child(loadout)
	_raid_foot = null
	# How to deploy, in pictures (H22 #9): 1 pick a node (map or YOUR NODES), 2 press a
	# card: it goes to the target. The cards sit beside the steps.
	var deploy_row := HBoxContainer.new()
	deploy_row.add_theme_constant_override("separation", 14)
	loadout.body.add_child(deploy_row)
	deploy_row.add_child(_deploy_steps())
	# W8b: at big text the cards are one grid row (a flow reported its narrowest height, 355 px
	# for one row of 180 px cards, and pushed the column off the screen).
	var cards: Container = HFlowContainer.new()
	if Settings.text_scale >= RAID_BIG_SCALE - 0.001:
		var unique := {}
		for aid in c.armory:
			unique[aid] = true
		var grid := GridContainer.new()
		grid.columns = maxi(1, unique.size())
		cards = grid
	cards.name = "AssetCards"
	cards.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cards.add_theme_constant_override("h_separation", 14)
	cards.add_theme_constant_override("v_separation", 8)
	deploy_row.add_child(cards)
	var seen := {}
	for i in c.armory.size():
		var aid: StringName = c.armory[i]
		if seen.has(aid):
			continue
		seen[aid] = true
		var data := lookup.get_content(aid) as DefenseAssetData
		var card := AssetCard.new(aid, TextDb.t(data, "display_name") if data != null else String(aid), data.integrity if data != null else 0, c.armory.count(aid))
		card.set_effect(data)  # H24 S14: what it does, in a line and a pictogram
		card.tooltip_text = UiTip.fold(tr("%s\n%s\nPress to deploy it to %s (the target: pick another node on the map or in YOUR NODES).") % [TextDb.t(data, "description") if data != null else "", card.numbers_tip(), site_name(selected_site)]
			+ " " + UiTip.for_input(tr("Or drag it onto any of your nodes."), tr("Or pick it up and move it onto any of your nodes.")))
		card.disabled = selected_site == &"" or not c.grid.is_active_node(selected_site)
		var index := i
		card.pressed.connect(func() -> void: deploy_asset(index, selected_site))
		# ANIM-4: or drag it onto a node (the map or YOUR NODES); the pad picks it up.
		drops.add_source(card, {"kind": "asset", "index": index, "asset": aid, "prefer": selected_site})
		cards.add_child(card)
	if c.armory.is_empty():
		var empty := _para(tr("Armory empty: runs bank assets from their drops."))
		empty.custom_minimum_size.x = RAID_SIDE_WIDTH * 0.5  # W8b: it wraps (at 2.0 one line was 1373 px)
		cards.add_child(empty)
	_set_panel(outer, "raid")
	if raid_legend.foldable():
		set_page_prompts(prompts_for("raid") + [[&"cycle_target", "Key"]])  # ANIM-R2 R13: as the Grid
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, Vector2(0.36, 0.42))
	city_overlay.selected_id = selected_site
	city_overlay.node_clicked.connect(func(id: StringName) -> void:
		if RunManager.campaign.grid.is_claimed(id):
			select_target(id))
	_raid_avoid = [side, loadout]
	city_overlay.avoid_controls([side, loadout, raid_legend])  # labels clear of the panels and the key
	_register_raid_drops(claimed, loadout)
	place_raid_legend.call_deferred()
	# ANIM-R1 M2: the playout's zoomed map baked behind the setup (off the main thread), so
	# START DEFENSE opens onto a city that is already there.
	_prebake_playout.call_deferred(RunManager.campaign, null)
	spacer.resized.connect(place_raid_legend)
	raid_legend.minimum_size_changed.connect(_on_raid_legend_resized)
	if not wireframe.city.rebuilt.is_connected(place_raid_legend):
		wireframe.city.rebuilt.connect(place_raid_legend)
	if _last_warned_raid != String(pending.get("raid_id", "")):
		_last_warned_raid = String(pending.get("raid_id", ""))
		Dialogue.raid_warning(c.corporation_id, StringName(String(pending.get("raid_id", raid.id))), c.raids_won + c.raids_lost, "raid")


## Makes claimed node `site_id` the raid setup's target (map click, or its target button
## in the node orders for the pad and keyboard; H20).
func select_target(site_id: StringName) -> void:
	# ANIM-4: the target already picked stays as it is (no rebuild), so a press on its node
	# can go on into a drag of its assets.
	if panel_name == "raid" and site_id == selected_site and _panel != null:
		var same := _panel.find_child("Target_%s" % site_id, true, false) as Control
		if same != null:
			same.grab_focus.call_deferred()
		return
	selected_site = site_id
	if panel_name == "raid":
		wireframe.hold_camera()  # ANIM-5: the map holds still while the page rebuilds
	show_raid()
	var b := _panel.find_child("Target_%s" % site_id, true, false) as Control if _panel != null else null
	if b != null:
		b.grab_focus.call_deferred()


## The raid at a glance: the projected result as a stamp, then badges for home before and
## after, threats destroyed, strength, steps, the entry Sites and the link changes; the
## raid's warning in the tooltip.
func _raid_card(raid: RaidData, pending: Dictionary, projection: RaidResolver.RaidResult) -> TerminalWindow:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var corp_col := Palette.corp_color(c.corporation_id)
	var card := TerminalWindow.new(tr("RAID // %s") % TextDb.t(raid, "display_name"), corp_col)
	card.name = "RaidCard"
	card.tooltip_text = UiTip.fold(TextDb.t(raid, "warning_text"))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	card.body.add_child(row)
	# A forecast, not a result (H22 #9): "IF THE RAID RUNS NOW: HOME -5" on a dashed
	# ring like combat's NEXT plate; the tooltip says so. ANIM-R4 H3: the verdict names the
	# losses (RaidVerdict), ALL HOLD only when there are none.
	var verdict := raid_verdict(projection)
	var clean := RaidVerdict.clean_projection(projection)
	var stamp := ForecastStamp.new(FORECAST_CAPTION, verdict, RaidVerdict.color_of(clean), RaidVerdict.icon_of(clean))
	stamp.custom_minimum_size = Vector2(PROJECTION_STAMP, PROJECTION_STAMP) * (1.0 + (Settings.text_scale - 1.0) * PROJECTION_FOLLOW)
	stamp.tooltip_text = UiTip.fold(forecast_tip(projection))
	row.add_child(stamp)
	# W8b: at big text the facts are a two-column grid (a flow reported a four-row height).
	var facts: Container = HFlowContainer.new()
	if Settings.text_scale >= RAID_BIG_SCALE - 0.001:
		var fgrid := GridContainer.new()
		fgrid.columns = 2
		facts = fgrid
	facts.name = "RaidFacts"
	facts.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	facts.add_theme_constant_override("h_separation", 10)
	facts.add_theme_constant_override("v_separation", 4)
	row.add_child(facts)
	var home_col := RaidVerdict.color_of(projection.home_after >= projection.home_before)
	# H23 S5: every number says what it counts ("HOME 50 > 40", "STOPPED 0/2", "STRENGTH
	# +0%"), and its tooltip says what it means.
	var home_badge := Badge.new(tr("HOME %d → %d") % [projection.home_before, projection.home_after], home_col, GLYPH_HOME,
		tr("Your home server (CORE) now and after the raid: %d → %d integrity. At 0 the campaign is lost. Exact: the playout matches it.") % [projection.home_before, projection.home_after]).with_meter(projection.home_after, c.grid.home_max_integrity).with_icon(StatIcon.HOME)
	home_badge.name = "HomeForecast"
	facts.add_child(home_badge)
	var total := projection.threats_destroyed + projection.threats_reached_home + _still_active(projection)
	var stopped := Badge.new(tr("STOPPED %d/%d") % [projection.threats_destroyed, total], Palette.CELL_ACID, GLYPH_THREAT,
		tr("Threats your nodes destroy: %d of the %d that come. The rest reach your nodes or the home server.") % [projection.threats_destroyed, total])
	stopped.name = "ThreatsStopped"
	facts.add_child(stopped)
	var strength := Badge.new(tr("STRENGTH %s%%") % TextDb.signed(roundi(CampaignRules.raid_strength_pct(c, cfg, pending, RunManager.corporation))), corp_col, GLYPH_RULE,
		tr("How much stronger than normal the threats are (from Heat, ICE and seized Sites). 0% is normal strength."))
	strength.name = "RaidStrength"
	facts.add_child(strength)
	# Entry Sites: a badge each for a few, else one count (names in its tooltip); the
	# dashed routes on the map show them all.
	var entries := PackedStringArray()
	for e in CampaignRules.raid_entries(c, RunManager.corporation, pending):
		entries.append(site_name(e))
	if entries.size() <= MAX_ENTRY_BADGES:
		for entry in entries:
			facts.add_child(Badge.new(entry, corp_col, GLYPH_ENTRY, tr("Threats come in at %s (the dashed routes on the map).") % entry))
	else:
		facts.add_child(Badge.new(tr("%d ENTRY SITES") % entries.size(), corp_col, GLYPH_ENTRY, tr("Threats come into the city at %d Sites: %s. They follow the dashed routes on the map to your nodes.") % [entries.size(), ", ".join(entries)]))
	for e in projection.events:
		if e.get("type", "") in ["link_frozen", "link_altered"]:
			facts.add_child(Badge.new(tr("link"), Palette.RESIST_GOLD, GLYPH_LINK, String(e["text"])))
	return card


## The raid forecast in words: what happens if the raid runs now (H22 #9; ANIM-R4 H3: the
## one verdict, RaidVerdict, translated).
static func raid_verdict(projection: RaidResolver.RaidResult) -> String:
	return RaidVerdict.of_projection(projection)


## What a node's raid outcome word means (H23 S5).
static func outcome_tip(outcome: String) -> String:
	if outcome == "holds":
		return TranslationServer.translate("HOLDS: the node survives and keeps fighting.")
	if outcome == "":
		return ""
	return TranslationServer.translate("%s: the node falls; threats go on past it.") % outcome_word(outcome)


## A node's raid outcome as the screen writes it ("HOLDS", "BREACHED"), translated.
static func outcome_word(outcome: String) -> String:
	return TranslationServer.translate(outcome.to_upper()) if outcome != "" else "?"


## The forecast stamp's tooltip: a projection, exact, and how to change it.
func forecast_tip(projection: RaidResolver.RaidResult) -> String:
	var what := tr("your network holds every threat")
	if projection.campaign_lost:
		what = tr("the home server falls and the campaign is lost")
	elif not RaidVerdict.clean_projection(projection):
		# ANIM-R4 H3: the losses, in the verdict's words (a Disabled node with every threat
		# stopped is not "holds every threat").
		what = tr("it costs you %s") % raid_verdict(projection).replace("\n", ", ")
	return tr("Forecast, not a result: if you start the defence now, %s. The playout matches it exactly. The raid has not happened yet: deploy assets or pick other targets to change it.") % what


## The raid legend at the first spot over the map that covers no node's icon or label
## (H22 #9: pinned bottom left it covered CORE at 1.6). When every spot covers a node
## (threat routes cross the whole city), the camera frames the map beside the legend's
## column (moved, and zoomed out as far as that needs), then the legend is placed again.
func place_raid_legend() -> void:
	if raid_legend == null or not is_instance_valid(raid_legend) or city_overlay == null or not is_instance_valid(city_overlay):
		return
	# ANIM-5: measured with the camera rig at rest (a held frame may be on screen).
	if _raid_strip:
		wireframe.unrigged(func() -> bool:
			_place_raid_strip()
			return true)
	else:
		wireframe.unrigged(func() -> float: return LegendSpot.place(raid_legend, city_overlay))
	# H23 S14: the nodes must also sit inside the map's free part (they sat under the top
	# bar or the DEFENSE LOADOUT). Framing runs on the positions measured after the city
	# redrew (this runs on `rebuilt`), so each pass corrects the last; at most
	# RAID_REFRAMES_MAX passes.
	var free := raid_free_rect()
	var box: Rect2 = wireframe.unrigged(raid_node_box)
	if not free.has_area() or not box.has_area():
		return
	# ANIM-R1 M15: the whole page's framing is bounded, whatever its layouts do. A free
	# rect that kept changing reset the per-layout pass count, and a measure that never held
	# still asked for a check every frame: under some layouts and timings the framing never
	# ended (each pass a new camera, a new city build), the full suite hanging at 100% CPU.
	_raid_checks += 1
	if _raid_checks > RAID_CHECKS_MAX or _raid_passes >= RAID_PASSES_MAX:
		wireframe.ease_camera()
		return
	# Act only on a settled measure: the same free rect and node box for RAID_STABLE_FRAMES
	# frames in a row. The icons follow the camera a redraw or two late (and jump again when
	# the city's new stretch is baked), and the page's layout settles over a few frames;
	# acting on a passing measure moved the camera twice as far.
	if not free.is_equal_approx(_raid_free) or not box.is_equal_approx(_raid_box):
		if not free.is_equal_approx(_raid_free):
			_raid_reframes = 0  # a new layout: its own passes
		_raid_free = free
		_raid_box = box
		_raid_same = 0
	elif Engine.get_process_frames() != _raid_frame:
		_raid_same += 1  # once a frame, however often the city redraws in it
	_raid_frame = Engine.get_process_frames()
	if _raid_reframes >= RAID_REFRAMES_MAX or (free.encloses(box) and _raid_same >= RAID_STABLE_FRAMES):
		wireframe.ease_camera()  # ANIM-5: settled: the held picture eases to it
		return
	if _raid_same < RAID_STABLE_FRAMES:
		if not get_tree().process_frame.is_connected(place_raid_legend):
			get_tree().process_frame.connect(place_raid_legend, CONNECT_ONE_SHOT)
		return
	if free.encloses(box):
		wireframe.ease_camera()
		return
	var city := wireframe.city
	var screen := get_global_rect()
	var k := 1.0
	if box.size.x > free.size.x or box.size.y > free.size.y:
		# W8b: aimed RAID_AIM_INSET inside the free part, so icons floating up to clear each other
		# as the map zooms out still land inside it.
		var aim := (free.size - Vector2.ONE * RAID_AIM_INSET * 2.0).max(Vector2.ONE)
		k = minf(1.0, minf(aim.x / box.size.x, aim.y / box.size.y) * RAID_FIT_SHARE)
	# H24 S5: nodes that cannot fit beside the key's column even at the zoom floor (a late
	# campaign at text scale 1.6: the column took 368 px and the icons sat under it) get the
	# strip key along the map's foot instead, as the Grid has.
	if not _raid_strip and raid_legend.is_visible_in_tree() and city.scale.x * k < raid_min_zoom() * RAID_STRIP_BELOW:
		_use_raid_strip()
		return
	_raid_reframes += 1
	_raid_passes += 1
	# Never further out than RAID_MIN_ZOOM (a far camera bakes a huge stretch of city).
	var floor_zoom := raid_min_zoom()
	k = clampf(k, floor_zoom / maxf(floor_zoom, city.scale.x), 1.0)
	var anchor := city.focus_anchor
	if k < 1.0:
		# Zooming by k about the focus point moves the box centre to focus + (from - focus)
		# * k; the focus goes where that puts the centre on the free rect's centre.
		var focus_at := screen.position + city.focus_anchor * screen.size
		anchor = (free.get_center() - (box.get_center() - focus_at) * k - screen.position) / screen.size
		_raid_step = {}
	else:
		# A move only: how far the box went for the last move (per axis) sets this one's
		# size, so the measured response, not the planned one, steers the camera.
		var want := free.get_center() - box.get_center()
		var gain := Vector2.ONE
		if not _raid_step.is_empty():
			var moved: Vector2 = box.get_center() - Vector2(_raid_step["centre"])
			var stepped: Vector2 = _raid_step["step"]
			for axis in 2:
				if absf(stepped[axis]) > 1.0 and absf(moved[axis]) > 1.0:
					gain[axis] = clampf(stepped[axis] / moved[axis], RAID_GAIN_MIN, RAID_GAIN_MAX)
		var step := want * gain
		anchor = city.focus_anchor + step / screen.size
		_raid_step = {"centre": box.get_center(), "step": step}
	_raid_same = 0
	_raid_box = Rect2()
	_frame_city(city.scale.x * k, city.focus_grid, anchor)
	if not get_tree().process_frame.is_connected(place_raid_legend):
		get_tree().process_frame.connect(place_raid_legend, CONNECT_ONE_SHOT)


## Share of the free rect the raid's nodes are framed into (a margin round them), and the
## furthest the raid map zooms out (H24 S5: 0.6 left a late campaign's nodes outside the
## map at text scale 1.6).
const RAID_FIT_SHARE := 0.9
const RAID_MIN_ZOOM := 0.36
## W8b: at big text (RAID_BIG_SCALE up) the map's area is short: its floor goes lower.
const RAID_MIN_ZOOM_BIG := 0.2
const RAID_BIG_SCALE := 1.3
## W8b: from this text scale START DEFENSE heads the map column.
const RAID_HUGE_SCALE := 1.8


## The furthest the raid map zooms out at the current text size.
func raid_min_zoom() -> float:
	return RAID_MIN_ZOOM_BIG if Settings.text_scale >= RAID_BIG_SCALE - 0.001 else RAID_MIN_ZOOM

## W8b: how far inside the free part the raid map is aimed (px).
const RAID_AIM_INSET := 16.0
## The column key gives way to the strip when the nodes would need a zoom under this share
## of RAID_MIN_ZOOM to fit beside it (1: as soon as the floor would be passed).
const RAID_STRIP_BELOW := 1.0
## The raid key is a strip along the map's foot (H24 S5), the layout it was chosen for
## (`raid_layout_key`), and the panels the map's labels keep clear of.
var _raid_strip: bool = false
var _raid_strip_key: String = ""
var _raid_avoid: Array[Control] = []
## W8b: the loadout lying along the map's foot at big text (null: under the map).
var _raid_foot: Control = null
## Bounds of a camera move's measured gain (anchor px per px the nodes moved).
const RAID_GAIN_MIN := 0.25
const RAID_GAIN_MAX := 4.0
## The free rect the passes were counted for, and the last move ({centre, step}).
var _raid_free: Rect2 = Rect2()
var _raid_step: Dictionary = {}
## The last node box measured and for how many frames in a row it (and the free rect) held.
var _raid_box: Rect2 = Rect2()
var _raid_same: int = 0
var _raid_frame: int = -1
## Frames a measure must hold before the camera acts on it.
const RAID_STABLE_FRAMES := 2
## ANIM-R1 M15: bounds on one raid page's framing, whatever its layouts do: the camera
## moves (over every layout the page goes through) and the checks (frames and redraws the
## framing looks at the map). Past either, the frame it has is the frame it keeps.
const RAID_PASSES_MAX := RAID_REFRAMES_MAX * 3
const RAID_CHECKS_MAX := 240
var _raid_passes: int = 0
var _raid_checks: int = 0


## The part of the raid map's area the nodes should sit in (screen px): the area less its
## margin and less the legend's column (the legend's side of the area).
func raid_free_rect() -> Rect2:
	var area_ctl := raid_legend.get_parent() as Control if raid_legend != null and is_instance_valid(raid_legend) else null
	if area_ctl == null:
		return Rect2()
	# The area as far as it is on screen (a page taller than the screen scrolls).
	var area := area_ctl.get_global_rect().intersection(get_global_rect()).grow(-LegendSpot.MARGIN)
	if _raid_foot != null and is_instance_valid(_raid_foot) and _raid_foot.is_visible_in_tree():
		area.size.y = maxf(0.0, minf(area.end.y, _raid_foot.get_global_rect().position.y - LegendSpot.MARGIN) - area.position.y)
	if not raid_legend.is_visible_in_tree():
		return area
	if _raid_strip:
		# The strip along the area's foot: the nodes sit above it.
		var top := raid_legend.get_global_rect().position.y - LegendSpot.MARGIN
		return Rect2(area.position, Vector2(area.size.x, maxf(0.0, top - area.position.y)))
	# The legend's column at the area's left (LegendSpot tries it first, so the legend lands
	# there once the nodes leave it).
	var left := area.position.x + raid_legend.get_combined_minimum_size().x * raid_legend.scale.x + LegendSpot.MARGIN
	return Rect2(left, area.position.y, maxf(0.0, area.end.x - left), area.size.y)


## The screen box round the raid map's node icons and tier pips (empty when none).
func raid_node_box() -> Rect2:
	var rects := LegendSpot.node_rects(city_overlay, false)
	if rects.is_empty():
		return Rect2()
	var box := rects[0]
	for r in rects:
		box = box.merge(r)
	return box


## Screen rects of the raid map's node icons and labels (the legend must cover none).
func raid_node_rects() -> Array[Rect2]:
	return LegendSpot.node_rects(city_overlay)


## Whether the raid key is the strip along the map's foot now (H24 S5).
func raid_legend_is_strip() -> bool:
	return _raid_strip


## The layout a strip key was chosen for: the text size, the screen and the raid map's
## nodes (a redraw of the same setup keeps the strip; a new layout tries the column again).
func raid_layout_key() -> String:
	var n := 0
	if RunManager.campaign != null:
		n = RunManager.campaign.grid.claimed_ids().size()
	return "%.2f|%s|%d|%s" % [Settings.text_scale, size, n, RunManager.campaign.corporation_id if RunManager.campaign != null else &""]


## Swaps the raid's column key for the strip key along the map's foot (H24 S5) and frames
## the map again above it.
func _use_raid_strip() -> void:
	if raid_legend == null or not is_instance_valid(raid_legend):
		return
	var area := raid_legend.get_parent() as Control
	var keys := raid_legend.only.duplicate()
	area.remove_child(raid_legend)
	raid_legend.queue_free()
	_raid_strip = true
	_raid_strip_key = raid_layout_key()
	raid_legend = MapLegend.pin_to(area, RunManager.campaign.corporation_id, true).show_only(keys)
	raid_legend.minimum_size_changed.disconnect(raid_legend._repin)
	raid_legend.minimum_size_changed.connect(_on_raid_legend_resized)
	raid_legend.fold_changed.connect(_place_raid_strip)
	TextDb.translates_itself(raid_legend)  # its row words are keys
	var avoid: Array[Control] = []
	for ctl in _raid_avoid:
		if is_instance_valid(ctl):
			avoid.append(ctl)
	avoid.append(raid_legend)
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.avoid_controls(avoid)
	_raid_reframes = 0
	_raid_free = Rect2()
	_raid_box = Rect2()
	_raid_same = 0
	_raid_step = {}
	place_raid_legend.call_deferred()


## The strip key along the foot of the raid map's area (on screen), as wide as the area.
func _place_raid_strip() -> void:
	var area_ctl := raid_legend.get_parent() as Control
	if area_ctl == null:
		return
	var shown := area_ctl.get_global_rect().intersection(get_global_rect())
	if shown.size.x <= LegendSpot.MARGIN * 2.0 or shown.size.y <= LegendSpot.MARGIN * 2.0:
		return
	raid_legend.set_strip_width(shown.size.x - LegendSpot.MARGIN * 2.0)
	var own := raid_legend.get_combined_minimum_size()
	raid_legend.set_anchors_preset(Control.PRESET_TOP_LEFT)
	raid_legend.scale = Vector2.ONE
	raid_legend.size = own
	var foot := shown.end.y
	if _raid_foot != null and is_instance_valid(_raid_foot) and _raid_foot.is_visible_in_tree():
		foot = minf(foot, _raid_foot.get_global_rect().position.y)  # W8b: above the loadout
	var bottom := foot - area_ctl.global_position.y
	raid_legend.position = Vector2(LegendSpot.MARGIN, maxf(LegendSpot.MARGIN, bottom - own.y - LegendSpot.MARGIN))


func _on_raid_legend_resized() -> void:
	place_raid_legend.call_deferred()


## How to deploy (H22 #9): numbered steps with the map's node icon and the Armory icon.
func _deploy_steps() -> VBoxContainer:
	var steps := VBoxContainer.new()
	steps.name = "DeploySteps"
	steps.add_theme_constant_override("separation", 6)
	steps.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var side := UiTheme.BASE_SIZE * Settings.text_scale * IconMark.SIZE_FACTOR * DEPLOY_ICON_GROW
	var target := site_name(selected_site) if selected_site != &"" else "?"
	for step in [[StatIcon.MAP, tr("1  Pick a node"), UiTip.for_input(tr("Pick the target: click a node of yours on the map, or its button in YOUR NODES."), tr("Pick the target: press a node of yours on the map, or its button in YOUR NODES."))],
			[StatIcon.ARMORY, tr("2  Press a card"), tr("Press an asset card: it deploys to the target (%s now).") % target]]:
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 6)
		row.tooltip_text = UiTip.fold(String(step[2]))
		row.mouse_filter = Control.MOUSE_FILTER_PASS
		row.add_child(IconMark.standalone(step[0], side, Palette.CELL_ACID))
		# W8b (§5.3): at big text a step is its number and icon (its words in the tooltip), so the
		# three defence cards keep one row beside it.
		var words := String(step[1]) if Settings.text_scale < STEP_ICONS_SCALE - 0.001 else String(step[1]).substr(0, 1)
		var l := _label(words)
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(l)
		steps.add_child(row)
	var to := _label("> %s" % target)
	to.name = "DeployTarget"
	to.add_theme_color_override("font_color", Palette.CELL_ACID)
	steps.add_child(to)
	return steps


## One claimed node in the raid orders: its target button (name, node type) and its
## projected outcome and assets as badges; the target's row also carries the withdraw and
## move buttons for its assets.
func _node_order_row(site_id: StringName, projection: RaidResolver.RaidResult, claimed: Array[StringName]) -> Control:
	var c := RunManager.campaign
	var n: Dictionary = projection.nodes.get(String(site_id), {})
	var holds := String(n.get("outcome", "")) == "holds"
	var box := VBoxContainer.new()
	box.name = "Order_%s" % site_id
	var row := HFlowContainer.new()
	row.add_theme_constant_override("h_separation", 8)
	box.add_child(row)
	var picked := site_id == selected_site
	var target := _button(("> %s" if picked else "%s") % site_name(site_id), func() -> void: select_target(site_id))
	target.name = "Target_%s" % site_id
	target.custom_minimum_size.x = TARGET_BUTTON_WIDTH
	target.alignment = HORIZONTAL_ALIGNMENT_LEFT
	if picked:
		target.add_theme_color_override("font_color", Palette.CELL_ACID)
	target.disabled = not c.grid.is_active_node(site_id)
	_add_tip(row, target, tr("%s (%s): make it the target for the Armory's assets.") % [site_name(site_id), _display(c.grid.node_type_of(site_id))])
	if not n.is_empty():
		# H23 S5: the numbers are the node's integrity (HP); HOLDS / BREACHED said in the tip.
		row.add_child(Badge.new(tr("HP %s → %s %s") % [n.get("before", "?"), n.get("after", "?"), outcome_word(String(n.get("outcome", "")))],
			RaidVerdict.color_of(holds), GLYPH_NODE, tr("%s's integrity (HP) now and after the raid: %s → %s. %s") % [site_name(site_id), n.get("before", "?"), n.get("after", "?"), outcome_tip(String(n.get("outcome", "")))]))
	var assets := c.grid.assets_on(site_id)
	for i in assets.size():
		var badge := Badge.new("", Palette.CELL_PINK, "", _display(assets[i]), assets[i])
		badge.name = "Placed_%s_%d" % [site_id, i]
		row.add_child(badge)
		# ANIM-4: a placed asset drags off its node: onto another node (moves it) or the
		# DEFENSE LOADOUT (back to the Armory), as its buttons below do.
		drops.add_source(badge, _placed_payload(site_id, i, assets[i]))
	if picked:
		var moves := HFlowContainer.new()
		moves.name = "Moves"
		moves.add_theme_constant_override("h_separation", 6)
		box.add_child(moves)
		for i in assets.size():
			var idx := i
			var withdraw := _button(tr("Withdraw %s") % _display(assets[i]), func() -> void: move_asset(site_id, idx, &""))
			_add_tip(moves, withdraw, tr("Back to the Armory."))
			# ANIM-4: the pick-up key on an asset's button carries that asset.
			drops.add_source(withdraw, _placed_payload(site_id, i, assets[i]))
			for other in claimed:
				if other != site_id and c.grid.is_active_node(other):
					var oid := other
					var move := _button("%s > %s" % [_display(assets[i]), site_name(other)], func() -> void: move_asset(site_id, idx, oid))
					_add_tip(moves, move, tr("Move it to %s.") % site_name(other))
					drops.add_source(move, _placed_payload(site_id, i, assets[i]))
	return box


## ANIM-4: the drag payload of asset `index` (id `asset_id`) deployed on `site_id`.
func _placed_payload(site_id: StringName, index: int, asset_id: StringName) -> Dictionary:
	return {"kind": "placed", "site": site_id, "index": index, "asset": asset_id, "prefer": site_id}
## The raid's part of the Grid as an overlay graph: claimed nodes (coloured by `results`
## outcome, with their assets), the Sites on the threat routes, links among them.
## `c` draws another campaign state than the current one (ANIM-5: the playout starts from
## the Grid as it stood before the raid); `include` keeps more Sites on the map (the
## pre-raid network after the raid, so a Seized node keeps its stamp).
func raid_graph(results: Variant, markers: Dictionary, c: CampaignState = null, include: Array = []) -> Dictionary:
	if c == null:
		c = RunManager.campaign
	var g := CityLayout.grid_graph(c, RunManager.corporation, CityLayout.threat_paths(c, RunManager.corporation), selected_site)
	var nodes_res: Dictionary = results.nodes if results is RaidResolver.RaidResult else results
	var network := {}
	for id in c.grid.claimed_ids():
		network[id] = true
	for path in CityLayout.threat_paths(c, RunManager.corporation):
		for id in path:
			network[id] = true
	for id in markers:
		network[id] = true
	for id in include:
		network[id] = true
	var nodes: Array[Dictionary] = []
	for n in g["nodes"]:
		if not network.has(n["id"]):
			continue
		var res: Dictionary = nodes_res.get(String(n["id"]), {})
		if not res.is_empty():
			n["color"] = RaidVerdict.color_of(String(res["outcome"]) == "holds")
			n["result"] = "%s → %s %s" % [res["before"], res["after"], outcome_word(String(res["outcome"]))]
			n["label"] = site_name(n["id"])  # never the raw id (H20)
			# H23 S5: the tag's numbers and word explained on hover.
			n["tip"] = tr("%s: integrity (HP) %s → %s in the raid. %s") % [site_name(n["id"]), res["before"], res["after"], outcome_tip(String(res["outcome"]))]
		n["assets"] = c.grid.assets_on(n["id"])
		# W8b: a raid map shows no run-difficulty pips (a raid is not a run; the pips stacked the
		# crowded raid map taller than its area at big text).
		n["tier"] = 0
		n["threat_corp"] = String(c.corporation_id)
		nodes.append(n)
	var edges: Array[Dictionary] = []
	for e in g["edges"]:
		if network.has(e["a"]) and network.has(e["b"]):
			edges.append(e)
	return {"nodes": nodes, "edges": edges}


## Codex (GDD 8.1): everything the Cell knows, zine-styled, plus the lexicon.
func show_codex() -> void:
	var box := VBoxContainer.new()
	box.add_child(GraffitiTag.new(tr("CODEX")))
	var entries := Codex.entries(RunManager.lookup(), RunManager.profile)
	var tabs := HFlowContainer.new()
	box.add_child(tabs)
	var body := ZineNote.new("", Vector2(900, 380)).make_reference()
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for section in entries:
		var name: String = section
		tabs.add_child(_button(tr(name), func() -> void: _fill_codex(body, name, entries[name])))
	box.add_child(body)
	_fill_codex(body, "Slices", entries["Slices"])
	if not Dialogue.history.is_empty():
		var lines := ZineNote.new(tr("LINES HEARD"), Vector2(900, 100)).make_reference()
		for h in Dialogue.history.slice(maxi(0, Dialogue.history.size() - 6)):
			lines.append("[%s] %s" % [Dialogue.speaker_name(int(h["speaker"]), StringName(String(h.get("corporation", "")))), h["text"]])
		box.add_child(lines)
	box.add_child(_icon(_button(tr("Back to HQ"), show_hq if RunManager.campaign != null else show_start), StatIcon.BACK))
	_set_panel(box, "codex")


func _fill_codex(body: ZineNote, section: String, items: Array) -> void:
	body.clear()
	body.append("[b]%s[/b]" % tr(section).to_upper())
	for item in items:
		body.append("[b]%s[/b] - %s" % [item["title"], String(item["text"]).replace("\n", " / ")])


## Raid playout (GDD 7.2, 9.3): threat markers animate over the Grid; 1x/2x/4x and skip.
## Instant (straight to the summary) when headless or under reduce-effects.
func show_raid_playout(events: Array[Dictionary], before: CampaignState = null) -> void:
	var c := RunManager.campaign
	# The raid live on the city, the camera zoomed in on the fight and following it; the
	# RAID FEED at the side.
	var box := HBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(spacer)
	# Art pass W9F (§6.10: legends fold to MAP KEY above 1.3): at 2.0 the open key covered
	# the playout's verdict stamp.
	var legend := MapLegend.pin_to(spacer, c.corporation_id, Settings.text_scale >= MapLegend.FOLD_SCALE - 0.001)
	_fight_area = [spacer, legend]
	var side := VBoxContainer.new()
	side.add_theme_constant_override("separation", 12)
	box.add_child(side)
	# ANIM-5: the setup's forecast rides along and resolves into the real verdict at the end
	# (the same words: the forecast is exact).
	var r := c.last_raid
	# ANIM-R4 H3: the one verdict (RaidVerdict), the same words as the setup's forecast.
	var verdict := RaidVerdict.of_result(r)
	var clean := RaidVerdict.clean(r)
	var forecast := ForecastStamp.new(LIVE_CAPTION, verdict, RaidVerdict.color_of(clean), RaidVerdict.icon_of(clean))
	forecast.name = "PlayoutForecast"
	forecast.custom_minimum_size = Vector2(PROJECTION_STAMP, PROJECTION_STAMP) * (1.0 + (Settings.text_scale - 1.0) * PROJECTION_FOLLOW)
	forecast.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	side.add_child(forecast)
	var feed := TerminalWindow.new(tr("RAID FEED // LIVE"), Palette.corp_color(c.corporation_id))
	side.add_child(feed)
	var cont := _button(tr("Continue"), _after_playout)
	cont.name = "PlayoutContinue"
	# W8b (§6 Disabled, critique 25): while the raid plays Continue is the theme's locked
	# state (DISABLED outline, a lock, the label 4.5:1), never a faded primary.
	cont.theme_type_variation = UiTheme.PRIMARY
	cont.disabled = true
	cont.tooltip_text = UiTip.fold(tr("Skip"))
	_set_panel(box, "raid_playout")
	# The map as it stood before the raid (Seized nodes still yours until they flip).
	var pre := before if before != null else c
	var kept: Array = pre.grid.claimed_ids()
	var g := raid_graph({}, {}, pre)
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, PLAYOUT_ANCHOR, PLAYOUT_ZOOM)
	city_overlay.avoid_controls([side])
	var overlay := city_overlay
	playout = RaidPlayoutPanel.new(overlay, PLAYOUT_LOG_SIZE)
	feed.body.add_child(playout)
	var fx := playout.attach_fx(r, c.grid.home_site_id, c.grid.home_max_integrity, Palette.corp_color(c.corporation_id))
	# ANIM-R1 M4: each step's fight is framed (the camera eases to it) before it plays, and
	# every hit on home flies its number into the top bar's HOME, which rolls down.
	playout.framer = _frame_fight.bind(overlay)
	playout.event_shown.connect(_on_raid_event_shown)
	if fx != null and Motion.animating():
		hud_home_shown = int(r.get("home_before", c.grid.home_integrity))
		_refresh_status()
		fx.home_hit_shown.connect(_fly_home_number)
	playout.finished.connect(func() -> void:
		cont.disabled = false
		hud_home_shown = -1
		hud_heat_shown = -1
		hud_raids_shown = -1
		_refresh_status()
		forecast.resolve(RESULT_CAPTION, verdict)
		# W8b (§11 Raid): the end frames the verdict banner and home, not the last fight.
		_frame_fight([RunManager.campaign.grid.home_site_id], overlay)
		# The result's tint spreads from the nodes that flipped (NeonCity, one bake).
		wireframe.city.release_influence()
		if is_instance_valid(overlay):
			var done := raid_graph(RunManager.campaign.last_raid.get("nodes", {}), overlay.markers, null, kept)
			overlay.set_graph(done["nodes"], done["edges"]))
	# Skip jumps straight to the summary (ANIM-5).
	playout.skipped.connect(_after_playout)
	side.add_child(cont)
	var instant := not Motion.animating()
	playout.play(events, instant)
	if instant:
		_after_playout()


## ANIM-R1 M2: bakes (ahead, off the main thread) the stretch of city the raid playout's
## camera can show for campaign `c`'s raid map: every node of it as the fight's focus at
## PLAYOUT_ZOOM, under influence `inf` (null: the city's current one).
func _prebake_playout(c: CampaignState, inf: Variant) -> void:
	if c == null or not is_inside_tree() or wireframe == null:
		return
	var nodes: Array = raid_graph({}, {}, c)["nodes"]
	var view := size / PLAYOUT_MIN_ZOOM
	var region := Rect2()
	var first := true
	for n: Dictionary in nodes:
		var at: Vector2 = n["at"]
		var w := NeonCity.world_of(at.x + 0.5, at.y + 0.5)
		var r := Rect2(w - PLAYOUT_ANCHOR * view, view)
		region = r if first else region.merge(r)
		first = false
	if not first:
		wireframe.city.prebake(region.grow(NeonCity.REGION_MARGIN), inf)


## The raid playout's camera: zoom and where its focus sits on screen.
const PLAYOUT_ZOOM := 1.9
## ANIM-R2 R6: the RAID FEED log (it was 330x330, half the window beside the map).
const PLAYOUT_LOG_SIZE := RaidPlayoutPanel.LOG_SIZE
const PLAYOUT_ANCHOR := Vector2(0.36, 0.55)
## ANIM-R1 M4: the furthest out a framed fight goes (its guns and targets must all show).
const PLAYOUT_MIN_ZOOM := 1.2


## ANIM-R1 M4: frames a raid step's fight (`sites`: the guns firing and their targets, else
## the nodes hit, else where threats move or enter) at PLAYOUT_ZOOM, easing the camera there
## (it never cuts); returns the seconds the ease takes (the step's beats wait for it), 0
## when the frame does not change.
func _frame_fight(sites: Array[StringName], overlay: CityMapOverlay) -> float:
	if not is_instance_valid(overlay) or overlay != city_overlay or sites.is_empty():
		return 0.0
	var pts := PackedVector2Array()
	for id in sites:
		pts.append(Vector2(overlay.lot_of(id)) + Vector2(0.5, 0.5))
	return wireframe.frame_points(pts, fight_area(_fight_area), PLAYOUT_ZOOM, PLAYOUT_MIN_ZOOM)


## The playout map's parts the fight frame keeps to: [the map's area, its key].
var _fight_area: Array = []


## ANIM-R1 M4: the free part of a playout map (screen px): its area right of its key's
## column (the key sits at the area's left), less a margin.
static func fight_area(parts: Array) -> Rect2:
	if parts.is_empty() or not is_instance_valid(parts[0]):
		return Rect2()
	var area := (parts[0] as Control).get_global_rect()
	if parts.size() > 1 and is_instance_valid(parts[1]) and (parts[1] as Control).is_visible_in_tree():
		var key := (parts[1] as Control).get_global_rect()
		var right := minf(area.end.x, key.end.x)
		area = Rect2(Vector2(right, area.position.y), Vector2(area.end.x - right, area.size.y))
	return area.grow(-LegendSpot.MARGIN * 2.0)


## ANIM-R1 M4: the top bar's HOME during a raid's playout: the value the hits shown so far
## leave (-1: the campaign's own).
var hud_home_shown: int = -1
## ANIM-R4 H11a: the top bar's HEAT and RAIDS during a raid's playout: what the feed has told
## so far (-1: the campaign's own). They change with the line that changes them: Heat with
## its "Heat +5 for the lost raid: 1 → 6." line, RAIDS going down with the raid's end line
## and up with a threshold's line that queues a raid.
var hud_heat_shown: int = -1
var hud_raids_shown: int = -1


## ANIM-R4 H11a: a raid event the feed has just told (RaidPlayoutPanel.event_shown).
func _on_raid_event_shown(e: Dictionary) -> void:
	match String(e.get("type", "")):
		"heat":
			if hud_heat_shown >= 0 and e.has("after"):
				hud_heat_shown = int(e["after"])
		"raid_end":
			if hud_raids_shown >= 0:
				hud_raids_shown = maxi(0, hud_raids_shown - 1)
		"heat_threshold":
			if hud_raids_shown >= 0 and _threshold_raids(int(e.get("heat", 0))):
				hud_raids_shown += 1
		_:
			return
	_refresh_status()


## Whether the Heat threshold at `at` queues a raid.
static func _threshold_raids(at: int) -> bool:
	for t in RunManager.config().heat_thresholds:
		if t != null and t.heat == at:
			return t.event_raid != null
	return false


## ANIM-R1 M4: a hit on home: its red number flies from the node on the map into the top
## bar's HOME (`home_number_fly`), which then shows the lower value (the tag bumps and rolls).
func _fly_home_number(damage: int, site: StringName) -> void:
	var land := func(total: int = damage) -> void:
		if hud_home_shown >= 0:
			hud_home_shown = maxi(0, hud_home_shown - total)
			_refresh_status()
	var to := hud.stats.icon_point(StatIcon.HOME)
	if not Motion.live(&"home_number_fly") or city_overlay == null or not is_instance_valid(city_overlay) or to == Vector2.INF:
		land.call()
		return
	var p := city_overlay.icon_at(site)
	if p.x == INF:
		land.call()
		return
	var from := city_overlay.get_global_transform() * p
	# W8b (lint, 2.0): hits that land together (a skipped playout finishes every step at
	# once) fly as one number with their sum, never two numbers stacked on the map.
	for other in find_children("HomeHitNumber", "Label", false, false):
		var flying := other as Label
		if flying.is_queued_for_deletion():
			continue
		var sum := int(flying.get_meta(&"damage", 0)) + damage
		flying.set_meta(&"damage", sum)
		flying.text = "-%d" % sum
		flying.size = flying.get_combined_minimum_size()
		flying.pivot_offset = flying.size * 0.5
		return
	var num := Label.new()
	num.name = "HomeHitNumber"
	num.set_meta(&"damage", damage)
	num.top_level = true
	num.mouse_filter = Control.MOUSE_FILTER_IGNORE
	num.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	num.text = "-%d" % damage
	num.add_theme_font_override("font", Palette.display())
	num.ready.connect(UiTheme.track_label.bind(num))  # art pass W9F (§4.2)
	num.add_theme_font_size_override("font_size", roundi(HOME_NUMBER_FONT * Settings.text_scale))
	num.add_theme_color_override("font_color", Palette.CELL_PINK)
	num.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	num.add_theme_constant_override("outline_size", 6)
	num.z_index = 60
	add_child(num)
	num.size = num.get_combined_minimum_size()
	num.pivot_offset = num.size * 0.5
	num.global_position = from - num.size * 0.5
	num.scale = Vector2.ONE * Motion.amplitude(&"home_number_fly")
	var e := Motion.entry(&"home_number_fly")
	var tw := num.create_tween().set_parallel(true)
	tw.tween_property(num, "global_position", to - num.size * 0.5, Motion.seconds(&"home_number_fly")).set_delay(Motion.delay_of(&"home_number_fly")).set_ease(e.ease).set_trans(e.trans)
	tw.tween_property(num, "scale", Vector2.ONE, Motion.seconds(&"home_number_fly")).set_delay(Motion.delay_of(&"home_number_fly")).set_ease(e.ease).set_trans(e.trans)
	tw.chain().tween_callback(func() -> void:
		land.call(int(num.get_meta(&"damage", damage)))
		num.queue_free())


## The flying home-hit number's lettering at text scale 1.0 (px).
const HOME_NUMBER_FONT := 30


func _after_playout() -> void:
	hud_home_shown = -1
	hud_heat_shown = -1
	hud_raids_shown = -1
	for n in find_children("HomeHitNumber", "Label", false, false):
		n.queue_free()
	wireframe.city.release_influence()
	if RunManager.campaign.is_over():
		show_end()
	else:
		show_raid_summary()


func show_raid_summary() -> void:
	var c := RunManager.campaign
	var r := c.last_raid
	var outer := HBoxContainer.new()
	outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var table := Control.new()
	table.name = "WarTable"
	table.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	table.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# ANIM-R4 H3: the report's stamp is the raid's one verdict, as the playout's stamp
	# resolved (it said BREACHED for a raid home never felt, beside HOLDS rows).
	var clean := RaidVerdict.clean(r)
	var stamp := ForecastStamp.new(RESULT_CAPTION, RaidVerdict.of_result(r), RaidVerdict.color_of(clean), RaidVerdict.icon_of(clean))
	stamp.name = "RaidVerdict"
	stamp.resolved = true
	stamp.custom_minimum_size = Vector2(150, 150)
	stamp.size = stamp.custom_minimum_size
	stamp.position = Vector2(20, 16)
	stamp.rotation_degrees = -8.0
	table.add_child(stamp)
	outer.add_child(table)
	MapLegend.pin_to(table, c.corporation_id, Settings.text_scale >= MapLegend.FOLD_SCALE - 0.001)  # art pass W9F (§6.10)
	var report := TerminalWindow.new(tr("RAID REPORT"), RaidVerdict.color_of(clean))
	report.custom_minimum_size.x = 340
	outer.add_child(report)
	var box := report.body
	# The result as badges (H20): home, threats, then each node's outcome by name.
	var facts := HFlowContainer.new()
	facts.name = "RaidResult"
	facts.add_theme_constant_override("h_separation", 10)
	facts.add_theme_constant_override("v_separation", 4)
	box.add_child(facts)
	facts.add_child(Badge.new("%d → %d" % [int(r.get("home_before", 0)), int(r.get("home_after", 0))], RaidVerdict.color_of(int(r.get("home_after", 0)) >= int(r.get("home_before", 0))), GLYPH_HOME,
		tr("Home integrity before and after the raid.")).with_meter(int(r.get("home_after", 0)), c.grid.home_max_integrity).with_icon(StatIcon.HOME))
	facts.add_child(Badge.new(tr("%d destroyed") % int(r.get("threats_destroyed", 0)), Palette.CELL_ACID, GLYPH_THREAT, tr("Threats your network destroyed.")))
	if int(r.get("threats_reached_home", 0)) > 0:
		facts.add_child(Badge.new(tr("%d reached home") % int(r.get("threats_reached_home", 0)), Palette.HARM, GLYPH_THREAT, tr("Threats that hit the home server.")))
	var ids: Array = r.get("nodes", {}).keys()
	ids.sort()
	for id in ids:
		var n: Dictionary = r["nodes"][id]
		var holds := String(n["outcome"]) == "holds"
		var node_row := HFlowContainer.new()
		node_row.add_child(_label(site_name(StringName(String(id)))))
		node_row.add_child(Badge.new("%d → %d %s" % [int(n["before"]), int(n["after"]), outcome_word(String(n["outcome"]))], RaidVerdict.color_of(holds), GLYPH_NODE,
			tr("Integrity before and after, and whether the node held.")).with_icon(RaidVerdict.outcome_icon(holds)))
		box.add_child(node_row)
	for key in ["seized", "disabled"]:
		for id in r.get(key, []):
			box.add_child(Badge.new("%s %s" % [site_name(StringName(String(id))), tr(key.to_upper())], Palette.RESIST_GOLD, GLYPH_RULE,
				tr("Seized: the corporation took the Site back.") if key == "seized" else tr("Disabled: repair the node on the Grid.")))
	box.add_child(_icon(_button(tr("Back to HQ"), show_hq), StatIcon.BACK))
	_set_panel(outer, "raid_summary")
	var g := raid_graph(r.get("nodes", {}), {})
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, Vector2(0.36, 0.55))
	city_overlay.avoid_controls([report])


func show_end() -> void:
	# Art pass W8d (ART_BIBLE §11 Campaign end, §8 T4, critique 62/63): the end staged over
	# the city as two templates (CampaignEndStage): WON = the corp's landmark falls and is
	# sprayed out, CORP DOWN, the crew wall; LOST = the Cell's hexagon cracks, the city greys,
	# CELL BURNED. The same words and records as before: the beats, the profile, the ICE
	# records (the receipt's tooltip keeps ice_records_text() whole), the two actions.
	var c := RunManager.campaign
	var won := c.outcome == CampaignState.Outcome.WON
	Dialogue.speak("win" if won else "loss", RC.Voice.DISPATCH, c.corporation_id, &"", c.campaign_seed)
	var corp := RunManager.corporation
	var beats: Array = []
	for b in CampaignRules.revealed_beats(c, corp):
		beats.append([TextDb.t(b, "title"), TextDb.t(b, "text")])
	var p := RunManager.profile
	var records := CampaignEndStage.records_of(p, RunManager.lookup(), RunManager.config().rebel_cell_unlock_ice, RunManager.ice_cap(c.corporation_id))
	var headline := (tr("CAMPAIGN WON - %s is down") % TextDb.t(corp.final_boss, "display_name")) if won else tr("CAMPAIGN LOST - home server destroyed")
	var stage := CampaignEndStage.new(won, c.corporation_id, TextDb.t(corp, "display_name"), headline, CrewWall.crew_of(c.roster), beats, records)
	stage.receipt.tooltip_text = UiTip.fold(ice_records_text())
	stage.foot_bar = pad_prompts
	# Art pass W9F: the LOST grey is the city's own flatline context (whole screen).
	if background != null and background.city != null:
		stage.atmosphere = background.city.atmosphere()
	var city := background.city.atmosphere() if background != null and background.city != null else null
	stage.new_button.text = tr("New campaign")
	stage.new_button.pressed.connect(func() -> void:
		if city != null:
			city.clear_campaign_progress()  # the next campaign starts from no lean (art pass W9F)
		RunManager.campaign = null
		show_start())
	_icon(stage.new_button, StatIcon.PLAY)
	stage.title_button.text = tr("Back to title")
	stage.title_button.pressed.connect(RunManager.go_to_title)
	_icon(stage.title_button, StatIcon.EXIT)
	if city != null:
		stage.lean_from = city.state.progress
		stage.city_lean.connect(func(f: float) -> void: city.set_campaign_progress(f, c.corporation_id))
	_set_panel(stage, "end")
	# Art pass W9F (W8d request): one scrim over the whole city behind every piece of the
	# screen (the top bar, the subtitle band and the prompt strip too), not the page's rect;
	# it goes with the stage.
	var end_scrim := GlassScrim.full_screen()
	end_scrim.name = "EndScrim"
	add_child(end_scrim)
	move_child(end_scrim, maxi(background.get_index(), wireframe.get_index()) + 1)
	stage.use_screen_scrim()
	stage.tree_exiting.connect(end_scrim.queue_free)
	# The city shows behind the stage (never a glass box over it).
	_panel_host.theme_type_variation = &""
	if entering:
		stage.play()
	else:
		stage.finish_now()


# --- Helpers ----------------------------------------------------------------------------------

## Frames the ANIM-5 demos wait for the page to settle, and the most they wait for the
## city's bake before playing anyway.
const DEMO_SETTLE_FRAMES := 20
const DEMO_BAKE_FRAMES := 240


## ANIM-5 frame capture (dev shortcut, a demo campaign in its own slot): once the page and
## the city's bake have settled, plays motion `id` and prints the frame it starts on
## ("anim5: <id> starts on frame N") for tools/design_lab/frame_strip.py.
func _demo_anim(id: String) -> void:
	var tune_script: GDScript = load("res://scripts/ui/netrun_scene.gd")
	tune_script.demo_tune(OS.get_cmdline_user_args())
	var c := RunManager.campaign
	if id == "heat_pulse":
		c.heat = 20
		show_hq()
	for f in DEMO_SETTLE_FRAMES:
		await get_tree().process_frame
	var city := (background.city if background.visible else wireframe.city)
	for f in DEMO_BAKE_FRAMES:
		if city.showing_current_look() and city.camera_settled() and city.bake_fade >= 1.0:
			break
		await get_tree().process_frame
	if id.begins_with("drag_"):
		await _demo_drag(id)
		return
	print("anim5: %s starts on frame %d" % [id, Engine.get_frames_drawn()])
	match id:
		"site_select":
			select_site(stepped_site(1))
		"raid_playout":
			fight_raid()
		"asset_drop":
			if not c.armory.is_empty():
				deploy_asset(0, selected_site)
		"heat_pulse":
			c.heat = 30
			show_hq()
		"jack_in":
			RunManager.scene_switching_enabled = true
			var sites := RunManager.launchable_sites()
			var living := c.living_operatives()
			if not sites.is_empty() and not living.is_empty():
				launch(sites[0].id, living[0].id)
		"influence_spread":
			# A second Site cleared and claimed (a demo campaign): the tint spreads from it once
			# its new look has baked.
			var corp := RunManager.corporation
			for sd in RunManager.launchable_sites():
				if not c.grid.is_claimed(sd.id):
					CampaignRules.on_run_completed(c, corp, RunManager.config(), _demo_run(sd.id))
					CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), sd.id, &"firewall_relay")
					break
			city.sync_influence()
			for f in DEMO_BAKE_FRAMES:
				if city.spreading():
					print("anim5: influence_spread spreads from frame %d" % Engine.get_frames_drawn())
					break
				await get_tree().process_frame


## ANIM-4 frame capture: frames a scripted pointer takes from the item to where it lets go,
## the frames it rests there first, the frames a page gets to lay out, and the arc of the
## pointer's path (px up at its middle).
const DEMO_DRAG_FRAMES := 18
const DEMO_DRAG_HOLD := 3
const DEMO_LAYOUT_FRAMES := 12
const DEMO_DRAG_ARC := 40.0
## Where the demo lets go: this far off the target's centre (px), at most this share of
## its size (so it stays inside).
const DEMO_RELEASE_OFFSET := Vector2(18, 12)
const DEMO_RELEASE_SHARE := 0.3


## ANIM-4 frame capture (a demo campaign in its own slot): picks an item up, carries it
## along a scripted pointer path and lets go: on a target that takes it (`drag_asset`,
## `drag_crew`, `drag_loadout`), on one that refuses it (`drag_asset_refuse`,
## `drag_crew_refuse`) or on nothing (`drag_crew_cancel`, `drag_loadout_cancel`). Prints
## "anim4: <id> starts on frame N" at the pick-up.
func _demo_drag(id: String) -> void:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var layer := drops
	var src: Control = null
	var target_id := ""
	var end := Vector2.INF
	if id.begins_with("drag_asset"):
		if id == "drag_asset_refuse":
			# The relay's second slot filled: the last asset has nowhere to go there.
			CampaignRules.deploy_asset(c, cfg, lookup, 0, selected_site)
		show_raid()
		for f in DEMO_LAYOUT_FRAMES:
			await get_tree().process_frame
		var cards := _panel.find_child("AssetCards", true, false)
		src = cards.get_child(cards.get_child_count() - 1) as Control
		target_id = "node:%s" % (selected_site if id == "drag_asset_refuse" else c.grid.home_site_id)
	elif id == "drag_crew_refuse":
		show_hq()
		for f in DEMO_LAYOUT_FRAMES:
			await get_tree().process_frame
		src = _panel.find_child("Crew_%s" % c.living_operatives()[0].id, true, false) as Control
		target_id = "station:%s" % c.grid.claimed_ids()[c.grid.claimed_ids().size() - 1]
	elif id.begins_with("drag_crew"):
		RunManager.scene_switching_enabled = false  # the capture holds on the drop, not the jack
		var sites := RunManager.launchable_sites()
		if not sites.is_empty():
			selected_site = sites[0].id
		show_grid()
		for f in DEMO_LAYOUT_FRAMES:
			await get_tree().process_frame
		src = _grid_chips[0] if not _grid_chips.is_empty() else null
		target_id = "jack"
		if id == "drag_crew_cancel":
			end = Vector2(size.x * 0.3, size.y * 0.45)
	elif id.begins_with("drag_loadout"):
		var op := c.living_operatives()[0]
		op.rank = 3
		open_loadout(op)
		var view := get_node("LoadoutView") as LoadoutView
		view.show_spinner()
		for f in DEMO_LAYOUT_FRAMES:
			await get_tree().process_frame
		layer = view.drops
		var options := CampaignRules.ring_segment_options(op, lookup.get_content(op.class_id) as ClassData)
		src = view.find_child("Swap_%s" % options[0], true, false) as Control if not options.is_empty() else null
		target_id = "ring:1"
		if id == "drag_loadout_cancel":
			end = (view._view as SpinnerView).window.get_global_rect().position + Vector2(40, 120)
	if src == null:
		print("anim4: %s has nothing to drag" % id)
		return
	var from := src.get_global_rect().get_center()
	layer.start_carry(src, false)
	layer.point_at(from)
	if end == Vector2.INF:
		# Let go a little off the target's centre (inside it), so the snap onto it shows.
		var r := layer.locate(layer.target(target_id))
		end = r.get_center() + DEMO_RELEASE_OFFSET.min(r.size * DEMO_RELEASE_SHARE)
	print("anim4: %s starts on frame %d" % [id, Engine.get_frames_drawn()])
	for i in DEMO_DRAG_FRAMES:
		await get_tree().process_frame
		var q := Tween.interpolate_value(0.0, 1.0, float(i + 1) / DEMO_DRAG_FRAMES, 1.0, Tween.TRANS_SINE, Tween.EASE_IN_OUT) as float
		layer.point_at(from.lerp(end, q) - Vector2(0, DEMO_DRAG_ARC * sin(PI * q)))
	for i in DEMO_DRAG_HOLD:
		await get_tree().process_frame
	print("anim4: %s lets go on frame %d" % [id, Engine.get_frames_drawn()])
	layer.release_at(end)


func _still_active(projection: RaidResolver.RaidResult) -> int:
	return projection.seized.size()


func _demo_run(site_id: StringName) -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	return r


func _exploit_names(c: CampaignState) -> String:
	var names := PackedStringArray()
	for e in c.exploits:
		names.append(exploit_name(e))
	return ", ".join(names) if not names.is_empty() else tr("none (%d needed for the breach)") % RunManager.config().min_exploits_for_breach


## An Exploit's name as the screens write it ("Intel"), translated.
static func exploit_name(type: int) -> String:
	return TranslationServer.translate(String(RC.ExploitType.keys()[type]).capitalize())


## The Armory's count as the HQ badge and the raid setup both write it ("ARMORY 3/6",
## H24 S14: the same words and meaning on both screens).
func armory_words() -> String:
	return tr("ARMORY %d/%d") % [RunManager.campaign.armory.size(), RunManager.config().armory_capacity]


## What the ARMORY count means (the HQ badge's and the raid setup's tooltip).
func armory_tip() -> String:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var what := tr("The Armory: defence assets banked from runs, deployed on your nodes in raid setup.") if not c.armory.is_empty() else tr("The Armory is empty: runs bank defence assets from their drops.")
	return tr("%s\nARMORY %d/%d: %d assets waiting in the Armory (not counting those deployed on your nodes) of the %d it holds.") % [what, c.armory.size(), cfg.armory_capacity, c.armory.size(), cfg.armory_capacity]


## The campaign's share code as a line (H24 S11: it read like debug output on the Pirate
## Radio note): the radio's tooltip and the Settings menu show it.
func campaign_code_line() -> String:
	return PauseMenu.code_line()


func _refresh_status() -> void:
	var c := RunManager.campaign
	if c == null:
		_status.text = tr("No campaign.")
		return
	var cfg := RunManager.config()
	_status.text = "Heat %d/%d | Schematics %d | Home %d/%d | Exploits %d | Raids pending %d | ICE %d | %s" % [
		c.heat, cfg.heat_max, c.schematics, c.grid.home_integrity, c.grid.home_max_integrity,
		c.exploits.size(), c.pending_raids.size(), c.ice_level, "campaign over" if c.is_over() else "active"]
	# H24 S3: the tags' names are keys (translated where drawn); the tooltips translated here.
	hud.set_stats([[TextDb.mark("HEAT"), str(c.heat if hud_heat_shown < 0 else hud_heat_shown), "/%d" % cfg.heat_max, heat_tip()],
		[TextDb.mark("SCHEMATICS"), str(c.schematics), "", tr("Schematics: the campaign's currency. Recruit, claim and upgrade nodes, repair, scrub Heat, buy boosts and Profile unlocks.")],
		[TextDb.mark("HOME"), str(c.grid.home_integrity if hud_home_shown < 0 else hud_home_shown), "/%d" % c.grid.home_max_integrity, tr("Home server integrity. At 0 the campaign is lost; raids that reach it take it down. Patch it at HQ.")],
		[TextDb.mark("EXPLOITS"), str(c.exploits.size()), "/%d" % cfg.min_exploits_for_breach, tr("Exploits found: %s. The breach on the corporation's core needs %d.") % [_exploit_names(c), cfg.min_exploits_for_breach]],
		[TextDb.mark("RAIDS"), str(c.pending_raids.size() if hud_raids_shown < 0 else hud_raids_shown), "", tr("Raids pending against your network. Set up the defence before the next run.")],
		[TextDb.mark("ICE"), str(c.ice_level), "", _ice_description(c.ice_level)],
		[TextDb.mark("CREW"), str(c.living_operatives().size()), "", tr("Living operatives in the Cell.")]],
		# H24 S16: whose numbers these are (a run adds its own group).
		[[0, tr("CAMPAIGN"), tr("The campaign's numbers: they stay between runs.")]])
	var op := selected_op()
	hud.loadout_button.visible = op != null
	if op != null:
		hud.set_daemons(op.daemon_ids)


## What the Heat number means now: the next threshold and the rules the crossed ones added.
func heat_tip() -> String:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var next := -1
	for t in cfg.heat_thresholds:
		if t != null and t.heat > c.heat and (next < 0 or t.heat < next):
			next = t.heat
	var lines := PackedStringArray()
	lines.append(tr("Heat %d of %d: how hard the corporation hunts the Cell.") % [c.heat, cfg.heat_max])
	if next >= 0:
		lines.append(tr("Next threshold at %d.") % next)
	var mods := PackedStringArray()
	for m in HeatRules.active_modifiers(c, cfg):
		mods.append(_modifier_text(m))
	lines.append(tr("In force: %s.") % (", ".join(mods) if not mods.is_empty() else tr("nothing yet")))
	return "\n".join(lines)


## A rule modifier as words ("Raid strength +10%").
static func _modifier_text(m: RuleModifierData) -> String:
	var key: String = RC.RuleModifierType.keys()[m.type]
	var pct := key.ends_with("_PCT")
	# H24 S2: the sign from TextDb.signed (no "%+" in a translated line).
	return "%s %s%s" % [TranslationServer.translate(key.trim_suffix("_PCT").capitalize()), TextDb.signed(roundi(m.value)), "%" if pct else ""]


## The operative VIEW LOADOUT and the Daemon tray show: the one picked on a dossier, else
## the first living operative (null when nobody is alive).
func selected_op() -> OperativeState:
	var c := RunManager.campaign
	if c == null:
		return null
	var living := c.living_operatives()
	for op in living:
		if op.id == selected_operative:
			return op
	return living[0] if not living.is_empty() else null


## A Site's name as the Grid shows it (the home server is CORE); never a raw id.
func site_name(site_id: StringName) -> String:
	if site_id == &"":
		return "-"
	var c := RunManager.campaign
	if c != null and c.grid != null and site_id == c.grid.home_site_id:
		return tr(HOME_LABEL)
	var sd := CampaignRules.site_data(RunManager.corporation, site_id) if RunManager.corporation != null else null
	return TextDb.t(sd, "display_name") if sd != null else String(site_id)


## A content id's display name (node types, assets, boosts) through TextDb (H21 #19), else
## the id.
func _display(id: StringName) -> String:
	var res := RunManager.lookup().get_content(id)
	return TextDb.t(res, "display_name") if res != null and "display_name" in res else String(id)


## Adds `control` to `parent` with a wrapped tooltip; returns it.
func _add_tip(parent: Node, control: Control, tip: String) -> Control:
	control.tooltip_text = UiTip.fold(tip)
	parent.add_child(control)
	return control


## The Cell at a glance as badges (the HQ's CELL STATUS; H20 replaces the SYSTEM ONLINE
## text): home integrity with a meter, each Exploit found (or how many the breach needs),
## the Armory's assets by icon and count, and every rule the crossed Heat thresholds add.
func cell_badges() -> HFlowContainer:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var flow := HFlowContainer.new()
	flow.name = "CellBadges"
	flow.add_theme_constant_override("h_separation", 12)
	flow.add_theme_constant_override("v_separation", 6)
	# H21 #10: each badge names what it counts and carries the icon of that stat's top-bar
	# tag (house = HOME, diamond = EXPLOITS, crate = ARMORY); Armory assets by short name.
	var home_col := Palette.CELL_ACID if c.grid.home_integrity * 2 > c.grid.home_max_integrity else Palette.CELL_PINK
	var home := Badge.new(tr("HOME %d/%d") % [c.grid.home_integrity, c.grid.home_max_integrity], home_col, GLYPH_HOME,
		tr("Home server integrity. At 0 the campaign is lost.")).with_meter(c.grid.home_integrity, c.grid.home_max_integrity).with_icon(StatIcon.HOME)
	home.name = "HomeBadge"
	flow.add_child(home)
	var exploits := Badge.new(tr("EXPLOITS %d/%d") % [c.exploits.size(), cfg.min_exploits_for_breach], Palette.CELL_ACID if not c.exploits.is_empty() else Palette.NET_CYAN, GLYPH_EXPLOIT,
		tr("Exploits found: %s. Exploit Sites on the Grid give one each; the breach on the corporation's core needs %d.") % [_exploit_names(c), cfg.min_exploits_for_breach]).with_icon(StatIcon.EXPLOITS)
	exploits.name = "ExploitsBadge"
	flow.add_child(exploits)
	for e in c.exploits:
		var ename := exploit_name(e)
		flow.add_child(Badge.new(ename, Palette.CELL_ACID, GLYPH_EXPLOIT,
			tr("Exploit %s found (%d/%d for the breach).") % [ename, c.exploits.size(), cfg.min_exploits_for_breach]).with_icon(StatIcon.EXPLOITS))
	# ANIM-R1 M5: the Cell's claimed Sites (its network), the counter a territory change bumps.
	var sites := maxi(0, c.grid.claimed_ids().size() - 1)
	var network := Badge.new(tr("SITES %d") % sites, Palette.CELL_PINK, GLYPH_NODE,
		tr("Sites your network holds besides CORE: claim cleared Sites on the City Grid.")).with_icon(StatIcon.MAP)
	network.name = "NetworkBadge"
	flow.add_child(network)
	var armory := Badge.new(armory_words(), Palette.CELL_PINK, GLYPH_NODE, armory_tip()).with_icon(StatIcon.ARMORY)
	armory.name = "ArmoryBadge"
	flow.add_child(armory)
	var seen := {}
	for aid in c.armory:
		if seen.has(aid):
			continue
		seen[aid] = true
		var data := lookup.get_content(aid) as DefenseAssetData
		flow.add_child(Badge.new("%s x%d" % [_display(aid), c.armory.count(aid)], Palette.CELL_PINK, "", tr("%s (Armory %d/%d)\n%s") % [
			_display(aid), c.armory.size(), cfg.armory_capacity, TextDb.t(data, "description") if data != null else ""], aid))
	for m in HeatRules.active_modifiers(c, cfg):
		flow.add_child(Badge.new(_modifier_text(m), Palette.corp_color(c.corporation_id), GLYPH_RULE, tr("In force since a Heat threshold. Scrub Heat to fall back under it.")).with_icon(StatIcon.HEAT))
	return flow


## ANIM-R1 M5: a territory change landed on the city: the counter it changes bumps (the
## CELL STATUS SITES badge on the HQ page).
func _on_territory_marked(_marks: Array) -> void:
	var badge := _panel.find_child("NetworkBadge", true, false) as Control if _panel != null else null
	if badge != null and badge.is_visible_in_tree():
		Motion.pop(badge, &"sticky_bump")
	refresh_site_card()


## ANIM-R3 B6: the Grid's Site card rebuilt in place for the campaign as it is now (a claim
## seen on the map while the card still offered CLAIM); nothing off the Grid.
func refresh_site_card() -> void:
	if panel_name != "grid" or _panel == null or RunManager.campaign == null:
		return
	var old := _panel.find_child("SelectedSite", true, false) as Control
	var site := CampaignRules.site_data(RunManager.corporation, selected_site)
	if old == null or site == null:
		return
	# Only when what the card shows changed (the city marks its territory on redraws too: a
	# rebuild for nothing re-laid the page, which redrew the city, which marked again...).
	var shows := [selected_site, int(RunManager.campaign.grid.status_of(selected_site))]
	if old.get_meta(&"shows", []) == shows:
		return
	var launchable := RunManager.launchable_sites()
	launchable.append_array(RunManager.patrol_sites())
	var card := _site_card(site, launchable, RunManager.campaign.living_operatives(), _node_choices())
	card.size_flags_horizontal = old.size_flags_horizontal
	card.size_flags_vertical = old.size_flags_vertical
	var parent := old.get_parent()
	var at := old.get_index()
	parent.remove_child(old)
	old.queue_free()
	parent.add_child(card)
	parent.move_child(card, at)
	_fix_card_height(card)
	TextDb.shown_as_given(card)


## Refusals, saves and unlocks the player must see (the log strip is optional): a toast.
func notify(text: String, warn: bool = false) -> void:
	ToastNote.show_on(self, text, warn)


func _report(events: Array[Dictionary]) -> void:
	if RunManager.campaign != null:
		CampaignRules.name_pending_raids(RunManager.campaign, RunManager.lookup(), events)
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")
			if String(e.get("type", "")) in TOAST_WARN_EVENTS:
				notify(String(e["text"]), true)
			elif String(e.get("type", "")) in TOAST_NEWS_EVENTS:
				notify(String(e["text"]))


## A button whose label ends in the key hint for `action`; relabelled when the device or
## the binds change (H20).
func _hint_button(text: String, action: StringName, on_pressed: Callable) -> Button:
	var b := _button(text, on_pressed)
	b.set_meta(&"hint_base", text)
	b.set_meta(&"hint_action", action)
	_hint_label(b)
	_hint_buttons.append(b)
	return b


func _hint_label(b: Button) -> void:
	# W8a: with a pad the prompt bar names the button; the line keeps its words only.
	var key := "" if Settings.pad_active else Settings.hint(StringName(b.get_meta(&"hint_action")))
	b.text = ("%s %s" % [String(b.get_meta(&"hint_base")), key]).strip_edges()


func _relabel_hints() -> void:
	var alive: Array[Button] = []
	for b in _hint_buttons:
		if is_instance_valid(b) and not b.is_queued_for_deletion():
			_hint_label(b)
			alive.append(b)
	_hint_buttons = alive


func _build_ui() -> void:
	background = CyberdeckBackground.new()
	background.city.territory_marked.connect(_on_territory_marked)
	add_child(background)
	wireframe = WireframeBackground.new()
	wireframe.city.territory_marked.connect(_on_territory_marked)
	wireframe.visible = false
	add_child(wireframe)
	# Art pass W8b (§2 DECK): the HQ's cyberdeck frame, under the page (it frames the scroll).
	deck_frame = DeckFrame.new()
	deck_frame.visible = false
	add_child(deck_frame)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE  # city map screens take clicks behind
	add_child(root)
	hud = HudBar.new()
	hud.loadout_pressed.connect(open_loadout)
	hud.daemons_pressed.connect(open_daemons)
	root.add_child(hud)
	_status = hud.label
	# The subtitles' own band under the top bar: no control and no stat tag under it (H21 #11).
	subtitle_strip = SubtitleStrip.new()
	root.add_child(subtitle_strip)
	var scroll := ScrollContainer.new()
	scroll.name = "PageScroll"
	scroll.follow_focus = true  # pad focus scrolls long lists (Grid Sites)
	# Never sideways: rows wrap (HFlowContainer) to the 1280-wide screen instead.
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(scroll)
	deck_frame.target = scroll
	# The deck's keyboard edge: a row of its own under the page, so nothing scrolls under it.
	var keys := Control.new()
	keys.name = "DeckKeys"
	keys.mouse_filter = Control.MOUSE_FILTER_IGNORE
	keys.custom_minimum_size.y = DeckFrame.KEYBOARD_H
	keys.visible = false
	root.add_child(keys)
	deck_frame.keys_row = keys
	_panel_host = PanelContainer.new()
	_panel_host.theme_type_variation = &"GlassPanel"
	_panel_host.material = UiTheme.crt_material()
	_panel_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.add_child(_panel_host)
	# Pad prompts in a row of their own under the page (H23 S11).
	pad_prompts = PadPrompts.new()
	root.add_child(pad_prompts)
	_log = RichTextLabel.new()
	_log.theme_type_variation = &"LogText"
	_log.material = UiTheme.crt_material()
	_log.bbcode_enabled = true
	_log.scroll_following = true
	_log.custom_minimum_size = Vector2(0, 96)
	root.add_child(_log)
	# Shown only when the player turns it on in Options.
	_log.visible = Settings.system_log
	Settings.changed.connect(func() -> void: _log.visible = Settings.system_log)
	# More below (the HQ's BLACK MARKET): a tag at the foot of the page while it scrolls on.
	more_hint = ScrollHint.new(scroll)
	add_child(more_hint)
	# ANIM-4: drag and drop over every page (targets pulse, the pad's reticle, flights).
	drops = DropLayer.new()
	_wire_drops(drops)
	add_child(drops)
	hud.watch_drops(drops)  # W8b §6.9: a tag that takes the carried item shows its brackets


## ANIM-4: a drop layer's questions and intents come to this screen: whether a target
## takes an item (the rules, dry-run), what the item looks like, and the drop itself.
func _wire_drops(layer: DropLayer) -> void:
	layer.check = drop_error
	layer.ghost_maker = drop_ghost
	layer.dropped.connect(_on_dropped)
	layer.refused.connect(_on_refused)
	layer.carry_changed.connect(_on_carry_changed)


## Turns the buttons in `box` into "> ITEM" terminal menu lines.
func _as_menu(box: Control) -> void:
	for b in box.get_children():
		if b is Button:
			b.theme_type_variation = &"MenuItem"
			(b as Button).alignment = HORIZONTAL_ALIGNMENT_LEFT
	# ANIM-6: the highlight slides, the line types in, the caret blinks.
	MenuMotion.attach(box)


## A long line of prose that wraps to the panel width (profile, unlocks, records).
func _para(text: String) -> Label:
	var l := _label(text)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return l


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	return b


## Puts the currency's StatIcon `kind` after button `b`'s price (H23 S13: "(25)" did not
## say it was Schematics): a mark at the button's right end, the words kept clear of it.
## The kind is in the button's "price_kind" meta.
func _price_icon(b: Button, kind: StringName) -> IconMark:
	var px := roundf(UiTheme.BASE_SIZE * Settings.text_scale * IconMark.SIZE_FACTOR)
	var mark := IconMark.standalone(kind, px)
	mark.name = "PriceIcon"
	b.add_child(mark)
	b.set_meta(&"price_kind", kind)
	var place := func() -> void:
		# ANIM-R1 M12: right after the price ("pay 25" then the icon), not at the far end of
		# a wide menu line; never past the button's right edge.
		var end_x := b.size.x - px - PRICE_ICON_GAP * 0.5
		var sb := b.get_theme_stylebox(&"normal")
		var font := b.get_theme_font(&"font")
		if sb != null and font != null and b.alignment == HORIZONTAL_ALIGNMENT_LEFT:
			var icon_w := float(b.icon.get_width()) + b.get_theme_constant(&"h_separation") if b.icon != null else 0.0
			var text_w := font.get_string_size(b.text, HORIZONTAL_ALIGNMENT_LEFT, -1, b.get_theme_font_size(&"font_size")).x
			end_x = minf(end_x, sb.get_margin(SIDE_LEFT) + icon_w + text_w + PRICE_ICON_GAP)
		mark.position = Vector2(end_x, (b.size.y - px) * 0.5)
	# The theme's boxes are known once the button is in the tree: room made on the right then.
	var make_room := func() -> void:
		for st in [&"normal", &"hover", &"pressed", &"hover_pressed", &"focus", &"disabled"]:
			var sb := b.get_theme_stylebox(st)
			if sb == null:
				continue
			var room := sb.duplicate() as StyleBox
			room.content_margin_right = sb.get_margin(SIDE_RIGHT) + px + PRICE_ICON_GAP
			b.add_theme_stylebox_override(st, room)
		place.call()
	if b.is_inside_tree():
		make_room.call()
	else:
		b.ready.connect(make_room, CONNECT_ONE_SHOT)
	b.resized.connect(place)
	return mark


## Puts StatIcon `kind` before button `b`'s words (H21 #13: menus in words only); returns b.
func _icon(b: Button, kind: StringName) -> Button:
	IconMark.attach(b, kind)
	return b
