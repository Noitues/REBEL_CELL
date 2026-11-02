# Corp skin token sets (test B: colour + material + pattern)

A skin is one object (`cs_skin.Skin`): palette, material functions (cell, bezel, annulus, tape, rim, arcframe), vector pieces (token frame, landing-disc frame, ticket, crest, cell detail), and a hue shift for the schedule tape. Swapping the corp = swapping the object. Source: `src_snapshot/cs_skin.py`, installed by `cs_run.py`.

## Solace Biosystems (lab glass)
- Palette: primary lime #96FF46 (tape, glaze dots, strands #6ED646), glass #14462E, glass highlight #60D26E, bed #06120D, porcelain #E2EED8 / shade #96B096, deep strand #18624E.
- Secondary pink #FF4696: DEMOTED. It appears only as rose nuclei (#E27AA0, 4 px, about 34 percent alpha, one cell in five) under the glass. Never on a fill, edge, token, tape or rim. The only flat saturated pink on screen stays the player wheel. If tier II needs it, use the same rose nucleus, larger, still under glass.
- Material: leaf-green lab glass tint (40-46 percent) over the old slate cell (kind wash survives), gloss sheen top-left, tray bevel hairline in pale lime.
- Pattern: voronoi cell-membrane network (30 px pitch, 13 percent), nuclei, sparse bubbles with a specular dot (16-20 percent). Same family at 10-20 percent on the bezel, landing annulus, arc frames and tape.
- Token frame: porcelain glazed ring (mid value, ink groove against the lane ring so the depth ring still reads), lime glaze dot at 12 o'clock. Landing discs: smaller porcelain ring.
- Tape (THIS TURN, +N cells, HOLD cells): the SCHEDULE orange is hue-rotated +68 degrees to lime; glass bubbles and a gloss line on top.
- Rim: porcelain band r489-500 carrying a lime/teal double helix with rungs (71 turns, closes seamlessly) and six porcelain roundel crests on the sector spokes.
- Ticket: chamfered lab-slide glass, porcelain edge, small roundel crest.

## Meridian Freight (container yard)
- Palette: primary orange #FF8C1A (tape, rim, frames), oxide paint #964C1A, steel #463E38, bed #0E0B09, hazard black #140F0C, paint #ECD6B2. Secondary red #FF2E28 is NOT used (it is HARM): no red in the skin.
- Material: oxide-painted corrugated steel; radial ribs (6.5 px pitch, phased to each sector so they start at the cell edge), a few paint scuffs.
- Pattern: ribs only (trough 17 percent, ridge 7 percent), painted steel edge hairline, four rivets per cell, barcode strip on tickets. Stencilled container numbers: not drawn in this plate (the hook exists, `empty_marks`); empty cells are legible without it.
- Token frame: orange steel octagon with four corner castings, ink groove against the lane ring. Landing discs: smaller octagon.
- Tape: stays Meridian orange; ribs run along the tape so the chevrons cross them; a bright lip line.
- Rim: hazard stripes (orange/black, 45 degrees, 311 stripes, seamless) r489-500, same hazard lips on the bezel edges, six crane-A crest plates on the sector spokes.
- Ticket: square-cut shipping tag, orange edge, barcode, corner rivets.
- No yellow: yellow is BOSS_GOLD and the plan colour, so the hazard stripe is orange/black.
