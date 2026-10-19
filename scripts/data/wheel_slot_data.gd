class_name WheelSlotData
extends Resource
## One position on a wheel: a slice plus its optional Firmware.

@export var slice: SliceData
@export var firmware: FirmwareData
## Plan 2 N12 (R11, Q20): the slot's arc in ticks, 0-30 (0 = an empty arc that owns no tick).
## RC.SIZE_AUTO (the default) is an equal share: 30 / slot count, so a 6-slot wheel reads 5
## and a satellite's 2-3 slots read 15 / 10. A wheel's slots are all AUTO or all sized.
@export_range(-1, 30) var size_ticks: int = RC.SIZE_AUTO
## Plan 2 N12 (R11): an authored sub-tick quality map, one RC.PrecisionTier per tick of the
## slot (its length must equal the size); empty = the default map for the size.
@export var tick_quality: PackedInt32Array = PackedInt32Array()
