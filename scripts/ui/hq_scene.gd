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
	GridState.SiteStatus.CLAIMED: "claimed", GridState.SiteStatus.TAKEN: "TAKEN"} # TR

## Screen numbers on the HUD strip, by panel name (STYLE_GUIDE 4, "Neon city"); the
## titles are `screen_title`.
const SCREEN_NUMBERS := {"start": "00", "hq": "01", "raid": "03", "raid_playout": "03", "raid_summary": "03"}

## The home server's name on the Grid, the raid map and the orders (never its id).
const HOME_LABEL := "CORE" # TR
## Event types that pop a toast (H20: the log strip is optional): refusals in pink,
## news in acid.
const TOAST_WARN_EVENTS: Array[String] = ["refused", "deploy_failed", "undock_failed"]
const TOAST_NEWS_EVENTS: Array[String] = ["unlocked"]
## Glyphs for Site objectives and facts on badges (the map uses the same).
const GLYPH_EXPLOIT := "◈"
const GLYPH_HEAT := "❄"
const GLYPH_CENTRAL_SERVER := "✦"
const GLYPH_HOME := "⌂"
const GLYPH_NODE := "⬡"
const GLYPH_RULE := "!"
const GLYPH_UPGRADE := "▲"
const GLYPH_GUARD := "☻"
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
## The raid setup's big button (H24 S14: "RUN THE RAID" read like attacking).
const START_DEFENSE := "START DEFENSE" # TR
## Words the screens translate that sit in the core's data (H24 S1: exported by the "# TR"
## marker): run kinds, raid outcomes, Exploit types and rule modifier names.
const RUN_KIND_WORDS := ["netrun", "patrol", "reclaim", "boss"] # TR
const OUTCOME_WORDS := ["HOLDS", "DOWN", "TAKEN", "PASSED"] # TR
## ART-6 3A: the home server's label outcome when it falls (shown_outcome; RaidVerdict.BREACHED's word).
const OUTCOME_BREACHED := "breached"
const EXPLOIT_WORDS := ["Intel", "Breach", "Virus"] # TR
const MODIFIER_WORDS := ["Heat Gain", "Heat Sink", "Heat Objective Sites", "Elite Frequency", "Cycle Price", "Shop Stock", # TR
	"Raid Strength", "Raid Extra Wave", "Enemy Resistance", "Death Heat", "Exploit Heat", "Boss Phase Early", # TR
	"Boss Extra Pointer", "Starting Bug Card", "No First Turn Free Nudge", "Repair Cost", "Taken Raid Strength", # TR
	"Purge Threshold", "Boss Strength"] # TR
const TARGET_BUTTON_WIDTH := 150.0
## The launch button on a Site's card: the same words as the HQ's JACK IN stamp (H21 #21).
const JACK_IN := "JACK IN" # TR
## ART-10 4C: the screen-title stickers (lettering px at 1.0, tilt in degrees).
const TITLE_STICKER_PX := 30.0
const TITLE_STICKER_TILT := -3.0
## What each Site status means (the selected Site card's status badge).
const STATUS_TIPS := {GridState.SiteStatus.CORPORATE: "Corporate: run it to clear it.", # TR
	GridState.SiteStatus.CLEARED: "Cleared: claim it to build a node of your network.", # TR
	GridState.SiteStatus.CLAIMED: "Claimed: part of your network; it defends in raids.", # TR
	GridState.SiteStatus.TAKEN: "TAKEN by a raid: run it again to take it back."} # TR

var _status: Label
## Top strip: screen title and the status line (`_status`).
var hud: HudBar
## The subtitles' band under the top bar (H21 #11).
var subtitle_strip: SubtitleStrip
## "More below" at the foot of a page that scrolls on (H21 #15).
var more_hint: ScrollHint
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var panel_name: String = ""
var background: CyberdeckBackground
var wireframe: WireframeBackground
var playout: RaidPlayoutPanel = null
## The raid setup's map key (placed clear of the nodes).
var raid_legend: MapLegend = null
## The Grid map's key, on the map (H23 #3), and the passes fitting the map so far.
var grid_legend: MapLegend = null
## ART-5 5a: the Grid's player camera on the 3D city (wheel, drag, WASD, the pad's right
## stick) and its minimap terminal (on the map's foot, left of the key); freed with the page.
var grid_controls: CityGridControls = null
var grid_minimap: CityMinimap = null
## ART-5 5e: the Grid map's off-screen TARGET arrow (null off the Grid or headless 2D).
var grid_target: TargetEdgeMarker = null
## Leans shorter than this (screen px) are not worth a new frame.
const GRID_LEAN_MIN := 1.0
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
## ANIM-4: pages whose items the pick-up key takes (the pad prompt names it).
const DRAG_PANELS: Array[String] = ["hq", "raid"]
## Whether the last page entered a new panel (its entrance plays) or rebuilt the same one.
var entering: bool = false


func _ready() -> void:
	UiTheme.apply(self)
	MotionSkip.register(self)  # ANIM-R6 C13: the page's pops complete with every other motion
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
	# ANIM-R6 C16: the campaign's end page in context (--demo-campaign-end=won|lost).
	for a in args:
		var outcome := demo_end_of(a)
		if outcome >= 0:
			demo_campaign_end(outcome)
			return
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
			var classes: Array[ClassData] = []
			for id in [&"ghost", &"rigger", &"botnet", &"wrecker", &"phantom", &"overclocker", &"hivemind"]:
				classes.append(RunManager.lookup().get_content(id) as ClassData)
			DemoSetup.roster_of(RunManager.campaign, classes)  # ANIM-R6 C16: views write no state
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
			DemoSetup.set_schematics(c, DEMO_SCHEMATICS)
			var grid_data := RunManager.corporation.city_grid
			var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
			CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), _demo_run(first))
			CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
			DemoSetup.set_armory(c, DEMO_ARMORY)
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
	# ANIM-R6 D11: the log strip (an Options switch) translates its words.
	_log.append_text("[b]%s[/b] %s\n" % [tr("New campaign"), tr("(seed %d, ICE %d, %s) against %s. Story path: %s.") % [seed, RunManager.campaign.ice_level,
		RunManager.campaign.home_variant_id, TextDb.t(RunManager.corporation, "display_name"), RunManager.campaign.story_path_id]])
	show_hq()


func resume() -> void:
	if RunManager.scene_change_pending():
		return
	if RunManager.resume():
		_log.append_text("[b]%s[/b]\n" % tr("Resumed."))
		if RunManager.has_active_run():
			RunManager.go_to_netrun()
		else:
			show_hq()
	else:
		_log.append_text("[color=orange]%s[/color]\n" % tr("Nothing to resume."))
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
		if get_tree().process_frame.is_connected(fit_hq_map):
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
## The cache key the running warm pass started from (ANIM-R5 P14).
var _warm_key: int = 0
## Campaign hashes worked out (`campaign_key`), for tests (ANIM-R5 P14).
static var campaign_hashes: int = 0


## The campaign state's key for the preview cache (its serialised form's hash).
static func campaign_key(c: CampaignState) -> int:
	if c == null:
		return 0
	campaign_hashes += 1
	return var_to_str(c.to_dict()).hash()


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
	_warm_key = _previews_key
	_warm_sites.clear()
	var sites := RunManager.launchable_sites()
	sites.append_array(RunManager.patrol_sites())
	for s in sites:
		if not _previews.has(s.id):
			_warm_sites.append(s.id)
	if not _warm_sites.is_empty() and is_inside_tree() and not get_tree().process_frame.is_connected(_warm_preview_step):
		get_tree().process_frame.connect(_warm_preview_step, CONNECT_ONE_SHOT)


## ANIM-R5 P14: the campaign is hashed once per warm pass (`_warm_previews`), not every frame
## (var_to_str of the whole campaign each frame). A step stops when the cache has been re-keyed
## since (the Grid's `_sync_previews` found the campaign changed); a preview worked out after
## a change the pass did not see is keyed to the old state, which the next sync drops.
func _warm_preview_step() -> void:
	if panel_name != "hq" or RunManager.campaign == null or _warm_sites.is_empty() or not is_inside_tree():
		return
	if _previews_key != _warm_key:
		_warm_sites.clear()
		return
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
	# Parity fix (RAID-08): where START DEFENSE was, for its peel (the playout page is not laid
	# out yet when the peel starts).
	var start := _panel.find_child("RunRaid", true, false) as Control if _panel != null and is_instance_valid(_panel) else null
	_start_was = start.get_global_rect() if start != null and start.is_visible_in_tree() else Rect2()
	wireframe.city.pin_influence(CityInfluence.of(RunManager.campaign, RunManager.corporation))
	if Motion.animating() and RunManager.campaign != null:
		hud_home_shown = RunManager.campaign.grid.home_integrity  # ANIM-R1 M4: HOME rolls down as hits land
		# ANIM-R4 H11a: Heat and RAIDS hold too, until the feed tells what changes them.
		hud_heat_shown = RunManager.campaign.heat
		hud_raids_shown = RunManager.campaign.pending_raids.size()
	var events := RunManager.fight_raid()
	_note_raid_outcome(events)  # ART-6 3A: the report prints the Heat and the reward
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
	# HQ-B: the runner is the hand's lifted card; the page rebuilds with it, focus on JACK IN.
	_hq_focus = "Launch"
	pick_runner(operative_id)


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
			# picks the operative in the list; only pressing JACK IN starts the run. HQ-B: dropped
			# on a Site, it selects that Site too.
			if value is StringName and value != &"":
				selected_site = value
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
		var card := _panel.find_child("Crew_%s" % c.roster[c.roster.size() - 1].id, true, false) as Control if c != null and not c.roster.is_empty() else null
		# HQ-B: from the MARKET hand the new operative lands on the CREW tab.
		return card if card != null else _panel.find_child("Tab_CREW", true, false) as Control
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
	# ART-11 4D: the campaign lost lock goes with its page.
	if name != "end_lock" and end_lock != null and is_instance_valid(end_lock):
		end_lock.queue_free()
		end_lock = null
	# ANIM-4: the old page's drop targets go with it (a flight in the air keeps going).
	if drops != null:
		drops.reset()
	if _panel != null:
		_panel.queue_free()
	# ART-5 5a: the City Grid is the unified 3D city; ART-3 6w: the raid's pages too (setup,
	# playout, report), holding the RAID band (see-through buildings, management lanes). The
	# other net pages keep the 2D city until their views move onto it.
	if wireframe != null:
		wireframe.use_city3d(name == "hq" or name in RAID_CITY_PAGES, CityLod.Band.RAID)
	_clear_city_map()
	# City map screens: clicks fall through the empty panel area to the map.
	var on_city := name in ["hq", "raid", "raid_playout", "raid_summary", "end_lock"] or name.begins_with("city")
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE if on_city else Control.MOUSE_FILTER_STOP
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel = p
	# ANIM-6: a new page enters (glass slides in, back to the HQ from the left); the same page
	# rebuilt after an action just shows.
	# HQ-B: the HQ and its raid setup are one page (a tab switch, not a new page).
	entering = name != panel_name and not (name in HQ_PAGES and panel_name in HQ_PAGES)
	var back := name == "hq" and panel_name != ""
	panel_name = name
	# ANIM-5: only the Grid and the playout ease their camera; any other page shows its
	# frame at once.
	if wireframe != null and not name in ["hq", "raid", "raid_playout"]:
		wireframe.settle_camera()
	# H24 S4: the page shows its words as given (translated once, where they are built).
	TextDb.shown_as_given(p)
	_panel_host.add_child(p)
	if more_hint != null and is_instance_valid(more_hint):
		# ANIM-R6 C15: the HQ page's own snap (the others keep theirs: the raid setup's card row
		# is taller than any snap would keep whole).
		more_hint.snap_rows = name == "hq"
		more_hint.reset_snap()
	# Screens built from terminal windows let the city show between them.
	# ANIM-R5 P4: the campaign's end too (it was a near-opaque glass page of terminal lines).
	_panel_host.theme_type_variation = &"" if name in ["hq", "start", "raid", "raid_playout", "raid_summary", "end", "end_lock"] or name.begins_with("city") else &"GlassPanel"
	# HQ-B (Q6): the HQ shows no title (the HEAT gauge holds the bar's first slot).
	hud.set_screen("" if name in HQ_PAGES else String(SCREEN_NUMBERS.get(name, "")), "" if name in HQ_PAGES else screen_title(name))
	if not name in HEAT_BUTTON_PAGES:
		close_heat_terminal(false)
	if not name in HQ_PAGES:
		hq_map_mode(false)  # HQ-B: the map mode is the HQ's (and its raid setup's) only
	# H24 S15: lines tied to the screen being left end here.
	Dialogue.enter_screen(name)
	set_page_prompts(prompts_for(name))
	UiWrap.fit(p)
	UiFocus.link_layout(p)
	# ANIM-R3 B5: the raid playout goes on from the raid setup's map: it shows whole at once
	# (a page entrance showed a dim, half-drawn map for its first frames).
	# ART-11 4D: the campaign's end plays its own motion (the lock, the dossier's cover).
	if entering and not name in ["raid_playout", "end_lock", "end"]:
		if _panel_host.theme_type_variation == &"" and name != "start":
			PageTransition.glass_is_windows(p)  # ANIM-R1 M11: the roll band crosses the windows only
		PageTransition.enter(p, PageTransition.look_of(p), UiFocus.focus_first.bind(p), -1 if back else 1)
	else:
		UiFocus.focus_first(p)
	_scroll_to_top.call_deferred()
	# Worlds (STYLE_GUIDE 1): the room is a cyberdeck, the Grid and raids are wireframe.
	var net := name in ["hq", "raid", "raid_playout", "raid_summary", "end_lock"] or name.begins_with("city")
	background.visible = not net
	wireframe.visible = net
	AudioDirector.play_music("raid" if name.begins_with("raid") else "hq",
		RunManager.campaign.corporation_id if RunManager.campaign != null else &"")
	if RunManager.campaign != null:
		var band := RunManager.campaign.heat_majors_crossed(RunManager.config())
		background.heat_band = band
		# ANIM-R5 P2: a raid's playout holds the Heat band of before the raid (as it holds the
		# pre-raid tint): a band crossed by the raid is a new look, rebaked mid-raid.
		wireframe.corp_creep = (_creep_band if _creep_band >= 0 else band) / 3.0
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
func open_loadout(op: OperativeState = null) -> void:
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


## HQ-B (Q9): the Codex, in the pause menu (the start page's Codex line opens it there).
func open_codex() -> void:
	if _settings_panel == null:
		open_settings()
	if _settings_panel != null:
		_settings_panel.show_codex()


func open_settings() -> void:
	if _settings_panel != null:
		_settings_panel.queue_free()
		_settings_panel = null
		return
	_settings_panel = PauseMenu.new()
	_settings_panel.position = Vector2((size.x - PauseMenu.MENU_SIZE.x) / 2.0, SubtitleStrip.top_below(PAUSE_TOP))  # under the subtitle band (H22: the top bar grows with its words)
	_settings_panel.resumed.connect(open_settings)
	# ART-0 F (ported from art-pass W8a, §10 rule 6): the open modals close before the title.
	_settings_panel.quit_to_title.connect(func() -> void: open_settings(); PageTransition.after_modals(self, RunManager.go_to_title))
	add_child(_settings_panel)
	get_tree().paused = false


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_settings"):
		open_settings()
		get_viewport().set_input_as_handled()
		return
	# HQ-B (Q1): H, or the pad's View (the run's rewind button; the HQ has no rewind), drops
	# the Heat terminal from the gauge.
	if panel_name in HEAT_BUTTON_PAGES and _settings_panel == null and (event.is_action_pressed(HeatGauge.OPEN_ACTION)
			or (event is InputEventJoypadButton and event.is_action_pressed(&"rewind"))):
		toggle_heat_terminal()
		get_viewport().set_input_as_handled()
		return
	# H24 K1: the pad's key button (Y) opens and folds the Grid's map key at big text.
	if event.is_action_pressed("cycle_target") and panel_name in HQ_PAGES and grid_legend != null \
			and is_instance_valid(grid_legend) and grid_legend.visible and grid_legend.foldable():
		grid_legend.set_opened(not grid_legend.opened)
		get_viewport().set_input_as_handled()
		return
	# HQ-B: LB / RB (Q / E) switch the hand's tabs; R opens the raid setup (RAID SETUP [R]).
	if panel_name in HQ_PAGES and _settings_panel == null and not has_node("LoadoutView") and not has_node("DaemonTray"):
		for step in [[&"nudge_left", -1], [&"nudge_right", 1]]:
			if event.is_action_pressed(step[0]) and not event.is_echo():
				open_hand(posmod(hand_tab + int(step[1]), TAB_WORDS.size()))
				get_viewport().set_input_as_handled()
				return
		if event.is_action_pressed(&"toggle_ring") and not event.is_echo() and RunManager.campaign != null and not RunManager.campaign.pending_raids.is_empty():
			open_hand(HandTab.DEFENCE)
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
		# ART-0 F (ported from art-pass W8a, §10 rule 6): a modal never outlives a page change.
		PageTransition.after_modals(self, show_hq)
		get_viewport().set_input_as_handled()


## Panels B leaves for the HQ (their "Back to HQ" button).
const BACK_PANELS: Array[String] = ["raid"]
## ANIM-R6 C7: the pad prompt of the maps' folding key (exported for the translators).
const KEY_PROMPT := "Key" # TR


# --- ANIM-R6 C13: the page's short pops complete with every other motion ----------------------

## The page's pops (Motion.pop on a piece of the page: a verdict stamp landing, the SITES
## badge's bump, a crew card popping as a drop lands) are motion like any other: a press
## while one plays completes it (and every other running motion) by the one rule
## (MotionSkip.handle). The HQ answers for them (MotionSkip.GROUP).
func _input(event: InputEvent) -> void:
	if MotionSkip.is_press(event) and motion_running():
		MotionSkip.handle(event, self)


## MotionSkip: a pop plays on a piece of the page.
func motion_running() -> bool:
	return not popping().is_empty()


## MotionSkip: every pop at its rest.
func complete_motion() -> void:
	for n in popping():
		Motion.stop(n)


## ANIM-R6 C13: the page's pieces whose pop plays now (tests).
func popping() -> Array[Node]:
	var out: Array[Node] = []
	if _panel == null or not is_instance_valid(_panel) or not is_inside_tree():
		return out
	var key := StringName(Motion.META_PREFIX + "scale")
	if _panel.has_meta(key):
		out.append(_panel)
	for n in _panel.find_children("*", "CanvasItem", true, false):
		if n.has_meta(key):
			out.append(n)
	# HQ-B (a): the Heat gauge's bump (a Site claimed) is the HQ's too.
	if hud != null and is_instance_valid(hud) and hud.heat_gauge != null and hud.heat_gauge.has_meta(key):
		out.append(hud.heat_gauge)
	return out


## The pad prompts of panel `p_name` (H23 S11): A presses the focused control, B goes back
## where the panel has a Back to HQ, Menu opens the settings.
static func prompts_for(p_name: String) -> Array:
	var out: Array = [[&"ui_accept", "Select"]] # TR
	# ANIM-4: the pick-up key carries the focused item to a target (D-pad, A drops).
	if p_name in DRAG_PANELS:
		out.append([&"end_turn", "Pick up"]) # TR
	if p_name in BACK_PANELS:
		out.append([&"ui_cancel", "Back"]) # TR
	# HQ-B: the hand's tabs, the Heat terminal and the map key.
	if p_name == "hq":
		out.append([&"nudge_right", "Tabs"]) # TR
		out.append([&"rewind", "Heat"]) # TR
		out.append([&"cycle_target", KEY_PROMPT])
	out.append([&"open_settings", "Settings"]) # TR
	return out


