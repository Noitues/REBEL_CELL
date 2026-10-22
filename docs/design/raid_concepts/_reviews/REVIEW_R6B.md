# Raid concepts G, H, P, HP: independent critic review (R6B)

Scope: 56 frames (plain and scrambled, all viewed at full size), the four SPECs, RULES.md and DEPTH.md. I spot-read
`concept_p6_stakes.py`, `concept_hp6_merged.py` and `bastion_campaign.py` to check frame numbers against stated rules.
Visual polish is not scored. 7 = what a good shipped game does. 9+ = best in class.

## 1. Score table

| Concept | What/why/when | Predictability | No-words | Decision depth | Consequences | **Total /50** | Verdict |
|---|---|---|---|---|---|---|---|
| **G** Merged Telegraph | 7 | **8** | 6 | 4 | 6 | **31** | The best telegraph of the four, on a puzzle that its own draft coins solve for you. |
| **H** Bastion | **8** | 6 | 6 | 6 | 7 | **33** | The only structural fix for "one right answer", but its forecast hides the investment payoff that is its whole point. |
| **P** Stakes | 7 | 5 | 5 | **7** | **7** | **31** | Real "what do I give up" choices that reach the deckbuilder loop, but the prices on the cards are wrong or missing. |
| **HP** Bastion+Stakes | 8 | 5 | 5 | 6 | 7 | **31** | On paper it has the highest ceiling. In practice it is H re-run with P's rules, and the shown line never fires them. |

No concept reaches 9 on any axis. The barriers are in section 4.

---

## 2. Per concept

### G: Merged Telegraph (anchor)

**Justifications**
- **What/why/when 7.** `0_netrun.png` gives the full chain: a Heat bar with the raid size per tier, "51 > 50 → raid", a dial
  for netruns until home, and a cobalt ring where the raid lands. `1_warning.png` draws every route end to end.
  It loses points for two reasons. Only the current raid is telegraphed, so the next tier's raid is a surprise until
  `7_next_raid.png`. And the size pips on the Heat bar (`0_netrun.png`) are tiny shields that read as decoration.
- **Predictability 8.** Fixed routes plus per-node outcome tags (`✓ -5`, `TAKEN`) that update with placements
  (`3_planning.png`: what-if "lost 2 > 1, net -36 > -27"). `4_forecast.png` adds three ranked plans with a full net box
  (+12 kills, +6 clean, -8 patch = +10). That checks out against the tags (Relay 5 + Proxy 3). This is the closest any
  concept gets to Into the Breach. It is held at 8 for these reasons:
  - The attack order lives in a bottom strip of 7 chips, not on the board. ITB puts the numbers on the units.
  - The Lockdown link is drawn **teal**, the Cell's "good" color, in `7_next_raid.png`.
  - The draft coins in `7_next_raid.png` render old/new values as an overstruck mash ("+3 1̶ 3").
  - The aftermath projection in `6_aftermath.png` assumes "the same pieces left in place". That is a line the player
    cannot actually play, because G re-drafts every raid.
- **No-words 6.** The scrambled frames read nearly the same as the plain ones, because so much is iconic. The map
  layer (arrows, red X, flags, check tags) passes. The economy layer does not: `ⓘ` coins, `✖4 • ○` stat lines on draft
  cards, kill-cam inset, and the net box (`4_forecast.png` scrambled) all need learning.
- **Decision depth 4.** `2_draft.png` prints each card's marginal value (Turret +1, ICE +6, Decoy -7, Sentry -1,
  Railgun +11). The top three coins *are* plan 1 in `4_forecast.png` (Turret, ICE, Railgun, +10). The draft is
  answered by the UI. DEPTH.md agrees: the same best draft in 8 raids of 10, and 2.6 drafts within 3 net. The three
  forecast plans are all "home -0" and within 6 net of each other. That is a spreadsheet with the answer pre-filled.
- **Consequences 6.** The CLEAN stamp, the net, and TAKEN flags and scuffs that persist on the map are all legible
  (`6_aftermath.png`). The per-node patch choice is fake, though: patch all (-8, then -22) totals -30, skip Relay -35,
  skip all -32. One row dominates. Losses cost only Schematics, so nothing touches the netrun/deck loop. A CLEAN
  verdict is followed by a projected -22 next raid, which is honest but deflating.

