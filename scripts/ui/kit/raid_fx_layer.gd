class_name RaidFxLayer
extends Control
## Raid execution drawn on the city map (Animation pass ANIM-5, handoff 4.15): threats
## travel their street routes between nodes, guns fire traces, ICE LOCK rings close on a
## threat and freeze it, a DECOY's lure pulls a threat aside, damage numbers pop off
## nodes, HOLDS / DOWN / TAKEN / BREACHED stamps flip onto nodes, the home server's
## integrity drains with a lag bar, and a TAKEN node tints the streets round it in the
## corporation's colour until the city's real tint spreads (NeonCity).
##
## A child of a CityMapOverlay (it pans and zooms with the city; sizes are screen px x the
## overlay's `screen_k`). The RaidPlayoutPanel feeds it beats (RaidBeats, built from the
## resolver's events) on its own clock, which runs at Motion.speed (1x / 2x / 4x). The
## city backdrop keeps its own clock. View only: it reads events and the resolved raid,
## never game state, and uses no RNG.

## Node outcomes (RaidResolver) and their stamp words (the raid summary's words, in the
## same order), translated when drawn.
const STAMP_OUTCOMES: Array[String] = ["holds", "down", "taken", "passed", "breached"]
const STAMP_TEXT: Array[String] = ["HOLDS", "DOWN", "TAKEN", "PASSED", "BREACHED"] # TR
## Screen px (x screen_k): stamp lettering, its padding, tilt (degrees) and lift over
## the icon; damage numbers; traces; hit rings; the home bar and its gap under CORE.
## ANIM-R1 M4: stamps, numbers, traces and tokens grew (the raid was unreadable at map
## scale); the gun that fires rings itself (MUZZLE_RING) as its trace leaves.
const STAMP_FONT := 21
const STAMP_PAD := 6.0
const STAMP_TILT := -6.0
const STAMP_LIFT := 38.0
const NUMBER_FONT := 28
const TRACE_WIDTH := 3.5
const HIT_RING := 14.0
const MUZZLE_RING := 20.0
const FROST_RING := 13.0
const HOME_BAR := Vector2(64, 7)
const HOME_BAR_GAP := 8.0
const PULL_DASH := 6.0
## A threat token is the map's marker this much bigger.
## ANIM-R2 R6: bigger again, and high-contrast whatever the corporation: a white diamond
## ringed in THREAT_RED on a dark keyline (Solace's green threats were green on a green
## city), the corporation's colour only as a dot at its heart; a moving token leaves a
## fading red trail of TRAIL_DOTS dots, TRAIL_STEP of the move apart.
const TOKEN_SCALE := 3.0
const THREAT_RED := Color("#FF2A3D")
## ANIM-R4 H11a: the token stands on a dark halo ringed in paper, whatever the node under it
## (its red glow over a pink node read pinkish on pink): the halo (radius x the token), its
## colour and the rim's width (px x screen_k).
const TOKEN_HALO := 1.45
const TOKEN_HALO_COLOR := Color(0.02, 0.02, 0.05, 1.0)
const TOKEN_RIM := 2.0
const TRAIL_DOTS := 7
const TRAIL_STEP := 0.05
## ANIM-R2 R6: the raid's result banner ("HOME -5", "HOME HOLDS"): lettering and padding
## (screen px x screen_k) and its lift over the home node's stamp.
const BANNER_FONT := 34
const BANNER_PAD := 10.0
const BANNER_LIFT := 96.0
const STAGGER_MOTION := &"raid_outcome_stagger"
const BANNER_MOTION := &"raid_result_banner"
## The banner's words (translated when drawn). ANIM-R3 B5: the banner is home's one verdict
## (home gets no stamp of its own): what it lost and the resolved outcome. ANIM-R4 H3: in
## the raid verdict's words (RaidVerdict): "HOME -5 · HOLDS" (never "HOME HIT"), and
## BREACHED, the verdict's own word, when the home server fell.
const BANNER_HOME := "HOME %s · HOLDS" # TR
const BANNER_HOLDS := "HOME HOLDS" # TR
const BANNER_BREACHED := RaidVerdict.BREACHED
## ANIM-R3 B5: gap between the banner and what it keeps clear of, and from the map's edge
## (screen px x screen_k); numbers on one node stack this many of their lines apart.
const BANNER_CLEAR := 8.0
const NUMBER_STACK := 1.05
const NUMBER_GAP := 6.0
## A number's drawing: it holds whole for this share of its time, then fades out (ANIM-R6 C4:
## the inline 0.66 / 0.34, named; the time is `node_damage_number`'s).
const NUMBER_HOLD_SHARE := 0.66

## ANIM-R1 M4: a hit on the home server shows now (its number starts): `damage` from Site
## `site` (the screen flies the number into its home counter).
signal home_hit_shown(damage: int, site: StringName)
## Alpha of a TAKEN node's corporate tint disc (its reach is CityInfluence.RADIUS lots).
const TINT_ALPHA := 0.24
## ART-0 E (ported from art-pass W6, ART_BIBLE v2 5.3): each drawn effect's motion entry,
## whose tier it keeps to. All are local (T2 on a node or a threat, T3 for a district's tint
## and the result banner): nothing here is T4 and nothing covers the screen.
const FX_MOTION := {"trace": &"turret_trace", "hit": &"raid_hit_effect", "lock": &"ice_lock_ring", "frost": &"ice_lock_ring",
	"number": &"node_damage_number", "stamp": &"raid_flip", "outcome": &"raid_outcome_stagger", "banner": &"raid_result_banner",
	"tint": &"influence_spread", "home": &"home_lag", "token": &"raid_move", "withdraw": &"raid_threat_withdraw",
	"mark": &"raid_mark_write", "breach": &"raid_bits_burst", "field": &"raid_slow_field", "ice": &"raid_ice_grow", "repair": &"raid_repair_rise"}
## A raid hit's ring reaches at most this many of its rest radii (its threat's region, T2).
const HIT_REGION := 2.0
const TINT_RINGS := 24

# --- ART-6 3A: the raid in grease pencil, vehicle icons v4 and the station bonuses -------------
## ART_BIBLE v2 §4.8: state marks (INCOMING, DOWN, TAKEN) write ~0.4 s, hold ~1.5 s, wipe
## ~0.4 s; TAKEN v2 is normal weight above the node; BREACHED is one slow heavy wax pass with
## an underline, a red bit explosion at CORE and its links de-powering segment by segment.
## The marks run on real time from when their beat starts (a reading hold is never shortened
## at 2x / 4x; slower speeds hold longer), and a skip shows their end state.
const MARK_WRITE := &"raid_mark_write"
const MARK_HOLD := &"raid_mark_hold"
const MARK_WIPE := &"raid_mark_wipe"
const BREACH_WRITE := &"raid_breached_write"
const BREACH_BITS := &"raid_bits_burst"
const SLOW_FIELD := &"raid_slow_field"
const ICE_GROW := &"raid_ice_grow"
const REPAIR_RISE := &"raid_repair_rise"
const MARK_INCOMING := "INCOMING" # TR
## Pencil word sizes (screen px x screen_k x text scale): state marks, the verdict banner,
## BREACHED; their stroke widths (x size) and the lift of a word above its node (x icon r).
const MARK_LIFT := 2.4
const HOLDS_TICK := 16.0
## Screen px: a mark's lift above its node (the strokes are the kit's one wax width, B1b).
const MARK_LIFT_PX := 46.0
## Screen px between two marks shown at once on one node (the later one stacks above).
const MARK_STACK_GAP_PX := 6.0
## The vehicle icon's radius (screen px x screen_k), the ice round a frozen one (its half
## width x radius; the baked concept ice: folder, growth steps, the ellipse's half width in
## the image px, manifest.json), the slow field's radius (x the node icon) and rings.
const VEHICLE_R := 11.0
const ICE_BLOCK := 2.1
const ICE_DIR := "res://assets/raid/ice/"
const ICE_STEPS := 8
const ICE_ART_RX := 50.0
const FIELD_R := 3.2
const FIELD_RINGS := 3
## The slow field as the concept's fx_slow_v2 draws it: the edge's dashes, their gap (share
## of a dash step), its turn (dashes a cycle) and width (px x screen_k); the drifting rings'
## dashes, the share of them they lose and of the radius they cross going in, their width;
## the ground's foreshortening (y x).
const FIELD_DASHES := 40
const FIELD_GAP := 0.45
const FIELD_EDGE_TURN := 0.6
const FIELD_EDGE_W := 5.0
const FIELD_RING_DASHES := 34
const FIELD_DASH_LOSS := 0.6
const FIELD_INNER := 0.75
const FIELD_RING_W := 3.0
const FIELD_SQUASH := 0.55
## Repair (concept fx_repair_v2): the rising "+" marks (count, their stagger across the
## socket, its half width x the node icon, rise, arm and width in screen px x screen_k) and the
## pale streaks (count, speed x the marks', length, paleness).
const SPARKS := 7
const SPARK_STEP := 0.4625
const SPARK_SPREAD := 1.5
const SPARK_RISE := 60.0
const SPARK_ARM := 3.5
const SPARK_W := 2.0
const STREAKS := 5
const STREAK_SPEED := 1.375
const STREAK_LEN := 12.0
const STREAK_PALE := 0.5
## BREACHED's bits: the burst radius on screen (screen px x screen_k).
const BITS_R := 120.0
## The concept's own bit explosion (ui21.bit_burst, baked by tools/art_pipeline/raid/bake_bits.py):
## one strip of BITS_FRAMES frames of BITS_FRAME_PX, the burst centred at BITS_CENTRE_PX with
## radius BITS_ART_R, drawn BITS_LIFT_ART above the node as screens22's home-breached frame
## does (all in the bake's px; they mirror assets/raid/bits/manifest.json).
const BITS_SHEET := "res://assets/raid/bits/bits.png"
const BITS_FRAMES := 24
const BITS_FRAME_PX := Vector2(460, 380)
const BITS_CENTRE_PX := Vector2(230, 200)
const BITS_ART_R := 190.0
const BITS_LIFT_ART := 10.0


