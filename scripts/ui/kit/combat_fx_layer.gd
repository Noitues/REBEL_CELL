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
## The slap shrinks the card from its flight size to 1 over this share of the slap.
const SLAP_SHRINK_SHARE := 0.5
## ANIM-R2 E10 (named, were inline): a number grows in from this share of its size; a crit
## pops from this scale and settles; a travelling number fades to this alpha on its way.
const GROW_FROM := 0.6
const CRIT_POP_SCALE := 1.35
const TRAVEL_FADE_TO := 0.6
## ANIM-R6 D2 (were inline): a drawn mark that grows in from a smaller size (an impact's
## glyph, a status mark, a block or heal number) settles with this overshooting shape.
const POP_SETTLE_TRANS := Tween.TRANS_BACK
const POP_SETTLE_EASE := Tween.EASE_OUT
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
## going (their `on_done` runs) and are freed. A held word stays, landed (ANIM-R6 A15).
func clear() -> void:
	sprites.clear()
	for f in flights.duplicate():
		_end_flight(f)
	flights.clear()
	if not held_word.is_empty():
		held_word["age"] = _word_landed_at(held_word)
	set_process(false)
	queue_redraw()


## ANIM-R6 A15: the word that stays (VICTORY once a fight is won): it lands like `word` (the
## `victory_stamp` pop) and then holds at full strength until `release_word` (the fight is
## left for its loot), never fading to a ghost. Not an effect that plays: `busy` ignores it.
var held_word: Dictionary = {}


## Lands `text` at `at` (global) and keeps it (see `held_word`); `instant` (a skip, reduce
## effects) shows it landed at once.
func hold_word(at: Vector2, text: String, color: Color, font_size: int = -1, instant: bool = false) -> void:
	var live := Motion.live(&"victory_stamp") and not instant
	held_word = {"kind": "word", "at": at, "text": text, "color": color, "delay": Motion.delay_of(&"victory_stamp") if live else 0.0,
		"dur": INF, "land": Motion.seconds(&"victory_stamp") if live else 0.0, "from": Motion.amplitude(&"victory_stamp") if live else 1.0,
		"fs": font_size if font_size > 0 else roundi(WORD_FONT * Settings.text_scale), "age": 0.0}
	if live:
		set_process(true)
	queue_redraw()


## The held word goes (the fight it said is over and left, or a new one starts).
func release_word() -> void:
	held_word = {}
	queue_redraw()


static func _word_landed_at(w: Dictionary) -> float:
	return float(w.get("delay", 0.0)) + float(w.get("land", 0.0))


func _process(delta: float) -> void:
	var landing := not held_word.is_empty() and float(held_word["age"]) < _word_landed_at(held_word)
	if landing:
		held_word["age"] = minf(float(held_word["age"]) + delta, _word_landed_at(held_word))
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
	if sprites.is_empty() and flights.is_empty() and (held_word.is_empty() or float(held_word["age"]) >= _word_landed_at(held_word)):
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
	if crit and Motion.live(&"number_crit"):
		burst(at, color, &"number_crit")
	return rect


## ANIM-R3 A6a: what a hit did, shown where it struck (`at`, global: the arrowhead on the
## victim's HP ring or its token): a glyph (`icon`, a slice type: DEFRAG for a hit soaked
## whole, DETOUR for one evaded) and `text` ("0"), popping from `impact_mark`'s amplitude
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
	if crit and Motion.live(&"number_crit"):
		burst(at, color, &"number_crit", delay)


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
## "6" at half power) over `ride_swap` of the flight; `scale` > 1 draws the riding
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
## whole screen. ART-0 E (ported from art-pass W6, ART_BIBLE v2 5.3): a local flash like any
## other: through the one flash limiter (Fx.request_flash), its alpha and duration held to
## `id`'s tier.
func disc_flash(at: Vector2, radius: float, color: Color, id: StringName) -> void:
	if not Motion.live(id) or not Fx.request_flash():
		return
	var tier := VfxTier.of(id)
	_add({"kind": "disc", "at": at, "r": radius, "color": color, "alpha": VfxTier.clamp_alpha(tier, Motion.amplitude(id)),
		"dur": VfxTier.clamp_seconds(tier, Motion.seconds(id))})


# --- Wheel-local T3 bursts (ART-0 E, ported from art-pass W6; ART_BIBLE v2 5.3) -------------

## The kinds of wheel_burst: a Perfect landing and a boss's phase change.
const BURST_PERFECT := &"perfect"
const BURST_PHASE := &"phase"
## Each kind's motion entry (T3: duration, peak alpha).
const BURST_MOTION := {&"perfect": &"wheel_burst_perfect", &"phase": &"wheel_burst_phase"}
## A burst's region is its wheel: the disc and its rim, HP arc and bezel, this many disc
## radii out; its ring grows from the rim by BURST_RING_GROW radii (held inside the region).
const WHEEL_REGION := 1.35
const BURST_RING_GROW := 0.3
## Ring widths (px at its start and end) and the glow's rim share of the disc.
const BURST_RING_W0 := 10.0
const BURST_RING_W1 := 2.0
const BURST_GLOW_EDGE := 1.0
## The phase ring: dashes round it (long and short alternate, so it reads without colour),
## the share of each step a long dash fills, a short dash's share of a long one, its turn
## over the burst (rad) and the ring's width share.
const PHASE_DASHES := 16
const PHASE_DASH_FILL := 0.6
const PHASE_SHORT_DASH := 0.45
const PHASE_TURN := 0.35
const PHASE_RING_SHARE := 0.7
## The phase's glow and rim shares of its alpha and the rim's width (px); the Perfect's
## paper ring's lag (share of the way to the coloured ring) and alpha share.
const PHASE_GLOW_ALPHA := 0.5
const PHASE_RIM_ALPHA := 0.6
const PHASE_RIM_W := 2.0
const PERFECT_PAPER_LAG := 0.6
const PERFECT_PAPER_ALPHA := 0.8
const BURST_SEGMENTS := 48
const BURST_DASH_SEGMENTS := 6
## Below this span (px) a glow is degenerate and is not drawn.
const POLY_MIN_SPAN := 0.5


