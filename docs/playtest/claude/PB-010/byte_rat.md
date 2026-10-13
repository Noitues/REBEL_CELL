# Motion feedback — byte_rat · PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · session date not recorded

> Written by a Claude motion tester (docs/process/05_CLAUDE_PLAYTESTER.md §6). It played through
> the screen like any tester; at moments that should animate it captured a burst of frames
> (~15 fps, up to 5 s) and judged them as a contact sheet. It cannot hear sound and sees motion
> only as sampled frames: smoothness below ~15 fps, easing curves and sub-frame flicker are out
> of its reach. Contact sheets are in the session folder's `motion/`.

## 1. Session

- **Tester / persona:** byte_rat / Explorer / completionist
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740 · **Played:** 60 min · **Moments judged:** 38
- **Settings:** defaults

## 2. Verdict per moment type

| Moment type | Seen | Typical duration | Verdict | What reads well | What does not |
|---|---|---|---|---|---|
| Card played onto a wheel | Yes (several) | 0.9–1.85 s | Hard to follow | Arrow and ring show which card goes to which wheel; card is absorbed with sparks (sheet 0005) | After the absorb the effect is muddled. Little impact: no hit flash, number pop or shake. Result tags are tiny. Sheets 0003, 0004, 0007, 0008 show the card never visibly leaves or resolves. |
| Nudge / spin | Yes | ~1.1–1.7 s | Clear but flat | Yellow targeting line draws in about 0.2 s (sheet 0002) | After the aim line, nothing changes. Sheet 0021: wheel spin and segment shuffle have no clear link to the card. |
| SEND IT resolution (needles, damage, block) | Yes | 2.2–2.4 s | Hard to follow | Beam from player wheel to enemy, with HP ticking down (sheets 0019, 0020) | Crowded; thin lines get lost on the busy background; damage numbers are tiny; wheels change with no visible transition. |
| Perfect / precision hit | Yes | within the SEND IT bursts | Clear but flat | PERFECT tag appears on the wheel | Underplayed. The tag lingers and vanishes with no payoff (sheets 0018, 0019). |
| Enemy turn / pointer attack | Yes | ~0.2–0.5 s | Hard to follow | Red return line from the enemy wheel is visible (sheet 0019) | Arrives after a lull and feels disconnected from the player's strike. |
| Fight won / lost | Yes | ~4.8 s (win) | Clear but flat | Win finale is the best beat: wheel shatters, FIGHT WON and OURS NOW text (sheet 0012). | Middle of the sequence is weak and long. Defeat screen showed no animation (sheet 0026). The loot screen after a win was already settled with no entrance (sheets 0022, 0031). |
| Reward reveal and pick | Yes | 0.9–1.8 s | Hard to follow | Chosen card flies to the deck | Unchosen cards vanish at once, leaving blank white slots for ~0.5 s. Hard cut to the map or a second sheet. Error toast gone in ~0.25 s (sheet 0040). |
| Map move / node entry | Yes | 0.7–1.8 s | Janky or glitchy | Route line draws quickly (sheet 0024) | Hard cut to a dark combat frame with the UI placed but no background. Background then pops in with no fade (sheets 0017, 0030). |
| Screen transitions (title, HQ, city, menus) | Yes | 0.4–2.5 s | Clear but flat | Jack-in typed command line is a nice thematic touch. Summary glitch-out is stylish. | Small and low contrast. About 0.7 s of dead "Connecting to HQ" hold. HQ layout slides and snaps in (sheet 0034). Menu clicks showed no feedback (sheets 0001, 0014). Pause blur is a hard cut. |
| Raid playout | Yes | ~5 s | Hard to follow | Report card appears quickly | Tiny low-contrast dots on a dark map. The stamp lands with no punch. The live feed is small text. |
| City Grid recolour / claim | Not encountered | – | – | – | – |

## 3. Pacing

