class_name RaidIntelStrip
extends Control
## ART-6 3A: THREAT INTEL's scanned threats (ART_BIBLE v2 §4.8 "scanned vehicle silhouettes";
## round 20 `ui20.intel_holo`): each threat type the raid sends as its v4 icon, scanlined in
## the holo, with its route letter and name under it ("A1 HAULER"). View only.

## The icon radius and the column width (px at 1.0), the caption gap and scanline pitch.
const ICON_R := 9.0
const COLUMN := 82.0
const CAPTION_GAP := 4.0
const SCAN_PITCH := 3.0

## Parity RAID-03: the width at the right the strip leaves free (px; the holo's DECRYPTED stamp).
var reserve_right: float = 0.0:
	set(v):
		reserve_right = v
		queue_redraw()
## [{type, name, letter}] in route order.
var units: Array[Dictionary] = []
var corporation_id: StringName = &""


func _init(p_corporation: StringName = &"", p_units: Array[Dictionary] = []) -> void:
	corporation_id = p_corporation
	units = p_units
	name = "IntelStrip"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_k = Settings.text_scale
	var k := _k
	var f := Palette.mono()
	var px := UiTheme.font_px_at(UiTheme.CAPTION, k)
	custom_minimum_size = Vector2(0, (ICON_R * RaidVehicle.RING * 2.0 + CAPTION_GAP) * k + f.get_height(px))


## M14 BIG-TEXT b: the text scale the strip was built at (a fit box may build it smaller than the
## player's): it draws at the size it measured.
var _k: float = 1.0


func _draw() -> void:
	var k := _k
	var f := Palette.mono()
	var px := UiTheme.font_px_at(UiTheme.CAPTION, k)
	var col_w := COLUMN * k
	var per_row := maxi(1, floori(maxf(0.0, size.x - reserve_right) / col_w))
	var r := ICON_R * k
	var skin := RaidSkin.of(corporation_id)
	for i in mini(units.size(), per_row):
		var u: Dictionary = units[i]
		var cx := col_w * (i + 0.5)
		var c := Vector2(cx, r * RaidVehicle.RING)
		RaidVehicle.draw(self, c, r, String(u.get("type", RaidVehicle.HEAVY)), corporation_id, 1.0, [], NAN, 0.0, 0.9)
		var y := c.y - r * RaidVehicle.RING
		while y < c.y + r * RaidVehicle.RING:
			draw_line(Vector2(cx - r * 2.2, y), Vector2(cx + r * 2.2, y), Color(Palette.NIGHT_SKY, 0.3), 1.0)
			y += SCAN_PITCH
		var cap := "%s %s" % [String(u.get("letter", "")), String(u.get("name", ""))]
		var w := minf(f.get_string_size(cap, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x, col_w - 4.0)
		HighContrast.draw_text(self, f, Vector2(cx - w * 0.5, c.y + r * RaidVehicle.RING + CAPTION_GAP * k + f.get_ascent(px)), cap, HORIZONTAL_ALIGNMENT_LEFT, col_w - 4.0, px,
			skin.holo.lerp(Palette.TEXT_HI, 0.35))
