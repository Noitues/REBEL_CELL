class_name AssetIcon
extends RefCounted
## Line icons for defence assets (reference: the raid DEFENSE LOADOUT cards), drawn on
## any CanvasItem so the raid board and the loadout cards share them. Unknown assets get
## a plain square.

const COLORS := {&"turret": Color("#5CE1FF"), &"sentry": Color("#3DFF8B"), &"railgun": Color("#FF3DA8"),
	&"flak_array": Color("#FFB000"), &"ice_lock": Color("#8FE8FF"), &"tar_pit": Color("#B04DFF"),
	&"decoy": Color("#FFD24D"), &"honeypot_node": Color("#FF8C1A")}


static func color_of(asset_id: StringName) -> Color:
	return COLORS.get(asset_id, Palette.NET_CYAN)


## Draws `asset_id`'s icon centred on `c`, `r` = half size.
static func draw_icon(ci: CanvasItem, c: Vector2, r: float, asset_id: StringName, backed: bool = true) -> void:
	var col := color_of(asset_id)
	if backed:
		ci.draw_circle(c, r * 1.25, Color(Palette.NIGHT_SKY, 0.9))
		ci.draw_arc(c, r * 1.25, 0, TAU, 20, col, 1.2)
	var w := maxf(1.2, r * 0.16)
	match asset_id:
		&"turret", &"sentry", &"railgun":
			# Tripod legs, a body and a barrel (longer for the railgun, an eye for sentry).
			ci.draw_line(c + Vector2(0, r * 0.1), c + Vector2(-r * 0.7, r * 0.8), col, w)
			ci.draw_line(c + Vector2(0, r * 0.1), c + Vector2(r * 0.7, r * 0.8), col, w)
			ci.draw_rect(Rect2(c + Vector2(-r * 0.45, -r * 0.35), Vector2(r * 0.9, r * 0.5)), col)
			var barrel := r * (1.2 if asset_id == &"railgun" else 0.8)
			ci.draw_line(c + Vector2(r * 0.3, -r * 0.15), c + Vector2(r * 0.3 + barrel, -r * 0.45), col, w * 1.3)
			if asset_id == &"sentry":
				ci.draw_circle(c + Vector2(0, -r * 0.1), r * 0.18, Palette.NIGHT_SKY)
		&"flak_array":
			for k in 8:
				var a := TAU * k / 8.0
				ci.draw_line(c + Vector2(cos(a), sin(a)) * r * 0.3, c + Vector2(cos(a), sin(a)) * r * 0.85, col, w)
			ci.draw_circle(c, r * 0.22, col)
		&"ice_lock":
			var cube := PackedVector2Array([c + Vector2(0, -r * 0.8), c + Vector2(r * 0.7, -r * 0.4), c + Vector2(r * 0.7, r * 0.4), c + Vector2(0, r * 0.8), c + Vector2(-r * 0.7, r * 0.4), c + Vector2(-r * 0.7, -r * 0.4), c + Vector2(0, -r * 0.8)])
			ci.draw_polyline(cube, col, w)
			ci.draw_line(c + Vector2(-r * 0.7, -r * 0.4), c, col, w)
			ci.draw_line(c + Vector2(r * 0.7, -r * 0.4), c, col, w)
			ci.draw_line(c, c + Vector2(0, r * 0.8), col, w)
		&"tar_pit":
			for k in 3:
				var y := -r * 0.4 + k * r * 0.4
				var pts := PackedVector2Array()
				for m in 7:
					pts.append(c + Vector2(-r * 0.8 + m * r * 0.27, y + sin(m * 1.6) * r * 0.12))
				ci.draw_polyline(pts, col, w)
		&"decoy":
			var dia := PackedVector2Array([c + Vector2(0, -r * 0.85), c + Vector2(r * 0.6, 0), c + Vector2(0, r * 0.85), c + Vector2(-r * 0.6, 0), c + Vector2(0, -r * 0.85)])
			ci.draw_polyline(dia, col, w)
			ci.draw_circle(c, r * 0.18, col)
		&"honeypot_node":
			var hexa := PackedVector2Array()
			for k in 7:
				hexa.append(c + Vector2(cos(TAU * k / 6.0), sin(TAU * k / 6.0)) * r * 0.75)
			ci.draw_polyline(hexa, col, w)
			ci.draw_circle(c, r * 0.28, col)
		_:
			ci.draw_rect(Rect2(c - Vector2(r * 0.6, r * 0.6), Vector2(r * 1.2, r * 1.2)), col, false, w)
