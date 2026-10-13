# Motion feedback — blue_hour · PB-004 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not recorded

> Written by a Claude motion tester (docs/process/05_CLAUDE_PLAYTESTER.md §6). It played through
> the screen like any tester; at moments that should animate it captured a burst of frames
> (~15 fps, up to 5 s) and judged them as a contact sheet. It cannot hear sound and sees motion
> only as sampled frames: smoothness below ~15 fps, easing curves and sub-frame flicker are out
> of its reach. Contact sheets are in the session folder's `motion/`.

## 1. Session

- **Tester / persona:** blue_hour / Explorer / completionist
- **Build:** main @ 19ad76a3 · **Played:** 15 min · **Moments judged:** 29
- **Settings:** defaults

The campaign was INCOMPLETE (time ran out). Breaker 1 died on L4 against the Recall Unit. Breaker 2 was on L1 when I quit.

## 2. Verdict per moment type

| Moment type | Seen | Typical duration | Verdict | What reads well | What does not |
|---|---|---|---|---|---|
| Card played onto a wheel | Yes (several) | 0.4–1.2 s | clear but flat / hard to follow | The targeting arc ties the card to the enemy wheel slot. The hand closes up and RAM drops. | The card often just vanishes. The yellow burst hides the changed segment. Several clicks showed no readable motion. |
| Nudge / spin | Partly | not captured separately | no animation seen | Tutorial taught nudge in-fight. | No dedicated capture. The wheel rearranged with no highlight on what changed. |
| SEND IT resolution (needles, damage, block) | Yes (several) | 3–5 s | clear but flat; too slow on the longer ones | The attack line goes out, the hit lands, the HP drops, and the counter-line comes back. The tutorial-fight kill is satisfying. | Thin lines, tiny particles and a tiny damage number. Dead gaps of about 1 s. The longest runs near 5 s. |
| Perfect / precision hit | Yes (once) | 3.5 s | clear but flat | The PERFECT tag, line, burst and HP drop (38 to 14) are in a readable order. | No shake, enlarged number or flash, so a Perfect feels like a normal hit. |
| Enemy turn / pointer attack | Yes (within SEND IT) | about 1–2 s | clear but flat | The red line and burst on my wheel show the counter-hit. | The red line is thin and subtle. |
| Fight won / lost | Yes | 3.2 s (won) | clear and satisfying (won); no animation seen on the settled banner | The FIGHT WON banner, DELETED stamp and the wheel shattering give the win weight. The flatline screen has a good line. | The win banner is already settled when the next click lands, so the click gets no reaction. The training-sim victory banner ignored clicks, Enter and the lower-right click; I only got out through the pause menu. |
| Reward reveal and pick | Yes (2) | 1.4–1.8 s | hard to follow | The picked card flies up. | The other slots go blank white. The sheet is empty for a beat, then hard-cuts to the map. No deck-add confirmation. |
| Map move / node entry | Yes | about 1–1.4 s | janky or glitchy | The destination is clear. | The node gets no press feedback. The map hard-cuts to combat with no transition. The combat UI appears fully formed. |
| Screen transitions (title, HQ, city, menus) | Yes | 0.5–1.5 s | clear but flat | The jack-in terminal typing names the route. The scan band on START is a nice touch. The glitch-out into CONNECTING TO HQ fits the theme. | The shop-to-map change is an abrupt cut into a blurry zoom. The loading card is static. Buttons give no press feedback. |
| Raid playout | not encountered | – | – | – | – |
| City Grid recolour / claim | not encountered | – | – | – | – |

## 3. Pacing

- Animations I would want to skip after seeing them twice:
  - Full SEND IT resolutions (about 4–5 s each, with idle mid-gaps).
  - The empty loot sheet beat (about 1 s).
  - The static CONNECTING TO HQ card (about 0.4 s).
