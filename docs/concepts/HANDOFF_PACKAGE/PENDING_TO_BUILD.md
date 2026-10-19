# Messages to the build session, held (2026-10-18)

The app paused session-to-session messages after 10 sends. Send these on the designer's next message.

1. **Derive v2 review is done:** art-pass e4d5ecdc (built on 08064867), `HANDOFF_PACKAGE/DERIVE_V2_REVIEW.md`. Its final section, "AD resolutions", wins over the earlier rows and over the proposal, and it answers every blocking question.
   - Rooms and columns:
     - Both quads are normalised to BL, BR, TR, TL as seen from the street.
     - `u` is the signed distance from `street.a`.
     - `face` is one float.
   - Camera:
     - Yaw follows the rig convention: 0 = north, clockwise.
     - The street `pitch_o` is 2.0, and more rig constants are stored.
     - `zoom_dive` is measured to the OVERVIEW target.
   - Section and occlusion:
     - `section.params` and `occlusion.params` are per pose.
     - `sec_plinth` is 0.1425 BU.
     - **Q3.10 is reversed:** the JSON uses the shader's 28 flat KEYS.
   - Dress lists:
     - Beams: `lean` is [x, y], plus `sweep_deg` and `phase`.
     - Lanes: each lane has `streaks[]`, with the speed quantised to the 4 s loop.
     - Signs have `band_pal`. Lamps and washes store `pal`.
     - Glows: a palette id plus drift.
     - Fog: one global box.
   - Readers accept rest, workshop and cache as room kinds.
   - Still open on art-pass: the look-bias sign, to be checked against a still.
2. **Meridian HQ rect overlap (NA-02 question): not intended.**
   - An HQ rect is exclusive. Spec 2.0 step 1 and 3.1 step 2 say landmark lots are excluded from the frontage and fill rules, and the 8.6 lot coverage rule needs ≥ 90 %.
   - City cells 13:-36 and 13:-32 originate inside [4,-36,10,10], so the gantry footprint must clear them.
   - The fix is on the game side (layout / NeonCity): place no city cell whose rect intersects an HQ rect. Until then, the exporter flags them in a `hq_overlaps[]` diagnostic list. They must not be silently dropped, because dropping them would change the bids the game uses.
   - Check that the other corps' rects are clear too.
3. NA-02 merge acknowledged. Run id, kind = "hq" for a boss run, `nodes[].lot` in BU and the per-corp landmark seeds are all fine with art-pass. The 9 MB `city.json` is fine because it is built once per layout seed.
4. **NA-04 asks:**
   - Pin `p_city_night` to ded90765. Don't regenerate `rules_check.md`; the 4K finals become golden plates.
   - The check input shapes are answered in `DERIVE_V2_REVIEW.md`, "Check input shapes for NA-04":
     - The beam list is accepted, with the spot/shaft fields from the look.preset rig and `route_bids` = `route_keys`.
     - `items[{kind, pos}]` is rejected; the checks use the typed dress lists, flattened for 12.4.5.
     - `zoned.rail.piers` is accepted.
     - The 0.5 BU box is accepted (provisional).
5. **W0_COMBAT review (main ccdf8bc1): FIX LIST. Not approved yet. Panels 2, 3, 4 and 5 are approved as they are.**
   - **Panel 1, confirmed:** the enrage tooltip covers the boss wheel's top-left slices and the needle zone, which is the information that matters at turn 10.
     - Anchor it outside the disc: below-right of the badge, clamped to the view, with a 12 px gap from the wheel's rim ring.
     - Give it the standard dark tooltip plate, so it doesn't read as text over the city.
   - **Panel 6, confirmed and more serious:** at 1080p the disabled nudge arrows can't be seen at all. The toast sits at the bottom centre, far from the aim ring, so nothing on screen links the refusal to the satellite.
     - Draw the disabled arrows at full enabled size, 50 % grey, with a red diagonal strike.
     - Add a short refusal shake on the aim ring (about 0.25 s, ±3 px) and a red flash on the satellite.
     - Either anchor the toast beside the aim ring, or give it a leader line to the ring.
   - **Known items, also required before approval:** THE PANOPTICON name, and the EVADE / EVADED → SANDBOX / SANDBOXED word sweep (result chip and LAST TURN line).
   - Re-send the sheet once these are in. I will review only panels 1 and 6, plus the changed words.