## The VFX tier of drawn effect `kind` (a FX_MOTION key; T2 when unknown).
static func fx_tier(kind: String) -> int:
	return VfxTier.of(FX_MOTION[kind]) if FX_MOTION.has(kind) else VfxTier.T2

var overlay: CityMapOverlay
## The playout clock (seconds at 1x): advances by frame time x Motion.speed.
var clock: float = 0.0
var threat_color: Color = Palette.CORP_SOLACE
var home_id: StringName = &""
var home_max: int = 1
## Home integrity shown now (after the hits played so far) and where its lag bar starts.
var home_value: int = 0
var _home_from: int = 0
var _home_lag_t0: float = -INF
var _tokens: Dictionary = {}  # threat id (String) -> token
var _fx: Array[Dictionary] = []
var _stamps: Dictionary = {}  # site id (String) -> {"word", "color", "t0", "dur"}
var _tints: Array[Dictionary] = []
var _tint_fade_t0: float = INF
var _results: Dictionary = {}
var _owner_done: bool = false
## ANIM-R1 M4: hits on home still to show ({"t0", "damage", "site"}), in time order.
var _home_due: Array[Dictionary] = []
## ANIM-R2 R6: the raid's result banner ({"text", "color", "t0"}; {} before the end).
var _banner: Dictionary = {}
## Home integrity as shown now (the hits that have shown so far; the bar draws it).
var home_shown: int = 0
## ANIM-R3 B5: each node's integrity as the numbers so far leave it (site id -> int, from the
## resolved raid's `before`), so the disabling hit shows the integrity it takes and every
## node's numbers add up to its before - after.
var _node_left: Dictionary = {}
## ART-6 3A: the raiding corporation (vehicle icons' kit), real seconds since setup (marks
## run on it), the pencil marks ({kind, site, word, col, t0, real0, above}), slow fields and
## repair sparks ({site, t0, dur}), BREACHED's start (clock; INF none), INCOMING once per Site.
var corporation_id: StringName = &""
var _real: float = 0.0
var _marks: Array[Dictionary] = []
## ART-6 3A: the entry Sites the route pencil letters (A, B, C; RaidRouteLayer.letters): a
## mark on one stacks above its letter (INCOMING sat on the "A").
var entry_letters: Dictionary = {}
var _fields: Array[Dictionary] = []
var _sparks: Array[Dictionary] = []
var _breach_t0: float = INF
var _incoming: Dictionary = {}
var _live_key: String = ""


func _init(p_overlay: CityMapOverlay = null) -> void:
	overlay = p_overlay
	_ci = self
	name = "RaidFx"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Starts a playout: the resolved raid (`results`: RaidResult.to_dict / campaign.last_raid),
## the home Site, its full integrity and the threats' colour.
func setup(results: Dictionary, p_home: StringName, p_home_max: int, color: Color) -> void:
	_results = results
	home_id = p_home
	home_max = maxi(1, p_home_max)
	home_value = int(results.get("home_before", home_max))
	home_shown = home_value
	_home_due.clear()
	_home_from = home_value
	threat_color = color
	clock = 0.0
	_tokens.clear()
	_fx.clear()
	_stamps.clear()
	_tints.clear()
	_tint_fade_t0 = INF
	_owner_done = false
	_banner = {}
	_node_left.clear()
	_marks.clear()
	_fields.clear()
	_sparks.clear()
	_incoming.clear()
	_breach_t0 = INF
	_real = 0.0
	if RunManager.campaign != null:
		corporation_id = RunManager.campaign.corporation_id
	_withdraw_len = RaidBeats.raw_seconds(WITHDRAW_MOTION)
	var nodes: Dictionary = results.get("nodes", {})
	for id in nodes:
		_node_left[String(id)] = int(nodes[id].get("before", 0))
	# ANIM-R5 P8: the map's labels keep off the tokens standing on its nodes, and the moving
	# parts (tints, traces, tokens, locks, hits) draw under the labels: a token passing a node
	# never hides its name (CORE's label went under the token on it mid-raid).
	if overlay != null:
		overlay.token_radius = CityMapOverlay.MARKER_SIZE * TOKEN_SCALE * TOKEN_HALO
		_ensure_under()
		overlay.socket_live = socket_state  # ART-6 3A: sockets drain and fall as the hits land
	queue_redraw()


## ANIM-R5 P8: the layer under the map's labels the moving parts draw on (the stamps, home's
## bar, the numbers and the banner stay on this one, over the labels).
var _under: Control = null
## The canvas item the moving parts draw on (`_under`, else this layer).
var _ci: CanvasItem = null


func _ensure_under() -> void:
	if _under != null and is_instance_valid(_under):
		return
	var labels: Control = overlay._tags if overlay != null else null
	if labels == null or not is_instance_valid(labels):
		return
	_under = Control.new()
	_under.name = "RaidFxUnder"
	_under.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_under.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_under.draw.connect(_draw_under)
	overlay.add_child(_under)
	overlay.move_child(_under, labels.get_index())


func _exit_tree() -> void:
	if _under != null and is_instance_valid(_under):
		_under.queue_free()
	_under = null
	if _pool != null and is_instance_valid(_pool):
		_pool.release()
	_pool = null


func _process(delta: float) -> void:
	if not is_visible_in_tree():
		return
	# After the playout the layer keeps its own time (the tint fade, the last numbers).
	if _owner_done:
		clock += delta
	_real += delta
	_start_marks()
	_update_hover()
	_lay_pencil()
	_refresh_sockets()
	_show_due_hits()
	if _tint_fade_t0 == INF and not _tints.is_empty() and overlay != null and overlay.city != null and overlay.city.influence_pin == null \
			and overlay.city.showing_current_look():
		_tint_fade_t0 = clock
	queue_redraw()
	if _under != null and is_instance_valid(_under):
		_under.queue_redraw()


## Every beat at its end at once (Skip, reduce effects, headless).
func finish_all() -> void:
	clock = maxf(clock, _last_end())
	_show_due_hits()
	home_shown = home_value
	# ART-6 3A: every pencil mark at its end (written, held, wiped; BREACHED stays).
	for m in _marks:
		m["real0"] = _real - mark_length(m) - 1.0
		m["started"] = true
	_refresh_sockets()
	queue_redraw()


# --- ART-6 3A: marks, sockets, vehicles -----------------------------------------------------------

## The real seconds a motion entry of the marks takes: its raw time, longer at a slower
## speed, never shorter at 2x / 4x (a reading time). Hold entries keep their time switched off.
static func mark_seconds(id: StringName) -> float:
	var e := Motion.entry(id)
	if e == null:
		return 0.0
	if id != MARK_HOLD and not Motion.live(id):
		return 0.0
	return maxf(e.duration, e.duration / maxf(Motion.speed, Motion.SPEED_MIN))


## A mark's whole length (real s): write, hold, wipe (BREACHED: its slow pass, then it stays).
func mark_length(m: Dictionary) -> float:
	if bool(m.get("stays", false)):
		return mark_seconds(BREACH_WRITE if bool(m.get("heavy", false)) else MARK_WRITE)
	return mark_seconds(MARK_WRITE) + mark_seconds(MARK_HOLD) + mark_seconds(MARK_WIPE)


## Mark `m`'s progress now: [write 0..1, wipe 0..1] (before its start: [0, 0]).
func mark_progress(m: Dictionary) -> Vector2:
	if not bool(m.get("started", false)):
		return Vector2.ZERO
	var r0 := float(m["real0"])
	var t := _real - r0
	var w := mark_seconds(BREACH_WRITE if bool(m.get("heavy", false)) else MARK_WRITE)
	var write := 1.0 if w <= 0.0 else clampf(t / w, 0.0, 1.0)
	if bool(m.get("stays", false)):
		return Vector2(write, 0.0)
	var h := mark_seconds(MARK_HOLD)
	var wp := mark_seconds(MARK_WIPE)
	var wipe := 0.0
	if t >= w + h:
		wipe = 1.0 if wp <= 0.0 else clampf((t - w - h) / wp, 0.0, 1.0)
	return Vector2(write, wipe)


## Marks whose beat has come start on the real clock.
func _start_marks() -> void:
	for m in _marks:
		if not bool(m.get("started", false)) and clock >= float(m["t0"]):
			m["real0"] = _real
			m["started"] = true


func _mark(kind: String, site: StringName, word: String, t0: float, above: bool, heavy: bool = false, stays: bool = false) -> void:
	_marks.append({"kind": kind, "site": site, "word": word, "t0": t0, "real0": -1.0, "above": above, "heavy": heavy, "stays": stays})


## The pencil marks (tests): [{kind, site, word}].
func marks() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for m in _marks:
		out.append({"kind": m["kind"], "site": m["site"], "word": m["word"]})
	return out


