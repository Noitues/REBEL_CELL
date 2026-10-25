# Critic review: concept G, round 4 (Merged Telegraph)

I reviewed all 16 frames (`r4/mockups/*`, `r4/scrambled/*`), `SPEC_R4.md` and `RULES.md`, and checked the numbers in
`tools/raid_concepts/sim.py` and `concept_g4_merged.py` (plus the lab's own `payout_r4.txt` / `g4_out.txt` run output).
I did not open any earlier review.

## 1. Score table

| Axis | Score |
|---|---|
| 1. What / why / when | **7** |
| 2. Outcome predictability | **7** |
| 3. No-words test | **6** |
| 4. Decision depth | **5** |
| 5. Consequences | **7** |
| **Total** | **32 / 50** |

**Verdict:** the telegraph contract (fixed routes, per-node tags, net before you commit) is now good. But the one
"depth" argument this round adds (plan 1 vs plan 2 through the next raid) is broken by its own rules. The draft
preview tells the player nothing, and one gun (the Railgun) is the answer.

---

## 2. Per axis

### 1. What / why / when: 7
- **Why** works. `0_netrun.png` and `1_warning.png` carry the chain "flame 51 > |50 → shield", and the Heat bar is the
  player's own number. In `0_netrun` the cobalt pips above each Heat tick (2/3/4/5) give the raid size before it
  happens. That is a good, cheap device.
- **When** is the dial: 2 segments, a netrun hex and "2". Drawing the unit (the hex) fixes the old ambiguity. It is
  still a bare "2" with nothing showing that the raid lands **on arrival at HQ**. The netrun map in `0_netrun` gives
  no marker on the route itself (for example the node after which the raid lands). Isle of Arrows
  (`s2_when_vs_isle_of_arrows.jpg`) puts the wave count *and* the spawn size **at the entry point** on the board. G
  keeps them in two HUD gadgets.
- **What** is clear at the warning (`1_warning.png`): three threat chips, each with its route spelled out as node
  icons (Relay > Vault > Home, Proxy > Vault, Proxy). It appears only from the warning on. The netrun map shows the
  three chips without their routes.
- **Contradiction.** The tier pips say 4 threats at 75. `7_next_raid.png` (Heat 76) draws 3, because
  `next_raid()` in `concept_g4_merged.py` reruns the Heat-50 `THREAT_DEF`. The "what" signal is therefore wrong on the
  one frame that shows a second raid.

**+2:**
- (a) Put the raid on the netrun map as a node: a cobalt shield on the HQ-return edge, with the dial counting down to it.
- (b) Show the next raid's roster (chips) next to the tier pips while the player is still choosing netruns, so the
  player can choose *not* to cross 75.
- (c) Make the next-raid frame use the tier's roster.

### 2. Outcome predictability: 7
- **Fixed routes plus no cascade make the warning honest.** In `1_warning.png` every tag (TAKEN, −5, check) has a drawn
  cause on its arrow. `4_forecast.png` puts a skull where each threat dies and gives every node a tag (check 0, −5,
  −3). That is Into-the-Breach-shaped (`s1_warning_vs_itb.jpg`). I checked the numbers: P1 = Relay 15>10, Proxy 15>12,
  3 kills, patch 8, net +10, 9 beats, 15 s. They match the sim.
- **What keeps it at 7:**
  - **The next-raid line contradicts the net.** The plan row's "flame → bolt-flag 3" (`4_forecast`) and `7_next_raid`
    are computed on the **unpatched** map (`next_raid()` starts from `after` hp). The +10 net on the same row has
    **already paid** the −8 patch. If the player pays as the net says, Relay is back at 15, and the next raid is
    identical after plan 1 and plan 2. The forecast shows two incompatible futures in one row. That is a
    predictability failure, by the brief's own definition.
  - **The next-raid count assumes zero defense.** It runs `Plan({})`. "3 lost" means "3 lost if you place nothing
    next time", which no player will read correctly.
  - **The mirror's rounding is not the game's.** `sim.py` does `round(dmg * 1.5)` in Python, which uses banker's
    rounding, so a Sentry with the crew deals 3 × 1.5 → **4**. `raid_resolver.gd:485` uses `roundi`, which rounds
    half away from zero → **5**. Plan 2 (Sentry and crew on Proxy, net +9) and every Sentry-and-crew plan in the
    12,960 sweep may not match the build.
  - **The playout clock drifts.** `5_resolution.png` says "0:05 / 0:15" at beat 5/9 after a kill-cam has played. The
    code counts `now * BEAT_S` and leaves the 2 s kill-cams out, so the clock and the total disagree.
  - **Strike order is shown only during the playout.** The numbered badges appear in `5_resolution`. The forecast has
    no "attack order" view (ITB has one, top-right of its frame).
  - **The tie-break glyph is hard-coded at Relay** (`routes()` always draws `route_glyph(ENFORCER)` beside RELAY). In
    `1_warning` the Enforcer goes to Proxy, so the glyph sits on a route it does not take.

**+2:**
- (a) The next-raid line must be computed on the map the net assumes, the post-patch map, or it must be split into
  "patched / unpatched" with both nets. Better: make patching a per-node choice in the aftermath (the trade-off is
  then real, see Barriers B1).
- (b) Run the next raid against the tier roster and the player's *current* plan, re-placed. Otherwise drop it.
- (c) Fix the rounding (`math.floor(x + 0.5)`), and re-measure.
- (d) Add an ITB-style "order" toggle on the forecast that prints the strike badges.

### 3. No-words test: 6
- The scrambled frames are almost identical to the plain ones, because G uses few words. That is to its credit. Routes,
  the red X, the TAKEN flag, the teal check and the CLEAN stamp shape all survive scrambling
  (`scrambled/1_warning.png`, `scrambled/6_aftermath.png`: "AYPYB" still reads as a verdict stamp by shape and color).
- The **economy glyphs do not survive**.
  - The draft cards (`scrambled/2_draft.png`) read "bolt flag 2-struck 1". With no words, nothing says "nodes lost in
    this raid if you take only this card".
  - The plan rows (`scrambled/4_forecast.png`) stack three lines of micro-glyphs: home −0, bolt-flag 0, scuffed
    icons, flame → bolt-flag 3. The coin glyph (a circle with a bar) reads as a power symbol.
  - The planning chip "bolt-flag 2-struck 1, −27" (`scrambled/3_planning.png`) has no anchor.
- The meaning of "bolt + flag" (DOWN or TAKEN) has to be learned. Super Auto Pets (`s5_resolution_vs_sap.jpg`) gets by
  with two numbers per unit and nothing else.
- Threat silhouettes are tiny (10 px chips) and differ mostly by an inner glyph.

**+2:**
- (a) One currency icon that looks like a part or chip, not a power button.
- (b) Replace "bolt-flag N" with N small node silhouettes greyed or crossed, so a count becomes a picture.
- (c) Cut the plan row to two lines: verdict stamp shape, net. Put the per-node detail on the map, where it already
  is.
- (d) Make the threat silhouettes 2× larger, and distinct in outline, not only in the inner glyph.

### 4. Decision depth: 5
- **The draft preview carries no information.** `PREVIEW` = Turret 1, ICE 2, Decoy 1, Sentry 1, Railgun 1
  (`g4_out.txt`). Four of five cards say "2 → 1". The Railgun, which is in **every** top plan under all three payout
  settings (`payout_r4.txt`), looks exactly like the Decoy. ICE, which is in plans 1 and 2, previews as *useless*
  ("2"). A preview that says the right pick is worthless teaches the wrong lesson. The metric (single card,
  `crew="SAFE"` fixed) cannot see combinations, and combinations are the whole game.
- **The answer is "take the Railgun".**
  - At 4/6 payout the top drafts are Turret+ICE+Railgun +10, ICE+Sentry+Railgun +9 and Turret+Sentry+Railgun +4. The
    first two are 1 Schematic apart.
  - RULES.md R5 admits that without the Railgun no clean defense exists. A draft with one mandatory card is a draft of
    2 from 4.
- **The plan 1 vs plan 2 trade-off is not real.** It rests on the unpatched next raid (see axis 2). Remove that and
  the choice is +10 vs +9.
- **Who writes the three plan rows?** `4_forecast` shows three complete plans. If the game proposes them, the forecast
  solves the puzzle. If they are the player's saved attempts, that must be visible (an empty slot, "save plan").
- **What stays good:**
  - 1-move changes 57.6 % (RULES.md), so placements matter.
  - Clean is 4.8 % of plans: real, but hard.
  - The what-if chip in `3_planning` (lost 2 > 1, net −36 > −27) is the right live feedback.
- But in one 6-node scenario with 5 pieces this is a small solved puzzle. The second raid will not feel different
  unless the corp changes the problem. Rogue Tower (`s4_planning_vs_rogue_tower.jpg`) gives each piece a targeting
  choice. G's guns have hidden fixed targeting ("first" / "high").

**+2:**
- (a) The draft preview becomes the **marginal value**: the best net with this card minus the best net without it,
  over all placements. Then the Railgun shows +20 and the Decoy shows ~0, and the ICE combo value shows.
- (b) A per-raid corp trait that breaks the Railgun answer, for example "shielded: the first hit on each threat is
  absorbed", or turn on `auditor_hunts` so stacking 3 pieces on Relay draws fire.
- (c) Expose targeting as a choice on each gun: first, strongest or nearest-home.
- (d) Plan rows are player-saved only.

### 5. Consequences: 7
- **The CLEAN / HOLDS / BREACHED tiers with the net box** (`6_aftermath.png`) are legible and fair. Skull ×3 +12,
  check +6, patch −8, = +10, and it matches the forecast row exactly. That promise-kept moment is the best thing in G.
- **Persistence.** Scuffed nodes keep their −5 / −3 tag on the map. The patch list ("−5 → 5", "−3 → 3") prices them.
  The record row gains a teal shield. "51 = 51" states plainly that Heat did not move.
- **What keeps it at 7:**
  - **It barely motivates.** +10 against a bare −36 is a good spread, but the frames never show what 10 Schematics
    *buys* (one Relay install is 8). Backpack Battles (`s6_aftermath_vs_backpack.jpg`) ties the result to the run's
    stakes: wins, lives, rank.
  - **The patch choice is missing.** The aftermath lists prices but no buttons, so "unpatched" in `7_next_raid` is an
    unexplained state.
  - **TAKEN as an entry point is never shown persisting.** No frame shows a corp-owned node on the map between raids.
  - **The record is two small shields** with no link to anything.

**+2:**
- (a) A per-node PATCH / LEAVE choice in the aftermath, with the next raid's route redrawn live as you toggle. That
  makes the scuffed-draws-the-raid rule a felt decision.
- (b) Show what the net buys: the next install or repair it affords, ghosted on the map.
- (c) A frame with a TAKEN node, recolored cobalt as a corp spawn, with the reclaim netrun visible on the netrun map.

### Fit with hands-off execution
- The planning carries the agency, and the forecast is a contract, so watching is a check that the promise is kept.
  That is the right model (Mechabellum, SAP).
- 15 s for 9 beats is fine. The kill-cam with "+4" turns each kill into a payout beat, which is the right emotional
  hook.
- **Risk:** with a forecast this exact, the playout adds zero information. Most players will skip by the second raid.
- Give the playout one thing the forecast does not show:
  - the shots landing on HP pips;
  - a slow-motion beat on the decisive shot;
  - a running net counter that climbs to the promised number.

### Fit with the deckbuilder campaign
- Three to five raids, a few minutes each: the draft, placement and forecast fit.
- "Raids do not move Heat" means exactly the 25/50/75/100 cadence, four raids, never more, never fewer. Good for
  pacing, and it removes the perverse D27 incentive (a clean win pulling the next raid closer).
- "Next raid" depth only works if the next raid is computed honestly.

### Rule-change costs (each SPEC change)

| Change | Worth it? |
|---|---|
| No cascade | Yes. It removes the only undrawn damage, and costs nothing in clean plans. |
| Graded payout (4 per kill, 6 clean, net) | Yes. It turns the result into a number the player can chase. 4/6 is the right split: 0/12 makes everything all-or-nothing, 5/0 ties clean with non-clean. |
| Raids do not move Heat (against D27) | Yes. The D27 +5 Heat on a clean defense punished success. |
| CLEAN / HOLDS / BREACHED (against D28) | Yes. Two tiers cannot reward a clean defense. |
| Beat pacing (against D26) | Yes, if the clock counts kill-cams. Step-locking is less readable than beat-locking. |
| Effective numbers printed on placed pieces | Yes, but fix the rounding first. |
| Draft preview | Not as built. The metric is wrong (see B3). |
| Next-raid line | Not as built (see B1). |

---

## 3. The 5 biggest problems
1. **The next-raid forecast double-counts the patch.** The net assumes you patched. The next-raid line assumes you did
   not. The plan 1 vs plan 2 "depth" exists only in that gap (`4_forecast.png`, `7_next_raid.png`,
   `next_raid()`).
2. **The draft preview is non-informative and misleading.** It shows 1 for four cards and 2 for ICE, while the Railgun
   is mandatory and ICE sits in both clean plans (`2_draft.png`, `card_preview()`).
3. **Railgun dominance.** Every best plan under every payout uses it, and without it no clean defense exists. The
   draft is really 2 of 4.
4. **The next raid ignores the tier roster** (3 threats at Heat 76 while the pips say 4) and assumes no defense.
5. **Mirror drift.** Python's banker's rounding vs `roundi` (Sentry with crew 4 vs 5), and a playout clock without
   kill-cams. The "every number from the sim" guarantee is broken in exactly the places a player would test.

## 4. The 5 most valuable ideas
1. **Fixed routes drawn end to end, with the route spelled as node icons per threat** (`1_warning.png`). The arrow is
   the promise.
2. **The net in the same glyphs, before and after.** The forecast's net box and the aftermath's net box are the same
   object with the same numbers (`4_forecast.png` → `6_aftermath.png`).
3. **The kill-cam pays the salvage** (`5_resolution.png`). It gives a hands-off fight a reward beat per kill.
4. **Scuffed damage persists and steers the next route** (the weakest tie-break). The link between raids is right; it
   just needs the patch to be a choice.
5. **Raid size per Heat tier as pips on the Heat bar** (`0_netrun.png`). The player sees the price of the next 25 Heat
   while choosing netruns.

---

## 5. Barriers (everything holding an axis below 9). All are designer decisions.

| # | Barrier | Axes held | Change | Cost |
|---|---|---|---|---|
| B1 | The patch is automatic and implicit. The net charges it, the next raid ignores it. | 2, 4, 5 | Make the patch a per-node choice in the aftermath (PATCH / LEAVE, 1 Schematic per point). The forecast's next-raid line then shows both branches, or only the post-patch one. | Small view and state work: a patch action for non-home nodes (C2 already needs it). One test: patched map = fresh next raid. |
| B2 | The next raid is simulated with the Heat-50 roster and no defense. | 1, 2 | Simulate the tier's roster (4 at 75) with the player's current pieces re-placed, or drop the line. | Lab only: a `THREAT_DEF` per tier. For the build, the forecast must know the next roster, so it has to be fixed by content at the warning. |
| B3 | The draft preview metric (single card in isolation, crew pinned to SAFE). | 4, 3 | Show the marginal net: best plan with the card minus best without it. Or show "clean possible: yes/no" per card. | About 5 × 3,240 resolves per draft: fine offline, needs a budget at runtime (precompute at the warning). |
| B4 | **Content limit:** the Railgun is the only high-damage piece; no clean defense exists without it. | 4 | Add a second clean path: a Sentry/crew synergy, a trap that damages held threats, or a corp trait per raid that hard-counters the Railgun (armored, or `auditor_hunts`). | New content plus balance passes. It reopens the clean % (target about 3-8 %). |
| B5 | Hidden fixed gun targeting ("first", "high"). | 2, 4 | Show the targeting rule on each piece (icon), and optionally let the player set it per gun. | View only for display. Setting it is a small resolver option, and it multiplies the plan space by 2-3. |
| B6 | Single 6-node scenario, 3-threat roster. Depth is measured on one map. | 4 | Measure clean % and dominant-draft frequency over 3-4 maps and the 75 / 100 tiers before ruling R5 (N = 3). | Lab time only. |
| B7 | Strike order is visible only during the playout (C6). | 2 | Add an attack-order toggle in planning and the forecast with numbered badges (ITB). | View only; the data is already deterministic. |
| B8 | The tie-break glyph (R3) is not drawn where routes fork. | 2, 3 | Draw it at the actual fork of the threat whose tie it breaks; none where there is no tie. | View only. |
| B9 | D26, challenged (beat pacing). | 2 | **Accept** beat pacing, but count kill-cams in the clock and keep the 40 s cap honest. | Trivial. |
| B10 | D27, challenged (raids do not move Heat). | 1, 5 | **Accept.** Optionally, a CLEAN takes −5 Heat (pushes the next raid away), as a second reward lever. | That changes campaign cadence (raids could fall below 4). Measure over campaign sims first. |
| B11 | D28, challenged (three tiers). | 5 | **Accept.** Give HOLDS its own stamp color and shape, distinct from CLEAN in the scrambled test. | Trivial. |
| B12 | The C7 "when" ruling (the raid always lands on return). | 1 | Accept, but draw the landing point on the netrun map's route, not only in the dial. | View only. |
| B13 | The sim.py rounding mirror (Python banker's rounding vs GDScript `roundi`). | 2 | Use `math.floor(x + 0.5)`, then re-run `rule_metrics_r4` and every concept's numbers. | Lab only, but every published Sentry-and-crew number may shift. |
| B14 | The coin / "bolt-flag" glyph vocabulary. | 3 | One currency icon; node silhouettes instead of counts. | Art and view. |

---

## 6. Visual-quality read for Phase 3: the 5 frames needing AAA treatment
1. **`1_warning.png`.** The routes must read as threat in motion: animated cobalt flow along each route, the threat
   silhouette walking the head of its arrow, and the node tags as physical plates that snap on. Reference: ITB's
   tile telegraphs plus Kingdom Rush's path flow.
2. **`5_resolution.png`.** Real projectile and impact language per gun (the turret's tracer, the Sentry's double tap,
   the Railgun's charged beam), HP pips draining on the threat, the kill-cam as a real camera push-in, and a net
   counter climbing.
3. **`6_aftermath.png`.** The CLEAN stamp as a physical slam with screen shake, nodes healing or scarring visually
   (a scuffed node shows cracks), and the net box as a ticking tally.
4. **`4_forecast.png`.** The plan rows as tactile cards and the map as a "ghost replay" preview. It must feel like
   holding a contract, not reading a spreadsheet.
5. **`2_draft.png`.** The cards need weight and distinct silhouettes at 2× size, and the marginal-value preview
   needs to *glow* on the cards that matter.

## 7. Sheets built (all in `D:/rc_tmp/raid_design_lab/critic_r4/`)
- `s1_warning_vs_itb.jpg`: `1_warning` vs Into the Breach (per-tile threat, attack order)
- `s2_when_vs_isle_of_arrows.jpg`: `0_netrun` vs Isle of Arrows (wave count, spawn size at the entry)
- `s3_draft_vs_rogue_tower.jpg`: `2_draft` vs Rogue Tower (cards picked on the live path)
- `s4_planning_vs_rogue_tower.jpg`: `3_planning` vs Rogue Tower (damage, range, target priority on the piece)
- `s5_resolution_vs_sap.jpg`: `5_resolution` vs Super Auto Pets (stats on units, rewind/pause/fast/skip)
- `s6_aftermath_vs_backpack.jpg`: `6_aftermath` vs Backpack Battles (result tied to run stakes)
- `s7_next_raid_vs_thronefall.jpg`: `7_next_raid` vs Thronefall (composition read from icons per group)
- Working contact sheets: `work/cs_td.jpg`, `work/cs_ab.jpg`
- Scripts: `sheets.py`, `contact.py`
- New references: `refs/isle_of_arrows/steam_00-04.jpg`. All cited URLs, new and reused, are in
  `refs/SOURCES_R4.tsv`.