6. **W0_SITENAMES review (main 0a596d73): FIX LIST. Panel 2 (raid map) is approved.**
   - **Panel 1, Grid:** the before and after halves are pixel-alike, with no name label and no Site card in either, so the panel shows nothing to judge. A flow test isn't visual evidence. Re-capture with a Site selected, so its card renders, and with one Site hovered. The card and the hover label must show the SiteText type, not a name.
   - **Panel 3, netrun header:** no visible difference between the halves. Add a 2× crop of the spot where the Site name used to sit (header or dossier line), before and after. If no name was shown there, say so and drop the panel.
   - **Panel 4, reward header:** "SITE" is too weak. Use the tier and the SiteText type: `LOOT // NETRUN: T2 <TYPE>`, e.g. "T2 SERVER RACK". Use the type word, not the objective. The tier tells the player why the loot is what it is. HQ runs keep `LOOT // NETRUN: <HQ BUILDING>`.
   - Re-send the sheet with panels 1, 3 and 4 only.
7. **W0_COMBAT re-run (main 6f5eac32): item 5 still stands for panels 1 and 6.**
   - The words are fixed: THE PANOPTICON, and SANDBOXED / +N SANDBOX. Those words are approved.
   - Panel 1 is still not fixed: the enrage tooltip still covers the boss wheel's top-left and its needle.
   - Panel 6 is still not fixed: the disabled nudge arrows still can't be seen, and the toast is still far from the aim ring.
   - Apply item 5's fixes to those two panels, then re-send panels 1 and 6 only.
8. **B_TEACH_W0 (main 6f5eac32): APPROVED.**
   - Row 6: the whole THIS TURN list now shows.
   - "1 LANDS HERE" sits clear of the box.
   - The box stays clear of both wheels.
   - Non-blocking: row 7's AFTER has a hovered JOLT card that its BEFORE lacks. Keep before and after in the same state in future captures. A still can't show the NEXT pulse, so please state its minimum alpha or luma in the B_TEACH notes. It should stay at least 0.6 of full.
9. **B_MENU_C_SCREENS (main 7397cd01): FIX LIST.** Every finding in your .md is confirmed. Additions:
   - **C6 pause menu:** besides centring it, make "set apart" stronger. A blank gap reads as a layout accident. Add a thin divider rule above Quit to Main Menu, and keep at least one row height between Abandon Run and the Quit rows. Abandon keeps its pink and "No Going Back".
   - **C7 tiles:** the price must not wrap. Use the HUD's Schematics icon with the number, "UNLOCKS · [icon] 60", on one line, and drop the word. Move the currency line from the far right of the Target head to directly under the TARGET heading, left-aligned next to the tiles, with the same icon in the Schematics HUD colour: "[icon] 37 held, earned in a campaign". This replaces the P2 "too faint" fix.
   - **C8 toast:** use the chip/sticker style with the card's type icon. It isn't plain mono text. The bottom-centre position is fine.
   - **G14 confirm:**
     - Show both chips as icons in the dialog: Barbed Wire → Burner (struck). Today the scrim blurs exactly what is being lost.
     - Use one text style for both lines, not large sans plus small mono.
     - Text: "Socket Barbed Wire into slot 5?" / "Burner is destroyed. This can't be undone."
     - KEEP is the default focus and the safe primary. SOCKET IT is a red-outlined destructive button, not a sticker equal to KEEP.
     - Leave at least 16 px between the buttons and the panel edge.
   - **C4 Heat tooltip:** fix the widow as you noted. Otherwise approved.
   - **Cross-ref:** the "LOOT // NETRUN: SITE" header and the "T1 // SITE" card in panel 5 follow item 6, i.e. tier + SiteText type.
   - Re-send the whole sheet after your fix slice.

