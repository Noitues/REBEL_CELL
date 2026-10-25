# L16 UI: presentation only, from the L15 critic (main scene and board)

The rules are unchanged (L14). The view keeps every L15 behavior unless this spec changes it.

1. **LOCKED raids resolve fast.**
   - When the PLAN forecast is LOCKED (all 12 outcomes share a tier), LAUNCH plays the beams back to back at 2×
     speed. It skips the reveal pauses and the RESPONSE panel only when every response row is "changes nothing".
     Then it shows the aftermath stamp.
   - Show a "LOCKED: fast resolve" chip.
   - Unlocked raids keep the full reveal ladder at normal speed, and their reveal beats get a short hold so the
     reveal lands.
   - Shot names stay the same; skipped beats still emit their shot, as the fast frame.
2. **Glyph-first responses.**
   - Hovering or selecting a response row previews its effect on the board:
     - SACRIFICE: a shield dome on HOME and a cobalt crumble on the cell;
     - REDEPLOY: a ghost arrow from the source to the target;
     - DEPLOY: a ghost sentry dropping in;
     - JAM: a struck-out hound on the hunter lanes.
   - Each row leads with a large verb glyph before any text.
3. **Five distinct tier shapes** instead of heart variants: HOLDS = full shield, BATTERED = cracked shield, DAMAGED =
   broken heart, BREACHED = skull, EVADED = open eye.
   - Use the same glyphs everywhere: forecast, rows, stamps, the record and HOME glyphs.
   - Pin the tier ladder in the legend as glyph + one word, ordered best to worst.
4. **Response confirm.** When HOLD is selected, HOME ≤ 1, and some visible row has a strictly better worst tier, the
   launch asks "HOLD is worse than <row glyph>: launch anyway?".
5. **Price Heat where it is chosen.**
   - The intensity cards replace "HOLDABLE" with two numbers: the projected Heat penalty at leg end and the leg-value
     delta, from the rules' `score()` on the between state.
   - The three cards stay side by side.
6. **Give the board room.**
   - During playout phases (known beams to aftermath), collapse the side panel to a slim strip and fit the camera
     wider. Use `_fit_camera` with a larger viewport rect. Restore it at BETWEEN or PLAN.
   - At Heat ≥ 75, stacked sentries and markers on one district fan out, offset around the cell center.
7. **Readability.** Panel text is at least 14 px, with no truncation.