## ART-6 3A: Site `site`'s live socket (CityMapOverlay.socket_live): its health as the hits
## so far leave it, DOWN from its DOWN beat, TAKEN (burnt) once its TAKEN mark has wiped.
func socket_state(site: StringName) -> Variant:
	if overlay == null:
		return null
	var n := overlay._node_dict(site)
	if n.is_empty() or not n.has("socket"):
		return null
	var most := int((n["socket"] as Dictionary).get("max", 1))
	var out := {}
	if site == home_id:
		out["health"] = float(home_shown) / float(maxi(1, home_max))
	elif _node_left.has(String(site)):
		out["health"] = float(int(_node_left[String(site)])) / float(maxi(1, most))
	var st: Dictionary = _stamps.get(String(site), {})
	if not st.is_empty() and clock >= float(st["t0"]):
		match String(st.get("outcome", "")):
			"down":
				out["state"] = RaidSocket.STATE_DOWN
			"taken":
				out["state"] = RaidSocket.STATE_DOWN
				for m in _marks:
					if m["kind"] == "taken" and m["site"] == site and mark_progress(m).y >= 1.0:
						out["state"] = RaidSocket.STATE_TAKEN
	if _breach_t0 != INF and site == home_id and clock >= _breach_t0:
		out["state"] = RaidSocket.STATE_DOWN
	return out


## The overlay's sockets redraw when a live value changed.
func _refresh_sockets() -> void:
	if overlay == null or overlay.nodes.is_empty():
		return
	var parts := PackedStringArray()
	for n: Dictionary in overlay.nodes:
		if n.has("socket"):
			parts.append(str(socket_state(n["id"])))
	var key := ",".join(parts)
	if key != _live_key:
		_live_key = key
		overlay.queue_redraw()


## ANIM-R1 M4: the hits on home whose time has come show (home_hit_shown each).
func _show_due_hits() -> void:
	while not _home_due.is_empty() and clock >= float(_home_due[0]["t0"]):
		var h: Dictionary = _home_due.pop_front()
		home_shown = maxi(0, home_shown - int(h["damage"]))
		home_hit_shown.emit(int(h["damage"]), StringName(h["site"]))


## The playout has ended: from now on the layer runs its own clock (tint fade).
func release() -> void:
	_owner_done = true


func _last_end() -> float:
	var end := 0.0
	for id in _tokens:
		var t: Dictionary = _tokens[id]
		for k in ["enter_at", "dead_at"]:
			if t.has(k):
				end = maxf(end, float(t[k]) + float(t.get(k + "_dur", 0.0)))
		if t.has("move"):
			end = maxf(end, float(t["move"]["t0"]) + float(t["move"]["dur"]))
	for f in _fx:
		end = maxf(end, float(f["t0"]) + float(f["dur"]))
	for id in _stamps:
		end = maxf(end, float(_stamps[id]["t0"]) + float(_stamps[id]["dur"]))
	if not _banner.is_empty():
		end = maxf(end, float(_banner["t0"]) + Motion.seconds(BANNER_MOTION))
	return maxf(end, _home_lag_t0 + RaidBeats.raw_seconds(&"home_lag"))


## Plays one beat (RaidBeats.timeline) starting at clock time `t0`.
func play_beat(b: Dictionary, t0: float) -> void:
	var e: Dictionary = b["event"]
	var dur := float(b["dur"])
	match String(b["type"]):
		"threat_enters":
			# ART-6 3A: its v4 icon (type from its rules, its health from its integrity), and
			# INCOMING written once at the Site it enters by.
			var tid := StringName(String(e.get("threat_content", "")))
			var td: ThreatData = RunManager.lookup().get_content(tid) as ThreatData if RunManager.lookup().has(tid) else null
			var most := int(e.get("integrity", td.integrity if td != null else 1))
			_tokens[String(e["threat"])] = {"site": StringName(e["site"]), "enter_at": t0, "enter_at_dur": dur,
				"type": RaidVehicle.type_of(td), "max": maxi(1, most), "hits": []}
			var entry := StringName(e["site"])
			if not _incoming.has(entry):
				_incoming[entry] = true
				_mark("incoming", entry, CityMapOverlay.tr_word(MARK_INCOMING), t0, true)
		"move":
			var tok: Dictionary = _tokens.get_or_add(String(e["threat"]), {"site": StringName(e["from"])})
			tok["move"] = {"from": StringName(e["from"]), "to": StringName(e["to"]), "t0": t0, "dur": dur,
				"decoy": StringName(e.get("target", "")) if bool(e.get("decoy", false)) else &""}
			tok["site"] = StringName(e["to"])
			tok.erase("frozen")
		"held":
			_fx.append({"kind": "frost", "threat": String(e["threat"]), "t0": t0, "dur": dur})
			if _tokens.has(String(e["threat"])):
				_tokens[String(e["threat"])]["frozen"] = true
		"ice_lock", "station_hold":
			_fx.append({"kind": "lock", "threat": String(e["threat"]), "t0": t0, "dur": dur})
			if _tokens.has(String(e["threat"])):
				_tokens[String(e["threat"])]["frozen"] = true
				# ART-6 3A: a stationed Ghost slows (its field under the units); ICE freezes.
				_tokens[String(e["threat"])]["status"] = RaidVehicle.STATUS_SLOWED if String(b["type"]) == "station_hold" else RaidVehicle.STATUS_FROZEN
				_tokens[String(e["threat"])]["status_t0"] = t0
			if String(b["type"]) == "station_hold":
				_fields.append({"site": StringName(e["site"]), "t0": t0})
		"shot":
			# ANIM-R1 M4: strictly shot, hit, number: the trace flies to the threat over
			# `turret_trace`, the hit lands as it arrives, the damage rises after the hit.
			var trace := RaidBeats.raw_seconds(&"turret_trace")
			var hit := RaidBeats.raw_seconds(&"raid_hit_effect")
			_fx.append({"kind": "trace", "site": StringName(e["site"]), "threat": String(e["threat"]), "t0": t0, "dur": trace, "hit": hit})
			_fx.append({"kind": "hit", "threat": String(e["threat"]), "t0": t0 + trace, "dur": hit})
			if _tokens.has(String(e["threat"])):
				(_tokens[String(e["threat"])]["hits"] as Array).append([t0 + trace, int(e.get("damage", 0))])
			if int(e.get("damage", 0)) > 0:
				_fx.append({"kind": "number", "threat": String(e["threat"]), "text": TextDb.signed(-int(e["damage"])), "value": -int(e["damage"]),
					"color": Palette.CELL_ACID, "t0": t0 + trace + hit, "dur": RaidBeats.raw_seconds(&"node_damage_number")})
		"threat_destroyed":
			var tok: Dictionary = _tokens.get(String(e["threat"]), {})
			if not tok.is_empty():
				tok["dead_at"] = t0
				tok["dead_at_dur"] = dur
		"node_hit", "cascade", "home_hit":
			# ANIM-R3 B5: one number per hit, the integrity it really took (a cascade or a hit
			# on home stops at 0), on the node it hit; home's also fly into HOME.
			var site := home_id if String(b["type"]) == "home_hit" else StringName(e["site"])
			if site == home_id:
				var took := mini(int(e.get("damage", 0)), home_value)
				_number(site, -took, Palette.CELL_PINK, t0, dur)
				_home_hit(took, t0, site)
			else:
				var left := int(_node_left.get(String(site), 0))
				var took := mini(int(e.get("damage", 0)), left)
				_node_left[String(site)] = left - took
				_number(site, -took, Palette.CELL_PINK, t0, dur)
		"station_regen":
			var site := StringName(e["site"])
			_node_left[String(site)] = int(_node_left.get(String(site), 0)) + int(e.get("amount", 0))
			_number(site, int(e.get("amount", 0)), Palette.CELL_ACID, t0, dur)
			_sparks.append({"site": site, "t0": t0})  # ART-6 3A: the repair rises with "+" sparks
		"down":
			# ANIM-R3 B5: the hit that disables takes what integrity was left (its own number).
			var site := StringName(e["site"])
			var left := int(_node_left.get(String(site), 0))
			if left > 0:
				_number(site, -left, Palette.CELL_PINK, t0, dur)
			_node_left[String(site)] = 0
			_stamp(site, "down", Palette.CELL_PINK, t0, dur)
			_mark("down", site, tr_outcome("down"), t0, false)
		"taken":
			# ANIM-R3 B5: a Site taken with integrity left (threats standing on it at the step
			# cap) loses it all: its own number, so the numbers add up to before - after.
			var taken_site := StringName(e["site"])
			var taken_left := int(_node_left.get(String(taken_site), 0))
			if taken_left > 0:
				_number(taken_site, -taken_left, Palette.RESIST_GOLD, t0, dur)
			_node_left[String(taken_site)] = 0
			_stamp(taken_site, "taken", Palette.RESIST_GOLD, t0, dur)
			_mark("taken", taken_site, tr_outcome("taken"), t0, true)
			_tints.append({"site": StringName(e["site"]), "t0": t0, "dur": RaidBeats.raw_seconds(&"influence_spread")})
		"home_lost":
			# ANIM-R3 B5: home's verdict is its banner (no stamp over it).
			_banner = {"text": CityMapOverlay.tr_word(BANNER_BREACHED), "color": Palette.CELL_PINK, "t0": t0, "breached": true}
			_breach_t0 = t0  # ART-6 3A: the red bit explosion at CORE, its links de-powering
			_mark("breached", home_id, CityMapOverlay.tr_word(BANNER_BREACHED), t0 + mark_seconds(BREACH_BITS) * 0.5, true, true, true)
		"raid_end":
			# ANIM-R2 R6: the outcomes stamp node after node (`raid_outcome_stagger`, by id),
			# then the result banner stamps over home. ANIM-R3 B5: every node's stamp is its
			# resolved outcome (one verdict word per node, the word its label says), home's
			# verdict is the banner alone.
			# ANIM-R6 C11: every threat still on the map withdraws at the verdict (a red X strikes
			# it as it fades): the Collector stood on CORE through HOME -5 · HOLDS and read as
			# "the enemy is still in my home".
			_withdraw_all(t0)
			var flip := Motion.seconds(STAGGER_MOTION)
			var gap := Motion.delay_of(STAGGER_MOTION)
			var at := t0
			var last := t0 - gap
			var ids: Array = _results.get("nodes", {}).keys()
			ids.sort()
			for id in ids:
				var sid := StringName(String(id))
				if sid == home_id:
					continue
				var outcome := String(_results["nodes"][id].get("outcome", "holds"))
				if stamp_word(sid) == stamp_text(outcome):
					continue
				_stamp(sid, outcome, stamp_color(outcome), at, flip)
				last = at
				at += gap
			# The end state is the resolved raid's (never a sum that could drift): a change
			# no event showed gets its own number too.
			if _results.has("home_after"):
				var after := int(_results["home_after"])
				if after != home_value:
					_number(home_id, after - home_value, Palette.CELL_PINK, t0, dur)
					_home_hit(home_value - after, t0, home_id)
			if _banner.is_empty():
				var lost := int(_results.get("home_before", home_value)) - int(_results.get("home_after", home_value))
				_banner = {"text": CityMapOverlay.tr_word(BANNER_HOME) % TextDb.signed(-lost) if lost > 0 else CityMapOverlay.tr_word(BANNER_HOLDS), "holds": lost > 0,
					"color": Palette.CELL_PINK if lost > 0 else Palette.CELL_ACID,
					"t0": maxf(t0, last + flip) + Motion.delay_of(BANNER_MOTION)}
	queue_redraw()


