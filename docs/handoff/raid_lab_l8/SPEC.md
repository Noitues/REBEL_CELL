# Raid lab L8: the city raid (spec)

The designer asked on 2026-10-23 to move the raid onto the city view between the two HQs. They also asked for a click
phase that stands in for the netruns, and for minimal tower defense to come back. The lab is a playable demo, so
**ownership, the hunter and the beams must read on the city board**. No critic yet.

Everything lives in new folders:
- the rules oracle in `tools/raid_concepts/` (Python);
- the lab in `tools/raid_lab_city/` (Godot 4.7, GDScript, static typing, tabs).

Never touch `scripts/`, `content/` or `scenes/`. Deterministic: no global randi/randf; all randomness is seeded
`random.Random(n)` in Python and lives in the leg data.

## 1. The map
- **The grid:** a 4 × 3 grid of districts between the two HQs.
  - Columns `x = 0..3` (`W = 4`): x = 0 is next to **our HQ** (HOME, off-grid on the left, x = -1), and x = 3 is next to
    the **corp HQ** (off-grid on the right, x = 4).
  - Rows `y = 0..2` (`H = 3`) are the three **routes** (north, mid, south) running from the corp HQ to ours.
  - The three columns of cells are linked by **streets** (vertical).
- **Cell data:**
  - each cell has a **value** `v` in {4, 6, 8, 10, 12};
  - 3 cells with x ≥ 1 carry an **EXPLOIT** (a key needed for the final assault on the corp HQ).
- **Ownership** per cell: `NEUTRAL`, or owned with a status `OK`, `DOWN` or `TAKEN`. TAKEN is corp ground for the rest
  of the leg.
- **Leg start:** we own 2 seeded cells at x = 0 (status OK). Everything else is NEUTRAL.

## 2. A leg: 3 raids, each in phases
1. **CAPTURE (stands in for a netrun).** Claim exactly 1 NEUTRAL cell. The cell must be orthogonally adjacent to an
   owned non-TAKEN cell, or at x = 0 (adjacent to HOME). It becomes owned OK. You can't skip this.
2. **PLAN.** Place your sentries and the ghost.
   - Sentries: at most 1 per cell, on owned non-TAKEN cells.
   - Ghost: 0 or 1, from the kit, on an owned non-TAKEN cell or HOME. It costs +5 Heat.
3. **FORECAST.** The result of each of the 3 sealed candidates for this placement, assuming HOLD, plus the best
   response's result.
