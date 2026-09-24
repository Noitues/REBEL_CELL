class_name CorporationData
extends Resource
## A corporation: its grid, enemies, raids, Exploits and story (8.3).

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var logo: Texture2D
@export var city_grid: CityGridData
@export var enemies: Array[EnemyData] = []
@export var elites: Array[EnemyData] = []
@export var final_boss: EnemyData
@export var exploits: Array[ExploitData] = []
@export var story_paths: Array[StoryPathData] = []
@export var raids: Array[RaidData] = []
@export var events: Array[TerminalEventData] = []
## REBEL_CELL: build grid, enemies and raids from the player's profile.
@export var generated_from_profile: bool = false


func validate(min_exploits: int = 3) -> PackedStringArray:
	var errors := PackedStringArray()
	if not generated_from_profile:
		if city_grid == null:
			errors.append("Corporation %s has no City Grid." % id)
		else:
			errors.append_array(city_grid.validate(min_exploits))
		if final_boss == null or not final_boss.is_boss:
			errors.append("Corporation %s needs a final boss marked is_boss." % id)
	if story_paths.size() < 5 or story_paths.size() > 6:
		errors.append("Corporation %s has %d story paths; design calls for 5-6." % [id, story_paths.size()])
	for p in story_paths:
		if p:
			errors.append_array(p.validate(min_exploits))
	for e in enemies + elites:
		if e:
			errors.append_array(e.validate())
	return errors
