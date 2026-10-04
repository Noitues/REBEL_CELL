# Round 32: UI chrome fixes (designer review of round 31)

Round 31's rules still apply (see `../round31_ui_chrome/NOTES.md`). This round changes only the four points below.

## 1. ABANDON RUN: both buttons are stickers
See `abandon_dialog.png`. The kit's modal in `ui_kit.png` follows the same rule.
- **CANCEL** is the *calm* sticker: slate ink lettering on white vinyl (`FILL_CALM` #545C6E → #242834). It has **default focus**, because it is the safe choice.
- **BURN IT** is the *hot* sticker: pink.
- Each sticker carries a plain line under it: "keep running [B]" and "abandon, lose GHOST [hold A]".

The dialog body stays terminal. Its costs follow GDD 4.2:
- the operative is lost with everything unbanked;
- Heat rises by 10 + tier (+12 at tier 2);
- Schematics already banked at a Server Rack stay banked.

**Proposal (open question):** on a pad, BURN IT needs a 0.8 s **hold**, shown as a lime ring filling, so a stray press can't end a run. B cancels at once. A mouse click works directly.

The states strip shows:
- CANCEL: idle, focus and pressed;
- BURN IT: idle, hover, hold and pressed.

## 2. Title menu wording: no more EXFIL
The menu the game needs (art_asset G1/G2/G7, GDD 1.3):
- Continue (with the slot summary)
- New campaign
- Campaign slots
- Tutorial
- Codex
- Stats & achievements
- Options
- Quit

Every punchy verb keeps a **plain-language label** with it, so the meaning is never lost.

**Option A, "THE PLAN"** (`title_screen.png` + `title_screen.gif`). The designer's three verbs become the three big actions. They are numbered in grease pencil, with a bracket, so the plan *is* the menu. Each sticker sits beside a terminal chip that holds the plain meaning.

| Sticker | Plain label | Detail |
|---|---|---|
| 1. BREACH (hot pink, default focus) | CONTINUE | slot 1 // Halcyon Civic // run 9 // Heat 58 |
| 2. DISABLE (calm) | TUTORIAL | learn the wheels on a practice target |
| 3. OVERTHROW (calm) | NEW CAMPAIGN | pick a corporation to bring down |

The rest of the menu sits in a terminal MORE panel in plain words: CAMPAIGN SLOTS, CODEX, STATS & ACHIEVEMENTS, OPTIONS, QUIT. DISABLE → Tutorial is the weakest pairing. The alternative is DISABLE → CAMPAIGN SLOTS, "take over a saved Cell".

**Option B, "one verb per item"** (`title_screen_option_b.png`). BREACH is the one sticker (CONTINUE + slot summary). Every terminal line is a verb with its item underneath:

| Verb | Item |
|---|---|
| OVERTHROW | new campaign |
| CASE FILES | campaign slots: load, delete |
| DRILL | tutorial |
| INTEL | codex |
| RAP SHEET | stats & achievements |
| RIG | options |
| GO DARK | quit |

"1. BREACH / 2. DISABLE / 3. OVERTHROW" stays as the Cell's grease-pencil slogan, top right.

My pick is **A**. It uses the designer's words and keeps three big, readable choices. The seven verbs in B are fun, but they cost a beat of reading for each line.

The typography board's pencil sample now reads 1. BREACH / 2. DISABLE / 3. OVERTHROW.

## 3. Corp paperwork: Courier Prime (SIL OFL 1.1)
- Every paper sample now uses the shippable stack:
  - typewriter fields and document titles: **Courier Prime** Regular / Bold;
  - letterheads: **IBM Plex Sans Condensed Medium**, already in the repo;
  - stamps: Anton.
- Bahnschrift is gone from the paper medium.
- **Font files not yet fetched:**
  - The download needs the user's own go-ahead in chat. An agent message relaying approval doesn't count, so nothing was downloaded.
  - `scripts/fetch_courier_prime.py` is ready. It fetches `CourierPrime-Regular.ttf`, `CourierPrime-Bold.ttf` and `OFL.txt` (saved as `OFL_CourierPrime.txt`), each well under 100 KB, from the Google Fonts repository (`github.com/google/fonts/main/ofl/courierprime`) into `fonts/`.
  - Until then, `ui31.PRIME` is False and Courier New stands in, and the typography board says so in its licence lines.
  - After fetching, re-run `typography.py`, `ui_kit.py` and `abandon.py`. The boards pick the files up automatically.
- For Godot: import both as MSDF like the other faces (`assets/fonts/README.md`). Add a README row: *Courier Prime, corp paperwork, OFL 1.1*.

## 4. Backdrops: no fist roads, the latest Meridian fortress
Both the map HUD and the title now start from round 30's `city_night_hq_v6.jpg`. That is the same render as `hq_meridian_city.jpg` (same script run), so it carries the latest container fortress. Round 31's title used round 25's v3 map with the old Meridian.

`scripts/defist.py` replaces the red fist roads under REBEL_CELL with ordinary city blocks:
1. A mask is made from the saturated-red road pixels inside the Cell district.
2. Each masked pixel takes city cloned from 4-9 iso street steps away (14.35 x 7.17 px per step on the 2560 map). The least-red candidate is chosen per region, using a 36 px blurred score, so neighbouring pixels come from the same source and the patches stay whole.
3. The Cell's base buildings are never used as a clone source.
4. Any leftover red glow is pulled back to night asphalt.

The REBEL_CELL label is kept on the map. The title still patches out all territory labels, as in round 31.
- This is a concept-board fix only. The real map should re-render the district once its redesign lands.

## Files
| File | What |
|---|---|
| `typography.png` | Paper row: Courier Prime + Plex letterhead + Anton stamp. Pencil sample: OVERTHROW. |
| `ui_kit.png` | The modal uses CANCEL (calm sticker, focus) + BURN IT (hot sticker); the paper panel uses the new stack. |
| `abandon_dialog.png` | The full ABANDON RUN dialog over a paused netrun, plus the state strip. |
| `title_screen.png` / `title_screen.gif` | Option A, over the fixed v6 city: 960x540, 48 x 80 ms, seamless. |
| `title_screen_option_b.png` | Option B. |
| `city_map_hud.png` | Round 31's HUD on the fixed v6 map. |
| `contact_sheet.jpg` | Everything above on one page. |
| `scripts/` | All scripts. Run them from this folder in this order: `city_frames.py`, then the boards (`typography.py`, `ui_kit.py`, `abandon.py`, `title.py`, `city_hud.py`), then `contact.py`. `fetch_courier_prime.py` runs only after approval. |
| `fonts/` | Empty until Courier Prime is fetched. |

The round 31 scripts were copied unchanged except:
- `ui31.py`: Courier Prime paths, `FILL_CALM`, Anton stamps;
- `bases.py` and `city_hud.py`: the defisted v6 base;
- `title.py`: options A and B;
- `typography.py` and `ui_kit.py`: the new paper stack and the two-sticker modal;
- `contact.py`: the round 32 contents.

## Open questions
1. Approve the Courier Prime download? See point 3 for the files and source.
2. Title: option A or B? If A, is DISABLE → Tutorial right?
3. Hold-to-confirm for BURN IT on a pad?
