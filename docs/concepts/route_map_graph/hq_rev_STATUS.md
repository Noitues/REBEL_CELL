# HQ revision v2 (hq_rev): status

- 20:05  Kit work done (all four kit corps): `hq_kit/downtown.py` (dense city blocks right up to the compound walls,
  360 deg) + `hq_kit/section.py` (the storyboard's SECTION CUT generalised to the orbiting camera: city buildings
  between the camera and the framed rooms are cut below the sight line, dark poche on the cut tops); v2 outputs are
  written as `*_v2.png` (v1 kept); heavy passes in `D:\rc_scratch\hq_rev\<corp>\`.
  Meridian v2 (the ring route round all four walls, the shuttle containers, the slewing keep crane) and Rebel Cell v2
  (the Tokyo alley canyon round option A's three lanes, multilingual blade signs, holograms, the red fist hologram, the
  MAINFRAME v4 red sign on lane 1) are built; Eevee previews in `D:\rc_scratch\hq_rev\<corp>\prev\`.
  GPU: queued (`GPU_WAITING_hq_rev`) behind the storyboard and city_all_corps. The first locked batch renders the
  1280 x 720 TEST overviews for the coordinator: Rebel Cell (overview + decision + the red sequence) and Meridian
  (overview + decision) -> `D:\rc_scratch\hq_rev\tests\` (composed with UI + value numbers). Full renders wait for
  approval of those.
- 20:47  TEST batch 1 rendered (Cycles HIP, 1280 x 720, 32 spp) and composed in `D:\rc_scratch\hq_rev\tests\`
  (`<corp>_<shot>_test.png` with UI, `_plate.png` without, `values_*.json`): Rebel Cell overview + decision + the red
  sequence RS_1..4, Meridian overview + decision, Orbital overview + decision, Solace overview + decision, Halcyon
  overview + decision E (`halcyon_*`). Values (median / under 0.10 / landmark ratio): Rebel 0.311 / 21 % / 3.8,
  Meridian 0.069 / 61 % / 3.3, Orbital 0.125 / 39 % / 3.5, Solace 0.089 / 54 % / 3.8, Halcyon 0.119 / 43 % / 3.3,
  red sequence 0.035-0.052 / 62-72 %.
- 20:55  Review received (art director via coordinator): Orbital PASS; red sequence concept PASS. Working on: Rebel Cell
  (no lit fog plane: the section is now a clean cut through the alley kerb with the tunnel in the earth face under the
  street, a deeper wet alley with stalls; the MAINFRAME v4 red sign as the large hero landmark; Tokyo-alley room
  interiors and shutters; red sequence: arterials dark / red inside the ring, the crest fist outline rasterised to the
  grid, haze + low strata), Meridian (orange haze bank round the fort, neutral further out, brighter city), Solace
  (green porthole / rim light, the two towers separated with visible cross-links, no flat sky band, a dark dressed
  plinth with a lit entry). A second test batch follows.
- 21:50  hq_rev v2 agent took over (the previous agent was stopped mid-round). Adopted its orphan runner's f1 batch
  (Orbital stills + sheet, Halcyon H_overview / H_decision_E / H_hover_E full renders, done 21:22, lock released) and
  composed them: `hq_orbital/H_*_v2.png`, `hq_halcyon/H_*_v2.png`. The dossier letterhead is per HQ (HALCYON / CIVIC
  SECURITY), and so is the hover node file's seal, which had also defaulted to Meridian on every HQ. Checked on all
  five HQs.
  OCCLUSION rule (designer note) in the kit for all five HQs: `downtown.occlusion_params / occlusion_state` +
  `section.py` v3. A building is cut when it blocks the cone from the camera to the active room plus the visible route
  nodes (10 % margin; only the targets behind it count). FLATTEN cuts it to a 6.4 BU lit stub with poche; GHOST fades a
  stub that still blocks to 18 % with faint edges. Soft cone borders handle the easing. The rule is documented in every
  NOTES. Meridian: the freight line reads from the overview (rail-side sheds along the corridor). Solace: rim +
  portholes, towers apart, bridges only on the cross-links, graded sky, dark dressed plinth with a lit entry. Rebel
  Cell: THE UNDERCROFT (a sunken service street in front of the tunnel lane) replaces the fog plane; the fist uses
  majority line blocks; slight bloom. TEST batch 2 queued (`batches/t2.json`, GPU_WAITING_hq_rev behind the storyboard).
- 00:08  TEST batch 2 (t2: 00:00-00:03 after a 2 h 15 min wait behind the storyboard) and t2b (Meridian + Solace values
  retest, 00:05-00:07) are composed in `D:\rc_scratch\hq_rev\tests\` (`*_t2.png` / `*_t2b.png`, plus `_plate`, `_thumb`
  and `values_*_t2*.json`). Lock released. Values (median / under 0.10 / landmark ratio):
  - Rebel overview 0.155 / 42 % / 9.4; Rebel decision 0.131 / 44 % / 6.2.
  - Red sequence RS_1..4: 0.042-0.061 / 64-74 %.
  - Meridian t2: 0.347, blown by the orange bank. t2b: overview 0.163 / 27 % / 1.73, decision 0.149 / 31 % / 1.52.
  - Solace t2b: overview 0.120 / 42 % / 3.9, decision 0.159 / 28 % / 3.6.
  - Occlusion: Meridian overview flattened 17, ghosted 7; Meridian decision flattened 12; Solace overview flattened 4.
  Meridian pipeline spec (art director, via the coordinator) is applied after its t2 render (t2b shows it):
  - the deck is at 73.7 BU, about 2 storeys over the frontage, with the rail-side frontage capped at 57.7;
  - the line leaves by the north rail-yard gate;
  - the moat runs on the W, S and E sides only, and the north side is a paved rail yard with sidings and no bridge.
  Waiting for review before the full renders of Rebel Cell, Meridian and Solace.
- 00:55  FULL v2 renders done and composed (art director approved t2 / t2b with tweaks). Batches f2 (Rebel Cell), f3
  (Meridian + Solace), f2b + f2c (Rebel Cell floor re-renders); the lock was released between every batch, and nobody
  else was waiting.
  - Rebel Cell (`hq_rebel_cell/*_v2.png`):
    - Files: H_overview / H_decision / H_hover, H_red_1..4, H_midrun / H_switch / H_showdown.
    - Values: overview 0.061 / 57 %, ratio 10.4; decision 0.078 / 56 %; RS 0.036-0.055.
    - The t2 smear was the post's zoom LOD: it blurs every ground-index pixel when zoomed out. The undercroft floor is
      now its own sharp wet asphalt; with that blur gone, the overview median fell from 0.155 in t2.
  - Meridian (`hq_meridian/H_*_v2.png` + sheet):
    - Values: overview 0.165 / 25 %, ratio 1.72; decision 0.149 / 28 %, ratio 1.45.
    - The freight line rises on a 3 % grade from the north rail yard; the moat is on W/S/E only.
  - Solace (`hq_solace/H_*_v2.png` + sheet):
    - Values: overview 0.096 / 52 %, ratio 3.2; decision 0.128 / 36 %, ratio 3.2.
    - The bridges no longer carry the rim, and the sky strip is trimmed.
  - The hover stills are the power-cut state (medians about 0.01).
  - Halcyon / Orbital: no re-render; their NOTES say the finals predate the occlusion rule.
