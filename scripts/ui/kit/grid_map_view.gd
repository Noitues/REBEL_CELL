class_name GridMapView
extends Control
## City Grid as wireframe (STYLE_GUIDE 4): isometric wireframe buildings per Site,
## claimed Sites in cell_pink with spray circles, corporate Sites in the corporation
## colour, cleared Sites dim cyan, Seized Sites crossed out, links as net_cyan lines,
## frozen links in resist_gold, threat paths as glowing corporate arrows (pending raid
## entry -> home) and, during a playout, threat markers on the Sites they stand on.
## Emits site_clicked so the sidebar can act; the view never changes state.
##
## H22: the Site labels follow Settings.text_scale (redrawn when it changes), use the
## translated Site names, and lead with the map's tier difficulty pips
## (CityMapOverlay.draw_tier).
##
## H23 #1: labels are placed, not stamped under each block: no two labels (pips
## included) overlap, a crowded label shortens or is left out (see `layout_labels`), and
## every Site keeps a tooltip naming it, its tier, kind and status.
##
## H24: objective and home Sites float the map's own icon (CityMapOverlay.draw_icon, not a
## font glyph: K5); every word drawn here goes through the TranslationServer once (K7:
## "CORE", "T2", HOME); a label never covers a Site's block or icon (K8: at 1.6 the T1
## labels sat on the stacked blocks), it shortens or is left out instead.

signal site_clicked(site_id: StringName)

## Label font sizes at text scale 1.0 (px): Site labels on a dense (> 16 Sites) and a
## sparse Grid, and the second line (node / home integrity, threats).
const LABEL_FONT_DENSE := 9
const LABEL_FONT := 10
const DETAIL_FONT := 9
## The tier pips' scale in a label at text scale 1.0, and their gap to the text (px).
const PIP_SCALE := 0.8
const PIP_TEXT_GAP := 4.0
## H23 #1 label layout (px): the pill's padding, the margin kept inside the view, the gap
## between a Site's block and its label, and how far the objective badge floats over
## the roof.
const LABEL_PAD := 2.0
const LABEL_EDGE := 2.0
const LABEL_GAP := 3.0
const BADGE_LIFT := 12.0

var campaign: CampaignState = null
var corp: CorporationData = null
var threat_paths: Array[Array] = []  # each: Array[StringName] of site ids
## Raid playout: site id -> Array[String] of threat names standing there.
var threat_markers: Dictionary = {}
## Site picked by the player (drawn with an acid ring).
var selected_id: StringName = &""
var _positions: Dictionary = {}
## The labels of the last draw ({text, size}), for checks.
var drawn_labels: Array[Dictionary] = []
## The tier pips of the last draw (Site id -> tier), for checks.
var drawn_tiers: Dictionary = {}
## H23 #1: the label rects of the last draw (Site id -> Rect2, px; pips included), for
## checks. A Site left out for room has none.
var label_rects: Dictionary = {}
## H24 K8: what each Site draws (its block and floating icon; Site id -> Rect2, px), for
## the label layout and checks; and the map icon kind each Site floats (K5).
var icon_rects: Dictionary = {}
var drawn_icons: Dictionary = {}


func _init() -> void:
	custom_minimum_size = Vector2(760, 380)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mouse_filter = Control.MOUSE_FILTER_STOP
	resized.connect(queue_redraw)
	Settings.changed.connect(queue_redraw)


## Label font size now (px): `base` at the current text scale.
static func label_size(base: int) -> int:
	return maxi(1, roundi(base * Settings.text_scale))


