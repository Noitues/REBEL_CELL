class_name PaperIndexTab
extends MenuChip
## M14 BIG-TEXT b (art director): a paper index tab sticking out of a sheet's foot (the folded
## work order's MORE / BACK). A MenuChip (pad, keyboard, the focus frame, the press) drawn as a
## tab of the sheet's stock: its top tucks under the sheet (`tuck` px, drawn by the owner over
## it), the foot corners cut, a thin ink edge and contact shadow, its word at body size in ink.
## The owner turns it with the sheet (FitBuildBox.tab). View only.

## The foot corners' cut (px at 1.0) and the shadow's drop (px at 1.0).
const CORNER := 6.0
const SHADOW_DROP := 2.0
## The room above and below the word (px): a slim tab (a chip's is MenuChip.PAD's).
const PAD_V := 4.0

## How far the tab's top is under the sheet (px): the word centres in what shows below it.
var tuck: float = 0.0


func _init(p_text: String = "") -> void:
	super._init(p_text, "", Palette.CELL_PINK)
	plate = &""
	label_step = UiTheme.BODY
	refit()


## The tab's size: the chip's width; its word's height, PAD_V round it and the tucked part.
func measure() -> Vector2:
	var m := super.measure()
	m.y = ceilf(Chrome.caps_font(label_step).get_height(Chrome.px(label_step)) + PAD_V * 2.0 + tuck)
	return m


func _draw() -> void:
	var st := KitState.of(self)
	var hot := st == KitState.HOVER or st == KitState.FOCUS or st == KitState.PRESSED
	var k := Settings.text_scale
	var r := Rect2(Vector2(0.0, KitState.lift(st)), size)
	var cut := minf(r.size.y * 0.35, CORNER * k)
	var pts := PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), Vector2(r.end.x, r.end.y - cut),
		Vector2(r.end.x - cut, r.end.y), Vector2(r.position.x + cut, r.end.y), Vector2(r.position.x, r.end.y - cut)])
	var drop := PackedVector2Array()
	for p in pts:
		drop.append(p + Vector2(0.0, SHADOW_DROP * k))
	draw_colored_polygon(drop, Color(Palette.INK, 0.28))
	draw_colored_polygon(pts, Palette.PAPER if hot else Palette.PAPER_ALT)
	var edge := pts.duplicate()
	edge.append(pts[0])
	draw_polyline(edge, Color(Palette.INK, 0.35), 1.0)
	var lf := Chrome.caps_font(label_step)
	var lp := Chrome.px(label_step)
	var word := shown_text()
	var w := lf.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, lp).x
	var y := r.position.y + tuck + (r.size.y - tuck - lf.get_height(lp)) * 0.5 + lf.get_ascent(lp)
	var x := r.position.x + (r.size.x - w) * 0.5
	var ink := Palette.INK if not disabled else Palette.INK.lerp(Palette.PAPER, 0.5)
	if hot and not disabled:
		x += lp * CARET_SHARE * 0.5
		HighContrast.draw_text(self, lf, Vector2(x - lp * CARET_SHARE, y), ">", HORIZONTAL_ALIGNMENT_LEFT, -1, lp, Palette.CELL_PINK)
	HighContrast.draw_text(self, lf, Vector2(x, y), word, HORIZONTAL_ALIGNMENT_LEFT, -1, lp, ink)
	KitState.draw_frame(self, r, st, false)
