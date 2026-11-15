# Takeover in Deface v3: the B-086 state set (reference for build), 2026-11-15

Designer approved Deface v3 as the Takeover look (A-119). This set re-renders the B-086 states in it, with the A-119 rulings:
1. **Status = sticker, value = grease pencil.** A status sticker carries no number. Its count or turns are written beside it in pencil.
2. **Pencil may carry forecast numbers.**

Player words follow NAME_MAP section E:
- program, LOADED, RAM;
- QUEUE / SPENT / DELETED;
- COMMIT, ROLLBACK [Z];
- SCHEDULE;
- "pointer" and "health" are unchanged.

The pink SEND IT sticker sits over the washed-out system word `COMMIT`, with "END TURN [SPACE]" under it. Multi-target follows
build B-091: one pick, and the card's selector adds the rest.

| File | State (tk_states) | Shows |
|---|---|---|
| `v3_board.png` | BOARD | Rest. Five programs as die-cut stickers on the glass; TIME BOMB grey with red pencil "needs 4 RAM". Forecast in pencil on the wedges (→9, →4, LOST −1 HP). BLOCK / VIRUS stickers with "x2" / "x1" in pencil. SHROUD / TRACED stickers by RAM. HUD COMMIT totals. |
| `v3_play.png` | PLAY | BREACH peeled and held top right (peel curl, liner outline left). Yellow pencil line to FIREWALL 2 with "−3". CORE and FIREWALL looped. TAKEN in pencil. RAM hatches 3 → 2. HUD play line and rule. |
| `v3_worm.png` | BOARD + WORM held | WORM held, hovering TURRET. The selector `target_and_corp_nb` adds CACHE and NODE. Loops 1 (TURRET, heavier), 2 (CACHE), 3 (NODE); one pencil line through them in order; "+V" on each. HUD: "WORM on TURRET: 1 virus on TURRET, CACHE, NODE" and the rule. |
| `v3_forecast.png` | FORECAST | Your ICE hovered. Numbered pencil arrows 11.1 −2 and 13.1 −3 (red), 11.2 BLOCK 2 (yellow), 16.1 on LOST. The same steps listed in the HUD. The health mark is outlined cyan. |
| `v3_resolve.png` | RESOLVE | The COMMIT replay at step 13: the hub reads COMMIT 13 COUNTER, and the pointers are lit. Played steps stay as numbered pencil (8.1 +2 round the inner ring, 11.1, 11.2, 13.1). A RETAKEN temporary-word sticker sits on ICE. Corp-teal 0/1 shards go round the rim, then up to the health tape. The HUD shows the replay step and the steps done. |
| `v3_wallseal.png` | WALLSEAL | Corp WALL pair on TURRET and corp SEAL on CORE, unchanged enamel. Your WALL is a sticker on the NODE / FIREWALL boundary, and your SEAL a sticker on FIREWALL, each with "1 turn" in pencil. |
| `v3_win.png` | WIN | 12/12. A yellow WHEEL TAKEN result-stamp sticker on the hub. A yellow pencil ring round the wheel and "OURS NOW". The result in the HUD. A CONTINUE sticker (no COMMIT or ROLLBACK). |
| `v3_sheet.jpg` | | All seven, with captions. |

## Calls
1. **Pencil values sit beside their stickers:** "x2" by BLOCK, "x1" by VIRUS and SHROUD, "1 turn" by your WALL and SEAL.
   TRACED has no count, so it gets no pencil.
2. **Corp walls, seals and statuses stay enamel or teal** (corp material). Only the runner's become stickers.
3. **The resolve FX follow bible 3.20.** The corp's hit is 0/1 shards in the attacker's colour (corp teal) curving round the
   rim, never across the face. The retake word is a temporary-label sticker that will dissolve to bits. The arrows for the
   steps already played stay as pencil (the B-088 replay), and the pencil is never covered.
4. **WORM order** is the target first, then its corp neighbours, tie-broken by content id then node id: TURRET, CACHE, NODE.
   NODE's own "→4" mark moved to the wedge's other inner corner to make room.
5. **Held stickers sit top right**, clear of the health tape, the status stickers and every pencil mark. This fixes the v3
   issue where the held sticker covered the G2 chip.
6. **The open right side is fixed.** The HUD panel is drawn by this script, and SEND IT sits right under it. When the panel is
   tall (the hover step list), the sticker shrinks to fit.
7. **Win:** CONTINUE is a pink verb sticker (bible 1.2 lists CONTINUE as a verb sticker; the reward screen pairs it with the
   pencil OURS NOW). The hand, RAM cost and ROLLBACK are not shown.
8. **The resolve HUD** says "health 27 → 26 at 16". The loss lands at step 16.1, which has not played yet at step 13.

## Bible lines followed
| Plate | Bible |
|---|---|
| all | 1.2 media table (stickers fixed, pencil = plan true to the rules, yellow plan / red loss, no UI covers pencil); 1.3 verb over a system word; 2.9 type (Anton, Permanent Marker wax, Share Tech Mono); 3.1 RAM pips, UNDO / ROLLBACK as a terminal chip; 3.18 die-cut, gloss band, yellow cost dot (grey when it can't be afforded) |
| board, wallseal | 1.2: temporary effect words are stickers; ruling 1: values in pencil |
| play, worm | 2.10: a focused sticker shows only the peel curl; 3.18 steps 2-4: hover hatches RAM, peel leaves a liner outline, a yellow pencil line to the target and a pencil loop round each valid target; 3.19: pencil 7 px with an ink edge |
| forecast | B-088 numbered arrows in pencil (designer ruling 2), with the HUD step list |
| resolve | 3.20: shards in the source colour go round the rim; temporary labels dissolve to bits |
| win | 1.2 result stamp as a sticker; 2.x reward screen: yellow pencil "OURS NOW" and a CONTINUE sticker |

## Limits
- Positions of stickers and pencil are hand-set; build needs a label auto-placer (already owed).
- WORM's loop on NODE crosses the VIRUS sticker there; both still read.
- The washed-out `COMMIT` word is mostly behind SEND IT. Only its edges show, as with EXECUTE in the bible reference.
- Stills only: no peel, slap, dissolve or shard motion. The resolve shards are one frame.
- Glyphs are borrowed from the locked cards, and the status-sticker colours are a first pass.
- The locked measured checks were not run. Numbers come from tk_states (illustrative).
- Illegal-target reasons (the codes build uses: not corp, sealed, not next to yours, no virus, hp above the cap, the card's own
  rule) are not drawn in this set. `../inspiration/rendered/df3_invalid.png` shows the pattern with the "not next to yours"
  wording.

## Source
`D:/rc_scratch/takeover/inspiration/insp_v3set.py`. Run `python insp_v3set.py`, or name the plates
(`board play worm forecast resolve wallseal win sheet`). It imports `insp_deface3.py`, `insp_deface3b.py`,
`insp_render.py` and `tk_render.py` / `tk_states.py` without changing them.