4. **LAUNCH:**
   1. beam 1;
   2. extra 1 if Heat ≥ 50, extra 2 if Heat ≥ 75 (Heat at launch includes the ghost's +5);
   3. **REVEAL** of the sealed beam;
   4. the **RESPONSE**;
   5. the sealed beam;
   6. the hunter.
5. **AFTERMATH**, with the tier stamp.
6. **BETWEEN** (not after raid 3):
   1. repair at most 1 DOWN cell, cost v // 2;
   2. build at most 1 sentry of a chosen type, cost `SENTRY_PRICE` = 4;
   3. pick an intensity.

   Bank is spent in that order. Then income is added and Heat rises.
7. **RECORD** after raid 3 or a breach.

## 3. Threats (typed)
- **Types:**

  | Code | Name | Shape | Look |
  |---|---|---|---|
  | `D` | DRONE | triangle | a drone swarm |
  | `N` | NETRUNNER | square | a data spike / ICE worm |
  | `E` | ENFORCER | circle | an armored convoy |

  Shape = type everywhere.
- **Every beam has a type and a line.** A line is an ordered list of cells.
  - **ROUTE line** (row y): it always runs from x = 3 to x = 0, then reaches **HOME**.
  - **STREET line** (column x): it runs y = 0→2 or 2→0, seeded, and does not reach HOME.
- **Beam 1, extra 1 and extra 2** are known and seeded per raid: kind (route or street), index, direction and type.
- **Sealed beam:** 3 candidates, always the three ROUTES. Each route carries a distinct type, a seeded permutation:
  candidate k = route k with type `perm[k]`. The real candidate is seeded per raid. The candidates are drawn with their
  shapes, so the player knows "one of these three convoys comes".
- **Hunter:** its type is known (seeded per raid). It sweeps the STREET (column) of the first touch of the raid, top to
  bottom (y = 0→2).
  - A first touch is any cell hit, or a sentry block, by beam 1, the extras or the sealed beam. HOME never counts.
  - With no touch it sweeps its own seeded street.

## 4. Resolving a line (both Python and GDScript)
Each raid keeps a `seen` set of cells hit this raid. HOME can be hit at most once per raid. Scan a line's cells in
order:
1. **A ghosted cell:** pass.
2. **A cell with a sentry of the beam's type: BLOCK.** Record the touch `(cell, "block")`, which counts as a touch.
   **The line stops**, and a route stopped this way never reaches HOME.
3. **An owned, non-TAKEN cell not in `seen`:** HIT. OK → DOWN, DOWN → TAKEN, and a TAKEN cell loses its sentry
   immediately. Record `(cell, "hit")`, add it to `seen`, continue.
4. **Otherwise** (NEUTRAL, TAKEN or already seen): pass.
5. **Reaching HOME (route lines only):** if HOME is not ghosted and has not been hit this raid, HOME −1. Record
   `("HOME", "home")`.

A sentry of another type does not block; its cell is hit normally, and the sentry survives DOWN. **EVADED** means no
touches at all: Heat −10 after the raid.

## 5. Response (after the reveal; it costs a SPOOF charge from the kit plus `SPOOF_HEAT` = 2 Heat, added after the sweep)
- **HOLD:** free.
- **REDEPLOY s → c:** move one placed sentry to another owned non-TAKEN cell with no sentry. It applies to the sealed
  beam and the hunter only, since beam 1 and the extras have already fired.
- **JAM:** the hunter does not run.

## 6. Kit, bank, Heat, score
- **Kit at leg start:**
  - sentries: one each of D, N and E (a pool by type; they persist across the leg, a TAKEN cell loses its sentry);
  - ghost 2;
  - spoof 2.
- **Ghost and spoof are spent per use.**
- **Sentry placement.** Each PLAN screen re-places all the sentries in the pool; placement starts from the previous raid's
  cells. A sentry lost on a TAKEN cell leaves the pool.
- **Money and Heat:**
  - `START_BANK` = 10, `START_HEAT` = 44;
  - extra beams at `EXTRA_AT` = 50 and `STRONG_AT` = 75;
  - `HOME_HP` = 3.
- **Intensity** (Heat added, income multiplier):

  | Intensity | Heat | Income |
  |---|---|---|
  | LOW | +6 | ×0.5 |
  | NORMAL | +12 | ×1.0 |
  | HOT | +18 | ×1.5 |

  Income = `int(sum(v // 3 over owned OK cells) * mult)`.
- **Tiers:**
  - BREACHED: HOME is 0;
  - DAMAGED: HOME lost integrity this raid;
  - EVADED: no touches;
  - BATTERED: 2 or more cells newly DOWN, or any newly TAKEN;
  - HOLDS: otherwise.
- **Score:** `bank + sum(v - (v//2 if DOWN)) over owned non-TAKEN + EXPLOIT_BONUS(6) per owned non-TAKEN EXPLOIT cell
  - 8 * HOME lost - 1.0 * max(0, Heat - 44)`. A breach scores -100 (shown as "campaign lost", no score).

## 7. Python oracle: `tools/raid_concepts/sweep_l8.py`
- **Dataclasses:** `Line(kind, index, cells, type, home)` (home is True for routes), `Raid`, `Leg`, `State`.
  `State` is frozen: heat, bank, home_hp, owned dict as a sorted tuple, sentries as a sorted tuple of (cell, type),
  pool counts, kit.
- **Functions:**
  - `make_leg(seed)`, `initial(leg)`, `capture_options(leg, st)`, `capture(leg, st, cell)`;
  - `placements(leg, st)`, which yields (sentry map, ghost);
  - `resolve(leg, raid, st, cand, place, response)`, which returns (state after, touches) and accepts any response;
  - `response_options(leg, raid, st, cand, place)`;
  - `between(leg, st, repair, build, intensity)`, `between_options`;
  - `tier`, `score`, `forecast(leg, raid, st, place)`;
  - `greedy_leg(leg)`, where each phase maximizes EV over the 3 candidates with the best response, and kit is valued
    `KIT_VALUE` = 2.5 mid-leg;
  - `naive_leg(leg)`: capture the highest-value option, keep sentries where they were (else the first cells), never
    ghost or respond, repair the biggest, NORMAL, build nothing.
- **`__main__`** runs 20 legs and prints SUMMARY JSON: greedy vs naive score, breach rates, response use, sentry
  blocks per raid, tier mix and capture choices. It writes `D:/rc_tmp/raid_design_lab/sweep_l8.json`.
- **Golden:** `tools/raid_concepts/l8_golden.py` writes `tools/raid_lab_city/data/l8_golden.json`:
  - config;
  - legs 0, 3, 5 and 8, each with its leg data and the greedy and naive lines step by step;
  - 200 random raids (random legal state, placement, candidate and response) with touches, tier, after-state and score;
  - 100 random between steps;
  - 100 random capture checks.

## 8. Godot lab: `tools/raid_lab_city/`
- **`l8_rules.gd`** (`class_name L8Rules`, RefCounted, static only): the port, with the same function names.
  Dictionaries carry the state.
- **`parity_check.gd`** (`extends SceneTree`): replays the golden and exits non-zero on any mismatch.
- **`l8_board.gd`** (`class_name L8Board`, Node3D, built in code, in a SubViewport): the **city view**.
  - **Look:** the target frames (`docs/design/raid_concepts/raid_target/`) and `l7_board.gd`.
  - **The board:** a dark slab city block, seen in iso with a long lens. **Our HQ** is a warm amber tower on the left
    and the **corp HQ** a cobalt (#3D6BFF) tower on the right. The 3 **routes** are lit roads between them, and the 4
    **streets** are thinner cross roads.
  - **Districts:** small building clusters.
    - NEUTRAL: dim gray.
    - Owned: a warm amber holo ring with a value-pip stack, and an EXPLOIT key glyph if present.
    - DOWN: a wrench and a flicker.
    - TAKEN: cobalt.
  - **Sentries:** holo decals on the cell. Type colors: drone = cyan, netrunner = magenta, enforcer = orange. Each has
    its shape on a small pylon.
  - **Ghost:** a dashed ring.
  - **Beams are typed vehicles/effects that travel** the line cell by cell along the road, each in its type color and
    shape:
    - drones: a swarm of small triangles;
    - netrunner: a fast glowing worm;
    - enforcer: a chunky convoy.

    A BLOCK is a shield flash where the vehicle stops. A HIT is a strike on the district. A route reaching HOME hits
    the HQ tower (a shake and a red integrity pip).
  - **Hunter:** a cobalt hound glyph that turns at the first touch and runs down the street.
  - **Sealed candidates:** ghosted convoys waiting at the corp HQ end of each route. At the reveal, two dissolve and the
    real one lights.
  - **API:** `setup(leg: Dictionary)`, `show_state(st: Dictionary, place: Dictionary)`,
    `cell_screen_pos(cell: Vector2i) -> Vector2`, `play(cues: Array, speed: float) -> Signal (finished)`, and
    `highlight(cells: Array, color: Color)`.
- **`raid_lab_city.gd` + `.tscn`** (a Control root; the UI is built in code): the phases from §2 as screens over the board.
  - **Layout:** a top HUD (Heat bar with 50/75 notches, raid i/3, HOME pips, bank, score), a right panel 420 px wide,
    and a bottom hint line. 1280 × 720, text 1.0, US English.
  - **CAPTURE:** legal cells glow; click one.
  - **PLAN:** keys 1–3 pick a sentry type, G picks the ghost, then click a cell; Z undoes, and Enter goes to the
    forecast.
  - **FORECAST:** per candidate (shape + route name): what gets hit, HOME, and the tier with HOLD and with the best
    response. Enter launches.
  - **RESPONSE:** rows HOLD / every REDEPLOY / JAM, each with its exact result. Click a row, or press H or J.
  - **BETWEEN:** click a DOWN cell to repair it, buttons for building a D, N or E sentry, and LOW / NORMAL / HOT cards
    with income and Heat after.
  - **RECORD:** per-raid tiers, cells kept, exploits kept, and the score.
  - **Speed:** keys 1, 2 and 4 during the playout; I toggles instant.
  - **Command-line flags:**
    - `--leg=N`;
    - `--auto=greedy|naive` replays the golden line;
    - `--shots=<abs dir>` saves a PNG per screen and per playout beat (instant beats), then quits;
    - `--scramble` replaces words with seeded noise.
- **`README.md`:** how to play, the rules in short, and the flags.
