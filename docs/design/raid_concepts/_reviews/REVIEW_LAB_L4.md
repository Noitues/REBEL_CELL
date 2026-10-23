# REVIEW: Sweep-raid lab L4 (fresh critic)

**Verdict: 33/50 (S 4, V 4, Fit 6). It ties Kingdom Rush and sits just under FTL. The presentation is now strong: what is happening, why, and what will happen is clear on every beat. The score is held down by the rules. The planned line takes the same flat damage tax every raid, the one live mid-raid decision is usually empty, and a lost campaign is settled before the last raid begins, with no warning at the point where it could still have been avoided.**

Material judged: `shots_scrambled/` (leg 5, read first, notes kept in `scripts/scrambled_notes.txt`), `shots/` (leg 0 planned), `shots_breach/` (leg 0 naive), `shots_breachfix_demo/`, `LAB_README.md`. Contact sheets: `sheets/`. Side-by-side sheets: `refs/side_by_side_itb_vs_lab.png`, `refs/side_by_side_invisible_vs_lab.png`, `refs/side_by_side_scrambled_vs_plain.png`.

## Scores

| Axis | Score | Reason |
|---|---|---|
| W what / why / when | 8 | Every beat is named (sweep timeline 1 / + / 2 / 3, "BEAM 2 UNSEALS", "THE HUNTER TURNS"). The touch log and aftermath ledger explain every number. The cost is too many accounting figures (bank, assets kept, "was N", leg value, Heat carried, score). |
| P predictability | 8 | The per-shape forecast with the hold vs best-spoof result, the "worst:" line, the Heat-band chain, intensity cards that show next Heat and beams, and a breach warning that names a lever. It loses points because nothing projects past the current raid (P1-3). |
| N no words | 6 | From the scrambled run alone I read the grid, assets and values, HOME pips, the Heat bar with its two lines, the beams, the sealed-line candidates, levers changing paths, the forecast as a table per shape, the tier stamps and the repair costs. I could not read what go dark and the black disc do, the hunter's targeting, the score, or the struck-out chip. |
| D decision depth | 5 | Planning is real but small: 1 ghost, up to 2 decoys and 1 go dark on about 10 cells. The spoof is empty in 2 of 3 raids. Between raids it is always "repair all, no buy, pick LOW/NORMAL". The line feels solved. |
| C persistence | 6 | HOME integrity, Heat ratchet, kit depletion and campaign loss all carry forward. Asset damage is wiped by repair every interval, so the main visible harm does not last. |
| **Total** | **33/50** | |
| S suspense | 4 | The forecast already shows the range, the reveal picks one of three known rows, and the playout is hands-off. The breach raid is a foregone conclusion. |
| V visuals | 4 | Clean, consistent placeholder vector work with a disciplined palette. Beams stack and crowd once three of them are on the grid. No motion beyond pulses. |
| Fit | 6 | Fits a cyberpunk "cell under sweep" fantasy and the roguelite campaign stakes. Against a deckbuilder core, the raid adds bookkeeping more than drama. |

## Placement

| Game | /50 | S | V |
|---|---|---|---|
| Into the Breach | 45 | 5 | 8 |
| Slay the Spire | 42 | 6 | 7 |
| Invisible, Inc. | 39 | 9 | 7 |
| FTL | 35 | 8 | 7 |
| **Lab L4** | **33** | **4** | **4** |
| Kingdom Rush | 33 | 8 | 8 |
| Teamfight Tactics | 31 | 8 | 7 |

