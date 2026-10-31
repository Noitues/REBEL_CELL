# Cohesion redo 2: supporting screens on the r42 city (concept plates, PIL composites)

Plates (1920x1080): `01_terminal_event.png` (+ `01b_terminal_event_memo.png`, the memo variant), `02_dialogue_A.png` (CRT feed) and `02_dialogue_B.png` (sticker), `03_reward_fight_won.png`, `04_shop_mainframe.png`, `05_deck_screen.png`, `06_server_rack.png`, `07_heat_strip_by_page.png`. Also `contact_old_vs_new.jpg` (old left, new right) and `squint_<plate>.png` (plate left, 1/16 scale + blur back up, right).

## Method
All seven source plates were PIL chrome over a pre-rendered backdrop, so the original scripts were copied into `scripts/` (r31lib, sticker_lib19, assets, event, dialogue, reward, shop, shop2, shop3, recycle, server_rack, b44, deck_viewer, topbar44, kit44, ui31, sticker_lib31) and rerun with the backdrop swapped (`common42.py`, one `build_*.py` per screen, `make_contact.py`). Only fixes in copies: font ROOT and CONCEPTS paths, backdrop calls, Solace text, one pencil arrow. Nothing painted over old frames. Rebuild: `python assets.py` (tiles), Blender for the two busts (`bust_blender.py`, into scratch/), then `python build_event.py`, `build_dialogue.py`, `build_reward.py`, `build_shop.py`, `build_deck.py`, `build_rack.py`, `topbar44.py`, `make_contact.py`.

## Backdrop and grade
- Strong map-pages grade (`r42lib.grade`): value x0.58 outside the focus rects, x0.78 inside (focus = the UI footprint), saturation pull 0.18 buildings / 0.55 neon, then 1.5-5 px blur so chrome leads.
- r42 city (`plan_r42.png`): event, dialogue A/B, deck, heat-strip HQ/route/event rows.
- Picked cutaway (`combat_backdrop/v2/room_bio_bare.png`, Solace lab over a wet street): reward, shop, server rack, heat-strip combat row. Same grade.

## Solace text
| old | new | where |
|---|---|---|
| Meridian moved the depot's Rack... Logistics Director | Solace moved the Seed Vault's Rack... A Claims Adjuster | dialogue speaker line (Claims Adjuster is a GDD A.3 Solace elite) |
| NETRUN: MERIDIAN DEPOT 15 | NETRUN: SEED VAULT EXCHANGE | reward strip |
| CARGO HAULER (beaten ring) | WARDEN | reward |
| SERVER RACK 7/7 // MERIDIAN DEPOT 15 | ... // SEED VAULT EXCHANGE | rack strip |
| LOGISTICS DIRECTOR DOWN | CLAIMS ADJUSTER DOWN | rack BANKED tag |
| old Meridian city, depot, MARKET NEON facade, Meridian-gold crane | r42 city / Solace cutaway | all backdrops |
Event (Solace Biosystems header, runner Solace picked up) was already Solace. MAINFRAME shop flavour is generic.

## Changes beyond the swap
- Reward: the "OURS NOW" pencil pointed at the old depot sign; it now points at the lab. The old depot lime/pink takeover recolour is dropped.
- Shop: the MAINFRAME tube sign is redrawn on the cutaway street; the old pink-to-blue facade recolour is switched off.
- Heat strip: rows rebuilt from the new plates (HQ and route rows from `map_pages_r42`).

## Squint (1/16 scale)
All PASS: UI panels, yellow/pink stickers and pencil lead; the dim city or cutaway sits as a violet/green texture, lime park and Solace green still recognisable. Weakest: dialogue A/B, where the lit city between the portraits is the brightest background area; fine, but a smaller focus rect would sink it further.

## Skipped / still not Solace
- `solace_vertical/nodes/godot/frames/now_event.png`: a Godot-rendered build frame (UI only as pixels), skipped; the concept event plate replaces it.
- Heat strip combat row: the E10 combat plate (D:/rc_tmp/combat_critic) is still the old city with Meridian "M" units and is not mine; the row shows the Heat chip on the cutaway instead and is labelled as such.
- Card art and the `placeholder: own pass` panels (MICROCHIPS, DAEMONS), the `STREET MERC` and `CELL-9` names are not corp text and unchanged. Cutaway signs (VITA, BAR, GENE) come from that plate.
- Rack ladder and shop item names are generic gameplay terms.
- Process slip: I typed `python -` once inside a shell command (hung on stdin, stopped by task id; nothing ran from it).
