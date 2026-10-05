class_name HeatGlitchLayer
extends ColorRect
## ART-0 audit B1 (ART_BIBLE v2 §3.15, §5.3, §5.5, Appendix B; round 18-22 heat_glitch): the
## Heat glitch, the Options extra (Settings › Accessibility "Heat glitch", `Settings.heat_glitch`,
## off by default). A screen-wide post glitch over the combat world that grows with the Heat
## band: short periodic bursts (CampaignConfigData.heat_glitch_*), each band adding a layer
## (COOL a luminance dip and line jitter; NOTICED chromatic tears; FLAGGED a scanline roll
## and macroblocks; HUNTED a hold slip, an RGB split and ambient scanlines; PURGE = HUNTED).
## It sits between the backdrop (city + Heat lights) and the wheels, FX and HUD, so every
## value stays readable (the bible's protect mask: wheel discs get <= 35 %; here 0 %).
## - Exempt from VfxTier (Settings.VFX_TIER_EXEMPT): full screen, but it adds no light.
## - Off under reduce effects (and headless): Motion.live(&"heat_glitch").
## - Flash limiter on: no luminance dip and no roll brightening (it changes no light).
## - Off: the static corp edge tint at HUNTED and PURGE only (§5.5), no motion.
## Timing: `heat_glitch` in ui_motion.tres (duration = how long a glitch state holds;
## amplitude = the edge tint's alpha). View only: no state, no RNG (the shader hashes the
## state index).

## The motion entry (kind LOOP; exempt from its tier).
const MOTION := &"heat_glitch"
const SHADER := preload("res://shaders/heat_glitch.gdshader")
const BANDS := 5
## The first band the edge tint, the hold slip and the ambient scanlines show at (HUNTED).
const HUNTED := 3
## Per band, the look a burst adds (round 18 heat_glitch band table; px at 1920 x 1080):
## the tears' sideways slip and RGB split, the roll, the hold slip, the frame's split, the
## ambient scanlines' darkening.
const TEAR_PX: Array[float] = [0.0, 18.0, 26.0, 40.0, 40.0]
const TEAR_SPLIT_PX: Array[float] = [0.0, 4.0, 5.0, 7.0, 7.0]
const ROLL: Array[bool] = [false, false, true, true, true]
const SLIP_PX: Array[float] = [0.0, 0.0, 0.0, 14.0, 14.0]
const SPLIT_PX: Array[float] = [0.0, 0.0, 0.0, 6.0, 6.0]
const SCAN: Array[float] = [0.0, 0.0, 0.0, 0.07, 0.07]
## COOL's luminance dip at the burst's peak and the roll band's brightening (both skipped
## under the flash limiter).
const DIP := 0.07
const ROLL_GAIN := 0.22
## The envelope rises over this share of the burst's first part (up fast, out).
const ENV_RISE := 1.15
## Glitch states per period: the seed's stride between periods.
const SEED_STRIDE := 1000.0

## The band shown (0 COOL .. 4 PURGE).
var band: int = 0
## The corporation's colour for the edge tint and the blocks.
var corp_color: Color = Palette.HEAT_B
## The motion lab shows the glitch without touching the player's Settings.
var force_on: bool = false
var _t: float = 0.0
var _mat: ShaderMaterial


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	material = _mat
	color = Palette.NO_TINT
	visible = false
	set_process(false)


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	if not Settings.changed.is_connected(refresh):
		Settings.changed.connect(refresh)
	refresh()


## Shows Heat band `p_band` (0 COOL .. 4 PURGE) with `p_corp` as the corporation's colour.
func set_band(p_band: int, p_corp: Color = Palette.HEAT_B) -> void:
	band = clampi(p_band, 0, BANDS - 1)
	corp_color = p_corp
	refresh()


## Whether the glitch animates now: the option on (or the lab's force) and motion live
## (not under reduce effects, not headless).
func animated() -> bool:
	return (Settings.heat_glitch or force_on) and Motion.live(MOTION)


## The look of band `b` (pure numbers): `glitch_on` the option, `live` motion allowed,
## `limiter` the flash limiter. {animated, period, burst, tears, blocks, tear_px,
## tear_split_px, roll, roll_gain, dip, slip_px, split_px, scan, edge}.
static func look(b: int, glitch_on: bool, live: bool, limiter: bool, cfg: CampaignConfigData = null) -> Dictionary:
	var c := cfg if cfg != null else RunManager.config()
	var i := clampi(b, 0, BANDS - 1)
	var on := glitch_on and live
	return {
		"animated": on,
		"period": c.heat_glitch_period[i], "burst": c.heat_glitch_burst[i],
		"tears": c.heat_glitch_tears[i] if on else 0, "blocks": c.heat_glitch_blocks[i] if on else 0,
		"tear_px": TEAR_PX[i] if on else 0.0, "tear_split_px": TEAR_SPLIT_PX[i] if on else 0.0,
		"roll": ROLL[i] and on, "roll_gain": 0.0 if limiter else ROLL_GAIN,
		"dip": 0.0 if (limiter or not on) else DIP,
		"slip_px": SLIP_PX[i] if on else 0.0, "split_px": SPLIT_PX[i] if on else 0.0,
		"scan": SCAN[i] if on else 0.0,
		"edge": Motion.amplitude(MOTION) if i >= HUNTED else 0.0,
	}


## The burst at `t` seconds into the loop: {env (0 between bursts), q (0..1 across the
## burst), seed (the glitch state)}; a state holds `step` seconds.
static func burst_at(t: float, period: float, burst: float, step: float) -> Dictionary:
	var age := fposmod(t, period)
	var cycle := floorf(t / period)
	if age > burst or burst <= 0.0:
		return {"env": 0.0, "q": 0.0, "seed": cycle * SEED_STRIDE}
	var st := maxf(step, 0.001)
	var held := (floorf(age / st) + 0.5) * st  # a state shows the middle of its step
	var q := clampf(held / burst, 0.0, 1.0)
	return {"env": sin(PI * minf(1.0, q * ENV_RISE)), "q": q, "seed": cycle * SEED_STRIDE + floorf(age / st)}


## Re-reads the Settings and the band: shows the layer when it animates or tints.
func refresh() -> void:
	var lk := look(band, Settings.heat_glitch or force_on, Motion.live(MOTION), Settings.flash_limiter)
	for k in ["tears", "blocks", "tear_px", "tear_split_px", "roll_gain", "dip", "slip_px", "split_px", "scan", "edge"]:
		_mat.set_shader_parameter(k, float(lk[k]))
	_mat.set_shader_parameter("roll", 1.0 if bool(lk["roll"]) else 0.0)
	_mat.set_shader_parameter("edge_color", corp_color)
	_mat.set_shader_parameter("block_color", corp_color)
	_mat.set_shader_parameter("env", 0.0)
	var on := bool(lk["animated"])
	visible = on or float(lk["edge"]) > 0.0
	set_process(on)


func _process(delta: float) -> void:
	var lk := look(band, true, true, Settings.flash_limiter)
	_t += delta
	var b := burst_at(_t, float(lk["period"]), float(lk["burst"]), Motion.seconds(MOTION))
	_mat.set_shader_parameter("env", float(b["env"]))
	_mat.set_shader_parameter("q", float(b["q"]))
	_mat.set_shader_parameter("seed", float(b["seed"]))