## Parity NEWC-01..04 (designer 2026-10-05): the new campaign page is the art pass build's
## planning table (ported from art-m13-final scripts/ui/hq_scene.gd `show_start`, W8b) in the
## v2 kit. The pickers are tiles, every choice visible at once with locked ones showing their
## unlock (NEWC-01, NEWC-04: no dropdown, no popup list): Target as corporation tiles (hue
## stripe, crest, `Best ICE`), ICE as a big `- n +` stepper, Home server as tiles (house icon,
## lock, `UNLOCKS · cost`), Crew as portrait tiles (the class's v2 bust). Main's NEW CAMPAIGN
## title sticker and TRUST NO ONE pencil stay, and the one verb, START, is a pink vinyl sticker
## at the head's right end, where the eye ends (NEWC-02). The seed, today's run and the share
## codes are main's own and stay, on plain cyan terminals (lime is focus only, v2 §2.10); the
## share code row folds away under its terminal (NEWC-03). Choices come from the profile's
## unlocks as before (RunManager.available_*); a locked tile can't be picked.
func show_start() -> void:
	# The pickers' tile sizes at text scale 1.0 (px, they grow to hold their words) and the
	# crew's portrait swatch.
	const CORP_TILE := Vector2(224, 76)
	const HOME_TILE := Vector2(168, 64)
	const CREW_TILE := Vector2(176, 76)
	const CREW_SWATCH := 56.0
	# The START sticker's lettering size (px at 1.0) and tilt (degrees), the seed's top value.
	const START_PX := 36.0
	const START_TILT := 2.0
	const SEED_MAX := 999999
	# From this text scale today's run and the share codes stack (side by side the run's lines
	# wrapped in a narrow column).
	const CODES_STACK_FROM := 1.6
	# Today's run beside the share codes: its share of the row (the codes' is 1).
	const DAILY_SHARE := 0.6
	var lookup := RunManager.lookup()
	var profile := RunManager.profile
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	var head := HBoxContainer.new()
	head.name = "PageHead"
	head.add_theme_constant_override("separation", 24)
	# ART-10 4C (v2 §1.2, §2.10): the yellow title sticker and the Cell's motto in grease
	# pencil (the spray tag and scrawl are rejected media).
	head.add_child(_title_sticker(tr("NEW CAMPAIGN"), "NEW CAMPAIGN"))
	head.add_child(PencilWords.new(tr("TRUST NO ONE"), -4.0))
	var head_gap := Control.new()
	head_gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head_gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	head.add_child(head_gap)
	box.add_child(head)
	var setup := CrtWindow.new(tr("NEW CAMPAIGN // [HQ] the deck is warm. Jack a campaign in."))
	setup.name = "PlanningTable"
	box.add_child(setup)
	# A group's head: its icon and words in terminal CAPS (cyan: the Cell's own system).
	var plan_head := func(words: String, icon: StringName) -> HBoxContainer:
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", UiTheme.SP_S)
		var mark := IconMark.standalone(icon, UiTheme.font_px(UiTheme.LABEL), PaletteSkins.chrome(Palette.NET_CYAN))
		mark.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(mark)
		row.add_child(Chrome.caps_label(words.to_upper(), UiTheme.LABEL, PaletteSkins.chrome(Palette.NET_CYAN)))
		return row
	# What unlocks a locked choice: the Black Market's price ("UNLOCKS · 80"), or the ICE every
	# corporation must be cleared at (REBEL_CELL's free unlock); the tooltip says where to buy.
	var unlock_words := func(u: ProfileUnlockData) -> String:
		if u != null and u.schematic_cost > 0:
			return tr("UNLOCKS · %d") % u.schematic_cost
		if u != null and u.requires_all_corporations_at_ice >= 0:
			return tr("OPENS AT ICE %d EVERYWHERE") % u.requires_all_corporations_at_ice
		return tr("LOCKED")
	var unlock_tip := func(u: ProfileUnlockData) -> String:
		if u == null:
			return ""
		if u.schematic_cost > 0:
			return "%s %s" % [TextDb.t(u, "description"), tr("Buy it at the HQ Black Market with campaign Schematics (%d).") % u.schematic_cost]
		return tr("Clear every corporation at ICE %d to open it.") % u.requires_all_corporations_at_ice
	# Locked choices after the open ones, cheapest first, then by id (deterministic).
	var locked_order := func(a: Resource, b: Resource) -> bool:
		var ua := CampaignRules.unlock_for(lookup, a)
		var ub := CampaignRules.unlock_for(lookup, b)
		# A price before a free, earned unlock; then the price; then the id.
		var fa := ua == null or ua.schematic_cost <= 0
		var fb := ub == null or ub.schematic_cost <= 0
		if fa != fb:
			return fb
		var ka: int = 0 if fa else ua.schematic_cost
		var kb: int = 0 if fb else ub.schematic_cost
		return ka < kb or (ka == kb and String(a.get("id")) < String(b.get("id")))
	# Each picker starts on the game's default choice (the daily run's, a share code's) when it
	# is open, else on the first open one.
	var pick_default := func(open: Array, id: StringName) -> int:
		for i in open.size():
			if open[i].get("id") == id:
				return i
		return 0
	# A locked tile refused: the toast says what it is and how it opens.
	var refused_note := func(i: int, pick: TilePicker) -> void:
		var t: Dictionary = pick.tiles[i]
		notify(tr("%s is locked. %s") % [String(t.get("name", "")), String(t.get("tip", t.get("unlock", "")))], true)
	# TARGET: every corporation, the open ones first (main's order); a locked REBEL_CELL stays
	# a secret (no spoiler, as the ICE records): CLASSIFIED, no crest.
	var corps := RunManager.available_corporations()
	var open_ids := {}
	var corp_tiles: Array[Dictionary] = []
	for corp in corps:
		open_ids[corp.id] = true
		corp_tiles.append({"name": TextDb.t(corp, "display_name"), "meta": tr("Best ICE: %s") % HudStats.ice_value(profile.best_ice_for(corp.id)),
			"corp": corp.id})
	var locked_corps: Array[Resource] = []
	for id in lookup.ids_of_class(&"CorporationData"):
		var corp := lookup.get_content(id) as CorporationData
		if corp != null and not open_ids.has(corp.id):
			locked_corps.append(corp)
	locked_corps.sort_custom(locked_order)
	for res in locked_corps:
		var corp := res as CorporationData
		var u := CampaignRules.unlock_for(lookup, corp)
		var secret := corp.generated_from_profile
		corp_tiles.append({"name": tr("CLASSIFIED") if secret else TextDb.t(corp, "display_name"), "corp": corp.id, "redacted": secret,
			"locked": true, "unlock": unlock_words.call(u), "tip": unlock_tip.call(u)})
	setup.body.add_child(plan_head.call(tr("Target:"), StatIcon.MAP))
	var corp_pick := PlanningPicker.new(corp_tiles, 0, CORP_TILE)
	corp_pick.name = "CorporationPicker"
	corp_pick.value = pick_default.call(corps, RunManager.DEFAULT_CORPORATION)
	corp_pick.refused.connect(refused_note.bind(corp_pick))
	setup.body.add_child(corp_pick)
	# ICE: a big stepper fronting the spin box (each corporation has its own ICE ladder, GDD 3.4).
	var first_corp: StringName = corps[corp_pick.selected()].id if not corps.is_empty() else RunManager.DEFAULT_CORPORATION
	var cap := RunManager.ice_cap(first_corp)
	var ice_head: HBoxContainer = plan_head.call(tr("ICE difficulty (0-%d):") % cap, StatIcon.ICE)
	var ice_label := ice_head.get_child(1) as Label
	ice_label.mouse_filter = Control.MOUSE_FILTER_PASS
	ice_label.tooltip_text = UiTip.fold(tr("ICE is the difficulty ladder: each level adds a rule against the Cell. Clear a level to unlock the next one for this corporation."))
	setup.body.add_child(ice_head)
	var ice_spin := SpinBox.new()
	ice_spin.name = "IceSpin"
	ice_spin.min_value = 0
	ice_spin.max_value = cap
	ice_spin.value = 0
	var ice_row := HBoxContainer.new()
	ice_row.name = "IceRow"
	ice_row.add_theme_constant_override("separation", UiTheme.SP_M)
	ice_row.add_child(ValueStepper.new(ice_spin, "Ice"))
	var ice_text := _para(_ice_description(0))
	ice_text.name = "IceText"
	ice_text.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	ice_row.add_child(ice_text)
	setup.body.add_child(ice_row)
	ice_spin.value_changed.connect(func(v: float) -> void: ice_text.text = _ice_description(int(v)))
	corp_pick.tile_chosen.connect(func(i: int) -> void:
		var corp_cap := RunManager.ice_cap(corps[i].id)
		ice_spin.max_value = corp_cap
		ice_label.text = (tr("ICE difficulty (0-%d):") % corp_cap).to_upper())
	# HOME SERVER: the variants, the open ones first.
	var variants := RunManager.available_home_variants()
	var home_tiles: Array[Dictionary] = []
	var locked_homes: Array[Resource] = []
	for v in variants:
		home_tiles.append({"name": TextDb.t(v, "display_name"), "icon": StatIcon.HOME, "tip": TextDb.t(v, "description")})
	for id in lookup.ids_of_class(&"HomeServerVariantData"):
		var v := lookup.get_content(id) as HomeServerVariantData
		if v != null and not variants.has(v):
			locked_homes.append(v)
	locked_homes.sort_custom(locked_order)
	for res in locked_homes:
		var u := CampaignRules.unlock_for(lookup, res)
		home_tiles.append({"name": TextDb.t(res, "display_name"), "icon": StatIcon.HOME, "locked": true, "unlock": unlock_words.call(u),
			"tip": "%s %s" % [TextDb.t(res, "description"), unlock_tip.call(u)]})
	setup.body.add_child(plan_head.call(tr("Home server:"), StatIcon.HOME))
	var home_pick := PlanningPicker.new(home_tiles, 0, HOME_TILE)
	home_pick.name = "HomePicker"
	home_pick.value = pick_default.call(variants, RunManager.DEFAULT_HOME)
	home_pick.refused.connect(refused_note.bind(home_pick))
	setup.body.add_child(home_pick)
	# CREW: the first operative's class, as portraits.
	var classes := RunManager.available_classes()
	var class_tiles: Array[Dictionary] = []
	var locked_classes: Array[Resource] = []
	for cls in classes:
		class_tiles.append({"name": TextDb.t(cls, "display_name"), "class": cls.id, "tip": TextDb.t(cls, "description")})
	for id in lookup.ids_of_class(&"ClassData"):
		var cls := lookup.get_content(id) as ClassData
		if cls != null and not classes.has(cls):
			locked_classes.append(cls)
	locked_classes.sort_custom(locked_order)
	for res in locked_classes:
		var u := CampaignRules.unlock_for(lookup, res)
		class_tiles.append({"name": TextDb.t(res, "display_name"), "class": res.get("id"), "locked": true, "unlock": unlock_words.call(u),
			"tip": "%s %s" % [TextDb.t(res, "description"), unlock_tip.call(u)]})
	setup.body.add_child(plan_head.call(tr("Crew:"), StatIcon.OPERATIVE))
	var class_pick := PlanningPicker.new(class_tiles, 0, CREW_TILE, CREW_SWATCH)
	class_pick.name = "ClassPicker"
	class_pick.value = pick_default.call(classes, RunManager.DEFAULT_CLASS)
	class_pick.refused.connect(refused_note.bind(class_pick))
	setup.body.add_child(class_pick)
	# The city seed (ART-10 4C, audit P3: the words say what it does, with a tooltip).
	var seed_row := HBoxContainer.new()
	seed_row.name = "SeedRow"
	seed_row.add_theme_constant_override("separation", UiTheme.SP_S)
	var seed_label := Chrome.caps_label(tr("City seed (same seed, same city):").to_upper(), UiTheme.LABEL, PaletteSkins.chrome(Palette.NET_CYAN))
	seed_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	seed_label.mouse_filter = Control.MOUSE_FILTER_PASS
	seed_label.tooltip_text = UiTip.fold(tr("The seed builds the campaign's city and runs: the same seed gives the same campaign. Share it with a friend to play the same city."))
	seed_row.add_child(seed_label)
	var seed_spin := SpinBox.new()
	seed_spin.min_value = 0
	seed_spin.max_value = SEED_MAX
	seed_spin.value = 1
	seed_spin.name = "SeedSpin"
	seed_spin.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	seed_row.add_child(seed_spin)
	var next_seed := _icon(_button(tr("Next seed"), func() -> void: seed_spin.value = int(seed_spin.value) + 1), StatIcon.RUNS)
	next_seed.tooltip_text = UiTip.fold(tr("Try the next city: the seed goes up by one."))
	next_seed.name = "SeedNext"
	seed_row.add_child(next_seed)
	setup.body.add_child(seed_row)
	# START: the one verb, a pink vinyl sticker at the head's right end (NEWC-02).
	var start_btn := VerbSticker.new(tr("START"), VerbSticker.Fill.PINK, START_PX, START_TILT)
	start_btn.pre_translated = true
	start_btn.name = "StartCampaign"
	start_btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	start_btn.tooltip_text = UiTip.fold(tr("Start a new campaign with this plan: the target, ICE, home server, crew and city seed."))
	start_btn.pressed.connect(func() -> void:
		var ci := corp_pick.selected()
		var hi := home_pick.selected()
		var ki := class_pick.selected()
		new_campaign(int(seed_spin.value), int(ice_spin.value), variants[hi].id if hi < variants.size() else RunManager.DEFAULT_HOME,
			classes[ki].id if ki < classes.size() else RunManager.DEFAULT_CLASS,
			corps[ci].id if ci < corps.size() else RunManager.DEFAULT_CORPORATION))
	head.add_child(start_btn)
	# Today's run and the share codes, side by side on plain cyan terminals (NEWC-03).
	var code_split := BoxContainer.new()
	code_split.name = "CodesSplit"
	code_split.vertical = Settings.text_scale >= CODES_STACK_FROM
	code_split.add_theme_constant_override("separation", 14)
	box.add_child(code_split)
	var daily := CrtWindow.new(tr("TODAY'S RUN"))
	daily.name = "DailyRun"
	daily.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	daily.size_flags_stretch_ratio = DAILY_SHARE
	daily.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	code_split.add_child(daily)
	var today := Time.get_date_dict_from_system()
	var daily_seed := CampaignCode.daily_seed(today["year"], today["month"], today["day"])
	daily.tag_label.text = "%04d-%02d-%02d" % [today["year"], today["month"], today["day"]]
	for line in daily_lines(daily_seed):
		daily.body.add_child(_label(line))
	var daily_btn := _icon(_button(tr("Daily run"), func() -> void: new_campaign(daily_seed)), StatIcon.PLAY)
	daily_btn.name = "DailyRunButton"
	daily_btn.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	daily.body.add_child(daily_btn)
	var codes := CrtWindow.new(tr("SHARE CODES"))
	codes.name = "ShareCodes"
	codes.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	codes.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	code_split.add_child(codes)
	codes.body.add_child(_para(tr("A share code holds a whole plan: target, ICE, city seed, home server and crew.")))
	# The code row folds away under its toggle (the build's SHARE CODES drawer).
	var code_row := HFlowContainer.new()
	code_row.name = "CodesRow"
	code_row.visible = false
	var code_edit := LineEdit.new()
	code_edit.name = "CodeEdit"
	code_edit.placeholder_text = tr("RC1-corporation-ice-seed-home-class")
	code_edit.custom_minimum_size.x = 360
	# Esc leaves the field (a focused LineEdit would otherwise swallow it).
	code_edit.gui_input.connect(func(ev: InputEvent) -> void:
		if ev.is_action_pressed("ui_cancel") or ev.is_action_pressed("open_settings"):
			code_edit.release_focus()
			code_edit.accept_event()
			UiFocus.focus_first(_panel))
	code_row.add_child(code_edit)
	code_row.add_child(_icon(_button(tr("Start from code"), func() -> void: start_from_code(code_edit.text)), StatIcon.PLAY))
	var codes_toggle := _icon(_button(tr("Enter a share code"), func() -> void:
		code_row.visible = not code_row.visible
		UiFocus.link_layout(_panel)
		if code_row.visible:
			code_edit.grab_focus.call_deferred()), StatIcon.MORE)
	codes_toggle.name = "CodesToggle"
	codes_toggle.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	codes.body.add_child(codes_toggle)
	codes.body.add_child(code_row)
	var lower := HBoxContainer.new()
	lower.add_theme_constant_override("separation", 14)
	box.add_child(lower)
	var menu := CrtWindow.new(tr("CYBERDECK"))
	menu.custom_minimum_size.x = 300
	menu.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	lower.add_child(menu)
	var records := CrtWindow.new(tr("PROFILE // RECORDS"), Palette.CELL_PINK)
	records.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lower.add_child(records)
	if RunManager.has_save():
		menu.body.add_child(_icon(_button(tr("Resume saved campaign"), resume), StatIcon.CONTINUE))
	var p := profile
	records.body.add_child(_para(tr("Profile: %d campaigns started, %d won, %d lost; %d runs completed, %d operatives lost, raids %d/%d; best ICE %s.") % [
		p.campaigns_started, p.campaigns_won, p.campaigns_lost, p.runs_completed, p.operatives_lost, p.raids_won, p.raids_lost, HudStats.ice_value(p.best_ice)]))
	records.body.add_child(_para(ice_records_text()))
	var unlock_names := PackedStringArray()
	for uid in p.unlocks:
		var ud := lookup.get_content(uid) as ProfileUnlockData
		unlock_names.append(TextDb.t(ud, "display_name") if ud != null else String(uid))
	records.body.add_child(_para(tr("Unlocks: %s") % (", ".join(unlock_names) if not unlock_names.is_empty() else tr("none yet (buy them at HQ with campaign Schematics)"))))
	var options_btn := _hint_button(tr("Options"), &"open_settings", open_settings)
	options_btn.name = "OptionsButton"
	menu.body.add_child(_icon(options_btn, StatIcon.SETTINGS))
	# HQ-B (Q9): the Codex is the pause menu's (one Codex); this button opens it there.
	menu.body.add_child(_icon(_button(tr("Codex"), open_codex), StatIcon.CODEX))
	menu.body.add_child(_icon(_button(tr("Back to title"), RunManager.go_to_title), StatIcon.EXIT))
	_as_menu(menu.body)
	_set_panel(box, "start")


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


## HQ-B (M14, HQ redesign direction B "THE HAND", designer rulings 2026-10-05): the HQ is the
## live 3D city at the RAID band (the raid setup's view, 6w), and the Grid page folds into it.
## Over the city: the raid's paper work order at the top left while one is pending (RAID
## SETUP under it), the hand of cards along the foot behind its CREW / MARKET / DEFENCE tabs,
## the selected Site's card at the right over the one pink sticker slot (JACK IN), and the
## minimap with the folded MAP KEY at the top right. Click a Site (or step them with the pad
## on the map), pick the runner's card, press JACK IN. Every action goes through the rules.
## The DEFENCE tab with a raid pending is the raid setup on this same page (`show_raid`).
func show_hq() -> void:
	if RunManager.campaign == null:
		show_start()
		return
	# Back from the raid setup (B, the CREW tab, a page that left it): the crew's hand.
	if hand_tab == HandTab.DEFENCE and not RunManager.campaign.pending_raids.is_empty():
		hand_tab = HandTab.CREW
	_build_hq_page("hq")


## HQ-B: builds the HQ page as `page_name`: "hq" (the CREW / MARKET / DEFENCE hands) or "raid"
## (the DEFENCE hand as the raid setup, in place: the same city, camera, card row and slot).
func _build_hq_page(page_name: String) -> void:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var raid_mode := page_name == "raid"
	# The camera stays where the player left it when the same page rebuilds (a pick, a buy, a tab).
	var keep := _city_frame() if panel_name in HQ_PAGES and city_overlay != null and is_instance_valid(city_overlay) else {}
	_sync_previews()
	# ANIM-R4 H10: what the pages this one leads to need is made ahead.
	AudioDirector.prewarm_music(["raid", "netrun", "combat"], c.corporation_id)
	if not raid_mode:
		_warm_previews.call_deferred()
	_grid_chips.clear()
	_jack_button = null
	var launchable := RunManager.launchable_sites()
	launchable.append_array(RunManager.patrol_sites())
	if selected_site == &"" or CampaignRules.site_data(corp, selected_site) == null:
		selected_site = launchable[0].id if not launchable.is_empty() else c.grid.home_site_id
	# HQ-B (e): a saved run waiting: its Site is the selection (its resume jacks along that link).
	if RunManager.has_active_run() and not raid_mode and CampaignRules.site_data(corp, resume_site()) != null:
		selected_site = resume_site()
	if selected_op() != null:
		selected_operative = selected_op().id
	var pending := RunManager.pending_raid()
	var raid: RaidData = CampaignRules.raid_data(pending, RunManager.lookup()) if not pending.is_empty() else null
	var projection: RaidResolver.RaidResult = RunManager.project_raid() if not pending.is_empty() else null
	var page := Control.new()
	page.name = "HqPage"
	hq_page = page
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	page.size_flags_vertical = Control.SIZE_EXPAND_FILL
	# The map cursor: the pad's place on the map (left / right step the Sites, the map follows).
	var cursor := HqMapCursor.new()
	cursor.name = "MapCursor"
	cursor.stepped.connect(_cursor_step)
	cursor.tooltip_text = UiTip.fold(UiTip.for_input(tr("The city: click a Site to select it; the wheel zooms, a drag pans."),
		tr("The city: left and right step through the Sites; down to the hand.")))
	page.add_child(cursor)
	# The work order while a raid is pending (corp paper), RAID SETUP under it; in the setup the
	# whole forecast with the Cell's stamp.
	if raid != null:
		# It scrolls inside its room at big text (the map keeps its part).
		var order := VBoxContainer.new()
		order.name = "WorkOrder"
		order.add_theme_constant_override("separation", 8)
		order.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var paper_scroll := ScrollContainer.new()
		paper_scroll.name = "WorkOrderPaper"
		paper_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		paper_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
		paper_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
		order.add_child(paper_scroll)
		var paper := VBoxContainer.new()
		paper.name = "WorkOrderBox"
		paper.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		paper_scroll.add_child(paper)
		paper.add_child(_raid_card(raid, pending, projection, not raid_mode))
		var setup := MenuChip.new(tr("RAID SETUP"), "[%s]" % Settings.hint(&"toggle_ring").strip_edges().trim_prefix("[").trim_suffix("]"), Palette.CELL_PINK)
		setup.name = "RaidSetup"
		setup.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		setup.pressed.connect(show_raid)
		setup.tooltip_text = UiTip.fold(tr("RAID SETUP: a raid is coming along the red pencil routes: set up the defence."))
		setup.visible = not raid_mode
		order.add_child(setup)
		if raid_mode:
			order.add_child(_raid_intro())
		page.add_child(order)
	# The hand: its tabs and the cards of the deck picked.
	page.add_child(_hand_tabs())
	var hand := ScrollContainer.new()
	hand.name = "Hand"
	hand.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	hand.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
	hand.follow_focus = true
	hand.mouse_filter = Control.MOUSE_FILTER_PASS
	var cards := HBoxContainer.new()
	cards.name = "HandCards"
	cards.alignment = BoxContainer.ALIGNMENT_BEGIN
	cards.add_theme_constant_override("separation", roundi(HqLayout.GAP * 2.0 * HqLayout.object_scale(Settings.text_scale)))
	cards.custom_minimum_size.y = (HqLayout.CARD.y + HqLayout.LIFT) * HqLayout.object_scale(Settings.text_scale)
	hand.add_child(cards)
	page.add_child(hand)
	if raid_mode:
		_fill_defence_hand(cards)
	else:
		match hand_tab:
			HandTab.MARKET:
				_fill_market_hand(cards)
			HandTab.DEFENCE:
				_fill_armory_hand(cards)
			_:
				_fill_crew_hand(cards, launchable)
	for k in cards.get_children():
		(k as Control).size_flags_vertical = Control.SIZE_SHRINK_END  # on the hand's foot
	# The card column: the selected Site's card (its facts, IF CLEARED, its actions); in the
	# setup THREAT INTEL and YOUR NETWORK. It scrolls inside its room at big text (the minimap
	# and the key keep theirs).
	var column := ScrollContainer.new()
	column.name = "CardColumn"
	column.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	column.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
	column.follow_focus = true
	column.mouse_filter = Control.MOUSE_FILTER_PASS
	var stack := VBoxContainer.new()
	stack.name = "CardStack"
	stack.alignment = BoxContainer.ALIGNMENT_END
	stack.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	stack.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Room round the cards for their glow and scrim (the scroll clips at its edge).
	var card_margin := MarginContainer.new()
	card_margin.name = "CardMargin"
	card_margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card_margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		card_margin.add_theme_constant_override(side, roundi(RaidHolo.SCRIM_OUT * 2.0))
	card_margin.add_child(stack)
	column.add_child(card_margin)
	var site := CampaignRules.site_data(corp, selected_site)
	if raid_mode:
		_defence_cards(stack, raid, pending, projection)
	elif site != null:
		var card := _site_card(site, launchable, c.living_operatives(), _node_choices())
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		stack.add_child(card)
	page.add_child(column)
	# The verb slot: the one pink sticker (JACK IN for a runnable Site, a saved run's resume;
	# START DEFENSE with Speed / Skip in the setup).
	var verb_sites: Array[SiteData] = []
	if not raid_mode:
		verb_sites = launchable
	page.add_child(_verb_slot(site if not raid_mode else null, verb_sites, raid_mode))
	# The pirate radio as one ON AIR line (Q7) at the foot, under the hand.
	var dj_line := Dialogue.line("dj", RC.Voice.NARRATOR, c.corporation_id, &"", c.runs_started + c.runs_completed * 7)
	var dj_text := Dialogue.voice_text(dj_line) if dj_line != null else tr("lo-fi loop: HQ")
	var ticker := OnAirTicker.new(PackedStringArray([dj_text, tr("vs %s | ICE %d%s") % [TextDb.t(corp, "display_name"), c.ice_level, tr(" | ASSIST") if c.is_assisted() else ""]]))
	ticker.name = "OnAir"
	ticker.tooltip_text = UiTip.fold("%s\n%s" % [dj_text, campaign_code_line()])
	ticker.mouse_filter = Control.MOUSE_FILTER_PASS
	page.add_child(ticker)
	_set_panel(page, page_name)
	page.resized.connect(_place_hq)
	for piece in page.get_children():
		if piece is Control:
			(piece as Control).minimum_size_changed.connect(_queue_place_hq)
	for deep in ["WorkOrder/WorkOrderPaper/WorkOrderBox", "Hand/HandCards", "CardColumn/CardMargin/CardStack"]:
		var n := page.get_node_or_null(deep) as Control
		if n != null:
			n.minimum_size_changed.connect(_queue_place_hq)
	# The map on the city: every Site as its v4 marker, the Cell's nodes as their raid sockets
	# on uplink pads; a pending raid's routes as red pencil: dashed (a what-if) at the HQ, solid
	# with each node's forecast in the setup.
	var g := hq_graph(projection if raid_mode else null)
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, keep.get("anchor", HQ_ANCHOR), keep.get("scale", 1.0),
		keep.get("focus", Vector2.INF))
	city_overlay.selected_id = selected_site
	city_overlay.boss_exploits = Vector2i(c.exploits.size(), cfg.min_exploits_for_breach)
	if raid_mode:
		city_overlay.node_clicked.connect(func(id: StringName) -> void:
			if RunManager.campaign.grid.is_claimed(id):
				select_target(id))
	else:
		city_overlay.node_clicked.connect(select_site)
	_mount_hq_routes(projection, raid_mode)
	wireframe.city.set_city_life(GridCityLife.of(c, corp, cfg))
	_mount_hq_map_tools(page)
	hq_map_mode(true)
	_place_hq()
	_sync_hq_band()
	if keep.is_empty():
		_hq_fit_pending = true
		_hq_fit_passes = 0
		if not get_tree().process_frame.is_connected(fit_hq_map):
			get_tree().process_frame.connect(fit_hq_map, CONNECT_ONE_SHOT)
	else:
		wireframe.ease_camera()
	if raid_mode:
		_register_raid_drops(c.grid.claimed_ids(), hand)
		set_page_prompts(prompts_for("raid") + [[&"cycle_target", KEY_PROMPT]])
		# ANIM-R1 M2: the playout's zoomed map baked behind the setup, so START DEFENSE opens onto
		# a city that is already there.
		_prebake_playout.call_deferred(c, null)
	else:
		_register_hq_drops_b(launchable)
		tell_new_beats()  # HQ-B (f, Q8): a beat revealed since the HQ last showed: corp news
		_hq_idle()
	_link_hq_focus(page)
	if _hq_focus != "":
		_focus_named.call_deferred(_hq_focus)
		_hq_focus = ""
	if _last_warned_raid != String(pending.get("raid_id", "")) and not pending.is_empty():
		_last_warned_raid = String(pending.get("raid_id", ""))
		Dialogue.raid_warning(c.corporation_id, StringName(String(pending.get("raid_id", ""))), c.raids_won + c.raids_lost, "raid")


## H23 S5 / parity RAID-02: what the raid is and what to do, in one plain sentence, on a dark
## plate; HQ-B (c): under the work order in the setup.
func _raid_intro() -> Control:
	var intro := _para(TextDb.ui_text("ui.raid_intro"))
	intro.name = "RaidIntro"
	intro.add_theme_color_override("font_color", Palette.PAPER)
	var intro_box := PanelContainer.new()
	intro_box.name = "RaidIntroBox"
	intro_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var plate := StyleBoxFlat.new()
	plate.bg_color = Color(Palette.SCRIM, RAID_INTRO_PLATE_ALPHA)
	plate.set_content_margin_all(UiTheme.SP_S)
	intro_box.add_theme_stylebox_override(&"panel", plate)
	intro_box.add_child(intro)
	return intro_box


## HQ-B: the pages that are the HQ (its hands, and the DEFENCE hand's raid setup).
const HQ_PAGES: Array[String] = ["hq", "raid"]


