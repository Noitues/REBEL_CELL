# H7 Bastion raid lab: fresh critic review

Verdict: a correct, honest, legible ledger machine with no suspense. It works as a puzzle (find the 2 buys that turn the forecast to CLEAN) and fails as a spectacle. The exact forecast that makes P a 9 is the same thing that makes S a 2.

Method: I read the 12 planned-line captures (`shots/`) and the 12 no-buy captures (`shots_bare/`) in order, wrote down what I understood (`first_read_notes.md`), and only then read `LAB_README.md` and GDD sections 1.1 to 1.3. Reference sheet: `sheet_lab_vs_refs.png`, which puts lab captures next to Into the Breach, Kingdom Rush and Bad North.

## Scores (calibrated to shipped games; 7 = a good shipped game)

| Axis | Score | One-line reason |
| --- | --- | --- |
| W what / why / when | 6 | "Defend these 6 nodes from blue lanes, raid at Heat 26/51/76" comes across. Two things never do: what the bank is for beyond the next buy, and how Heat or my netruns cause the raids. The hex "2/3/3" (netruns) is only decoded by the README. |
| P predictability before commit | 9 | The forecast is exact. It names every lost node, the net and the bank after, and the planned line matched it to the coin (31, 51, 61). The corp-adapts chip names the counter before I buy. Best in class, Into the Breach tier. |
| N no-words readability | 4 | Threats are three-letter text in identical blue hexes (COU, ENF, BAI, LCK, AUD, INS); without text they are all the same unit. Node state (HOLDS / SCUFFED -N / TAKEN) is text in boxes; only the red X on a taken node reads wordlessly. The same hex glyph means netruns on the raid card and base income in the ledger. |
| D decision depth | 4 | 5 pieces, at most 2 per visit, 6 nodes, 1 crew token, with undo and an exact forecast. In practice you place, look at the forecast, undo, and repeat until it says CLEAN. Corp adaptation is the only counter-pressure, and it is shown up front. There is no tension between banking and spending. |
| C consequences | 5 | Footholds, survivors and the bank all persist, which is good. But a near-wipe (5 of 6 nodes TAKEN) is still stamped "HOLDS". Losing a node costs less patch than a scuff (bare raid 3: FW + SAFE taken, net -5). A negative bank greys out the whole shop, so there is no way back. The bank chart flattens negatives to 0. The record table truncates "lost VA". |
| Fit to premise | 4 | The Solace debt-collector theme (Bailiff, Collector, Courier, Lockdown) fits the subscription-bricking corp well. The verbs do not: turrets, railguns and sentries on a node graph is generic tower defense. Nothing is evaded, hidden, spoofed or hacked toward a core. |
| V visual quality vs AAA | 2 | Placeholder vector shapes on flat navy, tiny chips and 8 px HP bars. Against Kingdom Rush's equally small units (see the sheet) the gap is total. It is honest placeholder work, not a look. |
| S suspense during playout | 2 | I already know the outcome to the coin before I press START, and I have zero input. The playout is a text log in a side panel plus chips sliding along lines. Nothing in it can surprise me. |

Core five (W P N D C): 28 / 50. All eight axes: 36 / 80.

## The 5 changes that would most raise the total

1. **Forecast a band, not an exact result (designer decision).** Visit screen, right column. Keep the exact forecast for nodes the player has fully covered, but show the others as "at risk" (amber) and keep one element hidden until the raid: either one threat per raid as a ghost chip, or one unknown trait that is revealed in beat 1. The other option is to keep the exact forecast and let the playout show it being earned: put the forecast's per-node predictions on the map and tick each one off as it resolves. Either way the playout gets something unknown, or something to confirm. Expected gain: S +3 to +4, D +1 (a hedge versus over-commit decision appears), P -1 at most.

2. **Show threat intents on the board, Into the Breach style.** Visit and raid screens. During the visit, draw every telegraphed threat's route as an arrow ending at its target node, with the damage it will deal printed on that node ("-9"). That moves the forecast from the side panel onto the map. Replace the lettered hexes with silhouettes, one per role: Courier as a fast arrow, Enforcer as a heavy block, Bailiff with a shield, Lockdown as a padlock. Size them by HP and put the trait badge on the chip. Expected gain: N +2, P stays 9, W +1.

