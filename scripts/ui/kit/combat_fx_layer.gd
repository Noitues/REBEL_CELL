class_name CombatFxLayer
extends Control
## The combat scene's motion overlay (Animation pass ANIM-2 / ANIM-3): short-lived drawn
## effects over the arena (floating numbers, hit lines, bursts, rings, status stamps, the
## pieces of a broken wheel, hub glass, VHS rewind lines, the VICTORY / DEFEAT stamp, the
## deck and discard piles, the aim reticle) and card copies that fly (play, discard,
## exhaust, a cancelled drag's return). Every timing comes from ui_motion.tres through
## `Motion`; nothing is added when motion doesn't play (reduce effects, headless), so the
## end state never waits on it. View only: it draws, it never touches game state, and its
## scatter comes from hashes, never from an RNG. It takes no input.

## Floating number lettering at text scale 1.0 (px) and its white outline.
const NUMBER_FONT := 24
const NUMBER_OUTLINE := 6
## Star burst: spikes round a crit, and their inner radius share.
const BURST_SPIKES := 10
const BURST_INNER := 0.35
## Hit line arrowhead (px).
const ARROW_HEAD := 9.0
## A number's rise shape: it grows over this share of its life, then holds, and fades
## over the last FADE_SHARE.
const GROW_SHARE := 0.25
const FADE_SHARE := 0.35
## ANIM-R2 E10 (named, were inline): a number grows in from this share of its size; a crit
## pops from this scale and settles; a travelling number fades to this alpha on its way.
const GROW_FROM := 0.6
const CRIT_POP_SCALE := 1.35
const TRAVEL_FADE_TO := 0.6
## ANIM-R4 C5: a hit's projectile flies over `hit_line_flight`'s share of `hit_line` (the
## impact), and its line fades over the rest (the table's, see line_share()).
## The number riding with a projectile: its size as a share of a floating number's, and its
## offset from the projectile's head (share of that size).
const RIDE_FONT_SHARE := 0.8
const RIDE_OFFSET := 0.9
## ANIM-R3 A6c / ANIM-R4 C5: the slice's own value rides `ride_swap`'s share of the flight,
## shrinking to `ride_shrink`'s share of its size, before the dealt value takes its place
## (both in the motion table).
## Status stamp lettering (px at text scale 1.0) and its disc.
const STAMP_FONT := 16
const STAMP_DISC := 11.0
## Glass shards of a breached hub, and ember flecks of an exhausted card.
const GLASS_SHARDS := 12
const EMBERS := 9
## VHS rewind bands across the arena.
const VHS_BANDS := 7
const VHS_BAND_PX := 3.0
## VICTORY / DEFEAT lettering at text scale 1.0 (px).
const WORD_FONT := 64
## Pile marks: a small stack of card backs (px at text scale 1.0).
const PILE_SIZE := Vector2(34, 46)
const PILE_LAYERS := 3
## Reticle brackets round the aimed zone (px).
const RETICLE_RADIUS := 16.0
const RETICLE_ARC := 0.45
## A discarded card shrinks to this scale and loses this much alpha on its way.
const DISCARD_SCALE := 0.4
const DISCARD_FADE := 0.6

## Live sprites: each {kind, age, dur, ...}; drawn and aged in _process.
var sprites: Array[Dictionary] = []
## Card copies in flight: {node, tween, to, kind}.
var flights: Array[Dictionary] = []
## The aim reticle (global), shown while a card is aimed; `reticle_visible` false = none.
var reticle_pos: Vector2 = Vector2.ZERO
var reticle_visible: bool = false
var reticle_pop: float = 0.0
var _reticle_tween: Tween = null
var _serial: int = 0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_process(false)


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## True while any effect or flight is still playing.
func busy() -> bool:
	return not sprites.is_empty() or not flights.is_empty()


## Ends every effect at once (skip): sprites vanish, flying cards land where they were
## going (their `on_done` runs) and are freed.
func clear() -> void:
	sprites.clear()
	for f in flights.duplicate():
		_end_flight(f)
	flights.clear()
	set_process(false)
	queue_redraw()


func _process(delta: float) -> void:
	var keep: Array[Dictionary] = []
	var arrived: Array[Callable] = []
	for s in sprites:
		s["age"] = float(s["age"]) + delta
		if float(s["age"]) < float(s["dur"]) + float(s.get("delay", 0.0)):
			keep.append(s)
		elif String(s["kind"]) == "travel" and (s["on_arrive"] as Callable).is_valid():
			arrived.append(s["on_arrive"])
	sprites = keep
	for c in arrived:
		c.call()
	queue_redraw()
	if sprites.is_empty() and flights.is_empty():
		set_process(false)


func _add(s: Dictionary) -> void:
	_serial += 1
	s["serial"] = _serial
	s["age"] = 0.0
	sprites.append(s)
	set_process(true)
	queue_redraw()


## A sprite's progress 0..1 (0 before its delay has run).
static func _p(s: Dictionary) -> float:
	var d := float(s["dur"])
	var a := float(s["age"]) - float(s.get("delay", 0.0))
	return clampf(a / d, 0.0, 1.0) if d > 0.0 else 1.0


static func _ease(s: Dictionary) -> float:
	return Tween.interpolate_value(0.0, 1.0, _p(s), 1.0, int(s.get("trans", Tween.TRANS_LINEAR)), int(s.get("ease", Tween.EASE_OUT)))


## Hash noise 0..1 (decoration only).
static func _h(a: int, b: int, c: int = 0) -> float:
	return float(hash(Vector3i(a, b, c)) & 0xFFFF) / 65535.0


func _local(global: Vector2) -> Vector2:
	return global - get_global_rect().position


# --- Effects -----------------------------------------------------------------------------

## A number that pops at `at` (global) and drifts `rise` px along `dir` (`id` = its motion
## entry: amplitude = the drift unless `rise` >= 0). Crits grow by `number_crit` and get
## a star burst. Returns the rect it covers at its biggest (global), for layout checks.
func number(at: Vector2, text: String, color: Color, id: StringName, dir: Vector2 = Vector2.UP, crit: bool = false, rise: float = -1.0,
		font_size: int = -1, band: String = "", extra_delay: float = 0.0, icon: int = -1) -> Rect2:
	var fs := number_font(crit) if font_size <= 0 else font_size
	var drift := Motion.amplitude(id) if rise < 0.0 else rise
	var rect := number_rect(at, text, crit, dir * drift, fs, icon)
	if not Motion.live(id):
		return rect
	_hurry(band)
	var e := Motion.entry(id)
	_add({"kind": "number", "at": at, "text": text, "color": color, "dur": Motion.seconds(id), "delay": Motion.delay_of(id) + extra_delay,
		"dir": dir, "rise": drift, "fs": fs, "crit": crit, "ease": e.ease, "trans": e.trans, "band": band, "icon": icon})
	# Art pass W6 (ART_BIBLE 8): the slice's own hit shape where the number lands: a crit
	# shatters (it was a star burst), a guard's shield / evade number its plates / smear, a
	# heal its plus signs.
	if crit:
		hit_vfx(at, HIT_CRIT, Color(0, 0, 0, 0), extra_delay + Motion.delay_of(id))
	elif _guard_icon(icon, []) >= 0:
		hit_vfx(at, hit_kind(_guard_icon(icon, [])), Color(0, 0, 0, 0), extra_delay + Motion.delay_of(id))
	elif id == &"heal_number":
		hit_vfx(at, HIT_HEAL, Color(0, 0, 0, 0), extra_delay + Motion.delay_of(id))
	return rect


## ANIM-R3 A6a: what a hit did, shown where it struck (`at`, global: the arrowhead on the
## victim's HP ring or its token): a glyph (`icon`, a slice type: DEFEND for a hit soaked
## whole, EVADE for one evaded) and `text` ("0"), popping from `impact_mark`'s amplitude
## scale after `delay` (the impact), holding its duration and fading.
## ANIM-R4 C6c: with `items` (hit_equation's: sword and the raw hit, the guard's glyph and
## what it took, "=" and what got through) the mark is that equation, the one notation for
## a hit meeting a guard ("8 - 8 = 0" as glyphs).
func impact(at: Vector2, text: String, icon: int, color: Color, delay: float = 0.0, items: Array = []) -> void:
	if not Motion.live(&"impact_mark"):
		return
	var fs := roundi(NUMBER_FONT * Settings.text_scale * IMPACT_FONT_SHARE)
	_add({"kind": "impact", "at": at, "text": text, "icon": icon, "color": color, "fs": fs, "delay": delay,
		"dur": Motion.seconds(&"impact_mark"), "from": Motion.amplitude(&"impact_mark"), "items": items})
	# Art pass W6 (ART_BIBLE 8): the guard that met the hit shows its shape where it struck
	# (hex plates for a shield or a block, an afterimage smear for an evade).
	var guard := _guard_icon(icon, items)
	if guard >= 0:
		hit_vfx(at, hit_kind(guard), Color(0, 0, 0, 0), delay)


## The box an impact mark covers at rest (global), for the layout checks.
static func impact_rect(at: Vector2, text: String, icon: int, items: Array = []) -> Rect2:
	var fs := roundi(NUMBER_FONT * Settings.text_scale * IMPACT_FONT_SHARE)
	var w := equation_width(items, fs, Palette.display()) if not items.is_empty() \
		else Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + glyph_width(fs, icon)
	return Rect2(at - Vector2(w * 0.5 + fs * 0.2, fs * 0.65), Vector2(w + fs * 0.4, fs * 1.3))


