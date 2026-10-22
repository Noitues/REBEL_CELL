# REVIEW: M10 MANHUNT r10 (sweep raid), fresh critic

**Verdict: 28/50. Clean core idea (Invisible Inc. guard vision on a 4x3 asset grid), but the frames hide the third beam, drop two lever costs from the ledger, mix two currencies, and add a timing press the GDD pillars rule out. It scores below every shipped reference.**

## Scores

| Axis | Score | One-line reason |
|---|---|---|
| W what/why/when | 6 | The contact icon chain (checks, flame, shield, network) explains why the raid comes. Beam 3, the hunter, is never drawn on the grid, so "when does what" is only half shown. |
| P predictability | 6 | Beam 1 is drawn in full and each sealed line gets a thumbnail, which is good guard-vision practice. But the thumbnails ignore beam 3, the risk bar hatches all 19 instead of marking 0-18, and the spoof's outcome depends on a dexterity press. |
| N no-words | 4 | Scrambled, I could read assets, values, beams, the Heat bar, the -8 and 19 -> 11. I could not read the lever costs and counts, the hunter, the contact chain, or which sealed line was picked until frame 4 (see below). |
| D decision depth | 6 | Four levers in three currencies, a decoy that blocks two lines at once, and holding the spoof wins only 60% (so it is a real choice, not a dominant one). But it is a 6-asset, 3-line puzzle that a player solves in about 20 seconds, and the spoof is a single press. |
| C consequences | 6 | DOWN plus wrench, with repair taken off the key, is persistent and motivating. But the ghost (+5 Heat) and decoy (-3) are never charged, the coin icon is charged against a hexagon bar, and EVADED "+6" has no unit. |
| **Total** | **28/50** | |
| S suspense | 6 | The reveal changes the result on 53% of networks, and the press window is a real held breath. But it happens once per raid; beam 3 never visibly plays, so the 3-beam sequence ends early. |
| V visuals | as shown 4 / information layout 5 | Clean low-fi lines. The legend panel jumps to three positions over five frames. The forecast thumbnails sit away from the grid they describe, so you must read thumbnail, then legend, then grid. ITB and Invisible paint threat on the tiles themselves. |
| Fit to premise | 6 | Hackers ghosting, decoying and spoofing a corp sweep fits the theme well. But (a) the abstract 4x3 grid is not the City Grid network or its links (GDD 3.1: raids travel along links), and (b) the timing press breaks Pillar 4, "Raids are deterministic graph auto-battles with a planning phase". |

## Against the six shipped systems (same rubric)

ITB 45 > StS 42 > Invisible 39 > FTL 35 > Kingdom Rush 33 > TFT 31 > **Manhunt 28**.

