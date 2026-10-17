DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01Pwhsr37qaTLGweKcvA9Ree, custom_id vis__summary; status ok; tokens in 28524 cache-write 60174 cache-read 0 out 4227; cost $0.125 -->

# Vision review: cross-corp summary

Sources: the six per-corp vision reviews (Halcyon, Orbital, Rebel Cell, Solace, Meridian, Tethys). All luma figures in them are by-eye estimates from downscaled frames and are uncertain; nothing here is measured. Aurelian has no review document. The "seven HQs" in the brief are Halcyon, Meridian, Orbital, Solace, Rebel Cell, Aurelian and Tethys, of which six are covered here.

## Patterns

| # | Rule | Corps affected | How often | Shared-kit fix |
|---|---|---|---|---|
| P1 | Landmark does not lead its ring (8.3, 12.2, R-FOCUS-1, `landmark.lead`) | Halcyon, Solace, Meridian, Tethys, Rebel Cell; Orbital judged plausibly OK | 5 of 6 (reviewers estimate under 1.5 or doubtful; none measured) | Add a shared landmark-light stage in `hq/scene`: rim, cornice cove and uplight lights on the landmark layer, keyed to hit 1.5-2.0x. Run 12.2 from the object-index pass on every plate so the estimates become numbers. |
| P2 | Even window carpet, no quiet apron or dark blocks (13.1 rank 3, `density.falloff`, R-CALM-1/2) | Halcyon, Orbital, Solace, Meridian, Tethys | 5 of 6 (the Rebel Cell review does not raise it, and HIGH variance is intended there) | Implement `density.falloff` once in `hq.downtown` / the zoned-city dress step: `near_k` 0.25 at the compound edge, `dark_block_share` 0.2, buildings kept (8.2, C6). |
| P3 | District hue not carried by the fabric (13.1 rank 5, `palette.districts`, 3.4) | Halcyon (not violet-grey), Orbital (warm and rainbow, not ice blue), Solace (warm amber, no green), Meridian (magenta and violet dilute orange), Tethys (near-monochrome teal; Tethys frames read teal, 3.4 gives blue) | 5 of 6 | Drive bank glows, trims and window tint from the 3.4 `lang` hue table plus the `district_weights` blend (3.5b), so the neon_bay magenta/cyan defaults do not leak into corp districts. |
| P4 | Value band likely off (12.1, `values.solve`) | OVERVIEW: Halcyon, Rebel Cell, Meridian bright; Orbital, Tethys dark. DECISION: Rebel Cell bright; Meridian and Solace possibly dark. | All 6, but in both directions and all uncertain | Run the exposure solve after the vignette (13.1 rank 10) and write R-VAL-1/2/3 into `checks_<run>.json` for every plate. Do not tune by eye. |
| P5 | Hero signage on route columns missing or unreadable (9.1, `dressing.signs`) | Halcyon, Orbital, Rebel Cell, Meridian, Tethys, Solace (floating bars not on faces) | 6 of 6 | One shared `dressing.signs` pass for HQ views: a hero sign per route column in the district hue pair, and every sign anchored to a building face. Tethys may need an underwater variant (Q in its review). |
| P6 | Hover power cut deviates from 9.4 | Orbital (far harsher, near black), Meridian (harsher than x 0.20), Halcyon (pyramid body not cut), Rebel Cell (weaker: signage still saturated, branch not x 1.35), Solace (two bright branches competing) | 5 of 6 | One 2D grade pass with the four presets (`cut_level` 0.20, `cut_desat` 0.70, `branch_boost` 1.35, `type_glow` 1.0) and a branch mask. Remove any residual 3D cut (9.4 rule 3); the Orbital reviewer asks whether both are applied. Include emissive signs in the desaturation. |
| P7 | Foreground clutter near the decision set not stubbed or ghosted (7.1) | Halcyon, Meridian (left wall mass), Orbital and Rebel Cell (uncertain), Tethys (dam, uncertain) | 3 to 5, mostly uncertain | Check that `occlusion_state` is wired in every HQ job (including the new landmark plugins), and add an automatic check that foreground tops are cut or ghosted. |
| P8 | Pencil or label collisions (9.2, `CLEAR_PAD`, Art Bible 1.2) | Orbital (TARGET line through the ANTENNA ELITE room), Halcyon (CLIMB chip on a dashed path), Meridian (tooltip on the pencil, lime spikes), Solace (caption overflow), Rebel Cell (TARGET label cut at the edge), Tethys (thin pencil, tiny label, TEST caption) | 6 of 6 | Extend the "Wax clear of stickers and UI" check in 12.6 to labels, tags and TARGET words, and add a text-fit check for caption cards. |
| P9 | Beams read as rods (4.1, 12.5) | Halcyon (streak and apex shaft); the others do not mention beams | 1 (Tethys notes only a faint plume) | Run the 12.5 config and image checks on HQ plates. |
| P10 | TARGET edge arrow absent when the TARGET is off-screen (9.5b) | Rebel Cell, Meridian (both DECISION and HOVER) | 2 | Both reviewers are unsure whether the arrow is a Godot overlay absent from renders by design. See Q below. |

## Outliers

