# Sweep-raid lab L2: critic review

**Verdict: 33/50 (W7 P9 N5 D5 C7), S4, V4, Fit 7. It ties Kingdom Rush's wave (33) and sits just under FTL (35). The forecast is excellent. The decisions are thin. Not ready for the real build as it stands. Fix D first.**

Material read, in this order: shots_scrambled/ (23 frames, leg 5), shots/ (44 frames, leg 0, planned line), shots_breach/ (44 frames, leg 0, naive line), then LAB_README.md. I did not launch Godot. I opened no other critic folder and nothing under docs/design/raid_concepts/.

## Score table

| | Score | One-line reason |
|---|---|---|
| W what / why / when | 7 | The contact screen states the raid's strength by Heat band, the beams it brings and the cadence (3 raids, +12 Heat between). The "why" (what the corp wants, why Heat grows) never appears outside the README. |
| P predictability | 9 | The forecast lists every sealed-line case, with "hold -> best spoof" and HOME worst case. All 3 captured legs resolved exactly as forecast (leg 0 R1 x2, R2 x1, R3 x3). This is close to Into the Breach. The point lost: the map slots are 10 px glyph pairs stacked on crowded beams. |
| N no-words | 5 | Icons carry the nouns: coins, bolt = DOWN, server + pips = HOME, numbered beam badges. Every verb is in words: stamps, ledger rows, spoof options, the repair step. The dashed ring has three meanings. Red pips mark raids that lost nothing. |
| D decision depth (leg) | 5 | One of each lever, reset every raid. The ghost went out in 9 of 9 raids, the spoof was used 9 of 9 times and the forecast names the best spoof. Repair is score-neutral and adds income, so it is always right. The real decisions are ghost placement near a Heat line and decoy versus evade. |
| C consequences | 7 | DOWN, then TAKEN, and HOME integrity persist across the leg. Breach ends the campaign on a full-screen card, and it was forecast ("worst case: lose 1") before launch, so it is fair. The careful line still bleeds value (50 -> 45) under three identical "CELL HOLDS" stamps, which does little to motivate. |
| **Total** | **33/50** | |
| S suspense | 4 | The only open question is which of 3 lines is sealed, and it resolves at the unseal. After that the spoof is a lookup and the rest plays out a known result. The breach card is the one real spike. |
| V visuals | 4 | Clean placeholder vector work with a consistent palette. Beams overlap at 2+ known beams, the stamp sub-line overflows its box, "HOME -" is clipped. There is no motion beyond pulses (frames only). |
| Fit | 7 | Ghost, decoy, go dark and spoof against corp sweeps over one cell network fits a "hackers evading the corp" premise. HOME breach = campaign lost lands hard. |

## Placement among the six

ITB 45 > StS 42 > Invisible Inc. 39 > FTL 35 > **L2 lab 33** = Kingdom Rush 33 > TFT 31.

- **Above TFT** on W and P: the information here is complete and verified, while TFT's round is a coin flip you watch.
- **Level with Kingdom Rush:** better predictability, much worse suspense and visuals.
- **Below FTL and Invisible Inc. on D and S.** Invisible Inc.'s alarm is one shared clock that every action spends. Here each raid resets the levers and the only shared clock (Heat) rises +12 per interval no matter what you do. The ghost's +5 matters only in the 45-49 and 70-74 windows.
- **The gap to Slay the Spire (StS) is depth, not information.** Slay the Spire's intents leave you a hand of trade-offs. This lab's forecast hands you the answer.

## What the scrambled captures said, and failed to say

What I understood without words (leg 5):
- A Heat bar with two lines.
- A coin bank.
- A 4x3 grid of coin-valued nodes and a server with 3 pips that I must protect.
- Blue beams in a numbered order (1, +, ?, 3), with dashed lines for the possible ones.
- Three placeable things, each with a cost chip: a flame (+5) and a coin (-3).
- A teal tool used mid-sweep.
- A teal stamp (good) and an orange stamp, and a ledger that adds up.
- Between raids, per-node +N income.

What it failed to say:
1. **The difference between levers.** The ghost (yellow dashed ring), the spoof (teal dashed ring) and the sealed beam (blue dashed "?" ring) all read as the same mark. I could not tell hide-from-all from skip-one-node.
2. **Go dark (the black disc).** Its cost chip is a crossed-out icon and a number. I could not tell what it does or how it differs from the ghost.
3. **The spoof decision.** The options are a row of node glyphs, each with an outcome chip. I could not tell that I was meant to click a node on the lit line, or why the "hold" row is special.
4. **The outcome.** On raid 2 the decoy took the only contact and nothing was lost, yet the raid pip turned **red**, the same as raid 3. Red pip with an orange stamp reads as "you lost". Only the words "a decoy took the beam" say otherwise, and they are scrambled. The evade bonus (-10 Heat) shows only as a teal number.
5. **The repair step.** Leg 5 had no DOWN assets, so 04/05 and 10/11 are identical frames: a beat with no visible choice. I could not tell what "repair" is from these frames.
6. **The score line** ("ZRXSF 80 = kdqv 32 + dzzfgz vfeg 48 - AXJF ...") is all words, so its formula is unreadable.
7. **The scramble is weak.** It is a fixed one-letter substitution, and I could decode it from "Afdg 44" next to the flame ("Heat"). Others can too. Use random per-glyph noise, or shape-preserving blocks, if this is meant as a real no-words test.

## Ledger and consistency errors found

