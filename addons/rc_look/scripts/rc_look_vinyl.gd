class_name RcLookVinyl
extends RefCounted
## LOOK-TOOLBOX module 13: the vinyl sticker look. Static GDScript mirrors of shaders/rc_vinyl.gdshaderinc (the kit
## sticker's rim, gloss, holographic band, fold, flap, dissolve, grey and shadow; the chrome verb sticker's markers,
## fills, glitch bands and band; the holo foil fill; the card stand-in), the presets for every stock and verb colour,
## and material builders for the four lab wrappers. Every number comes from look_vinyl.tres. Colours here are
## Vector3 (rgb) so the mirrors stay linear maths. Lab only: no view uses this yet.
##
## The hash-based forms (dissolve cell order, holo sparkles) run on a float32 sin on the GPU; the mirror runs in
## double precision, so it matches the form, not the pixel, for those two. Everything else matches to float noise.

const KIT_SHADER_PATH := "res://addons/rc_look/shaders/rc_vinyl_kit.gdshader"
const CHROME_SHADER_PATH := "res://addons/rc_look/shaders/rc_vinyl_chrome.gdshader"
const FILL_SHADER_PATH := "res://addons/rc_look/shaders/rc_vinyl_fill.gdshader"
const CARD_SHADER_PATH := "res://addons/rc_look/shaders/rc_vinyl_card.gdshader"
## Presets every config must carry: the kit stocks and the chrome verb colours.
const REQUIRED: Array[StringName] = [&"kit_pink", &"kit_red", &"kit_yellow", &"kit_white", &"kit_ink", &"kit_kraft",
	&"kit_holo", &"chrome_pink", &"chrome_yellow", &"chrome_blue", &"chrome_grey", &"chrome_glitch"]
## Dissolve verdict of a pixel.
enum Dissolve { KEEP, WHITE, CUT }
## The fold-frame corner ids of the shader (0 top-left, 1 top-right, 2 bottom-left, 3 bottom-right).
const CORNER_TOP_LEFT := 0
const CORNER_TOP_RIGHT := 1
const CORNER_BOTTOM_LEFT := 2
const CORNER_BOTTOM_RIGHT := 3
## A marker-decoded vertex colour that is neither marker (a plain pixel).
const KIND_NONE := 0
const KIND_MAGENTA := 1
const KIND_GREEN := 2
## The shader's own "no band / no sweep" sentinel: the sweep uniform's off value and its test threshold.
const SWEEP_OFF := -10000.0
const SWEEP_ON_MIN := -1000.0

## The holo stock's field seed in the lab art.
const LAB_HOLO_SEED := 11.0

static var _config: RcLookVinylConfig = null


## The default config (addons/rc_look/config/look_vinyl.tres), loaded once.
static func config() -> RcLookVinylConfig:
	if _config == null:
		_config = load(RcLookVinylConfig.DEFAULT_PATH)
	return _config


## The preset `id` (a REQUIRED name), or null.
static func preset(id: StringName, cfg: RcLookVinylConfig = null) -> RcLookVinylPreset:
	var c := cfg if cfg != null else config()
	return c.presets.get(id)


# ---------------------------------------------------------------------------------------------------------------
# Presets to uniforms
# ---------------------------------------------------------------------------------------------------------------

