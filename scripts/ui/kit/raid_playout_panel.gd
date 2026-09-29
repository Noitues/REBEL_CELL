class_name RaidPlayoutPanel
extends VBoxContainer
## Raid playout (GDD 7.2, 9.3): plays a resolved raid's events step by step with 1x / 2x /
## 4x speed and Skip, drives the map's threat markers (a GridMapView or a CityMapOverlay,
## both expose `threat_markers`) and reports the step log in a zine note. The result is
## precomputed and deterministic; this panel is presentation only. Emits finished when
## the last step has played.
##
## Animation pass ANIM-5 (raid execution): on a CityMapOverlay the raid plays as motion
## (`attach_fx`: a RaidFxLayer on the map). Each step's beats and length come from
## RaidBeats, built from the resolver's events (never recomputed); the panel's clock runs
## at Motion.speed, which the speed buttons set (1x / 2x / 4x, back to 1x when the playout
## ends) so every beat scales. Skip jumps every beat to its end and emits `skipped` (the
## screens go straight to the summary); a press (the one rule, MotionSkip) ends the current
## step's motion. Instant (tests, headless, reduce effects): every step and beat at once.

signal finished
## Skip was pressed: the playout jumped to its end (screens show the summary).
signal skipped
## ANIM-R4 H11a: event `e` has been told (its feed line, if it has one, is in the feed): the
## screens change a top-bar value (Heat, RAIDS) only then, never before its line shows.
signal event_shown(e: Dictionary)

## The map the threats are shown on: a GridMapView or a CityMapOverlay (both expose
## `threat_markers`).
var grid_view: Control = null
var log_note: ZineNote
var step_label: Label
var speed: float = 1.0
## The motion layer on a CityMapOverlay (null on a GridMapView or with no map).
var fx: RaidFxLayer = null
var _steps: Array = []  # Array[Array[Dictionary]] grouped by step (RaidBeats.group)
var _threat_sites: Dictionary = {}  # threat id -> site
var _threat_names: Dictionary = {}
var _dead: Dictionary = {}
var _index: int = 0
var _done: bool = false
var _instant: bool = false
## The playout clock (seconds at 1x; advances at Motion.speed) and when the next step
## starts on it.
var _clock: float = 0.0
var _next_at: float = 0.0
var _set_speed: bool = false
## ANIM-R1 M4: the screen's camera for each step: called with the step's focus Sites
## (RaidBeats.focus_sites) as the step starts; it eases the map to them and returns the
## seconds that takes, which the step's beats wait (the fight is framed before it plays).
## Not called when the playout is instant.
var framer: Callable = Callable()
## ANIM-R2 R6: a step's beats start this share of the way through its camera ease (they
## waited the whole ease: the playout opened on ~2 s of a still map while it framed).
const FRAME_WAIT_SHARE := 0.35
## ANIM-R2 R6: the log window beside a playout map (px at text scale 1.0; it was 330x330,
## half the window: now a short strip that follows its newest line).
const LOG_SIZE := Vector2(330, 150)
## The step label's width at text scale 1.0 (px).
const STEP_LABEL_W := 90.0
## ANIM-R3 B5: the RAID FEED's sentences, translated once here: display names, never an id
## (the resolver's own log lines named Sites by id: "Turret at t1_a hits..."). Each takes
## names and numbers in order.
const FEED_ENTERS := "%s enters at %s." # TR
const FEED_MOVES := "%s moves from %s to %s." # TR
const FEED_HELD := "%s is held at %s (%d more)." # TR
const FEED_GHOSTS := "The operative on %s ghosts %s for %d step(s)." # TR
const FEED_ICE := "ICE Lock on %s holds %s for %d step(s)." # TR
const FEED_SHOT := "%s on %s hits %s for %d." # TR
const FEED_DESTROYED := "%s is destroyed." # TR
const FEED_NODE_HIT := "%s takes %d damage: HP %d → %d." # TR
const FEED_CASCADE := "Cascade: %s takes %d damage: HP %d → %d." # TR
const FEED_DISABLED := "%s is DISABLED." # TR
const FEED_SEIZED := "%s is SEIZED." # TR
const FEED_HOME_HIT := "%s reaches %s: %d damage, HP %d → %d." # TR
const FEED_HOME_LOST := "%s is lost. The campaign is over." # TR
const FEED_REGEN := "The operative on %s patches it: %s." # TR
const FEED_CUTS := "%s cuts a new route: %s - %s." # TR
const FEED_NO_ROUTE := "%s finds no locked route to open near %s." # TR
const FEED_FREEZES := "%s freezes the link %s - %s for this raid." # TR
const FEED_RECALLED := "%s returns to the reserves." # TR
const FEED_REPELLED := "Raid repelled after %d step(s)." # TR
const FEED_ENDED := "Raid over after %d step(s)." # TR
const FEED_TALLY := "Threats destroyed: %d. Reached home: %d. Disabled: %d. Seized: %d." # TR
const FEED_WON := "Reward: %s Schematics." # TR
const FEED_CAMPAIGN_LOST := "The home server is gone. Campaign lost." # TR
const FEED_HEAT := "Heat %s: %d → %d." # TR
const FEED_HEAT_RAID := "Heat %s for the lost raid: %d → %d." # TR
## ANIM-R4 H11a: a Heat threshold the raid's Heat crossed, and what it brings.
const FEED_THRESHOLD := "Heat %d crossed: %s" # TR
const FEED_STEP := "Step %d" # TR
## The resolved raid (RaidResult.to_dict) the feed's end tally reads.
var results: Dictionary = {}
## ANIM-R4 H11a: each node's integrity as the feed has told it so far (site id -> HP; home
## under its id), from the resolved raid's "before": a hit's line says the HP it really took
## and where it left the node, the numbers the map's labels and floats show.
var _hp: Dictionary = {}


