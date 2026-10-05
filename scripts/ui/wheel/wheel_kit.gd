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
const BOSS_HUB := {&"the_manifest": &"hub_priority_routing", &"civic_core": &"hub_emergency_powers",
	&"commons_array": &"hub_station_keeping", &"renewal_engine": &"hub_auto_renew", &"dispatch_core": &"hub_root_access"}

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
