# Combat effects that need an animation (round 19 inventory)

**Sources:**
- `docs/GDD.md` §2;
- `scripts/data/rc.gd` (the authoritative enums);
- `content/` (cards, slices, hub cores, ring segments, enemies, daemons, firmware);
- `docs/art_asset.md` Part K;
- `content/config/ui_motion.tres` (existing motion ids are in `code` style).

**The shared language** (rounds 18–19), for every entry:
- **Glyphs:** 0/1 glyphs (Share Tech Mono atlas) in the colour of the slice that caused the event.
- **Words and objects:** vinyl stickers.
- **Plans:** opaque grease pencil.
- **Light:** glow is additive, with light spill. No spray.
- **Tier:** each entry is held to its VfxTier.
- **Reduced:** the version that colour and number carry alone.

There is **no poison, burn or damage-over-time status** in the game. The closest tick is CORRUPTED's self-damage, so the "poison tick" request is answered by **CORRUPTED tick**.

**Priority:**
- **P1:** must ship with the combat facelift. It is seen in most fights.
- **P2:** common, but only on some builds or enemies.
- **P3:** rare, or a polish item.
- ✅ = animated in round 18 or 19 (file named).

## A. Damage and defence
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| Hit on slice | ATTACK / `DEAL_DAMAGE` | Tracer from the blade, then 0/1 shards from the hit point in the attacker colour; the number pops and flies to HP. ✅ r18 `damage_shards.gif` | P1 |
| Hit on HP arc | ATTACK → player | The drained arc segments flash and become the shards. ✅ r18 | P1 |
| Crit | CRIT / PERFECT / `seg_x2` | Hit-stop for 3 frames, code streaks, RGB split, XL tier. ✅ r18 | P1 |
| Blocked hit | block soaks | Shards bounce off the FIREWALL wall; a `BLOCK 12 → 2` equation chip. ✅ r18 | P1 |
| Block gain | DEFEND / `GAIN_BLOCK` | Cyan 0/1 stream from the slice to the rim. A crenellated wall is laid brick by brick on the side facing the enemy; a BLOCK chip shows by HP. ✅ r19 `fx_block_shield.gif` | P1 |
| Shield gain | SHIELD / `GAIN_SHIELD` (cap 15) | Hex plates tile on in a honeycomb arc, with a ripple. A SHIELD chip; persistent shimmer. ✅ r19 `fx_block_shield.gif` | P1 |
| Block expires | turn start | The wall's bricks drop out course by course and pixel away (200 ms). | P2 |
| Shield broken | shield → 0 | The hexes crack from the hit point outward, then shatter into 0/1. | P2 |
| Evade | EVADE | The slice gives a `>>` token sticker on the rim. On the hit, the wheel side-steps with RGB after-images, the tracer passes the ghost and fizzles, and the token peels off. ✅ r19 `fx_evade.gif` | P1 |
| Pierce | `seg_pierce` | The tracer is a needle line that punches *through* the wall or hex (a hole, then the bricks close up). The shards come out on the far side. | P2 |
| Bodyguard intercept | satellite takes the hit | The tracer bends to the docked drone; the drone's mini-HP chips. | P2 |
| Partial / Good / Perfect | precision tiers | The result word sticker sizes (existing `precision_*`); the shard tier follows the damage. | P1 |
| Firmware counter-triggers | `ON_SLICE_TRIGGER` (counterstrike, barbed_wire, leech, siphon…) | A small chip sticker pops from the firmware slot, then a mini-tracer (in the chip's colour) to its target. | P3 |

## B. Healing
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| Heal | HEAL slice / `HEAL` effect | Green `+` and `1` glyphs rise from below and are drawn into the HP arc. Segments relight one by one (white flash, then green), and a `+n` rises. ✅ r19 `fx_heal.gif` | P1 |
| Enemy hub per-turn heal | hub passive | The same effect, sourced from the hub; a slow pulse ring first. | P2 |

## C. Statuses (slice-level, both sides)
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| Apply CORRUPTED | `APPLY_STATUS` / dose / corrupt_packet | A violet code bolt hits the slice; the overlay tears on (bands left to right), and the diamond badge slaps on. | P1 |
| CORRUPTED tick | CORRUPTED resolves | The slice spasms (tear bands). Violet bits drip out of it into your HP arc (−3). A violet bolt cracks one RAM pip (−1 RAM). ✅ r19 `fx_corrupt_tick.gif` | P1 |
| Parasite attach | PARASITE / citation / leech_worm | A bug sticker crawls in along the rim and docks on the slice. A `×0.5` chip; output glyphs drain into the bug. | P2 |
| Encrypt | ENCRYPTED | A cyan cipher grid scrolls over the slice, then locks (padlock badge). On absorb, the grid shatters instead of the status landing. | P2 |
| Overclock | OVERCLOCKED | Heat shimmer and a ×1.5 chip. On trigger: a big burst, then the slice cools to CORRUPTED (the overlay tears on). | P2 |
| Cleanse | CLEANSE / sanitize | A white scan wipe across the slice; the overlay peels off like a sticker. | P2 |
| Predicted status | preview | A dashed badge outline (the round 17 rule), drawn during the card preview. | P1 |

## D. Wheel manipulation
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| Spin | SPIN N | Rotational blur, an n-tick trail, and the ghost meets the blade. ✅ r19 `card_play_v2.gif` | P1 |
| Card-play preview | forecast | A chevron chase plus ghost landings (locked round 17). ✅ r19 | P1 |
| Nudge | NUDGE ±1 | A one-tick step with a notch click and a small overshoot (existing `wheel_nudge`). The free-nudge pip empties. | P1 |
| Resistance absorbs | `MODIFY_RESISTANCE` | The wheel strains, then springs back. An `ABSORBED` grey chip, and a resistance pip burns down. | P1 |
| Respin | RESPIN / turn start | A fast blur spin. The checkpoint stamp (a vinyl `CHECKPOINT` tag) slaps on. | P1 |
| Flip | FLIP | The disc scales X 1 → 0 → −1 with a mirror sheen; blocked = a shake and a lock icon. | P2 |
| Freeze | FREEZE / `seg_anchor` | Frost crystals grow on the rim, then a `SKIP RESPIN` tag. | P2 |
| Snap to centre | SNAP_TO_CENTER | The needle glides to the slice centre, with a magnet-click flash. | P2 |
| Inner ring turn | ring scope | The inner ring rotates alone, with a contrasting blur direction. | P2 |
| Retrigger / echo | RETRIGGER / `seg_echo` | The slice fires twice: a ghost copy of its burst at 50 %, with an `AGAIN` chip. | P2 |
| Linked bus / ring lock | custom handlers | A cable glyph links the two wheels for a beat; a lock clamp on the ring. | P3 |

## E. Needles, hubs and bosses
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| Hub breach | HUB_BREACH | Code shards punch into the hub; the hub goes static-grey with a `BREACHED 1` tag. | P2 |
| Boss phase change | phases + overrides | Hit-stop, then the banner flips. The wheel swaps through a scanline wipe, and the new phase pip lights. | P1 |
| Needles multiply | MULTIPLY | New blades extrude from the bezel, with a spark. | P1 (bosses) |
| Needles migrate | MIGRATE | A ghost blade at the telegraphed spot (preview style); the blade slides there next turn. | P2 |
| Needles orbit | ORBIT | The blades travel N ticks with an orbit trail (`orbit_trail`). | P2 |
| Class core Perfect hook | ON_PERFECT | The hub core glyph flares, then the hook effect. | P2 |

## F. Satellites and drones
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| Deploy / dock | DEPLOY / enemy spawns | 0/1 bits stream from the hub to a dock point and assemble into a hex drone sticker, which slaps on with a clamp. ✅ r19 `fx_drone.gif` | P1 |
| Drone attack | satellite mini-wheel | The drone's eye charges, then a mini tracer and S-tier shards on the target. ✅ r19 `fx_drone.gif` | P1 |
| Drone destroyed | satellite HP 0 | The hex cracks, then pops into 0/1, and the dock clamp springs open. | P1 |
| Undock / move | `undock` card | The drone lifts (bigger shadow) and slides to the next slot. | P3 |
| Seed drone (botnet) | `botnet_seed` | A tiny 1-HP drone sprouts from the Perfect slice. | P3 |

## G. Cards and deck
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| Hover / peel / slap / dissolve | card play | ✅ r18–19 | P1 |
| Draw | `DRAW_CARDS` | Stickers peel off the deck liner and slap into the hand, fanning in. | P1 |
| Discard | turn end | Cards fold and slide to the discard pile, shrinking. | P1 |
| Exhaust | exhaust | The sticker burns: the edge curls, embers, then it pixels into 0/1 ash (existing `card_exhaust`). | P1 |
| Reshuffle | discard → draw | A stack riffle with a counter tick. | P2 |
| Can't afford / refusal | RAM refusal | The card shakes; a `NEED n RAM` marker tag. | P1 |
| Bug card | curse | Dead-pixel glitch on its face; it buzzes in the hand. | P3 |

## H. RAM and resources
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| RAM gain | turn start / `GAIN_RAM` | Pips fill left to right with a cyan pulse; a `+n RAM` float. | P1 |
| RAM spend / drain | spend / `DRAIN_RAM` / tariff | The pips hatch, then crack into 0/1 (violet when drained by an enemy). ✅ the CORRUPTED tick shows it | P1 |
| Heat or currency from a trigger | `MODIFY_HEAT` / cycles | A small chip flies to the top bar. | P3 |

## I. Turn flow and fight end
| Effect | Game term | Motion idea | Prio |
|---|---|---|---|
| SEND IT | resolve | The marker press, then the 3 passes pulse (`resolve_pass`). | P1 |
| Enemy defeated | enemy break / `hub_shatter` | Cracks run along the slice seams, and the wheel breaks into its 6 slices plus the hub and ring. They fall away, shedding 0/1 in their colours; then a `DELETED` vinyl sticker slaps on. ✅ r19 `fx_enemy_defeated.gif` | P1 |
| Player flatlined | operative lost | The wheel goes dark, slice by slice, then FLATLINED. | P1 |
| Enemy entering | combat start | The wheel prints in with a scan wipe; the banner drops. | P2 |
| Rewind | undo | VHS rewind scrub (`rewind_scrub`). | P1 |
| Lethal preview | forecast | A red grease underline plus a `LETHAL` tag. | P1 |

## Batch 1 (animated this round)
| # | File | Shows |
|---|---|---|
| 1 | `fx_block_shield.gif` | Player FIREWALL resolves to BLOCK 5 (a brick wall), then the boss gains SHIELD 4 (hex plates). |
| 2 | `fx_heal.gif` | You heal +6 (27 → 33): three segments relight. |
| 3 | `fx_corrupt_tick.gif` | Your CORRUPTED EXPLOIT resolves: −3 HP and −1 RAM. |
| 4 | `fx_drone.gif` | THE MANIFEST deploys a drone that docks, then attacks your pointer slice. |
| 5 | `fx_evade.gif` | PROXY gives EVADE; the boss's EXPLOIT 14 is dodged. |
| 6 | `fx_enemy_defeated.gif` | The final crit breaks THE MANIFEST; the slices fall away, then DELETED. |
