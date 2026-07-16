@tool
extends RefCounted
# open_scene — open scene "{{path}}" (a res:// path) in the editor

func execute(executeContext):
	var ei = executeContext.editor_plugin.get_editor_interface()
	if not ResourceLoader.exists("{{path}}"):
		executeContext.output("error", "scene not found: {{path}}")
		return
	ei.open_scene_from_path("{{path}}")
	executeContext.output("opened", "{{path}}")