## HQ-B: the one call point where the HQ (and its raid setup) turns the city's map mode on
## (designer ruling 2026-10-05: raid and netrun views grey the city and lower its opacity so the
## nodes and links pop). S-MAPVIEW's map mode follows the view band (on at RAID / NETRUN): the HQ
## holds the RAID band, zoomed out past the raid range the GRID band (Q4: the whole city, map
## mode off). The HQ draws no dimming of its own.
func hq_map_mode(on: bool) -> void:
	if on:
		_sync_hq_band()


## HQ-B: the hand's decks behind the tabs.
enum HandTab { CREW, MARKET, DEFENCE }
## The deck the hand shows (kept across rebuilds).
var hand_tab: int = HandTab.CREW
## The tabs' words (translation keys).
const TAB_WORDS: Array[String] = ["CREW", "MARKET", "DEFENCE"] # TR
## From this text scale the tabs show their word only (the count in the tooltip).
const TAB_LINE_BELOW := MapLegend.FOLD_SCALE
## Where the camera frames the HQ's map before its fit (screen share), and the frame waiting.
const HQ_ANCHOR := Vector2(0.45, 0.42)
var _hq_fit_pending: bool = false
## A control to focus once the HQ page is rebuilt (the map cursor after a step, a card).
var _hq_focus: String = ""
## The map tools on the HQ page: the minimap terminal and the folded MAP KEY line.
var hq_minimap: CityMinimap = null
var hq_legend: MapLegend = null
## HQ-B: the HQ page on screen (its name may take a suffix while the last one is freed).
var hq_page: Control = null


## The city camera's frame now: {scale, focus, anchor}.
func _city_frame() -> Dictionary:
	var city := wireframe.city
	return {"scale": city.scale.x, "focus": city.focus_grid if city.focus_grid != Vector2.INF else Vector2.INF, "anchor": city.focus_anchor}


## HQ-B: the tabs, one MenuChip each with its count under the word (CREW 3 / 4, MARKET the
## Schematics, DEFENCE the raids pending or the Armory); the open one is filled. LB / RB
## (Q / E) switch them.
func _hand_tabs() -> VBoxContainer:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var tabs := VBoxContainer.new()
	tabs.name = "HandTabs"
	tabs.add_theme_constant_override("separation", 6)
	tabs.alignment = BoxContainer.ALIGNMENT_END
	var lines := ["%d / %d" % [c.living_operatives().size(), c.roster.size()], str(c.schematics),
		(tr("RAID %d") % c.pending_raids.size()) if not c.pending_raids.is_empty() else (tr("ARMORY %d/%d") % [c.armory.size(), cfg.armory_capacity])]
	var tips := [UiTip.for_input(tr("CREW: your operatives as cards. Pick the runner, drag a card onto one of your nodes to station them."),
			tr("CREW: your operatives as cards. Pick the runner; pick a card up and move it onto one of your nodes to station them.")),
		tr("MARKET: recruits, the next run's boosts and Profile unlocks, paid in Schematics."),
		tr("DEFENCE: the Armory's defence cards; with a raid pending, the raid setup.")]
	for i in TAB_WORDS.size():
		var hot := i == HandTab.DEFENCE and not c.pending_raids.is_empty()
		# At big text the count under the word goes to the tooltip (the column keeps the hand's
		# height; the top bar shows the same numbers).
		var small := Settings.text_scale < TAB_LINE_BELOW - 0.001
		var tab := MenuChip.new(tr(TAB_WORDS[i]), lines[i] if small else "", Palette.CELL_PINK if hot else PaletteSkins.chrome(Palette.NET_CYAN))
		tab.pre_translated = true
		tab.name = "Tab_%s" % TAB_WORDS[i]
		tab.plate = &"tab"  # ui31.tabs: the open one filled
		tab.refit()
		tab.selected = i == hand_tab
		tab.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tab.alignment = HORIZONTAL_ALIGNMENT_CENTER
		tab.tooltip_text = UiTip.fold(tips[i] if small else "%s (%s)" % [tips[i], lines[i]])
		tab.pressed.connect(open_hand.bind(i))
		tabs.add_child(tab)
	return tabs


## HQ-B: shows deck `tab` in the hand (CREW, MARKET, DEFENCE). DEFENCE with a raid pending is
## the raid setup.
func open_hand(tab: int) -> void:
	if tab == HandTab.DEFENCE and RunManager.campaign != null and not RunManager.campaign.pending_raids.is_empty():
		hand_tab = tab
		show_raid()
		return
	hand_tab = tab
	_hq_focus = "Tab_%s" % TAB_WORDS[tab]
	if panel_name in HQ_PAGES:
		wireframe.hold_camera()
	show_hq()


## HQ-B: the crew as cards in roster order, the flatlined last (Q12); the runner's card is
## lifted; a card that can't run the selected Site is greyed with the rule's reason. A press
## picks the runner (VIEW LOADOUT and DAEMONS follow); a drag stations them on one of your
## nodes, brings them back on CORE, or picks them for a Site.
func _fill_crew_hand(cards: HBoxContainer, launchable: Array[SiteData]) -> void:
	var c := RunManager.campaign
	var lookup := RunManager.lookup()
	var order: Array[OperativeState] = []
	for op in c.roster:
		if op.alive:
			order.append(op)
	for op in c.roster:
		if not op.alive:
			order.append(op)
	var runnable := false
	for s in launchable:
		if s.id == selected_site:
			runnable = true
	for op in order:
		var where := CampaignRules.stationed_site(c, op.id)
		var card := CrewHandCard.new(op.class_id, op.id, op.name, op.rank)
		card.name = "Crew_%s" % op.id
		card.dead = not op.alive
		if not op.alive:
			card.status = tr(CrewHandCard.FLATLINED)
			card.status_color = Palette.TEXT_MID
		elif where != &"":
			card.status = tr(CrewHandCard.ON_SITE) % site_name(where).to_upper()
			card.status_color = PaletteSkins.chrome(Palette.NET_CYAN)
		else:
			card.status = tr(CrewHandCard.READY)
		if op.alive and runnable:
			card.refusal = _pick_error(op.id, selected_site)
			if card.refusal == DropLayer.SKIP:
				card.refusal = ""
		card.picked = op.alive and op.id == selected_operative
		var cls := lookup.get_content(op.class_id) as ClassData
		card.tooltip_text = UiTip.fold("%s R%d, %s. HP %d/%d, DECK %d, DAEMONS %d.%s%s%s" % [op.name, op.rank, TextDb.t(cls, "display_name") if cls != null else String(op.class_id),
			op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size(),
			(" " + tr("Stationed on %s.") % site_name(where)) if where != &"" else "",
			("\n" + card.refusal) if card.refusal != "" else "",
			("\n" + UiTip.for_input(tr("Press to pick them as the runner. Drag the card onto one of your nodes to station them there, or onto CORE to bring them back."),
				tr("Press to pick them as the runner. Pick the card up and move it onto one of your nodes to station them there, or onto CORE to bring them back."))) if op.alive else ""])
		card.disabled = not op.alive
		var oid := op.id
		card.pressed.connect(pick_runner.bind(oid))
		if op.alive:
			drops.add_source(card, {"kind": "crew", "op": op.id, "motion": &"crew_assign", "prefer": where})  # a press picks the runner; a drag or the pick-up key carries
		cards.add_child(card)
		if op.alive and where != &"" and op.id == selected_operative:
			var recall_chip := MenuChip.new(tr("RECALL"), site_name(where).to_upper())
			recall_chip.name = "Recall_%s" % op.id
			recall_chip.pre_translated = true
			recall_chip.size_flags_vertical = Control.SIZE_SHRINK_END
			recall_chip.tooltip_text = UiTip.fold(tr("Bring %s back from %s.") % [op.name, site_name(where)])
			recall_chip.pressed.connect(recall.bind(oid))
			cards.add_child(recall_chip)


## HQ-B: picks operative `operative_id` as the runner (the lifted card); nothing starts.
func pick_runner(operative_id: StringName) -> void:
	select_operative(operative_id)
	_hq_focus = "Crew_%s" % operative_id
	if panel_name == "hq":
		wireframe.hold_camera()
		show_hq()


## HQ-B: the Black Market as the hand (direction_B_market.jpg): HIRE cards for the recruits,
## the next run's boosts as stickers over gold price tags, Profile unlocks as terminal chips,
## each group under its caption. A press buys (the item flies to where it went); a drag onto
## its target buys too (a recruit onto the CREW tab, a boost onto the next run's kit).
func _fill_market_hand(cards: HBoxContainer) -> void:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var recruits := _market_group(cards, "Recruits", tr("RECRUIT"))
	for cls in RunManager.available_classes():
		var cid := cls.id
		var pay := {"kind": "recruit", "cls": cid, "motion": &"crew_assign"}
		var price := CampaignRules.rookie_price(c, cfg)
		var card := CrewHandCard.new(cid, &"", TextDb.t(cls, "display_name"), 0)
		card.hire = true
		card.name = "Recruit_%s" % cls.id
		card.status = tr("%d SCHEMATICS") % price
		card.status_color = Palette.RESIST_GOLD
		card.tooltip_text = UiTip.fold("%s\n%s" % [TextDb.t(cls, "description"), UiTip.for_input(tr("Press to hire (it joins the crew), or drag it onto the CREW tab."),
			tr("Press to hire (it joins the crew), or pick it up and move it onto the CREW tab."))])
		var ref: Array = [card]
		card.pressed.connect(func() -> void: _market_buy(ref[0], pay, func() -> void: recruit(cid)))
		drops.add_source(card, pay)
		recruits.add_child(card)
	var boosts := _market_group(cards, "Boosts", tr("NEXT RUN'S BOOSTS"))
	for b in cfg.netrun_boosts:
		if b == null:
			continue
		var bid := b.id
		var pay := {"kind": "boost", "boost": bid}
		var stack := VBoxContainer.new()
		stack.alignment = BoxContainer.ALIGNMENT_END
		stack.add_theme_constant_override("separation", 4)
		var sticker := VerbSticker.new(TextDb.t(b, "display_name").to_upper(), VerbSticker.Fill.BLUE, BOOST_STICKER_PX, BOOST_STICKER_TILT)
		sticker.pre_translated = true
		sticker.name = "Boost_%s" % b.id
		sticker.tooltip_text = UiTip.fold(TextDb.t(b, "description"))
		sticker.disabled = c.pending_boosts.has(b.id) or c.schematics < b.cost
		var ref: Array = [sticker]
		sticker.pressed.connect(func() -> void: _market_buy(ref[0], pay, func() -> void: buy_boost(bid)))
		drops.add_source(sticker, pay)
		stack.add_child(sticker)
		var tag := PriceTag.new(tr("%d SCHEMATICS") % b.cost)
		tag.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		stack.add_child(tag)
		boosts.add_child(stack)
	# ANIM-4: the next run's kit (always shown: the boosts' drop target).
	var queued := PackedStringArray()
	for bid in c.pending_boosts:
		for b in cfg.netrun_boosts:
			if b != null and b.id == bid:
				queued.append(TextDb.t(b, "display_name"))
	var queue := Label.new()
	queue.name = "QueuedBoosts"
	queue.text = tr("queued: %s") % (", ".join(queued) if not queued.is_empty() else "-")
	queue.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	queue.mouse_filter = Control.MOUSE_FILTER_PASS
	queue.size_flags_vertical = Control.SIZE_SHRINK_END
	queue.tooltip_text = UiTip.fold(UiTip.for_input(tr("The boosts bought for the next run. Drag a boost here to buy it."), tr("The boosts bought for the next run. Pick a boost up and move it here to buy it.")))
	boosts.add_child(queue)
	var unlocks := _market_group(cards, "Unlocks", tr("PROFILE UNLOCKS"))
	# Two rows of chips (one column of them ran up over the map), as many columns as they need.
	var col := GridContainer.new()
	col.name = "UnlockGrid"
	col.add_theme_constant_override("h_separation", 6)
	col.add_theme_constant_override("v_separation", 6)
	col.size_flags_vertical = Control.SIZE_SHRINK_END
	unlocks.add_child(col)
	var any := false
	for id in lookup.ids_of_class(&"ProfileUnlockData"):
		var u := lookup.get_content(id) as ProfileUnlockData
		# Free unlocks (REBEL_CELL) open by themselves once their requirements are met.
		if u == null or RunManager.profile.has_unlock(u.id) or u.schematic_cost == 0:
			continue
		any = true
		var uid := u.id
		var chip := MenuChip.new(TextDb.t(u, "display_name"), tr("%d SCHEMATICS") % u.schematic_cost)
		chip.pre_translated = true
		chip.name = "Unlock_%s" % u.id
		chip.tooltip_text = UiTip.fold(TextDb.t(u, "description"))
		chip.disabled = c.schematics < u.schematic_cost
		chip.pressed.connect(purchase_unlock.bind(uid))
		col.add_child(chip)
	col.columns = maxi(1, ceili(col.get_child_count() / float(UNLOCK_ROWS)))
	if not any:
		var done := Label.new()
		done.text = tr("everything unlocked")
		col.add_child(done)


## The boost stickers' lettering (px at 1.0) and tilt (degrees).
const BOOST_STICKER_PX := 22.0
const BOOST_STICKER_TILT := -2.0
## The Profile unlocks' rows in the market hand.
const UNLOCK_ROWS := 2


## A captioned group in the market hand (`id` names it), returned for its items.
func _market_group(cards: HBoxContainer, id: String, caption: String) -> HBoxContainer:
	var box := VBoxContainer.new()
	box.name = id
	box.add_theme_constant_override("separation", 4)
	var cap := Label.new()
	cap.name = "Caption"
	cap.text = caption
	cap.add_theme_font_override("font", Palette.mono())
	cap.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	cap.add_theme_color_override("font_color", PaletteSkins.chrome(Palette.NET_CYAN))
	box.add_child(cap)
	var row := HBoxContainer.new()
	row.name = "Items"
	row.add_theme_constant_override("separation", roundi(HqLayout.GAP * HqLayout.object_scale(Settings.text_scale)))
	row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	box.add_child(row)
	cards.add_child(box)
	return row


## HQ-B (b): the DEFENCE hand with no raid pending: the Armory's defence cards (they deploy in
## a raid's setup), or what the Armory is when it is empty.
func _fill_armory_hand(cards: HBoxContainer) -> void:
	var c := RunManager.campaign
	var lookup := RunManager.lookup()
	var seen := {}
	for aid in c.armory:
		if seen.has(aid):
			continue
		seen[aid] = true
		var data := lookup.get_content(aid) as DefenseAssetData
		var card := AssetCard.new(aid, TextDb.t(data, "display_name") if data != null else String(aid), data.integrity if data != null else 0, c.armory.count(aid))
		card.set_effect(data)
		card.name = "Armory_%s" % aid
		card.tooltip_text = UiTip.fold("%s\n%s\n%s" % [TextDb.t(data, "description") if data != null else "", card.numbers_tip(), armory_tip()])
		card.focus_mode = Control.FOCUS_ALL
		cards.add_child(card)
	if c.armory.is_empty():
		var empty := _para(tr("Armory empty: runs bank assets from their drops."))
		empty.name = "ArmoryEmpty"
		empty.custom_minimum_size.x = HqLayout.CARD.x * 2.0
		cards.add_child(empty)


## HQ-B: the one pink sticker slot (bottom right): JACK IN for a runnable Site with the picked
## runner (the run's resume while a saved run waits); its system word under it. Named "Launch".
func _verb_slot(site: SiteData, launchable: Array[SiteData], raid_mode: bool = false) -> Control:
	var c := RunManager.campaign
	var slot := VBoxContainer.new()
	slot.name = "VerbSlot"
	slot.alignment = BoxContainer.ALIGNMENT_END
	slot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	slot.add_theme_constant_override("separation", 4)
	if raid_mode:
		_defence_verb(slot)
		return slot
	var runnable := false
	for s in launchable:
		if site != null and s.id == site.id:
			runnable = true
	var resume := RunManager.has_active_run()
	var v := {"verb": VERB_JACK_IN, "price": -1} if resume else site_verb(site, runnable)
	var verb := String(v.get("verb", ""))
	if verb == "":
		return slot
	var sticker := VerbSticker.new(tr(verb), VerbSticker.Fill.PINK, VERB_STICKER_PX, VERB_STICKER_TILT)
	sticker.pre_translated = true
	sticker.name = VERB_NODE_NAMES.get(verb, "Verb")
	sticker.size_flags_horizontal = Control.SIZE_SHRINK_END
	var sid: StringName = site.id if site != null else &""
	if verb == VERB_JACK_IN:
		sticker.add_to_group(Fx.JACK_FOCUS_GROUP)
		_jack_button = sticker
		if resume:
			sticker.tooltip_text = UiTip.fold(tr("JACK IN: back into the run you left."))
			sticker.pressed.connect(resume_run)
		else:
			sticker.tooltip_text = UiTip.fold(tr("JACK IN to %s: start a %s here with %s.") % [site_name(sid), tr(CampaignRules.run_kind_for(c, site)), selected_op().name if selected_op() != null else "-"])
			sticker.pressed.connect(press_verb.bind(v, sid))
			sticker.disabled = selected_op() == null
	else:
		sticker.tooltip_text = UiTip.fold(verb_tip(v, site))
		sticker.pressed.connect(press_verb.bind(v, sid))
	slot.add_child(sticker)
	# Q11: the price in a gold tag under the sticker (bible 1.2: never on the sticker).
	if int(v.get("price", -1)) >= 0:
		var tag := PriceTag.new(tr(PRICE_WORDS) % int(v["price"]))
		tag.name = "VerbPrice"
		tag.size_flags_horizontal = Control.SIZE_SHRINK_END
		slot.add_child(tag)
	if verb != VERB_JACK_IN:
		return slot
	var word := Label.new()
	word.name = "SystemWord"
	word.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	word.text = jack_system_word(site)
	word.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	# One line under the sticker (a system word, not a sentence): cut with an ellipsis, whole in
	# its tooltip.
	word.clip_text = true
	word.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	word.mouse_filter = Control.MOUSE_FILTER_PASS
	word.tooltip_text = word.text
	word.custom_minimum_size.y = Palette.mono().get_height(UiTheme.font_px(UiTheme.CAPTION))  # a clipped Label reports no height
	word.add_theme_font_override("font", Palette.mono())
	word.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	word.add_theme_color_override("font_color", Color(Palette.PAPER, HudSkin.SYSTEM_WORD_ALPHA * 2.0))
	slot.add_child(word)
	# Q3: a raid pending fires mid-run (the rule kept); the system word says so, in the raid's pink.
	if not resume and not c.pending_raids.is_empty():
		var warn := Label.new()
		warn.name = "RaidMidRun"
		warn.text = "> " + tr(RAID_MID_RUN)
		warn.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		warn.add_theme_font_override("font", Palette.mono())
		warn.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
		warn.add_theme_color_override("font_color", Palette.CELL_PINK)
		warn.tooltip_text = UiTip.fold(tr("A raid is pending: JACK IN now and it hits your network as an interlude in the run (or defend first: RAID SETUP)."))
		warn.mouse_filter = Control.MOUSE_FILTER_PASS
		slot.add_child(warn)
	return slot


## The verb stickers' node names (tests and the pad find them by these).
const VERB_NODE_NAMES := {VERB_JACK_IN: "Launch", VERB_CLAIM: "Claim", VERB_REPAIR: "Repair", VERB_UPGRADE: "Upgrade", VERB_PATCH: "Patch"}


## What verb `v` does on `site`, in its tooltip.
func verb_tip(v: Dictionary, site: SiteData) -> String:
	var c := RunManager.campaign
	match String(v.get("verb", "")):
		VERB_CLAIM:
			return tr("CLAIM %s: build a %s here (%d Schematics). It joins your network and defends in raids.") % [site_name(site.id), _display(StringName(String(v.get("node", "")))), int(v["price"])]
		VERB_REPAIR:
			return tr("REPAIR %s: bring the DOWN node back online (%d Schematics).") % [site_name(site.id), int(v["price"])]
		VERB_UPGRADE:
			return tr("UPGRADE %s: one level up from level %d (%d Schematics).") % [site_name(site.id), c.grid.upgrade_level_of(site.id), int(v["price"])]
		VERB_PATCH:
			return tr("PATCH CORE: +%d integrity (%d Schematics).") % [int(v.get("points", 0)), int(v["price"])]
	return ""


## The verb sticker's lettering (px at 1.0) and tilt (degrees).
const VERB_STICKER_PX := 46.0
const VERB_STICKER_TILT := -3.0
## Q3: the system word while a raid waits (a translation key).
const RAID_MID_RUN := "raid incoming mid-run" # TR


## HQ-B (bible 1.3: a word over its system word): what JACK IN does, as the deck types it:
## `> jack --from <owned end> --to <Site>`; with a raid pending, `raid incoming mid-run` (Q3).
func jack_system_word(site: SiteData) -> String:
	var at := site
	if RunManager.has_active_run():
		# The resume jacks along the saved run's own link.
		at = CampaignRules.site_data(RunManager.corporation, resume_site())
	if at == null:
		return ""
	var link := RunManager.jack_link(at.id)
	return "> jack --from %s --to %s" % [String(link.get("from", "")), String(link.get("to", site_name(at.id)))]


## HQ-B (e): the Site a saved run was started on (&"" with none waiting): its resume jacks along
## that Site's link on the HQ's city, as every netrun start does.
func resume_site() -> StringName:
	return RunManager.netrun.run.site_id if RunManager.has_active_run() else &""


## HQ-B (e): JACK IN while a saved run waits: back into it (one run at a time) with the same
## link jack (4.6) from its Site (the deck monitor's CRT push is gone with the deck).
func resume_run() -> void:
	if not RunManager.scene_change_pending():
		RunManager.go_to_netrun(Callable(), resume_site())


## HQ-B: the HQ's map graph: every Site as the Grid draws it (v4 markers, links, threat
## arrows), the Cell's nodes as their raid sockets (on uplink pads, with stationed beacons)
## and the assets placed on them.
func hq_graph(projection: RaidResolver.RaidResult = null) -> Dictionary:
	var c := RunManager.campaign
	var g := grid_graph()
	for n: Dictionary in g["nodes"]:
		n["threat_corp"] = String(c.corporation_id)
		if not c.grid.is_claimed(n["id"]):
			continue
		n["assets"] = c.grid.assets_on(n["id"])
		# In the raid setup each node of the Cell's carries its forecast (3A: the ring, the tag).
		var res: Dictionary = projection.nodes.get(String(n["id"]), {}) if projection != null else {}
		if not res.is_empty():
			var outcome := shown_outcome(String(res["outcome"]), n["id"] == c.grid.home_site_id, int(res["after"]))
			n["color"] = Palette.CELL_ACID if outcome == "holds" else Palette.CELL_PINK
			n["result"] = "%s → %s %s" % [res["before"], res["after"], outcome_word(outcome)]
			n["label"] = site_name(n["id"])
			n["tip"] = tr("%s: integrity (HP) %s → %s in the raid. %s") % [site_name(n["id"]), res["before"], res["after"], outcome_tip(outcome)]
		n["socket"] = raid_socket(n["id"], res, projection != null, c)
	if projection == null:
		return g
	# The raid setup (S-MAPVIEW, designer 2026-10-05): the major (raid) nodes only, the Cell's
	# network and the Sites its threats take; the HQ's other hands show every Site (the Grid).
	var major := RaidMapNodes.major_ids(c, RaidMapNodes.route_paths(projection.events), projection.nodes)
	var nodes: Array[Dictionary] = []
	for n: Dictionary in g["nodes"]:
		if major.has(n["id"]):
			nodes.append(n)
	var edges: Array[Dictionary] = []
	for e: Dictionary in g["edges"]:
		if major.has(e["a"]) and major.has(e["b"]):
			if e.get("arrows", false):
				e["pencil"] = true  # ART-6 3A: the threat routes are the pencil's (RaidRouteLayer)
			edges.append(e)
	return {"nodes": nodes, "edges": edges}


## HQ-B: the pending raid's routes on the HQ map in red pencil, their entries lettered: dashed
## (a what-if) at the HQ, solid (the resolver's projection: preview equals result) in the
## setup, written on when they change; the stationed beacons and uplink pads.
func _mount_hq_routes(projection: RaidResolver.RaidResult = null, solid: bool = false) -> void:
	if city_overlay == null or not is_instance_valid(city_overlay):
		return
	raid_routes = RaidRouteLayer.new(city_overlay)
	city_overlay.add_child(raid_routes)
	city_overlay.add_child(RaidBeaconLayer.new(city_overlay))
	if projection != null:
		var paths := raid_route_paths(projection.events)
		if solid:
			var key := str(paths)
			raid_routes.set_routes(paths, key != _routes_shown)
			_routes_shown = key
		else:
			raid_routes.set_routes([] as Array[Array], false)
			raid_routes.set_what_if(paths)
	_mount_uplink_pads()


