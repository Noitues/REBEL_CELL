class_name PaletteSkins
extends RefCounted
## ART-12 12s (the M12 box "Skins": procedural palette skins on the v2 tokens). A skin gives
## the Cell's terminal chrome tokens (TOKENS: the navy glass, its cyan edge, the terminal
## and text whites, the selected fill and the words on it, the CRT glass) other values,
## made procedurally from the v2 values by one RECIPE (in OKLCH: a hue for the light ink
## tokens and one for the dark glass, a chroma scale, a lightness shift for the accent; the
## v2 lightness of every other token is kept, so contrast holds). Nothing else changes: semantic tokens (HARM / GAIN, the Heat bands,
## the corp kits, slices, Daemons, rarity, FOCUS, the stickers) keep their v2 values and
## every greyscale pairing cue (Palette.PAIRED_WITH) stays, layouts and sizes are untouched.
##
## Palette's tokens are compile-time constants read by every view, so a skin is realised
## where the chrome is drawn: `apply` re-values a built theme (UiTheme.build calls it before
## high contrast), and the kit's own chrome painters (`chrome`: the terminal box, HudSkin's
## terminal panel, the CRT panel) ask for the skin's value of a v2 chrome colour. A colour
## that is not a chrome token comes back unchanged, so a corp edge or a Heat word is never
## re-valued. View only: it reads Settings and never changes game state.

## The default skin: palette v2 exactly as ART_BIBLE §2 lists it.
const DEFAULT := &"v2"
## Every skin, the default first (Settings.PALETTE_SKINS and the Options picker follow it).
const IDS: Array[StringName] = [&"v2", &"cobalt", &"graphite"]
## The picker's words, in IDS order (keys).
const WORDS := ["Cell cyan (palette v2, the default)", "Cobalt (deep blue terminal)", "Graphite (neutral grey terminal)"] # TR
## The chrome tokens a skin re-values (Palette constant names). NET_CYAN, NET_BG_OUTER share
## the edge's and the selected words' values, so in the chrome they follow them; where cyan
## means PROTECT (shield slices and FX, the TURN Daemon, Uncommon) it is drawn from those
## semantic tokens and keeps #5CE1FF.
const TOKENS: Array[StringName] = [&"TERMINAL_BG", &"TERMINAL_BG_HOT", &"TERMINAL_EDGE", &"TERMINAL_TEXT",
	&"TEXT_HI", &"TEXT_MID", &"TEXT_LO", &"SELECTED", &"ON_SELECTED", &"CRT_GLASS_TOP", &"CRT_GLASS_BOTTOM"]
## Skin id -> recipe. "ink_hue" / "glass_hue": the OKLCH hue (degrees) given to the light
## tokens (OKLab L >= INK_LIGHTNESS: edge, text, the selected fill) and to the dark ones (the
## glass); absent = each token keeps its v2 hue. "chroma": every token's chroma is scaled by it
## (then lowered to fit sRGB); "glass_chroma" scales the dark ones once more. "accent_light":
## the OKLab lightness shift of ACCENT_TOKENS only.
## v2 is the identity (the bible's values exactly).
const RECIPES := {
	&"v2": {},
	&"cobalt": {"ink_hue": 262.0, "glass_hue": 266.0, "chroma": 1.0, "glass_chroma": 1.8, "accent_light": -0.07},
	&"graphite": {"chroma": 0.08},
}
## The OKLab lightness from which a token counts as ink (light) rather than glass (dark).
const INK_LIGHTNESS := 0.5
## The accent tokens (the edge and the selected fill share a value).
const ACCENT_TOKENS: Array[StringName] = [&"TERMINAL_EDGE", &"SELECTED"]
## Steps of the chroma search that keeps a turned colour inside sRGB.
const GAMUT_STEPS := 18
## How far outside 0..1 a channel may sit and still count as in gamut (float noise).
const GAMUT_EPSILON := 0.0005

## skin id -> {token: Color}, built on first use.
static var _cache: Dictionary = {}
## skin id -> {opaque v2 rgba32: opaque skin Color}, built on first use.
static var _maps: Dictionary = {}


## Whether `skin` is a known skin id.
static func has(skin: StringName) -> bool:
	return IDS.has(skin)


## The skin Settings shows now (the default when Settings has none or an unknown id).
static func active() -> StringName:
	# Looked up by node, not the autoload's name, so tools run with -s (no autoload names
	# while they compile) can load the kit.
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null or tree.root == null:
		return DEFAULT
	var settings := tree.root.get_node_or_null(^"Settings")
	if settings == null:
		return DEFAULT
	var s := StringName(str(settings.get(&"palette_skin")))
	return s if has(s) else DEFAULT


## The v2 value of chrome token `token` (Palette's constant).
static func v2_value(token: StringName) -> Color:
	return (Palette as Script).get_script_constant_map().get(token, Palette.AUTO)


## `token`'s value under `skin` (v2's for v2, an unknown skin or a token outside TOKENS).
static func resolve(skin: StringName, token: StringName) -> Color:
	if not TOKENS.has(token):
		return v2_value(token)
	return values(skin).get(token, v2_value(token))


## Every TOKENS value under `skin` ({token: Color}; the v2 values for an unknown skin).
static func values(skin: StringName) -> Dictionary:
	if not has(skin):
		skin = DEFAULT
	if not _cache.has(skin):
		var out := {}
		var r: Dictionary = RECIPES[skin]
		for t in TOKENS:
			out[t] = _recolour(v2_value(t), r, ACCENT_TOKENS.has(t))
		_cache[skin] = out
	return _cache[skin]


