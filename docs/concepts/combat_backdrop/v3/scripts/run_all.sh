#!/bin/bash
# renders + posts all 7 rooms (v3 seeds). usage: run_all.sh
cd D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3/scripts
for spec in "server_room 23 srv 4.4" "greenhouse 37 gh 4.4" "records_office 41 rec 4.4" "lobby 53 lobby 4.4" "event_room 67 event 4.4" "shop 71 shop 0.62"; do
  set -- $spec
  bash render_room.sh $1 $2 $3 12
  python post.py $3 0.58 $4
done
