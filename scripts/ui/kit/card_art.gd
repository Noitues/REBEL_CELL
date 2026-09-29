class_name CardArt
extends RefCounted
## Card presentation (ART_BIBLE 6.3, 7.3; W4): the card type a card's colour stands for,
## the effect family its illustration is drawn from, and the procedural two-colour
## risograph stand-in painter (a hash-seeded CPU print, cached). Reads content only; pure
## presentation, deterministic, no RNG.

## Card types (ART_BIBLE 6.3: card colour means card type). The value is the ZineCard
## Variant the type is printed on: WHEEL cards on paper, SYSTEM cards on black, HACK cards
## on pink.
enum Type { WHEEL, SYSTEM, HACK }
## The sticker stock (ZineCard.Variant: PAPER 0, BLACK 1, PINK 2) of each type.
const TYPE_VARIANT := {Type.WHEEL: 0, Type.SYSTEM: 1, Type.HACK: 2}
## The type's name and its stock in words (the detail view and the codex say which).
const TYPE_WORDS := {Type.WHEEL: "WHEEL CARD", Type.SYSTEM: "SYSTEM CARD", Type.HACK: "HACK CARD"} # TR
const TYPE_STOCK_WORDS := {Type.WHEEL: "paper", Type.SYSTEM: "black", Type.HACK: "pink"} # TR
## What each type does, one line (the detail view's type row).
const TYPE_TEXT := {Type.WHEEL: "Moves wheels: spins, nudges, flips, snaps and freezes.", # TR
	Type.SYSTEM: "Runs your rig: block, shield, healing, RAM and cards.", # TR
	Type.HACK: "Attacks the target: damage, statuses, breaches and stripped resistance."} # TR

## The statuses that harm the slice they land on (a HACK card applies them).
const HARMFUL_STATUSES: Array[int] = [RC.Status.CORRUPTED, RC.Status.PARASITE]


## The card's type from its first effect (its primary one). Null or effectless: WHEEL.
static func type_of(card: CardData) -> int:
	if card == null:
		return Type.WHEEL
	for e in card.effects:
		if e == null:
			continue
		return _type_of_effect(e)
	return Type.WHEEL


static func _type_of_effect(e: EffectData) -> int:
	match e.type:
		RC.EffectType.DEAL_DAMAGE:
			return Type.SYSTEM if e.target == RC.EffectTarget.SELF else Type.HACK
		RC.EffectType.APPLY_STATUS:
			return Type.HACK if HARMFUL_STATUSES.has(e.status) else Type.SYSTEM
		RC.EffectType.HUB_BREACH, RC.EffectType.DRAIN_RAM:
			return Type.HACK
		RC.EffectType.MODIFY_RESISTANCE:
			return Type.HACK if e.amount < 0 else Type.SYSTEM
		RC.EffectType.GAIN_BLOCK, RC.EffectType.GAIN_SHIELD, RC.EffectType.EVADE, RC.EffectType.HEAL, \
				RC.EffectType.CLEANSE, RC.EffectType.GAIN_RAM, RC.EffectType.DRAW_CARDS, RC.EffectType.DEPLOY_DRONE, \
				RC.EffectType.MODIFY_HEAT, RC.EffectType.GAIN_CYCLES, RC.EffectType.GAIN_SCHEMATICS:
			return Type.SYSTEM
		RC.EffectType.CUSTOM:
			if e.custom_handler != null and e.custom_handler.resource_path.get_file().get_basename() == "steady_hand_handler":
				return Type.SYSTEM
	return Type.WHEEL


## The ZineCard.Variant (stock colour) a card is printed on.
static func variant_of(card: CardData) -> int:
	return int(TYPE_VARIANT[type_of(card)])


# --- Photocopy grain (COMMON stock, ART_BIBLE 6.3) ---------------------------------------------

## The tileable grain tile's side (px), how many of its pixels carry a toner speck (per
## 1024), and the grain's and specks' opacity (0..255; the card tints it with its ink).
const GRAIN_SIDE := 96
const SPECK_PER_1024 := 9
const GRAIN_MAX := 70
const SPECK_ALPHA := 255
static var _grain: ImageTexture = null


## A tileable photocopy grain (white with alpha; drawn modulated by the card's ink): fine
## noise plus a few toner specks. Built once from an integer hash (deterministic).
static func grain_texture() -> Texture2D:
	if _grain == null:
		_grain = ImageTexture.create_from_image(grain_image())
	return _grain


## The grain tile as an Image (FORMAT_LA8).
static func grain_image() -> Image:
	var data := PackedByteArray()
	data.resize(GRAIN_SIDE * GRAIN_SIDE * 2)
	for y in GRAIN_SIDE:
		for x in GRAIN_SIDE:
			var h := ihash(x * 73 + y * 9151 + 17)
			var i := (y * GRAIN_SIDE + x) * 2
			data[i] = 255
			data[i + 1] = SPECK_ALPHA if (h & 1023) < SPECK_PER_1024 else ((h >> 10) & 255) * GRAIN_MAX / 255
	return Image.create_from_data(GRAIN_SIDE, GRAIN_SIDE, false, Image.FORMAT_LA8, data)


## A 31-bit integer hash (deterministic decoration noise; never an RNG).
static func ihash(v: int) -> int:
	var h := (v ^ 0x5bd1e995) & 0x7fffffff
	h = ((h ^ (h >> 15)) * 0x2c1b3c6d) & 0x7fffffff
	h = ((h ^ (h >> 12)) * 0x297a2d39) & 0x7fffffff
	return (h ^ (h >> 15)) & 0x7fffffff


# --- Illustration stand-ins (ART_BIBLE 7.3; designer ruling Q1) ---------------------------------
# A two-colour risograph print: a key pass in INK (PAPER on black stock) and a spot pass in
# the Cell's fluorescent pink, each screened as halftone dots at its own angle, the spot
# pass slightly off register, on a photocopy stock of the card type's colour (paper /
# black / pink) with grain, toner specks and copier streaks. About 30 base compositions,
# one per effect family, shared and tinted per type; rare and class cards get a unique
# variation (composition seeded from a hash of the card id). The master aspect is 3:2
# (768x512 finals); the stand-in renders at the window's height bucket and is cached per
# key and bucket. A card's own `art` texture (CardData.art) replaces the stand-in.

## The effect families, in brief order (docs/art_briefs/cards/).
const FAMILIES: Array[StringName] = [&"spin", &"spin_heavy", &"backspin", &"gear", &"nudge", &"jam", &"inner_ring",
	&"snap", &"flip", &"respin", &"freeze", &"strip", &"breach", &"damage", &"arc", &"overload", &"block", &"shield",
	&"evade", &"heal", &"cleanse", &"corrupt", &"overclock", &"encrypt", &"parasite", &"ram", &"drain", &"draw",
	&"drone", &"calibrate", &"ring_lock", &"steady", &"undock", &"amplify", &"chip"]
