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
