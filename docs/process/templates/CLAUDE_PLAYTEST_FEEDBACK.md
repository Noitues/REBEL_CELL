# Playtest feedback — <handle> · <batch> · build <sha> · <date>

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** <handle>
- **Persona / focus / quirks:** <persona label> / <focus label> / <quirks>
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ <sha>
- **Total playtime:** <wall-clock minutes from first start to the end screen> (<n> actions,
  <n> sessions if the game was quit and continued)
- **Campaign setup:** corporation <name>, ICE <n>, home server <variant>, starting roster
  <classes>, campaign code <code if the game shows one, else "not shown">
- **How far did you get?** (tick one, fill the numbers)
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**: home server **BREACHED** after <n> netruns, in a raid triggered by <cause>
  - [ ] Campaign **won**: final server breached after <n> netruns
  - [ ] Campaign **abandoned** / could not continue (why: bug, soft-lock, out of time)
  - Netruns: <n> started, <n> completed, <n> operative deaths (where: Router / Elite Router /
    Server Rack, layer <n>)
  - Highest Site tier reached: T<n> · Exploits held: <n> · Sites claimed at the end: <n>
  - Raids: <n> survived (CELL HOLDS), <n> nodes lost (DOWN / TAKEN)
  - Final Heat: <n> (band) · Home server integrity: <n>/<max>
- **Overall enjoyment (1–10):** <n> — <one sentence why>

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? <answer>
  - Did SEND IT ever give a different result from the preview chips? <no / yes: turn, numbers, screenshot>
  - Did UNDO / rewind behave as expected? <answer>
- **Card balance & utility:**
  - Overpowered / automatic picks (cards, Firmware, Daemons) and why: <list or "none seen">
  - Useless / never worth picking, and why: <list or "none seen">
- **Synergies & archetypes:**
  - Per operative/class you ran: did a strategy come together (e.g. big spins, precision
    Perfects, drones, nudge control), or was the deck a random pile? <answer>
- **Card text & clarity:** easy to understand at a glance? <Yes / No> — confusing cards,
  keywords, slice icons, statuses or numbers: <list>

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun <too short / just right / too long> (~<n> min each);
  whole campaign <too short / just right / too long> (~<n> min)
- **Netrun map & encounters:** did Routers, Elite Routers, Terminals (events), Mainframes
  (shops) and Server Racks stay engaging or repeat? <answer>
- **City Grid & HQ:** were Site choices meaningful? Recruiting, stationing, installing
  nodes, spending Schematics: <answer>
- **Heat:** could you predict and manage it? Did thresholds and their raids feel fair? <answer>
- **Raids:** were the setup, projected outcome and playout understandable and fair? <answer>
- **RNG & fairness (1–5, 1 = always fair, 5 = felt cheated):** <n> — <the moment that set the score>
- **Permadeath & meta-progression:** did losing an operative feel earned? Did profile
  unlocks / ICE make you want to start another campaign right away? <answer>

## 4. UI, controls & audio

- **Information in combat:** easy to see deck / discard / draw piles, RAM, HP, enemy wheels
  and pointers (what the enemy will do)? <answer>
- **Information outside combat:** map, City Grid, HQ, raid setup — anything you looked for
  and could not find? <answer>
- **Controls:** mouse and keyboard smooth and responsive? Missing or unshown shortcuts,
  lost or doubled inputs: <answer>
- **Visual feedback:** did card plays, spins, hits and Perfects feel impactful on screen?
  (Audio not judged: the run is muted.) <answer>

## 5. Focus questions (<focus label>)

1. <question> — <answer>
2. <question> — <answer>
3. <question> — <answer>

## 6. Open feedback

- **Favourite moment or build:** <answer>
- **Biggest frustration / moment you wanted to quit:** <answer>
- **One thing to change or add right now:** <answer>

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity (crash / blocker / wrong / cosmetic) | Shot |
|---|---|---|---|---|---|---|

**Confusion log** (moments you did not know what to do): `<time> — <screen> — <what> — <how long, what resolved it>`

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: <handle>
persona: <persona id>
focus: <focus id>
build: <sha>
outcome: WON | LOST | ABANDONED | INCOMPLETE
netruns_completed: <n>
operative_deaths: <n>
raids_survived: <n>
playtime_min: <n>
enjoyment: <1-10>
rng_fairness: <1-5>
netrun_length: too short | just right | too long
campaign_length: too short | just right | too long
text_clear: yes | no
op_picks: <comma-separated names or none>
weak_picks: <comma-separated names or none>
bugs: <n>
top_frustration: <one line>
top_change: <one line>
```
