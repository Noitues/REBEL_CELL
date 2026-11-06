CAP = {
'send_it': {
 'cur': 'Flat yellow, cropped by the right and bottom edges, hint hidden under it.',
 'A': 'One-line sticker, vinyl yellow gradient, white die-cut 9 px, fully inside the 24 px margin; UNDO tab and hint dock to it.',
 'B': 'Stacked SEND / IT with the arrow-through-ring verb mark always on the plate; squarer, findable at a glance.',
 'C': 'Round die-cut seal (button silhouette, stitched ring): the one round shape on the screen, so it is the verb.'},
'undo_chip': {
 'cur': 'Floats 60 px above SEND IT, [Z] same size as the word.',
 'A': 'Tab tucked under the sticker top edge, same width; word 22, Z as a keycap; locked = grey edge + tick.',
 'B': 'Glyph-led compact chip right-aligned, hinged to the sticker with two ink clasps.',
 'C': 'Hangs under the sticker like a secondary link: keycap first, word, undo arc; locked = grey tick.'},
'nameplate': {
 'cur': 'Alone in the corner over the outer arcs; cyan equals the terminal cyan.',
 'A': 'Corner label, two lines + class emblem disc, vinyl cyan gradient (a step lighter than the terminal), clears the arcs.',
 'B': 'Under the RAM readout (bible 3.1), one line. Fits in p1 but collides with the stars row once the HUD grows (p2, p3).',
 'C': 'Round seal: emblem over CELL-9 and // BREAKER; same silhouette family as option C of SEND IT.'},
'sticker_material': {
 'cur': 'Shadow (5,9) vs cards (4,8), flat fills, border 12 px.',
 'A': 'Matte vinyl: gradient, thin top highlight, border 0.14 x size (max 12), ink 3, one shadow (4,8) blur 8 k .5.',
 'B': 'Printed vinyl: same spec plus halftone dot shading and paper grain.',
 'C': 'Lacquer: same spec plus specular band and a peeled corner.'},
'stickers_nowords': {
 'cur': 'Blank yellow and cyan plates, empty terminal.',
 'A': 'Verb = arrow through ring; UNDO = undo arc; CELL-9 = Breaker emblem + 9 tally strokes (5 + 4).',
 'B': 'Verb = arrow into a bar (the line is crossed); nameplate = round seal; UNDO glyph-led chip.',
 'C': 'Verb = Enter return arrow (the commit key); UNDO hangs below with keycap first.'},
'bottom_hint': {
 'cur': 'y 1070 under SEND IT, mono 16, mostly covered.',
 'A': 'Plain line under the stack, mono 18 TEXT_MID, block cursor; fully visible.',
 'B': 'Console strip the width of the sticker: a terminal plate holds the line, cyan cursor.',
 'C': 'Removed at rest; appears as a CRT tag over SEND IT on hover or focus (second row).'},
'card_targeting': {
 'cur': 'Not drawn.',
 'A': 'Valid = white hairline corner ticks; focus = lime corner brackets (2.10). Rings: ticks on tags, lime arcs on the focused ring.',
 'B': 'Valid = a small ring marker at each target centre; focus = lime brackets + a lime dot.',
 'C': 'Valid = dashed white outline on each target; focus = lime brackets.'},
'hover_tag': {
 'cur': 'Top-left corner, 500 px from the unit, Plex 18, 63-char lines, two colours.',
 'A': 'Bottom-left callout with a yellow leader to the cell; 4 lines <= 41 chars, Plex 20, one text colour (keywords Medium).',
 'B': 'Datasheet under the cell with a notch pointing at it: header band + 3 rows; covers the bottom bezel while hovering.',
 'C': 'Two columns (facts | cost) in the right gutter, leader from the cell end; farthest, least cover.'},
'hover_path': {
 'cur': 'Clean vector, large filled arrowhead.',
 'A': 'Continuous wax pencil 7 px with ink, open hand-drawn arrowhead, start dot.',
 'B': 'Stippled: tapped dots every 13 px, open arrow; the cell stays visible under it.',
 'C': 'Soft highlighter wax underlay + one sharp pencil line, hooked tip.'},
'hover_slice_highlight': {
 'cur': 'Yellow arcs added over red trim, HP ring and bars.',
 'A': 'Yellow rim arc in the trim slot; the hovered unit trim is removed (replace, not add).',
 'B': 'Pencil end ticks across the rim at both ends of each hit slice, no new arc.',
 'C': 'Wax wedge outline round each hit slice.'},
'hover_focus_dim': {
 'cur': 'Unit screens at 50 percent (overlays at 36).',
 'A': 'All non-hovered unit screens at the bible 38 percent.',
 'B': 'Ghost grade (like consumed units): 40 percent and desaturated.',
 'C': 'Spotlight: screens at 62 percent but the whole board outside the hovered cell and hit slices x0.6.'},
'hover_dim_overlay': {
 'cur': 'Marks at 36 percent, non-hovered landing arcs removed.',
 'A': 'Marks and landing arcs at one value, 38 percent; nothing removed.',
 'B': 'Marks and arcs desaturated to grey at 50 percent.',
 'C': 'Defocus: marks and arcs blurred 1.6 px at 45 percent.'},
'hovered_cell_outline': {
 'cur': 'Yellow dashed outline duplicating the pencil.',
 'A': 'Lime corner brackets (2.10).',
 'B': 'One solid plan-yellow outline 4 px with ink.',
 'C': 'White inner hairline + lime edge ticks.'},
'trigger_path': {
 'cur': 'Straight vector, typed X on the cell edge.',
 'A': 'Wax line from the Payload outer edge, hand-drawn X over the target.',
 'B': 'Line with open arrowhead, target scribbled out.',
 'C': 'Origin dot, line, target circled and crossed (reticle).'},
'twist_badge': {
 'cur': '34 px disc bigger than the tag, thin chevron.',
 'A': 'Pill the height of the tag, docked to its end; twist glyph + fat chevron.',
 'B': 'Solid yellow end cap fused to the tag, ink glyph + ink chevron.',
 'C': 'Pencil: the tag ringed + a clockwise arrow along the ring.'},
'refund_burst': {
 'cur': 'Gold burst on the dead cell edge covers the token.',
 'A': 'Token over the open stretch of the cell, REFUND tag (mono 18) under it, clear of the pencil X.',
 'B': 'Pip badge on the dead token shoulder, tag below the pair.',
 'C': 'Ticket: token + REFUND in one plate bridging the open stretch.'},
'refund_token': {
 'cur': 'Gold 12-point burst + cyan pip at four sizes.',
 'A': 'Cyan pip + plus; star burst in pale cyan at board size, halo at row and chip, pip only at strip.',
 'B': 'Pip + plus; pop ticks above (four at board size, three at row and chip).',
 'C': 'Pip + plus in a white ink ring with six ticks at board size, plain ring at row, pip at chip and strip.'},
'resolve_fire_lines': {
 'cur': 'Thin 2.4 dashed variant, ends in nothing.',
 'A': 'The decide-state tracer at 55 percent, with its result marks.',
 'B': 'Lines removed; one cyan pip per shot on each gun slice rim.',
 'C': 'Tapering streaks ending on the target token ring.'},
'no_target_tag': {
 'cur': 'Tracer reaches a unit (this state has no idle gun).',
 'A': 'Terminal tag across the slice rim, inside the slice, never over a cell.',
 'B': 'Dead-end stub with a bar cap and a barred circle: no word.',
 'C': 'Text hugging the slice rim, no plate.'},
}
