# PT-001 — M14 close-out group 2

since 6fb177a4 · main @ 4780b5c0 · 2026-10-12 · build: run from the editor (F5) or `godot --path .`

## 1. Scope and changes (what is new for you)
- Big text (Options → text size 1.6 / 2.0): save slots show a compact folder (tab, corp, Heat) with LOAD, DELETE
  and the CAN'T UNDO pencil under it; ICE / RUNS / FILED move to LOAD's tooltip. No paging inside a folder.
- Codex: the tab pager's `< +n` / `+n >` arrows show only when there is something to page to.
- HQ Grid: the camera never shows past the city's edge; the boss's TARGET pencil is never under a panel (an edge
  arrow shows instead, one TARGET only); Site names step aside from the pencil.
- HQ: the hand, the selected card and the Heat terminal page with MORE instead of clipping at big text.
- Raid: setup's INTERCEPTED warning is a toast in the foot band (in place of ON AIR) — no standing corp band; SAVED
  clears MAP KEY; INCOMING pencilled once; the after-action report shows CELL HOLDS on page 1 at big text; Continue on
  the raid result is a pink verb sticker whose whole word shows with focus.
- Mainframe (between runs): read blocks, REMOVE A CARD cards, loadout spinner words and the Daemon tray fit at 1.0–2.0.
- Combat: the fanned hand keeps every card's cost and title visible at rest (1.0 / 1.6 / 2.0).
- High contrast (Options): every screen; drawn words (combat numbers, card names) lift to 7:1. Colour-blind setting:
  the Grid's pending raid route is barbed.
- Campaign loss: no raid toast after the loss; DISPATCH's subtitle reads through the takeover; the corp memo's routing
  line wraps.
- New campaign: no line from the previous campaign's dialogue shows again.

Known limits (not FAILs): REBEL_CELL / Halcyon Central Server is off-frame on the Grid by design (edge arrow);
a two-line raid warning toast grows upward from the foot band by about one line at 2.0.
Settings touched: text size, high contrast, colour-blind, reduce effects (steps say when; set back after).
Seed for the campaign steps: any NEW RUN (no seed needed); pick the corp the step names.

## 2. Playtest steps
| # | Where (reach it) | Do | Look for | PASS when | Time |
|---|---|---|---|---|---|
| 1 | Title → Options | Set text size 2.0, back to Title → CONTINUE / LOAD | the save slots | each folder shows tab, corp and Heat, with LOAD, DELETE and "CAN'T UNDO" whole under it; no folder cut in half | 2 |
| 2 | Slots (step 1) | Move focus onto LOAD, then scroll to the next folder | tooltip; paging | ICE / RUNS / FILED appear in LOAD's tooltip; the page moves a whole folder at a time | 1 |
| 3 | Options | Text size 1.6, back to slots | the pencil | "CAN'T UNDO" is whole and its arrow starts after the O | 1 |
| 4 | Title → CODEX | Page the tabs left and right to both ends | the `< +n` / `+n >` arrows | an arrow shows only when there are tabs hidden on its side; the row never jumps | 1 |
| 5 | NEW RUN → Meridian, text 1.0 → HQ | Look at the Grid | city edge; TARGET | no black void past the city edge; the boss shows as one edge arrow, not a pencil under the crew hand | 2 |
| 6 | Same HQ, text 2.0 | Look at the Grid, then select a Site | edge; labels; card | no void past the edge; no Site name sits on the TARGET arrow / word / chip; the Site card stays above JACK IN | 2 |
| 7 | NEW RUN → REBEL_CELL, text 2.0 → HQ | Look at the TARGET arrow | the "Old Safehouse" label | the label stands clear of the arrow's chip (a small gap) | 1 |
| 8 | HQ at text 2.0 | Page the hand and the Heat terminal (MORE) | clipping | every card and the Heat page show whole; MORE pages them | 2 |
| 9 | HQ → let a raid arrive → raid setup (text 1.0) | Watch the top and the foot of the screen | the corp warning | INTERCEPTED appears as a toast in the foot band for ~2 s, then ON AIR returns; no standing band under the title | 2 |
| 10 | Raid setup at text 2.0 | Look at the top bar after a save | SAVED vs MAP KEY | SAVED never sits on the MAP KEY chip | 1 |
| 11 | Raid setup → START DEFENSE | Watch the playout | pencil words | INCOMING is written once, at the entry Site | 2 |
| 12 | Raid ends → report (text 2.0) | Read page 1 | the verdict | CELL HOLDS (or the loss verdict) is on page 1, over the paper's lower right | 1 |
| 13 | Raid result | Focus / hover Continue at text 1.0 and 2.0 | the sticker | Continue is a pink sticker; the whole word CONTINUE shows with the fold | 1 |
| 14 | HQ → JACK IN → combat (text 2.0) | Look at the fanned hand at rest | card faces | every card's cost number and title are readable; only body-line ends tuck under | 2 |
| 15 | Combat → finish a run → Mainframe (text 2.0) | Open REMOVE A CARD and the loadout spinner | fit | cards whole, spinner words whole, the Daemon tray beside ROUTE, nothing off screen | 3 |
| 16 | Options → High contrast ON; visit Title, HQ, raid setup, combat | Read every word | contrast | every word reads clearly on a solid backing, including combat damage numbers and card names | 4 |
| 17 | Options → Colour-blind ON → HQ with a raid pending | Look at the dashed what-if raid route | the route | the route carries barbs/ticks and reads apart from the network | 1 |
| 18 | A campaign you lose (let Heat run out or the HQ fall) | Watch the takeover end | toast; subtitle; memo | no raid toast after the loss; DISPATCH's subtitle reads over the takeover; the corp memo's routing line wraps whole | 5 |
| 19 | After step 18 → NEW RUN | Watch the first HQ / DISPATCH lines | dialogue | no line from the previous campaign shows again | 2 |
| 20 | Options | Set text size 1.0, high contrast OFF, colour-blind OFF | settings | settings back to how they were | 1 |

Total: ~37 min

## 3. Expected vs actual (how to judge)
PASS = the "PASS when" sentence holds at first sight.
FAIL = it does not, or anything crashes, hangs, shows a `KEY_` / rules-English string, loses input,
or looks wrong for more than a second.
PARTIAL = passes with a nit you would still ship (say what).
SKIP = could not run the step (say why).

## 4. Feedback (paste back as is)
```
PLAYTEST: PT-001
STATUS: PASS | FAIL | PARTIAL
STEPS: <only the steps that are not PASS, e.g. "3 FAIL, 7 PARTIAL, 12 SKIP">
LOGS: <optional: path to the Godot log, or the ERROR lines>
NOTES: <optional: "<step>: <what you saw>" per line>
RULINGS: <optional: answers to CP-002, "1A 2C">
```