- Its closest relative is Invisible Inc.'s guard sweep: sealed lines work like guard patrols with uncertainty, and ghost/decoy work like stealth tools. It loses about 11 points there. Invisible paints cones and the alarm on the world, while this concept moves the forecast into side thumbnails (P, N). Invisible's levers also chain across many turns, while this is one shot (D).
- It beats TFT on P and on suspense-per-decision. It loses on C (TFT's HP loss is one clean number; here three costs are shown inconsistently) and on N.
- Its suspense (6) sits under FTL, Invisible, KR and TFT (8-9), because the playout is one reveal plus one press.
- Side-by-side sheet: `side_by_side.png`. ITB numbers the attack order on the tiles; Invisible draws guard vision and the alarm on the map; MotN's light cone reads as "seen" with no words. Manhunt's dashed beams come close to the MotN read. Its forecast does not come close to ITB's in-place telegraph.

Reference URLs (images only, Steam store screenshots, saved in refs/; urls.txt lists all 12):
- Into the Breach: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/590380/ss_4b985c7747c1ff0b7fbbf3eaf8ca5a1272f0dadb.1920x1080.jpg
- Invisible Inc.: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/243970/ss_5bc3599a1531d384933c93e2cc8f5df464ce9bec.1920x1080.jpg
- Mark of the Ninja: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/214560/ss_152fb144da101f023f0440b2755b0a9f9e3847ce.1920x1080.jpg

## The 3 changes that would raise it most

1. **Draw the hunter, and make the forecast the whole sweep (about +4: W, P, N, S).** As soon as the plan creates a "first find", draw beam 3's turn on the grid: here the decoy in column 4 sends the hunter down column 4. That one line also explains why the 8 in column 4 is ghosted. Without it, the example plan looks like +5 Heat wasted, because the decoy already blocks beam 1 below that 8. Each thumbnail should show the result of all three beams under that sealed line, not just beam 2's hits. Number the beams' order on the grid the way ITB does, and play beam 3 in the playout (the BEAM counter stops at 2/3 and never shows 3/3). No rule change.
2. **One ledger, one currency, charged when you place a lever (about +3: C, N).** Ghost: Heat 52 -> 57 in frame 2, shown on the bar. Decoy: key 19 -> 16 in frame 2. Show the repair in hexagons, not coins, so the end state reads 16 -> 8 (or whatever the rules say). Mark the 0-18 risk as a bracket on the key bar (from 19 down to 1), not hatching over the whole bar. Give EVADED's +6 an icon. **Designer decision:** the spec's "repair = asset value, taken off the key" conflicts with GDD 3.3 (repair = 50% of install cost, in Schematics), and the "key in Schematics" conflicts with GDD 1.3 (win = enough Exploits). Rule on one of each and make the frames follow it.
3. **Make the spoof a deterministic post-reveal choice, not a timing press (about +2: P, Fit, D). Designer decision.** Pillar 4 says raids are deterministic auto-battles with a planning phase, and Pillar 1 keeps the skill press in wheel combat. Keep the strong part: you spend it after the reveal. Make it "after the reveal, pick one node this beam skips", and add a second decision point (for example, the hunter's column is chosen after beam 2 resolves, so the spoof can pull the hunter). If the press stays, the frame must show the cursor and where it lands. Right now the teal window has nothing moving through it.

## What the scrambled frames failed to communicate

- **Contact chain (frame 1):** four checks -> flame -> shield -> square reads as "4 done, then heat, then defense, then slot". The "network = your haul" link is not readable, and there are 4 checks but 6 assets.
- **Lever legend:** "+5 flame" and "-3 coin" read as costs. "x0" under the crossed-out income icon reads as an effect ("income x0"), while "x1" under the spoof reads as a count. The same notation carries two meanings. I could not tell which levers are 1-use and which are unlimited.
- **Beam 3:** a red ring with a "3" token and a down arrow, floating off-grid to the right. I read it as "something lost or voided", not "hunter that follows the first find". It never appears again.
- **Sealed lines:** I could not tell the three dashed lines were alternatives, not simultaneous beams, until frame 4 dims two of them. The end shapes (diamond, triangle, square) carry the meaning, but nothing says "only one of these".
- **Forecast thumbnails:** I matched them to the end shapes, but they are tiny. Red dots on the 4-dot rows need counting against the main grid to find which asset they mean.
- **Hatched bar:** I could not tell it was a range at risk; it reads as "all 19 at risk".
- **Playout:** the teal ring on the 10 read as "protected". The teal window bar reads as "timing", but with no cursor I could not see when to press. The 1x/2x/4x buttons read.
- **Aftermath:** the stamp reads as a verdict by shape and color, and "1 xxxx" reads as "1 something". The red X with wrench on the 8 and the matching -8 and 19 -> 11 were the clearest thing in the set.

## Ledger and consistency errors between frames

1. **Heat never charges the ghost:** 52 in all five frames, though the ghost (+5) is placed from frame 2 on. It should read 57.
2. **The key never charges the decoy:** 19/25 through frames 2-4, then 19 -> 11 (-8 repair only). Correct would be 19 -> 16 -> 8, or the decoy price is wrong.
3. **Currency mix:** the repair is shown as "coin -8" but taken off the hexagon (Schematics) bar. The decoy is also priced in coins (-3) against nothing visible. Asset values are coins, the key is hexagons, and the two are never converted.
4. **Beam 2 arrowhead:** in frame 4 it runs through the 10 to the top edge, which is correct, since the spoof made it skip the 10. In frame 5 the arrow ends at the 10, which implies the beam stopped on (found) the 10.
5. **Beam 3 is absent:** the progress bar is at 2/3 in frame 4, and the aftermath shows only beams 1 and 2. Per the spec, the hunter should sweep column 4, find nothing (decoy, then ghosted 8), and that should be shown to justify the ghost.
6. **The example plan looks redundant:** the decoy in column 4 row 2 stops beam 1 (from the bottom) before the ghosted 8 in column 4 row 1. With beam 3 hidden, the ghost looks like 5 Heat spent for nothing.
7. **Contact count:** 4 checkmarks against 6 assets on the grid.
8. **Legend panel position:** top-right (frame 2) -> lower-middle (frame 3) -> top-right (frame 4) -> lower-right (frame 5). The aftermath relabels the spoof's x1 to x0 (correct) and greys the go-dark x0, which already read x0 in frame 2.
9. **Forecast check:** triangle = 10 + 8 = 18, square = 0 (decoy blocks), diamond = 4, so the 0-18 range in the caption is correct. Only the bar's drawing is wrong.

Files: `REVIEW.md`, `side_by_side.png`, `refs/` (12 Steam screenshots plus urls.txt), `scripts/` (fetch_refs.py, refgrid.py, sidebyside.py).
