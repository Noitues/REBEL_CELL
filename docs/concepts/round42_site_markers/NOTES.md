# Round 42: City Grid Site markers

This covers the backlog gap in `GDD_ART_COVERAGE.md` §2.11: "Site markers: kind / tier / status, none for corporate Sites". It uses GDD 3.3 and 4.1 and `RC.SiteObjective` (NONE / EXPLOIT / HEAT_REDUCTION / RECLAIM / BOSS).

Nothing is committed and `scratch/` is cleared.

## Files

| File | What it shows |
|---|---|
| `site_markers.png` | **The key sheet.** See below. |
| `site_markers_on_map.png` | **The default view** on the round 37 city map, at the same brightness (`city_view.base_map`). See below. |
| `scripts/markers42.py` | The marker kit (`marker()`, `locked_link()`), the key sheet and the map. The other scripts are round 37 copies. |

### `site_markers.png` in detail
- **The main grid:** 4 kinds (a regular Site at T1 and at T3, an Exploit Site, a Heat objective) × 6 statuses:
  - corporate, not yet;
  - corporate, selectable;
  - cleared;
  - claimed;
  - disabled;
  - seized.
- **Second row:**
  - the 3 Exploit types;
  - the close zoom (×1.7, with labels);
  - CORE;
  - BOSS (T4);
  - the locked cross-link.

### `site_markers_on_map.png` in detail
- Claimed nodes, with the CORE heart and one DISABLED node.
- Cleared Sites (patrol).
- Selectable Sites, including one Heat objective and one SEIZED Site.
- The three Exploit Sites and two Heat objectives, pinned.
- A locked cross-link.
- The TARGET, with its chip placed clear of the pencil.
- A key strip.

## The system: one marker, five layers

Each layer answers one question, and each comes from an already-locked language.

| Layer | Answers | Look |
|---|---|---|
| **Pad** (raid socket on the street) | OWNERSHIP | Corporate: dark pad, orange pins. Claimed: the Cell's lime raid node. **Seized: red pins** (also an entry point, GDD 3.3). Disabled: amber. Cleared: grey. |
| **Icon disc**, in normal colours (option A) | KIND (`SiteObjective`) | Regular: the corp crest (Meridian crane-A, orange). **Exploit: a gold key plate plus a type sub-badge** (INTEL magnifier, BREACH key, VIRUS bug). **Heat objective: a dark-orange flame** (Heat B colour). Claimed or disabled Sites become the Cell's node icon. |
| **Ring** (locked option A) | AVAILABILITY | White = not yet. **Orange = selectable** (the run colour). Lime = yours or visited (cleared Sites too). Amber = disabled. |
| **Pips** (1–3 squares under the disc) | TIER T1–T3 | Exploit Sites carry gold pips. T4 is the boss: no pips, it gets the locked TARGET circle and the `CENTRAL SERVER // EXPLOITS n/3` chip. |
| **Corner badge** (top right) | STATUS beyond corporate | CLEARED: grey check (the disc greys; PATROL on hover, round 36). SEIZED: red ✕ (ring orange while a Reclaim run is possible). DISABLED: amber hazard ▲, with the node fill drained (raid health v2). |

**Special markers:**
- **CORE:** the lime heart node.
- **Boss:** the HQ landmark itself, with the red pencil TARGET circle.
- **Locked cross-link:** grey dashes and a **padlock disc** at the midpoint (it opens with an Intel Exploit or an objective, GDD 4.1).

**Readability:**
- **Grid zoom:** the marker is about 30 px. Kind reads from the disc, availability from the ring colour, tier from the pips, and status from the badge or pad.
- **Close zoom:** ×1.7, plus a terminal chip with the tier and name.
- **No UI on grease pencil:** chips and labels are placed clear of the TARGET circle and its word.

## Hidden-nodes rule (round 37), refined
- **Hidden by default:** regular Sites that are not selectable.
- **Pinned (always shown):**
  - Exploit Sites and Heat objective Sites, drawn at 90 % with white rings;
  - your nodes;
  - cleared and seized Sites;
  - the boss.
- **Why:** the campaign goals (3 Exploits to breach the boss, and the Heat sinks) are never hidden by the declutter.
- **Legend hover** and **Options > "Always show all nodes"** still reveal everything.

