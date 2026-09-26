class_name RaidBoardView
extends GridMapView
## The raid war table (reference: "Cell Defense Raid Setup"): the Cell's network on a
## dark isometric plate. CORE (home) sits on a pulsing hex pad; claimed nodes are hex
## pads coloured by their projected outcome (holds / breached / seized) with integrity
## and their deployed assets orbiting as icons; corporate entry points blink as warning
## markers and threat routes run toward CORE as moving chevrons. During the playout
## (RaidPlayoutPanel sets `threat_markers`) threats stand on their Sites as corporate
## diamonds. Pure view; clicking a pad emits site_clicked.

## Projected or final result per claimed Site: id -> {before, after, outcome}.
var node_results: Dictionary = {}
var anim_t: float = 0.0
const PAD := 22.0


func _init() -> void:
	super()
	custom_minimum_size = Vector2(1180, 400)


func _process(delta: float) -> void:
	if Settings.reduce_effects or not is_visible_in_tree():
		return
	anim_t += delta
	queue_redraw()


## Isometric layout centred on CORE: map positions become a diamond board.
func _layout_positions() -> void:
	_positions.clear()
	if corp == null or campaign == null:
		return
	# Normalise the map's bounding box onto the plate, then turn it 45 degrees.
	var min_p := Vector2(1e9, 1e9)
	var max_p := Vector2(-1e9, -1e9)
	for s in corp.city_grid.sites:
		if s != null:
			min_p = min_p.min(s.map_position)
			max_p = max_p.max(s.map_position)
	var span := (max_p - min_p).max(Vector2(1, 1))
	var c := Vector2(size.x * 0.5, size.y * 0.52)
	for s in corp.city_grid.sites:
		if s == null:
			continue
		var d := (s.map_position - min_p) / span * 2.0 - Vector2.ONE
		_positions[s.id] = c + Vector2((d.x - d.y) * 0.5 * size.x * 0.4, (d.x + d.y) * 0.5 * size.y * 0.4)


