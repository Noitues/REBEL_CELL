# Motion feedback — halfmoon · PB-003 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not recorded

> Written by a Claude motion tester (docs/process/05_CLAUDE_PLAYTESTER.md §6). It played through
> the screen like any tester; at moments that should animate it captured a burst of frames
> (~15 fps, up to 5 s) and judged them as a contact sheet. It cannot hear sound and sees motion
> only as sampled frames: smoothness below ~15 fps, easing curves and sub-frame flicker are out
> of its reach. Contact sheets are in the session folder's `motion/`.

## 1. Session

- **Tester / persona:** halfmoon / Explorer / completionist
- **Build:** main @ 19ad76a3 · **Played:** 17 min · **Moments judged:** 23
- **Settings:** defaults

The run ended early, so this is INCOMPLETE. The Breaker was bricked in Fight 4 (a Rack, L4) by the Claims Adjuster. I stopped there, and the end screen was not checked in the journal.

## 2. Verdict per moment type

| Moment type | Seen | Typical duration | Verdict | What reads well | What does not |
|---|---|---|---|---|---|
| Card played onto a wheel | Yes, many | ~1.0-1.4 s | clear but flat | The card travels, lands on a slice and the slice highlights. The aim arrow draws in by ~0.28 s. | The hit is small: soft sparks, no shake and no number pop. Once the arrow pointed at the enemy wheel while the card landed on mine. The small red status icons that appear afterwards are easy to miss. |
| Nudge / spin | Yes | ~0.8-1.5 s | clear but flat | The targeting arrow and the highlighted wedge make the target obvious. | After selection nothing animates, and the frames sit static. |
| SEND IT resolution (needles, damage, block) | Yes | ~1.6 s | clear but flat, sometimes hard to follow | The yellow projectile crosses, sparks land and enemy HP ticks 40→37→34. | Hits are understated. Pink particles at my wheel are unexplained. The player phase blends into the enemy telegraph. Some turn rollovers show only a hand redraw and a hard cut to the new turn number. |
| Perfect / precision hit | Not encountered | n/a | not encountered | n/a | n/a |
| Enemy turn / pointer attack | Partly (red telegraph line) | ~0.2 s | hard to follow | A red line and dot run from the enemy wheel toward mine. | There is no clear break from my phase, and I saw no distinct enemy attack animation. |
| Fight won / lost | Won seen; lost not captured | static | no animation seen | FIGHT WON, DELETED and OURS NOW are legible at once. | The banner never animates in the captured windows. A win feels flat. I did not capture the defeat. |
| Reward reveal and pick | Yes, 5 times | ~1.5-1.8 s | hard to follow | The chosen card lifts and flies toward the deck icon. | The other cards vanish at the same moment, leaving blank white slots for ~0.4 s. The fly-to-deck is small and fast. The firmware sheet pops in with no transition, and then a hard cut to a blurred map. |
| Map move / node entry | Yes, 4 times | ~0.4-0.8 s of dead time, then a cut | clear but flat; janky once | The typed jack command line is readable (about 0.75 s). | There is no click feedback for 0.4-0.8 s. Then a hard cut to the fight, and once a dark half-built frame with the background popping in. |
| Screen transitions (title, HQ, city, menus) | Partly | brief | hard to follow | Not much. | The reward-to-map transition is a hard cut from a flat dark map to a detailed one. The blurred zoomed streak frame is abrupt. |
| Raid playout | Not encountered | n/a | not encountered | n/a | n/a |
| City Grid recolour / claim | Not encountered | n/a | not encountered | n/a | n/a |

## 3. Pacing

- Animations I would skip after seeing them twice:
  - The loot-sheet empty-slot gap, ~0.4 s.
  - The map-node click dead time, ~0.8 s, before the cut.
  - The card-to-wheel travel, ~1 s, which is acceptable but repeated every card.
- Moments that felt instant where motion would explain cause and effect:
  - The turn rollover after SEND IT (a hard cut to the new turn number).
  - The victory banner.
  - The RAM changes and the negative "-N" tag, which never animate or explain themselves.
  - The node selection on the map.
  - Which card or slice was affected at turn start.
