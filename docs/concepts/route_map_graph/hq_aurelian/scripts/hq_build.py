"""Aurelian HQ: the engine's corp build hook (hq_scene.py calls build(K) -> hooks). The landmark lives in
aurelian_landmark.py (one model for the city and the HQ, spec 8.6b)."""
import aurelian_landmark as AL


def build(K):
    return AL.build_hq(K, rooms=True)
