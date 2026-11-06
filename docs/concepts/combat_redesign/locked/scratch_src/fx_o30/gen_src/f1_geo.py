"""f1_geo: the finalist-1 board layout.  Import FIRST (before any other generator module).  Tower r196, trim r200-210, rings 214-..., arcs 436-470."""
import sys
sys.dont_write_bytecode = True
import cv_lib
RS = cv_lib.RS
RS.update(hub=50, s0=68, s1=184, hp0=52, hp1=64, c0=214, T=57, bz0=388, bz1=422)
TOWER_R = 196
