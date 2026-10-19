"""poses: assemble `poses_<run>.json` v1 from a derive v2 file (spec 2.2 `rig`, 5, 6, 7; review Q2.1-Q2.5, Q3.2-Q3.4).

Stores OVERVIEW, the first DECISION, the dive end poses, the rig constants, the zoom block, the lod and section blocks,
per-pose check values (`zoom_dive`, `zoom_detail`, lod weights, occlusion params and affected buildings, and for the HQ the
section params) and `fixtures[]` walks for parity: the first decision, a mid-route one and the last layer, each with a
HOVER pose, plus 5 dive samples. DECISION and HOVER for the live walk are computed at runtime from the real walked list.
Standard library only.
"""
import math
from typing import Any, Dict, List, Optional

from . import lod as LOD
from . import occlusion as OCC
from . import rig as RG
from . import section as SEC
from .derive.street import layer_nodes
from .hq import orbit as HO
from .hq import slots as HS

VERSION = 1
DIVE_SAMPLES = (0.0, 0.25, 0.5, 0.75, 1.0)
FIXTURE_WALKS = ("first", "mid", "last")


def successors(run_graph: Dict[str, Any], node: Optional[str]) -> List[str]:
    """Option ids after `node` (edge targets sorted by id), or the layer-1 nodes before the first step."""
    if node is None:
        return [n["id"] for n in layer_nodes(run_graph)[0][1]]
    return sorted(e["b"] for e in run_graph["edges"] if e["a"] == node)


