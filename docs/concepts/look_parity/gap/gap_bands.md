# Brightness gap per band (measure only, no tuning)

Bands from id.png: sky = class 0, facades = 1/2/3/5/6, floor = 4. R-DET-2 (blobs/MP, rule >= 450) and R-HUE-1 (hue entropy bits, rule >= 3.8) per band use the band as the valid mask.

## overview

| band | metric | plate | seed 1 | seed 2 |
|---|---|---|---|---|
| frame | share | 1.000 | 1.000 | 1.000 |
| frame | median | 0.130 | 0.107 | 0.089 |
| frame | under_010 | 0.299 | 0.446 | 0.559 |
| frame | over_085 | 0.005 | 0.000 | 0.000 |
| frame | R-DET-2 | 676 | 51 | 61 |
| frame | R-HUE-1 | 4.10 | 3.02 | 3.64 |
| sky | share | 0.099 | 0.390 | 0.001 |
| sky | median | 0.098 | 0.111 | 0.092 |
| sky | under_010 | 0.517 | 0.397 | 0.608 |
| sky | over_085 | 0.000 | 0.000 | 0.000 |
| sky | R-DET-2 | 0 | 6 | 0 |
| sky | R-HUE-1 | 2.68 | 2.75 | 1.10 |
| facades | share | 0.822 | 0.400 | 0.506 |
| facades | median | 0.135 | 0.100 | 0.070 |
| facades | under_010 | 0.288 | 0.499 | 0.660 |
| facades | over_085 | 0.005 | 0.000 | 0.001 |
| facades | R-DET-2 | 1421 | 92 | 87 |
| facades | R-HUE-1 | 4.09 | 2.99 | 4.29 |
| floor | share | 0.079 | 0.210 | 0.492 |
| floor | median | 0.155 | 0.108 | 0.107 |
| floor | under_010 | 0.142 | 0.433 | 0.454 |
| floor | over_085 | 0.014 | 0.000 | 0.000 |
| floor | R-DET-2 | 6325 | 64 | 34 |
| floor | R-HUE-1 | 3.99 | 2.87 | 3.29 |

## decision

| band | metric | plate | seed 1 | seed 2 |
|---|---|---|---|---|
| frame | share | 1.000 | 1.000 | 1.000 |
| frame | median | 0.141 | 0.131 | 0.144 |
| frame | under_010 | 0.327 | 0.372 | 0.363 |
| frame | over_085 | 0.010 | 0.002 | 0.001 |
| frame | R-DET-2 | 459 | 171 | 157 |
| frame | R-HUE-1 | 3.90 | 4.18 | 4.33 |
| sky | share | 0.020 | 0.065 | 0.000 |
| sky | median | 0.118 | 0.155 | n/a |
| sky | under_010 | 0.399 | 0.046 | n/a |
| sky | over_085 | 0.010 | 0.000 | n/a |
| sky | R-DET-2 | 0 | 17 | n/a |
| sky | R-HUE-1 | 3.75 | 2.65 | n/a |
| facades | share | 0.748 | 0.513 | 0.627 |
| facades | median | 0.160 | 0.153 | 0.176 |
| facades | under_010 | 0.296 | 0.270 | 0.280 |
| facades | over_085 | 0.009 | 0.002 | 0.002 |
| facades | R-DET-2 | 954 | 208 | 165 |
| facades | R-HUE-1 | 3.73 | 4.15 | 4.40 |
| floor | share | 0.232 | 0.422 | 0.373 |
| floor | median | 0.110 | 0.088 | 0.099 |
| floor | under_010 | 0.419 | 0.545 | 0.503 |
| floor | over_085 | 0.012 | 0.002 | 0.001 |
| floor | R-DET-2 | 4258 | 177 | 158 |
| floor | R-HUE-1 | 3.51 | 3.67 | 3.79 |
