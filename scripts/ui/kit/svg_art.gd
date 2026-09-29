class_name SvgArt
extends RefCounted
## Baked vector art (ART_BIBLE §4.3 rule 5; art pass W8a): the logo, the scrawls and the
## corporation landmark glyphs are SVG files under `assets/art/`, rasterised at the size a
## view draws them (crisp at every text scale and resolution) and cached per size. The
## source file is read when it is present (editor, tests, a build that ships the .svg);
## otherwise the imported texture is used. Paths and sizes only: never game state.

const LOGO := "res://assets/art/logo_rebel_cell.svg"
const SCRAWL_NEVER_SLEEP := "res://assets/art/scrawl_never_sleep.svg"
const SCRAWL_TRUST_NO_ONE := "res://assets/art/scrawl_trust_no_one.svg"
const LANDMARK_DIR := "res://assets/art/landmarks/"
## Rasterise at this multiple of the drawn size (sharp when a view scales it up a little).
const OVERSAMPLE := 2.0

static var _cache: Dictionary = {}
static var _sizes: Dictionary = {}


## The landmark glyph's file for corporation `corp_id` ("" when it has none).
static func landmark_path(corp_id: StringName) -> String:
	var p := LANDMARK_DIR + String(corp_id) + ".svg"
	return p if FileAccess.file_exists(p) or ResourceLoader.exists(p) else ""


## The SVG's own size (its width and height attributes, px).
static func natural_size(path: String) -> Vector2:
	if _sizes.has(path):
		return _sizes[path]
	var out := Vector2.ZERO
	var svg := FileAccess.get_file_as_string(path)
	if svg != "":
		var head := svg.substr(0, svg.find(">", svg.find("<svg")))
		out = Vector2(_attr(head, "width"), _attr(head, "height"))
	else:
		var t := load(path) as Texture2D
		if t != null:
			out = t.get_size()
	_sizes[path] = out
	return out


static func _attr(head: String, key: String) -> float:
	var at := head.find(" %s=\"" % key)
	if at < 0:
		return 0.0
	var from := at + key.length() + 3
	return head.substr(from, head.find("\"", from) - from).to_float()


## The art at `height` px tall (its width follows the aspect), as a texture.
static func texture(path: String, height: float) -> Texture2D:
	var nat := natural_size(path)
	if nat.y <= 0.0:
		return null
	var s := snappedf(maxf(0.05, height * OVERSAMPLE / nat.y), 0.05)
	var key := "%s@%.2f" % [path, s]
	if _cache.has(key):
		return _cache[key]
	var tex: Texture2D = null
	var svg := FileAccess.get_file_as_string(path)
	if svg != "":
		var img := Image.new()
		if img.load_svg_from_string(svg, s) == OK:
			img.generate_mipmaps()
			tex = ImageTexture.create_from_image(img)
	if tex == null:
		tex = load(path) as Texture2D
	_cache[key] = tex
	return tex
