DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id vis__rebel_cell; status ok; tokens in 6007 cache-write 69629 cache-read 0 out 3985; cost $0.113 -->

# Vision review: rebel_cell

All luma figures are estimates by eye on downscaled, UI-covered frames. Treat them as uncertain.

## Per frame

### OVERVIEW (H_overview_v3.png)

**What it shows:** Elevated 3/4 view of a Tokyo-canyon district with a lime walked path on the left, orange options, and a white dashed route to a red-circled TARGET at right. A vertical red MAINFRAME sign stands behind the target. Two lanes (roof row and street/tunnel row) are visible, with road and traffic streaks in the foreground.

**Rule breaks**
1. **Value band (12.1):** the frame looks bright and busy. I estimate the median around 0.18-0.22 (above the 0.17 warn edge) and under-0.10 pixels around 20-25 % (below the 25 % floor). Over-0.85 looks plausibly within 2.5 %, but the neon cores may push it. Uncertain; measure it.
2. **Landmark ratio (12.2) / 8.5:** the MAINFRAME sign reads as a bright red strip, but it competes with the cyan/magenta signage band at mid-frame and with the red fist at the far right. The fist is the identity landmark in the Art Bible 2.4 and it is clipped at the right edge. Ratio is unmeasurable by eye; the competition from adjacent neon makes it doubtful it holds 1.5x.
3. **8.8 / 8.5 mapping of MAINFRAME:** the sign sits on the roof behind the target, but the target room is a separate box in front of it. Per spec the sign "marks DISPATCH." Here the room and sign are not unified. The sign is cropped at the top by the dive of the camera (top of the sign is lost).
4. **9.1 hero signage:** route columns do not visibly carry blade or band signs in their district hue. The signage is the city's generic carpet. No clear hero sign is tied to a route column. The sign density (HIGH variance) is correct for Rebel Cell, but the density is not graded by `landmark.lead` / `dressing.signs` (13.1 rank 2, 8).
5. **13.1 `foreground.street` (rank 7):** the bottom ~25 % is road, rail and a tunnel mouth. Streaks and lamps are present, which is an improvement. But the large near-black band under the road is dead space (calm tiles are probably well over 32 %). The dark arch at bottom center is an unexplained shape.
6. **Occlusion (7.1):** the foreground rooftops with water tanks left of center sit close to the left-lane rooms. I cannot confirm a clean cut or ghost. Uncertain.
7. **UI over art (Art Bible 1.2):** the dossier card, ROUTE panel and SYNC STRIKE panel overlap city detail. They do not cover grease pencil in this frame. No break found.
8. **Palette (13.1 rank 5):** I see magenta, cyan, green and amber, so hue entropy is likely fine. The corp red is confined to the right edge, so the frame does not say "red corp" until the target.

**Readability:** The route is clear: lime path, orange option rings and white dash read well. The target circle plus "TARGET" text is findable, though the text sits under the sign and the label "CENTRAL SERVER // DISPATCH C..." is cut off at the right edge. The hovered branch does not apply. Competing elements: the mid-frame neon sign strip (HOTEL, KARAOKE), the cyan "ORBITAL" billboard top-center, and the bright red/pink fist at far right.

**Strengths to keep:** Strong depth layering (foreground road, mid canyon, tall back towers). Windows give a believable floor count. Route colors follow the 9.2 states. The lit shop-front base reads as street-level light. The wet road and streaks are convincing.

**Fix list**
- [art] Measure luma. If the median is above 0.19, lower the exposure or window `lit` share in the back rows. Keep route rooms unchanged.
- [art] Pull the camera or shift the frame so the MAINFRAME sign is fully in frame and the target label is not clipped; it is the landmark and should have its own rim.
- [art] Dim the signage band directly beside the sign (`landmark.lead`) so the red sign leads.
- [art] Remove or explain the dark arch bottom-center; shorten the dead road band.
- [spec] Define how the red fist (identity) and MAINFRAME (landmark) both appear in OVERVIEW without both being cropped.

### DECISION (H_decision_v3.png)

**What it shows:** The camera moves closer and the frame is held on the current options (BREAKER row and branches). The path and rooms are larger. The TARGET text appears at the right, with the circle and sign cut off by the frame.

**Rule breaks**
1. **9.5b off-screen TARGET marker:** the target is mostly off-screen to the right. I see the "TARGET" pencil word and a sliver of red circle at the edge, but no clear edge arrow with a chip. If under 50 % visible, an arrow is required. Not seen; uncertain at this crop.
2. **Value band (12.1):** brighter and more saturated than OVERVIEW. Estimated median 0.18-0.24; I suspect a warn or fail. Under-0.10 likely 15-25 %. Uncertain.
3. **6.4 camera:** Rebel Cell's spec says DECISION is the side view at yaw 0. This frame is still a clear 3/4 elevated view (the roofs show their tops). Not the spec's side view. Pitch looks well above the 17-19 deg range.
4. **Landmark ratio (12.2):** the MAINFRAME sign is out of frame in DECISION. That is acceptable for the camera, but the HQ identity is lost.
5. **9.1 signage:** the same as OVERVIEW. No visible hero sign per route column. At this zoom there should be a full-sign tier (5.2b tier 2); the signs are readable, but they are the generic city set.
6. **12.6 available rooms unblocked:** the option rooms (BREAKER right branch) are clear. The room at center-left is partly overlapped by a grey stair/roof element. Uncertain.

