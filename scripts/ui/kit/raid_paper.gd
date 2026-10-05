class_name RaidPaper
extends PanelContainer
## ART-6 3A: an intercepted corp document (ART_BIBLE v2 §1.2 "Corp paper", §4.8): the raid's
## work order (RAID INCOMING, stamped INTERCEPTED) and the after-action raid report (stamped
## CLASSIFIED). Paper stock with a faint grain, the raiding corp's letterhead (its seal, name
## and division line, a rule in its hue), Courier fields, redacted lines and the footer meta,
## a paper clip, and an Anton rubber stamp. Ported from art-concepts-r43 round 20-21
## `ui19.dossier`, `ui20.memo_glass`, `ui21.report_doc`.
##
## The words are real Labels (translated, measured, laid out at every text scale); the paper,
## seal, redactions, clip and stamp are drawn. Put rows in `body` (`add_row`). Seam: 1B's
## corp paper panel material replaces `_draw`'s stock (DECISIONS "Art direction — ART-6 3A").

## Rubber stamp words (translated when drawn).
const STAMP_INTERCEPTED := "INTERCEPTED" # TR
const STAMP_CLASSIFIED := "CLASSIFIED" # TR
## The footer meta line (round 21).
const FOOTER := "%s  //  INTERNAL  //  DO NOT FORWARD" # TR

## The letterhead's height (px at text scale 1.0) and the seal's radius in it.
const LETTERHEAD_H := 46.0
const SEAL_R := 15.0
## Margins (px at 1.0): sides, top under the clip, and the footer's room (redactions + meta).
const PAD := 14.0
const FOOTER_H := 46.0
## Redacted bars: rows, height, the share of the width they run to.
const REDACT_ROWS := 2
const REDACT_H := 6.0
const REDACT_SPAN := 0.62
## Paper grain: specks per 10 000 px² and their alpha.
const GRAIN_DENSITY := 6.0
const GRAIN_ALPHA := 0.08
## The rubber stamp: Anton size (px at 1.0), tilt (degrees), ink alpha, box padding.
const STAMP_PX := 26
const STAMP_TILT := -9.0
const STAMP_ALPHA := 0.78
const STAMP_PAD := 6.0
## The paper clip at the top left (px at 1.0): its x, width and height.
const CLIP_X := 34.0
const CLIP_W := 13.0
const CLIP_H := 34.0
## The page's own tilt (degrees): stolen paper is never square.
const PAGE_TILT := 0.0

var skin: RaidSkin
var stamp_word: String = STAMP_INTERCEPTED
## The document's number on its footer and letterhead ("WO 50-HC-114").
var number: String = ""
## Where the stamp sits, as a share of the page (its centre).
var stamp_at: Vector2 = Vector2(0.74, 0.91)
var body: VBoxContainer
var title_label: Label
var sub_label: Label
var _k: float = 1.0


func _init(p_corporation: StringName = &"halcyon", p_title: String = "", p_stamp: String = STAMP_INTERCEPTED, p_number: String = "") -> void:
	skin = RaidSkin.of(p_corporation)
	stamp_word = p_stamp
	number = p_number
	_k = Settings.text_scale
	name = "RaidPaper"
	mouse_filter = Control.MOUSE_FILTER_PASS
	var box := StyleBoxEmpty.new()
	box.content_margin_left = PAD * _k
	box.content_margin_right = PAD * _k
	box.content_margin_top = (LETTERHEAD_H + PAD * 0.5) * _k
	box.content_margin_bottom = FOOTER_H * _k
	add_theme_stylebox_override("panel", box)
	body = VBoxContainer.new()
	body.name = "PaperBody"
	body.add_theme_constant_override("separation", roundi(2 * _k))
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(body)
	title_label = Label.new()
	title_label.name = "PaperTitle"
	title_label.text = p_title
	title_label.add_theme_font_override("font", Palette.display())
	title_label.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.TITLE))
	title_label.add_theme_color_override("font_color", Palette.INK)
	title_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.add_child(title_label)
	sub_label = Label.new()
	sub_label.name = "PaperSub"
	sub_label.add_theme_font_override("font", Palette.paper())
	sub_label.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	sub_label.add_theme_color_override("font_color", Palette.INK.lerp(Palette.PAPER, 0.42))
	sub_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sub_label.visible = false
	body.add_child(sub_label)