func _init(p_grid_view: Control = null, log_size: Vector2 = Vector2(600, 120)) -> void:
	grid_view = p_grid_view
	TextDb.shown_as_given(self)  # H24 S4: its words translated here, shown as given
	var controls := HBoxContainer.new()
	add_child(controls)
	step_label = Label.new()
	step_label.text = tr("Setup")
	step_label.custom_minimum_size.x = STEP_LABEL_W * Settings.text_scale
	step_label.add_theme_font_override("font", Palette.display())
	step_label.ready.connect(UiTheme.track_label.bind(step_label))  # art pass W9F (§4.2)
	step_label.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.TITLE))  # W8b §4.3.1: a type step
	step_label.add_theme_color_override("font_color", Palette.CELL_ACID)
	controls.add_child(step_label)
	for s in [1.0, 2.0, 4.0]:
		var b := Button.new()
		b.name = "Speed%dx" % int(s)
		b.focus_mode = Control.FOCUS_ALL
		b.text = "%dx" % int(s)
		var value: float = s
		b.pressed.connect(func() -> void: set_speed(value))
		controls.add_child(b)
	var skip := Button.new()
	skip.name = "Skip"
	skip.text = tr("Skip")
	skip.pressed.connect(skip_pressed)
	controls.add_child(skip)
	log_note = ZineNote.new(tr("PLAYOUT"), log_size)
	# ANIM-R4 H11a: the feed writes changes as "HP 30 → 25": its lettering has the arrows.
	log_note.label.add_theme_font_override("normal_font", Palette.mono_arrows())
	log_note.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(log_note)


func _exit_tree() -> void:
	_restore_speed()


## Puts the raid's motion on the map (a CityMapOverlay): `results` is the resolved raid
## (campaign.last_raid / RaidResult.to_dict), `home` the home Site, `home_max` its full
## integrity, `color` the threats' colour. Call before `play`.
func attach_fx(p_results: Dictionary, home: StringName, home_max: int, color: Color) -> RaidFxLayer:
	results = p_results
	if not (grid_view is CityMapOverlay):
		return null
	var overlay := grid_view as CityMapOverlay
	if fx == null or not is_instance_valid(fx):
		fx = RaidFxLayer.new(overlay)
		overlay.add_child(fx)
		# W8b (critique 24/26): the raid's glow, hits and numbers draw under the map's labels
		# (a node's name is never covered; the numbers keep off the labels themselves).
		var labels := overlay.get_node_or_null(^"Labels")
		if labels != null:
			overlay.move_child(fx, labels.get_index())
	fx.setup(p_results, home, home_max, color)
	overlay.draw_markers = false
	return fx


## Loads a raid's events and starts playing. `instant` (tests, reduce-effects) shows all.
func play(events: Array[Dictionary], instant: bool = false) -> void:
	_threat_sites.clear()
	_threat_names.clear()
	_reset_hp()
	_dead.clear()
	_index = 0
	_done = false
	_instant = instant
	_clock = 0.0
	_next_at = 0.0
	_steps = RaidBeats.group(events)
	log_note.clear()
	if _instant:
		skip_to_end()
	else:
		_show_step()


## 1x / 2x / 4x: the playout and every motion it builds run this much faster.
func set_speed(value: float) -> void:
	speed = maxf(Motion.SPEED_MIN, value)
	Motion.set_speed(speed)
	_set_speed = true


