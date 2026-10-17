DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id vis__halcyon; status ok; tokens in 6001 cache-write 0 cache-read 69629 out 4121; cost $0.034 -->

# Vision review: halcyon

All luma figures are estimates by eye from downscaled frames (<= 1568 px). Treat them as uncertain until `HM/hq_values.py` runs on the real plates. The frames carry UI, so the value band, which is measured without UI, can only be judged roughly.

## Per frame

### OVERVIEW (H_overview_v2.png)

**What it shows:** A high 3/4 aerial of the stepped Halcyon pyramid in a dense, lit city. The walked lime route runs along the lowest tier. An orange option branch climbs the right side to a red-circled TARGET at the top, with a warm amber shaft rising from the apex.
The corp file card, ROUTE panel, HUD strip, DISPATCH ticker, THE EYE panel and legend are all drawn over it.

**Rule breaks:**
1. Value band (12.1, R-VAL-1/2): the frame looks bright and busy. My eyeball median is about 0.18-0.22, above the 0.19 fail line, and under-0.10 share looks near 15-25 %, below the 25-40 % band. Everywhere except the pyramid reads as lit, with almost no calm dark. Uncertain; measure it.
2. Density falloff (13.1 rule 3, R-CALM-1/2): the city carpet is even and window-dense right up to the compound, with no quiet apron and no dark blocks. Calm tiles look well under 12 %.
3. Landmark ratio (8.3, 12.2): the pyramid's cool cyan edge glow reads, but its body is roughly the same luma as the surrounding window field. It probably measures below 2x, and may fall below the 1.5 floor. Uncertain. The top-right and left tower fields compete.
4. Hero sign rule (9.1, `dressing.signs`): there is no readable hero sign on a route column. The only text sits in UI chips. Plinth lettering at the base is tiny and illegible.
5. Beam style (4.1, 12.5): the grey diagonal streak at upper right reads as a hard-edged rod, not a soft cone. The warm apex shaft is a narrow pillar and also reads rod-like. Uncertain at this size.
6. Camera (6.4): the pitch looks steeper than the 26 deg OVERVIEW pitch. Uncertain.
7. Hue spread (13.1 rule 5, R-HUE): the city is mostly warm window dots with scattered multi-hue neon dashes, and it reads as a confetti carpet rather than a violet-grey civic district (3.4). The corp hue is carried only by the pyramid.

**Readability:**
- Landmark: the pyramid reads at the center, but only through its edge glow.
- Route: the lime walked route is clear. The orange branch is clear. The TARGET circle plus label is the strongest read in the frame.
- Competing: the many saturated neon dashes (pink, cyan, yellow) in the city fabric, and the bright beam streak top right.
- Crowding: the ring badges along the bottom edge are small, and the "IN THE EYE" tag crowds a node at the right corner.

**Strengths to keep:**
- The tiered silhouette is unambiguous.
- Route state colors follow 9.2 (lime walked, orange option).
- The TARGET pencil circle and its label.
- The apex glow gives the eye a destination.

**Fix list:**
1. [art] Dim the window density and neon dashes within the apron to `near_k` 0.25 at the compound edge, and add `dark_block_share` 0.2 (13.1 rule 3).
2. [art] Re-solve exposure after the vignette (`values.solve`) and re-measure median, under-0.10 and over-0.85.
3. [art] Replace the rod-like beam streak with soft cones, per 4.1 rules 1-5.
4. [art] Raise the pyramid's key and cornice coves, and add rim light so the ratio is 1.5-2.0 (8.3).
5. [art] Add one legible hero sign (blade or wall, 9.1) on a lower-tier route column.
6. [spec] Q: confirm the OVERVIEW pitch against the spec's 26 deg.

### DECISION (H_decision_E_v2.png)

**What it shows:** A near-front view up the pyramid face. The current route row sits at the bottom with lit room cutaways, and the node stickers sit on them. The orange climb line runs straight up to the top room and the TARGET circle.
The city beyond is dark, with big pastel rectangles and neon strips on both sides.

**Rule breaks:**
1. Occlusion/foreground (7.1): the left and right foreground carries bright vertical neon bars and large pastel blocks that are very close in luma to the active room. They sit near the decision set and are not cut to stubs or ghosted. Uncertain how much is geometry versus signage.
2. Hue (13.1 rule 5, 3.4): the pastel pink, green and cyan rectangles read as candy, off the violet-grey civic language. They look like holo-billboard planes with no sign content.
3. Value band (12.1): the pyramid face is bright cool grey with big flat lit tier tops. My eyeball median is about 0.16-0.20 and the dark city beyond is crushed, so the distribution is bimodal. Uncertain.
4. Room readability (12.6): the rooms in the row look about 70-90 px tall at this scale, which is fine. The two option rooms on the right are red-tinted "IN THE EYE" and read as locked, but their glyphs are weak at this size.
5. Camera (6.4): the framing is front-on and centered on the current room, which is correct. The vertical climb line is a clean straight run, but the "CLIMB 1/2" chip sits partly on a dashed white path and is clipped at the right edge. Uncertain.
6. Hero sign (9.1): no hero sign on a route column again, only the TARGET chip.