## Sets the small line under the title ("MERIDIAN FREIGHT // WORK ORDER 52-MF-114").
func set_sub(text: String) -> void:
	sub_label.text = text
	sub_label.visible = text != ""


## Adds a field row: `label` on the left in the paper face, `value` on the right in Anton,
## in ink (or HARM_INK for a loss, GAIN_INK for a gain). Returns the value's Label (named
## `value_name` when given) so a view can find it.
func add_row(label: String, value: String, value_col: Color = Palette.INK, value_name: String = "") -> Label:
	var row := HBoxContainer.new()
	row.name = "Row_%d" % body.get_child_count()
	row.add_theme_constant_override("separation", roundi(8 * _k))
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var l := Label.new()
	l.text = label
	l.add_theme_font_override("font", Palette.paper())
	l.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	l.add_theme_color_override("font_color", Palette.INK.lerp(Palette.PAPER, 0.3))
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = 60.0 * _k
	row.add_child(l)
	var v := Label.new()
	if value_name != "":
		v.name = value_name
	v.text = value
	v.add_theme_font_override("font", Palette.display())
	v.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.BODY))
	v.add_theme_color_override("font_color", value_col)
	v.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	v.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(v)
	body.add_child(row)
	var rule := HSeparator.new()
	rule.add_theme_stylebox_override("separator", _rule_box())
	rule.add_theme_constant_override("separation", 0)
	rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(rule)
	return v


func _rule_box() -> StyleBoxLine:
	var s := StyleBoxLine.new()
	s.color = Palette.PAPER_ALT.darkened(0.12)
	s.thickness = 1
	return s


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var k := _k
	# A soft drop shadow, then the stock.
	draw_rect(Rect2(r.position + Vector2(5, 7) * k, r.size), Color(Palette.NIGHT_SKY, 0.55))
	draw_rect(r, Palette.NOTE_PAPER)
	_grain(r)
	# The letterhead: seal, corp name, division, and the rule in the corp's ink.
	var seal_c := Vector2(PAD + SEAL_R, PAD * 0.6 + SEAL_R) * k
	draw_seal(self, seal_c, SEAL_R * k, skin.paper_hue, false, skin.corporation_id)
	var head_font := Palette.display()
	var head_px := UiTheme.font_px(UiTheme.LABEL)
	var x := seal_c.x + (SEAL_R + 8.0) * k
	draw_string(head_font, Vector2(x, seal_c.y - 1.0 * k), skin.corp_name(), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - x - PAD * k, head_px, skin.paper_hue)
	var meta_font := Palette.paper()
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
	draw_string(meta_font, Vector2(x, seal_c.y + meta_px * 0.95), skin.division(), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - x - PAD * k, meta_px,
		Palette.INK.lerp(Palette.PAPER, 0.45))
	var rule_y := LETTERHEAD_H * k
	draw_line(Vector2(PAD * k, rule_y), Vector2(r.size.x - PAD * k, rule_y), skin.paper_hue, 2.0 * k)
	# The footer: redacted lines and the meta line.
	var fy := r.size.y - FOOTER_H * k + 8.0 * k
	for row in REDACT_ROWS:
		var bx := PAD * k
		var i := 0
		while bx < r.size.x * REDACT_SPAN:
			var ln := (34.0 + 26.0 * absf(RaidPencil.noise(row * 31 + 7, i))) * k
			draw_rect(Rect2(bx, fy + row * (REDACT_H + 5.0) * k, ln, REDACT_H * k), Palette.INK)
			bx += ln + (6.0 + 6.0 * absf(RaidPencil.noise(row * 17 + 3, i))) * k
			i += 1
	draw_string(meta_font, Vector2(PAD * k, r.size.y - 7.0 * k), tr(FOOTER) % skin.corp_name(), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - PAD * 2.0 * k, meta_px,
		Palette.INK.lerp(Palette.PAPER, 0.5))
	_clip(k)
	if stamp_word != "":
		draw_stamp(self, Vector2(r.size.x * stamp_at.x, r.size.y * stamp_at.y), tr(stamp_word), roundi(STAMP_PX * k), Palette.HARM_INK, deg_to_rad(STAMP_TILT))


