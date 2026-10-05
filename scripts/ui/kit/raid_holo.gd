class_name RaidHolo
extends PanelContainer
## ART-6 3A: hacked corp intel as a decrypted holo (ART_BIBLE v2 §1.2 "Decrypted holo",
## §4.8 THREAT INTEL): the raiding corp's tint at about 78 % over a near-opaque scrim (0.88),
## 4 px scanlines, 3-4 slow bands, a +-2 px RGB split on the edge only, and the corp seal
## cracked by a red fracture under a DECRYPTED stamp. Ported from art-concepts-r43 round 21
## `ui21.intel_holo` / `seal_overlay` and round 19 `ui19.holo`.
##
## Words are Labels in `body`; the plate, scanlines, bands, edge split, seal and stamp are
## drawn. The bands drift with `raid_holo_band` (a T0 loop; still under reduce effects, where
## the static scanlines stay, §5.4). Seam: 1B's holo material replaces `_draw`'s plate.

const STAMP_DECRYPTED := "DECRYPTED" # TR
const KEY_LINE := "DECRYPTED BY THE CELL  //  KEY %s" # TR
const BAND_MOTION := &"raid_holo_band"

## The scrim behind the holo (§1.2: near opaque) and how far it reaches past the plate (px).
const SCRIM_ALPHA := 0.88
const SCRIM_OUT := 4.0
## The plate: the corp tint's alpha over the scrim, the scanline pitch (px, §1.2: 4 px) and
## their darkness, the bands (count, height share, alpha).
const PLATE_ALPHA := 0.2
const SCAN_PITCH := 4.0
const SCAN_ALPHA := 0.22
const BANDS := 3
const BAND_H := 0.1
const BAND_ALPHA := 0.1
## The edge's RGB split (px, §1.2: +-2 px, the edge only) and its alpha.
const SPLIT := 2.0
const SPLIT_ALPHA := 0.55
## The header: its height (px at 1.0), the seal's radius in it.
const HEAD_H := 58.0
const SEAL_R := 21.0
const PAD := 12.0
## The DECRYPTED stamp: Anton size (px at 1.0) and tilt (degrees).
const STAMP_PX := 22
const STAMP_TILT := -10.0
## The stamp's centre from the plate's right edge (px at 1.0).
const STAMP_RIGHT := 62.0

var skin: RaidSkin
var title: String = ""
var key: String = ""
var body: VBoxContainer
var _k: float = 1.0
var _t: float = 0.0


func _init(p_corporation: StringName = &"halcyon", p_title: String = "", p_key: String = "") -> void:
	skin = RaidSkin.of(p_corporation)
	title = p_title
	key = p_key
	_k = Settings.text_scale
	name = "RaidHolo"
	mouse_filter = Control.MOUSE_FILTER_PASS
	var box := StyleBoxEmpty.new()
	box.content_margin_left = PAD * _k
	box.content_margin_right = PAD * _k
	box.content_margin_top = HEAD_H * _k
	box.content_margin_bottom = PAD * _k
	add_theme_stylebox_override("panel", box)
	body = VBoxContainer.new()
	body.name = "HoloBody"
	body.add_theme_constant_override("separation", roundi(4 * _k))
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(body)


## A line of holo text (terminal face) in the holo's colour (or `col`).
func add_line(text: String, col: Color = Palette.AUTO, step: int = UiTheme.CAPTION) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", Palette.mono())
	l.add_theme_font_size_override("font_size", UiTheme.font_px(step))
	l.add_theme_color_override("font_color", col if col.a > 0.0 else skin.holo.lerp(Palette.TEXT_HI, 0.35))
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(l)
	return l


func _process(delta: float) -> void:
	if Motion.live(BAND_MOTION):
		_t += delta
		queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var k := _k
	var tint := skin.holo
	draw_rect(r.grow(SCRIM_OUT * k), Color(Palette.NIGHT_SKY, SCRIM_ALPHA))
	# 1A's HoloPanel plate (the corp tint at HOLO_TINT over the night, its glowing edge).
	draw_style_box(UiTheme.holo_box(tint), r)
	draw_rect(r, Color(tint, PLATE_ALPHA * 0.5))
	# Slow bands drifting down (still under reduce effects).
	var period := maxf(0.001, Motion.seconds(BAND_MOTION)) if Motion.live(BAND_MOTION) else 0.0
	for b in BANDS:
		var u := fposmod((b / float(BANDS)) + (_t / period if period > 0.0 else 0.0), 1.0)
		var h := r.size.y * BAND_H
		draw_rect(Rect2(0, u * (r.size.y + h) - h, r.size.x, h), Color(tint, BAND_ALPHA))
	var y := 0.0
	while y < r.size.y:
		draw_line(Vector2(0, y), Vector2(r.size.x, y), Color(Palette.NIGHT_SKY, SCAN_ALPHA), 1.0)
		y += SCAN_PITCH
	# The edge: a red copy left, a cyan copy right, the corp edge on top (§1.2: edge only).
	draw_rect(r.grow(-1.0).grow_individual(SPLIT, 0, -SPLIT, 0), Color(Palette.HARM, SPLIT_ALPHA), false, 1.5 * k)
	draw_rect(r.grow(-1.0).grow_individual(-SPLIT, 0, SPLIT, 0), Color(Palette.NET_CYAN, SPLIT_ALPHA), false, 1.5 * k)
	draw_rect(r.grow(-1.0), tint, false, 1.5 * k)
	# The header: the cracked seal, the title, the corp's net and the Cell's key.
	var seal_c := Vector2(PAD + SEAL_R, PAD * 0.4 + SEAL_R) * k
	RaidPaper.draw_seal(self, seal_c, SEAL_R * k, tint, true, skin.corporation_id)
	var x := seal_c.x + (SEAL_R + 8.0) * k
	var title_px := UiTheme.font_px(UiTheme.LABEL)
	var f := Palette.display()
	draw_string(f, Vector2(x, PAD * 0.5 * k + f.get_ascent(title_px)), title, HORIZONTAL_ALIGNMENT_LEFT, r.size.x - x - PAD * k, title_px, tint.lerp(Palette.TEXT_HI, 0.2))
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
	var mono := Palette.mono()
	var line_y := PAD * 0.5 * k + f.get_height(title_px) + mono.get_ascent(meta_px)
	draw_string(mono, Vector2(x, line_y), skin.corp_name(), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - x - PAD * k, meta_px, tint.lerp(Palette.TEXT_HI, 0.3))
	if key != "":
		draw_string(mono, Vector2(x, line_y + mono.get_height(meta_px)), tr(KEY_LINE) % key, HORIZONTAL_ALIGNMENT_LEFT, r.size.x - x - PAD * k, meta_px, Palette.GAIN)
	RaidPaper.draw_stamp(self, Vector2(r.size.x - STAMP_RIGHT * k, HEAD_H * 0.42 * k), tr(STAMP_DECRYPTED), roundi(STAMP_PX * k), Palette.GAIN, deg_to_rad(STAMP_TILT))


## The Cell's decryption key for raid `raid_id` ("7F-A2"; a hash, never an RNG).
static func key_of(raid_id: StringName) -> String:
	var h := absi(hash(String(raid_id)))
	return "%02X-%02X" % [h % 256, (h / 256) % 256]
