class_name GridMapView
extends Control
## City Grid as wireframe (STYLE_GUIDE 4): isometric wireframe buildings per Site,
## claimed Sites in cell_pink with spray circles, corporate Sites in the corporation
## colour, cleared Sites dim cyan, Seized Sites crossed out, links as net_cyan lines,
## frozen links in resist_gold, threat paths as glowing corporate arrows (pending raid
## entry -> home) and, during a playout, threat markers on the Sites they stand on.
## Emits site_clicked so the sidebar can act; the view never changes state.

signal site_clicked(site_id: StringName)

var campaign: CampaignState = null
var corp: CorporationData = null
var threat_paths: Array[Array] = []  # each: Array[StringName] of site ids
## Raid playout: site id -> Array[String] of threat names standing there.
var threat_markers: Dictionary = {}
## Site picked by the player (drawn with an acid ring).
var selected_id: StringName = &""
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
		_positions[s.id] = Vector2(60 + t.x * (size.x - 140), 50 + t.y * (size.y - 110) + t.x * 12)


func site_at(point: Vector2) -> StringName:
	for id in _positions:
		if point.distance_to(_positions[id]) < 24:
			return id
	return &""


func position_of(site_id: StringName) -> Vector2:
	return _positions.get(site_id, Vector2.ZERO)


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
	var dense := corp.city_grid.sites.size() > 16
	# Links (open, opened-locked, locked, frozen).
	for s in corp.city_grid.sites:
		if s == null:
			continue
		for l in s.links:
			if _positions.has(l):
				var frozen := campaign.grid.is_link_frozen(s.id, l)
				if frozen:
					_dashed_line(_positions[s.id], _positions[l], Palette.RESIST_GOLD)
				else:
					draw_line(_positions[s.id], _positions[l], Color(Palette.NET_CYAN, 0.12), 6.0)
					draw_line(_positions[s.id], _positions[l], Color(Palette.NET_CYAN, 0.6), 1.5)
		for l in s.locked_links:
			if _positions.has(l):
				var open := campaign.grid.is_link_open(s.id, l)
				var col := Color(Palette.NET_CYAN, 0.6) if open else Color(Palette.NET_CYAN, 0.2)
				if campaign.grid.is_link_frozen(s.id, l):
					col = Palette.RESIST_GOLD
				_dashed_line(_positions[s.id], _positions[l], col)
	# Threat paths: glowing corporate arrows.
	for path in threat_paths:
		for i in path.size() - 1:
			if _positions.has(path[i]) and _positions.has(path[i + 1]):
				var a: Vector2 = _positions[path[i]]
				var b: Vector2 = _positions[path[i + 1]]
				draw_line(a, b, Color(corp_col, 0.12), 14.0)
				draw_line(a, b, Color(corp_col, 0.3), 7.0)
				draw_line(a, b, corp_col, 2.5)
				var dir := (b - a).normalized()
				var tip := b - dir * 30
				draw_line(tip, tip - dir.rotated(0.5) * 10, corp_col, 2.0)
				draw_line(tip, tip - dir.rotated(-0.5) * 10, corp_col, 2.0)
	# Sites as iso wireframe blocks.
	for s in corp.city_grid.sites:
		if s == null:
			continue
		var p: Vector2 = _positions[s.id]
		var h := (12.0 + s.tier * 6.0) if dense else (18.0 + s.tier * 9.0)
		var w := 16.0 if dense else 26.0
		var d := 9.0 if dense else 14.0
		var col := corp_col
		var status := campaign.grid.status_of(s.id)
		match status:
			GridState.SiteStatus.CLAIMED:
				col = Palette.CELL_PINK
			GridState.SiteStatus.CLEARED:
				col = Color(Palette.NET_CYAN, 0.7)
			GridState.SiteStatus.SEIZED:
				col = Palette.RESIST_GOLD
		if s.id == campaign.grid.home_site_id:
			for k in 3:
				draw_arc(p, w + 10 + k * 9, 0, TAU, 40, Color(Palette.CELL_PINK, 0.55 - k * 0.15), 2.0 - k * 0.4)
		_iso_block(p, w, d, h, col)
		if s.id == selected_id:
			draw_arc(p + Vector2(0, -h * 0.5), w + 10, 0, TAU, 32, Palette.CELL_ACID, 2.0)
		if status == GridState.SiteStatus.CLAIMED:
			draw_arc(p + Vector2(0, 6), w + 4, 0, TAU * 0.92, 24, Color(Palette.CELL_PINK, 0.5), 4.0)
			draw_arc(p + Vector2(3, 4), w - 2, 0.5, TAU * 0.8 + 0.5, 20, Color(Palette.CELL_PINK, 0.3), 2.0)
		if status == GridState.SiteStatus.SEIZED:
			draw_line(p + Vector2(-w * 0.6, -w * 0.6), p + Vector2(w * 0.6, w * 0.6), Palette.RESIST_GOLD, 2.0)
			draw_line(p + Vector2(-w * 0.6, w * 0.6), p + Vector2(w * 0.6, -w * 0.6), Palette.RESIST_GOLD, 2.0)
		var glyph := ""
		match CampaignRules.site_objective(campaign, s):
			RC.SiteObjective.EXPLOIT:
				glyph = "◈"
			RC.SiteObjective.HEAT_REDUCTION:
				glyph = "❄"
			RC.SiteObjective.BOSS:
				glyph = "✦"
		if glyph != "" or s.id == campaign.grid.home_site_id:
			_badge(p + Vector2(0, -h - d - 12), 9.0 if dense else 11.0, col, glyph if glyph != "" else "⌂")
		var label := ("T%d %s" % [s.tier, glyph]) if dense else ("T%d %s %s" % [s.tier, s.display_name, glyph])
		if s.id == campaign.grid.home_site_id:
			label = "CORE"
		_tag(p + Vector2(-40, d + 16), label, 9 if dense else 10, Palette.PAPER)
		if status == GridState.SiteStatus.CLAIMED and s.id != campaign.grid.home_site_id:
			var site := campaign.grid.site(s.id)
			var level := campaign.grid.upgrade_level_of(s.id)
			_tag(p + Vector2(-40, d + 29), "%s %d/%d%s" % [campaign.grid.node_type_of(s.id), site["integrity"], site["max_integrity"], (" +%d" % level) if level > 0 else ""], 9, Palette.CELL_ACID)
		elif s.id == campaign.grid.home_site_id:
			_tag(p + Vector2(-40, d + 29), "HOME %d/%d" % [campaign.grid.home_integrity, campaign.grid.home_max_integrity], 9, Palette.CELL_ACID)
		# Raid playout: threats standing on this Site as corporate markers.
		if threat_markers.has(s.id):
			var names: Array = threat_markers[s.id]
			for k in names.size():
				var mp := p + Vector2(-20 + k * 14, -h - 22)
				draw_circle(mp, 6, corp_col)
				draw_circle(mp, 9, Color(corp_col, 0.35))
			draw_string(Palette.mono(), p + Vector2(-40, -h - 30), ", ".join(names), HORIZONTAL_ALIGNMENT_LEFT, 140, 9, corp_col)


