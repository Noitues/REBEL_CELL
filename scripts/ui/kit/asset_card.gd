class_name AssetCard
extends Button
## A defence asset as a taped paper card (reference: DEFENSE LOADOUT): the asset's icon
## on a dark window, its name, integrity and how many sit in the Armory. Emits Button
## signals; the scene decides what a press means (deploy to the Site picked on the board).
## H22 #9: the numbers sit on a dark plate in light lettering (dark grey on beige was
## unreadable, more so under the disabled shade), the lettering follows the text size and
## the card's size is `card_size()` (the icon window gives way first at big text).

var asset_id: StringName = &""
var display_name: String = ""
var integrity: int = 0
var count: int = 1
var _hot: bool = false

## A card at text scale 1.0 (px), and how much of the text scale its size follows.
const BASE_SIZE := Vector2(110, 120)
const SIZE_FOLLOW := 0.5
## Lettering at text scale 1.0: name, integrity, count.
const NAME_SIZE := 12
const NUMBER_SIZE := 14
const COUNT_SIZE := 17
## Padding (px), the icon window's least height (px) and the icon's share of it.
const PAD := 8.0
const WINDOW_MIN_H := 40.0
const ICON_SHARE := 0.34
## The disabled shade (lighter than before: the numbers stay readable under it).
const DISABLED_SHADE := Color(0, 0, 0, 0.3)


func _init(p_asset_id: StringName = &"", p_name: String = "", p_integrity: int = 0, p_count: int = 1) -> void:
	asset_id = p_asset_id
	display_name = p_name
	integrity = p_integrity
	count = p_count
	custom_minimum_size = card_size()
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


