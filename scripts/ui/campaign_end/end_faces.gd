class_name EndFaces
extends RefCounted
## ART-11 4D: the faces the corp paper of the campaign end uses (ART_BIBLE v2 §2.9): Courier
## Prime Regular / Bold (1A's `Palette.paper` / `paper_bold`) for typed fields and titles, and
## the auditor's ballpoint hand. Look only.


## Courier Prime Regular (typed fields).
static func typed() -> Font:
	return Palette.paper()


## Courier Prime Bold (typed titles).
static func typed_bold() -> Font:
	return Palette.paper_bold()


## The auditor's ballpoint hand. No ballpoint face ships (DECISIONS "Art direction — ART-11 4D
## campaign end", open question): the one handwriting face (Permanent Marker), small and in
## ballpoint blue, never in the grease pencil's wax colours.
static func ballpoint() -> Font:
	return Palette.pencil()