## ANIM-R6 C11: the threats still standing at clock time `t0` withdraw from it
## (`raid_threat_withdraw`: faded out under a red X; gone at once when it is off).
func _withdraw_all(t0: float) -> void:
	for id in _tokens:
		var t: Dictionary = _tokens[id]
		if t.has("dead_at") and float(t["dead_at"]) <= t0:
			continue
		t["dead_at"] = t0
		t["dead_at_dur"] = _withdraw_len
		t["withdrawn"] = true


const WITHDRAW_MOTION := &"raid_threat_withdraw"
## The withdrawal's time (s at 1x), read as the playout is set up.
var _withdraw_len: float = 0.0


## ANIM-R3 B5: a stamp's colour by outcome (acid holds, gold taken, pink the rest).
static func stamp_color(outcome: String) -> Color:
	match outcome:
		"holds":
			return Palette.CELL_ACID
		"taken":
			return Palette.RESIST_GOLD
	return Palette.CELL_PINK


func _number(site: StringName, value: int, col: Color, t0: float, dur: float) -> void:
	if value == 0:
		return
	_fx.append({"kind": "number", "site": site, "text": TextDb.signed(value), "value": value, "color": col, "t0": t0, "dur": dur})


func _stamp(site: StringName, outcome: String, col: Color, t0: float, dur: float) -> void:
	_stamps[String(site)] = {"word": stamp_text(outcome), "color": col, "t0": t0, "dur": dur, "outcome": outcome}


## ANIM-R3 B5: an outcome's word, translated (the stamp's word; the rows and labels say the
## same).
static func tr_outcome(outcome: String) -> String:
	return CityMapOverlay.tr_word(stamp_text(outcome)) if outcome != "" else "?"


## The stamp word for node outcome `outcome` (untranslated; drawn translated).
static func stamp_text(outcome: String) -> String:
	var i := STAMP_OUTCOMES.find(outcome)
	return STAMP_TEXT[i] if i >= 0 else outcome.to_upper()


func _home_hit(damage: int, t0: float, site: StringName = &"") -> void:
	_home_from = _home_lag_value()
	home_value = maxi(0, home_value - damage)
	_home_lag_t0 = t0
	if damage != 0:
		_home_due.append({"t0": t0, "damage": damage, "site": site if site != &"" else home_id})
		_home_due.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return float(a["t0"]) < float(b["t0"]))


## The home bar's white lag segment now (it trails home_value by `home_lag`).
func _home_lag_value() -> float:
	var e := Motion.entry(&"home_lag")
	if e == null or _home_lag_t0 == -INF or not Motion.live(&"home_lag"):
		return home_shown
	var u := clampf((clock - _home_lag_t0 - e.delay) / maxf(e.duration, 0.001), 0.0, 1.0)
	return float(Tween.interpolate_value(float(_home_from), float(home_shown - _home_from), u, 1.0, e.trans, e.ease))


# --- Checks (tests) ---------------------------------------------------------------------------

## The stamp word on Site `site` ("" when none).
func stamp_word(site: StringName) -> String:
	return String(_stamps.get(String(site), {}).get("word", ""))


## ANIM-R3 B5: the numbers shown on Site `site` (its hits and patches, in order; tests).
func numbers_at(site: StringName) -> Array[int]:
	var out: Array[int] = []
	for f in _fx:
		if f["kind"] == "number" and f.has("site") and StringName(f["site"]) == site:
			out.append(int(f["value"]))
	return out


## Every stamp (site id -> word).
func stamps() -> Dictionary:
	var out := {}
	for id in _stamps:
		out[id] = _stamps[id]["word"]
	return out


## Where threat `id` stands (after its last move) and whether it is still in the raid.
func token_site(id: String) -> StringName:
	return StringName(_tokens.get(id, {}).get("site", &""))


func token_alive(id: String) -> bool:
	var t: Dictionary = _tokens.get(id, {})
	return not t.is_empty() and (not t.has("dead_at") or clock < float(t["dead_at"]))


## The threats standing on the map now, site id -> ids (sorted).
func standing() -> Dictionary:
	var out := {}
	var ids := _tokens.keys()
	ids.sort()
	for id in ids:
		if token_alive(String(id)):
			(out.get_or_add(_tokens[id]["site"], []) as Array).append(String(id))
	return out


# --- Drawing ----------------------------------------------------------------------------------

func _draw() -> void:
	if overlay == null or overlay.city == null:
		return
	var k := overlay.screen_k()
	var at := _token_positions()
	if _under == null or not is_instance_valid(_under):
		_draw_moving(k, at)
	for id in _stamps:
		_draw_stamp(StringName(id), _stamps[id], k)
	_draw_home(k)
	_draw_breach(k)
	_draw_sparks(k)
	# ANIM-R3 B5: numbers over the stamps (a stamp hid the hit on home under it).
	for f in _fx:
		if f["kind"] == "number":
			_draw_number(f, k, at)
	# ART-6 3A: the verdict banner and the state marks are grease pencil on the pencil layer
	# (_lay_pencil), above every panel.


## The moving parts (tints, traces, tokens, ICE locks, hits) on `_ci`.
func _draw_moving(k: float, at: Dictionary) -> void:
	_draw_tints(k)
	_draw_fields(k)
	for f in _fx:
		if f["kind"] == "trace":
			_draw_trace(f, at, k)
	for id in _tokens:
		_draw_token(String(id), at, k)
	for f in _fx:
		match String(f["kind"]):
			"lock", "frost":
				_draw_lock(f, at, k)
			"hit":
				_draw_hit(f, at, k)


func _draw_under() -> void:
	if overlay == null or overlay.city == null or not is_visible_in_tree():
		return
	_ci = _under
	_draw_moving(overlay.screen_k(), _token_positions())
	_ci = self


## ANIM-R2 R6: the result banner over home: stamps on from `raid_result_banner`'s amplitude
## and stays (the result).
func _draw_banner(_k: float) -> void:
	pass  # ART-6 3A: home's verdict is grease pencil on the pencil layer (_lay_pencil)


## ART-6 3A: the verdict banner's pencil type step (BREACHED writes larger, heavy).
func banner_step() -> int:
	return UiTheme.DISPLAY if bool(_banner.get("breached", false)) else UiTheme.TITLE

## ANIM-R6 C11: the banner's words in their colours: [[words, colour], ...]. HOME -5 · HOLDS
## is its damage (pink, to the last " · ") then HOLDS (acid); any other banner is one colour.
func banner_parts() -> Array:
	var text := banner_text()
	var col: Color = _banner.get("color", Palette.CELL_PINK)
	var cut := text.rfind(HOLDS_BREAK)
	if not bool(_banner.get("holds", false)) or cut < 0:
		return [[text, col]]
	cut += HOLDS_BREAK.length()
	return [[text.left(cut), col], [text.substr(cut), Palette.CELL_ACID]]


## Where HOME -5 · HOLDS changes colour (after its dot).
const HOLDS_BREAK := " · "


## The result banner's words ("" before the raid's end; tests).
func banner_text() -> String:
	return String(_banner.get("text", ""))


