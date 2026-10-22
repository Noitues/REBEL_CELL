# Playtest findings: PB-SOL-1 · build 52626bcd24d785a8dd7c75b213a52ea639892935 · 2026-10-21

> Synthesised from 5 Claude playtest reports, their screen audits and motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.
> No separate screen audits or motion contact sheets came with this batch, so audit and feel items come from the reports only.

## 1. Headline

- **No tester finished a netrun or a campaign.**
  - The furthest anyone got was a T1 Site.
  - mothball and static_fox each started 4 netruns and survived 1 raid.
  - There were 9 operative deaths across 3 testers.
  - Enjoyment averaged 3.2/10.
- **Two hard stops ended 4 of the 5 sessions.**
  - **RESPIN locks UNDO.** cinder_ivy and copperjack were left with staged cards, a LETHAL preview and 4–5 HP, and both quit there.
  - **Raid stationing never registers.** mothball and tinroof hit this; tinroof's session ended on it.
- **Lost or repeated clicks on core buttons affected every tester.** The buttons were JACK IN, LOOT and loot CONTINUE, and Quit. Keyboard input usually got through.
- **Combat is skill-limited, not overtuned.** The ground truth shows:
  - A Perfect was reachable on 94–100% of turns. Testers landed one on only 15–57% of turns.
  - Damage taken per turn (3.0–6.4) roughly matched doing nothing (3.3–6.4) for every tester. The best plan took 0.3–1.5.
  - Testers dealt 4.2–8.7 per turn against a best of 17.1–18.9, which explains the long fights.
  - The attrition and "forced fights at low HP" complaints are therefore tester-skill signals. The actionable problems are teaching and targeting clarity.
- This is the first batch, so there is no trend.