## Paper grain: deterministic specks (a hash, no RNG).
func _grain(r: Rect2) -> void:
	var n := clampi(int(r.get_area() / 10000.0 * GRAIN_DENSITY), 0, 600)
	for i in n:
		var p := Vector2((RaidPencil.noise(41, i) * 0.5 + 0.5) * r.size.x, (RaidPencil.noise(83, i) * 0.5 + 0.5) * r.size.y)
		var s := 1.0 + absf(RaidPencil.noise(5, i)) * 2.0
		draw_rect(Rect2(p, Vector2(s, 1.0)), Color(Palette.INK, GRAIN_ALPHA * absf(RaidPencil.noise(9, i))))


## The paper clip over the top edge.
func _clip(k: float) -> void:
	var x := CLIP_X * k
	var steel := Palette.TEXT_MID
	for j in 2:
		var w := (CLIP_W - j * 4.0) * k
		var h := (CLIP_H - j * 9.0) * k
		var top := (-10.0 + j * 4.0) * k
		var r := Rect2(x - w * 0.5, top, w, h)
		draw_line(r.position + Vector2(0, w * 0.5), Vector2(r.position.x, r.end.y - w * 0.5), Color(Palette.NIGHT_SKY, 0.6), 3.0 * k)
		draw_line(Vector2(r.end.x, r.position.y + w * 0.5), r.end - Vector2(0, w * 0.5), Color(Palette.NIGHT_SKY, 0.6), 3.0 * k)
		draw_arc(Vector2(x, r.position.y + w * 0.5), w * 0.5, PI, TAU, 10, steel, 2.0 * k)
		draw_arc(Vector2(x, r.end.y - w * 0.5), w * 0.5, 0, PI, 10, steel, 2.0 * k)
		draw_line(r.position + Vector2(0, w * 0.5), Vector2(r.position.x, r.end.y - w * 0.5), steel, 2.0 * k)
		draw_line(Vector2(r.end.x, r.position.y + w * 0.5), r.end - Vector2(0, w * 0.5), steel, 2.0 * k)


## An Anton rubber stamp: `word` in a box, tilted `tilt` radians round `c`, in `col` ink.
static func draw_stamp(ci: CanvasItem, c: Vector2, word: String, px: int, col: Color, tilt: float) -> void:
	var f := Palette.display()
	var sz := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var pad := STAMP_PAD * px / float(STAMP_PX)
	var box := Rect2(-sz.x * 0.5 - pad, -sz.y * 0.5 - pad * 0.4, sz.x + pad * 2.0, sz.y + pad * 0.8)
	var ink := Color(col, STAMP_ALPHA)
	ci.draw_set_transform(c, tilt, Vector2.ONE)
	ci.draw_rect(box, ink, false, maxf(2.0, px * 0.12))
	ci.draw_string(f, Vector2(-sz.x * 0.5, -sz.y * 0.5 + f.get_ascent(px)), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, ink)
	# Worn ink: a few paper-coloured nicks across the word.
	for i in 5:
		var p := Vector2(RaidPencil.noise(13, i) * sz.x * 0.5, RaidPencil.noise(29, i) * sz.y * 0.4)
		ci.draw_rect(Rect2(p, Vector2(px * 0.3, px * 0.06)), Color(Palette.NOTE_PAPER, 0.5))
	ci.draw_set_transform(Vector2.ZERO)


