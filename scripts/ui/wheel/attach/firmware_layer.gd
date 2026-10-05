class_name FirmwareLayer
extends Control
## The firmware sockets of one wheel (ART_BIBLE v2 §3.9; z-order 5 of §3.21): a die on each slice
## that carries firmware, on the slice midline in the hub-side band between the hub ring and the read
## block, pins into the core; enemy wheels use the same socket. View only.

## The socket's centre and the chip's width in master units (§3.9: ρ ≈ 160 of R_IN 130 .. R_OUT 360,
## chip 50; §3.21 firmware zone 142..194), the chip never below MIN_CHIP px.
const SOCKET_AT := 168.0
const CHIP := 50.0
const MIN_CHIP := 12.0
## Below this rim radius (px at 720 high) the die draws 0.9x and simple (§3.9 "Below r = 150").
const SMALL_RIM := 100.0
const SMALL_SCALE := 0.9

var host: WheelAttachments = null
## The atlas glyphs this layer queues while it draws (1C).
var glyphs: GlyphBatch
## Per-slot trigger flash 0..1 (the trigger cue's FLARE: ART-3 sets it through `flash_slot`).
var flashes: Dictionary = {}


func _init() -> void:
	name = "FirmwareSockets"
	glyphs = GlyphBatch.make()
	add_child(glyphs)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## ART-3's seam for the trigger cue: lights slot `slot`'s LED, lip and pins (0..1).
func flash_slot(slot: int, amount: float) -> void:
	flashes[slot] = clampf(amount, 0.0, 1.0)
	queue_redraw()


## Where slot `slot`'s firmware trigger starts on screen (its die's centre: the LAND -> FLARE -> TRACE
## cue runs from here, §3.9), or Vector2.INF when the slot has none: the seam for the trigger beat
## (2D) and its FX (ART-3).
func trigger_origin(slot: int) -> Vector2:
	var s := socket(slot)
	return global_position + Vector2(s["at"]) if not s.is_empty() else Vector2.INF


## Where slot `slot`'s socket stands (local) and its chip width, as drawn now; {} without firmware.
func socket(slot: int) -> Dictionary:
	if host == null or not host.live():
		return {}
	var c := host.shown()
	if slot < 0 or slot >= c.wheel.slot_firmware_ids.size() or c.wheel.slot_firmware_ids[slot] == &"":
		return {}
	var u := host.unit()
	var a := host.slot_angle(slot, host.view.shown_rotation())
	var chip := maxf(MIN_CHIP, CHIP * u)
	if host.rim() < SMALL_RIM:
		chip *= SMALL_SCALE
	var at := host.center() + Vector2(cos(a), sin(a)) * SOCKET_AT * u
	return {"at": at, "size": chip, "id": c.wheel.slot_firmware_ids[slot]}


func _draw() -> void:
	glyphs.clear()
	if host == null or not host.live():
		return
	var c := host.shown()
	for slot in c.wheel.slot_firmware_ids.size():
		var s := socket(slot)
		if s.is_empty():
			continue
		var fw := host.view.lookup.get_content(StringName(s["id"])) as FirmwareData
		FirmwareSocket.draw_die(self, glyphs, s["at"], float(s["size"]), host.center(), fw, float(flashes.get(slot, 0.0)))