## The label shown under Site `s` (tier, translated name on a sparse Grid, objective
## glyph; "CORE" for the home Site).
func site_label(s: SiteData, dense: bool) -> String:
	if campaign != null and s.id == campaign.grid.home_site_id:
		return CityLayout.home_label()
	return CityMapOverlay.tier_text(s.tier) if dense else "%s %s" % [CityMapOverlay.tier_text(s.tier), TextDb.t(s, "display_name")]


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
	drawn_labels.clear()
	drawn_tiers.clear()
	drawn_icons.clear()
	icon_rects.clear()
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
	# Sites as iso wireframe blocks; their labels are placed after (H23 #1).
	var jobs: Array[Dictionary] = []
	var bodies: Array[Rect2] = []
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
		# H24 K5: the map's own icon over objective Sites and CORE (the same drawing as the
		# city map and the key).
		var kind := CityLayout.site_kind(campaign, s)
		var floats := kind != CityMapOverlay.KIND_TIER
		var badge_r := 9.0 if dense else 11.0
		if floats:
			CityMapOverlay.draw_icon(self, kind, p + Vector2(0, -h - d - BADGE_LIFT), badge_r, col)
			drawn_icons[s.id] = kind
		var home := s.id == campaign.grid.home_site_id
		var detail_text := ""
		if status == GridState.SiteStatus.CLAIMED and not home:
			var site := campaign.grid.site(s.id)
			var level := campaign.grid.upgrade_level_of(s.id)
			detail_text = "%s %d/%d%s" % [_node_name(campaign.grid.node_type_of(s.id)), site["integrity"], site["max_integrity"], (" +%d" % level) if level > 0 else ""]
		elif home:
			detail_text = "%s %d/%d" % [CityMapOverlay.tr_word("HOME"), campaign.grid.home_integrity, campaign.grid.home_max_integrity]
		var body := _body_rect(p, w, d, h, floats, badge_r)
		icon_rects[s.id] = body
		jobs.append({"id": s.id, "p": p, "body": body,
			"prio": 0 if s.id == selected_id else (1 if home else (2 if status == GridState.SiteStatus.CLAIMED else 3)),
			"tier": 0 if home else s.tier, "variants": _variants(s, dense, detail_text)})
		bodies.append(body)
		# Raid playout: threats standing on this Site as corporate markers.
		if threat_markers.has(s.id):
			var names: Array = threat_markers[s.id]
			for k in names.size():
				var mp := p + Vector2(-20 + k * 14, -h - 22)
				draw_circle(mp, 6, corp_col)
				draw_circle(mp, 9, Color(corp_col, 0.35))
			draw_string(Palette.mono(), p + Vector2(-40, -h - 30), ", ".join(names), HORIZONTAL_ALIGNMENT_LEFT, 140 * Settings.text_scale, label_size(DETAIL_FONT), corp_col)
	for l in layout_labels(jobs, bodies):
		_draw_label(l)


## The rect Site block `p` covers (its footprint glow up to its roof and badge), in px.
static func _body_rect(p: Vector2, w: float, d: float, h: float, badge: bool, badge_r: float) -> Rect2:
	var top := h + d + (BADGE_LIFT + badge_r if badge else 0.0)
	return Rect2(p.x - w, p.y - top, w * 2.0, top + d)


## The label variants of Site `s`, longest first (H23 #1): name and detail line, name,
## the short "T2 glyph", the tier pips alone. Each: {lines: [[text, font size, colour]],
## pips: bool}.
func _variants(s: SiteData, dense: bool, detail_text: String) -> Array[Dictionary]:
	var home := s.id == campaign.grid.home_site_id
	var fs := label_size(LABEL_FONT_DENSE if dense else LABEL_FONT)
	var dfs := label_size(DETAIL_FONT)
	var main := site_label(s, dense)
	var short := CityLayout.home_label() if home else CityMapOverlay.tier_text(s.tier)
	var out: Array[Dictionary] = []
	if detail_text != "":
		out.append({"lines": [[main, fs, Palette.PAPER], [detail_text, dfs, Palette.CELL_ACID]], "pips": not home})
	out.append({"lines": [[main, fs, Palette.PAPER]], "pips": not home})
	if short != main:
		out.append({"lines": [[short, fs, Palette.PAPER]], "pips": not home})
	if not home:
		out.append({"lines": [], "pips": true})
	return out


## The size of a label variant (px): the tier pips leading its first line, each line on
## its pill.
static func _variant_size(v: Dictionary) -> Vector2:
	var f := Palette.mono()
	var ps := PIP_SCALE * Settings.text_scale
	var pips := CityMapOverlay.tier_pips_size(ps) if v["pips"] else Vector2.ZERO
	var lines: Array = v["lines"]
	if lines.is_empty():
		return pips + Vector2(LABEL_PAD, LABEL_PAD) * 2.0
	var wide := 0.0
	var tall := 0.0
	for k in lines.size():
		var line: Array = lines[k]
		var tw := f.get_string_size(line[0], HORIZONTAL_ALIGNMENT_LEFT, -1, line[1]).x
		if k == 0 and v["pips"]:
			tw += pips.x + PIP_TEXT_GAP
		wide = maxf(wide, tw)
		tall += f.get_height(line[1])
	return Vector2(wide, maxf(tall, pips.y)) + Vector2(LABEL_PAD, LABEL_PAD) * 2.0


