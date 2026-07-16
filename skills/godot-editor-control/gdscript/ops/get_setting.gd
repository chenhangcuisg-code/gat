@tool
extends RefCounted
# get_setting — read project setting "{{key}}" (e.g. application/config/name)

func execute(executeContext):
	var has = ProjectSettings.has_setting("{{key}}")
	executeContext.output("key", "{{key}}")
	executeContext.output("exists", str(has))
	if has:
		executeContext.output("value", str(ProjectSettings.get_setting("{{key}}")))
