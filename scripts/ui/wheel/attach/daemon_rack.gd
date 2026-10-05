class_name DaemonRack
extends Control
## The Daemon rack (ART_BIBLE v2 §3.1, §3.13; round 34 `daemon_row`): a narrow CRT plate on the left
## edge beside the operative's wheel, "DAEMONS" over a column of CRT tiles in install order; more than
## MAX_TILES shows the last tile as "+N". Each tile: the Daemon's sigil in its phosphor colour, the
## rarity on its bezel, an idle scan bar rolling (phase per slot) and a heartbeat LED. The fire cue
## (flash, RGB split, packet line) is ART-3's (`fire_slot` is its seam). Hover a tile for what the
## Daemon does. View only: it reads the installed Daemons from the scene's DaemonRow.

## The idle scan bar's roll (one pass per `seconds`, looping); reduce effects: no bar.
const SCAN_MOTION := &"daemon_rack_scan"
## Tile size and gap, plate padding and header height (px at 720 high, text scale 1.0).
const TILE := 40.0
const GAP := 6.0
const PAD := 5.0
const HEADER := 16.0
## Tiles at most; beyond, the last one says "+N".
const MAX_TILES := 6
## Left inset from the view's edge (px).
const INSET := 6.0
## Header text size (px at 1.0), sigil radius (share of the tile), scan bar height (share).
const HEADER_PX := 12
const SIGIL := 0.32
const SCAN_H := 0.14
## The phosphor glow behind a sigil and the scan bar's alpha.
const GLOW_ALPHA := 0.16
const SCAN_ALPHA := 0.22
## The heartbeat LED (share of the tile) and its dim alpha.
const LED := 0.06
const LED_DIM := 0.35

## The scene's DaemonRow (the installed ids and the lookup).
var source: DaemonRow = null
## The wheel it stands beside (its vertical centre).
var view: WheelView = null
## Per-slot fire flash 0..1 (ART-3's trigger cue sets it).
var fire: Dictionary = {}
var _clock: float = 0.0


## Puts a rack beside `v` (on its left edge) reading `row`, and returns it.
static func mount(v: WheelView, row: DaemonRow) -> DaemonRack:
	var r := DaemonRack.new()
	r.view = v
	r.source = row
	v.add_child(r)
	return r


func _init() -> void:
	name = "DaemonRack"
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_text = " "
	tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED


## ART-3's seam: lights tile `slot` (0..1) for the fire cue.
func fire_slot(slot: int, amount: float) -> void:
	fire[slot] = clampf(amount, 0.0, 1.0)
	queue_redraw()


func ids() -> Array[StringName]:
	var none: Array[StringName] = []
	return source.daemon_ids if source != null else none


## The plate's rect (local to the view) for `n` Daemons.
func plate_rect(n: int) -> Rect2:
	var ts := Settings.text_scale
	var shown := mini(n, MAX_TILES)
	var w := TILE * ts + PAD * 2.0
	var h := HEADER * ts + PAD * 2.0 + shown * TILE * ts + maxi(0, shown - 1) * GAP
	var cy := (view.global_center() - view.global_position).y if view != null else h * 0.5
	var top := clampf(cy - h * 0.5, 0.0, maxf(0.0, (view.size.y if view != null else h) - h))
	return Rect2(Vector2(INSET, top), Vector2(w, h))


## The tile rect of slot `k` (local to this rack).
func tile_rect(k: int) -> Rect2:
	var ts := Settings.text_scale
	return Rect2(Vector2(PAD, PAD + HEADER * ts + k * (TILE * ts + GAP)), Vector2(TILE * ts, TILE * ts))


func _process(delta: float) -> void:
	var n := ids().size()
	visible = n > 0 and view != null and view.combatant != null
	if not visible:
		return
	var r := plate_rect(n)
	if position != r.position or size != r.size:
		position = r.position
		size = r.size
	if Motion.live(SCAN_MOTION):
		_clock = fposmod(_clock + delta / maxf(0.001, Motion.seconds(SCAN_MOTION)), 1.0)
		queue_redraw()


func _get_tooltip(at_position: Vector2) -> String:
	var list := ids()
	for k in mini(list.size(), MAX_TILES):
		if tile_rect(k).has_point(at_position):
			if k == MAX_TILES - 1 and list.size() > MAX_TILES:
				return source.describe_all()
			var d := source.lookup.get_content(list[k]) as DaemonData if source.lookup != null else null
			return Codex.describe(d) if d != null else String(list[k])
	return source.describe_all() if source != null else ""


func _draw() -> void:
	var list := ids()
	if list.is_empty():
		return
	var ts := Settings.text_scale
	draw_rect(Rect2(Vector2.ZERO, size), Palette.TERMINAL_BG)
	draw_rect(Rect2(Vector2.ZERO, size), Palette.TERMINAL_EDGE, false, 1.5)
	AttachStyle.draw_centred(self, AttachStyle.label_font(), Vector2(size.x * 0.5, PAD + HEADER * ts * 0.45), tr("DAEMONS"), roundi(HEADER_PX * ts), Palette.TERMINAL_TEXT)
	var shown := mini(list.size(), MAX_TILES)
	for k in shown:
		var r := tile_rect(k)
		var id: StringName = list[k]
		var d := source.lookup.get_content(id) as DaemonData if source.lookup != null else null
		var rarity: int = d.rarity if d != null else RC.Rarity.COMMON
		var phos := DaemonSigil.color_of(id)
		var f := float(fire.get(k, 0.0))
		draw_rect(r, AttachStyle.glass(0.95))
		draw_rect(r.grow(-2.0), Color(phos, GLOW_ALPHA + 0.5 * f))
		if k == shown - 1 and list.size() > MAX_TILES:
			AttachStyle.draw_centred(self, AttachStyle.value_font(), r.get_center(), "+%d" % (list.size() - MAX_TILES + 1), roundi(TILE * ts * 0.4), Palette.TERMINAL_TEXT, 2)
		else:
			DaemonSigil.draw_sigil(self, r.get_center(), r.size.x * SIGIL, id, rarity)
		# Idle: the scan bar rolls down the tile, each slot on its own phase; the LED beats with it.
		var phase := fposmod(_clock + float(k) / MAX_TILES, 1.0)
		if Motion.live(SCAN_MOTION):
			var bar := Rect2(Vector2(r.position.x, r.position.y + phase * r.size.y * (1.0 - SCAN_H)), Vector2(r.size.x, r.size.y * SCAN_H))
			draw_rect(bar, Color(phos, SCAN_ALPHA))
		var beat := 1.0 if phase < 0.12 or not Motion.live(SCAN_MOTION) else LED_DIM
		draw_circle(r.position + Vector2(r.size.x - r.size.x * LED * 2.0, r.size.y * LED * 2.0), r.size.x * LED, Color(phos, beat))
		draw_rect(r, AttachStyle.rarity_color(rarity), false, 1.5)