## Mapping to the rules
- **Exploit Sites:** T2 only (GDD 4.1, DECISIONS 2026-10, "Exploits stay on T2"). The type sub-badge maps to `RC.ExploitType` INTEL / BREACH / VIRUS. Meridian names them Shipping Manifests, Customs Override Keys and Rogue Routing Table.
- **RECLAIM** is not a separate kind on the map. A **Seized** Site *is* the Reclaim objective (GDD 3.3: a single combat with tiny rewards), so its marker is the seized state with an orange ring when reachable.
- **Statuses (GDD 3.3):**
  - Corporate: the default.
  - Cleared: used up; patrol is allowed (GDD 3.3, 2026-09-24).
  - Claimed: a node is installed.
  - Disabled: a claimed node at 0 integrity.
  - Seized: returned to the corporation.

## Open questions (DECISIONS.md)
1. **Pinning.** Exploit and Heat objective Sites are always visible even before they are reachable. Should their tier and type stay hidden until decrypted? The proposal shows the kind but no rewards.
2. **Claimed vs disabled icon.** A claimed Site shows the installed node type (the relay icon here; the real type in game). The Site's original kind (Exploit or Heat) is lost on claim. Is that fine?
3. **Seized and pins.** A seized Site keeps its tier pips, because a Reclaim run doesn't change the tier.

## Godot notes
- **One `SiteMarker` scene:**
  - pad = the raid socket shader with `pin_color`;
  - disc = one texture per kind, plus an exploit sub-badge atlas;
  - ring = `ring_color` (locked option A);
  - pips = a 3-slot `HBox`;
  - badge = an atlas of 3.
- **State** comes from a pure function of `SiteData.objective`, `tier` and the campaign Site state.
- **The locked link** is a dashed `Line2D` with a padlock `Sprite2D` at the polyline midpoint.

## Build (from `scripts/`)
Run `python markers42.py all`. All randomness is seeded.

## v2 (`site_markers_v2.png`, `site_markers_on_map_v2.png`; the v1 images are kept)

Changes from the designer's review:
1. **Customs: a tipping weigh scale.** This is the Exploit type badge for BREACH (Meridian's Customs Override Keys). The beam tips to show the override is in progress.
2. **Yours: the rebel FIST.** Every claimed node uses the fist (the REBEL_CELL crest from round 15) in lime. CORE keeps the heart: it is the home server, the one node whose loss ends the campaign, so it needs its own icon.
3. **T2 Exploit plate: a keyring with three keys dangling.** It no longer shares the single key with Customs. Three keys also hint at "3 Exploits open the Central Server".
4. **Disabled: a circled lightning bolt** in the corner badge. Yellow bolt, lime circle: no power.
5. **Seized: a red caution triangle** with "!". This is the old hazard shape, now in red (the threat colour).
6. **Disabled stays in the player colour.** Ring and pad are lime; the pad is dimmer. The drained node fill (raid health v2) and the bolt carry the state. Amber is gone from Site markers, so nothing reads as corp orange.

Other icon choices (unchanged from v1):
- **INTEL: a magnifier.** Shipping Manifests are read, not opened.
- **VIRUS: the virus slice glyph.** Players already know it from combat.
- **Heat objective: the flame.** Its dark orange is the locked Heat B colour, and its darker disc sets it apart from corp Sites.
- **Cleared: a grey check.** The Site is done, but its ring stays lime as visited.
- **Regular Site: the corp crest** (Meridian crane-A). Each corp uses its own crest.
- **Locked link: a padlock.**

## v3 (`site_markers_v3.png`, `site_markers_on_map_v3.png`; v1 and v2 are kept)

The designer's review showed the real problem was meaning, not shape, so the v2 icon swaps are reverted. v3 uses the v1 icons for customs, yours, T2 keys and seized, plus these changes:
1. **Disabled: a plain white lightning bolt** (no circle) laid across the whole marker.
2. **The whole marker greys out when disabled:** disc, ring, pad glow and pips.
3. **The key now means only "Exploit Site".** In v1, BREACH's type badge was also a key. BREACH now has a new icon: a **raised customs boom gate** (the override lifts the barrier, matching Meridian's "Customs Override Keys").
4. **De-powered links.** On the city map, every link to a seized or disabled node is drawn as a dim grey double trace with a **break in the middle** (two bent loose ends): no power flows. A disabled node gets its links back when repaired; a seized one when reclaimed.
5. **Plain-language legend.** The key sheet (now 1920×1640) has a "WHAT EACH ICON MEANS IN THE GAME" section: one short line per icon, ring, pip, TARGET and padlock, written from the rules (GDD 3.2–3.3, 4.1, 9 Exploit effects).
