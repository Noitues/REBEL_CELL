# Plan 2 B-MENU + C-SCREENS capture sheet (W0 MENUSHEET)

Sheet: `B_MENU_C_SCREENS.jpg`, one row per change, BEFORE (left, tree at `06eaeef7^`) | AFTER (right, main 6f5eac32+).
1920x1080, text 1.0, driven from fixtures. Script: `tools/design_lab/plan2_w0_menusheet_capture.gd`, sheet: `plan2_w0_menusheet_sheet.py`.
Findings only; nothing fixed.

## Panels
1. **C6 pause menu.** Netrun pause with Abandon Run (pink, "No Going Back") in the right column. AFTER: a blank gap under Abandon separates it from Quit to Main Menu / Quit to Desktop; BEFORE the three sit in one stack. Resume alone left.
2. **C7 New Campaign.** AFTER: locked tiles read "UNLOCKS · 60 SCHEMATICS" (price wraps to two lines, "SCHEMATICS" on the second), and the Target row carries "Unlocks cost Schematics (you hold 37), earned in a campaign." at its right end (fixture: 37 held). BEFORE: bare "UNLOCKS · 60".
3. **C8 loot pick toast.** Card picked from a card + firmware pair of offers. AFTER: toast "Taken: Twist, added to your deck." at the foot; the row also reads TAKEN: Twist (both trees). BEFORE: no toast.
4. **G14 socket confirm.** Barbed Wire into slot 5 holding Burner. AFTER: ConfirmDialog "Socket Barbed Wire into slot 5? It destroys Burner, already there." / "The old chip is destroyed. It cannot be undone." with KEEP and SOCKET IT. BEFORE: no dialog, the chip is taken at once (the panel shows the resulting page).
5. **C4 Heat tooltip.** Heat 12: AFTER "Next threshold at 20: An extra elite patrols the next netrun." BEFORE: "Next threshold at 20." Tooltip is the gauge's own custom tooltip placed by hand (native tooltips do not open in the quiet window).

Not shown: B-MENU raid-setup keys (Enter = START DEFENSE, Backspace = BACK): input only, covered by the unit test.

## Findings (none fixed)
- P1: the pause menu renders top-left, not centered, at 1920x1080 in this fixture (PauseMenu added full-rect to a plain Control; the live game's host may place it). Unverified in the real flow; worth a human look.
- P1: the dialog's second sentence repeats the first ("It destroys Burner" then "The old chip is destroyed"); the SOCKET IT / KEEP stickers sit tight on the panel's bottom edge; the dialog is a few px left of center (about 948 vs 960). The scrim blacks out the whole loot page.
- P2: the currency line is small grey caption text at the far right of the Target head, far from the locked tiles and easy to miss; no color cue that it is the currency.
- P2: the Heat tooltip text wraps ("netrun." alone on a line).
- P3 (fixture note): BEFORE panel 3 header says "CONTINUUM BILLING FARM", AFTER says "SITE": site naming differs between the trees, not part of this change.
- P3: toast is plain acid-edged mono text on the dim page; legible, no icon.
