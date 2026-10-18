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
