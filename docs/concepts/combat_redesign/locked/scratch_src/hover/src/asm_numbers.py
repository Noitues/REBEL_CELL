"""asm_numbers: tower numbers recounted from the state vs what the (locked) tower drawing functions are told to draw."""
import sys, json
sys.dont_write_bytecode = True
import lw_render
import f1_infocheck as IC
res = IC.numbers()
json.dump(res, open('D:/rc_scratch/combat_redesign/locked/hover/work/numbers.json', 'w'), indent=1, default=str)