## ART_BIBLE v2 5.3 T3: a burst on one wheel only, never the screen (it retires the
## full-screen Perfect and boss-phase flashes). `wheel_center` (global) and `radius` (the
## disc's) name the wheel; `kind` is BURST_PERFECT (a radial glow and a ring pulse in `color`,
## default CELL_PINK) or BURST_PHASE (a broken ring in `color`, the boss's corp hue, over a
## faint glow). Peak alpha and duration come from the kind's entry held to T3 (<= 70%,
## <= 1.2 s); the ring stays inside the wheel's region. Through the one flash limiter.
## Reduce effects, headless or the entry off: nothing (the end state at once). Returns
## whether it plays.
func wheel_burst(wheel_center: Vector2, radius: float, kind: StringName, color: Color = Palette.AUTO, pip: Vector2 = Vector2.INF) -> bool:
	var id: StringName = BURST_MOTION.get(kind, &"")
	# ART-2 2C §3.16 phase change v3: orange bits stream from the crossed phase pip (`pip`)
	# under the arc to the bezel, whether or not the limiter lets the burst's flash show.
	if kind == BURST_PHASE and pip != Vector2.INF and radius > 0.0:
		phase_bits(wheel_center, radius, pip)
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
		"reach": wheel_burst_reach(radius), "ease": e.ease, "trans": e.trans})
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
		_draw_glow(c, r, Color(col, a * PHASE_GLOW_ALPHA))
		var step := TAU / PHASE_DASHES
		var turn := PHASE_TURN * q
		var w := lerpf(BURST_RING_W0, BURST_RING_W1, q) * PHASE_RING_SHARE
		for k in PHASE_DASHES:
			var fill := PHASE_DASH_FILL * (1.0 if k % 2 == 0 else PHASE_SHORT_DASH)
			var a0 := turn + k * step
			draw_arc(c, ring_r, a0, a0 + step * fill, BURST_DASH_SEGMENTS, Color(col, a), w, true)
		draw_arc(c, r * BURST_GLOW_EDGE, 0.0, TAU, BURST_SEGMENTS, Color(col, a * PHASE_RIM_ALPHA), PHASE_RIM_W, true)
		return
	_draw_glow(c, r, Color(col, a))
	draw_arc(c, ring_r, 0.0, TAU, BURST_SEGMENTS, Color(col, a), lerpf(BURST_RING_W0, BURST_RING_W1, q), true)
	# A thin paper ring lags the pink one: the latch's click, readable without colour.
	draw_arc(c, lerpf(r, ring_r, PERFECT_PAPER_LAG), 0.0, TAU, BURST_SEGMENTS, Color(Palette.PAPER, a * PERFECT_PAPER_ALPHA), BURST_RING_W1, true)


## A radial glow: `col` at the centre fading to nothing at `r`.
func _draw_glow(c: Vector2, r: float, col: Color) -> void:
	if r * BURST_GLOW_EDGE < POLY_MIN_SPAN:
		return
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
	var tag := {"kind": "tag", "at": at, "text": text, "color": color, "fs": fs, "dur": Motion.seconds(&"result_stamp") + hold,
		"land": Motion.seconds(&"result_stamp"), "from": Motion.amplitude(&"result_stamp"), "delay": delay, "icon": icon}
	_add(tag)
	# ART-2 2C §3.20: every word an effect stamps is a temporary label: it ends by dissolving
	# left to right into 0/1 bits (in its last `temp_label` seconds), never a plain fade.
	if Motion.live(&"temp_label"):
		tag["dissolve"] = minf(Motion.seconds(&"temp_label"), maxf(0.0, float(tag["dur"]) - float(tag["land"])))
		if float(tag["dissolve"]) > 0.0:
			_label_bits(tag)
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
	SliceIcon.draw_icon(ci, c, r, RC.SliceType.DEFRAG, col)
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


## A broken wheel: `pieces` ([polygon (global), colour]) fall `enemy_break`'s amplitude px
## with a spin each, fading out.
## ART-2 2C §3.20 enemy defeated v2: the pieces fly apart and fall; round them the hub
## shockwave and the bits they shed in their own colours, and `word` (DELETED for an enemy)
## as a temporary label that dissolves to bits (`defeat_fx`).
func shards(pieces: Array, word: String = "") -> void:
	if not Motion.live(&"enemy_break") or pieces.is_empty():
		return
	_add({"kind": "shards", "pieces": pieces, "dur": Motion.seconds(&"enemy_break"), "fall": Motion.amplitude(&"enemy_break"),
		"ease": Motion.entry(&"enemy_break").ease, "trans": Motion.entry(&"enemy_break").trans})
	var mid := Vector2.ZERO
	var count := 0
	var colors: Array[Color] = []
	for pc in pieces:
		for v in (pc[0] as PackedVector2Array):
			mid += v
			count += 1
		var col: Color = pc[1]
		if not colors.has(Color(col, 1.0)):
			colors.append(Color(col, 1.0))
	mid /= maxf(1.0, float(count))
	var r := 0.0
	for pc in pieces:
		for v in (pc[0] as PackedVector2Array):
			r = maxf(r, v.distance_to(mid))
	defeat_fx(mid, r, colors, word)


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
func play_card(card: ZineCard, from: Rect2, from_rotation: float, to: Vector2, exhaust: bool, on_done: Callable = Callable(),
		hub: Vector2 = Vector2.INF) -> float:
	# ART-2 2C D16: the card's slap point is where its effect starts (CardFx.origin), even
	# when its motion doesn't play.
	slap_point = to
	if not Motion.live(&"card_play"):
		card.free()
		if on_done.is_valid():
			on_done.call()
		return 0.0
	_adopt(card, from, from_rotation)
	# ART-2 2C §3.18: the sticker's material (the gloss band and the dissolve's scan front).
	card.material = StickerSeam.card_material(card.size)
	# ANIM-R6 A11: each part plays only when its own entry is on (a switched-off stamp or burn
	# takes no time: the card lands, then goes at once).
	var stamps := Motion.live(&"card_stamp")
	var gone_id := &"card_exhaust" if exhaust else &"effect_burst"
	var goes := Motion.live(gone_id)
	var fly := Motion.seconds(&"card_play")
	var land := Motion.seconds(&"card_stamp") if stamps else 0.0
	var gone := Motion.seconds(gone_id) if goes else 0.0
	var fe := Motion.entry(&"card_play")
	var end_pos := to - card.size * 0.5
	var size := Motion.amplitude(&"card_play")
	# ART-2 2C §3.18 step 3, the peel: the sticker pops free (`card_peel`) and a faint liner
	# stays in its slot through the flight.
	if Motion.live(&"card_peel"):
		_add({"kind": "liner", "rect": from, "rot": from_rotation, "dur": fly + Motion.seconds(&"card_peel")})
	var tw := card.create_tween()
	tw.tween_property(card, "position", end_pos, fly).set_ease(fe.ease).set_trans(fe.trans)
	if Motion.live(&"card_peel"):
		var pe := Motion.entry(&"card_peel")
		var pop := minf(Motion.seconds(&"card_peel"), fly * CARD_GROW_SHARE)
		tw.parallel().tween_property(card, "scale", Vector2.ONE * Motion.amplitude(&"card_peel"), pop).set_ease(pe.ease).set_trans(pe.trans)
		tw.parallel().tween_property(card, "scale", Vector2.ONE * size, fly * CARD_GROW_SHARE).set_delay(pop).set_ease(CARD_GROW_EASE)
	else:
		tw.parallel().tween_property(card, "scale", Vector2.ONE * size, fly * CARD_GROW_SHARE).set_ease(CARD_GROW_EASE)
	# §3.18 step 4: it tilts by its velocity (a spring lag), straight again as it lands.
	tw.parallel().tween_method(_tilt_step.bind(card, from_rotation, signf(to.x - from.get_center().x)), 0.0, 1.0, fly)
	if stamps:
		# §3.18 step 5, the slap: drop from a size up, squash 1.13 / 0.86, overshoot, settle;
		# the white contact ring and the gloss sweep.
		tw.tween_callback(func() -> void: _slap(to, card))
		tw.tween_method(_slap_step.bind(card, size), 0.0, 1.0, land)
	var f := {"node": card, "tween": tw, "to": to, "kind": "exhaust" if exhaust else "play", "on_done": on_done}
	if goes and exhaust:
		var xe := Motion.entry(&"card_exhaust")
		tw.tween_callback(func() -> void: embers(Rect2(card.global_position, card.size)))
		tw.tween_property(card, "scale:y", 0.0, gone).set_ease(xe.ease).set_trans(xe.trans)
		tw.parallel().tween_property(card, "modulate", Color(Palette.CELL_PINK.darkened(0.6), 0.0), gone)
	elif goes:
		# §3.18 step 6, dissolve A: a scan front runs down the card; each cell decodes to a 0/1
		# glyph and spirals clockwise into the hub, absorbed over the last 30 %.
		var into := hub if hub != Vector2.INF else to
		tw.tween_callback(func() -> void: _dissolve(card, to, into, gone))
		tw.tween_method(func(p: float) -> void: StickerSeam.set_scan(card, p / CardFx.SCAN_SHARE), 0.0, 1.0, gone)
	tw.tween_callback(func() -> void: _end_flight(f))
	flights.append(f)
	set_process(true)
	# ANIM-R3 A6i: the card is gone (dissolved or burnt) before its effect plays, so it never
	# covers the wheel while that spins.
	return fly + land + gone


