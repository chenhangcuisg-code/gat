@tool
extends RefCounted
# play — run the project's main scene from the editor

func execute(executeContext):
	var ei = executeContext.editor_plugin.get_editor_interface()
	ei.play_main_scene()
	executeContext.output("playing", "main_scene")
