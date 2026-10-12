# Motion feedback — <handle> · <batch> · build <sha> · <date>

> Written by a Claude motion tester (docs/process/05_CLAUDE_PLAYTESTER.md §6). It played through
> the screen like any tester; at moments that should animate it captured a burst of frames
> (~15 fps, up to 5 s) and judged them as a contact sheet. It cannot hear sound and sees motion
> only as sampled frames: smoothness below ~15 fps, easing curves and sub-frame flicker are out
> of its reach. Contact sheets are in the session folder's `motion/`.

## 1. Session

- **Tester / persona:** <handle> / <persona label>
- **Build:** main @ <sha> · **Played:** <minutes> min · **Moments judged:** <n>
- **Settings:** <defaults / reduce effects on / ...>

## 2. Verdict per moment type

| Moment type | Seen | Typical duration | Verdict | What reads well | What does not |
|---|---|---|---|---|---|
| Card played onto a wheel | | | | | |
| Nudge / spin | | | | | |
| SEND IT resolution (needles, damage, block) | | | | | |
| Perfect / precision hit | | | | | |
| Enemy turn / pointer attack | | | | | |
| Fight won / lost | | | | | |
| Reward reveal and pick | | | | | |
| Map move / node entry | | | | | |
| Screen transitions (title, HQ, city, menus) | | | | | |
| Raid playout | | | | | |
| City Grid recolour / claim | | | | | |

Verdicts: clear and satisfying · clear but flat · too slow · too fast · hard to follow ·
janky or glitchy · flash/comfort risk · no animation seen.

## 3. Pacing

- Animations you would want to skip after seeing them twice: <list with durations>
- Moments that felt instant where motion would explain cause and effect: <list>
- Waiting: total time spent watching animations vs. deciding, if you could tell: <answer>

## 4. Problems (each with the contact sheet path)

| # | Moment | Sheet | What happened | Why it is a problem | Severity (glitch / unreadable / slow / polish) |
|---|---|---|---|---|---|

## 5. Best and worst

- **Most satisfying motion:** <answer + sheet>
- **Most confusing or annoying motion:** <answer + sheet>
- **One change to the game's motion right now:** <answer>

## 6. Summary (machine-read by tools/playtest/aggregate.py)

```
SUMMARY
handle: <handle>
persona: <persona id>
focus: animation_feel
build: <sha>
outcome: WON | LOST | ABANDONED | INCOMPLETE
netruns_completed: <n>
operative_deaths: <n>
raids_survived: <n>
playtime_min: <n>
enjoyment: <1-10>
rng_fairness: <1-5 or n/a>
netrun_length: too short | just right | too long
campaign_length: too short | just right | too long
text_clear: yes | no
op_picks: none
weak_picks: none
bugs: <n motion problems>
top_frustration: <one line>
top_change: <one line>
```
