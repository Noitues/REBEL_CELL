class_name RingMods
extends RefCounted
## Round 45 (designer-approved 2026-10-13, docs/concepts/round45_inner_ring/NOTES.md on art-pass 2216c126):
## how the inner ring's modifiers read. One table per segment id: its mark in the ghost wedge (`kind`, size,
## layout), its tint (the ring notch, the wedge edge, the word plate's border, the tooltip title), the words
## on its plate. The designer's rulings apply: marks at 38 %, halo 40 %, every mark about 1.3x (DOUBLE 75),
## spacing kept, PIERCE chevrons 1.4x with a 2 px ink keyline, one modifier per slice. View data only.

## Mark families the wedge shader draws (its `mod` uniform picks the family through `kind`).
enum Kind { GLYPH, CHEVRON, GLITCH }

## The id the wedge shader reads for "no wedge" (a blank segment, no ring).
const NONE := -1

## Per segment: `mod` (the shader's id), `kind`, `tint`, `size` (master units: a glyph's atlas box, a
## chevron's width, a glitch block), `row` (radial pitch), `arc` (arc-length pitch; a chevron's column
## step in degrees), `glyph` (atlas key, GLYPH only), `keyline` (ink keyline, master units), `mark` (the
## text before the word on the plate; a glyph is drawn when empty). DOUBLE's box is 100 because the atlas's
## "x2" glyph fills about 0.53 of its box: its lettering stands about 53 tall, NOTES' 75-pt mark x 0.7 cap.
## DOUBLE / PIERCE / CORRUPT are NOTES' own; ANCHOR / ACCEL / ECHO are not in the round (it rendered
## statuses there): they take the glyph family at the status marks' size and spacing, ACCEL in Heat
## orange (NOTES' OVERCLOCKED, which the concept drew with the accelerator's texture), ECHO in the
## encrypted cyan (the ring's own echo colour), ANCHOR in the ring's own anchor steel (DECISIONS 2026-10-13).
const MODS := {
	&"seg_x2": {"mod": 0, "kind": Kind.GLYPH, "tint": Palette.RING_DOUBLE, "size": 100.0, "row": 68.0, "arc": 92.0,
		"glyph": &"seg_x2", "keyline": 0.0, "mark": "×2"},
	&"seg_pierce": {"mod": 1, "kind": Kind.CHEVRON, "tint": Palette.RING_PIERCE, "size": 50.0, "row": 30.0, "arc": 14.0,
		"glyph": &"seg_pierce", "keyline": 2.0, "mark": ""},
	&"seg_corrupt": {"mod": 2, "kind": Kind.GLITCH, "tint": Palette.RING_CORRUPT, "size": 29.0, "row": 29.0, "arc": 29.0,
		"glyph": &"seg_corrupt", "keyline": 0.0, "mark": ""},
	&"seg_anchor": {"mod": 3, "kind": Kind.GLYPH, "tint": Palette.RING_ANCHOR, "size": 57.0, "row": 64.0, "arc": 78.0,
		"glyph": &"seg_anchor", "keyline": 0.0, "mark": ""},
	&"seg_accelerator": {"mod": 4, "kind": Kind.GLYPH, "tint": Palette.RING_ACCEL, "size": 57.0, "row": 64.0, "arc": 78.0,
		"glyph": &"seg_accelerator", "keyline": 2.0, "mark": ""},
	&"seg_echo": {"mod": 5, "kind": Kind.GLYPH, "tint": Palette.RING_ECHO, "size": 57.0, "row": 64.0, "arc": 78.0,
		"glyph": &"seg_echo", "keyline": 0.0, "mark": ""},
}
## CORRUPT's second colour: a block whose hash passes GLITCH_PINK_AT is pink; one past GLITCH_FILL_AT fills.
const GLITCH_PINK := Palette.RING_GLITCH_PINK
## A blank segment's active plate and tick dot: cream at 80 %.
const BLANK_TINT := Palette.RING_BLANK
## The ring's inactive segments: their texture at 42 %; the tint notch along the outer lip (r 124..127, 90 %,
## ending 3 units short of each groove).
const DIM_TEX := 0.42
const NOTCH_W := 3.0
const NOTCH_A := 0.90
const NOTCH_END := 3.0
## The active segment's raised plate (3 in, 4 out of the band), its gunmetal lift, the tint lips' width, the
## end caps (5 units across r 95..133) and the glow (blur 7, 85 %).
const RAISE_IN := 3.0
const RAISE_OUT := 4.0
const PLATE_LIGHT := 1.15
const LIP_W := 1.1
const CAP_W := 5.0
const CAP_OVER := 2.0
const GLOW_PX := 7.0
const GLOW_A := 0.85

