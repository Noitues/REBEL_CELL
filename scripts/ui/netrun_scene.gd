extends Control
## Functional M2 netrun scene (placeholder look): start screen, map, combat (embedded
## CombatScene), rewards, Terminal events, Modem shop and the run summary. Every
## action goes through RunManager's NetrunSession; the scene only displays state.

const COMBAT_SCENE := preload("res://scenes/combat/combat_scene.tscn")
## What each route node holds (the route buttons' tooltips).
## H24 S3: the words in these constants are translation keys ("# TR"), translated where
## shown; every page but the fight shows its words as given (TextDb.shown_as_given).
const NODE_TIPS := {RC.InfilNodeType.ROUTER: "Router: a fight. Win it for Cycles and loot.", # TR
	RC.InfilNodeType.TERMINAL: "Terminal: an event with choices.", # TR
	RC.InfilNodeType.MODEM: "Modem: the cyber shop (cards, Firmware, Daemons, slices, card removal).", # TR
	RC.InfilNodeType.SERVER_RACK: "Server Rack: the Site's guardian. Breach it to complete the run."} # TR

## What each route node is, in a word (H21 #14: two "Router" buttons looked the same) and
## as an icon; an elite Router is an "Elite fight" with the crown.
const NODE_WORDS := {RC.InfilNodeType.ROUTER: "Fight", RC.InfilNodeType.TERMINAL: "Event", # TR
	RC.InfilNodeType.MODEM: "Shop", RC.InfilNodeType.SERVER_RACK: "Rack"} # TR
const NODE_ICONS := {RC.InfilNodeType.ROUTER: StatIcon.FIGHT, RC.InfilNodeType.TERMINAL: StatIcon.TERMINAL,
	RC.InfilNodeType.MODEM: StatIcon.SHOP, RC.InfilNodeType.SERVER_RACK: StatIcon.RACK}
const ELITE_WORD := "Elite fight" # TR
## The pause menu's least top (px); it opens under the subtitle band.
const PAUSE_TOP := 100.0
## A reachable route node's colour on the map (route_graph) and on its button's icon.
const ROUTE_NEXT_COLOR := Palette.CELL_ACID
## The home server's name (as the HQ shows it; never its id).
const HOME_LABEL := "CORE" # TR
## The Modem's quadrant (px) and the room its window frame and title take (px): shop cards
## grow with the text size only as far as a quadrant holds them (H21 #15).
const MODEM_QUAD := Vector2(490, 250)
const QUAD_FRAME := Vector2(24, 56)
const QUAD_GAP := 12.0
## LEAVE THE MODEM's exit icon beside it (px; art pass W8c: the tag sits at the page's foot).
const LEAVE_ICON := 34.0
## Loot stickers at text scale 1.0 and the most a row of them may grow (px).
const LOOT_CARD := Vector2(150, 170)
const LOOT_ROW_MAX := 900.0
## The least gap between loot stickers (px; their tilt's reach is added, ANIM-R2 E8).
const LOOT_GAP := 14.0
## ANIM-R1 M11: the gap between the loot stickers and Skip at text scale 1.0 (px): a
## sticker's rest tilt and hover lift reach this far below its box.
const LOOT_SKIP_GAP := 14.0
## Room above the event's paper at text scale 1.0 (px): its tape and title keep clear of
## the subtitle band (H23 S10).
const EVENT_TOP_GAP := 12.0
## The event's choice column keeps this far from the screen's right edge at text scale 1.0
## (px; H24 S9: its buttons ran to x=1280, the right border cut).
const EVENT_RIGHT_GAP := 16.0
## The loot and reward kinds as the LOOT title words them (keys).
const LOOT_WORDS := {"card": "card", "firmware": "Firmware chip", "daemon": "Daemon", "slice": "slice"} # TR
## Passes fitting the route map beside the ROUTE column (H24 S12), the route's own zoom
## and anchor, and the smallest the fit may make it (the city's zoom).
const ROUTE_FITS_MAX := 3
const ROUTE_ZOOM := 1.45
const ROUTE_ANCHOR := Vector2(0.46, 0.58)
const ROUTE_MIN_ZOOM := 0.7
## ANIM-R3 B8: the whole route is framed down to this zoom (icons keep their screen size, so
## a far-out route stays readable); a route that needs less shows the part the player decides
## on (route_focus_ids) at ROUTE_MIN_ZOOM or closer.
const ROUTE_FIT_FLOOR := 0.4
## The slice tiles in the Modem at text scale 1.0 (px): they widen with the text as far as
## their window holds them (H24 S10: "BUY 100-150" shrank to fit a fixed tile at 1.6).
const SLICE_TILE := Vector2(96, 130)
## Share of the text scale the lower row's tiles grow in height by.
const TILE_GROW := 0.4
## ANIM-R2 E6: a chip or Daemon tile at text scale 1.0 (px, as ZineCard.as_tile makes it),
## the steps it grows by, and the effect lettering it grows for (px): it grows until its
## whole text fits at this size or more, as far as its window holds it.
const CHIP_TILE := Vector2(118, 150)
const CHIP_FIT_STEP := 6.0
const CHIP_READABLE := 10
## The Daemon tile may widen by this share of the text scale's growth (the SLICES window
## beside it keeps its row).
const DAEMON_WIDEN := 0.25
## The raid setup's big button (H24 S14; as the HQ's).
const START_DEFENSE := "START DEFENSE" # TR

var _status: Label
## Top strip: screen title and the status line (`_status`).
var hud: HudBar
## The subtitles' band under the top bar (H21 #11); hidden while a fight docks its own.
var subtitle_strip: SubtitleStrip
## The route drawn on the city (map phase) and whether it is zoomed out to the Grid.
var city_overlay: CityMapOverlay = null
var _grid_zoomed: bool = false
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var combat_scene: Control = null
var background: WireframeBackground
var map_view: NetrunMapView = null
var playout: RaidPlayoutPanel = null
var _spoken_events: Dictionary = {}
var _settings_panel: PauseMenu = null
## The route's node buttons (their key hints follow the device).
var _route_buttons: Array[Button] = []
## The route view's key: the route's node kinds (placed clear of the nodes; null when
## zoomed out, where the campaign map's MapLegend shows in the ROUTE window).
var route_legend: RouteLegend = null
## Pad button prompts at the foot of the screen (H23 S11).
var pad_prompts: PadPrompts
## Art pass W8c: "MORE BELOW" at the foot of a page that scrolls on (§5.3).
var more_hint: ScrollHint = null
## The screen on show (screen_name) and whether the last page entered a new screen (its
## entrance plays) or refreshed the same one (Animation pass ANIM-6).
var _shown_screen: String = ""
var entering: bool = false
## Capture demos (--demo-buy / --demo-pick / --demo-choose) act this many frames in, once
## the screen has come in.
const DEMO_ACTION_FRAMES := 30

## Event types that pop a toast (H20: the log strip is optional).
const TOAST_WARN_EVENTS: Array[String] = ["refused", "deploy_failed", "undock_failed"]


func _ready() -> void:
	UiTheme.apply(self)
	# Subtitles sit in the top band, clear of every control (H20); combat docks its own.
	Dialogue.dock_default()
	Settings.hints_changed.connect(_relabel_route)
	Settings.hints_changed.connect(_reword_tips)  # art pass W8c: tips follow the device
	# Capture variants (ANIM-6): --demo-set / --demo-speed tune a copy of the motion table.
	MotionDemo.apply_args()
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
		elif a.begins_with("--demo-scale="):
			# Captures at a text size (ANIM-R2): this run only, never saved.
			Settings.text_scale = float(a.trim_prefix("--demo-scale="))
			Settings.changed.emit()
	if args.has("--demo-shop"):
		RunManager.save_slot = "demo"
		new_campaign(1)
		start_run(1)
		RunManager.netrun.run.cycles = 120
		RunManager.netrun._open_shop()
		_show_current()
		if args.has("--demo-deckview"):
			open_remove()
			(get_node("DeckView") as DeckView).select(2)
		elif args.has("--demo-carddetail"):
			open_remove()
			(get_node("DeckView") as DeckView).open_card.call_deferred(2)
		elif args.has("--demo-spinnerview"):
			open_overwrite(1)
			(get_node("SpinnerView") as SpinnerView).select(2)
		elif args.has("--demo-loadout"):
			open_loadout()
		elif args.has("--demo-daemons"):
			RunManager.netrun.run.operative.daemon_ids.append_array([&"twin_pointer", &"shield_cache", &"zero_day", &"feedback_loop"])
			_refresh_status()
			open_daemons()
			(get_node("DaemonTray") as DaemonTray).show_card(&"shield_cache", false)
		elif args.has("--demo-spinnergrid"):
			open_overwrite(1)
		elif args.has("--demo-deckgrid"):
			open_remove()
		elif args.has("--demo-buy"):
			# Capture (ANIM-6): the first card is bought once the Modem has come in.
			MotionDemo.after_frames(self, DEMO_ACTION_FRAMES, func() -> void: buy("cards", 0))
		_demo_drag_arg(args)
		return
	if args.has("--demo-event") or args.has("--demo-dispatch") or args.has("--demo-loot"):
		# Screenshot shortcuts for the Terminal event (street / DISPATCH voice) and loot.
		RunManager.save_slot = "demo"
		new_campaign(1)
		start_run(1)
		var run := RunManager.netrun.run
		if args.has("--demo-loot"):
			run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
			run.phase = RunState.Phase.REWARD
		else:
			run.event_id = &"ev_dispatch_early_reply" if args.has("--demo-dispatch") else &"ev_leash_on_the_floor"
			run.phase = RunState.Phase.EVENT
		_show_current()
		# Capture (ANIM-6): the loot's second card is picked / the first choice is taken.
		if args.has("--demo-pick"):
			MotionDemo.after_frames(self, DEMO_ACTION_FRAMES, func() -> void: choose_reward(1))
		elif args.has("--demo-choose"):
			MotionDemo.after_frames(self, DEMO_ACTION_FRAMES, func() -> void: choose_event(0))
		_demo_drag_arg(args)
		return
	for a in args:
		if a.begins_with("--demo-w8c-end="):
			# Art pass W8c captures (dev flag only): the run's end (died, completed, aborted)
			# reached through the session's own ending, its T4 sequence playing.
			_demo_w8c_end(a.trim_prefix("--demo-w8c-end="))
			return
	if args.has("--demo-gridzoom"):
		_grid_zoomed = true
	if args.has("--demo-run") or args.has("--demo-combat") or args.has("--demo-tutorial"):
		# Dev shortcut for screenshots: godot --path . -- --demo-run (uses its own save slot)
		RunManager.save_slot = "demo"
		new_campaign(1)
		for a in args:
			if a.begins_with("--demo-class="):
				# Screenshot operative of another class (campaign-only, bypasses Profile unlocks).
				var cls := RunManager.lookup().get_content(StringName(a.trim_prefix("--demo-class="))) as ClassData
				if cls != null:
					RunManager.campaign.roster.clear()
					RunManager.campaign.recruit(cls)
		start_run(1)
		if args.has("--demo-combat") or args.has("--demo-tutorial"):
			RunManager.pending_tutorial = args.has("--demo-tutorial")
			enter_node(RunManager.netrun.available_nodes()[0])
		elif args.has("--demo-anim=route_pulse"):
			_demo_route_pulse.call_deferred()
		elif args.has("--demo-interlude"):
			# ANIM-R3 B5 captures: the run opens on a raid interlude (Heat past 25 queues one).
			HeatRules.add_heat(RunManager.campaign, RunManager.config().major_heat_levels()[0] + 1, RunManager.config(), "demo")
			RunManager.netrun._maybe_raid_interlude()
			_show_current()
		for a in args:
			# ANIM-R2 R2 profiling: the route shows, then N frames in the first fight on it opens.
			if a.begins_with("--demo-run-fight="):
				MotionDemo.after_frames(self, int(a.trim_prefix("--demo-run-fight=")), _demo_enter_fight)
			elif a.begins_with("--demo-end="):
				_demo_combat_end(a.trim_prefix("--demo-end="))  # ANIM-R5 combat: win / lose
		return
	if RunManager.has_active_run():
		_show_current()
	else:
		_show_start()


# --- Public API (used by buttons and the integration test) --------------------------

func new_campaign(seed: int) -> void:
	RunManager.new_campaign(seed)
	_log.append_text("[b]New campaign[/b] (seed %d): %d Schematics, %d rookies.\n" % [seed, RunManager.campaign.schematics, RunManager.campaign.roster.size()])
	_show_start()


func start_run(_tier: int = 1) -> void:
	var s := RunManager.start_run()
	if s == null:
		_log.append_text("[color=orange]No living operative or open Site: go to HQ.[/color]\n")
		return
	_report(s.last_events)
	_show_current()


func resume() -> void:
	if RunManager.resume():
		_log.append_text("[b]Resumed.[/b]\n")
		_show_current()
	else:
		_log.append_text("[color=orange]Nothing to resume.[/color]\n")


func enter_node(node_id: StringName) -> void:
	if _travelling:
		# A choice pressed while the last move still plays skips it (input skips to the end).
		_end_travel()
		return
	var s := RunManager.netrun
	var from := s.run.current_node_id
	_report(s.enter_node(node_id))
	RunManager.after_step()
	# ANIM-5 (4.16): the move plays on the route map (a light pulse along the link, the new
	# node pops up, the old one dims), then the node's screen opens. The rules have already
	# run; this only delays the view.
	var secs := 0.0
	if city_overlay != null and is_instance_valid(city_overlay) and not _grid_zoomed and RunManager.netrun != null \
			and RunManager.netrun.run.current_node_id == node_id:
		# ANIM-R1 M7 / ANIM-R4 H11c: the map shows the run's new state as the move starts (it
		# waited for the pulse to land): the [1] / [2] labels on the new next nodes, the ROUTE
		# window's buttons the same choices, the node left ticked and dimmed as visited, the
		# walked route a faint trail; the marker travels the link to the node entered.
		var r := route_graph()
		city_overlay.set_graph(r["nodes"], r["edges"])
		_refresh_route_choices()
		secs = city_overlay.travel(from, node_id)
	if secs <= 0.0:
		_show_current()
		return
	_travelling = true
	get_tree().create_timer(secs).timeout.connect(_end_travel)


## Art pass W8c capture (dev flag only): the demo run ends through the session's own ending
## (`died`: the flatline, `completed`: the clean exit, `aborted`: the home server lost) and
## the run-end stage plays; prints the frame it starts on.
func _demo_w8c_end(kind: String) -> void:
	RunManager.save_slot = "demo"
	new_campaign(1)
	start_run(1)
	var s := RunManager.netrun
	match kind:
		"completed":
			s.call(&"_complete_run")
		"aborted":
			s.run.outcome = RunState.Outcome.ABORTED
			s.run.phase = RunState.Phase.ENDED
		_:
			s.call(&"_die")
	_report(s.last_events)
	for f in DEMO_SETTLE_FRAMES:
		await get_tree().process_frame
	print("MotionDemo: w8c run end (%s) starts on frame %d" % [kind, Engine.get_frames_drawn()])
	_show_current()


## ANIM-R2 R2 profiling: enters the first open Router (a fight), else the first open node.
func _demo_enter_fight() -> void:
	var open: Array = RunManager.netrun.available_nodes()
	for id in open:
		if int(RunManager.netrun.run.map.get_node(id).get("type", -1)) == RC.InfilNodeType.ROUTER:
			enter_node(id)
			return
	enter_node(open[0])


## ANIM-5 frame capture (dev shortcut): once the route map and the city have settled, a
## move plays on the map; prints the frame it starts on. ANIM-R4 H11c: a real move (the demo
## run, in its own slot, stands on its first node, then moves on to the next): the pulse, the
## new choices on the map and in the ROUTE window at once, the walked link as a trail.
func _demo_route_pulse() -> void:
	demo_tune(OS.get_cmdline_user_args())
	var s := RunManager.netrun
	var first: StringName = s.available_nodes()[0]
	s.run.current_node_id = first
	s.run.visited.append(first)
	_show_map()
	for f in DEMO_SETTLE_FRAMES:
		await get_tree().process_frame
	for f in DEMO_BAKE_FRAMES:
		if background.city.showing_current_look() and background.city.camera_settled() and background.city.bake_fade >= 1.0:
			break
		await get_tree().process_frame
	print("anim5: route_pulse starts on frame %d" % Engine.get_frames_drawn())
	enter_node(s.available_nodes()[0])


## ANIM-4b frame capture: frames a scripted pointer takes from the item to where it lets go,
## the frames it rests there first, the frames a page gets to lay out after a change, and
## the arc of the pointer's path (px up at its middle), as the HQ's ANIM-4 demos.
const DEMO_DRAG_FRAMES := 18
const DEMO_DRAG_HOLD := 3
const DEMO_LAYOUT_FRAMES := 12
const DEMO_DRAG_ARC := 40.0
## Where the demo lets go: this far off the target's centre (px), at most this share of its
## size (so it stays inside); the Cycles a refusal demo leaves the player.
const DEMO_RELEASE_OFFSET := Vector2(10, 8)
const DEMO_RELEASE_SHARE := 0.3
const DEMO_POOR_CYCLES := 5
const DEMO_RICH_CYCLES := 300


## `--demo-anim=drag_*` (with --demo-shop or --demo-loot): the drag plays once the page has
## come in.
func _demo_drag_arg(args: PackedStringArray) -> void:
	for a in args:
		if a.begins_with("--demo-anim=drag_"):
			var id := a.trim_prefix("--demo-anim=")
			MotionDemo.after_frames(self, DEMO_ACTION_FRAMES, func() -> void: _demo_drag(id))


## ANIM-4b frame capture: picks an item up, carries it along a scripted pointer path and
## lets go: a Modem card onto the deck (`drag_buy_card`), a microchip onto a slot it fits
## (`drag_buy_chip`), a card too dear for the Cycles left (`drag_buy_refuse`), a deck card
## onto the shredder (`drag_shred`), a loot card onto the deck (`drag_loot`). Prints
## "anim4b: <id> starts on frame N" at the pick-up.
func _demo_drag(id: String) -> void:
	var s := RunManager.netrun
	var layer := drops
	var src: Control = null
	var target_id := "deck"
	match id:
		"drag_buy_card", "drag_loot":
			src = _page_item("Stickers", 1 if id == "drag_loot" else 0)
		"drag_buy_refuse":
			s.run.cycles = DEMO_POOR_CYCLES
			_show_current()
			for f in DEMO_LAYOUT_FRAMES:
				await get_tree().process_frame
			src = _page_item("Stickers", 0)
		"drag_buy_chip":
			# Enough Cycles for any chip (the demo shows a purchase, not a refusal).
			s.run.cycles = DEMO_RICH_CYCLES
			_show_current()
			for f in DEMO_LAYOUT_FRAMES:
				await get_tree().process_frame
			src = _page_item("Chips", 0)
			target_id = "slot:0"
			if src != null:
				drops.start_carry(src, false)
				for k in s.run.operative.slot_slice_ids.size():
					if drops.takes("slot:%d" % k):
						target_id = "slot:%d" % k
						break
				drops.cancel()
				drops.finish_all()
		"drag_shred":
			open_remove()
			for f in DEMO_LAYOUT_FRAMES:
				await get_tree().process_frame
			layer = modal_drops
			var view := get_node_or_null("DeckView") as DeckView
			src = view.card(0) if view != null else null
			target_id = "shred"
	if src == null or layer == null:
		print("anim4b: %s has nothing to drag" % id)
		return
	var from := src.get_global_rect().get_center()
	get_viewport().gui_release_focus()  # the focused tile's tip would cover the capture
	layer.start_carry(src, false)
	layer.point_at(from)
	var r := layer.locate(layer.target(target_id))
	var end := r.get_center() + DEMO_RELEASE_OFFSET.min(r.size * DEMO_RELEASE_SHARE)
	print("anim4b: %s starts on frame %d" % [id, Engine.get_frames_drawn()])
	for i in DEMO_DRAG_FRAMES:
		await get_tree().process_frame
		var q := Tween.interpolate_value(0.0, 1.0, float(i + 1) / DEMO_DRAG_FRAMES, 1.0, Tween.TRANS_SINE, Tween.EASE_IN_OUT) as float
		layer.point_at(from.lerp(end, q) - Vector2(0, DEMO_DRAG_ARC * sin(PI * q)))
	for i in DEMO_DRAG_HOLD:
		await get_tree().process_frame
	print("anim4b: %s lets go on frame %d" % [id, Engine.get_frames_drawn()])
	layer.release_at(end)


## Frames the ANIM-5 demo waits for the page to settle, and the most it waits for the
## city's bake before playing anyway.
const DEMO_SETTLE_FRAMES := 20
const DEMO_BAKE_FRAMES := 240


## ANIM-5 variants for review: `--demo-tune=<id>:<duration>[:<amplitude>]` plays `id`
## with those values (a duplicate of the table; the file never changes).
static func demo_tune(args: PackedStringArray) -> void:
	var cfg: UiMotionData = null
	for a in args:
		if not a.begins_with("--demo-tune="):
			continue
		var parts := a.trim_prefix("--demo-tune=").split(":")
		if cfg == null:
			cfg = (load(Motion.CONFIG_PATH) as UiMotionData).duplicate(true)
		var e := cfg.find(StringName(parts[0]))
		if e == null or parts.size() < 2:
			continue
		e.duration = float(parts[1])
		if parts.size() > 2:
			e.amplitude = float(parts[2])
	if cfg != null:
		Motion.use_config(cfg)


## ANIM-R4 H11c: the ROUTE window shows the view's choices now (a move has started).
func _refresh_route_choices() -> void:
	var row := _panel.find_child("RouteNodes", true, false) as VBoxContainer if _panel != null and is_instance_valid(_panel) else null
	if row == null:
		return
	_fill_route_choices(row)
	UiFocus.link_layout(_panel)
	UiFocus.focus_first(row)


## ANIM-5: a netrun move is playing on the route map (the node's screen opens after it).
var _travelling: bool = false


## Ends the move (its time is up, or input skipped it) and opens the node's screen.
func _end_travel() -> void:
	if not _travelling:
		return
	_travelling = false
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.finish_travel()
	_show_current()


func choose_reward(index: int, slot: int = -1) -> void:
	_choose_reward(index, slot, true)