## HQ-B: the minimap terminal and the folded MAP KEY at the top right, the player's camera
## (wheel, drag, WASD, the right stick; zooming out past the raid range takes the GRID band,
## Q4) and the off-screen TARGET arrow (Q5: the Central Server outside the fit).
func _mount_hq_map_tools(page: Control) -> void:
	var c := RunManager.campaign
	hq_legend = MapLegend.new(c.corporation_id, true, true)
	hq_legend.name = "MapLegend"
	hq_legend.always_fold = true
	hq_legend.use_site_markers(not c.pending_raids.is_empty())
	hq_legend.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.add_child(hq_legend)
	TextDb.translates_itself(hq_legend)
	hq_legend.show_all_changed.connect(func(on: bool) -> void:
		if city_overlay != null and is_instance_valid(city_overlay):
			city_overlay.show_all = on)
	hq_legend.fold_changed.connect(_place_hq)
	grid_legend = hq_legend
	raid_legend = hq_legend if panel_name == "raid" else null
	grid_controls = null
	grid_minimap = null
	grid_target = null
	hq_minimap = null
	if wireframe.city3d:
		hq_minimap = CityMinimap.new()
		hq_minimap.name = "HqMinimap"
		hq_minimap.visible = Settings.text_scale < MapLegend.FOLD_SCALE - 0.001
		page.add_child(hq_minimap)
		grid_minimap = hq_minimap
		grid_controls = CityGridControls.new(wireframe.city, self, _hq_apply_frame)
		grid_controls.sites_of = _minimap_sites
		page.add_child(grid_controls)
		grid_controls.attach(city_overlay, hq_minimap)
		grid_target = TargetEdgeMarker.make(city_overlay)
		grid_target.avoid.append(hq_legend)
		grid_target.avoid.append(hq_minimap)
		page.add_child(grid_target)
		grid_target.pan_requested.connect(grid_controls.centre_on)
		if not wireframe.city.rebuilt.is_connected(grid_controls.sync_minimap):
			wireframe.city.rebuilt.connect(grid_controls.sync_minimap)


## HQ-B: a frame the player's camera asks for (wheel, drag, keys, minimap, edge arrow): the
## city takes it and the view band follows its zoom (Q4).
func _hq_apply_frame(z: float, f: Vector2, a: Vector2) -> void:
	_frame_city(z, f, a)
	_sync_hq_band()
	wireframe.city.update_camera()


## HQ-B (Q4): the HQ holds the RAID band (see-through buildings, management lanes) up to the
## raid range's widest frame (`raid_fit_max`); zoomed out past it the city takes the GRID band
## (solid buildings, the whole city).
func _sync_hq_band() -> void:
	if wireframe == null or not panel_name in HQ_PAGES:
		return
	wireframe.use_city3d(true, hq_band())


## HQ-B (Q4): the view band for the HQ's camera now.
func hq_band() -> int:
	var ortho := RaidZoomFit.ortho_of(wireframe.city.scale.x, size.x)
	return CityLod.Band.RAID if ortho <= CityView3D.CONFIG.raid_fit_max + HQ_BAND_SLACK else CityLod.Band.GRID


## Ortho slack (BU) at the band's edge (a fit at the clamp stays in the RAID band).
const HQ_BAND_SLACK := 1.0


## HQ-B: places the page's pieces by HqLayout (on every resize: text scale, window).
func _place_hq() -> void:
	if _panel == null or not is_instance_valid(_panel) or _panel != hq_page:
		return
	var page := _panel
	var o_scale := HqLayout.object_scale(Settings.text_scale)
	# The ON AIR line along the page's foot (Q7); the rest is laid out above it.
	var ticker := page.get_node_or_null("OnAir") as Control
	var foot := ticker.get_combined_minimum_size().y if ticker != null else 0.0
	if ticker != null:
		ticker.position = Vector2(0.0, page.size.y - foot)
		ticker.size = Vector2(page.size.x, foot)
	var area := Vector2(page.size.x, maxf(1.0, page.size.y - foot))
	var order := page.get_node_or_null("WorkOrder") as Control
	var r := HqLayout.rects(area, Settings.text_scale, order != null)
	# The tabs stand on the foot (as tall as their words need), the hand beside them.
	var tabs := page.get_node("HandTabs") as Control
	var tmin := tabs.get_combined_minimum_size()
	var tr_: Rect2 = r["tabs"]
	tabs.size = Vector2(maxf(tr_.size.x, tmin.x), maxf(tr_.size.y, tmin.y))
	tabs.position = Vector2(tr_.position.x, area.y - HqLayout.MARGIN - tabs.size.y)
	var verb := page.get_node("VerbSlot") as Control
	var vr: Rect2 = r["verb"]
	var vmin := verb.get_combined_minimum_size()
	verb.size = Vector2(maxf(vr.size.x, vmin.x), maxf(vr.size.y, vmin.y))
	verb.position = Vector2(area.x - HqLayout.MARGIN - verb.size.x, area.y - HqLayout.MARGIN - verb.size.y)
	var hand := page.get_node("Hand") as Control
	var hr: Rect2 = r["hand"]
	var hand_h := maxf(hr.size.y, (hand.get_child(0) as Control).get_combined_minimum_size().y)
	hand.position = Vector2(tabs.position.x + tabs.size.x + HqLayout.GAP, area.y - HqLayout.MARGIN - hand_h)
	# The card column: its width, or what its widest card needs.
	var column := page.get_node("CardColumn") as Control
	var col_w := maxf((r["card"] as Rect2).size.x, (column.get_child(0) as Control).get_combined_minimum_size().x)
	var col_x := area.x - HqLayout.MARGIN - col_w
	hand.size = Vector2(maxf(1.0, minf(verb.position.x, col_x) - HqLayout.GAP - hand.position.x), hand_h)
	var foot_top := minf(hand.position.y, tabs.position.y)
	if order != null:
		var o: Rect2 = r["order"]
		# The paper scrolls in what RAID SETUP leaves it (the chip always shows).
		var paper := order.get_node("WorkOrderPaper/WorkOrderBox") as Control
		# What the paper's scroll leaves (RAID SETUP, the setup's instruction line) and their gaps.
		var chip_h := order.get_combined_minimum_size().y + order.get_theme_constant("separation")
		order.position = o.position
		order.size = Vector2(maxf(o.size.x, paper.get_combined_minimum_size().x), minf(paper.get_combined_minimum_size().y + chip_h, maxf(chip_h + 1.0, foot_top - HqLayout.GAP - o.position.y)))
	var top := HqLayout.MARGIN
	var bottom_now := verb.position.y - HqLayout.GAP
	if hq_minimap != null and is_instance_valid(hq_minimap):
		# The minimap is optional at the raid zoom (proposal §1 #20): it gives its room to a card
		# that needs it (CLAIM's tiles), and shows only below the key's fold scale.
		var key_h := hq_legend.fit_size().y + HqLayout.GAP if hq_legend != null and is_instance_valid(hq_legend) else 0.0
		var need := (column.get_child(0) as Control).get_combined_minimum_size().y
		hq_minimap.visible = Settings.text_scale < MapLegend.FOLD_SCALE - 0.001 \
			and need <= bottom_now - (top + hq_minimap.get_combined_minimum_size().y + HqLayout.GAP + key_h)
	if hq_minimap != null and is_instance_valid(hq_minimap) and hq_minimap.visible:
		var ms := hq_minimap.get_combined_minimum_size()
		hq_minimap.size = ms
		hq_minimap.position = Vector2(area.x - HqLayout.MARGIN - ms.x, top)
		top += ms.y + HqLayout.GAP
	if hq_legend != null and is_instance_valid(hq_legend):
		var ls := hq_legend.get_combined_minimum_size()
		hq_legend.size = ls
		hq_legend.position = Vector2(area.x - HqLayout.MARGIN - ls.x, top)
		top += hq_legend.fit_size().y + HqLayout.GAP
	var bottom := verb.position.y - HqLayout.GAP
	column.size = Vector2(col_w, maxf(1.0, minf((column.get_child(0) as Control).get_combined_minimum_size().y, bottom - top)))
	column.position = Vector2(col_x, bottom - column.size.y)
	_hq_free = Rect2(Vector2(order.position.x + order.size.x + HqLayout.MARGIN if order != null else HqLayout.MARGIN, HqLayout.MARGIN), Vector2.ZERO)
	_hq_free.end = Vector2(column.position.x - HqLayout.MARGIN, foot_top - HqLayout.MARGIN)
	_hq_free.size = _hq_free.size.max(Vector2.ONE)
	var cursor := page.get_node("MapCursor") as Control
	cursor.position = _hq_free.position
	cursor.size = _hq_free.size
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.screen_rect = page.get_global_rect()
		var avoid: Array[Control] = [tabs, hand, verb, column]
		for extra in [order, hq_minimap, hq_legend, ticker]:
			if extra != null and is_instance_valid(extra):
				avoid.append(extra)
		city_overlay.avoid_controls(avoid)


## HQ-B: the map's free part as last placed (page px).
var _hq_free: Rect2 = Rect2()


## HQ-B: lays the page out again once this frame's sizes have settled (a piece's minimum size
## changed: a sticker refitted for the text size, a card's rows wrapped).
func _queue_place_hq() -> void:
	if not get_tree().process_frame.is_connected(_place_hq):
		get_tree().process_frame.connect(_place_hq, CONNECT_ONE_SHOT)


## HQ-B: the map's free part (global px, or page px with `local`): the page less the work
## order, the hand, the tabs, the ON AIR line and the right column, where the camera fits the
## network.
func hq_free_rect(local: bool = false) -> Rect2:
	if _panel == null or not is_instance_valid(_panel) or _panel != hq_page:
		return Rect2()
	return _hq_free if local else Rect2(_panel.get_global_rect().position + _hq_free.position, _hq_free.size)


## HQ-B (Q5): the lots the HQ's camera fits: the Cell's network, the Sites a run can start
## from now (patrols too) and a pending raid's routes; the Central Server shows by its edge
## arrow when it falls outside.
func hq_fit_lots() -> PackedVector2Array:
	var out := PackedVector2Array()
	if city_overlay == null or not is_instance_valid(city_overlay) or RunManager.campaign == null:
		return out
	var want := {}
	for id in hq_fit_ids():
		want[id] = true
	for n in city_overlay.nodes:
		if want.has(n["id"]):
			out.append(Vector2(city_overlay.lot_of(n["id"])) + Vector2(0.5, 0.5))
	return out


## HQ-B (Q5): the Sites the HQ's camera fits: the Cell's network and a pending raid's routes,
## and at the HQ (not in the raid setup) every Site a run can start from now.
func hq_fit_ids() -> Array[StringName]:
	var c := RunManager.campaign
	var ids: Array[StringName] = []
	ids.append_array(c.grid.claimed_ids())
	if panel_name != "raid":
		for s in RunManager.launchable_sites():
			ids.append(s.id)
		for s in RunManager.patrol_sites():
			ids.append(s.id)
	for path in CityLayout.threat_paths(c, RunManager.corporation):
		for id in path:
			ids.append(StringName(String(id)))
	return ids


## HQ-B: frames the HQ's map once its page is laid out: the fit lots in the free part at the
## raid zoom (RaidZoomFit, clamped to the raid range), then up to HQ_FIT_PASSES corrections
## on the icons as drawn (a socket floats over its roof: the lots alone frame a little low),
## never out past the raid range; then the held picture eases to it.
func fit_hq_map() -> void:
	if not panel_name in HQ_PAGES or city_overlay == null or not is_instance_valid(city_overlay):
		_hq_fit_pending = false
		return
	var free := hq_free_rect()
	var lots := hq_fit_lots()
	if not free.has_area() or lots.is_empty():
		_end_hq_fit()
		return
	var scr := get_global_rect()
	var city := wireframe.city
	if _hq_fit_passes == 0:
		_frame_city(RaidZoomFit.fit_zoom(CityView3D.CONFIG, lots, free.size * HQ_FIT_SHARE, size.x), _centre_of(lots), (free.get_center() - scr.position) / scr.size)
	else:
		var box := hq_fit_box()
		var aim := Rect2(free.get_center() - free.size * HQ_FIT_SHARE * 0.5, free.size * HQ_FIT_SHARE)
		if not box.has_area() or aim.encloses(box):
			_end_hq_fit()
			return
		var k := 1.0
		if box.size.x > aim.size.x or box.size.y > aim.size.y:
			k = minf(aim.size.x / box.size.x, aim.size.y / box.size.y)
		var floor_zoom := RaidZoomFit.zoom_of(CityView3D.CONFIG.raid_fit_max, size.x)
		k = clampf(k, floor_zoom / maxf(floor_zoom, city.scale.x), 1.0)
		var focus_at := scr.position + city.focus_anchor * scr.size
		var anchor := (aim.get_center() - (box.get_center() - focus_at) * k - scr.position) / scr.size
		_frame_city(city.scale.x * k, city.focus_grid, anchor)
	_hq_fit_passes += 1
	_sync_hq_band()
	city.update_camera()
	if grid_controls != null and is_instance_valid(grid_controls):
		grid_controls.sync_minimap()
	if _hq_fit_passes > HQ_FIT_PASSES:
		_end_hq_fit()
		return
	get_tree().process_frame.connect(fit_hq_map, CONNECT_ONE_SHOT)


## Correction passes of the HQ's fit after the first frame, and the passes so far.
const HQ_FIT_PASSES := 4
## The share of the free part the fitted Sites take (designer 2026-10-05: err on showing more
## city round the network).
const HQ_FIT_SHARE := 0.65
var _hq_fit_passes: int = 0


func _end_hq_fit() -> void:
	_hq_fit_pending = false
	_hq_fit_passes = 0
	# Parity GRID-12's idea, carried over (orchestrator 2026-10-05): once fitted, the camera
	# pans (never zooms) the way that shows the most city in the map, every fitted Site kept in
	# the free part (a network on the city's edge left a third of the map past the last block).
	if panel_name in HQ_PAGES and city_overlay != null and is_instance_valid(city_overlay) and hq_page != null:
		var held: Array[Rect2] = []
		for id in hq_fit_ids():
			var r := _map_node_rect(id)
			if r.has_area():
				held.append(r)
		var free := hq_free_rect()
		var area := hq_page.get_global_rect()
		if not held.is_empty() and free.has_area():
			var pan: Vector2 = wireframe.unrigged(func() -> Vector2: return grid_city_pan(free, area, held))
			if pan.length() >= GRID_LEAN_MIN:
				var city := wireframe.city
				_frame_city(city.scale.x, city.focus_grid, city.focus_anchor + pan / get_global_rect().size)
				city.update_camera()
				if grid_controls != null and is_instance_valid(grid_controls):
					grid_controls.sync_minimap()
			# A network wider than the raid range's widest view leaves some Sites out: the
			# selected one is panned in (its card and verb speak of it).
			_hold_selected_in(free)
	wireframe.ease_camera()


## HQ-B: pans (never zooms) the camera the least way that brings the selected Site's icon
## inside `free` (global px, less the layout margin); nothing when it is in already.
func _hold_selected_in(free: Rect2) -> void:
	if selected_site == &"":
		return
	var r: Rect2 = wireframe.unrigged(func() -> Rect2: return _map_node_rect(selected_site))
	var room := free.grow(-HqLayout.MARGIN)
	if not r.has_area() or not room.has_area() or room.encloses(r):
		return
	var d := Vector2.ZERO
	if r.position.x < room.position.x:
		d.x = room.position.x - r.position.x
	elif r.end.x > room.end.x:
		d.x = room.end.x - r.end.x
	if r.position.y < room.position.y:
		d.y = room.position.y - r.position.y
	elif r.end.y > room.end.y:
		d.y = room.end.y - r.end.y
	var city := wireframe.city
	_frame_city(city.scale.x, city.focus_grid, city.focus_anchor + d / get_global_rect().size)
	city.update_camera()
	if grid_controls != null and is_instance_valid(grid_controls):
		grid_controls.sync_minimap()


## HQ-B: the screen box (global px) round the icons of the Sites the HQ's camera fits.
func hq_fit_box() -> Rect2:
	var box := Rect2()
	var first := true
	for id in hq_fit_ids():
		var r := _map_node_rect(id)
		if not r.has_area():
			continue
		box = r if first else box.merge(r)
		first = false
	return box


## HQ-B: the map cursor stepped (pad left / right): the next Site in the Grid's order is
## selected and the cursor keeps the focus.
func _cursor_step(step: int) -> void:
	_hq_focus = "MapCursor"
	if panel_name == "raid":
		# The setup steps through the Cell's nodes (the defences' targets).
		var claimed := RunManager.campaign.grid.claimed_ids()
		if not claimed.is_empty():
			select_target(claimed[posmod(claimed.find(selected_site) + step, claimed.size())])
		return
	step_site(step)


## HQ-B: the HQ's drag targets: your nodes on the map take a crew card (station; CORE
## recalls), each runnable Site takes one (picks them as its runner), the CREW tab takes a
## recruit, the next run's kit a boost.
func _register_hq_drops_b(launchable: Array[SiteData]) -> void:
	var c := RunManager.campaign
	for site_id in c.grid.claimed_ids():
		var sid: StringName = site_id
		var kind := "recall" if sid == c.grid.home_site_id else "station"
		drops.add_target("%s:%s" % [kind, sid], ["crew"], kind, sid, _map_node_rect.bind(sid))
	for s in launchable:
		if not c.grid.is_claimed(s.id):
			drops.add_target("site:%s" % s.id, ["crew"], "jack", s.id, _map_node_rect.bind(s.id))
	var crew_tab := _panel.find_child("Tab_CREW", true, false) as Control
	if crew_tab != null:
		drops.add_target("roster", ["recruit"], "roster", null, DropLayer.rect_of(crew_tab))
	var queue := _panel.find_child("QueuedBoosts", true, false) as Control
	if queue != null:
		drops.add_target("queue", ["boost"], "queue", null, DropLayer.rect_of(queue))
	if _jack_button != null:
		drops.add_target("jack", ["crew"], "jack", selected_site, DropLayer.rect_of(_jack_button))


## HQ-B: the pad's paths on the HQ: the map cursor first; down from it to the hand (the
## lifted card), up from the hand back to it; the tabs left of the hand, the card's actions
## and the verb at the right; the work order's RAID SETUP above the map.
func _link_hq_focus(page: Control) -> void:
	var cursor := page.get_node("MapCursor") as Control
	var cards: Array[Control] = []
	_usable_in(page.get_node("Hand"), cards)
	var tabs: Array[Control] = []
	_usable_in(page.get_node("HandTabs"), tabs)
	var card_actions: Array[Control] = []
	_usable_in(page.get_node("CardColumn"), card_actions)
	var verb: Array[Control] = []
	_usable_in(page.get_node("VerbSlot"), verb)
	var setup := page.find_child("RaidSetup", true, false) as Control
	var lifted: Control = null
	for k in cards:
		if k is CrewHandCard and (k as CrewHandCard).picked:
			lifted = k
	if lifted == null and not cards.is_empty():
		lifted = cards[0]
	if lifted != null:
		cursor.focus_neighbor_bottom = cursor.get_path_to(lifted)
	elif not tabs.is_empty():
		cursor.focus_neighbor_bottom = cursor.get_path_to(tabs[0])
	var key: Control = hq_legend.fold_button if hq_legend != null and is_instance_valid(hq_legend) else null
	if setup != null:
		cursor.focus_neighbor_top = cursor.get_path_to(setup)
		setup.focus_neighbor_bottom = setup.get_path_to(cursor)
		if key != null:
			setup.focus_neighbor_right = setup.get_path_to(key)
	elif key != null:
		cursor.focus_neighbor_top = cursor.get_path_to(key)
	if key != null:
		key.focus_neighbor_bottom = key.get_path_to(cursor)
		key.focus_neighbor_left = key.get_path_to(setup if setup != null else cursor)
		if not card_actions.is_empty():
			card_actions[0].focus_neighbor_top = card_actions[0].get_path_to(key)
	if not card_actions.is_empty():
		cursor.focus_neighbor_right = cursor.get_path_to(card_actions[0])
	for i in cards.size():
		var k := cards[i]
		k.focus_neighbor_top = k.get_path_to(cursor)
		if i > 0:
			k.focus_neighbor_left = k.get_path_to(cards[i - 1])
		elif not tabs.is_empty():
			k.focus_neighbor_left = k.get_path_to(tabs[mini(hand_tab, tabs.size() - 1)])
		if i + 1 < cards.size():
			k.focus_neighbor_right = k.get_path_to(cards[i + 1])
		elif not verb.is_empty():
			k.focus_neighbor_right = k.get_path_to(verb[0])
	for i in tabs.size():
		var t := tabs[i]
		if i > 0:
			t.focus_neighbor_top = t.get_path_to(tabs[i - 1])
		else:
			t.focus_neighbor_top = t.get_path_to(cursor)
		if i + 1 < tabs.size():
			t.focus_neighbor_bottom = t.get_path_to(tabs[i + 1])
		if not cards.is_empty():
			t.focus_neighbor_right = t.get_path_to(cards[0])
	for v in verb:
		if not card_actions.is_empty():
			v.focus_neighbor_top = v.get_path_to(card_actions[card_actions.size() - 1])
		if not cards.is_empty():
			v.focus_neighbor_left = v.get_path_to(cards[cards.size() - 1])
	if not card_actions.is_empty() and not verb.is_empty():
		card_actions[card_actions.size() - 1].focus_neighbor_bottom = card_actions[card_actions.size() - 1].get_path_to(verb[0])
	for a in card_actions:
		if a.focus_neighbor_left == NodePath():
			a.focus_neighbor_left = a.get_path_to(cursor)


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


## HQ-B (b): the City Grid page folded into the HQ (the HQ is the raid-band city with every
## Site on it): the Grid opens the HQ with its selected Site.
func show_grid() -> void:
	show_hq()


## Parity fix (GRID-12): the boss's TARGET pencil (circle and word) as global rects: the
## Grid's fit, lean and pan hold it on the map with the nodes (it sat half under the minimap
## or the side column). Empty without a shown Central Server.
func _grid_pencil_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	if city_overlay == null or not is_instance_valid(city_overlay) or not city_overlay.is_inside_tree():
		return out
	var xf := city_overlay.get_global_transform()
	for n in city_overlay.nodes:
		if CityMapOverlay.is_boss(n) and city_overlay.marker_shown(n):
			var l := city_overlay.boss_layout(n)
			for key in ["circle", "word"]:
				if l.has(key):
					out.append(xf * (l[key] as Rect2))
	return out


## Parity fix (GRID-12): the pan (screen px) that shows the most of the city in the map's
## `area` (global) while every node (icon and tier pips) stays inside `free` (global): the
## best of GRID_CITY_STEPS² pans over the room the nodes leave, the shortest on a tie.
func grid_city_pan(free: Rect2, area: Rect2, held: Array[Rect2] = []) -> Vector2:
	# HQ-B: the HQ holds only its fitted Sites (`held`) in the free part.
	var rects: Array[Rect2] = held.duplicate() if not held.is_empty() else LegendSpot.node_rects(city_overlay, false)
	rects.append_array(_grid_pencil_rects())
	if rects.is_empty():
		return Vector2.ZERO
	var box := rects[0]
	for r in rects:
		box = box.merge(r)
	var aim := free.grow(-LegendSpot.FIT_INSET) if free.size.x > LegendSpot.FIT_INSET * 4.0 and free.size.y > LegendSpot.FIT_INSET * 4.0 else free
	# Per axis: the pans that hold the box in `aim` (which may move a node or the pencil back
	# onto the map); where the box is wider than `aim`, no pan on that axis.
	var lo := aim.position - box.position
	var hi := aim.end - box.end
	for axis in 2:
		if lo[axis] > hi[axis]:
			lo[axis] = 0.0
			hi[axis] = 0.0
	var best := Vector2.ZERO
	var best_share := -1.0  # a pan in the range always wins (it may have to move the box in)
	for i in GRID_CITY_STEPS + 1:
		for j in GRID_CITY_STEPS + 1:
			var d := Vector2(lerpf(lo.x, hi.x, float(i) / GRID_CITY_STEPS), lerpf(lo.y, hi.y, float(j) / GRID_CITY_STEPS))
			var share := grid_on_city_share(area, d)
			if share > best_share + 0.0001 or (is_equal_approx(share, best_share) and d.length() < best.length()):
				best = d
				best_share = share
	return best


## Parity fix (GRID-12): the share of the map `area`'s (global) sample points whose ground lies
## on the city (the config's city rect), with the camera panned by `pan` screen px.
func grid_on_city_share(area: Rect2, pan: Vector2 = Vector2.ZERO) -> float:
	var city := wireframe.city
	var to_page := get_global_transform().affine_inverse()
	var cfg_rect := Rect2(CityView3D.CONFIG.city_rect)
	var focus := city.focus_grid if city.focus_grid != Vector2.INF else Vector2.ZERO
	var on := 0
	for i in GRID_CITY_SAMPLES:
		for j in GRID_CITY_SAMPLES:
			var p := to_page * (area.position + area.size * Vector2((i + 0.5) / GRID_CITY_SAMPLES, (j + 0.5) / GRID_CITY_SAMPLES))
			if cfg_rect.has_point(CityMapCamera.grid_at(p - pan, size, focus, city.focus_anchor, city.scale.x, city.tile_b())):
				on += 1
	return float(on) / float(GRID_CITY_SAMPLES * GRID_CITY_SAMPLES)


