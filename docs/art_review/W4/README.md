# W4 Cards (branch `art/w4-cards`, from `art-pass`)

ART_BIBLE §6.3, §7.3, §7.4, §2 (PAPER), §4.3, §8. Presentation only: no rule, content value
or save format changed; no content `.tres` edited.

## Images

| File | What it shows |
|---|---|
| `cards_1.0.png`, `cards_1.6.png`, `cards_2.0.png` | `tools/design_lab/cards_lab.tscn --scale=N`: the three card types (paper / black / pink) at COMMON / UNCOMMON / RARE, each as the compact hand face and the full face; one card per effect family; every unique-art card (rares and class cards). |
| `cards_grey.png` | The 1.0 sheet in greyscale: rarity reads by pip (dot / diamond / star) and edge (plain / white die-cut / hatched foil). |
| `foil_strip.png` | A rare card at six pointer tilts (top), then the same six under reduce effects (bottom: one static sheen). |
| `detail_before_after.png` | The Modem's REMOVE A CARD detail (`--demo-shop --demo-carddetail`), before (face text repeated, empty art) and after (detail card + glass notes). `detail_lab.png`: two details from the lab. |
| `harness/*.jpg` | W10 harness, before (`W10/baseline/full`) vs after, for combat_start, combat_hover, loot, modem, hq_loadout_deck at 1.0 mouse and 1.6 pad; `harness/lint_report.md` is the runtime lint of the after pack. |
| `concepts/` | Pixel-art concepts, one per family, and `contact_sheet.png` (Q6: concepts only). |

## What changed (files)

- `scripts/ui/kit/zine_card.gd`: the §6.3 frame (cost gem, Anton title, 60% art window, effect band with glyph + key number, Plex rules); compact face (hand) vs full face (`fit_whole`, DETAIL); type colour from `CardArt`; rarity stocks and the foil layer; the no-truncation ladder and tall mode; `set_hovered`, `auto_hover`, `HOVER_SCALE`; `as_detail`; FOCUS brackets; tiles migrated to tokens and steps; every "…" path removed.
- `scripts/ui/kit/card_art.gd` (new, `CardArt`): card type, effect families (35), unique-art rule, the CPU two-ink riso painter with a cache and a per-frame budget, photocopy grain.
- `shaders/foil.gdshader` (new): rc_common include, `reduce_effects` → static sheen.
- `scripts/ui/kit/inspect_popup.gd`: `card_detail`, `card_notes`, `detail_card`.
- `scripts/ui/kit/deck_view.gd`: full faces, room for tape/lift, SCRIM, the new detail.
- `scripts/ui/kit/drag_ghost.gd`: cards at 60%, `center_global()`.
- `tools/design_lab/cards_lab.gd/.tscn`, `tools/art_concepts/*` (briefs, concepts, card dump), `docs/art_briefs/cards/**`.
- `tests/unit/test_art_w4_cards.gd` (fast, 24 tests), manifest entry; `tools/visual_qa/lint_baseline.json` (zine_card and deck_view down to 0); `assets/text/strings.csv` (export).

## ART_BIBLE §14 checklist (what W4 touched)

