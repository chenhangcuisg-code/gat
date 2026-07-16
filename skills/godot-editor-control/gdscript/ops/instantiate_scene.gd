@tool
extends RefCounted
# instantiate_scene — instance packed scene "{{scene}}" under "{{parent}}" as "{{name}}"

func execute(executeContext):
	var ei = executeContext.editor_plugin.get_editor_interface()
	var root = ei.get_edited_scene_root()
	if root == null:
		executeContext.output("error", "no scene is open")
		return
	if not ResourceLoader.exists("{{scene}}"):
		executeContext.output("error", "scene not found: {{scene}}")
		return
	var parent = root if "{{parent}}" == "." else root.get_node_or_null("{{parent}}")
	if parent == null:
		executeContext.output("error", "parent not found: {{parent}}")
		return
	var inst = load("{{scene}}").instantiate()
	inst.name = "{{name}}"
	parent.add_child(inst)
	inst.owner = root
	executeContext.output("instanced", str(root.get_path_to(inst)))
