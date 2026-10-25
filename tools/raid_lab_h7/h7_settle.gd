class_name H7Settle
extends RefCounted
## The money and state outcome of one raid (output of H7Campaign.settle).

var state: H7State
## salvage x kills + clean bonus (the payout).
var pay: int = 0
## Repair bill: home loss + scuffed points (not after CLEAN) + DOWN at half install.
var bill: int = 0
var spend: int = 0
## Income granted after this raid (0 after the last raid or a breach).
var income: int = 0
var kills: int = 0
## pay - bill (the raid net shown as a signed coin).
var net: int = 0
