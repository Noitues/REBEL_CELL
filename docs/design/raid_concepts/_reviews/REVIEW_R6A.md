# Raid concepts G / H / P / HP: critic R6A review

Independent review. Sources: all 56 frames (plain and scrambled) at full size, RULES.md, DEPTH.md, the four SPECs, and spot
checks of `concept_h6_bastion.py`, `concept_p6_stakes.py`, `concept_hp6_merged.py`, `bastion_campaign.py`,
`depth_harness.py` (`net`/`price`) and `sim.py`. Comparison refs are listed per concept. URLs are in `refs/SOURCES_R6A.tsv`.

Note on the no-words test: the scrambled frames scramble only the text. Every icon, color and number stays. So the test
asks whether the glyph vocabulary carries the meaning. It does not ask whether the screens are wordless.

## 1. Scores

| Concept | What/why/when | Predictability | No-words | Decision depth | Consequences | Total | Verdict |
|---|---|---|---|---|---|---|---|
| **G** Merged Telegraph | 8 | 8 | 6 | **4** | 7 | **33** | The best readout of the four, but the UI solves the puzzle: the draft coins and the top-3 plans hand you the answer. |
| **H** Bastion | 7 | 6 | 6 | 6 | 7 | **32** | Real depth across raids, but the shop forecast hides it (the two lines read -33 vs -35 when the truth is 34 vs -3). |
| **P** Stakes | 7 | 5 | 6 | 6 | 7 | **31** | Trading one node job against another is the right kind of choice. The front is a menu the game picked, and its money is wrong. |
| **HP** Bastion+Stakes | 7 | 6 | 5 | 6 | **8** | **32** | The strongest consequence loop. In practice it is H with job stickers: P's front is gone, and its depth is unmeasured. |

Calibration: 9 is Into the Breach's telegraph, 7 is a good shipped game. None of these is a 9 anywhere. G's readout is the
closest, held back by glyph density and the solved draft.

---

## 2. Per concept

### G: Merged Telegraph (round 5 anchor)

**Justifications.**
- **What/why/when: 8.**
  - `0_netrun.png` has the whole chain: Heat bar with tier ticks and the threat count per tier, "51 > |50 → shield"
    (the why), the netrun dial "2" (the when), and the cobalt ring on home (the where).
  - Below 9 because the tier pips, the dial and the roster chips (`12/5`, corner glyphs) form a small legend the player
    must learn before any of it reads.
- **Predictability: 8.**
  - Fixed routes plus per-node tags (`1_warning.png`) and the forecast in `4_forecast.png`: per-node ✓/−N tags, the net box
    (3 kills = +12, +6 clean, −8 patch = +10, which reconciles), and attack-order chips (step, gun, target, damage) in the
    ITB style.
  - `5_resolution.png` numbers its shots, and the clock counts beats plus kill-cams.
  - Deductions:
    - in `7_next_raid.png` the struck old values overprint the new ones on every card (it reads "+3/1 3", "+3/11 3");
    - the Railgun card still flags the Enforcer as its target, although plating now nullifies it;
    - in the aftermath, every option's next-raid projection is negative (−22 / −32 / −32), and it never says whether
      that number already includes the patch spend.
- **No-words: 6.** Routes, red X and TAKEN flags survive the scramble (`scrambled/1_warning.png`). But the forecast is
  glyph soup (`scrambled/4_forecast.png`): ✓0, −0, a coin with +10, ∞ with a red corner, struck icons, and a 7-chip
  attack strip. That is a spreadsheet in icons. The meaning of "SCUFFED" (✓ with a red corner and −5) cannot be guessed.
- **Decision depth: 4.**
  - DEPTH.md: the same best draft in 0.8 of raids, and 2.6 drafts within 3 net. Structurally there is near-one answer.
  - Worse, the UI publishes it. In `2_draft.png` each card's coin is its marginal value over the full sweep
    (Railgun +11, ICE +6, Turret +1, Sentry −1, Decoy −7), so "take the top three" is the answer.
  - `4_forecast.png` then lists the three best plans. The player is choosing from the solver's output.
  - The fragility of 0.93 means hand-placing feels like defusing a bomb, not reasoning.
- **Consequences: 7.**
  - CLEAN stamp plus the net box, and persistent TAKEN flags and scuffs.
  - `6_aftermath.png` is a real choice: patch per node, each with a next-raid projection.
  - Two problems. The whole economy reads as a treadmill: the bare raid nets −36 and every next-raid option is negative.
    And the bottom panel covers the Safehouse node and the Depot.