- **Tethys:** only an OVERVIEW and a test closeup (with a TEST caption) were reviewed, with no DECISION or HOVER. The reviewer judges the nodes as identical dots with no stickers or kind colors, which breaks 9.3. This reads as an earlier stage than the other five. It also has no row in the 6.4 camera table, and an unexplained "ATLANTIS STATION" label.
- **Rebel Cell:** the only corp where the reviewer reports the DECISION camera as a 3/4 elevated view, against the spec's side view at yaw 0 (6.4). It is also the one corp whose cut is weaker than spec, not harsher, and the only one with a strong street-level foreground (road, streaks, lamps), though with some dead space under it.
- **Orbital:** the only corp with a "too dark" HOVER, near x 0.05-0.10. Its identity holds in OVERVIEW (rocket, silo, ring) but the rocket is missing in DECISION. It also has an unexplained pink dome and a black rectangle in DECISION.
- **Meridian:** the reviewer finds no crane keep, moat, freight viaduct or rail yard in any frame. No other review reports a whole landmark mechanic missing.
- **Halcyon:** the pyramid body is cyan-white, not violet. The eye turret and amber rim are not clearly visible.

## Set coherence

- **Contradiction on pitch:** the Halcyon reviewer says the OVERVIEW pitch looks steeper than 26 deg and asks to confirm. The Orbital reviewer says its roughly 45-50 deg matches the spec's 46. These are different corps with different spec values, so not a conflict, but the Halcyon pitch is open.
- **Contradiction on dark vs bright city:** Halcyon, Rebel Cell and Meridian OVERVIEW are judged bright; Orbital and Tethys OVERVIEW dark. All uncertain. A shared exposure solve would settle this.
- **Shared strengths:** the UI chrome, pencil state colors (lime walked, orange option, white ahead, red TARGET) and the legend are consistent across corps. Each reviewer finds the route and TARGET readable in at least some frames.
- **Corp identity** rests mostly on landmark silhouette and UI text, not on district hue or fabric. Reviewers say Halcyon, Solace, Meridian and Rebel Cell frames could read as a generic neon city without the labels. Only Tethys's silhouette is called unmistakable. Halcyon and Tethys could be confused at thumbnail size, per the Tethys reviewer, though water and dam rule that out.
- **One city:** the same base fabric (warm window dots plus magenta/cyan/yellow dashes) appears behind most corps. That is consistent with one continuous city, but it means the per-district hue (3.4) is not yet visible. As reviewed, the seven would sit in one city mainly because they share one generic fabric, not because of designed district transitions.
- **Missing frames:** Tethys has no DECISION or HOVER final. Aurelian has no frames and no review at all, and its HQ needs a design pass first (8.7 rule 5). Its landmark cannot be checked against 8.6b. The 12.2 and R-FOCUS-1 gates and the camera table cannot be completed without them.

## Top 5 findings

1. **BLOCKER (Tethys, Aurelian):** no DECISION or HOVER for Tethys and no frames for Aurelian, so 6.4, 7.1 and 9.4 cannot be accepted for two of seven corps. Also Solace: its district color identity is absent from the surrounding city, which the reviewer rates a blocker.
2. **MAJOR (5 corps):** landmark does not clearly lead its surroundings (12.2, R-FOCUS-1); all estimates by eye.
3. **MAJOR (5 corps):** even window carpet with no apron (`density.falloff`) and district hue not carried by the fabric (`palette.districts`).
4. **MAJOR (Orbital, Meridian, Halcyon, Rebel Cell, Solace):** hover power cut off-spec in both directions (9.4); the Orbital reviewer suspects a double 3D plus 2D cut.
5. **MAJOR (Meridian, Rebel Cell):** landmark identity missing or clipped (Meridian crane, moat and viaduct absent; Rebel Cell MAINFRAME sign and fist cropped). Rebel Cell also has the target off-screen with no 9.5b arrow and a DECISION camera that does not match 6.4.

## Recommended order of fixes

1. **Measure first:** run 12.1, 12.2 and the 12.7 composition checks on all existing plates. Most findings above are by-eye and some (value band, ratio) may change sign.
2. **Shared kit:** the single 2D hover grade (9.4) with the 3D cut removed; one `values.solve` after the vignette; the district hue source for glows and trims (3.4, 3.5b); `density.falloff` in the downtown / zoned-city dress step.
3. **Shared kit:** the landmark light stage (rim, cove, uplight) and the 12.2 check wired to the object-index pass; the `dressing.signs` HQ pass with every sign on a face.
4. **Shared kit:** extend the 12.6 wax-clear check to labels and captions; confirm the occlusion helper runs for every landmark plugin.
5. **Per corp:** Solace hue and DECISION centering; Meridian landmark elements from `zoned.json` (rail, moat, crane); Rebel Cell sign framing and camera; Orbital pencil routing; Halcyon hue and eye.
6. **Missing frames:** build Tethys DECISION and HOVER (add its 6.4 row) and start the Aurelian design pass.

Q: Does Godot draw the 9.5b TARGET edge arrow as an overlay, so its absence in Meridian and Rebel Cell renders is by design? (build session)
Q: Is the Rebel Cell DECISION still the side view at yaw 0 (6.4), or has the 3/4 view replaced it? (designer)
Q: Is the Halcyon pyramid meant to be cyan-white, or violet per Art Bible 2.4? (art director)
Q: Tethys hue: the 3.4 blue (0.184, 0.42, 1.0) or the teal in the frames? And is "ATLANTIS STATION" a leftover label? (art director)
Q: Are the Orbital pink dome and the black rectangle in DECISION intended elements? (art director)
