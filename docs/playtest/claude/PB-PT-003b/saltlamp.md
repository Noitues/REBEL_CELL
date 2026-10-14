# Playtest feedback — saltlamp · PB-PT-003b · build 3eac0f086e6d32f23afd7c95dbb0e7eb35379339 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** saltlamp
- **Persona / focus / quirks:** Story and tone fan (novice) / Pacing and session length / prefers on-screen keyboard shortcuts; right-clicks new cards or icons to inspect them first
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 3eac0f086e6d32f23afd7c95dbb0e7eb35379339
- **Total playtime:** 40 wall-clock minutes (354 actions, 1 session; ended with in-game Quit when time ran out)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, Standard Home Server, starting roster Breaker, campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time, INCOMPLETE; quit mid-fight, Breaker 4 at 41/60 vs Billing Daemon 24/42)
  - Netruns: 4 started, 0 completed, 3 operative deaths (Breaker 1 on L3 Triage Unit fight, Breaker 2 on the Collections Agent fight at Continuum Billing Farm, Breaker 3 on the L2 Dosage Dispenser fight at 2/60 HP). The fourth netrun with Breaker 4 was unfinished.
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: 0 (journal shows none)
  - Raids: 0 survived (CELL HOLDS); one raid played out, two Collectors reached HOME SERVER, 0 threats destroyed, home server 50 to 38. Nodes lost: not encountered.
  - Final Heat: 38 (Noticed) · Home server integrity: 38/60
- **Overall enjoyment (1–10):** 4 — The writing and the death lines land, but the wheel loop was slow and I lost three runners.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? Partly. Previews helped, but fights ran 10-13 turns and mostly felt like grinding with Jolt and Fine Tune.
  - Did SEND IT ever give a different result from the preview chips? Not clearly confirmed. At 27.3m the Jolt preview showed my Breaker taking 17 and the Agent only dropping 6, and I felt the previews kept shifting. Fine Tune on an enemy wheel at 10.7m needed Space to commit; clicking the wheel did nothing.
  - Did UNDO / rewind behave as expected? Only used in the tutorial, where Z was clear. Not used in the campaign.
- **Card balance & utility:**
  - Overpowered / automatic picks: Jolt (1 RAM, 3 ticks) and Fine Tune did most of the work. Brute Spin and Fine Tune finished the Dispenser fast.
  - Useless / never worth picking: Mirror Flip, which was blocked by resistance or Guard every time I looked at it. Overdrive I never trusted, because it corrupts the slice. Siphon did not save my last runner.
- **Synergies & archetypes:** No strategy came together. I only ran Breakers, and the deck felt like a small pile of nudges and spins.
- **Card text & clarity:** Mostly yes in tooltips, but hand text is small and truncated with ellipses (e.g. "Blocked while th..."). Overlapping cards hide text too.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too long (fights of 12-13 turns ran about 2-3 min each); whole campaign unknown, not finished in 40 min.
- **Netrun map & encounters:** The route map was readable, but the confirm step only unlocks after picking a node. I saw almost no variety in 40 min, mostly Fights, one rack choice, and the same Collections Agent twice.
- **City Grid & HQ:** Site locks (Clear First) narrowed choices. A recruit at 15 Schematics was refused because I had only 5. The click on the recruit card did nothing, which cost me about a minute.
- **Heat:** I could see it climbing (+11 per flatline), but I could not manage it. Raid thresholds felt scary.
- **Raids:** The setup was understandable, but with an empty Armory I could only watch the home server go from 50 to 38.
- **RNG & fairness (1–5):** 3 — Entering L3 at 9/60 HP, with no heal until run end, set the run up to fail.
- **Permadeath & meta-progression:** The deaths hurt and the last lines ("let it be for nothing") are great, but the first two felt like the game's pacing rather than my mistakes. I didn't reach a point where I wanted to restart.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM and the enemy wheels were visible. Card text is tiny and clipped, and I wanted to know what the enemy's Perfect marker actually does.
- **Information outside combat:** The map labels sit far from their nodes. I could not tell which nodes were which without hovering. Hover tooltips for locked sites stacked over the selected site panel.
- **Controls:** Number-key shortcuts only half-worked: key 3 did nothing at 19.1m, perhaps because of RAM. Space and Enter worked well. Pause menu has Abandon Run and Quit right next to Resume with no buffer.
- **Visual feedback:** Previews are good. The wheel loop is dramatic but slow, and hits did not feel punchy because I was skipping through them.

## 5. Focus questions (Pacing and session length)

1. Which part of the loop felt too long? Too short? — Too long: the tutorial (about 4 min of repeated free nudges over 10 turns), and every combat at 10-13 turns. Too short: the HQ visits and the raid, which flashed by.
2. Which animation or transition did you most want to skip? — The iris wipe on a black screen at 37.1m, and the per-turn wheel resolve loop.
3. Would you start another netrun right now? Why or why not? — Not eagerly. The world and death lines pull me in, but another 12-turn fight at low HP with no heal does not.

## 6. Open feedback

- **Favourite moment or build:** The operative's dying lines ("Tell the Cell it was worth the Cycles"; the invoice is in the mail) and the Dosage Dispenser kill in 4 turns.
- **Biggest frustration / moment you wanted to quit:** Entering the L3 fight at 9 HP with no heal, and later the 2/60 HP rack choice.
- **One thing to change or add right now:** Shorten fights and the tutorial, and let the player skip the wheel resolve animation.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Fight vs Dosage Dispenser | Clicked the enemy wheel with Fine Tune aimed (10.7-10.8m) | Click applies the card | Nothing happened; Space was needed | wrong | 0074.png |
| 2 | Collections Agent fight | Pressed key 3 for Brute Spin (19.1m) | Card plays | Nothing visible | wrong | 0133.png |
| 3 | HQ market | Clicked recruit card (16.8-17.0m) | Hire or a message | Nothing visible; only later "Not enough Schematics" | wrong | 0119.png |
| 4 | Crew tab | Journal NOW block said R0 was ready (37.0m) | Matches the screen | Only Breaker 4 was ready | cosmetic | 0222.png |
| 5 | Campaign map | Tooltips and labels | Readable labels | Tooltip over the info panel, clipped labels | cosmetic | 0154.png |

**Confusion log**:
- 12.7m — firmware chip pick — the other option hidden behind the loot sheet — resolved at 32.0m, when both were visible.
- 33.0-34.9m — route map — hovering RACK for a heal, tooltip unclear — about 2 min, resolved by committing.
- 16.8-17.2m — HQ market — recruit click did nothing — about 30 s, resolved by reading the Schematics count.
- 23.6-24.1m — campaign map — Vault locked behind Clear First — about 30 s, resolved by routing to the Hub.

## 8. Summary

```
SUMMARY
handle: saltlamp
persona: PB-PT-003b
focus: pacing
build: 3eac0f086e6d32f23afd7c95dbb0e7eb35379339
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 3
raids_survived: 0
playtime_min: 40
enjoyment: 4
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Jolt, Fine Tune, Brute Spin
weak_picks: Mirror Flip, Overdrive
bugs: 5
top_frustration: Fights run 10-13 turns of slow wheel resolve, and low HP carries over with no heal until run end.
top_change: Shorten fights and the tutorial, add a skip for the wheel animation, and offer a heal mid-run.
```