## ANIM-R6 A11 (drawing shapes of the card's flight, not timings: those are `card_play`,
## `card_stamp`, `card_exhaust` and `effect_burst` in the table): the card grows to
## `card_play`'s size over this share of the flight, easing out; the dissolve fades easing
## out while it shrinks easing in (it thins away before it vanishes).
const CARD_GROW_SHARE := 0.5
const CARD_GROW_EASE := Tween.EASE_OUT


## ART-2 2C §3.18 step 4: the flying card turns from its slot's tilt to upright, leaning
## FLIGHT_TILT into its travel (`dir` = its side) at mid-flight.
static func _tilt_step(p: float, card: Control, from_rotation: float, dir: float) -> void:
	if is_instance_valid(card):
		card.rotation = from_rotation * (1.0 - p) + FLIGHT_TILT * sin(PI * p) * dir


## §3.18 step 5: the slap's scale at `p` (from the flight's `size` down to 1, squashed).
static func _slap_step(p: float, card: Control, size: float) -> void:
	if is_instance_valid(card):
		card.scale = CardFx.slap_scale(p) * lerpf(size, 1.0, minf(1.0, p / SLAP_SHRINK_SHARE))


## §3.18 step 5: the card lands at `at`: the white contact ring, the gloss sweep (D16: the
## slap point is where its effect starts).
func _slap(at: Vector2, card: Control) -> void:
	slap_point = at
	if not Motion.live(&"card_slap_ring"):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"card_slap_ring"), Motion.seconds(&"card_slap_ring"))
	var r0 := card.size.length() * 0.5 if is_instance_valid(card) else IMPACT_DISC
	_add({"kind": "slap_ring", "at": at, "r0": r0 * SLAP_RING_FROM, "grow": Motion.amplitude(&"card_slap_ring"), "dur": dur})
	if is_instance_valid(card):
		var e := Motion.entry(&"card_slap_ring")
		var tw := card.create_tween()
		tw.tween_method(StickerSeam.set_gloss.bind(card), -0.2, 1.2, dur).set_ease(e.ease).set_trans(e.trans)
		tw.tween_callback(StickerSeam.set_gloss.bind(-1.0, card))


## The slap ring starts at this share of the card's half-diagonal.
const SLAP_RING_FROM := 0.55


## §3.18 step 6: dissolve A's bits for `card` landed at `at`, spiralling into `hub` over
## `seconds`.
func _dissolve(card: Control, at: Vector2, hub: Vector2, seconds: float) -> void:
	if not is_instance_valid(card):
		return
	var r := Rect2(at - card.size * 0.5, card.size)
	last_origin = at
	bits(CardFx.dissolve_path(r, seconds, hub, Settings.text_scale), Palette.CELL_ACID.lerp(Palette.RESIST_GOLD, 0.5), &"effect_burst")


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
	if sprites.is_empty() and flights.is_empty() and (held_word.is_empty() or float(held_word["age"]) >= _word_landed_at(held_word)):
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
			_:
				_draw_fx2(s)  # ART-2 2C: bits, the card's slap and the locked effect set
	if not held_word.is_empty() and float(held_word["age"]) >= float(held_word.get("delay", 0.0)):
		_draw_word(held_word)  # ANIM-R6 A15: VICTORY holds at full strength
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
	# ART-2 2D (§6.4 live numbers): 1A's live_number look: the LIVE_NUMBER_RIM rim and a glow
	# in the number's own colour (its LabelSettings, drawn at the number's animated size).
	var ls := UiTheme.live_number(UiTheme.DISPLAY, Color(s["color"]))
	var lf: Font = ls.font if ls.font != null else f
	draw_string_outline(lf, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, ls.outline_size + ls.shadow_size, Color(ls.shadow_color, ls.shadow_color.a * alpha))
	draw_string_outline(lf, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, ls.outline_size, Color(ls.outline_color, alpha))
	draw_string(lf, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(s["color"], alpha))


## ANIM-R3 A6a: a hit's outcome where it struck: its glyph and "0", popping in and fading.
func _draw_impact(s: Dictionary) -> void:
	var a := float(s["age"]) - float(s.get("delay", 0.0))
	var d := maxf(0.001, float(s["dur"]))
	var q := clampf(a / (d * GROW_SHARE), 0.0, 1.0)
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, POP_SETTLE_TRANS, POP_SETTLE_EASE))
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
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, POP_SETTLE_TRANS, POP_SETTLE_EASE))
	var dissolve := float(s.get("dissolve", 0.0))
	var alpha := minf(1.0, q * 2.0)
	var cut := 0.0
	if dissolve > 0.0:
		# ART-2 2C §3.20: a temporary label dissolves left to right into bits (_label_bits).
		cut = clampf((a - _tag_dissolve_at(s)) / dissolve, 0.0, 1.0)
	else:
		alpha *= 1.0 - clampf((_p(s) - (1.0 - FADE_SHARE)) / FADE_SHARE, 0.0, 1.0)
	var fs := int(s["fs"])
	var text := String(s["text"])
	var font := Palette.marker()
	var icon := String(s.get("icon", ""))
	var iw := stamp_icon_width(fs, icon)
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + iw
	var box := Rect2(-w * 0.5 - fs * WORD_BOX_PAD, -fs * WORD_BOX_H * 0.5, w + fs * WORD_BOX_PAD * 2.0, fs * WORD_BOX_H)
	var col: Color = s["color"]
	var cut_x := box.position.x + box.size.x * cut
	draw_set_transform(_local(s["at"]), WORD_TILT, Vector2.ONE * sc)
	# ART-2 2C §3.18 / §3.20: a vinyl word sticker: a white die-cut edge, the colour's fill,
	# ink or paper lettering (whichever reads on it), cut away from the left as it dissolves.
	var shown := Rect2(Vector2(cut_x, box.position.y), Vector2(box.end.x - cut_x, box.size.y))
	if shown.size.x > 0.0:
		draw_rect(shown.grow(STICKER_EDGE), Color(Palette.STICKER_DIE_CUT, alpha))
		draw_rect(shown, Color(col, alpha))
	var ink := Palette.INK if Palette.contrast(col, Palette.INK) >= Palette.contrast(col, Palette.PAPER) else Palette.PAPER
	if icon == GUARD_NULL and -w * 0.5 >= cut_x:
		draw_guard_null(self, Vector2(-w * 0.5 + fs * GLYPH_SHARE * 0.5, 0.0), fs * GLYPH_SHARE * 0.5, Color(ink, alpha))
	if cut <= 0.0:
		draw_string(font, Vector2(-w * 0.5 + iw, fs * 0.35), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(ink, alpha))
	else:
		var x := -w * 0.5 + iw
		for ch in text:
			var cw := font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			if x + cw * 0.5 >= cut_x:
				draw_string(font, Vector2(x, fs * 0.35), ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(ink, alpha))
			x += cw
	draw_set_transform(Vector2.ZERO)


