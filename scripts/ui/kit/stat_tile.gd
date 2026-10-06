class_name StatTile
extends Button
## Parity STATS-01 (designer group ruling 2026-10-05: the build reworked in v2): one profile
## number as a terminal tile, ported from art-m13-final `scripts/ui/title_scene.gd` `_stat_cell`
## (the build's StatField icon + number over its name) and drawn in the v2 kit: a small
## terminal panel (Chrome.draw_terminal: navy glass, the cut corner, the Cell's cyan edge), the
## art pass's StatIcon in its own colour, the number in the terminal mono and the name in
## terminal CAPS under it. A focus stop (the pad walks the tiles; the lime brackets show it);
## what it counts is its tooltip. View only.

## The tile's width at text scale 1.0 (px; it grows with the text), its pads and the gap
## between the icon and the number.
const WIDTH := 178.0
const PAD := Vector2(12, 8)
const ICON_GAP := 8.0
## The icon's radius as a share of the number's font size.
const ICON_SHARE := 0.5
const VALUE_STEP := UiTheme.TITLE
const NAME_STEP := UiTheme.CAPTION
## The tile's own chamfer (a small panel's cut corner).
const CHAMFER := 8.0

var kind: StringName = &""
var value: String = ""
var caption: String = ""


## A tile for StatIcon `p_kind`, its `p_value` (a number or "—") and its name `p_caption`
## (translated by the caller); `tip` is the tooltip's extra line.
func _init(p_kind: StringName, p_value: String, p_caption: String, tip: String = "") -> void:
	PaletteSkins.watch(self)  # the skin's chrome follows a pick
	kind = p_kind
	value = p_value
	caption = p_caption
	name = "Stat_%s" % String(p_kind)
	focus_mode = Control.FOCUS_ALL
	size_flags_horizontal = Control.SIZE_EXPAND_FILL  # a grid's row of tiles fills its window
	set_meta(UiFocus.META_NO_SCALE, true)
	tooltip_text = UiTip.fold(p_caption + ("\n" + tip if tip != "" else ""))
	for box in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled", &"focus"]:
		add_theme_stylebox_override(box, StyleBoxEmpty.new())
	KitState.track(self)
	refit()


func _ready() -> void:
	Settings.changed.connect(refit)


func _exit_tree() -> void:
	if Settings.changed.is_connected(refit):
		Settings.changed.disconnect(refit)


## The caption as shown (CAPS).
func shown_caption() -> String:
	return caption.to_upper()


## Sizes the tile to its words (a Button's own minimum ignores a script's draw).
func refit() -> void:
	var w := WIDTH * Settings.text_scale
	var cf := Chrome.caps_font(NAME_STEP)
	var cp := Chrome.px(NAME_STEP)
	var vf := Palette.mono()
	var vp := Chrome.px(VALUE_STEP)
	var room := w - PAD.x * 2.0
	var cap_h := cf.get_multiline_string_size(shown_caption(), HORIZONTAL_ALIGNMENT_LEFT, room, cp, -1, CrtSwitch.WRAP).y
	custom_minimum_size = Vector2(w, ceilf(PAD.y * 2.0 + vf.get_height(vp) + cap_h))
	queue_redraw()


func _draw() -> void:
	var st := KitState.of(self)
	var r := Rect2(Vector2(0, KitState.lift(st)), size)
	var hot := st == KitState.HOVER or st == KitState.FOCUS
	var glass := PaletteSkins.chrome(Palette.TERMINAL_BG)
	if hot:
		glass = glass.lerp(PaletteSkins.chrome(Palette.NET_CYAN), UiTheme.FILL_SHIFT)
	Chrome.draw_terminal(self, r, KitState.edge_color(st, Palette.NET_CYAN), glass, CHAMFER)
	var vf := Palette.mono()
	var vp := Chrome.px(VALUE_STEP)
	var ir := vp * ICON_SHARE
	var top := r.position.y + PAD.y
	StatIcon.draw(self, Vector2(r.position.x + PAD.x + ir, top + vf.get_height(vp) * 0.5), ir, kind, StatIcon.color_of(kind))
	draw_string(vf, Vector2(r.position.x + PAD.x + ir * 2.0 + ICON_GAP, top + vf.get_ascent(vp)), value, HORIZONTAL_ALIGNMENT_LEFT, -1, vp, Palette.TEXT_HI)
	var cf := Chrome.caps_font(NAME_STEP)
	var cp := Chrome.px(NAME_STEP)
	draw_multiline_string(cf, Vector2(r.position.x + PAD.x, top + vf.get_height(vp) + cf.get_ascent(cp)), shown_caption(), HORIZONTAL_ALIGNMENT_LEFT,
		r.size.x - PAD.x * 2.0, cp, -1, Palette.TEXT_MID, CrtSwitch.WRAP)
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), st)
