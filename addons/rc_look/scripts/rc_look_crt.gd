class_name RcLookCrt
extends RefCounted
## LOOK-TOOLBOX module 14: the CRT / terminal glass. The shader side is rc_crt.gdshaderinc; this is its exact GDScript
## mirror plus the presets (config/look_crt.tres: "terminal" the Cell's cyan glass, "firmware", "schematics", "dispatch",
## "corp" the CrtTerminalPanel accents; "ui_panel" crt_panel; "fx_overlay" scanline.gdshader as Fx sets it; "neon_sketch"
## the city's scan). Pure: no Node, no Settings. Lab only: no call site is migrated.

const DEFAULT_PATH := "res://addons/rc_look/config/look_crt.tres"
const REQUIRED: Array[StringName] = [&"terminal", &"firmware", &"schematics", &"dispatch", &"corp", &"ui_panel",
		&"fx_overlay", &"neon_sketch"]
## What reduce effects does: KEEP_STATIC the static scanlines (and the screen vignette) stay, only motion stops (rc_live's
## way); ZERO_SCAN the scanlines go too, as a script zeroes them (ui_theme, neon_city); HIDE the whole overlay is hidden
## (fx.gd's scanline layer). Flicker and the roll stop in all three.
enum Reduce { KEEP_STATIC, ZERO_SCAN, HIDE }
## The glow's falloff length as a share of its reach, and its floor (px): crt_terminal.gdshader's.
const GLOW_REACH := 0.42
const GLOW_MIN_PX := 0.5
## scanline.gdshader's pi.
const SINE_PI := 3.14159

static var _cfg: RcLookCrtConfig


## The shipped presets, loaded once.
static func default_config() -> RcLookCrtConfig:
	if _cfg == null:
		_cfg = load(DEFAULT_PATH) as RcLookCrtConfig
	return _cfg


## A shipped preset by name (null when unknown).
static func preset(name: StringName) -> RcLookCrtPreset:
	return default_config().presets.get(name) as RcLookCrtPreset


## Scanline mask (1 on the dark line), as rcl_crt_scan.
static func scan(y_px: float, period_px: float, phase: float) -> float:
	return 1.0 if fposmod(y_px / period_px - phase, 1.0) >= 0.5 else 0.0


## The sine scanlines, as rcl_crt_scan_sine.
static func scan_sine(y01: float, density: float) -> float:
	return 0.5 + 0.5 * sin(y01 * density * SINE_PI)


## The flicker gain, as rcl_crt_flicker.
static func flicker(t: float, rate_rad_s: float, amount: float) -> float:
	return 1.0 - amount * (0.5 + 0.5 * sin(t * rate_rad_s))


## The rolling band's profile, as rcl_crt_roll.
static func roll(y01: float, band: float, width: float) -> float:
	return exp(-pow((y01 - band) / width, 2.0))


## The glass's inner vignette gain, as rcl_crt_vignette_sd.
static func vignette_sd(sd: float, reach_px: float, floor_gain: float) -> float:
	return lerpf(floor_gain, 1.0, smoothstep(0.0, reach_px, -sd))


## The screen vignette gain, as rcl_crt_vignette_uv.
static func vignette_uv(uv: Vector2, amount: float, inner: float, outer: float) -> float:
	return 1.0 - amount * smoothstep(inner, outer, uv.distance_to(Vector2(0.5, 0.5)))


## The outer glow's alpha, as rcl_crt_glow.
static func glow(sd: float, glow_px: float, strength: float) -> float:
	return exp(-sd / maxf(glow_px * GLOW_REACH, GLOW_MIN_PX)) * strength


## The band's position (0..1) at time t: fract(t / seconds), the shader's `band`.
static func band_at(t: float, seconds: float) -> float:
	return fposmod(t / maxf(seconds, 0.1), 1.0)


## The numbers a screen runs with when reduce effects is `on`, by convention `how` (-1 = the config's): a Dictionary of
## scan_strength, flicker, roll_strength, screen_vignette, hex_alpha and `visible`. Not on: the preset's own numbers.
static func resolve(p: RcLookCrtPreset, on: bool, how: int = -1) -> Dictionary:
	var r := {&"scan_strength": p.scan_strength, &"flicker": p.flicker, &"roll_strength": p.roll_strength,
			&"screen_vignette": p.screen_vignette, &"hex_alpha": p.hex_alpha, &"visible": true}
	if not on:
		return r
	var c := default_config().reduce if how < 0 else how
	r[&"flicker"] = 0.0
	r[&"roll_strength"] = 0.0
	if c == Reduce.ZERO_SCAN or c == Reduce.HIDE:
		r[&"scan_strength"] = 0.0
	if c == Reduce.HIDE:
		r[&"screen_vignette"] = 0.0
		r[&"visible"] = false
	return r