1. **Spoof decision offered after the campaign was lost** (breach 20_r3_decision). Beam 1 took HOME 1 -> 0, the pips show 3 X, yet the sweep still stops for "SPOOF DECISION". The breach card should fire on the touch that empties HOME, or skip the decision.
2. **"CELL HOLDS" stamped on raids where HOME was hit** (breach R1 "4 DOWN HOME -1", R2 "3 DOWN 1 TAKEN HOME -1"). The cell did not hold. You need a third outcome word and color between EVADED and BREACHED.
3. **Red raid pip for raids that lost nothing.** Leg 5 R2 and R3 each lost 0, yet show the same red pip as a HOME hit. Pip color should follow losses, not "not evaded".
4. **The repair is refused while the panel shows funds** (breach 07). The panel says "NEXT RAID 9" while the strip says "not enough Schematics: repair costs 2". Repairs are paid before income, which is a legitimate rule, but the panel shows the post-income bank as though it can be spent. Show "bank now" next to the repair line.
5. **"Leg value now" on the between-raids screen ignores the pending income** (leg 0 R1: shows 44 while NEXT RAID is 12, and the next aftermath counts the income). It is consistent with the formula but not with the panel right above it. Label it "before income" or include the income.
6. **The record mixes delta and cumulative views.** Breach R3 "STATUS CHANGES x1 TAKEN" sits beside a mini map showing 2 TAKEN cells, one of them carried over from R2. This is fine once you know it, but there is no marker for carried-over states.
7. **Clipping.** The "HOME -" pill is cut off (breach 05, 13) and the stamp sub-line overflows its box (breach 13). At 3 known beams, badges and glyph slots overlap the HOME pips (breach and leg 0 19_r3_forecast).
8. **Capture order.** 04_r1_beam_b2 (spoof already used) sorts before 04_r1_decision, and 04_r1_unseal says "Held, not used." before the decision exists. That wording reads as a final result. Use "Held, decide after the reveal".
9. **The careful line ends below where it started.** Leg 0 opens worth 50 (bank 10 + assets 40) and the best play ends at 45. Every stamp is "CELL HOLDS", and there is no par or target to show whether 45 is good. The rules are consistent here, but players will read it as "nothing I do works".
10. **"Leg score: -100" on a "THE CAMPAIGN IS LOST" card.** The score is meaningless once the campaign is gone. Drop it or call it what it is.

No arithmetic errors. Every ledger I checked reconciles across all 3 legs: Heat before + ghost + run, bank before - decoy - repair + income, and score = bank + assets net of DOWN halves - 8 per pip. Preview equals result in every captured raid.

## The 5 changes that would most raise it

1. **Make levers scarce across the leg, not per raid** (designer decision). For example, 2 ghosts and 1 decoy for the whole 3-raid leg, or levers bought from the bank between raids. As things stand, "use everything every raid" is the line, so D stays at 5. Expected D +2, S +1.
2. **Stop the forecast from naming the best spoof** (designer decision; the F1 toggle already exists). Keep the per-line outcomes, drop the teal best-skip mark and the "best spoof" column. The one mid-sweep choice then becomes a real read under pressure, not a lookup. Better still, make the spoof cost something (Heat or a pip of bank) so that holding it is a real choice. Expected D +1, S +2, P -0.5.
3. **Give repair a real trade-off** (designer decision). As built, repairing an asset converts v//2 of bank into v//2 of asset value (score-neutral), plus it adds income and protection from TAKEN, so it is always right. Possible fixes: repair adds Heat, or repair takes the asset's next interval of income, or the repair budget competes with lever purchases (see 1). Expected D +1.
4. **Add an outcome tier and fix the color language.** Use EVADED (teal), HELD clean (no losses, neutral), CELL HIT (losses, orange), HOME HIT (red) and BREACHED. Pips and stamps should follow losses. Give ghost, spoof and sealed beam three distinct marks: for example, ghost = hollow eye/hatch, spoof = teal skip-arrow on the node, sealed = "?" badge only, no ring. Expected N +2, C +0.5.
5. **Let Heat respond to play** (designer decision). Right now +12 per interval dominates, and the ghost's +5 only matters in two narrow windows. Possible fixes: evade -10 made reachable (it is near-impossible once a known extra beam runs), Heat cost per touch, or lowering the +12 so lever Heat is the main driver. Then the Heat line becomes the leg's shared clock, as Invisible Inc.'s alarm is. Expected D +1, S +1, C +0.5.

(Outside the top five: stop the playout at the breach, add a par or target score on the record, and spread out badges on the 3-beam raids.)

## References

I downloaded no reference screenshots: downloading files from the web needs the user's own approval, and the instruction to do so came from an agent. The comparison sheet `refs/critic_sheet.png` is built from the lab's own captures instead (scrambled vs readable forecast, decoy-only red pip, spoof lookup, stamp overflow, spoof-after-breach, refused repair, careful record). The calibration games are judged from the rubric scores given and from general knowledge of those systems:
- Into the Breach: telegraphed enemy attacks, everything shown.
- Slay the Spire: intent icons.
- Invisible Inc.: the alarm-level clock.

## Ready for the real build?

**No, not as a ruleset. Yes, as a forecast and ledger engine.**

- **Port it:** the forecast, the preview equals result guarantee, DOWN -> TAKEN escalation, HOME integrity and the full-screen breach. All of them work and are legible.
- **Do not port yet:**
  - The per-raid lever reset.
  - The forecast that solves the spoof for the player.
  - The always-right repair.
  - The outcome / color language.

Scored now, the system is a 33. It will not reach the 39+ tier (Invisible Inc.) until a resource spans the leg and the mid-sweep choice is unsolved on screen. Run one more lab round on changes 1-3 (designer decisions) before it goes into the real build.
