# Plan 1 wave 3 / 3b review sheets

Before = main @ 90088e64 (gate/PT-002), after = main @ 8727fd3c. Left | right, 1600 px wide, text 1.0, seed 1 (HQ sheet
seed 7). Made by `tools/design_lab/w3_sheets_capture.gd` (`--group=grid|route|hq|w3b`) through `run_windowed.py`, the same
script on both trees. No game code was changed.

## W3_GRID.jpg
1. HQ idle: reachable Sites tagged, orange ring on the next Site.
2. Locked Site (Pricing Memo Archive) hovered: "LOCKED: clear Continuum Billing Farm first (ringed on the map)", prerequisite double ring.
2b. Same Site selected: prerequisite stays ringed.
3. Runnable Site file at Heat 22: FLATLINE row "HEAT +11 -> 33 // RAID AT HEAT 30".
4. CORE card, Heat 0, 0 Schematics: Heat Scrub disabled with "SCRUB UNAVAILABLE: Heat is already 0".
5. GRID VIEW during a run.

Not captured: the RAID badge on a Site's gains row. No launchable Site on seed 1 crosses a raid line when cleared at any Heat
15-79 (the capture searched); the FLATLINE row's raid line (panel 3) stands for it.

## W3_ROUTE.jpg
1. Route map: pick prompt, disabled CONFIRM, corner badge shapes, key strip, operative file with AT LARGE.
2. Node 1 picked at HP 53/60: CONFIRM names it "(Enter)", node file "53 / 60 on arrival", HEALS line.
3. Pick prompt tooltip (map key). Panel 3 has no "before" (the tooltip is new).

## W3_HQ.jpg
1. All flatlined: FREE HIRE recover card, JACK IN disabled. 2. JACK IN tooltip. 3. CREW tab. 4. MARKET tab (before: counts "2/2", number on MARKET).
5. Three claimed Sites with a raid queued. 6. Raid-queued note in the foot band (staged: Heat set to 30 after the page was built).

## W3B.jpg
1. UNDO after Malware Drop: toast "UNDO is blocked: Malware Drop rolled a random result." 2. Q/E with no free nudge, 0 RAM: "No free nudge left, and an extra nudge costs 1 RAM." (tutorial overlay removed for the capture; see finding F7).

## Findings (nothing hidden, nothing fixed)
- F1 (GRID 2): the hover file card for the locked Site still carries a DECRYPTED stamp over its top, although W3-GRID says a locked Site's file loses it (the selected card does; the hover preview does not).
- F2 (GRID 2): the tooltip covers the ringed prerequisite's neighbors and half of the hover card; the double ring itself is hard to tell from the single orange ring at this size.
- F3 (GRID 3): the FLATLINE value wraps in three lines ("HEAT +11 ->" / "33 // RAID AT" / "HEAT 30"); the arrow is split from its total.
- F4 (GRID 4): the CORE card's text runs into the foot (the ticker line clips "you never run it."); title reads "HOME SERVER // HOME SERVER".
- F5 (GRID 5, likely real): GRID VIEW's camera does not frame the run path or the TARGET marker; only a yellow link stub is on screen top-left, so the path and target the legend line talks about cannot be seen. The map also gets no tags beyond Sites in view.
- F6 (ROUTE 1/2): the node file's DECRYPTED stamp touches the HEALS line at the bottom right; the key strip is legible, badges are small (about 10 px) but distinct in shape.
- F7 (W3B 2): with the tutorial box open, the nudge refusal toast sits behind the box (only its last line shows under it). Outside the tutorial it is clear.
- F8 (HQ 5): the CLAIMED stamps no longer overlap each other but are faint and partly under the red raid pencil; with the INTERCEPTED toast holding the foot, the Heat note falls back to the top left and covers the work order's header.
- F9 (HQ 6): the foot-band note overlaps the left end of the ON AIR line (covers "ON AIR" text).
