import sys
import scenes2 as SC
from m2 import *
name = sys.argv[1]; reduce = sys.argv[2] == 'r'; f = int(sys.argv[3]); box = [int(v) for v in sys.argv[4:8]]
a = getattr(SC, 'b_' + name)(f, reduce=reduce, mode='board')
Image.fromarray(a).crop(box).save('D:/rc_scratch/tide_concepts/p2m_work/tb.png')