## Parity fix (GRID-12): the pans tried per axis and the map's sample points per side.
const GRID_CITY_STEPS := 8
const GRID_CITY_SAMPLES := 12


## ANIM-R5 P8: the run rows' gains read as what clearing gives, never as buttons: a caption
## before them ("IF CLEARED:"), the Sites a clear opens named as Sites, CLAIMABLE for a Site
## that can be claimed.
const GAIN_CAPTION := "IF CLEARED:" # TR
const GAIN_OPENS_ONE := "OPENS %d SITE" # TR
const GAIN_OPENS := "OPENS %d SITES" # TR
## ANIM-R6 C15: what claiming means, in the badge's own words (CLAIMABLE left a beginner asking).
const GAIN_CLAIMABLE := "CAN BE YOUR NODE" # TR


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
		out.append(Badge.new(CityMapOverlay.tr_word("EXPLOIT"), Palette.CELL_ACID, "", CityMapOverlay.tr_word("Clearing it gives the %s Exploit for the Central Server breach.") % ename).with_icon(StatIcon.EXPLOITS))
	var heat := int(preview.get("heat", 0))
	if heat != 0:
		out.append(Badge.new(CityMapOverlay.tr_word("HEAT %s") % TextDb.signed(heat), Palette.NET_CYAN if heat < 0 else StatIcon.color_of(StatIcon.HEAT), "",
			CityMapOverlay.tr_word("Clearing it changes Heat by %s.") % TextDb.signed(heat)).with_icon(StatIcon.COOLING if heat < 0 else StatIcon.HEAT))
	if bool(preview.get("raid", false)):
		out.append(Badge.new(CityMapOverlay.tr_word("RAID"), Palette.CELL_PINK, "", CityMapOverlay.tr_word("Clearing it now brings a raid on your network.")).with_icon(StatIcon.RAIDS))
	var sch := int(preview.get("schematics", 0))
	if sch != 0:
		out.append(Badge.new(TextDb.signed(sch), Palette.NET_CYAN, "", CityMapOverlay.tr_word("Clearing it gives %s Schematics.") % TextDb.signed(sch)).with_icon(StatIcon.SCHEMATICS))
	var opens: Array = preview.get("opens", [])
	if not opens.is_empty():
		var named := PackedStringArray()
		for id in opens:
			named.append(_site_kind_name(id))
		# ANIM-R5 P8: says what opens ("OPENS 1" read as a count of nothing).
		out.append(Badge.new(CityMapOverlay.tr_word(GAIN_OPENS_ONE if opens.size() == 1 else GAIN_OPENS) % opens.size(), Palette.NET_CYAN, "",
			CityMapOverlay.tr_word("Clearing it opens %d more Sites to runs: %s.") % [opens.size(), "; ".join(named)]).with_icon(StatIcon.LINKS))
	if bool(preview.get("claimable", false)):
		# ANIM-R5 P8: a quality, not a verb (CLAIM read as a button on the row).
		out.append(Badge.new(CityMapOverlay.tr_word(GAIN_CLAIMABLE), Palette.CELL_TURF, "", CityMapOverlay.tr_word("Once cleared you can claim it (Schematics): it becomes a node of your network, which raids come for.")).with_icon(StatIcon.CLAIM))
	if out.is_empty():
		out.append(Badge.new(CityMapOverlay.tr_word("NO GAIN"), Color(Palette.PAPER, 0.6), "", CityMapOverlay.tr_word("A patrol: loot, Heat and Rank from the run, no objective.")).with_icon(StatIcon.RUNS))
	for b in out:
		b.name = "Gain_%d" % out.find(b)
	return out


## ART-5 5a: the Grid's Sites for the minimap: yours lime, the target red, the rest white.
func _minimap_sites() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if city_overlay == null or not is_instance_valid(city_overlay):
		return out
	for n in city_overlay.nodes:
		var kind := "site"
		if String(n.get("kind", "")) == CityMapOverlay.KIND_HOME or String(n.get("mark", "")) == CityMapOverlay.MARK_SPRAY:
			kind = "you"
		elif String(n.get("kind", "")) == CityMapOverlay.KIND_CENTRAL_SERVER:
			kind = "target"
		out.append({"at": Vector2(city_overlay.lot_of(n["id"])) + Vector2(0.5, 0.5), "kind": kind})
	return out


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
	if city.view3d != null and not city.view3d.uplink_pads.is_empty():
		city.view3d.set_uplink_pads([])  # ART-3 6w: the raid's pads go with its map
	if city.focus_grid != Vector2.INF or city.scale != Vector2.ONE:
		city.focus_grid = Vector2.INF
		city.scale = Vector2.ONE
		city.offset_right = 0
		city.offset_bottom = 0
		city.refresh()


## The campaign's Grid as a graph for the city overlay (CityLayout.grid_graph).
func grid_graph() -> Dictionary:
	return CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, _threat_paths(), selected_site, true)


## Pending raids' routes, entry -> home, for the map's corporate arrows.
func _threat_paths() -> Array[Array]:
	return CityLayout.threat_paths(RunManager.campaign, RunManager.corporation)


## Selects a Site clicked on the Grid map and redraws the Grid with its actions first.
## ANIM-5 (4.14): the picture holds the old frame while the page refits and then eases
## to the new one (the camera leans toward the Site, `grid_lean`).
func select_site(site_id: StringName) -> void:
	if panel_name in HQ_PAGES:
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
		RC.SiteObjective.CENTRAL_SERVER:
			return GLYPH_CENTRAL_SERVER
	return CityMapOverlay.tier_text(site.tier)


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
	var card := CrtWindow.new(site_name(site.id), accent)
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
	elif objective == RC.SiteObjective.CENTRAL_SERVER:
		facts.add_child(Badge.new(tr("CENTRAL SERVER"), Palette.corp_color(c.corporation_id), GLYPH_CENTRAL_SERVER, tr("The corporation's core. The breach needs %d Exploits.") % cfg.min_exploits_for_breach))
	elif site.objective == RC.SiteObjective.HEAT_REDUCTION:
		facts.add_child(Badge.new(CityMapOverlay.tr_word("off"), Color(Palette.NET_CYAN, 0.6), GLYPH_HEAT, tr("This Site's Heat objective is switched off at this ICE level.")).with_icon(StatIcon.COOLING))
	if c.grid.is_claimed(site.id):
		var node_col := Palette.CELL_TURF if int(s["condition"]) != GridState.Condition.DOWN else Palette.RESIST_GOLD
		# HQ-B: CORE's integrity is the home server's (the grid keeps it apart from its Site row).
		var home := site.id == c.grid.home_site_id
		var integ := c.grid.home_integrity if home else int(s["integrity"])
		var most := c.grid.home_max_integrity if home else int(s["max_integrity"])
		var node_text := "%s %d/%d" % [_display(c.grid.node_type_of(site.id)), integ, most]
		if int(s["condition"]) == GridState.Condition.DOWN:
			node_text += tr(" DOWN")
		var node_data := lookup.get_content(c.grid.node_type_of(site.id)) as NetworkNodeData
		facts.add_child(Badge.new(node_text, node_col, GLYPH_NODE, TextDb.t(node_data, "description") if node_data != null else "").with_meter(integ, most))
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
	# ART-5 5d (Group 1 naive audit P2): a Site with no JACK IN says why, and what to do first.
	var why := why_not_runnable(site, launchable_here, living)
	if why != "":
		var note := Label.new()
		note.name = "WhyNot"
		note.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # translated here, once
		note.text = why
		note.theme_type_variation = UiTheme.BODY_TEXT
		note.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.BODY))
		note.add_theme_color_override("font_color", Palette.TEXT_HI)
		UiWrap.whole_words(note)
		note.custom_minimum_size.x = MIN_NOTE_WIDTH
		card.body.add_child(note)
		card.body.move_child(note, row.get_index())
	if launchable_here and not living.is_empty():
		# HQ-B: the runner is the hand's lifted card; JACK IN is the verb slot's sticker. The card
		# names who runs it (or the rule's reason they can't).
		var runner := selected_op()
		var runner_line := Label.new()
		runner_line.name = "Runner"
		runner_line.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		var why_runner := _pick_error(runner.id, site.id) if runner != null else ""
		if why_runner == DropLayer.SKIP:
			why_runner = ""
		runner_line.text = (tr("RUNNER: %s R%d") % [runner.name, runner.rank]) if runner != null else ""
		if why_runner != "":
			runner_line.text += "  //  " + why_runner
		runner_line.add_theme_color_override("font_color", Palette.HARM if why_runner != "" else Palette.CELL_ACID)
		UiWrap.whole_words(runner_line)
		runner_line.custom_minimum_size.x = MIN_NOTE_WIDTH
		card.body.add_child(runner_line)
		card.body.move_child(runner_line, row.get_index())
	# HQ-B (b): the crew's posts on the node card: the runner stations here (a free post on an
	# active node of yours) or comes back from here.
	var who := selected_op()
	if who != null and c.grid.is_active_node(site.id) and site.id != c.grid.home_site_id:
		var node_data := lookup.get_content(c.grid.node_type_of(site.id)) as NetworkNodeData
		var here := CampaignRules.stationed_site(c, who.id) == site.id
		if here:
			var oid := who.id
			var rb := _button(tr("Recall %s") % who.name, func() -> void: recall(oid))
			rb.name = "RecallHere"
			_add_tip(row, rb, tr("Bring %s back from %s.") % [who.name, site_name(site.id)])
		elif node_data != null and node_data.station_slots > 0 and c.grid.stationed_on(site.id) == &"":
			var oid := who.id
			var sid := site.id
			var sb := _button(tr("Station %s") % who.name, func() -> void: station(oid, sid))
			sb.name = "StationHere"
			_add_tip(row, sb, tr("%s guards %s (%s): the class's station bonus helps it hold in raids.") % [who.name, site_name(site.id), TextDb.t(node_data, "description")])
	# HQ-B (d): what clearing it gives and risks (the rules' own preview: preview equals result),
	# for a Site a run can start from.
	if launchable_here and site.id != c.grid.home_site_id:
		var gains := HFlowContainer.new()
		gains.name = "IfCleared"
		gains.add_theme_constant_override("h_separation", 8)
		gains.add_theme_constant_override("v_separation", 4)
		var cap := Label.new()
		cap.name = "GainsCaption"
		cap.text = tr(GAIN_CAPTION)
		cap.add_theme_font_override("font", Palette.mono())
		cap.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
		cap.add_theme_color_override("font_color", PaletteSkins.chrome(Palette.NET_CYAN))
		cap.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		gains.add_child(cap)
		for g: Badge in run_gains(site, clear_preview_of(site)):
			gains.add_child(g)
		card.body.add_child(gains)
		card.body.move_child(gains, row.get_index())
	# HQ-B (d) (Q11, q11_a_claim.png): a cleared Site of the Cell's to build on: the node tiles
	# with their prices (the locked ones show their unlock); the pick sets CLAIM's price.
	if c.grid.is_cleared(site.id) and site.claimable:
		var cap := Label.new()
		cap.name = "PickCaption"
		cap.text = tr("PICK THE NODE TO BUILD")
		cap.add_theme_font_override("font", Palette.mono())
		cap.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
		cap.add_theme_color_override("font_color", PaletteSkins.chrome(Palette.NET_CYAN))
		card.body.add_child(cap)
		var tiles := GridContainer.new()
		tiles.name = "NodeTiles"
		tiles.columns = NODE_TILE_COLUMNS
		tiles.add_theme_constant_override("h_separation", 6)
		tiles.add_theme_constant_override("v_separation", 6)
		card.body.add_child(tiles)
		var picked := claim_choice()
		for node in choices:
			var available := CampaignRules.node_available(RunManager.profile, lookup, node)
			var unlock := _unlock_cost_of(node)
			var tile := MenuChip.new(TextDb.t(node, "display_name"), (tr("%d SCHEM.") % node.install_cost) if available else (tr("unlock %d") % unlock if unlock > 0 else tr("locked")))
			tile.pre_translated = true
			tile.name = "NodeTile_%s" % node.id
			tile.plate = &"tile"  # settings.py tiles: the picked one filled
			tile.refit()
			tile.selected = node.id == picked
			tile.disabled = not available
			tile.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			tile.tooltip_text = UiTip.fold(TextDb.t(node, "description"))
			var nid := node.id
			tile.pressed.connect(pick_claim.bind(nid))
			tiles.add_child(tile)
		card.body.move_child(cap, row.get_index())
		card.body.move_child(tiles, row.get_index())
	# HQ-B (d): a Site whose verb is not JACK IN but a run can start from (a cleared or claimed
	# Site's patrol): PATROL IT INSTEAD, a chip on the card (the slot holds CLAIM / UPGRADE ...).
	if launchable_here and site_verb(site, true).get("verb", "") != VERB_JACK_IN and not living.is_empty():
		var sid5 := site.id
		var patrol := MenuChip.new(tr("PATROL IT INSTEAD"), tr("a full run, no objective"))
		patrol.pre_translated = true
		patrol.name = "PatrolHere"
		patrol.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		patrol.tooltip_text = UiTip.fold(tr("JACK IN to %s for a patrol with %s: loot, Heat and Rank from the run, no objective.") % [site_name(sid5), selected_op().name if selected_op() != null else "-"])
		patrol.pressed.connect(func() -> void:
			var op := selected_op()
			if op != null:
				launch(sid5, op.id))
		row.add_child(patrol)
	return card


## The node tiles' columns on the CLAIM card.
const NODE_TILE_COLUMNS := 2


## The Schematics a Profile unlock that opens node type `node` costs (0 when none is listed).
func _unlock_cost_of(node: NetworkNodeData) -> int:
	var u := CampaignRules.unlock_for(RunManager.lookup(), node)
	return u.schematic_cost if u != null else 0


## ART-5 5d: the "why not" note's narrowest width (px; it wraps inside the card).
const MIN_NOTE_WIDTH := 120.0
const WHY_CORE := "This is your CORE, your home server: you defend it in raids; you never run it." # TR
const WHY_BREACH := "The Central Server's breach needs %d Exploits; you hold %d. Clear the Exploit Sites (gold keys) first." # TR
const WHY_FROM := "Not reachable yet. Clear a Site linked to it first: %s. Then it opens (orange ring) and JACK IN shows here." # TR
const WHY_FAR := "Not reachable yet. Clear the Sites between it and your network first; it opens when a linked Site is yours." # TR
const WHY_CREW := "No operative can run it now. Recruit or rest your crew at the HQ, then come back." # TR


## ART-5 5d (Group 1 naive audit P2): why Site `site` shows no JACK IN, in plain words, with
## what to do first ("" when it can be run now).
func why_not_runnable(site: SiteData, launchable_here: bool, living: Array[OperativeState]) -> String:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	if site.id == c.grid.home_site_id:
		return tr(WHY_CORE)
	if launchable_here:
		return "" if not living.is_empty() else tr(WHY_CREW)
	if CampaignRules.site_objective(c, site) == RC.SiteObjective.CENTRAL_SERVER and c.exploits.size() < RunManager.config().min_exploits_for_breach:
		return tr(WHY_BREACH) % [RunManager.config().min_exploits_for_breach, c.exploits.size()]
	var from := PackedStringArray()
	for s in corp.city_grid.sites:
		if s != null and (s.links.has(site.id) or (s.locked_links.has(site.id) and c.grid.is_link_open(s.id, site.id))):
			from.append(site_name(s.id))
	from.sort()
	return tr(WHY_FROM) % ", ".join(from) if not from.is_empty() else tr(WHY_FAR)


## HQ-B (c) (direction_B_defence.jpg): the raid setup is the HQ's DEFENCE hand, in place: the
## same page, the same camera, the same card row and sticker slot. The routes go solid (the
## resolver's projection: preview equals result), the Cell's sockets carry their forecast,
## the work order prints the whole forecast with its stamp, the hand holds the Armory's
## defence cards (press: deploy to the target; drag onto any of your nodes), the card column
## holds THREAT INTEL and YOUR NETWORK (each node's forecast; pick the target), and the
## sticker slot holds START DEFENSE with the Speed / Skip strip under it. B or the CREW tab
## goes back to the crew; the raid waits until the defence starts.
func show_raid() -> void:
	var c := RunManager.campaign
	if c == null or RunManager.pending_raid().is_empty():
		hand_tab = HandTab.CREW
		show_hq()
		return
	hand_tab = HandTab.DEFENCE
	var claimed := c.grid.claimed_ids()
	if not claimed.has(selected_site):
		selected_site = claimed[claimed.size() - 1] if not claimed.is_empty() else &""
	_build_hq_page("raid")


## HQ-B (c): the DEFENCE hand in the raid setup: the Armory's defence cards (3A's AssetCard,
## what each does in a line and a pictogram). A press deploys it to the target (the node
## picked on the map or in YOUR NETWORK); a drag puts it on any of your nodes (the grease
## pencil's IF PLACED forecast while carried). Named "AssetCards" (the row) for the tests.
func _fill_defence_hand(cards: HBoxContainer) -> void:
	var c := RunManager.campaign
	var lookup := RunManager.lookup()
	cards.name = "AssetCards"
	var seen := {}
	for i in c.armory.size():
		var aid: StringName = c.armory[i]
		if seen.has(aid):
			continue
		seen[aid] = true
		var data := lookup.get_content(aid) as DefenseAssetData
		var card := AssetCard.new(aid, TextDb.t(data, "display_name") if data != null else String(aid), data.integrity if data != null else 0, c.armory.count(aid))
		card.set_effect(data)
		card.name = "Asset_%s" % aid
		card.tooltip_text = UiTip.fold(tr("%s\n%s\nPress to deploy it to %s (the target: pick another node on the map or in YOUR NETWORK).") % [TextDb.t(data, "description") if data != null else "", card.numbers_tip(), site_name(selected_site)]
			+ " " + UiTip.for_input(tr("Or drag it onto any of your nodes."), tr("Or pick it up and move it onto any of your nodes.")))
		card.disabled = selected_site == &"" or not c.grid.is_active_node(selected_site)
		var index := i
		card.pressed.connect(func() -> void: deploy_asset(index, selected_site))
		drops.add_source(card, {"kind": "asset", "index": index, "asset": aid, "prefer": selected_site})
		cards.add_child(card)
	if c.armory.is_empty():
		var empty := _para(tr("Armory empty: runs bank assets from their drops."))
		empty.name = "ArmoryEmpty"
		empty.custom_minimum_size.x = HqLayout.CARD.x * 2.0
		cards.add_child(empty)


## HQ-B (c): the raid setup's card column: THREAT INTEL (the decrypted holo: each entry route,
## its units and what they go for) over YOUR NETWORK (each node's forecast chip; its target
## button makes it the defences' target, the target's row withdraws or moves its assets).
func _defence_cards(stack: VBoxContainer, raid: RaidData, pending: Dictionary, projection: RaidResolver.RaidResult) -> void:
	var c := RunManager.campaign
	var claimed := c.grid.claimed_ids()
	stack.add_child(_threat_intel(raid, pending, projection))
	var orders_win := RaidTerminal.new(tr("YOUR NETWORK"), Palette.NET_CYAN)
	orders_win.name = "NodeOrders"
	orders_win.tag_label.text = ""  # HQ-B: the target row carries its ">" (a tag ran over the title in the column)
	var orders := VBoxContainer.new()
	orders.name = "Orders"
	orders.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	orders.add_theme_constant_override("separation", 4)
	orders_win.body.add_child(orders)
	for site_id in claimed:
		orders.add_child(_node_order_row(site_id, projection, claimed))
	stack.add_child(orders_win)


## HQ-B (c): the sticker slot in the raid setup: START DEFENSE (3A's pink RaidSticker) with
## the Speed / Skip strip under it (greyed until the playout).
func _defence_verb(slot: VBoxContainer) -> void:
	var run_btn := RaidSticker.new(tr(START_DEFENSE), START_STICKER_STEP, RaidSticker.PINK)
	run_btn.name = "RunRaid"
	run_btn.size_flags_horizontal = Control.SIZE_SHRINK_END
	run_btn.pressed.connect(fight_raid)
	run_btn.tooltip_text = UiTip.fold(tr("Start the defence: the raid plays out on the map; the result matches the forecast."))
	slot.add_child(run_btn)
	var strip := RaidSpeedStrip.new(RunManager.config().raid_step_cap)
	strip.name = "SpeedStrip"
	strip.size_flags_horizontal = Control.SIZE_SHRINK_END
	slot.add_child(strip)


## ART-3 6w: the raid's pages on the unified 3D city at the RAID band.
const RAID_CITY_PAGES: Array[String] = ["raid", "raid_playout", "raid_summary"]


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
	var from_cursor := _hq_focus == "MapCursor"  # HQ-B: a pad step on the map keeps the map's focus
	selected_site = site_id
	if panel_name == "raid":
		wireframe.hold_camera()  # ANIM-5: the map holds still while the page rebuilds
	show_raid()
	var b := _panel.find_child("Target_%s" % site_id, true, false) as Control if _panel != null else null
	if b != null and not from_cursor:
		b.grab_focus.call_deferred()


# --- ART-6 3A raid presentation: setup panels (ART_BIBLE v2 §4.8 "Panels by fiction") -----------
## The raid's words for its targets' routing rules (THREAT INTEL and the work order's TARGET).
const RAID_TARGETS := {RC.ThreatRouting.SHORTEST_TO_HOME: "CORE (home)", RC.ThreatRouting.HIGHEST_VALUE: "highest-value node", # TR
	RC.ThreatRouting.WEAKEST_NODE: "weakest node"} # TR
## The intercepted work order's lines (corp paper, §1.2).
const ORDER_KIND := "RAID INCOMING  //  %s" # TR
const ORDER_UNITS := "%d IN %d WAVE" # TR
const ORDER_UNITS_MANY := "%d IN %d WAVES" # TR
## The forecast stamp's size on the work order (a share of the playout's stamp).
const ORDER_STAMP_SHARE := 0.78
## START DEFENSE's sticker lettering (px at text scale 1.0) and THREAT INTEL's width beside
## the loadout (px at 1.0).
const START_STICKER_STEP := UiTheme.TITLE
## Parity fix (RAID-02): the raid instruction line's dark plate (SCRIM's ink, this opaque).
const RAID_INTRO_PLATE_ALPHA := 0.85


## The raid at a glance as the corp's own intercepted WORK ORDER (ART_BIBLE v2 §4.8: corp
## paper with its letterhead, redactions and INTERCEPTED; round 20-21 `memo_glass`): the
## raid's name, its target, units, entry Sites, strength and what it would cost if it ran
## now (the forecast is exact), with the Cell's forecast stamp on it; the raid's warning in
## the tooltip. Named "RaidCard"; its values keep their names (HomeForecast, ThreatsStopped,
## RaidStrength) for the pad and the tests.
## HQ-B: what set a pending raid off, as the work order prints it ("HEAT 50 CROSSED").
func raid_trigger_words(pending: Dictionary) -> String:
	match int(pending.get("source", -1)):
		RC.RaidTriggerSource.HEAT_THRESHOLD:
			return tr("HEAT %d CROSSED") % int(pending.get("heat", 0))
		RC.RaidTriggerSource.TERRITORY_CLAIM, RC.RaidTriggerSource.NODE_BUILT:
			return tr("NODE BUILT")
		RC.RaidTriggerSource.RETALIATION:
			return tr("RETALIATION")
	return tr("ORDERS")