## ANIM-R3 B5: where the result banner sits (local px, unrotated; empty when home is off
## the map): above home's icon when that is clear, else below its bar, else to its left or
## right: the first spot that keeps BANNER_CLEAR off every stamp, node label and icon, and
## inside the map; the least covered one when none is clear (at big text a stamp above and a
## label beside can leave no room).
func banner_rect() -> Rect2:
	if _banner.is_empty() or overlay == null:
		return Rect2()
	var p := overlay.icon_at(home_id)
	if p.x == INF:
		return Rect2()
	var k := overlay.screen_k()
	# ART-6 3A: the pencil words' size (BREACHED writes larger, heavy).
	# The pencil word's screen size, in this layer's px (the map's zoom undone).
	var size := RaidPencilPool.word_size(String(_banner["text"]), banner_step()) / maxf(RaidMapAnchor.scale(overlay), 0.001) \
		+ Vector2(BANNER_PAD, BANNER_PAD) * 2.0 * k
	var clear := BANNER_CLEAR * k
	var r_icon := CityMapOverlay.ICON_RADIUS_BIG * k
	var bar_bottom := r_icon + (HOME_BAR_GAP + HOME_BAR.y) * k
	# ANIM-R5 P6: the stamp_rect spot search (NeonCity.stamp_rect): the spots round home,
	# then the same ring of spots further out (BANNER_RINGS steps of the banner's height), the
	# tilted box tested against every stamp, label, icon, home's bar and threat token; the first
	# clear spot wins, else the least covered (at 1.6 the first ring's spots all touched CORE's
	# label or the token standing on it).
	var spots: Array[Vector2] = []
	for ring in BANNER_RINGS:
		var out := ring * (size.y + clear)
		spots.append_array([
			p + Vector2(0, -r_icon - clear - size.y * 0.5 - out),
			p + Vector2(0, bar_bottom + clear + size.y * 0.5 + out),
			p + Vector2(r_icon + clear + size.x * 0.5 + out, 0),
			p + Vector2(-r_icon - clear - size.x * 0.5 - out, 0),
			p + Vector2(r_icon + size.x * 0.5 + out, -r_icon - clear - size.y * 0.5 - out),
			p + Vector2(-r_icon - size.x * 0.5 - out, -r_icon - clear - size.y * 0.5 - out),
			p + Vector2(r_icon + size.x * 0.5 + out, bar_bottom + clear + size.y * 0.5 + out),
			p + Vector2(-r_icon - size.x * 0.5 - out, bar_bottom + clear + size.y * 0.5 + out),
		])
	var avoid := banner_avoid()
	# The map's own visible area, clear of the panels and the key over it (labels keep to it).
	var area := overlay.label_area().grow(-clear)
	avoid.append_array(overlay.label_blocks())
	var best := Rect2()
	var best_hits := INF
	for c in spots:
		var r := Rect2(c - size * 0.5, size)
		# Kept inside the map (slid in from an edge).
		r.position = r.position.clamp(area.position, (area.end - r.size).max(area.position))
		var tilted := NeonCity._tilted_bounds(r, STAMP_TILT)
		var hits := 0.0
		for a in avoid:
			var g := a.grow(clear * 0.5)
			if tilted.intersects(g):
				hits += tilted.intersection(g).get_area() + 1.0
		if hits < best_hits:
			best_hits = hits
			best = r
			if hits == 0.0:
				break
	return best


## ANIM-R5 P6: rings of spots the banner tries round home (the first at its edge).
const BANNER_RINGS := 3


## ANIM-R5 P6: the threat tokens standing now (local px: each token's halo box).
func token_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	if overlay == null:
		return out
	var k := overlay.screen_k()
	var s := CityMapOverlay.MARKER_SIZE * k * TOKEN_SCALE * TOKEN_HALO
	var at := _token_positions()
	for id in at:
		var t: Dictionary = _tokens[id]
		var p: Vector2 = at[id]
		if p.x == INF or clock < float(t.get("enter_at", -INF)):
			continue
		if t.has("dead_at") and clock >= float(t["dead_at"]) + float(t.get("dead_at_dur", 0.0)):
			continue
		# ANIM-R6 C11: a threat withdrawing at the verdict is leaving: home's banner (placed at
		# the verdict) does not dodge it, so the banner never jumps as it goes.
		if bool(t.get("withdrawn", false)) and clock >= float(t["dead_at"]):
			continue
		out.append(Rect2(p - Vector2(s, s), Vector2(s, s) * 2.0))
	return out


## ANIM-R3 B5: what the banner keeps clear of: every stamp, node label and node icon (local
## px), home's bar.
func banner_avoid() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var k := overlay.screen_k()
	for id in _stamps:
		out.append(stamp_rect(StringName(id)))
	for key in overlay.label_rects():
		out.append(overlay.label_rects()[key])
	for n: Dictionary in overlay.nodes:
		var c := overlay.icon_at(n["id"])
		if c.x != INF:
			var r := CityMapOverlay.ICON_RADIUS_BIG * k
			out.append(Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0))
	var p := overlay.icon_at(home_id)
	if p.x != INF:
		var w := HOME_BAR.x * k
		out.append(Rect2(p + Vector2(-w * 0.5, CityMapOverlay.ICON_RADIUS_BIG * k + HOME_BAR_GAP * k), Vector2(w, HOME_BAR.y * k)))
	out.append_array(token_rects())
	return out


## ANIM-R3 B5: a stamp's box on Site `site` (local px, unrotated; empty when none).
func stamp_rect(site: StringName) -> Rect2:
	if not _stamps.has(String(site)):
		return Rect2()
	var p := overlay.icon_at(site)
	if p.x == INF:
		return Rect2()
	var k := overlay.screen_k()
	var fs := maxi(1, roundi(STAMP_FONT * Settings.text_scale * k))
	var word := CityMapOverlay.tr_word(String(_stamps[String(site)]["word"]))
	var size := Palette.display().get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs) + Vector2(STAMP_PAD, STAMP_PAD) * 2.0 * k
	return Rect2(p + Vector2(0, -STAMP_LIFT * k - CityMapOverlay.ICON_RADIUS * k) - size * 0.5, size)


func _u(t0: float, dur: float) -> float:
	if dur <= 0.0:
		return 1.0 if clock >= t0 else 0.0
	return clampf((clock - t0) / dur, 0.0, 1.0)


## ANIM-R6 C4: the length motion `id` takes of a beat's `dur`: all of it while `id` plays
## (Motion.live), 0 when it is switched off (reduce effects and headless too: the playout is
## instant then): the beat keeps its time on the clock and shows its end state from its
## start, with no motion (a token stands on its new node, a stamp lies flat, a number stands
## unrisen, home's bar has no lag).
static func motion_len(id: StringName, dur: float) -> float:
	return dur if Motion.live(id) else 0.0


## ANIM-R6 C4: how far (0..1) a beat of motion `id` from `t0` over `dur` has got now: 1 from
## its start when `id` doesn't play (tests read it too).
func beat_u(id: StringName, t0: float, dur: float) -> float:
	return _u(t0, motion_len(id, dur))


func _eased(id: StringName, u: float) -> float:
	var e := Motion.entry(id)
	return float(Tween.interpolate_value(0.0, 1.0, u, 1.0, e.trans, e.ease)) if e != null else u


## Every token's position now (local px), INF for one not on the map or not shown.
func _token_positions() -> Dictionary:
	var out := {}
	var resting := {}
	var ids := _tokens.keys()
	ids.sort()
	for id in ids:
		var t: Dictionary = _tokens[id]
		var mv: Dictionary = t.get("move", {})
		var moving: bool = not mv.is_empty() and clock < float(mv["t0"]) + _move_len(mv)
		var site: StringName = mv["from"] if moving and clock <= float(mv["t0"]) else t["site"]
		if not moving or clock <= float(mv["t0"]):
			(resting.get_or_add(site, []) as Array).append(id)
	for site in resting:
		var group: Array = resting[site]
		for i in group.size():
			out[group[i]] = overlay.marker_slot(site, i, group.size())
	for id in ids:
		var t: Dictionary = _tokens[id]
		var mv: Dictionary = t.get("move", {})
		if mv.is_empty() or clock <= float(mv["t0"]) or clock >= float(mv["t0"]) + _move_len(mv):
			continue
		out[id] = _along_move(mv, _eased(&"raid_move", _u(float(mv["t0"]), _move_len(mv))))
	return out


## ANIM-R6 C4: the time a move's token travels (0 when `raid_move` is off: it stands on its
## new node from the move's start).
func _move_len(mv: Dictionary) -> float:
	return motion_len(&"raid_move", float(mv["dur"]))


## A point `u` (0..1) along a move: from the threat's slot over its node, down the street
## route, up to the slot over the next node; a DECOY's pull veers it sideways mid-way.
func _along_move(mv: Dictionary, u: float) -> Vector2:
	var a := overlay.marker_slot(mv["from"], 0, 1)
	var b := overlay.marker_slot(mv["to"], 0, 1)
	if a.x == INF or b.x == INF:
		return b if u >= 1.0 else Vector2(INF, INF)
	var pts := PackedVector2Array([a])
	for p in overlay.route_between(mv["from"], mv["to"]):
		pts.append(overlay.grid_point_local(p))
	pts.append(b)
	var total := 0.0
	for i in pts.size() - 1:
		total += pts[i].distance_to(pts[i + 1])
	var d := u * total
	var at := b
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if d <= seg:
			at = pts[i].lerp(pts[i + 1], d / maxf(seg, 0.001))
			break
		d -= seg
	if mv["decoy"] != &"":
		var side := (b - a).orthogonal().normalized()
		at += side * sin(u * PI) * (Motion.amplitude(&"decoy_fire") if Motion.live(&"decoy_fire") else 0.0) * overlay.screen_k()
	return at


func _diamond(p: Vector2, s: float) -> PackedVector2Array:
	return PackedVector2Array([p + Vector2(0, -s), p + Vector2(s * 0.9, 0), p + Vector2(0, s), p + Vector2(-s * 0.9, 0)])


