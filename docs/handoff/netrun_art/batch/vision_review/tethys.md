DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id vis__tethys; status ok; tokens in 4194 cache-write 0 cache-read 69629 out 4405; cost $0.033 -->

# Vision review: tethys

Scope: two frames supplied (OVERVIEW `H_overview_v2.png`, and a closeup `tethys_closeup_v2.png` that is not a DECISION or HOVER final). No DECISION or HOVER frame exists, so those are not reviewed. All value numbers are by eye, from downscaled images, and are uncertain.

## Per frame

### OVERVIEW (`H_overview_v2.png`)

**What it shows:** High oblique view over a drowned city. A domed, spired tower with ringed satellite domes stands on a hexagonal platform, with a long dam wall in the foreground. A lime/orange route runs from the DOCK LOCK ring at the dam up the tower, with a dashed white section "under the water", ending at a red TARGET circle labelled CENTRAL SERVER // THE BLACK SMOKER.

**Rule breaks**
1. Value band (12.1, R-VAL-1/2/3): by eye, the upper half is a dark teal field, which suggests a median near or below 0.11 and well over 40 % of pixels under 0.10. The lit dam wall is the only bright mass. Likely a warn or fail on R-VAL-1/2; uncertain until measured. No obvious >2.5 % over 0.85 except possibly the tower cyan ring and wall highlights.
2. Landmark ratio (12.2, R-FOCUS-1): the tower is pale grey-cream against a blue-teal ring and is not clearly brighter than its surroundings. The warm lit dam wall in the foreground out-shines it (landmark.lead, 13.1 rank 8: "the top-1 % light never in a cell without a landmark"). Estimated ratio around 1.2-1.5; likely below 1.5. Uncertain.
3. Landmark footprint (8.6, 8.6b): the tower rises from a hex platform in the middle of the frame. I cannot verify a "fills its lot" fit or the canonical full-city silhouette from these images alone. [spec: needs the full-city landmark frame for the IoU >= 0.85 check, 8.6b rule 3].
4. Hue cluster (palette.districts, R-HUE-2): the frame is almost all one teal hue. Accents (green rings bottom-left, magenta/orange lines, amber wall lamps) are small. Top hue cluster is probably above 45 %. Tethys is "hull / wet hull", and that is a corp-view exemption only in the corp-HQ sense. R-HUE is exempted for corp HQ views, so this is a NIT under the spec but a legibility issue.
5. Foreground street (foreground.street, 13.1 rank 7): the bottom 20-25 % is the dam wall and a dark apron with cyan/red/green street lines. It reads as a set piece, not as a street with a wet surface. The DOCK LOCK start ring sits on the dam crest, over a dark building. The route's first leg passes over the wall and over a gate. Mostly legitimate for Tethys, but it eats the frame.
6. Grease pencil (Art Bible 1.2, 2.2): the route lines are thin, with no visible wax sheen, rough edge or dark under-shadow, so they read as clean vector strokes. The walked leg is lime (correct, CELL_TURF) but the thin line is lost over the lit wall and dark water. The "ahead" dashed white is correct per 9.2, though it is drawn on top of a bright tower face and gets lost. Judge at this size as uncertain.
7. Plan vs pencil colors (9.2): the orange segment just above the lime one reads as the "option" color. Fine, but it is only a few px long and doesn't read as a branch. No visible options fan or numbers, so the DECISION-grade readability can't be judged here.
8. Sticker and node language (9.3): nodes are small white dots in black rings on the satellite domes. There are no vinyl stickers, no shapes by node type, no kind colors (ROOM_TL). All nodes look identical, so type does not read by shape. As a "candidate rooms" test frame that may be intended, but it fails 9.3 rule 1 as a final.
9. Label chrome: the bottom-left caption "TEST // ATLANTIS STATION overview..." is test text in the frame. It is a Share Tech Mono strip, small and low contrast, and it must not ship. The red label "CENTRAL SERVER // THE BLACK SMOKER" is a red box with small text. It is legible but tiny, and the "TARGET" word is in a marker face (appropriate). Under 12.6, 1280x720 readability, the label is likely below the 24 px floor. Uncertain.
10. Name check (spec header): "THE BLACK SMOKER" is the working name and is used correctly. The caption says "ATLANTIS STATION", which is not in the supplied names. [spec] Q below.
11. Hero signage (9.1, dressing.signs): no readable hero sign on any route column is visible, and tower faces show none. Sign count at OVERVIEW is apparently near 0 text signs; the rule wants 6 legible. Underwater, this may be a deliberate Tethys choice, but the spec does not grant it.
12. Beam/fog (4.1, atmosphere.layers): there is a faint blue-white plume at the spire tip, and soft god-ray hints on the left. No clear beams in fog. Water caustic texture on the "ground" is good. The beam count and style cannot be judged. Uncertain.

**Readability:** Landmark: findable by shape and position (center, tallest, pale), but only moderately so; the wall competes in brightness and contrast. Route: the lime start and the white dashed climb are traceable, but the line thins over the tower and the dashed part crosses clutter. Target: the red circle and label are findable but small, sitting at the tower base left of the route, not on the dominant axis. Hovered branch: not applicable. Competing: the warm lit dam wall, the green neon rings bottom-left, and the many cyan lit window dots across the whole field (a carpet pattern: R-CALM likely low-variation in the upper half).

**Strengths to keep**
- A clear, unmistakable silhouette: stacked dome, ring of satellite domes, a spire with a ring. It reads as Tethys and as nobody else's HQ.
- The drowned city under caustic water, with fish and sharks, is atmospheric and specific to "wet hull".
- The dam wall with warm lamps gives a strong foreground depth plane and a clear entry point.
- The route is geographically legible from the dock to the center.