func _raid_card(raid: RaidData, pending: Dictionary, projection: RaidResolver.RaidResult, compact: bool = false) -> Control:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var skin := RaidSkin.of(c.corporation_id)
	var number := skin.order_number(StringName(String(pending.get("raid_id", raid.id))), int(pending.get("heat", c.heat)))
	var card := RaidPaper.new(c.corporation_id, TextDb.t(raid, "display_name").to_upper(), RaidPaper.STAMP_INTERCEPTED, number)
	card.name = "RaidCard"
	card.tooltip_text = UiTip.fold(TextDb.t(raid, "warning_text"))
	card.set_sub(tr(ORDER_KIND) % number)
	var row := HBoxContainer.new()
	row.name = "RaidFacts"
	row.add_theme_constant_override("separation", 6)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.body.add_child(row)
	var fields := VBoxContainer.new()
	fields.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	fields.add_theme_constant_override("separation", 1)
	fields.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(fields)
	# The rows go into the fields column (RaidPaper.add_row adds to its body: borrow it).
	var paper_body := card.body
	card.body = fields
	var targets := PackedStringArray()
	var units := 0
	for w in raid.waves:
		for t in w.threats:
			if t == null:
				continue
			units += 1
			var word := tr(String(RAID_TARGETS.get(t.routing, "")))
			if word != "" and not targets.has(word):
				targets.append(word)
	var total := projection.threats_destroyed + projection.threats_reached_home + _still_active(projection)
	var target_l := card.add_row(tr("TARGET"), ", ".join(targets).to_upper(), Palette.INK, "RaidTarget")
	_tip_label(target_l, tr("What the threats go for (their routing rule)."))
	var waves := raid.waves.size()
	var units_l := card.add_row(tr("UNITS"), (tr(ORDER_UNITS) if waves == 1 else tr(ORDER_UNITS_MANY)) % [units, waves], Palette.INK, "RaidUnits")
	var entries := PackedStringArray()
	for e in CampaignRules.raid_entries(c, RunManager.corporation, pending):
		entries.append(site_name(e))
	# The entry Sites in the units' tooltip (the pencil circles and letters them on the map).
	_tip_label(units_l, tr("Threats come into the city at %d Sites: %s. The red pencil routes on the map show where they go.") % [entries.size(), ", ".join(entries)])
	if compact:
		# HQ-B (direction_B.png): at the HQ the order reads at a glance: where they come in and what
		# set them off; the exact forecast is the raid setup's (RAID SETUP / DEFENCE).
		var letters := PackedStringArray()
		for i in entries.size():
			letters.append(RaidRouteMark.letter_of(i))
		var entry_l := card.add_row(tr("ENTRY SITES"), "%d (%s)" % [entries.size(), ", ".join(letters)], Palette.INK, "RaidEntries")
		_tip_label(entry_l, ", ".join(entries))
		card.add_row(tr("TRIGGER"), raid_trigger_words(pending), Palette.INK, "RaidTrigger")
		card.body = paper_body
		return card
	var strength := card.add_row(tr("STRENGTH"), tr("STRENGTH %s%%") % TextDb.signed(roundi(CampaignRules.raid_strength_pct(c, cfg, pending, RunManager.corporation))),
		Palette.INK, "RaidStrength")
	_tip_label(strength, tr("How much stronger than normal the threats are (from Heat, ICE and taken Sites). 0% is normal strength."))
	var lost_home := projection.home_after < projection.home_before
	var home := card.add_row(tr("IF IT RAN NOW"), tr("HOME %d > %d") % [projection.home_before, projection.home_after],
		Palette.HARM_INK if lost_home else Palette.INK, "HomeForecast")
	_tip_label(home, tr("Your home server (CORE) now and after the raid: %d → %d integrity. At 0 the campaign is lost. Exact: the playout matches it.") % [projection.home_before, projection.home_after])
	var stopped := card.add_row(tr("STOPPED"), tr("STOPPED %d/%d") % [projection.threats_destroyed, total], Palette.GAIN_INK if projection.threats_destroyed == total and total > 0 else Palette.INK, "ThreatsStopped")
	_tip_label(stopped, tr("Threats your nodes destroy: %d of the %d that come. The rest reach your nodes or the home server.") % [projection.threats_destroyed, total])
	var l := RaidVerdict.losses(_raid_dict(projection))
	if int(l["down"]) + int(l["taken"]) > 0:
		card.add_row(tr("DOWN / TAKEN"), "%d / %d" % [int(l["down"]), int(l["taken"])], Palette.HARM_INK, "RaidLosses")
	for e in projection.events:
		if e.get("type", "") in ["link_frozen", "link_altered"]:
			var link := card.add_row(tr("LINK"), tr("FROZEN") if e["type"] == "link_frozen" else tr("ALTERED"), Palette.HARM_INK)
			_tip_label(link, String(e["text"]))
	card.body = paper_body
	# The Cell's forecast stamp on the order (a dashed ring: a forecast, not a result).
	var verdict := raid_verdict(projection)
	var clean := RaidVerdict.clean_projection(projection)
	var stamp := ForecastStamp.new(FORECAST_CAPTION, verdict, RaidVerdict.color_of(clean), RaidVerdict.icon_of(clean))
	stamp.custom_minimum_size = Vector2(PROJECTION_STAMP, PROJECTION_STAMP) * ORDER_STAMP_SHARE * (1.0 + (Settings.text_scale - 1.0) * PROJECTION_FOLLOW)
	stamp.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	stamp.tooltip_text = UiTip.fold(forecast_tip(projection))
	row.add_child(stamp)
	return card


## ART-6 3A: the raid map's pencil routes (null off a raid page).
var raid_routes: RaidRouteLayer = null


## ART-6 3A: lays the pencil routes `paths` (Site id sequences) on the city map, written on.
func _mount_raid_routes(paths: Array[Array]) -> void:
	if city_overlay == null or not is_instance_valid(city_overlay):
		return
	raid_routes = RaidRouteLayer.new(city_overlay)
	city_overlay.add_child(raid_routes)
	city_overlay.add_child(RaidBeaconLayer.new(city_overlay))  # the R3 beacons of stationed operatives
	# Written on when they change (a new raid, a defence that turns a threat), not on every
	# rebuild of the page (picking a target).
	var key := str(paths)
	raid_routes.set_routes(paths, key != _routes_shown)
	_routes_shown = key
	_mount_uplink_pads()


var _routes_shown: String = ""


## ART-3 6w (bible §4.8 raid language B): the Cell's nodes on the raid map as the concept's
## uplink pads on their buildings' roofs, risers up the corner facing their street, on the 3D
## city (once its model is built). A view: it reads the map as laid out.
func _mount_uplink_pads() -> void:
	var view := wireframe.city.view3d if wireframe != null and wireframe.city3d else null
	if view == null:
		return
	if view.model == null:
		if not view.model_ready.is_connected(_mount_uplink_pads):
			view.model_ready.connect(_mount_uplink_pads, CONNECT_ONE_SHOT)
		return
	view.set_uplink_pads(RaidUplinkPads.of(view.model, view.cfg, raid_uplink_nodes()))


## ART-3 6w: the raid map's nodes that carry an uplink pad: the Cell's own (claimed at the time
## the map shows, home included), each with its building's lot and its street door, in the
## map's order.
func raid_uplink_nodes() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if city_overlay == null or not is_instance_valid(city_overlay) or RunManager.campaign == null:
		return out
	for n in city_overlay.nodes:
		if not n.has("socket"):
			continue
		var id: StringName = n["id"]
		out.append({"id": id, "lot": city_overlay.lot_of(id), "door": Vector2(city_overlay.street_door(id)) + Vector2(0.5, 0.5)})
	return out


## ART-6 3A: the raid setup is the page (the drag pencil draws only there).
func _raid_page_open() -> bool:
	return panel_name == "raid"


## ART-6 3A: the IF PLACED terminal's lines for carrying `payload` onto node `site_id`: the
## defence and the node, then what the forecast would change (that node's outcome, home's
## integrity), from the rules on a copy of the campaign (exact: preview equals result).
func if_placed_lines(payload: Dictionary, site_id: Variant) -> Array:
	var c := RunManager.campaign
	var pending := RunManager.pending_raid()
	if c == null or pending.is_empty() or not (site_id is StringName):
		return []
	var sid: StringName = site_id
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var copy := c.duplicate_state()
	match String(payload.get("kind", "")):
		"asset":
			CampaignRules.deploy_asset(copy, cfg, lookup, int(payload["index"]), sid)
		"placed":
			CampaignRules.move_asset(copy, cfg, lookup, payload["site"], int(payload["index"]), sid)
		_:
			return []
	var now := RunManager.project_raid()
	var then := CampaignRules.project_raid(copy, RunManager.corporation, cfg, lookup, pending)
	var lines: Array = ["%s > %s" % [_display(StringName(String(payload.get("asset", "")))).to_upper(), site_name(sid).to_upper()]]
	var a: Dictionary = now.nodes.get(String(sid), {})
	var b: Dictionary = then.nodes.get(String(sid), {})
	if not a.is_empty() and not b.is_empty():
		lines.append("%s  %s > %s" % [site_name(sid).to_upper(), outcome_word(String(a["outcome"])), outcome_word(String(b["outcome"]))])
	lines.append(tr("HOME %d > %d") % [now.home_after, then.home_after])
	return lines


## A paper value label with a tooltip (hovered, it shows the old badge's words).
func _tip_label(l: Label, tip: String) -> void:
	l.mouse_filter = Control.MOUSE_FILTER_PASS
	l.tooltip_text = UiTip.fold(tip)


## A projection as the dictionary RaidVerdict reads.
static func _raid_dict(p: RaidResolver.RaidResult) -> Dictionary:
	return {"campaign_lost": p.campaign_lost, "home_before": p.home_before, "home_after": p.home_after, "nodes": p.nodes}


## ART-6 3A: THREAT INTEL as decrypted holo (ART_BIBLE v2 §4.8; round 21 `intel_holo`): the
## corp seal cracked + DECRYPTED, one row per entry route (its letter, the units entering
## there, what they go for), the scanned threats under them. From the projection (exact:
## the playout matches it). Named "ThreatIntel".
func _threat_intel(raid: RaidData, pending: Dictionary, projection: RaidResolver.RaidResult) -> RaidHolo:
	var c := RunManager.campaign
	var holo := RaidHolo.new(c.corporation_id, tr("THREAT INTEL // SCAN"), RaidHolo.key_of(StringName(String(pending.get("raid_id", raid.id)))))
	holo.name = "ThreatIntel"
	var groups := raid_route_groups(projection)
	var units: Array[Dictionary] = []
	var seen := {}
	for gi in groups.size():
		var g: Dictionary = groups[gi]
		var names := PackedStringArray()
		var counts := {}
		var rules := PackedStringArray()
		for cid: StringName in g["threats"]:
			var td: ThreatData = RunManager.lookup().get_content(cid) as ThreatData if RunManager.lookup().has(cid) else null
			var nm := TextDb.t(td, "display_name").to_upper() if td != null else String(cid).to_upper()
			if not counts.has(nm):
				names.append(nm)
			counts[nm] = int(counts.get(nm, 0)) + 1
			var rule := tr(String(RAID_TARGETS.get(td.routing if td != null else RC.ThreatRouting.SHORTEST_TO_HOME, "")))
			if not rules.has(rule):
				rules.append(rule)
			if not seen.has(cid):
				seen[cid] = true
				units.append({"type": RaidVehicle.type_of(td), "name": nm, "letter": "%s%d" % [g["letter"], units.size() + 1]})
		if gi >= INTEL_ROWS_MAX:
			continue
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 6)
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(RaidRouteMark.new(String(g["letter"])))
		var words := VBoxContainer.new()
		words.add_theme_constant_override("separation", 0)
		words.mouse_filter = Control.MOUSE_FILTER_IGNORE
		words.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(words)
		holo.body.add_child(row)
		var listed := PackedStringArray()
		for nm in names:
			listed.append(nm if int(counts[nm]) == 1 else "%d %s" % [int(counts[nm]), nm])
		var head := holo.add_line(" + ".join(listed), Palette.AUTO, UiTheme.BODY)
		head.reparent(words)
		var sub := holo.add_line("> " + " / ".join(rules) + "  //  " + site_name(StringName(String(g["entry"]))))
		sub.reparent(words)
	if groups.size() > INTEL_ROWS_MAX:
		holo.add_line(tr("+%d more routes (the pencil letters them on the map)") % (groups.size() - INTEL_ROWS_MAX))

	if groups.is_empty():
		holo.add_line(tr("No threats can reach your network."))
	# The scanned threats strip at the base text size (bigger text keeps the map its room: the
	# names say the same).
	if not units.is_empty() and Settings.text_scale <= INTEL_STRIP_SCALE_MAX:
		holo.body.add_child(RaidIntelStrip.new(c.corporation_id, units))
	return holo


## THREAT INTEL shows its scanned threats strip up to this text scale.
const INTEL_STRIP_SCALE_MAX := 1.0
## THREAT INTEL lists at most this many entry routes (A, B, C); the rest are a count.
const INTEL_ROWS_MAX := 3


## ART-6 3A: the projection's threats grouped by their entry Site, in entry order (A first):
## [{"letter", "entry", "threats": [content ids]}]. Ties by Site id (deterministic).
static func raid_route_groups(projection: RaidResolver.RaidResult) -> Array[Dictionary]:
	var by_entry := {}
	var order: Array[StringName] = []
	if projection == null:
		return []
	for e in projection.events:
		if String(e.get("type", "")) != "threat_enters":
			continue
		var site := StringName(String(e.get("site", "")))
		if not by_entry.has(site):
			by_entry[site] = []
			order.append(site)
		(by_entry[site] as Array).append(StringName(String(e.get("threat_content", ""))))
	var out: Array[Dictionary] = []
	for i in order.size():
		out.append({"letter": RaidRouteMark.letter_of(i), "entry": order[i], "threats": by_entry[order[i]]})
	return out


## ART-6 3A: each threat's route in a resolved raid's events (its entry Site, then every Site
## it moves to), deduplicated, in the order the threats enter (the pencil routes: what the
## threats will do, as the forecast is exact).
static func raid_route_paths(events: Array) -> Array[Array]:
	return RaidMapNodes.route_paths(events)  # S-MAPVIEW: shared with the raid map's node filter


## ART-6 3A: claimed node `site_id`'s socket on the raid map (RaidSocket spec): its type's
## glyph, its state (DOWN / the raid's outcome when `res` is a result), its health now and the
## projected outcome as a forecast ring (`forecast`: `res` is the setup's projection).
func raid_socket(site_id: StringName, res: Dictionary, forecast: bool, c: CampaignState) -> Dictionary:
	var s := c.grid.site(site_id)
	var home := site_id == c.grid.home_site_id
	var glyph := RaidSocket.GLYPH_CORE if home else RaidSocket.glyph_of(c.grid.node_type_of(site_id))
	var integ := c.grid.home_integrity if home else int(s.get("integrity", 0))
	var most := c.grid.home_max_integrity if home else maxi(1, int(s.get("max_integrity", 1)))
	var state := RaidSocket.STATE_DOWN if not c.grid.is_active_node(site_id) else RaidSocket.STATE_HOLDS
	var spec := {"glyph": glyph, "state": state, "health": float(integ) / float(maxi(1, most)), "max": most}
	# The R3 class beacon of the operative stationed there (RaidBeaconLayer).
	var op_id := c.grid.stationed_on(site_id)
	if op_id != &"":
		for op in c.roster:
			if op.id == op_id:
				spec["beacon"] = op.class_id
	if not res.is_empty():
		var outcome := String(res.get("outcome", ""))
		if forecast:
			spec["forecast"] = outcome
		else:
			spec["health"] = float(int(res.get("after", integ))) / float(maxi(1, most))
			if outcome == "down":
				spec["state"] = RaidSocket.STATE_DOWN
			elif outcome == "taken":
				spec["state"] = RaidSocket.STATE_TAKEN
	return spec
# --- end ART-6 3A setup panels -------------------------------------------------------------------

## The raid forecast in words: what happens if the raid runs now (H22 #9; ANIM-R4 H3: the
## one verdict, RaidVerdict, translated).
static func raid_verdict(projection: RaidResolver.RaidResult) -> String:
	return RaidVerdict.of_projection(projection)


## What a node's raid outcome word means (H23 S5).
static func outcome_tip(outcome: String) -> String:
	if outcome == "holds":
		return TranslationServer.translate("HOLDS: the node survives and keeps fighting.")
	if outcome == OUTCOME_BREACHED:
		return TranslationServer.translate("BREACHED: your home server fell. The campaign is lost.")
	if outcome == "":
		return ""
	return TranslationServer.translate("%s: the node falls; threats go on past it.") % outcome_word(outcome)


## ART-6 3A (§4.8 BREACHED): the outcome a node's raid label shows: the core's `outcome`,
## except the home server brought to 0 (`after`), which reads BREACHED (the core keeps it
## "holds": the campaign is lost, not the node taken), as the map's word and banner do.
static func shown_outcome(outcome: String, home: bool, after: int) -> String:
	return OUTCOME_BREACHED if home and after <= 0 else outcome


## A node's raid outcome as the screen writes it ("HOLDS", "BREACHED"), translated.
static func outcome_word(outcome: String) -> String:
	return TranslationServer.translate(outcome.to_upper()) if outcome != "" else "?"


## The forecast stamp's tooltip: a projection, exact, and how to change it.
func forecast_tip(projection: RaidResolver.RaidResult) -> String:
	var what := tr("your network holds every threat")
	if projection.campaign_lost:
		what = tr("the home server falls and the campaign is lost")
	elif not RaidVerdict.clean_projection(projection):
		# ANIM-R4 H3: the losses, in the verdict's words (a DOWN node with every threat
		# stopped is not "holds every threat").
		what = tr("it costs you %s") % raid_verdict(projection).replace("\n", ", ")
	return tr("Forecast, not a result: if you start the defence now, %s. The playout matches it exactly. The raid has not happened yet: deploy assets or pick other targets to change it.") % what


## ortho (`raid_fit_max`, Appendix C #13).
## ortho (`raid_fit_max`, Appendix C #13), else RAID_MIN_ZOOM.
func raid_min_zoom() -> float:
	return RaidZoomFit.zoom_of(CityView3D.CONFIG.raid_fit_max, size.x)


## ART-3 6w: the raid playout's camera on the 3D city stays in the raid's ortho range: its
## close zoom is `raid_fit_min`'s and a framed fight goes no further out than `raid_fit_max`'s
## (the 2D city's PLAYOUT_ZOOM / PLAYOUT_MIN_ZOOM were ortho ~84 / ~133 on the city, the
## netrun transit's band).
func playout_zoom() -> float:
	if wireframe != null and wireframe.city3d:
		return RaidZoomFit.zoom_of(CityView3D.CONFIG.raid_fit_min, size.x)
	return PLAYOUT_ZOOM


func playout_min_zoom() -> float:
	if wireframe != null and wireframe.city3d:
		return RaidZoomFit.zoom_of(CityView3D.CONFIG.raid_fit_max, size.x)
	return PLAYOUT_MIN_ZOOM


## One claimed node in the raid orders: its target button (name, node type) and its
## projected outcome and assets as badges; the target's row also carries the withdraw and
## move buttons for its assets.
func _node_order_row(site_id: StringName, projection: RaidResolver.RaidResult, claimed: Array[StringName]) -> Control:
	var c := RunManager.campaign
	var n: Dictionary = projection.nodes.get(String(site_id), {})
	var box := VBoxContainer.new()
	box.name = "Order_%s" % site_id
	var row := HFlowContainer.new()
	row.add_theme_constant_override("h_separation", 8)
	box.add_child(row)
	var picked := site_id == selected_site
	# ART-6 3A: the node's socket glyph leads its terminal row (no tag: the type is the glyph).
	var glyph := RaidSocket.GLYPH_CORE if site_id == c.grid.home_site_id else RaidSocket.glyph_of(c.grid.node_type_of(site_id))
	row.add_child(RaidGlyphMark.new(glyph, not c.grid.is_active_node(site_id)))
	var target := _button(("> %s" if picked else "%s") % site_name(site_id), func() -> void: select_target(site_id))
	target.name = "Target_%s" % site_id
	target.custom_minimum_size.x = TARGET_BUTTON_WIDTH
	target.alignment = HORIZONTAL_ALIGNMENT_LEFT
	target.flat = true
	if picked:
		target.add_theme_color_override("font_color", Palette.CELL_ACID)
	target.disabled = not c.grid.is_active_node(site_id)
	_add_tip(row, target, tr("%s (%s): make it the target for the Armory's assets.") % [site_name(site_id), _display(c.grid.node_type_of(site_id))])
	if not n.is_empty():
		# H23 S5: the numbers are the node's integrity (HP); HOLDS / BREACHED said in the tip.
		# ART-6 3A: a status chip in the outcome's colour with its word (round 21 terminal rows).
		var outcome := shown_outcome(String(n.get("outcome", "")), site_id == c.grid.home_site_id, int(n.get("after", 1)))
		var chip := RaidChip.new(tr("HP %s → %s %s") % [n.get("before", "?"), n.get("after", "?"), outcome_word(outcome)], RaidChip.outcome_color(outcome))
		chip.name = "Chip_%s" % site_id
		chip.add_theme_font_override("font", Palette.mono_arrows())
		_add_tip(row, chip, tr("%s's integrity (HP) now and after the raid: %s → %s. %s") % [site_name(site_id), n.get("before", "?"), n.get("after", "?"), outcome_tip(outcome)])

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
## pre-raid network after the raid, so a TAKEN node keeps its stamp).
func raid_graph(results: Variant, markers: Dictionary, c: CampaignState = null, include: Array = []) -> Dictionary:
	if c == null:
		c = RunManager.campaign
	# S-MAPVIEW (designer 2026-10-05): the major (raid) nodes only: the Cell's network and the
	# Sites the raid's threats really take (its projection), not the whole frontier.
	var routes := RaidMapNodes.shown_routes(results, c, RunManager.corporation, RunManager.config(), RunManager.lookup())
	var g := CityLayout.grid_graph(c, RunManager.corporation, routes, selected_site)
	var nodes_res: Dictionary = results.nodes if results is RaidResolver.RaidResult else results
	var network := RaidMapNodes.major_ids(c, routes, nodes_res)
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
			var outcome := shown_outcome(String(res["outcome"]), n["id"] == c.grid.home_site_id, int(res["after"]))
			n["color"] = Palette.CELL_ACID if outcome == "holds" else Palette.CELL_PINK
			n["result"] = "%s → %s %s" % [res["before"], res["after"], outcome_word(outcome)]
			n["label"] = site_name(n["id"])  # never the raw id (H20)
			# H23 S5: the tag's numbers and word explained on hover.
			n["tip"] = tr("%s: integrity (HP) %s → %s in the raid. %s") % [site_name(n["id"]), res["before"], res["after"], outcome_tip(outcome)]
		n["assets"] = c.grid.assets_on(n["id"])
		n["threat_corp"] = String(c.corporation_id)
		if c.grid.is_claimed(n["id"]):
			n["socket"] = raid_socket(n["id"], res, results is RaidResolver.RaidResult, c)  # ART-6 3A
		nodes.append(n)
	var edges: Array[Dictionary] = []
	for e in g["edges"]:
		if network.has(e["a"]) and network.has(e["b"]):
			if e.get("arrows", false):
				e["pencil"] = true  # ART-6 3A: the threat routes are the pencil's (RaidRouteLayer)
			edges.append(e)
	return {"nodes": nodes, "edges": edges}


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
	var legend := MapLegend.pin_to(spacer, c.corporation_id)
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
	var forecast := ForecastStamp.new(FORECAST_CAPTION, verdict, RaidVerdict.color_of(clean), RaidVerdict.icon_of(clean))
	forecast.name = "PlayoutForecast"
	forecast.custom_minimum_size = Vector2(PROJECTION_STAMP, PROJECTION_STAMP) * (1.0 + (Settings.text_scale - 1.0) * PROJECTION_FOLLOW)
	forecast.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	side.add_child(forecast)
	# ART-6 3A: the live feed is the Cell's terminal (§1.2), the Speed / Skip strip at its foot.
	var feed := RaidTerminal.new(tr("LIVE RAID FEED"), Palette.HARM)
	feed.name = "RaidFeedWindow"
	side.add_child(feed)
	var cont := _button(tr("Continue"), _after_playout)
	cont.theme_type_variation = &"HotButton"
	cont.disabled = true
	if before != null and Motion.animating():
		_creep_band = before.heat_majors_crossed(RunManager.config())
	_set_panel(box, "raid_playout")
	# The map as it stood before the raid (TAKEN nodes still yours until they flip).
	var pre := before if before != null else c
	var kept: Array = pre.grid.claimed_ids()
	var g := raid_graph({}, {}, pre)
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, PLAYOUT_ANCHOR, playout_zoom())
	_mount_raid_routes(raid_route_paths(events))  # ART-6 3A: the plan stays drawn while it plays
	# ANIM-R6 C10: the playout opens framed on CORE and the Sites the raid enters at (it opened
	# on the middle of the whole network, CORE at the screen's edge, and eased from there).
	_playout_open = playout_frame_points(events)
	if not _playout_open.is_empty():
		_frame_city(playout_zoom(), _centre_of(_playout_open), PLAYOUT_ANCHOR)
	# ANIM-R5 P6: the key too (a label and home's banner went under the MAP LEGEND at 1.6).
	city_overlay.avoid_controls([side, legend])
	var overlay := city_overlay
	playout = RaidPlayoutPanel.new(overlay, PLAYOUT_LOG_SIZE)
	feed.body.add_child(playout)
	var fx := playout.attach_fx(r, c.grid.home_site_id, c.grid.home_max_integrity, Palette.corp_color(c.corporation_id))
	if fx != null and raid_routes != null and is_instance_valid(raid_routes):
		fx.entry_letters = raid_routes.letters.duplicate()  # ART-6 3A: marks stack above the letters
	# ANIM-R1 M4: each step's fight is framed (the camera eases to it) before it plays, and
	# every hit on home flies its number into the top bar's HOME, which rolls down.
	playout.framer = _frame_fight.bind(overlay)
	playout.event_shown.connect(_on_raid_event_shown)
	# ANIM-R5 P8: the forecast stamp in the side column never hides a node of the raid: it
	# turns see-through while one sits under it (it covered Scrub Records at 1.6).
	_playout_stamp = forecast
	if not wireframe.city.rebuilt.is_connected(_clear_stamp_of_nodes):
		wireframe.city.rebuilt.connect(_clear_stamp_of_nodes)
	if fx != null and Motion.animating():
		hud_home_shown = int(r.get("home_before", c.grid.home_integrity))
		_refresh_status()
		fx.home_hit_shown.connect(_fly_home_number)
	playout.finished.connect(func() -> void:
		cont.disabled = false
		# ANIM-R6 C10: the speed buttons are off now: the focus goes on to Continue.
		if cont.is_inside_tree():
			cont.grab_focus()
		hud_home_shown = -1
		hud_heat_shown = -1
		# ANIM-R6 C11: RAIDS drops with the verdict (the raid is dealt with), its tag pulsing,
		# never mid-feed with the "Raid over" line (read as "I lost a raid").
		var dealt := hud_raids_shown >= 0 and hud_raids_shown > RunManager.campaign.pending_raids.size()
		hud_raids_shown = -1
		_refresh_status()
		if dealt:
			hud.stats.land_pulse(StatIcon.RAIDS)
		forecast.resolve(RESULT_CAPTION, verdict)
		# ART-6 3A: the plan is done: its pencil routes cloth-wipe off.
		if raid_routes != null and is_instance_valid(raid_routes):
			raid_routes.wipe()
		# ANIM-R5 P2: the raid's Heat band reaches the city's look with its tint.
		_creep_band = -1
		wireframe.corp_creep = RunManager.campaign.heat_majors_crossed(RunManager.config()) / 3.0
		# The result's tint spreads from the nodes that flipped (NeonCity, one bake).
		wireframe.city.release_influence()
		if is_instance_valid(overlay):
			var done := raid_graph(RunManager.campaign.last_raid.get("nodes", {}), overlay.markers, null, kept)
			overlay.set_graph(done["nodes"], done["edges"])
			# ANIM-R5 P7: the verdict is in: the network's packets stop (one kept running to
			# CORE for 10+ s after "Raid over").
			overlay.packets = false)
	# Skip jumps straight to the summary (ANIM-5).
	playout.skipped.connect(_after_playout)
	side.add_child(cont)
	var instant := not Motion.animating()
	if instant:
		playout.play(events, true)
		_after_playout()
		return
	# ANIM-R6 C10: the first step starts on the panel's first frame, once the page is laid out:
	# the camera first fits CORE and the entries into the map's free part (the fight area has
	# no size before), then step 1 frames its fight from there.
	playout.play(events, false, false)
	_peel_start.call_deferred(feed)


