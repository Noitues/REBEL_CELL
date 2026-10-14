# PT-003 — Plan 1 waves 3–5 (overnight): city clarity, PT-002 bug fixes, rewards screen, input prompts, combat motion

since gate/PT-002 · main @ 1eda2a92 (batch build 3eac0f08) · 2026-10-14 · build: run from the editor (F5) or `godot --path .`
**Scope: text size 1.0, mouse and keyboard only.** Leave Options at 1.0, reduce effects OFF.
Built unattended overnight (DECISIONS "Overnight run"); every call made without you is logged there, with open
questions under "Open questions for the designer". Review sheets: `docs/art_review/PLAN1/W3_*.jpg`, `W3B.jpg`,
`W3_POLISH.jpg`, `W4_*.jpg`, `ANIM_COMBAT.jpg` (+ `ANIM_FLOW.jpg` if it merged).

## 1. Scope and changes (what is new for you)
- **City Grid (W3-GRID):**
  - Reachable Sites carry their name tag and orange ring.
  - Hovering or selecting a locked Site says "LOCKED: clear X first", rings that Site twice (+ CLEAR FIRST) and pans
    to it.
  - Site files forecast Heat ("FLATLINE: HEAT +N -> T", the raid line it crosses); Heat Scrub says why it is
    unavailable.
  - GRID VIEW during a run frames the run path and its target, with no node choices.
- **Route map (W3-ROUTE):**
  - A click selects a node; CONFIRM (or Enter) travels; number keys still travel at once.
  - Each node type has its own corner badge shape (the key strip shows the same).
  - A node file shows "HP: n / max on arrival" and where you heal; AT LARGE no longer hides max HP.
- **Raids (W3-RAID):**
  - 0 crew: a warning, and START DEFENSE asks first.
  - "HOME SERVER" everywhere.
  - The report's outcome word matches its stamp; CELL HOLDS is pencil, the rest of the pencil is gone.
  - A placed defense shows on its node; the glitch notches are a smear.
- **HQ (W3-HQ):**
  - All operatives flatlined: a FREE HIRE card leads the crew hand and JACK IN says why it's off.
  - No count lines on CREW / MARKET; CLAIMED stamps don't stack; the raid-queued note sits in the foot band.
- **PT-002 bugs (W3B):**
  - A card or nudge aim always cancels (Esc, right-click, Z, UNDO, Q/E, switching target) with no leftover RAM debt.
  - UNDO-blocked names the event ("… rolled a random result"); Q/E say why when no free nudge is left.
  - The tutorial never appears in real fights.
- **Rewards (W4):** a fight with two or more picks shows one list; open a row to pick or SKIP it (that pick only);
  PROCEED asks before giving up the rest.
- **Input prompts (W4):**
  - One chip look for every key prompt.
  - A Menu button at the top left (left of Heat).
  - Clicking outside the pause menu closes it.
- **Combat motion (ANIM-COMBAT):**
  - The wheel turns as a played card lands.
  - Damage numbers land on the HP counter and pulse it.
  - A PERFECT tag flies into the hit.
  - The enemy strikes back with no lull.

Known limits (not FAILs): 1.6 / 2.0, high contrast and gamepad are deferred. The Genome Core is unchanged (content
pass). Number keys on the route still travel without CONFIRM (open question).
Settings touched: none.

## 2. Playtest steps
| # | Where (reach it) | Do | Look for | PASS when | Time |
|---|---|---|---|---|---|
| 1 | Options | Reduce effects OFF, text 1.0 | — | (setup) | 1 |
| 2 | Title → NEW RUN → HQ | Look at the City Grid | tags, rings | Reachable Sites are named and ringed; you can tell where to go first | 2 |
| 3 | HQ Grid | Hover, then click, a locked Site | lock reason | It says what to clear first; that Site gets a double ring + CLEAR FIRST and comes into view | 2 |
| 4 | HQ Grid | Select a runnable Site | Site file | FLATLINE shows "HEAT +N -> T" on one line and the raid line under it | 1 |
| 5 | HQ → CORE (HOME SERVER card) at 0 Schematics | — | Heat Scrub | Disabled with the reason; the card's text doesn't clip | 1 |
| 6 | JACK IN → route map | Click a node, then CONFIRM | select / travel | The click only selects (file shows); CONFIRM travels; Enter also travels | 2 |
| 7 | Route map | Read the badges and the key strip; open a node file | shapes, HP | Each node type has its own shape; the file shows HP on arrival and heals | 2 |
| 8 | During a run → GRID VIEW | — | run path | The path and its target are on screen; no node choices there | 1 |
| 9 | Any fight | Start an aim (Fine Tune / Jolt / free nudge), then press Q or E, or switch target | aim | The aim ends cleanly; no arrow or RAM debt stays | 2 |
| 10 | A fight after a respin or random card | Press UNDO / Z | reason | The message names what blocked it | 1 |
| 11 | Any fight | Play a card; SEND IT | motion | The wheel turns as the card lands; numbers land on the HP counter; no beam overlap; the enemy strikes right after | 3 |
| 12 | A fight where you land a PERFECT | — | payoff | The PERFECT tag flies into the hit | 1 |
| 13 | Win a fight with 2+ picks | Open a row, take or SKIP; then PROCEED with one left | rewards list | Each row marks TAKEN / SKIPPED; SKIP skips only that pick; PROCEED asks first | 3 |
| 14 | HQ or the route | Click Menu (top left); click outside the pause menu | menu | Menu opens pause; an outside click closes it; prompts all share one chip look | 2 |
| 15 | HQ with 0 crew alive (let the crew flatline) | Look at CREW; try JACK IN | recovery | A FREE HIRE card is first; JACK IN says why it's off; hiring makes you deployable | 4 |
| 16 | HQ → a raid with 0 crew → START DEFENSE | — | warning | A warning shows and START DEFENSE asks first | 2 |
| 17 | Raid setup | Drop a defense card on a node | node | The node itself shows the defense (ring + pip) | 1 |
| 18 | Raid report | Read it | wording | The outcome word matches the stamp; CELL HOLDS is pencil; no circles / ticks | 2 |
| 19 | Tutorial, then a netrun fight | — | overlay | No tutorial box in real fights | 2 |

Total: ~35 min

## 3. Expected vs actual (how to judge)
PASS = the "PASS when" sentence holds at first sight.
FAIL = it does not, or anything crashes, hangs, shows a `KEY_` / rules-English string, loses input,
or looks wrong for more than a second.
PARTIAL = passes with a nit you would still ship (say what).
SKIP = could not run the step (say why).

## 4. Feedback (paste back as is)
```
PLAYTEST: PT-003
STATUS: PASS | FAIL | PARTIAL
STEPS: <only the steps that are not PASS, e.g. "3 FAIL, 7 PARTIAL, 12 SKIP">
LOGS: <optional: path to the Godot log, or the ERROR lines>
NOTES: <optional: "<step>: <what you saw>" per line>
```
