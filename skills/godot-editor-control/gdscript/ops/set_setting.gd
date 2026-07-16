@tool
extends RefCounted
# set_setting — set project setting "{{key}}" = {{value}} and persist project.godot
# {{value}} is raw GDScript (e.g. "res://ui/Main.tscn" , 60 , true)

func execute(executeContext):
	ProjectSettings.set_setting("{{key}}", {{value}})
	var err = ProjectSettings.save()
	executeContext.output("key", "{{key}}")
	executeContext.output("saved", "OK" if err == OK else "ERR %d" % err)
	executeContext.output("value", str(ProjectSettings.get_setting("{{key}}")))