- Waiting: I could not tell the total split. Individual animations were all under 2 s, so deciding took up most of the time.

## 4. Problems (each with the contact sheet path)

| # | Moment | Sheet | What happened | Why it is a problem | Severity (glitch / unreadable / slow / polish) |
|---|---|---|---|---|---|
| 1 | Map node to fight | motion/0015_map_choice.png | The map froze for 0.4 s, then a dark half-built frame appeared, then the background popped in. | It reads as a loading pop, and the click gets no acknowledgement. | glitch |
| 2 | Map node to fight | motion/0017_map_choice.png, motion/0021_map_choice.png | About 0.8 s of almost no response, then a hard cut. | The click feels unregistered. | polish |
| 3 | Reward pick | motion/0016_reward_choice.png, motion/0022_reward_choice.png, motion/0023_reward_choice.png | The unpicked cards vanish at once, the sheet is blank for ~0.4 s, and the next sheet swaps in abruptly. | The pick is not confirmed and the next reward stage is easy to miss. | unreadable |
| 4 | Reward to map | motion/0020_reward_choice.png | A hard cut from a flat dark map to the detailed city map. | Nothing links the click to the result. | polish |
| 5 | Reward click | motion/0019_reward_choice.png | Only a subtle card tint change, with no fly-to-deck. | It is unclear which reward was taken. | polish |
| 6 | SEND IT and turn change | motion/0006_combat_mid_turn.png, motion/0009_combat_mid_turn.png | The turn counter swaps with no emphasis, and the hand redraws with no wheel feedback. | The player cannot see what the turn did. | unreadable |
| 7 | Turn start | motion/0005_combat_turn_start.png, motion/0018_combat_turn_start.png | Only a faint tint and a hand reflow. | There is no signal that a new turn began. | polish |
| 8 | Card onto own wheel | motion/0007_combat_turn_start.png | The arrow pointed at the enemy wheel while the card landed on mine, and the red marker arrived late. | Contradictory cause and effect. | unreadable |
| 9 | Fight won | motion/0012_combat_result.png, motion/0013_combat_result.png | The banner is static with no entrance. | The win has no weight. | polish |
| 10 | Tutorial win screen | n/a (no sheet) | There was no visible Continue prompt, and clicks did nothing. Esc opened the pause menu. | It looked like a soft-lock, and I had to quit to the main menu. | glitch |

## 5. Best and worst

- **Most satisfying motion:** The attack sequence in motion/0004_combat_mid_turn.png. Cards leave, a projectile crosses, sparks land and the HP ticks down in steps. The aim arrow and highlighted wedge in motion/0001_combat_turn_start.png are the clearest cue in the game.
- **Most confusing or annoying motion:** The reward pick and exit (motion/0016, 0022 and 0023). Blank slots, vanishing cards and a hard cut to a streaky map left me unsure what I took. The unexplained negative RAM tag is a close second, because the counter never animates its changes.
- **One change to the game's motion right now:** Give every click a visible acknowledgement and a short transition. That means a node pulse plus a quick fade on map entry, and a clear card-to-deck flight with the rejected cards dimmed on the loot sheet.

Focus questions:
1. **Skip after twice:** The loot-sheet blank gap and the map-click dead time.
2. **Cause and effect failures:** Turn rollover after SEND IT, the reward pick, map node entry, and the RAM tax tag.
3. **Flash, strobe or glitch:** No strobing. The only glitch was the single dark half-built frame on map-to-fight entry (motion/0015_map_choice.png).

## 6. Summary (machine-read by tools/playtest/aggregate.py)

```
SUMMARY
handle: halfmoon
persona: PB-003
focus: animation_feel
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 1
raids_survived: 0
playtime_min: 17
enjoyment: 5
rng_fairness: n/a
netrun_length: too short
campaign_length: too short
text_clear: no
op_picks: none
weak_picks: none
bugs: 10
top_frustration: Hard cuts and blank loot slots with no click feedback make cause and effect unreadable, and the RAM tax tag is never explained.
top_change: Add click acknowledgement and short transitions on map entry and reward picks, with a clear card-to-deck flight.
```