## The master's aspect (768x512) and the render heights a window rounds up to (px).
const ASPECT := 1.5
const BUCKETS: Array[int] = [96, 128, 192, 256]
## Halftone: the dot cell as a share of the render height, the key and spot screen angles
## (degrees) and the spot pass's misregistration (share of the height).
const CELL_SHARE := 0.05
const KEY_ANGLE := 45.0
const SPOT_ANGLE := 15.0
const MISREG_SHARE := 0.014
## Photocopy stock: grain strength (0..1 of 255), toner specks per 1024 px, copier
## streak rows per 1024 rows and their darkening, and the edge burn.
const STOCK_GRAIN := 0.05
const STOCK_SPECKS := 3
const STREAK_ROWS := 12
const STREAK_SHADE := 0.06
const EDGE_BURN := 0.1
## Stand-ins rendered per frame at most (the rest draw next frame; ZineCard asks again).
const RENDERS_PER_FRAME := 2

static var _textures: Dictionary = {}
static var _frame: int = -1
static var _renders: int = 0
## Painter state for the composition being drawn.
static var _w: int = 0
static var _h: int = 0
static var _key: PackedFloat32Array
static var _spot: PackedFloat32Array
static var _seed: int = 0
static var _mirror: bool = false
static var _unique: bool = false


## The card's illustration family from its effects (its first effect, with a few pairs
## read together). A sticker without card data (Firmware, Daemon) is "chip".
static func family_of(card: CardData) -> StringName:
	if card == null:
		return &"chip"
	var first: EffectData = null
	var spins := 0
	var calibrate := false
	var self_harm := false
	for e in card.effects:
		if e == null:
			continue
		if first == null:
			first = e
		if e.type == RC.EffectType.SPIN:
			spins += 1
		if e.type == RC.EffectType.CUSTOM and _handler(e) == "calibrate_handler":
			calibrate = true
		if e.type == RC.EffectType.DEAL_DAMAGE and e.target == RC.EffectTarget.SELF:
			self_harm = true
	if first == null:
		return &"chip"
	if spins >= 2 or (first.type == RC.EffectType.SPIN and calibrate):
		return &"gear"
	match first.type:
		RC.EffectType.SPIN:
			if first.amount < 0:
				return &"backspin"
			return &"spin_heavy" if first.amount >= 6 else &"spin"
		RC.EffectType.NUDGE:
			if first.ring_scope == RC.RingScope.INNER:
				return &"inner_ring"
			return &"jam" if card.wheel_target == RC.WheelTarget.ENEMY else &"nudge"
		RC.EffectType.FLIP:
			return &"flip"
		RC.EffectType.RESPIN:
			return &"respin"
		RC.EffectType.FREEZE:
			return &"freeze"
		RC.EffectType.MODIFY_RESISTANCE:
			return &"strip"
		RC.EffectType.HUB_BREACH:
			return &"breach"
		RC.EffectType.DEAL_DAMAGE:
			if first.target == RC.EffectTarget.ALL_ENEMIES:
				return &"arc"
			return &"overload" if self_harm else &"damage"
		RC.EffectType.GAIN_BLOCK:
			return &"block"
		RC.EffectType.GAIN_SHIELD:
			return &"shield"
		RC.EffectType.EVADE:
			return &"evade"
		RC.EffectType.HEAL:
			return &"heal"
		RC.EffectType.CLEANSE:
			return &"cleanse"
		RC.EffectType.APPLY_STATUS:
			match first.status:
				RC.Status.CORRUPTED:
					return &"corrupt"
				RC.Status.OVERCLOCKED:
					return &"overclock"
				RC.Status.ENCRYPTED:
					return &"encrypt"
				RC.Status.PARASITE:
					return &"parasite"
		RC.EffectType.GAIN_RAM:
			return &"ram"
		RC.EffectType.DRAIN_RAM:
			return &"drain"
		RC.EffectType.DRAW_CARDS:
			return &"draw"
		RC.EffectType.DEPLOY_DRONE:
			return &"drone"
		RC.EffectType.SNAP_TO_CENTER:
			return &"snap"
		RC.EffectType.DOUBLE_NUDGE_CARDS, RC.EffectType.RETRIGGER:
			return &"amplify"
		RC.EffectType.CUSTOM:
			match _handler(first):
				"calibrate_handler":
					return &"calibrate"
				"momentum_handler":
					return &"spin"
				"ring_lock_handler":
					return &"ring_lock"
				"steady_hand_handler":
					return &"steady"
				"undock_handler":
					return &"undock"
	return &"chip"


static func _handler(e: EffectData) -> String:
	return e.custom_handler.resource_path.get_file().get_basename() if e.custom_handler != null else ""


## True when the card gets unique art (Q1): rare and up, and every class card.
static func is_unique(card: CardData) -> bool:
	return card != null and (card.rarity >= RC.Rarity.RARE or card.class_id != &"")


## The key a stand-in is cached and seeded by: the card id for unique art, else the family.
static func art_key(card: CardData, fallback: String = "") -> String:
	if is_unique(card):
		return "id:" + String(card.id)
	if card == null:
		return "chip:" + fallback
	return "family:" + String(family_of(card))


## The render height for a window `h` px tall (the smallest bucket that holds it).
static func bucket_for(h: float) -> int:
	for b in BUCKETS:
		if h <= b:
			return b
	return BUCKETS[BUCKETS.size() - 1]


## The card's illustration for a window `window_h` px tall: its own `art` texture when it
## has one (the final art swaps in with no code change, STYLE_GUIDE 7), else the cached
## stand-in, rendered now if the frame's budget allows (null = ask again next frame).
static func texture_for(card: CardData, variant: int, window_h: float, fallback: String = "") -> Texture2D:
	if card != null and card.art != null:
		return card.art
	var b := bucket_for(window_h)
	var ck := "%s|%d|%d" % [art_key(card, fallback), variant, b]
	if _textures.has(ck):
		return _textures[ck]
	var f := Engine.get_process_frames()
	if f != _frame:
		_frame = f
		_renders = 0
	if _renders >= RENDERS_PER_FRAME:
		return null
	_renders += 1
	var tex := ImageTexture.create_from_image(render_image(family_of(card), art_key(card, fallback), variant, b))
	_textures[ck] = tex
	return tex


## Drops every cached stand-in (tests; a language or content reload).
static func clear_cache() -> void:
	_textures.clear()