**3 biggest problems**
1. The marginal-value coins solve the draft. Decision depth collapses to "pick the three biggest numbers".
2. Losses fold into one currency, so every plan reduces to one net. DEPTH.md shows this is structurally dominant.
3. The playout is 9 beats + 3 kill-cams = 15 s (`5_resolution.png`), under D26's 20 s floor. The order is shown in a
   strip, not on the pieces.

**3 most valuable ideas**
1. Fixed routes as the telegraph ("a path is a promise"), with per-node outcome tags that update live while placing.
2. The net box in report units (kills / clean / patch / net), identical before and after the raid.
3. The what-if chip on placement (`3_planning.png`): one number delta per move.

**Refs used:** Kingdom Rush route arrows (`sheet_G_warning_vs_kingdomrush.jpg`); PvZ seed selection beside the zombie
roster (`sheet_G_draft_vs_pvz.jpg`); Into the Breach numbered attack order on the board (`sheet_G_forecast_vs_itb.jpg`);
Super Auto Pets rewind/pause/fast/skip (`sheet_G_resolution_vs_sap.jpg`).

**What would raise each axis by 2**
- *What/when 7→9:* telegraph the next two tiers' rosters on the Heat bar (H's strip) and keep the landing ring.
- *Predictability 8→10:* move the order numbers onto the shooters and targets on the map (ITB). Draw Lockdown cobalt.
  Render draft value changes as "old → new". Drop the "same pieces" projection, or project with the best re-draft.
- *No-words 6→8:* replace `✖4 • ○` with drawn reach rings and target glyphs on the card art. Make the net box a stacked
  bar (green in, red out) instead of four signed numbers.
- *Depth 4→6:* remove the marginal-value coins, or show them only after commit as a lesson. Make the draft come from
  pieces earned this run (DEPTH lever 2).
- *Consequences 6→8:* let losses hit jobs (P), and make the patch choice a real trade (for example a skipped patch
  keeps a cheap scuff that draws the next route, against Schematics now).

### H: Bastion

**Justifications**
- **What/why/when 8.** This is the best in the set. `0_campaign.png` puts all three raids of the leg on the Heat bar,
  with rosters at 25/50/75 and their corp entry sites, from visit 1. Thronefall and Defense Grid 2 both show the
  incoming waves before the build. It misses 9 for two reasons. There is no netrun dial in any H frame, so "when" is
  only a Heat value. And the Heat-50 roster row in `0_campaign.png` floats with no site attached, unlike the 25 and 75
  rows.
- **Predictability 6.** The per-raid forecast is G's, and it checks out. In `2_forecast.png`, kills 2 (+8), clean +6,
  patch -15 (Relay 9 + Vault 3 + Proxy 3) gives -1. The bank arithmetic holds across every frame (14 → 0 → -1 → +12 = 11
  → buy 11 → +15 → 15 → +12 −15 → 12 → +22 → 34). The **fortress forecast**, though, runs "no more buys". In `1_shop.png`
  the home line ends at -33 and the forward line at -35. That is a 2-point gap between lines that the record
  (`7_record.png`) shows end 37 apart. The one prediction H exists to make, "this buy pays off later", is the one it does
  not show. `3_resolution.png` also overlays two damage numbers ("-32") and has no clock.
- **No-words 6.** The map and the bank line (`7_record.png` scrambled) read without words. "-1 +12 ⬡ → 11" in
  `4_aftermath.png` reads. The shop's forecast rows are three columns of tiny struck glyphs, which are hard even with
  words.
- **Decision depth 6.** It is real at visit 1: the first purchase differs from greedy in 4 of 5 campaigns. Two caveats
  from the code:
  - GREEDY (`bastion_campaign.py`) maximizes the bank *after this raid, net of the purchase*. That charges a persistent
    asset as a consumable, so it is a strawman. A human who knows that pieces persist will not play like it. "Buy the
    big gun at home" is likely close to PLANNED, and that heuristic was not measured.
  - The sample is 5 campaigns.

  After visit 1 the depth drains away. `5_visit2.png` and `6_visit3.png` are CLEAN with every node checked, and raid 3
  is 4/4 kills. Once the fortress is right, raids are a formality. The shop cards show price only: no value and no
  target.