func _draw_token(id: String, at: Dictionary, k: float) -> void:
	var t: Dictionary = _tokens[id]
	var p: Vector2 = at.get(id, Vector2(INF, INF))
	if p.x == INF:
		return
	var enter := float(t.get("enter_at", -INF))
	if clock < enter:
		return
	var s := CityMapOverlay.MARKER_SIZE * k * TOKEN_SCALE
	var r := VEHICLE_R * k
	var alpha := 1.0
	if enter > -INF:
		var pop := beat_u(&"node_pop", enter, float(t.get("enter_at_dur", 0.0)))
		r *= lerpf(Motion.amplitude(&"node_pop"), 1.0, _eased(&"node_pop", pop)) if pop < 1.0 else 1.0
		alpha = pop if pop < 1.0 else 1.0
	var struck := -1.0
	if t.has("dead_at"):
		var withdrawn := bool(t.get("withdrawn", false))
		var du := beat_u(WITHDRAW_MOTION if withdrawn else &"raid_hit_effect", float(t["dead_at"]), float(t.get("dead_at_dur", 0.0)))
		if du >= 1.0:
			return
		if withdrawn:
			struck = du
		else:
			r *= lerpf(1.0, Motion.amplitude(&"raid_hit_effect"), du)
		alpha *= 1.0 - du
	var mv: Dictionary = t.get("move", {})
	var moving: bool = not mv.is_empty() and clock > float(mv["t0"]) and clock < float(mv["t0"]) + _move_len(mv)
	if moving and mv["decoy"] != &"":
		var lure := overlay.icon_at(mv["decoy"])
		if lure.x != INF:
			_dashed(lure, p, Color(Palette.RESIST_GOLD, 0.8), 1.5 * k, PULL_DASH * k)
	var heading := NAN
	if moving:
		# ANIM-R2 R6: a fading trail behind it along its street (ART-6 3A: in its corp colour).
		var u := _u(float(mv["t0"]), _move_len(mv))
		var trail := Palette.corp_color(corporation_id)
		for q in range(1, TRAIL_DOTS + 1):
			var tp := _along_move(mv, _eased(&"raid_move", maxf(0.0, u - q * TRAIL_STEP)))
			if tp.x != INF:
				var fade := 1.0 - float(q) / (TRAIL_DOTS + 1)
				_ci.draw_circle(tp, s * 0.3 * fade, Color(trail, 0.75 * fade * alpha))
	# ART-6 3A: the heading arrow rides the ring on hover only (§4.8).
	if _hovered == id:
		heading = _heading_of(t, p)
	var statuses: Array = []
	var frozen := bool(t.get("frozen", false))
	if frozen and t.has("status"):
		statuses.append(t["status"])
	RaidVehicle.draw(_ci, p, r, String(t.get("type", RaidVehicle.HEAVY)), corporation_id, token_hp(id), statuses, heading,
		fmod(anim_phase(), 1.0), alpha)
	if frozen and String(t.get("status", "")) == RaidVehicle.STATUS_FROZEN:
		_ice_block(p, r * ICE_BLOCK, beat_u(ICE_GROW, float(t.get("status_t0", 0.0)), RaidBeats.raw_seconds(ICE_GROW)), alpha, id.hash())
	# ANIM-R6 C11: the withdrawing threat is struck out (ART-6 3A: a red pencil X, _lay_pencil).


## ART-6 3A: threat `id`'s health now (0..1): its integrity less the shots landed so far.
func token_hp(id: String) -> float:
	var t: Dictionary = _tokens.get(id, {})
	if t.is_empty():
		return 0.0
	var left := int(t.get("max", 1))
	for h: Array in t.get("hits", []):
		if clock >= float(h[0]):
			left -= int(h[1])
	return clampf(float(left) / float(maxi(1, int(t.get("max", 1)))), 0.0, 1.0)


## The ring's dash phase (turns): it turns slowly while the raid plays (still when off).
func anim_phase() -> float:
	return clock * Motion.amplitude(SLOW_FIELD) if Motion.live(SLOW_FIELD) else 0.0


## The way token `t` (at `p`) heads: toward its next node when moving, else its last move's.
func _heading_of(t: Dictionary, p: Vector2) -> float:
	var mv: Dictionary = t.get("move", {})
	if mv.is_empty():
		return NAN
	var to := overlay.icon_at(mv["to"])
	var from := overlay.icon_at(mv["from"])
	if to.x == INF:
		return NAN
	var d := to - p if p.distance_to(to) > 2.0 else to - from
	return d.angle() if d.length() > 0.1 else NAN


## The token under the pointer ("" none): its heading shows on hover.
var _hovered: String = ""


func _update_hover() -> void:
	if overlay == null or not is_visible_in_tree():
		return
	var m := get_local_mouse_position()
	var at := _token_positions()
	var r := VEHICLE_R * overlay.screen_k() * RaidVehicle.RING
	var found := ""
	for id in at:
		var p: Vector2 = at[id]
		if p.x != INF and p.distance_to(m) <= r and token_alive(String(id)):
			found = String(id)
	_hovered = found


## ART-6 3A (§4.8 ICE, round 22 "ICE as crystals"): a threat encased in ice: the concept's own
## ice (ui22.ice, baked by tools/art_pipeline/raid/bake_ice.py into assets/raid/ice/), its
## crystals grown to `u` (the baked step), the ellipse `r` wide (half width) over the unit.
func _ice_block(c: Vector2, r: float, u: float, alpha: float, _seed: int) -> void:
	var step := clampi(ceili(clampf(u, 0.0, 1.0) * ICE_STEPS), 1, ICE_STEPS)
	var path := ICE_DIR + "ice_%02d.png" % step
	if not _ice_tex.has(path):
		_ice_tex[path] = load(path) if ResourceLoader.exists(path) else null
	var tex: Texture2D = _ice_tex[path]
	if tex == null:
		return
	var half := Vector2(tex.get_size()) * 0.5 * r / ICE_ART_RX
	_ci.draw_texture_rect(tex, Rect2(c - half, half * 2.0), false, Color(Palette.NO_TINT, alpha))

## ANIM-R1 M4: the shot: the gun's node rings as it fires, the trace flies from the gun to
## the threat over its duration (a bright head), then fades while the hit lands.
func _draw_trace(f: Dictionary, at: Dictionary, k: float) -> void:
	var t0 := float(f["t0"])
	var fly := float(f["dur"])
	var fade := float(f.get("hit", 0.0))
	if clock < t0 or clock >= t0 + fly + fade:
		return
	var from := overlay.icon_at(f["site"])
	var to: Vector2 = at.get(String(f["threat"]), Vector2(INF, INF))
	if from.x == INF or to.x == INF:
		return
	var u := beat_u(&"turret_trace", t0, fly)
	# ANIM-R6 C4: off, the whole trace stands for its time (no flight, no fade).
	var a := 1.0 if u < 1.0 or not Motion.live(&"turret_trace") else 1.0 - _u(t0 + fly, fade)
	var head := from.lerp(to, _eased(&"turret_trace", u))
	var muzzle := 1.0 - u
	if muzzle > 0.0:
		_ci.draw_arc(from, MUZZLE_RING * k * (1.0 + 0.4 * u), 0, TAU, 24, Color(Palette.CELL_ACID, muzzle), 3.0 * k)
	_ci.draw_line(from, head, Color(0, 0, 0, 0.6 * a), TRACE_WIDTH * 4.0 * k)
	_ci.draw_line(from, head, Color(Palette.CELL_ACID, 0.45 * a), TRACE_WIDTH * 3.0 * k)
	_ci.draw_line(from, head, Color(Palette.PAPER, a), TRACE_WIDTH * k)
	if u < 1.0:
		_ci.draw_circle(head, TRACE_WIDTH * 1.8 * k, Palette.PAPER)
	_ci.draw_circle(from, 4.0 * k, Color(Palette.CELL_ACID, a))


func _draw_lock(f: Dictionary, at: Dictionary, k: float) -> void:
	if clock < float(f["t0"]):
		return
	var u := _u(float(f["t0"]), float(f["dur"]))
	if f["kind"] == "frost" and (u >= 1.0 or not Motion.live(&"ice_lock_ring")):
		return
	var p: Vector2 = at.get(String(f["threat"]), Vector2(INF, INF))
	if p.x == INF:
		return
	var rest := FROST_RING * k
	if f["kind"] == "lock":
		if u >= 1.0:
			return
		# ANIM-R6 C4: off, the ring stands closed for its time (no closing).
		var shut := u if Motion.live(&"ice_lock_ring") else 1.0
		var r := lerpf(rest * Motion.amplitude(&"ice_lock_ring"), rest, _eased(&"ice_lock_ring", shut))
		_ci.draw_arc(p, r, 0, TAU, 28, Color(Palette.NET_CYAN, 0.35 + 0.65 * shut), 3.0 * k)
		for q in 6:
			var d := Vector2.from_angle(TAU * q / 6.0)
			_ci.draw_line(p + d * r, p + d * (r + 4.0 * k), Palette.NET_CYAN, 1.5 * k)
	else:
		_ci.draw_arc(p, rest * (1.0 + 0.3 * (1.0 - u)), 0, TAU, 20, Color(Palette.NET_CYAN, 1.0 - u), 2.0 * k)


func _draw_hit(f: Dictionary, at: Dictionary, k: float) -> void:
	var u := _u(float(f["t0"]), float(f["dur"]))
	if clock < float(f["t0"]) or u >= 1.0 or not Motion.live(&"raid_hit_effect"):
		return
	var p: Vector2 = at.get(String(f["threat"]), Vector2(INF, INF))
	if p.x == INF:
		return
	var r := HIT_RING * k * lerpf(1.0, Motion.amplitude(&"raid_hit_effect"), _eased(&"raid_hit_effect", u))
	# ART-0 E: held to its tier's reach (the threat's own spot, never the map).
	r = VfxTier.clamp_radius(fx_tier("hit"), r, HIT_RING * k, HIT_RING * k * HIT_REGION)
	_ci.draw_arc(p, r, 0, TAU, 20, Color(Palette.PAPER, 1.0 - u), 2.5 * k)
	for q in 4:
		var d := Vector2.from_angle(PI * 0.25 + q * PI * 0.5)
		_ci.draw_line(p + d * r * 0.6, p + d * r * 1.2, Color(Palette.CELL_ACID, 1.0 - u), 2.0 * k)