## Takes loot option `index` (as its sticker's press). `fly` false: a drag (ANIM-4b) already
## lands the item on its target, so the click's flight (ANIM-6) does not play too.
func _choose_reward(index: int, slot: int, fly: bool) -> void:
	var s := RunManager.netrun
	var offer := s.current_reward() if s.run.phase == RunState.Phase.REWARD else {}
	var left := s.run.pending_rewards.size()
	_report(s.choose_reward(index, slot))
	# The picked card lifts and flies to the deck (ANIM-6); the page is rebuilt under it.
	if s.run.pending_rewards.size() < left and not offer.is_empty():
		if fly:
			# Art pass W8c (§11 Loot, critique gifs/23: the pick wasn't celebrated): the picked
			# offer is stamped TAKEN (T2) as it lifts, then flies to CARDS.
			_fly_item(_page_item("Stickers", index), String(offer["kind"]), &"loot_pick", tr(LOOT_PICK_STAMP), Motion.amplitude(&"loot_pick"))
		# ANIM-R1 M11: the offers not taken fall away (`loot_reject`), picked by click or drag.
		# ANIM-R3 A7: within the loot's window (they fell across the route coming in under it).
		var fell := false
		for i in (offer["options"] as Array).size():
			var other := _page_item("Stickers", i)
			if i != index and other != null:
				if FlightFx.fly(self, other, other.get_global_rect().get_center() + Vector2(0.0, Motion.amplitude(&"loot_reject")), &"loot_reject", "", 0.0,
						loot_window_rect(other)) != null:
					fell = true
					other.modulate.a = 0.0  # its copy falls; the sticker is gone from its slot
		if fell:
			var picked := _page_item("Stickers", index)
			if fly and picked != null:
				picked.modulate.a = 0.0  # its fresh copy is flying to CARDS
			# ANIM-R4 C7: the loot page stays (inert) while the offers not taken fall inside its
			# window, and leaves when they have (they floated over the route map that came in
			# under them); a press ends them (FlightFx) and the page goes at once.
			RunManager.after_step()
			_hold_loot_page()
			return
	RunManager.after_step()
	_show_current()


## ANIM-R4 C7: the loot page waits for its falling offers (`loot_reject`), taking no input.
var _loot_hold: Tween = null


func _hold_loot_page() -> void:
	if _panel != null and is_instance_valid(_panel):
		var block := Control.new()
		block.name = "LootLeaving"
		block.mouse_filter = Control.MOUSE_FILTER_STOP
		block.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_panel.add_child(block)
	var owner := get_viewport().gui_get_focus_owner() if get_viewport() != null else null
	if owner != null and _panel != null and _panel.is_ancestor_of(owner):
		owner.release_focus()
	if _loot_hold != null and _loot_hold.is_valid():
		_loot_hold.kill()
	_loot_hold = create_tween()
	# Art pass W8c (overlaps ANIM-R5 B5, which bounds the hold by the picked card's flight
	# too): the pick's TAKEN stamp and its flight to CARDS land before the page goes; the
	# page still leaves as soon as nothing flies (`_loot_hold_step`).
	var hold := maxf(Motion.seconds(&"loot_reject") + Motion.delay_of(&"loot_reject"),
		Motion.delay_of(&"loot_pick") + Motion.seconds(&"sold_stamp") + Motion.seconds(&"loot_pick") * (1.0 + FlightFx.LIFT_SHARE))
	_loot_hold.tween_method(_loot_hold_step, 0.0, 1.0, hold + Motion.seconds(&"loot_reject"))
	_loot_hold.tween_callback(_end_loot_hold)


func _loot_hold_step(_p: float) -> void:
	if FlightFx.active_count(self) == 0:
		_end_loot_hold()


func _end_loot_hold() -> void:
	if _loot_hold == null:
		return
	if _loot_hold.is_valid():
		_loot_hold.kill()
	_loot_hold = null
	_show_current()


## True while the loot page waits for its falling offers (tests).
func loot_leaving() -> bool:
	return _loot_hold != null


## The loot window a sticker sits in (global; ANIM-R3 A7: loot not taken falls within it),
## an empty rect when it has none.
static func loot_window_rect(sticker: Control) -> Rect2:
	var n: Node = sticker
	while n != null and not (n is TerminalWindow):
		n = n.get_parent()
	return (n as Control).get_global_rect() if n != null else Rect2()


func skip_reward() -> void:
	_report(RunManager.netrun.skip_reward())
	RunManager.after_step()
	_show_current()


func choose_event(index: int) -> void:
	var s := RunManager.netrun
	var phase := s.run.phase
	var chosen := _panel.find_child("Choice%d" % (index + 1), true, false) as Control if _panel != null else null
	_report(s.choose_event_option(index))
	# The chosen outcome stamps (ANIM-6) over the next screen as it comes in.
	if phase == RunState.Phase.EVENT and s.run.phase != RunState.Phase.EVENT and chosen != null:
		# Art pass W8c (critique gifs/24: the note's picture stayed as a white bar over the
		# route): the stamp is the word CHOSEN over where the choice was, no picture of it.
		FlightFx.stamp_on(self, chosen, tr(EVENT_CHOSEN_STAMP), &"event_choice_stamp", false)
	RunManager.after_step()
	_show_current()


## Art pass W8c: the stamp a chosen event choice leaves (§6.6: ≤ 3 words).
const EVENT_CHOSEN_STAMP := "CHOSEN" # TR


func buy(kind: String, index: int, slot: int = -1) -> void:
	_buy(kind, index, slot, true)


## Buys stock item `index` of `kind` (as its BUY press). `fly` false: a drag (ANIM-4b)
## already lands the item on its target with SOLD, so the click's flight does not play too.
func _buy(kind: String, index: int, slot: int, fly: bool) -> void:
	var s := RunManager.netrun
	var cycles := s.run.cycles
	var item := _page_item({"cards": "Stickers", "firmware": "Chips", "daemons": "Daemons"}.get(kind, ""), index)
	_report(s.buy(kind, index, slot))
	# Bought (ANIM-6): SOLD stamps on its price and the item flies to its top bar icon.
	if fly and s.run.cycles < cycles:
		_fly_item(item, kind.trim_suffix("s"), &"buy_fly", tr("SOLD"))
	RunManager.after_step()
	_show_current()


## Item `index` of the row named `row` on the page on screen (a loot or shop sticker;
## ANIM-R1 M11: a Modem row's SOLD stubs are not items).
func _page_item(row: String, index: int) -> Control:
	var holder := _panel.find_child(row, true, false) if _panel != null and row != "" else null
	if holder == null or index < 0:
		return null
	var items := _row_items(holder)
	return items[index] if index < items.size() else null


## The items of a page row in stock order (a Modem row's SOLD stubs left out).
static func _row_items(row: Node) -> Array[Control]:
	var out: Array[Control] = []
	for c in row.get_children():
		if c is Control and not (c is ZineCard and (c as ZineCard).sold_stub):
			out.append(c as Control)
	return out


## Where an item of `kind` goes on the top bar: a card to CARDS, a Daemon to the DAEMONS
## icon, a Firmware chip or a slice to VIEW LOADOUT (global).
func item_target(kind: String) -> Vector2:
	match kind:
		"card":
			var p := hud.stats.icon_point(StatIcon.CARDS)
			if p != Vector2.INF:
				return p
		"daemon":
			if hud.daemon_button.is_visible_in_tree():
				return hud.daemon_button.get_global_rect().get_center()
	return hud.loadout_button.get_global_rect().get_center() if hud.loadout_button.is_visible_in_tree() else hud.get_global_rect().get_center()


func _fly_item(item: Control, kind: String, id: StringName, stamp: String = "", lift: float = 0.0) -> void:
	if item != null:
		FlightFx.fly(self, item, item_target(kind), id, stamp, lift)


func remove_card(deck_index: int) -> void:
	_report(RunManager.netrun.remove_card(deck_index))
	RunManager.after_step()
	_show_current()


func overwrite_slice(slot: int, stock_index: int) -> void:
	_report(RunManager.netrun.overwrite_slice(slot, stock_index))
	RunManager.after_step()
	_show_current()


func leave_shop() -> void:
	_report(RunManager.netrun.leave_shop())
	RunManager.after_step()
	_show_current()


func raid_deploy_run_asset(index: int, site_id: StringName) -> void:
	_report(RunManager.netrun.raid_deploy_run_asset(index, site_id))
	RunManager.after_step()
	_show_current()


func raid_deploy_armory(index: int, site_id: StringName) -> void:
	_report(RunManager.netrun.raid_deploy_armory(index, site_id))
	RunManager.after_step()
	_show_current()


func raid_move(from_site: StringName, index: int, to_site: StringName) -> void:
	_report(RunManager.netrun.raid_move(from_site, index, to_site))
	RunManager.after_step()
	_show_current()


func raid_fight() -> void:
	# ANIM-5: the playout starts from the Grid as it stood (a view copy) and the city holds
	# its pre-raid tint until the raid has played; the result spreads at the end.
	var before := RunManager.campaign.duplicate_state() if RunManager.campaign != null else null
	background.city.pin_influence(CityInfluence.of(RunManager.campaign, RunManager.corporation))
	var events := RunManager.netrun.raid_fight()
	_report(events)
	RunManager.after_step()
	_show_raid_playout(events, before)


## ANIM-R1 M8: whether the screen a jack in lands on is built and framed (Fx keeps its
## cover up until then, so it never lifts onto an empty dark screen): a page is on, the
## city behind it was drawn under the current camera (its placement: the route's nodes and
## labels in place), and the route map's fit passes have run. ANIM-R2 R1: the city's image
## is not waited for; it fades in over the night sky when its bake lands.
func arrival_ready() -> bool:
	if _panel == null or not is_instance_valid(_panel) or not _panel.is_inside_tree():
		return false
	var city: NeonCity = background.city if background != null else null
	if city != null and city.is_visible_in_tree():
		if not city.camera_settled():
			return false
		if city.rebuilt.is_connected(fit_route_map) or get_tree().process_frame.is_connected(fit_route_map) or _raid_map_framing:
			return false
	return true


func finish_run() -> void:
	# ANIM-R1 M1: a second press during the jack out asks nothing again.
	if RunManager.scene_change_pending():
		return
	RunManager.clear_run()
	RunManager.go_to_hq()
	_show_start()


func save_and_quit() -> void:
	if RunManager.scene_change_pending():
		return
	RunManager.autosave()
	_log.append_text("Saved.\n")
	RunManager.go_to_hq()
	_show_start()


# --- Panels --------------------------------------------------------------------------

func _show_current() -> void:
	if _loot_hold != null:
		# ANIM-R4 C7: whatever shows next ends the loot page's wait.
		if _loot_hold.is_valid():
			_loot_hold.kill()
		_loot_hold = null
	var s := RunManager.netrun
	if s == null:
		_show_start()
		return
	# Art pass W8c (ART_BIBLE §10 rule 6, W8a's after_modals): a modal never outlives a page
	# change: the page changes once the open viewers have closed (a rebuild of the same
	# page under a viewer, the Modem after a shred, goes on at once).
	if screen_name(s) != _shown_screen and PageTransition.modal_open(self):
		PageTransition.after_modals(self, _show_current)
		return
	_refresh_status()
	match s.run.phase:
		RunState.Phase.MAP:
			_show_map()
		RunState.Phase.COMBAT:
			_show_combat()
		RunState.Phase.REWARD:
			_show_reward()
		RunState.Phase.EVENT:
			_show_event()
		RunState.Phase.SHOP:
			_show_shop()
		RunState.Phase.RAID:
			_show_raid()
		_:
			_show_end()


## `glass` = false for screens built from their own terminal windows (the city shows
## between them).
func _set_panel(p: Control, glass: bool = true) -> void:
	if _panel != null:
		_panel.queue_free()
	_panel = p
	combat_scene = null
	# ANIM-4b: the old page's drop targets go with it (flights in the air keep going).
	if drops != null:
		drops.reset()
	# H24 S4: a page shows its words as given (translated once where built); the fight
	# translates its own.
	if not p.has_method("attach_netrun"):
		TextDb.shown_as_given(p)
	# A fight docks its subtitles in its own column and needs the height (H21 #11).
	subtitle_strip.visible = not p.has_method("attach_netrun")
	hud.stats.max_height = HudBar.BAND_HEIGHT if p.has_method("attach_netrun") else 0.0
	_panel_host.theme_type_variation = &"GlassPanel" if glass else &""
	_clear_route()
	# Art pass W8c (W7 hookup, ART_BIBLE §9.5, §2 CITY): a page starts with the city as a
	# backdrop (no map dim, no calm zones); the map pages (route, raid) and the paper pages
	# (event) set theirs after this.
	var no_calm: Array[Control] = []
	_city_page(false, no_calm)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_STOP
	_panel_host.add_child(p)
	var s := RunManager.netrun
	# ANIM-6: a new screen enters (glass slides in, paper drops); a page rebuilt on the same
	# screen (the Modem after a purchase) just shows. Focus lands when it ends.
	var screen := screen_name(s)
	entering = screen != _shown_screen
	_shown_screen = screen
	if p.has_method("focus_hand"):
		p.focus_hand()  # the combat scene links and focuses its own hand
	else:
		UiWrap.fit(p)
		UiFocus.link_layout(p)
		if entering:
			if not glass:
				# ANIM-R1 M11: a page of windows over the city: its glass is the windows, so
				# the CRT roll's band crosses them, never the whole screen (on the loot pick's
				# first frame it ran across half the screen over the bare city).
				PageTransition.glass_is_windows(p)
			PageTransition.enter(p, page_look(p), _focus_page.bind(p))
		else:
			_focus_page(p)
	_title_screen(s)
	set_page_prompts([] if p.has_method("attach_netrun") else prompts_for(s))
	# H24 S15: lines tied to the screen being left end here.
	Dialogue.enter_screen(screen_name(s))
	if s != null and not s.run.is_over():
		AudioDirector.play_music("raid" if s.run.phase == RunState.Phase.RAID else "netrun", s.campaign.corporation_id)
		if s.run.phase != RunState.Phase.COMBAT:
			background.visible = true
	if RunManager.campaign != null:
		background.corp_creep = clampf(RunManager.campaign.heat / float(RunManager.config().heat_max), 0.0, 1.0)
		background.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
		background.set_district(RunManager.campaign.corporation_id)
	# The combat panel brings its own log; give it the height instead.
	_log.custom_minimum_size = Vector2(0, 50 if p.get_script() == COMBAT_SCENE.get_script() or p.has_method("attach_netrun") else 110)


## Art pass W8c (W7 hookup): the city behind the page: map mode (§9.5: dimmed 40% and
## blurred under the Route and Raid maps) and the calm zones (§2 CITY: text panels over it).
func _city_page(map_mode: bool, calm: Array[Control]) -> void:
	if background == null or background.city == null:
		return
	background.set_map_mode(map_mode)
	background.set_calm_controls(calm)


## A page's first focus: the control it names (FIRST_FOCUS_META: the Modem's first item,
## ANIM-R3 A7: its prompt says "A Buy" and the focus sat on the socket list), else its first
## usable control.
func _focus_page(p: Control) -> void:
	var first: Variant = p.get_meta(FIRST_FOCUS_META) if is_instance_valid(p) and p.has_meta(FIRST_FOCUS_META) else null
	if first is Control and is_instance_valid(first) and (first as Control).is_inside_tree() \
			and (first as Control).get_focus_mode_with_override() != Control.FOCUS_NONE:
		_focus_now.call_deferred(p, first)
		return
	UiFocus.focus_first(p)


## Untyped on purpose: the deferred call can land after the page was freed.
func _focus_now(page, first) -> void:
	if not is_instance_valid(page) or not is_instance_valid(first) or not (first as Control).is_inside_tree() \
			or (first as Control).get_focus_mode_with_override() == Control.FOCUS_NONE:
		return
	var owner := get_viewport().gui_get_focus_owner()
	if owner == null or not (page as Node).is_ancestor_of(owner):
		(first as Control).grab_focus()


## The meta naming a page's first focus.
const FIRST_FOCUS_META := &"first_focus"
## Art pass W8c: the meta naming a page's material when it sits deeper than look_of reads
## (the event's paper inside its safe-margin frame).
const PAGE_LOOK_META := &"page_look"


## The page's look for its entrance (PageTransition: paper drops, glass slides).
static func page_look(p: Control) -> int:
	return int(p.get_meta(PAGE_LOOK_META)) if p.has_meta(PAGE_LOOK_META) else PageTransition.look_of(p)


## The pad prompts of the screen for the run's phase (H23 S11): A presses the focused
## choice (its verb here), B leaves the Modem, Menu opens the settings. A fight shows its
## own prompts.
static func prompts_for(s: NetrunSession) -> Array:
	var accept := "Select" # TR
	var out: Array = []
	if s != null:
		match s.run.phase:
			RunState.Phase.MAP:
				accept = "Go" # TR
			RunState.Phase.REWARD:
				accept = "Take" # TR
			RunState.Phase.EVENT:
				accept = "Choose" # TR
			RunState.Phase.SHOP:
				accept = "Buy" # TR
			RunState.Phase.COMBAT:
				return out
	out.append([&"ui_accept", accept])
	# ANIM-4b: the pick-up key carries the focused item to a target (D-pad, A drops).
	if s != null and has_drags(s):
		out.append([&"end_turn", "Pick up"]) # TR
	if s != null and s.run.phase == RunState.Phase.SHOP:
		out.append([&"ui_cancel", "Leave"]) # TR
	out.append([&"open_settings", "Settings"]) # TR
	return out


## The screen for the run's phase, as Dialogue scopes its lines (H24 S15).
static func screen_name(s: NetrunSession) -> String:
	if s == null:
		return "netrun_start"
	match s.run.phase:
		RunState.Phase.MAP:
			return "route"
		RunState.Phase.COMBAT:
			return "combat"
		RunState.Phase.REWARD:
			return "loot"
		RunState.Phase.EVENT:
			return "event"
		RunState.Phase.SHOP:
			return "shop"
		RunState.Phase.RAID:
			return "netrun_raid"
	return "run_end"


## A viewer, the Daemon tray or the pause menu is open over the screen (it takes B).
func _modal_open() -> bool:
	for n in ["DeckView", "SpinnerView", "LoadoutView", "DaemonTray"]:
		if has_node(n):
			return true
	return _settings_panel != null


## Names the screen on the HUD strip from the run phase (STYLE_GUIDE 4, "Neon city").
func _title_screen(s: NetrunSession) -> void:
	if s == null:
		hud.set_screen("", tr("NETRUN"))
		return
	match s.run.phase:
		RunState.Phase.MAP:
			hud.set_screen("", tr("NETRUN // ROUTE"))
		RunState.Phase.COMBAT:
			hud.set_screen("", "")
		RunState.Phase.REWARD:
			hud.set_screen("", tr("BREACH PAYOUT"))
		RunState.Phase.EVENT:
			# ANIM-R2 E2: a title as short as the Modem's, so the top bar keeps one row at 1.6
			# (the long one wrapped the tags onto two rows and pushed the page down).
			hud.set_screen("04", tr("TERMINAL EVENT"))
		RunState.Phase.SHOP:
			hud.set_screen("05", tr("MODEM CYBER SHOP"))
		RunState.Phase.RAID:
			hud.set_screen("", tr("NETRUN // RAID"))
		_:
			hud.set_screen("", tr("NETRUN // JACK OUT"))


## Art pass W8c: the start page's seed field: its first value and its most digits (the old
## spin box's 0-999999).
const START_SEED := 1
const SEED_DIGITS := 6


## The digits of `t` (a typed seed), in order.
static func seed_digits(t: String) -> String:
	var out := ""
	for ch in t:
		if ch >= "0" and ch <= "9":
			out += ch
	return out


func _show_start() -> void:
	_refresh_status()
	var box := VBoxContainer.new()
	box.add_child(GraffitiTag.new(tr("NETRUN")))
	var row := HBoxContainer.new()
	box.add_child(row)
	row.add_child(_label(tr("Campaign seed:")))
	# Art pass W8c (ART_BIBLE §6.5: seeds and codes in a mono text field, never a native
	# spin box): digits only; an empty field is seed 0.
	var seed_field := CodeField.new(str(START_SEED))
	seed_field.name = "SeedField"
	seed_field.field.max_length = SEED_DIGITS
	seed_field.text_changed.connect(func(t: String) -> void:
		var digits := seed_digits(t)
		if digits != t:
			seed_field.value = digits
			seed_field.field.caret_column = digits.length())
	row.add_child(seed_field)
	row.add_child(_button(tr("New campaign"), func() -> void: new_campaign(int(seed_digits(seed_field.value)))))
	if RunManager.has_save():
		box.add_child(_icon_button(tr("Resume saved game"), resume, StatIcon.CONTINUE))
	if RunManager.campaign != null:
		var living := RunManager.campaign.living_operatives()
		var info := tr("Campaign: Heat %d, Schematics %d, roster %d living.") % [RunManager.campaign.heat, RunManager.campaign.schematics, living.size()]
		box.add_child(_label(info))
		for op in living:
			box.add_child(_label(tr("  %s (%s) Rank %d, HP %d/%d, deck %d, daemons %d") % [op.name, _content_name(op.class_id), op.rank, op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size()]))
		if RunManager.has_active_run():
			box.add_child(_icon_button(tr("Continue the current run"), _show_current, StatIcon.CONTINUE))
		elif not living.is_empty():
			box.add_child(_icon_button(tr("Start a netrun at the first open Site"), func() -> void: start_run(1), StatIcon.PLAY))
		box.add_child(_icon_button(tr("Go to HQ (City Grid, raids, roster)"), RunManager.go_to_hq, StatIcon.BACK))
	_set_panel(box)


