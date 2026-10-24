# L17 UI: presentation only, from the L16 critic (main scene and board)

The rules are unchanged (L14). The view keeps every L16 behavior unless this spec changes it.

1. **An honest guard everywhere.**
   - Replace the bare "LOCKED" banner with the guard line: "HOLD → <tier glyph> TIER · best: <row glyph> <ROW> →
     <tier glyph> TIER". The best row is the row with the highest worst-tier, then the highest mean score. If no row
     beats HOLD, the line reads "HOLD → <tier> · no response changes this".
   - Show the guard line in PLAN (assuming HOLD) and in RESPONSE.
   - **The "worse than best row" confirm** fires whenever HOLD loses a HOME pip (on its worst outcome) that some
     visible row saves, at any HOME value.
   - **Fast resolve** happens only when every response row yields the same tier on every outcome. Otherwise the raid
     plays the full ladder.
2. **The forecast on the board.**
   - Hovering a forecast cell (A × B × hunter) or a response row draws that outcome on the city as a ghost overlay:
     - the beams it fires, as thin ghost lines;
     - the districts that go DOWN or TAKEN, as a ghost crumble tint;
     - the HOME pips lost, as ghost pips;
     - a large tier glyph over our HQ.
   - Clear the overlay on mouse exit.
   - Under `--auto`, show the overlay for the chosen row for 1 beat before LAUNCH, so the captures carry it.
3. **Intensity cards** show the net leg value as one large signed number, with small icons below it: captures (flag),
   income (coin) and Heat (flame).
4. **Card verbs on the board.** Placed SHIFT and JAM sentries show their verb glyph larger than a GUARD sentry does,
   so a held tool reads differently from a plain guard.
