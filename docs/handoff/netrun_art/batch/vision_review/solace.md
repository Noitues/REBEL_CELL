DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id vis__solace; status ok; tokens in 5987 cache-write 9454 cache-read 60175 out 3345; cost $0.041 -->

# Vision review: solace

All luma figures are estimates by eye on downscaled, compressed frames. They are not measurements. Confidence is "uncertain" wherever I say so.

## Per frame

### OVERVIEW (H_overview_v4.png)

**What it shows:** A high-angle aerial of a dense, lit night city. A Solace double helix (two tubes with rung bridges) rises from a lit plinth at lower center to the CENTRAL SERVER // THE GENOME CORE node at the top, with a red TARGET circle and pencil word. The route is drawn in lime, orange and white. Numbered options 1 and 2 are visible near the lower third.

**Rule breaks**
1. Value band (12.1, R-VAL-1/2): the frame reads bright and busy, with warm window dots almost everywhere. By eye the median looks above 0.17 and the under-0.10 share looks below 25 %, though the dark inter-block gaps may offset this. Uncertain; measure it.
2. Landmark ratio (12.2, 8.3, R-FOCUS-1): the helix is pale grey-silver with a faint green rim, and it is darker and lower in contrast than the surrounding lit towers. By eye it does not read 1.5-2x its ring. It leads by shape and by its route overlay, not by light.
3. Calm and rest areas (13.1 rule 3, R-CALM-1/2): the carpet of windows is even across the whole frame, with no quiet apron around the compound and no dark-block patches. This is the "even carpet" gap.
4. Palette (13.1 rule 5, R-HUE-1): the city is warm amber-orange with scattered magenta and cyan dots. Solace's leaf green #96FF46 appears only as a thin rim on the helix and green accents on the plinth. A Solace territory hue is hard to find.
5. Signage (9.1, 13.1 rule 2): small colored bars (magenta, cyan, yellow) are scattered at random. I cannot identify a hero sign or a blade sign on any route column. This is uncertain at this size.
6. Foreground street (13.1 rule 7): the lower 20-25 % is cut-roof grid with no clearly readable road, streak lanes or kerb lamps. The street-level light rule is not visible here.
7. Corp identity (8.5): the tubes look like segmented grey rings with a few skybridges, not smooth leaf-green glass with rows of oval portholes. Uncertain at this scale.
8. Overlay (9.2): the lime walked path and the orange options render over a busy field. Some link segments are thin near the plinth and compete with window dots.

**Readability:** The target is the clearest element, thanks to the red ring, TARGET word and label. The helix silhouette is findable because it is vertical against a flat grid. The route near options 1 and 2 is readable. What competes: the dense window field, and many small colored sign bars that have the same size and brightness as node rings.

**Strengths to keep:** The helix silhouette and its vertical lead to the target; the red TARGET marking; the legible HUD and legend; the plinth with its lit green marks; a dense, continuous city to the lot edge (8.2).

**Fix list**
1. [art] Lower window density and lit share in a ring around the compound (`density.falloff`: `near_k` 0.25, `dark_block_share` 0.2).
2. [art] Raise the helix rim and cove light to reach the 1.5-2x ring ratio, using light and not exposure (8.3).
3. [art] Pull the city palette toward the Solace district hue near the compound (`palette.districts`, 4 % minimum green).
4. [art] Add visible street light and a kerb lamp chain in the foreground (`foreground.street`).
5. [spec] Report the measured luma of this plate in `checks_<run>.json`; do not rely on this estimate.

### DECISION (H_decision_v4.png)

**What it shows:** A close view of the tube with oval cutaway floors, two route nodes (1 = shop, 2 = fight), skybridges across, and a lime walked line with orange option lines. The tube is dark and glossy with white ring bands.

**Rule breaks**
1. HQ camera (6.4): the current room is not "front and centre". The walked room sits lower-left and the two options span left to far right, so the decision set is not centered in the usable area. Uncertain, but it reads off-center.
2. Occlusion (7.1): the right tube and the bridges cross the frame near option 1. The tube edge appears to clip the upper right and the ghost or stub treatment is not clearly visible. Uncertain.
3. Value band (12.1): the tubes and city are mostly dark with bright lit windows. By eye the under-0.10 share may exceed 40 % on the tube area. Uncertain.
4. Hover and available-room clearance (12.6): option 1's opening overlaps the bridge and the pencil. Whether <= 8 % is blocked is not verifiable here.
5. Clutter (13.1 rule 2): colored rectangles (cyan, magenta, yellow) float over the city and do not sit on building faces. This breaks "every sign on a building face". Uncertain.
6. Identity (8.5): the portholes read as wide ellipses on a dark tube. The leaf-green fresnel rim (`rim_k` 0.9) is faintly visible, but the tube body is nearly black.

