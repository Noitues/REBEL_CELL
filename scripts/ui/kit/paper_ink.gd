class_name PaperInk
extends RefCounted
## Art pass WF (ART_BIBLE §12; v2 §5.6 keeps it): how the custom-drawn PAPER pieces look in
## high contrast (on main: the Polaroid, the toast, the crew dossier, the taped note and the
## subtitle paper). ART-0 F: ported from art-pass b9af7e3, on top of area C's HighContrast. PAPER keeps its stock colour, but
## every word on it goes INK (well over 7:1 on every stock), every edge is EDGE_PX of opaque
## INK, and nothing on it is translucent (backs, tape). Out of high contrast each call returns
## what it was given. Pure look helpers; they read `Settings.high_contrast`.

## A paper piece's edge in high contrast (px).
const EDGE_PX := 2.0
## The contrast every word on paper meets in high contrast (§12).
const MIN_CONTRAST := 7.0


## True while high contrast is on.
static func on() -> bool:
	return Settings.high_contrast


## A word's colour on paper: `col` normally, INK in high contrast.
static func text(col: Color) -> Color:
	return Palette.INK if on() else col


## An edge's colour: `col` normally, opaque INK in high contrast.
static func edge(col: Color) -> Color:
	return Palette.INK if on() else col


## An edge's width (px): `w` normally, at least EDGE_PX in high contrast.
static func edge_width(w: float) -> float:
	return maxf(w, EDGE_PX) if on() else w


## A back, tape or fill on the paper: `col` normally; in high contrast opaque, as `col`
## looks laid over `under` (the paper stock by default).
static func opaque(col: Color, under: Color = Palette.PAPER) -> Color:
	if not on():
		return col
	var c := Palette.over(under, col)
	c.a = 1.0
	return c
