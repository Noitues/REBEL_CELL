"""Baseline: the unmodified A2 city_build.py through the same wrapper path (for timing and like-for-like previews)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CITY = os.path.normpath(os.path.join(HERE, "..", "..", "city_all_corps", "scripts"))
sys.dont_write_bytecode = True
SRC = os.path.join(CITY, "city_build.py")
sys.path.insert(0, CITY)
g = {"__name__": "__main__", "__file__": SRC}
exec(compile(open(SRC, encoding="utf-8").read(), SRC, "exec"), g)
