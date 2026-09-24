extends RefCounted
## Scrubber (GDD 6.2): capturing a Server Rack removes 1 Heat instead of adding it.
## Run-level hook: returns a heat override the NetrunSession applies in place of the
## Rack's Heat.


func handle(context: Dictionary, _state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if int(context.get("trigger", -1)) != RC.Trigger.ON_SERVER_RACK_CAPTURE:
		return []
	return [{"type": "heat_override", "amount": -1, "source_id": &"scrubber", "text": "Scrubber: the Rack capture scrubs 1 Heat instead of adding it."}]