- **Consequences 7.** Persistence is the strongest of the four. Pieces stay on the map between raids, a TAKEN node
  destroys its pieces, and the bank line is a campaign record (`7_record.png`, compare Backpack Battles' wins/tries).
  The shown campaign never loses anything, so the cost of failure is only visible as a grey counterfactual line.
  A CLEAN raid 1 nets -1 in red, so success is framed as loss.

**3 biggest problems**
1. The fortress forecast hides the investment payoff (-33 vs -35 against an actual 34 vs -3).
2. Late raids go slack: a correct fortress makes raids 2–3 trivially CLEAN, with no corp counter-adaptation except
   Lockdown.
3. The depth claim rests on a strawman baseline and 5 campaigns.

**3 most valuable ideas**
1. The defense persists and depth lives in investment. This is the only lever in DEPTH.md that breaks the
   near-dominant answer without new content.
2. The whole leg is telegraphed on the Heat bar, with rosters and entry sites.
3. The bank line as the campaign record: one chart, readable without words.

**Refs used:** Defense Grid 2 wave strip + cores (`sheet_H_campaign_vs_dg2.jpg`); Thronefall map-badged enemy groups
during building (`sheet_H_shop_vs_thronefall.jpg`); They Are Billions persistent colony vs the big wave
(`sheet_H_visit3_vs_tab.jpg`); Backpack Battles run record (`sheet_H_record_vs_backpack.jpg`).

**What would raise each axis by 2**
- *What/when 8→10:* add G's netrun dial per telegraphed raid ("this one in about 2 netruns at your current pace"). Attach
  every roster row to its entry site.
- *Predictability 6→8:* show two forecast lines per candidate buy: "no more buys" and "with a typical follow-up" (one
  greedy follow-up buy per visit, which is cheap to compute). Show the bank delta on the hovered shop card. Add the beat
  clock and numbered shots to the playout.
- *No-words 6→8:* replace the per-raid glyph rows with a mini bank sparkline per line, which the record already proves
  reads.
- *Depth 6→8:* add escalation that answers the fortress. Telegraphed rosters gain one counter-piece aimed at your most
  stacked node (a generalized Lockdown, shown at telegraph time). Add P's node jobs so that *where* the fortress sits
  costs something.
- *Consequences 7→9:* tie income to jobs (Vault +3/netrun instead of a flat +12). Show what a TAKEN node took (pieces +
  job) as a ghost on the map until it is reclaimed.

### P: Stakes

**Justifications**
- **What/why/when 7.** The same chain as G, plus the jobs on the nodes at warning (`1_warning.png`). The link from the
  Proxy's intel job to the dial (`6_next_raid.png`: the dial starts at 2 because the Proxy fell) makes "when" a stake
  in its own right. Only one raid is telegraphed.
- **Predictability 5.** This is where P breaks.
  - `concept_p6_stakes.py: patch()` sums **scuffed** points only. Plan 3 in `3_front.png` ("gives up Safehouse + Proxy",
    **patch -0**) prices losing two nodes at zero. Their repair or reclaim cost is real and hidden, and the card makes
    the worst-looking trade look free.
  - The front cards show no kills, salvage or net. `5_aftermath.png` shows "-10" with no payout, while RULES says the
    +4/kill salvage still applies.
  - `6_next_raid.png` draws the Proxy whole on the map (the code calls `G4.base(d)` without the result) while its job is
    struck. The map contradicts the report.
  - `4_resolution.png` drops the shot numbers and the beat clock.
  - The planning frame shows plan 1's layout, but plan 2 is played. The railgun jumps from the Vault (12) to home (8).
- **No-words 5.** The job badges add a fifth layer of small glyphs (`ⓘ+3`, `⬡+1`, person, crosshair, eye). Struck-out
  jobs read well (`3_front.png` scrambled). The next-raid frame fails: the real roster (2 threats) and the plan-4
  counterfactual inset (4 threats) are two identical panels told apart only by a small "4".
- **Decision depth 7.** This is the best per-raid puzzle. 3.9 distinct "what you give up" sets, and 60 % of raids have 3
  or more (DEPTH.md). Sacrificing a node to save income is the Into the Breach "grid vs objective" trade, and survivors
  who rejoin give kills a future value (Defense Grid's carried cores). It is held at 7 because the job values are not
  modeled anywhere in the numbers. The front's breadth is measured, but nobody knows whether the options are close in
  value. If Proxy intel ("one netrun earlier") is weak, plan 2 is simply the answer every time.
- **Consequences 7.** This is the most motivating consequence design: losses reach the deckbuilder loop (Vault income,
  Relay branches, crew, home's gun, intel) and persist until repaired. HOLDS with a struck job (`5_aftermath.png`) is
  legible. The missing repair price and the map that "heals" the Proxy undercut it.

**3 biggest problems**
1. Wrong prices: patch excludes lost-node repair, payout is missing from cards and aftermath. Every comparison on the
   front is skewed toward giving things up.
2. Job values are unmeasured, so the front's breadth may be cosmetic.
3. A counterfactual inset that looks like the real roster, and a map that contradicts the report.

**3 most valuable ideas**
1. Every node has a job drawn on it. Losses are felt in the run, not only in Schematics.
2. The forecast shows the front of non-dominated plans, framed as "what you give up" rather than one score.
3. Survivors rejoin: kills deny reinforcements, so a cheap plan has a visible future cost.

**Refs used:** The Bazaar encounter choice with rewards up front (`sheet_P_front_vs_bazaar.jpg`); Into the Breach
objectives and persistent grid (`sheet_P_aftermath_vs_itb.jpg`); Defense Grid 2 carried cores
(`sheet_P_next_vs_dg2.jpg`); Backpack Battles per-item damage log (`sheet_P_resolution_vs_backpack_log.jpg`).

**What would raise each axis by 2**
- *What/when 7→9:* telegraph the next tier too, and show survivors walking back to their corp site on the map.
- *Predictability 5→7:* put the full price on each card: salvage, scuff patch, **repair/reclaim cost of each lost
  node**, and net. Draw lost nodes as lost in every later frame. Restore numbered shots and the clock.
- *No-words 5→7:* show the counterfactual inset only on hover over its card, ghosted and dashed. Cut the job badges to
  one glyph each, shared with the netrun-map icons.
- *Depth 7→9:* value the jobs in the harness (income per netrun × netruns to the next raid, and so on). Tune them so the
  front's plans sit within a few points of each other. Draw the draft from what the run earned.
- *Consequences 7→9:* make job loss visible on the netrun map (a missing branch, a greyed Vault income tick) the next
  time it bites.

### HP: Bastion + Stakes

**Justifications**
- **What/why/when 8.** H's leg telegraph plus jobs on the nodes (`0_campaign.png`). It has the same gaps: no dial, and
  the Heat-50 row has no site.
- **Predictability 5.** The carry-rule forecast is the one place survivors become visible. In `1_shop.png` the rosters
  grow by outlined survivors and line 2 ends at -46. It keeps H's "no more buys" flaw (home -36 vs forward -46, while the
  played record is 34 vs -11). `2_forecast.png` has an empty survivors panel ("→ ⬡" with nothing in it). The jobs do not
  enter the bank: `play()` and `forecast()` in `concept_hp6_merged.py` use `net(r)` only.
- **No-words 5.** This is the densest shop. Each forecast cell stacks a roster, struck job glyphs and a bank number at
  icon size (`1_shop.png` scrambled).
- **Decision depth 6.** It has the potential for the most depth, but HP measured none of its own. The two lines are H's
  lines re-run under the carry rule, not re-optimized. In the line shown, the home line kills everything, so neither
  jobs nor survivors ever fire. `3_aftermath.png`, `4_visit2.png` and `5_record.png` are H with extra badges.
- **Consequences 7.** The forward line's survivors compound (-3 under H becomes -11), which proves the carry rule has
  teeth. Jobs persist. The same "CLEAN = -1" framing as H.

**3 biggest problems**
1. There is no evidence that the merge adds depth: no re-optimized lines, and jobs are not valued.
2. It inherits H's hidden investment payoff, and adds glyph density on top.
3. The shown campaign never exercises the P half.

**3 most valuable ideas**
1. The carry rule *in the multi-raid forecast*: letting a threat live visibly fattens a telegraphed raid.
2. Jobs give the fortress's location a cost, which answers H's "late raids go slack" problem in principle.
3. One unified record (bank line) that both rule sets feed.

**Refs used:** The Last Spell map-tiled night threat (`sheet_HP_shop_vs_lastspell.jpg`); Rogue Tower target priority
and price panel (`sheet_HP_draft_vs_roguetower.jpg`); Defense Grid 2 cores (`sheet_P_next_vs_dg2.jpg`).

**What would raise each axis by 2**
- *What/when 8→10:* the same changes as H.
- *Predictability 5→7:* the same as H, plus fold the job value into the forecast bank. Delete empty panels.
- *No-words 5→7:* use one sparkline per line, with survivors drawn as extra pips on the roster box rather than more
  icons.
- *Depth 6→8:* run PLANNED vs heuristic play under the HP rules with jobs valued. Show a campaign where the forward line
  is tempting (a job worth defending forward).
- *Consequences 7→9:* the same as H.

---

## 3. Ranking and what to take forward

**Ranking:** H (33) > G = P = HP (31). Among the 31s, P has the best puzzle, G the best telegraph, and HP the best
ceiling with the least evidence.

**Take forward: H and P.** H fixes the structural single-answer problem (investment across raids). P makes losses
matter outside Schematics, and that is what gives an H fortress a reason to be placed anywhere but at home. G's
telegraph package is already shared by all of them and stays as the base. HP is the eventual merge, but only after the
measurements below exist.

**Steals**
- **H steals from G:** the netrun dial, live what-if chips, numbered shots and beat clock. G's *marginal coin* also works
  in H's shop, if it is computed over the leg ("this buy, over 3 raids: +N"). That is the honest version of H's missing
  payoff.
- **H steals from P:** node jobs, so a home-only fortress gives something up.
- **P steals from G:** the full net box on every card, and the resolution playout.
- **P steals from H:** the multi-raid telegraph strip, so "survivors rejoin" lands on a raid the player can already see.
- **G steals from P:** the front framing in place of three nets within 6 points of each other.

**Prototype first: H.** It is the cheapest change with a measured effect. Persistence plus a shop is mostly state and
view work on top of the existing resolver. It needs no new content, and it tests the riskiest claim directly: whether a
human finds the investment line without the beam search. Instrument it with the "typical follow-up" forecast line, and
measure a human against GREEDY and a "big gun at home" heuristic. Add P's jobs in the second prototype pass, valued in
the harness first.

---

## 4. Barriers to 9+ for the best concept (H)

Every item is a **designer decision**.

| # | Barrier | Axis it caps | Change that lifts it | Cost |
|---|---|---|---|---|
| B1 | **Fortress forecast is "no more buys" only** (H SPEC). | Predictability, Depth | Add a second projected line per candidate buy (one greedy follow-up buy per visit), plus a leg-wide marginal value on each shop card. | One beam-free sim pass per hover (precomputable). Risk: it solves the shop for the player, so show the line, not a "best" badge. |
| B2 | **Fixed 5-piece pool on a 6-node map** (content limit; DEPTH: near-dominant answer is structural). | Depth | Pieces earned in netruns (rewards, shops), so each run's Armory differs. | Content and reward work; ties raid depth to the deckbuilder economy, which is good. |
| B3 | **Static telegraphed rosters**: a correct fortress makes raids 2–3 trivial (`6_visit3.png`). | Depth, Consequences | Corp counter-adaptation shown at telegraph time: each tier adds a counter aimed at your most stacked node (generalize Lockdown). | One rule plus a test per counter. It keeps the telegraph honest because it is shown when the roster appears. |
| B4 | **D26: step-locked, readable 20–40 s playout.** H raid 1 is 3 steps, and G's beat rule gives 15 s. Padding to 20 s makes small raids drag, while 40 s caps big HP rosters (8 threats). | Fit with hands-off, No-words | Change it to "one beat per event, 10–40 s, with skip", and add a **post-raid scrubber/replay** (Super Auto Pets has rewind). Zero input during play stays. | Small: a ruling text change and view work. A scrubber does not break hands-off. |
| B5 | **D27: a clean defense gains Heat, any damage gains none.** The package already overrides it ("raids do not move Heat"). Under H, D27 punishes the correct fortress: every CLEAN pulls the next raid closer. It also rewards taking a deliberate scuff to avoid Heat. That is a perverse incentive that no forecast can make feel fair. | Consequences, Depth | Retire D27 in favor of "raids do not move Heat". If Heat must move, make it *damage* that raises Heat (the corp smells weakness), never success. | Ruling change; one test. |
| B6 | **D28: the verdict is only CELL HOLDS or BREACHED.** It erases CLEAN, which is the tier the +6 bonus and every forecast card key on. All four concepts already stamp CLEAN/HOLDS. | Consequences, No-words | Adopt three tiers: CLEAN / HOLDS / BREACHED, with per-node DOWN/TAKEN unchanged. | String and stamp work; a ruling change. |
| B7 | **Payout rule: net = salvage + clean bonus − full repair.** A CLEAN raid shows a red "-1" (`2_forecast.png`, `4_aftermath.png`). Success reads as failure, and the patch choice in G is dominated. | Consequences | Raise the clean bonus to cover typical scuff damage, or let SCUFFED heal 50 % free between raids. Keep full price for DOWN/TAKEN. | Tuning keys in config; re-run the harness. |
| B8 | **Flat +12 income between raids** (H SPEC), unconnected to the netruns. | Consequences, fit with the campaign | Income from jobs (Vault +3/netrun and so on), so a lost node is felt in the run (P). | Needs P's jobs valued; moderate. |
| B9 | **Cobalt threats.** Cobalt does not read as danger without learning. Red is spent on damage, and teal (the Cell's "good") is used for the Lockdown link (`6_visit3.png`, G `7_next_raid.png`). | No-words | Keep cobalt as ruled, but enforce it: every threat-caused effect (Lockdown, routes, survivors) cobalt; red only for loss; teal only for the Cell's good outcomes. Add a cobalt hazard pattern (hatching) on frozen links. | Low; view palette only. Challenging cobalt itself (orange/red threats) would cost a palette rework and collide with Heat orange. Not worth it. |
| B10 | **No netrun-pace "when"** in H (no dial). Heat thresholds are known, but "how many netruns" depends on play. | What/when | Project "about N netruns at current Heat gain" under each telegraphed raid, and keep G's dial for the next one. | View plus a simple projection. |
| B11 | **Depth evidence**: 5 campaigns against a strawman greedy (`bastion_campaign.py` charges purchases to the current raid). | Depth (credibility) | Re-measure against "persistent-aware greedy" and "biggest gun at home" heuristics, over 50+ campaigns, with jobs valued. | Harness time only. |

Package items that stay as they are: fixed routes, home is never a corridor, the weaker tie-break, ICE blocks the
strike, no cascade. They are what make G's predictability an 8, and each is worth its resolver cost. The **3-of-5 draft
(R5)** is worth it in G and P, but it is moot in H, which drops it. Keep it only if the Armory becomes run-earned (B2).

## 5. Sheets built

All under `D:/rc_tmp/raid_design_lab/critic_r6b/`:
- `sheet_G_warning_vs_kingdomrush.jpg`
- `sheet_G_draft_vs_pvz.jpg`
- `sheet_G_forecast_vs_itb.jpg`
- `sheet_G_resolution_vs_sap.jpg`
- `sheet_H_campaign_vs_dg2.jpg`
- `sheet_H_shop_vs_thronefall.jpg`
- `sheet_H_visit3_vs_tab.jpg`
- `sheet_H_record_vs_backpack.jpg`
- `sheet_P_front_vs_bazaar.jpg`
- `sheet_P_aftermath_vs_itb.jpg`
- `sheet_P_next_vs_dg2.jpg`
- `sheet_P_resolution_vs_backpack_log.jpg`
- `sheet_HP_shop_vs_lastspell.jpg`
- `sheet_HP_draft_vs_roguetower.jpg`

Reference contact sheets used for triage are in `work/cs_*.jpg`. New downloads are They Are Billions (8 Steam
screenshots). Sources: `D:/rc_tmp/raid_design_lab/refs/SOURCES_R6B.tsv`, which reuses the prior SOURCES URLs. The
Kingdom Rush wave image is from the prior set. The Hearthstone Battlegrounds wiki images were bot-blocked (an HTML
page came back), so they were deleted unused.
