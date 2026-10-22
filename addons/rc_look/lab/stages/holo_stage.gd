extends RcLookLabStage
## LOOK-TOOLBOX module 15 in the lab: the decrypted holo (the game's DecryptedHoloPanel, which is RcLookHolo) over a
## busy stand-in city so the translucency, the blur, the scan bands, the edge split and the cracked seal are all
## judged against something. Day and night change the city's brightness; the quality state drives the holo's rules.

## City stand-in: block grid cell (px at 1080p), the block colours' brightness by time, and the seed of the layout.
const CELL := Vector2(54.0, 40.0)
const CITY_SEED := 11
const CITY_NEON := [Color(1.0, 0.2, 0.7), Color(0.2, 0.9, 1.0), Color(1.0, 0.75, 0.15)]
const DAY_LIFT := 0.5
const NIGHT_LIFT := 0.22
## Panels: (corp colour, position, size). Meridian (orange, the concept's), Solace (the green that read as a terminal).
const PANELS := [
	{"tint": Palette.CORP_MERIDIAN, "at": Vector2(110.0, 150.0), "size": Vector2(560.0, 300.0), "corp": &"meridian", "title": "THREAT INTEL // SCAN"},
	{"tint": Palette.CORP_SOLACE, "at": Vector2(740.0, 150.0), "size": Vector2(560.0, 300.0), "corp": &"solace", "title": "SITE FILE // SOLACE"},
	{"tint": Palette.CORP_HALCYON, "at": Vector2(1330.0, 150.0), "size": Vector2(480.0, 300.0), "corp": &"halcyon", "title": "THREAT INTEL // SCAN"},
]
const TITLE_PX := 26
const BODY_PX := 17
const BODY_LINES := ["COLLECTOR   > HOME SERVER   T1 SITE", "COLLECTOR   > HOME SERVER   T1 SITE", "HAULER + COURIER   > weakest node", "DECRYPTED BY THE CELL  //  KEY 4C-E7"]
const TEXT_PAD := Vector2(24.0, 22.0)
const LINE_GAP := 34.0

var _city: Control
var _panels: Array[DecryptedHoloPanel] = []
var _lift := DAY_LIFT


func _ready() -> void:
	_city = Control.new()
	_city.set_anchors_preset(Control.PRESET_FULL_RECT)
	_city.draw.connect(_draw_city)
	add_child(_city)
	for p: Dictionary in PANELS:
		var h := DecryptedHoloPanel.new()
		h.scrim = false
		h.corp_color = p["tint"]
		h.corporation = p["corp"]
		h.position = p["at"]
		h.size = p["size"]
		h.seal_letter = String(p["corp"]).left(1).to_upper()
		add_child(h)
		var title := Label.new()
		title.text = p["title"]
		title.position = TEXT_PAD
		title.add_theme_font_size_override(&"font_size", TITLE_PX)
		title.add_theme_color_override(&"font_color", DecryptedHoloPanel.ink(p["tint"]))
		h.content.add_child(title)
		for i in BODY_LINES.size():
			var l := Label.new()
			l.text = BODY_LINES[i]
			l.position = TEXT_PAD + Vector2(0.0, 60.0 + i * LINE_GAP)
			l.add_theme_font_size_override(&"font_size", BODY_PX)
			l.add_theme_color_override(&"font_color", DecryptedHoloPanel.ink(p["tint"]))
			h.content.add_child(l)
		_panels.append(h)


func apply(time: StringName, quality: RcLookQualityState) -> void:
	_lift = NIGHT_LIFT if time == &"night" else DAY_LIFT
	_city.queue_redraw()
	for h in _panels:
		h.state_override = quality


func settle_frames() -> int:
	return 12


func _draw_city() -> void:
	var cols := int(size.x / CELL.x) + 1
	var rows := int(size.y / CELL.y) + 1
	for y in rows:
		for x in cols:
			var h := RcLookHolo.hash01(CITY_SEED + x * 31, y)
			var base := Color(h * 0.35, h * 0.3, 0.2 + h * 0.4) * _lift * 1.6
			base.a = 1.0
			_city.draw_rect(Rect2(Vector2(x, y) * CELL, CELL - Vector2(4.0, 4.0)), base)
			if h > 0.8:
				var n: Color = CITY_NEON[int(h * 100.0) % CITY_NEON.size()]
				_city.draw_rect(Rect2(Vector2(x, y) * CELL + Vector2(6.0, 6.0), Vector2(CELL.x - 16.0, 6.0)), n * (_lift * 2.2))