## The kit shader's uniforms for a kit stock at rest (what VinylSticker._sync sets); `body` is the die-cut body rect
## in the art texture (px). Pure.
static func kit_uniforms(id: StringName, body: Rect2, cfg: RcLookVinylConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	var p := preset(id, c)
	return {
		&"body_rect": Vector4(body.position.x, body.position.y, body.size.x, body.size.y),
		&"gloss_k": p.gloss_k,
		&"gloss_pos": c.gloss_pos_rest,
		&"gloss_angle_deg": c.gloss_angle_deg,
		&"glossy": p.glossy,
		&"rim": p.rim,
		&"corner": c.lab_corner,
		&"backing_color": p.backing_color(),
		&"shadow_color": p.shadow_color,
		&"band_width": c.band_width,
		&"band_alpha": c.band_alpha,
		&"band_deg": c.band_deg,
		&"peel_px": c.peel_px,
		&"dissolve_cell": c.dissolve_cell,
	}


## The chrome shader's uniforms for a verb colour of font size `font_px` on a word `box_w` px wide (what VerbSticker._draw
## and run_sweep set): the fill gradient over [fill_top_px, fill_bottom_px], the scan period as a share of the font size,
## and the sweep's half width from ONE source (run_sweep: band_width of the word's width, halved).
static func chrome_uniforms(id: StringName, font_px: float, fill_top_px: float, fill_bottom_px: float, box_w: float,
		cfg: RcLookVinylConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	var p := preset(id, c)
	return {
		&"top_color": p.fill_top,
		&"bottom_color": p.fill_bottom,
		&"white_color": c.die_cut,
		&"glitch_a": c.glitch_a,
		&"glitch_b": c.glitch_b,
		&"fill_top": fill_top_px,
		&"fill_bottom": fill_bottom_px,
		&"gloss": c.verb_gloss,
		&"sweep_width": c.band_width * box_w * 0.5,
		&"band_deg": c.band_deg,
		&"scan_period": maxf(c.verb_scan_period_min, font_px * c.verb_scan_period_share),
		&"band_h": 0.0,
	}


## The marker colour a chrome preset draws its lettering in.
static func marker_color(id: StringName, cfg: RcLookVinylConfig = null) -> Color:
	var p := preset(id, cfg)
	return Color(0, 1, 0) if p.marker == RcLookVinylPreset.Marker.GREEN else Color(1, 0, 1)


## A kit material over `art` (the baked sticker art) for kit stock `id`; `overrides` replaces uniforms after.
static func kit_material(id: StringName, art: Texture2D, body: Rect2, overrides: Dictionary = {}) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(KIT_SHADER_PATH)
	m.set_shader_parameter(&"art_tex", art)
	var u := kit_uniforms(id, body)
	u.merge(overrides, true)
	for k: StringName in u:
		m.set_shader_parameter(k, u[k])
	return m


## A chrome material for verb colour `id`.
static func chrome_material(id: StringName, font_px: float, fill_top_px: float, fill_bottom_px: float, box_w: float,
		overrides: Dictionary = {}) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(CHROME_SHADER_PATH)
	var u := chrome_uniforms(id, font_px, fill_top_px, fill_bottom_px, box_w)
	u.merge(overrides, true)
	for k: StringName in u:
		m.set_shader_parameter(k, u[k])
	return m


## A fill material (gradient or the holo foil) for kit stock `id` over [band_top, band_bottom] px.
static func fill_material(id: StringName, band_top: float, band_bottom: float, field: Vector2, seed_id: int) -> ShaderMaterial:
	var c := config()
	var p := preset(id)
	var m := ShaderMaterial.new()
	m.shader = load(FILL_SHADER_PATH)
	m.set_shader_parameter(&"mode", 1 if p.holo_face else 0)
	m.set_shader_parameter(&"fill_top", p.fill_top)
	m.set_shader_parameter(&"fill_bottom", p.fill_bottom)
	m.set_shader_parameter(&"band_top", band_top)
	m.set_shader_parameter(&"band_bottom", band_bottom)
	m.set_shader_parameter(&"holo_drift", c.holo_drift if p.holo_face else 0.0)
	m.set_shader_parameter(&"holo_seed", float(seed_id))
	m.set_shader_parameter(&"holo_sat", c.holo_sat)
	m.set_shader_parameter(&"field_size", field)
	return m


## A card stand-in material for a card of `size` px.
static func card_material(size: Vector2) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(CARD_SHADER_PATH)
	m.set_shader_parameter(&"card_size", size)
	return m


# ---------------------------------------------------------------------------------------------------------------
# Fold
# ---------------------------------------------------------------------------------------------------------------

## rcv_fold_frame: {"P": Vector2, "u": Vector2, "depth": float, "on": bool}. peel_back > 0 is the fixed 45 degree fold.
static func fold_frame(body: Rect2, corner: int, fold: float, peel_back: float, peel_px: float,
		cfg: RcLookVinylConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	var c0 := body.position
	var c1 := body.position + body.size
	var corner_pt := Vector2(c1.x if corner == 1 or corner == 3 else c0.x, c1.y if corner >= 2 else c0.y)
	var o := (c0 + c1) * 0.5
	var d := o - corner_pt
	var l := maxf(d.length(), 1.0)
	var u := d / l
	var depth := fold * l
	if peel_back > 0.0:
		u = Vector2(signf(d.x), signf(d.y)) * c.diag
		depth = peel_back * peel_px * c.diag
	return {"P": corner_pt + u * depth, "u": u, "depth": depth, "on": fold > 0.0 or peel_back > 0.0}


## rcv_folded_alpha: the sticker's alpha at px after the fold. `alpha_at` is Callable(Vector2) -> float.
static func folded_alpha(alpha_at: Callable, px: Vector2, fr: Dictionary) -> float:
	if not fr["on"]:
		return alpha_at.call(px)
	var u: Vector2 = fr["u"]
	var s := (px - (fr["P"] as Vector2)).dot(u)
	if s < 0.0:
		return 0.0
	var a: float = alpha_at.call(px)
	if s <= float(fr["depth"]):
		a = maxf(a, alpha_at.call(px - 2.0 * s * u))
	return a


## The signed distance of px behind the fold line (< 0 = the part that was folded away).
static func fold_s(px: Vector2, fr: Dictionary) -> float:
	return (px - (fr["P"] as Vector2)).dot(fr["u"])


## The peel leg (px) of a body `body_w` wide on a `screen_h` tall screen: short bodies (under `short_under` px at
## 1080p) use `short_leg`, long ones `long_leg`; never longer than the wider of the unscaled leg and the max share of the
## body (VinylSticker.peel_leg).
static func peel_leg(body_w: float, screen_h: float, text_scale: float, short_under: float, short_leg: float,
		long_leg: float, cfg: RcLookVinylConfig = null) -> float:
	var c := cfg if cfg != null else config()
	var k := screen_h / c.peel_board_h * text_scale
	var short := body_w / maxf(k, 0.01) < short_under
	var leg := (short_leg if short else long_leg) * k
	var k1 := screen_h / c.peel_board_h
	var leg1 := (short_leg if body_w / maxf(k1, 0.01) < short_under else long_leg) * k1
	return minf(leg, maxf(leg1, body_w * c.peel_max_share))


## VinylSticker.edge_for: a word's die-cut edge (px) for a font size of `px`.
static func edge_for(px: float, text_scale: float, cfg: RcLookVinylConfig = null) -> float:
	var c := cfg if cfg != null else config()
	return minf(px * c.edge_share, c.edge_max_px * maxf(1.0, text_scale))


# ---------------------------------------------------------------------------------------------------------------
# Kit: rim, gloss, band, flap, dissolve, grey, shadow
# ---------------------------------------------------------------------------------------------------------------

## rcv_kit_rim: `alpha_at` is Callable(Vector2) -> float; `a` the alpha at px.
static func kit_rim(rgb: Vector3, a: float, alpha_at: Callable, px: Vector2, rim: float, glossy: float,
		cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var k := rim * lerpf(c.rim_kraft_share, 1.0, glossy)
	var off := Vector2(c.rim_offset, c.rim_offset)
	var tl: float = alpha_at.call(px - off)
	var br: float = alpha_at.call(px + off)
	rgb = rgb.lerp(Vector3.ONE, clampf(a - tl, 0.0, 1.0) * c.rim_light_k * k)
	rgb = rgb.lerp(c.rim_shade_color, clampf(a - br, 0.0, 1.0) * c.rim_shade_k * k)
	var st := c.cut_step
	var m := minf(minf(alpha_at.call(px + Vector2(st, 0.0)), alpha_at.call(px - Vector2(st, 0.0))),
			minf(alpha_at.call(px + Vector2(0.0, st)), alpha_at.call(px - Vector2(0.0, st))))
	return rgb.lerp(c.cut_color, clampf(a - m, 0.0, 1.0) * c.cut_k * glossy)


## rcv_kit_gloss_t: 0..1 along the gloss diagonal.
static func gloss_t(px: Vector2, body: Rect2, angle_deg: float) -> float:
	var ang := deg_to_rad(angle_deg)
	var dir := Vector2(cos(ang), sin(ang))
	var q := (px - body.position) / Vector2(maxf(body.size.x, 1.0), maxf(body.size.y, 1.0))
	var qs := q * body.size
	var p10 := body.size.x * dir.x
	var p01 := body.size.y * dir.y
	var p11 := p10 + p01
	var mn := minf(minf(0.0, p10), minf(p01, p11))
	var mx := maxf(maxf(0.0, p10), maxf(p01, p11))
	return (qs.dot(dir) - mn) / maxf(mx - mn, 1.0)


## rcv_kit_spec: the specular strength at gloss coordinate t.
static func spec(t: float, gloss_k: float, gloss_pos: float, glossy: float, cfg: RcLookVinylConfig = null) -> float:
	var c := cfg if cfg != null else config()
	var soft_w := lerpf(c.soft_w_kraft, c.soft_w_glossy, glossy)
	var soft := exp(-pow((t - gloss_pos) / soft_w, 2.0)) * lerpf(c.soft_k_kraft, c.soft_k_glossy, glossy)
	var sharp := exp(-pow((t - gloss_pos - c.sharp_off) / c.sharp_w, 2.0)) * c.sharp_k * glossy
	var sharp2 := exp(-pow((t - gloss_pos - c.sharp2_off) / c.sharp2_w, 2.0)) * c.sharp2_k * glossy
	return maxf(maxf(soft, sharp), sharp2) * gloss_k


## rcv_kit_gloss: the vinyl colour with the gloss laid on.
static func kit_gloss(rgb: Vector3, px: Vector2, body: Rect2, gloss_k: float, gloss_pos: float, angle_deg: float,
		glossy: float, cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var s := spec(gloss_t(px, body, angle_deg), gloss_k, gloss_pos, glossy, c)
	return rgb.lerp(c.gloss_warm.lerp(Vector3.ONE, glossy), s)


## rcv_foil: the holographic foil colour at band coordinate dd.
static func foil(dd: float, cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var out := Vector3.ZERO
	for i in 3:
		var v := 0.5 + 0.5 * cos(c.foil_tau * (c.foil_phase[i] + dd * c.foil_dd))
		out[i] = clampf(pow(v, c.foil_pow) * c.foil_gain, 0.0, 1.0)
	return out


## rcv_band_w: the band's falloff at dd.
static func band_w(dd: float) -> float:
	return 1.0 - smoothstep(0.0, 1.0, absf(dd))


## rcv_band_mix: the foil laid over base (cover 1.0 on the kit, the glyph alpha on the chrome sticker).
static func band_mix(base: Vector3, foil_rgb: Vector3, w: float, alpha: float, cover: float,
		cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var m := base.lerp(foil_rgb, clampf(w * alpha * c.band_mix, 0.0, 1.0) * cover)
	var add := w * alpha * c.band_add * cover
	return Vector3(clampf(m.x + add, 0.0, 1.0), clampf(m.y + add, 0.0, 1.0), clampf(m.z + add, 0.0, 1.0))


## rcv_kit_band_dd: the band coordinate of px; the band lines run along band_deg's direction rotated 90 degrees
## (kit band at 45 degrees: the lines go "\", the band moves along (-1, 1)).
static func kit_band_dd(px: Vector2, body: Rect2, band_t: float, band_width: float, band_deg: float) -> float:
	var bd := deg_to_rad(band_deg)
	var n := Vector2(-sin(bd), cos(bd))
	var half_w := 0.5 * band_width * body.size.x
	var n0 := body.position.dot(n)
	var n1 := (body.position + Vector2(body.size.x, 0.0)).dot(n)
	var n2 := (body.position + Vector2(0.0, body.size.y)).dot(n)
	var n3 := (body.position + body.size).dot(n)
	var lo := minf(minf(n0, n1), minf(n2, n3)) - half_w
	var hi := maxf(maxf(n0, n1), maxf(n2, n3)) + half_w
	var centre := lerpf(lo, hi, band_t)
	return (px.dot(n) - centre) / maxf(half_w, 1.0)


## rcv_band_centre: the centre of a band at share t across `body` along its axis, half width half_w (the kit's band and,
## since the designer's ruling, the chrome's).
static func band_centre(body: Rect2, t: float, half_w: float, deg: float) -> float:
	var bd := deg_to_rad(deg)
	var n := Vector2(-sin(bd), cos(bd))
	var n0 := body.position.dot(n)
	var n1 := (body.position + Vector2(body.size.x, 0.0)).dot(n)
	var n2 := (body.position + Vector2(0.0, body.size.y)).dot(n)
	var n3 := (body.position + body.size).dot(n)
	return lerpf(minf(minf(n0, n1), minf(n2, n3)) - half_w, maxf(maxf(n0, n1), maxf(n2, n3)) + half_w, t)


## rcv_band_dd_at: the band coordinate of px for a band centred at `centre` along its axis.
static func band_dd_at(px: Vector2, centre: float, half_w: float, deg: float) -> float:
	var bd := deg_to_rad(deg)
	return (px.dot(Vector2(-sin(bd), cos(bd))) - centre) / maxf(half_w, 1.0)


## rcv_chrome_band_dd: the OLD chrome band coordinate (the band lines are x + y = sweep, so they run "/").
static func chrome_band_dd(local: Vector2, sweep: float, sweep_width: float, cfg: RcLookVinylConfig = null) -> float:
	var c := cfg if cfg != null else config()
	return (local.x + local.y - sweep) * c.diag / maxf(sweep_width, 1.0)


## The flap's adhesive back colour at share sf of the fold depth (rcv_kit_flap without the cut-edge tint).
static func flap_back(sf: float, backing: Vector3, peel_back: float, cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var back := backing.lerp(Vector3.ZERO, c.back_shade * pow(sf, c.back_shade_pow))
	back = back.lerp(Vector3.ONE, c.crease_k * exp(-pow(sf / c.crease_w, 2.0)))
	return back.lerp(Vector3.ONE, c.peel_light * peel_back)


## rcv_kit_flap: the flap folded over the sticker, or its cast shadow. Returns {"rgb": Vector3, "a": float}.
static func kit_flap(alpha_at: Callable, px: Vector2, fr: Dictionary, backing: Vector3, peel_back: float, rgb: Vector3,
		a: float, cfg: RcLookVinylConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	var u: Vector2 = fr["u"]
	var depth: float = fr["depth"]
	var s := fold_s(px, fr)
	if fr["on"] and s >= 0.0 and s <= depth:
		var fa: float = alpha_at.call(px - 2.0 * s * u)
		if fa > 0.0:
			var back := flap_back(s / maxf(depth, 1.0), backing, peel_back, c)
			var fe: float = alpha_at.call(px - 2.0 * s * u + u * c.flap_edge_off)
			back = back.lerp(c.flap_edge_color, clampf(fa - fe, 0.0, 1.0) * c.flap_edge_k)
			return {"rgb": rgb.lerp(back, fa), "a": maxf(a, fa)}
		if a > 0.0:
			var sp := px - c.flap_shadow_off
			var ss := (sp - (fr["P"] as Vector2)).dot(u)
			var fsh := 0.0
			if ss >= 0.0 and ss <= depth + c.flap_shadow_reach:
				fsh = alpha_at.call(sp - 2.0 * ss * u)
			return {"rgb": rgb.lerp(Vector3.ZERO, fsh * c.flap_shadow_k), "a": a}
	return {"rgb": rgb, "a": a}


## The uniform overrides of a named lab pose of a kit sticker (the frozen frames of the motions): rest, hover (lifted
## with the corner peeled back), fold (the exit peel), band (the scheduled holographic sweep mid-crossing), dissolve,
## disabled (80 % grey, alpha 0.8; disabled_legacy is the old kit's full grey), slap (the shine peak), peel_band (the peel
## with the band mid-crossing: the band is parallel to the fold).
static func kit_pose(pose: StringName, cfg: RcLookVinylConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	match pose:
		&"hover":
			return {&"lift": c.lab_lift, &"peel_back": c.lab_peel_back}
		&"fold":
			return {&"fold": c.lab_fold, &"lift": c.lab_lift}
		&"band":
			return {&"rainbow": 1.0, &"band_t": c.lab_band_t}
		&"peel_band":
			return {&"lift": c.lab_lift, &"peel_back": c.lab_peel_back, &"rainbow": 1.0, &"band_t": c.lab_band_t}
		&"dissolve":
			return {&"dissolve": c.lab_dissolve}
		&"disabled":
			return {&"grey": c.disabled_grey, &"opacity": c.disabled_alpha}
		&"disabled_legacy":
			return {&"grey": c.legacy_kit_disabled_grey, &"opacity": c.disabled_alpha}
		&"slap":
			return {&"gloss_k": c.lab_gloss_k, &"gloss_pos": c.lab_gloss_pos}
	return {}


## rcv_h21: the dissolve cell hash (double precision; see the class note).
static func h21(p: Vector2, cfg: RcLookVinylConfig = null) -> float:
	var c := cfg if cfg != null else config()
	var v := sin(p.dot(c.dissolve_hash)) * 43758.5453
	return v - floorf(v)


## rcv_dissolve_order: 0..1, x across the body plus the cell hash.
static func dissolve_order(px: Vector2, body: Rect2, cell_px: float, cfg: RcLookVinylConfig = null) -> float:
	var c := cfg if cfg != null else config()
	var cell := Vector2(floorf(px.x / cell_px), floorf(px.y / cell_px))
	return clampf((px.x - body.position.x) / maxf(body.size.x, 1.0), 0.0, 1.0) * c.dissolve_x + h21(cell, c) * c.dissolve_h


## rcv_kit_dissolve: what happens to a pixel of dissolve order `order` at dissolve share `dissolve`.
static func dissolve_verdict(order: float, dissolve: float, cfg: RcLookVinylConfig = null) -> int:
	var c := cfg if cfg != null else config()
	var cut := dissolve * c.dissolve_over
	if order < cut - c.dissolve_edge:
		return Dissolve.CUT
	if order < cut:
		return Dissolve.WHITE
	return Dissolve.KEEP


## rcv_grey (Rec.601 on display values).
static func grey(rgb: Vector3, amount: float, cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var l := rgb.dot(c.grey_luma)
	return rgb.lerp(Vector3(l, l, l), amount)


## The drop shadow's soft-disc offset and blur radius at `lift` (0..1).
static func shadow_offset(lift: float, cfg: RcLookVinylConfig = null) -> Vector2:
	var c := cfg if cfg != null else config()
	return c.shadow_off + c.shadow_off_lift * lift


static func shadow_radius(lift: float, cfg: RcLookVinylConfig = null) -> float:
	var c := cfg if cfg != null else config()
	return c.shadow_r + c.shadow_r_lift * lift


## rcv_kit_shadow from the two blurred coverages (`soft_blur` at the soft offset and radius, `contact_blur` at the
## contact offset and radius): the shadow alpha.
static func shadow_alpha(soft_blur: float, contact_blur: float, lift: float, shadow_k: float, dissolve: float,
		cfg: RcLookVinylConfig = null) -> float:
	var c := cfg if cfg != null else config()
	if shadow_k <= 0.0:
		return 0.0
	var soft_a := soft_blur * c.shadow_k * (1.0 - c.shadow_k_lift * lift)
	var contact := 0.0
	if lift < c.contact_lift_max:
		contact = contact_blur * c.contact_k * (1.0 - c.contact_lift_fall * lift)
	return clampf(maxf(soft_a, contact) * shadow_k * (1.0 - dissolve), 0.0, 1.0)


# ---------------------------------------------------------------------------------------------------------------
# Chrome
# ---------------------------------------------------------------------------------------------------------------

## rcv_chrome_marker: decodes a vertex colour into {"kind", "bright", "band"}.
static func chrome_marker(col: Color, cfg: RcLookVinylConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	var kind := KIND_NONE
	var bright := 1.0
	var band := 0.0
	var hi := maxf(col.r, maxf(col.g, col.b))
	if hi > c.marker_min:
		if col.g < c.marker_off * hi and absf(col.r - col.b) < c.marker_eq * hi:
			kind = KIND_MAGENTA
			bright = col.r
		elif col.r < c.marker_off * hi and col.g >= col.b:
			kind = KIND_GREEN
			bright = col.g
			band = floorf(col.b / col.g * c.glitch_bands + 0.5)
	return {"kind": kind, "bright": bright, "band": band}


## rcv_chrome_marker_fill: the magenta fill at local (gradient, rest gloss, white sweep). live = 1 unless reduce effects.
static func chrome_marker_fill(local: Vector2, fill_top: float, fill_bottom: float, top_c: Vector3, bottom_c: Vector3,
		gloss: float, sweep: float, sweep_width: float, live: float, white_k: float, cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var t := clampf((local.y - fill_top) / maxf(1.0, fill_bottom - fill_top), 0.0, 1.0)
	var rgb := top_c.lerp(bottom_c, t)
	rgb = rgb.lerp(Vector3.ONE, gloss * (1.0 - smoothstep(0.0, c.fill_gloss_end, t)))
	var d := absf((local.x - sweep) + (local.y - fill_top) * c.sweep_slant)
	return rgb.lerp(Vector3.ONE, white_k * live * (1.0 - smoothstep(0.0, sweep_width, d)))


## rcv_chrome_glitch_keep: false when the burst's band cut removes this pixel.
static func glitch_keep(local: Vector2, fill_top: float, band: float, band_h: float) -> bool:
	if band > 0.5:
		var y0 := fill_top + (band - 1.0) * band_h
		if local.y < y0 or local.y >= y0 + band_h:
			return false
	return true


## rcv_chrome_glitch: white with scan lines alternating glitch_a and glitch_b.
static func glitch_color(local: Vector2, fill_top: float, scan_period: float, white_c: Vector3, a_c: Vector3, b_c: Vector3,
		cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var row := floorf((local.y - fill_top) / scan_period)
	if fposmod(local.y - fill_top, scan_period) < c.scan_line_px:
		return a_c if fposmod(row, 2.0) < 0.5 else b_c
	return white_c


# ---------------------------------------------------------------------------------------------------------------
# Holo foil fill and card
# ---------------------------------------------------------------------------------------------------------------

## rcv_hsv2rgb.
static func hsv2rgb(h: float, s: float, v: float) -> Vector3:
	var out := Vector3.ZERO
	var offs := [1.0, 2.0 / 3.0, 1.0 / 3.0]
	for i in 3:
		var f := h + float(offs[i])
		f -= floorf(f)
		var p := absf(f * 6.0 - 3.0)
		out[i] = v * lerpf(1.0, clampf(p - 1.0, 0.0, 1.0), s)
	return out


static func _hash12_sin(p: Vector2) -> float:
	var v := sin(p.dot(Vector2(127.1, 311.7))) * 43758.5453
	return v - floorf(v)


## rcv_holo_fill (double precision; see the class note). phase = rc_time * holo_drift.
static func holo_fill(px: Vector2, field_size: Vector2, seed_id: float, phase: float, sat: float,
		cfg: RcLookVinylConfig = null) -> Vector3:
	var c := cfg if cfg != null else config()
	var uv := px / Vector2(maxf(field_size.x, 1.0), maxf(field_size.y, 1.0))
	var a1 := _hash12_sin(Vector2(seed_id, 1.0)) * c.holo_tau
	var a2 := _hash12_sin(Vector2(seed_id, 2.0)) * c.holo_tau
	var a3 := _hash12_sin(Vector2(seed_id, 3.0)) * c.holo_tau
	var hs := c.holo_uv.x * uv.x + c.holo_uv.y * uv.y + c.holo_warp1 * sin(c.holo_warp1_f.x * uv.x + a1) \
			+ c.holo_warp2 * sin(c.holo_warp2_f.x * uv.y + c.holo_warp2_f.y * uv.x + a2) + phase
	var hue := hs - floorf(hs)
	var val := c.holo_val + c.holo_val_amp * sin(c.holo_val_f * (uv.x - uv.y) + a3 + phase * c.holo_tau)
	var col := hsv2rgb(hue, sat, val)
	col = col * c.holo_silver + c.holo_silver_add
	var lf := (px.x - px.y * c.holo_line_slant) / c.holo_line_px
	lf -= floorf(lf)
	col = col.lerp(Vector3.ONE, (1.0 if lf >= c.holo_line_step else 0.0) * c.holo_line_k)
	var cell := Vector2(floorf(px.x / c.holo_spark_cell), floorf(px.y / c.holo_spark_cell))
	var sp := _hash12_sin(cell + Vector2(seed_id, seed_id))
	var at := (cell + Vector2(_hash12_sin(cell + Vector2(c.holo_spark_salt.x, c.holo_spark_salt.x)),
			_hash12_sin(cell + Vector2(c.holo_spark_salt.y, c.holo_spark_salt.y)))) * c.holo_spark_cell
	var d := (px - at).length()
	col = col.lerp(Vector3.ONE, (1.0 if sp >= c.holo_spark_step else 0.0)
			* smoothstep(c.holo_spark_edge.x, c.holo_spark_edge.y, d) * c.holo_spark_k)
	return Vector3(clampf(col.x, 0.0, 1.0), clampf(col.y, 0.0, 1.0), clampf(col.z, 0.0, 1.0))


## rcv_card_front: the scan front's height share for scan_y.
static func card_front(scan_y: float, edge_share: float) -> float:
	return lerpf(-edge_share, 1.0 + edge_share, scan_y)


## rcv_card_gloss's white share at uv.
static func card_gloss_share(uv: Vector2, gloss_t_v: float, gloss_width: float, gloss_alpha: float, live: float) -> float:
	var d := absf((uv.x + uv.y) * 0.5 - gloss_t_v)
	return smoothstep(gloss_width, 0.0, d) * gloss_alpha * live


# ---------------------------------------------------------------------------------------------------------------
# Lab stand-in art
# ---------------------------------------------------------------------------------------------------------------

## A stand-in die-cut sticker image for kit stock `id` (the game bakes the real one in a SubViewport): the extrude
## offset down-right, the white die-cut body, the fill gradient inset by the die-cut edge. Returns the image padded
## by config.lab_pad on every side; `body` (the die-cut box inside it) is the Rect2 the shader wants.
static func lab_art(id: StringName, body_size: Vector2 = Vector2.ZERO, cfg: RcLookVinylConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	var p := preset(id, c)
	var pad := int(c.lab_pad)
	var bsize := body_size if body_size != Vector2.ZERO else c.lab_body
	var sz := Vector2i(int(bsize.x) + pad * 2, int(bsize.y) + pad * 2)
	var img := Image.create(sz.x, sz.y, false, Image.FORMAT_RGBA8)
	var body := Rect2(Vector2(pad, pad), bsize)
	var ext := Vector2(c.extrude_px * c.extrude_slant, c.extrude_px)
	var edge := c.keyline_px
	var die_top := c.die_cut
	var rim_col := c.vinyl_ink
	for y in sz.y:
		for x in sz.x:
			var pt := Vector2(x, y) + Vector2(0.5, 0.5)
			var out := Color(0, 0, 0, 0)
			if _in_round(pt, body.position + ext, body.size, c.lab_radius):
				out = c.vinyl_extrude
			if _in_round(pt, body.position, body.size, c.lab_radius):
				out = rim_col
				var inner := Rect2(body.position + Vector2(edge, edge), body.size - Vector2(edge, edge) * 2.0)
				if _in_round(pt, inner.position, inner.size, c.lab_radius - edge):
					var face_edge := c.edge_max_px
					var fill_r := Rect2(inner.position + Vector2(face_edge, face_edge), inner.size - Vector2(face_edge, face_edge) * 2.0)
					out = die_top if id != &"kit_kraft" else p.backing
					if _in_round(pt, fill_r.position, fill_r.size, maxf(c.lab_radius - edge - face_edge, 1.0)):
						var t := clampf((pt.y - fill_r.position.y) / maxf(fill_r.size.y, 1.0), 0.0, 1.0)
						out = p.fill_top.lerp(p.fill_bottom, t)
						if p.holo_face:
							var h := holo_fill(pt - fill_r.position, fill_r.size, LAB_HOLO_SEED, 0.0, c.holo_sat, c)
							out = Color(h.x, h.y, h.z, 1.0)
			img.set_pixel(x, y, out)
	return {"image": img, "body": body}


static func _in_round(pt: Vector2, pos: Vector2, size: Vector2, radius: float) -> bool:
	var q := (pt - (pos + size * 0.5)).abs() - (size * 0.5 - Vector2(radius, radius))
	return Vector2(maxf(q.x, 0.0), maxf(q.y, 0.0)).length() + minf(maxf(q.x, q.y), 0.0) <= radius