## The netrun map as a wireframe graph (GDD 9.1): click a reachable node to enter it.
## Keyboard: 1-9 pick the reachable nodes in order.
func _show_map() -> void:
	var s := RunManager.netrun
	# The route on the city in blueprint, zoomed into the target Site's neighbourhood;
	# GRID VIEW zooms out to the whole campaign Grid (greyed city). `map_view` stays as the
	# route model (hidden): pad keys and clicks go through it as before.
	var panel := VBoxContainer.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var top := HBoxContainer.new()
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(top)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_child(spacer)
	map_view = NetrunMapView.new()
	map_view.visible = false
	map_view.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
	map_view.show_map(s.run.map, s.run.current_node_id, s.run.visited, s.available_nodes(), s.map_heat())
	map_view.node_clicked.connect(func(id: StringName) -> void:
		if RunManager.netrun != null and RunManager.netrun.available_nodes().has(id):
			enter_node(id))
	top.add_child(map_view)
	# The number keys pick nodes on the keyboard; the pad has none, so its hints are blank
	# (H20: each button carries its own key hint, refreshed when the device changes).
	var win := TerminalWindow.new(tr("ROUTE // pick the next node"), Palette.CELL_ACID)
	win.name = "RouteWindow"
	win.custom_minimum_size.x = 300
	win.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	# The route column: the choices, then the map key under them (H22 #14: the route view
	# had none; in the column it hides no part of the route).
	var route_col := VBoxContainer.new()
	route_col.name = "RouteColumn"
	route_col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	route_col.add_theme_constant_override("separation", 8)
	top.add_child(route_col)
	route_col.add_child(win)
	var row := VBoxContainer.new()
	row.name = "RouteNodes"
	win.body.add_child(row)
	_fill_route_choices(row)
	var zoom_btn := _button(tr("GRID VIEW") if not _grid_zoomed else tr("ROUTE VIEW"), func() -> void:
		_grid_zoomed = not _grid_zoomed
		_show_map())
	zoom_btn.name = "GridZoom"
	# Art pass W8c (ART_BIBLE §11 Route, §6.4): the choices lead; the view switch and Save &
	# quit are tertiary (words and icon, no box), so the compact list reads first.
	zoom_btn.theme_type_variation = UiTheme.TERTIARY
	zoom_btn.tooltip_text = UiTip.fold(tr("Zoom out to the whole City Grid.") if not _grid_zoomed else tr("Back to this run's route."))
	IconMark.attach(zoom_btn, StatIcon.MAP)
	win.body.add_child(zoom_btn)
	var quit_btn := _button(tr("Save & quit to start screen"), save_and_quit)
	quit_btn.name = "SaveQuit"
	quit_btn.theme_type_variation = UiTheme.TERTIARY  # art pass W8c: see GridZoom
	quit_btn.tooltip_text = UiTip.fold(tr("Save the run and leave it; Continue picks it up here."))
	IconMark.attach(quit_btn, StatIcon.SAVE)
	win.body.add_child(quit_btn)
	if _grid_zoomed:
		win.body.add_child(MapLegend.new(RunManager.campaign.corporation_id))
	else:
		# The route view's map key (H22 #14: it had none) in the room under the choices,
		# scaled down if that room is short (LegendSpot).
		top.size_flags_vertical = Control.SIZE_EXPAND_FILL
		route_col.size_flags_vertical = Control.SIZE_EXPAND_FILL
		var key_room := Control.new()
		key_room.name = "LegendRoom"
		key_room.mouse_filter = Control.MOUSE_FILTER_IGNORE
		key_room.size_flags_vertical = Control.SIZE_EXPAND_FILL
		route_col.add_child(key_room)
		# H23 S7: the route's own key, the node kinds this route has (not the campaign map's).
		route_legend = RouteLegend.new(RouteLegend.kinds_of(route_graph()["nodes"]), Palette.corp_color(RunManager.campaign.corporation_id))
		key_room.add_child(route_legend)
		spacer.name = "RouteMapArea"
		_route_area = spacer
	_set_panel(panel, false)
	# Art pass W8c (W7 hookup, ART_BIBLE §9.5): the map leads; the city under it dims and blurs.
	var calm: Array[Control] = [win]
	_city_page(true, calm)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if _grid_zoomed:
		var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, CityLayout.threat_paths(RunManager.campaign, RunManager.corporation), s.run.site_id)
		_mount_route(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, 0.85, Vector2(0.4, 0.56), Vector2.INF)
		city_overlay.avoid_controls([win])  # map labels stay clear of the ROUTE window
	else:
		var r := route_graph()
		_mount_route(r["nodes"], r["edges"], CityMapOverlay.Look.ISOLATE, ROUTE_ZOOM, ROUTE_ANCHOR, Vector2.INF)
		city_overlay.here_at = r["entry"]
		city_overlay.ease_rings()  # ANIM-5: the "you are here" ring eases in
		city_overlay.avoid_controls([win, route_legend])
		route_legend.minimum_size_changed.connect(func() -> void: place_route_legend.call_deferred())
		city_overlay.node_clicked.connect(func(id: StringName) -> void: map_view.node_clicked.emit(id))
		place_route_legend.call_deferred()
		route_legend.get_parent().resized.connect(place_route_legend)
		if not background.city.rebuilt.is_connected(place_route_legend):
			background.city.rebuilt.connect(place_route_legend)
		# H24 S12: the route's nodes fitted into the map area beside the ROUTE column (at 1.6 a
		# node sat under the ROUTE window).
		_route_fits = 0
		_fit_route_next_frame()
		spacer.resized.connect(_refit_route)
	# ANIM-R4 H10: a fight's, a boss's and a raid's music are made ahead (a fight's first frame
	# built its loop).
	AudioDirector.prewarm_music(["combat", "boss", "raid"], RunManager.campaign.corporation_id)
	# ANIM-R2 R1 / R2: the next screen is a fight's arena, the Modem, an event or loot, all on
	# the default frame of this city's look: baked now, behind the route (after its own view).
	_prebake_backdrops.call_deferred()


## The ROUTE window's choice buttons for the choices the view shows (view_choices: ANIM-R4
## H11c, the new ones as soon as a move starts), into `row` (emptied first).
func _fill_route_choices(row: VBoxContainer) -> void:
	var s := RunManager.netrun
	# Hidden and freed in place: the button pressed (the move) may be one of them, mid-signal.
	for old in row.get_children():
		(old as CanvasItem).visible = false
		old.queue_free()
	var available := view_choices(s)
	_route_buttons.clear()
	var twins := choice_twins(s)
	var differs := choice_differences(s)
	var ahead_rows := {}
	for i in available.size():
		var node := s.run.map.get_node(available[i])
		# H21 #14: what the node is (word + icon), its index on every device (the map's
		# label carries the same index), Heat when entering changes it.
		# Art pass W8c (ART_BIBLE §11 Route, critique 27): the button says what the node is
		# ("1 Fight"); its Heat, where it leads (H24 S12), whether it is the same as an earlier
		# choice (ANIM-R2 R12) and what only it reaches (ANIM-R3 B3) sit in one compact row
		# of icons and short words under it (the old "[2] Fight > Fight (same as 1)" / "then:"
		# line read harder than the map). The map labels and tooltips keep their words.
		var text := node_word(node)
		var heat := s.node_heat(available[i])
		var id: StringName = available[i]
		var b := _button(text, func() -> void: enter_node(id))
		b.name = "Node%d" % (i + 1)
		var marks := differs.get(id, []) as Array
		var twin := int(twins.get(id, -1))
		var next := next_kinds(s.run.map, node)
		if twin >= 0 or not marks.is_empty() or heat != 0 or not next.is_empty():
			ahead_rows[i] = _ahead_row(i, marks if twin < 0 else [], heat, next, twin)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.set_meta(&"route_base", text)
		b.set_meta(&"route_index", i)
		IconMark.attach(b, node_icon(node), StatIcon.color_of(node_icon(node)))
		# H22 #14: the node's own map icon (the map's painter, its colour for a next node),
		# so the same node looks the same on the button and on the map.
		IconMark.attach_map(b, CityMapOverlay.route_kind(int(node["type"]), bool(node["elite"])), ROUTE_NEXT_COLOR)
		b.tooltip_text = UiTip.fold(route_tip(s, node, heat))
		_route_buttons.append(b)
		row.add_child(b)
		if ahead_rows.has(i):
			row.add_child(ahead_rows[i])
	_label_route_buttons()


## ANIM-R2 R1 / R2: the default frame's bake at this scene's size and at the page's (a fight's
## arena fills the page), with the sizes it was drawn at lately (NeonCity.frame_sizes).
func _prebake_backdrops() -> void:
	if background == null or not is_inside_tree() or RunManager.campaign == null:
		return
	var sizes: Array[Vector2] = [size]
	if _panel_host != null and is_instance_valid(_panel_host):
		var inner := _panel_host.size
		var box := _panel_host.get_theme_stylebox(&"panel", &"GlassPanel")
		if box != null:
			inner -= box.get_minimum_size()
		sizes.append(inner.floor())
	background.city.prebake_frames(sizes)


## The route legend where it covers no route node (H22 #14).
func place_route_legend() -> void:
	if route_legend != null and is_instance_valid(route_legend) and city_overlay != null and is_instance_valid(city_overlay):
		LegendSpot.place(route_legend, city_overlay)


## The route map's area (left of the ROUTE column; null when zoomed out) and the fit
## passes so far (H24 S12).
var _route_area: Control = null
var _route_fits: int = 0


## The route's nodes (icons and pips) fitted into the map area beside the ROUTE column,
## once the page's layout has settled (H24 S12: at 1.6 a node sat under the ROUTE window):
## the camera pans and zooms out as far as ROUTE_MIN_ZOOM, and checks again once the city
## has redrawn (at most ROUTE_FITS_MAX passes).
func fit_route_map() -> void:
	if _grid_zoomed or _route_area == null or not is_instance_valid(_route_area) or not _route_area.is_inside_tree() \
			or city_overlay == null or not is_instance_valid(city_overlay):
		return
	var city := background.city
	if not city.camera_settled():
		_fit_route_after_redraw()
		return
	var area := _route_area.get_global_rect().intersection(get_global_rect())
	if area.size.x <= LegendSpot.MARGIN * 2.0 or area.size.y <= LegendSpot.MARGIN * 2.0:
		return
	if _route_fits >= ROUTE_FITS_MAX:
		return
	# ANIM-R3 B8: a margin the size of a node's reach (its icon, label tab and pips) off the
	# screen's edge, and the street marker kept in frame with the nodes.
	var free := area.grow(-ROUTE_MARGIN * Settings.text_scale)
	var here := city_overlay.here_marker_rects()
	# ANIM-R3 B8: the whole route when it fits at ROUTE_FIT_FLOOR or closer; else the part the
	# player decides on (where they are and the next choices) inside the area with its margins
	# (the whole route squeezed to the minimum zoom jammed its nodes against the screen's edge
	# and put the current node off it).
	var fit := LegendSpot.fit_into(city_overlay, free, ROUTE_ZOOM / city.scale.x, 0.0, [], here)
	if not fit.is_empty() and float(fit["zoom"]) * city.scale.x < ROUTE_FIT_FLOOR:
		fit = LegendSpot.fit_into(city_overlay, free, ROUTE_ZOOM / city.scale.x, ROUTE_MIN_ZOOM / city.scale.x, route_focus_ids(), here)
	elif fit.is_empty() and not route_frames(free):
		fit = LegendSpot.fit_into(city_overlay, free, ROUTE_ZOOM / city.scale.x, ROUTE_MIN_ZOOM / city.scale.x, route_focus_ids(), here)
	if fit.is_empty():
		return
	_route_fits += 1
	var k := float(fit["zoom"])
	var screen := get_global_rect()
	var focus_at := screen.position + city.focus_anchor * screen.size
	var to: Vector2 = fit["to"]
	var from: Vector2 = fit["from"]
	var anchor := (to - (from - focus_at) * k - screen.position) / screen.size
	city.scale = Vector2.ONE * city.scale.x * k
	city.offset_left = 0
	city.offset_top = 0
	city.offset_right = size.x / city.scale.x - size.x
	city.offset_bottom = size.y / city.scale.y - size.y
	city.focus_anchor = anchor
	city.refresh()
	_cut_camera_if_still()  # art pass W8c: reduce motion
	_fit_route_after_redraw()


## ANIM-R3 B8: the route nodes the player decides on: where they are and the next choices.
func route_focus_ids() -> Array:
	var s := RunManager.netrun
	var out: Array = []
	if s == null:
		return out
	if s.run.current_node_id != &"":
		out.append(s.run.current_node_id)
	out.append_array(s.available_nodes())
	return out


## ANIM-R3 B8: true when the part the player decides on (the "you are here" marker, the
## current node and the next choices) is inside `free` (screen px).
func route_frames(free: Rect2) -> bool:
	var rects := LegendSpot.node_rects(city_overlay, false, route_focus_ids())
	rects.append_array(city_overlay.here_marker_rects())
	for r in rects:
		if not free.encloses(r):
			return false
	return true


## ANIM-R3 B8: the route map's margin inside its area at text scale 1.0 (px): a node's icon,
## label tab and pips never touch the screen's edge.
const ROUTE_MARGIN := 36.0


func _fit_route_after_redraw() -> void:
	var city := background.city
	if city.is_baked():
		# ANIM-R2 R1: measured at once under the new camera (see hq_scene._fit_after_redraw).
		city.update_camera()
		fit_route_map()
		return
	if not city.rebuilt.is_connected(fit_route_map):
		city.rebuilt.connect(fit_route_map, CONNECT_ONE_SHOT | CONNECT_DEFERRED)


func _fit_route_next_frame() -> void:
	if not get_tree().process_frame.is_connected(fit_route_map):
		get_tree().process_frame.connect(fit_route_map, CONNECT_ONE_SHOT)


func _refit_route() -> void:
	_route_fits = 0
	_fit_route_next_frame()


## A route node in a word: Fight, Elite fight, Event, Shop, Rack (translated).
static func node_word(node: Dictionary) -> String:
	return TranslationServer.translate(ELITE_WORD if _is_elite(node) else String(NODE_WORDS.get(node["type"], "?")))


## Where a route node leads (H24 S12): the words of the nodes after it, in map order
## ("Event · Shop"), each kind once.
static func ahead_words(map: MapGraph, node: Dictionary) -> String:
	var words := PackedStringArray()
	for nxt in node.get("next", []):
		var n := map.get_node(nxt)
		if n.is_empty():
			continue
		var w := node_word(n)
		if not words.has(w):
			words.append(w)
	return " · ".join(words)


## A route choice's tooltip (H24 S12): what the node is, what it pays, Heat, and where it
## leads.
static func route_tip(s: NetrunSession, node: Dictionary, heat: int) -> String:
	var parts := PackedStringArray()
	parts.append(TranslationServer.translate(String(NODE_TIPS.get(node["type"], ""))))
	if int(node["type"]) == RC.InfilNodeType.ROUTER:
		var pay: Vector2i = s.config.cycles_elite_range if _is_elite(node) else s.config.cycles_router_range
		parts.append(TranslationServer.translate("Pays %d-%d Cycles.") % [pay.x, pay.y])
	if _is_elite(node):
		parts.append(TranslationServer.translate("Elite: a harder fight, and a Firmware chip to pick."))
	if heat != 0:
		parts.append(TranslationServer.translate("Entering it changes Heat by %s.") % TextDb.signed(heat))
	var ahead := ahead_words(s.run.map, node)
	if ahead != "":
		parts.append(TranslationServer.translate("Then you can go to: %s.") % ahead)
	return " ".join(parts)


## A route node's icon: crosshair, crown (elite), terminal, bag (shop), server rack.
static func node_icon(node: Dictionary) -> StringName:
	return StatIcon.ELITE if _is_elite(node) else StringName(NODE_ICONS.get(node["type"], &""))


static func _is_elite(node: Dictionary) -> bool:
	return bool(node["elite"]) and int(node["type"]) == RC.InfilNodeType.ROUTER


## The index route choice `i` shows on its button and its map label: the key that picks it
## on the keyboard ("[1]"), its number on a pad (H21 #14: the pad's labels were identical).
static func route_index_text(i: int) -> String:
	var hint := Settings.hint(StringName("card_%d" % (i + 1))) if i < 9 else ""
	return hint if hint != "" else str(i + 1)


## "[1] Fight" on the keyboard, "1 Fight" on a pad: the route's index follows the device
## and the binds.
func _relabel_route() -> void:
	_label_route_buttons()
	# The map's node labels carry the same hints.
	if not _route_buttons.is_empty() and not _grid_zoomed and city_overlay != null and is_instance_valid(city_overlay) and RunManager.netrun != null:
		var r := route_graph()
		city_overlay.set_graph(r["nodes"], r["edges"])


func _label_route_buttons() -> void:
	var alive: Array[Button] = []
	for b in _route_buttons:
		if not is_instance_valid(b) or b.is_queued_for_deletion():
			continue
		b.text = "%s %s" % [route_index_text(int(b.get_meta(&"route_index"))), String(b.get_meta(&"route_base"))]
		alive.append(b)
	_route_buttons = alive


## ANIM-R2 R12: the open choices that are the same as an earlier one: id -> the index of
## the first such choice. ANIM-R3 B3: the same means the same whole road ahead (it was the
## kind, Heat and the next layer's kinds only: 26 of 42 "(same as N)" choices differed
## further on): the node's kind and Heat and, recursively, the same of every node it leads
## to (subgraph_signatures). The enemy is rolled on entry, so twins really are one choice.
static func choice_twins(s: NetrunSession) -> Dictionary:
	var out := {}
	var first := {}
	var open := view_choices(s)
	var signs := subgraph_signatures(s.run.map, s.node_heat)
	for i in open.size():
		var sig: int = signs.get(open[i], -1)
		if first.has(sig):
			out[open[i]] = first[sig]
		else:
			first[sig] = i
	return out


## ANIM-R3 B3: every node's signature of the whole road from it (id -> int): two nodes get
## the same number exactly when their kinds, their Heat (`heat_of`: id -> int) and, as
## multisets, the signatures of the nodes they lead to are the same. Built from the last
## layer back, interned (linear in the map, no unfolding). Pure.
static func subgraph_signatures(map: MapGraph, heat_of: Callable) -> Dictionary:
	var out := {}
	var intern := {}
	for li in range(map.layers.size() - 1, -1, -1):
		for n: Dictionary in map.layers[li]:
			var kids: Array[int] = []
			for nxt in n.get("next", []):
				kids.append(int(out.get(nxt, -1)))
			kids.sort()
			var key := "%s|%s|%d|%s" % [int(n["type"]), _is_elite(n), int(heat_of.call(n["id"])), ",".join(PackedStringArray(kids.map(func(v: int) -> String: return str(v))))]
			if not intern.has(key):
				intern[key] = intern.size()
			out[n["id"]] = intern[key]
	return out


## ANIM-R3 B3: the kinds of node (their StatIcons, in AHEAD_ORDER) and Heat reachable
## further on from `node` (not the node itself). Pure.
static func ahead_kinds(map: MapGraph, node: Dictionary, heat_of: Callable) -> Array[StringName]:
	var seen := {}
	var found := {}
	var todo: Array = (node.get("next", []) as Array).duplicate()
	while not todo.is_empty():
		var id: StringName = todo.pop_back()
		if seen.has(id):
			continue
		seen[id] = true
		var n := map.get_node(id)
		if n.is_empty():
			continue
		found[node_icon(n)] = true
		if int(heat_of.call(id)) > 0:
			found[StatIcon.HEAT] = true
		todo.append_array(n.get("next", []))
	var out: Array[StringName] = []
	for k in AHEAD_ORDER:
		if found.has(k):
			out.append(k)
	return out


## The reward and risk icons a route choice can show, in order.
const AHEAD_ORDER: Array[StringName] = [StatIcon.ELITE, StatIcon.SHOP, StatIcon.TERMINAL, StatIcon.RACK, StatIcon.HEAT]


## ANIM-R3 B3: per open choice, the kinds ahead it reaches that not every choice reaches
## (id -> Array[StringName]): what telling them apart rests on.
static func choice_differences(s: NetrunSession) -> Dictionary:
	var open := view_choices(s)
	var per := {}
	var common := {}
	for i in open.size():
		var kinds := ahead_kinds(s.run.map, s.run.map.get_node(open[i]), s.node_heat)
		per[open[i]] = kinds
		if i == 0:
			for k in kinds:
				common[k] = true
		else:
			for k in common.keys():
				if not kinds.has(k):
					common.erase(k)
	var out := {}
	for id in per:
		var diff: Array[StringName] = []
		for k in per[id]:
			if not common.has(k):
				diff.append(k)
		out[id] = diff
	return out


## ANIM-R3 B3: the row under choice `i`'s button: its own Heat on entering (a Heat icon and
## the number, it was in words only) and the icons of what lies further on that the other
## choices do not reach, each with its word as a tooltip.
##
## Art pass W8c (ART_BIBLE §11 Route, critique 27): one compact row, icons with short words
## and no emoji: the Heat on entering ([flame] +2), where the choice leads next ([>] [x]
## Fight · [?] Event), then "(same as 1)" for a twin or, after a thin rule, what only this
## way reaches further on ([crown] Elite). An icon and its word stay together (a flow
## wraps between pairs, never inside one). `next` is next_kinds(); `twin` the index of
## the earlier choice this one equals (-1: none).
func _ahead_row(i: int, kinds: Array, heat: int, next: Array = [], twin: int = -1) -> Control:
	var row := HFlowContainer.new()
	row.name = "Ahead%d" % (i + 1)
	row.mouse_filter = Control.MOUSE_FILTER_PASS
	row.add_theme_constant_override("h_separation", UiTheme.SP_XS)
	var side := UiTheme.BASE_SIZE * Settings.text_scale * IconMark.SIZE_FACTOR
	var pad := Control.new()
	pad.custom_minimum_size.x = side
	pad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(pad)
	if heat != 0:
		var hp := _icon_word("EnterHeat", StatIcon.HEAT, TextDb.signed(heat), side, tr("Entering it changes Heat by %s.") % TextDb.signed(heat))
		hp.get_node(^"Word").name = "EnterHeatValue"
		row.add_child(hp)
	if not next.is_empty():
		var lead := IconMark.standalone(StatIcon.NEXT, side, Palette.TEXT_MID)
		lead.name = "AheadNext"
		lead.mouse_filter = Control.MOUSE_FILTER_PASS
		var words := PackedStringArray()
		for k: StringName in next:
			words.append(tr(String(ROUTE_SHORT.get(k, ""))))
		lead.tooltip_text = UiTip.fold(tr("Then you can go to: %s.") % " · ".join(words))
		row.add_child(lead)
		for k: StringName in next:
			row.add_child(_icon_word("Next_%s" % k, k, tr(String(ROUTE_SHORT.get(k, ""))), side, lead.tooltip_text))
	if twin >= 0:
		var same := _label(tr("(same as %d)") % (twin + 1))
		same.name = "TwinOf"
		same.add_theme_color_override("font_color", Palette.TEXT_MID)
		same.tooltip_text = UiTip.fold(tr("The same road as choice %d: the same kinds of node and Heat all the way on.") % (twin + 1))
		same.mouse_filter = Control.MOUSE_FILTER_PASS
		row.add_child(same)
	elif not kinds.is_empty():
		var rule := ColorRect.new()
		rule.name = "AheadRule"
		rule.color = Palette.TERMINAL_EDGE
		rule.custom_minimum_size = Vector2(1.0, side)
		rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(rule)
		for k: StringName in kinds:
			row.add_child(_icon_word("Ahead_%s" % k, k, tr(String(ROUTE_SHORT.get(k, ""))), side,
				tr("Further on: %s (only this way).") % tr(String(AHEAD_WORDS.get(k, "")))))
	return row


## Art pass W8c: an icon and its short word kept together (a route row's item): a box
## named `id` holding "Icon" and "Word" (the word in the icon's colour), with `tip`.
func _icon_word(id: String, kind: StringName, word: String, side: float, tip: String) -> Control:
	var pair := HBoxContainer.new()
	pair.name = id
	pair.mouse_filter = Control.MOUSE_FILTER_PASS
	pair.add_theme_constant_override("separation", UiTheme.SP_XS / 2)
	pair.tooltip_text = UiTip.fold(tip)
	var m := IconMark.standalone(kind, side, StatIcon.color_of(kind))
	m.name = "Icon"
	m.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pair.add_child(m)
	var l := _label(word)
	l.name = "Word"
	l.add_theme_color_override("font_color", StatIcon.color_of(kind).lerp(Palette.TEXT_HI, ROUTE_WORD_LIGHTEN))
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pair.add_child(l)
	return pair


## Art pass W8c: the short word beside each route icon (keys: the route's own node words, so
## the button, the map and the row name a node alike).
const ROUTE_SHORT := {StatIcon.FIGHT: "Fight", StatIcon.ELITE: ELITE_WORD, StatIcon.SHOP: "Shop", # TR
	StatIcon.TERMINAL: "Event", StatIcon.RACK: "Rack", StatIcon.HEAT: "Heat"} # TR
## How far a row's word is lightened from its icon's colour toward TEXT_HI (contrast §3.7 on glass).
const ROUTE_WORD_LIGHTEN := 0.35
## The order of the kinds a choice leads to next.
const NEXT_ORDER: Array[StringName] = [StatIcon.FIGHT, StatIcon.ELITE, StatIcon.TERMINAL, StatIcon.SHOP, StatIcon.RACK]


