# Metrics, round 10 (plan 01, whole frame minus the bay corner)

By D:/rc_scratch/g1/r10/../r9/metrics.py (a file, not in the repo). Plate = raw golden plate 01 (it carries beams, HUD and cards the live city lacks). r9 = head 89c28e35, r10 = head 06fa2a1d.

```
plate luma p1/5/25/50/75/95: 0.069 0.113 0.232 0.325 0.481 0.844
r9   luma p1/5/25/50/75/95: 0.089 0.157 0.261 0.336 0.441 0.810
r10  luma p1/5/25/50/75/95: 0.058 0.116 0.245 0.318 0.447 0.787
seed 3 (r10) luma p1/5/25/50/75/95: 0.062 0.124 0.240 0.302 0.408 0.746
seed 19 (r10)                       0.061 0.120 0.242 0.309 0.438 0.756

median rgb: plate (79,80,125)  r9 (74,83,137)  r10 (70,79,126)
region (third) median rgb, r10: top (55,79,128)  mid (80,88,133)  bottom (90,69,112)
  plate:                         top (59,83,139)  mid (92,85,130)  bottom (89,65,87)
warm share (amber pixels) by thirds, plate / r9 / r10:
  top    0.030 / 0.015 / 0.022
  mid    0.138 / 0.067 / 0.066
  bottom 0.280 / 0.222 / 0.243
  left   0.182 / 0.096 / 0.157
  centre 0.140 / 0.104 / 0.075
  right  0.137 / 0.093 / 0.098
  all    0.153 / 0.097 / 0.111
```
Reading: p1 / p5 / p25 are back at the plate (p5 0.116 vs 0.113; p25 0.245 vs 0.232; p1 a little under at 0.058 vs 0.069). p75 and p95 are a little under the plate (0.447 / 0.787 vs 0.481 / 0.844), since the lamp pools are now small ribbons. Warm share all is 11.1 % (plate 15.3 %); the mid band stays low (the plate's streets show through see-through buildings, ours are opaque and open ground is dark on purpose).

## Round 11 (plan)
luma p1/5/25/50/75/95: 0.058 0.112 0.236 0.295 0.390 0.813; median rgb (65,73,122); region medians top (51,74,124) mid (73,81,130) bottom (76,63,111); warm share top 0.006, mid 0.040, bottom 0.155, left 0.104, centre 0.046, right 0.050, all 0.067. Seed 3 p1/5/25/50/75/95: 0.061 0.121 0.236 0.286 0.355 0.762.

## Round 12 (plan)
luma p1/5/25/50/75/95: 0.061 0.121 0.238 0.299 0.405 0.843; median rgb (67,74,124).

## Round 13 (plan)
luma p1/5/25/50/75/95: 0.062 0.127 0.244 0.309 0.427 0.809; median rgb (69,77,124).

## Round 14 (plan, bay corner masked by rectangle)
luma p1/5/25/50/75/95: 0.046 0.069 0.173 0.271 0.374 0.770; median rgb (59,67,115).

## Round 15 (plan, bay masked)
luma p1/5/25/50/75/95: 0.043 0.065 0.163 0.267 0.366 0.769; median rgb (57,66,115).

## Round 16 (plan, bay masked)
luma p1/5/25/50/75/95: 0.042 0.064 0.164 0.265 0.369 0.772; median rgb (57,65,114).

## Round 17 (plan, bay masked)
luma p1/5/25/50/75/95: 0.041 0.064 0.187 0.317 0.434 0.823 (targets p50 ~0.31, p75 ~0.43: met; p1/p5 kept); median rgb (69,78,129).

## Round 18 (plan, bay masked)
luma p1/5/25/50/75/95: 0.041 0.065 0.188 0.318 0.435 0.825 (p50 / p75 on target).

## Round 19 (plan, bay masked by the rectangle x < 400, y < 300; script r19/tools/metrics.py)
luma p1/5/25/50/75/95: 0.034 0.071 0.199 0.312 0.445 0.812 (p50 on target, p75 +3 %); median rgb (68,77,123).
r18 re-rendered on the same mask: 0.041 0.065 0.187 0.318 0.435 0.825.

### Squint structure (r19/tools/structure.py): 320 px wide box downsample of the 1920 x 1080 frame
edge = mean Sobel gradient magnitude, local = mean |L - gaussian(L, 3 px)|, coarse = std of the 80 px wide downsample (district-scale value structure). "core" = crop x 200-1500, y 130-780.
```
            full frame (edge local coarse)   core crop (edge local coarse)
plate       0.1359 0.0849 0.1648            0.1347 0.0855 0.1750
r18         0.1410 0.0843 0.1227            0.1613 0.1000 0.1367
r19         0.1369 0.0837 0.1374            0.1519 0.0957 0.1553
```
Plate = left half of final/01 (it carries the yellow / blue / pink route lines, the white HQ ring and the cards, which is a large part of its coarse structure). Edge energy and local contrast were already at the plate's level in r18 (the facade texture), so only the coarse value structure tracks the plateau: +12 % (full) / +14 % (core) over r18, about 83 % / 89 % of the plate.

## Round 20 (plan, bay masked x < 400, y < 300)
luma p1/5/25/50/75/95: 0.043 0.081 0.202 0.309 0.428 0.811 (p50 / p75 on target; r19 0.034 0.071 0.199 0.312 0.445 0.812). Squint structure (full frame edge / local / coarse): r20 0.1340 0.0813 0.1278; r19 0.1369 0.0837 0.1374; r18 0.1410 0.0843 0.1227; plate 0.1359 0.0849 0.1648. Core crop coarse: plate 0.175, r19 0.155, r20 0.143, r18 0.137.

## Round 21 (plan, bay masked x < 400, y < 300)
luma p1/5/25/50/75/95: 0.035 0.064 0.190 0.305 0.443 0.808. Squint structure (edge / local / coarse), full frame: r21 0.1401 0.0864 0.1435; r20 0.1340 0.0813 0.1278; r19 0.1369 0.0837 0.1374; plate 0.1359 0.0849 0.1648. Core crop coarse: r21 0.164 (plate 0.175, r20 0.143, r19 0.155). In-frame kinds: dark gap 7.2 % of 1919 buildings, 9 white towers.

## Round 22 (plan, bay masked)
luma p1/5/25/50/75/95: 0.036 0.063 0.184 0.306 0.431 0.810 (p50 / p75 on target). Structure (edge / local / coarse) full frame r22 0.1406 0.0854 0.1392 (r21 0.1401 0.0864 0.1435; plate 0.1359 0.0849 0.1648); core crop coarse r22 0.158 (r21 0.164, plate 0.175). Edge energy (the metric held at 0.140) stays 0.1406.

## Round 23 (plan, bay masked)
luma p1/5/25/50/75/95: 0.026 0.051 0.178 0.304 0.437 0.808. Structure full frame (edge / local / coarse): r23 0.1417 0.0862 0.1467; r22 0.1406 0.0854 0.1392; plate 0.1359 0.0849 0.1648. Core crop coarse r23 0.168 (plate 0.175, r22 0.158).

## Round 24 (plan, bay masked)
luma p1/5/25/50/75/95: 0.036 0.059 0.162 0.312 0.431 0.811. Structure full frame (edge / local / coarse): r24 0.1479 0.0903 0.1349; r23 0.1417 0.0862 0.1467; plate 0.1359 0.0849 0.1648. Core crop coarse r24 0.154 (r23 0.168).

## Round 25 (plan, bay masked)
luma p1/5/25/50/75/95: 0.034 0.056 0.148 0.308 0.429 0.811. Structure full frame (edge / local / coarse): r25 0.1520 0.0929 0.1351; r24 0.1479 0.0903 0.1349; plate 0.1359 0.0849 0.1648. Core crop coarse r25 0.153.

## Round 26 (plan, bay masked)
luma p1/5/25/50/75/95: 0.039 0.061 0.156 0.312 0.434 0.803. Structure full frame (edge / local / coarse): r26 0.1397 0.0861 0.1370; r25 0.1520 0.0929 0.1351; plate 0.1359 0.0849 0.1648. Core crop coarse 0.155.

## Round 27 (plan, bay masked; the structure metric is reported only, no longer a target)
luma p1/5/25/50/75/95: 0.048 0.080 0.195 0.339 0.447 0.756. Structure full frame (edge / local / coarse): r27 0.1313 0.0791 0.1117; r26 0.1397 0.0861 0.1370; plate 0.1359 0.0849 0.1648. Corp kinds in the plan frame (1919 buildings): Solace 929, Halcyon 379, Meridian 321, Orbital 281 (no Aurelian HQ in this city).

## Round 28 (plan, bay masked; round-6 look)
luma p1/5/25/50/75/95: 0.061 0.097 0.167 0.286 0.397 0.726; median rgb (72,72,84). Structure (reported): edge 0.1202, coarse 0.0993.

## Round 29 (plan, bay masked; round-6 colour)
luma p1/5/25/50/75/95: 0.009 0.043 0.132 0.235 0.437 0.869; median rgb (50,57,100). Structure (reported): edge 0.1640, coarse 0.1339.

## Round 30 (plan, bay masked)
luma p1/5/25/50/75/95: 0.004 0.039 0.122 0.234 0.440 0.882; median rgb (55,57,86). Structure (reported): edge 0.1667, coarse 0.1405.
