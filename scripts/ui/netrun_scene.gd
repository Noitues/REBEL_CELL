extends Control
## Functional M2 netrun scene (placeholder look): start screen, map, combat (embedded
## CombatScene), rewards, Terminal events, Mainframe shop and the run summary. Every
## action goes through RunManager's NetrunSession; the scene only displays state.

const COMBAT_SCENE := preload("res://scenes/combat/combat_scene.tscn")
## What each route node holds (the route buttons' tooltips).
## H24 S3: the words in these constants are translation keys ("# TR"), translated where
## shown; every page but the fight shows its words as given (TextDb.shown_as_given).
const NODE_TIPS := {RC.InfilNodeType.ROUTER: "Router: a fight. Win it for Cycles and loot.", # TR
	RC.InfilNodeType.TERMINAL: "Terminal: an event with choices.", # TR
	RC.InfilNodeType.MAINFRAME: "Mainframe: the cyber shop (cards, Firmware, Daemons, slices, card removal).", # TR
	RC.InfilNodeType.SERVER_RACK: "Server Rack: the Site's guardian. Breach it to complete the run."} # TR

## What each route node is, in a word (H21 #14: two "Router" buttons looked the same) and
## as an icon; an elite Router is an "Elite fight" with the crown.
const NODE_WORDS := {RC.InfilNodeType.ROUTER: "Fight", RC.InfilNodeType.TERMINAL: "Event", # TR
	RC.InfilNodeType.MAINFRAME: "Shop", RC.InfilNodeType.SERVER_RACK: "Rack"} # TR
const NODE_ICONS := {RC.InfilNodeType.ROUTER: StatIcon.FIGHT, RC.InfilNodeType.TERMINAL: StatIcon.TERMINAL,
	RC.InfilNodeType.MAINFRAME: StatIcon.SHOP, RC.InfilNodeType.SERVER_RACK: StatIcon.RACK}
const ELITE_WORD := "Elite fight" # TR
## The pause menu's least top (px); it opens under the subtitle band.
const PAUSE_TOP := 100.0
## A reachable route node's colour on the map (route_graph) and on its button's icon.
## ART-7 3B (ART_BIBLE v2 4.6 option A): the selectable ring's orange.
const ROUTE_NEXT_COLOR := RouteInk.RING_AVAILABLE
## The home server's name (as the HQ shows it; never its id).
const HOME_LABEL := "CORE" # TR
## The Mainframe's quadrant (px) and the room its window frame and title take (px): shop cards
## grow with the text size only as far as a quadrant holds them (H21 #15).
const MAINFRAME_QUAD := Vector2(490, 250)
const QUAD_FRAME := Vector2(24, 56)
const QUAD_GAP := 12.0
## LEAVE MAINFRAME (in the free corner of the REMOVE A CARD quadrant, so the Mainframe ends
## on screen at text scale 1.6) and its exit icon beside it (px).
const LEAVE_AT := Vector2(900, 440)
const LEAVE_ICON := 34.0
## ART-0 C (text scale 2.0): the least gap kept between LEAVE THE MAINFRAME and the REMOVE A
## CARD row's pieces it would otherwise cover (px).
const LEAVE_GAP := 6.0
## Loot stickers at text scale 1.0 (the card face's 3:4, round 32 reward_screen_v2 at 720p; S-CARDFACE) and the
## most a row of them may grow (px).
const LOOT_CARD := Vector2(162, 216)
const LOOT_ROW_MAX := 1150.0
## The least gap between loot stickers (px; their tilt's reach is added, ANIM-R2 E8).
const LOOT_GAP := 14.0
## ANIM-R1 M11: the gap between the loot stickers and Skip at text scale 1.0 (px): a
## sticker's rest tilt and hover lift reach this far below its box.
const LOOT_SKIP_GAP := 14.0
## Room above the event's paper at text scale 1.0 (px): its tape and title keep clear of
## the subtitle band (H23 S10).
const EVENT_TOP_GAP := 12.0
## HEAT-ALL: above this text scale the event window has no gap above it: the Heat gauge makes the top bar two
## rows at the largest text and the gap was the room the choices needed.
const EVENT_GAP_MAX_SCALE := 1.6
## The event's choice column keeps this far from the screen's right edge at text scale 1.0
## (px; H24 S9: its buttons ran to x=1280, the right border cut).
const EVENT_RIGHT_GAP := 16.0
## The loot and reward kinds as the LOOT title words them (keys).
const LOOT_WORDS := {"card": "card", "firmware": "Firmware chip", "daemon": "Daemon", "slice": "slice"} # TR
## Passes fitting the route map beside the ROUTE column (H24 S12), the route's own zoom
## and anchor, and the smallest the fit may make it (the city's zoom).
const ROUTE_FITS_MAX := 3
## Parity ROUTE-06: passes after ROUTE_FITS_MAX that may bring where the player is and the
## next choices back into the free area (pan and zoom out only; `fit_route_map`).
const ROUTE_RESCUE_PASSES := 2
## The route's zoom before its fit (the fit then frames it between CityConfig's
## `route_ortho_near` and `route_ortho_far`, B3: review D14) and where it is anchored.
const ROUTE_ZOOM := 1.45
const ROUTE_ANCHOR := Vector2(0.46, 0.58)
## The slice tiles in the Mainframe at text scale 1.0 (px): they widen with the text as far as
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
## B5: the kit's CRT glass behind the page host (shown on glass pages).
var _panel_glass: CrtTerminalPanel = null
## B5 (D8 / D9): the run's Site close-up behind the loot and event pages, the copy the event's CAM feed reads, and
## the event's dim with the corp tint over it.
var site_backdrop: CombatBackdrop = null
var site_copy: BackBufferCopy = null
var site_dim: ColorRect = null
var _log: RichTextLabel
var _panel: Control = null
var combat_scene: Control = null
var background: WireframeBackground
## B1a (review D19, section d): the world's darkening under the UI, the panels' shadows and the
## light spill (UiScrimPools), over the city (and the HQ run's compound) and under every page. A
## fight has its own (the combat scene's, over its backdrop).
var scrim: UiScrimPools
var map_view: NetrunMapView = null
var playout: RaidPlayoutPanel = null
var _spoken_events: Dictionary = {}
var _settings_panel: PauseMenu = null
## The route's node buttons (their key hints follow the device).
var _route_buttons: Array[Button] = []
## The route view's key: the route's node kinds (placed clear of the nodes; null when
## zoomed out, where the campaign map's MapLegend shows in the ROUTE window).
var route_legend: RouteLegend = null
## ART-7 3B: the operative's corp-paper dossier over the map, and the decrypted node panel
## under the ROUTE window (route view only; null otherwise).
var dossier: OperativeDossier = null
var node_panel: RouteNodePanel = null
## ART-7 3B: the dressed room behind a node's own screen (event, shop, loot).
var node_backdrop: NodeBackdrop = null
## ART-8 8w: the HQ run's page on the compound (boss runs) and the Central Server's gate.
var hq_run_view: HqRunView = null
var gate: CentralServerGate = null
## Pad button prompts at the foot of the screen (H23 S11).
var pad_prompts: PadPrompts
## The screen on show (screen_name) and whether the last page entered a new screen (its
## entrance plays) or refreshed the same one (Animation pass ANIM-6).
var _shown_screen: String = ""
var entering: bool = false
## Capture demos (--demo-buy / --demo-pick / --demo-choose) act this many frames in, once
## the screen has come in.
const DEMO_ACTION_FRAMES := 30
## The loot `--demo-loot` offers (content ids).
const DEMO_LOOT := ["twist", "jam", "cache"]

## Event types that pop a toast (H20: the log strip is optional).
const TOAST_WARN_EVENTS: Array[String] = ["refused", "deploy_failed", "undock_failed"]


func _ready() -> void:
	UiTheme.apply(self)
	MotionSkip.register(self)  # ANIM-R5: the route move completes with every other motion
	# Subtitles sit in the top band, clear of every control (H20); combat docks its own.
	Dialogue.dock_default()
	Settings.hints_changed.connect(_relabel_route)
	RunManager.run_abandoned.connect(_on_run_abandoned)  # ABANDON-QUIT: from either pause menu
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
		# ANIM-R6 B2: dev flags set the run up through DemoSetup (views never write state).
		DemoSetup.open_shop(RunManager.netrun)
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
			DemoSetup.add_daemons(RunManager.netrun, [&"twin_pointer", &"shield_cache", &"zero_day", &"feedback_loop"] as Array[StringName])
			_refresh_status()
			open_daemons()
			(get_node("DaemonTray") as DaemonTray).show_card(&"shield_cache", false)
		elif args.has("--demo-spinnergrid"):
			open_overwrite(1)
		elif args.has("--demo-deckgrid"):
			open_remove()
		elif args.has("--demo-buy"):
			# Capture (ANIM-6): the first card is bought once the Mainframe has come in.
			MotionDemo.after_frames(self, DEMO_ACTION_FRAMES, func() -> void: buy("cards", 0))
		_demo_drag_arg(args)
		return
	if args.has("--demo-event") or args.has("--demo-dispatch") or args.has("--demo-loot"):
		# Screenshot shortcuts for the Terminal event (street / DISPATCH voice) and loot.
		RunManager.save_slot = "demo"
		new_campaign(1)
		start_run(1)
		if args.has("--demo-loot"):
			DemoSetup.offer_loot(RunManager.netrun, DEMO_LOOT)
		else:
			DemoSetup.open_event(RunManager.netrun, &"ev_dispatch_early_reply" if args.has("--demo-dispatch") else &"ev_leash_on_the_floor")
		_show_current()
		# Capture (ANIM-6): the loot's second card is picked / the first choice is taken.
		if args.has("--demo-pick"):
			MotionDemo.after_frames(self, DEMO_ACTION_FRAMES, func() -> void: choose_reward(1))
		elif args.has("--demo-choose"):
			MotionDemo.after_frames(self, DEMO_ACTION_FRAMES, func() -> void: choose_event(0))
		_demo_drag_arg(args)
		return
	# ANIM-R5 captures: the run-end page (died, completed, aborted), reached through the
	# session's own ending (dev flag only). ANIM-R6 B9: with --demo-combat the flag is the
	# fight's own ending (win / lose), played below in context.
	if run_end_demo(args) != "":
		_demo_run_end(run_end_demo(args))
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
				DemoSetup.only_class(RunManager.campaign, RunManager.lookup().get_content(StringName(a.trim_prefix("--demo-class="))) as ClassData)
		start_run(1)
		if args.has("--demo-combat") or args.has("--demo-tutorial"):
			RunManager.pending_tutorial = args.has("--demo-tutorial")
			enter_node(RunManager.netrun.available_nodes()[0])
		elif args.has("--demo-anim=route_pulse"):
			_demo_route_pulse.call_deferred()
		elif args.has("--demo-interlude"):
			# ANIM-R3 B5 captures: the run opens on a raid interlude (Heat past 25 queues one).
			DemoSetup.queue_raid_interlude(RunManager.netrun, RunManager.config())
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
	# ANIM-R6 D11: the log strip (an Options switch) translates its words.
	_log.append_text("[b]%s[/b] %s\n" % [tr("New campaign"), tr("(seed %d): %d Schematics, %d rookies.") % [seed, RunManager.campaign.schematics, RunManager.campaign.roster.size()]])
	_show_start()


func start_run(_tier: int = 1) -> void:
	var s := RunManager.start_run()
	if s == null:
		_log.append_text("[color=orange]%s[/color]\n" % tr("No living operative or open Site: go to HQ."))
		return
	_report(s.last_events)
	_show_current()


func resume() -> void:
	if RunManager.resume():
		_log.append_text("[b]%s[/b]\n" % tr("Resumed."))
		_show_current()
	else:
		_log.append_text("[color=orange]%s[/color]\n" % tr("Nothing to resume."))


func enter_node(node_id: StringName) -> void:
	if _travelling:
		# Defensive: while a move plays no press reaches a choice (ANIM-R5 B6: `_input` keeps
		# the route page's presses and ends the move); a call that still comes ends it.
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
	# ANIM-R5 B7: the demo reaches its first node through the session's own rules (the view
	# set the run's node and visited list itself): it enters the first Router, plays the fight
	# out with SEND IT, and skips the loot, so the run stands on that node with the map open.
	if not demo_first_node(s):
		print("anim5: route_pulse has no move to show")
		return
	_show_current()
	if not await _frames_in_tree(DEMO_SETTLE_FRAMES):
		return
	for f in DEMO_BAKE_FRAMES:
		if background.city.showing_current_look() and background.city.camera_settled() and background.city.bake_fade >= 1.0:
			break
		if not await _frames_in_tree(1):
			return
	print("anim5: route_pulse starts on frame %d" % Engine.get_frames_drawn())
	enter_node(s.available_nodes()[0])


## ANIM-R6 B9: the run-end page a capture asks for (`--demo-end=<kind>` without
## `--demo-combat`: with it, the kind is the fight's ending, win or lose, played in context);
## "" for none.
static func run_end_demo(args: PackedStringArray) -> String:
	if args.has("--demo-combat"):
		return ""
	for a in args:
		if a.begins_with("--demo-end="):
			return a.trim_prefix("--demo-end=")
	return ""


## ANIM-R5 capture (dev flag only): the demo run ends through the session's own ending
## (`died`: the flatline, `completed`: the clean exit) and the run-end page shows.
func _demo_run_end(kind: String) -> void:
	RunManager.save_slot = "demo"
	new_campaign(1)
	start_run(1)
	var s := RunManager.netrun
	DemoSetup.end_run(s, kind)
	_report(s.last_events)
	_show_current()


## ANIM-R5 B7 (dev flag only): the most SEND ITs the route demo's first fight may take.
const DEMO_FIGHT_TURNS := 60


## ANIM-R5 B7: moves the demo run onto its first node through NetrunSession only (enter_node,
## the fight's SEND ITs, skip_reward); true when it stands there with the map open.
static func demo_first_node(s: NetrunSession) -> bool:
	if s == null or s.available_nodes().is_empty():
		return false
	s.enter_node(s.available_nodes()[0])
	var turns := 0
	while s.in_combat() and turns < DEMO_FIGHT_TURNS:
		turns += 1
		s.combat_action(CombatAction.end_turn())
	while s.run.phase == RunState.Phase.REWARD:
		s.skip_reward()
	return s.run.phase == RunState.Phase.MAP and not s.available_nodes().is_empty()


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
## lets go: a Mainframe card onto the deck (`drag_buy_card`), a Firmware chip onto a slot it fits
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
			DemoSetup.set_cycles(s, DEMO_POOR_CYCLES)
			_show_current()
			if not await _frames_in_tree(DEMO_LAYOUT_FRAMES):
				return
			src = _page_item("Stickers", 0)
		"drag_buy_chip":
			# Enough Cycles for any chip (the demo shows a purchase, not a refusal).
			DemoSetup.set_cycles(s, DEMO_RICH_CYCLES)
			_show_current()
			if not await _frames_in_tree(DEMO_LAYOUT_FRAMES):
				return
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
			if not await _frames_in_tree(DEMO_LAYOUT_FRAMES):
				return
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
		if not await _frames_in_tree(1):
			return
		var q := Tween.interpolate_value(0.0, 1.0, float(i + 1) / DEMO_DRAG_FRAMES, 1.0, Tween.TRANS_SINE, Tween.EASE_IN_OUT) as float
		layer.point_at(from.lerp(end, q) - Vector2(0, DEMO_DRAG_ARC * sin(PI * q)))
	if not await _frames_in_tree(DEMO_DRAG_HOLD):
		return
	print("anim4b: %s lets go on frame %d" % [id, Engine.get_frames_drawn()])
	layer.release_at(end)


## ANIM-R5 B10: awaits `n` frames while the scene stays in the tree; false when it left
## (freed or taken out mid-wait: the caller stops, never calling get_tree() on nothing).
func _frames_in_tree(n: int) -> bool:
	for i in n:
		if not is_inside_tree():
			return false
		await get_tree().process_frame
	return is_inside_tree()


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
## ANIM-R5 B6: shown, not live: nothing on the route page takes focus while the move plays
## (a second A on the focused choice reached the session mid-move and was refused), and
## `_input` keeps the page's presses (they end the move and do nothing else). The node's
## screen comes next and takes the focus.
func _refresh_route_choices() -> void:
	var row := _panel.find_child("RouteNodes", true, false) as VBoxContainer if _panel != null and is_instance_valid(_panel) else null
	if row == null:
		return
	_fill_route_choices(row)
	UiFocus.link_layout(_panel)
	var owner := get_viewport().gui_get_focus_owner() if get_viewport() != null else null
	if owner != null and _panel.is_ancestor_of(owner):
		owner.release_focus()


## ANIM-5: a netrun move is playing on the route map (the node's screen opens after it).
var _travelling: bool = false


## ANIM-R5 B6: the controls whose presses a route move keeps (the route page).
func route_keep() -> Array:
	return [_panel] if _panel != null and is_instance_valid(_panel) else []


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
	# B5 (section f): the loot page's bar (CARDS) stays while the page does, so the pick flies to the tag it shows.
	_held_bar = bar_keys(s)
	_report(s.choose_reward(index, slot))
	# The picked card lifts and flies to the deck (ANIM-6); the page is rebuilt under it.
	if s.run.pending_rewards.size() < left and not offer.is_empty():
		if fly:
			var picked_item := _page_item("Stickers", index)
			# ART-9 4A: the sticker peels off the loot sheet as it lifts (`loot_peel`).
			var sheet := _panel.find_child("LootSheet", true, false) as LootSheet if _panel != null else null
			if sheet != null and picked_item != null:
				var at := picked_item.get_global_rect()
				sheet.peel(Rect2(at.position - sheet.global_position, at.size), (picked_item as ZineCard).accent if picked_item is ZineCard else Palette.TEXT_HI)
			_fly_item(picked_item, String(offer["kind"]), &"loot_pick", "", Motion.amplitude(&"loot_pick"))
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
	# ANIM-R5 B5: the picked card's flight (`loot_pick`, now the longer) lands before the page
	# goes too, so its landing pulse shows with the loot page still up.
	# (its lift takes FlightFx.lift_share() of its time on top of the travel).
	_hold_page(maxf(Motion.seconds(&"loot_reject") + Motion.delay_of(&"loot_reject"),
		Motion.seconds(&"loot_pick") * (1.0 + FlightFx.lift_share()) + Motion.delay_of(&"loot_pick")))


## ANIM-R4 C7 / ANIM-R6 B12: the page on show stays, inert (no input, no focus), while its
## flights and stamps play (the loot not taken falling, the event's outcome stamp), at most
## `hold` s (and one `loot_reject` more as grace), then the next page shows.
func _hold_page(hold: float) -> void:
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
	# The page leaves as soon as nothing flies (`_loot_hold_step`); the hold's time is only its
	# bound, with one `loot_reject` more as grace for a flight ending on the same frame.
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
	while n != null and not (n is TerminalWindow or n is LootSheet):
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
	# The chosen outcome stamps (ANIM-6). ANIM-R6 B12: on the event page, which stays (inert)
	# until the stamp has played and then leaves (it popped over the next page's route menu,
	# over its option [2]); a press ends the stamp and the page goes at once.
	if phase == RunState.Phase.EVENT and s.run.phase != RunState.Phase.EVENT and chosen != null:
		var row := chosen.get_node_or_null(^"OutcomeRow") as Control
		# ART-9 4A: the stamp says CHOSEN (round 31 `event_screen_memo`).
		if FlightFx.stamp_on(self, row if row != null else chosen, tr("CHOSEN")) != null:
			RunManager.after_step()
			_hold_page(Motion.seconds(&"event_choice_stamp") + Motion.delay_of(&"event_choice_stamp"))
			return
	RunManager.after_step()
	_show_current()


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
## ANIM-R1 M11: a Mainframe row's SOLD stubs are not items).
func _page_item(row: String, index: int) -> Control:
	var holder := _panel.find_child(row, true, false) if _panel != null and row != "" else null
	if holder == null or index < 0:
		return null
	var items := _row_items(holder)
	return items[index] if index < items.size() else null


## The items of a page row in stock order (a Mainframe row's SOLD stubs left out).
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
		# FIX-REDS-3: the bar already says the new numbers (Cycles spent: its tags move), so the
		# flight aims where its tag will rest, not where it stood before the purchase.
		_refresh_status()
		FlightFx.fly(self, item, item_target(kind), id, stamp, lift, Rect2(), _land_on.bind(kind))


## ANIM-R5 B5: a bought or picked item has landed: the top bar tag it went to pulses
## (`flight_land_pulse`: CARDS for a card; the DAEMONS icon or VIEW LOADOUT otherwise pop).
func _land_on(kind: String) -> void:
	if hud == null or not is_instance_valid(hud):
		return
	# ANIM-R6 B7: the bar's own (the motion lab plays the same on its pieces).
	hud.land_pulse(kind)


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
	# ANIM-R5 P2: behind the playout, the look its end shows after the raid: the fights'
	# stretch of city under the result's tint (it spreads at the end; until then the old image
	# stands in). ART-7 7w: the route after it is the 3D city (nothing to bake).
	if before != null and not events.is_empty():
		_prebake_raid_playout.call_deferred(before, CityInfluence.of(RunManager.campaign, RunManager.corporation))


## ANIM-R5 P2: the Heat the city's corporate creep shows while a raid's playout holds the
## pre-raid look (-1: the campaign's).
var _creep_heat: int = -1


## The city's corporate creep for Heat `heat` (0..1 of the Heat track).
static func creep_of(heat: int) -> float:
	return clampf(heat / float(RunManager.config().heat_max), 0.0, 1.0)


## ANIM-R5 P2: the mid-run raid's playout area, baked ahead (off the main thread) for campaign
## `c`'s raid map under influence `inf` (null: the city's current one): every node of it as a
## fight's focus at RAID_MIN_ZOOM (the interlude's playout ran ~5 s over the silhouette).
func _prebake_raid_playout(c: CampaignState, inf: Variant) -> void:
	if c == null or not is_inside_tree() or background == null:
		return
	var g := CityLayout.grid_graph(c, RunManager.corporation, CityLayout.threat_paths(c, RunManager.corporation))
	var region := Rect2()
	for n: Dictionary in g["nodes"]:
		var at: Vector2 = n["at"]
		var r := background.city.region_for(at + Vector2(0.5, 0.5), PLAYOUT_ANCHOR, RAID_MIN_ZOOM, size)
		region = r if not region.has_area() else region.merge(r)
	if region.has_area():
		background.city.prebake(region, inf, false, creep_of(RunManager.campaign.heat) if inf != null else -1.0)


## Where the interlude playout's fight sits on screen (its map area's centre; `_show_raid_playout`).
const PLAYOUT_ANCHOR := Vector2(0.4, 0.56)


## ANIM-R6 B4: the run end page's look baked ahead (off the main thread) from the fight that
## ended the run: the city's default frame at this screen's size under the campaign's Heat as
## it stands after the fight (a flatline adds Heat: a new look the fight's own bake never
## was). Returns the bake's key ("" when nothing was asked for: headless, or already baked).
## The run end's bake asked for when a fight ended the run, and the default frame's asked for
## when the fight began ("" when none: already baked, or headless).
var run_end_prebake: String = ""
var fight_prebake: String = ""


func prebake_run_end() -> String:
	if background == null or not is_inside_tree() or RunManager.campaign == null:
		return ""
	var city := background.city
	# The view the city shows with no route on it (a fight leaves the camera there, and the
	# run's end shows the same): measured, not worked out (frame_region is the HQ's frame).
	# The camera is brought up to date first: hidden behind the fight the city draws nothing,
	# so its last camera is the route's.
	city.update_camera()
	return city.prebake(city.view_rect(), null, false, creep_of(RunManager.campaign.heat))


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


## Abandon run (designer ruling 2026-10-05, GDD 4.5): the run ended as the operative's death
## (RunManager.abandon_run, from this scene's pause menu or the fight's): the pause closes, the
## run's report reads the events and the run's end page shows (FAILED - operative lost).
func _on_run_abandoned(events: Array[Dictionary]) -> void:
	if _settings_panel != null:
		open_settings()
	_report(events)
	_show_current()


func save_and_quit() -> void:
	if RunManager.scene_change_pending():
		return
	RunManager.autosave()
	_log.append_text(tr("Saved.") + "\n")
	RunManager.go_to_hq()
	_show_start()


# --- Panels --------------------------------------------------------------------------

func _show_current() -> void:
	_held_bar = []
	if _loot_hold != null:
		# ANIM-R4 C7: whatever shows next ends the loot page's wait.
		if _loot_hold.is_valid():
			_loot_hold.kill()
		_loot_hold = null
	var s := RunManager.netrun
	if s == null:
		_show_start()
		return
	# ART-0 F (ported from art-pass W8c, ART_BIBLE v1 §10 rule 6): a modal never outlives a
	# page change: the page changes once the open viewers have closed (a rebuild of the same
	# page under a viewer, the Mainframe after a shred, goes on at once).
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
	_update_node_backdrop()  # ART-7 3B: the node's dressed room behind its screen


## `glass` = false for screens built from their own terminal windows (the city shows
## between them).
func _set_panel(p: Control, glass: bool = true, screen_as: String = "") -> void:
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
	# S-COMBAT-HUD (parity CMB-07, combat_typical_v4): no global top bar in a fight; the TURN strip
	# and the corner chips stand alone and the wheels get the height (the bar's numbers keep
	# updating for the page after the fight).
	hud.visible = not p.has_method("attach_netrun")
	_panel_host.theme_type_variation = UiTheme.CRT_GLASS_PANEL if glass else &""
	_panel_glass.visible = glass
	# B5c (art director): the pages of stickers on the world keep them inside the screen's safe margin
	# (Fx.sticker_margin(): at the sides and the foot; the top bar is above them).
	var page_as := screen_name(RunManager.netrun) if screen_as == "" else screen_as
	if not glass and page_as in SAFE_MARGIN_SCREENS:
		var safe := StyleBoxEmpty.new()
		var m := Fx.sticker_margin()
		safe.content_margin_left = m
		safe.content_margin_right = m
		safe.content_margin_bottom = m
		_panel_host.add_theme_stylebox_override(&"panel", safe)
	else:
		_panel_host.remove_theme_stylebox_override(&"panel")
	_clear_route()
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_STOP
	_panel_host.add_child(p)
	_mark_scrim(p)
	var s := RunManager.netrun
	# ANIM-6: a new screen enters (glass slides in, paper drops); a page rebuilt on the same
	# screen (the Mainframe after a purchase) just shows. Focus lands when it ends.
	var screen := screen_name(s) if screen_as == "" else screen_as
	# ART-7 7w: the route page is the unified 3D city at the NETRUN band (GRID VIEW: the
	# Grid's band); the other pages keep the 2D city until their own views move onto it.
	if screen == "netrun_raid" or screen == RAID_PLAYOUT_SCREEN:
		# Parity RAID-13: the mid-run raid (its setup and its playout) is the unified 3D city at
		# the RAID band, as every other raid view (the HQ's setup, playout and report).
		use_route_city(true, CityLod.Band.RAID)
	else:
		use_route_city(screen == "route" and (s == null or s.run.kind != "boss" or _grid_zoomed))  # ART-8 8w: an HQ run draws its own compound city
	# LOOT-04 (designer 2026-10-05): the loot and event pages sit on the title's blurred city.
	# B5 (D8 / D9): now on the run's Site close-up (the blurred city stays their fallback under it).
	background.show_blurred_city(BLURRED_CITY_SCREENS.has(screen), BLURRED_CITY_LOOK,
		RunManager.campaign.corporation_id if RunManager.campaign != null else &"")
	_show_site_backdrop(screen, s)
	entering = screen != _shown_screen
	_shown_screen = screen
	# ART-9 4A: the Mainframe's facade stays only behind the Mainframe.
	if screen != "shop":
		_drop_shop_backdrop()
	if screen != "event" and _event_bbc != null and is_instance_valid(_event_bbc):
		_event_bbc.queue_free()
		_event_bbc = null
	# ANIM-R5 B2: an event's story and the run's end say long lines: their band holds two.
	subtitle_strip.set_lines(int(SUBTITLE_LINES.get(screen, 1)))
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
			PageTransition.enter(p, PageTransition.look_of(p), _settle_page.bind(p))
		else:
			_settle_page(p)
	_title_screen(s, screen)
	set_page_prompts([] if p.has_method("attach_netrun") else prompts_for(s))
	# H24 S15: lines tied to the screen being left end here.
	Dialogue.enter_screen(screen)
	if s != null and not s.run.is_over():
		AudioDirector.play_music("raid" if s.run.phase == RunState.Phase.RAID else "netrun", s.campaign.corporation_id)
	# ANIM-R5 B3: every page but a fight shows the city behind it (the run's end after a
	# flatline came up black: the fight had hidden it).
	if s == null or s.run.phase != RunState.Phase.COMBAT:
		background.visible = true
	if RunManager.campaign != null:
		# ANIM-R5 P2: a raid's playout holds the Heat creep of before the raid (as it holds the
		# pre-raid tint): its new Heat is a new look, which rebaked the whole playout mid-raid.
		background.corp_creep = creep_of(_creep_heat if _creep_heat >= 0 else RunManager.campaign.heat)
		background.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
		background.set_district(RunManager.campaign.corporation_id)
	# The combat panel brings its own log; give it the height instead.
	_log.custom_minimum_size = Vector2(0, 50 if p.get_script() == COMBAT_SCENE.get_script() or p.has_method("attach_netrun") else 110)


