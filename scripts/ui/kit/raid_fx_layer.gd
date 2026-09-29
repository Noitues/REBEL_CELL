class_name RaidFxLayer
extends Control
## Raid execution drawn on the city map (Animation pass ANIM-5, handoff 4.15): threats
## travel their street routes between nodes, guns fire traces, ICE LOCK rings close on a
## threat and freeze it, a DECOY's lure pulls a threat aside, damage numbers pop off
## nodes, HOLDS / DISABLED / SEIZED / BREACHED stamps flip onto nodes, the home server's
## integrity drains with a lag bar, and a Seized node tints the streets round it in the
## corporation's colour until the city's real tint spreads (NeonCity).
##
## A child of a CityMapOverlay (it pans and zooms with the city; sizes are screen px x the
## overlay's `screen_k`). The RaidPlayoutPanel feeds it beats (RaidBeats, built from the
## resolver's events) on its own clock, which runs at Motion.speed (1x / 2x / 4x). The
## city backdrop keeps its own clock. View only: it reads events and the resolved raid,
## never game state, and uses no RNG.

## Node outcomes (RaidResolver) and their stamp words (the raid summary's words, in the
## same order), translated when drawn.
const STAMP_OUTCOMES: Array[String] = ["holds", "disabled", "seized", "passed", "breached"]
const STAMP_TEXT: Array[String] = ["HOLDS", "DISABLED", "SEIZED", "PASSED", "BREACHED"] # TR
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
const THREAT_RED := Palette.HARM  # art pass W9F (§3.3): the threat's harm is HARM
## ANIM-R4 H11a: the token stands on a dark halo ringed in paper, whatever the node under it
## (its red glow over a pink node read pinkish on pink): the halo (radius x the token), its
## colour and the rim's width (px x screen_k).
const TOKEN_HALO := 1.45
const TOKEN_HALO_COLOR := Palette.NET_BG_OUTER  # art pass W9F: a token (not a literal)
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
## CAMPAIGN LOST, the verdict's own word, when the home server fell.
const BANNER_HOME := "HOME %s · HOLDS" # TR
const BANNER_HOLDS := "HOME HOLDS" # TR
const BANNER_BREACHED := RaidVerdict.LOST
## ANIM-R3 B5: gap between the banner and what it keeps clear of, and from the map's edge
## (screen px x screen_k); numbers on one node stack this many of their lines apart.
const BANNER_CLEAR := 8.0
const NUMBER_STACK := 1.05
const NUMBER_GAP := 6.0

## Art pass W6: the VFX tier of drawn effect `kind` (a FX_MOTION key; T2 when unknown).
static func fx_tier(kind: String) -> int:
	return VfxTier.of(FX_MOTION[kind]) if FX_MOTION.has(kind) else VfxTier.T2


## ANIM-R1 M4: a hit on the home server shows now (its number starts): `damage` from Site
## `site` (the screen flies the number into its home counter).
signal home_hit_shown(damage: int, site: StringName)
## Alpha of a Seized node's corporate tint disc (its reach is CityInfluence.RADIUS lots).
const TINT_ALPHA := 0.24
## Art pass W6 (ART_BIBLE 8): each drawn effect's motion entry, whose tier it keeps to. All
## are local (T2 on a node or a threat, T3 for a district's tint and the result banner):
## nothing here is T4 and nothing covers the screen.
const FX_MOTION := {"trace": &"turret_trace", "hit": &"raid_hit_effect", "lock": &"ice_lock_ring", "frost": &"ice_lock_ring",
	"number": &"node_damage_number", "stamp": &"raid_flip", "outcome": &"raid_outcome_stagger", "banner": &"raid_result_banner",
	"tint": &"influence_spread", "home": &"home_lag", "token": &"raid_move"}
## A raid hit's ring reaches at most this many of its rest radii (its node's region, T2).
const HIT_REGION := 2.0
const TINT_RINGS := 24

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


func _init(p_overlay: CityMapOverlay = null) -> void:
	overlay = p_overlay
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
	var nodes: Dictionary = results.get("nodes", {})
	for id in nodes:
		_node_left[String(id)] = int(nodes[id].get("before", 0))
	queue_redraw()


func _process(delta: float) -> void:
	if not is_visible_in_tree():
		return
	# After the playout the layer keeps its own time (the tint fade, the last numbers).
	if _owner_done:
		clock += delta
	_show_due_hits()
	if _tint_fade_t0 == INF and not _tints.is_empty() and overlay != null and overlay.city != null and overlay.city.influence_pin == null \
			and overlay.city.showing_current_look():
		_tint_fade_t0 = clock
	queue_redraw()


