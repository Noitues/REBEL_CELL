class_name KitDemo
extends RefCounted
## The motion lab's demos of the material kit (ART-1 1B; ANIMATION_HANDOFF 3, STYLE_GUIDE 5.1
## "the lab shows the real motion"): each kit entry plays on a fresh real piece (a
## VinylSticker, a CrtTerminalPanel, a GreasePencilMark, a DecryptedHoloPanel, a LightSpill,
## BinaryBits) put on `host`. `tools/design_lab/motion_lab.gd` calls `play` for its "kit"
## demos; `test_motion_lab_demos.gd` checks the piece reads the entry. A view (dev tool path).

const DEMO_ANCHOR := Vector2(300, 260)
## Offset from the anchor to the CRT panel's top-left corner.
const CRT_OFFSET := Vector2(200, 40)
## Size of the demo CRT panel.
const CRT_SIZE := Vector2(420, 80)
## Where the dissolving sticker's bits fly to, from the anchor.
const BITS_TARGET_OFFSET := Vector2(260, -160)
## Radii of the demo pencil circle.
const PENCIL_RADII := Vector2(60, 48)
## Offset from the anchor to the holo panel's top-left corner.
const HOLO_OFFSET := Vector2(200, 120)
## Size of the demo holo panel.
const HOLO_SIZE := Vector2(400, 240)
## Offset from the anchor to the bits-burst source rect's top-left corner.
const BURST_RECT_OFFSET := Vector2(80, 30)
## Size of the bits-burst source rect.
const BURST_RECT_SIZE := Vector2(160, 60)


## Builds the piece for `id` on `host` and plays its motion. Returns the demo's length (s).
static func play(id: StringName, host: Control) -> float:
	match id:
		&"gate_keycard_stagger", &"gate_socket_ring", &"gate_breach_ready":
			# ART-8 8w: the Central Server gate with all three Exploits (no boss wheel).
			var g := CentralServerGate.new()
			var all_kinds: Array[int] = []
			all_kinds.assign(CentralServerGate.KINDS)
			g.setup(&"meridian", "Meridian", "THE MASTER MANIFEST", 4, all_kinds, all_kinds.size(), null, null)
			host.add_child(g)
			return Motion.seconds(CentralServerGate.STAGGER) * all_kinds.size() + Motion.seconds(CentralServerGate.SLAP) 				+ Motion.seconds(CentralServerGate.RING) + Motion.seconds(CentralServerGate.READY)
		&"crt_type_on", &"crt_caret_blink", &"crt_hex_scroll":
			var p := CrtTerminalPanel.new()
			p.position = DEMO_ANCHOR - CRT_OFFSET
			p.size = CRT_SIZE
			host.add_child(p)
			return p.type_on("RAM 5/12  // next turn +2")
		&"sticker_slap", &"sticker_peel", &"sticker_dissolve", &"sticker_gloss_sweep", &"sticker_sweep_period", &"sticker_peel_back", &"sticker_corner_flutter", \
				&"sticker_hover", &"sticker_press":
			var s := VinylSticker.new()
			s.text = "SEND IT"
			s.fill = VinylSticker.Fill.HOLO
			host.add_child(s)
			s.place_center(DEMO_ANCHOR)
			match id:
				&"sticker_slap":
					return s.slap()
				&"sticker_peel":
					return s.peel()
				&"sticker_dissolve":
					var bits := BinaryBits.new()
					host.add_child(bits)
					return s.dissolve(bits, host.global_position + DEMO_ANCHOR + BITS_TARGET_OFFSET)
				&"sticker_gloss_sweep":
					return s.sweep()
				&"sticker_sweep_period":
					StickerSweepQueue.reset()
					StickerSweepQueue.next_period()
					return s.sweep()
				&"sticker_corner_flutter":
					s.flutter = true
					s.rest_curl = VinylSticker.FLUTTER_LOW
					return Motion.seconds(id)
				&"sticker_peel_back":
					s.set_state(VinylSticker.State.HOVER)
					return Motion.seconds(&"sticker_hover")
				&"sticker_hover":
					s.set_state(VinylSticker.State.HOVER)
					return Motion.seconds(id)
				&"sticker_press":
					s.set_state(VinylSticker.State.PRESSED)
					return Motion.seconds(id)
		&"pencil_write_on", &"pencil_wipe", &"pencil_glint":
			var m := GreasePencilMark.new()
			m.ink = GreasePencilMark.Ink.THREAT
			m.auto_write = false  # the demo plays the write or the wipe itself
			host.add_child(m)
			m.add_stroke(PencilShapes.hand_circle(DEMO_ANCHOR, PENCIL_RADII, 3))
			if id == &"pencil_wipe":
				return m.wipe()
			return m.write_on()
		&"holo_bands":
			var h := DecryptedHoloPanel.new()
			h.scrim = false
			h.position = DEMO_ANCHOR - HOLO_OFFSET
			h.size = HOLO_SIZE
			host.add_child(h)
			return Motion.seconds(id)
		&"light_spill_breathe":
			var l := LightSpill.new()
			l.position = DEMO_ANCHOR
			host.add_child(l)
			return Motion.seconds(id)
		&"bits_flight":
			var b := BinaryBits.new()
			host.add_child(b)
			var o := host.global_position
			var arr := b.burst_from_rect(Rect2(o + DEMO_ANCHOR - BURST_RECT_OFFSET, BURST_RECT_SIZE), o + DEMO_ANCHOR + BITS_TARGET_OFFSET, Palette.CELL_PINK)
			return arr[arr.size() - 1] if not arr.is_empty() else 0.0
	return 0.0