**Readability:** The routes are readable, the node icons and numbers are clear, and the tube with its interiors is easy to find. What competes: the bright city behind the dark tubes, and the neon sign bars.

**Strengths to keep:** The cutaway floors with lit offices and green accents; the clear numbered keys and the UP / ACROSS tags; the white and lime pencil states; the compositional diagonal of the bridge.

**Fix list**
1. [art] Re-center the camera shift so the current room and both options sit at the middle of the usable area (6.4 `centre_current`).
2. [art] Raise the tube's rim and cove light so the body separates from the city.
3. [art] Anchor floating sign bars to facades or remove them.
4. [spec] State how the occluders are expected to look (stub height, ghost 18 %) in a DECISION frame, so reviewers can check them.

### HOVER (H_hover_v4.png)

**What it shows:** The same camera as DECISION with the city dropped to near black. The hovered node (shop L3) shows a white link branch, a pencil highlight, and a green file card at lower left with a caption line.

**Rule breaks**
1. Power cut (9.4): outside the branch the city is near black, which is consistent with x 0.20 and 70 % desaturation. But the unhovered tube floors, the lime walked path and the orange option also appear dimmed, while the spec says the current room and branch light up. The "branch x 1.35" brightening is not obvious. Uncertain.
2. Pencil states (9.2): the hovered branch is drawn white and a second, orange branch is drawn over the right bridge. Two "lit" colors compete, and the white line crosses the frame edge. The branch is not clearly the only bright element.
3. Caption (UI): the bottom caption text runs past the card width into the legend area. This is a UI clip.
4. Hover frames are exempt from the value band (12.1), so the dark median is allowed.

**Readability:** The hovered shop node and its file card read well. The cut makes the route lines stand out sharply. What competes: the extra white curve on the right tube and the orange link, both at similar brightness.

**Strengths to keep:** The strong dark contrast that makes the route pop; the file card legibility; the tag labels (SHOP L3, ACROSS, UP); the type-colored node rings.

**Fix list**
1. [art] Use one branch color, with the rest of the pencil dimmed to the power-cut level.
2. [art] Brighten only the branch rooms (x 1.35) and keep the current room visible.
3. [art] Truncate or wrap the caption inside the card.
4. [spec] Define which pencil states stay at full strength during a hover.

## How the set holds together

**Continuity:** The HUD, the legend, the left dossier card and the node icons are consistent across all three frames. DECISION to HOVER keeps the same camera, which is correct. OVERVIEW to DECISION is a plausible zoom on the same helix, though the exact pose match is not checkable. The palette shifts from warm amber and magenta in OVERVIEW and DECISION to near black in HOVER, which is the designed cut.

**Corp identity:** The helix is the clearest Solace signal. Without it, the frames could be mistaken for any lit city, since the green identity color (8.5, art bible 2.4) is weak. The territory around the HQ carries no Solace material, such as pale green-grey facades or capsule bays, so a different corp's tower dropped in would read nearly the same.

## Top findings

1. BLOCKER: Solace's color identity is missing from the city around the compound; the territory reads as generic warm amber (`palette.districts`, 8.5).
2. MAJOR: The landmark does not clearly out-light its background in OVERVIEW; the 1.5-2x ratio is doubtful (12.2, 8.3).
3. MAJOR: The window field is an even carpet with no calm apron around the compound (`density.falloff`, R-CALM).
4. MAJOR: DECISION is not centered on the current room and its options (6.4), and its floating sign bars are not anchored to facades (13.1 rule 2).
5. NIT: HOVER shows two competing bright branches and the caption overflows its card (9.4, 9.2).

**Q:** Should the Solace city hue near the HQ follow `variance_pref` MEDIUM plus a green tint, or keep the amber district glow?
**Q:** Is the near-black tube body intended, or should the leaf-green glass read lit in DECISION?
