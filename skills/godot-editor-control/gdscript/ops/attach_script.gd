@tool
extends RefCounted
# attach_script — attach script "{{script}}" (res://) to node "{{node}}"

func execute(executeContext):
	var ei = executeContext.editor_plugin.get_editor_interface()
	var root = ei.get_edited_scene_root()
	if root == null:
		executeContext.output("error", "no scene is open")
		return
	var n = root if "{{node}}" == "." else root.get_node_or_null("{{node}}")
	if n == null:
		executeContext.output("error", "node not found: {{node}}")
		return
	if not ResourceLoader.exists("{{script}}"):
		executeContext.output("error", "script not found: {{script}}")
		return
	n.set_script(load("{{script}}"))
	executeContext.output("attached", "{{script}}")
	executeContext.output("node", "{{node}}")