## Art pass W8c: the kinds of node a route node leads to next (its "next" nodes' icons, each
## once, in NEXT_ORDER). Pure.
static func next_kinds(map: MapGraph, node: Dictionary) -> Array[StringName]:
	var found := {}
	for nxt in node.get("next", []):
		var n := map.get_node(nxt)
		if not n.is_empty():
			found[node_icon(n)] = true
	var out: Array[StringName] = []
	for k in NEXT_ORDER:
		if found.has(k):
			out.append(k)
	return out


## The words of the reward and risk icons (translated where shown).
const AHEAD_WORDS := {StatIcon.ELITE: "an Elite fight", StatIcon.SHOP: "a Shop", StatIcon.TERMINAL: "an Event", # TR
	StatIcon.RACK: "a Rack", StatIcon.HEAT: "Heat"} # TR


## The run's map as buildings in the target Site's neighbourhood (layers step in from
## the street towards the Site).
## ANIM-R4 H11c: the choices the route view shows: the open nodes, or, while the node just
## entered is being played (a move under way, a fight), the nodes it leads to (the next
## choices, shown at once: they were the old ones until the move's pulse landed).
static func view_choices(s: NetrunSession) -> Array[StringName]:
	var open := s.available_nodes()
	if not open.is_empty() or s.run.current_node_id == &"" or s.run.is_over():
		return open
	var out: Array[StringName] = []
	for n in s.run.current_node().get("next", []):
		out.append(n)
	return out


## ANIM-R4 H11c: the walked route (the nodes visited and the one the Cell stands on) stays
## on the map as a faint line (alpha of the Cell's pink, px width).
const ROUTE_TRAIL_ALPHA := 0.4
const ROUTE_TRAIL_WIDTH := 2.2


func route_graph() -> Dictionary:
	var s := RunManager.netrun
	var map := s.run.map
	var target: Vector2 = CityLayout.site_points(RunManager.corporation).get(s.run.site_id, NeonCity.hq_of(RunManager.corporation.id))
	var layers := map.layer_count()
	var available := view_choices(s)
	var type_glyph := {RC.InfilNodeType.ROUTER: "○", RC.InfilNodeType.TERMINAL: "▭", RC.InfilNodeType.MODEM: "◇", RC.InfilNodeType.SERVER_RACK: "⬢"}
	var twins := choice_twins(s)
	var rows := {}
	for n in map.all_nodes():
		rows[int(n["layer"])] = maxi(int(rows.get(int(n["layer"]), 0)), int(n["index"]) + 1)
	var nodes: Array[Dictionary] = []
	for n in map.all_nodes():
		var li := int(n["layer"])
		var count := int(rows[li])
		var at := target - CityLayout.RIGHT * (layers - li) * 1.7 + CityLayout.DOWN * (int(n["index"]) - (count - 1) * 0.5) * 2.2
		var col := Palette.NET_CYAN
		if n["id"] == s.run.current_node_id:
			col = Palette.CELL_PINK
		elif available.has(n["id"]):
			col = ROUTE_NEXT_COLOR
		elif s.run.visited.has(n["id"]):
			col = Palette.NET_CYAN  # ANIM-R1 M7: dimmed and ticked by the map (visited_dim)
		elif n["elite"] or n["type"] == RC.InfilNodeType.SERVER_RACK:
			col = Palette.corp_color(RunManager.campaign.corporation_id)
		var idx := available.find(n["id"])
		var label := "%s %s" % [route_index_text(idx), node_word(n)] if idx >= 0 else ""
		# ANIM-R3 B3: a choice's Heat shows on the map too (it was on its button in words only).
		var nh := s.node_heat(n["id"]) if idx >= 0 else 0
		if nh != 0:
			label += tr(" %s Heat") % TextDb.signed(nh)
		if twins.has(n["id"]):
			label += " " + tr("(same as %d)") % (int(twins[n["id"]]) + 1)
		# The reachable nodes carry their route button's index and word (H21 #14); "kind"
		# is the StatIcon the button shows.
		nodes.append({"id": n["id"], "at": at, "color": col, "glyph": type_glyph.get(int(n["type"]), "?"),
			"label": label, "big": n["type"] == RC.InfilNodeType.SERVER_RACK,
			# H23 S7: the kind and what it does, in the route key's words (H24 S3: translated).
			"tip": "%s." % tr(String(RouteLegend.MEANINGS.get(CityMapOverlay.route_kind(int(n["type"]), n["elite"]), node_word(n)))),
			# The map paints its own node icons (CityMapOverlay); the route buttons draw the same
			# kind with the same painter (H22 #14).
			"kind": CityMapOverlay.route_kind(int(n["type"]), n["elite"]), "icon": node_icon(n),
			"here": n["id"] == s.run.current_node_id, "next": idx >= 0,
			"visited": s.run.visited.has(n["id"]) and n["id"] != s.run.current_node_id})
	var edges: Array[Dictionary] = []
	for n in map.all_nodes():
		for nxt in n["next"]:
			var live: bool = n["id"] == s.run.current_node_id and available.has(nxt)
			var walked: bool = _walked(s, n["id"]) and _walked(s, nxt)
			if walked:
				edges.append({"a": n["id"], "b": nxt, "color": Color(Palette.CELL_PINK, ROUTE_TRAIL_ALPHA), "width": ROUTE_TRAIL_WIDTH, "dashed": false, "flow": false, "trail": true})
				continue
			edges.append({"a": n["id"], "b": nxt, "color": Palette.CELL_ACID if live else Color(Palette.NET_CYAN, 0.45), "width": 3.0 if live else 1.6, "dashed": not live, "flow": live})
	# ANIM-R3 B8: before the first node the Cell stands at the street, one step before the
	# route's first layer: the "you are here" marker is drawn there (it was drawn nowhere).
	var entry := Vector2.INF
	if s.run.current_node_id == &"":
		entry = target - CityLayout.RIGHT * (layers + 1) * 1.7
	return {"nodes": nodes, "edges": edges, "entry": entry}


## Whether the run has walked node `id` (visited, or where it stands).
static func _walked(s: NetrunSession, id: StringName) -> bool:
	return s.run.visited.has(id) or id == s.run.current_node_id


func _mount_route(nodes: Array[Dictionary], edges: Array[Dictionary], look: int, zoom: float, anchor: Vector2, focus: Vector2) -> void:
	_clear_route()
	var city := background.city
	city_overlay = CityMapOverlay.new(city)
	# H24 S4: the node tips come translated (the screens build them), shown as given.
	city_overlay.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	city.add_child(city_overlay)
	city_overlay.set_look(look)
	city_overlay.set_graph(nodes, edges)
	city.scale = Vector2(zoom, zoom)
	city.offset_left = 0
	city.offset_top = 0
	city.offset_right = size.x / zoom - size.x
	city.offset_bottom = size.y / zoom - size.y
	city.focus_grid = city_overlay.centre() if focus == Vector2.INF else focus
	city.focus_anchor = anchor
	city.refresh()
	_cut_camera_if_still()


## Art pass W8c (W9 reduce motion, ART_BIBLE §12): with camera moves off, a map page cuts to
## its end framing: any held frame or ease is dropped (the fit passes then land at once).
func _cut_camera_if_still() -> void:
	if not Motion.camera_moves_allowed() and background != null:
		background.settle_camera()


func _clear_route() -> void:
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.queue_free()
	city_overlay = null
	var city := background.city
	if city.focus_grid != Vector2.INF or city.scale != Vector2.ONE:
		city.focus_grid = Vector2.INF
		city.scale = Vector2.ONE
		city.offset_right = 0
		city.offset_bottom = 0
		city.refresh()


## Raid playout (GDD 7.2): threat markers animate over the Grid; 1x/2x/4x and skip. The
## raid plays on the city (the Grid overlay, like the HQ playout), the feed at the side.
func _show_raid_playout(events: Array[Dictionary], before: CampaignState = null) -> void:
	var c := RunManager.campaign
	var box := HBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(spacer)
	var legend := MapLegend.pin_to(spacer, c.corporation_id)
	_fight_parts = [spacer, legend]
	var side := VBoxContainer.new()
	side.add_theme_constant_override("separation", 12)
	box.add_child(side)
	var feed := TerminalWindow.new(tr("RAID FEED // LIVE"), Palette.corp_color(c.corporation_id))
	side.add_child(feed)
	playout = RaidPlayoutPanel.new(null, RaidPlayoutPanel.LOG_SIZE)
	feed.body.add_child(playout)
	var cont := _icon_button(tr("Continue"), _show_current, StatIcon.CONTINUE)
	cont.disabled = true
	playout.finished.connect(func() -> void:
		cont.disabled = false
		background.city.release_influence())
	# ANIM-5: Skip goes straight on (the raid's result).
	playout.skipped.connect(_show_current)
	side.add_child(cont)
	_set_panel(box, false)
	var calm_feed: Array[Control] = [side]
	_city_page(true, calm_feed)  # art pass W8c (W7 hookup, §9.5)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var pre := before if before != null else c
	var g := CityLayout.grid_graph(pre, RunManager.corporation, CityLayout.threat_paths(pre, RunManager.corporation))
	_mount_route(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, 0.85, Vector2(0.4, 0.56), Vector2.INF)
	city_overlay.avoid_controls([side])
	playout.grid_view = city_overlay
	playout.attach_fx(c.last_raid, c.grid.home_site_id, c.grid.home_max_integrity, Palette.corp_color(c.corporation_id))
	# ANIM-R1 M4: each step's fight is framed (the camera eases in to it) before it plays.
	playout.framer = _frame_fight.bind(city_overlay)
	# ANIM-R4 H11a: the top bar's Heat changes with the feed's Heat line, not before.
	if not _instant_playout() and before != null:
		hud_heat_shown = before.heat
		_refresh_status()
	playout.event_shown.connect(_on_raid_event_shown)
	playout.finished.connect(_release_hud_heat)
	playout.play(events, _instant_playout())
	if playout.is_done() and _instant_playout():
		_show_current()


## ANIM-R4 H11a: the top bar's HEAT during a raid's playout: what the feed has told (-1:
## the campaign's own).
var hud_heat_shown: int = -1


## ANIM-R4 H11a: a raid event the feed has just told: its Heat line moves the top bar's Heat.
func _on_raid_event_shown(e: Dictionary) -> void:
	if String(e.get("type", "")) == "heat" and hud_heat_shown >= 0 and e.has("after"):
		hud_heat_shown = int(e["after"])
		_refresh_status()


func _release_hud_heat() -> void:
	if hud_heat_shown >= 0:
		hud_heat_shown = -1
		_refresh_status()


## ANIM-R1 M4: the mid-run raid's camera: each step eases to its fight (the guns firing
## and their targets, else the nodes hit, else where threats go) at RAID_ZOOM; returns the
## seconds the ease takes (0 when the frame stays).
func _frame_fight(sites: Array[StringName], overlay: CityMapOverlay) -> float:
	if not is_instance_valid(overlay) or overlay != city_overlay or sites.is_empty():
		return 0.0
	var pts := PackedVector2Array()
	for id in sites:
		pts.append(Vector2(overlay.lot_of(id)) + Vector2(0.5, 0.5))
	var hq_script: GDScript = load("res://scripts/ui/hq_scene.gd")
	var secs := background.frame_points(pts, hq_script.fight_area(_fight_parts), RAID_ZOOM, RAID_MIN_ZOOM)
	# Art pass W8c (W9 reduce motion, ART_BIBLE §12): no camera move: the fight's frame cuts in.
	if not Motion.camera_moves_allowed():
		background.settle_camera()
		return 0.0
	return secs


## ANIM-R3 B5: the interlude's forecast words (the raid setup's, translated once) and its
## stamp's side at text scale 1.0 and how far it follows the text size.
const RAID_FORECAST_CAPTION := "IF THE RAID\nRUNS NOW:" # TR
const RAID_STAMP := 104.0
const RAID_STAMP_FOLLOW := 0.3


## ANIM-R1 M8: the raid interlude's map area, framed once laid out (every node of the Grid in
## it), and whether that framing is still to come (arrival_ready waits for it).
var _raid_map_area: Control = null
var _raid_map_framing: bool = false
## The interlude window's width at text scale 1.0 and how far it grows with the text (px, x).
const RAID_WINDOW_WIDTH := 560.0
const RAID_WINDOW_GROW := 1.3
const RAID_MAP_ANCHOR := Vector2(0.7, 0.55)


func _frame_raid_map() -> void:
	_raid_map_framing = true
	await get_tree().process_frame
	_raid_map_framing = false
	if _raid_map_area == null or not is_instance_valid(_raid_map_area) or city_overlay == null or not is_instance_valid(city_overlay):
		return
	var pts := PackedVector2Array()
	for n in city_overlay.nodes:
		pts.append(Vector2(n["at"]) + Vector2(0.5, 0.5))
	# (Art pass W8c, W9 reduce motion: the interlude's frame always cuts in; settle_camera
	# drops any hold, so no camera move plays with or without reduce motion.)
	background.frame_points(pts, _raid_map_area.get_global_rect().grow(-LegendSpot.MARGIN * 2.0), RAID_ZOOM, RAID_MIN_ZOOM)
	background.settle_camera()




## The raid playout map's parts the fight frame keeps to: [the map's area, its key].
var _fight_parts: Array = []
## ANIM-R1 M4: the mid-run raid playout's fight camera: the closest and furthest zoom.
const RAID_ZOOM := 1.6
const RAID_MIN_ZOOM := 0.85


func _instant_playout() -> bool:
	return not Motion.animating()


func _show_combat() -> void:
	var s := RunManager.netrun
	var scene: Control = COMBAT_SCENE.instantiate()
	scene.auto_start = false
	scene.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_set_panel(scene)
	background.visible = false  # the arena draws its own wireframe world
	combat_scene = scene
	scene.attach_netrun(s)
	scene.engine.state_changed.connect(_on_combat_state_changed)
	if scene.has_signal(&"continue_requested"):
		scene.connect(&"continue_requested", _leave_fight)


func _on_combat_state_changed(state: CombatState, _events: Array[Dictionary]) -> void:
	# ANIM-R5 combat 1: a SEND IT that ends the fight keeps the top bar (HP, CYCLES, Heat...)
	# and the run's report (its DISPATCH line) until the replay lands VICTORY / DEFEAT.
	var held := state.is_over() and combat_scene != null and combat_scene.has_method(&"outcome_pending") and bool(combat_scene.call(&"outcome_pending"))
	if not held:
		_refresh_status()
	if state.is_over():
		RunManager.after_step()
		var report: Array[Dictionary] = RunManager.netrun.last_events.duplicate()
		if held:
			combat_scene.connect(&"outcome_landed", _on_combat_outcome_landed.bind(report), CONNECT_ONE_SHOT)
		else:
			_report(report)
		# ANIM-R3 A6h: the fight's next step shows in SEND IT's place (LOOT when a payout
		# waits, else CONTINUE; ANIM-R5 combat 2: JACK OUT when the operative flatlined);
		# pressing it moves on now. The fight shows it once its outcome lands.
		if combat_scene != null and combat_scene.has_method(&"show_continue"):
			var phase := RunManager.netrun.run.phase if RunManager.netrun != null else RunState.Phase.MAP
			var next := TextDb.mark("LOOT") if phase == RunState.Phase.REWARD else TextDb.mark("CONTINUE")
			if state.outcome == CombatState.Outcome.DEFEAT:
				next = TextDb.mark("JACK OUT")
			combat_scene.call(&"show_continue", next)
		# Leave the final combat state visible for a moment, then move on: once the combat
		# replay (the last hits, the break, VICTORY) has played out or been skipped.
		_leave_generation += 1
		if combat_scene != null and combat_scene.has_method("motion_seconds_left") and float(combat_scene.call("motion_seconds_left")) > 0.0:
			combat_scene.connect("motion_settled", _hold_then_show.bind(_leave_generation), CONNECT_ONE_SHOT)
		else:
			_hold_then_show(_leave_generation)


## ANIM-R5 combat 1: the fight's outcome has landed: the top bar moves on and the run's
## report (a flatline's DISPATCH line) plays.
func _on_combat_outcome_landed(report: Array[Dictionary]) -> void:
	_refresh_status()
	_report(report)


## The pause on the final combat state (`combat_end_hold`) before the netrun moves on.
func _hold_then_show(generation: int = -1) -> void:
	var timer := get_tree().create_timer(Motion.seconds(&"combat_end_hold"))
	timer.timeout.connect(_leave_after_hold.bind(generation if generation >= 0 else _leave_generation))


## The hold ran out: the netrun moves on, unless the player already did.
func _leave_after_hold(generation: int) -> void:
	if generation == _leave_generation and combat_scene != null:
		_show_current()


## ANIM-R5 combat captures (dev shortcut, `--demo-combat --demo-end=win|lose`): once the
## fight's page has settled, the enemy (win) or the operative (lose) is set one hit from 0
## (demo run only) and the wheels nudged until the forecast ends the fight; then SEND IT.
func _demo_combat_end(kind: String) -> void:
	while combat_scene == null or PageTransition.running(self):
		await get_tree().process_frame
	for f in DEMO_SETTLE_FRAMES:
		await get_tree().process_frame
	var scene := combat_scene
	var eng: CombatEngine = scene.get(&"engine")
	var st := eng.state()
	if kind == "hover":
		# ANIM-R5 combat 7: a card hover that changes a tag (its WAS row shows).
		for i in st.hand.size():
			scene.call(&"_preview_card", i)
			for v in scene.call(&"_views"):
				if not (v as WheelView).was_tag.is_empty():
					print("MotionDemo: r5 combat hover card %d on frame %d" % [i, Engine.get_frames_drawn()])
					return
		return
	var want := CombatState.Outcome.VICTORY if kind == "win" else CombatState.Outcome.DEFEAT
	if kind == "win":
		st.enemies[0].hp = 1
	else:
		st.player.hp = 1
	for k in DEMO_END_TRIES:
		if eng.preview_end_turn().state.outcome == want:
			break
		if k % DEMO_END_NUDGES == DEMO_END_NUDGES - 1:
			# Nudges didn't do it: a turn passes (at once) and the fight is set up again.
			scene.call(&"end_turn")
			scene.call(&"skip_motion")
			st = eng.state()
			if kind == "win":
				st.enemies[0].hp = 1
			else:
				st.player.hp = 1
		else:
			scene.call(&"nudge_wheel", &"player" if kind == "win" or k % 2 == 0 else st.enemies[0].id, 1)
	scene.call(&"skip_motion")
	scene.call(&"_refresh", eng.state())
	for f in MotionDemo.START_FRAME:
		await get_tree().process_frame
	print("MotionDemo: r5 combat SEND IT (%s) on frame %d" % [kind, Engine.get_frames_drawn()])
	scene.call(&"end_turn")


## Nudges the combat end demo tries before sending anyway.
const DEMO_END_TRIES := 24
const DEMO_END_NUDGES := 4


## ANIM-R3 A6h: the fight's next-step action was pressed: on now (the hold is dropped).
func _leave_fight() -> void:
	if combat_scene == null:
		return
	_leave_generation += 1
	_show_current()


## Counts fight endings and early leaves (a hold that ran out after the player moved on
## does nothing).
var _leave_generation: int = 0


func _show_reward() -> void:
	var s := RunManager.netrun
	var offer := s.current_reward()
	var kind_word := tr(String(LOOT_WORDS.get(String(offer["kind"]), String(offer["kind"]))))
	var win := TerminalWindow.new(tr("RACK BREACHED // LOOT: pick a %s") % kind_word, Palette.CELL_ACID)
	win.name = "LootWindow"
	win.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	# Art pass W8c (ART_BIBLE §11 Loot, critique 48/61): the modal is 70% of the screen's
	# width; the offers fill its row at hover size or more.
	var modal_w := loot_modal_width()
	win.custom_minimum_size.x = modal_w
	var inner := modal_w - _window_frame_x(win)
	var box := win.body
	# ANIM-R4 C7: the tag fits the loot's row (its words shrink rather than run out of the
	# window under a long translation). Art pass W8c (§4.3 rule 5): with 140% of its width
	# to spare, so a longer translation still fits inside the modal.
	var tag := GraffitiTag.new(tr("LOOT: pick a %s") % kind_word).fit_width(inner / LOOT_TAG_SLACK)
	tag.name = "LootTag"
	box.add_child(tag)
	# Art pass W8c (critique 48/61: the LOOT drips lay on card 1's top edge): room for the
	# drips under the tag's words before the offers.
	var drip_gap := Control.new()
	drip_gap.name = "LootTagGap"
	drip_gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	drip_gap.custom_minimum_size.y = LOOT_TAG_GAP  # a card's hover lift (W4: 12 px, unscaled)
	box.add_child(drip_gap)
	var slot_option: SlotPicker = null
	# Offers as zine stickers (STYLE_GUIDE 4): cards show their RAM cost and what they do as
	# pictograms, others none. They grow with the text size as far as the row allows (H21).
	var stickers := HBoxContainer.new()
	stickers.name = "Stickers"
	stickers.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	# ANIM-4b: a Firmware chip drags onto a slot of the spinner shown beside the offer.
	var mini: SpinnerMini = null
	var room := inner  # art pass W8c: the modal's own width (was LOOT_ROW_MAX)
	# Art pass W8c (§6.4: a standalone action is sized to its label): Skip is a secondary
	# button at the foot's right, or, beside a Firmware offer, under the small spinner (the
	# slot tiles take the foot; the page keeps on screen at 1.6).
	var skip_home: BoxContainer = null
	if offer["kind"] == "firmware":
		var loot_row := HBoxContainer.new()
		loot_row.name = "LootRow"
		loot_row.add_theme_constant_override("separation", 14)
		box.add_child(loot_row)
		loot_row.add_child(stickers)
		var side := VBoxContainer.new()
		side.name = "LootSide"
		side.alignment = BoxContainer.ALIGNMENT_END
		side.add_theme_constant_override("separation", UiTheme.SP_S)
		loot_row.add_child(side)
		mini = _spinner_mini()
		mini.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		side.add_child(mini)
		skip_home = side
		room -= mini.custom_minimum_size.x + 14.0
		# Art pass W8c (§2, §6.5): the slot is picked on a row of slot tiles under the offers
		# (never a native dropdown); the small spinner beside them is where they drag.
		var slot_row := VBoxContainer.new()
		slot_row.name = "SlotRow"
		box.add_child(slot_row)
		slot_row.add_child(_label(tr("Socket into slot:")))
		slot_option = _slot_picker(s.run.operative, inner)
		slot_option.name = "SlotPick"
		slot_row.add_child(slot_option)
	else:
		box.add_child(stickers)
	var n: int = offer["options"].size()
	# ANIM-R2 E8: the gap between stickers keeps room for their rest tilt (a tilted CACHE lay
	# on JAM's cost badge at 1.0 and 1.6): the tilt's reach grows with the card.
	var tilt := sin(deg_to_rad(ZineCard.REST_TILT_MAX))
	# Art pass W8c (§11 Loot: cards at hover size): the offers fill the modal's row, never
	# smaller than a hovered card (HOVER_SCALE) nor larger than LOOT_FILL_MAX; their lettering
	# is the text size (the card grows taller for its words, W4).
	var ls := clampf((room - LOOT_GAP * (n - 1)) / maxf(1.0, n * (LOOT_CARD.x + LOOT_CARD.y * tilt)), ZineCard.HOVER_SCALE, LOOT_FILL_MAX)
	stickers.add_theme_constant_override("separation", roundi(LOOT_GAP + LOOT_CARD.y * ls * tilt))
	for i in n:
		var id := StringName(String(offer["options"][i]))
		var res := s.lookup.get_content(id)
		var cost := int(res.get("ram_cost")) if res is CardData else -1
		var sticker := ZineCard.new(TextDb.t(res, "display_name"), cost, TextDb.t(res, "description"), i).scaled(maxf(ls, Settings.text_scale))
		if res is CardData:
			sticker.with_card(res as CardData)
		sticker.fit_whole = true  # ANIM-R1 M10: the whole text on the card
		sticker.custom_minimum_size = LOOT_CARD * ls
		sticker.hotkey = ""  # rewards are picked by click or focus, not number keys
		# H24 S17: the whole text on hover and, for a pad or keyboard, on focus (FocusTip).
		var drag_kind := String({"card": "card", "firmware": "chip", "daemon": "daemon"}.get(String(offer["kind"]), ""))
		_input_tip(sticker, loot_tip(res), drag_kind)
		FocusTip.attach(sticker)
		var index: int = i
		sticker.pressed.connect(func() -> void: choose_reward(index, slot_option.selected() if slot_option != null else -1))
		stickers.add_child(sticker)
	# ANIM-R1 M11: room under the stickers for their tilt and lift (at 1.6 the CACHE card's
	# corner lay on the Skip bar).
	var gap := Control.new()
	gap.name = "SkipGap"
	gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	gap.custom_minimum_size.y = LOOT_SKIP_GAP * ls
	var skip := _button(tr("Skip"), skip_reward)
	skip.name = "Skip"
	skip.theme_type_variation = UiTheme.SECONDARY
	skip.tooltip_text = tr("Take nothing from this payout.")
	IconMark.attach(skip, StatIcon.SKIP)
	if skip_home != null:
		skip.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		skip_home.add_child(skip)
		box.move_child(box.get_node(^"SlotRow"), box.get_child_count() - 1)
	else:
		box.add_child(gap)
		skip.size_flags_horizontal = Control.SIZE_SHRINK_END
		box.add_child(skip)
	var wrap := CenterContainer.new()
	wrap.add_child(win)
	_set_panel(wrap, false)
	_register_loot_drops(stickers, mini, slot_option)
	if entering:
		_fan_loot.call_deferred(stickers)