func _draw() -> void:
	if campaign == null or corp == null:
		return
	_layout_positions()
	var corp_col := Palette.corp_color(corp.id)
	var home_id := campaign.grid.home_site_id
	var c := Vector2(size.x * 0.5, size.y * 0.52)
	# The plate: a dark iso diamond with a faint lattice.
	var plate := PackedVector2Array([c + Vector2(0, -size.y * 0.5), c + Vector2(size.x * 0.49, 0), c + Vector2(0, size.y * 0.5), c + Vector2(-size.x * 0.49, 0)])
	# Slab thickness under the front edges, then the top.
	var drop := Vector2(0, 14)
	draw_colored_polygon(PackedVector2Array([plate[3], plate[2], plate[2] + drop, plate[3] + drop]), Color("#141B2C"))
	draw_colored_polygon(PackedVector2Array([plate[2], plate[1], plate[1] + drop, plate[2] + drop]), Color("#0B0F1A"))
	draw_line(plate[3] + drop, plate[2] + drop, Color(Palette.CELL_PINK, 0.6), 1.5)
	draw_line(plate[2] + drop, plate[1] + drop, Color(Palette.CELL_PINK, 0.6), 1.5)
	draw_colored_polygon(plate, Color(Palette.NIGHT_SKY, 0.9))
	for k in range(1, 8):
		var t := k / 8.0
		draw_line(plate[0].lerp(plate[3], t), plate[1].lerp(plate[2], t), Color(Palette.NET_CYAN, 0.06), 1.0)
		draw_line(plate[0].lerp(plate[1], t), plate[3].lerp(plate[2], t), Color(Palette.NET_CYAN, 0.06), 1.0)
	draw_polyline(plate + PackedVector2Array([plate[0]]), Color(Palette.NET_CYAN, 0.35), 1.5)
	var claimed := campaign.grid.claimed_ids()
	# Links: faint everywhere, bright inside the Cell's network.
	for s in corp.city_grid.sites:
		if s == null:
			continue
		for l in s.links:
			if not _positions.has(l):
				continue
			var ours := claimed.has(s.id) and claimed.has(l)
			if ours:
				draw_line(_positions[s.id], _positions[l], Color(Palette.CELL_PINK, 0.18), 7.0)
				draw_line(_positions[s.id], _positions[l], Color(Palette.CELL_PINK, 0.9), 2.0)
			else:
				draw_line(_positions[s.id], _positions[l], Color(Palette.NET_CYAN, 0.12), 1.0)
	# Threat routes: corporate chevrons marching toward CORE.
	for path in threat_paths:
		for i in path.size() - 1:
			if not (_positions.has(path[i]) and _positions.has(path[i + 1])):
				continue
			var a: Vector2 = _positions[path[i]]
			var b: Vector2 = _positions[path[i + 1]]
			draw_line(a, b, Color(corp_col, 0.14), 12.0)
			draw_line(a, b, Color(corp_col, 0.55), 1.5)
			var dir := (b - a).normalized()
			var length := a.distance_to(b)
			var k := fmod(anim_t * 40.0, 22.0)
			while k < length - 8.0:
				var p := a + dir * k
				draw_line(p, p - dir.rotated(0.6) * 7.0, corp_col, 2.0)
				draw_line(p, p - dir.rotated(-0.6) * 7.0, corp_col, 2.0)
				k += 22.0
		if not path.is_empty() and _positions.has(path[0]):
			_warning(_positions[path[0]], corp_col)
	# Other Sites: small corporate blocks (seized ones gold, cleared ones cyan).
	for s in corp.city_grid.sites:
		if s == null or claimed.has(s.id) or s.id == home_id:
			continue
		var status := campaign.grid.status_of(s.id)
		var bc := Color(corp_col, 0.55)
		if status == GridState.SiteStatus.CLEARED:
			bc = Color(Palette.NET_CYAN, 0.55)
		elif status == GridState.SiteStatus.SEIZED:
			bc = Palette.RESIST_GOLD
		_block(_positions[s.id], 7.0 + s.tier * 2.0, 8.0 + s.tier * 7.0, bc)
	# Claimed pads and CORE.
	for id in claimed:
		if id == home_id or not _positions.has(id):
			continue
		_pad(id, _positions[id])
	if _positions.has(home_id):
		_core(_positions[home_id])
	# Playout: threats standing on Sites.
	for sid in threat_markers:
		if not _positions.has(sid):
			continue
		var names: Array = threat_markers[sid]
		var p: Vector2 = _positions[sid]
		for k in names.size():
			var mp := p + Vector2(-14 + k * 16, -PAD - 18)
			var dia := PackedVector2Array([mp + Vector2(0, -8), mp + Vector2(7, 0), mp + Vector2(0, 8), mp + Vector2(-7, 0)])
			draw_colored_polygon(dia, corp_col)
			draw_polyline(dia + PackedVector2Array([dia[0]]), Palette.PAPER, 1.0)
		_tag(p + Vector2(-50, -PAD - 32), ", ".join(names), 10, corp_col, 160.0)


## A little dark block with a coloured roof edge (a corporate Site on the board).
func _block(p: Vector2, w: float, h: float, col: Color) -> void:
	var d := w * 0.5
	var t := [p + Vector2(0, -d), p + Vector2(w, 0), p + Vector2(0, d), p + Vector2(-w, 0)]
	var up := Vector2(0, -h)
	draw_colored_polygon(PackedVector2Array([t[3], t[2], t[2] + up, t[3] + up]), Color("#141B2C"))
	draw_colored_polygon(PackedVector2Array([t[2], t[1], t[1] + up, t[2] + up]), Color("#0B0F1A"))
	draw_colored_polygon(PackedVector2Array([t[0] + up, t[1] + up, t[2] + up, t[3] + up]), Color(col, 0.25))
	draw_polyline(PackedVector2Array([t[0] + up, t[1] + up, t[2] + up, t[3] + up, t[0] + up]), col, 1.2)
	draw_line(t[2], t[2] + up, Color(col, 0.7), 1.0)
	draw_line(t[3], t[3] + up, Color(col, 0.5), 1.0)
	draw_line(t[1], t[1] + up, Color(col, 0.5), 1.0)


