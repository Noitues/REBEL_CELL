extends GutTest
## N19: listener fires. N6 is absent, so the collector reports null unless told listeners exist.

const P := &"player"


func test_fires_are_null_while_n6_is_absent() -> void:
	var m := SimMetrics.new(P)
	m.observe(true, [{"type": "listener_fire", "listener": "clawback"}])
	assert_null(m.to_dict(true)["listener_fires"])


func test_fires_count_by_listener_id_when_supported() -> void:
	var m := SimMetrics.new(P, true)
	for i in 3:
		m.observe(true, [{"type": "listener_fire", "listener": "clawback"}])
	assert_eq(m.to_dict(true)["listener_fires"], {"clawback": 3})


func test_no_fires_is_an_empty_dict_not_null_when_supported() -> void:
	assert_eq(SimMetrics.new(P, true).to_dict(true)["listener_fires"], {})
