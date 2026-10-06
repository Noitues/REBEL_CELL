class_name RaidHolo
extends PanelContainer
## ART-6 3A: hacked corp intel as a decrypted holo (ART_BIBLE v2 §1.2 "Decrypted holo",
## §4.8 THREAT INTEL), on 1B's DecryptedHoloPanel: the raiding corp's tint at about 78 %,
## 4 px scanlines, its slow bands, the RGB split on the edge only, the corp seal cracked by a
## red fracture and the DECRYPTED stamp. A container (the raid's column lays it out): the
## holo is its backdrop, its words are Labels in `body` under the header (the title, the
## corp's net and the Cell's key). Its scrim is local (a panel beside the map, not a modal):
## the holo's own 0.88 backing (B1c, D17).

const KEY_LINE := "DECRYPTED BY THE CELL  //  KEY %s" # TR
## The header's height (px at 1.0) and the room round the words.
const HEAD_H := 64.0
const PAD := 12.0
## Parity RAID-03: the DECRYPTED stamp sits at the holo's foot, on the seal at the right, never
## over the header's words (the title, the corp's net, the key) or a route row: the scanned
## threats strip leaves it its width, and without the strip the holo's foot keeps its height.
## The gap round it (px at 1.0).
const STAMP_GAP := 2.0

var skin: RaidSkin
var title: String = ""
var key: String = ""
var body: VBoxContainer
var holo: DecryptedHoloPanel
var _k: float = 1.0


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
	holo = DecryptedHoloPanel.new()
	holo.name = "Holo"
	holo.scrim = false
	holo.corp_color = skin.hue
	holo.seal_letter = skin.corp_name().left(1)
	holo.corporation = p_corporation  # B1c (D17): the seal carries the corp's emblem, cracked
	holo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(holo, false, Node.INTERNAL_MODE_FRONT)
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
	l.add_theme_color_override("font_color", col if col.a > 0.0 else DecryptedHoloPanel.ink(skin.holo))  # B1c-b: the tint on the words
	UiWrap.whole_words(l)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(l)
	return l


func _notification(what: int) -> void:
	if (what == NOTIFICATION_RESIZED or what == NOTIFICATION_SORT_CHILDREN) and holo != null:  # after the container fitted it
		holo.position = Vector2.ZERO
		holo.size = size
		_place_stamp()
		if _head != null:
			_head.position = Vector2.ZERO
			_head.size = size
			_head.queue_redraw()
		queue_redraw()


var _head: Control = null


## Parity RAID-03: where the header's words end (local y): the title, the corp's net, the key.
func head_bottom() -> float:
	var f := Palette.display()
	var mono := Palette.mono()
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
	return PAD * 0.5 * _k + f.get_height(UiTheme.font_px(UiTheme.LABEL)) + mono.get_height(meta_px) * (2.0 if key != "" else 1.0)


## Parity RAID-03: the stamp's slot at the holo's foot, at the right (the holo puts it top
## right, over the title and the key).
func _place_stamp() -> void:
	if holo == null or holo.stamp_slot == null:
		return
	var slot := holo.stamp_slot
	slot.position = Vector2(size.x - slot.size.x - UiTheme.SP_M, size.y - slot.size.y - UiTheme.SP_S)


## Parity RAID-03: the foot keeps the stamp's height under the rows (less what the scanned
## threats strip already takes beside it); the strip leaves the stamp its width.
func _fit_stamp(_n: Node = null) -> void:
	var strip: RaidIntelStrip = null
	for c in body.get_children():
		if c is RaidIntelStrip and not c.is_queued_for_deletion():
			strip = c
	var slot_h := DecryptedHoloPanel.STAMP_SLOT.y + UiTheme.SP_S + STAMP_GAP * _k
	var foot := slot_h
	if strip != null:
		strip.reserve_right = DecryptedHoloPanel.STAMP_SLOT.x + UiTheme.SP_M - PAD * _k
		foot = 0.0  # beside the strip (the strip's height is about the stamp's)
	var box := get_theme_stylebox(&"panel") as StyleBoxEmpty
	if box != null and not is_equal_approx(box.content_margin_bottom, PAD * _k + foot):
		box.content_margin_bottom = PAD * _k + foot
		queue_sort()


## The DECRYPTED stamp's rect (local).
func stamp_rect() -> Rect2:
	if holo == null or holo.stamp_slot == null:
		return Rect2()
	return Rect2(holo.stamp_slot.position, holo.stamp_slot.size)


## The header's words, drawn over the holo (the panel's own children draw after it).
func _header(on: Control) -> void:
	var k := _k
	var f := Palette.display()
	var title_px := UiTheme.font_px(UiTheme.LABEL)
	var x := PAD * k
	var room := size.x - x * 2.0  # parity RAID-03: the stamp is under the words now
	on.draw_string(f, Vector2(x, PAD * 0.5 * k + f.get_ascent(title_px)), title, HORIZONTAL_ALIGNMENT_LEFT, room, title_px, DecryptedHoloPanel.ink(skin.holo))
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
	var mono := Palette.mono()
	var line_y := PAD * 0.5 * k + f.get_height(title_px) + mono.get_ascent(meta_px)
	on.draw_string(mono, Vector2(x, line_y), skin.corp_name(), HORIZONTAL_ALIGNMENT_LEFT, room, meta_px, DecryptedHoloPanel.ink(skin.holo))
	if key != "":
		on.draw_string(mono, Vector2(x, line_y + mono.get_height(meta_px)), tr(KEY_LINE) % key, HORIZONTAL_ALIGNMENT_LEFT, size.x - x * 2.0, meta_px, Palette.GAIN)


func _ready() -> void:
	var head := Control.new()
	head.name = "Header"
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	head.draw.connect(_header.bind(head))
	holo.resized.connect(_place_stamp)
	body.child_entered_tree.connect(_fit_stamp)
	body.child_exiting_tree.connect(_fit_stamp)
	_fit_stamp()
	add_child(head, false, Node.INTERNAL_MODE_BACK)
	_head = head


## The Cell's decryption key for raid `raid_id` ("7F-A2"; a hash, never an RNG).
static func key_of(raid_id: StringName) -> String:
	var h := absi(hash(String(raid_id)))
	return "%02X-%02X" % [h % 256, (h / 256) % 256]