## Art pass W8c (ART_BIBLE §11 Loot): the modal's share of the screen's width, the room the
## graffiti title keeps for a longer translation (§4.3 rule 5: 140%), the gap under its
## drips (px at 1.0) and the most the offers grow by (their row filled).
const LOOT_MODAL_SHARE := 0.7
const LOOT_TAG_SLACK := 1.4
const LOOT_TAG_GAP := 12.0
const LOOT_FILL_MAX := 1.4
## The stamp word the picked offer takes before it flies to the deck (§6.6: ≤ 3 words; T2).
const LOOT_PICK_STAMP := "TAKEN" # TR


## Art pass W8c: the loot modal's width (px): LOOT_MODAL_SHARE of the page.
func loot_modal_width() -> float:
	var w := size.x if size.x > 0.0 else get_viewport_rect().size.x
	return roundf(w * LOOT_MODAL_SHARE)


## The horizontal room a terminal window's frame takes round its body (px; read from the
## screen's theme: the window is not in the tree yet).
func _window_frame_x(_win: TerminalWindow) -> float:
	var box := get_theme_stylebox(&"panel", &"TerminalPanel")
	return box.get_minimum_size().x if box != null else float(UiTheme.PANEL_PAD_H * 2)


## Art pass W8c (§6.5): a slot picker for operative `op`'s spinner, as many columns as
## `width` px holds; each tile tells the slot's whole name (slot_name) as its tip.
func _slot_picker(op: OperativeState, width: float) -> SlotPicker:
	var tiles := SlotPicker.tiles_for(op)
	for k in tiles.size():
		tiles[k]["tip"] = slot_name(op, k)
	var pick := SlotPicker.new(tiles)
	pick.fit_columns(width)
	return pick


## The loot fans in from the foot of its row, one after another (ANIM-6, `loot_fan`).
func _fan_loot(row: Control) -> void:
	if not is_instance_valid(row) or not row.is_inside_tree():
		return
	var r := row.get_global_rect()
	var n := row.get_child_count()
	for i in n:
		var card := row.get_child(i) as ZineCard
		if card == null:
			continue
		# ANIM-R1 M11: from the middle of the row's own foot (the deck pile), inside the row:
		# from under it the cards crossed the Skip bar at 1.6 on their way up.
		var from := Vector2(r.get_center().x, r.end.y - card.size.y * 0.5)
		var fan := Motion.amplitude(&"loot_fan") * (float(i) - (n - 1) * 0.5)
		card.fan_in(from, fan, Motion.delay_of(&"loot_fan") * i)


## Terminal event (GDD 4.2): zine paper for street and corporate voices; DISPATCH stays
## clean system text on a dark strip (STYLE_GUIDE 3), never zined.
##
## Art pass W8c (ART_BIBLE §11 Events, §4.1, §4.2, §3.1, critique 59/60, gifs/24):
## - The story sits on PAPER sized to its words (the paper is as tall as its text and as
##   wide as a ≤ 70-character line of the Plex body face, `BodyText`); DISPATCH keeps Share
##   Tech Mono on its dark strip, wrapped at ≤ 64 columns.
## - The speaker's plate appears once (the title is the paper's heading; the plate never
##   repeats the speaker or the title).
## - The subtitle band never repeats the story on the page (the story isn't said again).
## - Each choice's numbers show once, as glyph + number chips under its words (the "(+25
##   Cycles, +2 Heat)" words are gone); good and bad carry ▲ / ▼ as well as colour.
## - The chosen choice stamps CHOSEN as the next page comes in, with no picture of the
##   note (a white bar stayed over the route).
## - W7 hookup: the city is not a map here; the story's paper is a calm zone.
func _show_event() -> void:
	var s := RunManager.netrun
	var ev := s.current_event()
	var box := VBoxContainer.new()
	var body := VBoxContainer.new()
	body.add_theme_constant_override("separation", UiTheme.SP_XS)
	var dispatch := ev.speaker == RC.Voice.DISPATCH
	var ts := Settings.text_scale
	var page_w := (size.x if size.x > 0.0 else get_viewport_rect().size.x) - UiTheme.SAFE_MARGIN * 2.0
	var text_w := event_text_width(dispatch)
	# Side by side when the story and the choices both fit; else the choices go under it.
	var stacked := text_w + EVENT_PAPER_PAD * ts + EVENT_OPTIONS_MIN * ts + EVENT_SPLIT_GAP > page_w
	text_w = minf(text_w, page_w - EVENT_PAPER_PAD * ts)
	var holder: Control
	var who: String = Dialogue.speaker_name(ev.speaker, ev.corporation_id if ev.corporation_id != &"" else RunManager.campaign.corporation_id)
	var title := event_title(TextDb.t(ev, "title"), who)
	if dispatch:
		var strip := PanelContainer.new()
		var style := UiTheme.box(Palette.TERMINAL_BG, Palette.CRT_AMBER, 1, UiTheme.SP_M, UiTheme.PANEL_PAD_V)
		style.border_width_left = UiTheme.SP_XS
		style.shadow_color = Palette.SHADOW
		style.shadow_size = UiTheme.SP_S
		if Settings.high_contrast:
			style.bg_color = HighContrast.BG
		strip.add_theme_stylebox_override("panel", style)
		strip.material = UiTheme.crt_material()
		strip.add_child(body)
		holder = strip
	else:
		var panel := ZinePanel.new(title.to_upper(), -1.0).scale_title(ts)
		panel.content.add_child(body)
		holder = panel
		# The paper is as tall as its words (a ZinePanel has no size of its own; overlaps
		# ANIM-R5 B1's ZinePanel.fit_to_content: keep one on merge).
		body.minimum_size_changed.connect(_fit_paper.bind(panel))
		_fit_paper.call_deferred(panel)
	holder.name = "EventPanel"
	# H23 S10: room above the paper for its tape and title, clear of the subtitle band.
	var gap := Control.new()
	gap.name = "EventTopGap"
	gap.custom_minimum_size.y = EVENT_TOP_GAP * ts
	gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(gap)
	var split: BoxContainer = VBoxContainer.new() if stacked else HBoxContainer.new()
	split.name = "EventSplit"
	split.add_theme_constant_override("separation", roundi(EVENT_SPLIT_GAP))
	box.add_child(split)
	split.add_child(holder)
	holder.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	holder.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	var options := VBoxContainer.new()
	options.name = "EventChoices"
	options.add_theme_constant_override("separation", 14)
	options.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	split.add_child(options)
	# H24 S4: the speaker's name comes translated (once). Art pass W8c: the plate says it
	# once; DISPATCH's strip heads its title on a line of its own (the paper's title is its
	# heading).
	var speaker := _label(who)
	speaker.name = "SpeakerPlate"
	speaker.add_theme_color_override("font_color", Palette.CRT_AMBER if dispatch else Palette.CELL_PINK)
	body.add_child(speaker)
	if dispatch and title != "":
		var head := _label(title)
		head.name = "EventTitle"
		head.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.LABEL))
		head.add_theme_color_override("font_color", Palette.CRT_AMBER)
		body.add_child(head)
	var text := RichTextLabel.new()
	text.name = "EventText"
	text.fit_content = true
	# ANIM-R5 B1 (the same line): the words are laid out whole while they type in.
	text.visible_characters_behavior = TextServer.VC_CHARS_AFTER_SHAPING
	if not dispatch:
		text.theme_type_variation = UiTheme.BODY_TEXT  # §4.1: Plex for a text block
	text.custom_minimum_size = Vector2(text_w, 0)
	text.text = event_story(TextDb.t(ev, "text"), who)
	text.add_theme_color_override("default_color", Palette.CRT_AMBER if dispatch else Palette.INK)
	body.add_child(text)
	# Art pass W8c (§11 Events, critique 59/60): the story is on the page, so the subtitle
	# band does not say it again (it repeated the page at ~7 px). The band keeps the run's
	# other lines.
	_spoken_events[ev.id] = true
	for i in ev.choices.size():
		var c := ev.choices[i]
		var b := Button.new()
		# H21 #13: the outcome as icons with numbers under the words (Heat as it applies);
		# H22 #12: the amounts it will really apply (a heal at full HP, Heat at 0).
		var outcome := OutcomeRow.of_choice(s, c)
		var costs := OutcomeRow.words(outcome)
		# Art pass W8c: the numbers once, as the chips under the words (not "(+25 Cycles)").
		b.text = _choice_text(TextDb.t(c, "label"), "")
		var err := s.choice_error(c)
		b.disabled = err != ""
		var tip := err if err != "" else ((tr("Costs: %s.") % costs) if costs != "" else "")
		tip += ("\n" if tip != "" else "") + (OutcomeRow.describe(outcome) if not outcome.is_empty() else tr("No change to your numbers."))
		b.tooltip_text = UiTip.fold(tip)
		var index := i
		b.name = "Choice%d" % (i + 1)
		b.pressed.connect(func() -> void: _press_choice(index))
		b.theme_type_variation = &"NoteButton"
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		options.add_child(b)
		# H23 S9: no numbers for a change that is none; H24 S9: a choice that changes nothing
		# says so with the neutral "no change" mark (it showed nothing at all). Art pass W8c:
		# ▲ / ▼ beside each amount (EventOutcomeRow).
		var numbers := OutcomeRow.shown(outcome)
		var row := EventOutcomeRow.new(numbers if not numbers.is_empty() else OutcomeRow.no_change())
		OutcomeRow.attach(b, row)
		# ANIM-6: the outcome's icons pop when the choice is hovered or focused.
		b.mouse_entered.connect(func() -> void: Motion.pop(row, &"event_outcome_pop"))
		b.focus_entered.connect(func() -> void: Motion.pop(row, &"event_outcome_pop"))
	options.add_child(GraffitiScrawl.new(tr("PLAY IT\nSAFE??"), -6.0, 24))
	# H24 S9: the choices keep clear of the screen's right edge (their border was cut).
	options.custom_minimum_size.x = 0.0
	var right_gap := Control.new()
	right_gap.name = "EventRightGap"
	right_gap.custom_minimum_size.x = EVENT_RIGHT_GAP * ts
	right_gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if stacked:
		# Art pass W8c: under the story, the choices keep the same gap from the right edge.
		var row := HBoxContainer.new()
		row.name = "EventChoiceRow"
		split.remove_child(options)
		split.add_child(row)
		row.add_child(options)
		row.add_child(right_gap)
	else:
		split.add_child(right_gap)
	# Art pass W8c (§5.1): the page keeps the screen's safe margin on the left (the paper sat
	# on the screen's edge).
	var page := MarginContainer.new()
	page.name = "EventPage"
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.add_theme_constant_override("margin_left", UiTheme.SAFE_MARGIN)
	page.add_child(box)
	page.set_meta(PAGE_LOOK_META, PageTransition.Look.PAPER if not dispatch else PageTransition.Look.GLASS)
	_set_panel(page, false)
	var calm: Array[Control] = [holder]
	_city_page(false, calm)
	_register_event_drops(ev, options)
	# ANIM-R4 C7: the story types within `event_type`'s cap (0.8 s), not a char at a time
	# for 8 s under an empty panel.
	if entering and Typing.type_in(text, &"event_type") > 0.0:
		_hold_choices(options, text)


## Art pass W8c (ART_BIBLE §4.2: ≤ 70 characters a line of body text; §4.1: DISPATCH ≤ 64
## columns of mono): the event story's width at the player's text size (px).
static func event_text_width(dispatch: bool) -> float:
	var f := Palette.mono() if dispatch else Palette.body()
	var cols := EVENT_DISPATCH_COLUMNS if dispatch else EVENT_BODY_COLUMNS
	return ceilf(f.get_string_size(UiTip.COLUMN_SAMPLE.repeat(cols), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.BODY)).x)


## Art pass W8c: an event's title without a leading speaker ("DISPATCH: Early Reply" under
## the DISPATCH plate reads "Early Reply"): the plate says who, once.
static func event_title(title: String, who: String) -> String:
	var t := title.strip_edges()
	for sep: String in [":", " -", " —"]:
		var lead: String = who + sep
		if who != "" and t.to_lower().begins_with(lead.to_lower()):
			return t.substr(lead.length()).strip_edges()
	return "" if t.to_lower() == who.to_lower() else t


## Art pass W8c: an event's story without a leading "SPEAKER: " (the plate above says who,
## once; "DISPATCH: Good work at the Rack." reads "Good work at the Rack.").
static func event_story(text: String, who: String) -> String:
	var lead := who + ":"
	if who != "" and text.to_lower().begins_with(lead.to_lower()):
		return text.substr(lead.length()).strip_edges()
	return text


## The paper's height: its words' (a ZinePanel is a plain Control round its content).
func _fit_paper(panel: ZinePanel) -> void:
	if not is_instance_valid(panel):
		return
	panel.custom_minimum_size = panel.content.get_combined_minimum_size()


## Art pass W8c: the story's columns (§4.2, §4.1), the paper's padding round its words, the
## least width the choices keep beside it and the gap between (px at text scale 1.0).
const EVENT_BODY_COLUMNS := 70
const EVENT_DISPATCH_COLUMNS := 64
const EVENT_PAPER_PAD := 32.0
const EVENT_OPTIONS_MIN := 300.0
const EVENT_SPLIT_GAP := 22.0


## ANIM-R1 M9 / ANIM-R2 E1-E2: while the event's story types in, its choices wait. They stay
## enabled, focusable and readable (normal paper, outcome icons shown) with a "typing" mark
## (`EventHeldMark`: three dots in the corner, their words a little dimmer), so the page's
## focus lands on the first choice at once and a pad can move between them; a press first
## shows the words whole (the story and its subtitle together: Typing.finish_all, one press)
## and only a press on a released choice chooses. The choices go live when the words are
## whole; the first one takes focus then if nothing on the page has it (a pad-only player
## was stuck with every choice disabled and no focus).
func _hold_choices(options: Control, text: Control) -> void:
	var held: Array[WeakRef] = []
	for b in options.get_children():
		if b is Button and not (b as Button).disabled:
			var btn := b as Button
			btn.set_meta(HELD_META, true)
			btn.add_theme_color_override(&"font_color", Color(Palette.INK, HELD_INK_ALPHA))
			var mark := EventHeldMark.new()
			mark.name = "EventHeldMark"
			btn.add_child(mark)
			held.append(weakref(btn))
	if held.is_empty():
		return
	_held_choices = held
	_held_text = weakref(text)
	if not get_tree().process_frame.is_connected(_poll_held_choices):
		get_tree().process_frame.connect(_poll_held_choices)


## The meta a waiting choice carries, and how dim its words are meanwhile.
const HELD_META := &"event_choice_held"
const HELD_INK_ALPHA := 0.7

## The choices waiting for the event's words, and the words (weak: the page may go first).
var _held_choices: Array[WeakRef] = []
var _held_text: WeakRef = null


## A choice's press: a waiting choice shows the words whole instead (never chooses).
func _press_choice(index: int) -> void:
	var b := _panel.find_child("Choice%d" % (index + 1), true, false) as Button if _panel != null else null
	if b != null and b.has_meta(HELD_META):
		Typing.finish_all(get_tree())
		_poll_held_choices()
		return
	choose_event(index)


func _poll_held_choices() -> void:
	var text := _held_text.get_ref() as Control if _held_text != null else null
	if text != null and Typing.typing(text):
		return
	var first: Button = null
	for w in _held_choices:
		var b := w.get_ref() as Button
		if b != null:
			b.remove_meta(HELD_META)
			b.remove_theme_color_override(&"font_color")
			var mark := b.get_node_or_null(^"EventHeldMark")
			if mark != null:
				mark.queue_free()
			if first == null:
				first = b
	_held_choices.clear()
	_held_text = null
	if get_tree().process_frame.is_connected(_poll_held_choices):
		get_tree().process_frame.disconnect(_poll_held_choices)
	# E1: the pad has something to press once the choices act.
	if first != null and first.is_inside_tree():
		UiFocus.focus_first(first.get_parent(), true)


## True while the event's choices wait for its words (tests).
func choices_held() -> bool:
	var text := _panel.find_child("EventPanel", true, false) if _panel != null else null
	if text == null:
		return false
	for n in text.find_children("*", "RichTextLabel", true, false):
		if Typing.typing(n as Control):
			return true
	return false


## A spinner slot by what is in it, never by ids (H21 #12: "crit_12" in the socket list):
## "Slot 2: ATK 10 + Barbed Wire".
static func slot_name(op: OperativeState, k: int) -> String:
	var lookup := RunManager.lookup()
	var sd := lookup.get_content(op.slot_slice_ids[k]) as SliceData
	var slice := "?"
	if sd != null:
		slice = TranslationServer.translate(String(Palette.SLICE_NAMES.get(sd.slice_type, "?"))) + ((" %d" % sd.base_output) if sd.base_output > 0 else "")
	var fw_id: StringName = op.slot_firmware_ids[k] if k < op.slot_firmware_ids.size() else &""
	var fw: Resource = lookup.get_content(fw_id) if fw_id != &"" else null
	return TranslationServer.translate("Slot %d: %s%s") % [k + 1, slice, (" + %s" % TextDb.t(fw, "display_name")) if fw != null else ""]


## A Terminal choice's label with its costs from the data, replacing the hand-written
## "(...)" summary so a hidden or unscaled cost can't slip through.
static func _choice_text(label: String, costs: String) -> String:
	var base := label
	var open := base.rfind(" (")
	if open > 0 and base.ends_with(")"):
		base = base.substr(0, open)
	return base if costs == "" else "%s (%s)" % [base, costs]