## ART-2 2C: a word sticker's white die-cut edge (px).
const STICKER_EDGE := 3.0
## ART-2 2C enemy defeated v2: a piece's flight as shares of `enemy_break`'s amplitude (px):
## out from the middle, up, and the gravity that pulls it down after.
const PIECE_FLY := 0.55
const PIECE_UP := 0.6
const PIECE_GRAVITY := 1.6


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
			# value first, shrinking into what the hit deals ("12" -> "6" at half power; ANIM-R6 A4: never a fraction);
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
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, POP_SETTLE_TRANS, POP_SETTLE_EASE))
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
	# ART-2 2C §3.20 enemy defeated v2: the pieces fly apart from the wheel's middle (radial
	# plus up), then gravity takes them, spinning.
	var mid := Vector2.ZERO
	var count := 0
	for pc in pieces:
		for v in (pc[0] as PackedVector2Array):
			mid += v
			count += 1
	mid /= maxf(1.0, float(count))
	for k in pieces.size():
		var poly: PackedVector2Array = pieces[k][0]
		if poly.is_empty():
			continue
		var centre := Vector2.ZERO
		for v in poly:
			centre += v
		centre /= poly.size()
		# Each piece flies off along its own direction, up, then falls and turns (hash scatter).
		var side := (_h(int(s["serial"]), k) - 0.5) * 2.0
		var spin := side * PI * 0.5 * q
		var away := (centre - mid).normalized() if centre.distance_to(mid) > 0.5 else Vector2.UP
		var shift := away * fall * PIECE_FLY * q + Vector2(0.0, -fall * PIECE_UP * q + fall * PIECE_GRAVITY * (0.6 + 0.4 * _h(k, int(s["serial"]), 1)) * q * q)
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
	var sc := lerpf(float(s["from"]), 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, POP_SETTLE_TRANS, POP_SETTLE_EASE))
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


# --- ART-2 2C: sticker card play, 0/1 bits and the locked effect set --------------------------
# ART_BIBLE v2 §3.15, §3.18, §3.20, §5.3-5.4, §6.3. Every effect below plays only when its own
# motion entry is live (nothing under reduce effects or headless: the end state shows at once,
# and the scene never waits on it); local flashes go through the one limiter (a denied flash
# skips the flash and keeps the bits); durations and shake are held to each entry's tier.
# Bits are BitPath streams drawn through BitsSeam (1B's emitter once it lands).

## D16: the last played card's slap point (global; Vector2.INF = none): a card-caused
## effect's bits leave from here, never from the hand (CardFx.origin).
var slap_point: Vector2 = Vector2.INF
## Where the last effect's bits came from (global; tests read it: the D16 origin rule).
var last_origin: Vector2 = Vector2.INF
## The card's liner, a faint outline left in the hand slot through the flight (alpha).
const LINER_ALPHA := 0.35
## A card flight's tilt by velocity (rad at mid-flight; §3.18 step 4 spring lag).
const FLIGHT_TILT := 0.12
## Bit sizes (px at text scale 1.0) for the effect streams; the heal's share of `+` glyphs.
const BIT_MIN := 18.0
const BIT_MAX := 26.0
const BIT_END := 0.45
const HEAL_PLUS_SHARE := 0.3
## A stream's shares of its entry's time: bits appear over STREAM_STAGGER, each travels
## STREAM_TRAVEL (so the last lands by the end); the shape (wall, hexes, drone) follows them.
const STREAM_STAGGER := 0.35
const STREAM_TRAVEL := 0.4
## How far a stream bows to the side (px), and how far the heal's bits start below the wheel
## (share of its radius).
const STREAM_BOW := 40.0
const HEAL_FROM_BELOW := 0.55
## Hit shards: shares of `hit_shards`' time for the free flight, the suck's stagger and each
## shard's travel; their spread (rad) and their smallest glyph (share of the largest).
const SHARD_FREE := 0.28
const SHARD_STAGGER := 0.24
const SHARD_TRAVEL := 0.46
const SHARD_SPREAD := 2.4
const SHARD_MIN_SHARE := 0.6
## A blocked hit's bounced shards fall this far (px) as they fade.
const BOUNCE_FALL := 70.0
## The impact disc at a hit (px) and its tear's size (px): a 3-frame pixel tear.
const IMPACT_DISC := 16.0
const TEAR_PX := 34.0
const TEAR_SECONDS := 0.1
## Crit: crack reach (share of the wheel's radius) and the streaks' flight share.
const CRIT_REACH := 0.45
const STREAK_FLY := 0.3
## Evade: the token's place past the rim (share of the radius); its lift share of the
## effect and its exit (up then left, as shares of the amplitude).
const TOKEN_OUT := 0.12
const TOKEN_LIFT_SHARE := 0.25
const TOKEN_EXIT := Vector2(-1.4, -1.0)
## Corrupt: the glitch's rect round the slice (px at text scale 1.0) and the tick's tear spike.
const SLICE_BOX := Vector2(92, 58)
## Enemy defeated: the shockwave reaches this many radii; bits leave from this share of
## the radius and fall this far (px).
const SHOCK_REACH := 1.35
const DEFEAT_BITS_OUT := 0.8
const DEFEAT_FALL := 140.0
## Phase change: bits run under the HP arc at this share of the radius past the rim.
const PHASE_ARC_OUT := 1.12
## Temporary label: its bits per letter and how far they drift up (px).
const LABEL_BITS_PER_CHAR := 2
const LABEL_RISE := 26.0
## Respin / RAM gain / triggers: bit glyph size (px at text scale 1.0).
const SMALL_BIT := 17.0


## Adds a stream of bits (`path`) in `color`, starting `delay` s from now; returns its
## length (s). Not added when `id`'s motion doesn't play (returns 0).
func bits(path: BitPath, color: Color, id: StringName, delay: float = 0.0, dim: float = 1.0, trail: bool = true) -> float:
	if path == null or path.bits.is_empty() or not Motion.live(id):
		return 0.0
	_add({"kind": "bits", "path": path, "color": color, "delay": delay, "dur": maxf(0.001, path.length()), "dim": dim, "trail": trail})
	return path.length()


func _bit_px(px: float) -> float:
	return px * Settings.text_scale