## Held 2026-10-18 (second pause)
10. **City-plate update landed** on art-pass at 57c901fc and 8e6f6b7d: please re-run drift.
    - Every `capture.json` now has `time` ("day" for `city_a2_day`, "night" for all other plates).
    - City R-FOCUS-1 is now scored: night 1.77 (pass), day 0.93 (report).
    - On the day plate, the value band, `landmark_ratio` and R-FOCUS-1 are "report" and are not in its baseline.
    - HQ and street values are byte-identical.
    - The street capture stamps are now `ed8675a8`.
11. **NA-23 answers (W1_NA23, main 59a11ba6):**
   1. **12.6 route-never-occluded check: count by depth.** A pixel counts only if it is in front of the room: class 2, inside the room's screen box + 12 px, more than 1 BU nearer than the room's front, above stub, and surviving a 4 px erosion. That is art-pass `street_r2/scripts/r2_occlusion.py`. Add `depth.png` to the 12.0 capture: 16-bit linear camera depth, in BU × 100, nearest-sampled. Don't exclude the neighbours, and don't hold a clear ring.
   2. **Fix the span rule for every column.** Choose the span so that the smallest visible route room in OVERVIEW is ≥ 46 px, not the layer-1 rooms only. Regenerate the Python and fixtures. Spec 12.6 already says "every room". The concept parity follows the spec, not the other way round.
   3. **Adopt your id.png room encoding:** G is the 1-based place in the run graph, B is the layer, and route-building walls are class 2 with B = 1. Stubs stay class 2 with G = 255 and B = 0. I'll update §12.0.
   4. **Fog in NA-24:** agreed.
   - **R-REP-1:** your 0.785 equals my whole-frame value, so you are measuring the whole frame. Use the facade band `facade = [x0, y0, x1, y1] = [0.0, 0.10, 1.0, 0.80]`, as fractions of the frame, y from the top. Pass it as `spec["facade"]` to `pvc_metrics.repetition` (art-pass `golden_plates/scripts/make_plate.py:179-181`; `proc_vs_custom/scripts/pvc_metrics.py:15, 372`).
   - **W1_NA23 look: FIX LIST.**
     1. **Missing look.** DECISION and HOVER don't show the approved NA-22 lb1 look: no window carpet, no street wash, no trims. The buildings are blank dark slabs. The netrun views must run at lb1 with NA-22c.
     2. **Room placement.** Route rooms read as UI boxes stuck on blank walls. They must read as cutaways inside the route building: the room front is flush with the facade, and the building around it carries the facade, windows and wash, as in the concept (`street_r2` and the storyboard derive).
     3. **Lane markings.** The yellow stripes are too saturated and bright, and they dominate DECISION. Use the r2 streak lanes and desaturated kerb and lane lines.
     4. **HOVER.** The power cut grade is fine, since it is exempt.
     5. **Re-send.** OVERVIEW and DECISION for seed 1 after fixes 1–3.
