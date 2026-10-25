# L15 UI: presentation only, from the L14 critic (main scene and board)

The rules are unchanged (L14). The view only calls L8Rules, and it keeps every L14 behavior unless this spec changes it.

1. **Inline response results.**
   - Every response row shows its worst and best tier glyphs inline over the remaining (B, hunter) outcomes. Compute
     them with `resolve`; never require a hover.
   - Rows with identical outcomes merge into one row, "×N variants". Hovering expands it.
   - Rows whose mean score beats HOLD sort first and get a free gold edge. The gold edge marks "better than doing
     nothing", not "the best".
   - SCAN is removed from the view; `buy_hint` stays in the rules but is unused.
   - The list must fit without paging: at most 8 visible groups, plus a "more" fold.
2. **LOCKED raids.**
   - In PLAN, when all 12 forecast outcomes share one tier, the forecast reads "LOCKED: <tier glyph> <TIER>".
   - In RESPONSE, a paid row (+2 Heat) that does not change any outcome versus HOLD is greyed and marked "changes
     nothing". It can still be clicked.
3. **Ghosted rows with a reason.**
   - When DEPLOY or REDEPLOY is impossible, show one ghost row per kind with the reason. For example: "DEPLOY: no
     free district", "REDEPLOY: no SHIFT card in hand", "JAM: no JAM card in hand".
4. **The launch confirm** must trigger whenever HOME drops on every one of the 12 outcomes (HOME damaged or
   breached), and whenever HOME is at 1. L14 missed this in raids 1–2 of the breach run, so check the condition
   against `forecast()`.
5. **No truncation.**
   - Forecast cells use glyphs: HOME heart / broken heart / skull, cell count.
   - Panel lines wrap instead of ending in "…".
   - Widen the panel or shrink the font to 13 px minimum.
6. **Board clarity in playout.**
   - DONE beams dim to 25% alpha and thin lines.
   - The current beam is full strength.
   - Block markers and hit numbers are drawn only for the current beam, plus a small persistent X per hit cell.
   - Hunter candidate streets fade once the hunter is revealed.
7. **Cards, wordless.**
   - The verb glyph is the dominant symbol at card size (shield / curved arrow / zigzag).
   - The type shape becomes a corner badge in the type color.
   - A wound is a cracked card with a red X.
8. **The between screen, wordless.**
   - The intensity cards show their trade as icons: flame +N (Heat), coin +N (bank), flag + (extra capture),
     wrench (free repair).
   - The leg-value delta appears on all three cards side by side, not only the selected one.
   - Build and clean show as card icons with their price as coins.
9. **The Heat bar at 50 and 75** carries two small icons per tick: a beam ("+1 beam") and a card ("+1 card").
10. **Route outcome at HOME.** During PLAN, each route's lane end at HOME shows that route's worst tier glyph.
