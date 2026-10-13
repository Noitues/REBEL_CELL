class_name FaceText
extends RefCounted
## W2-A4 (6A): the words on a card / chip face. A card or chip whose use depends on something the
## player may not have (an inner ring, a slice of the right type) says so on its face, so it is never
## a trap. The conditions are read from the content (its effects, its allowed slice types); the face
## keeps the content's own description and adds the condition after it. Offers are unchanged.

## A card that moves the inner ring: only a wheel with an inner ring (one earned by rank) can play it.
const NEEDS_INNER := "Needs an inner ring." # TR
## A Firmware chip limited to some slice types: the types, in the player's words.
const FITS_ONLY := "Fits %s slices only." # TR
const FITS_SEP := " or " # TR


## The rules text of `card` as drawn on its face (and its tooltip): its description, then the condition.
static func card_text(card: CardData) -> String:
	if card == null:
		return ""
	var out := TextDb.t(card, "description")
	if needs_inner_ring(card):
		out += " " + TranslationServer.translate(NEEDS_INNER)
	return out


## The rules text of an offer: a card's, a Firmware chip's (with the slice types it fits), else the
## content's description.
static func offer_text(res: Resource) -> String:
	if res is CardData:
		return card_text(res as CardData)
	var d := TextDb.t(res, "description") if res != null and "description" in res else ""
	if res is FirmwareData:
		var fits := fits_text(res as FirmwareData)
		if fits != "":
			d += " " + fits
	return d


## True when a card needs the inner ring: one of its effects names it.
static func needs_inner_ring(card: CardData) -> bool:
	for e in card.effects:
		if e != null and e.ring_scope == RC.RingScope.INNER:
			return true
	return false


## "Fits SHIM slices only." for a chip limited to slice types ("" when it fits any slice).
static func fits_text(fw: FirmwareData) -> String:
	if fw.allowed_slice_types.is_empty():
		return ""
	var names := PackedStringArray()
	for t in fw.allowed_slice_types:
		names.append(TranslationServer.translate(String(Palette.SLICE_WORDS.get(t, "?"))))
	return TranslationServer.translate(FITS_ONLY) % TranslationServer.translate(FITS_SEP).join(names)