- **Against Kingdom Rush (tie) and TFT:** the lab wins on W and P. It shows exact outcomes before you commit, which neither of them does. It loses badly on S and V, and on D against TFT's economy.
- **Against FTL (+2 above):** FTL wins on D (many small trade-offs every jump), C (hull and crew loss stick) and S. The lab wins on P.
- **Against Invisible, Inc.:** this is the closest thematic neighbor (a corp sweep and a cell under alarm). Invisible wins on N (vision cones and alarm on the board), D and above all S, because its alarm escalates under your choices. See `refs/side_by_side_invisible_vs_lab.png`. Invisible puts the threat in the world, while the lab's decision panel offers five identical "x4" rows.
- **Against Into the Breach:** the lab copies the right idea, a telegraphed threat with exact results. ITB draws the threat on the tile and gives you more levers than threats, so every turn is a puzzle with a clean solution. The lab's kit is smaller than the beam count, so the "solution" is choosing what to lose. See `refs/side_by_side_itb_vs_lab.png`.

## Scrambled run: what came through and what did not

Read before any other material (leg 5, `shots_scrambled/`).

**Came through without words:**
- A 4x3 network of valued assets (yellow coin rings with numbers), and HOME as the server box with 3 pips (`01_r1_plan_empty`).
- A Heat bar with two thresholds that add beams. The contact screen's chip chain (`15_r2_contact`) shows "+" then "++" beams. The Heat climb 44 -> 51 -> 69 -> 74 is easy to follow.
- Numbered beams. The "?" beam has three candidate end shapes and resolves to one (`05_r1_unseal`, `21_r2_unseal`). The curved arrow reads as "this one turns".
- Placing a lever changes the beam drawing. The diamond stops beams (`17_r2_plan_levers`). The dashed ring adds Heat (+5 next to the bar, `02_r1_plan_levers`).
- The forecast is a per-shape table with outcome chips and an "after" column (`03_r1_forecast`, `18_r2_forecast`). A red-struck HOME pip in the forecast means a HOME hit (`34_r3_forecast`).
- The mid-raid decision is a card with per-option outcomes and a hold key (`06_r1_decision`, `22_r2_decision`).
- Outcome by stamp color: the teal r1 stamp and the grey r2/r3 stamps differ. A lightning bolt on a node means it is lost. The between screen shows a repair cost and a check (`29_r2_between_repairs`).
- The three intensity cards trade Heat against coins at three levels (`12_r1_between_open`).
- The record screen shows mini-grids with red frames on the cells that changed (`42_record`).

**Did not come through:**
- What the black disc (go dark) does, or why a struck-out chip sits above a node (`02_r1_plan_levers`, the node at (4,2)).
- What makes the hunter choose its column. The red target ring in `25_r2_hunter_turn` lands on the decoy, but the rule is not visible.
- Whether the skip-chevrons are a cost or a save.
- What the 48 under the top-right label means, and how the record's bottom-line formula is built.
- The difference between the two grey stamps "X 1 NLYL" and "X o wphst asse wjm mxzf": both are neutral grey, so a different-meaning outcome looks the same.
- Leg 5 raid 3 has no decision frame at all (no spoof left). Without words that reads as "the game skipped a step", not "you are out of spoofs".

Verdict on N: the core loop (threat, levers, forecast, reveal, result, repair, escalate) is readable from shape and color. The lever semantics and the scoring are not.

## Findings

### P1-1: The in-raid decision is usually empty (D, S)
- `shots/06_r1_decision.png`: HOLD gives x2. Every skip gives x2 or worse (decoy skip gives x3 and HOME -1). Hold is strictly best, so there is nothing to decide.
- `shots/38_r3_decision.png`: HOLD and all five skips give x4. This is an empty decision screen that stops the playout.
- `shots/22_r2_decision.png`: the only real choice in the whole planned leg (one node turns x3 into x2).
- `shots_scrambled/`: raid 3 has no decision at all (frames 37 -> 38 go straight to beam 2).
- The result is one meaningful click across three raids. The reveal, the lab's one suspense moment, then leads to a choice that does not matter.

