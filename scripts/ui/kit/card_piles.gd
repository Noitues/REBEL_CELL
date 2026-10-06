class_name CardPiles
extends Control
## S-CARDFACE (CMB-04; round 41 `combat_typical_v4`): the DECK and DISCARD piles beside the hand,
## each a small stack of face-down cards with its count on top and its word beside it; DECK over
## DISCARD, one column, so the hand keeps its width. Drawn procedurally: the concept draws the piles
## as plain dark card backs and there is no exported card back (the art pass baked only the faces).
## The counts are the fight's (the scene sets them). View only.

## One pile's card at text scale 1 (px; the deal's pile mark, CombatFxLayer.PILE_SIZE), the layers of
## its stack and their step (px), the gap between the piles and between a pile and its word (px at 1).
const CARD := CombatFxLayer.PILE_SIZE
const LAYERS := 3
const LAYER_STEP := 2.0
const GAP := 6.0
const WORD_GAP := 2.0
## The count's and the word's lettering at scale 1 (px), the outline's width.
const COUNT_PX := 20
const WORD_PX := 10
const EDGE_W := 1.5
const WORDS := ["DECK", "DISCARD"] # TR

var deck_count: int = 0
var discard_count: int = 0
var text_scale: float = 1.0


func _init(ts: float = 1.0) -> void:
	name = "CardPiles"
	mouse_filter = Control.MOUSE_FILTER_PASS
	size_flags_vertical = Control.SIZE_SHRINK_END
	set_scale_to(ts)


## Sizes the piles for text scale `ts`.
func set_scale_to(ts: float) -> void:
	text_scale = ts
	var word_w := 0.0
	for w in WORDS:
		word_w = maxf(word_w, Palette.mono().get_string_size(tr(w), HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(WORD_PX * ts)).x)
	var w := maxf(CARD.x * ts + LAYER_STEP * (LAYERS - 1), word_w)
	custom_minimum_size = Vector2(w, (_pile_h(ts)) * 2.0 + GAP * ts)
	queue_redraw()


func _pile_h(ts: float) -> float:
	return CARD.y * ts + LAYER_STEP * (LAYERS - 1) + WORD_GAP * ts + Palette.mono().get_height(roundi(WORD_PX * ts))


## Shows `deck` cards in the draw pile and `discard` in the discard pile.
func set_counts(deck: int, discard: int) -> void:
	deck_count = deck
	discard_count = discard
	tooltip_text = tr("Deck: %d cards to draw. Discard: %d cards (shuffled back in when the deck runs out).") % [deck, discard]
	queue_redraw()


## Pile `i`'s top card (local; 0 = DECK, 1 = DISCARD).
func pile_rect(i: int) -> Rect2:
	var card := CARD * text_scale
	var x := (size.x - card.x - LAYER_STEP * (LAYERS - 1)) * 0.5
	return Rect2(Vector2(x, i * (_pile_h(text_scale) + GAP * text_scale)), card)


func _draw() -> void:
	var s := text_scale
	var display := Palette.display()
	var mono := Palette.mono()
	var cfs := roundi(COUNT_PX * s)
	var wfs := roundi(WORD_PX * s)
	for i in 2:
		var top := pile_rect(i)
		var n := deck_count if i == 0 else discard_count
		# the stack: one layer per card up to LAYERS, the top one last
		for k in range(mini(LAYERS, maxi(1, n)) - 1, -1, -1):
			var r := Rect2(top.position + Vector2(LAYER_STEP * k, LAYER_STEP * (LAYERS - 1 - k)), top.size)
			draw_rect(r, Palette.INK if n > 0 else Color(Palette.INK, 0.4))
			draw_rect(r, Palette.TEXT_LO, false, EDGE_W)
		var face := Rect2(top.position + Vector2(0.0, LAYER_STEP * (LAYERS - 1)), top.size)
		var count := str(n)
		var cw := display.get_string_size(count, HORIZONTAL_ALIGNMENT_LEFT, -1, cfs).x
		draw_string(display, Vector2(face.position.x + (face.size.x - cw) * 0.5, face.position.y + face.size.y * 0.5 + (display.get_ascent(cfs) - display.get_descent(cfs)) * 0.5),
			count, HORIZONTAL_ALIGNMENT_LEFT, -1, cfs, Palette.TEXT_HI)
		var word := tr(WORDS[i])
		var ww := mono.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, wfs).x
		draw_string(mono, Vector2((size.x - ww) * 0.5, face.end.y + WORD_GAP * s + mono.get_ascent(wfs)), word, HORIZONTAL_ALIGNMENT_LEFT, -1, wfs, Palette.TEXT_LO)
