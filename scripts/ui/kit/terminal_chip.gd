class_name TerminalChip
extends StickerButton
## ART-2 2D (ART_BIBLE v2 §3.1, §4.13): a terminal chip button beside SEND IT (RESPIN, UNDO):
## a dark CRT plate with a cyan edge, the verb in mono caps over its cost and key ("RESPIN" /
## "4 RAM [R]"). Hover lifts it with a `>` caret (never a colour-only cue), focus is the lime
## brackets, a press drops it; disabled greys it with the lock tick (the undo block shows
## on UNDO this way, never as a word, D12). It keeps StickerButton's API (`text`, set_label,
## refit, pre_translated, drawn_icon) so the scene and its tests drive it unchanged.

## Lettering sizes (px at text scale 1.0): the verb and the line under it.
const WORD_FONT := 15
const SUB_FONT := 12
## Height, padding and the caret's room (px at text scale 1.0).
const CHIP_HEIGHT := 40.0
const CHIP_PAD := 10.0
const CARET_ROOM := 10.0


func _init(p_text: String = "") -> void:
	super(p_text, HudSkin.TERMINAL_BG, 0.0)
	material = HudSkin.crt_material()


## The verb (first word) and the rest of the label (cost and key).
func parts() -> PackedStringArray:
	var t := shown_text().strip_edges()
	var cut := t.find(" ")
	if cut < 0:
		return PackedStringArray([t, ""])
	return PackedStringArray([t.substr(0, cut), t.substr(cut + 1)])


func _fit() -> void:
	var s := Settings.text_scale
	var p := parts()
	var f := HudSkin.mono()
	var w := maxf(f.get_string_size(p[0], HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(WORD_FONT * s)).x,
		f.get_string_size(p[1], HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(SUB_FONT * s)).x)
	custom_minimum_size = Vector2(w + (CHIP_PAD * 2.0 + CARET_ROOM) * s, CHIP_HEIGHT * s)
	size = get_combined_minimum_size()


func _draw() -> void:
	var s := Settings.text_scale
	var st := state()
	var r := Rect2(Vector2(0.0, KitState.lift(st)), size)
	var edge := KitState.edge_color(st, HudSkin.TERMINAL_EDGE)
	HudSkin.draw_terminal_panel(self, r, edge, HudSkin.TERMINAL_BG)
	var p := parts()
	var f := HudSkin.mono()
	var wf := roundi(WORD_FONT * s)
	var sf := roundi(SUB_FONT * s)
	var col := KitState.label_color(st)
	var x := r.position.x + (CHIP_PAD + CARET_ROOM) * s
	if st == KitState.HOVER or st == KitState.FOCUS:
		draw_string(f, Vector2(r.position.x + CHIP_PAD * 0.5 * s, r.position.y + CHIP_PAD * 0.4 * s + f.get_ascent(wf)), ">", HORIZONTAL_ALIGNMENT_LEFT, -1, wf, HudSkin.FOCUS)
	draw_string(f, Vector2(x, r.position.y + CHIP_PAD * 0.4 * s + f.get_ascent(wf)), p[0], HORIZONTAL_ALIGNMENT_LEFT, -1, wf, col)
	if p[1] != "":
		draw_string(f, Vector2(x, r.end.y - CHIP_PAD * 0.5 * s), p[1], HORIZONTAL_ALIGNMENT_LEFT, -1, sf,
			HudSkin.PIP_ON if not disabled else HudSkin.TERMINAL_DIM)
	KitState.draw_frame(self, r, st, true)
