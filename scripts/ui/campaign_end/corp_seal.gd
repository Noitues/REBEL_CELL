class_name CorpSeal
extends RefCounted
## ART-11 4D: a corporation's seal (ART_BIBLE v2 §2.4 crests; round 20 lost20.py `seal`): a
## double ring with the house name round it and the corp's emblem inside (the concept's own
## emblems, exported: Halcyon's halo and triangle, Meridian's crane, Solace's helix, Orbital's
## ringed planet, DISPATCH's hex cell). The rings and the name stay drawn: the name is the
## translated house name. Drawn on any CanvasItem (the ransom notice, the dossier's
## letterhead). Look only.

## The rings' widths and the name band's radius, as shares of the seal's radius.
const OUTER_LINE := 0.06
const INNER_LINE := 0.03
const INNER_RING := 0.68
const NAME_RING := 0.84
const NAME_SIZE := 0.17
## The emblem's half size as a share of the radius (round 20 `seal`: 0.44 of the diameter).
const CREST := 0.44
## The emblems (M14 asset parity, `tools/art_pipeline/parity/export_campaign_end.py`).
const EMBLEM_DIR := "res://assets/campaign_end/emblem_%s.png"
## Arc segments for drawn circles.
const SEGMENTS := 48


## Draws the seal of `corporation_id` centred on `c`, radius `r`, in `col`, with `house_name`
## (translated) round it.
static func draw_seal(ci: CanvasItem, c: Vector2, r: float, corporation_id: StringName, col: Color, house_name: String) -> void:
	ci.draw_arc(c, r * (1.0 - OUTER_LINE * 0.5), 0.0, TAU, SEGMENTS, col, maxf(1.0, r * OUTER_LINE), true)
	ci.draw_arc(c, r * INNER_RING, 0.0, TAU, SEGMENTS, col, maxf(1.0, r * INNER_LINE), true)
	# The name round the band, repeated to fill it, each letter on the tangent.
	var f := Palette.mono()
	var fs := maxi(1, roundi(r * NAME_SIZE))
	var words := ("  %s  *" % house_name).to_upper()
	var ring := words + words
	var n := ring.length()
	for i in n:
		var a := -PI * 0.5 + TAU * i / n
		var p := c + Vector2(cos(a), sin(a)) * r * NAME_RING
		ci.draw_set_transform(p, a + PI * 0.5, Vector2.ONE)
		ci.draw_char(f, Vector2(-fs * 0.25, fs * 0.35), ring[i], fs, col)
	ci.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	draw_crest(ci, c, r * CREST, corporation_id, col)


## Draws `corporation_id`'s emblem centred on `c`, half size `r`: round 20 `seal`'s emblem (the
## round 6 corp emblem, M14 asset parity: `assets/campaign_end/emblem_<corp>.png`, exported by
## the concept's own scripts), tinted `col`.
static func draw_crest(ci: CanvasItem, c: Vector2, r: float, corporation_id: StringName, col: Color) -> void:
	var t := emblem(corporation_id)
	if t != null:
		ci.draw_texture_rect(t, Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0), false, col)


## Corporation `corporation_id`'s emblem mask (white), loaded once; null for an unknown id.
static func emblem(corporation_id: StringName) -> Texture2D:
	if not _emblems.has(corporation_id):
		var path := EMBLEM_DIR % String(corporation_id)
		_emblems[corporation_id] = load(path) as Texture2D if ResourceLoader.exists(path) else null
	return _emblems[corporation_id]


static var _emblems: Dictionary = {}