## Renders a stand-in: `family`'s composition (seeded by `key`) printed in two inks on the
## stock of card variant `variant` (ZineCard.Variant), `h` px tall at 3:2 (RGB8).
static func render_image(family: StringName, key: String, variant: int, h: int) -> Image:
	_h = maxi(8, h)
	_w = roundi(_h * ASPECT)
	_key = PackedFloat32Array()
	_key.resize(_w * _h)
	_spot = PackedFloat32Array()
	_spot.resize(_w * _h)
	_seed = ihash(key.hash())
	_unique = key.begins_with("id:")
	_mirror = _unique and (_seed & 1) == 1
	_compose(family)
	return _print(variant)


## The stock, key ink and spot ink of card variant `variant` (0 paper, 1 black, 2 pink).
static func inks(variant: int) -> Array[Color]:
	match variant:
		1:
			return [Palette.INK, Palette.PAPER, Palette.CELL_PINK]
		2:
			return [Palette.STICKER_PINK, Palette.INK, Palette.CELL_PINK]
	return [Palette.PAPER_ALT, Palette.INK, Palette.CELL_PINK]


## Screens the two tone passes into halftone dots and prints them on the stock.
static func _print(variant: int) -> Image:
	var cols := inks(variant)
	var stock: Color = cols[0]
	var key_ink: Color = cols[1]
	var spot_ink: Color = cols[2]
	var dark := stock.get_luminance() < 0.5
	var cell := maxf(2.0, _h * CELL_SHARE)
	var ka := deg_to_rad(KEY_ANGLE)
	var sa := deg_to_rad(SPOT_ANGLE)
	var kc := cos(ka) / cell
	var ks := sin(ka) / cell
	var sc := cos(sa) / cell
	var ss := sin(sa) / cell
	var mis := maxi(1, roundi(_h * MISREG_SHARE))
	var mdx := mis if (_seed & 2) == 0 else -mis
	var mdy := mis if (_seed & 4) == 0 else -mis
	var data := PackedByteArray()
	data.resize(_w * _h * 3)
	var streak_seed := _seed & 0xffff
	for y in _h:
		var streak := STREAK_SHADE if (ihash(y * 7919 + streak_seed) & 1023) < STREAK_ROWS else 0.0
		var ey := minf(float(y), float(_h - 1 - y)) / _h
		for x in _w:
			var i := y * _w + x
			# The stock: the type colour, grain, specks, a copier streak and a burnt edge.
			var n := ihash(i * 31 + streak_seed)
			var ex := minf(float(x), float(_w - 1 - x)) / _h
			var burn := EDGE_BURN * maxf(0.0, 1.0 - minf(ex, ey) * 12.0)
			var g := (float(n & 255) / 255.0 - 0.5) * STOCK_GRAIN - streak - burn
			var r := stock.r + g
			var gg := stock.g + g
			var b := stock.b + g
			if (n >> 8 & 1023) < STOCK_SPECKS:
				r = key_ink.r
				gg = key_ink.g
				b = key_ink.b
			# The spot pass, off register.
			var sx := clampi(x - mdx, 0, _w - 1)
			var sy := clampi(y - mdy, 0, _h - 1)
			var st := _spot[sy * _w + sx]
			if st > 0.0:
				var cov := _dot(x * sc + y * ss, -x * ss + y * sc, st, cell)
				if cov > 0.0:
					if dark:
						r = 1.0 - (1.0 - r) * (1.0 - spot_ink.r * cov)
						gg = 1.0 - (1.0 - gg) * (1.0 - spot_ink.g * cov)
						b = 1.0 - (1.0 - b) * (1.0 - spot_ink.b * cov)
					else:
						r *= lerpf(1.0, spot_ink.r, cov)
						gg *= lerpf(1.0, spot_ink.g, cov)
						b *= lerpf(1.0, spot_ink.b, cov)
			# The key pass.
			var kt := _key[i]
			if kt > 0.0:
				var cov := _dot(x * kc + y * ks, -x * ks + y * kc, kt, cell)
				if cov > 0.0:
					r = lerpf(r, key_ink.r, cov)
					gg = lerpf(gg, key_ink.g, cov)
					b = lerpf(b, key_ink.b, cov)
			var o := i * 3
			data[o] = clampi(roundi(r * 255.0), 0, 255)
			data[o + 1] = clampi(roundi(gg * 255.0), 0, 255)
			data[o + 2] = clampi(roundi(b * 255.0), 0, 255)
	return Image.create_from_data(_w, _h, false, Image.FORMAT_RGB8, data)


## A halftone dot's coverage (0..1) at screen coords (u, v) (in cells) for tone `t`: the
## dot's radius grows with the tone (solid above 0.92), with a one-pixel soft edge.
static func _dot(u: float, v: float, t: float, cell: float) -> float:
	if t >= 0.92:
		return 1.0
	var fu := u - floorf(u) - 0.5
	var fv := v - floorf(v) - 0.5
	var d := sqrt(fu * fu + fv * fv)
	var rad := sqrt(t) * 0.72
	return clampf((rad - d) * cell + 0.5, 0.0, 1.0)


# --- Painter primitives (unit space: x 0..1.5, y 0..1; tone 0..1, max-composited) ----------------

## A seeded 0..1 value for parameter `k` of this composition (hash of the key; no RNG).
static func _p(k: int) -> float:
	return float(ihash(_seed + k * 7919) & 0xffff) / 65535.0


## A jitter of +-`amount` for parameter `k` (0 for shared family art: seed from the family).
static func _j(k: int, amount: float) -> float:
	return (_p(k) - 0.5) * 2.0 * amount


static func _px(u: float) -> float:
	return (ASPECT - u if _mirror else u) * _h


static func _stamp(buf: PackedFloat32Array, i: int, v: float) -> void:
	if v < 0.0:
		buf[i] = 0.0
	elif v > buf[i]:
		buf[i] = v


## A disc (v < 0 knocks out to bare stock).
static func disc(buf: PackedFloat32Array, cx: float, cy: float, r: float, v: float) -> void:
	ring(buf, cx, cy, r * 0.5, r, v)


## An annulus of radius `r` and width `w`, from angle a0 to a1 (radians, clockwise from +x).
static func ring(buf: PackedFloat32Array, cx: float, cy: float, r: float, w: float, v: float, a0: float = 0.0, a1: float = TAU) -> void:
	var pcx := _px(cx)
	var pcy := cy * _h
	var ro := (r + w * 0.5) * _h
	var ri := maxf(0.0, (r - w * 0.5) * _h)
	var full := a1 - a0 >= TAU - 0.001
	if _mirror and not full:
		var t0 := PI - a1
		a1 = PI - a0
		a0 = t0
	for y in range(maxi(0, floori(pcy - ro)), mini(_h, ceili(pcy + ro) + 1)):
		for x in range(maxi(0, floori(pcx - ro)), mini(_w, ceili(pcx + ro) + 1)):
			var dx := x + 0.5 - pcx
			var dy := y + 0.5 - pcy
			var d := sqrt(dx * dx + dy * dy)
			if d > ro or d < ri:
				continue
			if not full:
				var a := fposmod(atan2(dy, dx) - a0, TAU)
				if a > a1 - a0:
					continue
			_stamp(buf, y * _w + x, v)


