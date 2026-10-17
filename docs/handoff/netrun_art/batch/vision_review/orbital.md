DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id vis__orbital; status ok; tokens in 5992 cache-write 9454 cache-read 60175 out 5457; cost $0.051 -->

# Vision review: orbital

All luma figures are estimates by eye on downscaled frames (about 1568 px wide). Nothing here was measured. Where the image is too small or compressed to judge, I say "uncertain".

## Per frame

### OVERVIEW (H_overview_v2.png)

**What it shows:** High oblique view down on the round launch podium. The rocket sits in the silo at center, with the dish stations on a ring, the red-lit antenna tower at lower left and a pink dome at lower right. A lime route loop circles the ring, an orange "next" link runs to the central server, and a red TARGET circle sits at the rocket.

**Rule breaks**
1. Value band (12.1, R-VAL-1/2): the city fabric is very dark, with lit windows as scattered dots. By eye the median looks well under 0.14 and the share under 0.10 looks above 40 %, because the black podium and the dark corners dominate. Uncertain, but likely fail or warn on R-VAL-2 (crushed). The dark-city look is not the issue; the podium floor and the frame corners carry it.
2. Calm tiles / hue (13.1 ranks 3 and 5, R-CALM-2, R-HUE-2): the surrounding city is an even carpet of warm yellow-white window dots, with colored neon streaks mostly in the corners. There is no apparent quiet apron. The warm yellow dominates, which suggests a top hue cluster above 45 % (uncertain). Orbital's ice-white and steel-blue (Art Bible 2.4, spec 3.4 blue-grey) barely shows in the fabric.
3. Landmark lead (8.3, 12.2, R-FOCUS-1): the rocket and podium read clearly through the light rim, the white podium rings and the lit rocket. The ratio looks plausibly above 1.5. But the warm window carpet right behind the rocket's top competes with its silhouette, and the red tower and the pink dome pull the eye away.
4. Route overlay vs landmark (9.2, Art Bible 1.2): the lime wax loop is very thick and runs over the podium rim and the dish stations. At lower left it doubles back on itself and tangles over the antenna base and the two elite rooms, which hides the geometry. The orange link and the red TARGET circle also cross the rocket body, so the rocket is partly covered.
5. Room readability (12.6, `room_px_target` 46 px): the route rooms are tiny rings on the platform edges and read as map markers, not as rooms with an opening. The antenna deck rooms are only just legible (uncertain).
6. HQ OVERVIEW camera (6.4, Orbital: pitch 46, lens 36, yaw NNW): the pitch looks steep, roughly 45-50, which matches. The framing is cut off at the right and lower-right edges, so the ring and the lime loop run close to the frame boundary.
7. Signage (9.1, `dressing.signs`): no legible hero signs or hero sign bands show on the surrounding buildings. Only the corp-neutral neon streaks and billboards appear, so a rule 2 failure (R-DET-2 uncertain).
8. Label collisions: the "LOCKED RETARGET 1/3" pencil text runs over the antenna base and the lime link. The "CENTRAL SERVER // LAUNCH CONTROL" tag sits right beside the red TARGET and the order of precedence is hard to read.

**Readability**
- Landmark: found in under a second (rocket, bright rings).
- Route: the lime loop is clear as a circuit. Which segment is "walked" versus "next" is clear only by color (lime vs orange), and the crossing at lower left is confusing.
- Target: found easily (red circle and word).
- Hovered branch: none in this frame.
- Competing: the red antenna tower's beacons, the pink dome, the neon streaks at the edges.

**Strengths to keep**
- The round podium with concentric rings and the hazard chevrons says "launch site".
- The rocket's rim light and warm white read well.
- The city has the right nocturnal depth, and the dish stations give the ring rhythm.
- The pencil/sticker language is consistent with the Art Bible: yellow-green plan line, red threat.

**Fix list**
1. [art] Reroute or thin the lime line at the antenna (lower left) so it does not double back over the elite rooms.
2. [art] Lift the podium floor by about 0.03-0.05 median luma (floods and uplights, not exposure, 8.3) to move the frame toward the 0.11-0.17 pass band.
3. [art] Apply the `density.falloff` apron: dim lit windows near the compound and add dark blocks, so the window carpet stops competing with the rocket.
4. [art] Push the fabric hue toward Orbital's ice blue and white (3.4), reserving warm yellow for sodium lamps, and keep the pink dome as a minor accent.
5. [art] Move the TARGET word so it does not overlap the tower beacon and keep it off the rocket body.
6. [spec] Q: is the pink dome an intended Orbital element? It is not in the 8.5 landmark list (podium, silo, rocket, dish ring, truss tower).