func _draw_number(f: Dictionary, k: float, where: Dictionary = {}) -> void:
	var u := _u(float(f["t0"]), float(f["dur"]))
	if clock < float(f["t0"]) or u >= 1.0:
		return
	# ANIM-R1 M4: a shot's damage rises off the threat it hit (where it stood when hit).
	var p: Vector2 = where.get(String(f["threat"]), Vector2(INF, INF)) if f.has("threat") else overlay.icon_at(f["site"])
	if f.has("threat") and p.x == INF:
		p = f.get("last_at", Vector2(INF, INF))
	elif f.has("threat"):
		f["last_at"] = p
	if p.x == INF:
		return
	# ANIM-R6 C4: off, the number stands where it rises from, whole, for its time.
	var live := Motion.live(&"node_damage_number")
	var rise := Motion.amplitude(&"node_damage_number") * k * _eased(&"node_damage_number", u) if live else 0.0
	var fs := maxi(1, roundi(NUMBER_FONT * Settings.text_scale * k))
	var font := Palette.display()
	var text := String(f["text"])
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	# ANIM-R3 B5: a node's number rises on its right, a threat's on its left (a threat standing
	# on a node never puts its number on the node's); numbers on one node at once stack.
	var at: Vector2
	if f.has("threat"):
		at = p + Vector2(-w - CityMapOverlay.MARKER_SIZE * TOKEN_SCALE * k - NUMBER_GAP * k, -rise)
	else:
		at = p + Vector2(CityMapOverlay.ICON_RADIUS_BIG * k + NUMBER_GAP * k, font.get_ascent(fs) * 0.5 - rise - _stack_of(f) * fs * NUMBER_STACK)
	var a := 1.0 if u < NUMBER_HOLD_SHARE or not live else (1.0 - u) / (1.0 - NUMBER_HOLD_SHARE)
	draw_string_outline(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(1, roundi(4.0 * k)), Color(0, 0, 0, 0.9 * a))
	draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(f["color"], a))


## How many numbers on the same Site show now and started before `f` (its row in the stack).
func _stack_of(f: Dictionary) -> int:
	var n := 0
	for g in _fx:
		if g == f:
			break
		if g["kind"] == "number" and g.has("site") and g["site"] == f["site"] and clock >= float(g["t0"]) and _u(float(g["t0"]), float(g["dur"])) < 1.0:
			n += 1
	return n


func _draw_stamp(_site: StringName, _s: Dictionary, _k: float) -> void:
	pass  # ART-6 3A: outcomes are pencil now (_lay_pencil: a HOLDS tick; DOWN / TAKEN marks)


## ART-6 3A: where each state mark shown now is written (mark index -> its word's centre,
## global px): DOWN over its node, INCOMING / TAKEN above theirs, BREACHED where the verdict
## sits. Two marks at once on one node never overlap (the later one stacks above the
## earlier one's top), and a mark written above an entry clears its pencil letter.
func mark_centres() -> Dictionary:
	var out := {}
	if overlay == null:
		return out
	var gxf := get_global_transform()
	var tops := {}
	for i in _marks.size():
		var m: Dictionary = _marks[i]
		var pr := mark_progress(m)
		if pr.x <= 0.0 or pr.y >= 1.0:
			continue
		var site := StringName(m["site"])
		var heavy := bool(m.get("heavy", false))
		var c: Vector2
		if heavy:
			var place := banner_rect()
			c = gxf * place.get_center() if place.has_area() else RaidMapAnchor.site(overlay, site) - Vector2(0, MARK_LIFT_PX)
		else:
			c = RaidMapAnchor.site(overlay, site)
			if bool(m.get("above", false)):
				c -= Vector2(0, MARK_LIFT_PX)
		if c.x == INF:
			continue
		if not heavy:
			var h := RaidPencilPool.word_size(String(m["word"]), UiTheme.TITLE).y
			if bool(m.get("above", false)) and entry_letters.has(site):
				# A mark written above an entry (INCOMING, TAKEN) clears its pencil letter; DOWN
				# stays written over the node.
				var letter := RaidMapAnchor.site(overlay, site) + RaidRouteLayer.LETTER_OFF
				var letter_top := letter.y - RaidPencilPool.word_size(String(entry_letters[site]), RaidRouteLayer.LETTER_STEP).y * 0.5
				c.y = minf(c.y, letter_top - h * 0.5 - MARK_STACK_GAP_PX)
			if tops.has(site):
				c.y = minf(c.y, float(tops[site]) - h * 0.5 - MARK_STACK_GAP_PX)
			tops[site] = c.y - h * 0.5
		out[i] = c
	return out


## ART-6 3A: the playout's pencil on 1B's grease pencil (RaidPencilPool, on the raid pencil
## layer above every panel), anchored through RaidMapAnchor: the state marks (DOWN written
## over its node, INCOMING / TAKEN above theirs, BREACHED heavy where the verdict sits, with
## its underline), home's verdict ("HOME -5" red, "HOLDS" yellow), a yellow tick on each
## node that holds at the verdict, a red X on a threat withdrawing.
func _lay_pencil() -> void:
	if overlay == null or overlay.city == null or not is_visible_in_tree():
		return
	if _pool == null:
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	var threat := GreasePencilMark.Ink.THREAT
	var plan := GreasePencilMark.Ink.PLAN
	var gxf := get_global_transform()
	var zoom := RaidMapAnchor.scale(overlay)
	var centres := mark_centres()
	for i in _marks.size():
		if not centres.has(i):
			continue
		var m: Dictionary = _marks[i]
		var pr := mark_progress(m)
		var heavy := bool(m.get("heavy", false))
		var c: Vector2 = centres[i]
		var step := UiTheme.DISPLAY if heavy else UiTheme.TITLE
		var write := minf(1.0, pr.x * (1.25 if heavy else 1.0))
		_pool.word("mark_%d" % i, String(m["word"]), c, step, threat, 1.0, write, pr.y, -0.05)
		if heavy:
			var size := RaidPencilPool.word_size(String(m["word"]), step)
			var y := c.y + size.y * 0.55
			var line := PackedVector2Array([Vector2(c.x - size.x * 0.56, y), Vector2(c.x + size.x * 0.56, y + size.y * 0.06)])
			_pool.stroke("under_%d" % i, [line], threat, clampf(pr.x * 1.25 - 0.25, 0.0, 1.0), 0.0, false, 9)
	# Home's verdict (not BREACHED: that is its own heavy mark). B1b pencil audit: kept for now
	# (it plays `raid_result_banner`); review RAID-10 moves it to the after-action paper's sticker,
	# a slice of its own (DECISIONS "B1b — wax pencil material and pencil audit").
	if not _banner.is_empty() and clock >= float(_banner["t0"]) and not bool(_banner.get("breached", false)):
		var place := banner_rect()
		if place.has_area():
			var u := beat_u(BANNER_MOTION, float(_banner["t0"]), Motion.seconds(BANNER_MOTION))
			var parts := banner_parts()
			var total := 0.0
			for part: Array in parts:
				total += RaidPencilPool.word_size(String(part[0]), banner_step()).x
			var c := gxf * place.get_center()
			var x := c.x - total * 0.5
			var done := 0.0
			for j in parts.size():
				var part: Array = parts[j]
				var w := RaidPencilPool.word_size(String(part[0]), banner_step()).x
				var share := w / maxf(total, 1.0)
				var pu := clampf((u - done) / maxf(share, 0.001), 0.0, 1.0)
				var ink := plan if (part[1] as Color) == Palette.CELL_ACID else threat
				_pool.word("banner_%d" % j, String(part[0]), Vector2(x + w * 0.5, c.y), banner_step(), ink, 1.0, pu, 0.0, deg_to_rad(STAMP_TILT))
				x += w
				done += share
	# A yellow tick on each node that holds, at the verdict.
	for id in _stamps:
		var s: Dictionary = _stamps[id]
		if clock < float(s["t0"]) or String(s.get("outcome", "")) != "holds":
			continue
		var p := RaidMapAnchor.site(overlay, StringName(id))
		if p.x == INF:
			continue
		var r := CityMapOverlay.ICON_RADIUS * zoom
		var tc := p + Vector2(r * RaidSocket.HALF.x * 1.1, -r * 0.9)
		var t := PackedVector2Array([tc + Vector2(-HOLDS_TICK * 0.5, 0), tc + Vector2(-HOLDS_TICK * 0.1, HOLDS_TICK * 0.4), tc + Vector2(HOLDS_TICK * 0.6, -HOLDS_TICK * 0.55)])
		_pool.stroke("tick_%s" % id, [t], plan, beat_u(&"raid_flip", float(s["t0"]), float(s["dur"])), 0.0, false, String(id).hash())
	# A red X on a threat withdrawing at the verdict.
	var at := _token_positions()
	for id in _tokens:
		var tk: Dictionary = _tokens[id]
		if not bool(tk.get("withdrawn", false)) or clock < float(tk["dead_at"]):
			continue
		var du := beat_u(WITHDRAW_MOTION, float(tk["dead_at"]), float(tk.get("dead_at_dur", 0.0)))
		var p: Vector2 = at.get(id, Vector2.INF)
		if du >= 1.0 or p.x == INF:
			continue
		var g := gxf * p
		var arm := VEHICLE_R * zoom * Motion.amplitude(WITHDRAW_MOTION)
		_pool.stroke("x_%s" % id, [PackedVector2Array([g + Vector2(-arm, -arm * 0.85), g + Vector2(arm, arm * 0.8)]),
			PackedVector2Array([g + Vector2(arm, -arm * 0.85), g + Vector2(-arm * 0.95, arm * 0.9)])], threat, 1.0, du, false, String(id).hash())
	_pool.end()


## The pencil marks laid now (tests).
func pencil_shown() -> Array[Node2D]:
	return _pool.shown() if _pool != null else []


var _pool: RaidPencilPool = null
## The baked ice steps, loaded once (path -> Texture2D or null).
static var _ice_tex: Dictionary = {}
static var _bits_tex: Texture2D = null
static var _bits_loaded: bool = false

