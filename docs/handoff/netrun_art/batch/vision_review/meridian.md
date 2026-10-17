DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id vis__meridian; status ok; tokens in 5992 cache-write 69629 cache-read 0 out 6273; cost $0.124 -->

# Vision review: meridian

All luma figures are estimated by eye on downscaled frames (<= 1568 px). Treat them as uncertain, not measured. I can only judge what is visible in the three images.

## Per frame

### OVERVIEW (H_overview_v3.png)

**What it shows:** A high oblique view of a walled container yard, the fortress, with two corner towers at the back and a lit gatehouse. The city fills the rest of the frame. The lime walked route runs along the front-right wall to an orange "next" link, and a white dashed "ahead" route climbs to the red TARGET circle at the upper left. The HUD, dossier, ROUTE panel and legend are all drawn.

**Rule breaks**
1. Value band (12.1, R-VAL-1/2/3), whole frame. By eye the city is bright, with a dense field of lit windows, orange sodium streaks, magenta glow top-left and top-right, and a bright yard floor. The median looks above 0.14 and the under-0.10 share looks below 25 %. This is uncertain. If a measurement confirms it, it is a fail on R-VAL-2. The 2.5 % cap over 0.85 is probably at risk where the gatehouse and the yard-floor glare burn out.
2. Landmark ratio (12.2, `landmark.lead` R-FOCUS-1), fortress vs ring. The fortress is large but not clearly 1.5-2x its surroundings. The wall rim is a thin pale line, while the surrounding towers carry about the same lit-window density and orange/magenta accents. The yard interior is bright, but the walls and towers are mid-tone and blend into the city. The ratio is uncertain but probably near the 1.5 lower limit. The spec's 8.3 asks for rims, cove lights and uplights on the landmark, and only the front rim and a few tower strips are readable.
3. Density rule (13.1 rank 3, `density.falloff`, R-CALM-1/2). There is no visible quiet apron. Lit-window density around the compound matches the far field. The whole frame reads as one even carpet of dots, which is the failure that rule 3 describes, and it competes with the route.
4. Palette (13.1 rank 5, `palette.districts`). Orange fits Meridian (8.5, 3.4), but the frame also carries large magenta/violet zones top-left and top-right and a lot of cyan and green window pips. Magenta and violet read as Halcyon's hue and the neon_bay districts. A viewer will not read this as an orange-dominant freight city.
5. Rail (8.5 Meridian, 3.4 L4, C8). The freight line on a viaduct at deck_z 17.5 BU is not visible anywhere. The foreground light streaks look like road traffic and the loop track. I cannot confirm any viaduct, signals or catenary masts. The DISPATCH text mentions a train and a quay, but I cannot find them in the frame. Uncertain.
6. Moat (8.5, C24). I cannot identify any moat on the W/S/E sides, and I see no rail yard or gate on the north side. Uncertain.
7. Crane (8.5, 8.6b). The slewing keep crane is not identifiable. The left tower and the top towers show as plain wall blocks with a red front face. The ART_BIBLE (2.4) calls for a "gantry-crane keep", and nothing in this frame reads as one, so the silhouette is a generic walled box.
8. Occlusion (7.1, 7.3). Buildings in front of the fortress, bottom-left and bottom-right, are not cut or ghosted. The near wall and the front-left towers partly cover some of the route nodes (for example, node icons on the left wall near the left tower sit in dark wall shadow). The pencil is legible, but the route nodes at the left tower base are small and low contrast. Some nodes sit hard against the wall and look nearly lost. Uncertain at this scale.
9. Signage (9.1, `dressing.signs`). No hero signs are identifiable on route columns, and no legible signs are visible. The only readable text is the TARGET pencil and the tooltip. Because this is an HQ and not a street, 9.1 applies only partly, but `dressing.signs` and the corp's identity (barcodes, container stencils, hazard rim) are barely visible.
10. Grease pencil (ART_BIBLE 1.2, spec 9.2). The pencil states follow the spec: lime walked, orange option, white dashed ahead, red TARGET. The orange "next" segment is short and sits against the orange-lit wall, so it nearly disappears. The lime path's two zigzag spikes (right side) look like a routing artifact and not a hand wobble. The pencil crosses stickers near the right wall, and the spec's 5 px `CLEAR_PAD` is not clearly respected there. Uncertain.
11. UI vs pencil (ART_BIBLE 1.2: no UI covers pencil). The TARGET tooltip "CENTRAL SERVER // THE MASTER MANIFEST" overlaps the pencil node and the dashed line just right of the target. This is a minor overlap, but a rule break.

