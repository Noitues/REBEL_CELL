"""Rebel Cell: the graph dispatcher. The designer asked for 2-3 concept OPTIONS for the Sync Strike route map; each
option is a graph module (hq_graph_A: three stacked lanes in a side view; hq_graph_C: the converging map; option B is
composed from option C's renders). The environment variable HQ_VARIANT picks one (default A, the designer's pick); this module replaces
itself with that module so every kit script (`import hq_graph as G`) sees the same graph.
"""
import importlib
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules[__name__] = importlib.import_module("hq_graph_" + os.environ.get("HQ_VARIANT", "A"))
