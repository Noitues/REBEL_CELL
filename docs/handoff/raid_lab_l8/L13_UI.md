# L13 UI: show the L13 rules, plus the L12 critic's presentation points (main scene and board only)

The rules are already in l8_rules.gd (see L13_RULES.md). The view only calls L8Rules.

## New rules on screen
1. **The hunter is a first-class threat with two sealed streets.**
   - In PLAN and FORECAST, both `hunter_cands` streets are drawn as dashed hound lanes with a pawprint glyph and a "?"
     badge. The hound stands between them.
   - **New beat, "HUNTER REVEAL",** after the sealed beam: one lane ignites and the other dissolves. Then the hound runs
     it.
   - The hunter gets its own row in the forecast panel and the launch list. Shot name: `rN_hunter_reveal`.
   - Calls go to `resolve`, `trace` and `hunter_line` with `hunt`. For the real line, use `raid.hunter_real`.
   - `forecast` now returns `outcomes[2]` per candidate. Show both, as "if hunter street A / if B" with the tier icons.
2. **SACRIFICE rows** in RESPONSE: "SACRIFICE <cell>: HOME is shielded this raid, <cell> is lost", with the result.
   - Hovering shows the cell crumbling to cobalt and a shield over our HQ.
   - Because the hunter is unknown at this point, every response row shows its result as a range over the two hunter
     streets: "HOLDS / DAMAGED".
3. **Intensity perks** on the cards, as a pictogram plus a short line:
   - NORMAL: "free repair" (wrench);
   - HOT: "2 captures next raid" (double flag);
   - LOW: none.
4. **Double CAPTURE.** When `extra_capture > 0`, CAPTURE runs twice ("Claim 2 of 2"). The golden `capture` is now a
   list, and `--auto` replays every entry.
5. **Score breakdown** shows the new Heat bands (50 / 75 penalties) and HOME at 15 each.

## L12 critic presentation points
6. **Graduated launch friction.**
   - Ask for a confirm whenever HOME drops on **every** candidate (any loss, not only a breach), or whenever HOME is
     at 1.
   - Always show the "One fix" line when one exists.
   - Replace "a response changes this" with the best response by mean over the hunter streets, for example "best
     response: JAM → HOLDS / HOLDS", or "no response saves this route".
7. **Wordless outcome layer.**
   - The per-route tier icons sit at each lane's corp-side entry and stay through the launch.
   - The three sealed candidates share a "?" glyph that collapses at the reveal.
   - Heat thresholds show as ghost beams on the corp tower: one ghost per extra beam the current Heat brings, and a
     faint one for the next threshold.
   - The DOWN countdown glyph stays.
8. **Panel text contrast.** Raise text sizes to at least 13 px and lift low-contrast grays. Nothing may clip.