## ANIM-R5 B4: a page settles (its first focus lands) once its entrance has ended AND the
## words typing on it and in the subtitle are whole, each within its cap (`dispatch_type`,
## `event_type`): a route or raid line typed on after the page had settled and fast players
## moved on without reading it. A press shows every typing word whole (the one-press rule),
## so the focus lands at once then. The event page gives focus at once (its choices wait for
## the words themselves: ANIM-R2 E1).
func _settle_page(p: Control) -> void:
	_stop_settle_poll()
	if words_typing() and _held_choices.is_empty():
		_settling = weakref(p)
		get_tree().process_frame.connect(_poll_settle)
		return
	_focus_page(p)


## True while words type on screen (a page's or the subtitle's).
func words_typing() -> bool:
	return is_inside_tree() and (Typing.any_typing(get_tree()) or Dialogue.typing())


## True while a page waits for its words before its focus lands (tests).
func page_settling() -> bool:
	return _settling != null


var _settling: WeakRef = null


func _poll_settle() -> void:
	var p := _settling.get_ref() as Control if _settling != null else null
	if p == null or p != _panel:
		_stop_settle_poll()
		return
	if words_typing():
		return
	_stop_settle_poll()
	_focus_page(p)


func _stop_settle_poll() -> void:
	_settling = null
	if is_inside_tree() and get_tree().process_frame.is_connected(_poll_settle):
		get_tree().process_frame.disconnect(_poll_settle)


## A page's first focus: the control it names (FIRST_FOCUS_META: the Mainframe's first item,
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


## B5 (integration review D8 / D9; designer ruling 6 "FIGHT WON + OURS NOW + CONTINUE on the dimmed fought Site"):
## the loot page sits on the fought Site's close-up in its won state (the district at 62 %, the target's lights in the
## Cell's colours, OURS NOW written on in yellow pencil: CombatBackdrop's own won look); the event page on the run's
## Site close-up dimmed to EVENT_DIM with the corp's tint (EVENT_TINT_SHARE), its CAM feed reading the close-up
## (SiteCopy) before the dim, so the feed is never an empty box. Every other page hides them.
func _show_site_backdrop(screen: String, s: NetrunSession) -> void:
	var on := (screen == "loot" or screen == "event") and s != null and RunManager.campaign != null
	site_backdrop.visible = on
	site_copy.visible = on and screen == "event"
	site_dim.visible = on and screen == "event"
	if not on:
		return
	var corp := RunManager.campaign.corporation_id
	# Loot (reward_screen_v2): the won Site stands low right, under the sheet's foot by CONTINUE, where OURS NOW
	# reads; the close-up is framed on its target, so the backdrop's rect is grown to put its middle at LOOT_SITE_AT.
	var at := LOOT_SITE_AT if screen == "loot" else Vector2(0.5, 0.5)
	site_backdrop.anchor_left = 0.0
	site_backdrop.anchor_top = 0.0
	site_backdrop.anchor_right = at.x * 2.0
	site_backdrop.anchor_bottom = at.y * 2.0
	site_backdrop.offset_left = 0.0
	site_backdrop.offset_top = 0.0
	site_backdrop.offset_right = 0.0
	site_backdrop.offset_bottom = 0.0
	site_backdrop.show_place(BackdropCatalog.place(corp, false, BackdropCatalog.is_day(RunManager.campaign), s.run.site_id))
	# OURS NOW only where it has its room (no UI may cover pencil): from LOOT_SIDE_FROM the loot's side column and
	# its sheet take the screen's foot, so the won Site shows without its word.
	var ink := site_backdrop.get_node_or_null(^"OursNow") as CanvasItem
	if ink != null:
		ink.visible = screen != "loot" or Settings.text_scale < LOOT_SIDE_FROM
	_ours_watch = screen == "loot" and ink != null and ink.visible
	set_process(_ours_watch)
	# Art director (D8): the loot's district sits at about 62 % under the page (the sheet and FIRMWARE DROP on their
	# own B1a pools); the picture layers dim (on top of the won look's own district dim round the target), the
	# OURS NOW pencil over them does not.
	var shade := Palette.NO_TINT.darkened(1.0 - LOOT_DISTRICT) if screen == "loot" else Palette.NO_TINT
	for layer in [^"Still", ^"WonStill"]:
		var pic := site_backdrop.get_node_or_null(layer) as CanvasItem
		if pic != null:
			pic.modulate = shade
	if screen == "loot":
		# The won look as the fight left it; OURS NOW writes on as the page shows (D25: never faded in).
		if site_backdrop.won < 1.0:
			site_backdrop.won = 1.0
	else:
		site_backdrop.won = 0.0
		var tint := Palette.corp_color(corp)
		site_dim.color = Color(EVENT_DIM, EVENT_DIM, EVENT_DIM).lerp(Color(tint.r, tint.g, tint.b) * EVENT_DIM * 2.0, EVENT_TINT_SHARE)
		site_dim.color.a = 1.0


## Art director (B5 fix 2): no UI may cover pencil. OURS NOW stands where the won Site's close-up puts it (its target's
## top); while the loot page shows, a frame that finds it under one of the page's panels or stickers (FIRMWARE DROP,
## the sheet, CONTINUE) leaves the word out rather than tuck it under them.
func _process(_delta: float) -> void:
	if not _ours_watch or site_backdrop == null or not site_backdrop.visible:
		_ours_watch = false
		set_process(false)
		return
	var ink := site_backdrop.get_node_or_null(^"OursNow") as CanvasItem if site_backdrop != null else null
	if ink == null or not ink.visible or _panel == null or not is_instance_valid(_panel):
		return
	var word := site_backdrop.ours_now()
	if word == null or not word.is_visible_in_tree():
		return
	if PageTransition.running(_panel) or FlightFx.active_count(self) > 0:
		return  # the page's parts are still coming in (the loot fans up through the word's place)
	for c in _panel.find_children("*", "Control", true, false):
		var ctl := c as Control
		if not ctl.is_visible_in_tree():
			continue
		if (ctl.has_meta(UiScrimPools.META_POOL) or ctl is BaseButton) and word_covered_by(word, ctl.get_global_rect()):
			ink.visible = false
			_ours_watch = false
			return


## True when screen rect `r` covers any of pencil word `word` (its tilted letters' box with their shadow: the two
## boxes are tested in both frames, so a tilted word's empty corners never count).
static func word_covered_by(word: GreasePencilWord, r: Rect2) -> bool:
	var font := Palette.pencil()
	var px := word.font_px()
	var local := Rect2(Vector2(0, -font.get_ascent(px)), font.get_string_size(word.text, HORIZONTAL_ALIGNMENT_LEFT, -1, px))
	local.end += GreasePencilMark.SHADOW_OFFSET
	var xf := word.get_global_transform()
	return (xf * local).intersects(r) and local.intersects(xf.affine_inverse() * r)


## True while the loot page watches OURS NOW against its panels.
var _ours_watch: bool = false


## B5 (D9): the run's Site close-up as a picture (its city close-up's render, else its still): what the event's CAM
## feed shows. Null when there is none (the feed falls back to the screen copy).
func site_picture() -> Texture2D:
	if site_backdrop == null:
		return null
	if site_backdrop.city != null:
		return site_backdrop.city.get_texture()
	return site_backdrop.get(&"_tex") as Texture2D  # CombatBackdrop's still (read only)


## B5 (D8, reward_screen_v2): where the won Site's target stands on the loot page (screen share): low right, clear
## of the sheet, so OURS NOW reads over it above CONTINUE.
const LOOT_SITE_AT := Vector2(0.86, 0.84)
## Art director (D8): the loot page's district brightness (review: "district at 62 %").
const LOOT_DISTRICT := 0.62
## B5 (D9): the event page's close-up dims to this share, and takes this share of the corp's tint.
const EVENT_DIM := 0.4
const EVENT_TINT_SHARE := 0.35


## The meta naming a page's first focus.
const FIRST_FOCUS_META := &"first_focus"
## ANIM-R5 B2: subtitle lines the band holds on a screen (1 elsewhere).
const SUBTITLE_LINES := {"event": 2, "run_end": 2}
## LOOT-04 (designer 2026-10-05): the pages over the title's blurred 3D city (their own look:
## centred darkening for a centred page); the Mainframe keeps its own facade (SHOP).
const BLURRED_CITY_SCREENS: Array[String] = ["loot", "event"]
## B1a: the page parts that are panels on the world (UiScrimPools.mark_panels_in).
const SCRIM_PANELS: Array[String] = ["TerminalWindow", "LootSheet", "OperativeDossier", "RouteNodePanel"]
## B5c: the netrun pages whose stickers stand on the world, kept inside the screen's sticker safe margin.
const SAFE_MARGIN_SCREENS: Array[String] = ["loot", "event", "shop", "run_end"]
const BLURRED_CITY_LOOK := preload("res://content/config/overlay_city_backdrop.tres")
## ANIM-R5 B8: the mid-run raid's playout, a screen of its own (its title, its lines).
const RAID_PLAYOUT_SCREEN := "netrun_raid_playout"


## The pad prompts of the screen for the run's phase (H23 S11): A presses the focused
## choice (its verb here), B leaves the Mainframe, Menu opens the settings. A fight shows its
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
## The route's title sticker: round 44 `route_page.png`'s NETRUN (B3; parity ROUTE-06 had round
## 37's THE GRID). The fit's rescue pass (`fit_route_map`) frames the route under any bar.
const ROUTE_TITLE := "NETRUN" # TR


func _title_screen(s: NetrunSession, screen: String = "") -> void:
	close_heat_terminal(false)
	if s == null:
		hud.set_screen("", tr("NETRUN"))
		return
	if screen == RAID_PLAYOUT_SCREEN:
		# ANIM-R5 B8: the raid plays out (the run's phase is the route again already).
		hud.set_screen("", tr("NETRUN // RAID"))
		return
	match s.run.phase:
		RunState.Phase.MAP:
			# S-HQRUN (orchestrator 2026-10-06): a boss (HQ) run's map carries its own title
			# sticker on the page; the band shows only the Heat gauge, as the HQ does.
			if s.run.kind == "boss" and not _grid_zoomed:
				hud.set_screen("", "")
			else:
				hud.set_screen("", tr(ROUTE_TITLE))
		RunState.Phase.COMBAT:
			hud.set_screen("", "")
		RunState.Phase.REWARD:
			hud.set_screen("", "")  # B5 (D8): the page's own FIGHT WON sticker names it; PAYOUT is the terminal's word
		RunState.Phase.EVENT:
			# ANIM-R2 E2: a title as short as the Mainframe's, so the top bar keeps one row at 1.6
			# (the long one wrapped the tags onto two rows and pushed the page down).
			hud.set_screen("04", tr("TERMINAL EVENT"))
		RunState.Phase.SHOP:
			hud.set_screen("05", tr("MAINFRAME SHOP"))
		RunState.Phase.RAID:
			hud.set_screen("", tr("NETRUN // RAID"))
		_:
			# ANIM-R6 B5: the title agrees with the verdict (it said JACK OUT beside FLATLINED).
			hud.set_screen("", tr(end_title(s.run.outcome)))


func _show_start() -> void:
	_refresh_status()
	var box := VBoxContainer.new()
	box.add_child(GraffitiTag.new(tr("NETRUN")))
	var row := HBoxContainer.new()
	box.add_child(row)
	row.add_child(_label(tr("Campaign seed:")))
	var seed_spin := SpinBox.new()
	seed_spin.min_value = 0
	seed_spin.max_value = 999999
	seed_spin.value = 1
	row.add_child(seed_spin)
	row.add_child(_button(tr("New campaign"), func() -> void: new_campaign(int(seed_spin.value))))
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
			_request_node(id))
	top.add_child(map_view)
	# The number keys pick nodes on the keyboard; the pad has none, so its hints are blank
	# (H20: each button carries its own key hint, refreshed when the device changes).
	# B3 (bible 4.6, round 44): on the run's own route the window is "> ROUTE" with GRID VIEW and
	# Save & quit only (the choices are the map's stickers).
	var win := TerminalWindow.new(tr("ROUTE") if route_on_map(s) else tr("ROUTE // pick the next node"), Palette.CELL_ACID)
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
	zoom_btn.tooltip_text = UiTip.fold(tr("Zoom out to the whole City Grid.") if not _grid_zoomed else tr("Back to this run's route."))
	IconMark.attach(zoom_btn, StatIcon.MAP)
	win.body.add_child(zoom_btn)
	var quit_btn := _button(tr("Save & quit"), save_and_quit)
	quit_btn.name = "SaveQuit"
	quit_btn.tooltip_text = UiTip.fold(tr("Save the run and leave it; Continue picks it up here."))
	IconMark.attach(quit_btn, StatIcon.SAVE)
	win.body.add_child(quit_btn)
	if _grid_zoomed:
		win.body.add_child(MapLegend.new(RunManager.campaign.corporation_id))
	elif s.run.kind == "boss":
		pass  # ART-8 8w: the HQ run shows its compound (_mount_hq_run), not the transit
	else:
		# ART-7 3B (ART_BIBLE v2 4.6): the map area with the dossier pinned at its top left and
		# the legend strip along its foot; the decrypted node panel at the foot of the column.
		_build_route_frame(top, spacer, route_col)
	_set_panel(panel, false)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if _grid_zoomed:
		var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, CityLayout.threat_paths(RunManager.campaign, RunManager.corporation), s.run.site_id)
		_mount_route(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, 0.85, Vector2(0.4, 0.56), Vector2.INF)
		city_overlay.avoid_controls([win])  # map labels stay clear of the ROUTE window
	elif s.run.kind == "boss":
		_mount_hq_run()
	else:
		var r := route_graph()
		_mount_route(r["nodes"], r["edges"], CityMapOverlay.Look.ISOLATE, ROUTE_ZOOM, ROUTE_ANCHOR, Vector2.INF)
		city_overlay.here_at = r["entry"]
		city_overlay.ease_rings()  # ANIM-5: the "you are here" ring eases in
		city_overlay.avoid_controls([win, route_legend, dossier, node_panel])
		# Parity ROUTE-01 b: the district plates keep off the top bar (the map runs under it).
		var plate_bar: Array[Control] = [hud]
		(city_overlay as RouteOverlay).plate_avoid = plate_bar
		route_legend.minimum_size_changed.connect(func() -> void: place_route_legend.call_deferred())
		city_overlay.node_clicked.connect(func(id: StringName) -> void: map_view.node_clicked.emit(id))
		_wire_route_frame()
		place_route_legend.call_deferred()
		route_legend.get_parent().resized.connect(place_route_legend)
		if not background.city.rebuilt.is_connected(place_route_legend):
			background.city.rebuilt.connect(place_route_legend)
		# H24 S12: the route's nodes fitted into the map area beside the ROUTE column (at 1.6 a
		# node sat under the ROUTE window).
		_route_fits = 0
		_route_under_dossier = false
		if dossier != null and is_instance_valid(dossier):
			dossier.force_compact = false
			dossier.visible = true
		_fit_route_next_frame()
		spacer.resized.connect(_refit_route)
	_mount_route_camera(panel)
	route_target = null
	if route_on_map(s) and city_overlay is RouteOverlay and _route_area != null and is_instance_valid(_route_area):
		# B3 b (art director): the TARGET off the route's frame gets the red pencil edge arrow with
		# its word (the City Grid's device, TargetEdgeMarker); a click pans to it.
		route_target = TargetEdgeMarker.make(city_overlay)
		route_target.avoid.append(route_legend)
		# B3 c: the TARGET is off frame if any of it sits under the top bar or the key strip; while
		# the arrow shows, the TARGET's own circle hides.
		route_target.covers.append(hud)
		var route_ov := city_overlay as RouteOverlay
		route_target.showing_changed.connect(func(on: bool) -> void:
			if is_instance_valid(route_ov):
				route_ov.target_off = on)
		_route_area.add_child(route_target)
		if route_controls != null:
			route_target.pan_requested.connect(route_controls.centre_on)
	# ANIM-R4 H10: a fight's, a boss's and a raid's music are made ahead (a fight's first frame
	# built its loop).
	AudioDirector.prewarm_music(["combat", "boss", "raid"], RunManager.campaign.corporation_id)
	# ANIM-R2 R1 / R2: the next screen is a fight's arena, the Mainframe, an event or loot, all on
	# the default frame of this city's look: baked now, behind the route (after its own view).
	_prebake_backdrops.call_deferred()


## The ROUTE window's choice buttons for the choices the view shows (view_choices: ANIM-R4
## H11c, the new ones as soon as a move starts), into `row` (emptied first).
func _fill_route_choices(row: VBoxContainer) -> void:
	var s := RunManager.netrun
	# Hidden and freed in place: the button pressed (the move) may be one of them, mid-signal.
	for old in row.get_children():
		if old is CanvasItem:
			(old as CanvasItem).visible = false
		old.queue_free()
	var available := view_choices(s)
	_route_buttons.clear()
	var twins := choice_twins(s)
	var differs := choice_differences(s)
	var ahead_rows := {}
	# Parity ROUTE-04: on the run's own route (not GRID VIEW, not a boss run's compound) the
	# choices are focus stops on their map stickers, not list rows (RouteStopPlacer).
	var placer: RouteStopPlacer = null
	if route_on_map(s):
		placer = RouteStopPlacer.new(self)
		row.add_child(placer)
	for i in available.size():
		var node := s.run.map.get_node(available[i])
		# H21 #14: what the node is (word + icon), its index on every device (the map's
		# label carries the same index), Heat when entering changes it.
		var text := node_word(node)
		var heat := s.node_heat(available[i])
		if heat != 0:
			text += tr(" %s Heat") % TextDb.signed(heat)
		# H24 S12: what lies beyond each choice ("> Event · Shop"): two "Fight" buttons read
		# the same; where they lead is what differs (the enemy is rolled on entry).
		var ahead := ahead_words(s.run.map, node)
		if ahead != "":
			text += "  > %s" % ahead
		var id: StringName = available[i]
		# ANIM-R2 R12: a choice that is the same as an earlier one (kind, Heat and what lies
		# beyond: the enemy is rolled on entry) says so, on the button and on the map.
		if twins.has(id):
			text += "  " + tr(TWIN_WORDS) % (int(twins[id]) + 1)
		var b := _button(text, func() -> void: _request_node(id))
		b.name = "Node%d" % (i + 1)
		# ANIM-R3 B3: what this choice leads to that the others do not (reward and risk
		# icons: Elite, Shop, Event, Rack, Heat further on); twins lead to the same.
		var marks := differs.get(id, []) as Array
		if placer == null and not twins.has(id) and (not marks.is_empty() or heat != 0):  # B3: none on the map (bible 4.6)
			ahead_rows[i] = _ahead_row(i, marks, heat)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.set_meta(&"route_base", text)
		b.set_meta(&"route_index", i)
		if placer == null:
			IconMark.attach(b, node_icon(node), StatIcon.color_of(node_icon(node)))
			# H22 #14: the node's own map icon (the map's painter, its colour for a next node),
			# so the same node looks the same on the button and on the map.
			IconMark.attach_map(b, CityMapOverlay.route_kind(int(node["type"]), bool(node["elite"])), ROUTE_NEXT_COLOR)
		b.tooltip_text = UiTip.fold(route_tip(s, node, heat) + ((" " + tr(TWIN_TIP) % (int(twins[id]) + 1)) if twins.has(id) else ""))
		# ART-7 3B: the focused choice's decrypted file shows in the node panel.
		b.focus_entered.connect(show_node_panel.bind(id))
		_route_buttons.append(b)
		row.add_child(b)
		if placer != null:
			placer.add_stop(b, id, _focus_route_choice)
		if ahead_rows.has(i) and placer == null:
			# B3: on the map the ROUTE window holds GRID VIEW and Save & quit only (bible 4.6);
			# what only a choice reaches stays in its stop's tooltip and its node panel.
			var ahead_row: Control = ahead_rows[i]
			ahead_row.set_meta(&"route_choice", id)
			# Parity ROUTE-04: on the map the window shows only the lit choice's "then:" line.
			ahead_row.visible = placer == null
			row.add_child(ahead_row)
	_label_route_buttons()


## Parity ROUTE-04: a stop on the map took the focus or the pointer: its node's file in the
## panel and, in the ROUTE window, its own "then:" line (what only it reaches) alone.
func _focus_route_choice(id: StringName) -> void:
	show_node_panel(id)
	var row := _panel.find_child("RouteNodes", true, false) if _panel != null and is_instance_valid(_panel) else null
	if row == null:
		return
	for c in row.get_children():
		if c is Control and (c as Control).has_meta(&"route_choice"):
			(c as Control).visible = StringName(c.get_meta(&"route_choice")) == id


## Parity ROUTE-04: true when the route's choices are picked on the map (their stickers are
## the focus stops): the run's own route, not GRID VIEW nor a boss run's compound.
func route_on_map(s: NetrunSession) -> bool:
	return s != null and not _grid_zoomed and s.run.kind != "boss"


## ANIM-R2 R1 / R2: the default frame's bake at this scene's size and at the page's (a fight's
## arena fills the page), with the sizes it was drawn at lately (NeonCity.frame_sizes).
func _prebake_backdrops() -> void:
	if background == null or not is_inside_tree() or RunManager.campaign == null:
		return
	var sizes: Array[Vector2] = [size]
	if _panel_host != null and is_instance_valid(_panel_host):
		var inner := _panel_host.size
		var box := _panel_host.get_theme_stylebox(&"panel", UiTheme.CRT_GLASS_PANEL)
		if box != null:
			inner -= box.get_minimum_size()
		sizes.append(inner.floor())
	# ART-7 7w: the route shows the 3D city; these pages draw the 2D one (baked under it).
	background.city.prebake_frames(sizes, false, true)


## The route legend where it covers no route node (H22 #14). ART-7 3B: the strip has a row
## of its own at the map's foot; it is scaled down only when wider than that row.
func place_route_legend() -> void:
	if route_legend != null and is_instance_valid(route_legend) and city_overlay != null and is_instance_valid(city_overlay):
		_fit_route_strip()


## The route map's area (left of the ROUTE column; null when zoomed out) and the fit
## passes so far (H24 S12).
var _route_area: Control = null
var _route_fits: int = 0


## The route's nodes (icons and pips) fitted into the map area beside the ROUTE column,
## once the page's layout has settled (H24 S12: at 1.6 a node sat under the ROUTE window):
## the camera pans and zooms out as far as ROUTE_MIN_ZOOM, and checks again once the city
## has redrawn (at most ROUTE_FITS_MAX passes, then up to ROUTE_RESCUE_PASSES that only pan and
## zoom out while where the player is and the next choices are not in the free area).
func fit_route_map() -> void:
	if _grid_zoomed or _route_area == null or not is_instance_valid(_route_area) or not _route_area.is_inside_tree() \
			or city_overlay == null or not is_instance_valid(city_overlay):
		return
	var city := background.city
	if not city.camera_settled():
		_fit_route_after_redraw()
		return
	if _route_under_dossier:
		_place_dossier()
	var area := route_free_area()
	if area.size.x <= LegendSpot.MARGIN * 2.0 or area.size.y <= LegendSpot.MARGIN * 2.0:
		return
	# ANIM-R3 B8: a margin the size of a node's reach (its icon, label tab and pips) off the
	# screen's edge, and the street marker kept in frame with the nodes.
	var free := area.grow(-ROUTE_MARGIN * Settings.text_scale)
	var here := city_overlay.here_marker_rects()
	if _route_fits >= ROUTE_FITS_MAX:
		# Parity ROUTE-06: the passes are spent but where the player is and the next choices are
		# not in the free area (the last pass's big zoom step was never checked: Meridian at 1.6
		# under THE GRID's taller bar ended with YOU ARE HERE on the key strip). A rescue pass
		# frames them without zooming in (a pan and at most a zoom out, the step the estimate
		# gets right), checked once more.
		if _route_fits >= ROUTE_FITS_MAX + ROUTE_RESCUE_PASSES or route_frames(free):
			return
		var rescue := LegendSpot.fit_into(city_overlay, free, 1.0, minf(1.0, route_zoom_far() / city.scale.x), route_focus_ids(), here)
		if not rescue.is_empty():
			_apply_route_fit(rescue)
		return
	# B3 b (art director, round 44 `route_page.png`): the frame is the walked path, the current
	# options and one layer ahead, at ortho `route_ortho_near`..`route_ortho_far`; the TARGET need
	# not be in it (off frame it gets the red pencil edge arrow, TargetEdgeMarker). A long walked
	# path that does not fit at the far ortho gives way: then the current node, the options and the
	# layer ahead; then the current node and the options.
	var near := route_zoom_near()
	var far := route_zoom_far()
	var fit := {}
	var sets: Array = [route_frame_ids(true), route_frame_ids(false), route_focus_ids()]
	for i in sets.size():
		var ids: Array = sets[i]
		var extra: Array[Rect2] = here.duplicate()
		extra.append_array(hidden_rects(ids))
		var f := LegendSpot.fit_into(city_overlay, free, near / city.scale.x, 0.0, ids, extra)
		var zoom_after := city.scale.x * (float(f["zoom"]) if not f.is_empty() else 1.0)
		if zoom_after >= far * ROUTE_FAR_TOLERANCE or i == sets.size() - 1:
			if zoom_after < far * ROUTE_FAR_TOLERANCE:
				f = LegendSpot.fit_into(city_overlay, free, near / city.scale.x, far / city.scale.x, ids, extra)
			fit = f
			break
	if fit.is_empty():
		return
	_apply_route_fit(fit)


## One fit pass: the city's camera zoomed by `fit`'s zoom and panned so its "from" point lands on
## its "to" point (LegendSpot.fit_into), then measured again once the city has redrawn.
func _apply_route_fit(fit: Dictionary) -> void:
	var city := background.city
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
	_fit_route_after_redraw()


## B3 (review D14, round 44 `route_page.png`): the city zoom at which the route page shows
## CityConfig's `route_ortho_near` (the closest the fit goes) and `route_ortho_far` (the
## furthest it frames the whole drawn route at).
func route_zoom_near() -> float:
	return RaidZoomFit.zoom_of(CityView3D.CONFIG.route_ortho_near, size.x)


