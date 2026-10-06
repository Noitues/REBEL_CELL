class_name AssetCard
extends Button
## A defence asset as the round 40 concept's dark card (parity RAID-01; `raid_view_v3`'s card row,
## ART_BIBLE v2 §4.8): the concept's own sticker card, baked by its generator
## (`tools/art_pipeline/raid/bake_defence_cards.py`: the dark face, the glyph window with the
## asset's glyph in its colour, the colour band along the top, the white die-cut and gloss), with
## its words written live at the concept's spots: the name (display face), `INT n` in the asset's
## colour, the count `xN`, and two rule lines (what it does, how it picks). Emits Button signals;
## the scene decides what a press means (deploy to the Site picked on the board). The card's size
## is `card_size()`; a narrower slot (the row fit) shrinks the whole card evenly (never squashed).

var asset_id: StringName = &""
var display_name: String = ""
var integrity: int = 0
var count: int = 1
var _hot: bool = false

## A card at text scale 1.0 (px; the concept card's aspect at the old card's height, so the map
## keeps its room), and how much of the text scale its size follows.
const BASE_SIZE := Vector2(105, 120)
const SIZE_FOLLOW := 0.5
## Lettering at text scale 1.0 (px): the name, the numbers row, the rule lines.
const NAME_SIZE := 16
const NUMBER_SIZE := 11
const EFFECT_SIZE := 10
## The least lettering (px); the words shrink together down to it while they don't fit the face.
const MIN_NUMBER_SIZE := 8
## The concept's layout on its 150 x 172 face (ui19.asset_card, 1x px): the words' left and right
## edges, where the name starts (under the glyph window), the face's foot margin.
const FACE_PX := Vector2(150, 172)
const TEXT_LEFT := 12.0
const TEXT_RIGHT := 138.0
const NAME_TOP := 84.0
const FOOT_PAD := 6.0
## The concept's grey for the rule lines (ui19: (190, 186, 205)).
const RULE_COLOR := Color(190.0 / 255.0, 186.0 / 255.0, 205.0 / 255.0)
## The disabled shade over the face (the numbers stay readable under it).
const DISABLED_SHADE := Color(0, 0, 0, 0.3)
## Hot (hovered / focused): the card lifts this many px (x the face's k) and gets an acid edge.
const HOT_LIFT := 4.0
const HOT_EDGE := 2.0
## The card's drop shadow (concept `place`: offset and opacity) and the face's corner (1x px).
const SHADOW_OFFSET := Vector2(3, 5)
const SHADOW_ALPHA := 0.38
const CORNER := 12.0
const FACE_RADIUS := 10.0
const FACE_BORDER := 7.0
## The baked cards and their manifest.
const CARD_DIR := "res://assets/raid/cards/"
const MANIFEST := "res://assets/raid/cards/manifest.json"

## Rule line 2 for a gun (how it picks its target) and for a lure (concept TRAY words).
const RULE_TARGETING := {RC.AssetTargeting.FIRST_IN_PATH: "first in path", RC.AssetTargeting.LOWEST_INTEGRITY: "weakest threat", # TR
	RC.AssetTargeting.HIGHEST_DAMAGE: "hardest hitter"} # TR
const RULE_OWN_NODE := "own node only" # TR
const RULE_LURE := "threats route to it" # TR

static var _manifest: Dictionary = {}
static var _textures: Dictionary = {}

## What the asset does (the effect line) and how it picks (the rule line): from its data.
var effect_kind: String = ""
var effect_text: String = ""
var rule_text: String = ""


func _init(p_asset_id: StringName = &"", p_name: String = "", p_integrity: int = 0, p_count: int = 1) -> void:
	asset_id = p_asset_id
	display_name = p_name
	integrity = p_integrity
	count = p_count
	custom_minimum_size = card_size()
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


## The card's size at the current text scale.
static func card_size() -> Vector2:
	return BASE_SIZE * (1.0 + (Settings.text_scale - 1.0) * SIZE_FOLLOW)


## The baked cards' manifest (loaded once).
static func manifest() -> Dictionary:
	if _manifest.is_empty() and FileAccess.file_exists(MANIFEST):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
		if parsed is Dictionary:
			_manifest = parsed
	return _manifest


## Asset `id`'s baked card (null when the concept has none).
static func texture_of(id: StringName) -> Texture2D:
	var key := String(id)
	if not _textures.has(key):
		var p := CARD_DIR + key + ".png"
		_textures[key] = load(p) if ResourceLoader.exists(p) else null
	return _textures[key]


## Asset `id`'s colour (the card's band, glyph and INT): the concept's, else AssetIcon's.
static func color_of(id: StringName) -> Color:
	var cards: Dictionary = manifest().get("cards", {})
	if cards.has(String(id)):
		var c: Array = (cards[String(id)] as Dictionary).get("color", [])
		if c.size() >= 3:
			return Color8(int(c[0]), int(c[1]), int(c[2]))
	return AssetIcon.color_of(id)


