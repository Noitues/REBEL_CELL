class_name AchievementBadge
extends Button
## Parity STATS-01 (designer group ruling 2026-10-05: the build reworked in v2): one achievement
## as a round badge, ported from art-m13-final `scripts/ui/kit/achievement_badge.gd`. Earned: a
## round sticker (the Cell's pink with the vinyl's white die-cut ring, v2 §1.2) with its
## StatIcon in ink and a slight tilt; not yet: a dashed outline sticker space with the icon open
## and a lock badge (never a faded colour). Its name in terminal CAPS under it; what it asks is
## the tooltip. A focus stop (the pad walks the badges; the lime brackets show it). Draw only.
## View only.

## The badge's diameter at text scale 1.0 (px; it grows with the text to SCALE_MAX, a drawn
## object), the gap to its name, the lock badge's radius, the die-cut ring's share of the
## radius, the earned tilt (deg) and the unearned outline's dashes.
const SIDE := 56.0
const SCALE_MAX := 1.3
const NAME_GAP := 4.0
const LOCK_R := 9.0
const RING_SHARE := 0.12
const TILT_DEG := -4.0
const DASHES := 32
const WIDTH_SHARE := 1.6
const NAME_STEP := UiTheme.CAPTION
## The earned sticker's drop shadow offset (px).
const SHADOW_OFFSET := Vector2(3, 4)
## Icon per achievement id (a missing id shows the BADGES icon).
const ICONS := {&"first_blood": StatIcon.RUNS, &"banked": StatIcon.RACK, &"breach": StatIcon.WON, &"clean_hands": StatIcon.CREW,
	&"ice_5": StatIcon.ICE, &"ice_10": StatIcon.ICE, &"purge_survivor": StatIcon.HEAT, &"wall": StatIcon.RAIDS,
	&"perfectionist": StatIcon.CHECK, &"final_final": StatIcon.JACK_IN}

var id: StringName = &""
var title: String = ""
var earned: bool = false
## B5 (round 44 B_menus `stats.png`): the badge sits on the white liner (LinerPanel): an earned badge is the glossy
## die-cut sticker, an unearned one only its empty kiss-cut outline in the liner, and the name is printed in the
## liner's ink.
var on_liner: bool = false
## B5: the kiss-cut's ink on the liner and its width (px).
const KISS_CUT_INK := Palette.LINER_KISS_CUT
const KISS_CUT_W := 1.5
const LINER_NAME_INK := Palette.LINER_NAME_INK
const LINER_NAME_DIM := Palette.LINER_NAME_DIM


func _init(p_id: StringName, p_title: String, p_text: String, p_earned: bool) -> void:
	id = p_id
	title = p_title
	earned = p_earned
	name = "Badge_%s" % String(p_id)
	focus_mode = Control.FOCUS_ALL
	set_meta(UiFocus.META_NO_SCALE, true)
	tooltip_text = UiTip.fold("%s\n%s%s" % [p_title, p_text, "" if p_earned else "\n" + TranslationServer.translate("Not earned yet.")])
	for box in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled", &"focus"]:
		add_theme_stylebox_override(box, StyleBoxEmpty.new())
	KitState.track(self)
	refit()


func _ready() -> void:
	Settings.changed.connect(refit)


func _exit_tree() -> void:
	if Settings.changed.is_connected(refit):
		Settings.changed.disconnect(refit)


## The badge's diameter (px).
static func side() -> float:
	return SIDE * minf(Settings.text_scale, SCALE_MAX)


## The name as shown (CAPS).
func shown_name() -> String:
	return title.to_upper()


## Sizes the badge: the disc, the gap and its name wrapped to WIDTH_SHARE discs (two lines).
func refit() -> void:
	var w := maxf(side() * WIDTH_SHARE, Chrome.caps_font(NAME_STEP).get_string_size(_longest_word(), HORIZONTAL_ALIGNMENT_LEFT, -1, Chrome.px(NAME_STEP)).x)
	custom_minimum_size = Vector2(ceilf(w), ceilf(side() + NAME_GAP + _name_h(w)))
	queue_redraw()


func _longest_word() -> String:
	var best := ""
	for wd in shown_name().split(" ", false):
		if wd.length() > best.length():
			best = wd
	return best


func _name_h(w: float) -> float:
	return Chrome.caps_font(NAME_STEP).get_multiline_string_size(shown_name(), HORIZONTAL_ALIGNMENT_CENTER, w, Chrome.px(NAME_STEP), -1, CrtSwitch.WRAP).y


## The unearned outline's colour: DISABLED, or TEXT_MID in high contrast (DISABLED is under
## 7:1 on black, §12).
static func outline_color() -> Color:
	return Palette.TEXT_MID if Settings.high_contrast else Palette.DISABLED


## The badge's disc (local).
func disc() -> Rect2:
	var s := side()
	return Rect2(Vector2((size.x - s) * 0.5, 0), Vector2(s, s))


func _draw() -> void:
	var st := KitState.of(self)
	var d := disc()
	d.position.y += KitState.lift(st)
	var c := d.get_center()
	var r := d.size.x * 0.5
	var kind: StringName = ICONS.get(id, StatIcon.BADGES)
	if earned:
		draw_set_transform(c, deg_to_rad(TILT_DEG), Vector2.ONE)
		draw_circle(SHADOW_OFFSET, r, Palette.SHADOW)
		draw_circle(Vector2.ZERO, r, Palette.GLYPH_FILL)  # the vinyl's white die-cut
		draw_circle(Vector2.ZERO, r * (1.0 - RING_SHARE), Palette.CELL_PINK)
		StatIcon.draw(self, Vector2.ZERO, r * 0.5, kind, Palette.INK)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	elif on_liner:
		draw_arc(c, r - 1.0, 0.0, TAU, 48, KISS_CUT_INK, KISS_CUT_W, true)  # B5: the empty kiss-cut in the liner
	else:
		for i in DASHES:
			if i % 2 == 0:
				draw_arc(c, r - 2.0, TAU * i / DASHES, TAU * (i + 1) / DASHES, 4, outline_color(), 2.0, true)
		StatIcon.draw(self, c, r * 0.45, kind, Palette.TEXT_MID)
		var lock_c := c + Vector2(r * 0.7, r * 0.7)
		var lr := LOCK_R * minf(Settings.text_scale, SCALE_MAX)
		draw_circle(lock_c, lr, PaletteSkins.chrome(Palette.TERMINAL_BG))
		draw_arc(lock_c, lr, 0, TAU, 20, outline_color(), 1.5, true)
		StatIcon.draw(self, lock_c, lr * 0.7, StatIcon.LOCK, Palette.TEXT_HI)
	var cf := Chrome.caps_font(NAME_STEP)
	var cp := Chrome.px(NAME_STEP)
	var name_col := Palette.TEXT_HI if earned else Palette.TEXT_MID
	if on_liner:
		name_col = LINER_NAME_INK if earned else LINER_NAME_DIM
	draw_multiline_string(cf, Vector2(0, side() + NAME_GAP + cf.get_ascent(cp)), shown_name(), HORIZONTAL_ALIGNMENT_CENTER, size.x, cp, -1,
		name_col, CrtSwitch.WRAP)
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), st)
