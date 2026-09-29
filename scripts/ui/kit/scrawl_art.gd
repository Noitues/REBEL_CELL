class_name ScrawlArt
extends VBoxContainer
## A marker scrawl as baked art (ART_BIBLE §4.3 rule 5; critique §6: NEVER SLEEP was live text
## in a display face and changed width with the language): the SVG drawn at `HEIGHT` x the
## text scale, tilted, with a translated subtitle under it in the player's language (shown
## when the language isn't English: the slogan carries meaning, §4.3 rule 5). Decoration:
## ignores the mouse, never takes focus. View only.

## The art's height at text scale 1.0 (px) and its tilt (degrees).
const HEIGHT := 76.0
const TILT := -6.0

var art: TextureRect
## The slogan in the player's language (hidden in English: the art says it).
var subtitle: Label
var path: String = ""


## `p_path`: an SvgArt scrawl; `words`: the slogan's key ("Never sleep"), translated here.
func _init(p_path: String = SvgArt.SCRAWL_NEVER_SLEEP, words: String = "Never sleep") -> void: # TR
	path = p_path
	name = "Scrawl"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_theme_constant_override("separation", 0)
	art = TextureRect.new()
	art.name = "Art"
	art.mouse_filter = Control.MOUSE_FILTER_IGNORE
	art.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	art.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	add_child(art)
	subtitle = Label.new()
	subtitle.name = "Subtitle"
	subtitle.text = tr(words)
	subtitle.add_theme_color_override("font_color", Palette.TEXT_HI)
	subtitle.add_theme_color_override("font_outline_color", Palette.INK)
	subtitle.add_theme_constant_override("outline_size", UiTheme.SP_XS)
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(subtitle)
	_refresh()


func _ready() -> void:
	pivot_offset = size * 0.5
	rotation_degrees = TILT
	if not Settings.changed.is_connected(_refresh):
		Settings.changed.connect(_refresh)


## True when the subtitle shows (any language but English).
static func needs_subtitle() -> bool:
	return not TranslationServer.get_locale().begins_with("en")


func _refresh() -> void:
	var h := HEIGHT * Settings.text_scale
	art.texture = SvgArt.texture(path, h)
	var nat := SvgArt.natural_size(path)
	art.custom_minimum_size = Vector2(h * nat.x / maxf(1.0, nat.y), h)
	subtitle.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	subtitle.visible = needs_subtitle()