## Every beat at its end at once (Skip, reduce effects, headless).
func finish_all() -> void:
	clock = maxf(clock, _last_end())
	_show_due_hits()
	home_shown = home_value
	queue_redraw()


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
			_tokens[String(e["threat"])] = {"site": StringName(e["site"]), "enter_at": t0, "enter_at_dur": dur}
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
		"shot":
			# ANIM-R1 M4: strictly shot, hit, number: the trace flies to the threat over
			# `turret_trace`, the hit lands as it arrives, the damage rises after the hit.
			var trace := RaidBeats.raw_seconds(&"turret_trace")
			var hit := RaidBeats.raw_seconds(&"raid_hit_effect")
			_fx.append({"kind": "trace", "site": StringName(e["site"]), "threat": String(e["threat"]), "t0": t0, "dur": trace, "hit": hit})
			_fx.append({"kind": "hit", "threat": String(e["threat"]), "t0": t0 + trace, "dur": hit})
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
		"disabled":
			# ANIM-R3 B5: the hit that disables takes what integrity was left (its own number).
			var site := StringName(e["site"])
			var left := int(_node_left.get(String(site), 0))
			if left > 0:
				_number(site, -left, Palette.CELL_PINK, t0, dur)
			_node_left[String(site)] = 0
			_stamp(site, "disabled", Palette.CELL_PINK, t0, dur)
		"seized":
			# ANIM-R3 B5: a Site seized with integrity left (threats standing on it at the step
			# cap) loses it all: its own number, so the numbers add up to before - after.
			var seized_site := StringName(e["site"])
			var seized_left := int(_node_left.get(String(seized_site), 0))
			if seized_left > 0:
				_number(seized_site, -seized_left, Palette.RESIST_GOLD, t0, dur)
			_node_left[String(seized_site)] = 0
			_stamp(seized_site, "seized", Palette.RESIST_GOLD, t0, dur)
			_tints.append({"site": StringName(e["site"]), "t0": t0, "dur": RaidBeats.raw_seconds(&"influence_spread")})
		"home_lost":
			# ANIM-R3 B5: home's verdict is its banner (no stamp over it).
			_banner = {"text": CityMapOverlay.tr_word(BANNER_BREACHED), "color": RaidVerdict.color_of(false), "t0": t0}  # W8b §3.3: HARM, never pink
		"raid_end":
			# ANIM-R2 R6: the outcomes stamp node after node (`raid_outcome_stagger`, by id),
			# then the result banner stamps over home. ANIM-R3 B5: every node's stamp is its
			# resolved outcome (one verdict word per node, the word its label says), home's
			# verdict is the banner alone.
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
					_number(home_id, after - home_value, Palette.HARM, t0, dur)
					_home_hit(home_value - after, t0, home_id)
			if _banner.is_empty():
				var lost := int(_results.get("home_before", home_value)) - int(_results.get("home_after", home_value))
				_banner = {"text": CityMapOverlay.tr_word(BANNER_HOME) % TextDb.signed(-lost) if lost > 0 else CityMapOverlay.tr_word(BANNER_HOLDS),
					"color": RaidVerdict.color_of(lost <= 0),
					"t0": maxf(t0, last + flip) + Motion.delay_of(BANNER_MOTION)}
	queue_redraw()


## ANIM-R3 B5: a stamp's colour by outcome (acid holds, gold seized, pink the rest).
static func stamp_color(outcome: String) -> Color:
	match outcome:
		"holds":
			return Palette.GAIN
		"seized":
			return Palette.RESIST_GOLD
	return Palette.HARM  # W8b §3.3: a fallen node is HARM, never the Cell's pink


func _number(site: StringName, value: int, col: Color, t0: float, dur: float) -> void:
	if value == 0:
		return
	_fx.append({"kind": "number", "site": site, "text": TextDb.signed(value), "value": value, "color": col, "t0": t0, "dur": dur})


func _stamp(site: StringName, outcome: String, col: Color, t0: float, dur: float) -> void:
	_stamps[String(site)] = {"word": stamp_text(outcome), "color": col, "t0": t0, "dur": dur}


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
	if e == null or _home_lag_t0 == -INF:
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
	_draw_tints(k)
	var at := _token_positions()
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
	for id in _stamps:
		_draw_stamp(StringName(id), _stamps[id], k)
	_draw_home(k)
	# ANIM-R3 B5: numbers over the stamps (a stamp hid the hit on home under it).
	for f in _fx:
		if f["kind"] == "number":
			_draw_number(f, k, at)
	_draw_banner(k)


