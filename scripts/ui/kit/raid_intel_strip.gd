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

## [{type, name, letter}] in route order.
var units: Array[Dictionary] = []
var corporation_id: StringName = &""


func _init(p_corporation: StringName = &"", p_units: Array[Dictionary] = []) -> void:
	corporation_id = p_corporation
	units = p_units
	name = "IntelStrip"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var k := Settings.text_scale
	var f := Palette.mono()
	var px := UiTheme.font_px(UiTheme.CAPTION)
	custom_minimum_size = Vector2(0, (ICON_R * RaidVehicle.RING * 2.0 + CAPTION_GAP) * k + f.get_height(px))


func _draw() -> void:
	var k := Settings.text_scale
	var f := Palette.mono()
	var px := UiTheme.font_px(UiTheme.CAPTION)
	var col_w := COLUMN * k
	var per_row := maxi(1, floori(size.x / col_w))
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
		draw_string(f, Vector2(cx - w * 0.5, c.y + r * RaidVehicle.RING + CAPTION_GAP * k + f.get_ascent(px)), cap, HORIZONTAL_ALIGNMENT_LEFT, col_w - 4.0, px,
			skin.holo.lerp(Palette.TEXT_HI, 0.35))