## Modem (GDD 11.2) in four quadrants over the storefront: MICROCHIPS (Firmware, top
## left), CARDS (as their own stickers, top right), SLICES + DAEMONS (bottom left, split)
## and REMOVE A CARD (bottom right, opens the deck viewer). Overwriting a slice opens the
## spinner viewer to pick the slot. "Leave the Modem" is a dripping tag in the corner.
func _show_shop() -> void:
	var s := RunManager.netrun
	var shop := s.run.shop
	var op := s.run.operative
	# Art pass W8c (ART_BIBLE §5.3, §11 Modem): the page is laid out by containers, not
	# fixed positions: the baked sign in its column, the four windows in a grid of two
	# columns (one at big text sizes, where the page scrolls inside its window with a hint),
	# LEAVE THE MODEM at the foot. Every window keeps its colour-coding.
	var root := HBoxContainer.new()
	root.name = "ModemRoot"
	root.add_theme_constant_override("separation", UiTheme.GUTTER)
	var sign := ModemSign.new()
	sign.name = "ModemSign"
	sign.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	root.add_child(sign)
	var main := VBoxContainer.new()
	main.name = "ModemMain"
	main.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main.add_theme_constant_override("separation", roundi(QUAD_GAP))
	root.add_child(main)
	var ts := Settings.text_scale
	var grid := GridContainer.new()
	grid.name = "ModemGrid"
	grid.columns = modem_columns(ts)
	grid.add_theme_constant_override("h_separation", roundi(QUAD_GAP))
	grid.add_theme_constant_override("v_separation", roundi(QUAD_GAP))
	main.add_child(grid)
	var q_size := modem_quad(ts)
	# Top left: microchips (Firmware). Art pass W8c (§2, §6.5): the slot a bought chip goes
	# into is picked on slot tiles (SlotPicker), never a native dropdown.
	var fw_slot: SlotPicker = null
	if not shop.get("firmware", []).is_empty():
		fw_slot = _slot_picker(op, q_size.x - QUAD_FRAME.x)
		fw_slot.name = "SocketPick"
	var chips_win := TerminalWindow.new(tr("MICROCHIPS"))
	chips_win.custom_minimum_size = q_size
	grid.add_child(chips_win)
	var chips := HBoxContainer.new()
	chips.name = "Chips"
	chips.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	chips.add_theme_constant_override("separation", 10)
	chips_win.body.add_child(chips)
	# Top right: cards as their stickers ("Stickers" holds them in stock order).
	var cards_win := TerminalWindow.new(tr("CARDS"), Palette.CELL_PINK)
	cards_win.custom_minimum_size = q_size
	grid.add_child(cards_win)
	var stickers := HBoxContainer.new()
	stickers.name = "Stickers"
	stickers.add_theme_constant_override("separation", 12)
	# Art pass W8c: room above the cards for their hover lift (a focused card lay on the
	# CARDS title).
	var lift_room := Control.new()
	lift_room.name = "CardsLiftRoom"
	lift_room.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cards_win.body.add_child(lift_room)
	cards_win.body.add_child(stickers)
	# Bottom left: slices (overwrite) and daemons side by side.
	# A 2-column grid (not an HBox) so pad focus walks every tile in both windows.
	var lower_left := GridContainer.new()
	lower_left.columns = 2
	lower_left.add_theme_constant_override("h_separation", 12)
	lower_left.custom_minimum_size = q_size
	grid.add_child(lower_left)
	var slices_win := TerminalWindow.new(tr("SLICES"), Palette.CRT_AMBER)
	slices_win.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lower_left.add_child(slices_win)
	var daemons_win := TerminalWindow.new(tr("DAEMONS"), Palette.NEON_VIOLET)
	lower_left.add_child(daemons_win)
	var daemon_row := HBoxContainer.new()
	daemon_row.name = "Daemons"
	daemons_win.body.add_child(daemon_row)
	var n := 0
	# ANIM-R1 M11: what the Modem offered when the player came in; a bought item stays as a
	# SOLD stub in its place (the rest keep their spots and colours).
	var seen := _shop_seen(s)
	# Cards grow with the text size as far as their quadrant holds them (H21 #15).
	var card_count: int = (seen["cards"] as Array).size()
	var card_fit := minf((q_size.x - QUAD_FRAME.x - QUAD_GAP * maxi(0, card_count - 1)) / maxf(1.0, card_count * ZineCard.STICKER_SIZE.x),
		# Art pass W8c: in one column (big text; the page scrolls) the cards may grow with the text.
		(q_size.y * (ts if grid.columns == 1 else 1.0) - QUAD_FRAME.y) / ZineCard.STICKER_SIZE.y)
	var cs := clampf(minf(ts, card_fit), 1.0, Settings.TEXT_SCALE_MAX)
	# Art pass W8c: the lift room is a card's hover lift, the half of its hover growth and the
	# focus brackets' offset.
	lift_room.custom_minimum_size.y = roundf(Motion.amplitude(&"card_hover") + (ZineCard.HOVER_SCALE - 1.0) * 0.5 * ZineCard.STICKER_SIZE.y * cs
		+ UiTheme.SP_XS * ts)
	for kind in ["cards", "firmware", "daemons"]:
		var prices: Array = shop.get(kind.trim_suffix("s") + "_prices", [])
		for slot: Array in shop_slots(seen[kind], shop.get(kind, [])):
			var i: int = slot[1]
			var id := StringName(String(slot[0]))
			var res := s.lookup.get_content(id)
			if i < 0:
				var stub := _sold_stub(TextDb.t(res, "display_name"), (res as CardData).ram_cost if res is CardData else -1, n, kind, cs, ts)
				match kind:
					"cards":
						stickers.add_child(stub)
					"firmware":
						chips.add_child(stub)
					_:
						daemon_row.add_child(stub)
				n += 1
				continue
			# H21 #12: the circle shows a card's real RAM cost; the price hangs on a tag with
			# the coin.
			var ram := (res as CardData).ram_cost if res is CardData else -1
			# H24 S3: the effect text alone (a "firmware: " prefix was an untranslated word).
			var sticker := ZineCard.new(TextDb.t(res, "display_name"), ram, shop_text(res), n)
			sticker.fit_whole = true  # ANIM-R1 M10: the whole text on the tile or card
			sticker.hotkey = ""
			sticker.with_price(int(prices[i]))
			if kind == "cards":
				sticker.scaled(cs).with_card(res as CardData)
			elif kind == "firmware":
				sticker.as_tile(ZineCard.Look.CHIP, Palette.NET_CYAN).tile_text(chip_text_scale(ts))
			elif kind == "daemons":
				sticker.as_tile(ZineCard.Look.CHIP, Palette.NEON_VIOLET).tile_text(chip_text_scale(ts))
			_input_tip(sticker, tr("%s\n%s\nBuy: %d Cycles (you have %d).") % [TextDb.t(res, "display_name"), shop_text(res), int(prices[i]), s.run.cycles],
				String({"cards": "card", "firmware": "chip", "daemons": "daemon"}[kind]))
			sticker.disabled = int(prices[i]) > s.run.cycles
			# H23 S8: a clear buy button on every item, and the whole text on focus.
			sticker.with_buy(TextDb.mark("BUY"))
			sticker.buy_button.have = s.run.cycles  # art pass W8c: NEED n · HAVE m when out of reach
			if kind != "cards":
				# ANIM-R2 E6: the tile grows until its whole text reads (at 1.6 a third of the
				# chips showed 1 of 2-3 lines at the 8 px floor). Art pass W8c: at `body`.
				var most := chip_tile_room(kind, (seen[kind] as Array).size(), ts, q_size)
				if kind == "firmware":
					# Art pass W8c: a microchip takes its share of the window's width first (its
					# body-size words take fewer lines), then grows taller as it must.
					sticker.custom_minimum_size = Vector2(most.x, CHIP_TILE.y * ts)
				fit_chip_tile(sticker, most)
			FocusTip.attach(sticker)
			var index: int = i
			var k: String = kind
			var price_i := int(prices[i])
			# ANIM-R2 E9: pressing an item out of reach says why on the money itself.
			sticker.gui_input.connect(func(ev: InputEvent) -> void:
				if sticker.disabled and (ev.is_action_pressed(&"ui_accept") or (ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed and (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT)):
					price_refused(price_i))
			sticker.set_meta(STOCK_META, i)
			sticker.pressed.connect(func() -> void: buy(k, index, fw_slot.selected() if k == "firmware" else -1))
			match kind:
				"cards":
					stickers.add_child(sticker)
				"firmware":
					chips.add_child(sticker)
				_:
					daemon_row.add_child(sticker)
			n += 1
	if not shop.get("firmware", []).is_empty():
		# Art pass W8c: the slot tiles under a caption saying what they are for (overlaps
		# ANIM-R5 B11's "Chips go into:" socket row; keep one caption on merge).
		var socket_row := VBoxContainer.new()
		socket_row.name = "SocketRow"
		var socket_word := _label(tr("Socket into slot:"))
		socket_word.name = "SocketWord"
		socket_word.tooltip_text = UiTip.fold(tr("The spinner slot a bought Firmware chip goes into."))
		socket_word.mouse_filter = Control.MOUSE_FILTER_PASS
		socket_row.add_child(socket_word)
		socket_row.add_child(fw_slot)
		chips_win.body.add_child(socket_row)
	if daemon_row.get_child_count() == 0:
		daemons_win.body.add_child(_label(tr("sold out")))
	var slice_row := HBoxContainer.new()
	slice_row.name = "Slices"
	slice_row.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	slice_row.add_theme_constant_override("separation", 8)
	slices_win.body.add_child(slice_row)
	var stock: Array = shop.get("slices", [])
	# A slice's price depends on the slot it overwrites: the tile shows the lowest ("N+"
	# when some slot costs more).
	var low := -1
	var high := -1
	for k in op.slot_slice_ids.size():
		var p := s.slice_overwrite_price(k)
		low = p if low < 0 else mini(low, p)
		high = maxi(high, p)
	for slot: Array in shop_slots(seen["slices"], stock):
		var i: int = slot[1]
		var sd := s.lookup.get_content(StringName(String(slot[0]))) as SliceData
		if sd == null:
			continue
		var slice_word := tr(String(Palette.SLICE_NAMES.get(sd.slice_type, "?")))
		if i < 0:
			var stub := _sold_stub("%s %d" % [slice_word, sd.base_output] if sd.base_output > 0 else slice_word, -1, (seen["slices"] as Array).size(), "slices", 1.0, ts)
			stub.custom_minimum_size = slice_tile_size((seen["slices"] as Array).size(), ts, q_size.x)
			stub.slice_type = sd.slice_type
			stub.slice_output = sd.base_output
			stub.accent = Palette.slice_color(sd.slice_type)
			slice_row.add_child(stub)
			continue
		var tile := ZineCard.new("%s %d" % [slice_word, sd.base_output] if sd.base_output > 0 else slice_word, -1, Codex.describe(sd), i)
		tile.set_meta(STOCK_META, i)
		tile.as_tile(ZineCard.Look.SLICE_TILE, Palette.slice_color(sd.slice_type)).tile_text(ts)
		tile.slice_type = sd.slice_type
		tile.slice_output = sd.base_output
		# H24 S10: the tile widens with the text size as far as the SLICES window holds the
		# row (its buy sticker "BUY 100-150" shrank to fit a fixed 96 px at 1.6).
		tile.custom_minimum_size = slice_tile_size((seen["slices"] as Array).size(), ts, q_size.x)
		tile.hotkey = ""
		if low >= 0:
			# ANIM-R2 E6: one price on the tile, what most slots cost ("BUY 100-150" wrapped
			# onto three lines at 1.6); the UPGRADE viewer shows the exact price of the slot
			# picked before anything is paid, and the tip names the pricier slot.
			tile.with_price(low)
		# H23 S8: the real prices (the slot you overwrite sets it), said in words.
		_input_tip(tile, tr("Overwrite a slot of your spinner with this slice. Price: %s Cycles%s (you have %d).\n") % [tile.price_words(),
			(tr(": %d for most slots, %d for a pricier one such as the Miss slot; you pick the slot next") % [low, high]) if high > low else "", s.run.cycles] + Codex.describe(sd),
			"slice")
		tile.with_buy(TextDb.mark("BUY"))
		tile.buy_button.have = s.run.cycles  # art pass W8c
		FocusTip.attach(tile)
		var si := i
		tile.pressed.connect(func() -> void: open_overwrite(si))
		slice_row.add_child(tile)
	# Bottom right: remove a card, an icon action that opens the deck viewer.
	var remove_win := TerminalWindow.new(tr("REMOVE A CARD"), Palette.CELL_ACID)
	remove_win.custom_minimum_size = q_size
	grid.add_child(remove_win)
	var remove_row := HBoxContainer.new()
	remove_row.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	remove_row.add_theme_constant_override("separation", 16)
	remove_win.body.add_child(remove_row)
	var shred := ZineCard.new(tr("SHRED A CARD"), -1, tr("Pick a card from your deck to remove."), 0)
	shred.as_tile(ZineCard.Look.CARD_TILE, Palette.CELL_ACID).tile_text(ts)
	shred.custom_minimum_size.y *= tile_growth(ts)
	shred.with_price(s.card_removal_price())
	shred.name = "RemoveCard"
	shred.hotkey = ""
	shred.disabled = s.run.cycles < s.card_removal_price() or op.deck.is_empty()
	shred.icon_kind = "shred"
	shred.tooltip_text = UiTip.fold(tr("Remove a card from your deck: %d Cycles (you have %d).") % [s.card_removal_price(), s.run.cycles])
	shred.pressed.connect(open_remove)
	shred.with_buy(TextDb.mark("SHRED"))
	shred.buy_button.have = s.run.cycles if not op.deck.is_empty() else -1  # art pass W8c
	FocusTip.attach(shred)
	remove_row.add_child(shred)
	# Art pass W8c (ART_BIBLE §11 Modem, critique 52): one Cycles readout, the top bar's
	# CYCLES tag (the wallet here said it twice). Refusals flash that tag (price_refused).
	# ANIM-4b: the spinner in small beside the wallet: microchips and slice upgrades drag onto
	# its slots (the socket list and the UPGRADE viewer stay).
	var mini := _spinner_mini()
	mini.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	remove_row.add_child(mini)
	# Art pass W8c: LEAVE THE MODEM taped at the REMOVE window's free right (it sat at a
	# fixed spot and overlapped the window as the windows grew with the text).
	var foot := HBoxContainer.new()
	foot.name = "ModemFoot"
	foot.alignment = BoxContainer.ALIGNMENT_END
	foot.size_flags_vertical = Control.SIZE_SHRINK_END
	foot.add_theme_constant_override("separation", UiTheme.SP_XS)
	remove_win.body.add_child(foot)
	var leave := DripButton.new(TextDb.mark("LEAVE THE MODEM"), "", DripButton.DRIP_PINK, 32, DripButton.LEAVE_MODEM_DRIPS)
	leave.name = "LeaveModem"
	leave.pressed.connect(leave_shop)
	leave.tooltip_text = tr("Leave the Modem and go back to the route.")
	var leave_icon := IconMark.standalone(StatIcon.EXIT, LEAVE_ICON, DripButton.DRIP_PINK)
	leave_icon.name = "LeaveIcon"
	leave_icon.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	leave_icon.tooltip_text = leave.tooltip_text
	leave_icon.mouse_filter = Control.MOUSE_FILTER_PASS
	foot.add_child(leave_icon)
	foot.add_child(leave)
	# ANIM-R3 A7: the first focus is the first item (one the Cycles reach, else the first),
	# never the socket list: the pad prompt says "A Buy".
	var first_item: ZineCard = null
	for row in [chips, stickers, slice_row, daemon_row]:
		for c in (row as Node).get_children():
			var zc := c as ZineCard
			if zc == null or zc.sold_stub:
				continue
			if first_item == null or (first_item.disabled and not zc.disabled):
				first_item = zc
			if not zc.disabled:
				break
		if first_item != null and not first_item.disabled:
			break
	if first_item != null:
		first_item.focus_mode = Control.FOCUS_ALL
		root.set_meta(FIRST_FOCUS_META, first_item)
	_set_panel(root, false)
	_register_shop_drops(mini, fw_slot)
	if entering:
		sign.warm_up()


## ANIM-R1 M11: the node meta naming a Modem item's stock index (SOLD stubs have none).
const STOCK_META := &"stock_index"
## What the Modem offered when the player came in (view memory, per visit): "key" (the
## run and node), then each kind's stock.
var _shop_memory: Dictionary = {}


## The Modem's stock as first seen on this visit, kind -> ids (taken again when the stock
## is not what was seen less some purchases: a new visit, a restock).
func _shop_seen(s: NetrunSession) -> Dictionary:
	var key := "%s|%s|%s" % [s.run.site_id, s.run.current_node_id, s.run.visited.size()]
	var shop := s.run.shop
	var fresh: bool = _shop_memory.get("key", "") != key
	if not fresh:
		for kind in ["cards", "firmware", "daemons", "slices"]:
			var cur: Array = shop.get(kind, [])
			var slots := shop_slots(_shop_memory.get(kind, []), cur)
			var live := 0
			for slot: Array in slots:
				if int(slot[1]) >= 0:
					live += 1
			if live != cur.size():
				fresh = true
	if fresh:
		_shop_memory = {"key": key}
		for kind in ["cards", "firmware", "daemons", "slices"]:
			_shop_memory[kind] = (shop.get(kind, []) as Array).duplicate()
	return _shop_memory


## ANIM-R1 M11: the Modem's places for one kind: [id, stock index] for each item first
## offered (`seen`), in order; the index is -1 for one bought since (a SOLD stub). Items are
## matched in order, so a repeated id keeps its place.
static func shop_slots(seen: Array, current: Array) -> Array[Array]:
	var out: Array[Array] = []
	var j := 0
	for i in seen.size():
		if j < current.size() and String(current[j]) == String(seen[i]):
			out.append([seen[i], j])
			j += 1
		else:
			out.append([seen[i], -1])
	return out


## A bought Modem item's place: its tile, dimmed, stamped SOLD; not a button any more.
func _sold_stub(title: String, ram: int, index: int, kind: String, cs: float, ts: float) -> ZineCard:
	var stub := ZineCard.new(title, ram, "", index)
	match kind:
		"cards":
			stub.scaled(cs)
		"firmware":
			stub.as_tile(ZineCard.Look.CHIP, Palette.NET_CYAN).tile_text(ts)
		"daemons":
			stub.as_tile(ZineCard.Look.CHIP, Palette.NEON_VIOLET).tile_text(ts)
		"slices":
			stub.as_tile(ZineCard.Look.SLICE_TILE, Palette.CRT_AMBER).tile_text(ts)
	stub.name = "Sold_%s_%d" % [kind, index]
	stub.hotkey = ""
	stub.sold_stub = true
	stub.disabled = true
	stub.focus_mode = Control.FOCUS_NONE
	stub.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stub.tooltip_text = ""
	return stub


## What a shop item does in words (H23 S8: microchips showed no description): the
## content's translated description, else the Codex's.
static func shop_text(res: Resource) -> String:
	var d := TextDb.t(res, "description") if res != null else ""
	return d if d != "" else (Codex.describe(res) if res != null else "")


## A loot offer's whole text (H24 S17: its name and what it does), shown on hover and, for
## a pad or keyboard, on focus.
static func loot_tip(res: Resource) -> String:
	if res == null:
		return ""
	var d := TextDb.t(res, "description") if "description" in res else ""
	return "%s\n%s" % [TextDb.t(res, "display_name"), d if d != "" else Codex.describe(res)]


## A slice tile's size in the Modem's SLICES window for `count` tiles at text scale `ts`
## (H24 S10): SLICE_TILE grown with the text as far as the window's width holds the row.
static func slice_tile_size(count: int, ts: float, quad_w: float = MODEM_QUAD.x) -> Vector2:
	var room := quad_w * 0.5 - QUAD_FRAME.x - 8.0 * maxi(0, count - 1)
	var k := clampf(minf(ts, room / maxf(1.0, count * SLICE_TILE.x)), 1.0, Settings.TEXT_SCALE_MAX)
	return Vector2(SLICE_TILE.x * k, SLICE_TILE.y * tile_growth(ts))


## How much taller a Modem tile in the lower row grows at text scale `ts` (H24 S10: at 1.6
## the name, the icon and a two-line buy sticker did not fit 130 px).
static func tile_growth(ts: float) -> float:
	return 1.0 + (ts - 1.0) * TILE_GROW


## ANIM-R2 E6: the most a chip ("firmware") or Daemon tile may grow to at text scale `ts`
## with `count` in its row: a microchip shares its window's width (the socket list under
## it), a Daemon widens a little (the SLICES window keeps its row); both may grow as tall
## as the lower row's tiles.
static func chip_tile_room(kind: String, count: int, ts: float, quad: Vector2 = MODEM_QUAD) -> Vector2:
	# Art pass W8c: chip text at `body` needs taller tiles (their window grows with them).
	var h := CHIP_TILE.y * maxf(tile_growth(ts), chip_text_scale(ts)) * CHIP_ROOM_TALL
	if kind == "firmware":
		var w := (quad.x - QUAD_FRAME.x - 10.0 * maxi(0, count - 1)) / maxf(1.0, count)
		return Vector2(maxf(CHIP_TILE.x, w), h)  # art pass W8c: its share of the window
	return Vector2(maxf(CHIP_TILE.x, minf(quad.x * 0.5 - QUAD_FRAME.x, CHIP_TILE.x * chip_text_scale(ts))), h)


## Art pass W8c (ART_BIBLE §11 Modem, critique 52: microchip text was ~7 px): the lettering
## scale a Modem chip or Daemon tile draws at, so its words (ZineCard's caption step) come
## out at the `body` step times the text size.
static func chip_text_scale(ts: float) -> float:
	return ts * float(UiTheme.BODY) / float(UiTheme.CAPTION)


## Art pass W8c: how many columns the Modem's windows take at text scale `ts` (two, one at
## big sizes: the page then scrolls inside its window).
static func modem_columns(ts: float) -> int:
	return 2 if ts <= MODEM_TWO_COLUMNS_MAX else 1


## Art pass W8c: a Modem window's least size at text scale `ts`: its share of the page's
## width beside the sign (MODEM_QUAD at 1.0 is the least), as tall as MODEM_QUAD.
func modem_quad(ts: float) -> Vector2:
	var page := (size.x if size.x > 0.0 else get_viewport_rect().size.x) - ModemSign.ART_SIZE.x - UiTheme.GUTTER - MODEM_PAGE_PAD
	var cols := modem_columns(ts)
	var w := (page - QUAD_GAP * (cols - 1)) / cols
	return Vector2(maxf(MODEM_QUAD.x, floorf(w)), MODEM_QUAD.y)


## Art pass W8c: the largest text scale the Modem keeps two columns at, the room the page's
## own frame takes (px), and how much taller than CHIP_TILE a chip may grow for body text.
const MODEM_TWO_COLUMNS_MAX := 1.15
const MODEM_PAGE_PAD := 24.0
const CHIP_ROOM_TALL := 1.6


## Grows `tile` (wider first, then taller, never past `most`) until its whole effect text
## fits at CHIP_READABLE px or more; at `most` its own fit (ZineCard.fit_whole) takes the
## text down as far as it must. Tiles already fitting stay as they are.
static func fit_chip_tile(tile: ZineCard, most: Vector2) -> void:
	var sz := tile.custom_minimum_size
	for i in 200:
		tile.size = sz
		if tile.buy_button != null:
			tile.buy_button.refit()  # its height at this width (one line or two) is the foot
		var parts := tile.tile_parts()
		if int(parts["rows"]) >= (parts["desc_lines"] as PackedStringArray).size() and int(parts["dfs"]) >= chip_readable(tile):
			break
		if sz.x < most.x:
			sz.x = minf(sz.x + CHIP_FIT_STEP, most.x)
		elif sz.y < most.y:
			sz.y = minf(sz.y + CHIP_FIT_STEP, most.y)
		else:
			break
	tile.size = sz
	tile.custom_minimum_size = sz


## Art pass W8c: the lettering a Modem chip's effect text must keep (px): the `body` step at
## the tile's own text size (chip_text_scale), never under CHIP_READABLE.
static func chip_readable(tile: ZineCard) -> int:
	return maxi(CHIP_READABLE, roundi(UiTheme.CAPTION * tile.text_scale))


## Opens a modal viewer over the netrun screen. The viewers hold focus themselves
## (UiFocus.hold: the D-pad and A can't reach the Modem behind them; focus returns to the
## tile that opened them on close).
func _open_modal(view: Control) -> void:
	add_child(view)
	# Art pass W8a/W8c (ART_BIBLE §10 rules 3, 6): the modal opens with W8a's motion and
	# counts as open, so a page change waits for it to close (`_show_current`).
	PageTransition.open_modal(view)


## Deck viewer in pick mode: the chosen card is removed for the shop's price.
func open_remove() -> void:
	var s := RunManager.netrun
	var view := DeckView.new(s.run.operative.deck, s.lookup, tr("REMOVE A CARD // %d CYCLES") % s.card_removal_price(), TextDb.mark("REMOVE"))
	view.card_picked.connect(remove_card)
	_open_modal(view)
	# ANIM-4b: the cards drag onto the SHRED tile (select + REMOVE stays).
	view.enable_drops(_modal_layer(view))


## Spinner viewer in pick mode: the chosen slot is overwritten with stock slice `stock_index`.
func open_overwrite(stock_index: int) -> void:
	var s := RunManager.netrun
	var sd := s.lookup.get_content(StringName(String(s.run.shop["slices"][stock_index]))) as SliceData
	var name_text := "%s %d" % [tr(String(Palette.SLICE_NAMES.get(sd.slice_type, "?"))), sd.base_output] if sd != null else "?"
	# The price depends on the slot (the Miss slot costs more): the view shows the picked
	# slot's own price and turns UPGRADE off when it is out of reach (H20).
	var view := SpinnerView.new(s.run.operative.slot_slice_ids, s.run.operative.slot_firmware_ids, s.lookup, tr("UPGRADE A SLICE // INSTALL %s") % name_text,
		TextDb.mark("UPGRADE"), RunManager.config().shop_slices)
	view.slot_picked.connect(func(slot: int) -> void: overwrite_slice(slot, stock_index))
	_open_modal(view)
	view.set_prices(s.slice_overwrite_price, s.run.cycles)
	# ANIM-4b: the slice being installed sits beside the wheel and drags onto a slot (select
	# + UPGRADE stays).
	if sd != null:
		var chip := ZineCard.new(name_text, -1, Codex.describe(sd), 0)
		chip.name = "InstallSlice"
		chip.as_tile(ZineCard.Look.SLICE_TILE, Palette.slice_color(sd.slice_type)).tile_text(Settings.text_scale)
		chip.slice_type = sd.slice_type
		chip.slice_output = sd.base_output
		chip.hotkey = ""
		chip.custom_minimum_size = Vector2(SpinnerView.SIDE_W, SLICE_TILE.y * tile_growth(Settings.text_scale))
		_input_tip(chip, "", "install")
		view.enable_drops(_modal_layer(view), chip, _item_payload("slice", "modal", stock_index, sd.id))


## Mid-run raid interlude (GDD 4.4, 7.3): setup with exact projection, run assets and
## the Armory both deployable, then the playout.
func _show_raid() -> void:
	var s := RunManager.netrun
	var c := s.campaign
	var pending := s.raid_pending()
	var raid := CampaignRules.raid_data(pending, s.lookup)
	var projection := s.raid_projection()
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	# ANIM-R3 B5: set up like the HQ's raid setup (it read as a debug form): the raid's
	# warning, a forecast stamp and the facts as badges, then a row per node.
	var warn := _label(TextDb.t(raid, "warning_text"))
	warn.name = "RaidWarning"
	warn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(warn)
	box.add_child(_raid_forecast(projection))
	var run_assets := s.run_assets()
	# ANIM-4b: the run's assets and the Armory's as chips to drag onto a node's row (the
	# lists and buttons stay); a placed asset's Withdraw drags onto another row or back onto
	# the Armory.
	var chips := VBoxContainer.new()
	chips.name = "RaidAssets"
	box.add_child(chips)
	var run_row := HFlowContainer.new()
	run_row.name = "RunAssetChips"
	run_row.add_theme_constant_override("h_separation", 8)
	chips.add_child(run_row)
	run_row.add_child(_label(tr("RUN ASSETS:")))
	for i in run_assets.size():
		run_row.add_child(_asset_chip("RunAsset_%d" % i, run_assets[i]))
	var armory_row := HFlowContainer.new()
	armory_row.name = "ArmoryChips"
	armory_row.add_theme_constant_override("h_separation", 8)
	chips.add_child(armory_row)
	armory_row.add_child(_label(tr("ARMORY:")))
	for i in c.armory.size():
		armory_row.add_child(_asset_chip("Armory_%d" % i, c.armory[i]))
	# Art pass W8c (critique 28): never an empty "RUN ASSETS:" / "ARMORY:" label: an empty
	# list hides its row (the ARMORY row stays, hidden, as the drop target a placed asset
	# goes back to), and with nothing at all to deploy one designed note says so.
	run_row.visible = not run_assets.is_empty()
	var placed := false
	for sid in c.grid.claimed_ids():
		placed = placed or not c.grid.assets_on(sid).is_empty()
	armory_row.visible = not c.armory.is_empty() or placed
	if c.armory.is_empty() and placed:
		# Empty but a place a deployed asset can go back to: it says so.
		var back := _label(tr("empty: drop a placed asset here"))
		back.name = "ArmoryEmpty"
		back.add_theme_color_override("font_color", Palette.TEXT_MID)
		armory_row.add_child(back)
	if run_assets.is_empty() and c.armory.is_empty():
		chips.add_child(_empty_assets_note())
	# Art pass W8c (§2, §6.5: never a native dropdown): the asset to deploy is picked once, on
	# tiles (the run's assets, then the Armory's); each node's row deploys it there. The
	# chips above still drag onto a row.
	var deploy_pick: TilePicker = null
	if not run_assets.is_empty() or not c.armory.is_empty():
		deploy_pick = TilePicker.new(deploy_tiles(run_assets, c.armory))
		deploy_pick.name = "DeployPick"
		deploy_pick.columns = maxi(1, floori(RAID_WINDOW_WIDTH * minf(Settings.text_scale, RAID_WINDOW_GROW) / ((TilePicker.TILE_W + TilePicker.TILE_GAP) * Settings.text_scale)))
		deploy_pick.tooltip_text = UiTip.fold(tr("The asset a row's Deploy here puts on its node."))
		var pick_row := VBoxContainer.new()
		pick_row.name = "DeployRow"
		pick_row.add_child(_label(tr("Deploy:")))
		pick_row.add_child(deploy_pick)
		chips.add_child(pick_row)
	for site_id in c.grid.claimed_ids():
		var row := HFlowContainer.new()  # wraps inside the 1280 screen (horizontal pass 10)
		row.name = "RaidRow_%s" % site_id
		var n: Dictionary = projection.nodes.get(String(site_id), {})
		row.add_child(_raid_node_badge(site_id, n))
		var deployed := c.grid.assets_on(site_id)
		for i in deployed.size():
			var idx := i
			var sid := site_id
			var withdraw := _button(tr("Withdraw %s") % _content_name(deployed[i]), func() -> void: raid_move(sid, idx, &""))
			withdraw.name = "Withdraw_%s_%d" % [sid, idx]
			_input_tip(withdraw, tr("Back to the Armory."), "withdraw")
			row.add_child(withdraw)
		if c.grid.is_active_node(site_id) and deploy_pick != null:
			# Art pass W8c: one button per row deploys the picked asset (DeployPick).
			var sid2 := site_id
			var n_run := run_assets.size()
			var deploy := _icon_button(tr("Deploy here"), func() -> void:
				var k := deploy_pick.selected()
				if k < n_run:
					raid_deploy_run_asset(k, sid2)
				else:
					raid_deploy_armory(k - n_run, sid2), StatIcon.ARMORY)
			deploy.name = "Deploy_%s" % site_id
			deploy.theme_type_variation = UiTheme.SECONDARY
			deploy.tooltip_text = UiTip.fold(tr("Deploy the asset picked above on %s.") % _site_name(site_id))
			row.add_child(deploy)
		box.add_child(row)
	var run_btn := _button(tr(START_DEFENSE), raid_fight)
	run_btn.name = "StartDefense"
	# Art pass W8c (§6.4, critique 28): the one primary, as in the HQ's raid setup; sized
	# to its label.
	run_btn.theme_type_variation = UiTheme.PRIMARY
	run_btn.size_flags_horizontal = Control.SIZE_SHRINK_END
	IconMark.attach(run_btn, StatIcon.RAIDS)
	box.add_child(run_btn)
	# ANIM-R1 M8: the interlude is a window beside the raid's map on the city (the Grid, the
	# threats' routes to CORE), framed before the jack's cover lifts: a jack into a mid-run
	# raid lands on the setup with its map, not on a dark page of text.
	var root := HBoxContainer.new()
	root.name = "RaidInterlude"
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var win := TerminalWindow.new(tr("RAID // %s") % TextDb.t(raid, "display_name"), Palette.corp_color(c.corporation_id))
	win.name = "RaidWindow"
	win.custom_minimum_size.x = RAID_WINDOW_WIDTH * minf(Settings.text_scale, RAID_WINDOW_GROW)
	win.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	win.body.add_child(box)
	root.add_child(win)
	var area := Control.new()
	area.name = "RaidMapArea"
	area.mouse_filter = Control.MOUSE_FILTER_IGNORE
	area.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(area)
	_set_panel(root, false)
	# Art pass W8c (W7 hookup, §9.5): the raid's map over a dimmed, blurred city.
	var calm: Array[Control] = [win]
	_city_page(true, calm)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var g := CityLayout.grid_graph(c, RunManager.corporation, CityLayout.threat_paths(c, RunManager.corporation))
	_mount_route(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, RAID_MIN_ZOOM, RAID_MAP_ANCHOR, Vector2.INF)
	city_overlay.avoid_controls([win])
	_raid_map_area = area
	_frame_raid_map.call_deferred()
	_register_raid_drops(run_assets, armory_row)


## ANIM-R3 B5: the interlude's forecast as the raid setup shows it: the dashed stamp ("IF
## THE RAID RUNS NOW: HOME -5") beside badges for home, threats stopped and steps.
func _raid_forecast(projection: RaidResolver.RaidResult) -> Control:
	var row := HBoxContainer.new()
	row.name = "RaidForecast"
	row.add_theme_constant_override("separation", 10)
	# ANIM-R4 H3: the one verdict (RaidVerdict), as the HQ's raid setup says it.
	var clean := RaidVerdict.clean_projection(projection)
	var stamp := ForecastStamp.new(RAID_FORECAST_CAPTION, RaidVerdict.of_projection(projection), RaidVerdict.color_of(clean), RaidVerdict.icon_of(clean))
	stamp.name = "InterludeForecast"
	stamp.custom_minimum_size = Vector2(RAID_STAMP, RAID_STAMP) * (1.0 + (Settings.text_scale - 1.0) * RAID_STAMP_FOLLOW)
	row.add_child(stamp)
	var facts := HFlowContainer.new()
	facts.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	facts.add_theme_constant_override("h_separation", 8)
	facts.add_theme_constant_override("v_separation", 4)
	row.add_child(facts)
	var c := RunManager.netrun.campaign
	var home_col := Palette.CELL_ACID if projection.home_after >= projection.home_before else Palette.CELL_PINK
	var home := Badge.new(tr("HOME %d → %d") % [projection.home_before, projection.home_after], home_col, "",
		tr("Your home server (CORE) now and after the raid: %d → %d integrity. At 0 the campaign is lost. Exact: the playout matches it.") % [projection.home_before, projection.home_after]).with_meter(projection.home_after, c.grid.home_max_integrity).with_icon(StatIcon.HOME)
	home.name = "HomeForecast"
	facts.add_child(home)
	var total := projection.threats_destroyed + projection.threats_reached_home
	var stopped := Badge.new(tr("STOPPED %d/%d") % [projection.threats_destroyed, maxi(total, projection.threats_destroyed)], Palette.CELL_ACID, "",
		tr("Threats your nodes destroy: %d of the %d that come. The rest reach your nodes or the home server.") % [projection.threats_destroyed, maxi(total, projection.threats_destroyed)]).with_icon(StatIcon.RAIDS)
	stopped.name = "ThreatsStopped"
	facts.add_child(stopped)
	return row


## ANIM-R3 B5: a node's row head as the raid setup writes it: its name and kind, its
## integrity now and after the raid, the outcome word in its colour.
func _raid_node_badge(site_id: StringName, n: Dictionary) -> Control:
	var c := RunManager.netrun.campaign
	var outcome := String(n.get("outcome", ""))
	var col := Palette.CELL_ACID if outcome == "holds" else Palette.CELL_PINK
	var text := tr("%s  HP %s → %s  %s") % [_site_name(site_id), n.get("before", "?"), n.get("after", "?"), RaidFxLayer.tr_outcome(outcome)]
	var tip := tr("%s (%s): integrity (HP) now and after the raid.") % [_site_name(site_id), _content_name(c.grid.node_type_of(site_id))]
	var names := PackedStringArray()
	for a in c.grid.assets_on(site_id):
		names.append(_content_name(a))
	if not names.is_empty():
		tip += " " + tr("Defences: %s.") % ", ".join(names)
	var b := Badge.new(text, col, "", tip)
	b.name = "RaidNode_%s" % site_id
	return b


## Art pass W8c: the deploy picker's tiles: the run's assets, then the Armory's (name, where
## it comes from as the meta line, the Armory icon).
func deploy_tiles(run_assets: Array[StringName], armory: Array) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for a in run_assets:
		out.append({"name": _content_name(a), "meta": tr("RUN ASSET"), "icon": StatIcon.ARMORY})
	for a in armory:
		out.append({"name": _content_name(a), "meta": tr("ARMORY"), "icon": StatIcon.ARMORY})
	return out


## Art pass W8c (critique 28): the designed empty state when there is nothing to deploy: the
## Armory icon and one caption line, never bare "RUN ASSETS:" / "ARMORY:" labels.
func _empty_assets_note() -> Control:
	var row := HBoxContainer.new()
	row.name = "NoAssets"
	row.add_theme_constant_override("separation", UiTheme.SP_S)
	var side := UiTheme.BASE_SIZE * Settings.text_scale * IconMark.SIZE_FACTOR
	row.add_child(IconMark.standalone(StatIcon.ARMORY, side, Palette.TEXT_MID))
	var l := _label(tr("No assets to deploy: this run carries none and the Armory is empty. Your nodes hold with what is on them."))
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.add_theme_color_override("font_color", Palette.TEXT_MID)
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.CAPTION))
	row.add_child(l)
	return row