## The whole card image in the control (local): the baked image's aspect, as wide as the control
## allows, top-centred (lifted while hot).
func card_rect() -> Rect2:
	var tex := texture_of(asset_id)
	var aspect := float(tex.get_width()) / float(tex.get_height()) if tex != null else BASE_SIZE.x / BASE_SIZE.y
	var w := minf(size.x, size.y * aspect)
	var r := Rect2(Vector2((size.x - w) * 0.5, 0), Vector2(w, w / aspect))
	return r


## The die-cut's corner radius (px): the concept face's corner plus its border (ui19
## card_sticker radius 10, border 7), at the face's scale. The parked card's vinyl matches it.
func die_cut_radius() -> float:
	return (FACE_RADIUS + FACE_BORDER) * face_k()


## The concept's 150 x 172 face inside the card (local).
func face_rect() -> Rect2:
	var r := card_rect()
	var fb: Array = manifest().get("face_box", [])
	if fb.size() < 4 or texture_of(asset_id) == null:
		return r
	return Rect2(r.position + Vector2(float(fb[0]), float(fb[1])) * r.size, Vector2(float(fb[2]), float(fb[3])) * r.size)


## The face's scale: screen px per concept px.
func face_k() -> float:
	return face_rect().size.x / FACE_PX.x


## The words' sizes and spots on the face (local): {"name", "num", "rule": px, "name_y", "num_y",
## "effect_y", "rule_y": baselines}. The sizes shrink together until the words end above the
## face's foot.
func _layout() -> Dictionary:
	var face := face_rect()
	var k := face_k()
	var s := Settings.text_scale
	var disp := Palette.display()
	var mono := Palette.mono()
	var plex := Palette.body_medium()
	var share := 1.0
	var out := {}
	while true:
		var ns := maxi(MIN_NUMBER_SIZE, roundi(NAME_SIZE * s * share))
		var num := maxi(MIN_NUMBER_SIZE, roundi(NUMBER_SIZE * s * share))
		var rs := maxi(MIN_NUMBER_SIZE, roundi(EFFECT_SIZE * s * share))
		var y := face.position.y + NAME_TOP * k
		var name_y := y + disp.get_ascent(ns)
		y += disp.get_height(ns)
		var num_y := y + mono.get_ascent(num)
		y += mono.get_height(num)
		# Room for both rule lines on every card (the concept's two), so a row's cards share
		# one lettering size whatever their words.
		var effect_y := y + plex.get_ascent(rs)
		y += plex.get_height(rs)
		var rule_y := y + plex.get_ascent(rs)
		y += plex.get_height(rs)
		out = {"name": ns, "num": num, "rule": rs, "name_y": name_y, "num_y": num_y, "effect_y": effect_y, "rule_y": rule_y, "end": y}
		if y <= face.end.y - FOOT_PAD * k or (ns <= MIN_NUMBER_SIZE and num <= MIN_NUMBER_SIZE and rs <= MIN_NUMBER_SIZE):
			break
		share -= 0.05
	return out


## The largest size <= `px` at which `text` fits `width` in `font` (not under MIN_NUMBER_SIZE).
static func _fit(font: Font, text: String, px: int, width: float) -> int:
	var fs := px
	while fs > MIN_NUMBER_SIZE and font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width:
		fs -= 1
	return fs