## ART-2 2C §3.20 hit / crit / blocked: 0/1 shards in the attacker's `color` burst from
## `hit_at` (global) outward from the wheel at `center` (outer radius `r_out`), tumble, then
## curve round the rim into `targets` (the drained HP arc segments). Count and size from the
## campaign config by `damage` (a crit the most, with crack lines and code streaks); a
## `blocked` hit pops the DEFRAG wall first and only `hit_blocked_wall`'s share of the shards
## gets through (the rest bounce off and fall). Starts `delay` s from now. Returns the shards'
## arrival times (s from now, ascending; precomputed: the view schedules on them and never
## reads a particle back); empty when it doesn't play.
func hit_shards(hit_at: Vector2, center: Vector2, r_out: float, targets: Array[Vector2], color: Color, damage: int, crit: bool,
		delay: float = 0.0, blocked: bool = false) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	if not Motion.live(&"hit_shards"):
		return out
	var cfg := RunManager.config()
	var tier := VfxTier.of(&"hit_crit_streaks") if crit else VfxTier.of(&"hit_shards")
	var dur := VfxTier.clamp_seconds(tier, Motion.seconds(&"hit_shards"))
	var n := cfg.fx_shard_count(damage, crit)
	var big := _bit_px(cfg.fx_glyph_px(damage, crit))
	var normal := (hit_at - center).normalized()
	var reach := VfxTier.clamp_radius(tier, Motion.amplitude(&"hit_shards") * (1.4 if crit else 1.0), r_out, r_out * WHEEL_REGION)
	var through := clampf(Motion.amplitude(&"hit_blocked_wall"), 0.0, 1.0) if blocked and Motion.live(&"hit_blocked_wall") else 1.0
	var seed := hash([hit_at.snapped(Vector2.ONE), damage, crit])
	var path := BitPath.shards(seed, hit_at, normal, n, SHARD_SPREAD * (1.25 if crit else 1.0), reach, dur * SHARD_FREE, dur * SHARD_STAGGER,
		dur * SHARD_TRAVEL, targets, center, r_out, big * SHARD_MIN_SHARE, big, BIT_END, blocked, through, BOUNCE_FALL)
	last_origin = hit_at
	bits(path, color, &"hit_shards", delay)
	# The impact disc (a local flash, through the limiter: denied, the shards still fly) and
	# a 3-frame pixel tear.
	if Fx.request_flash():
		_add({"kind": "disc", "at": hit_at, "r": IMPACT_DISC * Settings.text_scale, "color": Palette.PAPER,
			"alpha": VfxTier.clamp_alpha(tier, VfxTier.MAX_FLASH_ALPHA[VfxTier.T2]), "dur": TEAR_SECONDS, "delay": delay})
	_add({"kind": "tear", "at": hit_at, "color": color, "dur": TEAR_SECONDS, "delay": delay, "seed": seed})
	if blocked and Motion.live(&"hit_blocked_wall"):
		_add({"kind": "wall", "shape": "brick", "at": center, "r": r_out, "face": normal.angle(), "n": int(Motion.amplitude(&"block_wall")),
			"color": Palette.NET_CYAN, "dur": VfxTier.clamp_seconds(VfxTier.of(&"hit_blocked_wall"), Motion.seconds(&"hit_blocked_wall")),
			"delay": maxf(0.0, delay - Motion.seconds(&"hit_blocked_wall") * 0.25)})
	if crit and Motion.live(&"hit_crit_streaks"):
		var cd := VfxTier.clamp_seconds(VfxTier.of(&"hit_crit_streaks"), Motion.seconds(&"hit_crit_streaks"))
		_add({"kind": "crit", "at": hit_at, "n": int(Motion.amplitude(&"hit_crit_streaks")), "reach": r_out * CRIT_REACH, "color": color,
			"dur": cd, "delay": delay, "seed": seed})
	for i in path.bits.size():
		if not bool(path.bits[i].get("fade", false)):
			out.append(delay + path.arrival(i))
	out.sort()
	return out


## ART-2 2C §3.20 block / shield gain: `shape` "brick" (DEFRAG bricks pop in course by
## course) or "hex" (SANDBOX hex plates tile out with a ripple) on the side of the wheel at
## `center` (radius `r`) facing `foe` (global); its bits stream from `origin` (the slap point
## for a card, the slice otherwise: D16) to the wall first.
func wall(center: Vector2, r: float, foe: Vector2, shape: String, origin: Vector2, delay: float = 0.0) -> void:
	var id := &"block_wall" if shape == "brick" else &"shield_hex"
	if not Motion.live(id):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(id), Motion.seconds(id))
	var face := (foe - center).angle() if foe.distance_to(center) > 1.0 else 0.0
	var col := Palette.NET_CYAN if shape == "brick" else Palette.CELL_PINK.lerp(Palette.NET_CYAN, 0.6)
	var n := int(Motion.amplitude(id))
	var targets := BitPath.arc_points(center, r * (1.0 + FxDraw.WALL_OUT), face - FxDraw.WALL_SPAN * 0.5, face + FxDraw.WALL_SPAN * 0.5, n)
	last_origin = origin
	bits(BitPath.inflow(hash([center.snapped(Vector2.ONE), shape]), [origin], targets, n, dur * STREAM_STAGGER * 0.5, dur * STREAM_TRAVEL * 0.6,
		STREAM_BOW, _bit_px(BIT_MIN), _bit_px(BIT_MAX), BIT_END), col, id, delay)
	_add({"kind": "wall", "shape": shape, "at": center, "r": r, "face": face, "n": n, "color": col, "dur": dur, "delay": delay + dur * STREAM_STAGGER * 0.5})


## ART-2 2C §3.20 heal: green +/1/0 rise in from outside, below the wheel at `center`
## (radius `r`), into `targets` (the HP arc segments that come back), which relight white
## to green as their bits arrive. Returns the arrivals (s from now).
func heal_inflow(center: Vector2, r: float, targets: Array[Vector2], delay: float = 0.0) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	if not Motion.live(&"heal_inflow") or targets.is_empty():
		return out
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"heal_inflow"), Motion.seconds(&"heal_inflow"))
	var n := int(Motion.amplitude(&"heal_inflow"))
	# From outside: each bit starts past the rim, out from the segment it relights.
	var below: Array[Vector2] = []
	for k in n:
		var t: Vector2 = targets[k % targets.size()]
		var away := (t - center).normalized()
		below.append(t + away.rotated((BitPath.noise(n, k, 21) - 0.5) * 0.8) * r * (HEAL_FROM_BELOW + 0.4 * BitPath.noise(n, k, 22)))
	var path := BitPath.inflow(hash(center.snapped(Vector2.ONE)), below, targets, n, dur * STREAM_STAGGER, dur * STREAM_TRAVEL * 1.4, STREAM_BOW * 0.5,
		_bit_px(BIT_MIN), _bit_px(BIT_MAX), BIT_END, HEAL_PLUS_SHARE)
	last_origin = below[0]
	bits(path, Palette.GAIN, &"heal_inflow", delay)
	_add({"kind": "relight", "at": center, "targets": targets, "dur": dur, "delay": delay + dur * STREAM_STAGGER, "color": Palette.GAIN})
	for t in path.arrivals():
		out.append(delay + t)
	return out


