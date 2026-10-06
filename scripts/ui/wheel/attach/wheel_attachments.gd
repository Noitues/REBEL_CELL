class_name WheelAttachments
extends Control
## Everything docked on a wheel (ART-2 2B; ART_BIBLE v2 §3.9, §3.11, §3.17, §3.21): the firmware
## sockets, the drones and satellites (collapsed band, hover bloom into mini-wheels) and the
## animated card-play preview, as three layers over the wheel in the round 41 z-order (5 firmware,
## 10-12 dock lobes and drones, 14 card-preview ghosts). One child of each WheelView (`attach`).
## The seam to 2A's wheel: it reads the view's public geometry and state (`global_center`,
## `rim_radius`, `band_width`, `shown_rotation`, `shown_pointers`, the shown combatant and
## satellites, `ghost_rotation`, the aim zones) and never draws into the view; the view asks it
## where a satellite stands (`satellite_global_pos`) and leaves its own legacy drawing of these
## parts off while it is attached. View only: it never changes game state.

var view: WheelView = null
var sockets: FirmwareLayer
var dock: DroneDock
var preview: CardPreviewOverlay
var _sig: String = ""
var _preview_sig: String = ""


## Docks the attachment layers on `v` (once) and returns them.
static func attach(v: WheelView) -> WheelAttachments:
	if v.attachments != null:
		return v.attachments as WheelAttachments
	var a := WheelAttachments.new()
	a.view = v
	v.attachments = a
	v.add_child(a)
	return a


func _init() -> void:
	name = "Attachments"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	sockets = FirmwareLayer.new()
	sockets.host = self
	add_child(sockets)
	dock = DroneDock.new()
	dock.host = self
	add_child(dock)
	preview = CardPreviewOverlay.new()
	preview.host = self
	add_child(preview)


# --- Geometry read from the view (local to the view, which is local to these layers) -----------

## The combatant the view shows now (the replay's snapshot while a SEND IT plays).
func shown() -> CombatantState:
	if view == null:
		return null
	return view.shown_state if view.shown_state != null else view.combatant


## The satellites and drones the view shows now.
func shown_satellites() -> Array[CombatantState]:
	if view == null:
		return []
	return view.shown_satellites if view.shown_state != null else view.satellites


## True when the wheel is drawn whole (a fight shown, not beaten, not flipping).
func live() -> bool:
	var c := shown()
	return c != null and c.wheel != null and view.lookup != null and not view.defeated() and view.flip_squash >= 1.0


func center() -> Vector2:
	return view.global_center() - view.global_position


## The slices' outer edge (px).
func rim() -> float:
	return view.rim_radius()


## The slice band's width (px).
func band() -> float:
	return view.band_width()


## Pixels per master unit of the round 41 stack (the slices end at master 360).
func unit() -> float:
	return rim() / AttachStyle.MASTER_RIM


## Screen angle of slice `slot`'s midline at wheel rotation `rot` (ticks).
func slot_angle(slot: int, rot: float) -> float:
	var c := shown()
	var tps := c.wheel.ticks_per_slice() if c != null and c.wheel != null else 1
	return WheelView._ang(slot * tps - rot)


## The HP arc's outer edge (px) and its sector: drones dock outside it there (§3.11).
func hp_arc_outer() -> float:
	return rim() + WheelView.HP_ARC_OUT


## Whether screen angle `a` lies over the HP arc (the lower sector the view draws it in).
func over_hp_arc(a: float) -> bool:
	var bottom := absf(wrapf(a - PI * 0.5, -PI, PI))
	return sin(a) > sin(HP_ARC_FROM) and bottom >= HP_ARC_GAP


## Whether screen angle `a` lies in the HP arc's bottom gap (over the HP number).
func in_hp_gap(a: float) -> bool:
	return absf(wrapf(a - PI * 0.5, -PI, PI)) < HP_ARC_GAP


## The view's HP arc starts this far past 3 o'clock (rad) and ends as far before 9 o'clock, with a
## gap this wide (rad either side of 6 o'clock) over the HP number.
const HP_ARC_FROM := PI * 0.1
const HP_ARC_GAP := 0.34


## Where docked satellite `sat` stands on screen (its tile, or its mini-wheel when bloomed).
func satellite_global_pos(sat: CombatantState) -> Vector2:
	return global_position + dock.satellite_pos(sat)


func _process(_delta: float) -> void:
	if view == null:
		return
	var sig := _signature()
	var preview_sig := preview.signature()
	if sig != _sig:
		_sig = sig
		_preview_sig = preview_sig
		sockets.queue_redraw()
		dock.queue_redraw()
		preview.queue_redraw()
	elif preview_sig != _preview_sig:
		# ART-12 12p: the preview's chevron chase changes every frame while a card is hovered;
		# only the preview redraws for it (the sockets and the dock read none of its state: they
		# redrew every frame, 7 ms on the worst fixture's boss wheel).
		_preview_sig = preview_sig
		preview.queue_redraw()


## What the sockets and the dock draw from, as text: a change redraws every layer (the
## preview's own state is `preview.signature()`, which redraws the preview alone).
func _signature() -> String:
	var c := shown()
	if c == null or c.wheel == null:
		return ""
	var parts := PackedStringArray([str(center()), str(rim()), str(view.shown_rotation()), str(view.shown_pointers()),
		str(c.wheel.slot_firmware_ids), str(view.ghost_rotation), str(view.defeated()), str(view.flip_squash), str(view.inverted),
		str(view.targeted_satellite), str(view.valid_zones), str(view.hover_zone), str(Settings.text_scale), dock.signature()])
	for s in shown_satellites():
		parts.append("%s:%d:%d:%d" % [s.id, s.hp, s.dock_slot, s.wheel.rotation if s.wheel != null else 0])
	return "|".join(parts)