3. **Make the aftermath stamp and the economy tell the truth (partly a designer decision).** Aftermath and record screens.
   - Severity: grade the stamp by nodes lost and home integrity (CLEAN / SCUFFED / BLED / BREACHED, with matching color), so "HOLDS" can never sit on 5 of 6 taken nodes.
   - Designer decision: a TAKEN node should cost at least as much as its worst scuff, through rebuild cost or permanent income loss shown on the stamp. Right now taking losses is cheaper than barely holding.
   - Designer decision: a negative bank needs a way out (a sell-back, a crew-only visit with a visible benefit, or a debt floor). As it stands, one bad raid is a silent soft-lock: three greyed-out visits.
   - Bugs: let the bank chart plot negatives, stop truncating the "lost" column, use one label everywhere (the card says HELD, the stamp says HOLDS, the forecast says "HELD, patch").
   Expected gain: C +2.

4. **Put the playout on the board, not in the log.** Raid screen.
   - Effects: projectiles from each piece, bigger HP rings on nodes and threats, a kill pop with its "+4 salvage" coin flying to the bank, and a hit-stop plus red flash when a node falls.
   - Home: a home-integrity bar that is always visible.
   - Log: shrink it to a ticker or drop it. The numbered badges and the "-9" floaters are a good start but are 12 px.
   - Bug: the bank shows the pre-spend value during the raid (14 while the visit showed 4; 51 while it showed 39).
   Expected gain: S +1 to +2, N +1, V +1.

5. **Give the bank a purpose and the visit a real trade-off (designer decision).** Visit and leg views. Show on the leg view what the leg-end bank buys in the campaign (Schematics, an Exploit, a Heat drop). Then add one tension the forecast cannot solve for free. Some options:
   - interest on unspent bank;
   - corp adaptation escalating with total investment, not only the top piece;
   - a node-slot cap that forces you to choose between protecting the Vault (income) and the Proxy (sight two raids ahead).

   The Proxy's two-raid sight already has real value, so build on that: make information, not just towers, something you can buy. Expected gain: D +2, W +1, Fit +1.

Fit needs its own pass. Reskin the pieces as intrusion countermeasures (trace, honeypot, spoof route, ICE are all there in the premise) and let at least one verb redirect or hide traffic rather than shoot it. That is the difference between "hackers evading a corp" and "towers versus creeps".

## What a player could not understand from the captures alone

- What the hex number on each raid card means (netruns, per the README), and why the same hex glyph then means base income (+8) in the ledger.
- Which three-letter code is which threat, and what each one does (Lockdown freezing the Home to Firewall link, shown as a padlock on that link, is only explained in the README).
- Why raid 3's roster showed 6 chips after raid 1 and 4 at visit 2. Ghosted survivors from a forecast are not explained on screen.
- What the bank is for once the leg ends, and what happens to footholds and survivors after raid 3.
- Why the crew moved (+2 per shot needs the README), and what the Safehouse condition is.
- That "HOLDS" can mean "lost 5 of 6 nodes".
- What Decoy (an arch glyph) does. Its effect is never visible in the playout, and the enemy simply stops at the Firewall.
- How Heat relates to the player's actions. The thresholds 26/51/76 are shown, but nothing shows Heat rising.

## Playing it versus mockups

Playing it reveals problems mockups hide.

- **Suspense:** the suspense deficit only becomes obvious in motion. Watching 4 to 9 beats of an outcome I was already told, with no input, feels like waiting for a progress bar.
- **Bugs:** it surfaced real defects (pre-spend bank during the raid, the negative-bank chart clamp, column truncation, the HOLDS stamp on a wipe, taken cheaper than scuffed, the shop soft-lock at negative bank).
- **Decision loop:** it shows the place, check, undo loop, which a mockup presents as a considered plan.
- **Scale:** in the bare raid 3 capture, eight threat chips pile onto two nodes and become unreadable, which a static mockup never shows.

Playing it also confirms real strengths.

- The forecast really equals the result, and the bank arithmetic is checkable line by line.
- The corp-adapts chip (turret leads to Bailiff becoming ARMORED) is a clean, legible counter-pick.
- Telegraphing two raids while the Proxy holds is a good, readable stake. Losing the Proxy visibly blinds raid 3 (the eye-slash).
- The 1 s two-beat cadence (move, then shoot) is easy to follow at 1x.

The rules core is sound and auditable. The experience on top of it is not yet a game moment.

## References (images only, not executed)

- Into the Breach screenshot: https://upload.wikimedia.org/wikipedia/en/d/d0/Into_the_Breach_Screenshot.png (`refs/itb.png`)
- Kingdom Rush gameplay: https://upload.wikimedia.org/wikipedia/en/1/19/Kingdom_Rush_Gameplay.jpg (`refs/kingdom_rush.jpg`)
- Bad North key art: https://upload.wikimedia.org/wikipedia/en/0/09/Bad_North.jpg (`refs/bad_north.jpg`)
- Side-by-side sheet: `sheet_lab_vs_refs.png` (built by `scripts/make_sheet.py`)