def fixture_walks(run_graph: Dict[str, Any]) -> Dict[str, List[str]]:
    """Three deterministic walks: none, half way, and up to the last layer (first successor at every step)."""
    n = run_graph["layers"]
    walks = {"first": [], "mid": [], "last": []}
    cur: Optional[str] = None
    path: List[str] = []
    for step in range(1, n):
        opts = successors(run_graph, cur)
        cur = opts[0]
        path.append(cur)
        if step == max(1, n // 2):
            walks["mid"] = list(path)
    walks["last"] = list(path)
    return walks


def _layer_of(run_graph: Dict[str, Any], node: Optional[str]) -> int:
    if node is None:
        return 0
    return next(n["layer"] for n in run_graph["nodes"] if n["id"] == node)


class _Ctx:
    """Everything a pose record needs: the kind, rooms, boxes, camera functions."""

    def __init__(self, derive: Dict[str, Any], city: Dict[str, Any], run_graph: Dict[str, Any], net: Optional[Dict[str, Any]]):
        self.d, self.city, self.g, self.net = derive, city, run_graph, net
        self.kind = derive["kind"]
        self.rooms = derive["rooms"]
        self.layers = run_graph["layers"]
        self.ov = RG.Pose.from_json(derive["overview"])
        self.dec = RG.Pose.from_json(derive["decision"])
        skip = {r["bld"] for r in self.rooms.values()}
        self.boxes = OCC.building_boxes(city, skip)
        if self.kind == "hq":
            corp = derive["route_keys"][0].split(":", 1)[1]
            self.comp = HS.set_entrance(HS.plan_compound(HS.hq_lot_rect(city, corp), len(layer_nodes(run_graph))), self.ov, corp)
        self.d0 = None
        if self.kind == "street" and net is not None:
            tgt, w = RG.hq_page_camera(net)
            self.hq = RG.hq_page_pose(tgt, w)
            self.d0 = RG.dive_distance(self.hq, self.ov)
        self.d1, self.d_ov, self.d_dec = self.ov.dist, self.ov.dist, self.dec.dist

    def decision(self, current: Optional[str], options: List[str]) -> RG.Pose:
        layer = _layer_of(self.g, current)
        if self.kind == "hq":
            return HO.hq_decision(self.rooms, current, options, max(0, layer - 1) if current else 0, self.layers, None, self.comp["entrance"])
        u = RG.street_u(self.layers, layer)
        a = self.d["street"]["a"]
        return RG.street_decision(self.rooms, current, options, u, self.d["nrm"], self.d["start_left"], None, [a[0], a[1], 0.0])

    def hover(self, dec: RG.Pose, node: str) -> RG.Pose:
        if self.kind == "hq":
            return HO.hq_hover(dec, self.rooms[node])
        return RG.street_hover(dec, self.rooms[node], self.d["nrm"])

    def record(self, pose: RG.Pose, ids: List[str], decision: bool = False) -> Dict[str, Any]:
        """Pose plus its check values: zoom_dive / zoom_detail, lod weights, occlusion (and HQ section) params.

        A `decision` record's occlusion cone targets EVERY route room in frame (art-pass 6d214ce9), the `ids` rooms
        included; the HQ section params keep the `ids` points.
        """
        loc = pose.loc()
        pts = [[q[0], q[1], q[2] + self.rooms[i].get("ground_z", 0.0)] for i in ids for q in self.rooms[i]["front"]]
        occ_pts = pts
        if decision:
            vis = HO.visible_room if self.kind == "hq" else None
            occ_ids = sorted(set(ids) | set(OCC.rooms_in_frame(self.rooms, pose, RG.REF_W, RG.REF_H, vis)))
            occ_pts = [[q[0], q[1], q[2] + self.rooms[i].get("ground_z", 0.0)] for i in occ_ids for q in self.rooms[i]["front"]]
        rec: Dict[str, Any] = dict(pose=pose.to_json())
        if self.d0 is not None:
            rec["zoom_dive"] = LOD.zoom_dive(RG.dive_distance(pose, self.ov), self.d0, self.d1)
        rec["zoom_detail"] = LOD.zoom_detail(pose.dist, self.d_ov, self.d_dec)
        rec["lod_weights"] = LOD.weights(pose.dist)
        rec["occlusion"] = OCC.occlusion_block(OCC.occlusion_params(loc, occ_pts), self.boxes)
        if self.kind == "hq":
            hs = self.comp["half"][0]
            rec["section"] = SEC.section_params(loc, ("rect", hs, hs), pts if ids != list(self.rooms) else None)
        return rec


def build_poses(derive: Dict[str, Any], city: Dict[str, Any], run_graph: Dict[str, Any],
                net: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """`poses_<run>.json` v1 for a street or HQ derive. `net` feeds the street dive's HQ page camera."""
    cx = _Ctx(derive, city, run_graph, net)
    first = successors(run_graph, None)
    out: Dict[str, Any] = dict(
        version=VERSION, run=derive["run"], layout_seed=derive["layout_seed"], kind=derive["kind"],
        overview=cx.record(cx.ov, sorted(cx.rooms)), decision=cx.record(cx.dec, first, True),
        rig=dict(RG.RIG, look_bias_sign=RG.LOOK_BIAS_SIGN) if cx.kind == "street" else dict(HO.HQ_RIG),
        zoom=dict(d_ov=cx.d_ov, d_dec=cx.d_dec), lod=LOD.lod_block(), section=SEC.section_block())
    if cx.d0 is not None:
        out["zoom"].update(d0=cx.d0, d1=cx.d1)
        out["dive"] = dict(hq_pose=cx.hq.to_json(), overview_pose=cx.ov.to_json(), duration_s=RG.DIVE["duration_s"],
                           lag_k=RG.DIVE["lag_k"], lag_pow=RG.DIVE["lag_pow"], hq_lens=RG.DIVE["hq_lens"],
                           samples=[dict(u=u, pose=RG.dive_pose(u, cx.hq, cx.ov).to_json(),
                                         zoom_dive=LOD.zoom_dive(RG.dive_distance(RG.dive_pose(u, cx.hq, cx.ov), cx.ov),
                                                                 cx.d0, cx.d1)) for u in DIVE_SAMPLES])
    fixtures = []
    for name, walked in fixture_walks(run_graph).items():
        cur = walked[-1] if walked else None
        opts = successors(run_graph, cur)
        dec = cx.decision(cur, opts)
        hov = cx.hover(dec, opts[0])
        fixtures.append(dict(name=name, walked=walked, current=cur, options=opts, hover=opts[0],
                             decision=cx.record(dec, ([cur] if cur else []) + opts, True), hover_pose=hov.to_json()))
    out["fixtures"] = fixtures
    return out