func steps_total() -> int:
	return _steps.size()


func current_step() -> int:
	return _index


func is_done() -> bool:
	return _done


## The playout clock now (seconds at 1x).
func clock() -> float:
	return _clock


## The Skip button: every step and beat at its end, then `skipped` (the screen shows the
## summary).
func skip_pressed() -> void:
	skip_to_end()
	skipped.emit()


func skip_to_end() -> void:
	while _index < _steps.size():
		var tl := RaidBeats.timeline(_steps[_index])
		_apply_step(_steps[_index], _clock, tl)
		_clock += float(tl["seconds"])
		_index += 1
	_next_at = _clock
	if fx != null and is_instance_valid(fx):
		fx.clock = _clock
		fx.finish_all()
		_clock = fx.clock
	_finish()


func _process(delta: float) -> void:
	if _done or _instant or _steps.is_empty():
		return
	_clock += delta * Motion.speed
	if fx != null and is_instance_valid(fx):
		fx.clock = _clock
	if _clock >= _next_at:
		_show_step()


## ANIM-R2 R6: a press ends the current step's motion, by the one press rule (MotionSkip:
## any key, mouse button 1-3 or pad button going down; consumed, so nothing behind sees
## it). ANIM-R3 A2: a press that works the screen passes on untouched (MotionSkip.works_ui:
## a focus move, so the keys and the pad reach Skip and 2x / 4x; the Settings key; accept
## on the focused usable button; a click on a usable button), and while a PauseMenu is
## open every press is the menu's. Any other press skips one step.
func _input(event: InputEvent) -> void:
	if _done or _instant or not is_visible_in_tree() or not MotionSkip.is_press(event):
		return
	if MotionSkip.pause_open(self) or MotionSkip.works_ui(event, self):
		return
	skip_step()
	MotionSkip.consume(self, event)


## Ends the current step's motion at once (its beats at their ends).
func skip_step() -> void:
	_clock = maxf(_clock, _next_at)
	if fx != null and is_instance_valid(fx):
		fx.clock = _clock


## True when `event` is meant for a button (the panel's, the screen's, the settings'):
## MotionSkip.works_ui, kept under its ANIM-R2 name.
func _for_own_button(event: InputEvent) -> bool:
	return MotionSkip.works_ui(event, self)


## The panel's controls (Skip, 1x / 2x / 4x) in order: keys and the pad walk them.
func controls() -> Array[Button]:
	var out: Array[Button] = []
	for b in find_children("*", "Button", true, false):
		out.append(b as Button)
	return out


func _show_step() -> void:
	if _index >= _steps.size():
		_finish()
		return
	var start := _clock
	var tl := RaidBeats.timeline(_steps[_index])
	if framer.is_valid() and not (tl.get("beats", []) as Array).is_empty():
		# ANIM-R2 R6: the beats set off while the camera is still easing in (and a step with
		# nothing to show is not framed at all).
		start += float(framer.call(RaidBeats.focus_sites(_steps[_index], _threat_sites))) * FRAME_WAIT_SHARE
	_apply_step(_steps[_index], start, tl)
	_index += 1
	_next_at = start + float(tl["seconds"])
	if not is_inside_tree():
		skip_to_end()


func _apply_step(events: Array, start: float = 0.0, tl: Dictionary = {}) -> void:
	for e in events:
		var t: String = e.get("type", "")
		match t:
			"threat_enters":
				_threat_sites[e["threat"]] = e["site"]
				_threat_names[e["threat"]] = threat_word(e)
			"move":
				_threat_sites[e["threat"]] = e["to"]
			"threat_destroyed":
				_dead[e["threat"]] = true
			"home_hit":
				_dead[e["threat"]] = true
		var line := feed_line(e)
		if line != "":
			_log(line)
		event_shown.emit(e)
		if t == "raid_end":
			step_label.text = tr("Raid over")
		elif e.has("step"):
			step_label.text = tr("Step %d") % int(e["step"]) if int(e["step"]) > 0 else tr("Setup")
	if fx != null and is_instance_valid(fx):
		for b: Dictionary in tl.get("beats", []):
			fx.play_beat(b, start + float(b["t0"]))
	if grid_view != null:
		var markers := {}
		for id in _threat_sites:
			if _dead.has(id):
				continue
			markers.get_or_add(_threat_sites[id], []).append(_threat_names.get(id, String(id)))
		grid_view.set("threat_markers", markers)
		grid_view.queue_redraw()


func _log(line: String) -> void:
	log_note.append(line)


