@tool
extends RefCounted
# save_scene — save the currently edited scene to disk

func execute(executeContext):
	var ei = executeContext.editor_plugin.get_editor_interface()
	var root = ei.get_edited_scene_root()
	if root == null:
		executeContext.output("error", "no scene is open")
		return
	var err = ei.save_scene()
	executeContext.output("scene", str(root.scene_file_path))
	executeContext.output("result", "OK" if err == OK else "ERR %d" % err)