## ART-6 3A (§4.8): START DEFENSE peels away off the Speed / Skip strip as the playout starts
## (1B's vinyl peel, `sticker_peel`: one press ends it; gone at once when motion doesn't play).
## The strip stays where it was.
func _peel_start(feed: Control) -> void:
	if not is_instance_valid(feed) or not feed.is_inside_tree() or not Motion.live(VinylSticker.PEEL):
		return
	var strip := feed.find_child("SpeedStrip", true, false) as Control
	if strip == null and not _start_was.has_area():
		return
	var sticker := RaidSticker.new(tr(START_DEFENSE), START_STICKER_STEP, RaidSticker.PINK).stamp_only()
	sticker.name = "StartPeel"
	add_child(sticker)
	sticker.size = sticker.custom_minimum_size
	if _start_was.has_area():
		# Parity fix (RAID-08): it peels off where it was pressed (the strip under the feed is
		# not laid out yet on the playout's first frame: the sticker sat over the MAP LEGEND).
		sticker.global_position = _start_was.get_center() - sticker.size * 0.5
	else:
		var box := strip.get_global_rect()
		sticker.global_position = Vector2(box.end.x - sticker.size.x, box.position.y - sticker.size.y * 0.85)
	sticker.peel()
	sticker.vinyl.motion_finished.connect(func(_kind: StringName) -> void: sticker.queue_free(), CONNECT_ONE_SHOT)

## Parity fix (RAID-08): START DEFENSE's rect (global) when it was pressed (empty when none).
var _start_was: Rect2 = Rect2()

## ANIM-R6 C10: what the playout opens on (grid points; emptied once it has opened there).
var _playout_open: PackedVector2Array = PackedVector2Array()


## ANIM-R6 C10: CORE and the Sites the raid's threats enter at, as grid points (the lot
## centres) on the playout's map; empty off the map.
func playout_frame_points(events: Array[Dictionary]) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var c := RunManager.campaign
	if c == null or city_overlay == null or not is_instance_valid(city_overlay):
		return pts
	var ids: Array[StringName] = [c.grid.home_site_id]
	for e in events:
		if String(e.get("type", "")) == "threat_enters":
			var sid := StringName(String(e.get("site", "")))
			if sid != &"" and not ids.has(sid):
				ids.append(sid)
	for id in ids:
		if city_overlay.has_site(id):
			pts.append(Vector2(city_overlay.lot_of(id)) + Vector2(0.5, 0.5))
	return pts


static func _centre_of(pts: PackedVector2Array) -> Vector2:
	var c := Vector2.ZERO
	for p in pts:
		c += p
	return c / maxf(1.0, pts.size())


## ANIM-R5 P8: the playout's forecast stamp (null off the playout).
var _playout_stamp: ForecastStamp = null
## Its alpha while a node of the raid sits under it.
const STAMP_OVER_NODE_ALPHA := 0.3


## ANIM-R5 P8: the playout's forecast stamp goes see-through while any node of the raid is
## under it (the camera moved: the city redrew), and back when none is.
func _clear_stamp_of_nodes() -> void:
	if _playout_stamp == null or not is_instance_valid(_playout_stamp) or not _playout_stamp.is_inside_tree() \
			or city_overlay == null or not is_instance_valid(city_overlay):
		return
	_playout_stamp.modulate.a = STAMP_OVER_NODE_ALPHA if stamp_over_node(_playout_stamp, city_overlay) else 1.0


## True when a node icon of `overlay` sits under `stamp` (global px).
static func stamp_over_node(stamp: Control, overlay: CityMapOverlay) -> bool:
	var box := stamp.get_global_rect()
	var xf := overlay.get_global_transform()
	for n: Dictionary in overlay.nodes:
		var p := overlay.icon_at(n["id"])
		if p.x == INF:
			continue
		var r := overlay.icon_radius(n) * xf.get_scale().x
		if box.grow(r).has_point(xf * p):
			return true
	return false


## ANIM-R5 P2: the Heat band the Grid's corporate creep shows while a raid's playout holds
## the pre-raid look (-1: the campaign's).
var _creep_band: int = -1


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
		# ANIM-R5 P2: the post-raid look carries the raid's Heat band too (the playout holds the old).
		var creep := RunManager.campaign.heat_majors_crossed(RunManager.config()) / 3.0 if inf != null and RunManager.campaign != null else -1.0
		wireframe.city.prebake(region.grow(NeonCity.REGION_MARGIN), inf, false, creep)


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
	if not _playout_open.is_empty():
		# ANIM-R6 C10: the first framed step keeps CORE and the entries in its frame with its
		# fight (the raid opened on the far Site with CORE at the screen's edge).
		pts.append_array(_playout_open)
		_playout_open = PackedVector2Array()
	for id in sites:
		pts.append(Vector2(overlay.lot_of(id)) + Vector2(0.5, 0.5))
	return wireframe.frame_points(pts, fight_area(_fight_area), playout_zoom(), playout_min_zoom())


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
## its "Heat +5: Collector reached CORE: 1 → 6." line, RAIDS up with a threshold's line that
## queues a raid; ANIM-R6 C11: RAIDS goes down with the verdict, its tag pulsing (the raid
## dealt with; with the "Raid over" line mid-feed it read as a raid lost).
var hud_heat_shown: int = -1
var hud_raids_shown: int = -1


## ANIM-R4 H11a: a raid event the feed has just told (RaidPlayoutPanel.event_shown).
func _on_raid_event_shown(e: Dictionary) -> void:
	_clear_stamp_of_nodes()
	match String(e.get("type", "")):
		"heat":
			if hud_heat_shown >= 0 and e.has("after"):
				hud_heat_shown = int(e["after"])
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
## ANIM-R6 C2: a FlightFx flight (it was a tween of its own no press completed): it lands on
## HOME when it arrives or when a press completes it (MotionSkip), and HOME drops then.
func _fly_home_number(damage: int, site: StringName) -> void:
	var to := hud.stats.icon_point(StatIcon.HOME)
	if not Motion.live(&"home_number_fly") or city_overlay == null or not is_instance_valid(city_overlay) or to == Vector2.INF:
		_home_number_landed(damage)
		return
	var p := city_overlay.icon_at(site)
	if p.x == INF:
		_home_number_landed(damage)
		return
	var from := city_overlay.get_global_transform() * p
	var num := Label.new()
	num.name = "HomeHitNumber"
	num.mouse_filter = Control.MOUSE_FILTER_IGNORE
	num.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	num.text = "-%d" % damage
	num.add_theme_font_override("font", Palette.display())
	num.add_theme_font_size_override("font_size", roundi(HOME_NUMBER_FONT * Settings.text_scale))
	num.add_theme_color_override("font_color", Palette.CELL_PINK)
	num.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	num.add_theme_constant_override("outline_size", 6)
	var sz := num.get_combined_minimum_size()
	# It leaves the node big (`home_number_fly`'s amplitude) and shrinks into HOME.
	num.scale = Vector2.ONE * Motion.amplitude(&"home_number_fly")
	var flown := FlightFx.fly_node(self, num, Rect2(from - sz * 0.5, sz), to, &"home_number_fly", "", 0.0, Rect2(), _home_number_landed.bind(damage))
	if flown == null:
		_home_number_landed(damage)


## ANIM-R6 C2: a home-hit number has reached HOME (or a press completed its flight): HOME
## shows the value the hits shown so far leave.
func _home_number_landed(damage: int) -> void:
	if hud_home_shown >= 0:
		hud_home_shown = maxi(0, hud_home_shown - damage)
		_refresh_status()


## The flying home-hit number's lettering at text scale 1.0 (px).
const HOME_NUMBER_FONT := 30


func _after_playout() -> void:
	_playout_stamp = null
	hud_home_shown = -1
	hud_heat_shown = -1
	hud_raids_shown = -1
	# ANIM-R6 C2: a home-hit number still flying lands now (FlightFx).
	FlightFx.finish_all(self)
	wireframe.city.release_influence()
	if RunManager.campaign.is_over():
		show_end()
	else:
		show_raid_summary()


## ART-6 3A (ART_BIBLE v2 §4.8 "Raid report"): the raid report is the raiding corp's own
## AFTER-ACTION REPORT (corp paper, CLASSIFIED) with the Cell's pencil on it (circles, RIP,
## ticks) and CELL HOLDS slapped on top when the Cell survived (GDD 7.2); the raid's one
## verdict (RaidVerdict) still lands as its stamp on the table. Heat settles here.
const REPORT_TITLE := "AFTER-ACTION REPORT" # TR
const REPORT_OPERATION := "OPERATION: %s  //  TARGET: CELL NETWORK  //  OUTCOME: %s" # TR
const REPORT_FAILED := "FAILED" # TR
const REPORT_SUCCESS := "SUCCESS" # TR
const REPORT_INTACT := "%d / %d INTACT" # TR
const REPORT_DAMAGED := "%d / %d" # TR
const REPORT_SCHEMATICS := "%d SCHEMATICS" # TR
const REPORT_HEAT := "%d > %d" # TR
const REPORT_NO_CHANGE := "%d > %d NO CHANGE" # TR
const REPORT_BACK := "BACK TO THE GRID" # TR
## The report's paper width (px at 1.0) and the CELL HOLDS sticker's lettering (px at 1.0).
const REPORT_WIDTH := 400.0
const HOLDS_STICKER_STEP := UiTheme.DISPLAY
## The Heat and the reward the last raid's feed told ([before, after], Schematics; -1 none).
var _raid_heat: Array[int] = []
var _raid_reward: int = -1


## Notes the Heat change and the reward a raid's events tell (the report prints them).
func _note_raid_outcome(events: Array[Dictionary]) -> void:
	_raid_heat = []
	_raid_reward = -1
	for e in events:
		match String(e.get("type", "")):
			"heat":
				if e.has("before") and e.has("after"):
					if _raid_heat.is_empty():
						_raid_heat = [int(e["before"]), int(e["after"])]
					else:
						_raid_heat[1] = int(e["after"])
			"raid_won":
				_raid_reward = int(e.get("schematics", 0))


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
	MapLegend.pin_to(table, c.corporation_id)
	var skin := RaidSkin.of(c.corporation_id)
	var raid_key := StringName(String(r.get("raid_id", "")))
	var raid: RaidData = RunManager.lookup().get_content(raid_key) as RaidData if RunManager.lookup().has(raid_key) else null
	var raid_name := TextDb.t(raid, "display_name").to_upper() if raid != null else String(r.get("raid_id", "")).to_upper()
	var held := not bool(r.get("campaign_lost", false))
	var number := skin.order_number(StringName(String(r.get("raid_id", ""))), c.heat)
	var report := RaidPaper.new(c.corporation_id, tr(REPORT_TITLE), RaidPaper.STAMP_CLASSIFIED, number)
	report.name = "RaidReport"
	report.custom_minimum_size.x = REPORT_WIDTH * Settings.text_scale
	report.set_sub(tr(REPORT_OPERATION) % [raid_name, tr(REPORT_FAILED) if held else tr(REPORT_SUCCESS)])
	var side := VBoxContainer.new()
	side.name = "ReportColumn"
	side.add_theme_constant_override("separation", 10)
	side.add_child(report)
	outer.add_child(side)
	var box := report.body
	# The result as the corp wrote it (H20: home, threats, then each node by name).
	var facts := VBoxContainer.new()
	facts.name = "RaidResult"
	facts.add_theme_constant_override("separation", 0)
	facts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(facts)
	report.body = facts
	var destroyed := int(r.get("threats_destroyed", 0))
	var sent := destroyed + int(r.get("threats_reached_home", 0))
	var units := report.add_row(tr("UNITS DEPLOYED / DESTROYED"), "%d / %d" % [maxi(sent, destroyed), destroyed], Palette.HARM_INK if destroyed > 0 else Palette.INK, "ReportUnits")
	_tip_label(units, tr("Threats your network destroyed."))
	if _raid_reward >= 0:
		report.add_row(tr("EQUIPMENT LOST TO HOSTILES"), tr(REPORT_SCHEMATICS) % _raid_reward, Palette.HARM_INK, "ReportReward")
	var taken: Array = r.get("taken", [])
	var down_names := PackedStringArray()
	for id in r.get("nodes", {}).keys():
		if String(r["nodes"][id].get("outcome", "")) == "down":
			down_names.append(site_name(StringName(String(id))))
	var reclaimed := PackedStringArray()
	for id in taken:
		reclaimed.append(site_name(StringName(String(id))))
	if not reclaimed.is_empty():
		var rec := report.add_row(tr("SITES RECLAIMED"), "%d (%s)" % [reclaimed.size(), ", ".join(reclaimed).to_upper()], Palette.INK, "ReportReclaimed")
		_tip_label(rec, tr("TAKEN: the corporation took the Site back."))
	if not down_names.is_empty():
		var dn := report.add_row(tr("HOSTILE NODES DOWN"), ", ".join(down_names).to_upper(), Palette.INK, "ReportDown")
		_tip_label(dn, tr("DOWN: repair the node on the Grid."))
	var hb := int(r.get("home_before", 0))
	var ha := int(r.get("home_after", 0))
	var home := report.add_row(tr("HOSTILE HOME SERVER"), (tr(REPORT_INTACT) % [ha, c.grid.home_max_integrity]) if ha >= hb else (tr(REPORT_DAMAGED) % [ha, c.grid.home_max_integrity]),
		Palette.HARM_INK if ha < hb else Palette.INK, "ReportHome")
	_tip_label(home, tr("Home integrity before and after the raid."))
	if not _raid_heat.is_empty():
		var hv := report.add_row(tr("SUSPECT FILE (HEAT)"), (tr(REPORT_NO_CHANGE) if _raid_heat[0] == _raid_heat[1] else tr(REPORT_HEAT)) % [_raid_heat[0], _raid_heat[1]], Palette.INK, "ReportHeat")
		_tip_label(hv, tr("Heat settles here: what the raid changed."))
	report.body = box
	# Each node of the raid, by name: its integrity before and after and its outcome.
	var ids: Array = r.get("nodes", {}).keys()
	ids.sort()
	for id in ids:
		var n: Dictionary = r["nodes"][id]
		var outcome := shown_outcome(String(n["outcome"]), StringName(String(id)) == c.grid.home_site_id, int(n["after"]))
		# ANIM-R5 P8: the name and its HP on one row (the name wraps instead).
		var node_row := HBoxContainer.new()
		node_row.name = "ReportRow_%s" % String(id)
		node_row.add_theme_constant_override("separation", 8)
		var node_name := Label.new()
		node_name.text = site_name(StringName(String(id))).to_upper()
		node_name.add_theme_font_override("font", Palette.paper())
		node_name.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
		node_name.add_theme_color_override("font_color", Palette.INK.lerp(Palette.PAPER, 0.3))
		node_name.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		node_name.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		UiWrap.whole_words(node_name)
		node_row.add_child(node_name)
		var v := Label.new()
		v.name = "Value"
		v.text = "%d > %d %s" % [int(n["before"]), int(n["after"]), outcome_word(outcome)]
		v.add_theme_font_override("font", Palette.display())
		v.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.BODY))
		v.add_theme_color_override("font_color", Palette.INK if outcome == "holds" else Palette.HARM_INK)
		v.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		_tip_label(v, tr("Integrity before and after, and whether the node held."))
		node_row.add_child(v)
		box.add_child(node_row)
	var back := RaidSticker.new(tr(REPORT_BACK), START_STICKER_STEP, RaidSticker.PINK)
	back.name = "ReportBack"
	back.pressed.connect(show_hq)
	back.size_flags_horizontal = Control.SIZE_SHRINK_END
	_add_tip(side, back, tr("Back to the HQ."))
	_set_panel(outer, "raid_summary")
	var g := raid_graph(r.get("nodes", {}), {})
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, Vector2(0.36, 0.55))
	city_overlay.avoid_controls([side])
	city_overlay.packets = false  # ANIM-R5 P7: a report, not a live network (no packets loop)
	# The Cell's pencil on the corp's report, and CELL HOLDS slapped on top.
	var pencil := RaidReportPencil.new(report, r, held, _raid_reward)
	pencil.name = "ReportPencil"
	report.add_child(pencil)
	if held:
		var holds := RaidSticker.new(tr(RaidVerdict.CELL_HOLDS), HOLDS_STICKER_STEP, RaidSticker.YELLOW, -6.0).stamp_only()
		holds.name = "CellHolds"
		table.add_child(holds)
		_slap_holds.call_deferred(holds, table, report)


## ART-6 3A: CELL HOLDS slaps onto the report (1B's vinyl slap, `sticker_slap`; one press ends
## it; at rest at once when motion doesn't play), beside the report's top.
func _slap_holds(holds: RaidSticker, table: Control, report: Control) -> void:
	if not is_instance_valid(holds) or not is_instance_valid(table):
		return
	holds.size = holds.custom_minimum_size
	holds.pivot_offset = holds.size * 0.5
	# Slapped beside the report's top, over the table (clear of the verdict stamp at its left).
	var at := report.global_position + Vector2(-holds.size.x - SLAP_MARGIN * Settings.text_scale, SLAP_MARGIN * 2.0 * Settings.text_scale) if is_instance_valid(report) else table.global_position
	holds.global_position = at.max(table.global_position + Vector2(SLAP_MARGIN * 8.0, SLAP_MARGIN))
	holds.slap()


## Room round the CELL HOLDS sticker on the table (px at 1.0).
const SLAP_MARGIN := 24.0

## ART-11 4D (ART_BIBLE v2 §4.8; refs `docs/art_reference/campaign_end/`): the campaign's end.
## Lost (the home server BREACHED, ruling 6.2): the winning corporation's ransomware lock over
## the city (RansomLock: its house style and verb, every node padlocked, the Cell's stickers
## curling and dropping off, a countdown to the wipe), then its audit dossier on the Cell.
## Won: the same dossier, the corporation's failure (AT LARGE). Headless (tests) goes straight
## to the dossier; reduce effects shows the lock's end state for its reading hold. The views
## only read and emit: NEW CAMPAIGN / MAIN MENU are this scene's calls (Signal Up, Call Down).
## The wireframe city's bake the lock waits for at most (frames) before it plays anyway, and
## the most stickers of the Armory the lock puts on the glass.
const END_LOCK_WAIT_FRAMES := 240
const END_LOCK_CARDS := 5
## The lock's camera on the network: close enough that its padlocks stand round the notice.
const END_LOCK_ZOOM := 1.9
## The prints' crop round the home server and round the network (share of the screen's height
## and the network's bounds' margin, px).
const END_PRINT_HOME_SHARE := 0.36
const END_PRINT_MARGIN := 60.0

var end_lock: RansomLock = null
var _end_lock_frames: int = 0


func show_end() -> void:
	var c := RunManager.campaign
	var won := c.outcome == CampaignState.Outcome.WON
	Dialogue.speak("win" if won else "loss", RC.Voice.DISPATCH, c.corporation_id, &"", c.campaign_seed)
	if c.outcome == CampaignState.Outcome.LOST and RansomLock.plays_now():
		_show_end_lock()
	else:
		show_dossier([] as Array[Dictionary])


## The lock's page: the city with the Cell's network, the lock over the whole screen.
func _show_end_lock() -> void:
	var c := RunManager.campaign
	var page := Control.new()
	page.name = "EndLockPage"
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	page.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_set_panel(page, "end_lock")
	var g := raid_graph(c.last_raid.get("nodes", {}), {})
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, Vector2(0.5, 0.5), END_LOCK_ZOOM)
	city_overlay.packets = false
	if end_lock != null and is_instance_valid(end_lock):
		end_lock.queue_free()
	end_lock = RansomLock.new()
	add_child(end_lock)
	end_lock.nodes_provider = _end_lock_nodes
	end_lock.ready_check = _end_lock_ready
	end_lock.setup(c.corporation_id, TextDb.t(RunManager.corporation, "display_name"), c.grid.home_integrity, c.grid.home_max_integrity, end_stickers())
	end_lock.finished.connect(_on_end_lock_finished)


## Where every node of the Cell's network stands on screen now (global px), home flagged.
func _end_lock_nodes() -> Array:
	var out: Array = []
	if city_overlay == null or not is_instance_valid(city_overlay):
		return out
	var home := RunManager.campaign.grid.home_site_id if RunManager.campaign != null else &""
	var xf := city_overlay.get_global_transform()
	for n in city_overlay.nodes:
		var p := city_overlay.icon_pos(n)
		if p.x != INF:
			out.append({"at": xf * p, "home": n["id"] == home})
	return out


## The lock may play: the city has baked and settled (or it waited long enough).
func _end_lock_ready() -> bool:
	_end_lock_frames += 1
	var city := wireframe.city
	return _end_lock_frames >= END_LOCK_WAIT_FRAMES or (city.showing_current_look() and city.camera_settled() and city.bake_fade >= 1.0)


## The Cell's stickers on the glass when the lock takes it: the screen's title, the Armory's
## defence cards (up to END_LOCK_CARDS, in id order) and the Cell's name.
func end_stickers() -> Array[Dictionary]:
	var out: Array[Dictionary] = [{"text": tr("CELL DEFENSE"), "fill": VinylSticker.Fill.YELLOW, "size": UiTheme.HEADING}]
	var c := RunManager.campaign
	var ids: Array[StringName] = []
	for a in c.armory:
		if not ids.has(a):
			ids.append(a)
	for site in c.grid.claimed_ids():
		for a in c.grid.assets_on(site):
			if not ids.has(a):
				ids.append(a)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ids.slice(0, END_LOCK_CARDS):
		out.append({"asset": id, "text": TextDb.t(RunManager.lookup().get_content(id), "display_name").to_upper()})
	out.append({"text": "REBEL_CELL", "fill": VinylSticker.Fill.PINK, "size": UiTheme.TITLE})
	return out


func _on_end_lock_finished() -> void:
	var photos := end_photos(end_lock.snapshot, end_lock.snapshot_points)
	if end_lock != null and is_instance_valid(end_lock):
		end_lock.queue_free()
	end_lock = null
	show_dossier(photos)