**Readability:** The fortress is the main shape, and the walled box reads against the city because of the dark interior border and the lit yard. The lime route is clear, the TARGET circle is clear, and the dashed route is easy to follow. The next/option node is hard to find, because the orange link and the orange wall lights are similar. Competing: yard-floor glare, the streak lanes at lower center, and the magenta towers at the top.

**Strengths to keep:** The container-yard interior with stacked boxes reads as freight. The wall lines are crisp. Route colors follow 9.2. The red TARGET circle reads well. The HUD and legend are intact.

**Fix list**
1. [art] Lower the yard-floor and gatehouse highlights, then re-solve exposure after the vignette (13.1 rank 10); confirm with 12.1 numbers.
2. [art] Add a rim and uplight to the walls and towers (8.3 rule 2) so the ratio reaches 1.5-2.0, and measure it with 12.2.
3. [art] Dim windows within `apron_bu` of the walls and add dark blocks (13.1 rank 3); keep the buildings.
4. [art] Cut the magenta/violet bank glows near this HQ and push amber/sodium (3.4 freight hue (1.0, 0.549, 0.102)).
5. [art] Make the freight line visible: viaduct, piers, signals and masts from `zoned.json` (8.5, C8). [spec] Q: is it meant to appear in OVERVIEW?
6. [art] Give the "next" link a darker under-shadow or a white keyline so it separates from the orange wall (ART_BIBLE 1.2 pencil shadow).
7. [art] Remove the spikes on the lime path, or confirm they are intended wobble.
8. [art] Move the TARGET tooltip off the pencil.

### DECISION (H_decision_v3.png)

**What it shows:** A close view from above along the street and the yard wall. The current room is a lime-framed room with a pink sword sticker and a green event icon. Two options (1: a lit panel, 2: a pale blue room at the upper right) are in orange frames. The orange branch lines run to both, with a white dashed ahead line and a lime walked line at the lower left.

**Rule breaks**
1. Value band (12.1). The frame has large dark areas (the wall, the left mass) and strong sodium highlights on the trucks and wall strips. Median looks plausibly near 0.12-0.18 and the under-0.10 share plausibly 35-45 %. If measured above 40 %, R-VAL-2 fails. Over-0.85 pixels are probably near the limit at the lamp cores and truck headlights. Uncertain.
2. Camera (6.4, `HM/hq_cam.py:166-179`, "front and centre"). The current room sits at about the frame's center-right and lower-middle, not at the center of the usable area (x 300-1900, y 138-1012 at 1080p). The room is clearly right of and below center, and option 2 is at the upper right edge. Options 1 and 2 are spread far apart vertically. The DECISION azimuth rule says to look at the mean of the distinct normals, and the current shot looks off-axis. Uncertain without the room normals.
3. Room readability (12.6 "Available rooms unblocked", `room_px_target`). Option 1 (the "1" room) is small and dark, and its icon is tiny, partly hidden behind the pencil cluster. Option 2 is pale and flat, reading as an empty glass box, with no kind-specific interior or stencil. The rooms have little interior content. Blocked share uncertain.
4. Occlusion (7.1). The tall dark mass at the left (the wall of the compound or a building) fills about a third of the frame and is neither cut to a stub nor ghosted. It does not cover the rooms, so the rule technically holds, but it adds a large dead area and pushes the composition to the right.
5. Sticker rules (ART_BIBLE 1.2, 9.3). The sticker on the current room is readable. The option rooms have number chips ("1", "2") with no readable sticker faces and no die-cut border at this scale. The option stickers are small. Per 9.3, stickers sit at the left cut edge, 38 % down, and here they seem to overlap the frame edge. Uncertain.
6. Pencil (9.2). The orange branch to option 2 runs a long vertical line down the right of the wall, then a diagonal back to the current room. It overlaps the wall edge and a street light strip. The lime walked line at lower left runs off-screen with a sharp corner. The white dashed line passes through option 1's cluster and crosses the orange lines.
7. UI vs pencil. The legend and sidebar are clear of pencil. OK.
8. Identity (8.5, 3.4). Inside this frame there are trucks with orange roof lights and the wall's long light strip. I cannot see containers, a hazard rim, barcodes, rail or the crane. The scene reads as a generic night city with a warm street. Meridian is hard to recognize.
9. Palette (13.1 rank 5). The upper right has magenta and cyan strip signs, and the dark wall has pink/violet patches. These do not read as freight.
10. Bits of visible geometry: a dark stepped silhouette at upper left, with pink-lit edges and purple top faces, reads as stacked containers. Good, but its color is violet instead of rust or orange.

