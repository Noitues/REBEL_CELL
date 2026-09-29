class_name AchievementBadge
extends Control
## One achievement as a sticker badge (ART_BIBLE §11 Stats and achievements; critique 18:
## ASCII "[ ]" checkboxes): earned, a round PAPER sticker in `STICKER_PINK` with an INK
## ring, its StatIcon filled and a slight tilt; not yet earned, a dashed `DISABLED` outline
## with the icon open and a lock badge (§3.7, §6: never a faded colour). Its name sits under
## it (`caption`, TEXT_HI: readable on the glass it is stuck on); what it asks is the
## tooltip. Draw only. View only.

## The badge's diameter at text scale 1.0 (px), the name's room under it, the lock badge's
## radius and the dash length.
const SIDE := 64.0
const NAME_GAP := 4.0
const LOCK_R := 9.0
const DASH := 6.0
## Icon per achievement id (a missing id shows the BADGES icon).
const ICONS := {&"first_blood": StatIcon.RUNS, &"banked": StatIcon.RACK, &"breach": StatIcon.WON, &"clean_hands": StatIcon.CREW,
	&"ice_5": StatIcon.ICE, &"ice_10": StatIcon.ICE, &"purge_survivor": StatIcon.HEAT, &"wall": StatIcon.RAIDS,
	&"perfectionist": StatIcon.CHECK, &"final_final": StatIcon.JACK_IN}

var id: StringName = &""
var title: String = ""
var earned: bool = false
var _name: Label


func _init(p_id: StringName, p_title: String, p_text: String, p_earned: bool) -> void:
	id = p_id
	title = p_title
	earned = p_earned
	name = "Badge_%s" % String(p_id)
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_text = UiTip.fold("%s\n%s%s" % [p_title, p_text, "" if p_earned else "\n" + tr("Not earned yet.")])
	_name = Label.new()
	_name.name = "Name"
	_name.text = p_title
	_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_name.add_theme_color_override("font_color", Palette.TEXT_HI)
	_name.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	_name.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_name)


func _side() -> float:
	return SIDE * Settings.text_scale


func _get_minimum_size() -> Vector2:
	var w := _side() * 1.5
	var name_h := _name.get_combined_minimum_size().y if _name != null else 0.0
	# Two lines of name at most (the width is 1.5 badges).
	var f := _name.get_theme_font(&"font")
	var lines := 2.0 if f.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.CAPTION)).x > w else 1.0
	name_h = maxf(name_h, f.get_height(UiTheme.font_px(UiTheme.CAPTION)) * lines)
	return Vector2(w, _side() + NAME_GAP + name_h)


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and _name != null:
		_name.position = Vector2(0, _side() + NAME_GAP)
		_name.size = Vector2(size.x, size.y - _side() - NAME_GAP)


## The unearned outline's colour: DISABLED, or TEXT_MID in high contrast (the disabled
## colour HighContrast gives the theme: DISABLED is under 7:1 on black, §12).
static func outline_color() -> Color:
	return Palette.TEXT_MID if PaperInk.on() else Palette.DISABLED


## The badge's disc (local).
func disc() -> Rect2:
	var s := _side()
	return Rect2(Vector2((size.x - s) * 0.5, 0), Vector2(s, s))


func _draw() -> void:
	var d := disc()
	var c := d.get_center()
	var r := d.size.x * 0.5
	var kind: StringName = ICONS.get(id, StatIcon.BADGES)
	if earned:
		draw_set_transform(c, deg_to_rad(-4.0), Vector2.ONE)
		draw_circle(Vector2(3, 4), r, Palette.SHADOW)
		draw_circle(Vector2.ZERO, r, Palette.STICKER_PINK)
		draw_arc(Vector2.ZERO, r - 3.0, 0, TAU, 40, Palette.INK, 2.0, true)
		if PaperInk.on():
			# Art pass WF (§12): the sticker's own edge, opaque INK.
			draw_arc(Vector2.ZERO, r - PaperInk.EDGE_PX * 0.5, 0, TAU, 40, Palette.INK, PaperInk.EDGE_PX, true)
		StatIcon.draw(self, Vector2.ZERO, r * 0.5, kind, Palette.INK, true)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		return
	# Not yet: an outline sticker space, the icon open, and a lock.
	var n := 32
	for i in n:
		if i % 2 == 0:
			draw_arc(c, r - 2.0, TAU * i / n, TAU * (i + 1) / n, 4, outline_color(), 2.0, true)
	StatIcon.draw(self, c, r * 0.45, kind, Palette.TEXT_MID)
	var lock_c := c + Vector2(r * 0.7, r * 0.7)
	var lr := LOCK_R * Settings.text_scale
	draw_circle(lock_c, lr, HighContrast.BG if PaperInk.on() else Palette.TERMINAL_BG)
	draw_arc(lock_c, lr, 0, TAU, 20, outline_color(), PaperInk.edge_width(1.5), true)
	StatIcon.draw(self, lock_c, lr * 0.7, StatIcon.LOCK, Palette.TEXT_HI)
