#!/bin/sh
# q.sh <logfile> <id skin> ... : run MPST effects sequentially
cd /d/rc_scratch/combat_redesign/locked/fx_o30b/mpst/src
log=$1; shift
while [ $# -ge 2 ]; do
  python run_fx.py $1 $2 >> $log 2>&1 || echo "FAIL $1 $2" >> $log
  shift 2
done
echo "QDONE" >> $log