**Readability:**
- Landmark: the pyramid is unmistakable.
- Route: the current row, option 1 (red, "IN THE EYE") and option 2 (orange, top) are all findable, and the climb line is the clearest element.
- Competing: the neon bars at the left and right edges draw the eye away. The pale tier tops are the biggest bright areas on screen.
- UI: the left file card overlaps a bright billboard cluster, and the legend is dense.

**Strengths to keep:**
- Front-and-centre framing on the active room.
- Keyed outlines on the room cutaways.
- The straight orange climb that reads instantly.
- Option 1 and 2 numbered clearly.

**Fix list:**
1. [art] Run the occlusion rule on the foreground billboards and neon bars (stub plus ghost 18 %), or dim them.
2. [art] Pull the pastel planes toward violet-grey and add sign content, or remove them.
3. [art] Lower the tier-top albedo or key so the pyramid is not the biggest bright mass, while keeping 1.5-2x on the rooms.
4. [art] Move the CLIMB chip off the dashed path.
5. [spec] Q: confirm the locked "IN THE EYE" tint stays legible at 1280 x 720 (12.6).

### HOVER (H_hover_E_v2.png)

**What it shows:** The DECISION camera, shifted slightly higher, with the top room (option 2) hovered. A tooltip tag reads "FIGHT L6" and the node file panel sits at bottom left. The orange branch is bright, the lower route is lime, and the city is much darker than in DECISION.

**Rule breaks:**
1. Power cut (9.4): the surrounding city looks darkened to roughly x 0.2, which matches the preset. But the pyramid body itself is not dimmed uniformly. The big pale tier top at the right and center stays bright, so the cut reads as partial. Uncertain.
2. Branch boost (9.4): the hovered room and its climb line are brighter, but the branch glow and type glow are subtle. The room window reads, but the line is only a thin orange stroke.
3. Value band: hover frames are exempt from the band (12.1), so this is for information only.
4. Beam/halo: a yellow-gold ring at the top edge appears to be a glow from the apex and competes with the TARGET circle. Uncertain.
5. Occlusion (7.1): there are still bright vertical bars and planes at the left and right near the pyramid.
6. UI/pencil (9.2): the NODE FILE panel at bottom left overlaps the route lime line and sits near the edge. Check that no UI covers the pencil.

**Readability:**
- The hovered branch is findable: the top room plus the climb to it, with "FIGHT L6" attached.
- The competing items are the gold ring and the bright tier tops.
- The TARGET is findable. The red circle is partly hidden behind the apex glow.

**Strengths to keep:**
- The tooltip tag with a type and layer.
- The darkened city, which gives strong separation.
- The cursor sitting on the hovered room.
- The bottom row keeps its lime state.

**Fix list:**
1. [art] Apply the grade mask to the pyramid tiers outside the branch (the branch mask is the room polygons grown 8 px, per 9.4).
2. [art] Thicken the branch stroke or raise `branch_boost` toward 1.35.
3. [art] Drop the apex ring glow while hovering, or move it off the TARGET circle.
4. [art] Check that the node file panel does not overlap the pencil.
5. [spec] Q: confirm the target brightness for the off-branch pyramid body.

## How the set holds together

- **Continuity:** the three frames share one pyramid, the same route colors, and the same HUD and THE EYE panel. The camera steps from the high aerial to the near-front view and shifts slightly for the hover. The route UI is stable.
- **Palette:** the pyramid is consistently cyan-white, the lime/orange pencil is consistent, and the red "IN THE EYE" tint is consistent. The city is the weak link. It changes from warm window carpet in OVERVIEW to dark with pastel planes in DECISION and HOVER, so the world seems to shift between frames.
- **Scale:** the tier proportions and room size are plausible. The row of rooms on the lowest tier is large, and the upper tier rooms are small.
- **Corp identity:** the stepped tiers, the eye panel, the "EYE" label and the violet file card point to Halcyon. But the pyramid itself is cyan, not violet, and the city is not violet-grey. A frame crop of the building alone could be mistaken for Orbital or a generic tower. Identity rests on the UI and not the 3D. The eye turret and the amber rim (8.5) are not clearly visible. Uncertain.

## Top findings

1. **MAJOR:** The city fabric does not follow density falloff or district hue. It is an even, confetti-colored window carpet in OVERVIEW and pastel planes in DECISION and HOVER (13.1 rules 3 and 5, R-CALM, R-HUE).
2. **MAJOR:** The landmark ratio is probably below 1.5-2.0x in OVERVIEW and the pyramid competes with bright tier tops in DECISION (8.3, 12.2). Uncertain, since there is no object-index pass here.
3. **MAJOR:** Foreground neon bars and billboards sit near the decision set unoccluded (7.1) in DECISION and HOVER.
4. **MAJOR:** The hover power cut is partial. The pyramid body outside the branch stays bright (9.4).
5. **NIT:** There is no legible hero sign on any route column (9.1). The beam and apex shaft read rod-like (4.1, 12.5), and the Halcyon eye turret and amber rim are not visible (8.5).

Q: Is the cyan-white pyramid body intended, or should the Halcyon violet read on the landmark? ART_BIBLE 2.4 lists violet primary and amber secondary.
Q: Should the OVERVIEW pitch be 26 deg per 6.4, or is the steeper aerial approved?