## A raid interlude's asset chip (ANIM-4b): a taped note with the asset's name that only
## moves (a press picks it up, as the HQ's crew chips).
func _asset_chip(chip_name: String, asset: StringName) -> Button:
	var b := Button.new()
	b.name = chip_name
	b.theme_type_variation = &"NoteButton"
	b.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	b.text = _content_name(asset)
	_input_tip(b, "", "asset")
	return b


## Raid interlude: the run's and the Armory's chips drag onto every claimed node's row; a
## placed asset (its Withdraw) onto another row or onto the ARMORY chips.
func _register_raid_drops(run_assets: Array[StringName], armory_row: Control) -> void:
	var c := RunManager.campaign
	for i in run_assets.size():
		var chip := _panel.find_child("RunAsset_%d" % i, true, false) as Control
		if chip != null:
			drops.add_source(chip, {"kind": "run_asset", "index": i, "asset": run_assets[i], "motion": &"loadout_swap"}, true)
	for i in c.armory.size():
		var chip := _panel.find_child("Armory_%d" % i, true, false) as Control
		if chip != null:
			drops.add_source(chip, {"kind": "armory_asset", "index": i, "asset": c.armory[i], "motion": &"loadout_swap"}, true)
	for site_id in c.grid.claimed_ids():
		var sid: StringName = site_id
		var deployed := c.grid.assets_on(sid)
		for i in deployed.size():
			var w := _panel.find_child("Withdraw_%s_%d" % [sid, i], true, false) as Control
			if w != null:
				drops.add_source(w, {"kind": "placed", "site": sid, "index": i, "asset": deployed[i], "motion": &"loadout_swap"})
		var row := _panel.find_child("RaidRow_%s" % sid, true, false) as Control
		if row != null:
			drops.add_target("node:%s" % sid, ["run_asset", "armory_asset", "placed"], "node", sid, DropLayer.rect_of(row))
	drops.add_target("armory", ["placed"], "armory", &"", DropLayer.rect_of(armory_row))


## A content id's translated display name (the id only when there is no such content).
func _content_name(id: Variant) -> String:
	var res := RunManager.lookup().get_content(StringName(String(id)))
	return TextDb.t(res, "display_name") if res != null and "display_name" in res else String(id)


## A Site's translated name (CORE for the home server).
func _site_name(site_id: StringName) -> String:
	var c := RunManager.campaign
	if c != null and c.grid != null and site_id == c.grid.home_site_id:
		return tr(HOME_LABEL)
	var sd := CampaignRules.site_data(RunManager.corporation, site_id) if RunManager.corporation != null else null
	return TextDb.t(sd, "display_name") if sd != null else String(site_id)


## Art pass W8c (ART_BIBLE §11 Run failed, §8 T4, critique 51): the run's end staged over
## the city (RunEndStage): the operative's Polaroid flatlines, the city grades to grey, the
## verdict slams in at `hero` size, the run in numbers on a taped receipt with what the end
## means, then Back to HQ (the primary). FLATLINED, JACKED OUT and HOME FELL share the
## template. (Overlaps ANIM-R5 B3, which also moves the end over the city and adds the
## permadeath line and the Heat reason: on merge, keep this staging and put B3's words in
## the stage's fate line.)
func _show_end() -> void:
	var s := RunManager.netrun
	var o := s.run.outcome
	var won := o == RunState.Outcome.COMPLETED
	var aborted := o == RunState.Outcome.ABORTED
	var title := tr("NETRUN COMPLETE") if won else (tr("NETRUN ABORTED - the home server fell") if aborted else tr("NETRUN FAILED - operative lost"))
	var op := s.run.operative
	var stats := [[StatIcon.COMBATS, str(s.run.combats_won)], [StatIcon.ELITES, str(s.run.elites_defeated)], [StatIcon.CYCLES, str(s.run.cycles)],
		[StatIcon.BANKED, str(s.run.banked_schematics)], [StatIcon.HEAT, TextDb.signed(s.run.heat_gained)]]
	var stage := RunEndStage.new(o, tr(RunEndStage.verdict_of(o)), RunEndStage.color_of(o), op.class_id, op.id, op.name,
		tr("NETRUN"), stats, title)
	stage.receipt.tooltip_text = UiTip.fold(tr("Heat the run added (campaign Heat is now %d).") % s.campaign.heat)
	var back := stage.back_button
	back.text = tr("Back to HQ")
	back.pressed.connect(finish_run)
	back.tooltip_text = UiTip.fold(tr("Back to HQ: the campaign, the City Grid and the crew."))
	IconMark.attach(back, StatIcon.BACK)
	stage.set_meta(FIRST_FOCUS_META, back)
	# Never a black void: the city shows behind the end (a fight hid it).
	background.visible = true
	_set_panel(stage, false)
	if entering:
		stage.play()
	else:
		stage.finish_now()


# --- Drag and drop (Animation pass ANIM-4b) --------------------------------------------------
# Every item a run moves between places drags there too, as on the HQ (ANIM-4's DropLayer):
# Modem purchases onto the deck, a slot or the Daemons, deck cards onto the shredder, loot
# onto the deck, a slot or the Daemons, event rewards onto the deck or the Daemons, raid
# assets onto nodes. A drop is an intent: `_on_dropped` makes the same call the item's
# button makes (Signal Up, Call Down). Whether a target takes an item is the rules' own
# answer, asked of a copy of the run and the campaign (`_dry`): nothing here decides a rule.

## What an item's tooltip adds about dragging it, by item kind (keys).
const DRAG_TIPS := {"card": "Or drag it onto the CARDS tag: the card goes into your deck.", # TR
	"chip": "Or drag it onto a slot of your spinner: the chip goes into that slot.", # TR
	"daemon": "Or drag it onto the DAEMONS icon: the Daemon is installed.", # TR
	"slice": "Or drag it onto a slot of your spinner: the slice overwrites that slot."} # TR

## Art pass W8c (ART_BIBLE 6.8, 12; W9's audit, netrun_scene "Or drag it..."): the same tips
## for a pad player (never "click" or "drag": the pick-up button carries the item, the
## D-pad aims, A drops), and the tips the other drag items carry, both ways.
const DRAG_TIPS_PAD := {"card": "Or pick it up and move it onto the CARDS tag: the card goes into your deck.", # TR
	"chip": "Or pick it up and move it onto a slot of your spinner: the chip goes into that slot.", # TR
	"daemon": "Or pick it up and move it onto the DAEMONS icon: the Daemon is installed.", # TR
	"slice": "Or pick it up and move it onto a slot of your spinner: the slice overwrites that slot.", # TR
	"install": "Pick it up and move it onto a slot to overwrite that slot (or press it, then pick the slot).", # TR
	"withdraw": "Or pick it up and move it onto another node's row to move it there.", # TR
	"asset": "Pick it up and move it onto a node's row to deploy it there (or press it, then pick the row).", # TR
	"spinner": "Move a microchip or a slice onto a slot to put it there."} # TR
const DRAG_TIPS_MORE := {"install": "Drag it onto a slot to overwrite that slot (or press it, then pick the slot).", # TR
	"withdraw": "Or drag it onto another node's row to move it there.", # TR
	"asset": "Drag it onto a node's row to deploy it there (or press it, then pick the row).", # TR
	"spinner": "Drag a microchip or a slice onto a slot to put it there."} # TR
## The metas an input-aware tip keeps (its words before the drag line, the drag kind).
const TIP_BASE_META := &"tip_base"
const TIP_KIND_META := &"tip_drag_kind"


## Art pass W8c: `c`'s tooltip: `base` then the drag line of `kind` in the device's words
## (UiTip.for_input), folded; kept on `c` so a device change rewords it.
func _input_tip(c: Control, base: String, kind: String) -> void:
	c.set_meta(TIP_BASE_META, base)
	c.set_meta(TIP_KIND_META, kind)
	c.tooltip_text = input_tip_text(base, kind)


## The words of an input-aware tip for the device in use.
func input_tip_text(base: String, kind: String) -> String:
	var line := ""
	if kind != "":
		var mouse := String(DRAG_TIPS.get(kind, DRAG_TIPS_MORE.get(kind, "")))
		line = UiTip.for_input(tr(mouse), tr(String(DRAG_TIPS_PAD.get(kind, ""))))
	var parts := PackedStringArray()
	for w in [base, line]:
		if w != "":
			parts.append(w)
	return UiTip.fold("\n".join(parts))


## Rewords every input-aware tip on the page (the device changed).
func _reword_tips() -> void:
	if _panel == null or not is_instance_valid(_panel):
		return
	for n in _panel.find_children("*", "Control", true, false):
		if n.has_meta(TIP_KIND_META):
			(n as Control).tooltip_text = input_tip_text(String(n.get_meta(TIP_BASE_META)), String(n.get_meta(TIP_KIND_META)))


## The run's drop layer (over every page) and the pad prompts of the page on show (kept, so
## a carry can swap them and put them back).
var drops: DropLayer
var _page_prompts: Array = []
## The drop layer over an open viewer (the REMOVE deck view, the UPGRADE spinner view);
## null when none is open.
var modal_drops: DropLayer = null


## True when the run's page for `s` has items to pick up and carry (the pad's X prompt).
static func has_drags(s: NetrunSession) -> bool:
	match s.run.phase:
		RunState.Phase.SHOP, RunState.Phase.REWARD, RunState.Phase.RAID:
			return true
		RunState.Phase.EVENT:
			var ev := s.current_event()
			if ev != null:
				for c in ev.choices:
					if choice_item(c) != "":
						return true
	return false


## The kind of item an event choice hands over that has a place on screen to go ("card" to
## the deck, "daemon" to the Daemons), or "" (no item, or one with no second place: a
## Firmware chip goes on to the loot, where its slot is picked; an asset is banked at a
## Rack; a rescued operative joins the roster at HQ).
static func choice_item(c: EventChoiceData) -> String:
	if c == null or c.reward == null:
		return ""
	if c.reward is CardData:
		return "card"
	if c.reward is DaemonData:
		return "daemon"
	return ""


## Sets the page's pad prompts (kept, so a carry can swap them and put them back).
func set_page_prompts(list: Array) -> void:
	_page_prompts = list
	if (drops == null or drops.mode != DropLayer.Mode.CARRY) and (modal_drops == null or not is_instance_valid(modal_drops) or modal_drops.mode != DropLayer.Mode.CARRY):
		pad_prompts.set_prompts(list)


func _on_carry_changed(carrying: bool) -> void:
	pad_prompts.set_prompts([[&"ui_accept", "Drop"], [&"ui_cancel", "Cancel"]] if carrying else _page_prompts) # TR