12. **W1_NA24 street dressing: FIX LIST.** The overview improved a lot: the beams, less fog, the lanes, and the value band passes on both seeds.
   - **(a) Raise sign emission, in NA-24, not NA-33.** Signs are the main carrier of R-DET and R-CALM. Avoid over-0.85 whitening by stacking signs differently, not by dimming them:
     - each sign has a thin bright core line or text strokes (luma about 0.9 over a few px) on a softer panel (0.35–0.5);
     - combine overlapping additive layers with max, or clamp them, so they don't sum;
     - over 0.85 must stay ≤ 2.5 %.
   - **Hero signs.** They read as plain stacked lime bars, like girders, not signs. Make them blade signs:
     - 3–6 panels with glyph or text-block strokes;
     - a frame trim;
     - per-panel hue from the district hue + sec + one accent;
     - per-panel brightness variation.
     - Lime is right for Solace territory, but not as a single flat hue.
   - **(b) District palettes.** No palette assets exist yet; the source is the art-pass city preset (`city_all_corps/scripts/city_preset.py:28-55`, `DISTRICTS`). Proposed ids:
     - `solace_mint`: hue (0.239, 1.0, 0.545), sec (0.85, 1.0, 0.9), win [(0.75, 1.0, 0.82), (0.45, 1.0, 0.62), (0.95, 1.0, 0.95)].
     - `orbital_ice`: hue (0.498, 0.659, 1.0), sec (0.92, 0.96, 1.0), win [(0.70, 0.84, 1.0), (0.92, 0.95, 1.0), (0.55, 0.75, 1.0)].
     - Halcyon, Meridian and Rebel Cell have entries in the same table, so use those instead of `neon_bay` and `sodium_teal` where they differ.
   - **DECISION.** It still shows item 11's issues: blank slab buildings, rooms as boxes on walls, and loud yellow lanes. Item 11 stands.
   - **12.2 ≈ 4.0 on the street.** The route rooms glow too white against the dark city. Lower the room interior emission about 25 % (target ratio ≤ 2.5), so they still lead but don't punch holes.
   - **Streak lane clock** with period k·T: good catch.