## The dossier's prints (translated captions): crops of the screen as the lock took it (the
## home server, the whole network) when there is a picture, else drawn stand-ins; then the
## crew's most troublesome operative. A won campaign's first print is the corporation's boss.
func end_photos(shot: Image, points: Array) -> Array[Dictionary]:
	var c := RunManager.campaign
	var won := c.outcome == CampaignState.Outcome.WON
	var out: Array[Dictionary] = []
	var home_at := Vector2.INF
	var bounds := Rect2()
	for p: Dictionary in points:
		var at: Vector2 = p["at"]
		bounds = Rect2(at, Vector2.ZERO) if bounds.size == Vector2.ZERO and bounds.position == Vector2.ZERO else bounds.expand(at)
		if p.get("home", false):
			home_at = at
	var home_caption := tr("HOME SERVER - %d/%d") % [c.grid.home_integrity, c.grid.home_max_integrity]
	if won:
		var boss := RunManager.corporation.final_boss
		var boss_name := TextDb.t(boss, "display_name")
		out.append({"caption": tr("%s - OFFLINE") % boss_name, "subject": PortraitArt.enemy_subject(boss.id, boss_name, c.corporation_id, true)})
	elif shot != null and home_at != Vector2.INF:
		var side := shot.get_height() * END_PRINT_HOME_SHARE
		out.append({"caption": home_caption, "texture": _crop(shot, Rect2(home_at - Vector2(side, side) * 0.5, Vector2(side, side)))})
	else:
		out.append({"caption": home_caption})
	if shot != null and bounds.size != Vector2.ZERO:
		var r := bounds.grow(END_PRINT_MARGIN)
		var side := maxf(r.size.x, r.size.y)
		out.append({"caption": tr("NODES AT THE END"), "texture": _crop(shot, Rect2(r.get_center() - Vector2(side, side) * 0.5, Vector2(side, side)))})
	else:
		out.append({"caption": tr("NODES AT THE END")})
	var best: OperativeState = null
	for o in c.roster:
		if best == null or o.runs_completed > best.runs_completed:
			best = o
	if best != null:
		out.append({"caption": "%s - %s" % [best.name, tr("AT LARGE") if best.alive else tr("DECEASED")], "subject": PortraitArt.operative_subject(best.class_id, best.id, best.name)})
	return out


## A square crop of `shot` (clamped to it) as a texture.
static func _crop(shot: Image, r: Rect2) -> Texture2D:
	var full := Rect2i(Vector2i.ZERO, shot.get_size())
	var want := Rect2i(r.position.floor(), r.size.floor()).intersection(full)
	if want.size.x <= 0 or want.size.y <= 0:
		return null
	return ImageTexture.create_from_image(shot.get_region(want))


## The audit dossier (AuditDossier) with `photos` as its prints (drawn stand-ins when empty).
func show_dossier(photos: Array[Dictionary]) -> void:
	var c := RunManager.campaign
	if photos.is_empty():
		photos = end_photos(null, [])
	var beats: Array[Dictionary] = []
	for b in CampaignRules.revealed_beats(c, RunManager.corporation):
		beats.append({"title": TextDb.t(b, "title"), "text": TextDb.t(b, "text")})
	var facts := DossierFacts.build(c, RunManager.corporation, RunManager.profile, RunManager.config(), site_name, _class_name,
		beats, RunManager.ice_cap(c.corporation_id))
	var d := AuditDossier.new(facts, photos)
	d.new_campaign_pressed.connect(_on_end_new_campaign)
	d.main_menu_pressed.connect(RunManager.go_to_title)
	_set_panel(d, "end")


func _on_end_new_campaign() -> void:
	RunManager.campaign = null
	show_start()


## A class's display name (translated).
func _class_name(class_id: StringName) -> String:
	return TextDb.t(RunManager.lookup().get_content(class_id), "display_name")


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
		DemoSetup.set_heat(c, DEMO_HEAT_FROM)
		show_hq()
	# ANIM-R6 C16: the waits are one-shot connections to the frame signal (a freed HQ drops
	# them), never an await a freed scene would resume on.
	_demo_wait(DEMO_SETTLE_FRAMES, _demo_settled.bind(id))


func _demo_settled(id: String) -> void:
	_demo_wait(DEMO_BAKE_FRAMES, _demo_play.bind(id), _demo_city_ready)


## The demo's city has baked, eased and faded in.
func _demo_city_ready() -> bool:
	var city := _demo_city()
	return city.showing_current_look() and city.camera_settled() and city.bake_fade >= 1.0


func _demo_city() -> NeonCity:
	return background.city if background.visible else wireframe.city


func _demo_play(id: String) -> void:
	var c := RunManager.campaign
	if id.begins_with("drag_"):
		_demo_drag(id)
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
			DemoSetup.set_heat(c, DEMO_HEAT_TO)
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
			_demo_city().sync_influence()
			_demo_wait(DEMO_BAKE_FRAMES, _demo_spread_seen, _demo_spreading)


func _demo_spreading() -> bool:
	return _demo_city().spreading()


func _demo_spread_seen() -> void:
	if _demo_spreading():
		print("anim5: influence_spread spreads from frame %d" % Engine.get_frames_drawn())


## ANIM-R6 C16: calls `then` after `frames` process frames, or sooner once `until` (when given)
## holds; by one-shot connections to the tree's frame signal, bound to this scene (a freed
## HQ drops them: an await resumed on a freed HQ logged "class instance is gone").
func _demo_wait(frames: int, then: Callable, until: Callable = Callable()) -> void:
	if not is_inside_tree():
		return
	get_tree().process_frame.connect(_demo_tick.bind(frames, then, until), CONNECT_ONE_SHOT)


func _demo_tick(left: int, then: Callable, until: Callable) -> void:
	if left <= 0 or (until.is_valid() and bool(until.call())):
		then.call()
		return
	_demo_wait(left - 1, then, until)


## ANIM-R6 C16: `--demo-campaign-end=won|lost`: the campaign's end page in context (a demo
## campaign in its own slot, its outcome set): WON / LOST, or -1 for another argument.
static func demo_end_of(arg: String) -> int:
	if not arg.begins_with(DEMO_END_FLAG):
		return -1
	match arg.trim_prefix(DEMO_END_FLAG):
		"won":
			return CampaignState.Outcome.WON
		"lost":
			return CampaignState.Outcome.LOST
	return -1


const DEMO_END_FLAG := "--demo-campaign-end="
## The HQ demos' campaign: its Schematics, the raid demos' Armory, and the Heat poster demo's
## Heat before and after its crossing.
const DEMO_SCHEMATICS := 100
const DEMO_ARMORY: Array[StringName] = [&"turret", &"ice_lock", &"decoy"]
const DEMO_HEAT_FROM := 20
const DEMO_HEAT_TO := 30


## ANIM-R6 C16: shows the campaign's end page on a fresh demo campaign with `outcome`.
func demo_campaign_end(outcome: int) -> void:
	RunManager.save_slot = "demo"
	new_campaign(1)
	DemoSetup.end_campaign(RunManager.campaign, outcome)
	show_end()


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
	if id.begins_with("drag_asset"):
		if id == "drag_asset_refuse":
			# The relay's second slot filled: the last asset has nowhere to go there.
			CampaignRules.deploy_asset(c, cfg, lookup, 0, selected_site)
		show_raid()
	elif id == "drag_crew_refuse":
		show_hq()
	elif id.begins_with("drag_crew"):
		RunManager.scene_switching_enabled = false  # the capture holds on the drop, not the jack
		var sites := RunManager.launchable_sites()
		if not sites.is_empty():
			selected_site = sites[0].id
		show_grid()
	elif id.begins_with("drag_loadout"):
		var op := c.living_operatives()[0]
		DemoSetup.set_rank(op, 3)  # ANIM-R6 B2: dev flag only; views never write state
		open_loadout(op)
		(get_node("LoadoutView") as LoadoutView).show_spinner()
	# ANIM-R6 C16: one-shot waits (see _demo_wait).
	_demo_wait(DEMO_LAYOUT_FRAMES, _demo_drag_pick.bind(id))


## The item picked up once the page has laid out (ANIM-4 capture; see _demo_drag).
func _demo_drag_pick(id: String) -> void:
	var c := RunManager.campaign
	var layer := drops
	var src: Control = null
	var target_id := ""
	var end := Vector2.INF
	if id.begins_with("drag_asset"):
		var cards := _panel.find_child("AssetCards", true, false)
		src = cards.get_child(cards.get_child_count() - 1) as Control
		target_id = "node:%s" % (selected_site if id == "drag_asset_refuse" else c.grid.home_site_id)
	elif id == "drag_crew_refuse":
		src = _panel.find_child("Crew_%s" % c.living_operatives()[0].id, true, false) as Control
		target_id = "station:%s" % c.grid.claimed_ids()[c.grid.claimed_ids().size() - 1]
	elif id.begins_with("drag_crew"):
		src = _grid_chips[0] if not _grid_chips.is_empty() else null
		target_id = "jack"
		if id == "drag_crew_cancel":
			end = Vector2(size.x * 0.3, size.y * 0.45)
	elif id.begins_with("drag_loadout"):
		var op := c.living_operatives()[0]
		var view := get_node("LoadoutView") as LoadoutView
		layer = view.drops
		var options := CampaignRules.ring_segment_options(op, RunManager.lookup().get_content(op.class_id) as ClassData)
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
	_demo_wait(0, _demo_drag_step.bind(id, layer, from, end, 0))


## One frame of the scripted pointer's path (step `i` of DEMO_DRAG_FRAMES), then the rest
## there, then the release.
func _demo_drag_step(id: String, layer: DropLayer, from: Vector2, end: Vector2, i: int) -> void:
	if not is_instance_valid(layer):
		return
	if i < DEMO_DRAG_FRAMES:
		var q := Tween.interpolate_value(0.0, 1.0, float(i + 1) / DEMO_DRAG_FRAMES, 1.0, Tween.TRANS_SINE, Tween.EASE_IN_OUT) as float
		layer.point_at(from.lerp(end, q) - Vector2(0, DEMO_DRAG_ARC * sin(PI * q)))
		_demo_wait(0, _demo_drag_step.bind(id, layer, from, end, i + 1))
		return
	_demo_wait(DEMO_DRAG_HOLD - 1, _demo_drag_release.bind(id, layer, end))


func _demo_drag_release(id: String, layer: DropLayer, end: Vector2) -> void:
	if not is_instance_valid(layer):
		return
	print("anim4: %s lets go on frame %d" % [id, Engine.get_frames_drawn()])
	layer.release_at(end)


func _still_active(projection: RaidResolver.RaidResult) -> int:
	return projection.taken.size()


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
		hud.hide_heat()
		return
	var cfg := RunManager.config()
	_status.text = "Heat %d/%d | Schematics %d | Home %d/%d | Exploits %d | Raids pending %d | ICE %d | %s" % [
		c.heat, cfg.heat_max, c.schematics, c.grid.home_integrity, c.grid.home_max_integrity,
		c.exploits.size(), c.pending_raids.size(), c.ice_level, "campaign over" if c.is_over() else "active"]
	# HQ-B (Q1): Heat is the gauge in the bar's first slot (the HEAT stat tag gave it its place);
	# at the HQ it opens the Heat terminal (Scrub Heat).
	hud.set_heat(c.heat if hud_heat_shown < 0 else hud_heat_shown, cfg.heat_max, HeatRules.band_levels(c, cfg), panel_name in HEAT_BUTTON_PAGES, heat_tip())
	# H24 S3: the tags' names are keys (translated where drawn); the tooltips translated here.
	hud.set_stats([[TextDb.mark("SCHEMATICS"), str(c.schematics), "", tr("Schematics: the campaign's currency. Recruit, claim and upgrade nodes, repair, scrub Heat, buy boosts and Profile unlocks.")],
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


## HQ-B (Q1): the pages whose HEAT gauge is a button (it opens the Heat terminal with SCRUB
## HEAT); elsewhere in the scene it only shows.
const HEAT_BUTTON_PAGES: Array[String] = ["hq", "raid"]
## HQ-B: the Heat terminal dropped from the gauge (null when closed).
var heat_terminal: HeatTerminal = null


## HQ-B (Q1, `heat_indicator.jpg`): the HEAT gauge pressed (click, A, H or the pad's View):
## the Heat terminal drops from it, or folds back when it is open. SCRUB HEAT buys through
## the rules (`buy_heat_reduction`) and the terminal opens again on the new numbers.
func toggle_heat_terminal() -> void:
	if heat_terminal != null and is_instance_valid(heat_terminal):
		close_heat_terminal()
		return
	if RunManager.campaign == null or not panel_name in HEAT_BUTTON_PAGES:
		return
	heat_terminal = HeatTerminal.new(RunManager.campaign, RunManager.config(), false)
	heat_terminal.scrub_pressed.connect(_scrub_from_terminal)
	heat_terminal.closed.connect(close_heat_terminal)
	add_child(heat_terminal)
	TextDb.shown_as_given(heat_terminal)
	# Under the tag and the subtitles' band (a line spoken over it would cover its header).
	var tag := hud.heat_gauge.get_global_rect()
	tag.end.y = SubtitleStrip.top_below(tag.end.y)
	heat_terminal.drop_under(tag, get_global_rect())
	if heat_terminal.scrub != null:
		heat_terminal.scrub.grab_focus.call_deferred()


## HQ-B: folds the Heat terminal away; focus goes back to the gauge.
func close_heat_terminal(refocus: bool = true) -> void:
	if heat_terminal != null and is_instance_valid(heat_terminal):
		heat_terminal.queue_free()
		if refocus and hud.heat_gauge.is_visible_in_tree() and hud.heat_gauge.focus_mode != Control.FOCUS_NONE:
			hud.heat_gauge.grab_focus.call_deferred()
	heat_terminal = null


func _scrub_from_terminal() -> void:
	close_heat_terminal()
	buy_heat_reduction()
	toggle_heat_terminal()


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
	# H24 S2: the sign from TextDb.signed (no "%+" in a translated line). HQ-B: one wording,
	# the Heat terminal's.
	return HeatTerminal.modifier_text(m)


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


## ANIM-R1 M5: a territory change landed on the city: the counter it changes bumps (the
## CELL STATUS SITES badge on the HQ page).
func _on_territory_marked(_marks: Array) -> void:
	# HQ-B (Q1): CELL STATUS went; its SITES bump plays on the HEAT tag (the motion entry kept).
	var badge: Control = hud.heat_gauge if hud != null else null
	if badge != null and badge.is_visible_in_tree():
		Motion.pop(badge, &"sticky_bump")
	refresh_site_card()


## ANIM-R3 B6: the Grid's Site card rebuilt in place for the campaign as it is now (a claim
## seen on the map while the card still offered CLAIM); nothing off the Grid.
func refresh_site_card() -> void:
	if not panel_name in HQ_PAGES or _panel == null or RunManager.campaign == null:
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
	TextDb.shown_as_given(card)
	# HQ-B: the verb slot follows (a claim seen on the map leaves no CLAIM sticker).
	var old_slot := _panel.get_node_or_null("VerbSlot") as Control
	if old_slot != null and panel_name == "hq":
		var slot := _verb_slot(site, launchable)
		var slot_at := old_slot.get_index()
		_panel.remove_child(old_slot)
		old_slot.queue_free()
		_panel.add_child(slot)
		_panel.move_child(slot, slot_at)
		TextDb.shown_as_given(slot)
		slot.minimum_size_changed.connect(_queue_place_hq)
		_place_hq()
		_link_hq_focus(_panel)


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
	b.text = ("%s %s" % [String(b.get_meta(&"hint_base")), Settings.hint(StringName(b.get_meta(&"hint_action")))]).strip_edges()


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
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE  # city map screens take clicks behind
	add_child(root)
	hud = HudBar.new()
	hud.loadout_pressed.connect(open_loadout)
	hud.daemons_pressed.connect(open_daemons)
	hud.heat_pressed.connect(toggle_heat_terminal)
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
	# ANIM-R6 C15: the HQ page never ends in a half-cut row (at 1.6 the crew cards' Loadout
	# buttons were cut under MORE BELOW); worked out afresh for each page (_set_panel).
	add_child(more_hint)
	# ANIM-4: drag and drop over every page (targets pulse, the pad's reticle, flights).
	drops = DropLayer.new()
	_wire_drops(drops)
	add_child(drops)
	# ART-6 3A: the raid setup's drag in grease pencil (parked sticker, arrow, dock circle).
	var pencil := RaidDragPencil.new(drops)
	pencil.active = _raid_page_open
	pencil.forecast = if_placed_lines
	drops.add_child(pencil)


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
## ART-10 4C (v2 §2.10): a screen's title as a yellow vinyl sticker (never focused, no clicks).
func _title_sticker(word: String, key: String = "") -> VerbSticker:
	var s := VerbSticker.new(word, VerbSticker.Fill.YELLOW, TITLE_STICKER_PX, TITLE_STICKER_TILT, VerbSticker.title_art(key))
	s.pre_translated = true
	s.name = "TitleSticker"
	s.focus_mode = Control.FOCUS_NONE
	s.mouse_filter = Control.MOUSE_FILTER_IGNORE
	s.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	s.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	return s


func _para(text: String) -> Label:
	var l := _label(text)
	UiWrap.whole_words(l)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
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


## Puts StatIcon `kind` before button `b`'s words (H21 #13: menus in words only); returns b.
func _icon(b: Button, kind: StringName) -> Button:
	IconMark.attach(b, kind)
	return b


# --- HQ-B (d): the verb slot -----------------------------------------------------------------

## HQ-B (d) (designer ruling Q11, final): the selected thing's verb for the one sticker slot,
## with its price (the rules' own numbers: the preview is the purchase): {"verb", "price",
## "word" (the sticker's word, a translation key), "tip"}. A node of the Cell's: REPAIR when
## DOWN, else UPGRADE while it can rise; CORE: PATCH while damaged (what the Schematics buy);
## a cleared Site of the Cell's to build on: CLAIM (the picked node type's install); a Site a
## run can start from: JACK IN. "" when the selection has no verb (the card says why).
func site_verb(site: SiteData, runnable: bool) -> Dictionary:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	if site == null or c == null:
		return {"verb": ""}
	var sid := site.id
	if sid == c.grid.home_site_id:
		var points := patch_points()
		if points > 0:
			return {"verb": VERB_PATCH, "price": CampaignRules.home_repair_price(c, cfg, points), "points": points}
		return {"verb": ""}
	if c.grid.is_claimed(sid):
		if int(c.grid.site(sid).get("condition", 0)) == GridState.Condition.DOWN:
			return {"verb": VERB_REPAIR, "price": CampaignRules.repair_cost(c, cfg, lookup, sid)}
		var up := CampaignRules.upgrade_cost(c, cfg, sid)
		if c.grid.is_active_node(sid) and up >= 0:
			return {"verb": VERB_UPGRADE, "price": up}
	elif c.grid.is_cleared(sid) and site.claimable:
		var node := lookup.get_content(claim_choice()) as NetworkNodeData
		if node != null:
			return {"verb": VERB_CLAIM, "price": node.install_cost, "node": node.id}
	if runnable:
		return {"verb": VERB_JACK_IN, "price": -1}
	return {"verb": ""}


## The verbs (the stickers' words, translation keys).
const VERB_JACK_IN := "JACK IN" # TR
const VERB_CLAIM := "CLAIM" # TR
const VERB_REPAIR := "REPAIR" # TR
const VERB_UPGRADE := "UPGRADE" # TR
const VERB_PATCH := "PATCH" # TR
## The price tag's words (a translation key).
const PRICE_WORDS := "%d SCHEMATICS" # TR
## The node type CLAIM builds (picked on the card's tiles; kept across rebuilds).
var claim_pick: StringName = &""


## The node type CLAIM builds now: the one picked on the card if it can be built, else the
## first that can (id order, as `_node_choices`).
func claim_choice() -> StringName:
	var lookup := RunManager.lookup()
	var first: StringName = &""
	for node in _node_choices():
		if not CampaignRules.node_available(RunManager.profile, lookup, node):
			continue
		if node.id == claim_pick:
			return node.id
		if first == &"":
			first = node.id
	return first


## CORE's patch now: the integrity points the Schematics buy (all missing ones at most), the
## same count CampaignRules.repair_home restores.
func patch_points() -> int:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var missing := c.grid.home_max_integrity - c.grid.home_integrity
	var per := CampaignRules.home_repair_point_cost(c, cfg)
	return mini(missing, int(floor(c.schematics / maxf(0.0001, per))))


## HQ-B (d): picks node type `node_id` on the CLAIM card (the sticker's price follows).
func pick_claim(node_id: StringName) -> void:
	claim_pick = node_id
	_hq_focus = "NodeTile_%s" % node_id
	if panel_name in HQ_PAGES:
		wireframe.hold_camera()
	show_hq()


## HQ-B (d): presses the verb sticker's verb `v` on Site `sid` (the same calls the old
## buttons made).
func press_verb(v: Dictionary, sid: StringName) -> void:
	match String(v.get("verb", "")):
		VERB_CLAIM:
			claim(sid, StringName(String(v.get("node", ""))))
		VERB_REPAIR:
			repair(sid)
		VERB_UPGRADE:
			upgrade(sid)
		VERB_PATCH:
			repair_home()
		VERB_JACK_IN:
			var op := selected_op()
			if op != null:
				launch(sid, op.id)


# --- HQ-B (f): the story so far --------------------------------------------------------------

## HQ-B (f) (designer ruling Q8): the story beats this campaign's HQ has shown, per campaign
## (view memory, never game state): a beat revealed since (a run's end, a raid) is told as a
## corp-news toast when the HQ shows next; the story so far is the Codex's STORY section.
static var _beats_seen: Dictionary = {}
## The toast's words (a translation key).
const STORY_TOAST := "CORP NEWS // %s. The story so far is in the Codex (pause menu)." # TR


## HQ-B (f): toasts the beats revealed since the HQ last showed (none the first time a
## campaign's HQ shows: its beats so far are the Codex's). Returns the titles told.
func tell_new_beats() -> PackedStringArray:
	var told := PackedStringArray()
	var c := RunManager.campaign
	if c == null or RunManager.corporation == null:
		return told
	var key := "%s|%d" % [c.corporation_id, c.campaign_seed]
	var beats := CampaignRules.revealed_beats(c, RunManager.corporation)
	var seen: int = _beats_seen.get(key, beats.size())
	for i in range(mini(seen, beats.size()), beats.size()):
		var title := TextDb.t(beats[i], "title")
		told.append(title)
		notify(tr(STORY_TOAST) % title)
	_beats_seen[key] = beats.size()
	return told


# --- HQ-B (g): the HQ idle's motion entries, re-pointed onto the new page ---------------------

## The Sites' statuses this campaign's HQ last showed (view memory, never game state).
static var _sites_seen: Dictionary = {}


## HQ-B (g) (ANIM-6 4.13 kept, binding: art restyles motion, never drops an entry): the old
## HQ's idle moves onto the new page's pieces: `hq_crt_hum` hums the selected Site's CRT card
## (the deck monitor went), `radio_type` types JACK IN's system word in on arrival (the radio
## is the ON AIR crawl now), `jack_ring_breathe` breathes the JACK IN sticker, `polaroid_tilt`
## tilts a hovered crew card (CrewHandCard), and `minimap_pulse` rings the Sites whose status
## changed since the HQ last showed on the minimap (the 2D mini-map went). Headless and under
## reduce effects each is its end state.
func _hq_idle() -> void:
	if _panel == null or not is_instance_valid(_panel):
		return
	var card := _panel.find_child("SelectedSite", true, false) as Control
	if card != null:
		CrtHum.attach(card)
	var jack := _panel.find_child("Launch", true, false) as Control
	if jack != null and jack.is_visible_in_tree():
		Motion.loop_pulse(jack, ^"scale", &"jack_ring_breathe")
	var word := _panel.find_child("SystemWord", true, false) as Label
	if word != null and entering:
		Typing.type_in(word, &"radio_type")
	var changed := changed_sites()
	if hq_minimap != null and is_instance_valid(hq_minimap) and not changed.is_empty():
		var points: Array[Vector2] = []
		for id in changed:
			if city_overlay != null and city_overlay.has_site(id):
				points.append(Vector2(city_overlay.lot_of(id)) + Vector2(0.5, 0.5))
		hq_minimap.pulse(points)


## HQ-B (g): the Sites whose status changed since this campaign's HQ last showed (none the
## first time), in the Grid's order; seen now.
func changed_sites() -> Array[StringName]:
	var out: Array[StringName] = []
	var c := RunManager.campaign
	if c == null or RunManager.corporation == null:
		return out
	var key := "%s|%d" % [c.corporation_id, c.campaign_seed]
	var now := {}
	for s in RunManager.corporation.city_grid.sites:
		if s != null:
			now[s.id] = int(c.grid.status_of(s.id))
	if _sites_seen.has(key):
		var was: Dictionary = _sites_seen[key]
		for s in RunManager.corporation.city_grid.sites:
			if s != null and was.has(s.id) and int(was[s.id]) != int(now[s.id]):
				out.append(s.id)
	_sites_seen[key] = now
	return out