- Animations you would want to skip after seeing them twice: SEND IT resolution (~2.2–2.4 s), win finale (~4.8 s), "Connecting to HQ" hold (~0.7 s of dead time, ~1.8 s total), raid playout (~5 s).
- Moments that felt instant where motion would explain cause and effect: picking a loot card, event choices (sheet 0033), menu clicks, the Fine Tune nudge in my notes (RAM spent but no visible change until the turn resolved), and aiming a card after another card had been played.
- Waiting: I couldn't measure the split. Resolves and transitions were each a few seconds, which felt long when repeated across many turns.

## 4. Problems (each with the contact sheet path)

| # | Moment | Sheet | What happened | Why it is a problem | Severity (glitch / unreadable / slow / polish) |
|---|---|---|---|---|---|
| 1 | Turn rollover | motion/0006_combat_mid_turn.png | Header flipped Turn 1, Turn 2, then Turn 1 again within 1.3 s | Looks like a state flicker and confuses the turn number | glitch |
| 2 | Map to combat | motion/0017_map_choice.png, motion/0030_map_choice.png | Hard cut to a dark frame with UI but no background; background pops in later | Reads as a loading glitch | glitch |
| 3 | Card played | motion/0004_combat_mid_turn.png, motion/0007_combat_mid_turn.png, motion/0008_combat_mid_turn.png | Card never visibly leaves or lands; no number change | Cause and effect missing | unreadable |
| 4 | SEND IT | motion/0019_combat_turn_start.png, motion/0018_combat_turn_start.png | Overlapping beams and particles with tiny damage numbers | Can't tell who hit whom or for how much | unreadable |
| 5 | Reward pick | motion/0023_reward_choice.png, motion/0032_reward_choice.png, motion/0039_reward_choice.png | Blank white slots for ~0.5 s, then an abrupt swap or cut | Looks like a dead beat or a glitch | polish |
| 6 | Reward click rejected | motion/0040_reward_choice.png | Error toast gone in ~0.25 s | Can't be read; the click gave no card feedback | unreadable |
| 7 | Event choice | motion/0033_event_choice.png | Only a tiny tag colour change; no outcome shown | Player can't tell the click registered | unreadable |
| 8 | Raid playout | motion/0036_raid_setup.png, motion/0037_raid_playout.png | Tiny dots, a flickering icon, a pop-in CONTINUE button | Outcome unreadable | unreadable |
| 9 | HQ arrival | motion/0034_summary_or_end.png | Layout offsets then snaps; ~0.7 s dead hold | Janky and slow | slow |
| 10 | Menu and pause clicks | motion/0001_menu.png, motion/0014_menu.png, motion/0013_combat_result.png | No press feedback; pause panel jumps between frames | Weak response | polish |

## 5. Best and worst

- **Most satisfying motion:** The fight-won finale: the enemy wheel shatters into pieces and OURS NOW appears (motion/0012_combat_turn_start.png). The glitch-out exit from the run summary also felt stylish (motion/0034_summary_or_end.png).
- **Most confusing or annoying motion:** Card aiming and the resolve. Brute Spin aims fizzled repeatedly, and one stuck aim took about fifteen steps to clear. Fine Tune spent RAM with no visible effect until the turn resolved. Those turns gave no cause and effect (motion/0004_combat_mid_turn.png, motion/0021_combat_turn_start.png).
- **One change to the game's motion right now:** Put a big, readable hit on every resolve (damage number pop, wheel shake and a wedge pulse) and make a card visibly fly into its slot. That would also let me trim the SEND IT sequence.

Focus questions:
1. Skip after seeing twice: the SEND IT resolve, the win finale, and the "Connecting to HQ" hold.
2. Cause and effect failed in card plays, the nudge, the reward pick, event choices, menu clicks and the raid playout.
3. Flash or strobe: no flash risk seen. The turn header flicker (#1) and the map-to-combat pop-in (#2) were the glitches.

## 6. Summary (machine-read by tools/playtest/aggregate.py)

```
SUMMARY
handle: byte_rat
persona: PB-010
focus: animation_feel
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 4
raids_survived: 2
playtime_min: 60
enjoyment: 5
rng_fairness: n/a
netrun_length: just right
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: none
bugs: 10
top_frustration: Card aiming got stuck and cards or nudges showed no visible effect, so I couldn't see cause and effect.
top_change: Add bold hit feedback on resolve and a visible card-to-slot animation.
```