**Readability:** The current room (lime) is the clearest thing in the frame. The options are findable by their orange frames and numbers, but only the number chips identify them. The TARGET is off-screen at the top, and I see only a small icon at the top edge. 9.5b says an off-screen TARGET gets a red edge arrow, and I cannot find one. That is a rule break, uncertain. Competing: the bright truck cluster in the lower right, the long horizontal wall light strip, and the neon strips at upper right.

**Strengths to keep:** The street-level truck streaks and glow give life. The wall light strip gives strong perspective. The rain is subtle. The pencil colors follow the spec.

**Fix list**
1. [art] Re-aim the camera so the current room sits at frame center (6.4, `centre_current`); check the azimuth rule.
2. [art] Show an off-screen TARGET edge arrow, per 9.5b. [spec] Q: confirm the arrow is drawn by Godot, not the render.
3. [art] Give option rooms kind-specific interiors and readable stickers (9.3, ROOM_TL colors).
4. [art] Ghost or cut the left wall mass (7.1) so the left third carries less dead weight.
5. [art] Re-color the violet stacks to rust or orange (3.4 freight albedo) and reduce magenta strips.
6. [art] Reroute or shorten the orange branch so it does not run along the wall light strip; add the pencil under-shadow.
7. [art] Lower the truck headlight peaks to protect the 2.5 % cap.

### HOVER (H_hover_v3.png)

**What it shows:** The same camera as DECISION, with everything outside the hovered branch crushed to near black. The hovered option 2 (a pale room with a "FIGHT L6" tag and a cursor) and the current room stay lit, as do the pencil branch and the lime walked line. A FIGHT // L6 info card is open at lower left.

**Rule breaks**
1. Hover power cut (9.4, Q6). The spec values are outside x 0.20, 70 % desaturation, branch x 1.35 and type glow 1.0, so the outside should stay at about 20 % and the branch about 6x brighter than the rest. Here the surroundings look much darker than x 0.20 and near-black, and almost all window dots, signs and streaks are gone. It reads as roughly x 0.05-0.10, not 0.20. Uncertain by eye, but it looks harsher than specified. The wall, trucks and city lose all form, and the tunnel-like blackness removes the context that the always-alive city rule (9.6) asks for.
2. Branch coverage (9.4 rule 1: "the whole branch to the TARGET lights"). Only the two rooms and the pencil are lit. The path to the TARGET is the white dashed line, which fades out at the top, and the TARGET room itself is not lit. I see an unlit icon at the top of the frame. This breaks "the whole branch to the TARGET lights". Uncertain, because the target is partly off-frame.
3. Option 1. Option 1's room (the "1" node, at the middle left) stays visible but dim, with its icon in an orange ring, so the non-hovered option is still partly lit. The spec says everything outside the branch dims. The branch includes option 2 and the ahead route, so option 1 should be dim. It is acceptable, but it looks lit like the branch. Uncertain.
4. Value band (12.1). Hover frames are exempt, as the spec says. No finding, though I note that the frame is mostly under 0.10.
5. Info card. The FIGHT // L6 card covers part of the UI zone only and does not overlap pencil. OK. It shows the "41 / 60 on arrival" HP line, which is game data and fine.
6. Corp identity. With everything dark, Meridian identity is almost entirely gone: no orange wall, no containers.
7. Pencil. The lit branch in orange and the lime path read clearly. The lime path at the bottom runs into a bright truck, and the line vanishes near the lower center. Fine.