**3 biggest problems.**
1. The marginal-value coins and the top-3 plan list turn the planning into confirming the game's answer (`2_draft.png`,
   `4_forecast.png`).
2. One folded number (net) is the scoring, and DEPTH.md shows that folding always yields a near-dominant plan.
3. Glyph density. The forecast and the next-raid draft (`7_next_raid.png`, with overprinted struck values) need a legend.

**3 most valuable ideas.**
1. The netrun dial plus a landing ring on the netrun map (the "when" in the player's own unit, netruns).
2. The attack-order chip strip and numbered shots in the playout. This is the ITB contract made hands-off.
3. A per-node patch choice in the aftermath, each option with its next-raid consequence.

**Refs.**
- `sheet_01_attack_order_G_vs_ITB.jpg`: ITB numbers attacks on the board itself. G puts them in a strip you cross-reference.
- `sheet_07_routes_G_vs_IsleOfArrows_KR.jpg`: one route per spawn, plus a wave countdown.
- `sheet_02` (SAP playout).

**+2 per axis.**
- **What/when:** put the dial count on the Heat bar ("raid in 2 netruns"), and drop the threat-count pips.
- **Predictability:** draw the attack order on the map at the gun (as ITB does) and retire the strip. Show the
  aftermath projection as patch plus next net. Fix the overprint.
- **No-words:** cut the glyph types per screen to at most 6. SCUFFED becomes a cracked node ring, not a tag.
- **Depth:**
  - remove the marginal coins (show what each card covers, not its value);
  - show one forecast for the player's plan only, not the top 3;
  - stop folding losses into one number (take P's lever).
- **Consequences:** make a CLEAN raid net positive by construction (see barriers). Keep the map unobscured in the
  aftermath.

### H: Bastion

**Justifications.**
- **What/why/when: 7.**
  - `0_campaign.png` pins all three rosters to Heat thresholds from the first visit, the best "what" across the leg of
    any concept.
  - Lost against G:
    - the netrun dial is gone, so "when" is Heat-only;
    - the entry sites show only as tiny "1/2" digits under the chips;
    - the roster rows sit beside the Clinic and the Depot, which implies "raid 1 comes from the Clinic". In
      `1_shop.png` the Courier enters from the Depot.
- **Predictability: 6.** Per raid, it is G's readout without the attack-order strip.
  - The fortress forecast (`1_shop.png`, `5_visit2.png`) prints the **cumulative bank** (code: `bank += net(r)`) with
    the same coin glyph as the per-raid net box, and nothing says which it is. In `2_forecast.png`, "−1" appears in both
    the net box and forecast cell 1, and they mean different things.
  - The forecast is no-more-buys. On the decisive visit it shows home line −33 vs forward line −35. The real lines end
    at 34 vs −3 (`7_record.png`). The forecast is honest and still predicts nothing about the choice that matters.
  - The sim does not model a TAKEN node becoming a corp entry point (entries are drawn from C1/C2 only), so later
    telegraphed raids are optimistic for any line that loses a node.
- **No-words: 6.**
  - `scrambled/7_record.png` (bank line) reads with no words: good.
  - `scrambled/5_visit2.png` and `6_visit3.png` bundle 3 to 4 threats on one path as stacked parallel arrows. You
    cannot count them, nor tell who goes where (`sheet_08`).
  - Overprinted damage numbers ("−32/12") in `3_resolution.png`.
- **Decision depth: 6.**
  - Measured: PLANNED beats GREEDY by 14.8 (37 at most), and the first buy diverges in 4/5 campaigns. That is real
    depth, and the kind a roguelite wants (investment).
  - But it is depth the player cannot see at decision time (see predictability), so it is learned by losing, not by
    reading.
  - Unverified risk: the winning line in campaign 1 is "turtle at home". If PLANNED concentrates on home and Firewall in
    most campaigns, it becomes one learnable heuristic. Measure how often the PLANNED first buy is a home-adjacent node.
  - Per visit, 2 buys plus the crew suits a few minutes of setup.
- **Consequences: 7.** The best persistence of the four: pieces stay and the fortress visibly grows.
  - The record graph is a satisfying campaign summary.
  - Raid 1 is "CLEAN" and still nets −1 (`4_aftermath.png`). A green CLEAN stamp over a red net is demotivating and
    confusing.
  - No frame shows a TAKEN node destroying pieces, which is the consequence that teaches the system.

**3 biggest problems.**
1. The investment payoff is invisible at the shop (−33 vs −35), so the measured depth does not reach the player.
2. The forecast cells (bank) and the net box (raid) use one unlabeled glyph.
3. Bundled routes, and the Heat-only "when" with no netrun dial.

**3 most valuable ideas.**
1. Persistent pieces bought 2 per visit: investment across raids, very cheap in setup time.
2. The whole leg telegraphed from visit 1. It is the SAP tier table / Thronefall wave marker idea applied to a campaign.
3. The campaign bank line as the record (`7_record.png`).

**Refs.**
- `sheet_03_leg_telegraph_H_vs_SAP_tiers.jpg`
- `sheet_04_persistent_fortress_H_vs_RogueTower.jpg`: Rogue Tower's towers persist while the path grows. The investment
  reads on the board, not in a strip.
- `sheet_06_shop_forecast_H_HP_vs_Mechabellum.jpg`: Mechabellum shows both armies before the hands-off round. H shows
  only yours plus a strip.
- `sheet_08_stacked_routes_H_vs_ITB.jpg`

**+2 per axis.**
- **What/when:** restore G's netrun dial. Put an entry hex glyph (not a digit) on each roster chip.
- **Predictability:**
  - label the forecast cells as the bank, and the box as this raid;
  - add an "if you buy X next visit" ghost row, or show the threat strength growth against fortress damage per raid, so
    the home-vs-forward gap shows at visit 1;
  - model TAKEN entries.
- **No-words:** fan out the bundled routes (offset per threat with the threat's chip at the head). Never overprint numbers.
- **Depth:** measure the "turtle home" share. If it is above 60 %, vary the entry sites and node jobs per campaign so the
  right place to invest moves.
- **Consequences:** CLEAN must never net negative. Show a TAKEN node destroying its pieces in at least one frame of the
  forward line.

### P: Stakes

**Justifications.**
- **What/why/when: 7.**
  - G's dial and Heat bar, plus job badges on every node (`1_warning.png`). You see what the raid threatens in terms you
    care about: "the raid as it stands loses PROXY = intel".
  - The roster panel drops G's per-threat route chain. The panel is mostly empty space.
- **Predictability: 5.**
  - The front cards (`3_front.png`) show the drafted pieces but **not where they go**, and the map beside them shows the
    selected plan's outcome with no pieces on it.
  - The card's coin is the patch only, and the code (`patch()`) counts only scuff points. DOWN and TAKEN costs, which the
    shared package prices at half and full install, are omitted, and so is the payout (+4 per kill, +6 CLEAN). So plan 3,
    "gives up Safehouse + Proxy, −0", looks free. Its real net under the package differs. That is the package's money
    rule silently changed, an inconsistency the brief counts as a predictability failure.
  - Plans 1 and 2 use the same three pieces, so the difference is placement only, and it is invisible on the card.
  - In `5_aftermath.png` the Proxy is DOWN. In `6_next_raid.png` it is drawn at full health with intel still struck, and
    nothing explains it.
  - `4_resolution.png` has no numbered shots and no beat clock (a regression from G).
- **No-words: 6.**
  - The job glyphs (coin +3, hex +1, person, crosshair, eye) are well chosen, and a struck job reads instantly
    (`scrambled/5_aftermath.png`).
  - "Nobody returns" (a crossed generic threat → hex) is cryptic.
  - The next-raid inset (`6_next_raid.png`) does not mark which 2 of the 4 threats are survivors.
- **Decision depth: 6.**
  - This is the right kind of choice. Incommensurable stakes (intel vs 9 Schematics vs the crew next raid) make the
    player's run state the tie-breaker, as Backpack Battles' "take the win / survival" does (`sheet_05`).
  - Measured 3.9 distinct give-up sets, and 60 % of raids have 3 or more.
  - But the game enumerates the front and hands it over as a menu. The mockup shows 4 of 8, hand-picked in the code
    (`_WANT`) for a pretty spread. The spatial puzzle becomes "pick a card".
  - The job values are lopsided and thin. Proxy intel is "one netrun earlier", and the dial already gives 2. Relay
    "+1 branch" is hard to price.
- **Consequences: 7.**
  - Lost jobs persist on the map until repaired, and survivors rejoin the next raid. Both are excellent and persistent.
  - The P Heat-75 roster is hard-coded as Courier + Inspector, **2 threats after a 3-threat Heat-50 raid**. That
    contradicts the escalation the Heat bar promises.
  - HOLDS and −10 show no positive side (kills).

**3 biggest problems.**
1. The front is a menu the solver curated. It does not show the placements, and it drops the package's DOWN/TAKEN prices
   and the payout.
2. The jobs are worth too little to anchor a trade (intel is +1 netrun of warning).
3. Playout regressed (no shot order, no clock), and the survivor and repair states are inconsistent between frames.

**3 most valuable ideas.**
1. **Every node has a job, drawn on it.** It turns "node HP" into stakes the player values in run terms. This is the
   single best idea in round 6.
2. **Survivors rejoin.** It makes kills matter beyond salvage and gives every leak a visible future cost.
3. Losses kept unfolded (lost jobs, survivors and patch each shown) instead of one net.

**Refs.**
- `sheet_05_front_P_vs_BackpackBattles.jpg`: the Bazaar shows encounter rewards as icons before you commit.
- `sheet_02_hands_off_playout_G_P_vs_SAP.jpg`

**+2 per axis.**
- **What/when:** keep G's route chain per threat in the roster panel.
- **Predictability:**
  - do not show a front at all; forecast the player's own placement, with the lost jobs struck and the survivors marked;
  - optionally add a "what else could I keep?" hint that names one alternative give-up set without giving its placement;
  - price DOWN and TAKEN per the package; show the payout.
- **No-words:** draw survivors as outlined chips walking back to their corp hex. Draw a repaired node with its job still
  lost as a distinct state, or remove that state.
- **Depth:**
  - make the jobs worth fighting over: Proxy intel reveals the next roster's entries or traits; Relay +1 branch is a
    reward branch;
  - the player places, and the game only tells you what you give up.
- **Consequences:** fix the roster escalation, and show salvage next to the patch.

### HP: Bastion + Stakes

**Justifications.**
- **What/why/when: 7.** H's leg telegraph plus the job badges (`0_campaign.png`). It has the same H faults: no netrun
  dial, and the roster rows are misplaced beside the corp hexes.
- **Predictability: 6.**
  - The carry rule fixes H's worst gap partly. The shop forecast now separates the lines: home −1 / −4 / −36 vs forward
    −1 / −20 / −46 (`1_shop.png`), because survivors swell the later rosters, outlined in the forecast row. That is a
    10-point gap where H showed 2.
  - Still unlabeled cumulative bank, still no-more-buys, still no TAKEN-as-entry modelling.
  - No resolution frame at all.
  - Raid 1 is again CLEAN at −1.
- **No-words: 5.** It stacks H's strip with P's struck job icons at about 20 px (`scrambled/1_shop.png` forecast row 2 is
  unreadable: struck coin, struck hex, struck eye, and outlined survivor chips in a row).
- **Decision depth: 6.**
  - The investment depth is inherited from H. But HP's own depth is **not measured**: H's 14.8 comes from the no-carry
    campaign, and HP's forward line simply re-runs H's lines under the carry rule.
  - P's per-raid front, the source of P's depth, is dropped. On the shown home line no job is ever lost, so the job layer
    makes no decision in any frame.
- **Consequences: 8.** The strongest consequence loop of the four:
  - pieces persist;
  - leaks come back as bigger rosters, visible in the forecast before you commit;
  - jobs can be lost;
  - the record line ends 34 vs −11.

  The record graph lacks H's line legend.

**3 biggest problems.**
1. P's front and its trade-off are gone. The jobs are stickers on the shown line.
2. The depth is unmeasured under its own rules.
3. The shop strip is the densest glyph row in round 6.

**3 most valuable ideas.**
1. The carry rule inside the fortress forecast. It is the one change that makes the investment payoff visible at the shop.
2. Persistent pieces combined with persistent losses (jobs and survivors). The campaign remembers in both directions.
3. The record line under the carry rule.

**Refs.** `sheet_06_shop_forecast_H_HP_vs_Mechabellum.jpg`, `sheet_04` (Rogue Tower persistence), `sheet_05`
(P's trade-off that HP dropped).

**+2 per axis.**
- **What/when:** the netrun dial, and entry hexes on the roster chips.
- **Predictability:** label bank vs net, model TAKEN entries, and show a resolution frame with numbered shots.
- **No-words:** in the shop strip, show only per raid "home ok/hit, jobs lost count, survivors count". Detail goes on hover.
- **Depth:**
  - run `bastion_campaign.py` with carry and jobs and report regret;
  - give each visit a forced give-up, for example a roster that can only be fully stopped by abandoning one job node,
    so P's trade-off returns inside H's frame.
- **Consequences:** already strong. Show one losing frame.

---

## 3. Ranking and what to take forward

**Ranking by total:** G 33, H 32, HP 32, P 31. This ranking misleads: G's lead is presentation, and its depth is
structurally capped (DEPTH.md says no presentation fixes it). **Ranking by potential:** HP > H > P > G.

**Take forward two:**
- **H (as HP's spine, with the carry rule).** It is the only concept whose measured depth lives across raids, which is
  where a 3-to-5-raid roguelite campaign needs it. It is also the cheapest per visit (2 buys, no draft).
- **P's node jobs as the per-raid trade-off layer.** Do not keep P's front-as-menu.

The destination is a true HP, which round 6 did not build: persistent fortress, the carry rule, and node jobs. Each raid
should make the player choose which job to give up, through placement, with one forecast of their own plan.

**Steals:**
- **G → everyone:** the netrun dial, numbered shots and the beat clock in the playout, and the per-node patch choice in the
  aftermath.
- **HP → H:** the carry rule in the fortress forecast. It is the cheapest fix for H's invisible payoff.
- **P → HP:** jobs struck per forecast row and survivor chips, but forecast for the player's own plan, not a front.
- **Everyone must drop G's marginal-value coins and top-3 plan list.** They turn depth into reading the answer.

**Prototype first: H with the carry rule (HP minus jobs).** Its central claim cannot be judged from mockups: that a player
feels and learns the investment and leak trade-off across three raids. Only play across a full leg answers it. It needs the
fewest new systems (no draft, no job economy tied to the netrun layer). Jobs need the netrun loop to have value, so add
them second.

---

## 4. Barriers (to 9+ on any axis for the forward concept; every item is a **designer decision**)

**1. D26: a step-locked, readable 20–40 s playout, hands-off.**
- *Blocks:* consequences and predictability at scale. With beat pacing (1 s per shot, 2 s per kill-cam) and HP's carry
  rule, rosters reach 8 (forward line). A 40 s cap then forces compression, exactly when the player most needs to see why
  the leak happened.
- *Change:* cap by beats per threat, not total seconds. Collapse repeated shots by the same gun into one beat with ×N.
  Allow a "replay this node" after the raid.
- *Cost:* the playout spec and the clock UI. Raids of 8 threats may run about 50 s.
- *Worth it:* yes. Keep D26's zero input, and relax only the cap.

**2. D27: a clean defense gains Heat, any damage gains none.**
- *Blocks:* consequences (motivation) and what/when. It punishes success by pulling the next raid forward, and in H/HP it
  invalidates the leg telegraph shown at visit 1.
- *Change:* retire D27 and adopt the package's "raids do not move Heat".
- *Cost:* one ruling, and the GDD Heat text.
- *Worth it:* yes. Required for H's telegraph to be honest.

**3. D28: the verdict is only CELL HOLDS / BREACHED; nodes show DOWN or TAKEN.**
- *Blocks:* consequences. CLEAN is the only aspirational tier.
- *Change:* adopt the package's CLEAN / HOLDS / BREACHED, but redefine the CLEAN payout so that CLEAN never nets
  negative. Either scuffs within CLEAN are repaired free, or the CLEAN bonus is at least the scuff bill. H raid 1 and HP
  raid 1 currently stamp CLEAN at −1.
- *Cost:* a payout tweak and re-measured depth (cleaner plans become more attractive, so check the dominance again).
- *Worth it:* yes.

**4. Cobalt threats (by ruling) against a navy field, yellow Cell, teal OK, and blue UI chrome.**
- *Blocks:* no-words 9+. Threat cobalt shares its hue family with the dial, the roster panels, the corp hexes, the
  speed buttons and the ICE teal. Routes need a white core to read at all. Genre convention (ITB, KR, Thronefall skull
  markers) is warm or red for enemies. Here red is spent on damage and X marks, so "hostile" has no unique channel.
- *Change:* keep cobalt for the threat bodies, and move all UI chrome off blue (to neutral grey). Or give the threats a
  second channel: a hard silhouette plus an animated dash on routes.
- *Cost:* an art-direction ruling and a palette pass.
- *Worth it:* moving the chrome off blue is cheap and worth it. Overturning cobalt is not needed.

**5. One folded score (net = payout − patch) in G and H.**
- *Blocks:* depth (DEPTH.md: structural near-dominance).
- *Change:* keep losses unfolded (jobs, survivors, Schematics shown apart) as P does, but on the player's own plan.
- *Cost:* forecast UI, and the node jobs (below).
- *Worth it:* yes. This is the core depth fix.

**6. Solver output in the UI** (G's marginal coins and top-3 plans; P's curated front).
- *Blocks:* depth (it caps at "pick the highlighted card"). It also reaches past predictability into autoplay.
- *Change:* forecast only the plan the player has placed. Hints may name what an alternative gives up, but never where
  to put things.
- *Cost:* none (it removes UI).
- *Worth it:* yes.

**7. Content limit: 5 asset types, a 6-node map, a small threat pool, and a fixed Armory.**
- *Blocks:* depth. DEPTH lever 2, "the draft comes from what this run has earned", is implemented by **no** concept.
- *Change:* the pieces come from netrun rewards (H's shop stock drawn from the run). Add 2–3 asset verbs that interact
  with jobs (for example a piece that only works on a node whose job holds).
- *Cost:* content, and re-measurement.
- *Worth it:* yes, after the prototype.

**8. Node jobs need value from the netrun layer** (Proxy intel = +1 netrun of warning, Relay = +1 branch).
- *Blocks:* depth in P and HP. The trade is only real if the jobs are worth roughly the same.
- *Change:* tune the job values so that each is worth about 6–10 Schematics in typical runs. Make intel reveal more
  (entries or traits).
- *Cost:* netrun-layer hooks and balance.
- *Worth it:* yes.

**9. A TAKEN node becomes a corp entry point, not modelled in the sim.**
- *Blocks:* predictability in H and HP. The leg telegraph is optimistic.
- *Change:* model it, and show conditional entries in the forecast ("if Proxy falls, raid 3 enters here").
- *Cost:* sim and resolver work, plus a forecast glyph.
- *Worth it:* yes. It is also good drama.

**10. The crew ×1.5 with `roundi` rounding** (4 → 6, 8 → 12, 3 → 5).
- *Blocks:* predictability at 9. Effective numbers are printed, but the player cannot do the maths themselves (3 → 5 is
  not ×1.5 to a human).
- *Change:* a flat +N per piece on the crew's node.
- *Cost:* tuning, and the effective-number display.
- *Worth it:* marginal. Do it if a number change is cheap.

**11. Fixed routes (R1) and the plan-time Decoy.**
- *Blocks:* not a barrier to predictability; it is the reason predictability is 8. It limits depth only because the
  Decoy is the only route lever, and J showed barriers unused.
- *Change:* none now.

**12. Package inconsistency in P** (patch = scuffs only; DOWN and TAKEN unpriced).
- *Blocks:* predictability.
- *Change:* use the shared `price()`.
- *Cost:* trivial.
- *Worth it:* yes.

**13. The SCUFFED / CLEAN definition (C1).** A node at −9 is "clean". Combined with barrier 3, this is the source of the
CLEAN-at-a-loss stamp. Change it as in barrier 3.

---

## 5. Sheets built (all in `D:/rc_tmp/raid_design_lab/critic_r6a/`)
- `sheet_01_attack_order_G_vs_ITB.jpg`: G 4_forecast vs Into the Breach numbered attack order.
- `sheet_02_hands_off_playout_G_P_vs_SAP.jpg`: G 5_resolution, P 4_resolution vs Super Auto Pets battle.
- `sheet_03_leg_telegraph_H_vs_SAP_tiers.jpg`: H 0_campaign vs SAP tier table vs Thronefall wave markers.
- `sheet_04_persistent_fortress_H_vs_RogueTower.jpg`: H 6_visit3, 7_record vs Rogue Tower.
- `sheet_05_front_P_vs_BackpackBattles.jpg`: P 3_front vs Backpack Battles "choose wisely" vs Bazaar rewards.
- `sheet_06_shop_forecast_H_HP_vs_Mechabellum.jpg`: H 1_shop, HP 1_shop vs Mechabellum pre-fight board.
- `sheet_07_routes_G_vs_IsleOfArrows_KR.jpg`: G 1_warning (scrambled) vs Isle of Arrows vs KR Vengeance.
- `sheet_08_stacked_routes_H_vs_ITB.jpg`: H 5_visit2 (scrambled) bundled routes vs Into the Breach.

Refs reused from the prior set (no new downloads succeeded: hearthstone.wiki.gg returned HTML, which was deleted). They
are cited in `refs/SOURCES_R6A.tsv`.
