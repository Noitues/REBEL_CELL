class_name KitMaterials
extends RefCounted
## The material kit's register (ART-1 1B; ART_BIBLE v2 §1.2, §5.3, §6.3, §6.4): every material,
## the component that applies it, its shaders, its VfxTier (the tier of its resting look; its
## motions carry their own in ui_motion.tres) and its motion entries. Tests walk it (every
## shader reads the `reduce_effects` global, every material has a tier, every motion has an
## entry and a lab demo); the kit sheet lays it out. Pure data.

const T0 := VfxTier.T0
const T1 := VfxTier.T1
const T2 := VfxTier.T2

const ALL: Dictionary = {
	&"crt_terminal": {"component": "CrtTerminalPanel", "tier": T0,
		"shaders": ["res://shaders/kit/crt_terminal.gdshader"],
		"motions": [&"crt_type_on", &"crt_caret_blink", &"crt_hex_scroll"]},
	&"vinyl_sticker": {"component": "VinylSticker", "tier": T0,
		"shaders": ["res://shaders/kit/vinyl_sticker.gdshader", "res://shaders/kit/sticker_fill.gdshader"],
		"motions": [&"sticker_slap", &"sticker_peel", &"sticker_dissolve", &"sticker_gloss_sweep", &"sticker_sweep_period", &"sticker_peel_back", &"sticker_corner_flutter",
			&"sticker_hover", &"sticker_press"]},
	&"grease_pencil": {"component": "GreasePencilMark", "tier": T0,
		"shaders": ["res://shaders/kit/marker_stroke.gdshader"],
		"motions": [&"pencil_write_on", &"pencil_wipe", &"pencil_glint"]},
	&"light_spill": {"component": "LightSpill", "tier": T0,
		"shaders": ["res://shaders/kit/light_spill.gdshader"],
		"motions": [&"light_spill_breathe"]},
	&"decrypted_holo": {"component": "DecryptedHoloPanel", "tier": T0,
		"shaders": ["res://shaders/kit/decrypted_holo.gdshader"],
		"motions": [&"holo_bands"]},
	&"corp_paper": {"component": "CorpPaperPanel", "tier": T0,
		"shaders": ["res://shaders/kit/corp_paper.gdshader"],
		"motions": []},
	&"binary_bits": {"component": "BinaryBits", "tier": T2,
		"shaders": ["res://shaders/kit/binary_bits.gdshader"],
		"motions": [&"bits_flight"]},
	&"toon_ink": {"component": "ToonInkMaterial", "tier": T0,
		"shaders": ["res://shaders/kit/toon_ink.gdshader", "res://shaders/kit/toon_ink_hull.gdshader"],
		"motions": []},
}


## Every motion id of the kit, in register order.
static func motion_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for k in ALL:
		for id in ALL[k]["motions"]:
			out.append(id)
	return out


## Every shader path of the kit.
static func shader_paths() -> Array[String]:
	var out: Array[String] = []
	for k in ALL:
		for p in ALL[k]["shaders"]:
			out.append(p)
	return out