## A radial glow: tone `v` at the centre fading to 0 at radius `r`.
static func glow(buf: PackedFloat32Array, cx: float, cy: float, r: float, v: float) -> void:
	var pcx := _px(cx)
	var pcy := cy * _h
	var pr := r * _h
	for y in range(maxi(0, floori(pcy - pr)), mini(_h, ceili(pcy + pr) + 1)):
		for x in range(maxi(0, floori(pcx - pr)), mini(_w, ceili(pcx + pr) + 1)):
			var d := Vector2(x + 0.5 - pcx, y + 0.5 - pcy).length() / pr
			if d < 1.0:
				_stamp(buf, y * _w + x, v * (1.0 - d))


## An axis-aligned rectangle.
static func rect(buf: PackedFloat32Array, x0: float, y0: float, x1: float, y1: float, v: float) -> void:
	poly(buf, PackedVector2Array([Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)]), v)


## A rectangle `w` x `hh` centred at (cx, cy) turned `a` radians.
static func rect_rot(buf: PackedFloat32Array, cx: float, cy: float, w: float, hh: float, a: float, v: float) -> void:
	var c := Vector2(cx, cy)
	var ax := Vector2(cos(a), sin(a))
	var ay := ax.orthogonal()
	poly(buf, PackedVector2Array([c - ax * w * 0.5 - ay * hh * 0.5, c + ax * w * 0.5 - ay * hh * 0.5,
		c + ax * w * 0.5 + ay * hh * 0.5, c - ax * w * 0.5 + ay * hh * 0.5]), v)


## A convex polygon (unit points, either winding).
static func poly(buf: PackedFloat32Array, pts: PackedVector2Array, v: float) -> void:
	var p := PackedVector2Array()
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for q in pts:
		var pp := Vector2(_px(q.x), q.y * _h)
		p.append(pp)
		lo = lo.min(pp)
		hi = hi.max(pp)
	var n := p.size()
	for y in range(maxi(0, floori(lo.y)), mini(_h, ceili(hi.y) + 1)):
		for x in range(maxi(0, floori(lo.x)), mini(_w, ceili(hi.x) + 1)):
			var pt := Vector2(x + 0.5, y + 0.5)
			var pos := false
			var neg := false
			for k in n:
				var a := p[k]
				var b := p[(k + 1) % n]
				var cr := (b - a).cross(pt - a)
				if cr > 0.0:
					pos = true
				elif cr < 0.0:
					neg = true
				if pos and neg:
					break
			if not (pos and neg):
				_stamp(buf, y * _w + x, v)


## A thick line (a capsule) from (x0, y0) to (x1, y1), `w` wide.
static func line(buf: PackedFloat32Array, x0: float, y0: float, x1: float, y1: float, w: float, v: float) -> void:
	var a := Vector2(_px(x0), y0 * _h)
	var b := Vector2(_px(x1), y1 * _h)
	var r := w * _h * 0.5
	var lo := a.min(b) - Vector2(r, r)
	var hi := a.max(b) + Vector2(r, r)
	var ab := b - a
	var l2 := maxf(0.0001, ab.length_squared())
	for y in range(maxi(0, floori(lo.y)), mini(_h, ceili(hi.y) + 1)):
		for x in range(maxi(0, floori(lo.x)), mini(_w, ceili(hi.x) + 1)):
			var pt := Vector2(x + 0.5, y + 0.5)
			var t := clampf((pt - a).dot(ab) / l2, 0.0, 1.0)
			if pt.distance_to(a + ab * t) <= r:
				_stamp(buf, y * _w + x, v)


## A polyline of thick segments.
static func path(buf: PackedFloat32Array, pts: PackedVector2Array, w: float, v: float) -> void:
	for k in pts.size() - 1:
		line(buf, pts[k].x, pts[k].y, pts[k + 1].x, pts[k + 1].y, w, v)


## An arrowhead at `tip` pointing along `dir` (unit), `s` long.
static func head(buf: PackedFloat32Array, tip: Vector2, dir: Vector2, s: float, v: float) -> void:
	var d := dir.normalized()
	var o := d.orthogonal()
	poly(buf, PackedVector2Array([tip + d * s * 0.3, tip - d * s * 0.7 + o * s * 0.55, tip - d * s * 0.7 - o * s * 0.55]), v)


## A circular arrow of radius `r` from a0 to a1 (clockwise when a1 > a0), `w` thick.
static func arrow_arc(buf: PackedFloat32Array, cx: float, cy: float, r: float, a0: float, a1: float, w: float, v: float) -> void:
	ring(buf, cx, cy, r, w, v, minf(a0, a1), maxf(a0, a1))
	var tip := Vector2(cx, cy) + Vector2(cos(a1), sin(a1)) * r
	var dir := Vector2(-sin(a1), cos(a1)) * (1.0 if a1 > a0 else -1.0)
	head(buf, tip, dir, w * 3.2, v)


## A straight arrow.
static func arrow(buf: PackedFloat32Array, x0: float, y0: float, x1: float, y1: float, w: float, v: float) -> void:
	var d := Vector2(x1 - x0, y1 - y0).normalized()
	line(buf, x0, y0, x1 - d.x * w * 2.0, y1 - d.y * w * 2.0, w, v)
	head(buf, Vector2(x1, y1), d, w * 3.4, v)


## A spinner wheel: rim, spokes between `n` slices turned `rot`, a hub, and slice `hi`
## flooded in the spot pass.
static func wheel(cx: float, cy: float, r: float, n: int, rot: float, hi: int = 0) -> void:
	var step := TAU / n
	ring(_spot, cx, cy, r * 0.5, r * 0.62, 0.55, rot + hi * step, rot + (hi + 1) * step)
	ring(_key, cx, cy, r, r * 0.09, 1.0)
	ring(_key, cx, cy, r * 0.82, r * 0.03, 0.8)
	for k in n:
		var a := rot + k * step
		line(_key, cx + cos(a) * r * 0.2, cy + sin(a) * r * 0.2, cx + cos(a) * r, cy + sin(a) * r, r * 0.04, 0.9)
	disc(_key, cx, cy, r * 0.2, 1.0)
	disc(_key, cx, cy, r * 0.09, -1.0)


