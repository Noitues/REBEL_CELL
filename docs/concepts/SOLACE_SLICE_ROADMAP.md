# Solace vertical slice: art roadmap after the city view

Written 2026-10-29 by art-pass for a fresh session. Rulings live in `docs/concepts/DIRECTION_REVIEW.md` and the look rules in `docs/ART_BIBLE.md`. If this file disagrees with either, they win.

## Where things stand
- **City view (tide raid, Godot):**
  - Rounds r28–r35 brought the city back to the round-6 look (`round6_city_restyle/views/restyle_night_crop.png`):
    - Cv2 facets with cel bands and wobbly ink;
    - corp colour per building, weighted toward each HQ and capped at 0.65;
    - corp neon rims and masts;
    - saturated continuous avenues;
    - dark grey-green ground and blue bay water;
    - traffic and highways as in round 26 city motion.
  - The designer approved the buildings on r29.
  - Clone: `D:/rc_art/godot_look_tide`; branches `art/tide-rNN`.
  - Outputs and notes: `docs/concepts/tide_raid/G1_parity/rNN/` and `NOTES_ROUNDNN.md`.
- **Combat (Shifting Waves):** plates E7–E10 are done (display A with H's thin slice bars; ART_BIBLE §3.22). E11 waits for build's critic brief.
- **Build mailbox:** A-104 to A-108 are open (river width, Solace pocket parks, rail and wall routes, height rhythm, river infill and park-split streets and bay roads). Build's last entry is B-081.

## 1. Finish the city view (art-pass, in progress)
1. r35:
   - land, not water, under the highway by the bay;
   - the north-south wall route drawn as a highway;
   - the wall ring round the HQ removed.
   Then tell build the wall routes now draw as a highway or nothing (a new A entry).
2. A shoreline highlight where the bay meets the city (it needs the coast contour).
3. Designer approval side by side with the old `G1_parity/final/`, then replace final/.
4. Update the golden plates to the new rulings: round-6 look, corp colour, grey-green ground, blue bay, north-south highway, no HQ wall, river, no pink parks. Later work is judged against these, not the old AAA-2 plate.
5. Hand-off package for build:
   - the branch;
   - config switches, including `CityView3D.art_look`, which is false in `route_rig.gd` and keeps the city look out of the netrun;
   - the shaders changed (`wet_street` ground_mul, `city_ground` bay, CityCorpColor, avenue strips);
   - quality tiers;
   - the A-104 to A-108 specs.
   The full test suite runs at build's merge.

## 2. Cohesion pass (next)
- **Slice sheet:** one Solace frame of every state, side by side:
  - campaign: City Grid, Heat, win and lose;
  - run: Site dossier, netrun route, Terminal event;
  - combat: Shifting Waves, rewards and shop;
  - raid: setup and defense;
  - HQ: the boss run.
- **Check across the sheet:**
  - corp colours (ART_BIBLE §2.4);
  - the pink rule: unit screens only, darkened;
  - UI chrome;
  - value and contrast between states.
- **Raid mode:** a dimmed grade of the new city so the placement lines lead, as round 40 did for round 6 (`round40_city_unified/raid_view_v3.png`).
- **Output:** a list of what each state needs redone against the new city.

## 3. Netrun look: DESIGNER DECISION first
- ART_BIBLE §1.2 and §4.6 still put netrun streets and HQ netruns in AAA-2 realism (PBR, fog, no ink). The entry dive blends cel into realism.
- The city is now round-6 cel, and netruns use the real city buildings. The options:
  - **(a) Netrun stays AAA-2:** the dive crosses between looks.
  - **(b) Netrun goes cel:** one continuous look.
- This decides the transitions and the Solace HQ netrun.

## 4. Transitions storyboard, then the motion pass
- **Transitions:**
  - City Grid → netrun: the zoom into the street on shared geometry;
  - netrun → combat, and combat → back to the run;
  - City Grid → raid zoom, then raid → defense → result;
  - city → HQ approach.
- Each needs timings, camera paths and the UI hand-over, plus a reduced-motion variant.
- **Then the motion pass:**
  - the living city: traffic streaks move along the lanes; they are already per-entity quads;
  - sign flicker;
  - the transitions themselves.

## 5. Solace HQ netrun
- `solace_vertical/hq/` v5 plates predate the lime district helix and the round-6 look.
- Re-render them in the look chosen in step 3, then port them to Godot. The HQ boss combat backdrop follows.

## 6. Supporting screens in the converged look
Most of these exist from earlier rounds but were drawn against the old city. Recheck each against the slice sheet.
- **Story:**
  - DISPATCH briefings and dialogue busts (low-poly cel on a CRT feed);
  - the Terminal event card (a CAM feed tinted Solace).
- **Run:**
  - Site markers and dossiers on the new city;
  - reward, shop and deck screens.
- **Campaign:** the Heat strip and the campaign-lost screens.

## 7. Polish and reach (M4 / M12)
- Reduced-motion variants.
- Colour-blind check of the corp hues and avenue colours.
- Perf on the lower quality tiers, since the city now has more neon and ink.

## Order
1. The city view (step 1).
2. The cohesion sheet; it flags the redo list.
3. The netrun-look decision.
4. The transitions storyboard.
5. The Solace HQ netrun.
6. The supporting-screen redos.
7. The motion pass.
8. Polish.

## Standing rules for any session doing this
- Art only, no game design.
- Rules and layout go to build through the mailbox (A-NNN in art-pass `MAILBOX.md`).
- Never write in `D:/Godot/rebel_cell`.
- Never run `python -` in any form.
- D: drive only.
- Commit by explicit paths with the co-author line.
- Review every sheet side by side with its reference, against the ART_BIBLE, and with a squint test.
- Show the designer a checkpoint every few rounds rather than running long stretches alone.