## ANIM-R2 R6: the result banner over home: stamps on from `raid_result_banner`'s amplitude
## and stays (the result).
func _draw_banner(k: float) -> void:
	if _banner.is_empty() or clock < float(_banner["t0"]):
		return
	var place := banner_rect()
	if not place.has_area():
		return
	var u := _u(float(_banner["t0"]), Motion.seconds(BANNER_MOTION))
	var grow := lerpf(Motion.amplitude(BANNER_MOTION), 1.0, _eased(BANNER_MOTION, u))
	var fs := maxi(1, roundi(BANNER_FONT * Settings.text_scale * k))
	var font := Palette.display()
	var text := String(_banner["text"])
	var size := place.size
	var col: Color = _banner["color"]
	# ANIM-R3 B9: it fades in over `stamp_fade_in`'s share of its stamp-on (was u * 3.0).
	var a := clampf(u / maxf(Motion.amplitude(&"stamp_fade_in"), 0.001), 0.0, 1.0)
	draw_set_transform(place.get_center(), deg_to_rad(STAMP_TILT), Vector2.ONE * grow)
	var box := Rect2(-size * 0.5, size)
	draw_rect(box.grow(3.0 * k), Color(0, 0, 0, 0.85 * a))
	draw_rect(box, Color(Palette.NIGHT_SKY, 0.95 * a))
	draw_rect(box, Color(col, a), false, 3.0 * k)
	draw_string(font, box.position + Vector2(BANNER_PAD * k, BANNER_PAD * k + font.get_ascent(fs)), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(col, a))
	draw_set_transform(Vector2.ZERO)


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
	var fs := maxi(1, roundi(BANNER_FONT * Settings.text_scale * k))
	var size := Palette.display().get_string_size(String(_banner["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs) + Vector2(BANNER_PAD, BANNER_PAD) * 2.0 * k
	var clear := BANNER_CLEAR * k
	var r_icon := CityMapOverlay.ICON_RADIUS_BIG * k
	var bar_bottom := r_icon + (HOME_BAR_GAP + HOME_BAR.y) * k
	var spots: Array[Vector2] = [
		p + Vector2(0, -r_icon - clear - size.y * 0.5),
		p + Vector2(0, -BANNER_LIFT * k - r_icon),
		p + Vector2(0, bar_bottom + clear + size.y * 0.5),
		p + Vector2(-r_icon - clear - size.x * 0.5, 0),
		p + Vector2(r_icon + clear + size.x * 0.5, 0),
	]
	var avoid := banner_avoid()
	var area := get_rect().grow(-clear)
	var best := Rect2()
	var best_hits := INF
	for c in spots:
		var r := Rect2(c - size * 0.5, size)
		# Kept inside the map (slid in from an edge).
		r.position = r.position.clamp(area.position, (area.end - r.size).max(area.position))
		var hits := 0.0
		for a in avoid:
			var g := a.grow(clear * 0.5)
			if r.intersects(g):
				hits += r.intersection(g).get_area() + 1.0
		if hits < best_hits:
			best_hits = hits
			best = r
			if hits == 0.0:
				break
	return best


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
	return clampf((clock - t0) / maxf(dur, 0.001), 0.0, 1.0)


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
		var moving: bool = not mv.is_empty() and clock < float(mv["t0"]) + float(mv["dur"])
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
		if mv.is_empty() or clock <= float(mv["t0"]) or clock >= float(mv["t0"]) + float(mv["dur"]):
			continue
		out[id] = _along_move(mv, _eased(&"raid_move", _u(float(mv["t0"]), float(mv["dur"]))))
	return out


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
		at += side * sin(u * PI) * Motion.amplitude(&"decoy_fire") * overlay.screen_k()
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
	var alpha := 1.0
	if enter > -INF:
		var pop := _u(enter, float(t.get("enter_at_dur", 0.0)))
		s *= lerpf(Motion.amplitude(&"node_pop"), 1.0, _eased(&"node_pop", pop)) if pop < 1.0 else 1.0
		alpha = pop if pop < 1.0 else 1.0
	if t.has("dead_at"):
		var du := _u(float(t["dead_at"]), float(t.get("dead_at_dur", 0.0)))
		if du >= 1.0:
			return
		s *= lerpf(1.0, Motion.amplitude(&"raid_hit_effect"), du)
		alpha *= 1.0 - du
	var mv: Dictionary = t.get("move", {})
	var moving: bool = not mv.is_empty() and clock > float(mv["t0"]) and clock < float(mv["t0"]) + float(mv["dur"])
	if moving and mv["decoy"] != &"":
		var lure := overlay.icon_at(mv["decoy"])
		if lure.x != INF:
			_dashed(lure, p, Color(Palette.RESIST_GOLD, 0.8), 1.5 * k, PULL_DASH * k)
	if moving:
		# ANIM-R2 R6: a fading red trail behind it along its street.
		var u := _u(float(mv["t0"]), float(mv["dur"]))
		for q in range(1, TRAIL_DOTS + 1):
			var tp := _along_move(mv, _eased(&"raid_move", maxf(0.0, u - q * TRAIL_STEP)))
			if tp.x != INF:
				var fade := 1.0 - float(q) / (TRAIL_DOTS + 1)
				draw_circle(tp, s * 0.45 * fade, Color(THREAT_RED, 0.75 * fade * alpha))
	var dia := _diamond(p, s)
	# ANIM-R4 H11a: a dark halo with a paper rim under the diamond: high contrast on any node.
	draw_circle(p, s * TOKEN_HALO, Color(TOKEN_HALO_COLOR, TOKEN_HALO_COLOR.a * alpha))
	draw_arc(p, s * TOKEN_HALO, 0, TAU, 24, Color(Palette.PAPER, alpha), TOKEN_RIM * k)
	draw_polyline(dia + PackedVector2Array([dia[0]]), Color(0, 0, 0, 0.9 * alpha), 6.0 * k)
	draw_colored_polygon(dia, Color(Palette.PAPER, alpha))
	draw_polyline(dia + PackedVector2Array([dia[0]]), Color(THREAT_RED, alpha), 3.0 * k)
	draw_circle(p, s * 0.28, Color(threat_color, alpha))
	draw_arc(p, s * 0.28, 0, TAU, 12, Color(0, 0, 0, 0.8 * alpha), 1.0 * k)
	if t.get("frozen", false):
		draw_arc(p, FROST_RING * k, 0, TAU, 20, Color(Palette.NET_CYAN, 0.8 * alpha), 2.0 * k)


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
	var u := _u(t0, fly)
	var a := 1.0 if u < 1.0 else 1.0 - _u(t0 + fly, fade)
	var head := from.lerp(to, _eased(&"turret_trace", u))
	var muzzle := 1.0 - u
	if muzzle > 0.0:
		draw_arc(from, MUZZLE_RING * k * (1.0 + 0.4 * u), 0, TAU, 24, Color(Palette.CELL_ACID, muzzle), 3.0 * k)
	draw_line(from, head, Color(0, 0, 0, 0.6 * a), TRACE_WIDTH * 4.0 * k)
	draw_line(from, head, Color(Palette.CELL_ACID, 0.45 * a), TRACE_WIDTH * 3.0 * k)
	draw_line(from, head, Color(Palette.PAPER, a), TRACE_WIDTH * k)
	if u < 1.0:
		draw_circle(head, TRACE_WIDTH * 1.8 * k, Palette.PAPER)
	draw_circle(from, 4.0 * k, Color(Palette.CELL_ACID, a))


func _draw_lock(f: Dictionary, at: Dictionary, k: float) -> void:
	if clock < float(f["t0"]):
		return
	var u := _u(float(f["t0"]), float(f["dur"]))
	if f["kind"] == "frost" and u >= 1.0:
		return
	var p: Vector2 = at.get(String(f["threat"]), Vector2(INF, INF))
	if p.x == INF:
		return
	var rest := FROST_RING * k
	if f["kind"] == "lock":
		if u >= 1.0:
			return
		var r := lerpf(rest * Motion.amplitude(&"ice_lock_ring"), rest, _eased(&"ice_lock_ring", u))
		draw_arc(p, r, 0, TAU, 28, Color(Palette.NET_CYAN, 0.35 + 0.65 * u), 3.0 * k)
		for q in 6:
			var d := Vector2.from_angle(TAU * q / 6.0)
			draw_line(p + d * r, p + d * (r + 4.0 * k), Palette.NET_CYAN, 1.5 * k)
	else:
		draw_arc(p, rest * (1.0 + 0.3 * (1.0 - u)), 0, TAU, 20, Color(Palette.NET_CYAN, 1.0 - u), 2.0 * k)


func _draw_hit(f: Dictionary, at: Dictionary, k: float) -> void:
	var u := _u(float(f["t0"]), float(f["dur"]))
	if clock < float(f["t0"]) or u >= 1.0:
		return
	var p: Vector2 = at.get(String(f["threat"]), Vector2(INF, INF))
	if p.x == INF:
		return
	var r := HIT_RING * k * lerpf(1.0, Motion.amplitude(&"raid_hit_effect"), _eased(&"raid_hit_effect", u))
	# Art pass W6: held to its tier's reach (the threat's own spot, never the map).
	r = VfxTier.clamp_radius(fx_tier("hit"), r, HIT_RING * k, HIT_RING * k * HIT_REGION)
	draw_arc(p, r, 0, TAU, 20, Color(Palette.PAPER, 1.0 - u), 2.5 * k)
	for q in 4:
		var d := Vector2.from_angle(PI * 0.25 + q * PI * 0.5)
		draw_line(p + d * r * 0.6, p + d * r * 1.2, Color(Palette.CELL_ACID, 1.0 - u), 2.0 * k)


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
	var rise := Motion.amplitude(&"node_damage_number") * k * _eased(&"node_damage_number", u)
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
	if not f.has("threat"):
		at = _off_labels(at, Vector2(w, fs), p, k)
	var a := 1.0 if u < 0.66 else (1.0 - u) / 0.34
	draw_string_outline(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(1, roundi(4.0 * k)), Color(0, 0, 0, 0.9 * a))
	draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(f["color"], a))


## Art pass W8b (critique 24/26): a node's number at baseline `at` (text `box` px) moved off
## the map's labels: its own spot when clear, else left of its node, else above it.
func _off_labels(at: Vector2, box: Vector2, node_at: Vector2, k: float) -> Vector2:
	var labels: Array = overlay.label_rects().values()
	var tries: Array[Vector2] = [at, Vector2(node_at.x - CityMapOverlay.ICON_RADIUS_BIG * k - NUMBER_GAP * k - box.x, at.y),
		Vector2(node_at.x - box.x * 0.5, node_at.y - CityMapOverlay.ICON_RADIUS_BIG * k - NUMBER_GAP * k - box.y * 0.2)]
	for t in tries:
		var r := Rect2(t - Vector2(0, box.y * 0.8), box)
		var clear := true
		for l: Rect2 in labels:
			if r.intersects(l):
				clear = false
				break
		if clear:
			return t
	return at


## How many numbers on the same Site show now and started before `f` (its row in the stack).
func _stack_of(f: Dictionary) -> int:
	var n := 0
	for g in _fx:
		if g == f:
			break
		if g["kind"] == "number" and g.has("site") and g["site"] == f["site"] and clock >= float(g["t0"]) and _u(float(g["t0"]), float(g["dur"])) < 1.0:
			n += 1
	return n


func _draw_stamp(site: StringName, s: Dictionary, k: float) -> void:
	if clock < float(s["t0"]):
		return
	var p := overlay.icon_at(site)
	if p.x == INF:
		return
	var u := _u(float(s["t0"]), float(s["dur"]))
	var angle := lerpf(Motion.amplitude(&"raid_flip"), 0.0, _eased(&"raid_flip", u))
	var sx := maxf(0.05, cos(deg_to_rad(angle)))
	var word := CityMapOverlay.tr_word(String(s["word"]))
	var fs := maxi(1, roundi(STAMP_FONT * Settings.text_scale * k))
	var font := Palette.display()
	var size := font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs) + Vector2(STAMP_PAD, STAMP_PAD) * 2.0 * k
	var col: Color = s["color"]
	draw_set_transform(p + Vector2(0, -STAMP_LIFT * k - CityMapOverlay.ICON_RADIUS * k), deg_to_rad(STAMP_TILT), Vector2(sx, 1.0))
	var box := Rect2(-size * 0.5, size)
	draw_rect(box, Color(Palette.NIGHT_SKY, 0.85))
	draw_rect(box, col, false, 2.0 * k)
	draw_string(font, box.position + Vector2(STAMP_PAD * k, STAMP_PAD * k + font.get_ascent(fs)), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	draw_set_transform(Vector2.ZERO)


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


## Seized nodes' corporate tint: a soft disc grows over the streets round the node and
## holds (the city's own tint is baked at the raid's end) until the city's spread starts.
func _draw_tints(_k: float) -> void:
	var fade := 1.0
	if _tint_fade_t0 != INF:
		fade = 1.0 - _u(_tint_fade_t0, RaidBeats.raw_seconds(&"influence_crossfade"))
		if fade <= 0.0:
			return
	var reach := CityInfluence.RADIUS * NeonCity.TILE_A
	for t in _tints:
		if clock < float(t["t0"]):
			continue
		var c := overlay.icon_at(t["site"])
		if c.x == INF:
			continue
		var r := reach * _eased(&"influence_spread", _u(float(t["t0"]), float(t["dur"])))
		# Art pass W6: a district's wash, held to its tier's alpha (T3, never full screen).
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
		draw_line(a + dir * t, a + dir * minf(t + dash, length), col, width)