## ART-2 2C §3.20 evade gain: green bits from `origin` form the `>>` token on the rim at
## `at`. The standing EVADE badge is the wheel's.
func evade_gain(at: Vector2, origin: Vector2, delay: float = 0.0) -> void:
	if not Motion.live(&"evade_token"):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"evade_token"), Motion.seconds(&"evade_token"))
	last_origin = origin
	bits(BitPath.inflow(hash(at.snapped(Vector2.ONE)), [origin], [at], int(Motion.amplitude(&"drone_deploy")) / 2, dur * STREAM_STAGGER, dur * STREAM_TRAVEL,
		STREAM_BOW * 0.5, _bit_px(BIT_MIN), _bit_px(BIT_MAX), BIT_END), Palette.GAIN, &"evade_token", delay)
	_add({"kind": "token", "at": at, "to": at, "dur": dur, "delay": delay + dur * (STREAM_STAGGER + STREAM_TRAVEL), "lift": 0.0, "grow": true})


## ART-2 2C §3.20 evade v4: the `>>` token on the rim at `at` lifts early and flies up then
## left; the attack from `attack_from` bends off and chases it; both fade at the screen's
## edge. The wheel never moves.
func evade_token(at: Vector2, attack_from: Vector2, color: Color, delay: float = 0.0) -> void:
	if not Motion.live(&"evade_token"):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"evade_token"), Motion.seconds(&"evade_token"))
	var to := at + TOKEN_EXIT * Motion.amplitude(&"evade_token")
	_add({"kind": "token", "at": at, "to": to, "dur": dur, "delay": maxf(0.0, delay - dur * TOKEN_LIFT_SHARE), "lift": TOKEN_LIFT_SHARE, "grow": false})
	_add({"kind": "chase", "from": attack_from, "at": at, "to": to, "color": color, "dur": dur, "delay": delay})


## ART-2 2C §3.20 apply CORRUPTED v4: pink bits from `origin` (the slap point for a card)
## into the slice at `slice_at`, then the glitch takes the slice left to right with doubled
## tears. The result is the slice's overlay (the wheel's).
func corrupt_apply(slice_at: Vector2, origin: Vector2, delay: float = 0.0) -> void:
	if not Motion.live(&"corrupt_apply"):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"corrupt_apply"), Motion.seconds(&"corrupt_apply"))
	last_origin = origin
	var travel := bits(BitPath.inflow(hash(slice_at.snapped(Vector2.ONE)), [origin], [slice_at], int(Motion.amplitude(&"corrupt_tick")), dur * 0.2, dur * 0.3,
		STREAM_BOW * 0.4, _bit_px(BIT_MIN), _bit_px(BIT_MAX), BIT_END), Palette.CELL_PINK, &"corrupt_apply", delay)
	var box := SLICE_BOX * Settings.text_scale
	_add({"kind": "tears", "rect": Rect2(slice_at - box * 0.5, box), "wipe": clampf(Motion.amplitude(&"corrupt_apply") / maxf(0.01, dur), 0.05, 1.0),
		"color": Palette.CELL_PINK, "color2": Palette.NET_CYAN, "dur": maxf(0.05, dur - travel), "delay": delay + travel, "seed": hash(slice_at.snapped(Vector2.ONE))})


## ART-2 2C §3.20 CORRUPTED tick v3: a flash and tear spike on the slice at `slice_at`, the
## glitch wipes into pink/green bits that run round the rim of the wheel at `center`
## (outer radius `r_out`) into `targets` (HP). Returns the arrivals (s from now).
func corrupt_tick(slice_at: Vector2, center: Vector2, r_out: float, targets: Array[Vector2], delay: float = 0.0) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	if not Motion.live(&"corrupt_tick"):
		return out
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"corrupt_tick"), Motion.seconds(&"corrupt_tick"))
	var n := int(Motion.amplitude(&"corrupt_tick"))
	var seed := hash([slice_at.snapped(Vector2.ONE), n])
	var path := BitPath.shards(seed, slice_at, (slice_at - center).normalized(), n, SHARD_SPREAD, r_out * 0.2, dur * SHARD_FREE * 0.5, dur * SHARD_STAGGER,
		dur * SHARD_TRAVEL, targets, center, r_out, _bit_px(BIT_MIN), _bit_px(BIT_MAX), BIT_END)
	last_origin = slice_at
	# Pink and green bits: two halves of the stream in each colour.
	var half := BitPath.new()
	half.bits = path.bits.slice(n / 2)
	path.bits = path.bits.slice(0, n / 2)
	bits(path, Palette.CELL_PINK, &"corrupt_tick", delay)
	bits(half, Palette.GAIN, &"corrupt_tick", delay)
	var box := SLICE_BOX * Settings.text_scale
	_add({"kind": "tears", "rect": Rect2(slice_at - box * 0.5, box), "wipe": 1.0, "color": Palette.CELL_PINK, "color2": Palette.GAIN,
		"dur": dur * SHARD_FREE, "delay": delay, "seed": seed})
	if Fx.request_flash():
		_add({"kind": "disc", "at": slice_at, "r": box.y * 0.5, "color": Palette.PAPER, "alpha": VfxTier.clamp_alpha(VfxTier.of(&"corrupt_tick"), VfxTier.MAX_FLASH_ALPHA[VfxTier.T2]),
			"dur": TEAR_SECONDS, "delay": delay})
	for t in path.arrivals():
		out.append(delay + t)
	for t in half.arrivals():
		out.append(delay + t)
	out.sort()
	return out


## ART-2 2C §3.20 drone deploy: bits stream from `origin` (the slap point for a card, the
## hub otherwise) to the dock at `dock` and pack into the drone's hex; its sticker slaps on.
func drone_deploy(dock: Vector2, origin: Vector2, color: Color, delay: float = 0.0) -> void:
	if not Motion.live(&"drone_deploy"):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"drone_deploy"), Motion.seconds(&"drone_deploy"))
	last_origin = origin
	bits(BitPath.inflow(hash(dock.snapped(Vector2.ONE)), [origin], [dock], int(Motion.amplitude(&"drone_deploy")), dur * STREAM_STAGGER, dur * STREAM_TRAVEL,
		STREAM_BOW, _bit_px(SMALL_BIT), _bit_px(BIT_MAX), BIT_END), color, &"drone_deploy", delay)
	_add({"kind": "drone_hex", "at": dock, "color": color, "dur": dur, "delay": delay})


## ART-2 2C §3.20 drone attack: the drone's lens ring charges at `at` before its tracer.
func drone_attack(at: Vector2, color: Color, delay: float = 0.0) -> void:
	if not Motion.live(&"drone_attack"):
		return
	_add({"kind": "lens", "at": at, "color": color, "r": FxDraw.DRONE_HEX * Settings.text_scale, "grow": Motion.amplitude(&"drone_attack"),
		"dur": VfxTier.clamp_seconds(VfxTier.of(&"drone_attack"), Motion.seconds(&"drone_attack")), "delay": delay})


## ART-2 2C §3.20 drone destroyed v3: the hex at `at` cracks and pops into 0/1 bits, the
## clamp springs open.
func drone_destroyed(at: Vector2, color: Color, delay: float = 0.0) -> void:
	if not Motion.live(&"drone_destroyed"):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"drone_destroyed"), Motion.seconds(&"drone_destroyed"))
	var fly := Motion.amplitude(&"drone_destroyed")
	last_origin = at
	var pts: Array[Vector2] = []
	var n := int(Motion.amplitude(&"nudge_resist_bits")) + 4
	for k in n:
		var a := TAU * k / n
		pts.append(at + Vector2(cos(a), sin(a)) * fly)
	bits(BitPath.inflow(hash(at.snapped(Vector2.ONE)), [at], pts, n, dur * 0.1, dur * 0.8, STREAM_BOW * 0.2, _bit_px(SMALL_BIT), _bit_px(BIT_MIN), 1.0),
		color, &"drone_destroyed", delay)
	_add({"kind": "drone_burst", "at": at, "color": color, "fly": fly, "dur": dur, "delay": delay})


