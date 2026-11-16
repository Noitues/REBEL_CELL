"""Find the route rooms in the street_r2 overview: diff the route-overlay plate (03) against the closed plate (01),
same camera. Writes the diff mask and the room boxes to D:/rc_scratch/street_b/.

Run: python room_map.py
"""
import json
import os

import numpy as np
from PIL import Image

P = "D:/rc_art/art-pass/docs/concepts/route_map_graph/street_r2/plates/"
OUT = "D:/rc_scratch/street_b"


def main():
    a = np.asarray(Image.open(P + "01_OVERVIEW_closed_s1_plate.png").convert("RGB")).astype(np.float32)
    b = np.asarray(Image.open(P + "03_OVERVIEW_route_overlay_s1_plate.png").convert("RGB")).astype(np.float32)
    g = np.asarray(Image.open("D:/rc_art/art-pass/docs/concepts/golden_plates/street_overview.png").convert("RGB")).astype(np.float32)
    print("01 vs golden mean abs", float(np.abs(a - g).mean()))
    d = np.abs(b - a).max(axis=2)
    m = d > 40
    Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(OUT, "room_diff.png"))
    # connected components (4-neighbour, simple flood fill on a downsampled grid)
    s = 4
    hm = m[: m.shape[0] // s * s, : m.shape[1] // s * s].reshape(m.shape[0] // s, s, m.shape[1] // s, s).mean(axis=(1, 3)) > 0.3
    H, W = hm.shape
    lab = np.zeros(hm.shape, np.int32)
    boxes = []
    n = 0
    for y in range(H):
        for x in range(W):
            if hm[y, x] and not lab[y, x]:
                n += 1
                st = [(y, x)]
                lab[y, x] = n
                ys, xs = [], []
                while st:
                    cy, cx = st.pop()
                    ys.append(cy)
                    xs.append(cx)
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and hm[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n
                            st.append((ny, nx))
                if len(ys) >= 40:
                    boxes.append([min(xs) * s, min(ys) * s, (max(xs) + 1) * s, (max(ys) + 1) * s, len(ys)])
    boxes.sort(key=lambda q: (q[0], q[1]))
    for q in boxes:
        print(q)
    json.dump(boxes, open(os.path.join(OUT, "room_boxes.json"), "w"))


if __name__ == "__main__":
    main()
