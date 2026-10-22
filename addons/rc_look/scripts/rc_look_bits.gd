class_name RcLookBits
extends RefCounted
## LOOK-TOOLBOX module 16: binary bits. The shader side is rc_bits.gdshaderinc; this is the exact GDScript mirror of
## BitsPath (plan, control point, Bezier, ease, flight time, flip phase, spin, arrivals) plus the presets
## (config/look_bits.tres: today: "wheel" the GPU bits round a rim, "free" the same bowed sideways, "seam" the combat
## streams' look, "cpu" the CPU fallback as it is today; ruled by the designer (DIRECTION_REVIEW, 2026-10-22): "burst" and "stream"). Pure: no Node, no Settings, no RNG.
##
## Determinism: every per-bit number comes from `h01`, the same portable integer hash as KitNoise (three ints in,
## 0..1 out), never the game's RNG, a global random call or Godot's built-in hash() (not portable between builds; BitPath still uses
## it). The hash multiplies and shifts in GDScript's 64-bit signed ints, which wrap on overflow, and `>>` is an
## arithmetic shift; a port to another language must wrap at 64 bits and sign-extend the shift to match.

const DEFAULT_PATH := "res://addons/rc_look/config/look_bits.tres"
const REQUIRED: Array[StringName] = [&"wheel", &"free", &"seam", &"cpu", &"burst", &"stream"]
## The hash's primes and shifts (KitNoise), and the 16 bits kept.
const PRIME_A := 73856093
const PRIME_B := 19349663
const PRIME_C := 83492791
const MIX := 1274126177
const SHIFT_A := 13
const SHIFT_B := 16
const MASK := 0xFFFF
## The hash channels (BitsPath): flight, flip phase, spin speed, spin direction.
const CH_FLIGHT := 31
const CH_PHASE := 32
const CH_SPIN := 33
const CH_DIR := 34

static var _cfg: RcLookBitsConfig


## The shipped config, loaded once.
static func default_config() -> RcLookBitsConfig:
	if _cfg == null:
		_cfg = load(DEFAULT_PATH) as RcLookBitsConfig
	return _cfg


## A shipped preset by name (null when unknown).
static func preset(name: StringName) -> RcLookBitsPreset:
	return default_config().presets.get(name) as RcLookBitsPreset


## KitNoise.h01: a hash of up to three integers in 0..1 (64-bit wrap, see the header).
static func h01(a: int, b: int, c: int = 0) -> float:
	var n := (a * PRIME_A) ^ (b * PRIME_B) ^ (c * PRIME_C)
	n = (n ^ (n >> SHIFT_A)) * MIX
	n = n ^ (n >> SHIFT_B)
	return float(n & MASK) / float(MASK)


## The quadratic Bezier control point from `start` to `target` (BitsPath.control_point). With a wheel (rim_radius > 0)
## on the bisector of the start and target directions at rim_control x the radius; a start opposite the target turns
## the bisector a quarter turn. Without a wheel it bows sideways by free_bow of the length.
static func control_point(start: Vector2, target: Vector2, rim_centre: Vector2 = Vector2.ZERO, rim_radius: float = 0.0,
		cfg: RcLookBitsConfig = null) -> Vector2:
	var c := cfg if cfg != null else default_config()
	if rim_radius > 0.0:
		var a := (start - rim_centre).normalized()
		var b := (target - rim_centre).normalized()
		var bis := a + b
		if bis.length() < 0.001:
			bis = Vector2(-a.y, a.x)
		return rim_centre + bis.normalized() * c.rim_control * rim_radius
	var mid := (start + target) * 0.5
	var d := target - start
	return mid + Vector2(-d.y, d.x) * c.free_bow


## The point at `t` on the Bezier start -> ctrl -> target, as rcl_bits_at.
static func at(start: Vector2, ctrl: Vector2, target: Vector2, t: float) -> Vector2:
	var u := 1.0 - t
	return start * (u * u) + ctrl * (2.0 * u * t) + target * (t * t)


## The eased share of the path at time share `t` (slow, then sucked in), as rcl_bits_eased.
static func eased(t: float, cfg: RcLookBitsConfig = null) -> float:
	var c := cfg if cfg != null else default_config()
	t = clampf(t, 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t) * c.ease_smooth + t * t * c.ease_quad