- Moments that felt instant where motion would explain cause and effect:
  - Node clicks on the map.
  - Card plays that just vanish.
  - Loot pick confirmation.
  - Button presses.
  - Turn counter changes. I noticed turn 4 had arrived with no cue.
- Waiting: I could not tell the total split. Resolutions of 3–5 s each, repeated across a 14-turn fight, felt like a lot of watching.

## 4. Problems (each with the contact sheet path)

| # | Moment | Sheet | What happened | Why it is a problem | Severity |
|---|---|---|---|---|---|
| 1 | Targeting display | not captured on a sheet (journal notes only) | During Fine Tune, Brute Spin and Jolt targeting, the RAM readout dipped to -1, -2 or -3 on nearly every turn. Esc cleared it for a turn, then it came back. | It looks like an overdraw and misleads planning. | glitch |
| 2 | Fine Tune targeting, L1 turn 10 | not captured on a sheet (journal notes only) | The arrow stayed locked on the Daemon's top-right slot. Six clicks did nothing until I pressed Esc. | It feels like a stuck state with no cue. | glitch |
| 3 | Reward pick | motion/0025_reward_choice.png | The picked card flies away, the slots go blank white, then the screen hard-cuts to the map. | It reads as missing art, and the pick gets no payoff. | unreadable |
| 4 | Map node to fight | motion/0014_map_choice.png | There is no click feedback, then an abrupt cut into combat. | The delay feels like lag. | polish |
| 5 | Shop to map | motion/0026_shop.png | Hard cut into a blurry zoom. | The player loses track of where they are going. | polish |
| 6 | SEND IT resolution | motion/0006_combat_mid_turn.png | The sequence runs about 4–5 s with idle gaps, and the hits are weak. | It is slow when repeated. | slow |
| 7 | Card played mid-turn | motion/0004_combat_mid_turn.png | No card flight, number change or impact was visible. | I could not tell whether the click registered. | unreadable |
| 8 | Tutorial Next click | motion/0001_dialog_or_tutorial_text.png | No visible reaction to the click. | There is no button feedback. | polish |
| 9 | Training-sim victory banner | not captured on a sheet (journal notes only) | Clicks and Enter did nothing; I got out through the pause menu. | It reads as a dead end. | glitch |
| 10 | Flatline transition | motion/0027_summary_or_end.png | Coloured fringing glitch-out, then a static loading card and a hard pop into HQ. | It is on-theme but static. | polish |

## 5. Best and worst

- **Most satisfying motion:** The training-sim kill: card out, line, hit, enemy to 0/40, FIGHT WON, and the wheel shattering (motion/0008_combat_turn_start.png).
- **Most confusing or annoying motion:** The reward pick, where the card flies off, the slots go white, and the screen cuts to the map (motion/0025_reward_choice.png). The RAM readout flicker during targeting comes second.
- **One change to the game's motion right now:** Give every confirm a visible reaction: a pulse on the clicked node, a clear card landing on the wheel with the changed segment highlighted, and a short fade instead of hard cuts.

Focus questions:
1. **Skip after seeing twice:** the full SEND IT resolutions and the empty loot-sheet beat.
2. **Motion failed to show cause and effect:** node clicks, card plays that vanish, the loot pick, and the tutorial Next click.
3. **Flash, strobe or glitch:** nothing strobed. The RAM readout flickered during targeting. The white blank cards in the reward sequence looked like a glitch.

## 6. Summary (machine-read by tools/playtest/aggregate.py)

```
SUMMARY
handle: blue_hour
persona: PB-004
focus: animation_feel
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 2
operative_deaths: 1
raids_survived: 0
playtime_min: 15
enjoyment: 5
rng_fairness: n/a
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: none
bugs: 10
top_frustration: The RAM readout flickered negative during targeting on nearly every turn, and card plays and picks gave little visible cause and effect.
top_change: Add visible confirmation on every click (node pulse, card landing, loot pick) and shorten the SEND IT resolution.
```