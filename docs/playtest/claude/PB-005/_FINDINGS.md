# Playtest findings — PB-005 · build 19ad76a3a10c260a760667a0d6dde27156508740 · 2026-10-12

> Synthesised from 1 Claude playtest report, its screen audit and motion judgements
> (docs/process/05_CLAUDE_PLAYTESTER.md §9). Every finding names the testers who hit it and the
> evidence (report section, shot or contact sheet). Ingest per doc 04 §3: bugs and clarity items
> become slice items; balance and design items go to the checkpoint for the designer's ruling.

## 1. Headline

- This batch has one expert tester (nullpoint, focus raids), so every finding is single-tester. The tester rated the session **4/10**. The wheel combat interested them, but a forced corridor map ended in a death they felt they couldn't avoid.
- **Where they got stuck:** every route node had one option (Fight L2 → Fight L3 → forced Rack L4). There was no heal, shop or event. Breaker 1 entered the Rack at 11/60 HP, the Rack's opening preview was -11, and Breaker 1 died (nullpoint §3, §6; 0104, 0113).
- **How far they got:** 1 netrun started, 0 completed, T1, 1 operative death. The tester reached **no raid**, so the raid focus questions (§5) are all unanswered.
- **Combat preview trust:** in two cases the preview disagreed with the outcome. One was against a healer (Triage Unit) and one was after Freeze.
- **Harness:** a UnicodeEncodeError in the harness's own log print crashed it at 21.6 min (now fixed). This cost the remaining session time. It is not a game bug.
- **Trend:** no previous batch was provided, so there is nothing to compare against.

| Metric | This batch | Previous (none) |
|---|---|---|
| Testers (novice / intermediate / expert / motion) | 0 / 0 / 1 / 0 | n/a |
| Furthest progress | Netrun 1, died on L4 Server Rack; T1; 0 raids | n/a |
| Avg enjoyment (1–10) | 4.0 (n=1) | n/a |
| Avg RNG fairness (1 fair – 5 cheated) | 4.0 (n=1) | n/a |
| Bugs reported (deduplicated) | 7 raw: 5 game bugs in §2, 2 polish items moved to §3, 1 harness-only | n/a |

## 2. Bugs (→ slice items; P1 = fix before the next gate, P2 = next slice)

| ID | Sev | Area | Bug | Testers | Repro (from the reports) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| B1 | P2 | rules | The lethal preview didn't kill. The preview showed -18 against Triage Unit at 14 HP, but the enemy ended at 2/45. The tester suspects the preview ignores the enemy's heal or block. | nullpoint | Fight 3 (L3), turn 8, SEND IT at 15.2m | nullpoint §2, §7 #1; 0094/0095 | single |
| B2 | P2 | rules | Freeze landed (FROZEN tag shown), but the -3 lethal preview on the player didn't change. It is unclear whether the preview ignores Freeze or Freeze doesn't stop that hit. | nullpoint | L4 Rack, Freeze played at 19.2m | nullpoint §2, §7 #2; 0111 | single |
| B3 | P2 | screens | Firmware drop: both offers target Slot 1, so one offer is useless. | nullpoint | Firmware drop at 16.6m | nullpoint §7 #6; 0102 | single |
| B4 | P2 | screens | Tutorial popups appeared in the first fight after the tester skipped the tutorial. | nullpoint | Skip tutorial, start the first fight, popups at T1 (2.6m); the Skip button dismissed them | nullpoint §4 Controls, confusion log 2.6m | single |
| B5 | P2 | combat | Fine Tune, then clicking the wheel body, did nothing three times, with no hint on the wheel. | nullpoint | Combat L3, Fine Tune, then a wheel click ×3 at 13.9m | nullpoint §4, §7 #3; 0086 | unconfirmed-input (needs a human repeat) |

## 3. Clarity and UX (→ slice items, ranked by how many testers it cost)

