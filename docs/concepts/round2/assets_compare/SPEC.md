# Asset samples: side-by-side spec

Two styles render the **same sample assets on the same sheet layouts**, so the designer can compare them panel by panel.

| Style | Folder | Who |
|---|---|---|
| **S1: Cv2 + E cel shading** (triangle facets at Cv2 density, 3 hard toon light bands, wobbly ink outlines, painted rust/grime; see `docs/concepts/round2/r2_blend_EC_on_Cv2_day/city_day.png` and `r2_city_wide_helix/city_day_hidden_lines.png`) | `assets_compare/s1_cv2_cel/` | C agent (Pillow) |
| **S2: E format** (chunky wonky hand-painted gritty toon 3D, thick ink, rust and grime, crystal-faceted digital layer as in the E+C hybrid; see `docs/concepts/round2/r2e_handpainted_toon_gritty/` and `r2e_city_wide_helix/`) | `assets_compare/s2_e_toon/` | E agent (Blender) |

## Source of truth for the assets
`C:\Users\noitu\Documents\Godot\rebel_cell\docs\art_asset.md` is the designer's asset list. **Read the parts cited below.** Read it in place: it's in the main checkout. Don't copy or commit it.

## Sheets: identical layout in both styles
Each sheet is 1920×1080 PNG on a neutral dark-grey backdrop (#2A2A2E), with a small label under each item. **Use the same grid positions in both styles**, so the two can be stacked side by side.

1. `01_operatives.png`: Polaroid busts (art_asset §B1). The grid is 2 columns × 4 states. **Columns:** Breaker (heavy jacket, antenna-crowbar) and Ghost (hood, face mesh). **States (rows):** neutral, hurt, triumphant, flatlined. Each class gets its own silhouette and prop.
2. `02_enemies.png`: three enemy busts or holograms, left to right (§B2, Appendix Enemies):
   - **The Manifest:** Meridian boss, the routing core.
   - **Claims Adjuster:** a Solace elite.
   - **A collections drone:** a Meridian regular machine (B5).

   Each one wears its corporation's colour and pattern. Under each, show its **wheel bezel** as a ring segment. Meridian bezels are orange with container stripes; Solace bezels are mint green with helix dots.
3. `03_landmarks.png`: three corporation HQ landmarks as isolated buildings on small plinths (§A2):
   - **Freight Ziggurat** (Meridian): terraced freight building with container yards and a crane.
   - **Civic Pyramid** (Halcyon): tiered pyramid with colonnades and a halo ring.
   - **Orbital Tether** (Orbital): a needle tower with a tether rising into the sky.
4. `04_threats.png`: raid threat tokens at map-token size, each also shown 3× larger (§B4, Appendix Threats):
   - **Bailiff:** armoured, slow and heavy.
   - **Courier:** fast and fragile.
   - **Customs Agent:** seals the link behind it.

   Each must be readable at small size.
5. `05_cards.png`: three full cards (§E5, Appendix Cards):
   - **Backspin:** Common, spins a wheel 9 ticks counter-clockwise.
   - **Arc Flash:** Uncommon, 3 damage to every enemy.
   - **Bulwark:** Uncommon, gain 12 block.

   Each card needs a RAM cost gem, title, illustration, pictogram row and short text. Rarity must be visible. Add a 4th card face-down as the **card back**.
6. `06_icons.png`: icon sets (§E2, §E3, §I) on a 64 px grid, each also shown at 24 px:
   - **9 slice types:** ATTACK, CRITICAL, DEFEND, SHIELD, EVADE, HEAL, AFFLICT, DEPLOY, MISS.
   - **4 statuses:** CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE.

   The statuses must show whether each one helps or hurts.
7. `07_items.png`:
   - **Adrenal Loop:** a daemon (installed program token).
   - **Barbed Wire:** a firmware chip.
   - **A spinner slice tile:** an ATK 6 slice for sale.
   - **Currency icons:** Cycles, Schematics, RAM, Heat.
8. `08_stamps.png`: the headline words as graphic stamps (§J): **VICTORY · DEFEATED · SOLD · JACK IN · LETHAL · PHASE 2**. Paper and marker treatments are fine.

Also produce `contact_sheet.jpg` with all 8 sheets, and put your scripts in `scripts/`.

Keep the folder under 30 MB. Never run `python -`. Blender rules: headless, logs, timeout, no MCP. Don't touch other folders.