## The card's size at the current text scale.
static func card_size() -> Vector2:
	return BASE_SIZE * (1.0 + (Settings.text_scale - 1.0) * SIZE_FOLLOW)


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(Vector2(4, 5), size), Palette.SHADOW)
	if _hot and not disabled:
		draw_rect(r.grow(4), Color(Palette.CELL_ACID, 0.45))
	draw_rect(r, Palette.NOTE_PAPER)
	draw_rect(r, Color(Palette.INK, 0.5), false, 1.0)
	draw_rect(Rect2(size.x * 0.35, -6, 40, 12), Palette.NOTE_TAPE)
	var mono := Palette.mono()
	var ns := roundi(NAME_SIZE * s)
	draw_string(mono, Vector2(PAD, PAD + mono.get_ascent(ns)), display_name.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, size.x - PAD * 2.0, ns, Palette.INK)
	# The numbers' plate at the foot: integrity (hexagon) and the count in the Armory.
	var num := roundi(NUMBER_SIZE * s)
	var cs := roundi(COUNT_SIZE * s)
	var plate_h := maxf(mono.get_height(num), Palette.marker().get_height(cs)) + PAD * 0.5
	var plate := Rect2(0, size.y - plate_h, size.x, plate_h)
	var top := PAD + mono.get_height(ns) + PAD * 0.5
	# H24 S14: what the asset does, a pictogram and a line, over the numbers' plate.
	var es := roundi(EFFECT_SIZE * s)
	var effect_h := mono.get_height(es) + PAD * 0.25 if effect_text != "" else 0.0
	var win := Rect2(PAD, top, size.x - PAD * 2.0, maxf(WINDOW_MIN_H * (0.5 if effect_text != "" else 1.0), plate.position.y - top - PAD * 0.5 - effect_h))
	draw_rect(win, Palette.NIGHT_SKY)
	var icon_r := minf(win.size.x, win.size.y) * ICON_SHARE
	draw_circle(win.get_center(), icon_r * 1.08, Color(AssetIcon.color_of(asset_id), 0.12))
	AssetIcon.draw_icon(self, win.get_center(), icon_r, asset_id, false)
	if effect_text != "":
		var er := effect_rect()
		var pr := er.size.y * 0.42
		var pc := Vector2(er.position.x + pr, er.get_center().y)
		_draw_effect_icon(pc, pr, Palette.INK)
		var tx := pc.x + pr + EFFECT_GAP * s
		var fs := es
		while fs > MIN_NUMBER_SIZE and mono.get_string_size(effect_text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > er.end.x - tx:
			fs -= 1
		draw_string(mono, Vector2(tx, er.get_center().y + mono.get_ascent(fs) * 0.5 - mono.get_descent(fs) * 0.25), effect_text, HORIZONTAL_ALIGNMENT_LEFT, er.end.x - tx, fs, Palette.INK)
	if disabled:
		draw_rect(Rect2(0, 0, size.x, plate.position.y), DISABLED_SHADE)
	draw_rect(plate, Palette.INK)
	# H23 S5: the numbers in words ("HP 10", "1 LEFT"; "10" and "x1" were unexplained),
	# translated (H23 S16) and a size smaller while both don't fit the plate.
	var it := integrity_text()
	var ct := count_text()
	while (num > MIN_NUMBER_SIZE or cs > MIN_NUMBER_SIZE) and mono.get_string_size(it, HORIZONTAL_ALIGNMENT_LEFT, -1, num).x \
			+ Palette.marker().get_string_size(ct, HORIZONTAL_ALIGNMENT_LEFT, -1, cs).x + PAD * 3.0 > size.x:
		num = maxi(MIN_NUMBER_SIZE, num - 1)
		cs = maxi(MIN_NUMBER_SIZE, cs - 1)
	var base_y := plate.get_center().y + mono.get_ascent(num) * 0.5 - mono.get_descent(num) * 0.25
	draw_string(mono, Vector2(PAD, base_y), it, HORIZONTAL_ALIGNMENT_LEFT, -1, num, Palette.PAPER)
	var cw := Palette.marker().get_string_size(ct, HORIZONTAL_ALIGNMENT_LEFT, -1, cs).x
	draw_string(Palette.marker(), Vector2(size.x - PAD - cw, base_y), ct, HORIZONTAL_ALIGNMENT_LEFT, -1, cs, Palette.CELL_PINK)


## The least lettering of the numbers' plate (px).
const MIN_NUMBER_SIZE := 9
## The effect line's lettering at text scale 1.0 and the gap after its pictogram (px).
const EFFECT_SIZE := 10
const EFFECT_GAP := 3.0

## H24 S14: what the asset does (the defence cards had no words for it): a pictogram kind
## ("shoot", "hold", "lure") and a one-line effect in the player's language.
var effect_kind: String = ""
var effect_text: String = ""


## Sets the card's effect line from the asset's data (`effect_of`).
func set_effect(data: DefenseAssetData) -> void:
	var e := effect_of(data)
	effect_kind = e[0]
	effect_text = e[1]
	queue_redraw()


## An asset's effect as [pictogram kind, words] from its numbers: a gun "HITS 4 x2 · REACH
## 1", an ICE lock "HOLDS 2 STEPS", a decoy "LURES, PULL 3"; ["", ""] for none.
static func effect_of(data: DefenseAssetData) -> Array[String]:
	if data == null:
		return ["", ""] as Array[String]
	if data.damage > 0:
		var t := TranslationServer.translate("HITS %d") % data.damage
		if data.shots_per_step > 1:
			t += " x%d" % data.shots_per_step
		if data.range_hops > 0:
			t += TranslationServer.translate(" · REACH %d") % data.range_hops
		return ["shoot", t] as Array[String]
	if data.delay_steps > 0:
		return ["hold", TranslationServer.translate("HOLDS %d STEPS") % data.delay_steps] as Array[String]
	if data.decoy_pull > 0:
		return ["lure", TranslationServer.translate("LURES, PULL %d") % data.decoy_pull] as Array[String]
	return ["", ""] as Array[String]


## The effect line's rect (local): between the icon window and the numbers' plate.
func effect_rect() -> Rect2:
	if effect_text == "":
		return Rect2()
	var s := Settings.text_scale
	var mono := Palette.mono()
	var num := roundi(NUMBER_SIZE * s)
	var cs := roundi(COUNT_SIZE * s)
	var plate_h := maxf(mono.get_height(num), Palette.marker().get_height(cs)) + PAD * 0.5
	var h := mono.get_height(roundi(EFFECT_SIZE * s))
	return Rect2(PAD, size.y - plate_h - PAD * 0.25 - h, size.x - PAD * 2.0, h)


## The effect's pictogram: crosshair (it shoots), snowflake (it holds threats), a lure
## (arrows drawn to a point: it pulls their routes). StatIcon's own where one fits.
func _draw_effect_icon(c: Vector2, r: float, col: Color) -> void:
	match effect_kind:
		"shoot":
			StatIcon.draw(self, c, r, StatIcon.FIGHT, col)
		"hold":
			StatIcon.draw(self, c, r, StatIcon.ICE, col)
		"lure":
			draw_circle(c, r * 0.25, col)
			for k in 4:
				var a := PI * 0.25 + k * PI * 0.5
				var from := c + Vector2(cos(a), sin(a)) * r
				var to := c + Vector2(cos(a), sin(a)) * r * 0.45
				draw_line(from, to, col, 1.5)
				var side := Vector2(-sin(a), cos(a)) * r * 0.22
				draw_colored_polygon(PackedVector2Array([to, to + (from - to).normalized() * r * 0.3 + side, to + (from - to).normalized() * r * 0.3 - side]), col)


## The integrity as the card writes it ("HP 10"), in the player's language.
func integrity_text() -> String:
	return "%s %d" % [tr("HP"), integrity]


## How many sit in the Armory as the card writes it ("1 LEFT"), in the player's language.
func count_text() -> String:
	return "%d %s" % [count, tr("LEFT")]


## What the card's numbers mean (its tooltip adds this under the asset's description).
func numbers_tip() -> String:
	return tr("HP %d: the hits it takes before it breaks. %d LEFT: in the Armory to deploy.") % [integrity, count]
