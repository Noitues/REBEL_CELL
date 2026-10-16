"""HQ Meridian v3: the kit's corp build hook (hq_scene.py calls build(K) -> hooks). The landmark itself lives in the
importable module meridian_landmark.py (its entry point and how to place it in the city are documented there)."""
import meridian_landmark as ML


def build(K):
    return ML.build(K, rooms=True, rail=True)
