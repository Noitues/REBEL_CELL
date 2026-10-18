"""Aurelian HQ: no mechanic UI (art makes no rule; the HQ mechanic is the game sessions' call). The engine overlay's
hooks, all neutral: no badges, no telegraphs, no DISPATCH lines."""
import ui31 as K  # noqa: F401

DISPATCH = {"start": "Aurelian Concord. The Circus Aurelius."}      # neutral placeholder line (no rule, no hint)


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
