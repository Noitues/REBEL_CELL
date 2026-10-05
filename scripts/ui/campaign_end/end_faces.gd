class_name EndFaces
extends RefCounted
## ART-11 4D: the faces the corp paper of the campaign end needs (ART_BIBLE v2 §2.9): Courier
## Prime Regular / Bold for typed fields and titles. A seam until 1A lands Courier Prime in
## `assets/fonts/`: it reads the shipped face there first and, until then, the same OFL face
## the GUT addon carries, then falls back to the mono face. Look only.

## Where Courier Prime ships once 1A copies it (bible §2.9), then the copy the repo already has.
const TYPE_PATHS: Array[String] = ["res://assets/fonts/CourierPrime-Regular.ttf", "res://addons/gut/fonts/CourierPrime-Regular.ttf"]
const TYPE_BOLD_PATHS: Array[String] = ["res://assets/fonts/CourierPrime-Bold.ttf", "res://addons/gut/fonts/CourierPrime-Bold.ttf"]

static var _cache: Dictionary = {}


## Courier Prime Regular (typed fields), or the mono face.
static func typed() -> Font:
	return _first(TYPE_PATHS)


## Courier Prime Bold (typed titles), or the mono face.
static func typed_bold() -> Font:
	return _first(TYPE_BOLD_PATHS)


## The auditor's ballpoint hand. No ballpoint face ships (DECISIONS "Art direction — ART-11 4D
## campaign end", open question): the marker face, small and in ballpoint blue.
static func ballpoint() -> Font:
	return Palette.marker()


static func _first(paths: Array[String]) -> Font:
	var key := paths[0]
	if _cache.has(key):
		return _cache[key]
	var f: Font = null
	for p in paths:
		if ResourceLoader.exists(p):
			f = load(p) as Font
			if f != null:
				break
	if f == null:
		f = Palette.mono()
	_cache[key] = f
	return f
