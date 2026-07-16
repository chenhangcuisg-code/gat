# operations-cookbook.md — Godot 4.x 编辑器操作 GDScript 配方

"操控编辑器"本质 = 通过 broker 发送 **GDScript** 在编辑器里跑。本文是可直接用/改的配方库。
`gop.py op <name>` 用的模板就在 `gdscript/ops/*.gd`(整类模式)。

## 0. 写 GDScript 的硬规则(否则 compile_error)
- `func`(非 `def`)、`true/false/null`(非 `True/False/None`)、`var x := 1`(`:=` 类型推断)。
- **缩进用 Tab**(本库 `.gd` 全 Tab)。整类模式自己写整文件,缩进自洽即可。
- 很多 API 返回 `Error` 枚举(整数),`OK == 0`;**务必判 `== OK`**,非 0 即失败。
- 编辑器入口:`var ei = executeContext.editor_plugin.get_editor_interface()`
  (`editor_plugin` 仅 editor executor 有;新版也可用全局单例 `EditorInterface`)。
- 结果回传:`executeContext.output("key", value)`(value 尽量 `str(...)` 成字符串)。

## 1. 片段 vs 整类
**片段(默认,不含 extends)**——简单一次性查询:
```gdscript
var ei = executeContext.editor_plugin.get_editor_interface()
executeContext.output("scene", str(ei.get_edited_scene_root()))
```
**整类(含 extends)**——本库标准写法,规避自动包装混缩进:
```gdscript
@tool
extends RefCounted
func execute(executeContext):
	var ei = executeContext.editor_plugin.get_editor_interface()
	executeContext.output("ok", "1")
```

## 2. 场景树:读取
```gdscript
var root = ei.get_edited_scene_root()        # 当前编辑的场景根(无则 null)
for c in root.get_children():
	executeContext.output(str(c.name), c.get_class())
# 取某节点:root.get_node_or_null("Path/To/Node")
# 节点路径:str(root.get_path_to(node))
```
→ 见 `ops/tree.gd`。

## 3. 节点:增 / 删 / 改名 / 重定父
```gdscript
var n = ClassDB.instantiate("Sprite2D")      # 按类名建节点(先 ClassDB.class_exists 校验)
n.name = "Hero"
parent.add_child(n)
n.owner = root                                # ★ 关键:设 owner=场景根,保存时才会被序列化
# 删除:node.queue_free() 或 parent.remove_child(node); node.free()
# 重定父:old.remove_child(n); new.add_child(n); n.owner = root
```
→ 见 `ops/add_node.gd` / `ops/instantiate_scene.gd`。**忘了设 owner → 节点存不进 .tscn**。

## 4. 属性:读 / 写
```gdscript
var v = node.get("position")                 # 通用读
node.set("position", Vector2(120, 80))        # 通用写(值是 GDScript 表达式)
# 复杂值同理:Color(1,0,0), NodePath("../X"), preload(...), 资源等
```
→ 见 `ops/set_prop.gd`(`--set value=...` 传**原始 GDScript 表达式**,如 `value=Vector2(10,20)`)。

## 5. 脚本 / 资源
```gdscript
node.set_script(load("res://hero.gd"))        # 挂脚本
var packed = load("res://ui/Hud.tscn")        # 加载 PackedScene
var inst = packed.instantiate(); parent.add_child(inst); inst.owner = root
# 校验存在:ResourceLoader.exists("res://...")
```
→ 见 `ops/attach_script.gd`。

## 6. 保存 / 打开场景
```gdscript
ei.open_scene_from_path("res://ui/Main.tscn") # 打开
var err = ei.save_scene()                      # 保存当前(判 err==OK)
# 另存:ei.save_scene_as("res://new.tscn")
```
→ `ops/open_scene.gd` / `ops/save_scene.gd`。
> 进阶:保存/撤销/重做这类**菜单动作**,作者建议用**菜单项信号触发**而非直接 API,以保证编辑器状态一致
> (走 `get_editor_interface()` 找菜单按钮并 `emit_signal("pressed")`)。简单保存用 `save_scene()` 即可。

## 7. 运行 / 停止工程
```gdscript
ei.play_main_scene()        # 跑主场景
ei.play_current_scene()     # 跑当前场景
ei.stop_playing_scene()     # 停
```
→ `ops/play.gd`。

## 8. 项目设置
```gdscript
ProjectSettings.has_setting("application/config/name")
ProjectSettings.get_setting("application/config/name")
ProjectSettings.set_setting("application/run/max_fps", 60)
var err = ProjectSettings.save()             # 持久化到 project.godot(判 OK)
```
→ `ops/get_setting.gd` / `ops/set_setting.gd`。

## 9. 资源导入 / 文件系统刷新
```gdscript
ei.get_resource_filesystem().scan()          # 重扫资源(导入新文件后)
# 单文件重导:ei.get_resource_filesystem().reimport_files(["res://x.png"])
```

## 10. game executor(运行时)
`type=game` 时 **无 EditorInterface**,改用运行时场景树:
```gdscript
var tree = Engine.get_main_loop() as SceneTree
var player = tree.current_scene.get_node_or_null("Player")
executeContext.output("hp", str(player.hp))
```
> game executor 跑前先在编辑器开 **Ignore Error Breaks**,否则运行时报错会卡死游戏 → 请求 504 超时。

## 常见坑
- 节点没设 `owner` → 存不进场景。
- 改了场景没 `save_scene()` → 重载丢失。
- 直接改运行中 game 的状态不会回写编辑器场景(两套树)。
- `set()` 的属性名错 → 静默无效;用 `tree`/`get()` 先确认属性存在。
- 中文 `output` 值在 Windows 控制台可能显示乱码(编码问题),数据本身是 UTF-8,不影响逻辑。
