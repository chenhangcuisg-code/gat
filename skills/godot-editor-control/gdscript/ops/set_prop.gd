@tool
extends RefCounted
# set_prop — set property "{{property}}" = {{value}} on node "{{node}}"
# {{value}} is raw GDScript (e.g. Vector2(10,20) , "hello" , 42 , true)

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
	var before = n.get("{{property}}")
	n.set("{{property}}", {{value}})
	executeContext.output("node", "{{node}}")
	executeContext.output("property", "{{property}}")
	executeContext.output("before", str(before))
	executeContext.output("after", str(n.get("{{property}}")))
