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

## Findings (W0 SCREENSFIX, with the art-pass review, ART_REPLIES item 9)
- C6 pause menu: **not a bug** for the position (fixture fault; the real flow `NetrunScene.open_settings` centers it, test `test_pause_menu_real_flow_centered`). Per the review: the gap under Abandon is now one SP_XXL (48 px) with a thin pink divider rule (`AbandonRule`) in it; Abandon keeps pink and "No Going Back".
- C7 tiles: **fixed**. "UNLOCKS · [Schematics icon] 60" on one line, word dropped (`TilePicker.ICON_SLOT` + tile `unlock_icon`). Currency line: **fixed**, its own row directly under TARGET, left-aligned, Schematics icon in the HUD color: "[icon] 37 held, earned in a campaign." (body size).
- C8 toast: **fixed**. Paper chip, ink words, the loot kind's glyph (card / firmware / daemon). The glyph is the kind's StatIcon (there is no per-card-type icon in StatIcon; a card's attack/defense type icon would need the card-type art: NEEDS-DECISION if wanted).
- G14 socket confirm: **fixed**. "Socket Barbed Wire into slot 5?" / "Burner is destroyed. This can't be undone." in one text style; both chips as icons, Barbed Wire -> Burner struck in HARM red; KEEP stays the default-focus sticker; SOCKET IT is a red-outlined terminal button; panel is as wide as the dialog (centered to the pixel, measured 360..920 of 1280); the scrim dims lighter for dialogs (`Palette.SCRIM_DIALOG_ALPHA`); room under the buttons (`StickerPad`, SP_M x scale = 16 px at 1.0). Tests at 1920x1080 and 1280x720.
- C4 Heat tooltip: **fixed** (widow). The effect goes on its own line under "Next threshold at 20:".
- Site headers ("LOOT // NETRUN: SITE", "T1 // SITE"): not touched; a separate slice changes the reward header (item 6).
