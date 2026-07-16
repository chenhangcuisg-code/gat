@tool
extends RefCounted
# add_node — add a {{type}} named "{{name}}" under "{{parent}}" ("." = scene root)

func execute(executeContext):
	var ei = executeContext.editor_plugin.get_editor_interface()
	var root = ei.get_edited_scene_root()
	if root == null:
		executeContext.output("error", "no scene is open in the editor")
		return
	var parent = root if "{{parent}}" == "." else root.get_node_or_null("{{parent}}")
	if parent == null:
		executeContext.output("error", "parent not found: {{parent}}")
		return
	if not ClassDB.class_exists("{{type}}"):
		executeContext.output("error", "unknown class: {{type}}")
		return
	var n = ClassDB.instantiate("{{type}}")
	n.name = "{{name}}"
	parent.add_child(n)
	n.owner = root
	executeContext.output("added", str(root.get_path_to(n)))
	executeContext.output("class", "{{type}}")