**Readability:** The hovered branch is very easy to find, much easier than in DECISION. The player can find the current room, option 2 and the route. The cost is loss of spatial context. The unlit TARGET at the top is hard to find.

**Strengths to keep:** The clear branch emphasis. The hover tag "FIGHT L6". The info card reading. The pencil under-shadow works well against black.

**Fix list**
1. [art] Raise the outside level to the spec's x 0.20 (or tune toward x 0.35 as 9.4 allows) so the wall and the street still read.
2. [art] Light the full branch to the TARGET, including the target room and its edge marker.
3. [art] Dim option 1 to match the other non-branch rooms.
4. [spec] Q: does the 2D grade mask grow 8 px and blur 8 px as in 9.4 rule 6? Edges near the room look hard.

## How the set holds together

**Camera and scale:** OVERVIEW and DECISION are consistent in lighting direction and in the wall that runs diagonally through the frame. DECISION and HOVER share an identical camera, which is correct. The jump from OVERVIEW to DECISION is large, so I cannot confirm that the zoom is a 1.0 s log-space move on the same geometry. Room and route positions seem plausible. In OVERVIEW the lime route enters at the lower right, and in DECISION the walked lime line also comes in from the lower left. This is probably the same route but I cannot verify it. Uncertain.

**Palette:** Consistent across OVERVIEW and DECISION: sodium orange, with magenta and cyan accents. HOVER drops to near black, which is expected from the cut. The shared UI frame, pencil colors and legend are stable across all three.

**UI:** Identical, with the same HUD, dossier and ROUTE panel. HOVER adds the info card. The DISPATCH line is the same text in DECISION and HOVER and differs in OVERVIEW, which is acceptable.

**Corp identity:** Weak. The orange accent and the stacked-container yard in OVERVIEW are the only Meridian cues, plus the "MERIDIAN" dossier header. With the dossier removed, the frames could be mistaken for a generic cyberpunk city, or for Halcyon, because of the strong violet and magenta tones. DECISION and HOVER carry almost no Meridian-specific element.

## Top findings

1. **MAJOR:** The Meridian landmark identity is not shown: no readable crane keep, moat, freight viaduct or rail yard in any frame (8.5, 8.6b, C8, C24).
2. **MAJOR:** The hover cut looks much darker than the approved x 0.20 and does not light the branch to the TARGET (9.4); the city context is lost.
3. **MAJOR:** The landmark does not clearly lead its surroundings (12.2, R-FOCUS-1); it has no apron or dimming (`density.falloff`) and no rim lights, and the city competes with it.
4. **MAJOR:** DECISION framing is off-center: the current room is not at the usable-area center (6.4), the option rooms read as bare boxes (9.3), and the TARGET has no off-screen arrow (9.5b).
5. **NIT:** Magenta, violet and cyan accents dilute the freight hue (3.4, `palette.districts`), the value band probably runs bright in OVERVIEW and dark in DECISION (uncertain; measure with 12.1), and small pencil and tooltip overlaps remain (9.2, ART_BIBLE 1.2).

Q: Should the freight viaduct and rail yard be visible in OVERVIEW at this zoom, or only at street level?
Q: Is the TARGET edge arrow (9.5b) drawn by Godot as an overlay, and so absent from the renders by design?
Q: Is the lime path's zigzag in OVERVIEW the intended hand wobble or a route-path artifact?
