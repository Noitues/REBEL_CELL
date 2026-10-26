class_name TideGlyphView
extends Control
## Phase 3: one TideGlyphs glyph as a Control, so a panel row can carry a tier, a response or a card face between its labels.
## View only: it draws the glyph it is told.

enum Kind { TIER, RESPONSE, CARD, TYPE, VERB, FLAME, BEAM, CARD_TICK, PIP_DECK, TILE, CHIP, METER }

var kind: int = Kind.TIER
## The tier word, the verb or type letter, the response array, the card [id, type, verb].
var word: String = ""
var response: Array = []
var card: Array = []
var dim: bool = false
var gold: bool = false
var sent_type: String = ""
var color: Color = Palette.CLEAR
## A card face's title and Heat cost (-1: none).
var title: String = ""
var heat: int = -1
## A forecast tile's outcome count, the INFECTED meter's INFECTED and healthy cards.
var count: int = 0
var healthy: int = 0


static func tier(tier_word: String, px: float = 20.0) -> TideGlyphView:
	var g := TideGlyphView.new()
	g.kind = Kind.TIER
	g.word = tier_word
	g.custom_minimum_size = Vector2(px, px)
	return g


static func resp(r: Array, px: float = 30.0, sent: String = "", is_dim: bool = false) -> TideGlyphView:
	var g := TideGlyphView.new()
	g.kind = Kind.RESPONSE
	g.response = r
	g.sent_type = sent
	g.dim = is_dim
	g.custom_minimum_size = Vector2(px, px)
	return g


static func card_face(c: Array, size_px: Vector2, is_dim: bool = false, is_gold: bool = false, p_title: String = "", p_heat: int = -1) -> TideGlyphView:
	var g := TideGlyphView.new()
	g.kind = Kind.CARD
	g.card = c
	g.dim = is_dim
	g.gold = is_gold
	g.title = p_title
	g.heat = p_heat
	g.custom_minimum_size = size_px
	return g


## A forecast tile: the tier glyph on its color, "xN" when `n` outcomes share it.
static func tile(tier_word: String, size_px: Vector2, n: int = 1) -> TideGlyphView:
	var g := TideGlyphView.new()
	g.kind = Kind.TILE
	g.word = tier_word
	g.count = n
	g.custom_minimum_size = size_px
	return g


## A route chip: the letter (A, B, C) on the beam's type color (the map's beam carries the same chip).
static func chip(letter: String, col: Color, px: float = 18.0) -> TideGlyphView:
	var g := TideGlyphView.new()
	g.kind = Kind.CHIP
	g.word = letter
	g.color = col
	g.custom_minimum_size = Vector2(px, px)
	return g


## The INFECTED vs healthy meter with the CITY LOST line.
static func meter(infected: int, healthy_n: int, size_px: Vector2) -> TideGlyphView:
	var g := TideGlyphView.new()
	g.kind = Kind.METER
	g.count = infected
	g.healthy = healthy_n
	g.custom_minimum_size = size_px
	return g


static func icon(k: int, px: float = 16.0, col: Color = Palette.CLEAR) -> TideGlyphView:
	var g := TideGlyphView.new()
	g.kind = k
	g.color = col
	g.custom_minimum_size = Vector2(px, px)
	return g


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS


func _draw() -> void:
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.5
	match kind:
		Kind.TIER:
			TideGlyphs.tier(self, c, word, r * 0.92)
		Kind.RESPONSE:
			TideGlyphs.response(self, c, response, r * 0.8, dim, sent_type)
		Kind.CARD:
			TideGlyphs.card_face(self, Rect2(Vector2.ZERO, size), card, dim, gold, title, heat)
		Kind.TILE:
			TideGlyphs.tier_tile(self, Rect2(Vector2.ZERO, size), word, count)
		Kind.CHIP:
			TideGlyphs.route_chip(self, c, word, r, color)
		Kind.METER:
			TideGlyphs.infected_meter(self, Rect2(Vector2.ZERO, size), count, healthy)
		Kind.TYPE:
			TideGlyphs.type_shape(self, c, word, r * 0.9, color if color.a > 0.0 else TideGlyphs.type_color(word))
		Kind.VERB:
			TideGlyphs.verb(self, c, word, r * 0.85, color if color.a > 0.0 else TideGlyphs.INK)
		Kind.FLAME:
			TideGlyphs.flame(self, c, r * 0.65)
		Kind.BEAM:
			TideGlyphs.beam_tick(self, c, color if color.a > 0.0 else TideGlyphs.GOLD)
		Kind.CARD_TICK:
			TideGlyphs.card_tick(self, c, color if color.a > 0.0 else TideGlyphs.GOLD)
		Kind.PIP_DECK:
			var rr := Rect2(c - Vector2(r, r) * 0.7, Vector2(r, r) * 1.4)
			if word == "WOUND":
				draw_rect(rr, TideGlyphs.WOUND_FILL)
				TideGlyphs.crack(self, c, r * 0.6, TideGlyphs.RED, 1.5)
			else:
				draw_rect(rr, TideGlyphs.type_color(word).darkened(0.45))
				draw_rect(rr, TideGlyphs.type_color(word), false, 1.0)