## Places the Site labels (H23 #1: they piled up at 1.6): by priority (selected, CORE,
## claimed, the rest; ties by Site id), each at the first free spot round its block
## (below, above, right, left, then the corners), inside the view and clear of every
## label placed before (pips included: they are part of the label). A label with no room
## drops to a shorter variant (name, "T2", the pips alone); H24 K8: a label never lies on
## a Site's block or icon (it used to, as a last resort, on the stacked T1 blocks at 1.6);
## a label that fits nowhere is left out and the Site keeps its tooltip. Returns
## [{id, rect, variant}]; fills `label_rects`.
func layout_labels(jobs: Array[Dictionary], bodies: Array[Rect2]) -> Array[Dictionary]:
	var order := jobs.duplicate()
	order.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if a["prio"] != b["prio"]:
			return a["prio"] < b["prio"]
		return String(a["id"]) < String(b["id"]))
	var area := Rect2(Vector2.ZERO, size).grow(-LABEL_EDGE)
	var placed: Array[Dictionary] = []
	label_rects.clear()
	for job: Dictionary in order:
		var spot := {}
		# Clear of every block, shortening the label if need be (H24 K8: never over them).
		for v: Dictionary in job["variants"]:
			var box := _variant_size(v)
			for c in _label_spots(job["p"], job["body"], box):
				var r := Rect2(c, box)
				if area.encloses(r) and _label_free(r, placed, bodies, job["body"], true):
					spot = {"id": job["id"], "rect": r, "variant": v, "tier": job["tier"]}
					break
			if not spot.is_empty():
				break
		if not spot.is_empty():
			placed.append(spot)
			label_rects[job["id"]] = spot["rect"]
	return placed


## Candidate top-left corners for a `box` label round a Site at `p` whose block covers
## `body`: below, above, right, left, then the four corners.
static func _label_spots(p: Vector2, body: Rect2, box: Vector2) -> Array[Vector2]:
	var g := LABEL_GAP
	return [Vector2(p.x - box.x * 0.5, body.end.y + g), Vector2(p.x - box.x * 0.5, body.position.y - g - box.y),
		Vector2(body.end.x + g, p.y - box.y * 0.5), Vector2(body.position.x - g - box.x, p.y - box.y * 0.5),
		Vector2(body.end.x + g, body.end.y + g), Vector2(body.position.x - g - box.x, body.end.y + g),
		Vector2(body.end.x + g, body.position.y - g - box.y), Vector2(body.position.x - g - box.x, body.position.y - g - box.y)]


## True when label rect `r` overlaps no placed label (and, `strict`, no other Site's block).
static func _label_free(r: Rect2, placed: Array[Dictionary], bodies: Array[Rect2], own: Rect2, strict: bool) -> bool:
	for other in placed:
		if r.intersects(other["rect"]):
			return false
	if strict:
		for b in bodies:
			if b != own and r.intersects(b):
				return false
	return true


## Draws a placed label: its pill, the tier pips leading the first line, the lines.
func _draw_label(l: Dictionary) -> void:
	var r: Rect2 = l["rect"]
	var v: Dictionary = l["variant"]
	var f := Palette.mono()
	draw_rect(r, Color(Palette.NIGHT_SKY, 0.75))
	var x := r.position.x + LABEL_PAD
	var y := r.position.y + LABEL_PAD
	var lines: Array = v["lines"]
	if v["pips"]:
		var ps := PIP_SCALE * Settings.text_scale
		var pips := CityMapOverlay.tier_pips_size(ps)
		var line_h := f.get_height(lines[0][1]) if not lines.is_empty() else pips.y
		CityMapOverlay.draw_tier(self, Vector2(x + pips.x * 0.5, y + line_h * 0.5), int(l["tier"]), Palette.PAPER, ps)
		drawn_tiers[l["id"]] = int(l["tier"])
		x += pips.x + PIP_TEXT_GAP
	for k in lines.size():
		var line: Array = lines[k]
		draw_string(f, Vector2(x if k == 0 else r.position.x + LABEL_PAD, y + f.get_ascent(line[1])), line[0], HORIZONTAL_ALIGNMENT_LEFT, -1, line[1], line[2])
		drawn_labels.append({"text": line[0], "size": line[1]})
		y += f.get_height(line[1])


## Hover text for the Site under the pointer (H23 #1: a label left out for room still
## names its Site): the map tooltip (name, tier, kind, status); else the view's own.
func _get_tooltip(at_position: Vector2) -> String:
	var id := site_at(at_position)
	if id == &"" or campaign == null or corp == null:
		return tooltip_text
	var sd := CampaignRules.site_data(corp, id)
	if sd == null:
		return tooltip_text
	var kind := CityLayout.site_kind(campaign, sd)
	var name_text := CityLayout.home_label() if kind == CityMapOverlay.KIND_HOME else TextDb.t(sd, "display_name")
	return UiTip.fold(CityLayout.site_tip(name_text, sd.tier, campaign.grid.status_of(id), kind))


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


## A claimed node's display name (TextDb through the content lookup), else its id.
static func _node_name(node_id: StringName) -> String:
	var lookup := RunManager.lookup() if RunManager != null else null
	var res: Resource = lookup.get_content(node_id) if lookup != null else null
	return TextDb.t(res, "display_name") if res != null else String(node_id)


func _dashed_line(a: Vector2, b: Vector2, col: Color) -> void:
	var n := maxi(2, int(a.distance_to(b) / 10.0))
	for i in n:
		if i % 2 == 0:
			draw_line(a.lerp(b, float(i) / n), a.lerp(b, float(i + 1) / n), col, 1.0)
