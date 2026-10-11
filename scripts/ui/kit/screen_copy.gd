class_name ScreenCopy
extends RefCounted
## M14 SPILL (DECISIONS "M14 SPILL"): a fresh copy of the screen just before a screen reader draws.
## A canvas shader that takes `hint_screen_texture` reads the last copy of the screen made in its
## canvas layer. Since B1a b that is usually the scrim's AfterScrim (UiScrimPools), taken over the
## pooled world before any UI: a reader drawn later (a modal's glass blur, a sign's light spill)
## then paints that world back over the UI drawn in between (the title's delete-slot confirm lost
## the menu behind its blur; the Mainframe's SignSpill smeared the street over the pegboard), and a
## mipmapped reader in between can leave it blurred. `before` gives the reader its own viewport
## BackBufferCopy, an internal child drawn behind its parent, so the copy lands right before the
## reader wherever it draws (top level, behind its parent, any layer) and follows its visibility.
## Cost: one viewport copy per visible reader. View only.

const NODE_NAME := "ScreenCopy"


## Gives `reader` a viewport copy of the screen made just before it draws. Returns the copy.
static func before(reader: CanvasItem) -> BackBufferCopy:
	var copy := BackBufferCopy.new()
	copy.name = NODE_NAME
	copy.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
	copy.show_behind_parent = true
	reader.add_child(copy, false, Node.INTERNAL_MODE_FRONT)
	return copy
