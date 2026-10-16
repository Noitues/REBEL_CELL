"""Rebel Cell: the build dispatcher (HQ_VARIANT A | C, default A: the designer picked option A): see hq_graph.py."""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def build(K):
    return importlib.import_module("hq_build_" + os.environ.get("HQ_VARIANT", "A")).build(K)