| Metric | This batch | Previous (none) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 5 (2 / 2 / 1 / 0) | – |
| Furthest progress | T1 Site. 4 netruns started, 1 raid survived (mothball, static_fox). 0 netruns completed (tinroof's SUMMARY says 2, but the body counts completed fights). | – |
| Avg enjoyment (1–10) | 3.2 | – |
| Avg RNG fairness (1 fair – 5 cheated) | 4.0 | – |
| Bugs reported (deduplicated) | 14 (from 49 raw) | – |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B-01 | P1 | screens | **Loot sheet stalls.** Card frames stay dim or blank, LOOT and CONTINUE ignore clicks, and one pick was auto-taken. | cinder_ivy, copperjack, mothball, static_fox | Win a fight, press LOOT, take a card, press CONTINUE. LOOT needed 2–3 clicks. CONTINUE stayed greyed and ignored clicks, while Enter or Space worked (which key worked varied). Copperjack's sheet showed only CYCLES until PROCEED. mothball's frames were blank until clicked. cinder_ivy got a card she did not pick. | static_fox §7#1 (0054, 0115, 0954, 1194, 1357); cinder_ivy §7#7–8 (0124, 0274); copperjack §7#2 (0080); mothball §7#6–7 (0087, 0368) | confirmed: 4 testers. Every tester eventually got through by click or key, so the control does accept input. Still worth one human repeat of the click path. |
| B-02 | P1 | city | **JACK IN ignores the first clicks.** | cinder_ivy, copperjack, mothball, tinroof | Select the T1 site and click JACK IN. It needed 3–4+ clicks. mothball hit it three times (5.0m, 29.4m, 48.3m). Enter or a centre click worked. | cinder_ivy §7#8 (0074); copperjack §7#3 (0044); mothball §7#2 (0063); tinroof §7#3 (0064) | confirmed: 4 testers, and all got past it |
| B-03 | P1 | screens | **Quit to Main Menu or the Quit confirm ignores input.** | cinder_ivy, copperjack, mothball | Pause, then Quit. It needed a second try for cinder_ivy (35.4m) and copperjack (14.4m). For mothball the confirm ignored clicks, A and Enter for about 6 min (54.2–60.2m). Only Esc backed out, and the harness restarted the game several times. | cinder_ivy §7#8; copperjack §7#7 (0143); mothball §7#9 (0562) | confirmed: cinder_ivy and copperjack got through on retry, so mothball's case is real, not a sim artifact |
| B-04 | P1 | combat | **Target clicks on the player's own wheel are ignored** for Jolt and Fine Tune. | cinder_ivy, mothball, tinroof | Select Fine Tune or Jolt (aim defaults to the enemy wheel), then click your own wheel or the "glowing target". Nothing stages. cinder_ivy saw ~20 tries on turn 9, cleared only by Quit/Continue. mothball lost 19.9–24.0m. | cinder_ivy §7#4 (0086, 0261); mothball §7#3 (0225); tinroof §7#6 (0184) | confirmed: copperjack redirected successfully, so the control accepts input. Check the hit area against the highlighted target. |
| B-05 | P2 | screens | **Other single-control click losses.** | cinder_ivy, static_fox, tinroof | <ul><li>Tutorial Next, 1.4–2.0m (tinroof).</li><li>HQ DEFENSE took 3+ clicks, then a sudden dispatch (tinroof, 14.0m).</li><li>BACK TO HQ, 23.9m (tinroof).</li><li>Rest LEAVE: clicks ignored, Space worked (static_fox, 100.2m).</li><li>Wellness Kiosk option: clicks and key 1 ignored (static_fox, 12.3m).</li><li>Esc on the HQ map: nothing happened, while the MENU button works (cinder_ivy, 6.3m).</li></ul> | tinroof §7#2, #4, #5 (0022, 0156, 0248); static_fox §7#4–5 (1363, 0119); cinder_ivy §7#9 (0066) | unconfirmed-input: no other tester reported getting past these exact controls |
| B-06 | P1 | combat | **After RESPIN, UNDO refuses to clear cards staged before it.** With RAM debt the turn can only be sent, and Quit/Continue restores the same stuck state. | cinder_ivy, copperjack | Stage cards (incl. Overdrive or Brute Spin), then RESPIN at 4–5 HP vs Dosage Dispenser. UNDO/Z shows "Nothing to undo since your RESPIN" or "random spin can't be undone". RAM sits at 0–1/12 with debt and the preview stays LETHAL. Quit then Continue changes nothing (cinder_ivy 31.5–36.5m, copperjack 13.6–17.9m). | cinder_ivy §7#1 (0304, 0345); copperjack §7#1 (0162) | confirmed: 2 testers, steps agree. See D-04 for whether the lock is intended. |
| B-07 | P1 | city | **Raid Setup stationing never registers.** | mothball, tinroof | At Raid Setup, click the crew card, the readout, a node, and the CREW/DEFENSE tabs. Stationed stays 0 and the screen says NO CREW STATIONED. mothball tried ~30 clicks over 42.3–46.1m, then played the raid undefended. tinroof spent 24.7–30.5m on it and stopped. | mothball §5 Q3, §7#1 (0465); tinroof §7#1 (0308) | unconfirmed-input: no tester stationed anyone. The confirm dialog says "Station an operative on a node at HQ first" (see C-10). |
| B-08 | P2 | city | **Route/grid view toggle and map nodes ignore clicks.** | mothball, static_fox | Clicking ROUTE VIEW was ignored twice and Enter worked (static_fox, 65.9m). Grid view buttons barely responded (mothball, 34.4–36.4m). The player marker and the node at 240,350 ignored ~6 clicks (mothball, 14.3m). | static_fox §7#3 (0957); mothball §7#8, #10 (0167, 0380) | unconfirmed-input |
| B-09 | P2 | combat | **UNDO is unreliable outside RESPIN.** | cinder_ivy, copperjack | cinder_ivy saw "Nothing to undo" while cards were staged (tutorial turn 2, netrun turns 6/7/9). copperjack looped on undo for ~2 min on Collections Agent turn 2 (9.4–11.5m), with the 13→5 preview returning. | cinder_ivy §7#2 (0028, 0244); copperjack §7#8 (0115) | single (steps differ; mothball, static_fox and tinroof reported undo working) |
| B-10 | P2 | combat | **Preview flips between two results** on an unchanged setup. | cinder_ivy | Turn 7 (18.4–22.6m) and turn 9: the preview switched between LETHAL 9→0 and 9→7 with nothing changed. | cinder_ivy §7#3 (0183, 0240) | single |
| B-11 | P2 | rules | **Result differs from the preview.** | mothball | T1 Site fight, turn 11 (26.8m): the preview said Agent 7→0, but after SEND IT the Agent stayed at 7/40 with Guard 6. | mothball §2, §7#5 (0287) | single |
| B-12 | P2 | rules | **Mutual kill shows DEFEAT while the enemy shows DELETED**, and it costs the operative with no explanation. | mothball | Both sides reached 0 HP on the same turn (27.8m, 52.0m). | mothball §7#4 (0540) | single (see D-09) |
| B-13 | P2 | screens | **SKIP then CONTINUE leaves the player on the loot sheet.** | static_fox | 84.3m: press SKIP, then CONTINUE. Only picking a card and then Continue exited. | static_fox §7#2 (1162) | single (CONTINUE works elsewhere) |
| B-14 | P2 | combat | **Quit/Continue mid-fight restores an inconsistent combat display.** | cinder_ivy | On turn 9 the staged cards came back but the LETHAL preview was gone (HP 7→4). On turn 1 vs Dispenser, RAM read 2/12 with FREE NUDGE 1, then dropped to 0/12 after one nudge. | cinder_ivy §5 Q2 | single |

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C-01 | city | **Route and city maps are hard to read.** <ul><li>Nodes are dim and unlabeled.</li><li>The help says "click a numbered room", but few nodes show numbers.</li><li>The D badge and FRONT 4.0 are unexplained.</li><li>The legend is tiny or hidden by the "Taken" toast.</li><li>The toggle is called both GRID VIEW and OVERVIEW.</li><li>There is no per-node Heat cost.</li><li>A tooltip says T1 is "not reachable", yet it was the only node available.</li></ul> | 5 of 5 | mothball ~2 min on the lock chain, solved by clicking CLEAR FIRST. tinroof never found the icon meanings. | cinder_ivy §4; copperjack §4, §7#5 (0128); mothball §4, confusion 14.0m; static_fox §4; tinroof §4 | Label node types and numbers, keep the legend clear of toasts, use one name for the toggle, and show Heat per node. |
| C-02 | combat | **Card aiming is unclear.** Jolt and Fine Tune default to the enemy wheel. The "glowing target" prompt and Jolt's "NEED 1" badge are unexplained. | 4 of 5 (cinder_ivy, copperjack, mothball, tinroof) | mothball ~4 min (19.9–24.0m), and NEED 1 was never understood. tinroof ~0.8 min, then cancelled. | cinder_ivy confusion 8.1m; copperjack §2, §7#4 (0063); mothball §2, confusion 38.2m; tinroof confusion 16.4m | Make the default target and the valid targets explicit before the click, and explain NEED n. Pairs with B-04. |
| C-03 | screens | **Overlap and clipping at 1280×720.** <ul><li>Hand cards overlap and their text is cut.</li><li>The EXECUTE/SEND IT and LOOT/PROCEED labels overlap.</li><li>The RESIST tag covers enemy HP.</li><li>The tutorial box covers the wheels.</li><li>HQ counters and tab names are clipped, and there is no clear JACK IN button.</li><li>Stamps sit under SAVED.</li></ul> | 4 of 5 (cinder_ivy, copperjack, static_fox, tinroof) | Testers tripped on it while reading cards and labels. | cinder_ivy §4, §7#10 (0078, 0118); copperjack §4; static_fox §4, §7#9 (0903, 1120); tinroof §7#9 (0141) | Layout pass on combat hand, HUD and HQ at 1280×720. |
| C-04 | combat | **Wheel basics are never taught.** Free Nudge, the PERFECT/GOOD/WEAK tags, the 1/0 markers, LANDS HERE, Q/E, RAM and RESPIN go unexplained, and the tutorial is jargon-heavy. | 3 of 5 (mothball, tinroof, cinder_ivy) | mothball spent the whole sim unresolved. Ground truth: mothball and tinroof landed fewer Perfects than doing nothing would have (17 vs 25%, 18 vs 29%). | mothball §2, confusion 1.6m; tinroof §2, §5; cinder_ivy §2; ground-truth table | Plain-language, in-fight callouts for "land your needle on a high slice, push theirs onto a low/block slice". Tooltips alone failed, because the novices did not hover. |
| C-05 | combat | **The RESPIN, RAM debt and UNDO interaction is unexplained.** Overdrive's "RAM -1" debt appears silently, and the player is not warned that RESPIN locks earlier stages. | 3 of 5 (cinder_ivy, copperjack, tinroof) | cinder_ivy and copperjack both ended their sessions here. tinroof needed ~1.5 min on the tooltip. | cinder_ivy §7#6 (0113), confusion 11.5m, 31.5m; copperjack §2; tinroof confusion 4.1m | Warn before a RESPIN that commits staged cards, and explain debt where it appears. |
| C-06 | combat | **Players can't tell what a play pays or which pointer makes the preview lethal.** The elite's lower pointer sat on NULL while the preview still read LETHAL. A -11 self-hit had no visible cause. Brute Spin's "6 ticks" doesn't say what that gains. | 3 of 5 (static_fox, cinder_ivy, tinroof) | static_fox unresolved and lost the fight. tinroof did ~1.3 min of undos. cinder_ivy unresolved. | static_fox confusion 78.1m; cinder_ivy §7#5 (0044); tinroof confusion 21.3m | Attribute preview chips to their source pointer or slice. |
| C-07 | screens | **Reward pick state is ambiguous.** Unpicked cards fade, so the pick looks locked. CONTINUE and SKIP look alike. The confirm dialog ("Leave 1 reward(s) behind?" BACK / PROCEED) is unclear. | 3 of 5 (tinroof, cinder_ivy, copperjack) | tinroof ~0.3 min, resolved with CONTINUE. | tinroof §7#7 (0202); cinder_ivy §7#7; copperjack §7#6 (0082) | Show the chosen card, and use distinct buttons with plain Yes/No wording. |
| C-08 | screens | **Placeholder, stale or risky UI text and placement.** <ul><li>Placeholder tooltips: "Cache: placeholder text" and "Rest: placeholder text".</li><li>The banner still says RAID IN PROGRESS after "Raid over".</li><li>A toast showed deck 11 while the deck button showed 12.</li><li>The rest screen says "spent" next to a PATCH preview of 43/60.</li><li>Abandon Run sits next to Quit.</li></ul> | 3 of 5 (mothball, static_fox, copperjack) | Minor, though Abandon Run next to Quit risks losing a run. | mothball §7#11–13 (0374, 0487); static_fox §7#6–7 (1359, 1361); copperjack §7#7 | Text pass, plus moving Abandon Run away from Quit. |
| C-09 | city | **Crew and hire flow is unclear.** mothball never found "hire a rookie" in the CREW tab, while static_fox found the free hire. A crew card shows a FIRE stamp with a FREE label, and the site text says to hire a rookie while Breaker 3 is READY. | 2 of 5 (mothball, tinroof) | mothball never resolved it (28.5m, 52.4m). tinroof never resolved it (24.1m). | mothball §3, confusion 52.4m; tinroof §7#8 (0250) | Use one clearly labelled hire action and remove the misleading stamp. |
| C-10 | city | **Players don't know where stationing happens.** Both testers tried inside Raid Setup, but the dialog says to station "at HQ first". | 2 of 5 (mothball, tinroof) | ~4 min (mothball), ~6 min (tinroof). Never resolved. | mothball §5 Q3; tinroof §3, confusion 24.7m | Link from Raid Setup to the stationing step, or allow it there. Clarify this before treating B-07 as a code bug. |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D-01 | **HP attrition, forced fights at low HP, "no heal", deaths.** This is tester skill-limited. No tester aligned for Perfects and still lost. | all 5 | All five reported damage taken ≈ doing nothing, and Perfects landed on only 15–57% of turns when reachable on 94–100%. What each tester failed to read or do (→ C-02, C-04, C-06): <ul><li>**cinder_ivy:** 15% Perfects, 4.7 taken vs 4.7 no-action. Fought the default aim and never moved the enemy needle.</li><li>**copperjack:** 57% Perfects (the best) but 6.4 taken vs 6.4 no-action. Played only offense and spent RAM on stacked Brute Spin to 5 HP.</li><li>**mothball:** 18% Perfects, 4.5 taken vs 4.0 no-action, so his actions made things worse. Did not read the tags or Free Nudge.</li><li>**static_fox:** 24% Perfects, 3.0 taken vs 3.3 no-action. Did push one enemy needle onto a block slice (Claims Adjuster turn 2).</li><li>**tinroof:** 19% Perfects vs 29% from doing nothing. Played the leftmost card every time.</li></ul> | Once teaching lands, should heal access stay as is? Options: (a) keep it scarce as the skill gate, (b) make the existing heals (Rest, Wellness Kiosk) more visible on the route, (c) add a retreat or heal choice when HP is critical. |
| D-02 | **Fights and netruns feel too long.** This is tester skill-limited. | static_fox, cinder_ivy, mothball | Recall Unit took 23 turns and ~48 min (static_fox §5). cinder_ivy's fights reached 10 turns. 3 of 5 rated netruns "too long". Testers dealt 4.2–8.7 per turn vs 17.1–18.9 best, so fights ran roughly 2–4× the planned length. | What fight length should a mid-skill player see? Options: (a) leave it and fix teaching, (b) add a visible mid-fight hint when the player is far off the best line, (c) revisit enemy HP after a skilled-tester batch. |
| D-03 | **Wheels re-spin each turn and wipe good landings.** | copperjack | A Perfect 6 became a Weak 6 on Billing Daemon turn 4 (§2). | Is losing a landing between turns intended? Options: (a) keep, (b) signal the coming re-spin, (c) carry the landing over in some cases. |
| D-04 | **RESPIN commits earlier staged cards and blocks UNDO.** | cinder_ivy, copperjack | B-06 | Is the undo lock intended? Options: (a) keep it and warn before RESPIN, (b) let UNDO clear cards staged before the RESPIN but keep the spin, (c) refund or unstage when no legal non-lethal line remains. |
| D-05 | **Inner-ring cards look dead without an inner ring.** | cinder_ivy, static_fox | Inner Drift (cinder_ivy §2); Ring Tap and Gear Shift (static_fox §2). | Should these be offered when the player has no inner ring? Options: (a) gate the offers, (b) keep them and state the requirement on the card, (c) leave as is. |
| D-06 | **Testers split on card value.** | copperjack, mothball, static_fox, tinroof | Jolt was called OP ×2 and weak ×2 (mothball's view stems from targeting, B-04). Mirror Flip was called OP by static_fox and weak by copperjack, and is blocked by resist (static_fox). Overdrive was called risky at low HP. | Wait for a skilled batch before judging? Options: (a) no change, (b) tell the player when resist blocks Mirror Flip, (c) review after C-02 and C-04 land. |
| D-07 | **Heat escalation feels like piling on**, though the flatline cost is shown up front. | mothball, static_fox, tinroof | Flatline is +11 each time. Raids came at 25 and 50 (mothball §3). Heat went 0→43 (static_fox §3). A raid arrived before tinroof understood the basics. | Is raid pacing for early campaigns intended? Options: (a) keep, (b) give a grace period before the first raid, (c) surface the thresholds earlier. |
| D-08 | **Economy pinch.** Schematics ran short of a recruit while Cycles piled up unspent. | tinroof | 20 Schematics at start, 10 spent on Warm Cache, recruit costs 15. 42 Cycles lost on flatline, 58 unspent, no shop found (§5). This is one tester who always picks the leftmost option. | Should early spending be guarded? Options: (a) no change, (b) warn when a purchase blocks a recruit, (c) make a Cycles sink reachable earlier. |
| D-09 | **Mutual kill counts as defeat and permadeath.** | mothball | B-12 | Should a mutual kill be (a) a defeat, as now, but explained on screen, (b) a win, or (c) a distinct outcome? |

## 5. Motion and feel (→ the animation pass queue)

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| M-01 | Perfect landing | not judged | none | cinder_ivy and copperjack said it felt good and read well. tinroof and mothball said they could not tell what landed. |
| M-02 | Combat preview updates | not judged | none | cinder_ivy said the previews flicker too much to feel impactful. Possibly linked to B-10. |
| M-03 | Netrun intro cutscene | not judged | none | static_fox wanted to skip it (Space: SKIP is offered). The loot and screen transitions that stalled were worse (B-01). |

## 6. What worked (keep)

- **Preview chips** (LETHAL, skulls, exact HP deltas) were clear and matched results on most turns: copperjack, static_fox, mothball, cinder_ivy.
- **Landing a Perfect** felt earned: cinder_ivy, copperjack and static_fox all named one as their favourite moment.
- **Raid projection was readable and matched the playout** (Home 50→40 HOLDS): mothball, static_fox.
- **Flatline Heat cost shown up front** on the site panel: static_fox, tinroof, copperjack.
- **Save/Continue held campaign state** (Heat 11/34/50 restored): mothball. The title offered CONTINUE after Quit: copperjack.
- **Failure screens state permadeath plainly**: mothball.
- **Tooltips give exact numbers**: static_fox, mothball. Staging Brute Spin and Jolt to dodge a lethal slice felt like a real puzzle: static_fox.
- Quick HQ visits and the free rookie hire (static_fox). The look (tinroof).

## 7. Proposed actions

1. **Slice items.**
   - P1 bugs: B-01, B-02, B-03, B-04, B-06, B-07. B-07 should follow C-10, and needs a human repeat first.
   - P2 bugs: B-05, B-08, B-09, B-10, B-11, B-12, B-13, B-14.
   - Clarity: C-01, C-02, C-03, C-04, C-05, C-06, C-07, C-08, C-09, C-10.
2. **Checkpoint items for the designer:**
   - D-04: is the RESPIN undo lock intended (warn / unstage / refund)?
   - D-01: should heal access change once teaching lands (keep scarce / surface existing heals / add retreat)?
   - D-02: what is the target fight length (teaching only / in-fight hint / revisit after a skilled batch)?
   - D-09: how should a mutual kill resolve (explained defeat / win / distinct)?
   - D-03: is the between-turn re-spin intended (keep / signal / carry over)?
   - D-05: should inner-ring cards be offered without an inner ring (gate / state requirement / leave)?
   - D-07: is early raid pacing intended (keep / grace period / earlier thresholds)?
   - D-06: is card value judged too early (no change / resist feedback / review later)?
   - D-08: should early spending be guarded (no change / purchase warning / earlier Cycles sink)?
3. **Next batch:**
   - Have a human repeat the input items first (B-01–B-05, B-07, B-08).
   - Rerun 5 testers on the same build after the P1 fixes and C-02/C-04/C-05, with at least 2 experts so difficulty and length (D-01, D-02) can be read from players who align for Perfects.
   - Give one tester the raids focus with explicit stationing (C-10) to test the defended-raid projection.
   - Add a motion judge with contact sheets for the Perfect landing and the preview updates.