func route_zoom_far() -> float:
	return RaidZoomFit.zoom_of(CityView3D.CONFIG.route_ortho_far, size.x)


## B3: the route page's ortho now (BU across the page; tests and captures).
func route_ortho() -> float:
	return RaidZoomFit.ortho_of(background.city.scale.x, size.x)


## B3 b (round 44 `route_page.png`): the route nodes the page frames: the walked path (with
## `walked`), the current node, the options and the layer one step past them.
func route_frame_ids(walked: bool) -> Array:
	var s := RunManager.netrun
	var out: Array = []
	if s == null or city_overlay == null or not is_instance_valid(city_overlay):
		return out
	if walked:
		for id in s.run.visited:
			if not out.has(id):
				out.append(id)
	for id in route_focus_ids():
		if not out.has(id):
			out.append(id)
	var options := s.available_nodes()
	for e in city_overlay.edges:
		if options.has(e["a"]) and not out.has(e["b"]):
			out.append(e["b"])
	return out


## B3 b: screen rects (global px) of the nodes of `ids` the map hides (the layer ahead): the
## frame keeps room for them though they are not drawn.
func hidden_rects(ids: Array) -> Array[Rect2]:
	var out: Array[Rect2] = []
	if city_overlay == null or not is_instance_valid(city_overlay):
		return out
	var xf := city_overlay.get_global_transform()
	var k := xf.get_scale().x
	for n in city_overlay.nodes:
		if not ids.has(n["id"]) or city_overlay.marker_shown(n):
			continue
		var at := city_overlay.icon_pos(n)
		if at.x == INF:
			continue
		var r := city_overlay.icon_radius(n) * k
		out.append(Rect2(xf * at - Vector2(r, r), Vector2(r, r) * 2.0))
	return out


## B3 b: a frame set's zoom counts as within the far ortho down to this share of it (float noise).
const ROUTE_FAR_TOLERANCE := 0.995


## B3 b: the route page's off-frame TARGET arrow (null off the run's own route).
var route_target: TargetEdgeMarker = null


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


## ANIM-R6 B14: a choice the same as an earlier one says what that means (keys): "(same as
## 1)" puzzled a beginner (the same what?). The road ahead is the same; the enemy is picked
## on entry, so the two are one choice.
const TWIN_WORDS := "(same road as choice %d)" # TR
const TWIN_TIP := "Same kind, Heat and road ahead as choice %d: the enemy is picked when you enter, so either is the same pick." # TR


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
func _ahead_row(i: int, kinds: Array, heat: int) -> Control:
	# ANIM-R5 B9: a flow (an icon and its word stay together; a long row wraps in the window).
	var row := HFlowContainer.new()
	row.name = "Ahead%d" % (i + 1)
	row.mouse_filter = Control.MOUSE_FILTER_PASS
	row.add_theme_constant_override("h_separation", 4)
	var side := UiTheme.BASE_SIZE * Settings.text_scale * IconMark.SIZE_FACTOR
	var pad := Control.new()
	pad.custom_minimum_size.x = side
	pad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(pad)
	if heat != 0:
		var hm := IconMark.standalone(StatIcon.HEAT, side, StatIcon.color_of(StatIcon.HEAT))
		hm.name = "EnterHeat"
		hm.tooltip_text = UiTip.fold(tr("Entering it changes Heat by %s.") % TextDb.signed(heat))
		hm.mouse_filter = Control.MOUSE_FILTER_PASS
		row.add_child(hm)
		var hl := _label(TextDb.signed(heat))
		hl.name = "EnterHeatValue"
		row.add_child(hl)
	if not kinds.is_empty():
		var lead := _label(tr("then:"))
		lead.name = "AheadWord"
		row.add_child(lead)
		for k: StringName in kinds:
			# ANIM-R5 B9: the icon and its word ("then: [bag] Shop"): the bare icon lost a
			# beginner (was it a price? a lock?).
			var pair := HBoxContainer.new()
			pair.name = "Ahead_%s" % k
			pair.mouse_filter = Control.MOUSE_FILTER_PASS
			pair.add_theme_constant_override("separation", 2)
			pair.tooltip_text = UiTip.fold(tr("Further on: %s (only this way).") % tr(String(AHEAD_WORDS.get(k, ""))))
			var m := IconMark.standalone(k, side, StatIcon.color_of(k))
			m.name = "Icon"
			m.mouse_filter = Control.MOUSE_FILTER_IGNORE
			pair.add_child(m)
			var word := _label(tr(String(AHEAD_SHORT.get(k, ""))))
			word.name = "Word"
			word.add_theme_color_override("font_color", StatIcon.color_of(k))
			word.mouse_filter = Control.MOUSE_FILTER_IGNORE
			pair.add_child(word)
			row.add_child(pair)
	return row


## ANIM-R5 B9: the word beside each reward and risk icon under a route choice (keys: the
## route's own node words, so the button, the map and this row name a node alike).
const AHEAD_SHORT := {StatIcon.ELITE: ELITE_WORD, StatIcon.SHOP: "Shop", StatIcon.TERMINAL: "Event", # TR
	StatIcon.RACK: "Rack", StatIcon.HEAT: "Heat"} # TR


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
	var points := CityLayout.site_points(RunManager.corporation)
	if not points.has(s.run.site_id):
		points[s.run.site_id] = NeonCity.hq_of(RunManager.corporation.id)
	# S-MAPVIEW (designer 2026-10-05): the route's nodes sit along the link the run jacks along
	# (from the Cell's end to the run's Site), not scattered round the Site.
	var placed := RouteLinkLayout.place(CityView3D.CONFIG, map,
		RouteLinkLayout.link_of(CityView3D.CONFIG, RunManager.corporation, s.campaign, s.run.site_id, points))
	var spots: Dictionary = placed["nodes"]
	var available := view_choices(s)
	var type_glyph := {RC.InfilNodeType.ROUTER: "○", RC.InfilNodeType.TERMINAL: "▭", RC.InfilNodeType.MAINFRAME: "◇", RC.InfilNodeType.SERVER_RACK: "⬢"}
	var twins := choice_twins(s)
	# ART-7 3B: the TARGET (the final Rack) and what Heat has made harder (calm Heat, 4.3).
	var final_id: StringName = map.final_node_id()
	var heat_marks := route_heat_marks(s)
	var nodes: Array[Dictionary] = []
	for n in map.all_nodes():
		var at: Vector2 = spots[n["id"]]
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
			label += " " + tr(TWIN_WORDS) % (int(twins[n["id"]]) + 1)
		# ART-7 3B: the TARGET is named on the map (pencil) when it is not a choice yet.
		if label == "" and n["id"] == final_id and n["id"] != s.run.current_node_id:
			label = tr(RouteOverlay.TARGET_WORD)
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
			"visited": s.run.visited.has(n["id"]) and n["id"] != s.run.current_node_id,
			# ART-7 3B: option A's TARGET circle, the choice's number, and its calm-Heat mark
			# (only selectable nodes carry one, 4.3).
			"target": n["id"] == final_id, "number": idx + 1 if idx >= 0 else 0,
			"heat_chip": String(heat_marks.get(int(n["type"]), "")) if idx >= 0 else ""})
	var edges: Array[Dictionary] = []
	for n in map.all_nodes():
		for nxt in n["next"]:
			var live: bool = n["id"] == s.run.current_node_id and available.has(nxt)
			var walked: bool = _walked(s, n["id"]) and _walked(s, nxt)
			if walked:
				edges.append({"a": n["id"], "b": nxt, "color": Color(Palette.CELL_PINK, ROUTE_TRAIL_ALPHA), "width": ROUTE_TRAIL_WIDTH, "dashed": false, "flow": false, "trail": true,
					"state": RouteOverlay.STATE_WALKED})
				continue
			edges.append({"a": n["id"], "b": nxt, "color": Palette.CELL_ACID if live else Color(Palette.NET_CYAN, 0.45), "width": 3.0 if live else 1.6, "dashed": not live, "flow": live,
				"state": "live" if live else RouteOverlay.STATE_LATER})
	# ANIM-R3 B8: before the first node the Cell stands at the street, one step before the
	# route's first layer: the "you are here" marker is drawn there (it was drawn nowhere).
	var entry := Vector2.INF
	if s.run.current_node_id == &"":
		entry = placed["entry"]
	return {"nodes": nodes, "edges": edges, "entry": entry}


## Whether the run has walked node `id` (visited, or where it stands).
static func _walked(s: NetrunSession, id: StringName) -> bool:
	return s.run.visited.has(id) or id == s.run.current_node_id


# --- ART-7 3B: route presentation (ART_BIBLE v2 4.6; D13, D14) -------------------------------

## ART-7 3B (4.6 node backdrops): the room of the node the run stands on shows behind its
## event, shop and loot pages (the fight's arena is the combat screen's own); hidden on the
## map, in a fight, a raid and at the run's end.
func _update_node_backdrop() -> void:
	var s := RunManager.netrun
	var kind := ""
	if s != null and s.run.current_node_id != &"" and s.run.phase in [RunState.Phase.EVENT, RunState.Phase.SHOP, RunState.Phase.REWARD]:
		var node := s.run.current_node()
		if not node.is_empty():
			kind = CityMapOverlay.route_kind(int(node["type"]), bool(node["elite"]))
	if node_backdrop == null or not is_instance_valid(node_backdrop):
		if kind == "":
			return
		node_backdrop = NodeBackdrop.new()
		add_child(node_backdrop)
		move_child(node_backdrop, background.get_index() + 1)
	node_backdrop.show_room(kind, RunManager.campaign.corporation_id if RunManager.campaign != null else &"")


## The dossier's margin off the map area's corner and the gap the route keeps from it (px at
## text scale 1.0).
const DOSSIER_MARGIN := 10.0
## The Heat effect lines a choice carries (keys): fights under ENEMY_RESISTANCE, the shop
## under a SHOP_STOCK complication.
const HEAT_RESIST_WORDS := "HEAT: +%d RESISTANCE" # TR
const HEAT_SHOP_WORDS := "HEAT: SHOP STOCK %d" # TR
## The node panel's reward words (keys; numbers from the config).
const REWARD_CYCLES := "%d-%d Cycles, a card" # TR
const REWARD_FIRMWARE := "a Firmware chip to pick" # TR
const REWARD_FIRMWARE_MAYBE := "maybe a Firmware chip" # TR
const REWARD_RACK := "+%d Schematics banked, assets banked" # TR
const REWARD_DAEMON := "a Daemon to pick" # TR
const REWARD_OBJECTIVE := "the Site's objective" # TR
const REWARD_SHOP := "spend Cycles: cards, Firmware, slices" # TR
const REWARD_EVENT := "a choice, and its price" # TR
const PANEL_HEAT := "%s Heat on entry" # TR
## The node panel's title: the node's word and its layer.
const PANEL_TITLE := "%s // L%d" # TR


## The route view's frame: the dossier over the map area's top left, the legend strip in a
## row under the map area, the decrypted node panel at the foot of the ROUTE column.
func _build_route_frame(top: HBoxContainer, spacer: Control, route_col: VBoxContainer) -> void:
	top.size_flags_vertical = Control.SIZE_EXPAND_FILL
	route_col.size_flags_vertical = Control.SIZE_EXPAND_FILL
	# The map column: the map area over the strip's row.
	var left := VBoxContainer.new()
	left.name = "RouteMapColumn"
	left.mouse_filter = Control.MOUSE_FILTER_IGNORE
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.size_flags_vertical = Control.SIZE_EXPAND_FILL
	top.add_child(left)
	top.move_child(left, spacer.get_index())
	top.remove_child(spacer)
	left.add_child(spacer)
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	spacer.name = "RouteMapArea"
	_route_area = spacer
	# A plain row (no container): the strip never widens the map column at big text; it is
	# scaled down to the row instead (_fit_route_strip).
	var foot := Control.new()
	foot.name = "LegendRoom"
	foot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	foot.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.add_child(foot)
	# H23 S7: the route's own key, the node kinds this route has (not the campaign map's).
	route_legend = RouteLegend.new(RouteLegend.kinds_of(route_graph()["nodes"]), Palette.corp_color(RunManager.campaign.corporation_id))
	foot.add_child(route_legend)
	foot.custom_minimum_size.y = route_legend.get_combined_minimum_size().y
	# The dossier, pinned over the map's top left (corp paper).
	dossier = OperativeDossier.new()
	spacer.add_child(dossier)
	dossier.position = Vector2(DOSSIER_MARGIN, DOSSIER_MARGIN) * Settings.text_scale
	dossier.show_file(dossier_data())
	dossier.size = dossier.custom_minimum_size
	dossier.minimum_size_changed.connect(func() -> void:
		if is_instance_valid(dossier):
			dossier.size = dossier.custom_minimum_size)
	# The decrypted node panel at the foot of the column.
	var gap := Control.new()
	gap.name = "RouteColumnGap"
	gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	gap.size_flags_vertical = Control.SIZE_EXPAND_FILL
	route_col.add_child(gap)
	node_panel = RouteNodePanel.new()
	route_col.add_child(node_panel)
	var foot_gap := Control.new()
	foot_gap.name = "RouteColumnFoot"
	foot_gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	foot_gap.custom_minimum_size.y = DOSSIER_MARGIN * Settings.text_scale
	route_col.add_child(foot_gap)
	var first := view_choices(RunManager.netrun)
	show_node_panel(first[0] if not first.is_empty() else &"")


## Hooks the frame to the mounted map: the strip's hover shows every node (D13), the map's
## hover and the choices' focus show their node's file, Options' setting shows every node.
func _wire_route_frame() -> void:
	var overlay := city_overlay as RouteOverlay
	if overlay == null:
		return
	overlay.show_all = Settings.always_show_all_nodes
	overlay.heat_sweeps = route_heat_sweeps()
	route_legend.set_showing_all(overlay.show_all)
	route_legend.show_links_hovered.connect(_on_legend_hover)
	overlay.node_hovered.connect(func(id: StringName) -> void:
		if id != &"":
			show_node_panel(id))
	if not Settings.changed.is_connected(_on_route_settings):
		Settings.changed.connect(_on_route_settings)


## B3 (designer Q4): the strip's hover shows every run link as a hairline (nodes stay hidden).
func _on_legend_hover(on: bool) -> void:
	var overlay := city_overlay as RouteOverlay
	if overlay == null or not is_instance_valid(overlay):
		return
	overlay.show_links = on
	if route_legend != null and is_instance_valid(route_legend):
		route_legend.set_showing_links(on)


func _on_route_settings() -> void:
	var overlay := city_overlay as RouteOverlay
	if overlay == null or not is_instance_valid(overlay):
		return
	overlay.show_all = Settings.always_show_all_nodes
	if route_legend != null and is_instance_valid(route_legend):
		route_legend.set_showing_all(overlay.show_all)


## The strip at the map's foot, scaled down when wider than its row (big text).
func _fit_route_strip() -> void:
	var row := route_legend.get_parent() as Control
	if row == null:
		return
	var own := route_legend.get_combined_minimum_size()
	var k := minf(1.0, (row.size.x - LegendSpot.MARGIN * 2.0) / maxf(1.0, own.x)) if row.size.x > 0.0 else 1.0
	k = maxf(k, 0.1)
	route_legend.size = own
	route_legend.scale = Vector2(k, k)
	route_legend.position = Vector2(maxf(0.0, (row.size.x - own.x * k) * 0.5), 0.0)
	if not is_equal_approx(row.custom_minimum_size.y, ceilf(own.y * k)):
		row.custom_minimum_size.y = ceilf(own.y * k)
	_fit_node_panel()


## The node panel shows only when the ROUTE column has room for it under the window (big
## text on a small screen: the window's choices come first; the hover tips still say it all).
func _fit_node_panel() -> void:
	if node_panel == null or not is_instance_valid(node_panel) or not node_panel.is_inside_tree():
		return
	var col := node_panel.get_parent() as Control
	var win := col.find_child("RouteWindow", false, false) as Control if col != null else null
	var top := col.get_parent() as Control if col != null else null
	if win == null or top == null or top.size.y <= 0.0:
		return
	var need := win.get_combined_minimum_size().y + node_panel.get_combined_minimum_size().y + DOSSIER_MARGIN * Settings.text_scale * 3.0
	var fits := need <= top.size.y and node_panel.get_combined_minimum_size().x <= col.size.x + 1.0
	if node_panel.visible != (fits and not node_panel.data.is_empty()):
		node_panel.visible = fits and not node_panel.data.is_empty()


## ART-7 3B: the whole route needed the room under the dossier (this page).
var _route_under_dossier: bool = false


## With the route under it, the folded dossier takes the map area's corner (top left or
## bottom left) that covers least of where the player is and the next choices; their labels
## keep off it (avoid_controls).
func _place_dossier() -> void:
	if dossier == null or not is_instance_valid(dossier) or _route_area == null or city_overlay == null:
		return
	var m := DOSSIER_MARGIN * Settings.text_scale
	var focus := LegendSpot.node_rects(city_overlay, false, route_focus_ids())
	focus.append_array(city_overlay.here_marker_rects())
	var area := _route_area.get_global_rect()
	var best := Vector2(m, m)
	var best_hits := INF
	for at in [Vector2(m, m), Vector2(m, area.size.y - dossier.size.y - m)]:
		var hits := LegendSpot.covered(Rect2(area.position + at, dossier.size), focus)
		if hits < best_hits:
			best_hits = hits
			best = at
	dossier.position = best
	# Where the player is and the next choices come first: a file that would cover them in
	# both corners steps aside (the top bar keeps HP and Heat).
	dossier.visible = best_hits <= 0.0


## The map area the route is fitted into (screen px): the map area right of the dossier
## (the whole area once the route needed it).
func route_free_area() -> Rect2:
	var area := _route_area.get_global_rect().intersection(get_global_rect())
	if not _route_under_dossier and dossier != null and is_instance_valid(dossier) and dossier.is_visible_in_tree():
		var right := dossier.get_global_rect().end.x + DOSSIER_MARGIN * Settings.text_scale
		if right < area.end.x - LegendSpot.MARGIN * 4.0:
			area = Rect2(Vector2(right, area.position.y), Vector2(area.end.x - right, area.size.y))
	return area


## What the dossier shows: the run's operative as the target corporation's file on them.
func dossier_data() -> Dictionary:
	var s := RunManager.netrun
	var c := RunManager.campaign
	if s == null or c == null:
		return {}
	var op := s.run.operative
	var cls := RunManager.lookup().get_content(op.class_id) as ClassData
	var corp := RunManager.corporation
	var wheel: Array[String] = []
	for id in op.slot_slice_ids:
		var sd := RunManager.lookup().get_content(id) as SliceData
		if sd != null:
			wheel.append(tr(String(Palette.SLICE_NAMES.get(sd.slice_type, "?"))))
	# The rank's Hub Core upgrade, else the class wheel's own Hub.
	var hub: HubCoreData = null
	if cls != null:
		var hub_id := op.hub_id(cls)
		hub = RunManager.lookup().get_content(hub_id) as HubCoreData if hub_id != &"" else (cls.starting_wheel.hub if cls.starting_wheel != null else null)
	var station: Array[String] = []
	if cls != null:
		for te in cls.station_bonus:
			if te != null:
				station.append(Codex.describe_triggered(te))
	var ram := cls.max_ram if cls != null else 0
	ram = int(s.run.combat_overrides.get("max_ram", ram))
	return {"corp": TextDb.t(corp, "display_name") if corp != null else "", "corp_color": Palette.corp_color(c.corporation_id),
		"subject": op.name, "class_word": TextDb.t(cls, "display_name") if cls != null else "", "class_id": op.class_id,
		"operative_id": op.id, "rank": op.rank, "hp": op.hp, "max_hp": op.max_hp, "ram": ram, "wheel": wheel,
		"hub": TextDb.t(hub, "display_name") if hub != null else "", "deck": op.deck.size(), "station": station}


## Calm Heat (4.3): the effect line each node type Heat has made harder carries (type ->
## translated words): fights under the Heat's enemy resistance, the shop under a stock
## complication. Only the current rules' effects (GDD 4.3); none = {}.
func route_heat_marks(s: NetrunSession) -> Dictionary:
	var out := {}
	var resist := 0
	for m in HeatRules.active_modifiers(s.campaign, s.config):
		if m.type == RC.RuleModifierType.ENEMY_RESISTANCE:
			resist += int(m.value)
	if resist > 0:
		var words := tr(HEAT_RESIST_WORDS) % resist
		out[RC.InfilNodeType.ROUTER] = words
		out[RC.InfilNodeType.SERVER_RACK] = words
	var shop := int(s.run.combat_overrides.get("shop_stock_delta", 0))
	if shop < 0:
		out[RC.InfilNodeType.MAINFRAME] = tr(HEAT_SHOP_WORDS) % shop
	return out


## Calm Heat (4.3): the city-wide searchlights sweep from the first Heat band up.
func route_heat_sweeps() -> bool:
	var s := RunManager.netrun
	if s == null:
		return false
	var bands := HeatRules.band_levels(s.campaign, s.config)
	return HeatPoster.band_of(s.campaign.heat, bands) > 0


## Shows node `id`'s decrypted file in the panel (D14: every node the map shows is decrypted
## under the current rules).
func show_node_panel(id: StringName) -> void:
	if node_panel == null or not is_instance_valid(node_panel):
		return
	node_panel.show_node(id, node_panel_data(id))
	_fit_node_panel()


## The node panel's words for node `id` from the rules and the config ({} for none).
func node_panel_data(id: StringName) -> Dictionary:
	var s := RunManager.netrun
	if s == null or id == &"":
		return {}
	var node := s.run.map.get_node(id)
	if node.is_empty():
		return {}
	var cfg := s.config
	var rewards: Array[String] = []
	var scale := s.reward_scale()
	match int(node["type"]):
		RC.InfilNodeType.ROUTER:
			var pay: Vector2i = cfg.cycles_elite_range if _is_elite(node) else cfg.cycles_router_range
			rewards.append(tr(REWARD_CYCLES) % [roundi(pay.x * scale), roundi(pay.y * scale)])
			rewards.append(tr(REWARD_FIRMWARE) if _is_elite(node) else tr(REWARD_FIRMWARE_MAYBE))
		RC.InfilNodeType.SERVER_RACK:
			var ti := clampi(s.run.tier - 1, 0, cfg.rack_schematics_by_tier.size() - 1)
			rewards.append(tr(REWARD_RACK) % cfg.rack_schematics_by_tier[ti])
			rewards.append(tr(REWARD_OBJECTIVE) if id == s.run.map.final_node_id() else tr(REWARD_DAEMON))
		RC.InfilNodeType.MAINFRAME:
			rewards.append(tr(REWARD_SHOP))
		RC.InfilNodeType.TERMINAL:
			rewards.append(tr(REWARD_EVENT))
	var heat := s.node_heat(id)
	var heat_words := tr(PANEL_HEAT) % TextDb.signed(heat) if heat != 0 else ""
	var mark := String(route_heat_marks(s).get(int(node["type"]), ""))
	if mark != "":
		heat_words = mark if heat_words == "" else "%s; %s" % [heat_words, mark]
	return {"title": tr(PANEL_TITLE) % [node_word(node), int(node["layer"])], "tier": s.run.tier,
		"type": tr(String(RouteLegend.MEANINGS.get(CityMapOverlay.route_kind(int(node["type"]), bool(node["elite"])), node_word(node)))),
		"rewards": rewards, "heat": heat_words, "corp_color": Palette.corp_color(s.campaign.corporation_id)}


func _mount_route(nodes: Array[Dictionary], edges: Array[Dictionary], look: int, zoom: float, anchor: Vector2, focus: Vector2, raid_view: bool = false) -> void:
	_clear_route()
	var city := background.city
	# ART-7 3B: the run's own route draws in the v2 netrun look (RouteOverlay); GRID VIEW keeps
	# the campaign map's overlay, and so does a raid page (`raid_view`, parity RAID-13: the HQ's
	# raid view, its sockets and pencil routes).
	city_overlay = CityMapOverlay.new(city) if _grid_zoomed or raid_view else RouteOverlay.new(city)
	if raid_view:
		# B3 (review D5, the clutter rule): no node tags on a raid map (status on the node, the
		# name in its tooltip).
		city_overlay.tag_rule = CityMapOverlay.TagRule.LIT
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


## ART-7 7w: the player's camera on the route page (wheel / + - zoom about the cursor, drag,
## WASD and the right stick pan: 5a's CityGridControls), so the route can be looked at
## close up (the CLOSE car tier below ortho 150); null off the 3D city.
var route_controls: CityGridControls = null


## ART-7 7w: puts the backdrop on the unified 3D city for the route page (`on`: the NETRUN
## band; GRID VIEW holds the Grid's band) or back on the 2D city, with 5c's city motion on
## the 3D city (CityViewMotion: cars by zoom, sky lanes, billboards, the light spill).
func use_route_city(on: bool, band: int = -1) -> void:
	if background == null:
		return
	# Parity RAID-13: a raid page asks for the RAID band (`band`); the route NETRUN, GRID VIEW GRID.
	background.use_city3d(on, band if band >= 0 else (CityLod.Band.GRID if _grid_zoomed else CityLod.Band.NETRUN))
	var view := background.city.view3d
	if on and view != null and not view.has_node(ROUTE_MOTION_NAME):
		var home := NeonCity.hq_of(&"rebel_cell") + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
		var motion := CityViewMotion.make(view, null, home)
		motion.name = ROUTE_MOTION_NAME
		view.add_child(motion)


const ROUTE_MOTION_NAME := "CityMotion"


## ART-7 7w: a frame of the route page's player camera: zoom `zoom`, grid point `focus` at
## screen fraction `anchor` (the route fits move the same city).
func _frame_route_city(zoom: float, focus: Vector2, anchor: Vector2) -> void:
	var city := background.city
	city.scale = Vector2(zoom, zoom)
	city.offset_left = 0
	city.offset_top = 0
	city.offset_right = size.x / zoom - size.x
	city.offset_bottom = size.y / zoom - size.y
	city.focus_grid = focus
	city.focus_anchor = anchor
	city.refresh()
	city.update_camera()


## ART-7 7w: hooks the player's camera to the route map on the 3D city.
func _mount_route_camera(page: Control) -> void:
	route_controls = null
	if not background.city3d or city_overlay == null:
		return
	route_controls = CityGridControls.new(background.city, self, _frame_route_city)
	page.add_child(route_controls)
	route_controls.attach(city_overlay, null)


func _clear_route() -> void:
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.queue_free()
	city_overlay = null
	if hq_run_view != null and is_instance_valid(hq_run_view):
		hq_run_view.queue_free()
	hq_run_view = null
	close_gate()
	var city := background.city
	if city.focus_grid != Vector2.INF or city.scale != Vector2.ONE:
		city.focus_grid = Vector2.INF
		city.scale = Vector2.ONE
		city.offset_right = 0
		city.offset_bottom = 0
		city.refresh()


## ART-8 8w: the HQ run's page: the corporation's compound on the city (HqRunView, its own
## CityView3D) with the run's nodes, instead of the transit route.
func _mount_hq_run() -> void:
	var s := RunManager.netrun
	hq_run_view = HqRunView.new()
	background.add_child(hq_run_view)
	hq_run_view.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hq_run_view.show_run(RunManager.campaign.corporation_id, s.run.map, s.run.current_node_id, s.run.visited, s.available_nodes(), server_label())
	hq_run_view.node_pressed.connect(_request_node)


## ART-8 8w: the Central Server's name on the HQ run's page and gate (the Site's display
## name, upper case).
func server_label() -> String:
	var s := RunManager.netrun
	var site := CampaignRules.site_data(RunManager.corporation, s.run.site_id) if s != null else null
	return TextDb.t(site, "display_name").to_upper() if site != null else ""