## A corp seal at `c` (radius `r`) in `col`: two rings round the corp's crest (§2.4: Meridian
## the crane-A, Solace the helix, Halcyon the EYE, Orbital the ringed planet, REBEL_CELL the
## fist); `cracked` adds the Cell's red fracture through it (DECRYPTED, §1.2).
static func draw_seal(ci: CanvasItem, c: Vector2, r: float, col: Color, cracked: bool, corporation_id: StringName) -> void:
	var w := maxf(1.2, r * 0.1)
	ci.draw_arc(c, r, 0, TAU, 32, col, w * 1.3)
	ci.draw_arc(c, r * 0.76, 0, TAU, 28, col, w * 0.8)
	var s := r * 0.5
	match corporation_id:
		&"meridian":
			# Crane-A: an A frame with its jib and hook.
			ci.draw_line(c + Vector2(-s, s), c + Vector2(0, -s), col, w)
			ci.draw_line(c + Vector2(s, s), c + Vector2(0, -s), col, w)
			ci.draw_line(c + Vector2(-s * 0.5, s * 0.1), c + Vector2(s * 0.5, s * 0.1), col, w)
			ci.draw_line(c + Vector2(0, -s), c + Vector2(s * 1.1, -s * 0.7), col, w)
			ci.draw_line(c + Vector2(s * 1.0, -s * 0.72), c + Vector2(s * 1.0, -s * 0.1), col, w * 0.7)
		&"solace":
			# The helix: two crossing sine strands with rungs.
			var a := PackedVector2Array()
			var b := PackedVector2Array()
			for i in 13:
				var y := -s + 2.0 * s * i / 12.0
				var x := sin(i / 12.0 * TAU) * s * 0.55
				a.append(c + Vector2(x, y))
				b.append(c + Vector2(-x, y))
				if i % 3 == 0:
					ci.draw_line(c + Vector2(x, y), c + Vector2(-x, y), col, w * 0.6)
			ci.draw_polyline(a, col, w)
			ci.draw_polyline(b, col, w)
		&"orbital":
			ci.draw_circle(c, s * 0.55, col)
			ci.draw_set_transform(c, -0.35, Vector2(1.0, 0.36))
			ci.draw_arc(Vector2.ZERO, s * 1.1, 0, TAU, 28, col, w * 1.6)
			ci.draw_set_transform(Vector2.ZERO)
		&"rebel_cell":
			# The raised fist (thumb tucked): a block of knuckles on a wrist.
			ci.draw_rect(Rect2(c + Vector2(-s * 0.6, -s * 0.75), Vector2(s * 1.2, s * 0.85)), col)
			ci.draw_rect(Rect2(c + Vector2(-s * 0.38, s * 0.1), Vector2(s * 0.76, s * 0.75)), col)
			for i in 3:
				ci.draw_line(c + Vector2(-s * 0.6 + s * 0.4 * (i + 1), -s * 0.75), c + Vector2(-s * 0.6 + s * 0.4 * (i + 1), -s * 0.3), Color(Palette.NIGHT_SKY, 0.6), w * 0.5)
		_:
			# Halcyon's EYE: a lens with its pupil, scanning.
			var lid := PackedVector2Array()
			for i in 17:
				var t := float(i) / 16.0
				lid.append(c + Vector2(lerpf(-s * 1.1, s * 1.1, t), -sin(t * PI) * s * 0.62))
			for i in 17:
				var t := float(i) / 16.0
				lid.append(c + Vector2(lerpf(s * 1.1, -s * 1.1, t), sin(t * PI) * s * 0.62))
			ci.draw_polyline(lid, col, w)
			ci.draw_circle(c, s * 0.32, col)
	if cracked:
		var crack := Palette.HARM
		var pts := PackedVector2Array([c + Vector2(0.05, -1.05) * r, c + Vector2(-0.08, -0.4) * r, c + Vector2(0.1, 0.1) * r,
			c + Vector2(-0.06, 0.55) * r, c + Vector2(0.04, 1.05) * r])
		ci.draw_polyline(pts, Color(Palette.NIGHT_SKY, 0.8), w * 2.2)
		ci.draw_polyline(pts, crack, w * 1.2)
		ci.draw_line(c + Vector2(0.1, 0.1) * r, c + Vector2(0.55, 0.3) * r, crack, w * 0.8)