**Fix list**
1. [art] Raise the tower's key and rim light so it clearly leads the wall (aim for the 1.5-2.0x band in 12.2); lower the wall's lamp-wash by about a third.
2. [art] Measure luma; if median is below 0.11, lift the water fill and the window glow, keeping the tower brightest (12.1, values.solve).
3. [art] Give the grease pencil real wax treatment (opacity 0.96, under-shadow `PENCIL_SHADOW`, rough edge) and thicken it to the 9.2 widths (8 px walked, 5.2 px ahead at 1080p).
4. [art] Add node-kind stickers or rings by shape and ROOM_TL color on the satellite domes; keep numbers for options only.
5. [art] Remove the TEST caption. Enlarge the TARGET label to the 18 px terminal floor or move it onto the tower axis.
6. [art] Add at least one hero sign or lit band per route column on the tower and 6 legible signs across the sea city (9.1, dressing.signs), in a Tethys hull palette.
7. [art] Vary the window-dot pattern: dark patches and a calm apron near the tower (density.falloff) to break the carpet.
8. [spec] Decide whether underwater sign rules differ and write that in 9.1 if so.

### CLOSEUP (`tethys_closeup_v2.png`)

**What it shows:** The same scene from a lower, closer camera: tower and dam, no route, no UI. A wall of lit windows rings the far horizon, with tall posts topped with blue rings. This is not a DECISION or HOVER frame and has no route to judge.

**Rule breaks**
1. Not a deliverable frame: Tethys has no DECISION or HOVER final, so 6.4 (front and centre on the current room, pitch beat, hover pull), 9.4 (power cut) and the occlusion rule (7) cannot be verified. [spec] Blocks sign-off.
2. Camera (6.4): the tower is centered, but the framing is not on a room. The tower shrinks to about a third of the frame width, below the corp fill values of 0.56-0.74 given for others. Uncertain, as Tethys has no row in the 6.4 per-corp table. [spec] Add one.
3. Occlusion (7.1): the dam wall and the front plinth block the tower's lower half (the base cut-out is visible beneath the platform). No stub or ghost treatment visible, and the dam is not cut, so rooms on the lower tower faces would be hidden. Uncertain.
4. Background wall of lit windows at the horizon is a hard, even band. It reads as a flat backdrop (horizon.break, R-HOR-1: the straight line). The far posts with rings repeat evenly (repetition.guard).
5. Value band (12.1): by eye, again dark overall, with the lower-left bright street lines and the lit wall as the hot areas. The upper third is near black. Uncertain.
6. Landmark ratio: similar to the overview. The tower's top domes are brighter than in the overview, so this is probably slightly better, around 1.5. Uncertain.

**Readability:** Landmark reads clearly as a centered tower. No route or target is present. The competing elements are the dam wall lamps and the horizon ring of windows.

**Strengths to keep:** the tower's silhouette holds from both cameras (consistent with 8.6b); the wall's cast-light scallops are a good Tethys material read; the horizon posts give a sense of an enclosed dome.

**Fix list**
1. [spec] Add Tethys camera rows (pitch_lo-hi, lens, dmin, fill, OVERVIEW values) to 6.4.
2. [art] Produce DECISION and HOVER finals with sticker nodes, options and the 9.4 grade.
3. [art] Break the horizon band with an irregular skyline and fog layers (horizon.break).
4. [art] Add stub/ghost handling for the dam in DECISION so the lower rooms stay visible.
5. [art] Rim-light the tower base to separate it from the dark plinth.

## How the set holds together

Only two frames, one angle family, so continuity can only be partly judged. Palette and scale are consistent: the same tower, dam and teal water, and the lit-wall warmth carries across. The OVERVIEW has the route and UI; the closeup has none, so I cannot tell whether the camera moves from one to the other along the 6.4 rules or whether the UI language (stickers, ring colors, ROOM_TL kinds) is applied at all. Hover and the power cut cannot be compared. Another-corp test: with the spire and domes the silhouette is distinct, but the cream-and-teal palette with a ring and spire could be confused with Halcyon's pyramid-and-eye tone only at thumbnail size; the water, fish and dam rule that out. The identity is carried by environment, not by the corp hue. Tethys's hue in 3.4 is (0.184, 0.42, 1.0), a saturated blue, while the frames read teal-cyan; uncertain whether this is the grade.

## Top findings

1. BLOCKER: No DECISION or HOVER frames exist for Tethys, so 6.4, 9.4 and 7.1 cannot be accepted; the closeup is not a substitute.
2. MAJOR: The landmark does not clearly lead (12.2 / R-FOCUS-1): the lit dam wall competes and the ratio is likely under 1.5.
3. MAJOR: Overall value is probably too dark (12.1; upper half near black); must be measured and solved after the vignette.
4. MAJOR: Route pencil and nodes miss 9.2 / 9.3: thin vector lines, no wax finish, and identical node dots with no kind shapes or colors.
5. NIT: A TEST caption, tiny TARGET label and absent hero signage (9.1) remain; also a hue field that is near-monochrome teal.

Q: Does Tethys get its own row in the 6.4 camera table (pitch, lens, dmin, fill)?
Q: Is "ATLANTIS STATION" a name to keep, or a leftover test label? The working names use THE BLACK SMOKER only.
Q: Are underwater sign rules different from 9.1 (neon shapes, projected holos), and should the spec say so?
Q: Should Tethys's hue be the 3.4 blue (0.184, 0.42, 1.0) or the teal in these frames?