## ART-8 8w: a press on a node (map or ROUTE button). The Central Server's breach opens its
## gate first (bible 4.9); BREACH there enters the node. Every other node is entered at once.
## (enter_node itself is unchanged: tests and tools still reach the fight directly.)
func _request_node(id: StringName) -> void:
	var s := RunManager.netrun
	if s != null and s.run.kind == "boss" and gate == null and s.available_nodes().has(id):
		open_gate(id)
		return
	enter_node(id)


## ART-8 8w: shows the Central Server's gate for node `id` (the breach preview's boss).
func open_gate(id: StringName) -> void:
	var s := RunManager.netrun
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var held: Array[int] = []
	for ex in c.exploits:
		held.append(int(ex))
	gate = CentralServerGate.new()
	var site := CampaignRules.site_data(corp, s.run.site_id)
	gate.setup(c.corporation_id, TextDb.t(corp, "display_name"), server_label(), site.tier if site != null else s.run.tier,
		held, RunManager.config().min_exploits_for_breach, s.breach_preview(), RunManager.lookup())
	gate.breach_pressed.connect(func() -> void:
		close_gate()
		enter_node(id))
	gate.back_pressed.connect(close_gate.bind(true))
	add_child(gate)


## ART-8 8w: closes the gate (BREACH pressed, or back to the compound: `refocus` puts the
## focus back on the ROUTE window's choice).
func close_gate(refocus: bool = false) -> void:
	if gate != null and is_instance_valid(gate):
		gate.queue_free()
	gate = null
	if refocus and not _route_buttons.is_empty() and is_instance_valid(_route_buttons[0]) and _route_buttons[0].is_inside_tree():
		_route_buttons[0].grab_focus()


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
	var legend := MapLegend.pin_key_line(spacer, c.corporation_id)  # B3: the key strip, folded to MAP KEY
	_fight_parts = [spacer, legend]
	var side := VBoxContainer.new()
	side.add_theme_constant_override("separation", 12)
	box.add_child(side)
	var feed := TerminalWindow.new(tr("RAID FEED // LIVE"), Palette.corp_color(c.corporation_id))
	side.add_child(feed)
	playout = RaidPlayoutPanel.new(null, RaidPlayoutPanel.LOG_SIZE)
	feed.body.add_child(playout)
	var cont := _icon_button(tr("Continue"), _leave_raid_playout, StatIcon.CONTINUE)
	cont.disabled = true
	playout.finished.connect(func() -> void:
		cont.disabled = false
		# ANIM-R5 P7: the verdict is in: the network's packets stop.
		if city_overlay != null and is_instance_valid(city_overlay):
			city_overlay.packets = false
		# ANIM-R5 P2: the raid's Heat reaches the city's look with its tint.
		_creep_heat = -1
		background.corp_creep = creep_of(RunManager.campaign.heat)
		background.city.release_influence())
	# ANIM-5: Skip goes straight on (the raid's result).
	playout.skipped.connect(_leave_raid_playout)
	side.add_child(cont)
	if before != null and not _instant_playout():
		_creep_heat = before.heat
	_set_panel(box, false, RAID_PLAYOUT_SCREEN)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var pre := before if before != null else c
	# Parity RAID-13: the raid view's map (the network as it stood before the raid, the Sites the
	# raid takes) on the 3D city, the plan in pencil while it plays (the HQ's playout).
	var g := raid_map_graph({}, pre)
	_mount_route(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, raid_min_zoom(), PLAYOUT_ANCHOR, Vector2.INF, true)
	_mount_raid_routes(RaidMapNodes.route_paths(events))
	# ANIM-R5 P6: labels and home's banner keep off the key too.
	city_overlay.avoid_controls([side, legend])
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


## ANIM-R5 P10: Continue (or Skip) after the interlude's raid: the fight camera's frame is let
## go before the next page mounts (the route showed ~3 frames at the raid's zoom, the rig
## still holding it, then eased out): the route starts at its own framing.
func _leave_raid_playout() -> void:
	background.settle_camera()
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
	return background.frame_points(pts, hq_script.fight_area(_fight_parts), raid_zoom(), raid_min_zoom())


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


## ANIM-R6 B3: the frame's wait is a one-shot connection to a method of this scene (an await
## resumed on the freed scene): freed, the connection goes with it; out of the tree, the
## framing stops.
func _frame_raid_map() -> void:
	_raid_map_framing = true
	if not is_inside_tree():
		_raid_map_framing = false
		return
	if not get_tree().process_frame.is_connected(_frame_raid_map_now):
		get_tree().process_frame.connect(_frame_raid_map_now, CONNECT_ONE_SHOT)


func _frame_raid_map_now() -> void:
	_raid_map_framing = false
	# ANIM-R5 B10: the scene may have left the tree (a jack out, the scene freed) while it
	# waited a frame: nothing to frame then.
	if not is_inside_tree() or background == null or not is_instance_valid(background):
		return
	if _raid_map_area == null or not is_instance_valid(_raid_map_area) or city_overlay == null or not is_instance_valid(city_overlay):
		return
	background.frame_points(raid_frame_points(), _raid_map_area.get_global_rect().grow(-LegendSpot.MARGIN * 2.0), raid_zoom(), raid_min_zoom())
	background.settle_camera()


## ANIM-R5 P5: what the interlude's map frames: home (CORE) and the raid's entry Sites, the
## road the raid takes (it fitted the whole Grid, which at its least zoom left CORE under the
## RAID window).
func raid_frame_points() -> PackedVector2Array:
	var pts := PackedVector2Array()
	var s := RunManager.netrun
	if s == null or city_overlay == null or not is_instance_valid(city_overlay):
		return pts
	var c := s.campaign
	var want := {c.grid.home_site_id: true}
	for e in CampaignRules.raid_entries(c, RunManager.corporation, s.raid_pending()):
		want[e] = true
	for n in city_overlay.nodes:
		if want.has(n["id"]):
			pts.append(Vector2(n["at"]) + Vector2(0.5, 0.5))
	if pts.is_empty():
		for n in city_overlay.nodes:
			pts.append(Vector2(n["at"]) + Vector2(0.5, 0.5))
	return pts




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
	# ANIM-R6 B4: the city's default frame bakes behind the fight (a fight can be the first page
	# of a session: a resumed run, a capture), so the page after it, the run's end after a
	# flatline included, never waits for the session's first bake; a flatline's own look is
	# asked for again when the fight is lost (`_on_combat_state_changed`).
	fight_prebake = prebake_run_end()
	combat_scene = scene
	scene.attach_netrun(s)
	scene.engine.state_changed.connect(_on_combat_state_changed)
	if scene.has_signal(&"continue_requested"):
		scene.connect(&"continue_requested", _leave_fight)
	if scene.has_signal(&"shown_hp_changed"):
		scene.connect(&"shown_hp_changed", _on_combat_hp_shown)


## HEAT-ALL (Q2): the Heat terminal the gauge dropped, read-only in a run (null when closed).
var heat_terminal: HeatTerminal = null


## HEAT-ALL (Q1 / Q2): the HEAT gauge pressed: the Heat terminal drops from it read-only (no
## SCRUB in a run: Scrub Heat is at the HQ), or folds back when it is open.
func toggle_heat_terminal() -> void:
	if heat_terminal != null and is_instance_valid(heat_terminal):
		close_heat_terminal()
		return
	if RunManager.campaign == null:
		return
	heat_terminal = HeatTerminal.new(RunManager.campaign, RunManager.config(), true)
	heat_terminal.closed.connect(close_heat_terminal)
	add_child(heat_terminal)
	TextDb.shown_as_given(heat_terminal)
	heat_terminal.drop_under(hud.heat_gauge.get_global_rect(), get_global_rect())


## HEAT-ALL: folds the Heat terminal away; focus goes back to the gauge.
func close_heat_terminal(refocus: bool = true) -> void:
	if heat_terminal != null and is_instance_valid(heat_terminal):
		heat_terminal.queue_free()
		if refocus and hud.heat_gauge.is_visible_in_tree() and hud.heat_gauge.focus_mode != Control.FOCUS_NONE:
			hud.heat_gauge.grab_focus.call_deferred()
	heat_terminal = null


## What the Heat number means now: the next threshold and the rules in force.
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
		mods.append(HeatTerminal.modifier_text(m))
	lines.append(tr("In force: %s.") % (", ".join(mods) if not mods.is_empty() else tr("nothing yet")))
	return "\n".join(lines)


## ANIM-R6 A5 (combat, a minimal change here): a SEND IT replay landed its turn: the top bar's
## HP follows the fight (never before an outcome that still waits for its beat).
func _on_combat_hp_shown() -> void:
	if combat_scene != null and combat_scene.has_method(&"outcome_pending") and bool(combat_scene.call(&"outcome_pending")):
		return
	_refresh_status()


func _on_combat_state_changed(state: CombatState, _events: Array[Dictionary]) -> void:
	# ANIM-R5 combat 1: a SEND IT that ends the fight keeps the top bar (HP, CYCLES, Heat...)
	# and the run's report (its DISPATCH line) until the replay lands VICTORY / DEFEAT.
	var held := state.is_over() and combat_scene != null and combat_scene.has_method(&"outcome_pending") and bool(combat_scene.call(&"outcome_pending"))
	if not held:
		_refresh_status()
	if state.is_over():
		RunManager.after_step()
		# ANIM-R6 B4: a lost fight's run end is known now (the rules ran at SEND IT), seconds
		# before its page: its look (the flatline's Heat) bakes behind the replay and the hold
		# (the page opened on the silhouette, 24+ frames).
		if RunManager.netrun != null and RunManager.netrun.run.is_over():
			run_end_prebake = prebake_run_end()
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
		if state.outcome == CombatState.Outcome.DEFEAT and combat_scene != null and combat_scene.has_method(&"show_continue"):
			# ANIM-R6 A6 (combat, a minimal change here): a lost fight stays until JACK OUT is
			# pressed (DEFEAT and its stamp "stay until JACK OUT"; the hold left it ~0.7 s).
			return
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
## ANIM-R6 B3: every wait is a one-shot frame connection to this scene's own methods (it
## awaited frames and resumed on a freed scene); ANIM-R6 B2: the fight is set one hit from its
## end by DemoSetup (the view wrote the live fight's HP itself).
func _demo_combat_end(kind: String) -> void:
	_when_ready(func() -> bool: return combat_scene != null and is_instance_valid(combat_scene) and not PageTransition.running(self),
		_after_frames_here.bind(DEMO_SETTLE_FRAMES, _demo_combat_end_now.bind(kind)))


## ANIM-R6 B3: calls `step` once `ready_now` is true, checking once a frame through a one-shot
## connection to this scene (gone with the scene; stops when it leaves the tree).
func _when_ready(ready_now: Callable, step: Callable) -> void:
	if not is_inside_tree():
		return
	if ready_now.call():
		step.call()
		return
	get_tree().process_frame.connect(_when_ready.bind(ready_now, step), CONNECT_ONE_SHOT)


## ANIM-R6 B3: calls `step` `n` frames from now while the scene stays in the tree (one-shot
## connections to this scene: freed mid-wait, nothing resumes).
func _after_frames_here(n: int, step: Callable) -> void:
	if not is_inside_tree():
		return
	if n <= 0:
		step.call()
		return
	get_tree().process_frame.connect(_after_frames_here.bind(n - 1, step), CONNECT_ONE_SHOT)


func _demo_combat_end_now(kind: String) -> void:
	var scene := combat_scene
	if scene == null or not is_instance_valid(scene):
		return
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
	DemoSetup.one_hit_from_end(st, kind == "win")
	for k in DEMO_END_TRIES:
		if eng.preview_end_turn().state.outcome == want:
			break
		if k % DEMO_END_NUDGES == DEMO_END_NUDGES - 1:
			# Nudges didn't do it: a turn passes (at once) and the fight is set up again.
			scene.call(&"end_turn")
			scene.call(&"skip_motion")
			st = eng.state()
			DemoSetup.one_hit_from_end(st, kind == "win")
		else:
			scene.call(&"nudge_wheel", &"player" if kind == "win" or k % 2 == 0 else st.enemies[0].id, 1)
	scene.call(&"skip_motion")
	scene.call(&"_refresh", eng.state())
	_after_frames_here(MotionDemo.START_FRAME, _demo_combat_send.bind(kind))


func _demo_combat_send(kind: String) -> void:
	if combat_scene == null or not is_instance_valid(combat_scene):
		return
	print("MotionDemo: r5 combat SEND IT (%s) on frame %d" % [kind, Engine.get_frames_drawn()])
	combat_scene.call(&"end_turn")


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


# ==== ART-9 4A: loot (owner 4A) ====
## ART-9 4A (ART_BIBLE v2 §4.11 Reward LOCKED A; round 31 `reward_screen`, round 32
## `reward_screen_v2`): the payout. A title sticker names what paid out (FIGHT WON, ELITE DOWN,
## RACK BREACHED), a CRT strip under it the loot ("LOOT // FIGHT WON // pick a card"), the
## PAYOUT terminal top right (the run's Cycles and HP). The offers sit on a loot sheet (sticker
## liner with kiss-cut slots); a Firmware drop shows its socket list and your spinner in a
## FIRMWARE DROP terminal; a card offer shows the DECK counter with a pencil "+1 = N" to it. A
## pick peels off the sheet and flies to the deck (ANIM-6 `loot_pick`), Skip is a sticker.
func _show_reward() -> void:
	var s := RunManager.netrun
	var offer := s.current_reward()
	var ts := Settings.text_scale
	var os := minf(ts, ShopItem.OBJECT_MAX_SCALE)
	var kind_word := tr(String(LOOT_WORDS.get(String(offer["kind"]), String(offer["kind"]))))
	var source := tr(loot_source(s))
	var n: int = offer["options"].size()
	var page := VBoxContainer.new()
	page.name = "LootPage"
	page.add_theme_constant_override("separation", roundi(10 * minf(ts, ShopItem.OBJECT_MAX_SCALE)))
	# Top: the title sticker and the loot strip; the payout terminal on the right.
	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 18)
	page.add_child(top)
	# Big words (LOOT_SIDE_FROM up): the title and the strip share a row (the sheet takes the height).
	var compact := ts >= LOOT_SIDE_FROM
	var head: BoxContainer = HBoxContainer.new() if compact else VBoxContainer.new()
	head.alignment = BoxContainer.ALIGNMENT_BEGIN
	head.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(head)
	var title := HoloSticker.word(source, VinylSticker.Fill.YELLOW, os, LOOT_TITLE_PX)
	title.name = "LootTitle"
	title.focus_mode = Control.FOCUS_NONE
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	head.add_child(title)
	# big words: the title's words lead the strip instead (the sheet takes the height)
	title.visible = not compact
	# ANIM-R6 B10: the window names what paid out (it said RACK BREACHED after every fight).
	# Parity LOOT-02 (round 32 `reward_screen_v2`): the strip says where the loot came from on
	# the run: "LOOT // NETRUN: <SITE> // <NODE> n OF N".
	var win := _crt_one_line(CrtWindow.new(loot_strip(s, compact, source), Palette.NET_CYAN).with_kind(CrtWindow.kind_for(Palette.NET_CYAN), Palette.NET_CYAN))
	win.name = "LootWindow"
	win.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	win.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	win.body.visible = false  # a strip: its header line only
	head.add_child(win)
	var payout := _crt_one_line(CrtWindow.new(tr("PAYOUT"), Palette.NET_CYAN).with_kind(CrtWindow.kind_for(Palette.NET_CYAN), Palette.NET_CYAN))
	payout.name = "Payout"
	payout.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var op := s.run.operative
	# Parity LOOT-03: what this payout paid (the session's own events: preview equals result),
	# the wallet before and after, HP, and the Heat it added.
	var pay := payout_of(s)
	# big words: the lines stand side by side (one row: the sheet takes the height)
	var pay_rows: BoxContainer = payout.body
	if compact:
		pay_rows = HBoxContainer.new()
		pay_rows.add_theme_constant_override("separation", roundi(UiTheme.SP_L * ts))
		payout.body.add_child(pay_rows)
	var cyc_row := _payout_row(TextDb.mark("CYCLES"), TextDb.signed(int(pay["cycles"])) if bool(pay["paid"]) else str(s.run.cycles), Palette.CELL_ACID)
	cyc_row.name = "PayoutCycles"
	pay_rows.add_child(cyc_row)
	# big words: the wallet line goes (the top bar's CYCLES says it) so SKIP keeps the screen
	if bool(pay["paid"]) and ts < LOOT_SIDE_FROM:
		var wallet := _label(tr(PAYOUT_WALLET) % [s.run.cycles - int(pay["cycles"]), s.run.cycles])
		wallet.name = "PayoutWallet"
		wallet.add_theme_font_override(&"font", Palette.mono())
		wallet.add_theme_color_override(&"font_color", Palette.TEXT_MID)
		payout.body.add_child(wallet)
	pay_rows.add_child(_payout_row(TextDb.mark("HP"), "%d/%d" % [_shown_operative_hp(op.hp), op.max_hp], Palette.CELL_PINK))
	var heat_row := _payout_row(TextDb.mark("HEAT"), TextDb.signed(int(pay["heat"])), Palette.HARM if int(pay["heat"]) > 0 else Palette.TEXT_MID)
	heat_row.name = "PayoutHeat"
	pay_rows.add_child(heat_row)
	heat_row.visible = ts < LOOT_SIDE_FROM or int(pay["heat"]) != 0
	# The loot sheet; beside it PAYOUT, a Firmware drop's terminal, the deck and Skip.
	var sheet := LootSheet.new(tr("LOOT SHEET // %s // PICK 1 OF %d") % [source, n], "", tr(LOOT_FOOT) % [kind_word.to_upper()], os)
	var stickers := sheet.row
	var room := LOOT_ROW_MAX - LOOT_SIDE_W * os
	var slot_option: SpinnerMini = null
	var mini: SpinnerMini = null
	var loot_row := HBoxContainer.new()
	loot_row.name = "LootRow"
	loot_row.alignment = BoxContainer.ALIGNMENT_CENTER
	loot_row.add_theme_constant_override("separation", 14)
	# Parity LOOT-03 (round 32 `reward_screen_v2`): the page is the screen: title and strip top
	# left, PAYOUT top right, the sheet (and a Firmware drop beside it) in the middle, the DECK
	# counter bottom left and SKIP under the sheet.
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	page.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var mid := CenterContainer.new()
	mid.name = "LootMiddle"
	mid.size_flags_vertical = Control.SIZE_EXPAND_FILL
	page.add_child(mid)
	mid.add_child(loot_row)
	loot_row.add_child(sheet)
	var side := VBoxContainer.new()
	side.name = "LootSide"
	side.add_theme_constant_override("separation", roundi(12 * os))
	loot_row.add_child(side)
	# Big words (LOOT_SIDE_FROM up): the sheet takes the height, so the DECK counter and SKIP stand
	# in the column beside it (as ART-9 4A placed them) and stay on the screen.
	var foot := HBoxContainer.new()
	foot.name = "LootFoot"
	foot.add_theme_constant_override("separation", roundi(LOOT_GAP * os))
	if not compact:
		page.add_child(foot)
	var foot_left := HBoxContainer.new()
	foot_left.name = "LootFootLeft"
	foot_left.add_theme_constant_override("separation", 12)
	foot_left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	(side if compact else foot).add_child(foot_left)
	var foot_right := Control.new()
	foot_right.mouse_filter = Control.MOUSE_FILTER_IGNORE
	foot_right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(payout)
	if offer["kind"] == "firmware":
		var drop := _crt_one_line(CrtWindow.new(tr("FIRMWARE DROP"), Palette.CELL_ACID).with_kind(CrtWindow.kind_for(Palette.CELL_ACID), Palette.CELL_ACID))
		drop.name = "FirmwareDrop"
		side.add_child(drop)
		# ANIM-4b: a Firmware chip drags onto a slot of the spinner shown beside the offer.
		# Parity SHOP-06: the spinner is also the socket choice (it replaced the dropdown);
		# ANIM-R6 B8: the Mainframe's words name it ("Chips go into:").
		mini = _spinner_mini()
		mini.make_pickable(0)
		mini.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		drop.body.add_child(_socket_row(mini, tr(LOOT_SOCKET_TIP) + " " + drag_tip("loot_socket")))
		drop.body.add_child(mini)
		slot_option = mini
	# ANIM-R2 E8: the gap between stickers keeps room for their rest tilt (it grows with the card).
	var tilt := sin(deg_to_rad(ZineCard.REST_TILT_MAX))
	var ls := clampf(minf(ts, (room - LOOT_GAP * (n - 1)) / maxf(1.0, n * (LOOT_CARD.x + LOOT_CARD.y * tilt))), 1.0, Settings.TEXT_SCALE_MAX)
	stickers.add_theme_constant_override("separation", roundi(LOOT_GAP + LOOT_CARD.y * ls * tilt))
	for i in n:
		var id := StringName(String(offer["options"][i]))
		var res := s.lookup.get_content(id)
		var cost := int(res.get("ram_cost")) if res is CardData else -1
		var sticker := ZineCard.new(TextDb.t(res, "display_name"), cost, TextDb.t(res, "description"), i).scaled(ls)
		if res is CardData:
			sticker.with_card(res as CardData)
		elif res is FirmwareData or res is DaemonData:
			# S-CARDFACE: the one card face; its art panel shows the offer's own concept art
			sticker.as_offer("firmware" if res is FirmwareData else "daemon", ("chip_%s" if res is FirmwareData else "daemon_%s") % id)
		sticker.fit_whole = true  # ANIM-R1 M10: the whole text on the card
		sticker.custom_minimum_size = LOOT_CARD * ls
		sticker.hotkey = ""  # rewards are picked by click or focus, not number keys
		# H24 S17: the whole text on hover and, for a pad or keyboard, on focus (FocusTip).
		var drag_kind := String({"card": "card", "firmware": "chip", "daemon": "daemon"}.get(String(offer["kind"]), ""))
		sticker.tooltip_text = UiTip.fold(loot_tip(res) + ("\n" + drag_tip(drag_kind) if drag_kind != "" else ""))
		FocusTip.attach(sticker)
		var index: int = i
		sticker.pressed.connect(func() -> void: choose_reward(index, slot_option.selected() if slot_option != null else -1))
		sticker.focus_entered.connect(func() -> void: _loot_lit = sticker)
		sticker.mouse_entered.connect(func() -> void: _loot_lit = sticker)
		if slot_option != null and res is FirmwareData:
			_mark_socket_fits(sticker, slot_option, id)
		stickers.add_child(sticker)
	# The deck counter (a card goes there: "+1 = N" in pencil), then Skip as a sticker.
	if offer["kind"] == "card":
		# a small counter (round 31: DECK and the count on one line), no header strip
		var deck := CrtWindow.new("").with_kind(CrtWindow.kind_for(Palette.CELL_PINK), Palette.CELL_PINK)
		deck.name = "LootDeck"
		deck.size_flags_vertical = Control.SIZE_SHRINK_END
		var deck_row := HBoxContainer.new()
		deck_row.add_theme_constant_override("separation", 8)
		deck.body.add_child(deck_row)
		var deck_word := _label(tr("DECK"))
		deck_word.add_theme_font_override(&"font", Palette.mono())
		deck_word.add_theme_color_override(&"font_color", Palette.CELL_PINK)
		deck_word.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		deck_row.add_child(deck_word)
		var count := _label(str(op.deck.size()))
		count.name = "DeckCount"
		count.add_theme_font_override(&"font", Palette.display())
		count.add_theme_color_override(&"font_color", Palette.CELL_PINK)
		deck_row.add_child(count)
		foot_left.add_child(deck)
		var plus := PencilNote.new(tr("+1 = %d") % (op.deck.size() + 1), Palette.PENCIL_PLAN, -0.12, roundi(PencilNote.FONT_PX * os))
		plus.name = "DeckNote"
		plus.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		plus.with_arrow(Vector2(0, plus.custom_minimum_size.y * 0.6), Vector2(-28.0, plus.custom_minimum_size.y * 0.9), 4.0)
		foot_left.add_child(plus)
	var skip := HoloSticker.word(tr("Skip").to_upper(), VinylSticker.Fill.WHITE, os, LOOT_SKIP_PX)
	skip.name = "Skip"
	skip.pressed.connect(skip_reward)
	skip.tooltip_text = tr("Take nothing from this payout.")
	IconMark.attach(skip, StatIcon.SKIP)
	# Parity LOOT-03: under the sheet, in the middle of the foot (the DECK counter on its left)
	skip.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN if compact else Control.SIZE_SHRINK_CENTER
	(side if compact else foot).add_child(skip)
	# B5 (designer ruling 6, review D8: "the page ends on a sticker verb"): CONTINUE, the pink verb bottom right: the
	# same press as taking the lit sticker (the one holding the focus, the first by default), so the flow is the
	# rules' own pick.
	var go := HoloSticker.word(tr("CONTINUE"), VinylSticker.Fill.PINK, os, LOOT_CONTINUE_PX)
	go.name = "Continue"
	go.sticker.sweep_primary = true
	go.tooltip_text = UiTip.fold(tr("Take the lit sticker and go on."))
	go.pressed.connect(func() -> void: _continue_loot(stickers, slot_option))
	if compact:
		# B5c: SKIP and CONTINUE share a row in the side column (stacked, a Firmware drop's column ran past the
		# screen's foot and its safe margin at 2.0).
		var verbs := HBoxContainer.new()
		verbs.name = "LootVerbs"
		verbs.add_theme_constant_override(&"separation", roundi(UiTheme.SP_M * os))
		side.add_child(verbs)
		side.move_child(verbs, skip.get_index())
		skip.reparent(verbs, false)
		go.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		verbs.add_child(go)
		foot.queue_free()
		foot_right.queue_free()
	else:
		foot.add_child(foot_right)
		go.size_flags_horizontal = Control.SIZE_SHRINK_END
		foot.add_child(go)
	if side.get_child_count() == 0:
		side.visible = false
	_set_panel(page, false)
	_fit_loot_height(page, stickers, ls, tilt)
	_register_loot_drops(stickers, mini, slot_option)
	if entering:
		_fan_loot.call_deferred(stickers)


## B5 (D8): CONTINUE takes the loot sticker that holds the focus (the last one hovered or focused; the first when
## none has been), as its own press would.
func _continue_loot(stickers: Control, slot_option: SpinnerMini) -> void:
	if not is_instance_valid(stickers):
		return
	var items := _row_items(stickers)
	if items.is_empty():
		return
	var at := 0
	var owner := get_viewport().gui_get_focus_owner()
	for i in items.size():
		if items[i] == owner or items[i] == _loot_lit:
			at = i
	choose_reward(at, slot_option.selected() if slot_option != null else -1)


## B5: the loot sticker last hovered or focused (CONTINUE's pick).
var _loot_lit: Control = null
## B5 (D8): CONTINUE's lettering (px at scale 1).
const LOOT_CONTINUE_PX := 32


