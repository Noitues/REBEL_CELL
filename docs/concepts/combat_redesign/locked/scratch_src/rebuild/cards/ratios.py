"""ratios: plate vs paper and TOWER vs WAVE luminance ratios for the picked type hues."""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from de_lib import *
T, W, P = hx('006E66'), hx('B4AAFF'), hx('F4EEE0')
print('TOWER vs paper %.2f  WAVE vs paper %.2f  TOWER vs WAVE %.2f' % (ratio(T, P), ratio(W, P), ratio(T, W)))
print('L* TOWER %.1f WAVE %.1f paper %.1f Spin3 %.1f' % (Lstar(T), Lstar(W), Lstar(P), Lstar(hx('FF00F0'))))
