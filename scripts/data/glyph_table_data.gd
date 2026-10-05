class_name GlyphTableData
extends Resource
## The glyph atlas and its id -> glyph table (ART-1 1C; ART_BIBLE 3.5, 5.2, 6.2).
## `content/config/glyph_table.tres` is the shipped one: read-only at runtime.
##
## The atlas (`assets/glyphs/glyph_atlas.png`, built by tools/art_pipeline/glyphs/) is a
## single-channel signed distance field: cell i of `glyph_names` sits at column i % columns,
## row i / columns; each cell is `cell_px` square with the glyph's box (`box_px`) centred in
## it; a texel is 0.5 + distance / (2 * spread_px), inside positive, in cell pixels.
##
## Keys (`ids`) name what the game shows a glyph for, by kind: `type_<slice type>`,
## `status_<status>`, `effect_<effect type>` (card pictograms; `effect_spin_ccw` and
## `effect_nudge_inner` for the variants), `hub_<hub core id>`, `seg_<segment id>`,
## `firmware_<id>`, `daemon_<id>`, `exploit_<exploit type>`, `slice_<slice id>` (a special
## slice whose glyph is not its type's), `word_<corporation program word>` and `satellite`.
## A key whose art does not exist yet maps to PENDING (listed under DECISIONS "Open
## questions for the designer").

## The stand-in glyph for ids whose art does not exist yet.
const PENDING := &"pending"
## Where the shipped table lives.
const TABLE_PATH := "res://content/config/glyph_table.tres"

## The distance-field atlas.
@export var atlas: Texture2D
## Atlas cell names in cell order.
@export var glyph_names: PackedStringArray = PackedStringArray()
## Cells per atlas row.
@export var columns: int = 16
## Cell size in atlas pixels.
@export var cell_px: int = 128
## The glyph box inside a cell (atlas pixels); the margin holds the outline and AA.
@export var box_px: int = 96
## Distance range each side of the edge (atlas pixels) the field encodes.
@export var spread_px: int = 16
## Outline width as a fraction of the glyph box (bible 3.5: 0.075).
@export var outline_width: float = 0.075
## The 16 px rule (bible 5.2): the size the silhouettes are compared at.
@export var twin_px: int = 16
## The 16 px rule: the highest soft IoU allowed between two different glyphs.
@export var twin_max_iou: float = 0.68
## Pairs exempt from the 16 px rule ("a|b", atlas names): kept alike on purpose or known
## borderline (bible 5.2), each named in DECISIONS.
@export var twin_exceptions: PackedStringArray = PackedStringArray()
## Key -> atlas name (both StringName).
@export var ids: Dictionary = {}

var _index: Dictionary = {}


## The shipped table (content/config/glyph_table.tres).
static func shipped() -> GlyphTableData:
	return load(TABLE_PATH) as GlyphTableData


## The table key of slice type `type` (RC.SliceType).
static func key_for_slice_type(type: int) -> StringName:
	return StringName("type_" + String(RC.SliceType.keys()[type]).to_lower())


## The table key of status `status` (RC.Status, not NONE).
static func key_for_status(status: int) -> StringName:
	return StringName("status_" + String(RC.Status.keys()[status]).to_lower())


## The table key of a card effect's pictogram (RC.EffectType).
static func key_for_effect(type: int) -> StringName:
	return StringName("effect_" + String(RC.EffectType.keys()[type]).to_lower())


## The table key of an Exploit type (RC.ExploitType, not NONE).
static func key_for_exploit(type: int) -> StringName:
	return StringName("exploit_" + String(RC.ExploitType.keys()[type]).to_lower())


## The table key of a corporation's own program word (Palette.CORP_SLICE_WORDS).
static func key_for_word(word: String) -> StringName:
	return StringName("word_" + word.to_lower())


## The atlas name for `key`, or &"" when the table has no such key.
func glyph_for(key: StringName) -> StringName:
	return StringName(ids.get(key, &""))


## The atlas name for slice `slice`: its own (`slice_<id>`) when it has one, else its type's.
func glyph_for_slice(slice: SliceData) -> StringName:
	if slice == null:
		return &""
	var own := glyph_for(StringName("slice_" + String(slice.id)))
	return own if own != &"" else glyph_for(key_for_slice_type(slice.slice_type))


## True when `key` is mapped to the stand-in (no art yet).
func is_pending(key: StringName) -> bool:
	return glyph_for(key) == PENDING


## The cell index of atlas name `glyph`, or -1.
func cell_of(glyph: StringName) -> int:
	if _index.size() != glyph_names.size():
		_index.clear()
		for i in glyph_names.size():
			_index[StringName(glyph_names[i])] = i
	return int(_index.get(glyph, -1))


## The atlas region (pixels) of the whole cell of `glyph`; an empty rect when unknown.
func cell_region(glyph: StringName) -> Rect2:
	var i := cell_of(glyph)
	if i < 0 or columns <= 0:
		return Rect2()
	return Rect2((i % columns) * cell_px, (i / columns) * cell_px, cell_px, cell_px)


## How many atlas rows the cells need.
func rows() -> int:
	return 0 if columns <= 0 else (glyph_names.size() + columns - 1) / columns


## Problems with the table (empty when it is usable).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if atlas == null:
		errors.append("Glyph table has no atlas.")
	if columns <= 0 or cell_px <= 0 or box_px <= 0 or box_px > cell_px or spread_px <= 0:
		errors.append("Glyph table geometry is invalid (columns %d, cell %d, box %d, spread %d)." % [columns, cell_px, box_px, spread_px])
	if outline_width < 0.0 or outline_width * box_px > (cell_px - box_px) * 0.5 + 0.001 or outline_width * box_px > spread_px:
		errors.append("Glyph outline %.3f does not fit the cell margin or the field." % outline_width)
	if twin_px <= 0 or twin_max_iou <= 0.0 or twin_max_iou > 1.0:
		errors.append("Glyph 16 px rule settings are invalid.")
	var seen := {}
	for n in glyph_names:
		if n == "" or seen.has(n):
			errors.append("Glyph name '%s' is empty or repeated." % n)
		seen[n] = true
		if n.begins_with("placeholder"):
			errors.append("Glyph '%s' is a placeholder (bible 3.5: not in the game)." % n)
	if not seen.has(String(PENDING)):
		errors.append("Glyph table has no '%s' stand-in." % PENDING)
	if atlas != null and columns > 0 and (atlas.get_width() != columns * cell_px or atlas.get_height() != rows() * cell_px):
		errors.append("Glyph atlas is %dx%d, the table needs %dx%d." % [atlas.get_width(), atlas.get_height(), columns * cell_px, rows() * cell_px])
	for k in ids:
		if not (k is StringName) or not (ids[k] is StringName):
			errors.append("Glyph id '%s' must map a StringName to a StringName." % str(k))
		elif not seen.has(String(ids[k])):
			errors.append("Glyph id '%s' maps to unknown glyph '%s'." % [k, ids[k]])
	for pair in twin_exceptions:
		var ab := pair.split("|")
		if ab.size() != 2 or not seen.has(ab[0]) or not seen.has(ab[1]):
			errors.append("Glyph twin exception '%s' must name two atlas glyphs." % pair)
	return errors
