# Area: city (3D city, Grid, raid, HQ runs, netrun on the city, bake)

Owns: `scripts/city3d/`, `scripts/ui/city/`, `scripts/ui/raid/`, `scripts/ui/hq/`, the city tests
(`test_city3d_*`, `test_art5_*`, `test_art6_*`, `test_hq_*`, `test_anim_*_city`).
Reference: ART_BIBLE v2 §city, the Site/landmark concept exports, GDD 4 (campaign, Heat, raids),
TECH_SPEC 7 (raid resolver) and 10 (performance budget).
Rules specific here: raid words TAKEN / DOWN / HOLDS / BREACHED; DOWN uses the Site markers' white
bolt; Grid stays night; corp layouts aim into their own territory; the real bake is checked only on a
real renderer (`run_windowed.py -- -s tools/design_lab/bake_smoke.gd`), never headless; reduce
motion 40 % traffic must still show (ambience is reported under reduce motion).
Perf: 1080p frame time on this PC for both `city_quality` tiers, logged in the report.