func _iso_block(p: Vector2, w: float, d: float, h: float, col: Color) -> void:
	# A solid lit block (reference: the neon city) with a glowing roof edge.
	var top := PackedVector2Array([p + Vector2(0, -d), p + Vector2(w, 0), p + Vector2(0, d), p + Vector2(-w, 0)])
	var up := Vector2(0, -h)
	draw_colored_polygon(PackedVector2Array([p + Vector2(0, d * 1.6), p + Vector2(w * 1.5, 0), p + Vector2(0, -d * 1.6), p + Vector2(-w * 1.5, 0)]), Color(col, 0.1))
	var left := Palette.NIGHT_BLOCK_LIT.lerp(col, 0.18)
	var right := Palette.NIGHT_BLOCK.lerp(col, 0.08)
	draw_colored_polygon(PackedVector2Array([top[3], top[2], top[2] + up, top[3] + up]), left)
	draw_colored_polygon(PackedVector2Array([top[2], top[1], top[1] + up, top[2] + up]), right)
	draw_colored_polygon(PackedVector2Array([top[0] + up, top[1] + up, top[2] + up, top[3] + up]), col.darkened(0.45))
	# Window rows.
	var rows := int(h / 7.0)
	for r in rows:
		var y := -4.0 - r * 7.0
		draw_line(top[3].lerp(top[2], 0.2) + Vector2(0, y), top[3].lerp(top[2], 0.8) + Vector2(0, y), Color(col, 0.35), 1.5)
		draw_line(top[2].lerp(top[1], 0.2) + Vector2(0, y), top[2].lerp(top[1], 0.8) + Vector2(0, y), Color(col, 0.2), 1.5)
	var roof := PackedVector2Array([top[0] + up, top[1] + up, top[2] + up, top[3] + up, top[0] + up])
	draw_polyline(roof, Color(col, 0.25), 4.0)
	draw_polyline(roof, col, 1.5)
	draw_line(top[2], top[2] + up, Color(col, 0.6), 1.0)


## A hexagon badge floating over a Site: status colour, objective glyph inside.
func _badge(p: Vector2, r: float, col: Color, glyph: String) -> void:
	var pts := PackedVector2Array()
	for k in 7:
		pts.append(p + Vector2(cos(k * TAU / 6.0 + PI / 6.0), sin(k * TAU / 6.0 + PI / 6.0)) * r)
	draw_colored_polygon(pts, Color(Palette.NIGHT_SKY, 0.9))
	draw_polyline(pts, Color(col, 0.3), 4.0)
	draw_polyline(pts, col, 1.5)
	if glyph != "":
		draw_string(Palette.mono(), p + Vector2(-r, r * 0.45), glyph, HORIZONTAL_ALIGNMENT_CENTER, r * 2.0, int(r * 1.1), col)


## Text on a dark pill so it reads over links and blocks.
func _tag(at: Vector2, text: String, font_size: int, col: Color, width: float = 120.0) -> void:
	var f := Palette.mono()
	var tw := minf(f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x, width)
	draw_rect(Rect2(at.x - 3, at.y - font_size, tw + 6, font_size + 4), Color(Palette.NIGHT_SKY, 0.75))
	draw_string(f, at, text, HORIZONTAL_ALIGNMENT_LEFT, width, font_size, col)


func _dashed_line(a: Vector2, b: Vector2, col: Color) -> void:
	var n := maxi(2, int(a.distance_to(b) / 10.0))
	for i in n:
		if i % 2 == 0:
			draw_line(a.lerp(b, float(i) / n), a.lerp(b, float(i + 1) / n), col, 1.0)
