"""HQ Meridian v3: no mechanic UI yet (a design pass; the HQ mechanic is the game sessions' call). The kit overlay's
hooks, all neutral: no badges, no telegraphs."""
import ui31 as K  # noqa: F401

DISPATCH = {
    "start": "Meridian Freight. A castle made of boxes. The crane is the keep: get over the wall, up a leg, across.",
    "o1": "East wall. Climb the boxes to the leg, or drop to the train and go up from the quay.",
    "o2": "Leg's right above you. Or the express: a carriage is standing open at the quay.",
}


def node_mark(i, state, mech):
    return None


def marks(img, A, ov, mech, pose):
    return img


def dial(img, x, y, mech, ov):
    return img


def rule_note(i, walked, mech):
    return None


def legend_items():
    return []