### DECISION (H_decision_v2.png)

**What it shows:** A closer view up the antenna truss tower. The current room (ANTENNA ELITE) is a lit box with a sword sticker, and the lower room on the lime route is below it. A red pencil line runs up to the TARGET circle on the central server. Dishes flank the ring left and right, and the city rises behind.

**Rule breaks**
1. Room readability / available rooms unblocked (12.6): the red TARGET line runs straight through the ANTENNA ELITE room, from the "LAUNCH OVERRIDE" sticker to the TARGET circle, and the pencil text "LAUNCH OVERRIDE" is partly covered by the sticker ring. This breaks the rule that the opening is at most 8 % blocked (the room's left part).
2. Value band (12.1): this frame looks brighter and closer to the band than the OVERVIEW. The median looks plausible near 0.12-0.16. The lower-right and bottom-left corners are black and look crushed (uncertain). The black rectangle at bottom center looks like a clipped or unrendered patch (uncertain; it may be a mask).
3. Hover/landmark ratio (12.2): the tower reads clearly through its lit floors, but the dishes and the ring carry a strong pink/white rim that competes with the tower as it is cropped.
4. Overlay conflicts (9.2, `CLEAR_PAD`): the dashed white link goes to the upper right through the "CENTRAL SERVER // LAUNCH CONTROL" tag and ends in the tag's border. The TARGET tag text is clipped on the right ("LAUNCH CONTRO").
5. Camera (6.4, `dmin` 110 kit units, pitch 16-26): the view is looking up the tower with a rather low-angle pitch. The tower is cut off at the top by the frame, so the truss decks with their two vault rings are partly outside the usable area. The "front and centre" rule centers the current room, and this seems met roughly.
6. Signage (9.1): the nearby buildings show no hero signs or readable sign tiers (5.2b tier 2 would apply at this distance). The windows and neon bars are present, but no text signs are visible (uncertain at this size).
7. Palette (Art Bible 2.4, spec 3.4): the neon bars in pink, green, yellow and cyan at the edges make a rainbow fabric that reads as a generic cyberpunk city, not Orbital's cool ice-white and blue.

**Readability**
- Landmark: the tower reads as the HQ at this scale. The rocket is not visible, which weakens the "Orbital" read (see the set section).
- Route: the lime path enters from the bottom, passes the lower room and reaches the current room. The orange path at the right edge is clear but runs off-frame.
- Target: clear (red circle, word, tag).
- Hovered branch: none.
- Competing: the saturated neon bars on the buildings at left and right; the pink dish rims.

**Strengths to keep**
- The room boxes with a lime frame and the stickers read well; the sword sticker is crisp.
- The glossy, wet, dark deck gives good depth.
- The truss structure and the lit vault rings give the tower an identity.
- The camera is close enough that floors and rooms are separate, and the occlusion cut has plausibly worked (no big building in front of the rooms; uncertain).

**Fix list**
1. [art] Reroute the red TARGET pencil to the room's edge so it does not cross the ANTENNA ELITE opening, or end it at the room border.
2. [art] Move the "LAUNCH OVERRIDE" word clear of the sticker ring.
3. [art] Check the black rectangle at bottom center (likely an unlit slab); if geometry, add a floor rim or fill.
4. [art] Pull the neon bar hues toward Orbital's palette and cut saturation on the nearest ones.
5. [art] Add one visible rocket or silo cue (the rocket's tip or the silo ring) in the upper frame, or move the camera a bit back.
6. [spec] Q: does the DECISION frame need the full ring in view, or is the tower-only view acceptable for Orbital's identity?

### HOVER (H_hover_v2.png)

**What it shows:** The same view as DECISION, but the whole city is nearly black. The hovered room (LAUNCH CONTROL) has its file panel at lower left, a red pencil line from the current room (ANTENNA ELITE) up to the TARGET circle, and a sword sticker on the current room.

**Rule breaks**
1. Hover power cut (9.4): the cut looks much harsher than the specified x 0.20, 70 % desaturation, branch x 1.35. The city, the tower, the dishes and the ring are almost black and the whole frame is dominated by near-black. The decision frame's neon bars and window dots are nearly gone. The effect looks like x 0.05-0.10 (uncertain), so the "tunable toward x 0.35" ceiling is not even near. The ratio of the branch to the rest looks much greater than the specified 6x.
2. Value band (12.1): hover frames are exempt but reported. By eye, the median is far under 0.09 and the share under 0.10 is above 80 %. It is exempt, and I note it only as the cause of finding 1.
3. Branch light (9.4 rule 1): only the current room and a wide lime frame are lit. The TARGET circle and the hovered Launch Control room are lit, but the branch geometry between them (the tower core) is not lifted, so "the whole branch to the TARGET lights" is only met by the pencil line, not by the rooms.
4. Overlay (9.2): the red line crosses the current room and the "LAUNCH OVERRIDE" pencil word again. The cursor sits on the TARGET and the "LAUNCH CONTROL" tooltip tag collides with the red circle and the larger tag beside it.
5. Text overflow (Art Bible 2.9 floors): the bottom warning bar ("LAUNCH OVERRIDE: fire the rocket one round early...") runs past its red frame at right, and "The run ends" is cut or loose (uncertain; the text may be clipped by the legend).
6. File panel: the Launch Control panel's stamp at its lower right (a green rectangle with text) overlaps its radar graphic and looks smeared (uncertain, too small).

**Readability**
- Landmark: the tower's silhouette is nearly lost; only the ring and outlines are visible.
- Route: the lime path and the orange path are strongly legible. This is the cut working in favor of the route.
- Target: clear.
- Hovered branch: clear as the brightest region.
- Competing: the lit current room is bright at about the same level as the TARGET, so the branch to the hovered node does not dominate the current room.

**Strengths to keep**
- The hover reads instantly; the route and the file panel stand out.
- The pencil colors keep their meaning (red for threat, lime for walked).
- The tooltip panel's content is clear (tier, type, reward, HP).

**Fix list**
1. [art] Raise the cut level to x 0.20 and keep 70 % desaturation. Verify the grade in the 2D pass is not applied twice (once in the 3D lights and once in the 2D grade). Dropping the HQ's old 3D cut (9.4 rule 3) may not have been done.
2. [art] Lift the tower structure on the branch (the part between the current room and the TARGET) by the branch boost x 1.35.
3. [art] Separate the cursor, the "LAUNCH CONTROL" tooltip and the TARGET circle so they do not stack.
4. [art] Fit the bottom warning text inside its frame or wrap it to two lines.
5. [spec] Q: which of the 3D and 2D power cuts is applied in this render? If both, the build session removes the 3D one.

## How the set holds together

- **Camera:** the OVERVIEW is a high oblique over the whole podium; the DECISION is a close view up the tower. The jump is large and the tower is a different object from the rocket that leads the OVERVIEW. DECISION and HOVER share the same camera, as the rules intend (hover does not move the camera, 6.2). The pitch in DECISION looks fairly low versus the 16-26 range; the view is plausible.
- **Scale:** the room sizes change by a large factor between OVERVIEW and DECISION. That is expected, but the OVERVIEW rooms are marginal.
- **Palette:** the lime/orange/red pencil palette holds across the three frames. The fabric palette goes from warm yellow dots (OVERVIEW) to a rainbow of neon bars (DECISION) to near-black (HOVER), so the corp color does not carry.
- **UI:** the frame chrome is identical across the three frames (heat strip, dossier card, route panel, legend, view toggle); the retarget panel changes state correctly (circuit 2 to circuit 4). Good continuity.
- **Corp identity:** Orbital is identifiable only in the OVERVIEW (rocket, silo, dish ring, truss tower with beacons). In DECISION and HOVER the tower plus the dishes on the ring could be taken for another corp's compound, and the neon fabric reads as a generic city; the Art Bible's squint test (ice white / pale grey) fails because the frames read as warm yellow and pink. Uncertain whether the dim ice-white rim light is meant to carry it.

## Top findings

1. **MAJOR** - HOVER power cut is far harsher than the specified x 0.20 / 70 % grade (9.4); the tower and city are almost black, and the 3D cut may still be applied.
2. **MAJOR** - Overlay collisions: the red TARGET line crosses the current room and its "LAUNCH OVERRIDE" word in DECISION and HOVER, and the lime loop tangles over the antenna base in OVERVIEW (9.2, 12.6).
3. **MAJOR** - Orbital's palette does not carry the fabric: warm window carpet and rainbow neon replace ice white / steel blue (Art Bible 2.4, spec 3.4, R-HUE-2, `density.falloff`).
4. **MAJOR** - OVERVIEW is likely under the value band (estimated median under 0.11, over 40 % under 0.10; uncertain) with dark floor and corners (12.1).
5. **NIT** - Label and text clipping: the TARGET tag in DECISION, the bottom warning bar in HOVER, and tooltip stacking at the cursor; the unexplained pink dome and black rectangle need confirming.

Q: Is the pink dome in OVERVIEW an Orbital element (8.5)?
Q: Is the black rectangle at the bottom of DECISION an unlit slab or a mask?
Q: Which power cut (3D, 2D, or both) did this HOVER render apply?