### P1-2: The best line is a repeated flat damage tax that repair wipes (C, D)
- `shots/11_r1_aftermath.png`, `27_r2_aftermath.png`, `43_r3_aftermath.png`: BATTERED, BATTERED, BATTERED (2, 2, 4 DOWN).
- `44_record.png`: the same right-column assets go DOWN every raid.
- `19_r2_beam_b1.png` and `36_r3_beam_extra.png`: the Heat-50 "+" beam runs down the right column, and the kit has no decoy left to block it (`17_r2_plan_levers`, decoy 0; `32_r3_plan_empty`, decoy 0 and dark 0).
- `13_r1_between_repairs.png` and `29_r2_between_repairs.png`: every DOWN asset is repaired and the board resets. Shop: NO BUY both times (`14`, `30`).
- The player's real job is to pick which 2 assets to sacrifice and pay to restore them. Damage that resets is not a consequence. The only things that persist are the Heat number and the kit count.

### P1-3: Campaign loss is settled before the last raid, with no warning at the decision that caused it (P, C, Fit)
- `shots_breach/03_r1_forecast.png`: HOME -1 on every line ("worst: 5 DOWN, HOME -1"). There is no projection of where that leaves the leg.
- `shots_breach/28_r2_between_open.png` and `30_r2_between_picked.png`: HOME is at 1. NORMAL is picked and takes Heat to 78 with 3 known beams. LOW (72, 2 beams) is on screen. Neither card says "BREACH next raid" or "safe".
- `shots_breach/32_r3_plan_empty.png`: the first frame of raid 3 already says "No lever left in the kit avoids it". Frames 33 -> 35 are a forced march, and the first beam ends the campaign (`35_r3_breach_touch`).
- The breach warning (`shots_breachfix_demo/00`) works within a raid. It needs to fire one step earlier, on the intensity cards and the repair/shop picks, where the player still has levers.

### P2-1: The forecast chips around nodes are noise at this size (N, W)
- `shots/03_r1_forecast.png` and `shots/18_r2_forecast.png`: about 20 tiny shape+bolt chips sit around nodes, in addition to the side table.
- In the scrambled run these were the hardest marks to parse, and they duplicate the table. Into the Breach draws one strong mark per threatened tile (`refs/side_by_side_itb_vs_lab.png`).

### P2-2: Tier stamps flatten feedback (S, W)
- The planned line is BATTERED three times (`shots/44_record.png`). Only a naive line produces any other stamp: `shots_breach/11_r1_aftermath` is DAMAGED.
- The best play never earns a positive stamp, so the stamp does not reward good play.
- In the scrambled run two different outcomes share the same neutral grey (`shots_scrambled/27_r2_aftermath`, `41_r3_aftermath`).

### P2-3: Three-beam crowding (V, N)
- `shots_breach/32_r3_plan_empty.png` and `34_r3_forecast.png`: two solid lines, a dashed sealed line and the hunter column stack on column 3 over HOME. The ghost ring, the hunter arrow and the badges overlap there.
- This is the most dangerous moment of the leg and the least legible frame.

### P2-4: Too many accounting figures (W)
- The HUD shows bank, ASSETS KEPT and "was N". The ledger adds "Leg value now" and "Heat carried", and the record adds the score formula (`shots/12_r1_between_open.png`, `43_r3_aftermath.png`).
- Each figure is correct and reconciles, but a player has to learn five number names to judge one raid.

### P3-1: Hunter "own line" and the go-dark income chip still depend on words (N)
- The struck income chip above a dark node (`shots_scrambled/02_r1_plan_levers`) did not read as "no income".
- The hunter's choice of column is not visible in `shots_scrambled/25_r2_hunter_turn`.

### P3-2: An empty decision still pauses the playout (S)
- `shots/38_r3_decision.png` stops the hands-off sweep for a choice with five identical results.
- If a decision stays empty, it should be skipped automatically with a one-line chip. Better, it should not be empty at all (see change 1).

### P3-3: Good, keep
- The record mini-maps (`shots/44_record.png`).
- The kit tray with hollow pips.
- The intensity cards that show next Heat and beams.
- The breach warning that names and rings the lever (`shots_breachfix_demo/00` -> `02`).
- The shuffled shape per candidate, which removes the reveal tell.

