class_name GridMapView
extends Control
## City Grid as wireframe (STYLE_GUIDE 4): isometric wireframe buildings per Site,
## claimed Sites in cell_pink with spray circles, corporate Sites in the corporation
## colour, cleared Sites dim cyan, Seized Sites crossed out, links as net_cyan lines,
## threat paths as glowing corporate arrows (pending raid entry -> home). Emits
## site_clicked so the sidebar can act; the view never changes state.

signal site_clicked(site_id: StringName)

var campaign: CampaignState = null
var corp: CorporationData = null
var threat_paths: Array[Array] = []  # each: Array[StringName] of site ids
var _positions: Dictionary = {}


func _init() -> void:
	custom_minimum_size = Vector2(760, 380)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mouse_filter = Control.MOUSE_FILTER_STOP
	resized.connect(queue_redraw)


func show_grid(p_campaign: CampaignState, p_corp: CorporationData, p_threat_paths: Array[Array] = []) -> void:
	campaign = p_campaign
	corp = p_corp
	threat_paths = p_threat_paths
	_layout_positions()
	queue_redraw()


func _layout_positions() -> void:
	_positions.clear()
	if corp == null:
		return
	var min_p := Vector2(1e9, 1e9)
	var max_p := Vector2(-1e9, -1e9)
	for s in corp.city_grid.sites:
		if s == null:
			continue
		min_p = min_p.min(s.map_position)
		max_p = max_p.max(s.map_position)
	var span := (max_p - min_p).max(Vector2(1, 1))
	for s in corp.city_grid.sites:
		if s == null:
			continue
		var t := (s.map_position - min_p) / span
		# Isometric-ish projection: x spreads, y compresses and shifts with x.
		_positions[s.id] = Vector2(60 + t.x * (size.x - 140), 70 + t.y * (size.y - 150) + t.x * 20)


func site_at(point: Vector2) -> StringName:
	for id in _positions:
		if point.distance_to(_positions[id]) < 34:
			return id
	return &""


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var id := site_at(event.position)
		if id != &"":
			site_clicked.emit(id)


func _draw() -> void:
	if campaign == null or corp == null:
		return
	_layout_positions()  # the control's size is only final at draw time
	var corp_col := Palette.corp_color(corp.id)
	# Links (open, opened-locked, locked).
	for s in corp.city_grid.sites:
		if s == null:
			continue
		for l in s.links:
			if _positions.has(l):
				draw_line(_positions[s.id], _positions[l], Color(Palette.NET_CYAN, 0.45), 1.5)
		for l in s.locked_links:
			if _positions.has(l):
				var open := campaign.grid.is_link_open(s.id, l)
				_dashed_line(_positions[s.id], _positions[l], Color(Palette.NET_CYAN, 0.6) if open else Color(Palette.NET_CYAN, 0.2))
	# Threat paths: glowing corporate arrows.
	for path in threat_paths:
		for i in path.size() - 1:
			if _positions.has(path[i]) and _positions.has(path[i + 1]):
				var a: Vector2 = _positions[path[i]]
				var b: Vector2 = _positions[path[i + 1]]
				draw_line(a, b, Color(corp_col, 0.25), 8.0)
				draw_line(a, b, corp_col, 2.0)
				var dir := (b - a).normalized()
				var tip := b - dir * 30
				draw_line(tip, tip - dir.rotated(0.5) * 10, corp_col, 2.0)
				draw_line(tip, tip - dir.rotated(-0.5) * 10, corp_col, 2.0)
	# Sites as iso wireframe blocks.
	for s in corp.city_grid.sites:
		if s == null:
			continue
		var p: Vector2 = _positions[s.id]
		var h := 18.0 + s.tier * 9.0
		var col := corp_col
		var status := campaign.grid.status_of(s.id)
		match status:
			GridState.SiteStatus.CLAIMED:
				col = Palette.CELL_PINK
			GridState.SiteStatus.CLEARED:
				col = Color(Palette.NET_CYAN, 0.7)
			GridState.SiteStatus.SEIZED:
				col = Palette.RESIST_GOLD
		_iso_block(p, 26, 14, h, col)
		if status == GridState.SiteStatus.CLAIMED:
			draw_arc(p + Vector2(0, 6), 30, 0, TAU * 0.92, 24, Color(Palette.CELL_PINK, 0.5), 5.0)
			draw_arc(p + Vector2(3, 4), 24, 0.5, TAU * 0.8 + 0.5, 20, Color(Palette.CELL_PINK, 0.3), 3.0)
		if status == GridState.SiteStatus.SEIZED:
			draw_line(p + Vector2(-16, -16), p + Vector2(16, 16), Palette.RESIST_GOLD, 2.0)
			draw_line(p + Vector2(-16, 16), p + Vector2(16, -16), Palette.RESIST_GOLD, 2.0)
		var glyph := ""
		match s.objective:
			RC.SiteObjective.EXPLOIT:
				glyph = "◈"
			RC.SiteObjective.HEAT_REDUCTION:
				glyph = "❄"
			RC.SiteObjective.BOSS:
				glyph = "✦"
		var label := "T%d %s %s" % [s.tier, s.display_name, glyph]
		draw_string(Palette.mono(), p + Vector2(-40, h + 22), label, HORIZONTAL_ALIGNMENT_LEFT, 120, 10, Palette.PAPER)
		if status == GridState.SiteStatus.CLAIMED and s.id != campaign.grid.home_site_id:
			var site := campaign.grid.site(s.id)
			draw_string(Palette.mono(), p + Vector2(-40, h + 34), "%s %d/%d" % [campaign.grid.node_type_of(s.id), site["integrity"], site["max_integrity"]], HORIZONTAL_ALIGNMENT_LEFT, 120, 9, Palette.CELL_ACID)
		elif s.id == campaign.grid.home_site_id:
			draw_string(Palette.mono(), p + Vector2(-40, h + 34), "HOME %d/%d" % [campaign.grid.home_integrity, campaign.grid.home_max_integrity], HORIZONTAL_ALIGNMENT_LEFT, 120, 9, Palette.CELL_ACID)


func _iso_block(p: Vector2, w: float, d: float, h: float, col: Color) -> void:
	var top := PackedVector2Array([p + Vector2(0, -d), p + Vector2(w, 0), p + Vector2(0, d), p + Vector2(-w, 0)])
	var up := Vector2(0, -h)
	draw_polyline(PackedVector2Array([top[0] + up, top[1] + up, top[2] + up, top[3] + up, top[0] + up]), col, 1.5)
	for i in 4:
		draw_line(top[i], top[i] + up, Color(col, 0.7), 1.0)
	draw_polyline(PackedVector2Array([top[1], top[2], top[3]]), Color(col, 0.7), 1.0)
	draw_colored_polygon(PackedVector2Array([top[0] + up, top[1] + up, top[2] + up, top[3] + up]), Color(col, 0.12))


func _dashed_line(a: Vector2, b: Vector2, col: Color) -> void:
	var n := maxi(2, int(a.distance_to(b) / 10.0))
	for i in n:
		if i % 2 == 0:
			draw_line(a.lerp(b, float(i) / n), a.lerp(b, float(i + 1) / n), col, 1.0)
