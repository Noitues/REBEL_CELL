"""Tethys THE WATER LEVEL: world-space helpers. Camera is fitted from the rooms json (loc + 28..31 room correspondences,
f = 2130 px = 30 mm on a 36 mm sensor); the Z pass (axial depth) then gives every pixel a world position, so the water
plane (world z = Head step height) can be composited at its true height. Dry street z = 0 (DESIGN.md / art plan 0.1).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image

import solace_lib as L
import theme_lib as T

HQT = os.path.join(T.ROUTE, "hq_tethys")
RS = "D:/rc_scratch/tethys"
SRC = {
    "ov": dict(rooms=RS + "/final4/t_over_aaa_rooms.json", anc=RS + "/final4/t_over_aaa_anchors.json", z=RS + "/final4/t_over_aaa_z.npy",
               plate=HQT + "/H_overview_v2_plate.png", comp=HQT + "/H_overview_v2.png"),
    "dec": dict(rooms=RS + "/idpass/t_dec_aaa_rooms.json", anc=RS + "/idpass/t_dec_aaa_anchors.json", z=RS + "/idpass/t_dec_aaa_z.npy",
                plate=HQT + "/H_decision_v2_plate.png", comp=HQT + "/H_decision_v2.png"),
}
HEAD = {"LOW": 0.6, "RISING": 2.5, "HIGH": 5.0, "FALLING": 3.2}       # water plane height above the dry street (BU)
LOWER = {"deck_1", "deck_2", "deck_3", "deck_4", "deck_5", "server", "vent_cap", "collar", "cw_mid", "cw_pier"}
BASE_WATER = 2.5                                                      # the approved baseline baked into the plates


def fit_cam(rooms, loc, W=2560, H=1440):
    names = [k for k, v in rooms.items() if 0 < v["px"][0] < W and 0 < v["px"][1] < H]
    Pw = np.array([rooms[k]["world"] for k in names], float)
    px = np.array([rooms[k]["px"] for k in names], float)
    dw = Pw - loc
    dw /= np.linalg.norm(dw, axis=1)[:, None]
    f = 2130.0
    dc = np.stack([(px[:, 0] - W / 2) / f, -(px[:, 1] - H / 2) / f, -np.ones(len(px))], 1)
    dc /= np.linalg.norm(dc, axis=1)[:, None]
    U, S, Vt = np.linalg.svd(dc.T @ dw)
    D = np.diag([1, 1, np.linalg.det(Vt.T @ U.T)])
    return Vt.T @ D @ U.T, f


class Scene:
    def __init__(self, key, size=(1920, 1080)):
        s = SRC[key]
        self.key = key
        rj = json.load(open(s["rooms"]))
        a = json.load(open(s["anc"]))
        self.rooms = rj["rooms"]
        loc = np.array(a["cam"]["loc"], float)
        R, f = fit_cam(self.rooms, loc)
        z = np.load(s["z"])[..., 0].astype(np.float32)
        m = z.copy()                                  # the Z pass is stochastic on the water: take the nearest hit of a 5 x 5
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                m = np.minimum(m, np.roll(np.roll(z, dy, 0), dx, 1))
        z = m
        H, W = z.shape
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        valid = z < 1e8
        d = np.where(valid, z, 0)
        xc = (xx - W / 2) / f * d
        yc = -(yy - H / 2) / f * d
        pc = np.stack([xc, yc, -d], -1)
        P = loc[None, None, :] + pc @ R.T
        P = np.where(valid[..., None], P, np.nan)
        self.full = (W, H)
        self.valid = valid
        self.wx, self.wy, self.wz = P[..., 0], P[..., 1], P[..., 2]
        self.depth = z
        self.plate = np.asarray(Image.open(s["plate"]).convert("RGB"), np.float32) / 255.0
        self.comp = np.asarray(Image.open(s["comp"]).convert("RGB"), np.float32) / 255.0

    def px(self, name):
        p = self.rooms[name]["px"]
        return p[0], p[1]
