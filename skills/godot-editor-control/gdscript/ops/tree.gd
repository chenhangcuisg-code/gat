@tool
extends RefCounted
# tree — dump the currently edited scene tree (name [Class] (NodePath))

func execute(executeContext):
	var ei = executeContext.editor_plugin.get_editor_interface()
	var root = ei.get_edited_scene_root()
	if root == null:
		executeContext.output("error", "no scene is open in the editor")
		return
	var lines = []
	_walk(root, root, 0, lines)
	executeContext.output("root", str(root.name))
	executeContext.output("count", str(lines.size()))
	executeContext.output("tree", "\n".join(lines))

func _walk(node, root, depth, lines):
	var indent = "  ".repeat(depth)
	lines.append("%s%s [%s] (%s)" % [indent, node.name, node.get_class(), str(root.get_path_to(node))])
	for c in node.get_children():
		_walk(c, root, depth + 1, lines)
