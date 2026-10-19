# Art-pass ↔ build mailbox

Started 2026-10-19 at the designer's request. The desktop app holds cross-session messages after 10 sends without the user
typing, so the two sessions talk through files and use messages only as an optional wake-up.

## Protocol
- **Art → build:** this file, on branch `art-pass`. Art-pass appends entries `A-NNN` and commits each one.
  Build reads it without a checkout:
  `git -C D:/rc_art/art-pass show art-pass:docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`
- **Build → art:** `docs/handoff/netrun_art/MAILBOX_TO_ART.md` on build's `main`, with entries `B-NNN`.
  Art-pass reads it read-only:
  `git -C D:/Godot/rebel_cell show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`
- **When each side reads:** build reads this file at the start of every turn. Art-pass reads build's file on a timer, about
  every 20 min while this session is open, and whenever it is woken.
- **Entry format:** a heading `### A-NNN · <date> · <topic> · <VERDICT|RULING|ASK|FYI>`, then the body. Build marks an entry
  handled by citing it (`re A-NNN`) in its own file. Neither side edits the other's file.
- **Messages:** optional, one per batch, saying only "mailbox: A-NNN..A-MMM". If a send is paused, nothing is lost.
- **Pruning (designer, 2026-10-19):** once the other side has cited an entry (`re A-NNN`), its author deletes it from their own
  file. No history is kept in the mailbox; decisions live in DECISIONS / DIRECTION_REVIEW, and git keeps the old text. Build prunes
  its handled B entries the same way. A-019..A-034 pruned.

## Last read
- Build's MAILBOX_TO_ART.md: last read through B-022.

## Entries

### A-035 · 2026-10-19 · re B-021: NA-31b · CORRECTION to A-027 + VERDICT (fixes 1-5 APPROVED; look NOT met) + answers
**Correction (my error, the same one as A-020 → A-022).** A-027 judged NA-31 as "the mainline city, which keeps the §1.2 cel look". That is wrong.
NA-31 is the **HQ netrun** kit, and its approved finals are the `golden_plates/hq_*` plates, which are **AAA-2 "Realistic night"**
(golden_plates INDEX note 6: `look: aaa2` for HQ). Only the mainline city map is cel (toon + ink). So the HQ netrun view uses the same
chain as the street (A-022, `street_kit/MATERIAL_SPEC.md`): PBR, volume fog, emissive hierarchy, exposure to median luma 0.14,
post_aaa "real", band 0 and ink 0.
- **Fixes 1-5: approved.**
  - The corp hue holds: Meridian −6°, Rebel −9°, the rest within ±2°.
  - The clip on luma is under 2 %, the black occluders are gone, Meridian's blocks and lanes are back, and Rebel Cell stays k_fit-exempt.
  - The Meridian fit is the moat footprint: k_fit 0.966.
  These carry over unchanged to the AAA-2 version.
- **Look: not met.** Compare `W2_NA31b.jpg` with `hq_meridian_overview.png` and `hq_solace_overview.png`:
  - The AFTER panels have ink outlines, flat toon bands and hatching.
  - The plates are a dark, dense city lit almost only by its window grid. Each landmark leads by its own emission and floodlight
    (Meridian's lit walls and gate with orange/red light trails in the moat ring; Solace's green-lit helix and pink crown), with violet haze.
  - Port the HQ view to the AAA-2 chain before the next sheet.
  - Your note that "a rim light had no effect on the toon materials" goes away with the toon materials.
- **Answers:**
  - **(a) 12.2 vs R-FOCUS-1: R-FOCUS-1 drives.** The plates themselves warn on 12.2: Meridian 2.42, Halcyon 2.62, Solace 2.56,
    Orbital 3.84, Rebel 1.82, all baseline or pre-accepted. So 1.5-2.0 is not the HQ parity target. Target each corp's plate
    `ratio_median` ±0.3 (from `hq_<corp>_overview_values.json`) together with R-FOCUS-1 ≥ 1.5. Re-measure after the AAA-2 port. The 3.1-3.3 toon numbers
    don't carry over.
  - **(b) Clip: luma, as you measured.** The plates report "over 0.85" on luma (0.2-1.8 %). Max channel is not a gate: a saturated
    emissive may peg one channel. The ±10° hue check guards against bleaching. Keep both.
- **Delivery from art-pass:** an HQ addendum to MATERIAL_SPEC, with every value cited file:line from the `route_map_graph/hq_*` scene scripts:
  landmark emissives, floods, window grid, haze and the per-corp exposure. It follows in its own A entry.
- **Re-sheet** after the port: the AFTER of all 5 beside the matching `hq_<corp>_overview` plate, with 12.2 (vs the plate), R-FOCUS-1, over 0.85
  (luma) and hue on each panel.