## ART-2 2C §3.16 / §3.20 phase change v3: orange bits stream from the crossed phase pip
## `pip` (global) along under the HP arc of the wheel at `center` (radius `r`) to the bezel.
func phase_bits(center: Vector2, r: float, pip: Vector2, color: Color = Palette.CORP_MERIDIAN) -> void:
	if not Motion.live(&"phase_change_bits"):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"phase_change_bits"), Motion.seconds(&"phase_change_bits"))
	var a0 := (pip - center).angle()
	var n := int(Motion.amplitude(&"phase_change_bits"))
	# Along under the arc: targets spread from the pip round to the bezel's side (the arc's
	# ends), half each way.
	var ends := BitPath.arc_points(center, r * PHASE_ARC_OUT, a0 - PI * 0.45, a0 + PI * 0.45, n)
	last_origin = pip
	var path := BitPath.new()
	for i in n:
		var to: Vector2 = ends[i]
		var ctrl := center + ((pip + to) * 0.5 - center).normalized() * r * PHASE_ARC_OUT * 1.05
		var appear := dur * STREAM_STAGGER * float(i) / maxf(1.0, float(n - 1))
		path.bits.append({"from": pip, "burst": Vector2.ZERO, "ctrl": ctrl, "to": to, "appear": appear, "release": appear, "travel": dur * 0.55,
			"glyph": BitPath.ONE if BitPath.noise(n, i, 31) > 0.5 else BitPath.ZERO, "size": _bit_px(BIT_MAX), "fade": true, "end_scale": 1.0})
	bits(path, color, &"phase_change_bits", Motion.delay_of(&"phase_change_bits"))


## ART-2 2C §3.20 respin v3: the spent RAM pips at `pips` (global) crack into cyan bits that
## fly to the hub at `hub`; a temporary RESPIN label.
func respin_bits(pips: Array[Vector2], hub: Vector2, word: String = "") -> void:
	if not Motion.live(&"respin_bits") or pips.is_empty():
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"respin_bits"), Motion.seconds(&"respin_bits"))
	var per := maxi(1, int(Motion.amplitude(&"respin_bits")))
	var from: Array[Vector2] = []
	for p in pips:
		for k in per:
			from.append(p)
	last_origin = pips[0]
	bits(BitPath.inflow(hash(hub.snapped(Vector2.ONE)), from, [hub], from.size(), dur * STREAM_STAGGER, dur * STREAM_TRAVEL * 1.4, STREAM_BOW * 2.0,
		_bit_px(SMALL_BIT), _bit_px(BIT_MIN), BIT_END), Palette.NET_CYAN, &"respin_bits")
	if word != "":
		temp_label(hub, word, Palette.NET_CYAN)


## ART-2 2C §3.20 nudge + resistance: the RESIST chip at `at` cracks into grey bits, with a
## temporary `word`.
func nudge_resist(at: Vector2, word: String = "", delay: float = 0.0) -> void:
	if not Motion.live(&"nudge_resist_bits"):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"nudge_resist_bits"), Motion.seconds(&"nudge_resist_bits"))
	var n := int(Motion.amplitude(&"nudge_resist_bits"))
	var pts: Array[Vector2] = []
	for k in n:
		pts.append(at + Vector2((float(k) / maxf(1.0, n - 1.0) - 0.5) * 40.0 * Settings.text_scale, 0.0))
	last_origin = at
	bits(BitPath.drift(hash(at.snapped(Vector2.ONE)), pts, dur * 0.3, dur * 0.7, LABEL_RISE, _bit_px(SMALL_BIT), _bit_px(BIT_MIN)), Palette.DISABLED,
		&"nudge_resist_bits", delay)
	if word != "":
		temp_label(at, word, Palette.RESIST_GOLD, delay)


## ART-2 2C §3.20 RAM gain (option B): bits fall from the TURN banner at `from` down the
## centre gap into the meter's new pips at `pips` (global), `ram_gain_bits`' amplitude per pip.
func ram_gain(from: Vector2, pips: Array[Vector2]) -> void:
	if not Motion.live(&"ram_gain_bits") or pips.is_empty():
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(&"ram_gain_bits"), Motion.seconds(&"ram_gain_bits"))
	var per := maxi(1, int(Motion.amplitude(&"ram_gain_bits")))
	var to: Array[Vector2] = []
	for p in pips:
		for k in per:
			to.append(p)
	last_origin = from
	bits(BitPath.inflow(hash(from.snapped(Vector2.ONE)), [from], to, to.size(), dur * STREAM_STAGGER, dur * (1.0 - STREAM_STAGGER), STREAM_BOW * 0.25,
		_bit_px(SMALL_BIT), _bit_px(SMALL_BIT), BIT_END), Palette.NET_CYAN, &"ram_gain_bits")


## ART-2 2C §3.20 Daemon / firmware trigger: the source at `from` (a Daemon's sigil on the
## rack, a socketed firmware die) pulses and bits in `color` stream to `to`, where it acts.
## `id` is `daemon_trigger` or `firmware_trigger`.
func trigger_fx(from: Vector2, to: Vector2, color: Color, id: StringName = &"daemon_trigger", delay: float = 0.0) -> void:
	if not Motion.live(id):
		return
	var dur := VfxTier.clamp_seconds(VfxTier.of(id), Motion.seconds(id))
	last_origin = from
	_add({"kind": "lens", "at": from, "color": color, "r": FxDraw.DRONE_HEX * Settings.text_scale, "grow": FxDraw.DRONE_HEX * 0.5, "dur": dur * 0.4, "delay": delay})
	bits(BitPath.inflow(hash([from.snapped(Vector2.ONE), id]), [from], [to], int(Motion.amplitude(id)), dur * STREAM_STAGGER, dur * STREAM_TRAVEL * 1.4,
		STREAM_BOW, _bit_px(SMALL_BIT), _bit_px(BIT_MIN), BIT_END), color, id, delay + dur * 0.15)


## ART-2 2C §3.20 temporary label (one TempLabel look): a word sticker pops in at `at`,
## holds `temp_label`'s amplitude (s), then dissolves left to right into 0/1 bits that drift
## up and fade within the entry's duration. Returns the box it covers (global).
func temp_label(at: Vector2, text: String, color: Color, delay: float = 0.0, max_w: float = -1.0) -> Rect2:
	var hold := Motion.amplitude(&"temp_label") + Motion.seconds(&"temp_label") if Motion.live(&"temp_label") else 0.0
	return word_stamp(at, text, color, hold, max_w if max_w > 0.0 else get_global_rect().size.x, -1, delay)