## The spawn delay of a bit `x_share` (0 left .. 1 right) across its source, `spread` seconds from first to last.
static func spawn_delay(x_share: float, spread: float) -> float:
	return clampf(x_share, 0.0, 1.0) * spread


## Bit `i`'s flight time for burst seed `seed` around `flight` seconds.
static func flight_time(i: int, seed: int, flight: float, cfg: RcLookBitsConfig = null) -> float:
	var c := cfg if cfg != null else default_config()
	return flight * (1.0 + (h01(seed, i, CH_FLIGHT) * 2.0 - 1.0) * c.flight_spread)


## Bit `i`'s flip phase (0..1).
static func flip_phase(i: int, seed: int) -> float:
	return h01(seed, i, CH_PHASE)


## Bit `i`'s tumble speed (rad/s, either way).
static func spin(i: int, seed: int, cfg: RcLookBitsConfig = null) -> float:
	var c := cfg if cfg != null else default_config()
	var s := lerpf(c.spin_min, c.spin_max, h01(seed, i, CH_SPIN))
	return s if h01(seed, i, CH_DIR) > 0.5 else -s


## The tumble angle at `clock` s, as rcl_bits_spin_turn: speed x clock, plus the flip phase x `turn` when `phase_on`
## (the GPU shader; the CPU fallback leaves the phase out today).
static func spin_angle(clock: float, speed: float, phase: float, turn: float, phase_on: bool = true) -> float:
	return clock * speed + (phase * turn if phase_on else 0.0)


## The atlas frame (0 or 1) a bit shows at `age` s, as rcl_bits_flip before its (+ 0.5) / frames.
static func flip_frame(age: float, flip_s: float, phase: float, cfg: RcLookBitsConfig = null) -> int:
	var c := cfg if cfg != null else default_config()
	return int(floor(maxf(age, 0.0) / flip_s + phase * c.flip_spread)) % 2


## The frame channel the shader writes, as rcl_bits_flip.
static func flip_channel(age: float, flip_s: float, phase: float, frames: int, cfg: RcLookBitsConfig = null) -> float:
	return (float(flip_frame(age, flip_s, phase, cfg)) + 0.5) / float(frames)


## A bit's size share at time share `t`, as rcl_bits_scale (1 at the start, end_scale at the end).
static func scale_at(t: float, cfg: RcLookBitsConfig = null) -> float:
	var c := cfg if cfg != null else default_config()
	return lerpf(1.0, c.end_scale, t)


## A bit's colour `age` s into its flight: `hot_col` for the first `hot_s`, then `col`, as rcl_bits_color.
static func bit_color(hot_col: Color, col: Color, age: float, hot_s: float) -> Color:
	var k := clampf(age / maxf(hot_s, 0.001), 0.0, 1.0)
	return Color(lerpf(hot_col.r, col.r, k), lerpf(hot_col.g, col.g, k), lerpf(hot_col.b, col.b, k))


## Every bit's plan: [{start, ctrl, delay, flight, arrive, phase, spin}] for `starts` flying to `target` (with the
## wheel's centre and radius when it goes round a rim), exactly BitsPath.plan.
static func plan(starts: PackedVector2Array, target: Vector2, flight: float, spread: float, seed: int,
		rim_centre: Vector2 = Vector2.ZERO, rim_radius: float = 0.0, cfg: RcLookBitsConfig = null) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if starts.is_empty():
		return out
	var x0 := INF
	var x1 := -INF
	for p in starts:
		x0 = minf(x0, p.x)
		x1 = maxf(x1, p.x)
	for i in starts.size():
		var p := starts[i]
		var share := (p.x - x0) / (x1 - x0) if x1 > x0 else 0.0
		var delay := spawn_delay(share, spread)
		var fl := flight_time(i, seed, flight, cfg)
		out.append({"start": p, "ctrl": control_point(p, target, rim_centre, rim_radius, cfg), "delay": delay,
			"flight": fl, "arrive": delay + fl, "phase": flip_phase(i, seed), "spin": spin(i, seed, cfg)})
	return out


## The arrival times of a plan, sorted (the view schedules on these). With effects off (`live` false: reduce effects,
## headless, the entry switched off) no bit flies and every arrival is 0, the end state at once.
static func arrivals(p: Array[Dictionary], live: bool = true) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	for b in p:
		out.append(float(b["arrive"]) if live else 0.0)
	out.sort()
	return out
