class_name StickerArt
extends RefCounted
## The art pass's own word stickers (M14 asset parity): words the concepts drew as finished vinyl
## (`assets/fx/stickers/`, exported by `tools/art/export_combat_stickers.py` from the round 19-39
## generators on art-concepts-r43). A VinylSticker whose word is one of these shows the image instead of
## lettering it (its slap, peel, dissolve, hover, press and grey states still run on it); any other word,
## or a translated one, is lettered live. Lookup only.

const DIR := "res://assets/fx/stickers/"
## word -> [file, the lettering's px in the image (its size x the image's scale), whether the image carries
## its own finish (gloss, rim, drop shadow: the material adds none)].
const WORDS := {
	"SEND IT": ["send_it.png", 148.0, false],
	"PERFECT": ["word_perfect.png", 50.0, true],
	"GOOD": ["word_good.png", 42.0, true],
	"WEAK": ["word_weak.png", 50.0, true],
}

static var _cache: Dictionary = {}


## The baked sticker for `word` as shown ({"tex", "lettering_px", "own_finish"}), or {} when the art pass
## has none (the sticker letters it live).
static func lookup(word: String) -> Dictionary:
	if not WORDS.has(word):
		return {}
	if not _cache.has(word):
		var row: Array = WORDS[word]
		var tex := load(DIR + String(row[0])) as Texture2D
		_cache[word] = {"tex": tex, "lettering_px": float(row[1]), "own_finish": bool(row[2])} if tex != null else {}
	return _cache[word]