## The pointer (a wedge over the wheel's top).
static func pointer(cx: float, cy: float, r: float) -> void:
	poly(_key, PackedVector2Array([Vector2(cx, cy - r * 0.86), Vector2(cx - r * 0.13, cy - r * 1.18), Vector2(cx + r * 0.13, cy - r * 1.18)]), 1.0)


## Speed lines left of (x, y).
static func speed(x: float, y: float, n: int, span: float, length_u: float, v: float) -> void:
	for k in n:
		var yy := y - span * 0.5 + span * (k + 0.5) / n
		line(_spot, x - length_u * (0.6 + 0.4 * _p(900 + k)), yy, x, yy, 0.018, v)


## A starburst of `n` spikes.
static func burst(buf: PackedFloat32Array, cx: float, cy: float, r0: float, r1: float, n: int, v: float, rot: float = 0.0) -> void:
	for k in n:
		var a := rot + k * TAU / n
		var b := a + PI / n
		poly(buf, PackedVector2Array([Vector2(cx, cy) + Vector2(cos(a - 0.12), sin(a - 0.12)) * r0,
			Vector2(cx, cy) + Vector2(cos(b), sin(b)) * r1, Vector2(cx, cy) + Vector2(cos(a + 0.12), sin(a + 0.12)) * r0]), v)
	disc(buf, cx, cy, r0 * 1.05, v)


## A lightning bolt from (x0, y0) to (x1, y1) in `n` zigzags.
static func bolt(buf: PackedFloat32Array, x0: float, y0: float, x1: float, y1: float, n: int, amp: float, w: float, v: float, k0: int = 0) -> void:
	var pts := PackedVector2Array()
	var a := Vector2(x0, y0)
	var b := Vector2(x1, y1)
	var o := (b - a).orthogonal().normalized()
	for k in n + 1:
		var t := float(k) / n
		var side := 0.0 if k == 0 or k == n else (1.0 if k % 2 == 0 else -1.0) * amp * (0.6 + 0.8 * _p(k0 + k))
		pts.append(a.lerp(b, t) + o * side)
	path(buf, pts, w, v)


## A card outline (a playing card of the game) at (cx, cy), turned `a`.
static func card_shape(cx: float, cy: float, w: float, a: float, fill: float) -> void:
	rect_rot(_key, cx, cy, w, w * 1.35, a, 1.0)
	rect_rot(_key, cx, cy, w * 0.84, w * 1.19, a, -1.0)
	rect_rot(_spot, cx, cy, w * 0.84, w * 1.19, a, fill)


## A microchip: a die with pins.
static func chip(cx: float, cy: float, s: float) -> void:
	for k in 5:
		var o := -s * 0.4 + k * s * 0.2
		line(_key, cx + o, cy - s * 0.7, cx + o, cy + s * 0.7, s * 0.06, 1.0)
		line(_key, cx - s * 0.7, cy + o, cx + s * 0.7, cy + o, s * 0.06, 1.0)
	rect(_key, cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.5, 1.0)
	rect(_key, cx - s * 0.4, cy - s * 0.4, cx + s * 0.4, cy + s * 0.4, -1.0)
	rect(_spot, cx - s * 0.4, cy - s * 0.4, cx + s * 0.4, cy + s * 0.4, 0.5)
	rect(_key, cx - s * 0.18, cy - s * 0.18, cx + s * 0.18, cy + s * 0.18, 1.0)


## A padlock.
static func lock(cx: float, cy: float, s: float, open: bool = false) -> void:
	ring(_key, cx + (s * 0.25 if open else 0.0), cy - s * 0.35, s * 0.32, s * 0.12, 1.0, PI, TAU)
	line(_key, cx - s * 0.32 + (s * 0.25 if open else 0.0), cy - s * 0.35, cx - s * 0.32 + (s * 0.25 if open else 0.0), cy - s * 0.1 - (s * 0.2 if open else 0.0), s * 0.12, 1.0)
	line(_key, cx + s * 0.32 + (s * 0.25 if open else 0.0), cy - s * 0.35, cx + s * 0.32 + (s * 0.25 if open else 0.0), cy - s * 0.1, s * 0.12, 1.0)
	rect(_key, cx - s * 0.5, cy - s * 0.12, cx + s * 0.5, cy + s * 0.6, 1.0)
	rect(_spot, cx - s * 0.42, cy - s * 0.04, cx + s * 0.42, cy + s * 0.52, 0.7)
	disc(_key, cx, cy + s * 0.2, s * 0.1, -1.0)


# --- The compositions (one per family; unique cards vary them through _p / _j) ------------------

