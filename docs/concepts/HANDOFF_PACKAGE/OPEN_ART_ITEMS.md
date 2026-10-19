# Open art items (art-pass owns these; build is not chasing them)

Started 2026-10-19 from the W1 reviews. Close an item with its date and commit.

1. **Street DECISION R-REP-1 on seed 2.**
   - Main 6bc74790, NA-24c blades merged: seed 1 is 0.5544 (pass); seed 2 is 0.6051 (fail by 0.005, inside the ±0.015 run noise).
   - Dominant lags on the tiles at or above p90, at 1280 px: seed 1 is vertical (0,±5), (0,-8), (0,-10); seed 2 is vertical (0,-5), (-1,-7), (0,12) plus horizontal (8,0), (5,0), (4,0). That reads as window rows on the near facades.
   - Suspects: the window row pitch on near faces, the facet-row shading, and the near-facet ink wobble.
   - Fix idea: per-floor variation in the near-face window height and sill offset (lb > 0), so the row pitch isn't constant. Check that the r2 `r2_facade.py` floor bands do the same.
2. **Street OVERVIEW R-DET-1 is 0.0195-0.0210, against 0.028 (warn).**
   - This is no longer sign-limited after NA-24c. The NA-23c lane dimming also cost Sobel.
   - Look at non-sign detail: rooftop props, facade trims and ground clutter in the mid band.