## ANIM-R3 B5: event `e`'s RAID FEED sentence, translated, with display names (a Site's name,
## CORE for home, a threat's and a defence's names), "Step N: " before a step's lines; "" for
## an event the feed does not tell. Never a content or Site id.
func feed_line(e: Dictionary) -> String:
	var text := ""
	var t := String(e.get("type", ""))
	match t:
		"threat_enters":
			text = tr(FEED_ENTERS) % [threat_word(e), site_word(e.get("site", &""))]
		"move":
			text = tr(FEED_MOVES) % [threat_word(e), site_word(e.get("from", &"")), site_word(e.get("to", &""))]
		"held":
			text = tr(FEED_HELD) % [threat_word(e), site_word(e.get("site", &"")), _count_in(e, "(")]
		"station_hold":
			text = tr(FEED_GHOSTS) % [site_word(e.get("site", &"")), threat_word(e), _count_in(e, "for ")]
		"ice_lock":
			text = tr(FEED_ICE) % [site_word(e.get("site", &"")), threat_word(e), _count_in(e, "for ")]
		"shot":
			text = tr(FEED_SHOT) % [content_word(StringName(e.get("asset", &""))), site_word(e.get("site", &"")), threat_word(e), int(e.get("damage", 0))]
		"threat_destroyed":
			text = tr(FEED_DESTROYED) % threat_word(e)
		"node_hit", "cascade":
			var hit := _take(StringName(String(e.get("site", ""))), int(e.get("damage", 0)))
			text = tr(FEED_NODE_HIT if t == "node_hit" else FEED_CASCADE) % [site_word(e.get("site", &"")), hit[0], hit[1], hit[2]]
		"disabled":
			_hp[String(e.get("site", ""))] = 0
			text = tr(FEED_DISABLED) % site_word(e.get("site", &""))
		"seized":
			_hp[String(e.get("site", ""))] = 0
			text = tr(FEED_SEIZED) % site_word(e.get("site", &""))
		"home_hit":
			var home_hit := _take(_home(), int(e.get("damage", 0)))
			text = tr(FEED_HOME_HIT) % [threat_word(e), site_word(_home()), home_hit[0], home_hit[1], home_hit[2]]
		"home_lost":
			text = tr(FEED_HOME_LOST) % site_word(_home())
		"station_regen":
			var sid := String(e.get("site", ""))
			if _hp.has(sid):
				_hp[sid] = int(_hp[sid]) + int(e.get("amount", 0))
			text = tr(FEED_REGEN) % [site_word(e.get("site", &"")), TextDb.signed(int(e.get("amount", 0)))]
		"link_altered":
			if StringName(e.get("b", &"")) != &"":
				text = tr(FEED_CUTS) % [threat_word(e), site_word(e.get("a", &"")), site_word(e.get("b", &""))]
			else:
				text = tr(FEED_NO_ROUTE) % [threat_word(e), site_word(e.get("a", &""))]
		"link_frozen":
			text = tr(FEED_FREEZES) % [threat_word(e), site_word(e.get("a", &"")), site_word(e.get("b", &""))]
		"recalled":
			text = tr(FEED_RECALLED) % operative_word(e.get("operative", ""))
		"raid_end":
			text = (tr(FEED_REPELLED) if bool(e.get("won", false)) else tr(FEED_ENDED)) % int(e.get("steps", 0))
			if not results.is_empty():
				text += " " + tr(FEED_TALLY) % [int(results.get("threats_destroyed", 0)), int(results.get("threats_reached_home", 0)),
					(results.get("disabled", []) as Array).size(), (results.get("seized", []) as Array).size()]
		"raid_won":
			text = tr(FEED_WON) % TextDb.signed(int(e.get("schematics", 0)))
		"campaign_lost":
			text = tr(FEED_CAMPAIGN_LOST)
		"heat":
			var amount := int(e.get("amount", 0))
			if amount == 0:
				return ""
			# ANIM-R4 H11a: from and to as the rules applied them (it said "now" with the campaign's
			# final Heat: "+5 ... now 5" from 1).
			var after := int(e.get("after", RunManager.campaign.heat if RunManager.campaign != null else 0))
			var before := int(e.get("before", after - amount))
			text = (tr(FEED_HEAT_RAID) if String(e.get("reason", "")) == "lost raid" else tr(FEED_HEAT)) % [TextDb.signed(amount), before, after]
		"heat_threshold":
			var brings := _threshold_text(int(e.get("heat", 0)))
			text = tr(FEED_THRESHOLD) % [int(e.get("heat", 0)), brings]
		_:
			return ""
	if e.has("step") and int(e["step"]) > 0 and t != "raid_end":
		text = tr(FEED_STEP) % int(e["step"]) + ": " + text
	return text