| Item | Result |
|---|---|
| §3 tokens, §4 steps, §5 spacing only | **Pass**: static lint 0 in zine_card/deck_view; sizes via `UiTheme.font_px_at`. |
| Materials not mixed | **Pass**: the detail card (PAPER) sits beside its GLASS notes, not inside. |
| Focal order / one primary | n/a (components). |
| Six states | **Pass** for cards: idle, hover (lift/scale/straighten), focus (FOCUS brackets), pressed (Button), disabled (INK shade), refused (gem pulses HARM). |
| 1.0 / 1.6 / 2.0: no clipping, truncation, mid-word break, < 12 px | **Pass** on the card look (tested over all 71 cards). Chip tiles step to 12 px absolute in the Modem at 1.6 (see gaps). |
| Contrast §3.7 | Pass by construction (INK on paper/pink, PAPER on black, band inverted); not measured in `_draw` (the runtime lint can't see it). |
| Greyscale | **Pass** for rarity (pip + edge). **Gap** for card type: paper and pink stock are close in greyscale (see gaps). |
| Pad | Pass: focus brackets, pad hint in the band, foil follows the right stick or focus place. |
| Motion / VFX tier | Pass: hover reuses `card_hover` (T1); foil static under reduce effects. |
| No leftovers | Pass: foil canvas item freed with the card. |
| Review stills | This folder. |

## Decisions (one line each)

1. §6.3: two faces. The hand-size card (the unchanged 112x148 contract) shows the **compact face** (gem, title, 60% art, band; no rules text: the band, tooltip, forecast and detail carry the words). Cards that must show every word (`fit_whole`: Modem, loot, deck view; DETAIL) show the **full face**.
2. §4.3/§6.3: the full face's ladder is body → caption at 60% art → art yields to 15% → band drops → the card grows taller (tall mode); never an ellipsis, never mid-word.
3. §6.3: card type is derived from the first effect: WHEEL (paper) = moves wheels, SYSTEM (black) = defence/resources/buffs, HACK (pink) = damage, harmful statuses, breach, resistance strip, RAM drain. `variant` no longer follows hand position.
4. §6.3: rarity stock = COMMON photocopy grain, UNCOMMON white die-cut glossy sticker, RARE/BOSS foil; greyscale by pip glyph and edge.
5. §7.3: riso inks = INK key (PAPER on black stock) + CELL_PINK spot on a window stock of the type's colour; key screen 45°, spot 15°, spot 1.4% off register.
6. §7.3/Q1: 35 families (34 used + `chip` fallback); unique art for RARE+ and any class card, seeded by the id hash (mirror, jitter, accents).
7. Schema: `CardData.art: Texture2D` already existed and was unused, so it is the illustration override; **no schema change** (the brief's `illustration` field would duplicate it).
8. §6.3 hover: 12 px from `card_hover`, scale 1.12 as `ZineCard.HOVER_SCALE`, timing `card_hover`; no new motion ids (a new id must join W6's `REQUIRED_IDS` and the motion lab). Same for the foil smoothing and the ghost's 0.6.
9. §6.3 cost gem: a NOTE_YELLOW dot sticker (was CELL_ACID, which §3.3 reserves for focus); RAM refusal pulses HARM (was a literal red).
10. §2: the detail card is PAPER taped beside a GLASS notes panel (TerminalWindow), never inside it.
11. §6: keyboard/pad focus draws FOCUS 4-corner brackets; the old acid glow is gone.

## Couldn't do / known gaps

- **Card type in greyscale:** paper vs pink stock are close in luminance. Proposal: a type glyph (wheel / shield / bolt) on the band's right, or a pink hatch on HACK stock. Left for a bible ruling (§16).
- **Modem at 1.6:** chip tiles step their effect text down to 12 px (caption at 1.0) to fit W8's fixed quads; the caption floor at 1.6 is 19 px. W8b should give chip and card rows room (then drop the step-down in `tile_parts`).
- **Status glyphs** in the band (☠ ⚡ ⌗ ✺) are still font glyphs (an emoji face renders ⚡ in colour); §7.4 wants them as `StatIcon`s.
- The stand-in painter is CPU (GDScript): first paint of a card costs ~20–40 ms; the cache and a 2-per-frame budget keep frames smooth, and the deck view fills in over a few frames.

## Bible rules I'd question

- §6.3 "illustration window 60% of the card height" plus rules text cannot both fit a hand-size card at any usable hand size; decision 1 treats 60% as the art-first face and lets the full face yield.
- §6.3 "effect band … key number in heading": heading needs a 33 px band, 22% of a 148 px card; it steps down to title/label on hand cards.