## A drop layer's questions and intents come to this screen: whether a target takes an
## item (the rules, dry-run), what the item looks like, and the drop itself.
func _wire_drops(layer: DropLayer) -> void:
	layer.check = drop_error
	layer.ghost_maker = drop_ghost
	layer.dropped.connect(_on_dropped.bind(layer))
	layer.refused.connect(_on_refused)
	layer.carry_changed.connect(_on_carry_changed)


## A drop layer over viewer `view` (added after it, so it draws on top, and outliving it:
## a landing still plays as the viewer closes; it frees itself once its flights end).
func _modal_layer(view: Control) -> DropLayer:
	if modal_drops != null and is_instance_valid(modal_drops):
		modal_drops.retire()
	var layer := DropLayer.new()
	layer.name = "ModalDrops"
	_wire_drops(layer)
	add_child(layer)
	modal_drops = layer
	view.tree_exiting.connect(func() -> void:
		if is_instance_valid(layer):
			layer.retire()
		if modal_drops == layer:
			modal_drops = null, CONNECT_ONE_SHOT)
	return layer


## The top bar's CARDS tag (global; empty when not shown): where cards go.
func deck_rect() -> Rect2:
	var st := hud.stats
	if st == null or not st.is_visible_in_tree():
		return Rect2()
	var rects := st.tag_rects()
	for i in mini(st.items.size(), rects.size()):
		if st.icon_of(i) == StatIcon.CARDS:
			var xf := st.get_global_transform()
			return Rect2(xf * rects[i].position, rects[i].size * xf.get_scale())
	return Rect2()


## The targets every run page shares: the deck (the CARDS tag) and the Daemons (the top
## bar's DAEMONS icon, which opens the tray).
func _add_bar_targets(accepts_deck: Array, accepts_daemons: Array) -> void:
	if not accepts_deck.is_empty():
		drops.add_target("deck", accepts_deck, "deck", null, deck_rect)
	if not accepts_daemons.is_empty():
		drops.add_target("daemons", accepts_daemons, "daemons", null, DropLayer.rect_of(hud.daemon_button))


## The slots of the small spinner `mini` as targets of `accepts` on `layer`.
func _add_slot_targets(layer: DropLayer, mini: SpinnerMini, accepts: Array) -> void:
	for k in mini.slices.size():
		layer.add_target("slot:%d" % k, accepts, "slot", k, DropLayer.rect_of(mini.pad(k)))


## The running operative's small spinner (the Modem and a Firmware loot: its slots are
## where chips and slices go), each slot's pad named as the socket lists name it.
func _spinner_mini() -> SpinnerMini:
	var op := RunManager.netrun.run.operative
	var tips: Array = []
	for k in op.slot_slice_ids.size():
		tips.append(slot_name(op, k))
	var mini := SpinnerMini.new(op.slot_slice_ids, op.slot_firmware_ids, RunManager.lookup(), tips)
	_input_tip(mini, tr("Your spinner."), "spinner")
	return mini


## A drag payload for item `index` of `kind` ("card", "chip", "daemon", "slice") from `src`
## ("shop", "loot", "event", "modal"): purchases land shrinking into their target with
## SOLD (`drop_buy`), loot and event items without it.
func _item_payload(kind: String, src: String, index: int, item: StringName) -> Dictionary:
	var p := {"kind": kind, "src": src, "index": index, "item": item, "motion": &"drop_buy", "land": "buy"}
	if src in ["shop", "modal"]:
		p["stamp"] = tr("SOLD")
	return p


## Modem: cards drag onto the deck, microchips onto a slot of the small spinner, Daemons
## onto the DAEMONS icon, slice upgrades onto the slot they overwrite.
func _register_shop_drops(mini: SpinnerMini, fw_slot: SlotPicker) -> void:
	var shop := RunManager.netrun.run.shop
	for pair in [["Stickers", "cards", "card"], ["Chips", "firmware", "chip"], ["Daemons", "daemons", "daemon"], ["Slices", "slices", "slice"]]:
		var row := _panel.find_child(String(pair[0]), true, false) if _panel != null else null
		if row == null:
			continue
		var stock: Array = shop.get(String(pair[1]), [])
		var items := _row_items(row)
		for i in mini(items.size(), stock.size()):
			var c := items[i]
			if c == null:
				continue
			var p := _item_payload(String(pair[2]), "shop", i, StringName(String(stock[i])))
			if pair[2] == "chip" and fw_slot != null:
				p["prefer"] = fw_slot.selected()
			drops.add_source(c, p)
	_add_bar_targets(["card"], ["daemon"])
	if mini != null:
		_add_slot_targets(drops, mini, ["chip", "slice"])


## Loot: the offer drags onto where it goes (a card to the deck, a Firmware chip onto a slot,
## a Daemon onto the DAEMONS icon).
func _register_loot_drops(row: Control, mini: SpinnerMini, slot_option: SlotPicker) -> void:
	var offer := RunManager.netrun.current_reward()
	var kind := {"card": "card", "firmware": "chip", "daemon": "daemon"}.get(String(offer.get("kind", "")), "") as String
	if kind == "" or row == null:
		return
	var options: Array = offer["options"]
	for i in mini(row.get_child_count(), options.size()):
		var p := _item_payload(kind, "loot", i, StringName(String(options[i])))
		if slot_option != null:
			p["prefer"] = slot_option.selected()
		drops.add_source(row.get_child(i) as Control, p)
	_add_bar_targets(["card"], ["daemon"])
	if mini != null:
		_add_slot_targets(drops, mini, ["chip"])


## Event: a choice that hands over a card or a Daemon drags onto the deck or the Daemons (the
## choice's own press stays).
func _register_event_drops(ev: TerminalEventData, options: Control) -> void:
	var any := false
	for i in ev.choices.size():
		var kind := choice_item(ev.choices[i])
		var b := options.find_child("Choice%d" % (i + 1), false, false) as Control
		if kind == "" or b == null:
			continue
		var p := _item_payload(kind, "event", i, (ev.choices[i].reward as Resource).get("id"))
		drops.add_source(b, p)
		_input_tip(b, b.tooltip_text, kind)
		any = true
	if any:
		_add_bar_targets(["card"], ["daemon"])


## Whether `target` takes `payload`: "" yes, a reason (the rules' own refusal) no, or
## DropLayer.SKIP when the target is no place for it (where it already is).
func drop_error(payload: Dictionary, target: Dictionary) -> String:
	var s := RunManager.netrun
	if s == null:
		return DropLayer.SKIP
	var value: Variant = target.get("value")
	var i := int(payload.get("index", -1))
	var src := String(payload.get("src", ""))
	var ids: Array = [payload.get("item", &"")]
	match [String(payload.get("kind", "")), String(target.get("kind", ""))]:
		["card", "deck"], ["daemon", "daemons"]:
			var plural := "cards" if payload["kind"] == "card" else "daemons"
			match src:
				"shop":
					return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.buy(plural, i), ids)
				"loot":
					return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.choose_reward(i), ids)
				"event":
					return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.choose_event_option(i), ids)
		["chip", "slot"]:
			ids.append(s.run.operative.slot_firmware_ids[int(value)] if int(value) < s.run.operative.slot_firmware_ids.size() else &"")
			match src:
				"shop":
					return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.buy("firmware", i, int(value)), ids)
				"loot":
					return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.choose_reward(i, int(value)), ids)
		["slice", "slot"]:
			ids.append(s.run.operative.slot_firmware_ids[int(value)] if int(value) < s.run.operative.slot_firmware_ids.size() else &"")
			return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.overwrite_slice(int(value), i), ids)
		["deck_card", "shred"]:
			return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.remove_card(i), ids)
		["run_asset", "node"]:
			return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.raid_deploy_run_asset(i, value), ids + [value])
		["armory_asset", "node"]:
			return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.raid_deploy_armory(i, value), ids + [value])
		["placed", "node"]:
			if value == payload.get("site"):
				return DropLayer.SKIP
			return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.raid_move(payload["site"], i, value), ids + [value, payload["site"]])
		["placed", "armory"]:
			return _dry(func(d: NetrunSession) -> Array[Dictionary]: return d.raid_move(payload["site"], i, &""), ids + [payload["site"]])
	return DropLayer.SKIP


## Runs rule call `f` on a copy of the run and the campaign: its refusal text (content and
## Site ids in `ids` written as the screens name them), or "" when it would go through.
## The real run and campaign are never touched.
func _dry(f: Callable, ids: Array = []) -> String:
	var events: Array[Dictionary] = f.call(dry_session())
	for e in events:
		if String(e.get("type", "")) == "refused":
			return _named(String(e.get("text", "refused")), ids)
	return ""


## A copy of the running session with a copy of the campaign (a dry run's playground: the
## same rules, the same RNG state, nothing shared with the real ones).
func dry_session() -> NetrunSession:
	var s := RunManager.netrun
	var d := s.run.to_dict()
	d["streams"] = s.streams.to_dict()
	d["combat"] = s.combat.to_dict() if s.combat != null else {}
	return NetrunSession.from_dict(s.resolver, s.campaign.duplicate_state(), {"run": d}, s.corporation)


## `text` (a rules refusal) with the ids in `ids` written as the screens name them (the rules
## speak in ids: "barbed_wire does not fit a ATTACK slice.").
func _named(text: String, ids: Array) -> String:
	for id in ids:
		var key := String(id)
		if key == "" or not text.contains(key):
			continue
		var c := RunManager.campaign
		var is_site := c != null and c.grid != null and (c.grid.is_claimed(StringName(key)) or StringName(key) == c.grid.home_site_id)
		text = text.replace(key, _site_name(StringName(key)) if is_site else _content_name(key))
	return text


## What a dragged item looks like (its ghost and flying copies): a copy of its sticker or
## tile, else the item drawn from its content (an event's reward, a raid asset).
func drop_ghost(payload: Dictionary, source: Control) -> Control:
	if source is ZineCard:
		return (source as ZineCard).ghost_copy()
	var lookup := RunManager.lookup()
	var id := StringName(String(payload.get("item", payload.get("asset", ""))))
	var res := lookup.get_content(id) if id != &"" else null
	if res is CardData:
		var card := ZineCard.new(TextDb.t(res, "display_name"), (res as CardData).ram_cost, TextDb.t(res, "description"), 0).scaled(Settings.text_scale).with_card(res as CardData)
		card.hotkey = ""
		card.size = card.custom_minimum_size
		return card
	if res is DaemonData or res is FirmwareData:
		var tile := ZineCard.new(TextDb.t(res, "display_name"), -1, shop_text(res), 0)
		tile.as_tile(ZineCard.Look.CHIP, Palette.NEON_VIOLET if res is DaemonData else Palette.NET_CYAN).tile_text(Settings.text_scale)
		tile.hotkey = ""
		tile.size = tile.custom_minimum_size
		return tile
	if res is DefenseAssetData:
		var asset := AssetCard.new(id, TextDb.t(res, "display_name"), (res as DefenseAssetData).integrity, 1)
		asset.set_effect(res)
		asset.size = asset.custom_minimum_size
		return asset
	return null


## A valid drop: the same call the item's button makes (the layer already flies the copy).
## A viewer a drop was made in closes as its UPGRADE / REMOVE closes it, but only once the
## landing on its wheel or shredder has played (at once when none plays; any press ends
## the landing). The state changed already: this holds only the view.
func _close_after_landing(view: Control, layer: DropLayer) -> void:
	if view == null or not is_instance_valid(view):
		return
	var ref: WeakRef = weakref(view)
	var shut := func() -> void:
		var v: Control = ref.get_ref()
		if v != null and v.is_inside_tree() and v.has_method("close"):
			v.call("close")
			# The page was rebuilt under the viewer: focus its first control, as after a click.
			if _panel != null and is_instance_valid(_panel):
				UiFocus.focus_first.call_deferred(_panel)
	var f: Dictionary = layer.last_flight if layer != null else {}
	if f.is_empty() or not layer.flights.has(f):
		shut.call()
	else:
		f["on_done"] = shut


func _on_dropped(payload: Dictionary, target: Dictionary, layer: DropLayer) -> void:
	var value: Variant = target.get("value")
	var i := int(payload.get("index", -1))
	var src := String(payload.get("src", ""))
	match [String(payload.get("kind", "")), String(target.get("kind", ""))]:
		["card", "deck"], ["daemon", "daemons"]:
			match src:
				"shop":
					_buy("cards" if payload["kind"] == "card" else "daemons", i, -1, false)
				"loot":
					_choose_reward(i, -1, false)
				"event":
					choose_event(i)
		["chip", "slot"]:
			# The button path: pick the slot in the socket list, then press BUY (or take the loot).
			if src == "shop":
				_buy("firmware", i, int(value), false)
			else:
				_choose_reward(i, int(value), false)
		["slice", "slot"]:
			# In the UPGRADE viewer: select the slot and press UPGRADE; on the Modem page the
			# same call the viewer's UPGRADE makes.
			overwrite_slice(int(value), i)
			if src == "modal":
				_close_after_landing(get_node_or_null("SpinnerView") as Control, layer)
		["deck_card", "shred"]:
			# The button path: select the card and press REMOVE (the call REMOVE makes).
			var deck_view := get_node_or_null("DeckView") as DeckView
			if deck_view != null:
				# (No select: its REMOVE lettering would push the SHRED tile from under the copy.)
				var shredded := deck_view.card(i)
				if shredded != null:
					shredded.modulate.a = 0.0  # its copy is on its way into the shredder
			remove_card(i)
			_close_after_landing(deck_view, layer)
		["run_asset", "node"]:
			raid_deploy_run_asset(i, value)
		["armory_asset", "node"]:
			raid_deploy_armory(i, value)
		["placed", "node"]:
			raid_move(payload["site"], i, value)
		["placed", "armory"]:
			raid_move(payload["site"], i, &"")


## A drop the target refuses: nothing changes; the rules' reason shows, as a button's refusal
## does.
func _on_refused(_payload: Dictionary, _target: Dictionary, reason: String) -> void:
	_log.append_text("[color=orange]%s[/color]\n" % reason)
	ToastNote.show_on(self, reason, true)
	_flash_if_short(reason)


## ANIM-R2 E9: a purchase refused for want of Cycles flashes the money: the top bar's
## CYCLES tag (and the Modem's wallet) go red with "PRICE > CYCLES" under them.
func price_refused(price: int) -> void:
	var s := RunManager.netrun
	if s == null:
		return
	# ANIM-R3 A6j: the same plain words as a RAM refusal ("69 > 10" was a sum to decode).
	var text := tr("NEED %d · HAVE %d") % [price, s.run.cycles]
	hud.stats.flash_refusal(TextDb.mark("CYCLES"), text)
	var wallet := _panel.find_child("Wallet", true, false) as HudStats if _panel != null else null
	if wallet != null:
		wallet.flash_refusal(TextDb.mark("CYCLES"), text)


## A refusal's words name the price it wanted when Cycles fell short: flash the money.
func _flash_if_short(reason: String) -> void:
	if not reason.contains(tr("Cycles")) and not reason.contains("Cycles"):
		return
	var rx := RegEx.create_from_string("(\\d+)")
	var m := rx.search(reason)
	if m != null:
		price_refused(m.get_string(1).to_int())


# --- Helpers --------------------------------------------------------------------------

func _refresh_status() -> void:
	var c := RunManager.campaign
	if c == null:
		_status.text = tr("No campaign.")
		return
	var s := RunManager.netrun
	var text := "Heat %d/%d | Schematics %d | Armory %d" % [c.heat, RunManager.resolver.config.heat_max, c.schematics, c.armory.size()]
	if s != null and not s.run.is_over():
		var op := s.run.operative
		text += " || Run T%d seed %d | %s HP %d/%d Rank %d | Cycles %d | banked %d | node %s" % [s.run.tier, s.run.run_seed, op.name, op.hp, op.max_hp, op.rank, s.run.cycles, s.run.banked_schematics, s.run.current_node_id]
	_status.text = text
	# Every tag says what it means on hover (H21 #9); its icon is the resource's own.
	var stats := [[TextDb.mark("HEAT"), str(c.heat if hud_heat_shown < 0 else hud_heat_shown), "/%d" % RunManager.resolver.config.heat_max, tr("Heat: how hard the corporation hunts the Cell. Thresholds add raids and harder rules.")],
		[TextDb.mark("SCHEMATICS"), str(c.schematics), "", tr("Schematics: the campaign's currency, spent at HQ.")]]
	# H24 S16: whose numbers these are: the campaign's, then this run's.
	var captions := [[0, tr("CAMPAIGN"), tr("The campaign's numbers: they stay between runs.")]]
	if s != null and not s.run.is_over():
		var op := s.run.operative
		captions.append([stats.size(), tr("THIS RUN"), tr("This run's numbers: the operative's HP, the Cycles to spend, the deck, rank and what the run has banked.")])
		stats.append_array([[TextDb.mark("HP"), str(op.hp), "/%d" % op.max_hp, tr("%s's HP. At 0 the operative flatlines.") % op.name],
			[TextDb.mark("CYCLES"), str(s.run.cycles), "", tr("Cycles: this run's money, spent in the Modem.")],
			[TextDb.mark("CARDS"), str(op.deck.size()), "", tr("Cards in %s's deck (VIEW LOADOUT shows them).") % op.name],
			[TextDb.mark("RANK"), str(op.rank), "", tr("Rank: runs survived. It brings wheel upgrades and higher netrun tiers.")],
			[TextDb.mark("BANKED"), str(s.run.banked_schematics), "", tr("Schematics this run has banked for the campaign.")]])
	hud.set_stats(stats, captions)
	hud.loadout_button.visible = s != null and not s.run.is_over()
	if s != null and not s.run.is_over():
		hud.set_daemons(s.run.operative.daemon_ids)


## The top bar's DAEMONS icon: the running operative's Daemons as a tray of sigils.
func open_daemons() -> void:
	var s := RunManager.netrun
	if s == null or has_node("DaemonTray"):
		return
	var at := hud.daemon_button.get_global_rect().end.x
	add_child(DaemonTray.new(s.run.operative.daemon_ids, s.lookup, at, s.run.operative.name))


## VIEW LOADOUT: the running operative's deck and spinner.
func open_loadout() -> void:
	var s := RunManager.netrun
	if s == null:
		return
	_open_modal(LoadoutView.new(s.run.operative, s.lookup, RunManager.config().shop_slices))


func _report(events: Array[Dictionary]) -> void:
	var c := RunManager.campaign
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")
			if String(e.get("type", "")) in TOAST_WARN_EVENTS:
				ToastNote.show_on(self, String(e["text"]), true)
				_flash_if_short(String(e["text"]))
		if c == null:
			continue
		match String(e.get("type", "")):
			# H24 S15: a line tied to a screen ends when the player leaves it ("Jacking you
			# in" stayed on the Modem and the event).
			"run_start":
				Dialogue.speak("run_start", RC.Voice.DISPATCH, c.corporation_id, &"", c.runs_started, "route")
				if RunManager.netrun != null:
					Dialogue.bark(RunManager.netrun.run.operative.class_id, "jack_in", c.runs_started, "route")
			"run_complete":
				Dialogue.speak("run_complete", RC.Voice.DISPATCH, c.corporation_id, &"", c.runs_completed, "run_end")
			"run_died":
				Dialogue.speak("run_died", RC.Voice.DISPATCH, c.corporation_id, &"", c.deaths, "run_end")
			"rack_captured":
				Dialogue.speak("rack", RC.Voice.DISPATCH, c.corporation_id, &"", c.runs_started, "loot")
			"heat_threshold":
				Dialogue.threshold_line(c.corporation_id, int(e.get("heat", 0)), c.campaign_seed)
			"raid_interlude":
				Dialogue.raid_warning(c.corporation_id, StringName(String(e.get("queued_raid_id", e.get("raid_id", "")))), c.raids_won + c.raids_lost)


func open_settings() -> void:
	if _settings_panel != null:
		_settings_panel.queue_free()
		_settings_panel = null
		return
	_settings_panel = PauseMenu.new()
	_settings_panel.position = Vector2((size.x - PauseMenu.MENU_SIZE.x) / 2.0, SubtitleStrip.top_below(PAUSE_TOP))  # under the subtitle band (H22: the top bar grows with its words)
	_settings_panel.resumed.connect(open_settings)
	_settings_panel.quit_to_title.connect(func() -> void: open_settings(); RunManager.go_to_title())
	add_child(_settings_panel)
	get_tree().paused = false


func _input(event: InputEvent) -> void:
	# ANIM-R1 (MotionSkip): a press during a route move (key, click or pad button) ends it
	# and is consumed before any control sees it.
	# ANIM-R4 C2 (MotionSkip.verdict): a press that works the screen ends it and passes on; an
	# open pause menu keeps its presses.
	if not _travelling:
		return
	var v := MotionSkip.verdict(event, self)
	if v == MotionSkip.Verdict.IGNORE:
		return
	_end_travel()
	if v == MotionSkip.Verdict.CONSUME:
		MotionSkip.consume(self, event)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_settings") and combat_scene == null:
		open_settings()
		get_viewport().set_input_as_handled()
		return
	# B leaves the Modem (H23 S11). H24 S6: only a pad's B: a keyboard's Esc (ui_cancel too)
	# must not leave when open_settings is bound elsewhere.
	if event is InputEventJoypadButton and event.is_action_pressed("ui_cancel") and not event.is_action("open_settings") and not _modal_open() \
			and RunManager.netrun != null and RunManager.netrun.run.phase == RunState.Phase.SHOP:
		leave_shop()
		get_viewport().set_input_as_handled()
		return
	if map_view != null and is_instance_valid(map_view) and RunManager.netrun != null and RunManager.netrun.run.phase == RunState.Phase.MAP:
		var available := RunManager.netrun.available_nodes()
		for i in mini(9, available.size()):
			if event.is_action_pressed("card_%d" % (i + 1)):
				enter_node(available[i])
				get_viewport().set_input_as_handled()
				return


func _build_ui() -> void:
	background = WireframeBackground.new()
	add_child(background)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	hud = HudBar.new()
	hud.loadout_pressed.connect(open_loadout)
	hud.daemons_pressed.connect(open_daemons)
	root.add_child(hud)
	_status = hud.label
	subtitle_strip = SubtitleStrip.new()
	root.add_child(subtitle_strip)
	# Tall panels (a raid with many claimed Sites) scroll vertically; never sideways.
	var scroll := ScrollContainer.new()
	scroll.follow_focus = true
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
	_log.custom_minimum_size = Vector2(0, 110)
	root.add_child(_log)
	# Shown only when the player turns it on in Options.
	_log.visible = Settings.system_log
	Settings.changed.connect(func() -> void: _log.visible = Settings.system_log)
	# Art pass W8c (ART_BIBLE §5.3): a page taller than the screen (the Modem at 2.0) scrolls
	# inside its window with a visible MORE BELOW hint.
	more_hint = ScrollHint.new(scroll)
	add_child(more_hint)
	# ANIM-4b: drag and drop over every page (targets pulse, the pad's reticle, flights).
	drops = DropLayer.new()
	_wire_drops(drops)
	add_child(drops)


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	return b


## A button with a StatIcon before its words (H21 #13).
func _icon_button(text: String, on_pressed: Callable, kind: StringName) -> Button:
	var b := _button(text, on_pressed)
	IconMark.attach(b, kind)
	return b