## ANIM-R4 H11a: the feed's HP before the raid, from the resolved raid (home under its id).
func _reset_hp() -> void:
	_hp.clear()
	var nodes: Dictionary = results.get("nodes", {})
	for id in nodes:
		_hp[String(id)] = int((nodes[id] as Dictionary).get("before", 0))
	if results.has("home_before"):
		_hp[String(_home())] = int(results["home_before"])


## A hit of `damage` on `site` as the feed tells it: [taken, HP before, HP after]; what it
## takes stops at 0 (the map's numbers do the same). A site with no HP known (no resolved
## raid given) is taken to have just the damage left.
func _take(site: StringName, damage: int) -> Array[int]:
	var key := String(site)
	var before := int(_hp.get(key, damage))
	var took := mini(damage, before)
	_hp[key] = before - took
	return [took, before, before - took]


## The text of the threshold at Heat `at` (any kind), through TextDb; "" when none.
static func _threshold_text(at: int) -> String:
	var cfg: CampaignConfigData = RunManager.config() if RunManager.campaign != null else null
	if cfg == null:
		return ""
	for t in cfg.heat_thresholds:
		if t != null and t.heat == at:
			return TextDb.t(t, "event_text")
	return ""


## A Site's display name (CORE for home; the Site's own name; its id only when the content
## is unknown).
func site_word(id: Variant) -> String:
	var sid := StringName(String(id))
	if sid == &"":
		return "-"
	if sid == _home():
		return tr("CORE")
	var sd := CampaignRules.site_data(RunManager.corporation, sid) if RunManager.corporation != null else null
	return TextDb.t(sd, "display_name") if sd != null else String(sid)


## ANIM-R4 H4: a threat's name in the player's language, from the content the event names
## (`threat_content`: ThreatData's display_name through TextDb; the English display name
## never had a translation key of its own), else the name its entry gave, else its English
## name from the resolver's line; "a threat" when unknown.
func threat_word(e: Dictionary) -> String:
	var content := StringName(String(e.get("threat_content", "")))
	if content != &"":
		var td := RunManager.lookup().get_content(content) as ThreatData
		if td != null:
			return TextDb.t(td, "display_name")
	var id: Variant = e.get("threat", "")
	if _threat_names.has(id):
		return String(_threat_names[id])
	if e.has("text") and t_name_from(String(e["text"])) != "":
		return tr(t_name_from(String(e["text"])))
	return tr("a threat")


## ANIM-R4 H2: an operative's name (the campaign roster's; "an operative" when the id is not
## on it). The feed never shows an operative's id ("op_1 returns to the reserves").
static func operative_word(id: Variant) -> String:
	var c := RunManager.campaign
	if c != null:
		for op in c.roster:
			if String(op.id) == String(id):
				return op.name
	return TranslationServer.translate("an operative")


## The threat's name in a resolver line ("Step 1: Collector enters at t1_a.", "Setup:
## Collector cuts a new route..."); "" when not one.
static func t_name_from(line: String) -> String:
	var body := line.get_slice(": ", 1) if line.contains(": ") else line
	for verb in NAME_VERBS:
		if body.contains(verb):
			return body.get_slice(verb, 0)
	return ""


## The verbs that follow a threat's name in the resolver's lines.
const NAME_VERBS: Array[String] = [" enters", " cuts", " finds", " freezes"]


## A content id's display name (a defence), translated; the id when unknown.
static func content_word(id: StringName) -> String:
	var res := RunManager.lookup().get_content(id) if id != &"" else null
	return TextDb.t(res, "display_name") if res != null and "display_name" in res else String(id)


func _home() -> StringName:
	var c := RunManager.campaign
	return c.grid.home_site_id if c != null and c.grid != null else &""


## The first whole number after the last `after` in the event's line (a count the event
## keeps only in its words); 0 when none.
static func _count_in(e: Dictionary, after: String) -> int:
	var line := String(e.get("text", ""))
	var at := line.rfind(after)
	if at < 0:
		return 0
	var digits := ""
	for ch in line.substr(at + after.length()):
		if ch >= "0" and ch <= "9":
			digits += ch
		elif digits != "":
			break
	return int(digits) if digits != "" else 0


func _finish() -> void:
	if _done:
		return
	_done = true
	_restore_speed()
	if fx != null and is_instance_valid(fx):
		fx.release()
	finished.emit()


func _restore_speed() -> void:
	if _set_speed:
		_set_speed = false
		Motion.set_speed(1.0)