13. **W1_NA25 jack-in / jack-out review: FIX LIST.** The beat timing and the HQ-side terminal, rain and collapse read well. Skip lands on the same CHOOSE frame. MARK and ZOOM are fine.
   1. **The mid-dive blotches.** In "3d dive 1.5 s" there are irregular, cloud-shaped flat patches, white to pale pink, with no glow edge. They sit on roof caps and street tiles, cover roughly 3–5 % of the frame, and appear only in that frame. The shape looks like a noise mask, so my guess is the puddle / wet-surface mask going to full white specular while look_blend is between 0 and 1. A likely cause is that the wet roughness and puddles_sharp weight are at their netrun values while the mainline lighting is still on. Check the wet material and puddles_sharp across lb 0..1. The roof caps also hint at the section poche or the street wash evaluating on horizontal faces; the wash should apply to vertical faces only.
   2. **Black voids.** At "dive end", "4 REVEAL 1.5 s" and "JACK OUT reverse", the route rooms not yet revealed show as solid black boxes on the facades. Until the facade dissolve (NA-25b) exists, an unrevealed room must show its closed facade (the building's normal windows and wash), never a black slab.
   3. Accepted as NA-25b: the facade dissolve, the reverse from end pages and the HQ side, and Grid/Route zoom reusing the dive.
14. **W1_NA11 layout rules: FIX LIST.** The 6-floor frontage, the 8 BU border streets, parity and the unchanged bids are all good. The deviations are accepted (splitmix64, layout-time spikes, stacked parts unchanged). Two visual problems:
   1. **The street canyon closed up.** In the AFTER canyon, the raised frontage plus the spikes make a near-solid wall. The sky and the beam are almost gone, and the skyline no longer breaks. The r2 rule asks for a varied silhouette, not uniformly tall walls. Fix:
      - cap spikes at 1.6× the backdrop median, not 2×;
      - keep spikes ≥ 30 BU apart;
      - leave the rest of the frontage at 6–10 floors, varied.
      - Target: in the canyon camera, visible sky ≥ 15 % of the frame, and R-HOR-1 / R-SIL-1 passing.
   2. **The HQ page landmark gets crowded.** A cluster of new tall black towers next to the Halcyon HQ competes with it. Spec 8.8 says landmarks lead and the city stays subordinate. Fix: within 2 lots of an HQ lot, no building may be taller than 0.6× the HQ landmark's top, and those buildings are exempt from spikes.
   - Re-send both rows after the fixes, together with NA-11b's r2 diff.

## Held 2026-10-19 (messaging pause after 10 sends)

15. **NA-ID: three contract fixes come first** (art-pass 3c3f9106, 12.0, AD 2026-10-19). Part of the low 12.2 / R-FOCUS-1 comes from the id pass, not the art.
   1. Ground is class 4, not hidden. A hidden ground turns into class 0 and enters the 12.2 background mask {0, 2}. On Meridian, that puts the bright gold road grid into the background median. Draw the ground layer as class 4.
   2. Ground-lying compound parts go to class 4, not class 1: the plaza carpet, the apron trims, the rails at grade (the yellow on the HQ sheet), via an `id_ground` group or by glb mesh role. This is likely most of Meridian's 1.01 at a 0.48 landmark share. Rebel Cell's MAINFRAME sign stays class 1.
   3. capture.json: 1-space indent, sorted keys, LF (NA-02 JSON), not tabs. Add `time` ("night" by default, "day" for day frames).
   - Then re-run hq_meridian, landmark_solace and city_grid; whatever still fails goes on the art list. City R-FOCUS-1 at 1.05 is probably real. Class 3 / 6 at 0 px and no class 5 on HQ frames: fine.

16. **W1_NA25b (@7b5b02c4): APPROVED once the 3 items below land; re-send only those frames.**
   - Good: the blotches are fixed at the cause (glint scaled by distance, no near-mirror at half look_blend), worst frame at 0.003. The reverse order (dive back, NIGHT_SKY switch, CRT, rain, untype) reads in that order. The dive waits for the view, at 24 ms p95.
   1. The "dive back" scrim, as you already know.
   2. The "HQ side: night switch" panel is a flat navy frame. If it's a true hold in motion, it is a dark frame, which contradicts "0 dark frames". Either it lasts 1 frame or less (then say so) or crossfade through it. Re-send the 3 frames around it.
   3. Reveal dissolve: it's too subtle to read mid-frame. Make the Bayer cell at least 2 px at 1080p (4x4 matrix) so the grain reads as a dissolve and not as noise, and capture one mid frame on a seed with 5 or more rooms in frame.
   - Q, Grid/Route zoom: use the short zoom-only beat set, about 1.2 s. A toggle the player uses often shouldn't replay 4.5 s. The full dive plays only on entry (jack in) and on the jack-out reverse. Space still skips both.

17. **W1_NA12 (@c32775a3): FIX LIST.** Good: the seeds give distinct cities, seed 7 stays fixed, the NA-11 rules and the async build run unchanged, there are no HQ overlaps, and the 15° site rotation works. The coast doesn't read yet:
   1. **Answer to the Q: flat dark sea isn't enough before W2.** In the whole-city views the sea can't be told apart from the off-map void, so all three seeds read as a slab on black. W2's HQ work needs a visible coast: the Tethys WATER LEVEL is campaign-wide (designer ruling), and Orbital and Meridian sit on the shore in A2. The minimum water look:
      - a water material distinct from the void: deep blue-black, a slow normal ripple, and smeared neon/sodium reflections from the shore lights;
      - a lit shoreline band, i.e. a sea-wall line in the street colour plus a thin bright edge 1-2 px at the Grid zoom;
      - piers where a road meets the water;
      - the off-map void darker than the sea, or fogged, so the edge of the land reads.
      No terrain or hills before W2.
   2. **A2 is a bay, not a straight sea side.** In design_A2_horseshoe_bay.md the Cell sits at the bay head and the city wraps a concave bay. "One side is sea" with a straight shoreline loses the A2 silhouette that the designer picked. Give the shoreline a concave bay toward the Cell, plus some per-seed noise. The rules for HQ placement on the coast belong to the design/build sessions, not art-pass, but the Tethys HQ has to touch the water.
   3. **Contract:** add the coast to city.json as an optional additive key, so it stays v1-compatible and the Blender city plates can render the same coast. Shape: `coast: {"sea_side": "N|E|S|W", "shoreline": [[i, j], ...] (cell coords, the land side on the left), "sea_cells": <count>}`. Readers ignore unknown keys. Log it in DECISIONS (schema-minimal). Leave seed 7 without the key, so the fixtures don't change.
   4. **Art list (mine, not blocking):** in the whole-city zoom the HQs don't read as landmarks. Same family as the city R-FOCUS-1 1.05 on the NA-ID frames.
   - Re-send: the whole-city view for seeds 1 and 2 with the water look, plus one Grid-page crop at the shoreline.