static func _compose(family: StringName) -> void:
	# Every print gets a flat of halftone behind its subject (the spot's paper tint).
	glow(_spot, 0.75 + _j(1, 0.2), 0.5 + _j(2, 0.15), 0.7, 0.2)
	var cx := 0.75 + _j(3, 0.08)
	var cy := 0.52 + _j(4, 0.05)
	var rot := _j(5, 0.6)
	match family:
		&"spin":
			wheel(cx - 0.12, cy, 0.3, 6, rot, 1)
			pointer(cx - 0.12, cy, 0.3)
			arrow_arc(_key, cx - 0.12, cy, 0.4, -2.4, 0.6, 0.05, 1.0)
			speed(cx - 0.5, cy, 4, 0.36, 0.25, 0.8)
		&"spin_heavy":
			wheel(cx, cy, 0.3, 8, rot, 2)
			arrow_arc(_key, cx, cy, 0.38, -2.8, 1.2, 0.06, 1.0)
			arrow_arc(_spot, cx, cy, 0.46, -1.8, 2.2, 0.05, 0.9)
			speed(cx - 0.45, cy - 0.1, 6, 0.6, 0.3, 0.9)
			speed(cx + 0.7, cy + 0.1, 4, 0.4, 0.2, 0.7)
		&"backspin":
			wheel(cx + 0.1, cy, 0.3, 6, rot, 4)
			arrow_arc(_key, cx + 0.1, cy, 0.4, 0.8, -2.2, 0.05, 1.0)
			speed(cx + 0.72, cy, 4, 0.3, 0.22, 0.8)
		&"gear":
			for g in 2:
				var gx := cx - 0.2 + g * 0.42
				var gy := cy + (0.08 if g == 0 else -0.1)
				var gr := 0.2 if g == 0 else 0.16
				burst(_key, gx, gy, gr * 0.85, gr * 1.18, 10 if g == 0 else 8, 1.0, rot + g * 0.3)
				disc(_key, gx, gy, gr * 0.55, -1.0)
				disc(_spot, gx, gy, gr * 0.55, 0.6 if g == 0 else 0.3)
				disc(_key, gx, gy, gr * 0.18, 1.0)
			arrow_arc(_key, cx - 0.2, cy + 0.08, 0.32, 0.5, 2.2, 0.035, 1.0)
		&"nudge":
			wheel(cx, cy + 0.12, 0.42, 10, rot - PI * 0.5, 0)
			pointer(cx, cy + 0.12, 0.42)
			for side: float in [-1.0, 1.0]:
				head(_key, Vector2(cx + side * 0.34, cy - 0.3), Vector2(side, 0), 0.12, 1.0)
				head(_spot, Vector2(cx + side * 0.46, cy - 0.3), Vector2(side, 0), 0.1, 0.8)
		&"jam":
			wheel(cx + 0.15, cy, 0.34, 8, rot, 3)
			line(_key, cx - 0.55, cy + 0.34, cx + 0.05, cy - 0.12, 0.07, 1.0)
			poly(_key, PackedVector2Array([Vector2(cx + 0.02, cy - 0.16), Vector2(cx + 0.16, cy - 0.26), Vector2(cx + 0.08, cy - 0.06)]), 1.0)
			burst(_spot, cx + 0.06, cy - 0.14, 0.05, 0.16, 7, 0.9)
		&"inner_ring":
			ring(_key, cx, cy, 0.38, 0.05, 1.0)
			ring(_key, cx, cy, 0.24, 0.04, 1.0)
			ring(_spot, cx, cy, 0.18, 0.16, 0.7)
			for k in 6:
				var a := rot + k * TAU / 6.0
				line(_key, cx + cos(a) * 0.1, cy + sin(a) * 0.1, cx + cos(a) * 0.24, cy + sin(a) * 0.24, 0.02, 0.9)
			arrow_arc(_key, cx, cy, 0.3, -1.2, 1.0, 0.035, 1.0)
			disc(_key, cx, cy, 0.06, 1.0)
		&"snap":
			wheel(cx, cy, 0.34, 6, rot, 0)
			ring(_spot, cx, cy - 0.2, 0.12, 0.03, 1.0)
			line(_key, cx, cy - 0.46, cx, cy + 0.06, 0.02, 1.0)
			line(_key, cx - 0.16, cy - 0.2, cx + 0.16, cy - 0.2, 0.02, 1.0)
			ring(_key, cx, cy - 0.2, 0.07, 0.02, 1.0)
		&"flip":
			ring(_key, cx - 0.2, cy, 0.24, 0.05, 1.0, PI * 0.5, PI * 1.5)
			ring(_spot, cx - 0.2, cy, 0.12, 0.24, 0.6, PI * 0.5, PI * 1.5)
			ring(_key, cx + 0.2, cy, 0.24, 0.05, 1.0, -PI * 0.5, PI * 0.5)
			ring(_key, cx + 0.2, cy, 0.12, 0.24, 0.35, -PI * 0.5, PI * 0.5)
			line(_key, cx, cy - 0.42, cx, cy + 0.42, 0.015, 0.8)
			arrow(_key, cx - 0.2, cy - 0.34, cx + 0.2, cy - 0.34, 0.03, 1.0)
			arrow(_key, cx + 0.2, cy + 0.34, cx - 0.2, cy + 0.34, 0.03, 1.0)
		&"respin":
			for d in 2:
				var dx := cx - 0.2 + d * 0.36
				var dy := cy + (0.06 if d == 0 else -0.12)
				rect_rot(_key, dx, dy, 0.28, 0.28, rot * 0.5 + d * 0.5, 1.0)
				rect_rot(_key, dx, dy, 0.22, 0.22, rot * 0.5 + d * 0.5, -1.0)
				rect_rot(_spot, dx, dy, 0.22, 0.22, rot * 0.5 + d * 0.5, 0.45)
				for pip in (3 if d == 0 else 5):
					disc(_key, dx + _j(40 + pip + d * 10, 0.07), dy + _j(60 + pip + d * 10, 0.07), 0.025, 1.0)
			arrow_arc(_key, cx, cy, 0.42, 3.6, 5.8, 0.035, 1.0)
		&"freeze":
			for k in 6:
				var a := rot + k * TAU / 6.0
				var tip := Vector2(cx, cy) + Vector2(cos(a), sin(a)) * 0.38
				line(_key, cx, cy, tip.x, tip.y, 0.035, 1.0)
				var mid := Vector2(cx, cy).lerp(tip, 0.62)
				for side: float in [-0.7, 0.7]:
					var b := mid + Vector2(cos(a + side), sin(a + side)) * 0.12
					line(_key, mid.x, mid.y, b.x, b.y, 0.025, 1.0)
			glow(_spot, cx, cy, 0.5, 0.8)
			disc(_key, cx, cy, 0.05, 1.0)
		&"strip":
			for k in 4:
				var o := k * 0.07
				rect_rot(_key if k == 0 else _spot, cx - 0.1 + o, cy - 0.12 + o * 0.9, 0.5, 0.34, rot * 0.2 - 0.25 + k * 0.12, 1.0 if k == 0 else 0.55 - k * 0.1)
				rect_rot(_key, cx - 0.1 + o, cy - 0.12 + o * 0.9, 0.44, 0.28, rot * 0.2 - 0.25 + k * 0.12, -1.0)
			arrow(_key, cx + 0.15, cy - 0.3, cx + 0.5, cy - 0.42, 0.03, 1.0)
		&"breach":
			var pts := PackedVector2Array()
			for k in 6:
				pts.append(Vector2(cx, cy) + Vector2(cos(k * TAU / 6.0 + 0.52), sin(k * TAU / 6.0 + 0.52)) * 0.3)
			poly(_key, pts, 1.0)
			var inner := PackedVector2Array()
			for q in pts:
				inner.append(Vector2(cx, cy).lerp(q, 0.8))
			poly(_key, inner, -1.0)
			poly(_spot, inner, 0.5)
			for k in 5:
				var a := rot + k * TAU / 5.0
				bolt(_key, cx, cy, cx + cos(a) * 0.46, cy + sin(a) * 0.46, 3, 0.04, 0.022, 1.0, 100 + k * 10)
			burst(_spot, cx, cy, 0.06, 0.2, 9, 1.0)
		&"damage":
			disc(_key, cx + 0.25, cy + 0.05, 0.2, 1.0)
			disc(_key, cx + 0.25, cy + 0.05, 0.14, -1.0)
			disc(_key, cx + 0.25, cy + 0.05, 0.06, 1.0)
			bolt(_key, cx - 0.55, cy - 0.38, cx + 0.2, cy + 0.02, 4, 0.08, 0.05, 1.0, 120)
			burst(_spot, cx + 0.22, cy + 0.03, 0.1, 0.34, 12, 0.9, rot)
		&"arc":
			var nodes: Array[Vector2] = [Vector2(cx - 0.45, cy + 0.2), Vector2(cx, cy - 0.25), Vector2(cx + 0.45, cy + 0.18)]
			for k in nodes.size():
				disc(_key, nodes[k].x, nodes[k].y, 0.1, 1.0)
				disc(_spot, nodes[k].x, nodes[k].y, 0.2, 0.5)
			for k in nodes.size() - 1:
				bolt(_key, nodes[k].x, nodes[k].y, nodes[k + 1].x, nodes[k + 1].y, 5, 0.05, 0.022, 1.0, 140 + k * 10)
			bolt(_spot, cx - 0.6, cy - 0.4, cx - 0.1, cy - 0.25, 4, 0.05, 0.03, 1.0, 170)
		&"overload":
			rect(_key, cx - 0.2, cy - 0.28, cx + 0.2, cy + 0.36, 1.0)
			rect(_key, cx - 0.14, cy - 0.22, cx + 0.14, cy + 0.3, -1.0)
			rect(_key, cx - 0.07, cy - 0.35, cx + 0.07, cy - 0.28, 1.0)
			rect(_spot, cx - 0.14, cy - 0.22, cx + 0.14, cy + 0.3, 0.9)
			bolt(_key, cx - 0.06, cy - 0.15, cx + 0.04, cy + 0.2, 2, 0.06, 0.04, 1.0, 190)
			burst(_spot, cx, cy - 0.3, 0.12, 0.4, 14, 0.6, rot)
			arrow_arc(_key, cx, cy + 0.05, 0.42, 0.4, 2.6, 0.03, 1.0)
		&"block":
			for row in 4:
				for col in 4:
					var off := 0.08 if row % 2 == 1 else 0.0
					var bx := cx - 0.4 + col * 0.2 + off
					var by := cy - 0.3 + row * 0.16
					if bx > cx + 0.4:
						continue
					rect(_key, bx, by, bx + 0.18, by + 0.14, 1.0)
					rect(_key, bx + 0.02, by + 0.02, bx + 0.16, by + 0.12, -1.0)
					rect(_spot, bx + 0.02, by + 0.02, bx + 0.16, by + 0.12, 0.25 + 0.4 * _p(200 + row * 4 + col))
		&"shield":
			var pts := PackedVector2Array()
			for k in 6:
				pts.append(Vector2(cx, cy) + Vector2(cos(k * TAU / 6.0), sin(k * TAU / 6.0)) * 0.36)
			poly(_key, pts, 1.0)
			var inner := PackedVector2Array()
			for q in pts:
				inner.append(Vector2(cx, cy).lerp(q, 0.84))
			poly(_key, inner, -1.0)
			poly(_spot, inner, 0.6)
			for k in 3:
				var a := k * TAU / 6.0
				line(_key, cx + cos(a) * 0.3, cy + sin(a) * 0.3, cx - cos(a) * 0.3, cy - sin(a) * 0.3, 0.02, 0.9)
			arrow(_spot, cx - 0.7, cy - 0.3, cx - 0.4, cy - 0.12, 0.03, 1.0)
		&"evade":
			for k in 3:
				var ex := cx - 0.3 + k * 0.24
				var t := 0.25 + k * 0.35
				var buf := _key if k == 2 else _spot
				disc(buf, ex, cy - 0.26, 0.08, t)
				poly(buf, PackedVector2Array([Vector2(ex - 0.14, cy - 0.12), Vector2(ex + 0.12, cy - 0.12), Vector2(ex + 0.2, cy + 0.36), Vector2(ex - 0.08, cy + 0.36)]), t)
			arrow(_key, cx - 0.6, cy + 0.1, cx - 0.25, cy + 0.1, 0.025, 1.0)
		&"heal":
			rect_rot(_key, cx, cy, 0.62, 0.3, -0.5 + rot * 0.2, 1.0)
			rect_rot(_key, cx, cy, 0.56, 0.24, -0.5 + rot * 0.2, -1.0)
			rect_rot(_spot, cx, cy, 0.56, 0.24, -0.5 + rot * 0.2, 0.4)
			rect(_key, cx - 0.04, cy - 0.14, cx + 0.04, cy + 0.14, 1.0)
			rect(_key, cx - 0.14, cy - 0.04, cx + 0.14, cy + 0.04, 1.0)
			for k in 3:
				var px := cx + 0.35 + k * 0.1
				var py := cy - 0.3 + _j(210 + k, 0.1)
				rect(_spot, px - 0.012, py - 0.04, px + 0.012, py + 0.04, 1.0)
				rect(_spot, px - 0.04, py - 0.012, px + 0.04, py + 0.012, 1.0)
		&"cleanse":
			rect_rot(_spot, cx - 0.05, cy + 0.14, 0.7, 0.14, -0.2, 0.8)
			rect(_key, cx + 0.2, cy - 0.36, cx + 0.38, cy - 0.05, 1.0)
			rect(_key, cx + 0.16, cy - 0.42, cx + 0.3, cy - 0.36, 1.0)
			line(_key, cx + 0.16, cy - 0.4, cx + 0.06, cy - 0.44, 0.03, 1.0)
			for k in 6:
				disc(_key, cx - 0.05 - k * 0.08, cy - 0.34 + k * 0.035 + _j(220 + k, 0.03), 0.018 + 0.006 * (k % 2), 1.0)
		&"corrupt":
			for k in 9:
				var by := 0.1 + k * 0.09
				var bx := 0.15 + _p(230 + k) * 0.7
				rect(_key if k % 3 == 0 else _spot, bx, by, bx + 0.2 + _p(240 + k) * 0.5, by + 0.05, 1.0 if k % 3 == 0 else 0.8)
			disc(_key, cx, cy - 0.04, 0.16, 1.0)
			disc(_key, cx - 0.06, cy - 0.06, 0.04, -1.0)
			disc(_key, cx + 0.06, cy - 0.06, 0.04, -1.0)
			rect(_key, cx - 0.08, cy + 0.1, cx + 0.08, cy + 0.2, 1.0)
		&"overclock":
			chip(cx, cy + 0.1, 0.36)
			for k in 3:
				var hx := cx - 0.12 + k * 0.12
				var pts := PackedVector2Array()
				for q in 6:
					pts.append(Vector2(hx + (0.03 if q % 2 == 0 else -0.03), cy - 0.16 - q * 0.05))
				path(_spot, pts, 0.025, 1.0)
		&"encrypt":
			for k in 7:
				for q in 5:
					if _p(250 + k * 5 + q) > 0.45:
						rect(_spot, 0.1 + k * 0.19, 0.1 + q * 0.18, 0.2 + k * 0.19, 0.2 + q * 0.18, 0.5)
			lock(cx, cy + 0.02, 0.36)
		&"parasite":
			ring(_spot, cx, cy + 0.1, 0.3, 0.2, 0.55, -2.4, -0.7)
			var pts := PackedVector2Array()
			for k in 12:
				var t := float(k) / 11.0
				pts.append(Vector2(cx - 0.45 + t * 0.9, cy + sin(t * TAU * 1.5 + rot) * 0.12))
			path(_key, pts, 0.07, 1.0)
			disc(_key, pts[pts.size() - 1].x, pts[pts.size() - 1].y, 0.07, 1.0)
			disc(_key, pts[pts.size() - 1].x + 0.02, pts[pts.size() - 1].y - 0.02, 0.018, -1.0)
		&"ram":
			rect(_key, cx - 0.5, cy - 0.12, cx + 0.5, cy + 0.14, 1.0)
			rect(_key, cx - 0.46, cy - 0.08, cx + 0.46, cy + 0.1, -1.0)
			for k in 4:
				rect(_spot, cx - 0.42 + k * 0.22, cy - 0.06, cx - 0.26 + k * 0.22, cy + 0.08, 0.9)
			for k in 12:
				rect(_key, cx - 0.44 + k * 0.078, cy + 0.14, cx - 0.41 + k * 0.078, cy + 0.2, 1.0)
			arrow(_key, cx, cy - 0.44, cx, cy - 0.18, 0.035, 1.0)
		&"drain":
			rect(_key, cx - 0.5, cy - 0.2, cx + 0.5, cy + 0.06, 1.0)
			rect(_key, cx - 0.46, cy - 0.16, cx + 0.46, cy + 0.02, -1.0)
			for k in 4:
				rect(_spot, cx - 0.42 + k * 0.22, cy - 0.14, cx - 0.26 + k * 0.22, cy, 0.9 - k * 0.2)
			disc(_spot, cx + 0.1, cy + 0.28, 0.06, 1.0)
			poly(_spot, PackedVector2Array([Vector2(cx + 0.05, cy + 0.26), Vector2(cx + 0.1, cy + 0.12), Vector2(cx + 0.15, cy + 0.26)]), 1.0)
			line(_key, cx + 0.1, cy + 0.06, cx + 0.1, cy + 0.14, 0.02, 1.0)
		&"draw":
			for k in 3:
				card_shape(cx - 0.2 + k * 0.2, cy + 0.05 - (0.04 if k == 1 else 0.0), 0.24, -0.35 + k * 0.35, 0.2 + k * 0.25)
			arrow(_key, cx + 0.45, cy + 0.3, cx + 0.45, cy - 0.3, 0.03, 1.0)
		&"drone":
			rect(_key, cx - 0.14, cy - 0.06, cx + 0.14, cy + 0.08, 1.0)
			for side: Vector2 in [Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1), Vector2(1, 1)]:
				var rc := Vector2(cx, cy) + side * Vector2(0.28, 0.2)
				line(_key, cx, cy, rc.x, rc.y, 0.03, 1.0)
				ring(_key, rc.x, rc.y, 0.1, 0.02, 1.0)
				disc(_spot, rc.x, rc.y, 0.1, 0.5)
			disc(_spot, cx, cy + 0.02, 0.05, 1.0)
		&"calibrate":
			for k in 13:
				var tx := cx - 0.48 + k * 0.08
				line(_key, tx, cy + 0.2, tx, cy + 0.2 - (0.14 if k % 4 == 0 else 0.07), 0.018, 1.0)
			line(_key, cx - 0.5, cy + 0.2, cx + 0.5, cy + 0.2, 0.025, 1.0)
			poly(_spot, PackedVector2Array([Vector2(cx + _j(260, 0.2), cy + 0.02), Vector2(cx - 0.06 + _j(260, 0.2), cy - 0.14), Vector2(cx + 0.06 + _j(260, 0.2), cy - 0.14)]), 1.0)
			rect_rot(_key, cx + 0.15, cy - 0.28, 0.5, 0.06, -0.3, 1.0)
			ring(_key, cx + 0.38, cy - 0.35, 0.07, 0.035, 1.0, -2.2, 2.2)
		&"ring_lock":
			ring(_key, cx - 0.1, cy, 0.3, 0.06, 1.0)
			ring(_spot, cx - 0.1, cy, 0.3, 0.14, 0.4)
			for k in 3:
				rect_rot(_key, cx + 0.22 + k * 0.1, cy + 0.02 + (0.02 if k % 2 == 0 else -0.02), 0.12, 0.07, 0.4 * (1 if k % 2 == 0 else -1), 1.0)
				rect_rot(_key, cx + 0.22 + k * 0.1, cy + 0.02 + (0.02 if k % 2 == 0 else -0.02), 0.07, 0.025, 0.4 * (1 if k % 2 == 0 else -1), -1.0)
			lock(cx + 0.5, cy + 0.1, 0.22)
		&"steady":
			ring(_key, cx, cy, 0.3, 0.03, 1.0)
			ring(_key, cx, cy, 0.12, 0.02, 1.0)
			line(_key, cx - 0.42, cy, cx + 0.42, cy, 0.02, 1.0)
			line(_key, cx, cy - 0.42, cx, cy + 0.42, 0.02, 1.0)
			disc(_spot, cx, cy, 0.1, 1.0)
			rect(_key, cx - 0.4, cy + 0.34, cx + 0.4, cy + 0.44, 1.0)
			disc(_spot, cx + _j(270, 0.05), cy + 0.39, 0.035, 1.0)
		&"undock":
			ring(_key, cx - 0.15, cy + 0.05, 0.22, 0.04, 1.0)
			disc(_key, cx - 0.15, cy + 0.05, 0.08, 1.0)
			ring(_spot, cx - 0.15, cy + 0.05, 0.38, 0.012, 1.0)
			disc(_key, cx + 0.2, cy - 0.26, 0.07, 1.0)
			rect_rot(_key, cx + 0.2, cy - 0.26, 0.26, 0.05, 0.6, 1.0)
			arrow_arc(_key, cx - 0.15, cy + 0.05, 0.46, -0.4, 0.9, 0.03, 1.0)
		&"amplify":
			for k in 3:
				var ax := cx - 0.36 + k * 0.24
				head(_key if k == 2 else _spot, Vector2(ax + 0.14, cy), Vector2(1, 0), 0.34, 1.0 if k == 2 else 0.4 + k * 0.25)
			ring(_key, cx, cy, 0.42, 0.02, 0.7, -0.6, 0.6)
			ring(_key, cx, cy, 0.46, 0.02, 0.7, -0.5, 0.5)
		_:
			chip(cx, cy, 0.42)
	# Unique art (rares, class cards): an extra seeded accent across the composition.
	if _unique:
		for k in 3:
			disc(_spot, 0.15 + _p(300 + k) * 1.2, 0.1 + _p(310 + k) * 0.8, 0.02 + _p(320 + k) * 0.05, 1.0)
