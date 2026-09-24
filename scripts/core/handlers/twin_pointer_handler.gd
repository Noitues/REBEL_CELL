extends RefCounted
## Twin Pointer (GDD 6.2): your wheel is also read at the bottom; both trigger. Max RAM
## halved (rounded up). The pointer rule is symmetric (GDD 2.7), so enemy attacks hit
## whatever sits at both of your pointers too.


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if not (state is CombatState) or int(context.get("trigger", -1)) != RC.Trigger.ON_COMBAT_START:
		return []
	var wheel: WheelState = state.player.wheel
	var bottom := posmod(wheel.pointer_ticks[0] + RC.TICKS / 2, RC.TICKS)
	if not wheel.pointer_ticks.has(bottom):
		wheel.pointer_ticks.append(bottom)
	state.max_ram = (state.max_ram + 1) / 2
	state.ram = mini(state.ram, state.max_ram)
	return [{"type": "twin_pointer", "max_ram": state.max_ram,
		"text": "Twin Pointer: a second read head at tick %d; max RAM is %d." % [bottom, state.max_ram]}]