**Readability:** The route and options are very clear. Lime and orange rings read. The target is not findable without the arrow. The brightest items are the neon signs, not the rooms.

**Strengths to keep:** Rooms and interiors are legible at this scale. The rain on the street reads. Sticker-style node icons are consistent with the bible.

**Fix list**
- [art] Add the 9.5b edge arrow and chip for the target.
- [art] Check the median; drop the signage emission in the mid band by about 20 % if over 0.19.
- [spec] Reconcile 6.4 (DECISION as side view yaw 0) with the frames. Either the spec or the camera is wrong.
- [art] Reduce the grey stair/roof clutter that touches the option rooms.

### HOVER (H_hover_v3.png)

**What it shows:** The power cut is applied. The city is near-black, with the hovered FIGHT L3 branch lit and a white path to the kill-switch room. A red FIGHT // L3 info panel is at the bottom left, with a note strip.

**Rule breaks**
1. **9.4 power cut:** outside should be x 0.20 with 70 % desaturation and branch x 1.35. The outside city looks darker and nearly monochrome, which is consistent. But some window dots and signs (HOTEL, KARAOKE, magenta/green rooftops) still look fairly saturated and bright. The cut appears less than 70 % desat in places; uncertain. The branch itself does not look 1.35x brighter. The lit rooms are not strongly boosted.
2. **Branch scope (9.4 rule 1):** the whole branch to the TARGET should light. The path to the target is white and lit, but the downstream rooms (kill-switch at far right, target) are barely visible. The target is off-frame.
3. **Value band (12.1):** hover frames are exempt, so I report it only: the median is far under 0.14.
4. **UI over pencil (Art Bible 1.2):** the bottom note strip "BREAKER: straight on, SWITCH 1..." overlaps the bottom of the frame near the lane streaks. No pencil is covered. The panel is OK.
5. **Camera (6.4):** hover should move the camera 3 deg and dolly 0.96. The frame looks like DECISION, slightly shifted. Fine.
6. **Palette:** the red panel and the pink/cyan badge colors are correct. The panel red is used as a UI info panel while red is the corp hue and also HARM; the tint is acceptable here.

**Readability:** The hovered room is findable by the orange frame and cursor. The branch path is clear. The target is not visible, so "the whole branch to the target lights" cannot be read. What competes: the leftover neon bits in the mid-city.

**Strengths to keep:** The contrast between the lit branch and the dark city is dramatic. The route pencil stays clear. The hover info panel fits the paper-and-CRT language.

**Fix list**
- [art] Apply the 70 % desat to the emissive sign layer too (it looks excluded).
- [art] Raise the branch boost so the rooms read about 6x the rest.
- [art] Keep the target visible, or show the edge arrow, during hover.

## How the set holds together

- **Camera and scale:** OVERVIEW to DECISION is a plausible zoom on the same layout; the rooms scale consistently. Hover keeps the DECISION framing. The yaw is the same across all three, so there is no side-view change as spec 6.4 describes.
- **Palette:** the city palette is consistent (pink/cyan/amber). The UI matches the bible (lime, cyan CRT, paper card).
- **Corp identity:** the red MAINFRAME sign, the fist and the Tokyo canyon are all there, but the red appears only at the right edge, and the sign is cut in DECISION and absent in HOVER. Without the labels (DISPATCH, REBEL), the frames could read as a generic neon-city netrun. The corp is carried by text and the right edge, not by the dominant hue.
- **Scene continuity:** the same buildings and signs appear in all three. Good.

## Top findings

1. **MAJOR:** The corp's landmark (MAINFRAME sign) and fist are clipped, competing with neon, and absent from DECISION/HOVER, so Rebel Cell's identity and the 12.2 ratio fail.
2. **MAJOR:** The target is off-screen in DECISION and HOVER with no visible 9.5b edge arrow.
3. **MAJOR:** The DECISION camera does not match the spec's Rebel Cell side view (yaw 0, pitch 17-19), so either the spec or the camera is wrong.
4. **MAJOR:** The hover cut looks weaker than 9.4 (residual saturated signage; branch boost not 1.35x), and the downstream branch is hard to read.
5. **NIT:** The value band is probably high in OVERVIEW/DECISION (median over about 0.18, under-0.10 below 25 %), the hero signs on route columns are not distinguishable (9.1), and the foreground has dead dark space.

Q: Is the DECISION side view at yaw 0 (spec 6.4) still the intended Rebel Cell camera, or has the 3/4 view replaced it? (designer)
Q: Should the fist and MAINFRAME both be in frame at OVERVIEW? (art director)
Q: Does the 9.5b arrow apply inside the netrun when the target is partly clipped, as here? (designer)
