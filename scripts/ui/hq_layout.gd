class_name HqLayout
extends RefCounted
## HQ-B (M14, HQ redesign direction B "THE HAND"; `docs/art_review/HQ_REDESIGN/direction_B*.{png,jpg}`): where
## the HQ page's pieces sit over the city, as pure maths on the page's size and the text
## scale (tests read it; the page places by it). Layout at 1280x720 (the concept's 1920 x
## 2/3): the raid's paper work order at the top left while a raid is pending, the hand's
## tabs (CREW / MARKET / DEFENCE) and the hand of cards along the foot, the selected
## thing's card at the right over the one pink sticker slot at the bottom right; the map's
## free part is what is left (the camera fits the network into it). Words grow with the
## text; drawn objects (cards, the sticker) stop at x`OBJECT_SCALE_MAX` (STYLE 5.6).

## The page's margin (px at 1.0).
const MARGIN := 16.0
## Gap between pieces (px at 1.0).
const GAP := 10.0
## A hand card (px at 1.0): direction B's 113 x 150 at 720.
const CARD := Vector2(113, 150)
## How far the picked card lifts out of the hand (px at 1.0).
const LIFT := 14.0
## The tabs' column (px at 1.0; it grows with the words).
const TABS_WIDTH := 128.0
## The work order's width (px at 1.0; the paper grows with its words).
const ORDER_WIDTH := 228.0
## The selected thing's card (px at 1.0).
const CARD_COLUMN := 300.0
## The verb slot: the sticker, its price tag and its system word (px at 1.0).
const VERB := Vector2(280, 120)
## Drawn objects stop growing with the text at this scale (STYLE 5.6).
const OBJECT_SCALE_MAX := 1.3
## Words stop widening the panels at this scale (their lines wrap past it).
const WORDS_SCALE_MAX := 1.6


## A drawn object's growth at text scale `s`.
static func object_scale(s: float) -> float:
	return clampf(s, 1.0, OBJECT_SCALE_MAX)


## A panel of words' growth at text scale `s`.
static func words_scale(s: float) -> float:
	return clampf(s, 1.0, WORDS_SCALE_MAX)


## The page's rects (page px, origin at the page's top left) for a page of size `page` at
## text scale `s`; `order`: a raid's work order shows. Keys: "order", "tabs", "hand",
## "card", "verb", "free" (the map's free part).
static func rects(page: Vector2, s: float, order: bool) -> Dictionary:
	var o := object_scale(s)
	var w := words_scale(s)
	var m := MARGIN
	var hand_h := CARD.y * o + LIFT * o
	var hand_top := page.y - m - hand_h
	var tabs := Rect2(m, hand_top, TABS_WIDTH * w, hand_h)
	var verb := Rect2(page.x - m - VERB.x * o, page.y - m - VERB.y * o, VERB.x * o, VERB.y * o)
	var hand := Rect2(tabs.end.x + GAP, hand_top, maxf(CARD.x * o, verb.position.x - GAP - tabs.end.x - GAP), hand_h)
	var col_w := minf(CARD_COLUMN * w, page.x * 0.5)
	var card := Rect2(page.x - m - col_w, m, col_w, maxf(0.0, verb.position.y - GAP - m))
	var order_r := Rect2(m, m, ORDER_WIDTH * w, maxf(0.0, hand_top - GAP - m)) if order else Rect2()
	var left := order_r.end.x + m if order else m
	var free := Rect2(left, m, maxf(1.0, card.position.x - m - left), maxf(1.0, hand_top - m - m))
	return {"order": order_r, "tabs": tabs, "hand": hand, "card": card, "verb": verb, "free": free}