| ID | Area | Problem | Testers (of n) | Time lost / what resolved it | Evidence | Suggested direction |
|---|---|---|---|---|---|---|
| C1 | city | **Route map: no clear "pick the next node" step.** The single-option route panel ("Rack +2 Heat > Elite fight · Event") isn't linked to a map node. It is unclear whether the player picks on the map or in the panel, or whether numbered nodes are forced or alternatives. | 1 of 1 | 17.2m: checked Grid View and found no alternative | nullpoint §3, confusion log 17.2m; audit 0104, 0007, 0103 | Explicit pick prompt; link panel rows to map nodes |
| C2 | city | **Route map: node types and path are hard to read.** The node icons are tiny and similar, with only a slight ring-colour difference. The nodes, dashed path and tier badges blend into the busy city art. | 1 of 1 | Needed hover to tell node types apart | nullpoint §4; audit 0054 (colour_only), 0031, 0104 (low_contrast), 0103 | Distinct shapes per node type; contrast backing behind nodes and path |
| C3 | screens | **Loot sheet state is ambiguous.** Space only highlights card 1, the lit card looks already taken, and Continue takes the lit card. The footer "x1 CARD TAKEN" conflicts with "PICK 1 OF 3". A clipped "2x NUDGE" tooltip covers the HUD. | 1 of 1 | 5.7m | nullpoint §4, §7 #5; 0029/0030; audit 0029 (×3) | Separate highlighted and picked visuals; make Continue's effect explicit |
| C4 | combat | **Card text is clipped and the hand overlaps.** Mirror Flip reads "Blocked while th...", and overlapping cards hide costs. | 1 of 1 | Not resolved | nullpoint §2; audit 0012, 0011 | Fit or wrap descriptions; fan the hand so costs stay visible |
| C5 | combat | **Combat numbers are unexplained.** Turn-1 RAM is 6/12 with no reason given. The dial markers (1/0, +10, +6) are unexplained, and the "LAST TURN" captions are hard to read. | 1 of 1 | 6.6m; never resolved | nullpoint §2, §4, confusion log 6.6m | Tooltip or legend for the RAM cap and dial markers |
| C6 | city | **The goal and jargon are unexplained.** The TARGET label marks a different node than the selected site. The dossier terms (IF STATIONED (RAIDS), HUB CORE, Heat/COOL, Cycles) and the lock icons are cryptic. | 1 of 1 | Not resolved | nullpoint §4; audit 0054, 0005, 0007 (inconsistent_term) | Explain the goal and glossary on first view |
| C7 | screens | **The PROCEED button is hidden under the LOOT sticker** on the fight-won screen. | 1 of 1 | 5.5m | nullpoint §4, §7 #4; 0028 (audit major) | Move the sticker off the button |
| C8 | screens | **HQ Market hover tooltips don't line up with their buttons.** | 1 of 1 | 21.4m: resolved by hovering back and forth | nullpoint §3, confusion log 21.4m | Anchor each tooltip to its button |
| C9 | screens | **The HP max is hidden behind the AT LARGE stamp** on the dossier. | 1 of 1 | Not stated | nullpoint §4 | Keep the stamp clear of the stats |
| C10 | screens | **The main menu number stickers are unexplained.** The stickers (1 BREACH / 2 SIMULATE / 3 OVERTHROW) aren't tied to the buttons, and BREACH shows a lock with no reason. | 0 of 1 (audit only) | n/a | audit 0002, 0003 (merged) | Label or align each sticker with its button; explain the lock |
| C11 | combat | **The tutorial panel is a dense wall of text** that covers several concepts at once and sits over the battlefield. | 0 of 1 (audit only) | n/a | audit 0011 | Split into steps; move the panel off the centre |

## 4. Balance and design signals (→ checkpoint items for the designer; never straight into tuning)

| ID | Signal | Testers | Evidence | Question for the designer |
|---|---|---|---|---|
| D1 | **The netrun is a corridor with a forced Rack.** Every next node had one option and there was no heal, shop or Terminal, though the legend lists EVENT, SHOP and ELITE. The tester reached the Rack at 11/60 HP, faced a -11 opening preview, and died. They called this unearned. It was their top frustration and their one change. | nullpoint | nullpoint §3, §6, confusion log 17.2m; 0104, 0113; batch stats | Is the single-path layout intended at T1? Options: (a) guarantee at least one branch per layer, (b) guarantee a heal, shop or event before a Rack, (c) let a low-HP operative skip or retreat from a Rack, (d) keep it as is. If it is not intended, route it to a city bug. |
| D2 | **Inner-ring cards are offered to a deck with no inner ring.** Inner Drift, Inner Snap and Gear Shift were offered; Inner Drift raised an error banner and the pick was wasted. | nullpoint | nullpoint §2, confusion log 13.3m; 0080 | Should the loot pool (a) filter out cards the current wheel can't use, (b) keep them but mark them unusable, or (c) stay as is because the wheel is meant to gain an inner ring later? |
| D3 | **Patch+ was called overpowered** on the 12 slice (it became an 18). | nullpoint | nullpoint §2; batch stats | Is Patch+ on high slices the intended power spike? Options: (a) watch it over more testers, (b) review its scaling, (c) accept it. |
| D4 | **Bulkhead was called dead** on an offensive slice. | nullpoint | nullpoint §2 | Should Bulkhead (a) gain value on any slice, (b) be offered only when a defensive slice exists, or (c) stay situational? |
| D5 | **The deck had no answer to a healer.** The deck stayed "a small, random-feeling pile", the loot didn't build toward anything, and the tester often sent turns with most of their RAM unspent. | nullpoint | nullpoint §2 | Should early loot (a) steer toward an archetype, (b) add anti-heal or burst options, or (c) stay random? Is unspent RAM an intended signal? |
| D6 | **The Defence tab was empty with only a hint**, so there was nothing to set up for raids yet. | nullpoint | nullpoint §3, §5 | Is an empty Armory before the first completed netrun intended, or should the player start with a minimal defence kit? |

## 5. Motion and feel (→ the animation pass queue)

| ID | Moment | Verdict | Sheets | Problem |
|---|---|---|---|---|
| — | No motion judgements in this batch | — | — | — |

## 6. What worked (keep)

All of the following come from one tester (nullpoint).

- **Wheel preview of where a Firmware chip lands, plus the free Q nudge onto a good slice.** These were the tester's favourite moments (§2, §6).
- **Enemy needle preview, damage chips and the FROZEN tag** are clear and readable (§4).
- **Fast HQ loop after death** (§3).
- **A clean 4-turn lethal on the Dosage Dispenser** (§6).

## 7. Proposed actions

1. **Slice items:** bugs B1, B2, B3, B4 and B5 (human repeat first). There are no P1 bugs this batch. Then clarity items C1, C2, C3, C4, C5, C6, C7, C8, C9, then the audit-only items C10 and C11.
2. **Checkpoint items for the designer:** D1 (route branching and the forced Rack), D2 (inner-ring loot filtering), D3 (Patch+), D4 (Bulkhead), D5 (healer counterplay and early loot direction), D6 (empty Defence tab). Each is phrased as a question with options in §4.
3. **Next batch:**
   - Rerun the raid focus with several testers and enough session time to complete a netrun and reach a raid. The §5 focus questions are still unanswered.
   - Add novice and intermediate testers.
   - Repeat the Fine Tune wheel click (B5) with a human.
   - Retest the healer and Freeze preview cases (B1, B2) to move them from single to confirmed.