## ART-9 4A: the loot's title sticker and Skip lettering (px at scale 1) and the sheet's foot.
const LOOT_TITLE_PX := 56
## ART-9 4A: the column beside the loot sheet (PAYOUT, a Firmware drop, the deck, Skip; px at 1).
const LOOT_SIDE_W := 240.0
const LOOT_SKIP_PX := 30
const LOOT_FOOT := "x1 %s TAKEN // UNPICKED STICKERS FALL OFF" # TR
## Parity LOOT-02 / LOOT-03 (round 32 `reward_screen_v2`): the loot strip's words (the run's
## Site, the node's word and its layer of the route's layers; the Site only off a node) and the
## PAYOUT's wallet line.
const LOOT_STRIP := "LOOT // NETRUN: %s // %s %d OF %d" # TR
const LOOT_STRIP_SITE := "LOOT // NETRUN: %s" # TR
const LOOT_STRIP_SHORT := "%s // %s %d OF %d" # TR
const PAYOUT_WALLET := "wallet %d -> %d" # TR
## Parity LOOT-03: from this text size the DECK counter and SKIP stand beside the sheet (the
## concept's foot row would push SKIP under the screen's edge).
const LOOT_SIDE_FROM := 1.25
## Parity LOOT-03: the least the cards' scale gives way to at big text (they still grow: H-pass
## 21, "loot cards grow"), and the page's margin kept under it (px at the text scale).
const LOOT_PAGE_MARGIN := 8.0
const LOOT_BIG_FLOOR := 1.25


## Parity LOOT-03: the loot page keeps to the room under the bar (at 1.6 its cards grew past the
## screen's foot and the page scrolled): once laid out with this page's bar, the cards' scale
## `ls` gives way by what the page is over, never under 1 (nor under LOOT_BIG_FLOOR where they
## had grown past it); `tilt` keeps their rest tilt's room between them. It looks again on the
## next frame, when the bar has wrapped its tags for this page.
func _fit_loot_height(page: Control, stickers: Control, ls: float, tilt: float, low: float = -1.0, again: bool = true) -> void:
	if low < 0.0:
		low = maxf(1.0, minf(ls, LOOT_BIG_FLOOR))
	if again and is_inside_tree():
		get_tree().process_frame.connect(_refit_loot.bind(weakref(page), weakref(stickers), tilt, low), CONNECT_ONE_SHOT)
	# the bar as laid out (it wraps its tags at big text past its least height)
	var room := size.y - maxf(hud.size.y, hud.get_combined_minimum_size().y) - LOOT_PAGE_MARGIN * Settings.text_scale
	for n: Control in [subtitle_strip, pad_prompts, _log]:
		if n.visible:
			room -= n.get_combined_minimum_size().y
	var over := page.get_combined_minimum_size().y - room
	if over <= 0.0 or stickers.get_child_count() == 0:
		return
	var k := maxf(low, ls - over / LOOT_CARD.y)
	if k >= ls:
		return
	stickers.add_theme_constant_override("separation", roundi(LOOT_GAP + LOOT_CARD.y * k * tilt))
	for c in stickers.get_children():
		var card := c as ZineCard
		if card != null:
			card.scaled(k)
			card.custom_minimum_size = LOOT_CARD * k


## Parity LOOT-03: the loot page's second look, a frame on (weak refs: the page may be gone).
func _refit_loot(page_ref: WeakRef, stickers_ref: WeakRef, tilt: float, low: float) -> void:
	var page := page_ref.get_ref() as Control
	var stickers := stickers_ref.get_ref() as Control
	if page == null or stickers == null or not page.is_inside_tree() or stickers.get_child_count() == 0:
		return
	var first := stickers.get_child(0) as ZineCard
	if first != null:
		_fit_loot_height(page, stickers, first.text_scale, tilt, low, false)


## Parity LOOT-02: the loot strip ("LOOT // NETRUN: SOLACE CLINIC // FIGHT 3 OF 7"), translated.
## `short` (big words): what paid out (`source`, translated: the title sticker's words) and the
## node's place, so the strip and PAYOUT share a row.
func loot_strip(s: NetrunSession, short: bool = false, source: String = "") -> String:
	var site := server_label()
	var node := s.run.current_node() if s.run.current_node_id != &"" else {}
	if node.is_empty() or s.run.map == null:
		return tr(LOOT_STRIP_SITE) % site
	if short:
		return tr(LOOT_STRIP_SHORT) % [source, node_word(node).to_upper(), int(node["layer"]), s.run.map.layer_count()]
	return tr(LOOT_STRIP) % [site, node_word(node).to_upper(), int(node["layer"]), s.run.map.layer_count()]


## Parity LOOT-03: what the payout on show paid, from the session's own events of the step that
## brought it (the fight's win): {"paid": a Cycles event was there, "cycles": their sum,
## "heat": the Heat added}. The events are the rules' own: the numbers are the result.
static func payout_of(s: NetrunSession) -> Dictionary:
	var out := {"paid": false, "cycles": 0, "heat": 0}
	for e in s.last_events:
		match String(e.get("type", "")):
			"cycles":
				out["paid"] = true
				out["cycles"] = int(out["cycles"]) + int(e.get("amount", 0))
			"heat":
				out["heat"] = int(out["heat"]) + int(e.get("amount", 0))
	return out


## Parity LOOT-03: one PAYOUT line: the word in the terminal's ink, the value in Anton in `col`.
func _payout_row(word: String, value: String, col: Color) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 24)
	var k := _label(word)
	k.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	k.add_theme_color_override(&"font_color", Palette.TERMINAL_TEXT)
	row.add_child(k)
	var v := _label(value)
	v.add_theme_font_override(&"font", Palette.display())
	v.add_theme_color_override(&"font_color", col)
	row.add_child(v)
	return row


## ANIM-R6 B8: what the loot's socket list is for (a key; the Mainframe's SOCKET_TIP without
## buying).
const LOOT_SOCKET_TIP := "A Firmware chip upgrades one slot of your spinner: it works on the slice in that slot whenever the slice lands. Pick here which slot the chip you take goes into." # TR
## ANIM-R6 B10: what paid the loot out, by the node the run stands on (keys): a fight, an
## Elite, the Server Rack, an event.
## B5 (review D8: "PAYOUT is a terminal word"): the title sticker never says PAYOUT (an event's loot is EVENT LOOT,
## the rest LOOT); PAYOUT stays the terminal's.
const LOOT_SOURCES := {RC.InfilNodeType.ROUTER: "FIGHT WON", RC.InfilNodeType.SERVER_RACK: "RACK BREACHED", # TR
	RC.InfilNodeType.TERMINAL: "EVENT LOOT", RC.InfilNodeType.MAINFRAME: "LOOT"} # TR
const LOOT_ELITE := "ELITE DOWN" # TR
const LOOT_PLAIN := "LOOT" # TR


## ANIM-R6 B10: what paid out the loot on show, as its window names it (a key): the node the
## run stands on (an Elite fight has its own words).
static func loot_source(s: NetrunSession) -> String:
	var node := s.run.current_node() if s != null and s.run.current_node_id != &"" else {}
	if node.is_empty():
		return LOOT_PLAIN
	if _is_elite(node):
		return LOOT_ELITE
	return String(LOOT_SOURCES.get(int(node["type"]), LOOT_PLAIN))


## The loot fans in from the foot of its row, one after another (ANIM-6, `loot_fan`).
func _fan_loot(row: Control) -> void:
	if not is_instance_valid(row) or not row.is_inside_tree():
		return
	var r := row.get_global_rect()
	var n := row.get_child_count()
	_fan_row = weakref(row)
	for i in n:
		var card := row.get_child(i) as ZineCard
		if card == null:
			continue
		# ANIM-R1 M11: from the middle of the row's own foot (the deck pile), inside the row:
		# from under it the cards crossed the Skip bar at 1.6 on their way up.
		var from := Vector2(r.get_center().x, r.end.y - card.size.y * 0.5)
		var fan := Motion.amplitude(&"loot_fan") * (float(i) - (n - 1) * 0.5)
		card.fan_in(from, fan, Motion.delay_of(&"loot_fan") * i)


## ANIM-R6 B1: the loot row whose stickers fan in (weak: the page may go first). The deal is
## a motion of this screen (MotionSkip: one press lands every sticker at once), and the row
## is kept while it plays: a press on a sticker still fanning in (invisible in its delay, or
## on its way) lands the deal and picks nothing.
var _fan_row: WeakRef = null


## The loot row while its stickers still fan in (else null).
func fanning_row() -> Control:
	var row := _fan_row.get_ref() as Control if _fan_row != null else null
	if row == null or not row.is_inside_tree():
		return null
	for c in row.get_children():
		if c is ZineCard and (c as ZineCard).dealing():
			return row
	return null


## Lands every loot sticker still fanning in (the deal's end state).
func finish_fan() -> void:
	var row := _fan_row.get_ref() as Control if _fan_row != null else null
	_fan_row = null
	if row == null:
		return
	for c in row.get_children():
		if c is ZineCard:
			(c as ZineCard).finish_deal()


# ==== ART-9 4A: events (owner 4A) ====
## ART-9 4A (ART_BIBLE v2 §4.11 Events LOCKED as drawn; round 31 `event_screen`,
## `event_screen_memo`): a Terminal event. The story is in a CRT terminal tinted the corp colour
## ("> TERMINAL // SOLACE"), with a CAM feed of the city beside it, its title in Anton and the
## speaker under it; a corp speaker's story is an intercepted memo on corp paper taped over the
## terminal instead (INTERCEPTED // INTERNAL MAIL); DISPATCH has no feed (VOICE ONLY // NO FEED,
## red). The choices are sticker buttons with their number tab and their outcome chips (green
## gain, red cost, grey no change), the node's TERMINAL sticker beside the window and at most one
## pencil note ("PLAY IT SAFE??" at the choice that changes nothing). After the pick its outcome
## stamps CHOSEN on the page (ANIM-R6 B12).
func _show_event() -> void:
	var s := RunManager.netrun
	var ev := s.current_event()
	var ts := Settings.text_scale
	var os := minf(ts, ShopItem.OBJECT_MAX_SCALE)
	var dispatch := ev.speaker == RC.Voice.DISPATCH
	var corp_id := ev.corporation_id if ev.corporation_id != &"" else RunManager.campaign.corporation_id
	# Parity EVT-03 (round 31 `event_screen_memo`): a corp speaker's story is an intercepted memo.
	# B5 (review D10, designer ruling 5: DISPATCH is voice only, before and after the betrayal): DISPATCH is the Cell's
	# handler, never paper: the red voice trace (VOICE ONLY // NO FEED) and the transcript typed on in the red-accent
	# CRT.
	var memo := ev.speaker == RC.Voice.CORPO
	var tint := Palette.HARM if dispatch else Palette.corp_color(corp_id)
	var corp_res := s.lookup.get_content(corp_id)
	var corp_name := TextDb.t(corp_res, "display_name") if corp_res != null else String(corp_id)
	var box := VBoxContainer.new()
	box.name = "EventPage"
	# H23 S10: room above the window for its title, clear of the subtitle band.
	var gap := Control.new()
	gap.name = "EventTopGap"
	gap.custom_minimum_size.y = EVENT_TOP_GAP * ts if ts <= EVENT_GAP_MAX_SCALE else 0.0
	gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(gap)
	var split := HBoxContainer.new()
	split.add_theme_constant_override("separation", 18)
	box.add_child(split)
	# Parity EVT-01 (round 31 `event_screen`): the terminal names where the run stands
	# ("TERMINAL // SOLACE BIOSYSTEMS // NODE 4 OF 7").
	var holder := _crt_one_line(CrtWindow.new(event_header(s, tr("DISPATCH") if dispatch else corp_name.to_upper()), tint).with_kind(CrtWindow.kind_for(tint), tint))
	holder.name = "EventPanel"
	holder.tag_label.text = tr("INTERCEPT") if memo and not dispatch else tr("EVENT")
	holder.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	holder.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	split.add_child(holder)
	var inner := HBoxContainer.new()
	inner.add_theme_constant_override("separation", roundi(22 * os))
	holder.body.add_child(inner)
	var text := RichTextLabel.new()
	text.name = "EventText"
	text.fit_content = true
	# ANIM-R5 B1: the words are laid out whole while they type in.
	text.visible_characters_behavior = TextServer.VC_CHARS_AFTER_SHAPING
	text.text = TextDb.t(ev, "text")
	var right := VBoxContainer.new()
	right.add_theme_constant_override("separation", roundi(8 * os))
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var feed: CamFeed = null
	var cam_row: HBoxContainer = null
	# Left: the memo (corp speaker), the CAM feed, or DISPATCH's voice.
	if memo:
		var paper := CorpMemo.new(corp_name, tint, os)
		paper.custom_minimum_size = Vector2(EVENT_MEMO_W, 0)
		paper.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		text.custom_minimum_size = Vector2(EVENT_MEMO_W - CorpMemo.PAD.x * 2.0 * os, 0)
		text.add_theme_font_override(&"normal_font", Palette.paper())
		text.add_theme_color_override(&"default_color", Palette.PAPER_TYPE_INK)
		paper.body.add_child(text)
		inner.add_child(paper)
	else:
		feed = CamFeed.new(tr("CAM %02d  %s") % [absi(ev.id.hash()) % 90 + 4, TextDb.t(ev, "title").to_upper()], tint, dispatch, os)
		feed.custom_minimum_size = EVENT_CAM * os
		feed.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		if ts < EVENT_FEED_BELOW:
			inner.add_child(feed)
		else:
			# B5 (review Q14 / D9: shrink and reflow, never hide): at big text the feed is a 160 px wide strip above the
			# story, in one row with the title (CamRow) so the choices keep the screen.
			feed.custom_minimum_size = Vector2(EVENT_CAM_STRIP_W, EVENT_CAM_STRIP_H) * minf(ts, EVENT_CAM_STRIP_GROW)
			feed.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
			cam_row = HBoxContainer.new()
			cam_row.name = "CamRow"
			cam_row.add_theme_constant_override("separation", roundi(UiTheme.SP_M * os))
			cam_row.add_child(feed)
			right.add_child(cam_row)
		text.custom_minimum_size = Vector2(EVENT_TEXT_W, 0)
		text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		text.add_theme_font_override(&"normal_font", Palette.mono())
		text.add_theme_color_override(&"default_color", Palette.TERMINAL_TEXT)
	inner.add_child(right)
	# Right: who speaks, the title, the story (unless on the memo), then the choices.
	# H24 S4: the speaker's name comes translated (once).
	var who: String = Dialogue.speaker_name(ev.speaker, corp_id)
	if memo:
		var intercepted := _label(tr(DISPATCH_HEAD) if dispatch else tr("INTERCEPTED // %s INTERNAL MAIL") % corp_name.to_upper())
		intercepted.name = "EventIntercept"
		intercepted.add_theme_color_override(&"font_color", tint)
		intercepted.add_theme_font_override(&"font", Palette.mono())
		right.add_child(intercepted)
	# Naive-reader audit P3: DISPATCH's name once (its title already starts with it).
	var title := _label(TextDb.t(ev, "title").to_upper() if not memo or dispatch else who)
	title.name = "EventTitle"
	title.add_theme_font_override(&"font", Palette.display())
	title.add_theme_font_size_override(&"font_size", roundi(EVENT_TITLE_PX * os))
	title.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	if cam_row != null:
		title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		title.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		cam_row.add_child(title)
	else:
		right.add_child(title)
	# Naive-reader audit P3: DISPATCH's name once (its title already starts with it).
	var speaker := _label(tr("voice only // transcript") if dispatch else ((who + " - " + TextDb.t(ev, "title")) if memo else tr("%s // terminal log, unsigned") % who))
	speaker.add_theme_color_override(&"font_color", tint)
	speaker.add_theme_font_override(&"font", Palette.mono())
	right.add_child(speaker)
	# big words: the story and the choices take the room (the subtitle names the speaker)
	speaker.visible = ts < EVENT_FEED_BELOW
	if not memo:
		right.add_child(text)
	# Parity EVT-01 / EVT-02: under a CAM feed the choices take the terminal's whole width under
	# its story (round 31 `event_screen`); beside a memo they stay in the right column
	# (`event_screen_memo`). Either way each outcome's chips stand in a column beside its row.
	# From EVENT_CHOICES_BESIDE_FROM up the feed's height would push them off the screen: beside it.
	var choices_host: VBoxContainer = right if memo or ts >= EVENT_CHOICES_BESIDE_FROM else holder.body
	var choose := _label(tr("> CHOOSE"))
	choose.name = "EventChoose"
	choose.add_theme_color_override(&"font_color", tint)
	choose.add_theme_font_override(&"font", Palette.mono())
	choices_host.add_child(choose)
	choose.visible = ts < EVENT_FEED_BELOW
	if not _spoken_events.has(ev.id):
		_spoken_events[ev.id] = true
		# ANIM-R6 B12: the story is on the page; the subtitle bar no longer repeats it word for
		# word (kept for the history and voice-over). TextDb text is already translated.
		Dialogue.log_line(ev.speaker, TextDb.t(ev, "text"), corp_id)
	var options := VBoxContainer.new()
	options.name = "Choices"
	options.add_theme_constant_override("separation", roundi(8 * os))
	options.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	options.theme = ChoiceSticker.theme_for(ts)
	choices_host.add_child(options)
	var calm: Control = null
	for i in ev.choices.size():
		var c := ev.choices[i]
		var b := Button.new()
		# H21 #13: the outcome as chips under the words (Heat as it applies); H22 #12: the
		# amounts it will really apply (a heal at full HP, Heat at 0).
		var outcome := OutcomeRow.of_choice(s, c)
		var costs := OutcomeRow.words(outcome)
		b.text = _choice_text(TextDb.t(c, "label"), costs)
		var err := s.choice_error(c)
		b.disabled = err != ""
		var tip := err if err != "" else ((tr("Costs: %s.") % costs) if costs != "" else "")
		tip += ("\n" if tip != "" else "") + (OutcomeRow.describe(outcome) if not outcome.is_empty() else tr("No change to your numbers."))
		b.tooltip_text = UiTip.fold(tip)
		var index := i
		b.name = "Choice%d" % (i + 1)
		b.pressed.connect(func() -> void: _press_choice(index))
		b.theme_type_variation = ChoiceSticker.TYPE
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.autowrap_mode = TextServer.AUTOWRAP_WORD
		b.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		options.add_child(b)
		b.add_child(ChoiceSticker.new(i + 1, ts))
		# H23 S9 / H24 S9: a choice that changes nothing says so with the grey NO CHANGE chip.
		# Parity EVT-02: the chips in a column beside the sticker, readable at a glance.
		var numbers := OutcomeRow.shown(outcome)
		var row := OutcomeRow.new(numbers if not numbers.is_empty() else OutcomeRow.no_change())
		OutcomeRow.attach_beside(b, row, EVENT_CHIPS_GAP * os)
		if numbers.is_empty() and calm == null:
			calm = b
		# ANIM-6: the outcome's chips pop when the choice is hovered or focused.
		b.mouse_entered.connect(func() -> void: Motion.pop(row, &"event_outcome_pop"))
		b.focus_entered.connect(func() -> void: Motion.pop(row, &"event_outcome_pop"))
	# Parity EVT-02: the stickers take EVENT_CHOICE_SHARE of the row, the chips the rest.
	var chips_gap := EVENT_CHIPS_GAP * os
	options.resized.connect(func() -> void: fit_event_choices(options, chips_gap))
	# Beside the window: the RUN terminal, the node's TERMINAL sticker and, at most, one pencil note.
	var side := VBoxContainer.new()
	side.name = "EventSide"
	side.add_theme_constant_override("separation", 24)
	side.custom_minimum_size.x = EVENT_SIDE_W * (os if ts < EVENT_FEED_BELOW else 1.0)
	split.add_child(side)
	# Parity EVT-01 (round 31 `event_screen`): the RUN side terminal (HP, CYCLES, CREW); at big
	# text the top bar's tags say the same and the story takes the room.
	# B5 (review section f: "Loot / event: only what the choice changes"): the top bar carries what the choices change
	# (HP, Cycles, crew ...: event_bar_keys), in place of the RUN terminal.
	var node_sticker := HoloSticker.word(tr("TERMINAL"), VinylSticker.Fill.RED if dispatch else VinylSticker.Fill.WHITE, os, EVENT_STICKER_PX)
	node_sticker.name = "NodeSticker"
	node_sticker.focus_mode = Control.FOCUS_NONE
	node_sticker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	node_sticker.rotation = -0.06
	node_sticker.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	side.add_child(node_sticker)
	if calm != null:
		var note := PencilNote.new(tr("PLAY IT\nSAFE??"), Palette.PENCIL_PLAN, -0.06, roundi(PencilNote.FONT_PX * 1.2 * os))
		note.name = "EventNote"
		note.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		side.add_child(note)
		# Naive-reader audit P3: the arrow ends on the choice it means (whenever either moves).
		var aim := func() -> void:
			if is_instance_valid(note) and is_instance_valid(calm) and calm.is_inside_tree():
				var target := calm.get_global_rect()
				# Parity EVT-02: the arrow ends on the choice's NO CHANGE chip beside it.
				var chips := calm.get_node_or_null(^"OutcomeRow") as Control
				if chips != null and chips.visible and chips.size.x > 0.0:
					target = chips.get_global_rect()
				var to := Vector2(target.end.x + 6.0, target.get_center().y) - note.global_position
				note.with_arrow(Vector2(0.0, note.custom_minimum_size.y * 0.8), to, 24.0)
		note.item_rect_changed.connect(aim)
		calm.item_rect_changed.connect(aim)
		box.sort_children.connect(func() -> void: aim.call_deferred())
		split.sort_children.connect(func() -> void: aim.call_deferred())
	_set_panel(box, false)
	_event_backbuffer()
	# B5 (D9): the CAM feed shows the run's Site close-up itself (never an empty box, never the dimmed page behind).
	var cam := box.find_child("CamFeed", true, false) as CamFeed
	if cam != null and not cam.voice_only:
		cam.show_picture(site_picture())
	_register_event_drops(ev, options)
	# ANIM-R4 C7: the story types within `event_type`'s cap (0.8 s).
	if entering and Typing.type_in(text, &"event_type") > 0.0:
		_hold_choices(options, text)


## ART-9 4A: the event window's pieces at text scale 1 (px): the CAM feed, the story's width beside
## it, the memo's width, the title lettering, the TERMINAL sticker and the side column (parity
## EVT-01: wide enough for the RUN terminal).
const EVENT_CAM := Vector2(320, 230)
## B5 (Q14): the CAM strip above the story at big text: its width (px at 1; 160 px as the review asks) and the most it
## grows with the text.
const EVENT_CAM_STRIP_W := 160.0
const EVENT_CAM_STRIP_GROW := 1.2
## B5 (Q14): the strip's height (px at 1): a letterbox, short enough that the choices stay on screen at 2.0.
const EVENT_CAM_STRIP_H := 64.0
const EVENT_TEXT_W := 320.0
const EVENT_MEMO_W := 470.0
const EVENT_TITLE_PX := 34
const EVENT_STICKER_PX := 40
const EVENT_SIDE_W := 220.0
## Parity EVT-02 (round 31 `event_screen`): a choice sticker's share of its row and the gap (px at
## 1) before the outcome chips' column beside it.
const EVENT_CHOICE_SHARE := 0.55
const EVENT_CHIPS_GAP := 16.0
## Parity EVT-01: the text size from which the choices stay beside the CAM feed (under it they
## would leave the screen's foot).
const EVENT_CHOICES_BESIDE_FROM := 1.25
## Parity EVT-01 / EVT-03: the terminal's header with the run's place, the RUN terminal's words,
## and DISPATCH's transcript line.
const EVENT_HEADER := "TERMINAL // %s // NODE %d OF %d" # TR
const EVENT_HEADER_SITE := "TERMINAL // %s" # TR
const DISPATCH_HEAD := "TRANSCRIPT // DISPATCH // VOICE LOG" # TR


## Parity EVT-01: the event terminal's header: who it belongs to and the node it stands on of
## the route's layers ("TERMINAL // SOLACE BIOSYSTEMS // NODE 4 OF 7"), translated.
func event_header(s: NetrunSession, owner_words: String) -> String:
	var node := s.run.current_node() if s.run.current_node_id != &"" else {}
	if node.is_empty() or s.run.map == null:
		return tr(EVENT_HEADER_SITE) % owner_words
	return tr(EVENT_HEADER) % [owner_words, int(node["layer"]), s.run.map.layer_count()]


## Parity EVT-01 (round 31 `event_screen`): the RUN side terminal: the operative's HP, the
## run's Cycles and the crew still standing (the campaign's living operatives); its tag names
## the operative and class.
func _event_run_window(s: NetrunSession) -> CrtWindow:
	var op := s.run.operative
	var win := _crt_one_line(CrtWindow.new(tr("RUN"), Palette.NET_CYAN).with_kind(CrtWindow.kind_for(Palette.NET_CYAN), Palette.NET_CYAN))
	win.name = "EventRun"
	win.tag_label.text = "%s // %s" % [op.name.to_upper(), _content_name(op.class_id).to_upper()]
	win.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	win.body.add_child(_payout_row(TextDb.mark("HP"), "%d/%d" % [_shown_operative_hp(op.hp), op.max_hp], Palette.CELL_PINK))
	win.body.add_child(_payout_row(TextDb.mark("CYCLES"), str(s.run.cycles), Palette.CELL_ACID))
	win.body.add_child(_payout_row(TextDb.mark("CREW"), str(s.campaign.living_operatives().size()), Palette.TEXT_HI))
	return win


## Parity EVT-02: the choice stickers take EVENT_CHOICE_SHARE of `options`' width; each one's
## outcome chips fill the column beside it (after `gap` px).
static func fit_event_choices(options: Control, gap: float) -> void:
	if not is_instance_valid(options):
		return
	var w := options.size.x
	var plate := floorf(w * EVENT_CHOICE_SHARE)
	for b in options.get_children():
		if not (b is Button):
			continue
		(b as Button).custom_minimum_size.x = plate
		var row := (b as Node).get_node_or_null(^"OutcomeRow") as OutcomeRow
		if row != null:
			row.set_beside_width(maxf(0.0, w - plate - gap))
## The text size from which the event's CAM feed steps aside (the story takes its room).
const EVENT_FEED_BELOW := 1.25  # FIX-REDS-3: was 1.6; at 1.3 the feed with the choices beside it left the screen's foot
## The CAM feed's copy of the city (a BackBufferCopy after it, while the event shows).
var _event_bbc: BackBufferCopy = null


## Copies the city behind the event page for the CAM feed (once; freed with the screen).
## B5 (D9): the copy is SiteCopy, right over the Site's close-up and under the event's dim (the feed shows the Site,
## never an empty box).
func _event_backbuffer() -> void:
	site_copy.visible = true


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
			btn.add_theme_color_override(&"font_color", Color(Palette.TEXT_HI, HELD_INK_ALPHA))
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


## ANIM-R5 B11: what the Mainframe's socket list is for (a key).
const SOCKET_TIP := "A Firmware chip upgrades one slot of your spinner: it works on the slice in that slot whenever the slice lands. Pick here which slot a chip you BUY goes into." # TR


## A spinner slot by what is in it, never by ids (H21 #12: "overflow_12" in the socket list):
## "Slot 2: SHIM 10 + Barbed Wire".
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


# ==== ART-9 4A: MAINFRAME shop (owner 4A; 3B owns the route/map parts of this file) ====