## The 3 changes that would raise the score most

1. **Make the post-reveal response a real choice every raid** (D +1.5, S +2).
   - After the reveal, give the player a response with a trade-off. Examples: re-place one decoy onto the lit line at a Heat cost, or a spoof that costs Heat or kit so that "hold" is a real option.
   - Generate raids so that the real line always has at least two distinct outcomes among the options. The flow check already has the spoof-options data to test for this.
   - Auto-skip only when the kit is empty.
   - This turns the one tense beat (the reveal) into the decision, which is where Invisible, Inc. gets its S 9.
2. **Make damage stick or force a choice about it** (C +1.5, D +1).
   - Make repairs cost enough, or income fall enough, that you cannot repair everything every interval. Alternatively, let an unrepaired DOWN asset escalate to TAKEN in the next raid.
   - Vary the "+" beam's line per raid so the same column is not the permanent sacrifice.
   - Then the between screen becomes triage (repair, buy a lever, or bank), instead of "repair all, no buy" every time.
3. **Move the breach warning one step earlier, onto the between screen** (P +1, C +0.5, Fit +1).
   - On each intensity card, and after each repair or buy, show the next raid's breach status: "BREACH on 3/3 lines", "2/3", or "safe with a ghost".
   - Include intensity in the lever search.
   - The campaign loss in `shots_breach/` would then be a choice the player could see, not a verdict delivered at the start of raid 3.

Smaller but cheap: remove the per-node forecast chips (keep the table plus one mark per threatened node), and give the two neutral stamps distinct colors and glyphs. That is roughly N +1.

Rough ceiling if all three land: D 6.5-7, C 7.5, P 9, about 38-39/50, with S around 6. That puts the lab level with Invisible, Inc. on the total, without its suspense.

## Rules ceiling or presentation ceiling?

**It is mainly a rules ceiling now.** W and P are 8. The forecast, ledger, warning and record already present the rules about as clearly as a placeholder lab can, and further UI work will mostly add N and V points. D, C and S are capped by the rules themselves:
- **D:** the kit (2 ghosts, 2 decoys, 2 go dark for 3 raids) is smaller than the beam count once Heat passes 50, so the best line is to absorb damage.
- **D and S:** the spoof is usually empty, and the reveal picks among outcomes the player has already seen.
- **C:** repair returns the board to full every interval.
- **C and P:** the breach comes from multi-raid Heat and HOME arithmetic that no screen projects.

The one presentation item that would move a rules-bearing axis is change 3, and even that depends on a rules-side search (breach status by intensity). V 4 is a pure presentation ceiling. It does not affect the /50 total but will matter at Fit.

## References (images downloaded to `refs/raw/`)

- Into the Breach, `refs/raw/ref_1.jpg`: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/590380/ss_6113590509c195f98fa64cd738df534762e0c358.1920x1080.jpg
- Into the Breach, `refs/raw/ref_2.jpg`: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/590380/ss_edc919f964fd053441967b89592bc930a65f4171.1920x1080.jpg
- Invisible, Inc., `refs/raw/ref_3.jpg`: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/243970/ss_065423f51f4f35e9867ac6cec9598d32baf7c37b.1920x1080.jpg
- Invisible, Inc., `refs/raw/ref_4.jpg`: https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/243970/ss_33c9bdeb0dcbc64c6699e4375e591f7ab3c94ce3.1920x1080.jpg
- Screenshot lists: https://store.steampowered.com/api/appdetails?appids=590380&filters=screenshots and https://store.steampowered.com/api/appdetails?appids=243970&filters=screenshots

Scripts: `scripts/sheet.py`, `scripts/batch_sheets.py`, `scripts/side_by_side.py` (run as `python <file>`; the side-by-side was run with `python -P` so the folder of downloaded files is not put on the import path).

Process note: early on I ran one empty `python -c ""` no-op by mistake. It executed nothing, and every script after it was a file run as `python <file>`.
