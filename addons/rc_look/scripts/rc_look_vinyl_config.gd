class_name RcLookVinylConfig
extends Resource
## LOOK-TOOLBOX module 13 (vinyl sticker look): every number of the look in one resource
## (addons/rc_look/config/look_vinyl.tres). The "Shader" groups mirror, by name, the `const RCV_*` of
## shaders/rc_vinyl.gdshaderinc (a test keeps the two equal); the "Builder" groups are the numbers VinylSticker,
## VerbSticker and StickerSeam set from code; "presets" are the stocks and verb colours.

const DEFAULT_PATH := "res://addons/rc_look/config/look_vinyl.tres"

## Preset id -> RcLookVinylPreset.
@export var presets: Dictionary = {}
@export_group("Shader: rim and cut line")
@export var rim_offset: float = 2.0
@export var rim_kraft_share: float = 0.35
@export var rim_light_k: float = 0.85
@export var rim_shade_color: Vector3 = Vector3(0.157, 0.141, 0.173)
@export var rim_shade_k: float = 0.45
@export var cut_color: Vector3 = Vector3(0.133, 0.118, 0.149)
@export var cut_k: float = 0.7
@export var cut_step: float = 1.0
@export_group("Shader: gloss")
@export var soft_w_kraft: float = 0.25
@export var soft_w_glossy: float = 0.13
@export var soft_k_kraft: float = 0.10
@export var soft_k_glossy: float = 0.30
@export var sharp_off: float = 0.05
@export var sharp_w: float = 0.016
@export var sharp_k: float = 0.65
@export var sharp2_off: float = 0.085
@export var sharp2_w: float = 0.007
@export var sharp2_k: float = 0.45
@export var gloss_warm: Vector3 = Vector3(1.0, 0.96, 0.88)
@export_group("Shader: the holographic band")
@export var foil_tau: float = 6.28318
@export var foil_phase: Vector3 = Vector3(0.0, 0.33, 0.67)
@export var foil_dd: float = 0.7
@export var foil_pow: float = 0.55
@export var foil_gain: float = 1.3
@export var band_mix: float = 1.6
@export var band_add: float = 0.25
@export var diag: float = 0.70710678
@export_group("Shader: peel  fold and the flap")
@export var back_shade: float = 0.27
@export var back_shade_pow: float = 1.3
@export var crease_k: float = 0.67
@export var crease_w: float = 0.10
@export var peel_light: float = 0.35
@export var flap_edge_off: float = 1.2
@export var flap_edge_color: Vector3 = Vector3(0.275, 0.259, 0.282)
@export var flap_edge_k: float = 0.5
@export var flap_shadow_off: Vector2 = Vector2(2.0, 3.0)
@export var flap_shadow_reach: float = 8.0
@export var flap_shadow_k: float = 0.4
@export_group("Shader: dissolve")
@export var dissolve_hash: Vector2 = Vector2(41.3, 289.1)
@export var dissolve_x: float = 0.7
@export var dissolve_h: float = 0.3
@export var dissolve_over: float = 1.15
@export var dissolve_edge: float = 0.08
@export var dissolve_white: float = 0.9
@export_group("Shader: grey")
@export var grey_luma: Vector3 = Vector3(0.299, 0.587, 0.114)
@export_group("Shader: drop shadow")
@export var blur_golden: float = 2.39996
@export var shadow_off: Vector2 = Vector2(6.0, 10.0)
@export var shadow_off_lift: Vector2 = Vector2(26.0, 34.0)
@export var shadow_r: float = 10.0
@export var shadow_r_lift: float = 22.0
@export var shadow_k: float = 0.38
@export var shadow_k_lift: float = 0.4
@export var contact_off: Vector2 = Vector2(2.0, 3.0)
@export var contact_r: float = 2.0
@export var contact_k: float = 0.55
@export var contact_lift_max: float = 0.5
@export var contact_lift_fall: float = 2.0
@export_group("Shader: chrome markers and fills")
@export var marker_min: float = 0.02
@export var marker_off: float = 0.01
@export var marker_eq: float = 0.02
@export var glitch_bands: float = 8.0
@export var fill_gloss_end: float = 0.42
@export var sweep_white_k: float = 0.6
@export var sweep_slant: float = 0.45
@export var scan_line_px: float = 1.0
@export_group("Shader: holo foil fill")
@export var holo_tau: float = 6.28
@export var holo_uv: Vector2 = Vector2(0.85, 0.55)
@export var holo_warp1: float = 0.10
@export var holo_warp1_f: Vector2 = Vector2(7.0, 0.0)
@export var holo_warp2: float = 0.08
@export var holo_warp2_f: Vector2 = Vector2(6.0, 3.0)
@export var holo_val: float = 0.93
@export var holo_val_amp: float = 0.07
@export var holo_val_f: float = 9.0
@export var holo_silver: float = 0.78
@export var holo_silver_add: Vector3 = Vector3(0.20, 0.20, 0.22)
@export var holo_line_px: float = 5.0
@export var holo_line_slant: float = 0.6
@export var holo_line_step: float = 0.82
@export var holo_line_k: float = 0.18
@export var holo_spark_cell: float = 9.0
@export var holo_spark_salt: Vector2 = Vector2(3.1, 7.7)
@export var holo_spark_step: float = 0.86
@export var holo_spark_edge: Vector2 = Vector2(1.6, 0.4)
@export var holo_spark_k: float = 0.8
@export_group("Shader: card standin")
@export var card_scan_k: float = 0.85
@export_group("Builder: kit sticker")
## VinylSticker's rest state: the gloss at rest, where it sits, its angle, the rim, the sweep band's angle, width share
## and strength, the default peel leg (px), the dissolve cell (px), the holo drift (hue cycles per second), its saturation.
@export var gloss_rest: float = 0.22
@export var gloss_pos_rest: float = 0.32
@export var gloss_angle_deg: float = 28.0
@export var rim_rest: float = 0.8
@export var band_deg: float = 45.0
@export var band_width: float = 0.22
@export var band_alpha: float = 0.55
@export var peel_px: float = 34.0
@export var dissolve_cell: float = 4.0
@export var holo_drift: float = 0.04
@export var holo_sat: float = 0.55
## Disabled, both families (DIRECTION_REVIEW 82c92714): 80 % grey and alpha 0.8. The legacy_ values are what the old kit
## (full grey) and the old chrome (alpha 1) draw, for the old | new lab rows.
@export var disabled_grey: float = 0.8
@export var disabled_alpha: float = 0.8
@export var legacy_kit_disabled_grey: float = 1.0
@export var legacy_chrome_disabled_alpha: float = 1.0
## Geometry of the die-cut (the shader only reads its alpha): the object border, the word edge share and its cap (px),
## the keyline, the extrude, the extrude's slant, the shadow padding.
@export var border_px: float = 18.0
@export var edge_share: float = 0.14
@export var edge_max_px: float = 8.0
@export var keyline_px: float = 5.0
@export var extrude_px: float = 8.0
@export var extrude_slant: float = 0.55
@export var shadow_pad: float = 56.0
## The peel leg: the largest leg as a share of the body width, and the 1080p board it is measured on.
@export var peel_max_share: float = 0.18
@export var peel_board_h: float = 1080.0
@export_group("Builder: chrome verb sticker")
## VerbSticker's draw: die-cut, keyline and extrude as shares of the font size, the shadow share and alpha, the rim
## (px), the glitch split share, the scan period as a share of the font size (it has a
## floor, px; the sweep width has one source, run_sweep: band_width of the word's width, halved), the rest gloss, and the curl's back lighten and shadow (px).
@export var verb_die_cut: float = 0.17
@export var verb_keyline: float = 0.075
@export var verb_extrude: float = 0.1
@export var verb_shadow_share: float = 0.07
@export var verb_shadow_alpha: float = 0.55
@export var verb_rim_px: float = 2.0
@export var verb_split_share: float = 0.045
@export var verb_scan_period_share: float = 0.12
@export var verb_scan_period_min: float = 3.0
@export var verb_gloss: float = 0.22
@export var verb_curl_back_lighten: float = 0.35
@export var verb_curl_shadow_px: float = 3.0
@export_group("Builder: card stand-in")
## card_sticker_fx's never-set defaults: the scan line width, the die-cut edge share, the gloss band's width and alpha.
@export var card_scan_band: float = 0.04
@export var card_edge_share: float = 0.1
@export var card_gloss_width: float = 0.18
@export var card_gloss_alpha: float = 0.55
@export_group("Tokens")
## The sticker colours (palette.gd): die-cut, ink keyline (chrome extrude), kit extrude and shadow, the adhesive back,
## the two glitch scan colours.
@export var die_cut: Color = Color.WHITE
@export var vinyl_ink: Color = Color.BLACK
@export var vinyl_extrude: Color = Color.BLACK
@export var vinyl_backing: Color = Color.WHITE
@export var glitch_a: Color = Color.WHITE
@export var glitch_b: Color = Color.WHITE
@export_group("Lab")
## Fixed lab poses: the peel fold (share), the focus peel-back, the dissolve share, the hover lift, the band position,
## the slap gloss position and strength, the lifted corner; and the stand-in art (body size, corner radius, padding).
@export var lab_fold: float = 0.6
@export var lab_peel_back: float = 1.0
@export var lab_dissolve: float = 0.5
@export var lab_lift: float = 0.6
@export var lab_band_t: float = 0.5
@export var lab_gloss_pos: float = 0.5
@export var lab_gloss_k: float = 1.0
@export var lab_corner: int = 1
@export var lab_body: Vector2 = Vector2(260.0, 96.0)
@export var lab_radius: float = 22.0
@export var lab_pad: float = 56.0


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in RcLookVinyl.REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookVinylPreset:
			errs.append("%s is not an RcLookVinylPreset" % n)
			continue
		for e in (presets[n] as RcLookVinylPreset).validate():
			errs.append("%s: %s" % [n, e])
	for n: String in ["blur_golden", "soft_w_kraft", "soft_w_glossy", "sharp_w", "sharp2_w", "dissolve_over", "holo_line_px",
			"holo_spark_cell", "peel_board_h", "dissolve_cell"]:
		if float(get(n)) <= 0.0:
			errs.append("%s must be above 0 (%s)" % [n, get(n)])
	if gloss_rest < 0.0 or gloss_rest > 1.0:
		errs.append("gloss_rest must be 0..1 (%s)" % gloss_rest)
	for n: String in ["disabled_grey", "disabled_alpha", "legacy_kit_disabled_grey", "legacy_chrome_disabled_alpha"]:
		if float(get(n)) < 0.0 or float(get(n)) > 1.0:
			errs.append("%s must be 0..1 (%s)" % [n, get(n)])
	if band_width <= 0.0 or band_width > 1.0:
		errs.append("band_width must be in (0, 1] (%s)" % band_width)
	if peel_max_share <= 0.0 or peel_max_share >= 1.0:
		errs.append("peel_max_share must be in (0, 1) (%s)" % peel_max_share)
	if lab_corner < 0 or lab_corner > 3:
		errs.append("lab_corner must be 0..3 (%s)" % lab_corner)
	return errs