func _draw() -> void:
	var lift := Vector2(0, -HOT_LIFT * face_k()) if _hot and not disabled else Vector2.ZERO
	draw_set_transform(lift)
	var card := card_rect()
	var face := face_rect()
	var k := face_k()
	var col := color_of(asset_id)
	var round_box := func(fill: Color, rect: Rect2, edge: float = 0.0, edge_col: Color = Color.TRANSPARENT) -> void:
		var sb := StyleBoxFlat.new()
		sb.bg_color = fill
		sb.set_corner_radius_all(roundi(CORNER * k))
		if edge > 0.0:
			sb.draw_center = false
			sb.set_border_width_all(maxi(1, roundi(edge)))
			sb.border_color = edge_col
		draw_style_box(sb, rect)
	round_box.call(Color(Palette.SHADOW, SHADOW_ALPHA), Rect2(card.position + SHADOW_OFFSET * k, card.size))
	var tex := texture_of(asset_id)
	if tex != null:
		draw_texture_rect(tex, card, false)
	else:
		# No concept card for this asset: the face in the concept's colours, AssetIcon's picture.
		round_box.call(Palette.NIGHT_SKY, face)
		AssetIcon.draw_icon(self, face.position + Vector2(FACE_PX.x * 0.5, WINDOW_CENTRE_Y) * k, WINDOW_ICON_R * k, asset_id, false)
	if _hot and not disabled:
		round_box.call(Color.TRANSPARENT, card.grow(HOT_EDGE), HOT_EDGE * Settings.text_scale, Palette.CELL_ACID)
	var lay := _layout()
	var left := face.position.x + TEXT_LEFT * k
	var right := face.position.x + TEXT_RIGHT * k
	var width := right - left
	var disp := Palette.display()
	var mono := Palette.mono()
	var plex := Palette.body_medium()
	var name_up := display_name.to_upper()
	var ns := _fit(disp, name_up, int(lay["name"]), width)
	draw_string(disp, Vector2(left, float(lay["name_y"])), name_up, HORIZONTAL_ALIGNMENT_LEFT, width, ns, Palette.PAPER)
	# INT n in the asset's colour, xN at the right edge (paper).
	var num := int(lay["num"])
	var it := integrity_text()
	var ct := count_text()
	var cw := mono.get_string_size(ct, HORIZONTAL_ALIGNMENT_LEFT, -1, num).x
	draw_string(mono, Vector2(left, float(lay["num_y"])), it, HORIZONTAL_ALIGNMENT_LEFT, width - cw, num, col)
	draw_string(mono, Vector2(right - cw, float(lay["num_y"])), ct, HORIZONTAL_ALIGNMENT_LEFT, -1, num, Palette.PAPER)
	var rs := int(lay["rule"])
	if effect_text != "":
		draw_string(plex, Vector2(left, float(lay["effect_y"])), effect_text, HORIZONTAL_ALIGNMENT_LEFT, width, _fit(plex, effect_text, rs, width), RULE_COLOR)
	if rule_text != "":
		draw_string(plex, Vector2(left, float(lay["rule_y"])), rule_text, HORIZONTAL_ALIGNMENT_LEFT, width, _fit(plex, rule_text, rs, width), RULE_COLOR)
	if disabled:
		round_box.call(DISABLED_SHADE, face)
	draw_set_transform(Vector2.ZERO)


## The fallback face's glyph spot (concept window centre, 1x px from the face's top) and radius.
const WINDOW_CENTRE_Y := 43.0
const WINDOW_ICON_R := 24.0


## Sets the card's effect and rule lines from the asset's data (`effect_of`, `rule_of`).
func set_effect(data: DefenseAssetData) -> void:
	var e := effect_of(data)
	effect_kind = e[0]
	effect_text = e[1]
	rule_text = rule_of(data)
	queue_redraw()


## An asset's effect as [pictogram kind, words] from its numbers: a gun "HITS 4 x2 · REACH
## 1", an ICE lock "HOLDS 2 STEPS", a decoy "LURES, PULL 3"; ["", ""] for none.
static func effect_of(data: DefenseAssetData) -> Array[String]:
	if data == null:
		return ["", ""] as Array[String]
	if data.damage > 0:
		var t := TranslationServer.translate("HITS %d") % data.damage
		if data.shots_per_step > 1:
			t += " x%d" % data.shots_per_step
		if data.range_hops > 0:
			t += TranslationServer.translate(" · REACH %d") % data.range_hops
		return ["shoot", t] as Array[String]
	if data.delay_steps > 0:
		return ["hold", TranslationServer.translate("HOLDS %d STEPS") % data.delay_steps] as Array[String]
	if data.decoy_pull > 0:
		return ["lure", TranslationServer.translate("LURES, PULL %d") % data.decoy_pull] as Array[String]
	return ["", ""] as Array[String]


## An asset's second rule line (the concept's): how a gun picks ("first in path", "weakest
## threat", "hardest hitter"; "own node only" with no reach), "threats route to it" for a lure,
## "" for a hold. Translated.
static func rule_of(data: DefenseAssetData) -> String:
	if data == null:
		return ""
	if data.damage > 0:
		if data.range_hops <= 0:
			return TranslationServer.translate(RULE_OWN_NODE)
		return TranslationServer.translate(String(RULE_TARGETING.get(data.targeting, "")))
	if data.decoy_pull > 0 and data.delay_steps <= 0:
		return TranslationServer.translate(RULE_LURE)
	return ""


## The effect line's rect (local): the first rule line on the face.
func effect_rect() -> Rect2:
	if effect_text == "":
		return Rect2()
	var lay := _layout()
	var face := face_rect()
	var k := face_k()
	var plex := Palette.body_medium()
	var rs := int(lay["rule"])
	var top := float(lay["effect_y"]) - plex.get_ascent(rs)
	return Rect2(face.position.x + TEXT_LEFT * k, top, (TEXT_RIGHT - TEXT_LEFT) * k, plex.get_height(rs))


## The integrity as the card writes it ("INT 10", the concept's word), in the player's language.
func integrity_text() -> String:
	return "%s %d" % [tr("INT"), integrity]


## How many sit in the Armory as the card writes it ("x1"), in the player's language.
func count_text() -> String:
	return tr("x%d") % count


## What the card's numbers mean (its tooltip adds this under the asset's description).
func numbers_tip() -> String:
	return tr("INT %d: integrity, the hits it takes before it breaks. x%d: how many are in the Armory to deploy.") % [integrity, count]