## ANIM-R4 C6c: one notation for a hit and its guard, everywhere (the mark where a hit
## struck, the icon row under an HP): items [{icon (a slice type, -1 = none), text, color,
## sep ("" / the minus / "=", drawn before it)}]. Their width at `fs` in `font`.
static func equation_width(items: Array, fs: int, font: Font) -> float:
	var w := 0.0
	for it in items:
		if String(it.get("sep", "")) != "":
			w += fs * EQ_SEP_SHARE
		if int(it.get("icon", -1)) >= 0:
			w += fs * EQ_ICON_SHARE
		w += font.get_string_size(String(it["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * EQ_GAP_SHARE
	return maxf(0.0, w - fs * EQ_GAP_SHARE)


## Draws `items` (see equation_width) from `left_mid` (the left end of its middle line) on
## `ci` at `fs` in `font`, faded to `alpha`; `outline` rings the numbers (0 = none).
static func draw_equation(ci: CanvasItem, left_mid: Vector2, items: Array, fs: int, font: Font, alpha: float, outline: int = 0) -> void:
	var x := left_mid.x
	var mid := left_mid.y
	for it in items:
		var col := Color(it.get("color", Palette.PAPER), alpha)
		var sep := String(it.get("sep", ""))
		if sep != "":
			ci.draw_string(font, Vector2(x, mid + fs * 0.35), sep, HORIZONTAL_ALIGNMENT_CENTER, fs * EQ_SEP_SHARE, fs, Color(Palette.PAPER, alpha))
			x += fs * EQ_SEP_SHARE
		if int(it.get("icon", -1)) >= 0:
			SliceIcon.draw_icon(ci, Vector2(x + fs * EQ_ICON_SHARE * 0.5, mid), fs * 0.45, int(it["icon"]), col)
			x += fs * EQ_ICON_SHARE
		var t := String(it["text"])
		if outline > 0:
			ci.draw_string_outline(font, Vector2(x, mid + fs * 0.35), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, outline, Color(Palette.NIGHT_SKY, alpha))
		ci.draw_string(font, Vector2(x, mid + fs * 0.35), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
		x += font.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * EQ_GAP_SHARE


## The equation's parts (drawing, not motion): a joining sign's room, a glyph's room and the
## gap after a number, as shares of the lettering; the minus it uses.
const EQ_SEP_SHARE := 1.0
const EQ_ICON_SHARE := 1.05
const EQ_GAP_SHARE := 0.2
const EQ_MINUS := "−"


## ANIM-R1: a number that pops at `at` (global), holds (`number_to_hp`'s delay), then
## travels into `to` (the victim's HP counter) shrinking to `number_to_hp`'s amplitude;
## `on_arrive` runs as it gets there (the HP rolls down then). A skip drops it (the end
## state shows anyway). `band` names the hub band it sits in: a new number in the same
## band sends the one resting there on its way at once, so two never rest on each other.
## ANIM-R2: it shows `delay` seconds from now (a hit's impact); with `raw` it first shows
## the hit's raw number for `absorb` seconds (a guard takes its part meanwhile), then pops
## to `text`, the HP it takes, which is what travels.
func travel_number(at: Vector2, to: Vector2, text: String, color: Color, crit: bool, font_size: int, band: String,
		on_arrive: Callable = Callable(), delay: float = 0.0, raw: String = "", absorb: float = 0.0) -> void:
	if not Motion.live(&"number_to_hp"):
		if on_arrive.is_valid():
			on_arrive.call()
		return
	_hurry(band)
	var e := Motion.entry(&"number_to_hp")
	var swap := absorb if raw != "" else 0.0
	var hold := swap + Motion.delay_of(&"number_to_hp")
	_add({"kind": "travel", "at": at, "to": to, "text": text, "raw": raw, "swap": swap, "color": color, "fs": font_size, "crit": crit,
		"delay": delay, "hold": hold, "dur": hold + Motion.seconds(&"number_to_hp"),
		"shrink": Motion.amplitude(&"number_to_hp"), "ease": e.ease, "trans": e.trans, "band": band, "on_arrive": on_arrive})
	# Art pass W6 (ART_BIBLE 8): what got through lands with its slice's hit shape: a crit
	# shatters, a hit slashes, a heal ("+N") rises in plus signs.
	if crit:
		hit_vfx(at, HIT_CRIT, Color(0, 0, 0, 0), delay)
	elif text.begins_with("+"):
		hit_vfx(at, HIT_HEAL, Color(0, 0, 0, 0), delay)
	else:
		hit_vfx(at, HIT_ATTACK, Color(0, 0, 0, 0), delay)


## The numbers resting in `band` move on: a travelling one sets off now, a floating one
## goes (ANIM-R1: numbers never rest on each other).
func _hurry(band: String) -> void:
	if band == "":
		return
	for s in sprites.duplicate():
		if String(s.get("band", "")) != band:
			continue
		if String(s["kind"]) == "travel":
			s["age"] = maxf(float(s["age"]), float(s.get("delay", 0.0)) + float(s["hold"]))
		elif String(s["kind"]) == "number":
			sprites.erase(s)


## Numbers resting in their band now (not yet travelling): [{rect (global), band}], for
## the layout checks.
func resting_numbers() -> Array:
	var out: Array = []
	for s in sprites:
		var k := String(s["kind"])
		var a := float(s["age"]) - float(s.get("delay", 0.0))
		if a < 0.0:
			continue
		if k == "number" or (k == "travel" and a < float(s["hold"])):
			out.append({"rect": number_rect(s["at"], String(s["text"]), bool(s["crit"]), Vector2.ZERO, int(s["fs"]), int(s.get("icon", -1))), "band": String(s.get("band", ""))})
	return out


## Font size of a floating number (crits bigger by `number_crit`'s amplitude).
static func number_font(crit: bool) -> int:
	var fs := NUMBER_FONT * Settings.text_scale
	if crit:
		fs *= maxf(1.0, Motion.amplitude(&"number_crit"))
	return roundi(fs)


## Everything a number covers on its way (global): its start and end boxes merged.
static func number_rect(at: Vector2, text: String, crit: bool, travel: Vector2, font_size: int = -1, icon: int = -1) -> Rect2:
	var fs := number_font(crit) if font_size <= 0 else font_size
	var w := Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + NUMBER_OUTLINE + glyph_width(fs, icon)
	var box := Rect2(at - Vector2(w * 0.5, fs * 0.5), Vector2(w, fs))
	return box.merge(Rect2(box.position + travel, box.size))


## The room a number's glyph takes before its text (0 without one): ANIM-R3 A6e, a block is
## a shield glyph and its number, not a word.
static func glyph_width(fs: int, icon: int) -> float:
	return fs * (GLYPH_SHARE + GLYPH_GAP) if icon >= 0 else 0.0


## ANIM-R3: a number's glyph (a slice icon) as a share of its font size and the gap after
## it; an impact mark's lettering as a share of a floating number's.
const GLYPH_SHARE := 0.9
const GLYPH_GAP := 0.15
const IMPACT_FONT_SHARE := 0.85


## A star burst at `at` (global) growing to `id`'s amplitude px (or x its scale when the
## amplitude is a scale below 4).
func burst(at: Vector2, color: Color, id: StringName, delay: float = 0.0) -> void:
	if not Motion.live(id):
		return
	var amp := Motion.amplitude(id)
	var radius := amp if amp >= 4.0 else NUMBER_FONT * Settings.text_scale * amp
	_add({"kind": "burst", "at": at, "color": color, "dur": Motion.seconds(id), "radius": radius, "delay": delay})


## A ring at `at` (global) growing from `radius` by `id`'s amplitude px as it fades.
func ring(at: Vector2, radius: float, color: Color, id: StringName) -> void:
	if not Motion.live(id):
		return
	_add({"kind": "ring", "at": at, "r0": radius, "grow": Motion.amplitude(id), "color": color, "dur": Motion.seconds(id)})


## A hit from `from` to `to` (global): a projectile (a bright head with an arrowhead, its
## thick trail in the attacker's `color`) flies over `hit_line_flight` of `hit_line`, `label`
## (the hit's raw number) riding beside it; the line then fades with the arrowhead at the
## victim. ANIM-R2: hits play one at a time (the schedule spaces them `hit_line` apart).
## ANIM-R3 A6c: the aim's multiplier rides too: with `from_label` (the slice's own value)
## that value shows at launch and shrinks into `label` (the hit it deals: "12" becomes
## "6 ½" at half power) over `ride_swap` of the flight; `scale` > 1 draws the riding
## number bigger (a PERFECT landing).
func hit_line(from: Vector2, to: Vector2, color: Color, label: String = "", from_label: String = "", scale: float = 1.0) -> void:
	if not Motion.live(&"hit_line") or from.distance_to(to) < 1.0:
		return
	_add({"kind": "line", "from": from, "to": to, "color": color, "dur": Motion.seconds(&"hit_line"), "width": Motion.amplitude(&"hit_line"),
		"label": label, "from_label": from_label, "scale": scale})


## Every number on its way into an HP counter arrives now (its `on_arrive` runs: the HP
## rolls), and it leaves the layer (ANIM-R3 A5: THIS TURN never shows before a roll).
func arrive_all() -> void:
	var arrived: Array[Callable] = []
	for s in sprites.duplicate():
		if String(s["kind"]) == "travel":
			sprites.erase(s)
			if (s["on_arrive"] as Callable).is_valid():
				arrived.append(s["on_arrive"])
	for c in arrived:
		c.call()
	queue_redraw()


## True while a number is still on its way into an HP counter.
func travelling() -> bool:
	for s in sprites:
		if String(s["kind"]) == "travel":
			return true
	return false


## Seconds from a hit's launch to its impact at the victim (0 when hits don't fly).
static func impact_seconds() -> float:
	return Motion.seconds(&"hit_line") * line_share() if Motion.live(&"hit_line") else 0.0


## ANIM-R4 C5: the share of `hit_line` the projectile flies (the table's `hit_line_flight`).
static func line_share() -> float:
	return clampf(Motion.amplitude(&"hit_line_flight"), 0.05, 0.95)


## ANIM-R2 E5: a short local flash (a disc of `radius` at `at`, global) in `color`, `id`'s
## amplitude its alpha, fading over its duration: a wheel's break flashes here, never the
## whole screen.
## Art pass W6 (ART_BIBLE 8): a local flash like any other: through the one flash limiter
## (Fx.request_flash), its alpha and duration held to `id`'s tier.
func disc_flash(at: Vector2, radius: float, color: Color, id: StringName) -> void:
	if not Motion.live(id) or not Fx.request_flash():
		return
	var tier := VfxTier.of(id)
	_add({"kind": "disc", "at": at, "r": radius, "color": color, "alpha": VfxTier.clamp_alpha(tier, Motion.amplitude(id)),
		"dur": VfxTier.clamp_seconds(tier, Motion.seconds(id))})


# --- Wheel-local T3 bursts (art pass W6, ART_BIBLE 8) ---------------------------------------

## The kinds of wheel_burst: a Perfect landing and a boss's phase change.
const BURST_PERFECT := &"perfect"
const BURST_PHASE := &"phase"
## Each kind's motion entry (T3: duration, peak alpha).
const BURST_MOTION := {&"perfect": &"wheel_burst_perfect", &"phase": &"wheel_burst_phase"}
## A burst's region is its wheel: the disc and its rim, HP arc and bezel, this many disc
## radii out; its ring grows from the rim by RING_GROW radii (held inside the region).
const WHEEL_REGION := 1.35
const BURST_RING_GROW := 0.3
## Ring widths (px at its start and end) and the glow's rim share of the disc.
const BURST_RING_W0 := 10.0
const BURST_RING_W1 := 2.0
const BURST_GLOW_EDGE := 1.0
## The phase ring: dashes round it, the share of each step a dash fills, and its turn over
## the burst (rad). W1-CORPPATTERN: a CorpPattern-like broken ring until W1's CorpPattern lands.
const PHASE_DASHES := 16
const PHASE_DASH_FILL := 0.6
const PHASE_TURN := 0.35
const BURST_SEGMENTS := 48


## ART_BIBLE 8 T3: a burst on one wheel only, never the screen (it retires the full-screen
## Perfect and boss-phase flashes). `wheel_center` (global) and `radius` (the disc's) name
## the wheel; `kind` is BURST_PERFECT (a radial glow and a ring pulse in `color`, default
## CELL_PINK: the wheel-local inversion's light) or BURST_PHASE (a broken ring in `color`,
## the boss's corp hue, over a faint glow). Peak alpha and duration come from the kind's
## entry held to T3 (<= 70%, <= 1.2 s); the ring stays inside the wheel's region. Through
## the one flash limiter. Reduce effects, headless or the entry off: nothing (the end
## state at once). Returns whether it plays.
func wheel_burst(wheel_center: Vector2, radius: float, kind: StringName, color: Color = Color(0, 0, 0, 0)) -> bool:
	var id: StringName = BURST_MOTION.get(kind, &"")
	if id == &"" or radius <= 0.0 or not Motion.live(id):
		return false
	if not Fx.request_flash():
		return false
	var tier := VfxTier.of(id)
	var col := color
	if col.a <= 0.0:
		col = Palette.CELL_PINK if kind == BURST_PERFECT else Palette.NET_CYAN
	var e := Motion.entry(id)
	_add({"kind": "wheel_burst", "burst": kind, "at": wheel_center, "r": radius, "color": col,
		"alpha": VfxTier.clamp_alpha(tier, Motion.amplitude(id)), "dur": VfxTier.clamp_seconds(tier, Motion.seconds(id)),
		"reach": VfxTier.clamp_radius(tier, radius * (1.0 + BURST_RING_GROW), radius, radius * WHEEL_REGION),
		"ease": e.ease, "trans": e.trans})
	return true


## The farthest a wheel burst at `radius` reaches (px from its centre), for layout checks.
static func wheel_burst_reach(radius: float) -> float:
	return VfxTier.clamp_radius(VfxTier.T3, radius * (1.0 + BURST_RING_GROW), radius, radius * WHEEL_REGION)


func _draw_wheel_burst(s: Dictionary) -> void:
	var q := _ease(s)
	var fade := 1.0 - q
	var c := _local(s["at"])
	var r := float(s["r"])
	var a := float(s["alpha"]) * fade
	var col: Color = s["color"]
	var ring_r := lerpf(r, float(s["reach"]), q)
	if String(s["burst"]) == String(BURST_PHASE):
		_draw_glow(c, r, Color(col, a * 0.5))
		var step := TAU / PHASE_DASHES
		var turn := PHASE_TURN * q
		var w := lerpf(BURST_RING_W0, BURST_RING_W1, q) * 0.7
		for k in PHASE_DASHES:
			# Long and short dashes alternate: a pattern, not only a colour.
			var fill := PHASE_DASH_FILL * (1.0 if k % 2 == 0 else 0.45)
			var a0 := turn + k * step
			draw_arc(c, ring_r, a0, a0 + step * fill, 6, Color(col, a), w, true)
		draw_arc(c, r * BURST_GLOW_EDGE, 0.0, TAU, BURST_SEGMENTS, Color(col, a * 0.6), 2.0, true)
		return
	_draw_glow(c, r, Color(col, a))
	draw_arc(c, ring_r, 0.0, TAU, BURST_SEGMENTS, Color(col, a), lerpf(BURST_RING_W0, BURST_RING_W1, q), true)
	# A thin paper ring lags the pink one: the latch's click, readable without colour.
	draw_arc(c, lerpf(r, ring_r, 0.6), 0.0, TAU, BURST_SEGMENTS, Color(Palette.PAPER, a * 0.8), BURST_RING_W1, true)


# --- Per-slice hit shapes (art pass W6, ART_BIBLE 8) --------------------------------------------

## Each slice type has its own hit shape, so an outcome reads without colour: crit =
## shattered glass, attack = a slash streak, shield / defend = hex plates, evade = an
## afterimage smear, afflict = a glitch crawl, heal = rising plus signs, miss = static.
const HIT_CRIT := &"crit"
const HIT_ATTACK := &"attack"
const HIT_SHIELD := &"shield"
const HIT_EVADE := &"evade"
const HIT_AFFLICT := &"afflict"
const HIT_HEAL := &"heal"
const HIT_MISS := &"miss"
const HIT_KINDS: Array[StringName] = [&"crit", &"attack", &"shield", &"evade", &"afflict", &"heal", &"miss"]
## Each shape's motion entry (duration, reach in px, tier: T3 for a crit, T2 the rest).
const HIT_MOTION := {&"crit": &"hit_vfx_crit", &"attack": &"hit_vfx_attack", &"shield": &"hit_vfx_shield", &"evade": &"hit_vfx_evade",
	&"afflict": &"hit_vfx_afflict", &"heal": &"hit_vfx_heal", &"miss": &"hit_vfx_miss"}
## Slice type -> its hit shape. DEPLOY launches a drone whose own hits are attacks.
const HIT_BY_SLICE := {RC.SliceType.ATTACK: &"attack", RC.SliceType.CRIT: &"crit", RC.SliceType.DEFEND: &"shield",
	RC.SliceType.SHIELD: &"shield", RC.SliceType.EVADE: &"evade", RC.SliceType.HEAL: &"heal", RC.SliceType.AFFLICT: &"afflict",
	RC.SliceType.MISS: &"miss", RC.SliceType.DEPLOY: &"attack"}
## Hit shape -> the slice type whose colour it wears by default (ART_BIBLE 3.4).
const HIT_COLOR_SLICE := {&"crit": RC.SliceType.CRIT, &"attack": RC.SliceType.ATTACK, &"shield": RC.SliceType.DEFEND,
	&"evade": RC.SliceType.EVADE, &"afflict": RC.SliceType.AFFLICT, &"heal": RC.SliceType.HEAL, &"miss": RC.SliceType.MISS}
## Shape drawing (shares of the reach unless named px): glass shards and cracks; the slash's
## angle (rad), width and its speed lines; hex plates' size and stagger; evade ghosts and
## their spacing; glitch rows, bar height and jump rate (steps a second); plus signs, their
## size and stagger; static cells (px) and the share lit; outline widths (px).
const SHARDS := 9
const CRACKS := 7
const SLASH_ANGLE := -0.6
const SLASH_WIDTH := 0.28
const SLASH_LINES := 2
const HEX_SIZE := 0.38
const HEX_STAGGER := 0.07
const EVADE_GHOSTS := 4
const EVADE_RING := 0.42
const GLITCH_ROWS := 6
const GLITCH_BAR := 0.13
const GLITCH_RATE := 20.0
const PLUSES := 4
const PLUS_SIZE := 0.3
const PLUS_STAGGER := 0.12
const STATIC_CELL := 4.0
const STATIC_LIT := 0.5
const HIT_LINE_W := 2.5
const HIT_FILL_ALPHA := 0.35


## The hit shape of a `slice_type` (RC.SliceType); a crit landing (`crit`) is a crit.
static func hit_kind(slice_type: int, crit: bool = false) -> StringName:
	if crit:
		return HIT_CRIT
	return HIT_BY_SLICE.get(slice_type, HIT_ATTACK)


## Plays hit shape `kind` (HIT_KINDS) at `at` (global) after `delay` s, in `color` (default:
## its slice colour), `size` x its entry's reach. Its duration comes from the entry held to
## the entry's tier (T2; T3 for a crit). Reduce effects, headless or the entry off: nothing
## (the end state at once). Returns whether it plays.
func hit_vfx(at: Vector2, kind: StringName, color: Color = Color(0, 0, 0, 0), delay: float = 0.0, size: float = 1.0) -> bool:
	var id: StringName = HIT_MOTION.get(kind, &"")
	if id == &"" or not Motion.live(id):
		return false
	var tier := VfxTier.of(id)
	var e := Motion.entry(id)
	var col := color if color.a > 0.0 else Palette.slice_color(int(HIT_COLOR_SLICE[kind]))
	_add({"kind": "hitfx", "hit": kind, "at": at, "color": col, "delay": delay, "dur": VfxTier.clamp_seconds(tier, Motion.seconds(id)),
		"reach": Motion.amplitude(id) * maxf(size, 0.0), "fill": VfxTier.clamp_alpha(tier, HIT_FILL_ALPHA), "ease": e.ease, "trans": e.trans})
	return true


## Plays the hit shape of a `slice_type` landing (see hit_kind) at `at` (global).
func slice_hit(at: Vector2, slice_type: int, crit: bool = false, delay: float = 0.0) -> bool:
	return hit_vfx(at, hit_kind(slice_type, crit), Color(0, 0, 0, 0), delay)


## The hit shapes playing now (tests): their kinds.
func hit_kinds_playing() -> Array[StringName]:
	var out: Array[StringName] = []
	for s in sprites:
		if String(s["kind"]) == "hitfx":
			out.append(StringName(s["hit"]))
	return out


## The guard's slice type in an impact (its icon, or the guard glyph among an equation's
## items), -1 when none.
static func _guard_icon(icon: int, items: Array) -> int:
	var guards := [RC.SliceType.DEFEND, RC.SliceType.SHIELD, RC.SliceType.EVADE]
	if icon in guards:
		return icon
	for it in items:
		if int(it.get("icon", -1)) in guards:
			return int(it["icon"])
	return -1


func _draw_hitfx(s: Dictionary) -> void:
	var p := _p(s)
	var q := _ease(s)
	var c := _local(s["at"])
	var reach := float(s["reach"])
	var col: Color = s["color"]
	var fade := 1.0 - p
	var serial := int(s["serial"])
	match StringName(s["hit"]):
		HIT_CRIT:
			# Cracks run out first, then glass shards fly and turn.
			var crack := clampf(q * 2.5, 0.0, 1.0)
			for k in CRACKS:
				var a := TAU * (k + _h(serial, k)) / CRACKS
				var d := Vector2(cos(a), sin(a))
				var bend := d.orthogonal() * reach * 0.12 * (_h(k, serial, 2) - 0.5)
				var mid := c + d * reach * 0.45 * crack + bend
				draw_polyline(PackedVector2Array([c, mid, c + d * reach * 0.8 * crack]), Color(Palette.PAPER, fade), HIT_LINE_W, true)
			for k in SHARDS:
				var a := TAU * (k + 0.5 + _h(k, serial, 3)) / SHARDS
				var d := Vector2(cos(a), sin(a))
				var at := c + d * reach * (0.3 + 0.7 * q)
				var sz := reach * (0.14 + 0.1 * _h(k, serial, 4))
				var turn := (_h(serial, k, 5) - 0.5) * PI * q
				var tri := PackedVector2Array([at + d.rotated(turn) * sz, at + d.orthogonal().rotated(turn) * sz * 0.55, at - d.orthogonal().rotated(turn) * sz * 0.55])
				draw_colored_polygon(tri, Color(Palette.PAPER, float(s["fill"]) * 2.0 * fade))
				draw_polyline(PackedVector2Array([tri[0], tri[1], tri[2], tri[0]]), Color(col, fade), HIT_LINE_W * 0.6, true)
		HIT_ATTACK:
			# A tapered slash sweeps across, two thin speed lines beside it.
			var d := Vector2.from_angle(SLASH_ANGLE)
			var n := d.orthogonal()
			var from := c - d * reach * 0.5
			var head := from + d * reach * clampf(q * 1.4, 0.0, 1.0)
			var tail := from + d * reach * clampf((q - 0.3) * 1.4, 0.0, 1.0)
			var mid := (head + tail) * 0.5
			var w := reach * SLASH_WIDTH * fade
			draw_colored_polygon(PackedVector2Array([tail, mid + n * w, head, mid - n * w]), Color(col, fade))
			draw_polyline(PackedVector2Array([tail, mid + n * w, head, mid - n * w, tail]), Color(Palette.PAPER, fade), 1.5, true)
			for k in SLASH_LINES:
				var off := n * w * (1.8 + k * 0.9) * (1.0 if k % 2 == 0 else -1.0)
				draw_line(tail.lerp(head, 0.2) + off, tail.lerp(head, 0.8) + off, Color(Palette.PAPER, fade * 0.8), 1.5, true)
		HIT_SHIELD:
			# Seven hex plates snap together (centre, then its six neighbours).
			var hr := reach * HEX_SIZE
			var spots := [Vector2.ZERO]
			for k in 6:
				spots.append(Vector2.from_angle(PI / 6.0 + k * PI / 3.0) * hr * sqrt(3.0))
			for k in spots.size():
				var pop := clampf((p - k * HEX_STAGGER) / 0.35, 0.0, 1.0)
				if pop <= 0.0:
					continue
				var sc := Tween.interpolate_value(0.6, 0.4, pop, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT) as float
				var hex := PackedVector2Array()
				for v in 6:
					hex.append(c + spots[k] * sc + Vector2.from_angle(v * PI / 3.0) * hr * sc * 0.92)
				draw_colored_polygon(hex, Color(col, float(s["fill"]) * fade))
				hex.append(hex[0])
				draw_polyline(hex, Color(col, fade), HIT_LINE_W, true)
		HIT_EVADE:
			# Ghost rings trail aside, fainter each, with speed lines behind.
			var r := reach * EVADE_RING
			for k in EVADE_GHOSTS:
				var at := c + Vector2(reach * q * (1.0 - float(k) / EVADE_GHOSTS), 0.0)
				var a := fade * (1.0 - float(k) / EVADE_GHOSTS)
				draw_arc(at, r, 0.0, TAU, 24, Color(col, a), HIT_LINE_W if k == 0 else 1.5, true)
			for k in 3:
				var y := (k - 1) * r * 0.6
				draw_line(c + Vector2(-reach * 0.6, y), c + Vector2(-reach * 0.6 + reach * 0.5 * q, y), Color(Palette.PAPER, fade * 0.7), 1.5, true)
		HIT_AFFLICT:
			# Broken bars crawl down, jumping sideways GLITCH_RATE times a second.
			var step := floori(float(s["age"]) * GLITCH_RATE)
			var bar := reach * GLITCH_BAR
			for row in GLITCH_ROWS:
				if float(row) / GLITCH_ROWS > q * 1.3:
					break
				var y := c.y - reach * 0.5 + row * bar * 1.6
				var w := reach * (0.4 + 0.8 * _h(row, serial, 6))
				var x := c.x - w * 0.5 + (_h(row, step, serial) - 0.5) * reach * 0.5
				draw_rect(Rect2(x + 2.0, y, w, bar), Color(Palette.NET_CYAN, fade * 0.5))
				draw_rect(Rect2(x, y, w, bar), Color(col, fade))
		HIT_HEAL:
			# Plus signs rise one after another.
			for k in PLUSES:
				var t := clampf((p - k * PLUS_STAGGER) / (1.0 - PLUS_STAGGER * (PLUSES - 1)), 0.0, 1.0)
				if t <= 0.0 or t >= 1.0:
					continue
				var at := c + Vector2((float(k) / (PLUSES - 1) - 0.5) * reach * 1.2, -reach * t)
				var arm := reach * PLUS_SIZE * (0.7 + 0.3 * _h(k, serial, 7))
				var a := 1.0 - t
				for d in [Vector2.RIGHT, Vector2.DOWN]:
					draw_line(at - d * arm, at + d * arm, Color(Palette.NIGHT_SKY, a * 0.8), arm * 0.55 + 2.0)
					draw_line(at - d * arm, at + d * arm, Color(col, a), arm * 0.55)
		HIT_MISS:
			# A disc of static in a dashed ring (the MISS slice's dashes).
			var step := floori(float(s["age"]) * GLITCH_RATE)
			var cells := ceili(reach * 2.0 / STATIC_CELL)
			for i in cells:
				for j in cells:
					var o := Vector2(i + 0.5, j + 0.5) * STATIC_CELL - Vector2(reach, reach)
					if o.length() > reach or _h(i * 131 + j, step, serial) > STATIC_LIT:
						continue
					var lit := Palette.PAPER if _h(j, i, step) > 0.5 else col
					draw_rect(Rect2(c + o - Vector2.ONE * STATIC_CELL * 0.5, Vector2.ONE * STATIC_CELL), Color(lit, fade * 0.85))
			for k in 12:
				var a0 := TAU * k / 12.0
				draw_arc(c, reach, a0, a0 + TAU / 24.0, 4, Color(col, fade), HIT_LINE_W, true)


## A radial glow: `col` at the centre fading to nothing at `r`.
func _draw_glow(c: Vector2, r: float, col: Color) -> void:
	var edge := Color(col, 0.0)
	var cols := PackedColorArray([col, edge, edge])
	for k in BURST_SEGMENTS:
		var a0 := TAU * k / BURST_SEGMENTS
		var a1 := TAU * (k + 1) / BURST_SEGMENTS
		draw_polygon(PackedVector2Array([c, c + Vector2(cos(a0), sin(a0)) * r * BURST_GLOW_EDGE, c + Vector2(cos(a1), sin(a1)) * r * BURST_GLOW_EDGE]), cols)


## ANIM-R1: a word stamped at `at` (global) in a tilted box (BLOCKED, EVADED, NO DAMAGE,
## PHASE 2...): lands from `result_stamp`'s amplitude scale, holds `hold` seconds, fades.
## Its lettering fits `max_w` px (the hub it sits in). Returns the box it covers (global).
## ANIM-R3 A6a: with `icon` (GUARD_NULL) the word carries its drawn mark before it: a shield
## over the empty-set sign (NO DAMAGE, ALL BLOCKED).
func word_stamp(at: Vector2, text: String, color: Color, hold: float, max_w: float, max_fs: int = -1, delay: float = 0.0, icon: String = "") -> Rect2:
	var fs := word_stamp_font(text, max_w, max_fs, icon)
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * WORD_BOX_PAD * 2.0 + stamp_icon_width(fs, icon)
	var box := Rect2(at - Vector2(w * 0.5, fs * WORD_BOX_H * 0.5), Vector2(w, fs * WORD_BOX_H))
	if not Motion.live(&"result_stamp"):
		return box
	_add({"kind": "tag", "at": at, "text": text, "color": color, "fs": fs, "dur": Motion.seconds(&"result_stamp") + hold,
		"land": Motion.seconds(&"result_stamp"), "from": Motion.amplitude(&"result_stamp"), "delay": delay, "icon": icon})
	return box


## The stamp's font size: WORD_STAMP_FONT at the text scale (at most `max_fs`), smaller
## until it (with its mark, when `icon`) fits `max_w`.
static func word_stamp_font(text: String, max_w: float, max_fs: int = -1, icon: String = "") -> int:
	var fs := roundi(WORD_STAMP_FONT * Settings.text_scale)
	if max_fs > 0:
		fs = maxi(WORD_STAMP_MIN, mini(fs, max_fs))
	while fs > WORD_STAMP_MIN and Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * WORD_BOX_PAD * 2.0 + stamp_icon_width(fs, icon) > max_w:
		fs -= 1
	return fs


## The mark before a stamp's word: a shield over the empty-set sign (ANIM-R3 A6a).
const GUARD_NULL := "guard_null"


## The room a stamp's mark takes (0 without one).
static func stamp_icon_width(fs: int, icon: String) -> float:
	return fs * (GLYPH_SHARE + GLYPH_GAP) if icon != "" else 0.0


## The shield-over-empty-set mark centred at `c`, `r` px in radius, in `col`: a shield
## outline with a ring and slash inside (nothing got through).
static func draw_guard_null(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	SliceIcon.draw_icon(ci, c, r, RC.SliceType.DEFEND, col)
	var ring := r * 0.42
	ci.draw_arc(c + Vector2(0, r * 0.05), ring, 0.0, TAU, 16, Palette.NIGHT_SKY, maxf(2.0, r * 0.22), true)
	ci.draw_arc(c + Vector2(0, r * 0.05), ring, 0.0, TAU, 16, Palette.PAPER, maxf(1.2, r * 0.12), true)
	var d := Vector2(ring, -ring) * 0.8
	ci.draw_line(c + Vector2(0, r * 0.05) - d, c + Vector2(0, r * 0.05) + d, Palette.PAPER, maxf(1.2, r * 0.12), true)


## Word stamps (ANIM-R1): lettering at text scale 1.0 and its floor (px), the box's side
## padding and height (shares of the font size) and its tilt (rad).
const WORD_STAMP_FONT := 20
const WORD_STAMP_MIN := 9
const WORD_BOX_PAD := 0.3
const WORD_BOX_H := 1.4
const WORD_TILT := -0.2
## A projectile's head: its radius as a share of the line's width (ANIM-R4 C6d: bigger, and
## ringed in paper, so the operative's acid shot reads over its own acid wheel).
const PROJECTILE_HEAD := 1.8
const PROJECTILE_RING := 2.0
## ANIM-R3 A6g: the crack line's alpha and width (px; drawing, not motion). ANIM-R4 C5: the
## share of the break the pieces hold in place while it cracks is `break_crack`'s
## amplitude (the motion table).
const CRACK_ALPHA := 0.95
const CRACK_WIDTH := 3.0


## A status glyph stamped at `at` (global): lands from `status_stamp`'s amplitude scale,
## holds `hold` seconds (the wheel then shows the status itself) and fades.
func stamp(at: Vector2, glyph: String, color: Color, hold: float, delay: float = 0.0) -> void:
	if not Motion.live(&"status_stamp"):
		return
	_add({"kind": "stamp", "at": at, "glyph": glyph, "color": color, "dur": Motion.seconds(&"status_stamp") + hold,
		"land": Motion.seconds(&"status_stamp"), "from": Motion.amplitude(&"status_stamp"), "delay": delay})
	# Art pass W6 (ART_BIBLE 8): an afflict lands as a glitch crawl on its slice.
	hit_vfx(at, HIT_AFFLICT, Color(0, 0, 0, 0), delay)


## A broken wheel: `pieces` ([polygon (global), colour]) fall `enemy_break`'s amplitude px
## with a spin each, fading out.
func shards(pieces: Array) -> void:
	if not Motion.live(&"enemy_break") or pieces.is_empty():
		return
	_add({"kind": "shards", "pieces": pieces, "dur": Motion.seconds(&"enemy_break"), "fall": Motion.amplitude(&"enemy_break"),
		"ease": Motion.entry(&"enemy_break").ease, "trans": Motion.entry(&"enemy_break").trans})


## Hub glass shattering at `at` (global) out of a hub `radius` px across.
func glass(at: Vector2, radius: float, color: Color) -> void:
	if not Motion.live(&"hub_shatter"):
		return
	_add({"kind": "glass", "at": at, "r": radius, "color": color, "dur": Motion.seconds(&"hub_shatter"), "fly": Motion.amplitude(&"hub_shatter"),
		"ease": Motion.entry(&"hub_shatter").ease, "trans": Motion.entry(&"hub_shatter").trans})


## VHS rewind lines over `area` (global) for `rewind_scrub`'s duration (jitter px).
func vhs(area: Rect2) -> void:
	if not Motion.live(&"rewind_scrub"):
		return
	_add({"kind": "vhs", "rect": area, "dur": Motion.seconds(&"rewind_scrub"), "jitter": Motion.amplitude(&"rewind_scrub")})


## The VICTORY / DEFEAT stamp at `at` (global). ANIM-R4 C6g: `font_size` > 0 sets its
## lettering (VICTORY fitted to the room above the beaten wheel, `word_fit`).
func word(at: Vector2, text: String, color: Color, hold: float, font_size: int = -1) -> void:
	if not Motion.live(&"victory_stamp"):
		return
	_add({"kind": "word", "at": at, "text": text, "color": color, "delay": Motion.delay_of(&"victory_stamp"),
		"dur": Motion.seconds(&"victory_stamp") + hold, "land": Motion.seconds(&"victory_stamp"), "from": Motion.amplitude(&"victory_stamp"),
		"fs": font_size if font_size > 0 else roundi(WORD_FONT * Settings.text_scale)})


## ANIM-R4 C6g: the biggest VICTORY / DEFEAT lettering (px, at most WORD_FONT at the text
## scale, at least WORD_STAMP_MIN) whose box fits `room`.
static func word_fit(text: String, room: Vector2) -> int:
	var fs := roundi(WORD_FONT * Settings.text_scale)
	while fs > WORD_STAMP_MIN and (Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room.x or fs * WORD_BOX_H > room.y):
		fs -= 1
	return fs


## The box a VICTORY / DEFEAT word of `fs` px covers at rest, centred at `at` (global).
static func word_rect(at: Vector2, text: String, fs: int) -> Rect2:
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	return Rect2(at - Vector2(w * 0.5, fs * 0.65), Vector2(w, fs * 0.9))


## A deck or discard pile mark at `at` (global) for `seconds` (fading in and out).
func pile(at: Vector2, seconds: float) -> void:
	if not Motion.live(&"card_pile"):
		return
	_add({"kind": "pile", "at": at, "dur": seconds + Motion.seconds(&"card_pile") * 2.0, "fade": Motion.seconds(&"card_pile"),
		"alpha": Motion.amplitude(&"card_pile")})


## Embers rising off a burnt card at `rect` (global).
func embers(rect: Rect2) -> void:
	if not Motion.live(&"card_exhaust"):
		return
	_add({"kind": "embers", "rect": rect, "dur": Motion.seconds(&"card_exhaust")})


## Shows the aim reticle at `at` (global): it glides there from where it was with
## `target_snap` (a pop of amplitude px on arrival); `instant` puts it there at once.
func aim_reticle(at: Vector2, instant: bool = false) -> void:
	if _reticle_tween != null and _reticle_tween.is_valid():
		_reticle_tween.kill()
	var was_visible := reticle_visible
	reticle_visible = true
	if instant or not was_visible or not Motion.live(&"target_snap"):
		reticle_pos = at
		reticle_pop = 0.0
		queue_redraw()
		return
	var e := Motion.entry(&"target_snap")
	var from := reticle_pos
	_reticle_tween = create_tween()
	_reticle_tween.tween_method(_reticle_step.bind(from, at), 0.0, 1.0, Motion.seconds(&"target_snap")).set_ease(e.ease).set_trans(e.trans)


func _reticle_step(p: float, from: Vector2, at: Vector2) -> void:
	reticle_pos = from.lerp(at, p)
	reticle_pop = 1.0 - p
	queue_redraw()


func hide_reticle() -> void:
	if _reticle_tween != null and _reticle_tween.is_valid():
		_reticle_tween.kill()
	reticle_visible = false
	queue_redraw()


# --- Card flights -------------------------------------------------------------------------

## Flies `card` (a copy the layer now owns) from `from` (global rect, the hand slot or
## where the drag let go) to `to` (global, the zone's centre): `card_play` travel, a
## `card_stamp` landing, then it dissolves (`effect_burst`) or, when `exhaust`, burns
## (`card_exhaust`: curls up with embers). Returns the seconds until the effect may play
## (travel + stamp + its dissolve: ANIM-R3 A6i). `on_done` runs when it lands or is skipped.
func play_card(card: ZineCard, from: Rect2, from_rotation: float, to: Vector2, exhaust: bool, on_done: Callable = Callable()) -> float:
	if not Motion.live(&"card_play"):
		card.free()
		if on_done.is_valid():
			on_done.call()
		return 0.0
	_adopt(card, from, from_rotation)
	var fly := Motion.seconds(&"card_play")
	var land := Motion.seconds(&"card_stamp")
	var gone := Motion.seconds(&"card_exhaust") if exhaust else Motion.seconds(&"effect_burst")
	var fe := Motion.entry(&"card_play")
	var se := Motion.entry(&"card_stamp")
	var end_pos := to - card.size * 0.5
	var tw := card.create_tween()
	tw.tween_property(card, "position", end_pos, fly).set_ease(fe.ease).set_trans(fe.trans)
	tw.parallel().tween_property(card, "rotation", 0.0, fly).set_ease(fe.ease).set_trans(fe.trans)
	tw.parallel().tween_property(card, "scale", Vector2.ONE * Motion.amplitude(&"card_play"), fly * 0.5).set_ease(Tween.EASE_OUT)
	# The stamp: from a size up, down onto the target.
	tw.tween_property(card, "scale", Vector2.ONE * (1.0 / maxf(0.01, Motion.amplitude(&"card_stamp"))), land).set_ease(se.ease).set_trans(se.trans)
	var f := {"node": card, "tween": tw, "to": to, "kind": "exhaust" if exhaust else "play", "on_done": on_done}
	if exhaust:
		tw.tween_callback(func() -> void: embers(Rect2(card.global_position, card.size)))
		tw.tween_property(card, "scale:y", 0.0, gone).set_ease(Motion.entry(&"card_exhaust").ease).set_trans(Motion.entry(&"card_exhaust").trans)
		tw.parallel().tween_property(card, "modulate", Color(Palette.CELL_PINK.darkened(0.6), 0.0), gone)
	else:
		tw.tween_callback(func() -> void: burst(to, Palette.CELL_ACID, &"effect_burst"))
		tw.tween_property(card, "modulate:a", 0.0, gone).set_ease(Tween.EASE_OUT)
		tw.parallel().tween_property(card, "scale", Vector2.ZERO, gone).set_ease(Tween.EASE_IN)
	tw.tween_callback(func() -> void: _end_flight(f))
	flights.append(f)
	set_process(true)
	# ANIM-R3 A6i: the card is gone (dissolved or burnt) before its effect plays, so it never
	# covers the wheel while that spins.
	return fly + land + gone


## Flies `card` (a copy) from `from` to the discard pile at `to` (global) along an arc of
## `card_discard`'s amplitude px, after `delay` seconds.
func discard_card(card: ZineCard, from: Rect2, from_rotation: float, to: Vector2, delay: float) -> void:
	if not Motion.live(&"card_discard"):
		card.free()
		return
	_adopt(card, from, from_rotation)
	var e := Motion.entry(&"card_discard")
	var start := card.position
	var end_pos := to - card.size * 0.5
	var lift := Motion.amplitude(&"card_discard")
	var tw := card.create_tween()
	tw.tween_interval(delay)
	tw.tween_method(_discard_step.bind(card, start, end_pos, lift, e.trans, e.ease), 0.0, 1.0, Motion.seconds(&"card_discard"))
	var f := {"node": card, "tween": tw, "to": to, "kind": "discard", "on_done": Callable()}
	tw.tween_callback(func() -> void: _end_flight(f))
	flights.append(f)
	set_process(true)


## One step of a discard flight: along an arc, shrinking to DISCARD_SCALE and fading.
static func _discard_step(p: float, card: ZineCard, start: Vector2, end_pos: Vector2, lift: float, trans: int, ease: int) -> void:
	if not is_instance_valid(card):
		return
	var q: float = Tween.interpolate_value(0.0, 1.0, p, 1.0, trans, ease)
	card.position = start.lerp(end_pos, q) + Vector2(0, -lift * sin(PI * q))
	card.scale = Vector2.ONE * lerpf(1.0, DISCARD_SCALE, q)
	card.modulate.a = 1.0 - q * DISCARD_FADE


## A cancelled drag: `card` (a copy) glides from `from` (global, where it was let go) back
## to its hand slot `slot` (global rect), then `on_done` runs (the hand card shows again).
func return_card(card: ZineCard, from: Vector2, slot: Rect2, slot_rotation: float, on_done: Callable) -> void:
	if not Motion.live(&"drag_cancel_return"):
		card.free()
		on_done.call()
		return
	_adopt(card, Rect2(from - card.size * 0.5, card.size), 0.0)
	var e := Motion.entry(&"drag_cancel_return")
	var tw := card.create_tween()
	tw.tween_property(card, "position", _local(slot.position), Motion.seconds(&"drag_cancel_return")).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_property(card, "rotation", slot_rotation, Motion.seconds(&"drag_cancel_return")).set_ease(e.ease).set_trans(e.trans)
	var f := {"node": card, "tween": tw, "to": slot.get_center(), "kind": "return", "on_done": on_done}
	tw.tween_callback(func() -> void: _end_flight(f))
	flights.append(f)
	set_process(true)


## The last flight of `kind` ("play", "exhaust", "discard", "return"), or {}.
func last_flight(kind: String) -> Dictionary:
	for i in range(flights.size() - 1, -1, -1):
		if String(flights[i]["kind"]) == kind:
			return flights[i]
	return {}


func _adopt(card: ZineCard, from: Rect2, from_rotation: float) -> void:
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.focus_mode = Control.FOCUS_NONE
	card.drag_index = -1
	add_child(card)
	card.size = from.size
	card.pivot_offset = card.size * 0.5
	card.position = _local(from.position)
	card.rotation = from_rotation


func _end_flight(f: Dictionary) -> void:
	if not flights.has(f):
		return
	flights.erase(f)
	var tw: Tween = f["tween"]
	if tw != null and tw.is_valid():
		tw.kill()
	var node: Node = f["node"]
	if is_instance_valid(node):
		node.queue_free()
	var done: Callable = f.get("on_done", Callable())
	if done.is_valid():
		done.call()
	if sprites.is_empty() and flights.is_empty():
		set_process(false)


# --- Drawing ------------------------------------------------------------------------------

func _draw() -> void:
	for s in sprites:
		if float(s["age"]) < float(s.get("delay", 0.0)):
			continue
		match String(s["kind"]):
			"number":
				_draw_number(s)
			"travel":
				_draw_travel(s)
			"tag":
				_draw_tag(s)
			"impact":
				_draw_impact(s)
			"burst":
				_draw_burst(s)
			"ring":
				var p := _p(s)
				draw_arc(_local(s["at"]), float(s["r0"]) + float(s["grow"]) * p, 0, TAU, 40, Color(s["color"], 1.0 - p), 3.0, true)
			"line":
				_draw_line(s)
			"disc":
				var q := _p(s)
				draw_circle(_local(s["at"]), float(s["r"]), Color(s["color"], float(s["alpha"]) * (1.0 - q)))
			"stamp":
				_draw_stamp(s)
			"shards":
				_draw_shards(s)
			"glass":
				_draw_glass(s)
			"vhs":
				_draw_vhs(s)
			"word":
				_draw_word(s)
			"pile":
				_draw_pile(s)
			"embers":
				_draw_embers(s)
			"wheel_burst":
				_draw_wheel_burst(s)
			"hitfx":
				_draw_hitfx(s)
	if reticle_visible:
		var c := _local(reticle_pos)
		var r := RETICLE_RADIUS + Motion.amplitude(&"target_snap") * reticle_pop
		for k in 4:
			var a := PI * 0.25 + k * PI * 0.5
			draw_arc(c, r, a - RETICLE_ARC, a + RETICLE_ARC, 6, Palette.CELL_ACID, 2.5, true)


func _draw_number(s: Dictionary) -> void:
	var p := _p(s)
	var fs := int(s["fs"])
	var grow := clampf(p / GROW_SHARE, 0.0, 1.0)
	var size := fs
	if bool(s["crit"]):
		# The crit overshoots its size and settles (a pop).
		size = roundi(fs * lerpf(CRIT_POP_SCALE, 1.0, grow)) if p < GROW_SHARE else fs
	else:
		size = roundi(fs * lerpf(GROW_FROM, 1.0, grow))
	var at := _local(s["at"]) + (s["dir"] as Vector2) * float(s["rise"]) * _ease(s)
	var alpha := 1.0 - clampf((p - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0)
	var text := String(s["text"])
	var f := Palette.display()
	var icon := int(s.get("icon", -1))
	var gw := glyph_width(size, icon)
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x + gw
	var base := at + Vector2(-w * 0.5 + gw, size * 0.35)
	if icon >= 0:
		# ANIM-R3 A6e: a guard is its glyph and its number (a shield and "5", not "5 BLOCKED").
		var gc := at + Vector2(-w * 0.5 + size * GLYPH_SHARE * 0.5, 0.0)
		draw_circle(gc, size * GLYPH_SHARE * 0.55, Color(Palette.NIGHT_SKY, 0.8 * alpha))
		SliceIcon.draw_icon(self, gc, size * GLYPH_SHARE * 0.45, icon, Color(s["color"], alpha))
	draw_string_outline(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, NUMBER_OUTLINE, Color(Palette.PAPER, alpha))
	draw_string(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(s["color"], alpha))


## ANIM-R3 A6a: a hit's outcome where it struck: its glyph and "0", popping in and fading.
func _draw_impact(s: Dictionary) -> void:
	var a := float(s["age"]) - float(s.get("delay", 0.0))
	var d := maxf(0.001, float(s["dur"]))
	var q := clampf(a / (d * GROW_SHARE), 0.0, 1.0)
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT))
	var alpha := 1.0 - clampf((_p(s) - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0)
	var fs := maxi(1, roundi(float(s["fs"]) * sc))
	var text := String(s["text"])
	var f := Palette.display()
	var gw := glyph_width(fs, int(s["icon"]))
	var items: Array = s.get("items", [])
	var w := equation_width(items, fs, f) if not items.is_empty() else f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + gw
	var c := _local(s["at"])
	var col := Color(s["color"], alpha)
	draw_rect(Rect2(c - Vector2(w * 0.5 + fs * 0.2, fs * 0.65), Vector2(w + fs * 0.4, fs * 1.3)), Color(Palette.NIGHT_SKY, 0.85 * alpha))
	draw_rect(Rect2(c - Vector2(w * 0.5 + fs * 0.2, fs * 0.65), Vector2(w + fs * 0.4, fs * 1.3)), col, false, 2.0)
	if not items.is_empty():
		# ANIM-R4 C6c: the hit meets its guard: sword 8 - shield 8 = 0.
		draw_equation(self, c - Vector2(w * 0.5, 0.0), items, fs, f, alpha, NUMBER_OUTLINE)
		return
	SliceIcon.draw_icon(self, c + Vector2(-w * 0.5 + fs * GLYPH_SHARE * 0.5, 0.0), fs * GLYPH_SHARE * 0.45, int(s["icon"]), col)
	var base := c + Vector2(-w * 0.5 + gw, fs * 0.35)
	draw_string_outline(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, NUMBER_OUTLINE, Color(Palette.NIGHT_SKY, alpha))
	draw_string(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)


func _draw_travel(s: Dictionary) -> void:
	var a := float(s["age"]) - float(s.get("delay", 0.0))
	var hold := float(s["hold"])
	var swap := float(s.get("swap", 0.0))
	var fs := int(s["fs"])
	var at := _local(s["at"])
	var size := float(fs)
	var alpha := 1.0
	var text := String(s["text"])
	if a < swap:
		# ANIM-R2: the hit's raw number first (its guard takes its part meanwhile).
		text = String(s["raw"])
		var grow := clampf(a / maxf(0.001, swap * GROW_SHARE), 0.0, 1.0)
		size = fs * (lerpf(CRIT_POP_SCALE, 1.0, grow) if bool(s["crit"]) else lerpf(GROW_FROM, 1.0, grow))
	elif a < hold:
		var grow := clampf((a - swap) / maxf(0.001, (hold - swap) * GROW_SHARE), 0.0, 1.0)
		size = fs * (lerpf(CRIT_POP_SCALE, 1.0, grow) if bool(s["crit"]) or swap > 0.0 else lerpf(GROW_FROM, 1.0, grow))
	else:
		var d := maxf(0.001, float(s["dur"]) - hold)
		var q: float = Tween.interpolate_value(0.0, 1.0, clampf((a - hold) / d, 0.0, 1.0), 1.0, int(s["trans"]), int(s["ease"]))
		at = at.lerp(_local(s["to"]), q)
		size = fs * lerpf(1.0, float(s["shrink"]), q)
		alpha = lerpf(1.0, TRAVEL_FADE_TO, q)
	var isz := maxi(1, roundi(size))
	var f := Palette.display()
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, isz).x
	var base := at + Vector2(-w * 0.5, isz * 0.35)
	draw_string_outline(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, isz, NUMBER_OUTLINE, Color(Palette.PAPER, alpha))
	draw_string(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, isz, Color(s["color"], alpha))


func _draw_tag(s: Dictionary) -> void:
	var land := float(s["land"])
	var a := float(s["age"]) - float(s.get("delay", 0.0))
	var q := clampf(a / land, 0.0, 1.0) if land > 0.0 else 1.0
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT))
	var alpha := minf(1.0, q * 2.0) * (1.0 - clampf((_p(s) - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0))
	var fs := int(s["fs"])
	var text := String(s["text"])
	var font := Palette.marker()
	var icon := String(s.get("icon", ""))
	var iw := stamp_icon_width(fs, icon)
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + iw
	var box := Rect2(-w * 0.5 - fs * WORD_BOX_PAD, -fs * WORD_BOX_H * 0.5, w + fs * WORD_BOX_PAD * 2.0, fs * WORD_BOX_H)
	var col: Color = s["color"]
	draw_set_transform(_local(s["at"]), WORD_TILT, Vector2.ONE * sc)
	draw_rect(box, Color(Palette.NIGHT_SKY, 0.88 * alpha))
	draw_rect(box, Color(col, alpha), false, 3.0)
	if icon == GUARD_NULL:
		draw_guard_null(self, Vector2(-w * 0.5 + fs * GLYPH_SHARE * 0.5, 0.0), fs * GLYPH_SHARE * 0.5, Color(col, alpha))
	draw_string(font, Vector2(-w * 0.5 + iw, fs * 0.35), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(col, alpha))
	draw_set_transform(Vector2.ZERO)


func _draw_burst(s: Dictionary) -> void:
	var p := _p(s)
	var c := _local(s["at"])
	var r := float(s["radius"]) * (0.5 + 0.5 * p)
	var col := Color(s["color"], 1.0 - p)
	for k in BURST_SPIKES:
		var a := TAU * k / BURST_SPIKES + int(s["serial"]) * 0.37
		var d := Vector2(cos(a), sin(a))
		draw_line(c + d * r * BURST_INNER, c + d * r, col, 2.5)


func _draw_line(s: Dictionary) -> void:
	var p := _p(s)
	var share := line_share()
	var from := _local(s["from"])
	var to := _local(s["to"])
	var flight := clampf(p / share, 0.0, 1.0)
	var fade := clampf((p - share) / (1.0 - share), 0.0, 1.0)
	var head := from.lerp(to, flight)
	var tail := from.lerp(to, fade)
	var col := Color(s["color"], 1.0 - fade)
	var width := float(s["width"])
	draw_line(tail, head, Color(Palette.NIGHT_SKY, col.a * 0.7), width + 4.0)
	draw_line(tail, head, col, width)
	var d := (to - from).normalized()
	var arrow := ARROW_HEAD + width
	var n := d.orthogonal() * arrow * 0.6
	# The arrowhead leads the projectile and stays at the victim as the line fades.
	draw_colored_polygon(PackedVector2Array([head + d * arrow * 0.5, head - d * arrow * 0.5 + n, head - d * arrow * 0.5 - n]), col)
	if p < share:
		# The projectile's head, bright, flying from the attacker's slice.
		var hr := width * PROJECTILE_HEAD
		draw_circle(head, hr + PROJECTILE_RING + 2.0, Color(Palette.NIGHT_SKY, 0.8))
		draw_arc(head, hr + PROJECTILE_RING * 0.5, 0.0, TAU, 20, Palette.PAPER, PROJECTILE_RING, true)
		draw_circle(head, hr, col.lightened(0.35))
		var label := String(s.get("label", ""))
		var from_label := String(s.get("from_label", ""))
		if label != "":
			# ANIM-R2: the hit's number rides with it. ANIM-R3 A6c: its aim shows: the slice's own
			# value first, shrinking into what the hit deals ("12" -> "6 ½" at half power);
			# bigger on a PERFECT landing.
			var fs := roundi(NUMBER_FONT * Settings.text_scale * RIDE_FONT_SHARE * float(s.get("scale", 1.0)))
			var shown := label
			var swap := clampf(flight / maxf(0.01, Motion.amplitude(&"ride_swap")), 0.0, 1.0)
			if from_label != "" and swap < 1.0:
				shown = from_label
				fs = maxi(1, roundi(fs * lerpf(1.0, Motion.amplitude(&"ride_shrink"), swap)))
			var f := Palette.display()
			var w := f.get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			var off := d.orthogonal() * fs * RIDE_OFFSET
			if off.y > 0.0:
				off = -off
			var base := head + off + Vector2(-w * 0.5, fs * 0.35)
			draw_string_outline(f, base, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, NUMBER_OUTLINE, Palette.NIGHT_SKY)
			draw_string(f, base, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col.lightened(0.2))


func _draw_stamp(s: Dictionary) -> void:
	var land := float(s["land"])
	var a := float(s["age"])
	var q := clampf(a / land, 0.0, 1.0) if land > 0.0 else 1.0
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT))
	var alpha := 1.0 - clampf((_p(s) - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0)
	var c := _local(s["at"])
	var fs := roundi(STAMP_FONT * Settings.text_scale * sc)
	draw_circle(c, STAMP_DISC * Settings.text_scale * sc, Color(Palette.NIGHT_SKY, 0.9 * alpha))
	draw_arc(c, STAMP_DISC * Settings.text_scale * sc, 0, TAU, 20, Color(s["color"], alpha), 2.0)
	var w := Palette.mono().get_string_size(String(s["glyph"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	draw_string(Palette.mono(), c + Vector2(-w * 0.5, fs * 0.35), String(s["glyph"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(s["color"], alpha))


func _draw_shards(s: Dictionary) -> void:
	# ANIM-R3 A6g: the real wheel cracks, then its pieces fall. For the first `break_crack` of
	# the break every piece holds its place (the wheel as it was, its slices' art and values)
	# while white cracks run along the slice borders; then each piece drops and turns,
	# keeping its art, and fades.
	var p := _p(s)
	var crack_share := clampf(Motion.amplitude(&"break_crack"), 0.01, 0.95)
	var crack := clampf(p / crack_share, 0.0, 1.0)
	var q := 0.0
	if p > crack_share:
		q = Tween.interpolate_value(0.0, 1.0, (p - crack_share) / (1.0 - crack_share), 1.0, int(s.get("trans", Tween.TRANS_LINEAR)), int(s.get("ease", Tween.EASE_OUT)))
	var fall := float(s["fall"])
	var origin := get_global_rect().position
	var pieces: Array = s["pieces"]
	for k in pieces.size():
		var poly: PackedVector2Array = pieces[k][0]
		if poly.is_empty():
			continue
		var centre := Vector2.ZERO
		for v in poly:
			centre += v
		centre /= poly.size()
		# Each piece drifts off along its own crack, falls and turns (hash scatter).
		var side := (_h(int(s["serial"]), k) - 0.5) * 2.0
		var spin := side * PI * 0.5 * q
		var shift := Vector2(side * fall * 0.3, fall * (0.4 + 0.6 * _h(k, int(s["serial"]), 1))) * q
		var xf := Transform2D(spin, centre + shift - origin) * Transform2D(0.0, -centre)
		var fade := 1.0 - q
		var col: Color = pieces[k][1]
		var art: Dictionary = pieces[k][2] if (pieces[k] as Array).size() > 2 else {}
		# Drawn in the piece's own frame (global points through its transform), so the art
		# turns and falls with it.
		draw_set_transform_matrix(xf)
		draw_colored_polygon(poly, Color(col, col.a * fade))
		var closed := poly.duplicate()
		closed.append(poly[0])
		var rim: Color = art.get("rim", Palette.PAPER)
		draw_polyline(closed, Color(rim, 0.95 * fade), 1.8, true)
		if art.has("type"):
			SliceIcon.draw_on_slice(self, art["icon_at"], float(art["icon_r"]), int(art["type"]), Color(art["slice_col"], fade))
		if String(art.get("value", "")) != "":
			var vfs := int(art["value_fs"])
			draw_string(Palette.display(), (art["value_at"] as Vector2) + Vector2(-vfs, vfs * 0.4), String(art["value"]), HORIZONTAL_ALIGNMENT_CENTER, vfs * 2, vfs,
				Color(rim, fade))
		# The crack: a white line along the piece's border, drawn on over the first frames.
		if crack > 0.0 and fade > 0.0:
			var n := maxi(2, roundi(closed.size() * crack))
			draw_polyline(closed.slice(0, n), Color(Palette.PAPER, CRACK_ALPHA * fade), CRACK_WIDTH, true)
		draw_set_transform(Vector2.ZERO)


func _draw_glass(s: Dictionary) -> void:
	var q := _ease(s)
	var c := _local(s["at"])
	var r := float(s["r"])
	for k in GLASS_SHARDS:
		var a := TAU * (k + _h(k, int(s["serial"]))) / GLASS_SHARDS
		var d := Vector2(cos(a), sin(a))
		var p := c + d * (r * 0.4 + float(s["fly"]) * q)
		var size := r * (0.18 + 0.12 * _h(k, 7, int(s["serial"])))
		var tri := PackedVector2Array([p + d * size, p + d.orthogonal() * size * 0.5, p - d.orthogonal() * size * 0.5])
		draw_colored_polygon(tri, Color(Palette.PAPER, 0.85 * (1.0 - q)))
		draw_polyline(PackedVector2Array([tri[0], tri[1], tri[2], tri[0]]), Color(s["color"], 1.0 - q), 1.0)
	# The crack star on the hub glass itself.
	for k in GLASS_SHARDS / 2:
		var a := TAU * k / (GLASS_SHARDS / 2.0) + 0.3
		draw_line(c, c + Vector2(cos(a), sin(a)) * r, Color(Palette.PAPER, 0.9 * (1.0 - q)), 1.5)


func _draw_vhs(s: Dictionary) -> void:
	var p := _p(s)
	var r: Rect2 = s["rect"]
	var o := _local(r.position)
	var frame := Engine.get_process_frames()
	for k in VHS_BANDS:
		var y := o.y + fmod((_h(k, frame >> 1) + p) * r.size.y, r.size.y)
		var x := (_h(frame, k, 3) - 0.5) * 2.0 * float(s["jitter"])
		draw_rect(Rect2(Vector2(o.x + x, y), Vector2(r.size.x, VHS_BAND_PX)), Color(Palette.PAPER, 0.22 * (1.0 - p)))
		draw_rect(Rect2(Vector2(o.x - x, y + VHS_BAND_PX), Vector2(r.size.x, 1.0)), Color(Palette.CELL_PINK, 0.25 * (1.0 - p)))
	# Tape-rewind marks: two left-pointing triangles in the corner.
	var m := o + Vector2(12, 12)
	for k in 2:
		var x0 := m.x + k * 12.0
		draw_colored_polygon(PackedVector2Array([Vector2(x0, m.y + 7), Vector2(x0 + 11, m.y), Vector2(x0 + 11, m.y + 14)]), Color(Palette.PAPER, 0.9 * (1.0 - p)))


func _draw_word(s: Dictionary) -> void:
	var a := float(s["age"]) - float(s.get("delay", 0.0))
	var land := float(s["land"])
	var q := clampf(a / land, 0.0, 1.0) if land > 0.0 else 1.0
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT))
	var alpha := minf(1.0, q * 2.0) * (1.0 - clampf((_p(s) - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0))
	var fs := roundi(float(s.get("fs", WORD_FONT * Settings.text_scale)) * sc)
	var text := String(s["text"])
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var base := _local(s["at"]) + Vector2(-w * 0.5, fs * 0.35)
	draw_string_outline(Palette.marker(), base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, NUMBER_OUTLINE + 2, Color(Palette.NIGHT_SKY, alpha))
	draw_string(Palette.marker(), base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(s["color"], alpha))


func _draw_pile(s: Dictionary) -> void:
	var a := float(s["age"])
	var fade := float(s["fade"])
	var alpha := float(s["alpha"]) * minf(1.0, a / maxf(0.001, fade)) * minf(1.0, (float(s["dur"]) - a) / maxf(0.001, fade))
	var size := PILE_SIZE * Settings.text_scale
	var c := _local(s["at"])
	for k in PILE_LAYERS:
		var r := Rect2(c - size * 0.5 + Vector2(k * 2.0, -k * 2.0), size)
		draw_rect(r, Color(Palette.INK, alpha))
		draw_rect(r, Color(Palette.PAPER, alpha), false, 1.5)
	draw_rect(Rect2(c - size * 0.5 + Vector2(size.x * 0.3, -6.0), Vector2(size.x * 0.4, 6.0)), Color(Palette.TAPE, alpha))


func _draw_embers(s: Dictionary) -> void:
	var p := _p(s)
	var r: Rect2 = s["rect"]
	var o := _local(r.position)
	for k in EMBERS:
		var x := o.x + r.size.x * _h(k, int(s["serial"]))
		var y := o.y + r.size.y * (1.0 - p * (0.6 + 0.8 * _h(k, 5, int(s["serial"]))))
		var col := Palette.CELL_ACID if k % 3 == 0 else Palette.CELL_PINK
		draw_circle(Vector2(x, y), 2.0 + 2.0 * (1.0 - p), Color(col, 1.0 - p))