## ART-9 4A (ART_BIBLE v2 §4.10; round 34 `shop_v5`, round 12 F1b facade, round 33 sign v4 and
## `slice_wheel_offscreen`): the MAINFRAME on its street. The F1b facade fills the screen behind
## the page with the MAINFRAME sign v4 on its plate (MainframeFacade, its takeover sequences);
## the pegboard under the sign holds CARDS (stickers), FIRMWARE (chips in pink foam, the socket
## list under them), the info strip (the focused item's whole text) and DAEMONS (cartridges on
## hooks); the clerk's CRT terminal sits bottom left with the WALLET and the small spinner; the
## slice stock is a wheel mostly below the screen whose top wedges are for sale (kraft tags on
## their rims; a slice opens the UPGRADE viewer as before); card removal is the RECYCLE BIN on the
## sidewalk (it opens the deck viewer as before: the bin is the removal's look, cards only); the
## holographic LEAVE sticker is bottom right. Prices and actions are the current rules (GDD 11.2).
func _show_shop() -> void:
	var s := RunManager.netrun
	var shop := s.run.shop
	var op := s.run.operative
	var ts := Settings.text_scale
	var root := Control.new()
	root.name = "MainframeRoot"
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.custom_minimum_size = SHOP_ROOM
	# The pegboard: CARDS on the left; FIRMWARE, the info strip and DAEMONS on the right.
	var board := ShopPegboard.new(minf(ts, ShopItem.OBJECT_MAX_SCALE))
	# Big words: DAEMONS stands beside FIRMWARE (the board keeps its height) and the clerk keeps
	# only the wallet and the prices (the screen keeps room for the wheel).
	var wide := ts >= SHOP_WIDE_FROM
	root.add_child(board)
	# 1B LightSpill: the sign's light falls on the pegboard beside it (the street's own spill
	# is baked into the facade with the sign, round 33's composite).
	var spill := LightSpill.new()
	spill.name = "SignSpill"
	spill.gain = LightSpill.GAIN_SHOP * SHOP_SPILL_GAIN
	root.add_child(spill)
	var cols := HBoxContainer.new()
	cols.name = "Shelves"
	cols.add_theme_constant_override("separation", roundi(SHOP_COL_GAP * ts))
	cols.mouse_filter = Control.MOUSE_FILTER_IGNORE
	board.add_child(cols)
	# The FIRMWARE column comes first in the tree (the page's first focus and the pad's walk start
	# on the chips, as before) but stands on the right: the row lays out right to left, its
	# columns left to right.
	cols.layout_direction = Control.LAYOUT_DIRECTION_RTL
	var cards_col := VBoxContainer.new()
	cards_col.layout_direction = Control.LAYOUT_DIRECTION_LTR
	cards_col.add_theme_constant_override("separation", roundi(SHOP_ROW_GAP * ts))
	cards_col.add_child(ShopPegboard.tape("CARDS", ts))
	var stickers := HBoxContainer.new()
	stickers.name = "Stickers"
	stickers.add_theme_constant_override("separation", roundi(QUAD_GAP))
	stickers.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	cards_col.add_child(stickers)
	# the cards' kraft tags hang under them (round 34 shop_v5): their room under the row
	var tag_room := Control.new()
	tag_room.name = "CardTagRoom"
	tag_room.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tag_room.custom_minimum_size = Vector2(0, BuyButton.BUY_HEIGHT * ts)
	cards_col.add_child(tag_room)
	var right := VBoxContainer.new()
	right.name = "RightShelves"
	right.layout_direction = Control.LAYOUT_DIRECTION_LTR
	right.add_theme_constant_override("separation", roundi(SHOP_ROW_GAP * ts))
	cols.add_child(right)
	cols.add_child(cards_col)
	var fw_col := VBoxContainer.new()
	fw_col.add_theme_constant_override("separation", roundi(SHOP_ROW_GAP * ts))
	var dm_col := VBoxContainer.new()
	dm_col.add_theme_constant_override("separation", roundi(SHOP_ROW_GAP * ts))
	if wide:
		var pair := HBoxContainer.new()
		pair.add_theme_constant_override("separation", roundi(SHOP_COL_GAP))
		right.add_child(pair)
		pair.add_child(fw_col)
		pair.add_child(dm_col)
	else:
		right.add_child(fw_col)
		right.add_child(dm_col)
	fw_col.add_child(ShopPegboard.tape("FIRMWARE", ts))
	var chips := HBoxContainer.new()
	chips.name = "Chips"
	chips.add_theme_constant_override("separation", roundi(SHOP_ROW_GAP * ts))
	fw_col.add_child(chips)
	board.foam_row = chips
	# ANIM-4b: the spinner in small: Firmware and slice upgrades drag onto its slots. Parity
	# SHOP-06: with Firmware in stock it is also the socket choice (it replaced the dropdown).
	var fw_slot := _spinner_mini()
	var stocks_firmware: bool = not shop.get("firmware", []).is_empty()
	if stocks_firmware:
		fw_slot.make_pickable(0)
	var info :=_crt_one_line(CrtWindow.new("").with_kind(CrtWindow.kind_for(Palette.NET_CYAN), Palette.NET_CYAN))
	info.name = "ShopInfo"
	var os := minf(ts, ShopItem.OBJECT_MAX_SCALE)
	# big words: a narrower strip keeps the spinner beside it clear of the stock wheel's left tag
	var iw := SHOP_INFO_W * (minf(os, SHOP_INFO_WIDE_SCALE) if wide else os)
	info.custom_minimum_size = Vector2(iw, 0)
	var info_text := Label.new()
	info_text.name = "ShopInfoText"
	info_text.autowrap_mode = TextServer.AUTOWRAP_WORD
	info_text.custom_minimum_size = Vector2(iw - 24.0, 0)
	info_text.add_theme_color_override(&"font_color", Palette.TEXT_MID)
	info_text.add_theme_font_override(&"font", Palette.mono())
	info_text.text = UiTip.for_input(tr(SHOP_INFO_IDLE), tr(SHOP_INFO_IDLE_PAD))
	# the strip keeps to a few lines (the item's whole text is its tip)
	info_text.max_lines_visible = SHOP_INFO_LINES
	info_text.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	info.body.add_child(info_text)
	var daemon_row := HBoxContainer.new()
	daemon_row.name = "Daemons"
	daemon_row.add_theme_constant_override("separation", roundi(SHOP_ROW_GAP * ts))
	var n := 0
	# ANIM-R1 M11: what the Mainframe offered when the player came in; a bought item stays as a
	# SOLD stub in its place (the rest keep their spots).
	var seen := _shop_seen(s)
	var card_count: int = (seen["cards"] as Array).size()
	var card_fit := minf((SHOP_CARDS_ROOM.x - QUAD_GAP * maxi(0, card_count - 1)) / maxf(1.0, card_count * ZineCard.STICKER_SIZE.x),
		SHOP_CARDS_ROOM.y / ZineCard.STICKER_SIZE.y)
	var cs := clampf(minf(ts, card_fit), 1.0, Settings.TEXT_SCALE_MAX)
	for kind in ["cards", "firmware", "daemons"]:
		var prices: Array = shop.get(kind.trim_suffix("s") + "_prices", [])
		for slot: Array in shop_slots(seen[kind], shop.get(kind, [])):
			var i: int = slot[1]
			var id := StringName(String(slot[0]))
			var res := s.lookup.get_content(id)
			if i < 0:
				var stub := _sold_stub(TextDb.t(res, "display_name"), (res as CardData).ram_cost if res is CardData else -1, n, kind, cs, ts)
				_shop_shelf_look(stub, kind, res, id)
				({"cards": stickers, "firmware": chips}.get(kind, daemon_row) as Control).add_child(stub)
				n += 1
				continue
			# H21 #12: the circle shows a card's real RAM cost; the price hangs on its kraft tag.
			var ram := (res as CardData).ram_cost if res is CardData else -1
			var item := ShopItem.new(TextDb.t(res, "display_name"), ram, shop_text(res), n)
			item.fit_whole = true  # ANIM-R1 M10: the whole text on a card
			item.hotkey = ""
			item.with_price(int(prices[i]))
			if kind == "cards":
				item.scaled(cs).with_card(res as CardData)
				item.set_meta(BuyButton.TAG_BELOW, true)
			_shop_shelf_look(item, kind, res, id)
			item.tooltip_text = UiTip.fold(tr("%s\n%s\nBuy: %d Cycles (you have %d).") % [TextDb.t(res, "display_name"), shop_text(res), int(prices[i]), s.run.cycles]
				+ "\n" + drag_tip(String({"cards": "card", "firmware": "chip", "daemons": "daemon"}[kind])))
			item.disabled = int(prices[i]) > s.run.cycles
			# H23 S8: a clear buy button on every item (its kraft tag), the whole text on focus.
			item.with_buy(TextDb.mark("BUY"))
			FocusTip.attach(item)
			_shop_info_on(item, info_text, "%s  %s" % [TextDb.t(res, "display_name").to_upper(), shop_text(res)])
			var index: int = i
			var k: String = kind
			var price_i := int(prices[i])
			# ANIM-R2 E9: pressing an item out of reach says why on the money itself.
			item.gui_input.connect(func(ev: InputEvent) -> void:
				if item.disabled and (ev.is_action_pressed(&"ui_accept") or (ev is InputEventMouseButton and (ev as InputEventMouseButton).pressed and (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT)):
					price_refused(price_i))
			item.set_meta(STOCK_META, i)
			item.pressed.connect(func() -> void: buy(k, index, fw_slot.selected() if k == "firmware" else -1))
			if k == "firmware":
				_mark_socket_fits(item, fw_slot, id)
			({"cards": stickers, "firmware": chips}.get(kind, daemon_row) as Control).add_child(item)
			n += 1
	if stocks_firmware:
		# ANIM-R5 B11: the list says what it is for ("Chips go into: Slot 1: OVERFLOW 12"); parity
		# SHOP-06: the choice itself is the spinner beside the info strip, this line names it.
		cards_col.add_child(_socket_row(fw_slot, tr(SOCKET_TIP) + " " + drag_tip("socket")))
	var info_row := HBoxContainer.new()
	info_row.name = "InfoRow"
	info_row.add_theme_constant_override("separation", roundi(SHOP_ROW_GAP * 2.0 * ts))
	cards_col.add_child(info_row)
	info_row.add_child(info)
	dm_col.add_child(ShopPegboard.tape("DAEMONS", ts))
	dm_col.add_child(daemon_row)
	if daemon_row.get_child_count() == 0:
		var none := _label(tr("sold out"))
		none.add_theme_color_override(&"font_color", Palette.TEXT_MID)
		daemon_row.add_child(none)
	# The slice stock wheel (named Slices: its wedges for sale are the slice items).
	var wheel := SliceStockWheel.new()
	wheel.name = "Slices"
	root.add_child(wheel)
	var stock: Array = shop.get("slices", [])
	# A slice's price depends on the slot it overwrites: the tag shows the lowest (the UPGRADE
	# viewer shows the slot's own price before anything is paid).
	var low := -1
	var high := -1
	for k in op.slot_slice_ids.size():
		var p := s.slice_overwrite_price(k)
		low = p if low < 0 else mini(low, p)
		high = maxi(high, p)
	var slice_slots := shop_slots(seen["slices"], stock)
	for j in slice_slots.size():
		var slot: Array = slice_slots[j]
		var i: int = slot[1]
		var sd := s.lookup.get_content(StringName(String(slot[0]))) as SliceData
		if sd == null:
			continue
		var slice_word := tr(String(Palette.SLICE_NAMES.get(sd.slice_type, "?")))
		var title := "%s %d" % [slice_word, sd.base_output] if sd.base_output > 0 else slice_word
		var tile: ShopItem
		if i < 0:
			tile = _sold_stub(title, -1, slice_slots.size(), "slices", 1.0, ts)
		else:
			tile = ShopItem.new(title, -1, Codex.describe(sd), i)
			tile.set_meta(STOCK_META, i)
			tile.hotkey = ""
			if low >= 0:
				tile.with_price(low)
			# H23 S8: the real prices (the slot you overwrite sets it), said in words.
			tile.tooltip_text = UiTip.fold(tr("Overwrite a slot of your spinner with this slice. Price: %s Cycles%s (you have %d).\n") % [tile.price_words(),
				(tr(": %d for most slots, %d for a pricier one such as the NULL slot; you pick the slot next") % [low, high]) if high > low else "", s.run.cycles] + Codex.describe(sd)
				+ "\n" + drag_tip("slice"))
			tile.with_buy(TextDb.mark("BUY"))
			FocusTip.attach(tile)
			_shop_info_on(tile, info_text, "%s  %s" % [title, Codex.describe(sd)])
			var si := i
			tile.pressed.connect(func() -> void: open_overwrite(si))
		tile.on_shelf(ShopItem.Shelf.SLICE, ts, sd.id)
		tile.slice_type = sd.slice_type
		tile.slice_output = sd.base_output
		wheel.add_item(tile, j, slice_slots.size())
		tile.with_glyph(ShopItem.glyph_of("slices", sd.id, sd.slice_type))
	# The recycle bin: card removal (the deck viewer picks the card, as before).
	var shred := ShopItem.new(tr("RECYCLE BIN"), -1, tr("Pick a card from your deck to remove."), 0).on_shelf(ShopItem.Shelf.BIN, ts)
	shred.with_price(s.card_removal_price())
	shred.name = "RemoveCard"
	shred.hotkey = ""
	shred.disabled = s.run.cycles < s.card_removal_price() or op.deck.is_empty()
	shred.icon_kind = "shred"
	shred.tooltip_text = UiTip.fold(tr("Remove a card from your deck: %d Cycles (you have %d).") % [s.card_removal_price(), s.run.cycles])
	shred.pressed.connect(open_remove)
	shred.with_buy(TextDb.mark("BIN"))
	FocusTip.attach(shred)
	_shop_info_on(shred, info_text, tr("RECYCLE BIN  Remove a card from your deck: %d Cycles.") % s.card_removal_price())
	root.add_child(shred)
	# The clerk's terminal: the shop's rules in its own words, the WALLET and your spinner.
	var clerk := _crt_one_line(CrtWindow.new(tr("MAINFRAME // CLERK"), Palette.NET_CYAN).with_kind(CrtWindow.kind_for(Palette.NET_CYAN), Palette.NET_CYAN))
	clerk.name = "Clerk"
	clerk.tag_label.text = tr("SHOP")
	root.add_child(clerk)
	var face_row := HBoxContainer.new()
	face_row.add_theme_constant_override("separation", 14)
	clerk.body.add_child(face_row)
	var face := Control.new()
	face.name = "ClerkFace"
	face.custom_minimum_size = Vector2(CLERK_FACE, CLERK_FACE) * ts
	face.mouse_filter = Control.MOUSE_FILTER_IGNORE
	face.draw.connect(_draw_clerk_face.bind(face))
	face_row.add_child(face)
	var rules := _label(tr(CLERK_WORDS))
	rules.name = "ClerkWords"
	rules.add_theme_color_override(&"font_color", Palette.TERMINAL_TEXT)
	face_row.add_child(rules)
	face_row.visible = not wide
	var wallet_row := HBoxContainer.new()
	wallet_row.add_theme_constant_override("separation", 12)
	clerk.body.add_child(wallet_row)
	# The wallet (H21 #11): the Cycles to spend, in sight whatever covers the top bar.
	var wallet := HudStats.new()
	wallet.name = "Wallet"
	wallet.items = [[TextDb.mark("CYCLES"), str(s.run.cycles), "", tr("Cycles you have to spend in the Mainframe. Runs and events pay them; they don't leave the run.")]]
	wallet.custom_minimum_size.x = wallet.full_width(ts)
	wallet.mirror = hud.stats  # ANIM-R2 E9: it rolls with the top bar's CYCLES
	wallet.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	wallet_row.add_child(wallet)
	var mini := fw_slot
	mini.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	info_row.add_child(mini)
	if wide:
		# big words: the wallet joins the info strip and the clerk steps aside (the prices are
		# on every tag)
		# parity SHOP-03: at the end of the Daemons' row (under it the stock wheel's tags, lettered
		# bigger now, reached it at 2.0; over it the subtitle band)
		var shelf := HBoxContainer.new()
		shelf.name = "DaemonShelf"
		shelf.add_theme_constant_override("separation", roundi(SHOP_COL_GAP))
		dm_col.add_child(shelf)
		dm_col.move_child(shelf, daemon_row.get_index())
		daemon_row.reparent(shelf)
		wallet.reparent(shelf)
		wallet.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		wallet.custom_minimum_size.x = wallet.full_width(minf(ts, SHOP_WALLET_MAX_SCALE))
		wallet.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		clerk.visible = false
	var prices_line := _label(tr("card %d-%d · slice %d (NULL %d) · bin %d") % [RunManager.config().card_price_range.x, RunManager.config().card_price_range.y,
		RunManager.config().slice_overwrite_price, RunManager.config().null_slice_overwrite_price, s.card_removal_price()])
	prices_line.name = "ClerkPrices"
	prices_line.add_theme_color_override(&"font_color", Palette.TEXT_MID)
	prices_line.add_theme_font_override(&"font", Palette.mono())
	clerk.body.add_child(prices_line)
	# LEAVE: a holographic sticker with a pink chevron arrow.
	var leave := HoloSticker.new(tr("LEAVE"), tr("THE MAINFRAME"), os)
	leave.name = "LeaveMainframe"
	leave.pressed.connect(leave_shop)
	leave.tooltip_text = tr("Leave the Mainframe and go back to the route.")
	root.add_child(leave)
	# Parity SHOP-05 (round 34 shop_v5): the concept's own pink chevron sticker beside LEAVE
	# (shop2.leave_sticker()'s arrow, exported unchanged), pressed it leaves too.
	var leave_icon := leave_arrow(os)
	leave_icon.tooltip_text = leave.tooltip_text
	leave_icon.pressed.connect(leave_shop)
	root.add_child(leave_icon)
	# Grease pencil, true to the rules: only the top wedges are for sale; the bin takes cards;
	# the clerk's note.
	var top_note := PencilNote.new(tr("TOP %d ONLY") % stock.size() if stock.size() > 0 else "", Palette.PENCIL_PLAN, -0.08, roundi(PencilNote.FONT_PX * os))
	top_note.name = "TopNote"
	root.add_child(top_note)
	var bin_note := PencilNote.new(tr("BIN IT"), Palette.PENCIL_PLAN, -0.1, roundi(PencilNote.FONT_PX * os))
	bin_note.name = "BinNote"
	root.add_child(bin_note)
	var clerk_note := PencilNote.new(tr(CLERK_NOTE), Palette.PENCIL_PLAN, -0.05, roundi(PencilNote.FONT_PX * 0.8 * os))
	clerk_note.name = "ClerkNote"
	root.add_child(clerk_note)
	clerk_note.visible = not wide
	# ANIM-R3 A7: the first focus is the first item (one the Cycles reach, else the first),
	# never the socket list: the pad prompt says "A Buy".
	var first_item: ZineCard = null
	for row in [chips, daemon_row, stickers, wheel]:
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
	var lay := func() -> void: _layout_shop(root)
	root.resized.connect(lay)
	board.resized.connect(lay)
	clerk.resized.connect(lay)
	_set_panel(root, false)
	var facade := _shop_backdrop(s)
	var follow := func() -> void:
		if is_instance_valid(spill) and is_instance_valid(facade):
			var lv := facade.sign.spill()
			spill.lit = clampf(maxf(lv.x, lv.y), 0.0, 1.0)
			spill.color = Palette.SIGN_RED if lv.y > lv.x else Palette.SIGN_BLUE
	facade.sign.light_changed.connect(follow)
	# the page goes before the facade (a purchase rebuilds the page): its spill stops following
	var sign_ref: WeakRef = weakref(facade.sign)
	root.tree_exiting.connect(func() -> void:
		var sg := sign_ref.get_ref() as MainframeSign
		if sg != null and sg.light_changed.is_connected(follow):
			sg.light_changed.disconnect(follow), CONNECT_ONE_SHOT)
	follow.call()
	_layout_shop.call_deferred(root)
	_register_shop_drops(mini, fw_slot)
	if entering:
		facade.sign.warm_up()
		wheel.spin_in()


## ART-9 4A: the room the Mainframe page asks of its host (px; its pieces are placed on the
## street by `_layout_shop`), the pegboard's column and row gaps, the CARDS shelf's room, the
## info strip's width (px at scale 1), the clerk's face (px), the gap kept under the top bar for
## the sign, and the wheel's hub below the screen's foot (px).
const SHOP_ROOM := Vector2(1240, 520)
const SHOP_COL_GAP := 22.0
const SHOP_ROW_GAP := 6.0
const SHOP_CARDS_ROOM := Vector2(470, 300)
const SHOP_INFO_W := 250.0
const CLERK_FACE := 48.0
const SHOP_SIGN_GAP := 6.0
const SHOP_HUB_BELOW := 100.0
## The least of the wheel's wedges kept on screen (px).
const SHOP_WEDGE_SHOWN := 120.0
## ART-9 4A: from this text size DAEMONS stands beside FIRMWARE and the clerk shows only the wallet
## and the prices; the info strip's most lines.
const SHOP_WIDE_FROM := 1.25
const SHOP_INFO_LINES := 3
## ART-9 4A: the info strip's largest width scale at big text (its spinner stays clear of the wheel).
const SHOP_INFO_WIDE_SCALE := 0.92
## ART-9 4A: the sign's spill on the pegboard: its share of the shop gain and its reach (px).
const SHOP_SPILL_GAIN := 0.6
const SHOP_SPILL_REACH := 260.0
## ART-9 4A: where the pieces stand on the 1280x720 street (round 34 `shop_v5` x 0.8): the
## pegboard's centre x and top gap under the bar, the wheel's centre x, the bin's top left, the
## clerk's and LEAVE's margins from the screen's corners (px).
const SHOP_BOARD_X := 692.0
const SHOP_BOARD_TOP := 8.0
const SHOP_WHEEL_X := 672.0
const SHOP_BIN_AT := Vector2(1090, 392)
const SHOP_MARGIN := 14.0
## ART-9 4A: the clerk's words, its pencil note and the info strip's line before an item is
## focused (keys).
const CLERK_WORDS := "NO REFUNDS.\nNO NAMES.\nCYCLES ONLY." # TR
const CLERK_NOTE := "ask about the\nback room" # TR
## Parity fix (SHOP-01): the clerk's note starts this share along the words' width and this
## far (px) under their last line.
const CLERK_NOTE_OFFSET := 0.35
const CLERK_NOTE_GAP := 2.0
## The info line by device (UiTip.for_input( picks the pad's when pad_active).
const SHOP_INFO_IDLE := "> point at an item: what it does shows here. Drag Firmware or a slice onto a slot of your spinner." # TR
const SHOP_INFO_IDLE_PAD := "> focus an item: what it does shows here." # TR
## ART-9 4A: the wallet's largest scale at big text (it stands under the Daemons, clear of the
## stock wheel's and the bin's tags; the top bar's CYCLES keeps the full size).
const SHOP_WALLET_MAX_SCALE := 1.35
## Parity SHOP-05: LEAVE's pink chevron sticker (MainframeArt part, round 34 shop2.leave_sticker()).
const LEAVE_ARROW := "leave_arrow"


## Parity SHOP-05 (round 34 shop_v5): the concept's pink chevron sticker beside LEAVE, at object
## scale `os` (the art at MainframeArt.SCALE). No focus of its own: LEAVE is the page's verb and
## takes the pad; a press on the arrow leaves too.
static func leave_arrow(os: float) -> Button:
	var b := Button.new()
	b.name = "LeaveIcon"
	b.flat = true
	b.icon = MainframeArt.tex(LEAVE_ARROW)
	b.expand_icon = true
	b.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	for key in ["normal", "hover", "pressed", "disabled", "hover_pressed", "focus"]:
		b.add_theme_stylebox_override(key, StyleBoxEmpty.new())
	var art := b.icon.get_size() * MainframeArt.SCALE if b.icon != null else Vector2(LEAVE_ICON, LEAVE_ICON)
	b.custom_minimum_size = art * os
	b.focus_mode = Control.FOCUS_NONE
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	return b
## The facade behind the Mainframe (kept while the page is rebuilt on the same visit).
var _shop_facade: MainframeFacade = null
var _shop_facade_key: String = ""


## The facade for this visit behind the page (made once per visit; the city hides behind it).
func _shop_backdrop(s: NetrunSession) -> MainframeFacade:
	var key := String(_shop_memory.get("key", ""))
	if _shop_facade == null or not is_instance_valid(_shop_facade) or _shop_facade_key != key:
		_drop_shop_backdrop()
		_shop_facade = MainframeFacade.new(MainframeFacade.state_for(key))
		_shop_facade.sign.sequence_index = absi(key.hash()) % MainframeSign.SEQUENCE_ORDER.size()
		_shop_facade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(_shop_facade)
		move_child(_shop_facade, background.get_index() + 1)
		_shop_facade_key = key
	background.visible = false
	return _shop_facade


## Takes the facade away (another screen shows; the city comes back).
func _drop_shop_backdrop() -> void:
	if _shop_facade != null and is_instance_valid(_shop_facade):
		_shop_facade.queue_free()
	_shop_facade = null
	_shop_facade_key = ""
	if background != null:
		background.visible = true


## Places the Mainframe's pieces on the street (global targets on the 1280x720 screen, kept
## on screen at every text size): the pegboard under the bar between the sign and the bin, the
## clerk bottom left, the wheel's hub below the foot, the bin right, LEAVE bottom right, and the
## pencil notes beside what they mean.
func _layout_shop(root: Control) -> void:
	if not is_instance_valid(root) or not root.is_inside_tree():
		return
	var screen := get_viewport_rect().size
	var o := root.global_position
	var top := hud.get_global_rect().end.y
	if _shop_facade != null and is_instance_valid(_shop_facade):
		_shop_facade.top_clear = top + SHOP_SIGN_GAP
	var sign_right := _shop_facade.plate_rect().end.x if _shop_facade != null and is_instance_valid(_shop_facade) else 150.0
	var board := root.get_node_or_null(^"Pegboard") as Control
	var clerk := root.get_node_or_null(^"Clerk") as Control
	var wheel := root.get_node_or_null(^"Slices") as SliceStockWheel
	var bin := root.get_node_or_null(^"RemoveCard") as Control
	var tape := root.get_node_or_null(^"BinTape") as Control
	var leave := root.get_node_or_null(^"LeaveMainframe") as Control
	var icon := root.get_node_or_null(^"LeaveIcon") as Control
	if board == null or clerk == null or wheel == null or bin == null or leave == null:
		return
	board.size = board.get_combined_minimum_size()
	bin.size = bin.get_combined_minimum_size()
	# Between the sign and the bin; over the sign when the words are big (the sign is the world).
	var right_edge := screen.x - SHOP_MARGIN * 2.0 - bin.size.x - SHOP_MARGIN
	clerk.size = clerk.get_combined_minimum_size()
	clerk.global_position = Vector2(SHOP_MARGIN * 2.0, screen.y - SHOP_MARGIN - clerk.size.y)
	var left := sign_right + SHOP_MARGIN
	if clerk.visible and top + SHOP_BOARD_TOP + board.size.y > clerk.global_position.y:
		left = maxf(left, clerk.get_global_rect().end.x + SHOP_MARGIN)  # big words: beside the clerk
	var bx := clampf(SHOP_BOARD_X - board.size.x * 0.5, minf(left, right_edge - board.size.x), right_edge - board.size.x)
	board.global_position = Vector2(maxf(SHOP_MARGIN, bx), top + SHOP_BOARD_TOP)
	leave.size = leave.get_combined_minimum_size()
	if icon != null:
		icon.size = icon.get_combined_minimum_size()
	var icon_w := icon.size.x + SHOP_MARGIN if icon != null else 0.0
	leave.global_position = screen - leave.size - Vector2(SHOP_MARGIN * 2.0 + icon_w, SHOP_MARGIN)
	if icon != null:
		icon.global_position = Vector2(leave.get_global_rect().end.x + SHOP_MARGIN * 0.5, leave.get_global_rect().get_center().y - icon.size.y * 0.5)
	var bin_at := Vector2(screen.x - SHOP_MARGIN * 2.0 - bin.size.x, maxf(SHOP_BIN_AT.y, board.get_global_rect().end.y - bin.size.y * 0.4))
	bin_at.y = minf(bin_at.y, leave.global_position.y - bin.size.y - SHOP_MARGIN)
	bin.global_position = bin_at
	if tape != null:
		tape.size = tape.get_combined_minimum_size()
		tape.global_position = bin_at + Vector2((bin.size.x - tape.size.x) * 0.5, -tape.size.y - 4.0)
	# The hub stays below the screen and the rim below the board (its tags hang over the board's
	# foot), but some wedge always shows.
	var tag_h := SliceStockWheel.TAG_ROOM * Settings.text_scale
	var hub_y := clampf(board.get_global_rect().end.y - tag_h * 0.5 + SliceStockWheel.R_OUT, screen.y + SHOP_HUB_BELOW, screen.y + SliceStockWheel.R_OUT - SHOP_WEDGE_SHOWN)
	wheel.hub = Vector2(SHOP_WHEEL_X, hub_y) - o
	wheel.inner_visible = hub_y - screen.y + SHOP_MARGIN
	wheel.position = Vector2.ZERO
	wheel.size = root.size
	wheel.place_items()
	var spill := root.get_node_or_null(^"SignSpill") as LightSpill
	if spill != null and _shop_facade != null and is_instance_valid(_shop_facade):
		var plate := _shop_facade.plate_rect()
		spill.position = plate.get_center() + _shop_facade.global_position - o
		spill.source_size = plate.size
		spill.reach = SHOP_SPILL_REACH
	var top_note := root.get_node_or_null(^"TopNote") as PencilNote
	if top_note != null:
		var rim := Vector2(SHOP_WHEEL_X, hub_y - SliceStockWheel.R_OUT)
		top_note.size = top_note.custom_minimum_size
		top_note.global_position = rim + Vector2(-SliceStockWheel.R_OUT * 0.95, -top_note.size.y * 0.2)
		top_note.with_arrow(Vector2(top_note.size.x * 0.5, top_note.size.y), Vector2(top_note.size.x * 0.75, top_note.size.y + 34.0), -6.0)
	var bin_note := root.get_node_or_null(^"BinNote") as PencilNote
	if bin_note != null:
		bin_note.size = bin_note.custom_minimum_size
		bin_note.global_position = bin_at + Vector2(-bin_note.size.x - 6.0, bin.size.y * 0.35)
		bin_note.with_arrow(Vector2(bin_note.size.x * 0.6, bin_note.size.y), Vector2(bin_note.size.x + 4.0, bin_note.size.y + 26.0), 6.0)
	# the pencil notes never cover an item or its tag (big words): moved left, else left out
	if top_note != null:
		_shop_note_clear(top_note, root, true)
	if bin_note != null:
		_shop_note_clear(bin_note, root, false)  # it points at the bin: never moved away from it
	var clerk_note := root.get_node_or_null(^"ClerkNote") as PencilNote
	if clerk_note != null:
		clerk_note.size = clerk_note.custom_minimum_size
		var words := clerk.find_child("ClerkWords", true, false) as Control
		var under := words.get_global_rect() if words != null else clerk.get_global_rect()
		# Parity fix (SHOP-01; concept shop_v5): under the last clerk line, offset right of
		# the words' start (clear of the wallet beside it), never over "CYCLES ONLY.".
		var wallet := clerk.find_child("Wallet", true, false) as Control
		var x := under.position.x + under.size.x * CLERK_NOTE_OFFSET
		if wallet != null and wallet.is_visible_in_tree():
			x = maxf(x, wallet.get_global_rect().end.x + SHOP_MARGIN)
		x = minf(x, clerk.get_global_rect().end.x - clerk_note.size.x - SHOP_MARGIN * 0.5)
		clerk_note.global_position = Vector2(x, under.end.y + CLERK_NOTE_GAP)


## ART-9 4A: a v2 terminal (4C's CrtWindow) whose `> TITLE` keeps to one line: the strip widens
## to its title (the Mainframe's clerk, the loot's strips, the event terminal), as round 31-34 draw them.
func _crt_one_line(win: CrtWindow) -> CrtWindow:
	var head := win.find_child("TerminalTitle", true, false) as Label
	if head != null:
		var f := head.get_theme_font(&"font")
		var px := head.get_theme_font_size(&"font_size")
		head.custom_minimum_size.x = ceilf(f.get_string_size(head.text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x) + 2.0
	return win


## Moves a shop pencil note left off any item, tag or the wallet it covers (when `may_move`);
## hides it when no place is clear (a hint, never over what it points at).
func _shop_note_clear(note: PencilNote, root: Control, may_move: bool) -> void:
	var blocks: Array[Rect2] = []
	for n in root.find_children("*", "ShopItem", true, false):
		var it := n as ShopItem
		if it.visible and it.shelf != ShopItem.Shelf.SLICE:
			blocks.append(it.get_global_rect())
		if it.buy_button != null:
			blocks.append(it.buy_button.get_global_rect())
	for n in root.find_children("*", "SpinnerMini", true, false):
		blocks.append((n as Control).get_global_rect())
	for id in ["Wallet", "ShopInfo"]:
		var c := root.find_child(id, true, false) as Control
		if c != null and c.is_visible_in_tree():
			blocks.append(c.get_global_rect())
	note.visible = true
	for i in blocks.size() + 1:
		var r := note.get_global_rect()
		var hit := -1
		for k in blocks.size():
			if r.intersects(blocks[k]):
				hit = k
				break
		if hit < 0:
			return
		var x := blocks[hit].position.x - r.size.x - SHOP_MARGIN
		if not may_move or x < SHOP_MARGIN:
			note.visible = false
			return
		note.global_position.x = x
	note.visible = false
func _shop_shelf_look(item: ShopItem, kind: String, res: Resource, id: StringName) -> void:
	var ts := Settings.text_scale
	match kind:
		"firmware":
			item.on_shelf(ShopItem.Shelf.FIRMWARE, ts, id)
			var fw := res as FirmwareData
			if fw != null:
				item.rarity = fw.rarity
				var fits: PackedStringArray = []
				for t in fw.allowed_slice_types:
					fits.append(tr(String(Palette.SLICE_NAMES.get(t, "?"))))
				item.kind_line = "%s  %s" % [tr(ShopItem.rarity_word(fw.rarity)), " + ".join(fits) if not fits.is_empty() else tr("ANY SLICE")]
			item.with_glyph(ShopItem.glyph_of(kind, id))
		"daemons":
			item.on_shelf(ShopItem.Shelf.DAEMON, ts, id)
			var d := res as DaemonData
			if d != null:
				item.rarity = d.rarity
				item.kind_line = tr(ShopItem.rarity_word(d.rarity))
			item.with_glyph(ShopItem.glyph_of(kind, id))


## The info strip shows `text` (an item's whole text) while `item` is hovered or focused.
func _shop_info_on(item: Control, label: Label, text: String) -> void:
	var show := func() -> void:
		if is_instance_valid(label):
			label.text = "> " + text.replace("\n", "  ")
			label.add_theme_color_override(&"font_color", Palette.TERMINAL_TEXT)
	item.focus_entered.connect(show)
	item.mouse_entered.connect(show)


## The clerk's face on its screen: the concept's pixel grin (shop.clerk_panel, MainframeArt
## "clerk_face"), fitted to the face's box.
func _draw_clerk_face(face: Control) -> void:
	var t := MainframeArt.tex("clerk_face")
	if t == null:
		return
	var k := minf(face.size.x / t.get_size().x, face.size.y / t.get_size().y)
	face.draw_texture_rect(t, Rect2((face.size - t.get_size() * k) * 0.5, t.get_size() * k), false)


## ANIM-R1 M11: the node meta naming a Mainframe item's stock index (SOLD stubs have none).
const STOCK_META := &"stock_index"
## What the Mainframe offered when the player came in (view memory, per visit): "key" (the
## run and node), then each kind's stock.
var _shop_memory: Dictionary = {}


## The Mainframe's stock as first seen on this visit, kind -> ids (taken again when the stock
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


## ANIM-R1 M11: the Mainframe's places for one kind: [id, stock index] for each item first
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


## A bought Mainframe item's place: its object, dimmed, stamped SOLD; not a button any more.
func _sold_stub(title: String, ram: int, index: int, kind: String, cs: float, ts: float) -> ShopItem:
	var stub := ShopItem.new(title, ram, "", index)
	match kind:
		"cards":
			stub.scaled(cs)
		"slices":
			stub.on_shelf(ShopItem.Shelf.SLICE, ts)
	stub.name = "Sold_%s_%d" % [kind, index]
	stub.hotkey = ""
	stub.sold_stub = true
	stub.disabled = true
	stub.focus_mode = Control.FOCUS_NONE
	stub.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stub.tooltip_text = ""
	return stub


## What a shop item does in words (H23 S8: Firmware showed no description): the
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


## A slice tile's size in the Mainframe's SLICES window for `count` tiles at text scale `ts`
## (H24 S10): SLICE_TILE grown with the text as far as the window's width holds the row.
static func slice_tile_size(count: int, ts: float) -> Vector2:
	var room := MAINFRAME_QUAD.x * 0.5 - QUAD_FRAME.x - 8.0 * maxi(0, count - 1)
	var k := clampf(minf(ts, room / maxf(1.0, count * SLICE_TILE.x)), 1.0, Settings.TEXT_SCALE_MAX)
	return Vector2(SLICE_TILE.x * k, SLICE_TILE.y * tile_growth(ts))


## How much taller a Mainframe tile in the lower row grows at text scale `ts` (H24 S10: at 1.6
## the name, the icon and a two-line buy sticker did not fit 130 px).
static func tile_growth(ts: float) -> float:
	return 1.0 + (ts - 1.0) * TILE_GROW


## ANIM-R2 E6: the most a chip ("firmware") or Daemon tile may grow to at text scale `ts`
## with `count` in its row: a Firmware chip shares its window's width (the socket list under
## it), a Daemon widens a little (the SLICES window keeps its row); both may grow as tall
## as the lower row's tiles.
static func chip_tile_room(kind: String, count: int, ts: float) -> Vector2:
	var h := CHIP_TILE.y * tile_growth(ts)
	if kind == "firmware":
		var w := (MAINFRAME_QUAD.x - QUAD_FRAME.x - 10.0 * maxi(0, count - 1)) / maxf(1.0, count)
		return Vector2(maxf(CHIP_TILE.x, minf(w, CHIP_TILE.x * ts)), h)
	return Vector2(CHIP_TILE.x * (1.0 + (ts - 1.0) * DAEMON_WIDEN), h)


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
		if int(parts["rows"]) >= (parts["desc_lines"] as PackedStringArray).size() and int(parts["dfs"]) >= CHIP_READABLE:
			break
		if sz.x < most.x:
			sz.x = minf(sz.x + CHIP_FIT_STEP, most.x)
		elif sz.y < most.y:
			sz.y = minf(sz.y + CHIP_FIT_STEP, most.y)
		else:
			break
	tile.size = sz
	tile.custom_minimum_size = sz


## Opens a modal viewer over the netrun screen. The viewers hold focus themselves
## (UiFocus.hold: the D-pad and A can't reach the Mainframe behind them; focus returns to the
## tile that opened them on close).
func _open_modal(view: Control) -> void:
	add_child(view)
	# ART-0 F (ported from art-pass W8a / W8c, §10): the viewer opens with the modal motion
	# and counts as open, so a page change waits for it to close (`_show_current`).
	PageTransition.open_modal(view)


## Deck viewer in pick mode: the chosen card is removed for the shop's price.
func open_remove() -> void:
	var s := RunManager.netrun
	var view := DeckView.new(s.run.operative.deck, s.lookup, tr("RECYCLE BIN // REMOVE A CARD // %d CYCLES") % s.card_removal_price(), TextDb.mark("REMOVE"))
	view.card_picked.connect(remove_card)
	_open_modal(view)
	# ANIM-4b: the cards drag onto the SHRED tile (select + REMOVE stays).
	view.enable_drops(_modal_layer(view))


## Spinner viewer in pick mode: the chosen slot is overwritten with stock slice `stock_index`.
func open_overwrite(stock_index: int) -> void:
	var s := RunManager.netrun
	var sd := s.lookup.get_content(StringName(String(s.run.shop["slices"][stock_index]))) as SliceData
	var name_text := "%s %d" % [tr(String(Palette.SLICE_NAMES.get(sd.slice_type, "?"))), sd.base_output] if sd != null else "?"
	# The price depends on the slot (the NULL slot costs more): the view shows the picked
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
		chip.tooltip_text = UiTip.fold(drag_tip("install"))
		view.enable_drops(_modal_layer(view), chip, _item_payload("slice", "modal", stock_index, sd.id))


## Mid-run raid interlude (GDD 4.4, 7.3): setup with exact projection, run assets and
## the Armory both deployable, then the playout.
func _show_raid() -> void:
	var s := RunManager.netrun
	var c := s.campaign
	# B3 (review section c): from the run page into the raid, one binary-bits INCOMING transition.
	var from_route := _shown_screen == "route"
	var pending := s.raid_pending()
	var raid := CampaignRules.raid_data(pending, s.lookup)
	var projection := s.raid_projection()
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	# ANIM-R3 B5: set up like the HQ's raid setup (it read as a debug form): the raid's
	# warning, a forecast stamp and the facts as badges, then a row per node.
	var warn := _label(TextDb.t(raid, "warning_text"))
	warn.name = "RaidWarning"
	UiWrap.whole_words(warn)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	box.add_child(warn)
	box.add_child(_raid_forecast(projection))
	var run_assets := s.run_assets()
	# ANIM-4b: the run's assets and the Armory's as chips to drag onto a node's row (the
	# lists and buttons stay); a placed asset's Withdraw drags onto another row or back onto
	# the Armory.
	var chips := VBoxContainer.new()
	chips.name = "RaidAssets"
	box.add_child(chips)
	var armory_row: Control = null
	if run_assets.is_empty() and c.armory.is_empty():
		# Parity RAID-14 (the M13 build's designed empty state, art pass W8c): nothing to deploy
		# says why in one line (the two bare "none" captions read as a list that failed to load).
		armory_row = _empty_assets_note()
		chips.add_child(armory_row)
	else:
		var run_row := HFlowContainer.new()
		run_row.name = "RunAssetChips"
		run_row.add_theme_constant_override("h_separation", 8)
		chips.add_child(run_row)
		run_row.add_child(_label(tr("RUN ASSETS:")))
		for i in run_assets.size():
			run_row.add_child(_asset_chip("RunAsset_%d" % i, run_assets[i]))
		if run_assets.is_empty():
			run_row.add_child(_none_label())  # ANIM-R6 C15: never an empty caption
		armory_row = HFlowContainer.new()
		armory_row.name = "ArmoryChips"
		armory_row.add_theme_constant_override("h_separation", 8)
		chips.add_child(armory_row)
		armory_row.add_child(_label(tr("ARMORY:")))
		for i in c.armory.size():
			armory_row.add_child(_asset_chip("Armory_%d" % i, c.armory[i]))
		if c.armory.is_empty():
			armory_row.add_child(_none_label())
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
			withdraw.tooltip_text = UiTip.fold(tr("Back to the Armory.") + " " + drag_tip("withdraw"))
			row.add_child(withdraw)
		if c.grid.is_active_node(site_id):
			if not run_assets.is_empty():
				var pick := OptionButton.new()
				for a in run_assets:
					pick.add_item(tr("run: %s") % _content_name(a))
				row.add_child(pick)
				var sid2 := site_id
				row.add_child(_button(tr("Deploy run asset"), func() -> void: raid_deploy_run_asset(pick.selected, sid2)))
			if not c.armory.is_empty():
				var pick2 := OptionButton.new()
				for a in c.armory:
					pick2.add_item(tr("armory: %s") % _content_name(a))
				row.add_child(pick2)
				var sid3 := site_id
				row.add_child(_button(tr("Deploy armory asset"), func() -> void: raid_deploy_armory(pick2.selected, sid3)))
		box.add_child(row)
	# Parity RAID-14: START DEFENSE is the raid's pink vinyl sticker, as on every other raid page
	# (the HQ's DEFENCE slot): one sticker verb on the screen, at the window's foot.
	# (the run end's VinylButton: the same 1B vinyl as the HQ's RaidSticker, whose die-cut came
	# out narrower than its word on this page)
	var run_btn := VinylButton.new(TextDb.mark(START_DEFENSE), VinylSticker.Fill.PINK, START_STICKER_STEP)
	run_btn.name = "StartDefense"
	run_btn.size_flags_horizontal = Control.SIZE_SHRINK_END
	run_btn.pressed.connect(raid_fight)
	run_btn.tooltip_text = UiTip.fold(tr("Start the defence: the raid plays out on the map; the result matches the forecast."))
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
	# The window over its verb: START DEFENSE under the window's right corner, off the glass (in
	# the window the terminal's own type sizes cut the vinyl's lettering).
	var left_col := VBoxContainer.new()
	left_col.name = "RaidColumn"
	left_col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	left_col.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	left_col.add_theme_constant_override("separation", roundi(UiTheme.SP_S * Settings.text_scale))
	left_col.add_child(win)
	left_col.add_child(run_btn)
	root.add_child(left_col)
	var area := Control.new()
	area.name = "RaidMapArea"
	area.mouse_filter = Control.MOUSE_FILTER_IGNORE
	area.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(area)
	_set_panel(root, false)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Parity RAID-13: the raid's own map (the HQ's raid view: the Cell's network as raid sockets,
	# the Sites the threats really take, their routes in red pencil) on the 3D city.
	var g := raid_map_graph(projection, c)
	_mount_route(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, raid_min_zoom(), RAID_MAP_ANCHOR, Vector2.INF, true)
	_mount_raid_routes(RaidMapNodes.route_paths(projection.events))
	city_overlay.avoid_controls([win, run_btn])
	_raid_map_area = area
	_frame_raid_map.call_deferred()
	if from_route:
		RaidIncoming.play(self)
	# ANIM-R5 P2: behind the setup (after its own view), the playout's fights; on the 3D city
	# (parity RAID-13) there is nothing to bake.
	if not background.city3d:
		_prebake_raid_playout.call_deferred(c, null)
	_register_raid_drops(run_assets, armory_row)


## ANIM-R6 C15 (city agent, a small change here): what an empty RUN ASSETS: / ARMORY: row
## says (a naive player read the bare captions as a list that failed to load).
func _none_label() -> Label:
	var l := _label(tr(NONE_WORD))
	l.name = "NoAssets"
	l.add_theme_color_override("font_color", Color(Palette.PAPER, 0.6))
	return l


const NONE_WORD := "none" # TR
## Parity RAID-14: the interlude's empty state (the M13 build's words) and START DEFENSE's
## lettering (the HQ's setup letters its sticker at the TITLE step).
const NO_ASSETS_WORDS := "No assets to deploy: this run carries none and the Armory is empty. Your nodes hold with what is on them." # TR
const START_STICKER_STEP := UiTheme.TITLE


## Parity RAID-14 (ported from art-m13-final netrun_scene.gd `_empty_assets_note`, art pass W8c
## critique 28; v2 words in the terminal's mid ink): nothing to deploy, in one line with the
## Armory's icon, never bare "RUN ASSETS:" / "ARMORY:" captions.
func _empty_assets_note() -> Control:
	var row := HBoxContainer.new()
	row.name = "NoAssets"
	row.add_theme_constant_override("separation", UiTheme.SP_S)
	var side := UiTheme.BASE_SIZE * Settings.text_scale * IconMark.SIZE_FACTOR
	row.add_child(IconMark.standalone(StatIcon.ARMORY, side, Palette.TEXT_MID))
	var l := _label(tr(NO_ASSETS_WORDS))
	l.name = "NoAssetsWords"
	UiWrap.whole_words(l)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.add_theme_color_override("font_color", Palette.TEXT_MID)
	row.add_child(l)
	return row


## Parity RAID-13: the mid-run raid's map as the HQ's raid view draws it (S-MAPVIEW's major
## nodes only): the Cell's network as raid sockets (`RaidSocket`: glyph, state, health, the
## forecast ring of `results` when it is the setup's projection), every Site the raid's threats
## really take, the links among them; the threat routes are the pencil's (`_mount_raid_routes`).
## `results`: the projection (setup) or {} (the playout, from the pre-raid `c`).
func raid_map_graph(results: Variant, c: CampaignState) -> Dictionary:
	var corp := RunManager.corporation
	var routes := RaidMapNodes.shown_routes(results, c, corp, RunManager.config(), RunManager.lookup())
	var g := CityLayout.grid_graph(c, corp, routes)
	var nodes_res: Dictionary = (results as RaidResolver.RaidResult).nodes if results is RaidResolver.RaidResult else results
	var network := RaidMapNodes.major_ids(c, routes, nodes_res)
	var nodes: Array[Dictionary] = []
	for n in g["nodes"]:
		if not network.has(n["id"]):
			continue
		n["label"] = _site_name(n["id"])
		n["assets"] = c.grid.assets_on(n["id"])
		n["threat_corp"] = String(c.corporation_id)
		if c.grid.is_claimed(n["id"]) or n["id"] == c.grid.home_site_id:
			n["socket"] = raid_socket_spec(n["id"], nodes_res.get(String(n["id"]), {}), results is RaidResolver.RaidResult, c)
		nodes.append(n)
	var edges: Array[Dictionary] = []
	for e in g["edges"]:
		if network.has(e["a"]) and network.has(e["b"]):
			if e.get("arrows", false):
				e["pencil"] = true
			edges.append(e)
	return {"nodes": nodes, "edges": edges}


## Parity RAID-13: claimed node `site_id`'s raid socket (RaidSocket spec, as the HQ's raid view
## builds it: both call `RaidMapNodes.socket_spec`): its type's glyph, its state, its health
## now and the projected outcome as a forecast ring (`forecast`: `res` is the projection's).
static func raid_socket_spec(site_id: StringName, res: Dictionary, forecast: bool, c: CampaignState) -> Dictionary:
	return RaidMapNodes.socket_spec(site_id, res, forecast, c)  # FIX-REDS-3: one builder, shared with the HQ


## Parity RAID-13 (ART-6 3A): the raid's threat routes (Site id paths) in red pencil on the map,
## with the stationed operatives' beacons.
func _mount_raid_routes(paths: Array[Array]) -> void:
	if city_overlay == null or not is_instance_valid(city_overlay):
		return
	var routes := RaidRouteLayer.new(city_overlay)
	city_overlay.add_child(routes)
	city_overlay.add_child(RaidBeaconLayer.new(city_overlay))
	routes.set_routes(paths, entering)


## Parity RAID-13: the raid map's closest and furthest zoom: the raid band's ortho range on the
## 3D city (`raid_fit_min` / `raid_fit_max`, as the HQ's raid views), the 2D city's own else.
func raid_zoom() -> float:
	return RaidZoomFit.zoom_of(CityView3D.CONFIG.raid_fit_min, size.x) if background != null and background.city3d else RAID_ZOOM


func raid_min_zoom() -> float:
	return RaidZoomFit.zoom_of(CityView3D.CONFIG.raid_fit_max, size.x) if background != null and background.city3d else RAID_MIN_ZOOM


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


## A raid interlude's asset chip (ANIM-4b): a taped note with the asset's name that only
## moves (a press picks it up, as the HQ's crew chips).
func _asset_chip(chip_name: String, asset: StringName) -> Button:
	var b := Button.new()
	b.name = chip_name
	b.theme_type_variation = &"NoteButton"
	b.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	b.text = _content_name(asset)
	b.tooltip_text = UiTip.fold(drag_tip("asset"))
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


## ANIM-R5 B3 / ART-11 4D (ART_BIBLE v2 §1.2): the run's end over the city: the Cell's own CRT
## window in the middle of the screen (cyan for a run that jacked out, red for a loss) with the
## verdict slapped on the glass as a vinyl sticker (JACKED OUT yellow; FLATLINED, HOME FELL
## red; 1B's `sticker_slap`), what happened to the operative (a flatline is for good: GDD 4.2
## permadeath), the run in numbers and why Heat rose, then BACK TO HQ, the screen's one pink
## verb. HOME FELL hands over to the HQ's campaign lost lock.
const END_WIDTH := 600.0
const END_GROW := 1.3
## The verdict sticker's lettering (type step) and tilt (degrees).
const END_VERDICT_STEP := UiTheme.HEADING
const END_VERDICT_TILT := -6.0
## BACK TO HQ's lettering (type step).
const END_BACK_STEP := UiTheme.TITLE
## B5 fix 4: the room kept past BACK TO HQ's last letter for its focus fold (two no-break spaces).
const END_BACK_FOLD_ROOM := "\u00a0\u00a0"
## Parity END-01 (the build's RunEndStage, art pass W8c): the operative's Polaroid at text scale
## 1 (px; it grows to END_GROW) and its tilt (degrees), how far down the print the verdict
## sticker is slapped (share of its height), and the lost run's grey city (screen shader: the
## city greyed and darkened by END_GREY_DIM).
const END_PHOTO := Vector2(132, 160)
const END_PHOTO_TILT := -3.0
const END_VERDICT_OVER := 0.55
const END_GREY_SHADER := preload("res://shaders/screen_grey.gdshader")
const END_GREY_DIM := 0.35


## Parity END-01 / END-02: the operative's Polaroid with the verdict sticker slapped over its
## lower half (never over its caption's line), centred over each other.
func _end_photo(photo: Polaroid, verdict: Control) -> Control:
	var box := Control.new()
	box.name = "RunEndPhoto"
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(photo)
	box.add_child(verdict)
	var lay := func() -> void:
		if not is_instance_valid(box) or not is_instance_valid(photo) or not is_instance_valid(verdict):
			return
		var ps := photo.get_combined_minimum_size()
		var vs := verdict.get_combined_minimum_size()
		box.custom_minimum_size = Vector2(maxf(ps.x, vs.x), maxf(ps.y, ps.y * END_VERDICT_OVER + vs.y))
		photo.size = ps
		photo.position = Vector2((box.size.x - ps.x) * 0.5, 0.0)
		photo.pivot_offset = ps * 0.5
		verdict.size = vs
		verdict.position = Vector2((box.size.x - vs.x) * 0.5, ps.y * END_VERDICT_OVER)
	box.resized.connect(lay)
	verdict.minimum_size_changed.connect(lay)
	lay.call()
	return box


func _show_end() -> void:
	var s := RunManager.netrun
	var won := s.run.outcome == RunState.Outcome.COMPLETED
	var aborted := s.run.outcome == RunState.Outcome.ABORTED
	var col := Palette.NET_CYAN if won else Palette.HARM
	var title := tr("NETRUN COMPLETE") if won else (tr("NETRUN ABORTED - the home server fell") if aborted else tr("NETRUN FAILED - operative lost"))
	var report := TerminalWindow.new(title, col)
	report.name = "RunReport"
	report.custom_minimum_size.x = END_WIDTH * minf(Settings.text_scale, END_GROW)
	# Parity END-01 / END-02 (the M13 build's run end, art pass W8c, reworked in v2): beside the
	# report, the operative's Polaroid with the verdict sticker slapped over its foot (a flatline
	# greys the print and strikes it out in red pencil, 4B's KIA), BACK TO HQ under it.
	var head := HBoxContainer.new()
	head.name = "RunEndRow"
	head.add_theme_constant_override("separation", roundi(UiTheme.SP_L * Settings.text_scale))
	# The verdict: a sticker, display only (no focus; its tooltip says what it means).
	var stamp := VinylSticker.new()
	stamp.name = "ResultStamp"
	stamp.text = tr(end_verdict(s.run.outcome))
	stamp.fill = VinylSticker.Fill.YELLOW if won else VinylSticker.Fill.RED
	stamp.font_step = END_VERDICT_STEP
	stamp.focus_mode = Control.FOCUS_NONE
	stamp.mouse_filter = Control.MOUSE_FILTER_PASS
	stamp.tooltip_text = UiTip.fold(end_fate(s))
	# A container resets a child's tilt when it lays it out: the sticker's holder tilts it.
	var tilted := TiltBox.new(END_VERDICT_TILT, stamp)
	var op := s.run.operative
	var photo := Polaroid.new(op.name, "[PORTRAIT]", END_PHOTO_TILT)
	photo.name = "RunEndPolaroid"
	photo.custom_minimum_size = END_PHOTO * minf(Settings.text_scale, END_GROW)
	photo.set_operative(op.class_id, op.id)
	photo.kia = s.run.outcome == RunState.Outcome.DIED
	var side_col := VBoxContainer.new()
	side_col.name = "RunEndSide"
	side_col.alignment = BoxContainer.ALIGNMENT_CENTER
	side_col.add_theme_constant_override("separation", roundi(UiTheme.SP_M * Settings.text_scale))
	side_col.add_child(_end_photo(photo, tilted))
	head.add_child(side_col)
	var col_box := VBoxContainer.new()
	col_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col_box.add_theme_constant_override("separation", 10)
	report.body.add_child(col_box)
	head.add_child(report)
	# What happened to the operative, in words (a flatline is permanent).
	var fate := _label(end_fate(s))
	fate.name = "RunFate"
	UiWrap.whole_words(fate)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	fate.add_theme_color_override("font_color", Palette.TERMINAL_TEXT)
	col_box.add_child(fate)
	# The run in numbers as the top bar's paper tags (H20: no text summary).
	var tags := HudStats.new()
	tags.name = "RunTags"
	tags.items = [[TextDb.mark("COMBATS"), str(s.run.combats_won), "", tr("Fights won this run.")],
		[TextDb.mark("ELITES"), str(s.run.elites_defeated), "", tr("Elite fights won.")],
		[TextDb.mark("CYCLES"), str(s.run.cycles), "", tr("Cycles in hand when the run ended.")],
		[TextDb.mark("BANKED"), str(s.run.banked_schematics), "", tr("Schematics the run banked for the campaign.")],
		[TextDb.mark("HEAT"), TextDb.signed(s.run.heat_gained), "", tr("Heat the run added (campaign Heat is now %d).") % s.campaign.heat]]
	# The least room the tags need; they grow with the text size where the window allows.
	tags.custom_minimum_size.x = tags.compact_width(1.0)
	col_box.add_child(tags)
	# Why Heat rose, beside the HEAT tag's number.
	var why := HBoxContainer.new()
	why.name = "HeatReason"
	why.add_theme_constant_override("separation", 6)
	var side := UiTheme.BASE_SIZE * Settings.text_scale * IconMark.SIZE_FACTOR
	why.add_child(IconMark.standalone(StatIcon.HEAT, side, StatIcon.color_of(StatIcon.HEAT)))
	var why_text := _label(heat_reason(s))
	why_text.name = "HeatReasonText"
	UiWrap.whole_words(why_text)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	why_text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	why.add_child(why_text)
	col_box.add_child(why)
	# BACK TO HQ: the screen's one verb, a pink sticker under the verdict.
	var foot := HBoxContainer.new()
	foot.name = "RunEndFoot"
	foot.alignment = BoxContainer.ALIGNMENT_CENTER
	side_col.add_child(foot)
	var back := VinylButton.new(TextDb.mark("Back to HQ"), VinylSticker.Fill.PINK, END_BACK_STEP)
	back.name = "BackToHq"
	# Art director (B5 fix 4): BACK TO HQ is the page's first focus, so it shows its peel-back; the sticker keeps the
	# fold's room past its last letter (a no-break space of the sticker's own lettering) so the whole word shows.
	back.sticker.text += END_BACK_FOLD_ROOM
	back.pressed.connect(finish_run)
	back.tooltip_text = UiTip.fold(tr("Back to HQ: the campaign, the City Grid and the crew."))
	foot.add_child(back)
	# In the middle of the screen, the city round it (a page of windows, not a glass sheet);
	# parity END-01: a lost run (FLATLINED, HOME FELL) greys the city behind it (the build's
	# flatline context; a clean exit keeps its colour).
	var page := Control.new()
	page.name = "RunEndPage"
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	page.size_flags_vertical = Control.SIZE_EXPAND_FILL
	if not won:
		var grey := ColorRect.new()
		grey.name = "GreyCity"
		grey.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var mat := ShaderMaterial.new()
		mat.shader = END_GREY_SHADER
		mat.set_shader_parameter(&"dim", END_GREY_DIM)
		grey.material = mat
		page.add_child(grey)
		grey.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var wrap := CenterContainer.new()
	wrap.name = "RunEnd"
	wrap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.add_child(wrap)
	wrap.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	wrap.add_child(head)
	page.custom_minimum_size = head.get_combined_minimum_size()
	head.minimum_size_changed.connect(func() -> void:
		if is_instance_valid(page) and is_instance_valid(head):
			page.custom_minimum_size = head.get_combined_minimum_size())
	_set_panel(page, false)
	if entering:
		# The verdict slaps onto the glass (a pop from big; at rest at once when it does not play).
		_slap_verdict.call_deferred(stamp)


## The run end's verdict sticker slaps on (1B's `sticker_slap`) once laid out.
func _slap_verdict(stamp: VinylSticker) -> void:
	if is_instance_valid(stamp) and stamp.is_inside_tree():
		stamp.slap()


## ANIM-R5 B3: the run's verdict as its stamp says it (a key).
static func end_verdict(outcome: int) -> String:
	match outcome:
		RunState.Outcome.COMPLETED:
			return "JACKED OUT" # TR
		RunState.Outcome.ABORTED:
			return "HOME FELL" # TR
	return "FLATLINED" # TR


## ANIM-R6 B5: the run end's top bar title, as its verdict says it (a key).
static func end_title(outcome: int) -> String:
	match outcome:
		RunState.Outcome.COMPLETED:
			return "NETRUN // JACK OUT" # TR
		RunState.Outcome.ABORTED:
			return "NETRUN // HOME FELL" # TR
	return "NETRUN // FLATLINED" # TR


## ANIM-R5 B3: what the run's end means for the operative, in words (translated): a
## flatline is for good (GDD 4.2: permadeath, unbanked loot lost, banked Schematics kept).
static func end_fate(s: NetrunSession) -> String:
	var who := s.run.operative.name
	match s.run.outcome:
		RunState.Outcome.COMPLETED:
			return TranslationServer.translate("%s is back at HQ, healed, keeping the deck, Firmware and Daemons. Unspent Cycles became Schematics.") % who
		RunState.Outcome.ABORTED:
			return TranslationServer.translate("The home server fell: the campaign is lost.")
	return TranslationServer.translate("%s is gone for good (permadeath): an operative who flatlines never comes back. Banked Schematics are kept; Cycles and unbanked loot are lost.") % who


## ANIM-R5 B3: why the run added its Heat, one line (translated): the flatline's share (the
## session's own Heat event for it) and the rest from the route and its events.
static func heat_reason(s: NetrunSession) -> String:
	var total := s.run.heat_gained
	if total == 0:
		return TranslationServer.translate("Heat +0: this run added no Heat.")
	var death := -1
	for e in s.last_events:
		if String(e.get("type", "")) == "heat" and String(e.get("reason", "")) == DEATH_HEAT_REASON:
			death = int(e.get("amount", 0))
	var signed := TextDb.signed(total)
	if s.run.outcome != RunState.Outcome.DIED:
		return TranslationServer.translate("Heat %s: from the route's nodes and events.") % signed
	if death < 0:
		return TranslationServer.translate("Heat %s: flatlined on a run (and the route before it).") % signed
	if death >= total:
		return TranslationServer.translate("Heat %s: flatlined on a run.") % signed
	return TranslationServer.translate("Heat %s: %s for flatlining on a run, %s from the route's nodes and events.") % [signed, TextDb.signed(death), TextDb.signed(total - death)]


## The reason the session gives the Heat a flatline adds (NetrunSession._die).
const DEATH_HEAT_REASON := "operative death"


# --- Drag and drop (Animation pass ANIM-4b) --------------------------------------------------
# Every item a run moves between places drags there too, as on the HQ (ANIM-4's DropLayer):
# Mainframe purchases onto the deck, a slot or the Daemons, deck cards onto the shredder, loot
# onto the deck, a slot or the Daemons, event rewards onto the deck or the Daemons, raid
# assets onto nodes. A drop is an intent: `_on_dropped` makes the same call the item's
# button makes (Signal Up, Call Down). Whether a target takes an item is the rules' own
# answer, asked of a copy of the run and the campaign (`_dry`): nothing here decides a rule.

## What an item's tooltip adds about dragging it, by item kind (keys).
const DRAG_TIPS := {"card": "Or drag it onto the CARDS tag: the card goes into your deck.", # TR
	"chip": "Or drag it onto a slot of your spinner: the chip goes into that slot.", # TR
	"daemon": "Or drag it onto the DAEMONS icon: the Daemon is installed.", # TR
	"slice": "Or drag it onto a slot of your spinner: the slice overwrites that slot."} # TR
## ART-0 F (ported from art-pass W8c / W9F, ART_BIBLE v1 §6.8, §12): the drag lines of the
## other drag items (mouse words; DRAG_TIPS_PAD has each for a pad).
const DRAG_TIPS_MORE := {"install": "Drag it onto a slot to overwrite that slot (or press it, then pick the slot).", # TR
	"withdraw": "Or drag it onto another node's row to move it there.", # TR
	"asset": "Drag it onto a node's row to deploy it there (or press it, then pick the row).", # TR
	"spinner": "Drag Firmware or a slice onto a slot to put it there.", # TR
	"socket": "Dragging a chip onto a slot of the small spinner picks it too.", # TR
	"loot_socket": "Dragging it onto a slot of the small spinner picks it too."} # TR
## ART-0 F: the same lines for a pad player (never "click" or "drag": the pick-up button
## carries the item, the D-pad aims, A drops).
const DRAG_TIPS_PAD := {"card": "Or pick it up and move it onto the CARDS tag: the card goes into your deck.", # TR
	"chip": "Or pick it up and move it onto a slot of your spinner: the chip goes into that slot.", # TR
	"daemon": "Or pick it up and move it onto the DAEMONS icon: the Daemon is installed.", # TR
	"slice": "Or pick it up and move it onto a slot of your spinner: the slice overwrites that slot.", # TR
	"install": "Pick it up and move it onto a slot to overwrite that slot (or press it, then pick the slot).", # TR
	"withdraw": "Or pick it up and move it onto another node's row to move it there.", # TR
	"asset": "Pick it up and move it onto a node's row to deploy it there (or press it, then pick the row).", # TR
	"spinner": "Pick up Firmware or a slice and move it onto a slot to put it there.", # TR
	"socket": "Picking a chip up and moving it onto a slot of the small spinner picks it too.", # TR
	"loot_socket": "Picking it up and moving it onto a slot of the small spinner picks it too."} # TR


## ART-0 F (ported from art-pass W8c / W9F): the drag line of item kind `kind` in the words
## of the device in use (UiTip.for_input), translated; "" for an unknown kind.
func drag_tip(kind: String) -> String:
	var mouse := String(DRAG_TIPS.get(kind, DRAG_TIPS_MORE.get(kind, "")))
	if mouse == "":
		return ""
	return UiTip.for_input(tr(mouse), tr(String(DRAG_TIPS_PAD.get(kind, mouse))))

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
	# B5 (review section f): a bar without CARDS (the Mainframe): the deck is behind VIEW LOADOUT.
	if hud.loadout_button.is_visible_in_tree():
		return hud.loadout_button.get_global_rect()
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


## The running operative's small spinner (the Mainframe and a Firmware loot: its slots are
## where chips and slices go), each slot's pad named as the socket lists name it.
func _spinner_mini() -> SpinnerMini:
	var op := RunManager.netrun.run.operative
	var tips: Array = []
	for k in op.slot_slice_ids.size():
		tips.append(slot_name(op, k))
	var mini := SpinnerMini.new(op.slot_slice_ids, op.slot_firmware_ids, RunManager.lookup(), tips)
	mini.tooltip_text = UiTip.fold(tr("Your spinner.") + " " + drag_tip("spinner"))
	return mini


## A drag payload for item `index` of `kind` ("card", "chip", "daemon", "slice") from `src`
## ("shop", "loot", "event", "modal"): purchases land shrinking into their target with
## SOLD (`drop_buy`), loot and event items without it.
func _item_payload(kind: String, src: String, index: int, item: StringName) -> Dictionary:
	var p := {"kind": kind, "src": src, "index": index, "item": item, "motion": &"drop_buy", "land": "buy"}
	if src in ["shop", "modal"]:
		p["stamp"] = tr("SOLD")
	return p


## ART-0 C: LEAVE_AT, or just under the REMOVE A CARD row's pieces it would cover.
func _place_leave(leave: Control, icon: Control, row: Control, root: Control) -> void:
	if not is_instance_valid(leave) or not is_instance_valid(row) or not row.is_inside_tree():
		return
	var at := LEAVE_AT
	var span := Vector2(root.global_position.x + at.x, root.global_position.x + at.x + leave.size.x)
	for c in row.get_children():
		var r := (c as Control).get_global_rect()
		if r.end.x > span.x and r.position.x < span.y:
			at.y = maxf(at.y, r.end.y - root.global_position.y + LEAVE_GAP)
	leave.position = at
	icon.position = at + Vector2(-LEAVE_ICON - 4.0, 4.0)


## Parity SHOP-06: the line that names the socket choice: "Chips go into:" and the chosen slot
## in words (it follows the spinner's choice); `tip` says what it is for.
func _socket_row(mini: SpinnerMini, tip: String) -> Control:
	var op := RunManager.netrun.run.operative
	var row := HFlowContainer.new()
	row.name = "SocketRow"
	row.add_theme_constant_override("h_separation", 6)
	var word := _label(tr("Chips go into:"))
	word.name = "SocketWord"
	word.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	word.tooltip_text = UiTip.fold(tip)
	word.mouse_filter = Control.MOUSE_FILTER_PASS
	row.add_child(word)
	var choice := _label(slot_name(op, mini.selected()))
	choice.name = "SocketChoice"
	choice.add_theme_color_override(&"font_color", Palette.CELL_ACID)
	choice.add_theme_font_override(&"font", Palette.mono())
	choice.tooltip_text = word.tooltip_text
	choice.mouse_filter = Control.MOUSE_FILTER_PASS
	row.add_child(choice)
	mini.tooltip_text = word.tooltip_text
	mini.slot_chosen.connect(func(k: int) -> void:
		if is_instance_valid(choice):
			choice.text = slot_name(op, k))
	return row


## Parity SHOP-06 (round 34 `firmware_socket`): while Firmware chip `item` (id `id`) is pointed
## at or focused, the spinner greys the slots it cannot go into (the rules' own answer); off it,
## the marks clear.
func _mark_socket_fits(item: Control, mini: SpinnerMini, id: StringName) -> void:
	var on := func() -> void:
		if is_instance_valid(mini):
			mini.set_fits(socket_fits(id))
	var off := func() -> void:
		if is_instance_valid(mini):
			mini.set_fits([] as Array[bool])
	item.mouse_entered.connect(on)
	item.focus_entered.connect(on)
	item.mouse_exited.connect(off)
	item.focus_exited.connect(off)


## Parity SHOP-06: which slots of the running operative's spinner Firmware `id` goes into, by
## the socket rule itself (`NetrunSession.firmware_slot_error`, read-only): where it fits, not
## whether it is affordable (its price tag says that).
static func socket_fits(id: StringName) -> Array[bool]:
	var out: Array[bool] = []
	var s := RunManager.netrun
	if s == null:
		return out
	for k in s.run.operative.slot_slice_ids.size():
		out.append(s.firmware_slot_error(id, k) == "")
	return out


## Mainframe: cards drag onto the deck, Firmware onto a slot of the small spinner, Daemons
## onto the DAEMONS icon, slice upgrades onto the slot they overwrite.
func _register_shop_drops(mini: SpinnerMini, fw_slot: SpinnerMini) -> void:
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
func _register_loot_drops(row: Control, mini: SpinnerMini, slot_option: SpinnerMini) -> void:
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
		b.tooltip_text += "\n" + drag_tip(kind)
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
## speak in ids: "barbed_wire does not fit a SHIM slice.").
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
			# In the UPGRADE viewer: select the slot and press UPGRADE; on the Mainframe page the
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
## CYCLES tag (and the Mainframe's wallet) go red with "PRICE > CYCLES" under them.
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
		text += " || Run T%d seed %d | %s HP %d/%d Rank %d | Cycles %d | banked %d | node %s" % [s.run.tier, s.run.run_seed, op.name, _shown_operative_hp(op.hp), op.max_hp, op.rank, s.run.cycles, s.run.banked_schematics, s.run.current_node_id]
	_status.text = text
	# Every tag says what it means on hover (H21 #9); its icon is the resource's own.
	# HEAT-ALL (designer ruling Q1 / Q2): Heat is the gauge in the bar's first slot on every screen
	# (the HEAT stat tag gave it its place); in a run it opens the Heat terminal read-only.
	var cfg := RunManager.resolver.config
	hud.set_heat(c.heat if hud_heat_shown < 0 else hud_heat_shown, cfg.heat_max, HeatRules.band_levels(c, cfg), true, heat_tip())
	var stats := [[TextDb.mark("SCHEMATICS"), str(c.schematics), "", tr("Schematics: the campaign's currency, spent at HQ.")]]
	# H24 S16: whose numbers these are: the campaign's, then this run's.
	var captions := [[0, tr("CAMPAIGN"), tr("The campaign's numbers: they stay between runs.")]]
	if route_strip_only(s) and _held_bar.is_empty():  # B5: a leaving loot page keeps its own strip (its pick flies to CARDS)
		# B3 (round 44 `topbar_by_page.png`): the route page's strip is Heat (the gauge), HP and
		# Cycles; the rest is behind VIEW LOADOUT and the Heat terminal.
		var hop := s.run.operative
		stats = [[TextDb.mark("HP"), str(_shown_operative_hp(hop.hp)), "/%d" % hop.max_hp, tr("%s's HP. At 0 the operative flatlines.") % hop.name],
			[TextDb.mark("CYCLES"), str(s.run.cycles), "", tr("Cycles: this run's money, spent in the Mainframe.")]]
		captions = []
	elif s != null and not s.run.is_over():
		var op := s.run.operative
		captions.append([stats.size(), tr("THIS RUN"), tr("This run's numbers: the operative's HP, the Cycles to spend, the deck, rank and what the run has banked.")])
		stats.append_array([[TextDb.mark("HP"), str(_shown_operative_hp(op.hp)), "/%d" % op.max_hp, tr("%s's HP. At 0 the operative flatlines.") % op.name],
			[TextDb.mark("CYCLES"), str(s.run.cycles), "", tr("Cycles: this run's money, spent in the Mainframe.")],
			[TextDb.mark("CARDS"), str(op.deck.size()), "", tr("Cards in %s's deck (VIEW LOADOUT shows them).") % op.name],
			[TextDb.mark("RANK"), str(op.rank), "", tr("Rank: runs survived. It brings wheel upgrades and higher netrun tiers.")],
			[TextDb.mark("BANKED"), str(s.run.banked_schematics), "", tr("Schematics this run has banked for the campaign.")],
			[TextDb.mark("CREW"), str(c.living_operatives().size()), "", tr("The crew still standing.")]])
	# B5 (review section f, round 44 `topbar_by_page.png`): each netrun page's bar shows only what it is about (the
	# Heat gauge stays on every page, designer ruling Q1); everything else is behind VIEW LOADOUT.
	var keys := _held_bar if not _held_bar.is_empty() else bar_keys(s)
	if _held_bar.is_empty() and s != null and not s.run.is_over() and s.run.phase == RunState.Phase.MAP and not route_strip_only(s):
		keys = [BAR_ALL]  # B3: GRID VIEW and a boss run's compound keep the whole strip
	if not keys.has(BAR_ALL):
		stats = stats.filter(func(st: Array) -> bool: return keys.has(String(st[0])))
		captions = []
	elif s != null and not s.run.is_over():
		stats.pop_back()  # CREW: only the event's bar names it
	hud.set_stats(stats, captions)
	hud.loadout_button.visible = s != null and not s.run.is_over()
	if s != null and not s.run.is_over():
		hud.set_daemons(s.run.operative.daemon_ids)


## B5 (review section f): the bar's tags a netrun page shows (keys; BAR_ALL: the full bar): the route and transit
## Heat, HP and Cycles; the Mainframe its Cycles; the loot the deck when a card is on offer; an event what its
## choices change.
static func bar_keys(s: NetrunSession) -> Array:
	if s == null or s.run.is_over():
		return [BAR_ALL]
	match s.run.phase:
		RunState.Phase.MAP:
			return ["HP", "CYCLES"]
		RunState.Phase.SHOP:
			return ["CYCLES"]
		RunState.Phase.REWARD:
			return ["CARDS"] if String(s.current_reward().get("kind", "")) == "card" else []
		RunState.Phase.EVENT:
			return event_bar_keys(s)
	return [BAR_ALL]


## The bar's full set (every tag).
const BAR_ALL := "*"
## B5: the keys of the page still on show while it leaves (a loot pick's flight); empty: the page's own.
var _held_bar: Array = []
## An event's outcome kinds -> the bar tag that shows them.
const EVENT_BAR_TAGS := {StatIcon.HP: "HP", StatIcon.CYCLES: "CYCLES", StatIcon.OPERATIVE: "CREW", StatIcon.SCHEMATICS: "SCHEMATICS",
	StatIcon.CARDS: "CARDS"}


## The tags an event's choices change (in the bar's order), from the rules' own preview (OutcomeRow.of_choice).
static func event_bar_keys(s: NetrunSession) -> Array:
	var ev := s.current_event()
	var seen := {}
	if ev != null:
		for c in ev.choices:
			for it in OutcomeRow.of_choice(s, c):
				var tag: String = EVENT_BAR_TAGS.get(it.get("kind", &""), "")
				if tag != "":
					seen[tag] = true
	var out: Array = []
	for k in ["SCHEMATICS", "HP", "CYCLES", "CARDS", "CREW"]:
		if seen.has(k):
			out.append(k)
	return out

## B3: true when the top strip shows only the route page's numbers (HP, Cycles; Heat is the
## gauge): the run's own route on the map (not GRID VIEW, not a boss run's compound).
func route_strip_only(s: NetrunSession) -> bool:
	return s != null and not s.run.is_over() and s.run.phase == RunState.Phase.MAP and route_on_map(s)


## ANIM-R6 A5 (combat, a minimal change here): the operative's HP for the top bar: during a
## fight, the fight's (the run's is written only when it ends), as its replay has landed it.
func _shown_operative_hp(run_hp: int) -> int:
	if combat_scene != null and is_instance_valid(combat_scene) and combat_scene.has_method(&"top_bar_hp"):
		var hp := int(combat_scene.call(&"top_bar_hp"))
		if hp >= 0:
			return hp
	return run_hp


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
			# in" stayed on the Mainframe and the event).
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
	# ANIM-R5 B6: the route page's own controls are kept (`motion_keeps`): a press on a
	# choice, GRID VIEW or Save & quit ends the move and does nothing else (a choice pressed
	# now reached the session after the move had opened the node, and was refused).
	# ANIM-R5 (MotionSkip.handle): the press completes every running motion, the move too.
	# ANIM-R6 B1: and the loot's deal (it outlasted the page's entrance, which took the press
	# before, and nothing took one after).
	if _travelling or fanning_row() != null:
		MotionSkip.handle(event, self)


## MotionSkip (ANIM-R5): a route move plays; ANIM-R6 B1: or the loot fans in.
func motion_running() -> bool:
	return _travelling or fanning_row() != null


## MotionSkip (ANIM-R5 B6): the route page's controls a press during the move never works;
## ANIM-R6 B1: nor a loot sticker's while the deal plays (a sticker still in its delay is
## invisible: a click there picked an offer the player never saw).
func motion_keeps() -> Array:
	var keep := route_keep() if _travelling else []
	var row := fanning_row()
	if row != null:
		keep.append(row)
	return keep


## MotionSkip (ANIM-R5): the move ends and the node's screen opens; ANIM-R6 B1: the loot
## lands in its slots.
func complete_motion() -> void:
	finish_fan()
	_end_travel()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_settings") and combat_scene == null:
		open_settings()
		get_viewport().set_input_as_handled()
		return
	# B leaves the Mainframe (H23 S11). H24 S6: only a pad's B: a keyboard's Esc (ui_cancel too)
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
	# B5 (integration review D8 / D9, designer ruling 6): the loot and event pages sit on the run's Site close-up (the
	# combat's own backdrop: its still or its city close-up), won with OURS NOW behind the loot, dimmed with the corp
	# tint behind an event (its CAM feed copies the close-up before the dim). Hidden on every other page.
	site_backdrop = CombatBackdrop.new()
	site_backdrop.name = "SiteBackdrop"
	site_backdrop.visible = false
	add_child(site_backdrop)
	site_copy = BackBufferCopy.new()
	site_copy.name = "SiteCopy"
	site_copy.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
	site_copy.visible = false
	add_child(site_copy)
	site_dim = ColorRect.new()
	site_dim.name = "SiteDim"
	site_dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	site_dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var mul := CanvasItemMaterial.new()
	mul.blend_mode = CanvasItemMaterial.BLEND_MODE_MUL
	site_dim.material = mul
	site_dim.visible = false
	add_child(site_dim)
	scrim = UiScrimPools.attach_after(site_dim)
	scrim.spill.add_spill_source(_target_spill, Palette.PENCIL_THREAT)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	hud = HudBar.new()
	hud.loadout_pressed.connect(open_loadout)
	hud.daemons_pressed.connect(open_daemons)
	hud.heat_pressed.connect(toggle_heat_terminal)
	root.add_child(hud)
	UiScrimPools.mark_band(hud, SIDE_TOP)
	UiScrimPools.mark_panel(hud, false)
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
	# B5 (B1c follow-up 2): the kit's CRT glass behind the host (shown on glass pages), not the shared material.
	_panel_host.theme_type_variation = UiTheme.CRT_GLASS_PANEL
	_panel_glass = CrtTerminalPanel.behind(_panel_host)
	_panel_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.add_child(_panel_host)
	# Pad prompts in a row of their own under the page (H23 S11).
	pad_prompts = PadPrompts.new()
	root.add_child(pad_prompts)
	_log = RichTextLabel.new()
	_log.theme_type_variation = UiTheme.CRT_LOG_TEXT
	CrtTerminalPanel.behind(_log)
	_log.bbcode_enabled = true
	_log.scroll_following = true
	_log.custom_minimum_size = Vector2(0, 110)
	root.add_child(_log)
	# Shown only when the player turns it on in Options.
	_log.visible = Settings.system_log
	Settings.changed.connect(func() -> void: _log.visible = Settings.system_log)
	# ANIM-4b: drag and drop over every page (targets pulse, the pad's reticle, flights).
	drops = DropLayer.new()
	_wire_drops(drops)
	add_child(drops)


## B1a (review D19, section d): a page's windows sit on the world (a pool and a drop shadow), its
## route key lies on a dark band at the foot, and its pink verb sticker spills its pink. A fight
## marks its own.
func _mark_scrim(p: Control) -> void:
	if p.has_method("attach_netrun"):
		return
	UiScrimPools.mark_panels_in(p, SCRIM_PANELS)
	for legend in p.find_children("*", "RouteLegend", true, false):
		UiScrimPools.mark_band(legend as Control, SIDE_BOTTOM)
	UiSpillShadows.mark_verb_stickers_in(p)


## B1a (review D19): the map's red TARGET pencil lights the city round it (global px).
func _target_spill() -> Array:
	if city_overlay == null or not is_instance_valid(city_overlay) or not city_overlay.is_visible_in_tree():
		return []
	var word := city_overlay.target_word()
	if word == null or not word.is_visible_in_tree():
		return []
	return [word.global_rect()]


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