## ART-6 3A (§4.8 Ghost station bonus, round 22 `bonus_slow_v2`): the slow field under the
## units on the node whose operative holds them, drawn as the concept's `fx_slow_v2` draws it
## (screens22.py): the dashed edge carries it (FIELD_DASHES dashes, FIELD_GAP gap) and
## FIELD_RINGS slow-blue dashed rings drift inward, shrinking to FIELD_INNER of the radius
## and losing dashes and alpha as they go. Procedural because the rings move (an image can't
## drift inward); still, without the drift, under reduce effects.
func _draw_fields(k: float) -> void:
	for f in _fields:
		if clock < float(f["t0"]):
			continue
		var c := overlay.icon_at(f["site"])
		if c.x == INF:
			continue
		var R := CityMapOverlay.ICON_RADIUS * k * FIELD_R
		var period := maxf(0.001, Motion.seconds(SLOW_FIELD))
		var t := (clock - float(f["t0"])) / period if Motion.live(SLOW_FIELD) else 0.0
		_ci.draw_set_transform(c, 0.0, Vector2(1.0, FIELD_SQUASH))
		_dashed_ring(R, FIELD_DASHES, t * FIELD_EDGE_TURN, FIELD_EDGE_W * k, 1.0)
		for i in FIELD_RINGS:
			var q := fmod(t + float(i) / FIELD_RINGS, 1.0)
			_dashed_ring(R * (1.0 - FIELD_INNER * q), maxi(6, int(FIELD_RING_DASHES * (1.0 - FIELD_DASH_LOSS * q))), -t,
				FIELD_RING_W * k, 0.9 * (1.0 - q))
		_ci.draw_set_transform(Vector2.ZERO)


## One dashed ring of the slow field (concept `dashed_ground_ring`): `n` dashes from `phase`
## (in dashes), each FIELD_GAP short of the next.
func _dashed_ring(R: float, n: int, phase: float, width: float, alpha: float) -> void:
	for i in n:
		var a0 := TAU * (i + phase) / n
		var a1 := TAU * (i + phase + 1.0 - FIELD_GAP) / n
		_ci.draw_arc(Vector2.ZERO, R, a0, a1, 5, Color(Palette.RAID_SLOW_BLUE, alpha), width)

## ART-6 3A (§4.8 Rigger repair, round 22 `bonus_repair_v2`): health goes UP. The socket's
## baked fill steps back up (RaidSocket health v2) while the concept's `fx_repair_v2` marks
## rise off it (screens22.py): SPARKS "+" marks spread over the socket rising straight up and
## STREAKS pale vertical streaks. Procedural because they move.
func _draw_sparks(k: float) -> void:
	for f in _sparks:
		var u := beat_u(REPAIR_RISE, float(f["t0"]), RaidBeats.raw_seconds(REPAIR_RISE))
		if clock < float(f["t0"]) or u >= 1.0 or not Motion.live(REPAIR_RISE):
			continue
		var c := overlay.icon_at(f["site"])
		if c.x == INF:
			continue
		var spread := CityMapOverlay.ICON_RADIUS * k * SPARK_SPREAD
		for i in SPARKS:
			var q := fmod(u + float(i) / SPARKS, 1.0)
			var x := -spread + fmod(i * SPARK_STEP, 1.0) * spread * 2.0
			var p := c + Vector2(x, -SPARK_RISE * k * q)
			var s := SPARK_ARM * k
			var col := Color(Palette.GAIN, 1.0 - q)
			draw_line(p - Vector2(s, 0), p + Vector2(s, 0), col, SPARK_W * k)
			draw_line(p - Vector2(0, s), p + Vector2(0, s), col, SPARK_W * k)
		var pale := Palette.GAIN.lerp(Palette.TEXT_HI, STREAK_PALE)
		for i in STREAKS:
			var q := fmod(u * STREAK_SPEED + float(i) / STREAKS, 1.0)
			var x := -spread * 0.75 + spread * 1.5 * i / maxf(1.0, STREAKS - 1.0)
			var top := c + Vector2(x, -SPARK_RISE * k * q)
			draw_line(top, top + Vector2(0, -STREAK_LEN * k), Color(pale, 0.9 * (1.0 - q)), maxf(1.0, k))

## ART-6 3A (§4.8 BREACHED): a red bit explosion at CORE (0 / 1 glyphs blasting out and
## falling) and CORE's links de-powering segment by segment from the node outward.
func _draw_breach(k: float) -> void:
	if _breach_t0 == INF or clock < _breach_t0:
		return
	var c := overlay.icon_at(home_id)
	if c.x == INF:
		return
	var dur := RaidBeats.raw_seconds(BREACH_BITS)
	var u := beat_u(BREACH_BITS, _breach_t0, dur)
	# The links out of CORE go dark from CORE outward (the de-powered network).
	for e: Dictionary in overlay.edges:
		var other := &""
		if e["a"] == home_id:
			other = e["b"]
		elif e["b"] == home_id:
			other = e["a"]
		if other == &"" or e.get("pencil", false):
			continue
		var pts := PackedVector2Array([c])
		for q in overlay.route_between(home_id, other):
			pts.append(overlay.grid_point_local(q))
		var dead := RaidPencil.trimmed(pts, 0.0, clampf(u * 1.3, 0.0, 1.0))
		if dead.size() >= 2:
			draw_polyline(dead, Color(Palette.NIGHT_SKY, 0.85), 7.0 * k, true)
			draw_polyline(dead, Color(Palette.DISABLED, 0.6), 1.5 * k, true)
	if u >= 1.0 or not Motion.live(BREACH_BITS):
		return
	# The concept's burst (flash, shock ring, 0 / 1 bits blasting out and falling), frame by u.
	var sheet := bits_sheet()
	if sheet == null:
		return
	var s := BITS_R * k / BITS_ART_R
	var src := Rect2(Vector2(bits_frame(u) * BITS_FRAME_PX.x, 0.0), BITS_FRAME_PX)
	var at := c + (Vector2(0.0, -BITS_LIFT_ART) - BITS_CENTRE_PX) * s
	draw_texture_rect_region(sheet, Rect2(at, BITS_FRAME_PX * s), src)


## ART-6 3A: the baked BREACHED strip (null when it is missing), loaded once.
static func bits_sheet() -> Texture2D:
	if not _bits_loaded:
		_bits_loaded = true
		_bits_tex = load(BITS_SHEET) as Texture2D if ResourceLoader.exists(BITS_SHEET) else null
	return _bits_tex


## ART-6 3A: the strip frame shown at burst progress `u` (0..1): frame i is the concept's
## bit_burst at t = i / BITS_FRAMES.
static func bits_frame(u: float) -> int:
	return clampi(floori(clampf(u, 0.0, 1.0) * BITS_FRAMES), 0, BITS_FRAMES - 1)

func _draw_home(k: float) -> void:
	if home_id == &"":
		return
	var p := overlay.icon_at(home_id)
	if p.x == INF:
		return
	var w := HOME_BAR.x * k
	var h := HOME_BAR.y * k
	var r := Rect2(p + Vector2(-w * 0.5, CityMapOverlay.ICON_RADIUS_BIG * k + HOME_BAR_GAP * k), Vector2(w, h))
	draw_rect(r.grow(1.5 * k), Color(0, 0, 0, 0.85))
	var lag := clampf(_home_lag_value() / home_max, 0.0, 1.0)
	var now := clampf(float(home_shown) / home_max, 0.0, 1.0)
	draw_rect(Rect2(r.position, Vector2(w * lag, h)), Palette.PAPER)
	draw_rect(Rect2(r.position, Vector2(w * now, h)), Palette.CELL_ACID if now > 0.5 else Palette.CELL_PINK)


## TAKEN nodes' corporate tint: a soft disc grows over the streets round the node and
## holds (the city's own tint is baked at the raid's end) until the city's spread starts.
func _draw_tints(_k: float) -> void:
	var fade := 1.0
	if _tint_fade_t0 != INF:
		fade = 1.0 - beat_u(&"influence_crossfade", _tint_fade_t0, RaidBeats.raw_seconds(&"influence_crossfade"))
		if fade <= 0.0:
			return
	var reach := CityInfluence.RADIUS * NeonCity.TILE_A
	for t in _tints:
		if clock < float(t["t0"]):
			continue
		var c := overlay.icon_at(t["site"])
		if c.x == INF:
			continue
		var r := reach * _eased(&"influence_spread", beat_u(&"influence_spread", float(t["t0"]), float(t["dur"])))
		# ART-0 E: a district's wash, held to its tier's alpha (T3, never full screen).
		var mid := Color(threat_color, VfxTier.clamp_alpha(fx_tier("tint"), TINT_ALPHA * fade))
		var edge := Color(threat_color, 0.0)
		for q in TINT_RINGS:
			var a0 := TAU * q / TINT_RINGS
			var a1 := TAU * (q + 1) / TINT_RINGS
			var p0 := c + Vector2(cos(a0), sin(a0) * 0.5) * r
			var p1 := c + Vector2(cos(a1), sin(a1) * 0.5) * r
			draw_polygon(PackedVector2Array([c, p0, p1]), PackedColorArray([mid, edge, edge]))


func _dashed(a: Vector2, b: Vector2, col: Color, width: float, dash: float) -> void:
	var length := a.distance_to(b)
	# ANIM-R1 M15: a bounded count (a zero dash or a length not finite never loops).
	if dash <= 0.0 or not is_finite(length) or not is_finite(dash):
		return
	var dir := (b - a) / maxf(length, 0.001)
	for q in mini(CityMapOverlay.DASHES_MAX, ceili(length / (dash * 2.0))):
		var t := q * dash * 2.0
		_ci.draw_line(a + dir * t, a + dir * minf(t + dash, length), col, width)
