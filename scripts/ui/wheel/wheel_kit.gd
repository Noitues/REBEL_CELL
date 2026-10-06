class_name WheelKit
extends RefCounted
## Which kit a wheel wears (ART-2 2A; ART_BIBLE v2 2.4, 3.2-3.7, 3.16): the one place the wheel
## stack picks its material, tokens and screens, so 1A's palette v2 and 1B's material kit switch
## in here. A kit is the player's (the class accent on the Cell's machined steel) or a corp's
## (hue + material + crest, round 18 values; the material colours live in the disc shader's kit
## tables, indexed by `theme`). Rank picks the tier treatment: regular I, elite II, boss III (3.7).

## Kit order = the disc shader's `theme` index.
const THEMES: Array[StringName] = [&"player", &"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]
const SCREENS := "res://assets/wheel/screens/%s_screen.png"
const SCENES := "res://assets/wheel/screens/%s_scene.png"
const META := "res://assets/wheel/screens/meta.json"
## The atlases' row for a corp special (rows 0..8 follow RC.SliceType).
const SPECIAL_ROW := 9
## Boss hubs without their own core glyph yet: the bible's enemy hub emblems (3.3) by boss.
const BOSS_HUB := {&"civic_core": &"hub_emergency_powers",
	&"commons_array": &"hub_station_keeping", &"renewal_engine": &"hub_auto_renew", &"dispatch_core": &"hub_root_access"}

## Parity S-WHEEL (CMB-02, designer group ruling 2026-10-05: combat matches the concept). The
## screens' tone step (the disc shader's `tone`): the round 41 composite passes the disc has no
## room for (make_combat.bloom over the bright parts, frames.add_glow) folded into one step, so the
## slice screens read as saturated as the concept's: saturation away from the luma, then the part
## over the threshold lifted. Material, like the shader's kit tables; `tone` mirrors it for tests.
## WHEEL round 2 (designer): per kit. The player, Meridian and Rebel_Cell popped too much (less
## saturation and lift); Meridian also pulls its screens towards its palette orange (`pull`, the
## screen's luma re-coloured in the corp colour) and brightens them (`expo`), as the baked atlas's
## brown read too dark. Keys: sat (saturation), thresh / gain (the lift), pull, expo.
const TONE := {
	&"player": {"sat": 1.15, "thresh": 0.35, "gain": 0.6, "pull": 0.0, "expo": 1.0},
	&"meridian": {"sat": 1.1, "thresh": 0.35, "gain": 0.6, "pull": 0.65, "expo": 1.6},
	&"solace": {"sat": 1.4, "thresh": 0.3, "gain": 1.1, "pull": 0.0, "expo": 1.0},
	&"halcyon": {"sat": 1.4, "thresh": 0.3, "gain": 1.1, "pull": 0.0, "expo": 1.0},
	&"orbital": {"sat": 1.4, "thresh": 0.3, "gain": 1.1, "pull": 0.0, "expo": 1.0},
	&"rebel_cell": {"sat": 0.9, "thresh": 0.4, "gain": 0.4, "pull": 0.0, "expo": 0.85},
}
## The lit frame (CMB-02): the class accent's wash over the player's outer bevel and the glow of
## the frame's accent hairlines; a corp frame wears its rim instead of the wash (CMB-03).
const PLAYER_FRAME_TINT := 0.62
const PLAYER_FRAME_GLOW := 0.8
const CORP_FRAME_GLOW := 0.35
## The frame's outer radius (master units): the player's D4 frame and the wider corp frame that
## carries the corp rim (d4corp.render: R1 = R_OUT + 54 / + 64), and the elite collar beyond it.
const R_FRAME_PLAYER := 414.0
const R_FRAME_CORP := 424.0
const ELITE_COLLAR := 14.0

static var _meta: Dictionary = {}

var theme: int = 0
var corporation_id: StringName = &""
## 1 regular / player, 2 elite, 3 boss.
var tier: int = 1
var is_boss: bool = false
var is_elite: bool = false
## The frame accent: the class accent on the player's wheel, the corp hue on an enemy's.
var accent: Color = Palette.CELL_PINK
## The tier colours (3.7): the corp's primary and secondary (2.4), the player's gold and paper.
var tier_primary: Color = Palette.RESIST_GOLD
var tier_secondary: Color = Palette.PAPER
var screens: Texture2D = null
var scenes: Texture2D = null
## The enemy's name and its corp line for the boss banner.
var title: String = ""
var crest: StringName = &""


## The kit for combatant `c` (`class_id` names the player's class for its accent).
static func of(c: CombatantState, lookup: ContentLookup, class_id: StringName = &"breaker") -> WheelKit:
	var k := WheelKit.new()
	if c == null:
		return k
	var data: Resource = lookup.get_content(c.source_id) if lookup != null else null
	if c.is_player:
		k.accent = Palette.class_accent(class_id)
	else:
		var corp: StringName = data.corporation_id if data != null and "corporation_id" in data else &""
		k.corporation_id = corp
		k.theme = maxi(0, THEMES.find(corp)) if corp != &"" else 0
		if k.theme == 0 and corp == &"":
			k.theme = THEMES.find(&"rebel_cell")
		k.accent = Palette.corp_color(corp) if corp != &"" else Palette.corp_color(&"rebel_cell")
		k.is_boss = data != null and "is_boss" in data and bool(data.is_boss)
		k.is_elite = data != null and "is_elite" in data and bool(data.is_elite)
		k.tier = 3 if k.is_boss else (2 if k.is_elite else 1)
		k.crest = StringName("crest_" + String(THEMES[k.theme]))
		k.tier_primary = Palette.corp_color(THEMES[k.theme])
		k.tier_secondary = Palette.corp_secondary(THEMES[k.theme])
	k.screens = _load(SCREENS % THEMES[k.theme])
	k.scenes = _load(SCENES % THEMES[k.theme]) if k.theme != 0 else null
	return k


## Kit `theme`'s name (`player`, a corporation id).
func kit_name() -> StringName:
	return THEMES[theme]


## The D4 frame's outer radius (master units) before the elite collar and the threat ring.
func frame_radius() -> float:
	return R_FRAME_PLAYER if theme == 0 else R_FRAME_CORP


## The corp rim this kit's frame wears (the disc's `rim_kind`): 0 on the player's wheel, else the
## corp's theme index (d4corp.corp_rim: Meridian hazard, Solace studs, Halcyon colonnade,
## Orbital azimuth, Rebel_Cell broken segments).
func rim_kind() -> int:
	return theme


## This kit's tone step values (TONE[kit_name()]).
func tone_params() -> Dictionary:
	return TONE.get(kit_name(), TONE[&"player"])


## The screens' tone step (CMB-02, round 2 per kit), as the disc shader's `tone` applies it to a
## screen colour with this kit's values and accent.
func tone(c: Color) -> Color:
	var t := tone_params()
	var v := Vector3(c.r, c.g, c.b)
	var luma := Vector3(0.2126, 0.7152, 0.0722)
	var l := v.dot(luma)
	var acc := Vector3(accent.r, accent.g, accent.b)
	var la := maxf(0.05, acc.dot(luma))
	v = v.lerp(acc * (l / la), float(t["pull"])) * float(t["expo"])
	l = v.dot(luma)
	var sat := float(t["sat"])
	v = Vector3(maxf(0.0, lerpf(l, v.x, sat)), maxf(0.0, lerpf(l, v.y, sat)), maxf(0.0, lerpf(l, v.z, sat)))
	var th := float(t["thresh"])
	v += Vector3(maxf(v.x - th, 0.0), maxf(v.y - th, 0.0), maxf(v.z - th, 0.0)) * float(t["gain"])
	return Color(v.x, v.y, v.z, c.a)


## The hub emblem's glyph id for combatant `c` (3.3): its core's glyph, else its boss's enemy hub,
## else the corp crest.
func hub_glyph(c: CombatantState) -> StringName:
	if c == null or c.wheel == null:
		return &""
	var own := WheelGlyphs.hub_id(c.wheel.hub_id)
	if WheelGlyphs.has(own):
		return own
	if BOSS_HUB.has(c.source_id):
		return BOSS_HUB[c.source_id]
	return crest


## The baked screen atlases' layout (frames, rows, the texture-space size, the corp scene row).
static func meta() -> Dictionary:
	if _meta.is_empty() and FileAccess.file_exists(META):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(META))
		if parsed is Dictionary:
			_meta = parsed
	return _meta


## The scene row (fraction of the screen height the upright corp scene centres on) and the strip
## kept clear under it (fraction, -1 = none) for this kit.
func scene_rows() -> Vector2:
	var s: Dictionary = meta().get("scene", {}).get(String(kit_name()), {})
	return Vector2(float(s.get("yc", 0.5)), float(s.get("cut", -1.0)))


static func _load(path: String) -> Texture2D:
	return load(path) as Texture2D if ResourceLoader.exists(path) else null
