# Plan 2 B-MENU + C-SCREENS capture sheet (W0 MENUSHEET)

Sheet: `B_MENU_C_SCREENS.jpg`, one row per change, BEFORE (left, tree at `06eaeef7^`) | AFTER (right, main 6f5eac32+).
1920x1080, text 1.0, driven from fixtures. Script: `tools/design_lab/plan2_w0_menusheet_capture.gd`, sheet: `plan2_w0_menusheet_sheet.py`.
W0 SCREENSFIX: AFTER is the fixed tree (BEFORE unchanged, cropped from the first sheet).

## Panels
1. **C6 pause menu.** Netrun pause with Abandon Run (pink, "No Going Back") in the right column. AFTER: a blank gap under Abandon separates it from Quit to Main Menu / Quit to Desktop; BEFORE the three sit in one stack. Resume alone left.
2. **C7 New Campaign.** AFTER: locked tiles read "UNLOCKS · 60 SCHEMATICS" (price wraps to two lines, "SCHEMATICS" on the second), and the Target row carries "Unlocks cost Schematics (you hold 37), earned in a campaign." at its right end (fixture: 37 held). BEFORE: bare "UNLOCKS · 60".
3. **C8 loot pick toast.** Card picked from a card + firmware pair of offers. AFTER: toast "Taken: Twist, added to your deck." at the foot; the row also reads TAKEN: Twist (both trees). BEFORE: no toast.
4. **G14 socket confirm.** Barbed Wire into slot 5 holding Burner. AFTER: ConfirmDialog "Socket Barbed Wire into slot 5? It destroys Burner, already there." / "The old chip is destroyed. It cannot be undone." with KEEP and SOCKET IT. BEFORE: no dialog, the chip is taken at once (the panel shows the resulting page).
5. **C4 Heat tooltip.** Heat 12: AFTER "Next threshold at 20: An extra elite patrols the next netrun." BEFORE: "Next threshold at 20." Tooltip is the gauge's own custom tooltip placed by hand (native tooltips do not open in the quiet window).

Not shown: B-MENU raid-setup keys (Enter = START DEFENSE, Backspace = BACK): input only, covered by the unit test.

## Findings (W0 SCREENSFIX)
- P1 pause menu top-left: **not a bug**, a capture fixture fault. The real flow (`NetrunScene.open_settings`, as HQ and combat do) centers it across and sets it under the subtitle band. The capture now drives `open_settings` on a started run; panel 1 AFTER shows it. Test: `test_pause_menu_real_flow_centered` (1920x1080).
- P1 socket confirm: **fixed**. One sentence names both chips (the second line is gone; the destructive panel's CANNOT UNDO tag stays). Stickers get a `StickerPad` row (`UiTheme.SP_M` x text scale) under them. The dialog was 8 px off center because its panel (544) was narrower than the dialog (560): the panel now takes the dialog's width, so centering the dialog centers the panel (measured 360..920 of 1280). The scrim dims the page less for dialogs (`Palette.SCRIM_DIALOG_ALPHA` 0.32 via `GlassScrim.backdrop_for(dim_alpha)`; the page is still blurred). Tests: `test_confirm_dialog_centered_with_sticker_padding` at 1920x1080 and 1280x720.
- P2 currency line: **fixed**. Body size (`UiTheme.BODY`) in the Schematics color (`StatIcon.color_of`).
- P2 Heat tooltip: **fixed**. The effect goes on its own line under "Next threshold at 20:" ("Next threshold at %d:" key replaces the one-line key).
- P3 toast icon: **fixed**. `ToastNote` takes an optional StatIcon kind; a loot pick shows the card / firmware / daemon glyph (`NetrunScene.taken_icon`).
- P3 site-name note (BEFORE "CONTINUUM BILLING FARM" vs "SITE"): not part of this change, unchanged.