func _hex(p: Vector2, r: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in 7:
		var t := PI / 6.0 + TAU * k / 6.0
		pts.append(p + Vector2(cos(t) * r, sin(t) * r * 0.62))
	return pts


func _pad(id: StringName, p: Vector2) -> void:
	var res: Dictionary = node_results.get(String(id), {})
	var outcome := String(res.get("outcome", ""))
	var col := Palette.CELL_ACID
	if outcome in ["breached", "disabled", "destroyed"]:
		col = Palette.CELL_PINK
	elif outcome == "seized" or campaign.grid.status_of(id) == GridState.SiteStatus.SEIZED:
		col = Palette.RESIST_GOLD
	elif not campaign.grid.is_active_node(id):
		col = Color(Palette.NET_CYAN, 0.5)
	# Pad: extruded hex with a glowing rim.
	var top := _hex(p + Vector2(0, -6), PAD)
	var bottom := _hex(p, PAD)
	draw_colored_polygon(bottom, Color(Palette.NIGHT_SKY, 0.95))
	draw_colored_polygon(top, Color(col, 0.16))
	draw_polyline(top, Color(col, 0.3), 5.0)
	draw_polyline(top, col, 1.6)
	for k in [1, 2, 3]:
		draw_line(bottom[k], top[k], Color(col, 0.6), 1.0)
	if id == selected_id:
		draw_polyline(_hex(p + Vector2(0, -6), PAD + 7), Palette.CELL_ACID, 2.0)
	var node_type := String(campaign.grid.node_type_of(id))
	draw_string(Palette.display(), p + Vector2(-PAD, 2), node_type.substr(0, 1).to_upper(), HORIZONTAL_ALIGNMENT_CENTER, PAD * 2, 18, Palette.PAPER)
	var site := campaign.grid.site(id)
	var before := int(res.get("before", site.get("integrity", 0)))
	var after := int(res.get("after", before))
	_tag(p + Vector2(-44, PAD + 8), String(id), 10, Palette.PAPER, 100.0)
	_tag(p + Vector2(-44, PAD + 21), ("%d > %d %s" % [before, after, outcome.to_upper()]) if outcome != "" else "%d/%d" % [site.get("integrity", 0), site.get("max_integrity", 0)], 9, col, 120.0)
	# Deployed assets orbit the pad.
	var assets := campaign.grid.assets_on(id)
	for k in assets.size():
		var a := TAU * k / maxf(1.0, assets.size()) - PI * 0.5 + anim_t * 0.4
		var ap := p + Vector2(cos(a) * (PAD + 14), sin(a) * (PAD + 14) * 0.62 - 6)
		AssetIcon.draw_icon(self, ap, 8.0, assets[k])


func _core(p: Vector2) -> void:
	var pulse := 0.5 + 0.5 * sin(anim_t * 2.5)
	for k in 3:
		var r := PAD * 2.0 + k * 12.0 + pulse * 4.0
		draw_polyline(_hex(p, r), Color(Palette.CELL_PINK, 0.45 - k * 0.12), 2.0 - k * 0.5)
	var top := _hex(p + Vector2(0, -10), PAD * 1.5)
	draw_colored_polygon(_hex(p, PAD * 1.5), Palette.NIGHT_SKY)
	draw_colored_polygon(top, Color(Palette.CELL_PINK, 0.3))
	draw_polyline(top, Palette.CELL_PINK, 2.0)
	draw_string(Palette.display(), p + Vector2(-40, -2), "CORE", HORIZONTAL_ALIGNMENT_CENTER, 80, 20, Palette.PAPER)
	var g := campaign.grid
	var frac := float(g.home_integrity) / maxf(1.0, g.home_max_integrity)
	var bar := Rect2(p + Vector2(-36, PAD + 6), Vector2(72, 6))
	draw_rect(bar, Color(Palette.PAPER, 0.15))
	draw_rect(Rect2(bar.position, Vector2(bar.size.x * frac, bar.size.y)), Palette.CELL_ACID if frac > 0.5 else Palette.CELL_PINK)
	_tag(p + Vector2(-36, PAD + 26), "HOME %d/%d" % [g.home_integrity, g.home_max_integrity], 10, Palette.CELL_ACID)


func _warning(p: Vector2, col: Color) -> void:
	var on := fmod(anim_t, 1.0) < 0.6
	var tri := PackedVector2Array([p + Vector2(0, -34), p + Vector2(14, -10), p + Vector2(-14, -10)])
	draw_colored_polygon(tri, Color(col, 0.9 if on else 0.5))
	draw_polyline(tri + PackedVector2Array([tri[0]]), Palette.INK, 1.5)
	draw_string(Palette.display(), p + Vector2(-5, -13), "!", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.INK)
	draw_arc(p, 12, 0, TAU, 20, Color(col, 0.5), 2.0)