## The ghost wedge (master units, R_IN 130 .. R_OUT 360): r 133..353, its radial edges inset 5.
const WEDGE_R_IN := 133.0
const WEDGE_R_OUT := 353.0
const WEDGE_INSET := 5.0
## Fill, bottom to top: ink shade, tint wash, an ink halo under each mark, the marks (designer: 38 / 40 %).
const SHADE := 0.25
const WASH := 0.10
const HALO := 0.40
const PATTERN := 0.38
## The halo: the mark dilated 5 and blurred 3.
const HALO_GROW := 5.0
const HALO_BLUR := 3.0
## The read window: inside the read block's ellipse (96 x 50, feather 10) marks and halo are halved.
const READ_RADII := Vector2(96.0, 50.0)
const READ_FEATHER := 10.0
const READ_CLEAR := 0.5
## The edge: a 3-unit tint line at 90 % plus a 12-unit glow at 45 % (blur 7). Static.
const EDGE_W := 3.0
const EDGE_A := 0.90
const EDGE_GLOW_A := 0.45
const EDGE_GLOW_BLUR := 7.0
## The first mark row's centre sits this share of a row pitch out from the wedge's inner edge.
const ROW_LEAD := 0.55
## PIERCE streams outward at this many rows a second; CORRUPT's blocks re-roll this often (ring rule).
const PIERCE_ROWS_PER_S := 2.0
const GLITCH_RATE := 12.0
const GLITCH_FILL_AT := 0.55
const GLITCH_PINK_AT := 0.88
const GLITCH_SEED := 3.0

## The notch tick on the needle line: base 17 wide at r 114, tip at r 146, a 3-unit dot in the tint at r 119.
const TICK_BASE_R := 114.0
const TICK_TIP_R := 146.0
const TICK_W := 17.0
const TICK_DOT_R := 119.0
const TICK_DOT := 3.0
const TICK_INK := 2.0
const TICK_CREAM := Palette.RING_CREAM

## The word plate (words on demand): r = R_OUT - 14, 9 degrees clockwise of the needle (mirrored when it
## would leave the screen), 32 px tall at text 1.0, #0C0A12 at 95 %, a 2 px tint border, radius 6, 22 px
## lettering, a leader to r = R_OUT - 40.
const PLATE_R := 346.0
const PLATE_DEG := 9.0
const PLATE_H := 32.0
const PLATE_FILL := Palette.RING_PLATE_FILL
const PLATE_BORDER := 2.0
const PLATE_RADIUS := 6.0
const PLATE_FONT := 22
const PLATE_PAD := 10.0
const PLATE_GAP := 6.0
const PLATE_LEADER_R := 320.0
const PLATE_MARGIN := 8.0


## The table entry of segment `seg_id` (empty for a blank or unknown segment: no wedge, no notch).
static func of(seg_id: StringName) -> Dictionary:
	return MODS.get(seg_id, {})


## The shader id of segment `seg_id`'s modifier (NONE for a blank segment).
static func mod_id(seg_id: StringName) -> int:
	return int(of(seg_id).get("mod", NONE))


## Segment `seg_id`'s tint (cream at 80 % for a blank).
static func tint(seg_id: StringName) -> Color:
	return of(seg_id).get("tint", BLANK_TINT)
