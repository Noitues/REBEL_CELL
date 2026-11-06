import sys, os
name = sys.argv[1]
n = int(sys.argv[2])
FR = 'D:/rc_scratch/tide_concepts/p2m_work/frames/'
c = 0
for v in ('normal', 'reduce'):
    for f in range(n):
        p = FR + '%s_%s_%03d.png' % (name, v, f)
        if os.path.exists(p):
            os.remove(p); c += 1
print('removed', c)