## `c` as `skin` draws it: a v2 chrome colour (any alpha) becomes the skin's value with the
## same alpha; any other colour is returned as it is. `skin` empty = the active skin.
static func chrome(c: Color, skin: StringName = &"") -> Color:
	if skin == &"":
		skin = active()
	if skin == DEFAULT or not has(skin):
		return c
	var m := _map(skin)
	var key := Color(c, 1.0).to_rgba32()
	if not m.has(key):
		return c
	return Color(m[key] as Color, c.a)


## Re-values every chrome colour of `theme` for `skin` in place: its colours and the bg,
## border and shadow of its flat boxes. v2 leaves it as built. Safe to call twice.
static func apply(theme: Theme, skin: StringName) -> void:
	if theme == null or skin == DEFAULT or not has(skin):
		return
	var done := {}
	for type in theme.get_type_list():
		for name in theme.get_color_list(type):
			theme.set_color(name, type, chrome(theme.get_color(name, type), skin))
		for box_name in theme.get_stylebox_list(type):
			var sb := theme.get_stylebox(box_name, type)
			if sb != null and not done.has(sb.get_instance_id()):
				done[sb.get_instance_id()] = true
				apply_box(sb, skin)


## Re-values a flat box's bg, border and shadow for `skin` (other box kinds untouched).
static func apply_box(sb: StyleBox, skin: StringName = &"") -> void:
	var flat := sb as StyleBoxFlat
	if flat == null:
		return
	flat.bg_color = chrome(flat.bg_color, skin)
	flat.border_color = chrome(flat.border_color, skin)
	flat.shadow_color = chrome(flat.shadow_color, skin)


## Drops the built values (tests that change RECIPES' inputs; nothing at runtime needs it).
static func clear_cache() -> void:
	_cache.clear()
	_maps.clear()


static func _map(skin: StringName) -> Dictionary:
	if not _maps.has(skin):
		var m := {}
		var vals := values(skin)
		for t in TOKENS:
			m[Color(v2_value(t), 1.0).to_rgba32()] = Color(vals[t] as Color, 1.0)
		_maps[skin] = m
	return _maps[skin]


# --- OKLab (Björn Ottosson's matrices; sRGB D65) ---------------------------------------

## `c` in OKLab as Vector3(L, a, b) (alpha ignored).
static func oklab(c: Color) -> Vector3:
	var lin := c.srgb_to_linear()
	var l := 0.4122214708 * lin.r + 0.5363325363 * lin.g + 0.0514459929 * lin.b
	var m := 0.2119034982 * lin.r + 0.6806995451 * lin.g + 0.1073969566 * lin.b
	var s := 0.0883024619 * lin.r + 0.2817188376 * lin.g + 0.6299787005 * lin.b
	var l_ := _cbrt(l)
	var m_ := _cbrt(m)
	var s_ := _cbrt(s)
	return Vector3(0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
		1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
		0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


## The OKLab distance between two colours (alpha ignored).
static func delta_e(a: Color, b: Color) -> float:
	return oklab(a).distance_to(oklab(b))


## An OKLab Vector3(L, a, b) as linear RGB (may sit outside 0..1).
static func _linear_from_oklab(v: Vector3) -> Vector3:
	var l_ := v.x + 0.3963377774 * v.y + 0.2158037573 * v.z
	var m_ := v.x - 0.1055613458 * v.y - 0.0638541728 * v.z
	var s_ := v.x - 0.0894841775 * v.y - 1.2914855480 * v.z
	var l := l_ * l_ * l_
	var m := m_ * m_ * m_
	var s := s_ * s_ * s_
	return Vector3(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
		-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
		-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


## `c` made by `recipe` (see RECIPES); `accent` = one of ACCENT_TOKENS. Chroma is lowered
## until the colour fits sRGB. Alpha is kept. The empty recipe returns `c` exactly.
static func _recolour(c: Color, recipe: Dictionary, accent: bool) -> Color:
	if recipe.is_empty():
		return c
	var lab := oklab(c)
	var chroma := Vector2(lab.y, lab.z).length() * float(recipe.get("chroma", 1.0))
	var hue := atan2(lab.z, lab.y)
	var ink := lab.x >= INK_LIGHTNESS
	if not ink:
		chroma *= float(recipe.get("glass_chroma", 1.0))
	var hue_key := "ink_hue" if ink else "glass_hue"
	if recipe.has(hue_key):
		hue = deg_to_rad(float(recipe[hue_key]))
	var lightness := lab.x + (float(recipe.get("accent_light", 0.0)) if accent else 0.0)
	lightness = clampf(lightness, 0.0, 1.0)
	var lo := 0.0
	var hi := chroma
	var best := Vector3(lightness, chroma * cos(hue), chroma * sin(hue))
	if not _in_gamut(_linear_from_oklab(best)):
		best = Vector3(lightness, 0.0, 0.0)
		for i in GAMUT_STEPS:
			var mid := (lo + hi) * 0.5
			var v := Vector3(lightness, mid * cos(hue), mid * sin(hue))
			if _in_gamut(_linear_from_oklab(v)):
				lo = mid
				best = v
			else:
				hi = mid
	var rgb := _linear_from_oklab(best)
	var lin := Color(clampf(rgb.x, 0.0, 1.0), clampf(rgb.y, 0.0, 1.0), clampf(rgb.z, 0.0, 1.0), c.a)
	return lin.linear_to_srgb()


static func _in_gamut(v: Vector3) -> bool:
	return v.x >= -GAMUT_EPSILON and v.y >= -GAMUT_EPSILON and v.z >= -GAMUT_EPSILON \
		and v.x <= 1.0 + GAMUT_EPSILON and v.y <= 1.0 + GAMUT_EPSILON and v.z <= 1.0 + GAMUT_EPSILON


static func _cbrt(x: float) -> float:
	return signf(x) * pow(absf(x), 1.0 / 3.0)