## The bits a tag's word dissolves into (left to right), from its box at rest.
func _label_bits(s: Dictionary) -> void:
	var fs := int(s["fs"])
	var text := String(s["text"])
	var font := Palette.marker()
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + stamp_icon_width(fs, String(s.get("icon", "")))
	var at: Vector2 = s["at"]
	var n := maxi(4, text.length() * LABEL_BITS_PER_CHAR)
	var pts: Array[Vector2] = []
	for k in n:
		var x := -w * 0.5 + w * (float(k) + 0.5) / n
		pts.append(at + Vector2(x, (BitPath.noise(n, k, 41) - 0.5) * fs * 0.6).rotated(WORD_TILT))
	var dur := Motion.seconds(&"temp_label")
	bits(BitPath.drift(hash([at.snapped(Vector2.ONE), text]), pts, dur * 0.4, dur * 0.6, LABEL_RISE * Settings.text_scale, _bit_px(SMALL_BIT), _bit_px(BIT_MIN)),
		s["color"], &"temp_label", float(s.get("delay", 0.0)) + _tag_dissolve_at(s))


## When a tag starts to dissolve (s after it shows): its last `temp_label` seconds.
static func _tag_dissolve_at(s: Dictionary) -> float:
	return maxf(float(s.get("land", 0.0)), float(s["dur"]) - float(s.get("dissolve", 0.0)))


## ART-2 2C §3.20 enemy defeated v2: around the broken wheel's pieces, the hub shockwave
## and bits shed from the pieces in their own colours, falling; `word` (DELETED) as a
## temporary label. The pieces themselves fly apart in `shards`.
func defeat_fx(center: Vector2, r: float, colors: Array[Color], word: String = "") -> void:
	if not Motion.live(&"enemy_defeated_bits"):
		return
	var id := &"enemy_defeated_bits"
	var dur := VfxTier.clamp_seconds(VfxTier.of(id), Motion.seconds(id))
	var delay := Motion.delay_of(id)
	_add({"kind": "shockwave", "at": center, "r0": r * 0.3, "r1": r * SHOCK_REACH, "color": colors[0] if not colors.is_empty() else Palette.PAPER,
		"dur": dur * 0.5, "delay": delay})
	var n := int(Motion.amplitude(id))
	var per := maxi(1, n / maxi(1, colors.size()))
	for c in maxi(1, colors.size()):
		var from: Array[Vector2] = []
		var to: Array[Vector2] = []
		for k in per:
			var a := TAU * (c * per + k) / n + BitPath.noise(c, k, 51)
			var d := Vector2(cos(a), sin(a))
			from.append(center + d * r * DEFEAT_BITS_OUT * (0.5 + 0.5 * BitPath.noise(c, k, 52)))
			to.append(center + d * r * SHOCK_REACH + Vector2(0, DEFEAT_FALL))
		var path := BitPath.inflow(hash([center.snapped(Vector2.ONE), c]), from, to, per, dur * 0.5, dur * 0.45, STREAM_BOW * 0.3, _bit_px(SMALL_BIT), _bit_px(BIT_MAX), 1.0)
		for b in path.bits:
			b["fade"] = true
		bits(path, colors[c] if not colors.is_empty() else Palette.PAPER, id, delay)
	last_origin = center
	if word != "":
		temp_label(center, word, Palette.HARM, delay + dur * 0.3)


# --- ART-2 2C drawing ---------------------------------------------------------------------------

func _draw_fx2(s: Dictionary) -> void:
	var o := get_global_rect().position
	var p := _p(s)
	match String(s["kind"]):
		"bits":
			BitsSeam.draw(self, s["path"], float(s["age"]) - float(s.get("delay", 0.0)), s["color"], o, CardFx.HOT_SECONDS, bool(s.get("trail", true)), float(s.get("dim", 1.0)))
		"liner":
			FxDraw.liner(self, Rect2((s["rect"] as Rect2).position - o, (s["rect"] as Rect2).size), float(s["rot"]), LINER_ALPHA * (1.0 - p))
		"slap_ring":
			FxDraw.slap_ring(self, _local(s["at"]), float(s["r0"]), float(s["grow"]), p, 1.0)
		"wall":
			if String(s["shape"]) == "brick":
				FxDraw.bricks(self, _local(s["at"]), float(s["r"]), float(s["face"]), int(s["n"]), s["color"], p, 1.0)
			else:
				FxDraw.hexes(self, _local(s["at"]), float(s["r"]), float(s["face"]), int(s["n"]), s["color"], p, 1.0)
		"relight":
			var a := sin(p * PI)
			for t in s["targets"]:
				draw_circle(_local(t), 5.0 * Settings.text_scale, Color((Palette.PAPER as Color).lerp(s["color"], p), a))
		"token":
			var lift := float(s.get("lift", 0.0))
			var q := clampf((p - lift) / maxf(0.001, 1.0 - lift), 0.0, 1.0) if lift > 0.0 else 0.0
			var at := (s["at"] as Vector2).lerp(s["to"], q * q)
			var sc := clampf(p * 4.0, 0.0, 1.0) if bool(s.get("grow", false)) else 1.0
			FxDraw.token(self, at - o, sc, Palette.GAIN, 1.0 - (q if lift > 0.0 else clampf((p - 0.7) / 0.3, 0.0, 1.0)))
		"chase":
			# The attack bends off its line and chases the token out.
			var from: Vector2 = s["from"]
			var at0: Vector2 = s["at"]
			var to: Vector2 = s["to"]
			var head := BitPath.quad(from, at0, to, p)
			var tail := BitPath.quad(from, at0, to, maxf(0.0, p - 0.25))
			draw_line(tail - o, head - o, Color(s["color"], 1.0 - p), 4.0, true)
			draw_circle(head - o, 5.0, Color(Palette.PAPER, 1.0 - p))
		"tears":
			var r: Rect2 = s["rect"]
			FxDraw.tears(self, Rect2(r.position - o, r.size), clampf(p / float(s["wipe"]), 0.0, 1.0), s["color"], s["color2"], 1.0 - clampf((p - 0.8) / 0.2, 0.0, 1.0), int(s["seed"]))
		"tear":
			FxDraw.pixel_tear(self, _local(s["at"]), TEAR_PX * Settings.text_scale, s["color"], int(p * 3.0), int(s["seed"]))
		"drone_hex":
			FxDraw.drone_hex(self, _local(s["at"]), s["color"], clampf(p / (STREAM_STAGGER + STREAM_TRAVEL), 0.0, 1.0),
				clampf((p - STREAM_STAGGER - STREAM_TRAVEL) / maxf(0.01, 1.0 - STREAM_STAGGER - STREAM_TRAVEL), 0.0, 1.0), 1.0 - clampf((p - 0.9) / 0.1, 0.0, 1.0))
		"drone_burst":
			FxDraw.drone_burst(self, _local(s["at"]), s["color"], p, float(s["fly"]))
		"lens":
			var c := _local(s["at"])
			draw_arc(c, float(s["r"]) + float(s["grow"]) * (1.0 - p), 0.0, TAU, 32, Color(s["color"], p), 3.0, true)
		"crit":
			FxDraw.cracks(self, _local(s["at"]), int(s["n"]), float(s["reach"]), p, int(s["seed"]))
			FxDraw.streaks(self, _local(s["at"]), int(s["n"]), float(s["reach"]), p, STREAK_FLY, s["color"], int(s["seed"]))
		"shockwave":
			FxDraw.shockwave(self, _local(s["at"]), float(s["r0"]), float(s["r1"]), _ease(s), s["color"])
